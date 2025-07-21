# RJ AI Toolkit

🚀 **RJ的企业级AI工具包集合** - 包含Agent、RAG、Redis等多种AI开发工具

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Package Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/Wang-Theo/rj-ai-toolkit)

## ✨ 工具包特性

### 🤖 Agent Toolkit
- **智能Agent**: 基于LangChain框架的企业级智能对话代理
- **千问模型**: 深度集成阿里云千问大模型API
- **丰富工具**: 内置计算器、文本分析、情感分析等多种工具
- **易扩展**: 简单的接口设计，方便添加自定义工具
- **记忆功能**: 支持对话历史记忆和上下文管理
- **完整日志**: 详细的执行日志和错误处理

## 📦 安装

### 从 GitHub 安装（推荐）
```bash
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

### 从源码安装
```bash
git clone https://github.com/Wang-Theo/rj-ai-toolkit.git
cd rj-ai-toolkit
pip install -e .
```

## 🚀 快速开始

### 1. 环境配置
- **qwen api key**
```bash
# Windows
set DASHSCOPE_API_KEY=your_api_key_here

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key_here
```

### 2. 基本使用
```python
from agent_toolkit import EnterpriseAgent, Config
from agent_toolkit.tools import create_calculator_tool, create_text_analyzer_tool

# 创建配置
config = Config()

# 创建Agent
agent = EnterpriseAgent(config)

# 添加工具
agent.add_tool(create_calculator_tool())
agent.add_tool(create_text_analyzer_tool())

# 构建Agent
agent.build_agent()

# 运行查询
result = agent.run("请帮我计算 (25 + 35) * 2 的结果")
print(result["output"])
```

### 3. 高级配置
```python
from agent_toolkit import Config, EnterpriseAgent
from agent_toolkit.tools import *

# 自定义配置
config = Config(
    LLM_MODEL="qwen-plus",      # 指定模型
    LLM_TEMPERATURE=0.3,        # 调整创造性
    MAX_ITERATIONS=5,           # 限制迭代次数
    MAX_TOKENS=4000            # 控制响应长度
)

agent = EnterpriseAgent(config)

# 批量添加工具
agent.add_tools([
    create_calculator_tool(),
    create_text_analyzer_tool(),
    create_text_sentiment_tool()        # 情感分析
])

agent.build_agent()
```

### 4. 行为配置
```python
# 生产环境 - 静默模式
production_config = Config(
    VERBOSE=False,                      # 不显示执行过程
    RETURN_INTERMEDIATE_STEPS=False,    # 不返回中间步骤
    MAX_ITERATIONS=3                    # 快速响应
)

# 开发环境 - 调试模式  
debug_config = Config(
    VERBOSE=True,                       # 显示详细过程
    RETURN_INTERMEDIATE_STEPS=True,     # 返回所有步骤
    MAX_ITERATIONS=15                   # 允许复杂推理
)
```

## 🛠️ 内置工具

### 计算器工具
支持基本数学运算：加减乘除、括号

```python
result = agent.run("计算 (10 + 20) * 3")
```

### 文本分析工具
分析文本的统计信息和情感

```python
result = agent.run("分析这段文本：人工智能正在改变世界")
```

## 🔧 自定义工具

创建自定义工具非常简单：

```python
from langchain_core.tools import Tool

def create_my_tool():
    def my_function(input_text: str) -> str:
        return f"处理结果: {input_text.upper()}"
    
    return Tool(
        name="my_tool",
        description="将文本转换为大写",
        func=my_function
    )

# 使用自定义工具
agent.add_tool(create_my_tool())
```

## 🎨 自定义Agent模板

Agent支持自定义提示模板，让您可以定制Agent的行为和回答风格：

### 默认模板
Agent使用标准的ReAct（Reasoning + Acting）模板，包含思考、行动、观察的循环。

### 自定义模板示例

```python
# 创建友好的客服风格模板
customer_service_template = """你是一个友好专业的AI助手。请根据以下工具帮助用户解决问题：

可用工具：
{tools}

请使用以下格式回答：

用户问题：{input}
思考：分析用户需求，选择合适的工具
行动：[选择工具名称: {tool_names}]
行动输入：工具的具体参数
观察：工具返回的结果
思考：基于结果进行进一步分析
最终回答：给用户的友好完整回答

开始对话：
{agent_scratchpad}"""

# 使用自定义模板构建Agent
agent.build_agent(custom_prompt=customer_service_template)
```

## 📊 使用示例

### 批量任务处理
```python
queries = [
    "计算 2^10 的值",
    "分析文本：AI技术发展迅速，带来新机遇",
    "生成一个16位密码"  # 需要添加密码工具
]

for query in queries:
    result = agent.run(query)
    print(f"查询: {query}")
    print(f"结果: {result['output']}\n")
```

### 复杂对话
```python
# Agent会记住对话历史
agent.run("我想计算一些数学题")
agent.run("帮我算 15 * 8")
agent.run("再加上 32")  # Agent会理解上下文
```

### 自定义模板应用
```python
# 创建专业的金融顾问Agent
financial_template = """我是专业金融顾问，将为您提供财务分析和建议：

可用分析工具：
{tools}

分析框架：
客户需求：{input}
风险评估：评估投资风险和收益
数据分析：使用工具 [{tool_names}] 进行计算
投资建议：{agent_scratchpad}
风险提示：重要的风险提醒
总结：简明扼要的建议总结

开始咨询："""

# 应用自定义模板
agent.build_agent(custom_prompt=financial_template)

# 测试专业对话
result = agent.run("我有10万元想投资，年化收益8%，10年后能有多少钱？")
print(result["output"])
```

### 运行示例
```bash
# 完整功能演示（包含基础使用、自定义工具、自定义模板、配置演示等）
python examples/agent_examples/complete_example.py
```

## 🔍 API 参考

### EnterpriseAgent

主要的 Agent 类，提供智能对话能力。

#### 方法
- `add_tool(tool)`: 添加单个工具
- `add_tools(tools)`: 批量添加工具  
- `remove_tool(name)`: 移除指定工具
- `list_tools()`: 获取工具列表
- `build_agent(custom_prompt=None)`: 构建Agent执行器，支持自定义提示模板
- `run(query)`: 执行查询
- `reset_memory()`: 重置对话记忆
- `get_memory_summary()`: 获取记忆摘要
- `export_config()`: 导出配置信息

#### build_agent 详细说明

```python
# 使用默认模板
agent.build_agent()

# 使用自定义模板
custom_template = """你的自定义提示模板..."""
agent.build_agent(custom_prompt=custom_template)
```

**模板变量说明：**
- `{tools}`: 自动插入可用工具列表
- `{tool_names}`: 自动插入工具名称列表  
- `{input}`: 用户输入的问题
- `{agent_scratchpad}`: Agent的思考过程记录

### Config

配置类，用于设置模型和行为参数。

#### 主要属性
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| DASHSCOPE_API_KEY | str | None | 阿里云API密钥 |
| BASE_URL | str | https://dashscope.aliyuncs.com/compatible-mode/v1 | API基础URL |
| LLM_MODEL | str | qwen-max | 模型名称 |
| LLM_TEMPERATURE | float | 0.01 | 温度参数(0-1) |
| MAX_TOKENS | int | 8000 | 最大token数 |
| MAX_ITERATIONS | int | 10 | 最大迭代次数 |
| MEMORY_K | int | 10 | 保留对话轮数 |
| VERBOSE | bool | True | 是否显示详细执行过程 |
| RETURN_INTERMEDIATE_STEPS | bool | True | 是否返回中间步骤 |
| HANDLE_PARSING_ERRORS | bool | True | 是否处理解析错误 |

## 🏗️ 项目结构

```
rj-ai-toolkit/
├── agent_toolkit/                  # 🤖 Agent工具包
│   ├── __init__.py                # Agent包入口点
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── agent.py              # EnterpriseAgent类
│   │   └── config.py             # 配置管理
│   ├── tools/                     # Agent工具模块
│   │   ├── __init__.py
│   │   ├── calculator.py         # 计算器工具
│   │   └── text_analyzer.py      # 文本分析工具
│   └── utils/                     # Agent实用工具
│       └── __init__.py           # 通用工具函数
├── examples/                      # 📝 使用示例
│   └── agent_examples/           # Agent示例
│       └── complete_example.py   # 完整功能演示示例
├── setup.py                      # 📦 包配置文件
├── requirements.txt              # 📋 依赖清单
├── README.md                     # 📚 项目文档
├── LICENSE                       # ⚖️ MIT许可证
├── MANIFEST.in                   # 📄 打包清单
└── publish.bat                   # 🚀 发布脚本
```

## 🚀 支持的模型

支持阿里云千问系列所有模型：
- qwen-turbo
- qwen-plus  
- qwen-max
- qwen-max-longcontext

详细模型列表请参考：https://help.aliyun.com/zh/model-studio/getting-started/models

## 🤝 扩展开发

这个包设计用于持续扩展，未来计划添加：

- 🌐 **网络工具**: HTTP请求、API调用
- 📊 **数据分析**: Excel处理、图表生成  
- 🗄️ **数据库**: SQL查询、数据操作
- 🎨 **多媒体**: 图片处理、音频分析
- 🔗 **集成服务**: 第三方API集成

## ⚠️ 注意事项

1. 确保已设置正确的API密钥
2. 网络需要能够访问阿里云API
3. 根据使用量合理设置MAX_TOKENS避免超额
4. 自定义工具需要合理处理异常情况

## 🐛 故障排除

### 常见错误

1. **API密钥错误**
   ```
   请设置DASHSCOPE_API_KEY环境变量或在配置中提供API密钥
   ```
   解决：检查环境变量设置

2. **网络连接问题**
   ```
   Connection error
   ```
   解决：检查网络连接和防火墙设置

3. **模型调用失败**
   ```
   Model not found
   ```
   解决：检查模型名称是否正确

## 🐛 问题反馈

遇到问题或有建议？

- 📝 [提交Issue](https://github.com/Wang-Theo/rj-ai-toolkit/issues)
- 💬 [讨论区](https://github.com/Wang-Theo/rj-ai-toolkit/discussions)
- 📧 联系作者：renjiewang31@gmail.com

## 📜 更新日志

### v0.1.0 (2025-01-21)
- ✨ 初始版本发布
- 🤖 企业级Agent核心实现
- 🛠️ 基础工具集成（计算器、文本分析）
- 📝 完整文档和示例

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

**RJ AI Toolkit** - 让AI Agent开发更简单 🚀
