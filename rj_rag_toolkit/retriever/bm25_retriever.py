# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
BM25检索器

基于BM25算法的文本检索器，适用于传统的关键词匹配检索。
无状态设计，每次检索时传入内容块列表。
"""

from typing import Dict, Any, List, Optional
from .base_retriever import BaseRetriever

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class BM25Retriever(BaseRetriever):
    """BM25检索器
    
    使用BM25算法进行文本检索，适合传统的关键词匹配场景。
    """
    
    def __init__(self, 
                 tokenizer: str = 'jieba',
                 k1: float = 1.2,
                 b: float = 0.75,
                 epsilon: float = 0.25,
                 language: str = 'zh'):
        """初始化BM25检索器
        
        Args:
            tokenizer: 分词器名称 ('jieba' 或 'simple'，默认: 'jieba')
            k1: BM25参数k1 (默认: 1.2)
            b: BM25参数b (默认: 0.75)
            epsilon: BM25参数epsilon (默认: 0.25)
            language: 语言设置 ('zh' 或 'en'，默认: 'zh')
        """
        if not BM25_AVAILABLE:
            raise ImportError(
                "rank-bm25 is required for BM25Retriever. "
                "Install it with: pip install rank-bm25"
            )
        
        # BM25参数
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self.language = language
        self.tokenizer_name = tokenizer
        
        # 分词器
        self.tokenizer = self._get_tokenizer()
    
    def _get_tokenizer(self):
        """获取分词器"""
        if self.tokenizer_name == 'jieba' and self.language == 'zh':
            try:
                import jieba
                return lambda text: list(jieba.cut(text))
            except ImportError:
                print("jieba not available, using simple tokenizer")
                return self._simple_tokenizer
        else:
            return self._simple_tokenizer
    
    def _simple_tokenizer(self, text: str) -> List[str]:
        """简单分词器"""
        import re
        # 移除标点符号并转换为小写
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return text.split()
    
    def retrieve(self, 
                query: str,
                chunks: List[Dict[str, Any]],
                top_k: int = 10,
                min_score: Optional[float] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """使用BM25检索相关内容块
        
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
            
            # 对内容块分词
            tokenized_chunks = []
            for chunk in chunks:
                content = chunk.get('content', '')
                tokens = self.tokenizer(content)
                tokenized_chunks.append(tokens)
            
            # 构建BM25模型
            bm25_model = BM25Okapi(
                tokenized_chunks,
                k1=self.k1,
                b=self.b,
                epsilon=self.epsilon
            )
            
            # 查询分词
            query_tokens = self.tokenizer(query)
            
            # BM25检索
            scores = bm25_model.get_scores(query_tokens)
            
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
            print(f"BM25检索失败: {str(e)}")
            return []
