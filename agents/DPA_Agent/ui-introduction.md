# Agent 前端实现介绍

## 1. Agent 定义

### 1.1 什么是 Agent
Agent 是一个基于 Google ADK（Agent Development Kit）构建的智能符号回归系统。它通过多智能体协作，自动将原始数据转换为可解释的数学模型。

### 1.2 Agent 架构
系统采用分层的智能体架构：

```

```

每个智能体都有明确的职责：
- **ResearchAgent**: 分析输入数据，生成特征描述
- **PriorAgent**: 根据数据特征配置合适的数学算子
- **SymbolicAgent**: 执行 Py 符号回归算法
- **SummarizeAgent**: 生成科学报告

### 1.3 Agent 配置
通过 `config/agent-config.json` 文件可以灵活配置不同的 Agent 实现：

```json
{
  "agent": {
    "name": "agent",
    "module": "agent",
    "rootAgent": "root_agent"
  }
}
```

## 2. 后端架构

### 2.1 WebSocket 服务器
后端基于 FastAPI 框架，提供 WebSocket 实时通信能力：

- **文件**: `-websocket-server.py`
- **端口**: 8000
- **主要功能**:
  - WebSocket 连接管理
  - 会话（Session）管理
  - 消息路由和处理
  - 文件系统访问 API
  - Shell 命令执行（安全限制）

### 2.2 核心组件

#### SessionManager
管理所有客户端连接和会话：
```python
class SessionManager:
    - active_connections: 活跃的 WebSocket 连接
    - sessions: 所有会话数据
    - runners: 每个会话的 ADK Runner 实例
    - session_services: 会话持久化服务
```

#### Runner 集成
每个会话都有独立的 Runner 实例，用于执行 Agent 任务：
```python
runner = Runner(
    agent=rootagent,
    session_service=session_service,
    app_name=self.app_name
)
```

## 3. 前端与后端连接

### 3.1 WebSocket 通信协议
前端通过 WebSocket 与后端建立双向通信连接：

```typescript
// 前端连接代码 (ChatInterface.tsx)
const websocket = new WebSocket('ws://localhost:8000/ws')
```

### 3.2 消息类型
系统定义了多种消息类型用于不同的交互场景：

#### 用户消息
```json
{
  "type": "message",
  "content": "用户输入的内容"
}
```

#### 会话管理
```json
{
  "type": "create_session" | "switch_session" | "delete_session",
  "session_id": "会话ID"
}
```

#### 工具执行状态
```json
{
  "type": "tool",
  "tool_name": "工具名称",
  "status": "executing" | "completed",
  "is_long_running": true/false,
  "result": "执行结果"
}
```

#### Shell 命令
```json
{
  "type": "shell_command",
  "command": "要执行的命令"
}
```

### 3.3 实时状态同步
- **连接状态**: 实时显示 WebSocket 连接状态（已连接/连接中/未连接）
- **工具执行**: 实时展示长时间运行的工具状态
- **会话切换**: 支持多会话并行，历史记录独立保存

## 4. 前端功能实现

### 4.1 技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **UI 组件**: 
  - Framer Motion（动画）
  - Lucide React（图标）
  - React Markdown（Markdown 渲染）
  - React Syntax Highlighter（代码高亮）

### 4.2 核心功能

#### 聊天界面
- **组件**: `ChatInterface.tsx`
- **功能**:
  - 实时消息收发
  - Markdown 格式支持
  - 代码语法高亮
  - 工具执行状态展示
  - 消息历史记录

#### 会话管理
- **组件**: `SessionList.tsx`
- **功能**:
  - 创建新会话
  - 切换会话
  - 删除会话
  - 会话标题自动生成

#### 文件浏览器
- **组件**: `FileExplorer.tsx`
- **功能**:
  - 浏览输出目录文件树
  - 预览文件内容
  - 支持多种文件格式（JSON、Markdown、CSV 等）
  - 文件内容语法高亮

#### Shell 终端
- **组件**: `ShellTerminal.tsx`
- **功能**:
  - 执行 Shell 命令
  - 命令历史记录
  - 输出实时展示
  - 安全限制（危险命令黑名单）

#### 可调整面板
- **组件**: `ResizablePanel.tsx`
- **功能**:
  - 支持拖拽调整面板大小
  - 最小/最大尺寸限制
  - 流畅的调整动画

### 4.3 配置系统
通过 `useAgentConfig` Hook 加载后端配置：
```typescript
const { config, loading } = useAgentConfig()
// 配置包含：agent 信息、UI 设置、文件路径等
```

### 4.4 用户体验优化
- **加载状态**: 思考中的动画提示
- **错误处理**: 友好的错误信息展示
- **自动滚动**: 新消息自动滚动到底部
- **响应式设计**: 适配不同屏幕尺寸
- **暗色模式**: 支持明暗主题切换

## 5. 可迁移性

### 5.1 架构解耦
系统采用了高度解耦的架构设计：

#### Agent 层可替换
通过修改 `agent-config.json`，可以轻松切换不同的 Agent 实现：
```json
{
  "agent": {
    "module": "your_agentmodule",
    "rootAgent": "your_root_agent"
  }
}
```

#### 前后端分离
- 前端完全独立，通过 WebSocket 协议通信
- 后端提供标准化的 WebSocket 消息接口
- 文件访问通过 RESTful API

### 5.2 扩展性
#### 添加新的 Agent
1. 在新模块中定义 Agent
2. 更新 `agent-config.json` 配置
3. 无需修改前端或 WebSocket 服务器

#### 添加新的前端功能
1. 创建新的 React 组件
2. 定义新的消息类型
3. 在 WebSocket 服务器中添加消息处理逻辑

#### 自定义 UI 主题
通过 TailwindCSS 配置文件自定义样式主题

### 5.3 部署灵活性
- **前端**: 可独立部署为静态网站
- **后端**: 支持 Docker 容器化部署
- **配置**: 通过环境变量和配置文件管理

### 5.4 技术栈通用性
- 使用行业标准技术（React、WebSocket、FastAPI）
- 遵循 RESTful 和 WebSocket 标准协议
- 代码结构清晰，易于理解和维护

## 总结

Agent 前端实现了一个现代化的 AI Agent 交互界面，通过 WebSocket 实现了与后端 Agent 的实时通信。系统架构解耦、功能完善、易于扩展，为智能符号回归任务提供了直观、高效的用户界面。