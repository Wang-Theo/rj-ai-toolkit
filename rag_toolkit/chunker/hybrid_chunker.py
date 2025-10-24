"""
混合切块器

结合语义切块和递归切块的混合策略切块器。
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from .base_chunker import BaseChunker, ChunkConfig
from .recursive_chunker import RecursiveChunker
from .semantic_chunker import SemanticChunker


class HybridChunker(BaseChunker):
    """
    混合切块器
    
    先使用语义切块，如果块过大再使用递归切块进一步分割。
    """
    
    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        semantic_threshold: float = 0.6,
        max_chunk_size_multiplier: float = 1.5,
        **kwargs
    ):
        """
        初始化混合切块器
        
        Args:
            config: 切块配置
            semantic_threshold: 语义相似度阈值
            max_chunk_size_multiplier: 最大块大小倍数（超过 chunk_size * 此值需要进一步切分）
            **kwargs: 传递给 SemanticChunker 的其他参数
        """
        super().__init__(config)
        self.semantic_threshold = semantic_threshold
        self.max_chunk_size_multiplier = max_chunk_size_multiplier
        
        # 初始化两个切块器
        self.semantic_chunker = SemanticChunker(self.config, **kwargs)
        self.recursive_chunker = RecursiveChunker(self.config)
        
        # 统计信息
        self.stats = {
            "total_chunks": 0,
            "semantic_only_chunks": 0,
            "further_split_chunks": 0,
            "total_text_length": 0
        }
    
    def chunk_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        使用混合策略切分文本
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            
        Returns:
            切分后的文档块列表
        """
        if not text or not text.strip():
            return []
        
        # 首先使用语义切块
        semantic_chunks = self.semantic_chunker.chunk_text(text, metadata)
        
        # 检查是否有块过大需要进一步切分
        final_chunks = []
        max_size = self.config.chunk_size * self.max_chunk_size_multiplier
        
        for chunk in semantic_chunks:
            chunk_length = len(chunk.page_content)
            
            if chunk_length > max_size:
                # 使用递归切块进一步分割
                sub_chunks = self.recursive_chunker.chunk_text(
                    chunk.page_content, 
                    chunk.metadata
                )
                final_chunks.extend(sub_chunks)
                self.stats["further_split_chunks"] += len(sub_chunks)
            else:
                final_chunks.append(chunk)
                self.stats["semantic_only_chunks"] += 1
        
        # 更新统计
        self.stats["total_chunks"] += len(final_chunks)
        self.stats["total_text_length"] += len(text)
        
        return final_chunks
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        使用混合策略切分文档
        
        Args:
            document: 要切分的文档
            
        Returns:
            切分后的文档块列表
        """
        return self.chunk_text(document.page_content, document.metadata)
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        批量切分文档
        
        Args:
            documents: 要切分的文档列表
            
        Returns:
            切分后的文档块列表
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        avg_chunk_size = (
            self.stats["total_text_length"] / self.stats["total_chunks"]
            if self.stats["total_chunks"] > 0 else 0
        )
        
        return {
            **self.stats,
            "avg_chunk_size": avg_chunk_size,
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "semantic_threshold": self.semantic_threshold,
                "max_chunk_size_multiplier": self.max_chunk_size_multiplier
            },
            "semantic_chunker_stats": self.semantic_chunker.get_stats(),
            "recursive_chunker_stats": self.recursive_chunker.get_stats()
        }
