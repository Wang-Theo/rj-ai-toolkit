"""
文档重排序器

基于相关性分数的文档重排序策略管理器。
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from langchain.schema import Document
from .bge_ranker import BGERanker
from .cohere_ranker import CohereRanker
from .cross_encoder_ranker import CrossEncoderRanker


class RankStrategy(Enum):
    """重排序策略枚举"""
    BGE = "bge"
    COHERE = "cohere"
    CROSS_ENCODER = "cross_encoder"


class DocumentRanker:
    """
    文档重排序策略管理器
    
    不是重排序器本身，而是管理和选择不同重排序器的门面类。
    """
    
    def __init__(self, 
                 strategy: Union[RankStrategy, str] = RankStrategy.BGE,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化文档重排序策略管理器
        
        Args:
            strategy: 重排序策略
            config: 配置参数
        """
        self.config = config or {}
        self.strategy = RankStrategy(strategy) if isinstance(strategy, str) else strategy
        
        # 初始化各种重排序器
        self._init_rankers()
    
    def _init_rankers(self):
        """初始化各种重排序器实例"""
        try:
            self.bge_ranker = BGERanker(self.config.get('bge_config', {}))
        except:
            self.bge_ranker = None
            
        try:
            self.cohere_ranker = CohereRanker(self.config.get('cohere_config', {}))
        except:
            self.cohere_ranker = None
            
        try:
            self.cross_encoder_ranker = CrossEncoderRanker(self.config.get('cross_encoder_config', {}))
        except:
            self.cross_encoder_ranker = None
        
        # 重排序器字典，方便策略选择
        self.rankers = {
            RankStrategy.BGE: self.bge_ranker,
            RankStrategy.COHERE: self.cohere_ranker,
            RankStrategy.CROSS_ENCODER: self.cross_encoder_ranker
        }
    
    def _get_ranker_by_strategy(self, strategy: RankStrategy):
        """根据策略获取对应的重排序器"""
        ranker = self.rankers.get(strategy)
        if ranker is None:
            # 回退到可用的重排序器
            for r in self.rankers.values():
                if r is not None:
                    return r
            raise ValueError("没有可用的重排序器")
        return ranker
    
    # 委托给具体重排序器的方法
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            strategy: Optional[RankStrategy] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """对文档进行重排序（支持策略选择）"""
        ranker = self._get_ranker_by_strategy(strategy or self.strategy)
        return ranker.rank(query, documents, top_k, **kwargs)
    
    def compute_scores(self, 
                      query: str, 
                      texts: List[str],
                      strategy: Optional[RankStrategy] = None,
                      **kwargs) -> List[float]:
        """计算相关性分数（支持策略选择）"""
        ranker = self._get_ranker_by_strategy(strategy or self.strategy)
        return ranker.compute_scores(query, texts, **kwargs)
    
    def set_strategy(self, strategy: Union[RankStrategy, str]) -> None:
        """设置默认重排序策略"""
        self.strategy = RankStrategy(strategy) if isinstance(strategy, str) else strategy
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的重排序策略"""
        return [s.value for s, ranker in self.rankers.items() if ranker is not None]
    
    def compare_strategies(self, 
                          query: str,
                          documents: List[Dict[str, Any]],
                          top_k: Optional[int] = None) -> Dict[str, Any]:
        """比较不同策略的重排序效果"""
        results = {}
        
        for strategy, ranker in self.rankers.items():
            if ranker is None:
                continue
                
            try:
                ranked_docs = ranker.rank(query, documents, top_k)
                results[strategy.value] = {
                    "document_count": len(ranked_docs),
                    "avg_score": sum(doc.get('rerank_score', 0) for doc in ranked_docs) / len(ranked_docs) if ranked_docs else 0,
                    "top_scores": [doc.get('rerank_score', 0) for doc in ranked_docs[:5]]
                }
            except Exception as e:
                results[strategy.value] = {"error": str(e)}
        
        return results
    
    def initialize(self) -> bool:
        """初始化重排序器"""
        self.is_initialized = True
        return True
    
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """对文档进行重排序"""
        if not self.validate_documents(documents):
            return documents
        
        # 预处理查询
        processed_query = self.preprocess_query(query)
        
        # 计算分数
        doc_contents = [doc['content'] for doc in documents]
        scores = self.compute_scores(processed_query, doc_contents, **kwargs)
        
        # 后处理结果
        ranked_docs = self.postprocess_results(documents, scores)
        
        # 按分数排序
        ranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # 应用top_k限制
        if top_k is not None:
            ranked_docs = ranked_docs[:top_k]
        
        return ranked_docs
    
    def compute_scores(self, 
                      query: str,
                      documents: List[str],
                      **kwargs) -> List[float]:
        """计算查询与文档的相关性分数"""
        # 简单的基于关键词匹配的分数计算
        query_terms = set(query.lower().split())
        
        scores = []
        for doc in documents:
            doc_terms = set(doc.lower().split())
            
            # 计算交集比例
            intersection = query_terms.intersection(doc_terms)
            if len(query_terms) > 0:
                score = len(intersection) / len(query_terms)
            else:
                score = 0.0
            
            scores.append(score)
        
        return scores
