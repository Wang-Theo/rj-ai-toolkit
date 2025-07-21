"""
基础切块器

所有切块器的基类，定义统一的接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.schema import Document


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


@dataclass  
class ChunkMetadata:
    """切块元数据"""
    chunk_id: str
    source_doc_id: str
    chunk_index: int
    start_char: int
    end_char: int
    token_count: int
    chunk_type: str = "text"
    confidence_score: float = 1.0
    parent_chunk_id: Optional[str] = None
    

class BaseChunker(ABC):
    """
    基础切块器抽象类
    
    所有切块器都需要继承此类并实现抽象方法。
    """
    
    def __init__(self, config: ChunkConfig):
        """
        初始化切块器
        
        Args:
            config: 切块配置
        """
        self.config = config
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
    
    def _create_chunk_metadata(
        self, 
        chunk_id: str,
        source_doc_id: str, 
        chunk_index: int,
        start_char: int,
        end_char: int,
        token_count: int,
        original_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建切块元数据
        
        Args:
            chunk_id: 切块ID
            source_doc_id: 源文档ID
            chunk_index: 切块索引
            start_char: 起始字符位置
            end_char: 结束字符位置
            token_count: token数量
            original_metadata: 原始文档元数据
            
        Returns:
            完整的切块元数据
        """
        metadata = {
            "chunk_id": chunk_id,
            "source_doc_id": source_doc_id,
            "chunk_index": chunk_index,
            "start_char": start_char,
            "end_char": end_char,
            "token_count": token_count,
            "chunk_type": "text",
            "confidence_score": 1.0,
            "chunker_type": self.__class__.__name__
        }
        
        # 合并原始元数据
        if original_metadata:
            for key, value in original_metadata.items():
                if key not in metadata:  # 不覆盖切块特有的元数据
                    metadata[key] = value
                    
        return metadata
    
    def _estimate_token_count(self, text: str) -> int:
        """
        估算文本的token数量
        
        Args:
            text: 要估算的文本
            
        Returns:
            估算的token数量
        """
        # 简单估算：中文按字符数，英文按单词数*1.3
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace('\n', ' ').split()) - chinese_chars
        return chinese_chars + int(english_words * 1.3)
    
    def _generate_chunk_id(self, source_doc_id: str, chunk_index: int) -> str:
        """
        生成切块ID
        
        Args:
            source_doc_id: 源文档ID
            chunk_index: 切块索引
            
        Returns:
            切块ID
        """
        return f"{source_doc_id}_chunk_{chunk_index}"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取切块器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "chunker_type": self.__class__.__name__,
            "config": self.config.__dict__,
            "version": "1.0.0"
        }
