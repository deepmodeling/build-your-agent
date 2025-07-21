# 配置指南

本文档详细说明 Agent UI Kit 的所有配置选项。

## 配置文件位置

主配置文件：`config/agent-config.json`

## 配置项详解

### 1. Agent 配置

```json
{
  "agent": {
    "name": "显示名称",
    "description": "描述信息",
    "welcomeMessage": "欢迎消息",
    "module": "Python模块路径",
    "rootAgent": "Agent变量名"
  }
}
```

**字段说明：**
- `name`: 在 UI 中显示的 Agent 名称
- `description`: Agent 的简短描述
- `welcomeMessage`: 用户首次进入时的欢迎消息
- `module`: Python 模块的导入路径（如 `agent.agent` 或 `my_module.sub_module`）
- `rootAgent`: 模块中导出的 Agent 变量名

**示例：**
```json
{
  "agent": {
    "name": "代码助手",
    "description": "帮助编写和调试代码",
    "welcomeMessage": "你好！我可以帮你编写代码。",
    "module": "agents.code_assistant",
    "rootAgent": "assistant"
  }
}
```

### 2. UI 配置

```json
{
  "ui": {
    "title": "浏览器标题",
    "theme": {
      "primaryColor": "主色调",
      "secondaryColor": "辅助色"
    },
    "features": {
      "showFileExplorer": true,
      "showSessionList": true,
      "enableFileUpload": false
    }
  }
}
```

**功能开关：**
- `showFileExplorer`: 是否显示文件浏览器面板
- `showSessionList`: 是否显示会话列表
- `enableFileUpload`: 是否启用文件上传功能（开发中）

### 3. 文件管理配置

```json
{
  "files": {
    "outputDirectory": "output",
    "watchDirectories": ["output", "results"],
    "fileExtensions": {
      "supported": ["json", "md", "txt", "csv", "py", "js", "ts", "log"],
      "defaultViewer": {
        "json": "code",
        "md": "markdown",
        "csv": "table",
        "default": "code"
      }
    }
  }
}
```

**说明：**
- `outputDirectory`: 默认输出目录
- `watchDirectories`: 文件浏览器监视的目录列表
- `supported`: 支持预览的文件扩展名
- `defaultViewer`: 不同文件类型的默认查看器

### 4. WebSocket 配置

```json
{
  "websocket": {
    "host": "localhost",
    "port": 8000,
    "reconnectInterval": 3000,
    "maxReconnectAttempts": 10
  }
}
```

**参数说明：**
- `reconnectInterval`: 断线重连间隔（毫秒）
- `maxReconnectAttempts`: 最大重连次数

### 5. 会话配置

```json
{
  "session": {
    "persistent": false,
    "maxSessions": 50,
    "defaultSessionTitle": "新对话"
  }
}
```



**用途：**
- `displayNames`: 将工具内部名称映射为用户友好的显示名称
- `longRunningTools`: 标记为长时间运行的工具，UI 会显示特殊状态

## 环境变量配置

### Agent 环境变量

在 `agent/.env` 文件中配置：

```bash
# 模型选择
MODEL=deepseek/deepseek-chat

# API Keys
DEEPSEEK_API_KEY=your_key_here

```


## 配置加载顺序

1. 默认配置（代码中的默认值）
2. 配置文件（agent-config.json）
3. 环境变量（最高优先级）

## 配置验证

系统启动时会自动验证配置：
- 检查必需字段是否存在
- 验证模块是否可以导入
- 确认 Agent 变量是否存在

## 动态配置

配置通过 API 端点暴露给前端：
```
GET /api/config
```

前端通过 `useAgentConfig` Hook 获取配置：
```typescript
const { config, loading, error } = useAgentConfig()
```

## 最佳实践

1. **保持配置简洁** - 只修改需要的部分
2. **使用环境变量管理密钥** - 不要在配置文件中硬编码
3. **测试配置** - 修改后总是重启并测试
4. **版本控制** - 将配置文件纳入版本控制（除了 .env）

## 故障排除

### 配置未生效
1. 确保保存了配置文件
2. 重启 WebSocket 服务器
3. 清除浏览器缓存

### Agent 加载失败
1. 检查模块路径拼写
2. 确保 Python 可以导入该模块
3. 验证变量名是否正确

### UI 功能异常
1. 检查 features 配置
2. 确保布尔值格式正确（true/false）
3. 查看浏览器控制台错误