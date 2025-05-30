#!/bin/bash
# 简单的启动脚本，用于运行 PubChem MCP 服务器

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 Python 3 但未找到"
    exit 1
fi

# 运行服务器
echo "启动 PubChem MCP 服务器..."
cd "$SCRIPT_DIR/python_version"
python3 mcp_server.py

# 如果脚本运行到这里，说明服务器已经停止
echo "PubChem MCP 服务器已停止。"
