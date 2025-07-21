# 🚀 5分钟快速开始

## 第一步：准备你的 Agent

确保你的 Agent 基于 Google ADK 开发，并导出为一个变量（如 `root_agent`）。

```python
# your_agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    name="my_agent",
    model=LiteLlm(model="your-model"),
    instruction="你的 Agent 指令",
    tools=[...] 
)
```

## 第二步：配置文件

编辑 `config/agent-config.json`：

```json
{
  "agent": {
    "name": "我的智能助手",
    "description": "一句话描述",
    "welcomeMessage": "欢迎使用！",
    "module": "your_agent",        // 你的模块名
    "rootAgent": "root_agent"       // 导出的变量名
  }
}
```

## 第三步：启动系统

```bash
# 安装依赖
pip install -r requirements.txt
cd ui && npm install
cd ..

# 启动
./start-agent.sh
```

打开浏览器访问 http://localhost:5173

## 🎨 可选：自定义 UI

### 修改主题颜色
编辑 `config/agent-config.json`：
```json
"ui": {
  "theme": {
    "primaryColor": "blue",
    "secondaryColor": "purple"
  }
}
```

### 隐藏不需要的功能
```json
"features": {
  "showFileExplorer": false,  // 隐藏文件浏览器
  "showSessionList": false    // 隐藏会话列表
}
```

## 📝 常见问题

### API Key 配置
在 `agent/.env` 文件中配置：
```
MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=your_api_key
```

### 端口冲突
修改 `websocket-server.py` 中的端口：
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为其他端口
```

## 🎯 最佳实践

1. **保持 Agent 简单** - UI 会自动处理复杂的交互
2. **使用标准工具格式** - 工具执行状态会自动显示
3. **返回 Markdown** - UI 会自动渲染格式
