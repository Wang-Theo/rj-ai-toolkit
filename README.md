# RJ AI Toolkit

🚀 **企业级AI工具包集合** - 包含Agent、RAG等多种AI开发工具的完整解决方案

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Package Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/Wang-Theo/rj-ai-toolkit)

## 📦 工具包概览

RJ AI Toolkit 是一个企业级AI开发工具包集合，提供了开发智能应用所需的核心组件。每个工具包都可以独立使用，也可以组合使用来构建复杂的AI应用。

### 🤖 [ChatAgent](./rj_agent_toolkit/agents/README_AGENT.md)
**智能对话代理**
- **对话管理**: 持久化对话历史，支持多轮对话
- **工具调用**: 自动调用工具完成复杂任务
- **上下文控制**: 智能管理对话历史长度
- **灵活配置**: 自定义系统提示词和工具列表
- **LangChain集成**: 基于LangChain和LangGraph构建

### 🔌 [Model Clients](./rj_agent_toolkit/README.md)
**统一模型调用接口**
- **LLM模型**: 支持Ollama本地部署、通义千问API
- **Embedding模型**: 文本向量化，支持多种embedding模型
- **OCR模型**: 图像文字识别，支持表格识别
- **灵活配置**: 所有模型可自定义选择，无硬编码
- **统一接口**: 简洁一致的API设计

### 📚 [RAG Toolkit](./rj_rag_toolkit/README.md)
**检索增强生成工具包**
- 智能文档切块：递归切块、语义切块、邮件切块、幻灯片切块
- 多格式文档解析：PDF、DOCX、EML、MSG、PPTX等，支持OCR
- 统一图片处理：PNG格式，白底无透明，可配置DPI
- 高效向量检索：基于ChromaDB的向量存储
- 混合检索策略：结合向量检索和BM25算法
- 通用重排序器：支持任何重排序模型
- 完整的数据库管理：向量库操作和查询

## 🚀 快速开始

### 安装

#### 从 GitHub 安装（推荐）
```bash
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

#### 从 GitHub 更新
**⚠️ 重要：如果之前安装过旧版本，必须先卸载后重新安装**

```bash
# 1. 卸载旧版本（必须）
pip uninstall rj-ai-toolkit -y

# 2. 安装最新版本
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

或者使用强制重装（推荐）：
```bash
pip install --force-reinstall git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

#### 从源码安装
```bash
git clone https://github.com/Wang-Theo/rj-ai-toolkit.git
cd rj-ai-toolkit
pip install -e .
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本安装与使用

### ChatAgent 使用示例

```python
from rj_agent_toolkit import ChatAgent
from rj_agent_toolkit.model_clients import call_ollama_llm

# 创建 LLM
llm = call_ollama_llm(model="qwen2.5:7b")

# 创建 Agent
agent = ChatAgent(
    llm=llm,
    system_prompt="你是一个友好的AI助手"
)

# 开始对话
result = agent.chat(
    user_input="你好，请介绍一下自己",
    thread_id="session-001"
)

print(result['response'])
```

### Model Clients 使用示例

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

### RAG Toolkit 使用示例

```python
from rj_rag_toolkit import (
    RecursiveChunker,
    PDFParser,
    ChromaManager,
    VectorRetriever,
    Reranker
)
from rj_rag_toolkit.chunker import ChunkConfig

# 初始化组件
chunk_config = ChunkConfig(chunk_size=500, chunk_overlap=50)
chunker = RecursiveChunker(chunk_config)
parser = PDFParser()
db_manager = ChromaManager(
    persist_directory="./vector_db",
    collection_name="my_docs"
)

# 解析和切块
documents = parser.parse("path/to/document.pdf")
chunks = []
for doc in documents:
    doc_chunks = chunker.chunk_text(doc.page_content, doc.metadata)
    chunks.extend(doc_chunks)

# 存储到向量数据库
db_manager.add_documents(chunks)

# 创建检索器并搜索
retriever = VectorRetriever(db_manager)
results = retriever.retrieve(query="查询内容", top_k=5)

for result in results:
    print(f"相关度: {result['score']:.3f}")
    print(f"内容: {result['content'][:200]}...")
```

## 📖 详细文档

- **[ChatAgent 详细文档](./rj_agent_toolkit/agents/README_AGENT.md)** - 智能对话代理的使用说明
- **[Model Clients 详细文档](./rj_agent_toolkit/README.md)** - 模型调用接口的使用说明
  - [完整 API 文档](./rj_agent_toolkit/model_clients/README.md)
- **[RAG Toolkit 详细文档](./rj_rag_toolkit/README.md)** - 检索增强生成系统的详细说明

## 🔧 示例代码

### Model Clients 示例
```bash
# Model Clients 完整功能演示
python examples/model_clients_demo.py
```

### RAG 示例
```bash
# RAG快速开始
python examples/rag_examples/quick_start.py

# RAG完整功能演示
python examples/rag_examples/complete_rag_demo.py
```

## 🏗️ 项目结构

```
rj-ai-toolkit/
├── rj_agent_toolkit/              # 🤖 智能对话代理工具包
│   ├── README.md                  # Agent文档
│   ├── agents/                    # 🤖 对话代理
│   │   ├── README_AGENT.md        # Agent详细文档
│   │   └── chat_agent.py          # ChatAgent实现
│   ├── model_clients/             # 🔌 模型客户端
│   │   ├── README.md              # Model Clients文档
│   │   ├── llm.py                 # LLM模型接口
│   │   ├── embedding.py           # Embedding模型接口
│   │   └── ocr.py                 # OCR模型接口
│   ├── core/                      # 核心模块
│   ├── tools/                     # 内置工具
│   └── utils/                     # 实用工具
├── rj_rag_toolkit/                # 📚 检索增强生成工具包
│   ├── README.md                  # RAG文档
│   ├── chunker/                   # 文档切块器
│   ├── parser/                    # 文档解析器
│   ├── db_manager/                # 数据库管理器
│   ├── retriever/                 # 检索器
│   └── reranker/                  # 重排序器
├── examples/                      # 📝 使用示例
│   ├── agent_examples/            # Agent示例
│   └── rag_examples/              # RAG示例
├── requirements.txt               # 依赖清单
├── setup.py                      # 包配置
└── README.md                      # 总体文档
```

## ⚙️ 系统要求

- **Python**: 3.8+
- **操作系统**: Windows、Linux、macOS
- **内存**: 建议4GB以上（RAG功能）
- **存储**: 预留2GB空间用于模型缓存
- **Ollama**: 用于本地模型部署（可选）

## 🔧 配置说明

### 环境变量
```bash
# 通义千问 API（可选）
DASHSCOPE_API_KEY=your_dashscope_api_key

# Ollama 服务（可选，使用本地模型时需要）
# 默认: http://localhost:11434
```

### Ollama 配置
```bash
# 启动 Ollama 服务
ollama serve

# 拉取模型
ollama pull qwen3:8b
ollama pull bge-m3:latest
ollama pull qwen2.5vl:7b
```

### 向量数据库配置
- **向量数据库**: ChromaDB（默认）
- **文档数据库**: SQLite（默认）
- **可选**: Pinecone、Elasticsearch等

## 🚀 性能优化

### GPU加速

```python
# 启用GPU加速（需要CUDA）
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-large-zh-v1.5', device='cuda')

# 在ChromaManager中使用
db = ChromaManager(
    persist_directory="./chroma_db",
    embedding_function=model.encode
)
```

### 批量处理

```python
# 批量添加文档
results = []
for file_path in file_paths:
    doc = parser.parse(file_path)
    results.append(doc)

# 批量存储
db_manager.add_documents(results)
```

## 🤝 扩展开发

### 自定义模型调用

```python
from rj_agent_toolkit.model_clients import call_ollama_llm

# 使用自定义模型和参数
response = call_ollama_llm(
    system_prompt="你是专业助手",
    user_input="你好",
    model="custom-model:latest",
    base_url="http://your-server:11434/v1",
    temperature=0.8
)
```

### 自定义RAG组件
```python
from rj_rag_toolkit.parser import BaseParser

class CustomParser(BaseParser):
    def _get_supported_extensions(self):
        return ["custom"]
    
    def _parse_file_content(self, file_path):
        return "自定义解析结果"
```

## 🐛 故障排除

### 常见问题

1. **Ollama 连接失败**
   - 确保 Ollama 服务已启动：`ollama serve`
   - 检查端口是否被占用
   - 验证模型是否已下载

2. **API密钥配置**
   - 确保设置了正确的环境变量
   - 检查API密钥格式和权限

3. **依赖安装**
   - 使用虚拟环境避免冲突
   - 确保Python版本兼容

4. **模型下载**
   - 配置镜像源加速下载
   - 检查网络连接和防火墙

5. **内存不足**
   - 调整批处理大小
   - 使用更小的模型

### 技术支持

- 📝 [提交Issue](https://github.com/Wang-Theo/rj-ai-toolkit/issues)
- 💬 [讨论区](https://github.com/Wang-Theo/rj-ai-toolkit/discussions)
- 📧 联系作者：renjiewang31@gmail.com

## 📜 更新日志

### v0.1.0 (2025-01-21)
- ✨ 初始版本发布
- 🔌 Model Clients 核心功能
  - LLM 模型调用（Ollama、通义千问）
  - Embedding 模型支持
  - OCR 模型支持
- 📚 RAG Toolkit 基础功能
- 📝 完整文档和示例

## 🛣️ 开发路线图

### 短期计划
- [x] 🤖 **ChatAgent**: 智能对话代理（已完成）
- [ ] 🛠️ **更多工具**: 内置常用工具集
- [ ] 🌐 **网络工具**: HTTP请求、API调用工具
- [ ] 📊 **数据分析**: Excel处理、图表生成工具

### 中期计划
- [ ] 🎨 **多媒体**: 图片处理、音频分析工具
- [ ] 🔗 **集成服务**: 第三方API集成
- [ ] 📱 **Web界面**: 基于Streamlit的可视化界面

### 长期计划
- [ ] 🤖 **更多AI模型**: 支持更多开源和商业模型
- [ ] 🏢 **企业版**: 增强安全性和企业级功能
- [ ] ☁️ **云服务**: 提供云端部署方案

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目的支持：
- [LangChain](https://github.com/langchain-ai/langchain) - Agent和工具框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent状态管理
- [Ollama](https://github.com/ollama/ollama) - 本地LLM部署
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) - 文本向量化
- [BGE Models](https://github.com/FlagOpen/FlagEmbedding) - 中文Embedding模型

---

**RJ AI Toolkit** - 让AI开发更简单 🚀

*Made with ❤️ by Renjie Wang*
