"""
重排序器基类

定义重排序器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class BaseRanker(ABC):
    """重排序器基类
    
    定义所有重排序器必须实现的接口。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化重排序器
        
        Args:
            config: 重排序器配置参数
        """
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化重排序器
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表，每个文档包含：
                - content: 文档内容
                - score: 原始分数
                - metadata: 元数据
            top_k: 返回前K个结果 (None表示返回所有结果)
            **kwargs: 其他参数
            
        Returns:
            重排序后的文档列表
        """
        pass
    
    @abstractmethod
    def compute_scores(self, 
                      query: str,
                      documents: List[str],
                      **kwargs) -> List[float]:
        """计算查询与文档的相关性分数
        
        Args:
            query: 查询文本
            documents: 文档内容列表
            **kwargs: 其他参数
            
        Returns:
            相关性分数列表
        """
        pass
    
    def batch_rank(self, 
                  queries: List[str],
                  documents_list: List[List[Dict[str, Any]]],
                  top_k: Optional[int] = None,
                  **kwargs) -> List[List[Dict[str, Any]]]:
        """批量重排序
        
        Args:
            queries: 查询文本列表
            documents_list: 文档列表的列表
            top_k: 返回前K个结果
            **kwargs: 其他参数
            
        Returns:
            重排序后的文档列表的列表
        """
        results = []
        
        for query, documents in zip(queries, documents_list):
            ranked_docs = self.rank(query, documents, top_k, **kwargs)
            results.append(ranked_docs)
        
        return results
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置信息
        
        Returns:
            配置字典
        """
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置信息
        
        Args:
            new_config: 新配置
        """
        self.config.update(new_config)
    
    def is_ready(self) -> bool:
        """检查重排序器是否就绪
        
        Returns:
            是否就绪
        """
        return self.is_initialized
    
    def validate_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """验证文档格式
        
        Args:
            documents: 文档列表
            
        Returns:
            验证是否通过
        """
        for doc in documents:
            if not isinstance(doc, dict):
                return False
            
            # 检查必需字段
            if 'content' not in doc:
                return False
            
            # 检查内容是否为字符串
            if not isinstance(doc['content'], str):
                return False
        
        return True
    
    def preprocess_query(self, query: str) -> str:
        """预处理查询文本
        
        Args:
            query: 原始查询文本
            
        Returns:
            预处理后的查询文本
        """
        # 基础预处理：去除首尾空白
        processed_query = query.strip()
        
        # 可以在子类中重写以添加更多预处理逻辑
        return processed_query
    
    def preprocess_documents(self, documents: List[str]) -> List[str]:
        """预处理文档内容
        
        Args:
            documents: 原始文档内容列表
            
        Returns:
            预处理后的文档内容列表
        """
        # 基础预处理：去除首尾空白
        processed_docs = [doc.strip() for doc in documents]
        
        # 可以在子类中重写以添加更多预处理逻辑
        return processed_docs
    
    def postprocess_results(self, 
                           documents: List[Dict[str, Any]], 
                           scores: List[float]) -> List[Dict[str, Any]]:
        """后处理重排序结果
        
        Args:
            documents: 原始文档列表
            scores: 重排序分数列表
            
        Returns:
            后处理后的文档列表
        """
        # 将新分数添加到文档中
        processed_docs = []
        
        for doc, score in zip(documents, scores):
            processed_doc = doc.copy()
            processed_doc['rerank_score'] = score
            processed_docs.append(processed_doc)
        
        return processed_docs
    
    def combine_scores(self, 
                      original_scores: List[float],
                      rerank_scores: List[float],
                      alpha: float = 0.5) -> List[float]:
        """组合原始分数和重排序分数
        
        Args:
            original_scores: 原始检索分数
            rerank_scores: 重排序分数
            alpha: 组合权重 (0-1之间，0表示只用重排序分数，1表示只用原始分数)
            
        Returns:
            组合后的分数列表
        """
        if len(original_scores) != len(rerank_scores):
            raise ValueError("原始分数和重排序分数的长度必须相同")
        
        # 归一化分数到[0,1]范围
        def normalize_scores(scores):
            if not scores:
                return scores
            
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score == min_score:
                return [1.0] * len(scores)
            
            return [(score - min_score) / (max_score - min_score) for score in scores]
        
        norm_original = normalize_scores(original_scores)
        norm_rerank = normalize_scores(rerank_scores)
        
        # 组合分数
        combined_scores = [
            alpha * orig + (1 - alpha) * rerank
            for orig, rerank in zip(norm_original, norm_rerank)
        ]
        
        return combined_scores
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 子类可以重写以添加清理逻辑
        pass
