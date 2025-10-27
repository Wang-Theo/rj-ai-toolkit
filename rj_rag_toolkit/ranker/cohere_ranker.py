"""
Cohere重排序器

基于Cohere API的文档重排序器。
"""

from typing import Dict, Any, List, Optional
from .base_ranker import BaseRanker

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False


class CohereRanker(BaseRanker):
    """Cohere重排序器
    
    使用Cohere的rerank API进行文档重排序。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Cohere重排序器
        
        Args:
            config: 配置参数，支持以下选项：
                - api_key: Cohere API密钥
                - model: 重排序模型名称 (默认: rerank-multilingual-v2.0)
                - max_tokens_per_doc: 每个文档的最大token数 (默认: 512)
                - batch_size: 批处理大小 (默认: 100)
        """
        if not COHERE_AVAILABLE:
            raise ImportError(
                "cohere is required for CohereRanker. "
                "Install it with: pip install cohere"
            )
        
        super().__init__(config)
        
        self.api_key = self.config.get('api_key')
        if not self.api_key:
            raise ValueError("Cohere API key is required")
        
        self.model = self.config.get('model', 'rerank-multilingual-v2.0')
        self.max_tokens_per_doc = self.config.get('max_tokens_per_doc', 512)
        self.batch_size = self.config.get('batch_size', 100)
        
        self.client = None
    
    def initialize(self) -> bool:
        """初始化Cohere重排序器
        
        Returns:
            初始化是否成功
        """
        try:
            self.client = cohere.Client(api_key=self.api_key)
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"初始化Cohere重排序器失败: {str(e)}")
            self.is_initialized = False
            return False
    
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """使用Cohere API对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前K个结果
            **kwargs: 其他参数
                - return_documents: 是否返回文档内容 (默认: True)
                
        Returns:
            重排序后的文档列表
        """
        if not self.is_initialized or not self.client:
            return documents
        
        if not self.validate_documents(documents):
            return documents
        
        try:
            # 预处理查询
            processed_query = self.preprocess_query(query)
            
            # 提取文档内容
            doc_contents = [doc['content'] for doc in documents]
            processed_contents = self.preprocess_documents(doc_contents)
            
            # 截断过长的文档
            truncated_contents = self._truncate_documents(processed_contents)
            
            # 批量处理
            all_results = []
            
            for i in range(0, len(truncated_contents), self.batch_size):
                batch_contents = truncated_contents[i:i + self.batch_size]
                batch_docs = documents[i:i + self.batch_size]
                
                # 调用Cohere rerank API
                response = self.client.rerank(
                    model=self.model,
                    query=processed_query,
                    documents=batch_contents,
                    top_k=len(batch_contents),  # 获取所有结果
                    return_documents=kwargs.get('return_documents', True)
                )
                
                # 处理响应
                batch_results = self._process_cohere_response(
                    response, batch_docs, batch_contents
                )
                all_results.extend(batch_results)
            
            # 按分数重新排序
            all_results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 应用top_k限制
            if top_k is not None:
                all_results = all_results[:top_k]
            
            return all_results
            
        except Exception as e:
            print(f"Cohere重排序失败: {str(e)}")
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
            
        Returns:
            相关性分数列表
        """
        if not self.is_initialized or not self.client:
            return [0.0] * len(documents)
        
        try:
            # 预处理
            processed_query = self.preprocess_query(query)
            processed_docs = self.preprocess_documents(documents)
            truncated_docs = self._truncate_documents(processed_docs)
            
            # 批量处理
            all_scores = []
            
            for i in range(0, len(truncated_docs), self.batch_size):
                batch_docs = truncated_docs[i:i + self.batch_size]
                
                # 调用API
                response = self.client.rerank(
                    model=self.model,
                    query=processed_query,
                    documents=batch_docs,
                    top_k=len(batch_docs),
                    return_documents=False
                )
                
                # 提取分数
                batch_scores = [0.0] * len(batch_docs)
                for result in response.results:
                    batch_scores[result.index] = result.relevance_score
                
                all_scores.extend(batch_scores)
            
            return all_scores
            
        except Exception as e:
            print(f"计算Cohere分数失败: {str(e)}")
            return [0.0] * len(documents)
    
    def _truncate_documents(self, documents: List[str]) -> List[str]:
        """截断过长的文档
        
        Args:
            documents: 文档内容列表
            
        Returns:
            截断后的文档列表
        """
        truncated_docs = []
        
        for doc in documents:
            # 简单的token估算：按空格分割
            words = doc.split()
            
            if len(words) > self.max_tokens_per_doc:
                # 截断到最大token数
                truncated = ' '.join(words[:self.max_tokens_per_doc])
                truncated_docs.append(truncated)
            else:
                truncated_docs.append(doc)
        
        return truncated_docs
    
    def _process_cohere_response(self, 
                                response, 
                                original_docs: List[Dict[str, Any]],
                                doc_contents: List[str]) -> List[Dict[str, Any]]:
        """处理Cohere API响应
        
        Args:
            response: Cohere API响应
            original_docs: 原始文档列表
            doc_contents: 文档内容列表
            
        Returns:
            处理后的文档列表
        """
        # 创建索引到分数的映射
        score_map = {}
        for result in response.results:
            score_map[result.index] = result.relevance_score
        
        # 更新文档分数
        updated_docs = []
        
        for i, doc in enumerate(original_docs):
            updated_doc = doc.copy()
            updated_doc['rerank_score'] = score_map.get(i, 0.0)
            updated_docs.append(updated_doc)
        
        return updated_docs
    
    def get_supported_models(self) -> List[str]:
        """获取支持的重排序模型列表
        
        Returns:
            模型名称列表
        """
        # Cohere支持的重排序模型
        return [
            'rerank-multilingual-v2.0',
            'rerank-english-v2.0',
            'rerank-multilingual-v3.0',
            'rerank-english-v3.0'
        ]
    
    def estimate_cost(self, num_queries: int, num_documents: int) -> Dict[str, Any]:
        """估算API使用成本
        
        Args:
            num_queries: 查询数量
            num_documents: 文档数量
            
        Returns:
            成本估算信息
        """
        # Cohere rerank API的大概定价（需要根据实际情况调整）
        # 这里提供一个示例估算
        
        total_rerank_requests = num_queries * num_documents
        
        # 假设每1000次rerank请求的成本
        cost_per_1k_requests = 0.002  # 美元，需要根据实际定价调整
        
        estimated_cost = (total_rerank_requests / 1000) * cost_per_1k_requests
        
        return {
            'total_rerank_requests': total_rerank_requests,
            'estimated_cost_usd': round(estimated_cost, 4),
            'cost_per_1k_requests': cost_per_1k_requests,
            'currency': 'USD',
            'note': '这是一个估算值，实际成本可能有所不同'
        }
