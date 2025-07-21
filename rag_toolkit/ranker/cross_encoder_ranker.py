"""
CrossEncoder重排序器

基于CrossEncoder模型的文档重排序器，使用sentence-transformers库。
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .base_ranker import BaseRanker

try:
    from sentence_transformers import CrossEncoder
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class CrossEncoderRanker(BaseRanker):
    """CrossEncoder重排序器
    
    使用预训练的CrossEncoder模型进行文档重排序。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化CrossEncoder重排序器
        
        Args:
            config: 配置参数，支持以下选项：
                - model_name: 模型名称 (默认: ms-marco-MiniLM-L-12-v2)
                - device: 设备 (cpu/cuda，默认: cpu)
                - max_length: 最大序列长度 (默认: 512)
                - batch_size: 批处理大小 (默认: 32)
                - normalize_scores: 是否归一化分数 (默认: True)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for CrossEncoderRanker. "
                "Install it with: pip install sentence-transformers"
            )
        
        super().__init__(config)
        
        self.model_name = self.config.get('model_name', 'ms-marco-MiniLM-L-12-v2')
        self.device = self.config.get('device', 'cpu')
        self.max_length = self.config.get('max_length', 512)
        self.batch_size = self.config.get('batch_size', 32)
        self.normalize_scores = self.config.get('normalize_scores', True)
        
        self.model = None
    
    def initialize(self) -> bool:
        """初始化CrossEncoder重排序器
        
        Returns:
            初始化是否成功
        """
        try:
            # 加载CrossEncoder模型
            self.model = CrossEncoder(
                model_name=self.model_name,
                max_length=self.max_length,
                device=self.device
            )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"初始化CrossEncoder重排序器失败: {str(e)}")
            self.is_initialized = False
            return False
    
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """使用CrossEncoder对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前K个结果
            **kwargs: 其他参数
                - combine_scores: 是否组合原始分数 (默认: False)
                - alpha: 分数组合权重 (默认: 0.5)
                
        Returns:
            重排序后的文档列表
        """
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
            rerank_scores = self.compute_scores(processed_query, doc_contents, **kwargs)
            
            # 处理分数组合
            combine_scores = kwargs.get('combine_scores', False)
            if combine_scores and all('score' in doc for doc in documents):
                original_scores = [doc['score'] for doc in documents]
                alpha = kwargs.get('alpha', 0.5)
                combined_scores = self.combine_scores(original_scores, rerank_scores, alpha)
                final_scores = combined_scores
            else:
                final_scores = rerank_scores
            
            # 创建结果列表
            ranked_docs = []
            for doc, score in zip(documents, final_scores):
                ranked_doc = doc.copy()
                ranked_doc['rerank_score'] = score
                if combine_scores:
                    ranked_doc['combined_score'] = score
                ranked_docs.append(ranked_doc)
            
            # 按分数排序
            ranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 应用top_k限制
            if top_k is not None:
                ranked_docs = ranked_docs[:top_k]
            
            return ranked_docs
            
        except Exception as e:
            print(f"CrossEncoder重排序失败: {str(e)}")
            return documents
    
    def compute_scores(self, 
                      query: str,
                      documents: List[str],
                      **kwargs) -> List[float]:
        """计算查询与文档的相关性分数
        
        Args:
            query: 查询文本
            documents: 文档内容列表
            **kwargs: 其他参数
                - show_progress: 是否显示进度 (默认: False)
                
        Returns:
            相关性分数列表
        """
        if not self.is_initialized or not self.model:
            return [0.0] * len(documents)
        
        try:
            # 预处理
            processed_query = self.preprocess_query(query)
            processed_docs = self.preprocess_documents(documents)
            
            # 构建查询-文档对
            query_doc_pairs = [[processed_query, doc] for doc in processed_docs]
            
            # 批量预测分数
            show_progress = kwargs.get('show_progress', False)
            scores = self.model.predict(
                query_doc_pairs,
                batch_size=self.batch_size,
                show_progress_bar=show_progress
            )
            
            # 归一化分数
            if self.normalize_scores:
                scores = self._normalize_scores(scores)
            
            return scores.tolist() if hasattr(scores, 'tolist') else list(scores)
            
        except Exception as e:
            print(f"计算CrossEncoder分数失败: {str(e)}")
            return [0.0] * len(documents)
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """归一化分数到[0,1]范围
        
        Args:
            scores: 原始分数数组
            
        Returns:
            归一化后的分数数组
        """
        scores = np.array(scores)
        
        # 使用sigmoid函数归一化
        normalized = 1 / (1 + np.exp(-scores))
        
        return normalized
    
    def predict_batch(self, 
                     query_doc_pairs: List[List[str]],
                     **kwargs) -> List[float]:
        """批量预测查询-文档对的分数
        
        Args:
            query_doc_pairs: 查询-文档对列表
            **kwargs: 其他参数
                
        Returns:
            分数列表
        """
        if not self.is_initialized or not self.model:
            return [0.0] * len(query_doc_pairs)
        
        try:
            show_progress = kwargs.get('show_progress', False)
            scores = self.model.predict(
                query_doc_pairs,
                batch_size=self.batch_size,
                show_progress_bar=show_progress
            )
            
            if self.normalize_scores:
                scores = self._normalize_scores(scores)
            
            return scores.tolist() if hasattr(scores, 'tolist') else list(scores)
            
        except Exception as e:
            print(f"批量预测失败: {str(e)}")
            return [0.0] * len(query_doc_pairs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            模型信息字典
        """
        if not self.is_initialized or not self.model:
            return {}
        
        try:
            return {
                'model_name': self.model_name,
                'max_length': self.max_length,
                'device': str(self.device),
                'num_parameters': getattr(self.model.model, 'num_parameters', lambda: 0)(),
                'model_type': 'CrossEncoder'
            }
        except Exception as e:
            print(f"获取模型信息失败: {str(e)}")
            return {'model_name': self.model_name}
    
    def get_supported_models(self) -> List[str]:
        """获取支持的预训练模型列表
        
        Returns:
            模型名称列表
        """
        return [
            # MS MARCO模型
            'ms-marco-MiniLM-L-12-v2',
            'ms-marco-MiniLM-L-6-v2',
            'ms-marco-MiniLM-L-4-v2',
            'ms-marco-MiniLM-L-2-v2',
            'ms-marco-TinyBERT-L-2-v2',
            'ms-marco-electra-base',
            
            # 多语言模型
            'cross-encoder/ms-marco-MiniLM-L-12-v2',
            'cross-encoder/ms-marco-MiniLM-L-6-v2',
            'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1',
            
            # BGE模型
            'BAAI/bge-reranker-base',
            'BAAI/bge-reranker-large',
            
            # 其他
            'cross-encoder/stsb-roberta-large',
            'cross-encoder/nli-roberta-base'
        ]
    
    def save_model(self, save_path: str) -> bool:
        """保存模型到指定路径
        
        Args:
            save_path: 保存路径
            
        Returns:
            保存是否成功
        """
        if not self.is_initialized or not self.model:
            return False
        
        try:
            self.model.save(save_path)
            return True
        except Exception as e:
            print(f"保存模型失败: {str(e)}")
            return False
    
    def load_model(self, model_path: str) -> bool:
        """从路径加载模型
        
        Args:
            model_path: 模型路径
            
        Returns:
            加载是否成功
        """
        try:
            self.model = CrossEncoder(
                model_name=model_path,
                max_length=self.max_length,
                device=self.device
            )
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            self.is_initialized = False
            return False
