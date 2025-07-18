#!/bin/bash

echo "🚀 启动 NexusAgent 系统..."

# 清理现有进程
echo "清理现有进程..."
pkill -f "nexus-websocket-server.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 1

# 创建输出目录
mkdir -p output

# 启动 WebSocket 服务器（集成了 Agent）
echo "启动 NexusAgent WebSocket 服务器..."
python nexus-websocket-server.py > websocket.log 2>&1 &
WEBSOCKET_PID=$!

# 启动前端
echo "启动前端..."
cd nexus-ui
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ NexusAgent 系统已启动!"
echo "WebSocket 服务器: http://localhost:8000 (PID: $WEBSOCKET_PID)"
echo "前端界面: http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "日志文件："
echo "- 服务器日志: websocket.log"
echo "- 前端日志: frontend.log"
echo "使用方法："
echo "在浏览器中打开 http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 捕获 Ctrl+C
trap "echo '停止所有服务...'; kill $WEBSOCKET_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
wait