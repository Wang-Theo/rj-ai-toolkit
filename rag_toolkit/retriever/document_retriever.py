"""
文档检索器

统一的文档检索接口策略管理器。
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from langchain.schema import Document
from .vector_retriever import VectorRetriever
from .hybrid_retriever import HybridRetriever
from .bm25_retriever import BM25Retriever


class RetrieveStrategy(Enum):
    """检索策略枚举"""
    VECTOR = "vector"
    BM25 = "bm25"
    HYBRID = "hybrid"


class DocumentRetriever:
    """
    文档检索策略管理器
    
    不是检索器本身，而是管理和选择不同检索器的门面类。
    """
    
    def __init__(self, 
                 strategy: Union[RetrieveStrategy, str] = RetrieveStrategy.VECTOR,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化文档检索策略管理器
        
        Args:
            strategy: 检索策略
            config: 配置参数
        """
        self.config = config or {}
        self.strategy = RetrieveStrategy(strategy) if isinstance(strategy, str) else strategy
        
        # 初始化各种检索器
        self._init_retrievers()
    
    def _init_retrievers(self):
        """初始化各种检索器实例"""
        try:
            self.vector_retriever = VectorRetriever(self.config.get('vector_config', {}))
        except:
            self.vector_retriever = None
            
        try:
            self.bm25_retriever = BM25Retriever(self.config.get('bm25_config', {}))
        except:
            self.bm25_retriever = None
            
        try:
            # 混合检索器需要向量和BM25检索器
            if self.vector_retriever and self.bm25_retriever:
                self.hybrid_retriever = HybridRetriever(
                    self.vector_retriever, 
                    self.bm25_retriever,
                    self.config.get('hybrid_config', {})
                )
            else:
                self.hybrid_retriever = None
        except:
            self.hybrid_retriever = None
        
        # 检索器字典，方便策略选择
        self.retrievers = {
            RetrieveStrategy.VECTOR: self.vector_retriever,
            RetrieveStrategy.BM25: self.bm25_retriever,
            RetrieveStrategy.HYBRID: self.hybrid_retriever
        }
    
    def _get_retriever_by_strategy(self, strategy: RetrieveStrategy):
        """根据策略获取对应的检索器"""
        retriever = self.retrievers.get(strategy)
        if retriever is None:
            # 回退到可用的检索器
            for r in self.retrievers.values():
                if r is not None:
                    return r
            raise ValueError("没有可用的检索器")
        return retriever
    
    # 委托给具体检索器的方法
    def initialize(self, strategy: Optional[RetrieveStrategy] = None) -> bool:
        """初始化检索器（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.initialize()
    
    def add_documents(self, 
                     documents: List[Document],
                     strategy: Optional[RetrieveStrategy] = None,
                     **kwargs) -> bool:
        """添加文档（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.add_documents(documents, **kwargs)
    
    def retrieve(self, 
                query: str,
                top_k: int = 10,
                strategy: Optional[RetrieveStrategy] = None,
                **kwargs) -> List[Document]:
        """检索文档（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.retrieve(query, top_k, **kwargs)
    
    def update_document(self, 
                       doc_id: str,
                       document: Document,
                       strategy: Optional[RetrieveStrategy] = None,
                       **kwargs) -> bool:
        """更新文档（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.update_document(doc_id, document, **kwargs)
    
    def delete_document(self, 
                       doc_id: str,
                       strategy: Optional[RetrieveStrategy] = None,
                       **kwargs) -> bool:
        """删除文档（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.delete_document(doc_id, **kwargs)
    
    def clear(self, strategy: Optional[RetrieveStrategy] = None, **kwargs) -> bool:
        """清空检索器（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.clear(**kwargs)
    
    def get_stats(self, strategy: Optional[RetrieveStrategy] = None) -> Dict[str, Any]:
        """获取检索器统计信息（支持策略选择）"""
        retriever = self._get_retriever_by_strategy(strategy or self.strategy)
        return retriever.get_stats()
    
    def set_strategy(self, strategy: Union[RetrieveStrategy, str]) -> None:
        """设置默认检索策略"""
        self.strategy = RetrieveStrategy(strategy) if isinstance(strategy, str) else strategy
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的检索策略"""
        return [s.value for s, retriever in self.retrievers.items() if retriever is not None]
    
    def compare_strategies(self, 
                          query: str,
                          top_k: int = 10) -> Dict[str, Any]:
        """比较不同策略的检索效果"""
        results = {}
        
        for strategy, retriever in self.retrievers.items():
            if retriever is None:
                continue
                
            try:
                docs = retriever.retrieve(query, top_k)
                results[strategy.value] = {
                    "document_count": len(docs),
                    "avg_score": sum(getattr(doc, 'score', 0) for doc in docs) / len(docs) if docs else 0,
                    "top_scores": [getattr(doc, 'score', 0) for doc in docs[:5]]
                }
            except Exception as e:
                results[strategy.value] = {"error": str(e)}
        
        return results
    
    def search_with_auto_strategy(self, 
                                 query: str,
                                 top_k: int = 10) -> List[Document]:
        """使用自动选择的策略进行检索"""
        # 简单的策略选择逻辑
        if self.hybrid_retriever:
            return self.retrieve(query, top_k, RetrieveStrategy.HYBRID)
        elif self.vector_retriever:
            return self.retrieve(query, top_k, RetrieveStrategy.VECTOR)
        else:
            return self.retrieve(query, top_k, RetrieveStrategy.BM25)
