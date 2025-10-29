# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
基础切块器

所有切块器的基类，定义统一的接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """切块配置"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: Optional[List[str]] = None
    keep_separator: bool = False
    add_start_index: bool = True
    strip_whitespace: bool = True
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", " ", ""]


class BaseChunker(ABC):
    """
    基础切块器抽象类
    
    所有切块器都需要继承此类并实现抽象方法。
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        初始化切块器
        
        Args:
            config: 切块配置
        """
        self.config = config or ChunkConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """验证配置参数"""
        if self.config.chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")
        if self.config.chunk_overlap < 0:
            raise ValueError("chunk_overlap 不能小于 0")
        if self.config.chunk_overlap >= self.config.chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
    
    @abstractmethod
    def chunk(self, markdown_text: str) -> List[str]:
        """
        切分 Markdown 文本
        
        Args:
            markdown_text: 输入的 Markdown 文本
            
        Returns:
            切块后的文本列表
        """
        pass

