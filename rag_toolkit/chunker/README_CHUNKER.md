# Chunker 使用说明

## 概述

所有 Chunker 遵循统一接口：
- **输入**：Markdown 格式文本
- **输出**：`List[str]` 文本块列表
- **长度类型**：支持按字符数或 token 数切分

## RecursiveChunker

### 输入
- Markdown 格式文本（通用）

### 输出
- 按分隔符递归切分的文本块列表
- 支持重叠（增强上下文连续性）

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `chunk_size` | int | 1000 | 切块大小（字符数或 token 数） |
| `chunk_overlap` | int | 200 | 重叠大小 |
| `length_type` | str | "char" | 长度计算方式："char" 或 "token" |
| `separators` | List[str] | `["\n\n", "\n", " ", ""]` | 分隔符列表（优先级从高到低） |
| `keep_separator` | bool | False | 是否保留分隔符 |
| `add_start_index` | bool | True | 是否添加起始索引 |
| `strip_whitespace` | bool | True | 是否去除空白字符 |

### 使用

```python
from rag_toolkit.chunker import RecursiveChunker

# 基本用法
chunker = RecursiveChunker()
chunks = chunker.chunk(markdown_text)

# 按 token 数切分
chunker = RecursiveChunker(
    chunk_size=512,
    chunk_overlap=50,
    length_type="token"
)

# 自定义分隔符（适合中文）
chunker = RecursiveChunker(
    chunk_size=800,
    separators=["\n\n", "\n", "。", "！", "？", " "],
    keep_separator=True
)
```

## SemanticChunker

### 输入
- Markdown 格式文本（需要清晰的句子结构）

### 输出
- 按语义相似度切分的文本块列表
- 保持语义完整性

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `embedding_func` | Callable | **必需** | Embedding 函数：`func(texts: List[str]) -> List[List[float]]` |
| `chunk_size` | int | 1000 | 切块大小（字符数或 token 数） |
| `chunk_overlap` | int | 200 | 重叠大小 |
| `similarity_threshold` | float | 0.5 | 相似度阈值 |
| `min_chunk_size` | int | 100 | 最小块大小 |
| `length_type` | str | "char" | 长度计算方式："char" 或 "token" |

### 使用

```python
from rag_toolkit.chunker import SemanticChunker

# 定义 embedding 函数
def get_embeddings(texts: List[str]) -> List[List[float]]:
    # 使用你的 embedding 模型
    embeddings = model.encode(texts)
    return embeddings.tolist()

# 基本用法
chunker = SemanticChunker(
    embedding_func=get_embeddings,
    similarity_threshold=0.5
)
chunks = chunker.chunk(markdown_text)

# 按 token 数切分
chunker = SemanticChunker(
    embedding_func=get_embeddings,
    similarity_threshold=0.6,
    min_chunk_size=150,
    length_type="token"
)
```

## EMLChunker

**专用于 EMLParser 输出**：此切块器专门处理 `EMLParser.parse_file()` 生成的 Markdown 内容。

### 输入
- `EMLParser` 生成的 Markdown 格式邮件内容
- 自动识别 `## Email N` 邮件边界标记

### 输出
- 按邮件链切分的文本块列表
- 保护表格不被切分
- 可选删除邮箱地址

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `chunk_size` | int | 4000 | 切块大小（字符数或 token 数） |
| `length_type` | str | "token" | 长度计算方式："char" 或 "token" |
| `remove_emails` | bool | True | 是否删除邮箱地址 |

### 使用

```python
from rag_toolkit.chunker import EMLChunker
from rag_toolkit.parser import EMLParser

# 解析邮件
parser = EMLParser()
markdown_content = parser.parse_file("email.eml")

# 基本用法（删除邮箱）
chunker = EMLChunker()
chunks = chunker.chunk(markdown_content)

# 保留邮箱地址
chunker = EMLChunker(
    chunk_size=2000,
    length_type="char",
    remove_emails=False
)

# 按 token 数切分
chunker = EMLChunker(
    chunk_size=512,
    length_type="token",
    remove_emails=True
)
```

## PPTXChunker

**专用于 PPTXParser 输出**：此切块器专门处理 `PPTXParser.parse_file()` 生成的 Markdown 内容。

### 输入
- `PPTXParser` 生成的 Markdown 格式 PPT 内容
- 自动识别 `## Slide N` 幻灯片边界标记

### 输出
- 按幻灯片切分的文本块列表
- 保护表格不被切分
- 支持文件头内容（Slide 0）

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `chunk_size` | int | 4000 | 切块大小（字符数或 token 数） |
| `length_type` | str | "token" | 长度计算方式："char" 或 "token" |

### 使用

```python
from rag_toolkit.chunker import PPTXChunker
from rag_toolkit.parser import PPTXParser

# 解析 PPT
parser = PPTXParser()
markdown_content = parser.parse_file("presentation.pptx")

# 基本用法
chunker = PPTXChunker()
chunks = chunker.chunk(markdown_content)

# 按字符数切分
chunker = PPTXChunker(
    chunk_size=2000,
    length_type="char"
)

# 按 token 数切分
chunker = PPTXChunker(
    chunk_size=512,
    length_type="token"
)
```

## Embedding 函数配置

SemanticChunker 需要提供 `embedding_func` 参数，函数签名如下：

```python
def embedding_func(texts: List[str]) -> List[List[float]]:
    """
    Embedding 函数
    
    Args:
        texts: 文本列表（句子列表）
        
    Returns:
        向量列表，每个向量是浮点数列表
    """
    pass
```

**输入**：`List[str]` - 需要向量化的文本列表

**输出**：`List[List[float]]` - 对应的向量列表

## 选择指南

| 场景 | 推荐切块器 |
|------|-----------|
| 通用文档 | RecursiveChunker |
| 需要语义完整性 | SemanticChunker |
| 邮件内容 | EMLChunker |
| PPT 文档 | PPTXChunker |

## 注意事项

1. **Token vs 字符**：使用 `length_type="token"` 更精确控制 LLM 输入（使用 GPT-4 tokenizer）
2. **重叠大小**：`chunk_overlap` 可提高检索召回率（仅 RecursiveChunker 和 SemanticChunker 支持）
3. **语义切块**：需要提供 embedding 函数，计算开销较大
4. **特殊切块器**：
   - EMLChunker 和 PPTXChunker 需要对应 Parser 的输出
   - EMLChunker 和 PPTXChunker 不支持重叠（`chunk_overlap` 固定为 0）
   - EMLChunker 和 PPTXChunker 会自动保护表格内容不被切分
