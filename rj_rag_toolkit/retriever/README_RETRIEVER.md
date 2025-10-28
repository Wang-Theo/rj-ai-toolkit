# Retriever 使用说明

## 概述

所有 Retriever 遵循统一接口：
- **输入**：查询文本、内容块列表、top_k、min_score
- **输出**：按相关性排序的内容块列表
- **设计**：无状态，每次检索时传入内容块

## 内容块格式

### 输入格式
```python
chunks = [
    {
        'content': '文本内容',      # 必需
        'metadata': {...},          # 可选
        'id': 'chunk_001'           # 可选
    },
    ...
]
```

### 输出格式
```python
results = [
    {
        'content': '文本内容',      # 必有
        'score': 0.95,              # 必有，相关性分数
        'metadata': {...},          # 如果输入中有
        'id': 'chunk_001'           # 如果输入中有
    },
    ...
]
```

## BM25 Retriever

### 概述
基于 BM25 算法的文本检索器，适用于传统的关键词匹配检索。

### 依赖安装
```bash
pip install rank-bm25
pip install jieba  # 中文分词（可选）
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tokenizer` | str | 'jieba' | 分词器名称 ('jieba' 或 'simple') |
| `k1` | float | 1.2 | BM25 参数 k1，控制词频饱和度 |
| `b` | float | 0.75 | BM25 参数 b，控制文档长度归一化 |
| `epsilon` | float | 0.25 | BM25 参数 epsilon，IDF 平滑参数 |
| `language` | str | 'zh' | 语言设置 ('zh' 或 'en') |

### 使用示例

```python
from rj_rag_toolkit.retriever import BM25Retriever

# 基本用法
retriever = BM25Retriever()

chunks = [
    {'content': '机器学习是人工智能的一个分支'},
    {'content': '深度学习使用神经网络', 'metadata': {'source': 'book1'}},
    {'content': '自然语言处理是AI的重要应用', 'id': 'chunk_003'}
]

results = retriever.retrieve(
    query='人工智能',
    chunks=chunks,
    top_k=5
)

# 自定义参数
retriever = BM25Retriever(
    tokenizer='jieba',      # 使用 jieba 分词
    k1=1.5,                 # 调整词频权重
    b=0.75,                 # 调整长度归一化
    language='zh'           # 中文
)

# 使用分数阈值
results = retriever.retrieve(
    query='机器学习',
    chunks=chunks,
    top_k=10,
    min_score=0.5          # 只返回分数 >= 0.5 的结果
)

# 英文检索
retriever_en = BM25Retriever(
    tokenizer='simple',     # 简单空格分词
    language='en'
)
```

### 分词器说明

#### jieba 分词器
- 适用于中文文本
- 需要安装 jieba：`pip install jieba`
- 如果未安装，会自动降级为 simple 分词器

#### simple 分词器
- 移除标点符号
- 转换为小写
- 空格分词
- 适用于英文或简单场景

### BM25 参数调优指南

- **k1**：控制词频饱和度
  - 增大 k1：词频影响更大（适合长文档）
  - 减小 k1：词频影响更小（适合短文档）
  - 典型范围：1.2 ~ 2.0

- **b**：控制文档长度归一化
  - b = 1：完全归一化（长文档不占优势）
  - b = 0：不归一化（长文档有优势）
  - b = 0.75：平衡设置

- **epsilon**：IDF 平滑参数
  - 防止罕见词权重过高
  - 典型值：0.25

## Vector Retriever

### 概述
基于向量相似度的文本检索器，使用语义向量进行匹配。

### Embedding 函数

Vector Retriever 需要一个嵌入函数将文本转换为向量。

#### 函数签名
```python
def embedding_function(texts: List[str]) -> List[List[float]]:
    """
    文本嵌入函数
    
    Args:
        texts: 文本列表
        
    Returns:
        向量列表，每个向量是浮点数列表
    """
    pass
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `embedding_function` | callable | 必需 | 文本嵌入函数 |
| `similarity_metric` | str | 'cosine' | 相似度度量方式 |

### 相似度度量方式

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| `cosine` | 余弦相似度 | 通用，最常用 |
| `dot` | 点积相似度 | 向量已归一化时使用 |
| `euclidean` | 欧氏距离 | 需要考虑向量长度时使用 |

### 使用示例

```python
from rj_rag_toolkit.retriever import VectorRetriever

# 基本用法
retriever = VectorRetriever(
    embedding_function=openai_embed
)

chunks = [
    {'content': '机器学习是人工智能的一个分支'},
    {'content': '深度学习使用神经网络', 'metadata': {'source': 'book1'}},
    {'content': '自然语言处理是AI的重要应用', 'id': 'chunk_003'}
]

results = retriever.retrieve(
    query='人工智能的应用',
    chunks=chunks,
    top_k=5
)

# 使用点积相似度
retriever = VectorRetriever(
    embedding_function=openai_embed,
    similarity_metric='dot'
)

# 使用欧氏距离
retriever = VectorRetriever(
    embedding_function=openai_embed,
    similarity_metric='euclidean'
)

# 使用分数阈值
results = retriever.retrieve(
    query='深度学习',
    chunks=chunks,
    top_k=10,
    min_score=0.7          # 只返回相似度 >= 0.7 的结果
)
```

### 相似度分数范围

- **cosine**：-1 到 1（通常在 0 到 1 之间）
- **dot**：取决于向量长度，无固定范围
- **euclidean**：0 到 1（距离转换为相似度）

## Hybrid Retriever

### 概述
混合检索器，结合 BM25 和向量检索，使用融合策略提升检索效果。

### 融合策略

#### Weighted Fusion（加权融合）
- 对 BM25 和向量检索的分数进行归一化
- 按权重加权求和
- 适合大多数场景

#### RRF Fusion（倒数排名融合）
- Reciprocal Rank Fusion
- 基于排名而非分数进行融合
- 对分数尺度不敏感，更稳定

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `bm25_retriever` | BM25Retriever | 必需 | BM25 检索器实例 |
| `vector_retriever` | VectorRetriever | 必需 | 向量检索器实例 |
| `bm25_weight` | float | 0.5 | BM25 检索权重 |
| `vector_weight` | float | 0.5 | 向量检索权重 |
| `fusion_method` | str | 'weighted' | 融合方法 ('weighted' 或 'rrf') |
| `rrf_k` | int | 60 | RRF 参数 k |

### 使用示例

```python
from rj_rag_toolkit.retriever import BM25Retriever, VectorRetriever, HybridRetriever

# 创建检索器
bm25 = BM25Retriever(language='zh')
vector = VectorRetriever(embedding_function=openai_embed)

# 基本用法（加权融合，权重各 50%）
hybrid = HybridRetriever(
    bm25_retriever=bm25,
    vector_retriever=vector
)

chunks = [
    {'content': '机器学习是人工智能的一个分支'},
    {'content': '深度学习使用神经网络'},
    {'content': '自然语言处理是AI的重要应用'}
]

results = hybrid.retrieve(
    query='人工智能',
    chunks=chunks,
    top_k=5
)

# 调整权重（更重视向量检索）
hybrid = HybridRetriever(
    bm25_retriever=bm25,
    vector_retriever=vector,
    bm25_weight=0.3,         # 30% BM25
    vector_weight=0.7        # 70% 向量
)

# 使用 RRF 融合
hybrid = HybridRetriever(
    bm25_retriever=bm25,
    vector_retriever=vector,
    fusion_method='rrf',
    rrf_k=60
)

# 动态调整权重
hybrid.set_weights(bm25_weight=0.4, vector_weight=0.6)

# 使用分数阈值
results = hybrid.retrieve(
    query='深度学习',
    chunks=chunks,
    top_k=10,
    min_score=0.5
)
```

### 权重调优建议

#### 场景推荐

| 场景 | BM25 权重 | 向量权重 | 说明 |
|------|----------|----------|------|
| 关键词匹配为主 | 0.7 | 0.3 | 专业术语、代码检索 |
| 语义理解为主 | 0.3 | 0.7 | 问答、语义搜索 |
| 平衡模式 | 0.5 | 0.5 | 通用场景 |

#### 调优方法
1. 准备测试查询和标准答案
2. 测试不同权重组合
3. 评估检索准确率（Precision@K、Recall@K）
4. 选择表现最好的权重

### RRF 参数说明

- **rrf_k**：控制排名影响的平滑参数
  - 较大的 k：排名靠后的文档仍有机会
  - 较小的 k：更重视排名靠前的文档
  - 典型值：60（论文推荐值）

## 性能优化建议

### BM25 Retriever
- 中文文本：使用 jieba 分词
- 英文文本：使用 simple 分词
- 大量文档：考虑批量处理

### Vector Retriever
- 使用批量嵌入提升效率
- 选择合适的模型大小（速度 vs 精度）
- 考虑模型缓存和量化

### Hybrid Retriever
- 先调优单个检索器
- 再调整融合权重
- 使用 RRF 当分数尺度差异大时

## 常见问题

### Q: 如何选择检索器？
- **关键词搜索**：使用 BM25Retriever
- **语义搜索**：使用 VectorRetriever
- **综合效果**：使用 HybridRetriever

### Q: 如何设置 top_k 和 min_score？
- **top_k**：返回结果数量，通常 3-10 个
- **min_score**：质量阈值，过滤低相关性结果
- 建议先用 top_k，再用 min_score 精选

### Q: 为什么有些结果没有 metadata 或 id？
- 输出取决于输入：输入有 metadata 才会输出 metadata
- 这是设计特性：保持灵活性，避免空字典

### Q: BM25 和向量检索的分数可以比较吗？
- 不建议直接比较
- 使用 HybridRetriever 自动处理分数归一化和融合

### Q: 如何评估检索效果？
- 准备测试集（查询 + 相关文档）
- 计算 Precision@K、Recall@K、MRR
- A/B 测试不同配置
