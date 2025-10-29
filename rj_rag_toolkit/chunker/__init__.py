# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
文档切块器模块

提供多种文档切块策略：
- RecursiveChunker: 递归切块器
- SemanticChunker: 语义切块器
- EMLChunker: 邮件切块器
- PPTXChunker: 幻灯片切块器
"""

from .base_chunker import BaseChunker
from .recursive_chunker import RecursiveChunker  
from .semantic_chunker import SemanticChunker
from .eml_chunker import EMLChunker
from .pptx_chunker import PPTXChunker

__all__ = [
    "BaseChunker",
    "RecursiveChunker",
    "SemanticChunker",
    "EMLChunker",
    "PPTXChunker",
]
