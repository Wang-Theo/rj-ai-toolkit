# Model Clients 使用说明

## 概述

Model Clients 提供统一的接口调用各种AI模型，包括：
- **LLM 模型**：大语言模型（Ollama、通义千问）
- **Embedding 模型**：文本向量化模型
- **OCR 模型**：图像文字识别模型

所有模型客户端都支持自定义配置，无默认模型，使用者需根据实际需求指定模型名称。

---

## 环境配置

### Ollama 服务

确保 Ollama 服务已启动：

```bash
# 启动 Ollama 服务
ollama serve

# 拉取所需模型
ollama pull qwen3:8b
ollama pull bge-m3:latest
ollama pull qwen2.5vl:7b
```

### 通义千问 API

设置环境变量：

```bash
# Windows
set DASHSCOPE_API_KEY=your-api-key

# Linux/Mac
export DASHSCOPE_API_KEY=your-api-key
```

或在代码中直接传入 `api_key` 参数。

---

## LLM 模型

### call_ollama_llm

调用本地 Ollama 部署的大语言模型

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `system_prompt` | str | - | 系统提示词，定义模型的行为和角色 |
| `user_input` | str | - | 用户输入的问题或指令 |
| `model` | str | - | 模型名称（例如: "qwen3:8b", "llama3:8b"）**必填** |
| `base_url` | str | "http://localhost:11434/v1" | Ollama服务地址 |
| `temperature` | float | 0.01 | 温度参数，控制生成的随机性 |

#### 返回值

- `str`: 模型生成的回复内容

#### 使用示例

```python
from rj_agent_toolkit.model_clients import call_ollama_llm

# 基本用法
response = call_ollama_llm(
    system_prompt="你是一个专业的助手",
    user_input="什么是机器学习？",
    model="qwen3:8b"
)
print(response)

# 使用自定义服务地址
response = call_ollama_llm(
    system_prompt="你是一个编程助手",
    user_input="如何使用Python读取文件？",
    model="llama3:8b",
    base_url="http://192.168.1.100:11434/v1",
    temperature=0.7
)
```

---

### call_qwen_llm_api

调用通义千问 API 生成结果

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_json` | dict | - | 包含输入数据的 JSON 对象，键值对的内容需要与 input_variables_list 中的变量名对应 |
| `input_variables_list` | list | - | 提示模板中使用的变量名列表，确保与 input_json 的键一致 |
| `template` | str | - | 提示模板，定义了模型的输入格式和期望的输出格式 |
| `model` | str | - | 模型名称（例如: "qwen-max", "qwen-plus", "qwen-turbo"）**必填** |
| `api_key` | str | None | API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取 |
| `base_url` | str | "https://dashscope.aliyuncs.com/compatible-mode/v1" | 通义千问API地址 |
| `temperature` | float | 0.01 | 温度参数，控制生成的随机性 |

#### 返回值

- `str`: 模型生成的结果字符串

#### 使用示例

```python
from rj_agent_toolkit.model_clients import call_qwen_llm_api

# 基本用法
response = call_qwen_llm_api(
    input_json={"text": "返利率: 5%", "field": "rebate_rate"},
    input_variables_list=["text", "field"],
    template="从文本中提取{field}: {text}",
    model="qwen-max"
)
print(response)

# 使用自定义 API Key
response = call_qwen_llm_api(
    input_json={"question": "什么是AI？"},
    input_variables_list=["question"],
    template="请回答：{question}",
    model="qwen-plus",
    api_key="your-api-key-here",
    temperature=0.5
)
```

---

## Embedding 模型

### get_ollama_embedding

将文本转换为向量表示

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | str | - | 需要转换为向量的文本 |
| `model` | str | - | embedding模型名称（例如: "bge-m3:latest", "nomic-embed-text"）**必填** |
| `base_url` | str | "http://localhost:11434" | Ollama服务地址 |

#### 返回值

- `List[float]`: 文本的向量表示

#### 使用示例

```python
from rj_agent_toolkit.model_clients import get_ollama_embedding

# 基本用法
vector = get_ollama_embedding(
    text="这是一段测试文本",
    model="bge-m3:latest"
)
print(f"向量维度: {len(vector)}")

# 使用不同的模型
vector = get_ollama_embedding(
    text="Machine learning is a subset of artificial intelligence",
    model="nomic-embed-text",
    base_url="http://192.168.1.100:11434"
)

# 批量向量化
texts = ["文本1", "文本2", "文本3"]
vectors = [get_ollama_embedding(text, model="bge-m3:latest") for text in texts]
```

---

## OCR 模型

### call_ollama_ocr

从图片中提取文字内容

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `image_path` | str | - | 图像文件的路径 |
| `model` | str | - | OCR模型名称（例如: "qwen2.5vl:7b", "llava:13b"）**必填** |
| `base_url` | str | "http://localhost:11434" | Ollama服务地址 |
| `prompt` | str | None | 自定义提示词，如果为None则使用默认提示词 |

#### 返回值

- `str`: 提取的文字内容，表格以 HTML 格式呈现

#### 默认提示词

默认提示词会指导模型：
- 提取图片中的所有文字
- 如果包含表格，以 HTML 格式输出（使用 `<table>`, `<tr>`, `<th>`, `<td>` 标签）
- 非表格文本以原始顺序输出为纯文本
- 不添加解释或注释

#### 使用示例

```python
from rj_agent_toolkit.model_clients import call_ollama_ocr

# 基本用法
text = call_ollama_ocr(
    image_path="document.png",
    model="qwen2.5vl:7b"
)
print(text)

# 使用自定义提示词
custom_prompt = "请提取图片中的所有中文文字，保持原始格式"
text = call_ollama_ocr(
    image_path="chinese_doc.jpg",
    model="qwen2.5vl:7b",
    prompt=custom_prompt
)

# 使用不同的模型
text = call_ollama_ocr(
    image_path="receipt.png",
    model="llava:13b",
    base_url="http://192.168.1.100:11434"
)

# 处理表格图片
table_text = call_ollama_ocr(
    image_path="table.png",
    model="qwen2.5vl:7b"
)
# 输出会包含 HTML 格式的表格
```

---

## 注意事项

1. **模型参数必填**：所有函数的 `model` 参数都是必填的，需要根据实际部署的模型指定
2. **服务地址**：默认使用本地 Ollama 服务，如使用远程服务需指定 `base_url`
3. **API Key**：通义千问 API 需要有效的 API Key，建议通过环境变量配置
4. **模型兼容性**：确保指定的模型已在 Ollama 中下载或在 API 服务中可用
5. **Temperature 参数**：较低的值（如 0.01）产生更确定的输出，较高的值（如 0.7-1.0）产生更有创造性的输出

---

## 版本要求

- Python >= 3.8
- langchain >= 0.3.0
- langchain-openai
- langchain-ollama
- ollama (Python package)
