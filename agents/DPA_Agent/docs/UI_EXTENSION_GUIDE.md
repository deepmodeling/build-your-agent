# NexusAgent UI 扩展指南

本指南介绍如何扩展 NexusAgent 的前端界面和后端功能。

## 目录

1. [架构概述](#架构概述)
2. [前端扩展](#前端扩展)
3. [后端扩展](#后端扩展)
4. [WebSocket 通信协议](#websocket-通信协议)
5. [开发工作流](#开发工作流)

## 架构概述

NexusAgent UI 采用前后端分离架构：

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   前端 (React)   │ ←───────────────→ │  后端 (FastAPI)  │
│   localhost:5173 │                   │  localhost:8000  │
└─────────────────┘                    └─────────────────┘
         ↓                                      ↓
    Vite + React                          Google ADK + Agent
```

### 技术栈

**前端：**
- React 18 + TypeScript
- Vite 构建工具
- TailwindCSS 样式框架
- Framer Motion 动画库
- React Markdown 渲染
- Axios HTTP 客户端

**后端：**
- FastAPI Web 框架
- WebSocket 实时通信
- Google ADK Agent 框架
- 异步任务处理

## 前端扩展

### 1. 添加新组件

在 `nexus-ui/src/components/` 创建新组件：

```tsx
// nexus-ui/src/components/MyNewComponent.tsx
import React from 'react'
import { motion } from 'framer-motion'

interface MyNewComponentProps {
  data: any
  onAction: (action: string) => void
}

export const MyNewComponent: React.FC<MyNewComponentProps> = ({ data, onAction }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm"
    >
      {/* 组件内容 */}
    </motion.div>
  )
}
```

### 2. 扩展消息类型

修改 `ChatInterface.tsx` 中的消息处理：

```tsx
// 1. 定义新的消息类型
interface CustomMessage extends Message {
  type: 'custom'
  customData: any
}

// 2. 在 handleWebSocketMessage 中添加处理
if (type === 'custom') {
  const customMessage: CustomMessage = {
    id: `custom_${Date.now()}`,
    role: 'assistant',
    content: content,
    customData: data.customData,
    timestamp: new Date()
  }
  setMessages(prev => [...prev, customMessage])
  return
}

// 3. 在渲染部分添加自定义渲染
{message.type === 'custom' && (
  <MyNewComponent data={message.customData} />
)}
```

### 3. 添加新页面

创建新路由页面：

```tsx
// nexus-ui/src/pages/Analysis.tsx
import React from 'react'
import { useWebSocket } from '../hooks/useWebSocket'

export const Analysis: React.FC = () => {
  const { sendMessage, messages } = useWebSocket()
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">数据分析</h1>
      {/* 页面内容 */}
    </div>
  )
}

// 在 App.tsx 中添加路由
<Route path="/analysis" element={<Analysis />} />
```

### 4. 自定义 Hook

创建可复用的 Hook：

```tsx
// nexus-ui/src/hooks/useFileUpload.ts
import { useState, useCallback } from 'react'
import axios from 'axios'

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  
  const uploadFile = useCallback(async (file: File) => {
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await axios.post('/api/upload', formData, {
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded * 100) / e.total!))
        }
      })
      return response.data
    } finally {
      setUploading(false)
    }
  }, [])
  
  return { uploadFile, uploading, progress }
}
```

### 5. 主题定制

修改 `tailwind.config.js` 添加自定义主题：

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        'nexus': {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    }
  }
}
```

## 后端扩展

### 1. 添加新的 API 端点

在 `nexus-websocket-server.py` 中添加：

```python
@app.post("/api/analyze")
async def analyze_data(file: UploadFile = File(...)):
    """分析上传的数据文件"""
    contents = await file.read()
    
    # 调用 Agent 分析
    result = await manager.runner.analyze(contents)
    
    return JSONResponse(content={
        "status": "success",
        "result": result
    })

@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    status = await manager.get_task_status(task_id)
    return JSONResponse(content=status)
```

### 2. 扩展 WebSocket 消息类型

在 `AgentManager` 类中添加新的消息处理：

```python
async def process_message(self, message: str, websocket: WebSocket):
    # 解析消息类型
    try:
        msg_data = json.loads(message)
        msg_type = msg_data.get('type', 'text')
        
        if msg_type == 'file_analysis':
            # 处理文件分析请求
            file_path = msg_data.get('file_path')
            await self.handle_file_analysis(file_path, websocket)
            
        elif msg_type == 'config_update':
            # 更新配置
            config = msg_data.get('config')
            await self.update_config(config, websocket)
            
        else:
            # 默认文本消息处理
            await self.handle_text_message(message, websocket)
            
    except json.JSONDecodeError:
        # 作为普通文本处理
        await self.handle_text_message(message, websocket)
```

### 3. 集成新的 Agent 功能

扩展 Agent 调用：

```python
from DPA_subagent.custom_agent import CustomAnalysisAgent

class ExtendedAgentManager(AgentManager):
    def __init__(self):
        super().__init__()
        self.custom_agent = CustomAnalysisAgent()
    
    async def handle_custom_analysis(self, data: dict, websocket: WebSocket):
        """处理自定义分析"""
        # 发送开始状态
        await self.broadcast({
            "type": "analysis_start",
            "message": "开始自定义分析..."
        })
        
        # 执行分析
        result = await self.custom_agent.analyze(data)
        
        # 发送结果
        await self.broadcast({
            "type": "analysis_result",
            "result": result
        })
```


## WebSocket 通信协议

### 消息格式

所有 WebSocket 消息采用 JSON 格式：

```typescript
// 前端发送
interface ClientMessage {
  type: 'message' | 'file_analysis' | 'config_update'
  content?: string
  data?: any
}

// 后端响应
interface ServerMessage {
  type: 'user' | 'assistant' | 'tool' | 'system' | 'error' | 'complete'
  content: string
  timestamp?: string
  data?: any
}
```

### 消息流程

1. **连接建立**
   ```
   Client → Server: WebSocket 连接
   Server → Client: {"type": "system", "content": "已连接"}
   ```

2. **普通对话**
   ```
   Client → Server: {"type": "message", "content": "分析数据"}
   Server → Client: {"type": "tool", "tool_name": "pysr", "status": "executing"}
   Server → Client: {"type": "assistant", "content": "分析结果..."}
   Server → Client: {"type": "complete"}
   ```

3. **文件处理**
   ```
   Client → Server: {"type": "file_analysis", "file_path": "data.csv"}
   Server → Client: {"type": "tool", "tool_name": "file_reader", "status": "executing"}
   Server → Client: {"type": "analysis_result", "data": {...}}
   ```



## 最佳实践

1. **组件设计**
   - 保持组件小而专注
   - 使用 TypeScript 类型定义
   - 实现错误边界处理

2. **状态管理**
   - 对于简单状态使用 useState
   - 复杂状态考虑使用 useReducer
   - 全局状态可考虑 Context API

3. **性能优化**
   - 使用 React.memo 避免不必要的重渲染
   - 对大列表使用虚拟滚动
   - 图片懒加载

4. **安全考虑**
   - 验证所有用户输入
   - 使用 HTTPS 部署
   - 实现认证和授权

5. **错误处理**
   - 全局错误边界
   - WebSocket 重连机制
   - 用户友好的错误提示

## 示例：添加数据可视化功能

### 1. 安装依赖

```bash
cd nexus-ui
npm install recharts
```

### 2. 创建图表组件

```tsx
// nexus-ui/src/components/DataChart.tsx
import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

export const DataChart: React.FC<{ data: any[] }> = ({ data }) => {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  )
}
```

### 3. 后端支持

```python
@app.get("/api/chart-data")
async def get_chart_data():
    # 从分析结果生成图表数据
    data = [
        {"name": "Point 1", "value": 10},
        {"name": "Point 2", "value": 20},
        # ...
    ]
    return JSONResponse(content=data)
```

### 4. 集成到界面

```tsx
// 在 ChatInterface 中使用
import { DataChart } from './DataChart'

// 在消息渲染中
{message.type === 'chart' && (
  <DataChart data={message.chartData} />
)}
```

通过遵循本指南，你可以轻松扩展 NexusAgent UI 的功能，添加新的可视化组件、交互功能和数据处理能力。