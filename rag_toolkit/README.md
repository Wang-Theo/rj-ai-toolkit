# RAG Toolkit

📚 **企业级检索增强生成工具包** - 基于LangChain的智能文档处理和检索系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-blue.svg)](https://github.com/chroma-core/chroma)

## ✨ 核心特性

- **📄 智能切块**: 支持递归切块、语义切块等多种策略
- **🗂️ 多格式解析**: PDF、Word、文本、Markdown等文档格式
- **🔍 向量检索**: 基于BGE等先进嵌入模型的语义检索
- **⚡ 混合检索**: 结合向量检索和BM25的混合策略
- **🎯 智能重排**: 使用重排序模型提高检索精度
- **💾 数据管理**: 完整的文档和向量数据库管理

## 🏗️ 系统架构

```
RAG Toolkit
├── 📝 Parser (文档解析器)
│   ├── PDF解析器
│   ├── Word解析器
│   ├── 文本解析器
│   └── Markdown解析器
├── ✂️ Chunker (切块器)
│   ├── 递归切块器
│   ├── 语义切块器
│   └── 混合切块器
├── 💾 DB Manager (数据库管理器)
│   ├── 向量数据库 (ChromaDB)
│   └── 文档数据库 (SQLite)
├── 🔍 Retriever (检索器)
│   ├── 向量检索器
│   ├── BM25检索器
│   └── 混合检索器
├── 🎯 Ranker (重排序器)
│   ├── BGE重排序器
│   └── CrossEncoder重排序器
└── 🚀 RAG API (统一接口)
```

## 🚀 快速开始

### 1. 基本使用
```python
from rag_toolkit import RAGApi
from rag_toolkit.chunker import ChunkConfig, ChunkStrategy

# 初始化RAG系统
rag = RAGApi(
    vector_db_config={
        "persist_directory": "./vector_db",
        "collection_name": "my_docs"
    },
    chunk_config=ChunkConfig(chunk_size=500, chunk_overlap=50)
)

# 添加文档
result = rag.add_document("path/to/document.pdf")
print(f"添加成功，创建了 {result['chunk_count']} 个文档块")

# 智能搜索
results = rag.search(
    query="RAG系统如何工作？",
    top_k=5,
    retrieval_method="hybrid",  # 混合检索
    rerank=True  # 启用重排序
)

for result in results:
    print(f"相关度: {result['score']:.3f}")
    print(f"内容: {result['content'][:200]}...")
```

### 2. 批量处理文档
```python
# 添加整个目录的文档
result = rag.add_directory(
    directory_path="./documents",
    chunk_strategy=ChunkStrategy.SEMANTIC,  # 使用语义切块
    recursive=True,  # 递归搜索子目录
    file_pattern="*.pdf"  # 只处理PDF文件
)

print(f"处理了 {result['successful_documents']} 个文档")
print(f"总共创建 {result['total_chunks']} 个文档块")
```

### 3. 高级配置
```python
from rag_toolkit.chunker import ChunkConfig, ChunkStrategy
from rag_toolkit.parser import ParseConfig

# 切块配置
chunk_config = ChunkConfig(
    chunk_size=1000,           # 块大小
    chunk_overlap=100,         # 重叠大小
    separators=["\n\n", "\n", "。", "！", "？"],  # 分隔符
    add_start_index=True       # 添加位置索引
)

# 解析配置
parse_config = ParseConfig(
    extract_metadata=True,     # 提取元数据
    preserve_structure=True,   # 保留文档结构
    extract_tables=True,       # 提取表格
    extract_images=False       # 不提取图片
)

# 向量数据库配置
vector_db_config = {
    "persist_directory": "./chroma_db",
    "collection_name": "enterprise_docs",
    "embeddings": {
        "model_name": "BAAI/bge-large-zh-v1.5",  # 使用大模型
        "model_kwargs": {"device": "cuda"}        # GPU加速
    }
}

# 初始化高级RAG系统
rag = RAGApi(
    vector_db_config=vector_db_config,
    chunk_config=chunk_config
)
```

## 📊 切块策略对比

### 递归切块
```python
from rag_toolkit.chunker import DocumentChunker, ChunkStrategy

chunker = DocumentChunker(strategy=ChunkStrategy.RECURSIVE)
chunks = chunker.chunk_text(text)
# 特点：快速、稳定，适合大多数场景
```

### 语义切块
```python
chunker = DocumentChunker(strategy=ChunkStrategy.SEMANTIC)
chunks = chunker.chunk_text(text)
# 特点：保持语义完整性，适合复杂文档
```

### 混合切块
```python
chunks = chunker.chunk_with_hybrid_strategy(text)
# 特点：结合两种策略的优势
```

### 自动策略选择
```python
chunks = chunker.chunk_with_auto_strategy(text)
# 特点：自动选择最佳策略
```

## 🔍 检索策略

### 向量检索
```python
results = rag.search(
    query="查询内容",
    retrieval_method="vector",
    top_k=10
)
# 特点：语义相似度检索，理解查询意图
```

### 混合检索
```python
results = rag.search(
    query="查询内容",
    retrieval_method="hybrid",
    top_k=10
)
# 特点：结合语义和关键词检索
```

### 语义搜索
```python
results = rag.semantic_search(
    query="查询内容",
    similarity_threshold=0.7,  # 相似度阈值
    top_k=5
)
# 特点：高精度语义匹配
```

## 🎯 重排序功能

### 启用重排序
```python
# 使用默认重排序器
results = rag.search(query="查询", rerank=True)

# 手动重排序
from rag_toolkit.ranker import BGERanker
ranker = BGERanker()
reranked_results = ranker.rerank(query, results, top_k=5)
```

## 📁 支持的文档格式

| 格式 | 扩展名 | 解析器 | 特殊功能 |
|------|--------|--------|----------|
| PDF | .pdf | PDFParser | ✅ 元数据提取、分页信息 |
| Word | .docx, .doc | WordParser | ✅ 表格提取、样式保留 |
| 文本 | .txt | TextParser | ✅ 编码自动检测 |
| Markdown | .md | MarkdownParser | ✅ 结构保留、语法解析 |

## 🔧 自定义组件

### 自定义解析器
```python
from rag_toolkit.parser import BaseParser

class CustomParser(BaseParser):
    def _get_supported_extensions(self):
        return ["custom"]
    
    def _parse_file_content(self, file_path):
        # 实现自定义解析逻辑
        return "解析后的文本内容"

# 注册自定义解析器
parser.add_parser(["custom"], CustomParser())
```

### 自定义切块器
```python
from rag_toolkit.chunker import BaseChunker

class CustomChunker(BaseChunker):
    def chunk_text(self, text, metadata=None):
        # 实现自定义切块逻辑
        return chunks
```

## 💾 数据管理

### 数据库统计
```python
# 获取系统统计信息
stats = rag.get_statistics()
print(f"文档数量: {stats['documents_processed']}")
print(f"文档块数: {stats['chunks_created']}")
```

### 健康检查
```python
# 系统健康检查
health = rag.health_check()
print(f"系统状态: {health['status']}")
```

### 数据清理
```python
# 删除特定文档
rag.delete_document(doc_id)

# 清空所有数据
rag.clear_all()
```

## 📊 性能优化

### 向量数据库优化
```python
# 使用GPU加速
vector_config = {
    "embeddings": {
        "model_kwargs": {"device": "cuda"}
    }
}

# 批量处理
results = rag.add_documents(file_paths, batch_size=20)
```

### 检索优化
```python
# 设置过滤条件
results = rag.search(
    query="查询",
    filters={"source": "重要文档", "date": "2024"},
    top_k=10
)
```

## 🧪 示例代码

### 运行完整示例
```bash
# RAG快速开始
python examples/rag_examples/quick_start.py

# RAG完整功能演示  
python examples/rag_examples/complete_rag_demo.py
```

### 基础示例
```python
# 参考 examples/rag_examples/ 目录下的示例代码
```

## 🔧 故障排除

### 常见问题

1. **向量数据库连接失败**
   ```python
   # 检查ChromaDB是否正确安装
   pip install chromadb
   ```

2. **文档解析失败**
   ```python
   # 安装对应的解析库
   pip install PyMuPDF python-docx
   ```

3. **嵌入模型下载慢**
   ```python
   # 配置国内镜像源
   import os
   os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
   ```

### 性能调优

1. **内存优化**: 适当调整chunk_size和batch_size
2. **速度优化**: 使用GPU加速和缓存机制
3. **精度优化**: 调整相似度阈值和重排序参数

## 📈 评估指标

### 检索质量评估
```python
# 计算检索准确率
def evaluate_retrieval(queries, ground_truth):
    # 实现评估逻辑
    pass
```

### 系统监控
```python
# 监控系统性能
import time
start = time.time()
results = rag.search(query)
print(f"检索耗时: {time.time() - start:.2f}s")
```

---

**RAG Toolkit** - 让智能文档检索更简单 📚
