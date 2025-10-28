"""
混合检索器

结合BM25检索和向量检索的混合策略。
无状态设计，每次检索时传入内容块列表。
"""

from typing import List, Dict, Any, Optional
from .base_retriever import BaseRetriever
from .bm25_retriever import BM25Retriever
from .vector_retriever import VectorRetriever


class HybridRetriever(BaseRetriever):
    """混合检索器
    
    结合BM25和向量检索，使用加权融合策略。
    """
    
    def __init__(
        self, 
        bm25_retriever: BM25Retriever,
        vector_retriever: VectorRetriever,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        fusion_method: str = 'weighted',
        rrf_k: int = 60
    ):
        """初始化混合检索器
        
        Args:
            bm25_retriever: BM25检索器实例
            vector_retriever: 向量检索器实例
            bm25_weight: BM25检索权重 (默认: 0.5)
            vector_weight: 向量检索权重 (默认: 0.5)
            fusion_method: 融合方法 ('weighted' 或 'rrf'，默认: 'weighted')
            rrf_k: RRF参数k (默认: 60)
        """
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        
        # 归一化权重
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight
        
        # 融合方法
        self.fusion_method = fusion_method
        self.rrf_k = rrf_k
    
    def retrieve(self, 
                query: str,
                chunks: List[Dict[str, Any]],
                top_k: int = 10,
                min_score: Optional[float] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """使用混合策略检索相关内容块
        
        Args:
            query: 查询文本
            chunks: 内容块列表，每个块包含:
                - content: 文本内容
                - metadata: 元数据（可选）
                - id: 块ID（可选）
            top_k: 返回结果数量
            min_score: 最小相关性分数阈值（可选）
            **kwargs: 其他参数
                
        Returns:
            检索结果列表
        """
        if not chunks:
            return []
        
        try:
            # BM25检索
            bm25_results = self.bm25_retriever.retrieve(
                query=query,
                chunks=chunks,
                top_k=top_k * 2,  # 获取更多结果用于融合
                min_score=None,
                **kwargs
            )
            
            # 向量检索
            vector_results = self.vector_retriever.retrieve(
                query=query,
                chunks=chunks,
                top_k=top_k * 2,
                min_score=None,
                **kwargs
            )
            
            # 融合结果
            if self.fusion_method == 'rrf':
                combined_results = self._rrf_fusion(bm25_results, vector_results, top_k)
            else:  # weighted
                combined_results = self._weighted_fusion(bm25_results, vector_results, top_k)
            
            # 应用最小分数阈值
            if min_score is not None:
                combined_results = [r for r in combined_results if r['score'] >= min_score]
            
            return combined_results[:top_k]
            
        except Exception as e:
            print(f"混合检索失败: {str(e)}")
            # 失败时尝试返回向量检索结果
            try:
                return self.vector_retriever.retrieve(query, chunks, top_k, min_score, **kwargs)
            except:
                return []
    
    def _weighted_fusion(self, 
                        bm25_results: List[Dict[str, Any]], 
                        vector_results: List[Dict[str, Any]], 
                        top_k: int) -> List[Dict[str, Any]]:
        """加权融合策略
        
        Args:
            bm25_results: BM25检索结果
            vector_results: 向量检索结果
            top_k: 返回结果数量
            
        Returns:
            融合后的结果列表
        """
        # 归一化分数
        bm25_scores_norm = self._normalize_scores(bm25_results)
        vector_scores_norm = self._normalize_scores(vector_results)
        
        # 创建内容到结果的映射
        content_to_result = {}
        
        # 处理BM25结果
        for i, result in enumerate(bm25_results):
            content = result.get('content', '')
            if content:
                content_to_result[content] = {
                    'content': content,
                    'bm25_score': bm25_scores_norm[i],
                    'vector_score': 0.0
                }
                # 保留metadata和id（如果有）
                if 'metadata' in result:
                    content_to_result[content]['metadata'] = result['metadata']
                if 'id' in result:
                    content_to_result[content]['id'] = result['id']
        
        # 处理向量检索结果
        for i, result in enumerate(vector_results):
            content = result.get('content', '')
            if content in content_to_result:
                content_to_result[content]['vector_score'] = vector_scores_norm[i]
            elif content:
                content_to_result[content] = {
                    'content': content,
                    'bm25_score': 0.0,
                    'vector_score': vector_scores_norm[i]
                }
                # 保留metadata和id（如果有）
                if 'metadata' in result:
                    content_to_result[content]['metadata'] = result['metadata']
                if 'id' in result:
                    content_to_result[content]['id'] = result['id']
        
        # 计算加权分数
        combined_results = []
        for item in content_to_result.values():
            combined_score = (
                self.bm25_weight * item['bm25_score'] + 
                self.vector_weight * item['vector_score']
            )
            
            result = {
                'content': item['content'],
                'score': combined_score
            }
            
            # 如果有metadata，添加到结果中
            if 'metadata' in item:
                result['metadata'] = item['metadata']
            
            # 如果有ID，添加到结果中
            if 'id' in item:
                result['id'] = item['id']
            
            combined_results.append(result)
        
        # 按分数排序
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_results[:top_k]
    
    def _rrf_fusion(self, 
                   bm25_results: List[Dict[str, Any]], 
                   vector_results: List[Dict[str, Any]], 
                   top_k: int) -> List[Dict[str, Any]]:
        """倒数排名融合(Reciprocal Rank Fusion)策略
        
        Args:
            bm25_results: BM25检索结果
            vector_results: 向量检索结果
            top_k: 返回结果数量
            
        Returns:
            融合后的结果列表
        """
        # 创建内容到结果的映射
        content_to_result = {}
        
        # 处理BM25结果
        for rank, result in enumerate(bm25_results):
            content = result.get('content', '')
            if content:
                rrf_score = 1.0 / (self.rrf_k + rank + 1)
                content_to_result[content] = {
                    'content': content,
                    'bm25_rrf': rrf_score,
                    'vector_rrf': 0.0
                }
                # 保留metadata和id（如果有）
                if 'metadata' in result:
                    content_to_result[content]['metadata'] = result['metadata']
                if 'id' in result:
                    content_to_result[content]['id'] = result['id']
        
        # 处理向量检索结果
        for rank, result in enumerate(vector_results):
            content = result.get('content', '')
            rrf_score = 1.0 / (self.rrf_k + rank + 1)
            
            if content in content_to_result:
                content_to_result[content]['vector_rrf'] = rrf_score
            elif content:
                content_to_result[content] = {
                    'content': content,
                    'bm25_rrf': 0.0,
                    'vector_rrf': rrf_score
                }
                # 保留metadata和id（如果有）
                if 'metadata' in result:
                    content_to_result[content]['metadata'] = result['metadata']
                if 'id' in result:
                    content_to_result[content]['id'] = result['id']
        
        # 计算RRF分数
        combined_results = []
        for item in content_to_result.values():
            rrf_score = item['bm25_rrf'] + item['vector_rrf']
            
            result = {
                'content': item['content'],
                'score': rrf_score
            }
            
            # 如果有metadata，添加到结果中
            if 'metadata' in item:
                result['metadata'] = item['metadata']
            
            # 如果有ID，添加到结果中
            if 'id' in item:
                result['id'] = item['id']
            
            combined_results.append(result)
        
        # 按RRF分数排序
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_results[:top_k]
    
    def _normalize_scores(self, results: List[Dict[str, Any]]) -> List[float]:
        """归一化分数到[0, 1]范围
        
        Args:
            results: 检索结果列表
            
        Returns:
            归一化后的分数列表
        """
        if not results:
            return []
        
        scores = [r.get('score', 0.0) for r in results]
        
        min_score = min(scores)
        max_score = max(scores)
        
        # 避免除以零
        if max_score == min_score:
            return [1.0] * len(scores)
        
        # Min-Max归一化
        normalized = [(s - min_score) / (max_score - min_score) for s in scores]
        
        return normalized
    
    def set_weights(self, bm25_weight: float, vector_weight: float):
        """动态调整权重
        
        Args:
            bm25_weight: BM25权重
            vector_weight: 向量权重
        """
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight
