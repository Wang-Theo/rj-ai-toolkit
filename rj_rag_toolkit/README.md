# RAG Toolkit

📚 **企业级检索增强生成工具包** - 基于LangChain的智能文档处理和检索系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-blue.svg)](https://github.com/chroma-core/chroma)

## 🏗️ 系统架构

```
RAG Toolkit
├── 📝 Parser (文档解析器) → 详见 parser/README_PARSER.md
│   ├── PDFParser - PDF文档解析
│   ├── DOCXParser - Word文档解析
│   ├── EMLParser - 邮件解析
│   ├── MSGParser - Outlook邮件解析
│   └── PPTXParser - PowerPoint解析
├── ✂️ Chunker (切块器) → 详见 chunker/README_CHUNKER.md
│   ├── RecursiveChunker - 递归切块
│   ├── SemanticChunker - 语义切块
│   ├── EMLChunker - 邮件切块
│   └── PPTXChunker - 幻灯片切块
├── 💾 DB Manager (数据库管理器)
│   ├── BaseDBManager - 数据库基类
│   └── ChromaManager - ChromaDB向量数据库
├── 🔍 Retriever (检索器) → 详见 retriever/README_RETRIEVER.md
│   ├── VectorRetriever - 向量检索
│   ├── BM25Retriever - BM25检索
│   └── HybridRetriever - 混合检索
└── 🎯 Reranker (重排序器) → 详见 reranker/README_RERANKER.md
    └── Reranker - 通用重排序器
```

## 📖 详细文档

- **[Parser 文档](./parser/README_PARSER.md)** - 文档解析器详细使用说明
- **[Chunker 文档](./chunker/README_CHUNKER.md)** - 切块器详细使用说明
- **[Retriever 文档](./retriever/README_RETRIEVER.md)** - 检索器详细使用说明
- **[Reranker 文档](./reranker/README_RERANKER.md)** - 重排序器详细使用说明

## 📊 切块策略

> 详见 [Chunker 文档](./chunker/README_CHUNKER.md)

- **RecursiveChunker** - 递归切块，通用文本
- **SemanticChunker** - 语义切块，复杂文档
- **EMLChunker** - 邮件切块
- **PPTXChunker** - 幻灯片切块

```python
from rj_rag_toolkit import RecursiveChunker
from rj_rag_toolkit.chunker import ChunkConfig

config = ChunkConfig(chunk_size=500, chunk_overlap=50)
chunker = RecursiveChunker(config)
chunks = chunker.chunk_text(text)
```

## 🔍 检索策略

> 详见 [Retriever 文档](./retriever/README_RETRIEVER.md)

- **VectorRetriever** - 向量检索
- **BM25Retriever** - BM25检索
- **HybridRetriever** - 混合检索

```python
from rj_rag_toolkit import VectorRetriever, HybridRetriever

# 向量检索
vector_retriever = VectorRetriever(db_manager)
results = vector_retriever.retrieve(query="查询", top_k=10)

# 混合检索
hybrid_retriever = HybridRetriever(db_manager, alpha=0.5)
results = hybrid_retriever.retrieve(query="查询", top_k=10)
```

## 🎯 重排序

> 详见 [Reranker 文档](./reranker/README_RERANKER.md)

支持任何重排序模型（BGE、Cohere、CrossEncoder等）。

```python
from rj_rag_toolkit import Reranker

def my_rerank_function(query: str, doc: str) -> float:
    return score

reranker = Reranker(my_rerank_function)
reranked = reranker.rerank(query="查询", chunks=results, top_k=5)
```

## 📁 支持的文档格式

> 详见 [Parser 文档](./parser/README_PARSER.md)

| 格式 | 解析器 | 功能 |
|------|--------|------|
| PDF | PDFParser | 元数据提取、OCR |
| Word | DOCXParser | 表格提取、样式保留 |
| 邮件 | EMLParser | 附件处理、邮件头解析 |
| Outlook | MSGParser | Outlook邮件支持 |
| 幻灯片 | PPTXParser | 分页保留、图片处理 |

统一输出 Markdown 格式，图片为 PNG（白底）。

## 🔧 自定义组件

所有组件都支持自定义扩展，详见各模块文档。

```python
from rj_rag_toolkit.parser import BaseParser
from rj_rag_toolkit.chunker import BaseChunker

# 自定义解析器
class CustomParser(BaseParser):
    def _get_supported_extensions(self):
        return ["custom"]
    def _parse_file_content(self, file_path):
        return "解析结果"

# 自定义切块器
class CustomChunker(BaseChunker):
    def chunk_text(self, text, metadata=None):
        return chunks
```

## 💾 数据管理

```python
from rj_rag_toolkit import ChromaManager

db = ChromaManager(persist_directory="./chroma_db", collection_name="docs")
db.add_documents(chunks)
results = db.query(query_text="查询", top_k=5)
db.delete_documents(ids=["doc1", "doc2"])
db.clear_collection()
```