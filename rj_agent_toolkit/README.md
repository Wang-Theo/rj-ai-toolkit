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

### 功能概览

| 函数 | 用途 | 模型来源 |
|------|------|----------|
| `call_ollama_llm` | LLM对话 | Ollama 本地 |
| `call_qwen_llm_api` | LLM对话 | 通义千问 API |
| `get_ollama_embedding` | 文本向量化 | Ollama 本地 |
| `call_ollama_ocr` | 图片文字识别 | Ollama 本地 |

## 📚 详细文档

完整使用说明、API参数、配置方法等请查看：[Model Clients 完整文档](./model_clients/README_MODEL.md)
