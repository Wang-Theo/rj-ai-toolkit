# RJ Agent Toolkit

🤖 **智能对话代理工具包** - 基于 LangChain 和 LangGraph 的企业级 AI Agent 解决方案

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)

## ✨ 核心特性

### 🤖 [ChatAgent](./agents/README_AGENT.md)
**智能对话代理**
- **对话管理**: 持久化对话历史，支持多轮对话
- **工具调用**: 自动调用工具完成复杂任务
- **上下文控制**: 智能管理对话历史长度
- **配置管理**: PromptManager 管理 prompt，ToolManager 管理 tool 和 toolset

### 🔌 [Model Clients](./model_clients/README_MODEL.md)
**统一模型调用接口**
- **LLM模型**: 支持Ollama本地部署、通义千问API
- **Embedding模型**: 文本向量化，支持多种embedding模型
- **OCR模型**: 图像文字识别，支持表格识别
- **灵活配置**: 所有模型可自定义选择，无硬编码

## 🚀 快速开始

### 安装

```bash
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

### ChatAgent 示例

```python
from rj_agent_toolkit import ChatAgent
from rj_agent_toolkit.model_clients import call_ollama_llm

# 创建 LLM 和 Agent
llm = call_ollama_llm(model="qwen2.5:7b")
agent = ChatAgent(
    llm=llm,
    system_prompt="你是一个友好的AI助手"
)

# 对话
result = agent.chat(
    user_input="你好，请介绍一下自己",
    thread_id="session-001"
)
print(result['response'])
```

### Model Clients 示例

```python
from rj_agent_toolkit.model_clients import (
    call_ollama_llm,
    get_ollama_embedding,
    call_ollama_ocr
)

# 调用本地LLM
response = call_ollama_llm(
    system_prompt="你是一个专业助手",
    user_input="什么是机器学习？",
    model="qwen2.5:7b"
)

# 文本向量化
vector = get_ollama_embedding(
    text="这是一段测试文本",
    model="bge-m3:latest"
)

# 图片文字识别
text = call_ollama_ocr(
    image_path="document.png",
    model="qwen2.5vl:7b"
)
```

## � 详细文档

- **[ChatAgent 详细文档](./agents/README_AGENT.md)** - 智能对话代理的使用说明
- **[Model Clients 详细文档](./model_clients/README_MODEL.md)** - 模型调用接口的完整 API 文档
