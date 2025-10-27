"""
基于BGE模型的重排序器

使用BGE重排序模型提高检索精度。
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import numpy as np
from .base_ranker import BaseRanker

try:
    from sentence_transformers import CrossEncoder
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class BGERanker(BaseRanker):
    """BGE重排序器"""
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-reranker-base",
        device: str = "cpu",
        max_length: int = 512,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化BGE重排序器
        
        Args:
            model_name: 重排序模型名称
            device: 设备 (cpu/cuda)
            max_length: 最大序列长度
            config: 额外配置参数
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for BGERanker. "
                "Install it with: pip install sentence-transformers"
            )
        
        super().__init__(config)
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.batch_size = config.get('batch_size', 32) if config else 32
        
        self.model = None
    
    def initialize(self) -> bool:
        """初始化BGE重排序器"""
        try:
            self.model = CrossEncoder(
                self.model_name, 
                device=self.device,
                max_length=self.max_length
            )
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"初始化BGE重排序模型失败: {e}")
            self.is_initialized = False
            return False
    
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """使用BGE模型对文档进行重排序"""
        if not self.is_initialized or not self.model:
            return documents
        
        if not self.validate_documents(documents):
            return documents
        
        try:
            # 预处理查询
            processed_query = self.preprocess_query(query)
            
            # 提取文档内容
            doc_contents = [doc['content'] for doc in documents]
            
            # 计算重排序分数
            scores = self.compute_scores(processed_query, doc_contents, **kwargs)
            
            # 后处理结果
            ranked_docs = self.postprocess_results(documents, scores)
            
            # 按分数排序
            ranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 应用top_k限制
            if top_k is not None:
                ranked_docs = ranked_docs[:top_k]
            
            return ranked_docs
            
        except Exception as e:
            print(f"BGE重排序失败: {str(e)}")
            return documents
    
    def compute_scores(self, 
                      query: str,
                      documents: List[str],
                      **kwargs) -> List[float]:
        """计算查询与文档的相关性分数"""
        if not self.is_initialized or not self.model:
            return [0.0] * len(documents)
        
        try:
            # 预处理文档
            processed_docs = self.preprocess_documents(documents)
            
            # 构建查询-文档对
            query_doc_pairs = [[query, doc] for doc in processed_docs]
            
            # 批量计算分数
            scores = self.model.predict(
                query_doc_pairs,
                batch_size=self.batch_size,
                show_progress_bar=kwargs.get('show_progress', False)
            )
            
            # 使用sigmoid归一化分数
            normalized_scores = self._normalize_scores(scores)
            
            return normalized_scores.tolist() if hasattr(normalized_scores, 'tolist') else list(normalized_scores)
            
        except Exception as e:
            print(f"计算BGE分数失败: {str(e)}")
            return [0.0] * len(documents)
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """使用sigmoid函数归一化分数"""
        return 1 / (1 + np.exp(-np.array(scores)))
    
    def batch_rank(self, 
                  queries: List[str],
                  documents_list: List[List[Dict[str, Any]]],
                  top_k: Optional[int] = None,
                  **kwargs) -> List[List[Dict[str, Any]]]:
        """批量重排序"""
        results = []
        
        for query, documents in zip(queries, documents_list):
            ranked_docs = self.rank(query, documents, top_k, **kwargs)
            results.append(ranked_docs)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'max_length': self.max_length,
            'batch_size': self.batch_size,
            'is_initialized': self.is_initialized
        }
    
    def get_supported_models(self) -> List[str]:
        """获取支持的BGE重排序模型"""
        return [
            "BAAI/bge-reranker-base",
            "BAAI/bge-reranker-large",
            "BAAI/bge-reranker-v2-m3",
            "BAAI/bge-reranker-v2-gemma",
            "BAAI/bge-reranker-v2-minicpm-layerwise"
        ]
