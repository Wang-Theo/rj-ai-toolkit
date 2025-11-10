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
- **PromptManager**: 管理 system prompt，支持多用户多场景
- **ToolManager**: 双层管理工具和工具集，自动提取 LangChain 元数据
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

- [ChatAgent 详细文档](./rj_agent_toolkit/agents/README_AGENT.md)
- [Model Clients 详细文档](./rj_agent_toolkit/README.md)
- [RAG Toolkit 详细文档](./rj_rag_toolkit/README.md)

## 🔧 示例代码

查看 `examples/` 目录获取完整示例。

## 🏗️ 项目结构

```
rj-ai-toolkit/
├── rj_agent_toolkit/              # 智能对话代理工具包
│   ├── agents/
│   │   ├── chat_agent.py          # ChatAgent 实现
│   │   ├── prompt_manager.py      # Prompt 管理器
│   │   └── tool_manager.py        # Tool 管理器
│   └── model_clients/             # 模型客户端
│       ├── llm.py                 # LLM 接口
│       ├── embedding.py           # Embedding 接口
│       └── ocr.py                 # OCR 接口
├── rj_rag_toolkit/                # 检索增强生成工具包
│   ├── chunker/                   # 文档切块器
│   ├── parser/                    # 文档解析器
│   ├── db_manager/                # 数据库管理器
│   ├── retriever/                 # 检索器
│   └── reranker/                  # 重排序器
└── examples/                      # 使用示例
```

## ⚙️ 系统要求

- Python 3.8+
- Ollama（可选，用于本地模型）

## 🔧 配置说明

环境变量（可选）：
```bash
DASHSCOPE_API_KEY=your_key  # 通义千问 API
```

Ollama 使用：
```bash
ollama serve
ollama pull qwen3:8b
```

## 🤝 扩展开发

自定义模型调用：

```python
from rj_agent_toolkit.model_clients import call_ollama_llm

response = call_ollama_llm(
    system_prompt="你是专业助手",
    user_input="你好",
    model="custom-model:latest",
    base_url="http://your-server:11434/v1",
    temperature=0.8
)
```

自定义 RAG 组件：

```python
from rj_rag_toolkit.parser import BaseParser

class CustomParser(BaseParser):
    def _get_supported_extensions(self):
        return ["custom"]
    
    def _parse_file_content(self, file_path):
        return "自定义解析结果"
```

## 🐛 故障排除

常见问题：

1. **Ollama 连接失败** - 确保服务已启动：`ollama serve`
2. **依赖安装** - 使用虚拟环境避免冲突
3. **内存不足** - 使用更小的模型或调整批处理大小

技术支持：
- [提交 Issue](https://github.com/Wang-Theo/rj-ai-toolkit/issues)
- 邮箱：renjiewang31@gmail.com

## 📜 更新日志

**v0.1.0** (2025-01-21)

- ✨ 初始版本发布
- 🤖 ChatAgent 对话代理
- 🔌 Model Clients（LLM、Embedding、OCR）
- 📚 RAG Toolkit 基础功能

## 🛣️ 开发路线图

**短期计划**

- [x] ChatAgent 智能对话代理
- [ ] 更多内置工具集
- [ ] 数据分析工具

**中期计划**

- [ ] 多媒体处理工具
- [ ] 第三方 API 集成
- [ ] Web 可视化界面

**长期计划**

- [ ] 更多 AI 模型支持
- [ ] 企业版功能
- [ ] 云端部署方案

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - Agent 和工具框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 状态管理
- [Ollama](https://github.com/ollama/ollama) - 本地 LLM 部署
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) - 文本向量化
- [BGE Models](https://github.com/FlagOpen/FlagEmbedding) - 中文 Embedding 模型

---

**RJ AI Toolkit** - 让 AI 开发更简单 🚀
