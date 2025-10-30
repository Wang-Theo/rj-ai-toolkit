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
history = []

# 第一轮
result = agent.chat("我叫张三", thread_id=thread_id, history_messages=history)
history = result['messages']

# 第二轮（带上下文）
result = agent.chat("我叫什么名字？", thread_id=thread_id, history_messages=history)
# 输出: 你叫张三
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

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `llm` | LLM 实例 | **必需** | LangChain LLM 模型实例 |
| `system_prompt` | str | "You are a helpful assistant..." | 系统提示词 |
| `max_history_messages` | int | 20 | 最大历史消息数量 |
| `tools` | List | None | 工具列表（可选） |

## 返回值

`chat()` 方法返回字典：

```python
{
    'response': str,        # AI 回复
    'messages': List,       # 完整消息历史
    'thread_id': str        # 会话 ID
}
```

## 注意事项

1. **Token 限制**：合理设置 `max_history_messages` 避免超出模型限制
2. **工具定义**：工具的 `description` 要清晰，Agent 根据描述决定何时调用
3. **线程 ID**：为不同用户/会话分配不同的 thread_id
4. **持久化**：`MemorySaver` 仅在内存中保存状态，重启后会丢失

