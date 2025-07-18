# NexusAgent-SR

> 🔬 **基于Google ADK的符号回归智能代理系统**  
> 自动将原始数据转换为可解释的数学模型

[![License: MulanPSL-2.0](https://img.shields.io/badge/License-MulanPSL--2.0-blue.svg)](http://license.coscl.org.cn/MulanPSL2)
[![Python 3.11+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ 系统特性

- 🤖 **多智能代理协同** - 基于Google ADK框架的智能代理编排系统
- 📊 **自动数据分析** - 生成详细的数据特征描述和背景研究
- 🔍 **深度文献调研** - 基于AI的领域知识提取
- ⚡ **高效符号回归** - 基于PySR的高性能符号回归
- 📝 **智能报告生成** - 自动生成科学研究报告并迭代优化

## 🚀 快速开始

### 环境配置

1. **安装依赖**
```bash
pip install -r requirements.txt

cd nexus-ui
npm install >/dev/null 2>&1

```

2. **配置环境变量**
在项目DPA_subagent内创建 `.env` 文件：
```bash
# 模型配置
DEEPRESEARCH_MODEL=
DEEPRESEARCH_ENDPOINT=
DEEPRESEARCH_API_KEY=
TAVILY_API_KEY=
SEARCH_TOOL=tavily


#agent_model
MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=

```


系统启动后，可通过Web界面与NexusAgent进行交互。

## 💻 用户界面 (UI)

NexusAgent-SR 提供了现代化的 Web 用户界面，让您可以更直观地与系统交互。

### UI 特性

- 🎨 **现代化设计** - 基于 React + TailwindCSS 的响应式界面
- 💬 **实时对话** - WebSocket 支持的实时消息通信
- 📁 **文件管理** - 直接在界面中查看输出文件和结果
- 🔄 **任务状态** - 实时显示工具执行和任务进度
- 🌓 **深色模式** - 支持明暗主题切换

### 启动 UI

```bash
# 使用启动脚本

./start-nexus.sh

```

访问 http://localhost:5173 即可使用界面。

### UI 架构

- **前端**: React + TypeScript + Vite
- **后端**: FastAPI + WebSocket
- **通信**: 实时双向 WebSocket 连接

更多 UI 扩展信息请参考 [UI 扩展指南](docs/UI_EXTENSION_GUIDE.md)。

## 🏗️ 核心架构

### 智能代理编排 (`agent.py`)

系统由以下智能代理组成：

```
root_agent (NexusAgent)
├── research_agent     # 数据分析与描述生成
└── sr_iteration_agent # 符号回归迭代流程
    ├── prior_agent    # 先验知识配置
    ├── symbolic_agent # 符号回归执行
    └── summarize_agent # 结果总结生成
```

**主要代理功能：**
- **ResearchAgent**: 生成数据特征描述
- **PriorAgent**: 设置算子和映射配置
- **SymbolicAgent**: 执行符号回归算法
- **SummarizeAgent**: 生成科学研究报告

### 工具集合 (`tool/`)

| 工具模块 | 主要功能 | 说明 |
|---------|---------|------|
| `pysr.py` | 标准符号回归 | 基于PySR的多变量符号回归 |
| `deepresearch.py` | 深度研究 | AI驱动的文献调研和知识提取 |
| `summarize_report.py` | 报告生成 | 自动生成科学研究报告 |
| `iteration_manager.py` | 迭代管理 | 管理多轮实验的历史记录 |
| `task_manager.py` | 任务管理 | 异步任务状态跟踪 |
| `utils.py` | 工具函数 | 数据处理和表达式简化 |

## 📊 使用方式

### 1. Web界面交互

启动 `adk web` 后，在Web界面中输入任务描述：

```
I am working on a standard symbolic regression task. The dataset describes a biophysical neuronal dynamic system, in which: • x₁ represents the membrane potential, • x₂ is a fast activation variable (e.g., associated with fast ion channels), • x₃ is a slow adaptation variable (e.g., representing slow potassium or calcium currents). The objective is to infer the form of the differential equation governing the change in membrane potential, i.e.,   y = dx₁/dt as a function of x₁, x₂, and x₃. It is assumed that the system does not involve magnetic flux modulation.csv path is data/hr_example.csv

```




## 📋 输出结果

- **📊 最优表达式**: 发现的数学方程
- **📈 复杂度分析**: 模型复杂度和精度评估  
- **📝 科学报告**: 包含背景、方法、结果的完整报告
- **🔍 研究文献**: 相关领域的文献调研结果
- **📁 结果文件**: 
  - `output/summarize_report.md` - 总结报告
  - `results.json` - 完整的符号回归结果
  - `best.txt` - 最优表达式

## 🛠️ 开发说明

### 目录结构
```
NexusAgent/
├── DPA_subagent/           # 核心代理模块
│   ├── agent.py            # 主代理编排（已弃用）
│   ├── subagent.py         # 新的代理实现
│   ├── prompt/             # 提示词模板
│   ├── tool/               # 工具集合
│   └── .env                # 环境配置
├── nexus-ui/               # 前端界面
│   ├── src/                # React 源代码
│   │   ├── components/     # UI 组件
│   │   └── styles/         # 样式文件
│   └── package.json        # 前端依赖
├── data/                   # 示例数据
├── output/                 # 输出结果
├── docs/                   # 文档
│   └── UI_EXTENSION_GUIDE.md # UI 扩展指南
├── nexus-websocket-server.py # WebSocket 服务器
└── start-nexus.sh          # 启动脚本

```

### 扩展开发
- 添加新的符号回归算法: 扩展 `tool/pysr*.py`
- 集成新的AI模型: 修改 `subagent.py` 中的模型配置
- 自定义提示词: 编辑 `prompt/agent_prompt.py`
- 新增工具函数: 在 `tool/agent_tool.py` 中注册
- 扩展 UI 功能: 参考 [UI 扩展指南](docs/UI_EXTENSION_GUIDE.md)
- 添加新的 WebSocket 消息类型: 修改 `nexus-websocket-server.py`

## 🔧 故障排除

### 常见问题

1. **WebSocket 连接失败**
   - 确保后端服务器在 8000 端口运行
   - 检查防火墙设置

2. **前端无法加载**
   - 确保已安装 Node.js 和 npm
   - 运行 `npm install` 安装依赖

3. **代理执行超时**
   - 检查 API 密钥配置
   - 确认网络代理设置正确

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。

