# Reranker 使用说明

## Reranker 类

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rerank_function` | Callable | 必需 | 重排序函数，签名: `(query: str, doc: str) -> float` |

### rerank 方法

```python
def rerank(self, query: str, chunks: List[Dict], top_k: int = 10, show_progress: bool = False) -> List[Dict]
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | str | 查询文本 |
| `chunks` | List[Dict] | 内容块列表 |
| `top_k` | int | 返回结果数量 |

**返回：** `List[Dict]` - 重排序后的内容块列表

## 内容块格式

### 输入格式

```python
chunks = [
    {
        'content': '文本内容',      # 必需
        'score': 0.85,              # 可选
        'metadata': {...},          # 可选
        'id': 'chunk_001'           # 可选
    }
]
```

### 输出格式

```python
results = [
    {
        'content': '文本内容',      # 必有
        'rerank_score': 0.95,       # 必有，范围 [0, 1]
        'score': 0.85,              # 如果输入中有
        'metadata': {...},          # 如果输入中有
        'id': 'chunk_001'           # 如果输入中有
    }
]
```

## 重排序函数要求

重排序函数签名：

```python
def rerank_function(query: str, doc: str) -> float:
    """
    Args:
        query: 查询文本
        doc: 文档文本
        
    Returns:
        相关性分数（任意数值，会被自动归一化到 [0, 1]）
    """
```

## 使用示例

### 基本用法

```python
from sentence_transformers import CrossEncoder
from rj_rag_toolkit.ranker import Reranker

# 创建模型
model = CrossEncoder("BAAI/bge-reranker-base")

# 定义重排序函数
def rerank_func(query, doc):
    return model.predict([[query, doc]])[0]

# 创建重排序器
reranker = Reranker(rerank_function=rerank_func)

# 准备内容块
chunks = [
    {'content': '机器学习是人工智能的核心', 'score': 0.75},
    {'content': '深度学习使用神经网络', 'score': 0.80}
]

# 重排序
results = reranker.rerank(query='人工智能技术', chunks=chunks, top_k=2)

# 查看结果
for r in results:
    print(f"重排序分数: {r['rerank_score']:.2f}, 内容: {r['content']}")
```

### 与检索器配合

```python
from rj_rag_toolkit.retriever import HybridRetriever
from rj_rag_toolkit.ranker import Reranker

# 两阶段检索
retrieval_results = retriever.retrieve(query='问题', chunks=all_chunks, top_k=20)
final_results = reranker.rerank(query='问题', chunks=retrieval_results, top_k=5)
```

### 自定义重排序函数

```python
# 简单的关键词匹配
def keyword_rerank(query, doc):
    query_words = set(query.split())
    doc_words = set(doc.split())
    return len(query_words & doc_words) / len(query_words)

reranker = Reranker(rerank_function=keyword_rerank)

# 使用余弦相似度
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()

def tfidf_rerank(query, doc):
    vectors = vectorizer.fit_transform([query, doc])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

reranker = Reranker(rerank_function=tfidf_rerank)
```
