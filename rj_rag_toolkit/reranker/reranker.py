"""
通用重排序器

对检索结果进行重排序，提高检索精度。
"""

from typing import List, Dict, Any, Optional
import numpy as np


class Reranker:
    """通用重排序器
    
    使用重排序函数对检索结果进行重排序。
    """
    
    def __init__(self, rerank_function):
        """初始化重排序器
        
        Args:
            rerank_function: 重排序函数，接受 (query, doc) 返回分数
        """
        self.rerank_function = rerank_function
    
    def rerank(self, 
               query: str,
               chunks: List[Dict[str, Any]],
               top_k: Optional[int] = None,
               **kwargs) -> List[Dict[str, Any]]:
        """对内容块进行重排序
        
        Args:
            query: 查询文本
            chunks: 内容块列表，每个块包含:
                - content: 文本内容 (必需)
                - score: 原始分数（可选）
                - metadata: 元数据（可选）
                - id: 块ID（可选）
            top_k: 返回前K个结果（可选）
            **kwargs: 其他参数（保留用于扩展）
                
        Returns:
            重排序后的内容块列表，每个结果包含:
                - content: 内容块文本
                - rerank_score: 重排序分数
                - score: 原始分数（如果输入中有）
                - metadata: 元数据（如果输入中有）
                - id: 块ID（如果输入中有）
        """
        if not chunks:
            return []
        
        try:
            # 提取文档内容
            contents = [chunk.get('content', '') for chunk in chunks]
            
            # 计算重排序分数
            scores = []
            for content in contents:
                score = self.rerank_function(query, content)
                scores.append(score)
            
            # 使用sigmoid归一化分数
            normalized_scores = self._normalize_scores(scores)
            
            # 构建结果
            results = []
            for i, chunk in enumerate(chunks):
                result = {
                    'content': chunk.get('content', ''),
                    'rerank_score': float(normalized_scores[i])
                }
                
                # 保留原始分数（如果有）
                if 'score' in chunk:
                    result['score'] = chunk['score']
                
                # 保留metadata（如果有）
                if 'metadata' in chunk:
                    result['metadata'] = chunk['metadata']
                
                # 保留ID（如果有）
                if 'id' in chunk:
                    result['id'] = chunk['id']
                
                results.append(result)
            
            # 按重排序分数排序
            results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 应用top_k限制
            if top_k is not None:
                results = results[:top_k]
            
            return results
            
        except Exception as e:
            print(f"重排序失败: {str(e)}")
            return chunks
    
    def _normalize_scores(self, scores) -> np.ndarray:
        """使用sigmoid函数归一化分数到[0, 1]"""
        scores_array = np.array(scores)
        return 1 / (1 + np.exp(-scores_array))
