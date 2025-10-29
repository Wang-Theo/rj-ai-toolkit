# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
向量检索器

基于向量相似度的文本检索。
无状态设计，每次检索时传入内容块列表和embedding模型。
"""

from typing import List, Dict, Any, Optional, Callable
from .base_retriever import BaseRetriever


class VectorRetriever(BaseRetriever):
    """向量检索器
    
    使用向量相似度进行文本检索。
    """
    
    def __init__(self, 
                 embedding_function: Callable,
                 similarity_metric: str = 'cosine'):
        """初始化向量检索器
        
        Args:
            embedding_function: 文本嵌入函数，接受文本列表，返回向量列表
            similarity_metric: 相似度度量方式 ('cosine', 'euclidean', 'dot'，默认: 'cosine')
        """
        self.embedding_function = embedding_function
        self.similarity_metric = similarity_metric
    
    def retrieve(self, 
                query: str,
                chunks: List[Dict[str, Any]],
                top_k: int = 10,
                min_score: Optional[float] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """使用向量相似度检索相关内容块
        
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
            import numpy as np
            
            # 提取内容文本
            chunk_texts = [chunk.get('content', '') for chunk in chunks]
            
            # 生成查询向量
            query_embedding = self.embedding_function([query])[0]
            
            # 生成文档向量
            chunk_embeddings = self.embedding_function(chunk_texts)
            
            # 计算相似度
            scores = self._calculate_similarity(query_embedding, chunk_embeddings)
            
            # 获取top_k结果
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # 构建结果
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                
                # 应用最小分数阈值
                if min_score is not None and score < min_score:
                    continue
                
                chunk = chunks[idx]
                result = {
                    'content': chunk.get('content', ''),
                    'score': score
                }
                
                # 如果有metadata，添加到结果中
                if 'metadata' in chunk:
                    result['metadata'] = chunk['metadata']
                
                # 如果有ID，添加到结果中
                if 'id' in chunk:
                    result['id'] = chunk['id']
                
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"向量检索失败: {str(e)}")
            return []
    
    def _calculate_similarity(self, query_embedding, chunk_embeddings):
        """计算相似度分数
        
        Args:
            query_embedding: 查询向量
            chunk_embeddings: 文档向量列表
            
        Returns:
            相似度分数数组
        """
        import numpy as np
        
        query_vec = np.array(query_embedding)
        chunk_vecs = np.array(chunk_embeddings)
        
        if self.similarity_metric == 'cosine':
            # 余弦相似度
            query_norm = np.linalg.norm(query_vec)
            chunk_norms = np.linalg.norm(chunk_vecs, axis=1)
            
            # 避免除以零
            query_norm = query_norm if query_norm > 0 else 1e-10
            chunk_norms = np.where(chunk_norms > 0, chunk_norms, 1e-10)
            
            similarities = np.dot(chunk_vecs, query_vec) / (chunk_norms * query_norm)
            return similarities
            
        elif self.similarity_metric == 'dot':
            # 点积相似度
            return np.dot(chunk_vecs, query_vec)
            
        elif self.similarity_metric == 'euclidean':
            # 欧氏距离（转换为相似度分数）
            distances = np.linalg.norm(chunk_vecs - query_vec, axis=1)
            # 转换为相似度：距离越小，相似度越高
            similarities = 1 / (1 + distances)
            return similarities
            
        else:
            raise ValueError(f"不支持的相似度度量方式: {self.similarity_metric}")
