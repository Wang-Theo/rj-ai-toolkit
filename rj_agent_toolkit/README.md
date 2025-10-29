# Model Clients

🔌 **统一模型调用接口** - 提供简洁一致的AI模型调用方式

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)

## ✨ 核心特性

- **� LLM模型**: 支持Ollama本地部署和通义千问API
- **� Embedding模型**: 文本向量化，支持多种embedding模型
- **�️ OCR模型**: 图像文字识别，支持表格识别
- **⚙️ 灵活配置**: 所有模型可自定义选择，无硬编码
- **� 统一接口**: 简洁一致的API设计

## 🚀 快速开始

### 安装

```bash
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

### 基本使用

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
    model="qwen3:8b"
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

## 📚 详细文档

详细使用说明请查看：[Model Clients 完整文档](./model_clients/README.md)

## 🛠️ 功能模块

### LLM 模型

- **call_ollama_llm**: 调用本地 Ollama 部署的大语言模型
- **call_qwen_llm_api**: 调用通义千问 API

### Embedding 模型

- **get_ollama_embedding**: 文本向量化

### OCR 模型

- **call_ollama_ocr**: 图片文字识别

## 🔧 环境配置

### Ollama 服务

```bash
# 启动 Ollama 服务
ollama serve

# 拉取所需模型
ollama pull qwen3:8b
ollama pull bge-m3:latest
ollama pull qwen2.5vl:7b
```

### 通义千问 API

```bash
# Windows
set DASHSCOPE_API_KEY=your-api-key

# Linux/Mac
export DASHSCOPE_API_KEY=your-api-key
```

## � 使用示例

### LLM 模型调用

```python
from rj_agent_toolkit.model_clients import call_ollama_llm

response = call_ollama_llm(
    system_prompt="你是一个编程助手",
    user_input="如何使用Python读取文件？",
    model="qwen3:8b",
    temperature=0.7
)
print(response)
```

### 文本向量化

```python
from rj_agent_toolkit.model_clients import get_ollama_embedding

# 单个文本向量化
vector = get_ollama_embedding(
    text="这是一段测试文本",
    model="bge-m3:latest"
)
print(f"向量维度: {len(vector)}")

# 批量向量化
texts = ["文本1", "文本2", "文本3"]
vectors = [
    get_ollama_embedding(text, model="bge-m3:latest") 
    for text in texts
]
```

### OCR 识别

```python
from rj_agent_toolkit.model_clients import call_ollama_ocr

# 基本使用
text = call_ollama_ocr(
    image_path="document.png",
    model="qwen2.5vl:7b"
)

# 自定义提示词
custom_prompt = "请提取图片中的所有中文文字，保持原始格式"
text = call_ollama_ocr(
    image_path="chinese_doc.jpg",
    model="qwen2.5vl:7b",
    prompt=custom_prompt
)
```

## 🔍 API 参考

### call_ollama_llm

调用本地 Ollama 部署的大语言模型

**参数:**
- `system_prompt` (str): 系统提示词
- `user_input` (str): 用户输入
- `model` (str): 模型名称 **必填**
- `base_url` (str): Ollama服务地址，默认 "http://localhost:11434/v1"
- `temperature` (float): 温度参数，默认 0.01

**返回:** `str` - 模型回复

### get_ollama_embedding

文本向量化

**参数:**
- `text` (str): 需要转换的文本
- `model` (str): embedding模型名称 **必填**
- `base_url` (str): Ollama服务地址，默认 "http://localhost:11434"

**返回:** `List[float]` - 文本向量

### call_ollama_ocr

图片文字识别

**参数:**
- `image_path` (str): 图片路径
- `model` (str): OCR模型名称 **必填**
- `base_url` (str): Ollama服务地址，默认 "http://localhost:11434"
- `prompt` (str): 自定义提示词，默认 None

**返回:** `str` - 识别的文字

## ⚠️ 注意事项

1. **模型参数必填**: 所有函数的 `model` 参数都是必填的
2. **服务地址**: 默认使用本地 Ollama 服务
3. **API Key**: 通义千问 API 需要有效的 API Key
4. **模型兼容性**: 确保指定的模型已下载或可用

## 🚀 完整示例

```bash
# 运行完整示例
python examples/model_clients_demo.py
```

## � 支持的模型

### Ollama 本地模型
- **LLM**: qwen3:8b, llama3:8b, mistral等
- **Embedding**: bge-m3:latest, nomic-embed-text等
- **OCR**: qwen2.5vl:7b, llava:13b等

### 通义千问 API
- qwen-max
- qwen-plus
- qwen-turbo

详细模型列表请参考：
- [Ollama 模型库](https://ollama.com/library)
- [通义千问模型](https://help.aliyun.com/zh/model-studio/getting-started/models)

---

**Model Clients** - 让AI模型调用更简单 🚀
