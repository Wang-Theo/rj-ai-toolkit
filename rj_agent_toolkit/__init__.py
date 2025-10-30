# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
RJ AI Toolkit - Agent Module

企业级AI模型客户端工具包，是RJ AI Toolkit的一部分。
提供统一的模型调用接口，包括LLM、Embedding和OCR模型。

Author: Renjie Wang
Version: 0.1.0
"""

# Model Clients imports
from .model_clients import (
    call_ollama_llm,
    call_qwen_llm_api,
    get_ollama_embedding,
    call_ollama_ocr
)

# Agent imports
from .agents.chat_agent import ChatAgent

__version__ = "0.1.0"
__author__ = "Renjie Wang"
__email__ = "renjiewang31@gmail.com"
__description__ = "RJ AI Toolkit - Agent模块(模型客户端)"

__all__ = [
    # Model Clients exports
    "call_ollama_llm",
    "call_qwen_llm_api",
    "get_ollama_embedding",
    "call_ollama_ocr",
    # Agent exports
    "ChatAgent"
]

# 包级别的配置
DEFAULT_CONFIG = {
    "version": __version__,
    "package_name": "rj-ai-toolkit",
    "module_name": "agent_toolkit",
    "supported_python": ">=3.8",
}
