# Agent 使用说明

## 概述

ChatAgent 是基于 LangChain 和 LangGraph 的智能对话代理，提供：
- **对话管理**：持久化对话历史，支持多轮对话
- **工具调用**：自动调用工具完成复杂任务
- **上下文控制**：智能管理对话历史长度
- **灵活配置**：自定义系统提示词和工具列表

## 快速开始

### 基本用法

```python
from rj_agent_toolkit import ChatAgent
from rj_agent_toolkit.model_clients import call_ollama_llm

# 创建 LLM 和 Agent
llm = call_ollama_llm(model="qwen2.5:7b")
agent = ChatAgent(
    llm=llm,
    system_prompt="你是一个友好的AI助手"
)

# 对话
result = agent.chat(
    user_input="你好，请介绍一下自己",
    thread_id="session-001"
)
print(result['response'])
```

### 多轮对话

```python
thread_id = "user-123"

# 第一轮
result1 = agent.chat("我叫张三", thread_id=thread_id)

# 第二轮（Agent 自动从 MemorySaver 恢复历史）
result2 = agent.chat("我叫什么名字？", thread_id=thread_id)
# 输出: 你叫张三
```

### 获取历史对话

```python
# 获取历史
history = agent.get_history(thread_id="user-123")
# 返回: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

# 清除历史
agent.clear_history(thread_id="user-123")
```

### 使用工具

```python
from langchain.tools import Tool

# 定义工具
def search_product(query: str) -> str:
    return f"找到产品: {query}"

tools = [
    Tool(
        name="search_product",
        func=search_product,
        description="搜索产品信息。输入产品名称，返回产品详情"
    )
]

# 创建带工具的 Agent
agent = ChatAgent(
    llm=llm,
    system_prompt="你是一个购物助手",
    tools=tools
)

result = agent.chat("帮我搜索 iPhone 15", thread_id="session-001")
```

## API 方法

### `chat(user_input, thread_id, history_messages=None)`
发送消息并获取 AI 回复。

**返回值:** `{'response': str, 'messages': List, 'thread_id': str}`

### `get_history(thread_id)`
获取指定会话的完整历史对话。

**返回值:** `[{"role": "user", "content": "..."}, ...]`

### `clear_history(thread_id)`
清除指定会话的历史对话。

### `get_tools_info()`
获取已加载的工具信息。

## Thread ID 说明

`thread_id` 是自定义的字符串标识符，用于区分不同会话：

```python
# 用户级别
thread_id = f"user-{user_id}"

# 会话级别（UUID）
import uuid
thread_id = f"session-{uuid.uuid4()}"
```

**要点:**
- 相同 `thread_id` = 同一会话，自动恢复历史
- 不同 `thread_id` = 独立会话

## 注意事项

1. **Token 限制**：合理设置 `max_history_messages` 避免超出模型限制
2. **持久化**：`MemorySaver` 仅在内存中保存，进程重启后会丢失
3. **历史恢复**：调用 `chat()` 时无需手动传入 `history_messages`

