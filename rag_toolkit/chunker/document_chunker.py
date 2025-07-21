"""
文档切块器

提供统一的文档切块接口，支持多种切块策略的策略管理器。
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from langchain.schema import Document
from .base_chunker import BaseChunker, ChunkConfig
from .recursive_chunker import RecursiveChunker
from .semantic_chunker import SemanticChunker


class ChunkStrategy(Enum):
    """切块策略枚举"""
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class DocumentChunker:
    """
    文档切块策略管理器
    
    不是切块器本身，而是管理和选择不同切块策略的门面类。
    """
    
    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        strategy: Union[ChunkStrategy, str] = ChunkStrategy.RECURSIVE,
        **kwargs
    ):
        """
        初始化文档切块策略管理器
        
        Args:
            config: 切块配置
            strategy: 默认切块策略
            **kwargs: 其他参数
        """
        self.config = config or ChunkConfig()
        self.strategy = ChunkStrategy(strategy) if isinstance(strategy, str) else strategy
        
        # 初始化所有切块器
        self._init_chunkers(**kwargs)
    
    def _init_chunkers(self, **kwargs):
        """初始化各种切块器实例"""
        # 递归切块器
        self.recursive_chunker = RecursiveChunker(self.config)
        
        # 语义切块器
        semantic_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['embeddings', 'similarity_threshold', 'min_chunk_size']}
        self.semantic_chunker = SemanticChunker(self.config, **semantic_kwargs)
        
        # 切块器字典，方便策略选择
        self.chunkers = {
            ChunkStrategy.RECURSIVE: self.recursive_chunker,
            ChunkStrategy.SEMANTIC: self.semantic_chunker
        }
    
    def _get_chunker_by_strategy(self, strategy: ChunkStrategy) -> BaseChunker:
        """根据策略获取对应的切块器"""
        return self.chunkers.get(strategy, self.recursive_chunker)
    
    # 委托给具体切块器的基础方法
    def chunk_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        strategy: Optional[ChunkStrategy] = None
    ) -> List[Document]:
        """切分文本（支持策略选择）"""
        chunker = self._get_chunker_by_strategy(strategy or self.strategy)
        return chunker.chunk_text(text, metadata)
    
    def chunk_document(self, document: Document, strategy: Optional[ChunkStrategy] = None) -> List[Document]:
        """切分文档（支持策略选择）"""
        chunker = self._get_chunker_by_strategy(strategy or self.strategy)
        return chunker.chunk_document(document)
    
    def chunk_documents(self, documents: List[Document], strategy: Optional[ChunkStrategy] = None) -> List[Document]:
        """批量切分文档（支持策略选择）"""
        chunker = self._get_chunker_by_strategy(strategy or self.strategy)
        return chunker.chunk_documents(documents)
    
    def chunk_with_hybrid_strategy(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        semantic_threshold: float = 0.6
    ) -> List[Document]:
        """
        使用混合策略切分
        
        先使用语义切块，如果块过大再使用递归切块进一步分割。
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            semantic_threshold: 语义相似度阈值
            
        Returns:
            切分后的文档块列表
        """
        # 首先使用语义切块
        semantic_chunks = self.semantic_chunker.chunk_text(text, metadata)
        
        # 检查是否有块过大需要进一步切分
        final_chunks = []
        for chunk in semantic_chunks:
            if len(chunk.page_content) > self.config.chunk_size * 1.5:
                # 使用递归切块进一步分割
                sub_chunks = self.recursive_chunker.chunk_text(
                    chunk.page_content, 
                    chunk.metadata
                )
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def auto_select_strategy(self, text: str) -> ChunkStrategy:
        """
        自动选择最佳切块策略
        
        Args:
            text: 要分析的文本
            
        Returns:
            推荐的切块策略
        """
        # 分析文本特征
        text_length = len(text)
        
        # 简单的启发式规则
        if text_length < 1000:
            # 短文本，直接递归切块
            return ChunkStrategy.RECURSIVE
        
        # 分析语义结构
        try:
            semantic_analysis = self.semantic_chunker.analyze_semantic_structure(text)
            complexity = semantic_analysis["semantic_complexity"]
            
            if complexity == "high":
                # 语义复杂，使用语义切块
                return ChunkStrategy.SEMANTIC
            elif complexity == "medium":
                # 中等复杂度，使用混合策略
                return ChunkStrategy.HYBRID
            else:
                # 简单文本，使用递归切块
                return ChunkStrategy.RECURSIVE
        except:
            # 语义分析失败，使用递归切块
            return ChunkStrategy.RECURSIVE
    
    def chunk_with_auto_strategy(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        使用自动选择的策略切分文本
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            
        Returns:
            切分后的文档块列表
        """
        optimal_strategy = self.auto_select_strategy(text)
        
        if optimal_strategy == ChunkStrategy.HYBRID:
            return self.chunk_with_hybrid_strategy(text, metadata)
        else:
            return self.chunk_text(text, metadata, optimal_strategy)
    
    def set_strategy(self, strategy: Union[ChunkStrategy, str]) -> None:
        """设置默认切块策略"""
        self.strategy = ChunkStrategy(strategy) if isinstance(strategy, str) else strategy
    
    def update_config(self, config: ChunkConfig) -> None:
        """更新切块配置并重新初始化切块器"""
        self.config = config
        # 重新初始化所有切块器
        self.recursive_chunker = RecursiveChunker(self.config)
        # 语义切块器需要保持原有的额外配置
        self.chunkers[ChunkStrategy.RECURSIVE] = self.recursive_chunker
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取切块器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "current_strategy": self.strategy.value,
            "config": self.config.__dict__,
            "available_strategies": [s.value for s in ChunkStrategy],
            "chunker_stats": {
                "recursive": self.recursive_chunker.get_stats(),
                "semantic": self.semantic_chunker.get_stats()
            }
        }
    
    def compare_strategies(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        比较不同策略的切分效果
        
        Args:
            text: 要比较的文本
            metadata: 文档元数据
            
        Returns:
            比较结果
        """
        results = {}
        
        # 递归切块
        try:
            recursive_chunks = self.recursive_chunker.chunk_text(text, metadata)
            results["recursive"] = {
                "chunk_count": len(recursive_chunks),
                "avg_chunk_size": sum(len(c.page_content) for c in recursive_chunks) / len(recursive_chunks) if recursive_chunks else 0,
                "total_size": sum(len(c.page_content) for c in recursive_chunks)
            }
        except Exception as e:
            results["recursive"] = {"error": str(e)}
        
        # 语义切块
        try:
            semantic_chunks = self.semantic_chunker.chunk_text(text, metadata)
            results["semantic"] = {
                "chunk_count": len(semantic_chunks),
                "avg_chunk_size": sum(len(c.page_content) for c in semantic_chunks) / len(semantic_chunks) if semantic_chunks else 0,
                "total_size": sum(len(c.page_content) for c in semantic_chunks)
            }
        except Exception as e:
            results["semantic"] = {"error": str(e)}
        
        # 混合策略
        try:
            hybrid_chunks = self.chunk_with_hybrid_strategy(text, metadata)
            results["hybrid"] = {
                "chunk_count": len(hybrid_chunks),
                "avg_chunk_size": sum(len(c.page_content) for c in hybrid_chunks) / len(hybrid_chunks) if hybrid_chunks else 0,
                "total_size": sum(len(c.page_content) for c in hybrid_chunks)
            }
        except Exception as e:
            results["hybrid"] = {"error": str(e)}
        
        return results
