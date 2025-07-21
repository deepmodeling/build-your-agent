# 配置说明

## server 配置

在 `agent-config.json` 中的 `server` 部分用于配置前端开发服务器和访问控制：

```json
"server": {
  "port": 50002,
  "allowedHosts": ["cofg1321640.bohrium.tech"]
}
```

### 配置项说明

- **port**: 前端开发服务器端口（默认：50002）
- **allowedHosts**: 额外允许访问的主机列表

### 默认允许的主机

以下主机始终被允许访问，无需在配置中声明：
- `localhost`
- `127.0.0.1`
- `0.0.0.0`

### 使用示例

如果你需要允许额外的主机访问（例如远程服务器域名），只需在 `allowedHosts` 中添加：

```json
"server": {
  "port": 50002,
  "allowedHosts": [
    "example.com",
    "myserver.local",
    "192.168.1.100"
  ]
}
```

这些配置会同时应用于：
1. Vite 开发服务器的 `allowedHosts` 配置
2. WebSocket 服务器的 CORS 配置和 Host 验证