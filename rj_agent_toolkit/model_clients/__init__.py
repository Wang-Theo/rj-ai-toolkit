"""
模型客户端模块

提供统一的接口调用各种AI模型，包括LLM、Embedding和OCR模型。
"""

from .llm import call_ollama_llm, call_qwen_llm_api
from .embedding import get_ollama_embedding
from .ocr import call_ollama_ocr

__all__ = [
    "call_ollama_llm",
    "call_qwen_llm_api",
    "get_ollama_embedding",
    "call_ollama_ocr"
]
