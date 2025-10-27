"""
混合检索器

结合向量检索和关键字检索的混合策略。
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import numpy as np
from .base_retriever import BaseRetriever

try:
    from langchain_community.retrievers import BM25Retriever
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class HybridRetriever(BaseRetriever):
    """混合检索器 - 结合向量检索和BM25检索"""
    
    def __init__(
        self, 
        vector_db_manager,
        config: Optional[Dict[str, Any]] = None,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5
    ):
        """
        初始化混合检索器
        
        Args:
            vector_db_manager: 向量数据库管理器
            config: 配置参数
            bm25_weight: BM25检索权重
            vector_weight: 向量检索权重
        """
        super().__init__(config)
        self.vector_db = vector_db_manager
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.bm25_retriever = None
        self.documents = []  # 存储文档用于BM25
        
        # 确保权重总和为1
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight
    
    def initialize(self) -> bool:
        """初始化检索器"""
        try:
            if hasattr(self.vector_db, 'connect'):
                self.is_initialized = self.vector_db.connect()
            else:
                self.is_initialized = True
            return self.is_initialized
        except Exception as e:
            print(f"初始化混合检索器失败: {str(e)}")
            self.is_initialized = False
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]], **kwargs) -> List[str]:
        """添加文档到检索器"""
        # 添加到向量数据库
        collection_name = kwargs.get('collection_name', 'default')
        result_ids = self.vector_db.add_documents(collection_name, documents, **kwargs)
        
        # 转换为LangChain Document格式并存储用于BM25
        for doc in documents:
            langchain_doc = Document(
                page_content=doc.get('content', ''),
                metadata=doc.get('metadata', {})
            )
            self.documents.append(langchain_doc)
        
        # 重建BM25检索器
        self._build_bm25_retriever()
        
        return result_ids
    
    def _build_bm25_retriever(self) -> None:
        """构建BM25检索器"""
        if BM25_AVAILABLE and self.documents:
            try:
                texts = [doc.page_content for doc in self.documents]
                metadatas = [doc.metadata for doc in self.documents]
                self.bm25_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
            except Exception as e:
                print(f"构建BM25检索器失败: {str(e)}")
                self.bm25_retriever = None
    
    def retrieve(self, 
                query: str,
                top_k: int = 10,
                **kwargs) -> List[Dict[str, Any]]:
        """混合检索策略"""
        try:
            # 向量检索
            collection_name = kwargs.get('collection_name', 'default')
            vector_results = self.vector_db.search(collection_name, query, top_k * 2, **kwargs)
            
            # BM25检索
            bm25_results = []
            if self.bm25_retriever:
                try:
                    bm25_docs = self.bm25_retriever.get_relevant_documents(query)[:top_k * 2]
                    bm25_results = [
                        {
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'score': 1.0  # BM25没有直接的分数，使用固定值
                        }
                        for doc in bm25_docs
                    ]
                except Exception as e:
                    print(f"BM25检索失败: {str(e)}")
            
            # 合并和重排序结果
            combined_results = self._combine_results(vector_results, bm25_results, top_k)
            
            return combined_results
            
        except Exception as e:
            print(f"混合检索失败: {str(e)}")
            # 如果混合检索失败，至少返回向量检索结果
            try:
                collection_name = kwargs.get('collection_name', 'default')
                return self.vector_db.search(collection_name, query, top_k, **kwargs)
            except:
                return []
    
    def _combine_results(self, 
                        vector_results: List[Dict[str, Any]], 
                        bm25_results: List[Dict[str, Any]], 
                        top_k: int) -> List[Dict[str, Any]]:
        """合并和重排序结果"""
        # 创建内容到结果的映射
        content_to_result = {}
        
        # 处理向量检索结果
        for result in vector_results:
            content = result.get('content', '')
            if content:
                content_to_result[content] = {
                    'content': content,
                    'metadata': result.get('metadata', {}),
                    'vector_score': result.get('score', 0.0),
                    'bm25_score': 0.0
                }
        
        # 处理BM25检索结果
        for result in bm25_results:
            content = result.get('content', '')
            if content in content_to_result:
                content_to_result[content]['bm25_score'] = result.get('score', 0.0)
            elif content:
                content_to_result[content] = {
                    'content': content,
                    'metadata': result.get('metadata', {}),
                    'vector_score': 0.0,
                    'bm25_score': result.get('score', 0.0)
                }
        
        # 计算组合分数
        combined_results = []
        for result in content_to_result.values():
            combined_score = (
                self.vector_weight * result['vector_score'] + 
                self.bm25_weight * result['bm25_score']
            )
            
            combined_results.append({
                'content': result['content'],
                'metadata': result['metadata'],
                'score': combined_score,
                'vector_score': result['vector_score'],
                'bm25_score': result['bm25_score']
            })
        
        # 按组合分数排序
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_results[:top_k]
    
    def update_documents(self, documents: List[Dict[str, Any]], **kwargs) -> bool:
        """更新文档"""
        try:
            # 更新向量数据库
            collection_name = kwargs.get('collection_name', 'default')
            vector_updated = self.vector_db.update_documents(collection_name, documents, **kwargs)
            
            # 重建BM25索引（简单方法：清空重建）
            self.clear()
            self.add_documents(documents, **kwargs)
            
            return vector_updated
        except Exception as e:
            print(f"更新文档失败: {str(e)}")
            return False
    
    def delete_documents(self, document_ids: List[str], **kwargs) -> bool:
        """删除文档"""
        try:
            # 从向量数据库删除
            collection_name = kwargs.get('collection_name', 'default')
            vector_deleted = self.vector_db.delete_documents(collection_name, document_ids, **kwargs)
            
            # 从本地文档列表删除（通过内容匹配，这是一个简化的实现）
            # 在实际应用中，应该有更好的ID管理机制
            self.documents = [doc for doc in self.documents 
                            if doc.metadata.get('id') not in document_ids]
            
            # 重建BM25检索器
            self._build_bm25_retriever()
            
            return vector_deleted
        except Exception as e:
            print(f"删除文档失败: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """清空所有文档"""
        try:
            # 清空向量数据库
            vector_cleared = self.vector_db.clear()
            
            # 清空本地文档和BM25检索器
            self.documents.clear()
            self.bm25_retriever = None
            
            return vector_cleared
        except Exception as e:
            print(f"清空文档失败: {str(e)}")
            return False
    
    def count(self) -> int:
        """获取文档数量"""
        collection_name = self.config.get('collection_name', 'default')
        return self.vector_db.count(collection_name)
    
    def set_weights(self, bm25_weight: float, vector_weight: float):
        """动态调整权重"""
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight
