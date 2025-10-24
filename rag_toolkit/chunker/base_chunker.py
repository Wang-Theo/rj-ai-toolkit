"""
基础切块器

所有切块器的基类，定义统一的接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_core.documents import Document


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
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        将文本切分成块
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            
        Returns:
            切分后的文档块列表
        """
        pass
    
    @abstractmethod  
    def chunk_document(self, document: Document) -> List[Document]:
        """
        将文档切分成块
        
        Args:
            document: 要切分的文档
            
        Returns:
            切分后的文档块列表
        """
        pass
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        批量切分文档
        
        Args:
            documents: 要切分的文档列表
            
        Returns:
            所有切分后的文档块列表
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取切块器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "chunker_type": self.__class__.__name__,
            "config": self.config.__dict__
        }

