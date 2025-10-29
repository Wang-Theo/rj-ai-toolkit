# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
文档重排序器模块

提供通用的重排序器，支持任何 CrossEncoder 模型。
"""

from .reranker import Reranker

__all__ = ["Reranker"]
