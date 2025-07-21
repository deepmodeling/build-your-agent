# Agent UI 

## 这是什么？

Agent UI 是一个通用的 Web 界面框架，目前开放为 Google ADK Agent 提供即插即用的用户界面。

**核心特点：**
- 提供完整的聊天界面、文件管理、会话管理功能
- 通过配置文件即可接入任何 ADK Agent
- 无需修改前端代码

## 系统架构

```
采用前后端分离架构：

┌─────────────────┐     WebSocket      ┌─────────────────┐
│   前端 (React)   │ ←───────────────→ │  后端 (FastAPI)  │
│   localhost:5173 │                   │  localhost:8000  │
└─────────────────┘                    └─────────────────┘
         ↓                                      ↓
    Vite + React                          Google ADK + Agent

```

## 如何使用

### 前提条件
- Python 3.10+
- Node.js 16+
- 一个基于 Google ADK 开发的 Agent

### 安装步骤

1. **安装依赖**
   ```bash
   # Python 依赖
   pip install -r requirements.txt
   
   # 前端依赖
   cd ui
   npm install
   cd ..
   ```

2. **配置你的 Agent**
   
   编辑 `config/agent-config.json`：
   ```json
   {
     "agent": {
       "module": "your_module_name",    # 你的 Python 模块名
       "rootAgent": "your_agent_var"    # Agent 导出的变量名
     }
   }
   ```

3. **配置 API Key**
   
   创建 `agent/.env` 文件：
   ```
   
   DEEPSEEK_API_KEY=your_api_key
   # 或者使用其他模型
   ```

4. **启动系统**
   ```bash
   ./start-agent.sh
   ```

5. **访问界面**
   
   打开浏览器访问 http://localhost:5173

### 示例：替换为你的 Agent

假设你有一个 Agent 文件 `agent/my_agent.py`：

```python
# my_agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

my_assistant = Agent(
    name="my_assistant",
    model=LiteLlm(model="deepseek/deepseek-chat"),
    instruction="你是一个助手",
    tools=[]
)
```

只需修改配置：
```json
{
  "agent": {
    "module": "agent.my_agent",
    "rootAgent": "my_assistant"
  }
}
```

## 目录结构

```
.
├── agent/                  # Agent 模块目录
│   ├── agent.py           # 默认 Agent 实现
│   └── .env               # 环境变量配置
├── config/                # 配置目录
│   ├── agent-config.json  # Agent 配置
│   └── agent_config.py    # 配置加载器
├── ui/                    # 前端代码
│   ├── src/              # React 源码
│   └── package.json      # 前端依赖
├── websocket-server.py    # WebSocket 服务器
├── requirements.txt       # Python 依赖
└── start-agent.sh        # 启动脚本
```

## 功能列表

- ✅ 实时聊天界面
- ✅ Markdown 消息渲染
- ✅ 代码语法高亮
- ✅ 工具执行状态显示
- ✅ 多会话管理
- ✅ 文件浏览器
- ✅ Shell 终端
- ✅ 可调整面板布局

## 常见问题

1. **端口被占用**
   - 修改 `websocket-server.py` 中的端口号
   - 修改 `ui/vite.config.ts` 中的代理配置

2. **Agent 加载失败**
   - 确保模块路径正确
   - 确保 Agent 变量名正确
   - 检查 Python 导入路径

3. **API 认证失败**
   - 检查 `.env` 文件中的 API Key
   - 确保 API Key 有效

## 下一步

- 查看 [CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md) 了解详细配置
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始
