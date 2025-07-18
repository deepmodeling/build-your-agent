#!/usr/bin/env python3
"""
NexusAgent WebSocket 服务器
使用 Session 运行 rootagent，并通过 WebSocket 与前端通信
"""

import os
import asyncio
import json
import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from typing import Optional, Set, Dict, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
import uuid
import subprocess
import shlex

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
import uvicorn

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import configuration
from config.agent_config import agent_config

# Get agent from configuration
rootagent = agent_config.get_agent()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    id: str
    role: str  # 'user' or 'assistant' or 'tool'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: Optional[str] = None
    tool_status: Optional[str] = None

@dataclass 
class Session:
    id: str
    title: str = "新对话"
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_message_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, tool_name: Optional[str] = None, tool_status: Optional[str] = None):
        """添加消息到会话"""
        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            tool_name=tool_name,
            tool_status=tool_status
        )
        self.messages.append(message)
        self.last_message_at = datetime.now()
        
        if self.title == "新对话" and role == "user" and len(self.messages) <= 2:
            self.title = content[:30] + "..." if len(content) > 30 else content
        
        return message

app = FastAPI(title="NexusAgent WebSocket Server")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SessionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.sessions: Dict[str, Session] = {}
        self.runners: Dict[str, Runner] = {}
        self.session_services: Dict[str, InMemorySessionService] = {}
        # Use configuration values
        self.app_name = agent_config.config.get("agent", {}).get("name", "NexusAgent")
        self.user_id = "user_001"
        self.current_session_id: Optional[str] = None
        # 为每个WebSocket连接维护独立的shell状态
        self.shell_sessions: Dict[WebSocket, Dict[str, any]] = {}
        
    async def create_session(self) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id)
        
        # 先将会话添加到列表，让前端立即看到
        self.sessions[session_id] = session
        logger.info(f"创建新会话: {session_id}")
        
        # 异步创建 session service 和 runner，避免阻塞
        asyncio.create_task(self._init_session_runner(session_id))
        
        return session
    
    async def _init_session_runner(self, session_id: str):
        """异步初始化会话的runner"""
        try:
            session_service = InMemorySessionService()
            await session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            
            runner = Runner(
                agent=rootagent,
                session_service=session_service,
                app_name=self.app_name
            )
            
            self.session_services[session_id] = session_service
            self.runners[session_id] = runner
            
            logger.info(f"Runner 初始化完成: {session_id}")
            
        except Exception as e:
            logger.error(f"初始化Runner失败: {e}")
            # 清理失败的会话
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_services:
                del self.session_services[session_id]
            if session_id in self.runners:
                del self.runners[session_id]
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Session]:
        """获取所有会话列表"""
        return list(self.sessions.values())
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.runners:
                del self.runners[session_id]
            if session_id in self.session_services:
                del self.session_services[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False
    
    async def switch_session(self, session_id: str) -> bool:
        """切换当前会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            logger.info(f"切换到会话: {session_id}")
            return True
        return False
    
    async def connect_client(self, websocket: WebSocket):
        """连接新客户端"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # 如果没有会话，创建一个默认会话
        if not self.sessions:
            session = await self.create_session()
            self.current_session_id = session.id
            
        # 发送初始会话信息
        await self.send_sessions_list(websocket)
        
    def disconnect_client(self, websocket: WebSocket):
        """断开客户端连接"""
        self.active_connections.discard(websocket)
        # 清理shell会话
        if websocket in self.shell_sessions:
            del self.shell_sessions[websocket]
    
    async def send_sessions_list(self, websocket: Optional[WebSocket] = None):
        """发送会话列表到客户端"""
        sessions_data = []
        for session in self.sessions.values():
            sessions_data.append({
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "last_message_at": session.last_message_at.isoformat(),
                "message_count": len(session.messages)
            })
        
        message = {
            "type": "sessions_list",
            "sessions": sessions_data,
            "current_session_id": self.current_session_id
        }
        
        if websocket:
            await websocket.send_json(message)
        else:
            await self.broadcast(message)
    
    async def send_session_messages(self, session_id: str, websocket: Optional[WebSocket] = None):
        """发送会话的历史消息"""
        session = self.get_session(session_id)
        if not session:
            return
            
        messages_data = []
        for msg in session.messages:
            messages_data.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tool_name": msg.tool_name,
                "tool_status": msg.tool_status
            })
        
        message = {
            "type": "session_messages",
            "session_id": session_id,
            "messages": messages_data
        }
        
        if websocket:
            await websocket.send_json(message)
        else:
            await self.broadcast(message)
    
    async def broadcast(self, message: dict):
        """广播消息到所有客户端"""
        # 为消息添加唯一标识符
        if 'id' not in message:
            message['id'] = f"{message.get('type', 'unknown')}_{datetime.now().timestamp()}"
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.add(connection)
        
        # 移除断开的连接
        self.active_connections -= disconnected
    
    async def process_message(self, message: str, websocket: WebSocket):
        """处理用户消息"""
        if not self.current_session_id:
            await websocket.send_json({
                "type": "error", 
                "content": "没有活动的会话"
            })
            return
            
        # 等待runner初始化完成
        retry_count = 0
        while self.current_session_id not in self.runners and retry_count < 50:  # 最多等待5秒
            await asyncio.sleep(0.1)
            retry_count += 1
            
        if self.current_session_id not in self.runners:
            await websocket.send_json({
                "type": "error", 
                "content": "会话初始化失败，请重试"
            })
            return
            
        session = self.sessions[self.current_session_id]
        runner = self.runners[self.current_session_id]
        
        # 保存用户消息到会话历史
        session.add_message("user", message)
        
        try:
            
            content = types.Content(
                role='user',
                parts=[types.Part(text=message)]
            )
            
            # 收集所有事件
            all_events = []
            seen_tool_calls = set()  # 跟踪已发送的工具调用
            seen_tool_responses = set()  # 跟踪已发送的工具响应
            
            async for event in runner.run_async(
                new_message=content,
                user_id=self.user_id,
                session_id=self.current_session_id
            ):
                all_events.append(event)
                logger.info(f"Received event: {type(event).__name__}")
                
                # 检查事件中的工具调用（按照官方示例）
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        # 检查是否是函数调用
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            tool_name = getattr(function_call, 'name', 'unknown')
                            tool_id = getattr(function_call, 'id', tool_name)
                            
                            # 避免重复发送相同的工具调用
                            if tool_id in seen_tool_calls:
                                continue
                            seen_tool_calls.add(tool_id)
                            
                            # 检查是否是长时间运行的工具
                            is_long_running = False
                            if (hasattr(event, 'long_running_tool_ids') and 
                                event.long_running_tool_ids and 
                                hasattr(function_call, 'id')):
                                is_long_running = function_call.id in event.long_running_tool_ids
                            
                            await self.broadcast({
                                "type": "tool",
                                "tool_name": tool_name,
                                "status": "executing",
                                "is_long_running": is_long_running,
                                "timestamp": datetime.now().isoformat()
                            })
                            logger.info(f"Tool call detected: {tool_name} (long_running: {is_long_running})")
                        
                        # 检查是否是函数响应（工具完成）
                        elif hasattr(part, 'function_response') and part.function_response:
                            function_response = part.function_response
                            # 从响应中获取更多信息
                            tool_name = "unknown"
                            tool_result = None
                            
                            if hasattr(function_response, 'name'):
                                tool_name = function_response.name
                            
                            # 创建唯一标识符
                            response_id = f"{tool_name}_response"
                            if hasattr(function_response, 'id'):
                                response_id = function_response.id
                            
                            # 避免重复发送相同的工具响应
                            if response_id in seen_tool_responses:
                                continue
                            seen_tool_responses.add(response_id)
                            
                            if hasattr(function_response, 'response'):
                                response_data = function_response.response
                                
                                # 智能格式化不同类型的响应
                                if isinstance(response_data, dict):
                                    # 如果是字典，尝试美化JSON格式
                                    try:
                                        result_str = json.dumps(response_data, indent=2, ensure_ascii=False)
                                    except:
                                        result_str = str(response_data)
                                elif isinstance(response_data, (list, tuple)):
                                    # 如果是列表或元组，也尝试JSON格式化
                                    try:
                                        result_str = json.dumps(response_data, indent=2, ensure_ascii=False)
                                    except:
                                        result_str = str(response_data)
                                elif isinstance(response_data, str):
                                    # 字符串直接使用，保留原始格式
                                    result_str = response_data
                                else:
                                    # 其他类型转换为字符串
                                    result_str = str(response_data)
                                
                                await self.broadcast({
                                    "type": "tool",
                                    "tool_name": tool_name,
                                    "status": "completed",
                                    "result": result_str,
                                    "timestamp": datetime.now().isoformat()
                                })
                            else:
                                # 没有结果的情况
                                await self.broadcast({
                                    "type": "tool",
                                    "tool_name": tool_name,
                                    "status": "completed",
                                    "timestamp": datetime.now().isoformat()
                                })
                            
                            logger.info(f"Tool response received: {tool_name}")
            
            # 处理所有事件，只获取最后一个有效响应
            logger.info(f"Total events: {len(all_events)}")
            
            final_response = None
            # 从后往前查找最后一个有效的响应
            for event in reversed(all_events):
                if hasattr(event, 'content') and event.content:
                    content = event.content
                    # 处理 Google ADK 的 Content 对象
                    if hasattr(content, 'parts') and content.parts:
                        # 提取所有文本部分
                        text_parts = []
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            final_response = '\n'.join(text_parts)
                            break
                    elif hasattr(content, 'text') and content.text:
                        final_response = content.text
                        break
                elif hasattr(event, 'text') and event.text:
                    final_response = event.text
                    break
                elif hasattr(event, 'output') and event.output:
                    final_response = event.output
                    break
                elif hasattr(event, 'message') and event.message:
                    final_response = event.message
                    break
            
            # 只发送最后一个响应内容
            if final_response:
                logger.info(f"Sending final response: {final_response[:200]}")
                # 保存助手回复到会话历史
                session.add_message("assistant", final_response)
                
                await self.broadcast({
                    "type": "assistant",
                    "content": final_response,
                    "session_id": self.current_session_id
                })
            else:
                logger.warning("No response content found in events")
            
            # 发送一个空的完成标记，前端会识别这个来停止loading
            await self.broadcast({
                "type": "complete",
                "content": ""
            })
                    
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            await websocket.send_json({
                "type": "error",
                "content": f"处理消息失败: {str(e)}"
            })

# 创建全局管理器
manager = SessionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect_client(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                content = data.get("content", "").strip()
                if content:
                    await manager.process_message(content, websocket)
                    
            elif message_type == "create_session":
                # 创建新会话
                session = await manager.create_session()
                await manager.switch_session(session.id)
                await manager.send_sessions_list(websocket)
                await manager.send_session_messages(session.id, websocket)
                
            elif message_type == "switch_session":
                # 切换会话
                session_id = data.get("session_id")
                if session_id and await manager.switch_session(session_id):
                    await manager.send_session_messages(session_id, websocket)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "content": "会话不存在"
                    })
                    
            elif message_type == "get_sessions":
                # 获取会话列表
                await manager.send_sessions_list(websocket)
                
            elif message_type == "delete_session":
                # 删除会话
                session_id = data.get("session_id")
                if session_id and manager.delete_session(session_id):
                    # 如果删除的是当前会话，切换到其他会话或创建新会话
                    if session_id == manager.current_session_id:
                        if manager.sessions:
                            # 切换到第一个可用会话
                            first_session_id = list(manager.sessions.keys())[0]
                            await manager.switch_session(first_session_id)
                        else:
                            # 创建新会话
                            session = await manager.create_session()
                            await manager.switch_session(session.id)
                    await manager.send_sessions_list(websocket)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "content": "删除会话失败"
                    })
                    
            elif message_type == "shell_command":
                command = data.get("command", "").strip()
                if command:
                    await execute_shell_command(command, websocket, manager)
                
    except WebSocketDisconnect:
        manager.disconnect_client(websocket)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect_client(websocket)

@app.get("/api/files/tree")
async def get_file_tree(path: str = None):
    """获取文件树结构"""
    try:
        # Use configured output directory if no path specified
        if path is None:
            path = agent_config.get_files_config().get("outputDirectory", "output")
        
        base_path = Path(path)
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
            
        def build_tree(directory: Path):
            items = []
            try:
                for item in sorted(directory.iterdir()):
                    if item.name.startswith('.'):
                        continue
                        
                    node = {
                        "name": item.name,
                        "path": str(item.relative_to(".")),
                        "type": "directory" if item.is_dir() else "file"
                    }
                    
                    if item.is_dir():
                        node["children"] = build_tree(item)
                    else:
                        node["size"] = item.stat().st_size
                        
                    items.append(node)
            except PermissionError:
                pass
            return items
        
        return JSONResponse(content=build_tree(base_path))
        
    except Exception as e:
        logger.error(f"获取文件树错误: {e}")
        return JSONResponse(content=[], status_code=500)

@app.get("/api/files/{file_path:path}")
async def get_file_content(file_path: str):
    """获取文件内容"""
    try:
        file = Path(file_path)
        if not file.exists() or not file.is_file():
            return JSONResponse(
                content={"error": "文件未找到"},
                status_code=404
            )
        
        # 判断文件类型
        suffix = file.suffix.lower()
        
        # 文本文件
        if suffix in ['.json', '.md', '.txt', '.csv', '.py', '.js', '.ts', '.log', '.xml', '.yaml', '.yml']:
            try:
                content = file.read_text(encoding='utf-8')
                return PlainTextResponse(content)
            except UnicodeDecodeError:
                return JSONResponse(
                    content={"error": "无法解码文件内容"},
                    status_code=400
                )
        else:
            # 二进制文件
            return FileResponse(file)
            
    except Exception as e:
        logger.error(f"读取文件错误: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"{agent_config.config.get('agent', {}).get('name', 'NexusAgent')} WebSocket 服务器正在运行",
        "mode": "session",
        "endpoints": {
            "websocket": "/ws",
            "files": "/api/files",
            "file_tree": "/api/files/tree",
            "config": "/api/config"
        }
    }

@app.get("/api/config")
async def get_config():
    """获取前端配置信息"""
    return JSONResponse(content={
        "agent": agent_config.config.get("agent", {}),
        "ui": agent_config.get_ui_config(),
        "files": agent_config.get_files_config(),
        "websocket": agent_config.get_websocket_config()
    })

# 安全的命令白名单
SAFE_COMMANDS = {
    'ls', 'pwd', 'cd', 'cat', 'echo', 'grep', 'find', 'head', 'tail', 
    'wc', 'sort', 'uniq', 'diff', 'cp', 'mv', 'mkdir', 'touch', 'date',
    'whoami', 'hostname', 'uname', 'df', 'du', 'ps', 'top', 'which',
    'git', 'npm', 'python', 'pip', 'node', 'yarn', 'curl', 'wget',
    'tree', 'clear', 'history'
}

# 危险命令黑名单
DANGEROUS_COMMANDS = {
    'rm', 'rmdir', 'kill', 'killall', 'shutdown', 'reboot', 'sudo',
    'su', 'chmod', 'chown', 'dd', 'format', 'mkfs', 'fdisk', 'apt',
    'yum', 'brew', 'systemctl', 'service', 'docker', 'kubectl'
}

async def execute_shell_command(command: str, websocket: WebSocket, manager: SessionManager):
    """安全地执行 shell 命令（保持状态）"""
    try:
        # 获取或创建该连接的shell会话
        if websocket not in manager.shell_sessions:
            manager.shell_sessions[websocket] = {
                "cwd": os.getcwd(),
                "env": os.environ.copy()
            }
        
        shell_state = manager.shell_sessions[websocket]
        
        # 解析命令
        try:
            cmd_parts = shlex.split(command)
        except ValueError as e:
            await websocket.send_json({
                "type": "shell_error",
                "error": f"命令解析错误: {str(e)}"
            })
            return
            
        if not cmd_parts:
            return
            
        # 获取基础命令
        base_cmd = cmd_parts[0]
        
        # 检查是否是危险命令
        if base_cmd in DANGEROUS_COMMANDS:
            await websocket.send_json({
                "type": "shell_error",
                "error": f"安全限制: 命令 '{base_cmd}' 已被禁用"
            })
            return
            
        # 对于不在白名单中的命令，给出警告但仍然执行
        if base_cmd not in SAFE_COMMANDS:
            logger.warning(f"执行非白名单命令: {base_cmd}")
        
        # 处理cd命令
        if base_cmd == "cd":
            try:
                if len(cmd_parts) == 1:
                    # cd without args goes to home
                    new_dir = os.path.expanduser("~")
                else:
                    new_dir = os.path.expanduser(cmd_parts[1])
                
                # 处理相对路径
                if not os.path.isabs(new_dir):
                    new_dir = os.path.join(shell_state["cwd"], new_dir)
                
                new_dir = os.path.normpath(new_dir)
                
                if os.path.isdir(new_dir):
                    shell_state["cwd"] = new_dir
                    await websocket.send_json({
                        "type": "shell_output",
                        "output": f"Changed directory to: {new_dir}\n"
                    })
                else:
                    await websocket.send_json({
                        "type": "shell_error",
                        "error": f"cd: no such file or directory: {cmd_parts[1]}\n"
                    })
            except Exception as e:
                await websocket.send_json({
                    "type": "shell_error",
                    "error": f"cd: {str(e)}\n"
                })
            return
        
        # 处理pwd命令
        if base_cmd == "pwd":
            await websocket.send_json({
                "type": "shell_output",
                "output": f"{shell_state['cwd']}\n"
            })
            return
        
        # 创建进程（使用保存的工作目录）
        logger.info(f"执行命令: {command} 在目录: {shell_state['cwd']}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=shell_state["cwd"],
            env=shell_state["env"]
        )
        
        # 设置超时时间（30秒）
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
            
            # 发送标准输出
            if stdout:
                output = stdout.decode('utf-8', errors='replace')
                logger.info(f"命令输出: {len(output)} 字符")
                await websocket.send_json({
                    "type": "shell_output",
                    "output": output
                })
            
            # 发送错误输出
            if stderr:
                error = stderr.decode('utf-8', errors='replace')
                logger.warning(f"命令错误: {error}")
                await websocket.send_json({
                    "type": "shell_error",
                    "error": error
                })
                
            # 如果没有输出
            if not stdout and not stderr:
                logger.info("命令执行完成，无输出")
                await websocket.send_json({
                    "type": "shell_output",
                    "output": "命令执行完成（无输出）\n"
                })
                
        except asyncio.TimeoutError:
            # 超时，终止进程
            process.terminate()
            await process.wait()
            await websocket.send_json({
                "type": "shell_error",
                "error": "命令执行超时（30秒）"
            })
            
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        await websocket.send_json({
            "type": "shell_error",
            "error": f"执行命令失败: {str(e)}"
        })

if __name__ == "__main__":
    print("🚀 启动 NexusAgent WebSocket 服务器...")
    print("📡 使用 Session 模式运行 rootagent")
    print("🌐 WebSocket 端点: ws://localhost:8000/ws")
    uvicorn.run(app, host="0.0.0.0", port=8000)