"""
向量检索器

基于向量相似度的文档检索。
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from .base_retriever import BaseRetriever


class VectorRetriever(BaseRetriever):
    """向量检索器"""
    
    def __init__(self, vector_db_manager, config: Optional[Dict[str, Any]] = None):
        """
        初始化向量检索器
        
        Args:
            vector_db_manager: 向量数据库管理器
            config: 配置参数
        """
        super().__init__(config)
        self.vector_db = vector_db_manager
    
    def initialize(self) -> bool:
        """初始化检索器"""
        try:
            if hasattr(self.vector_db, 'connect'):
                self.is_initialized = self.vector_db.connect()
            else:
                self.is_initialized = True
            return self.is_initialized
        except Exception as e:
            print(f"初始化向量检索器失败: {str(e)}")
            self.is_initialized = False
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]], **kwargs) -> List[str]:
        """添加文档到检索器"""
        collection_name = kwargs.get('collection_name', 'default')
        return self.vector_db.add_documents(collection_name, documents, **kwargs)
    
    def retrieve(self, 
                query: str,
                top_k: int = 10,
                **kwargs) -> List[Dict[str, Any]]:
        """检索相关文档"""
        collection_name = kwargs.get('collection_name', 'default')
        return self.vector_db.search(collection_name, query, top_k, **kwargs)
    
    def update_documents(self, documents: List[Dict[str, Any]], **kwargs) -> bool:
        """更新文档"""
        collection_name = kwargs.get('collection_name', 'default')
        return self.vector_db.update_documents(collection_name, documents, **kwargs)
    
    def delete_documents(self, document_ids: List[str], **kwargs) -> bool:
        """删除文档"""
        collection_name = kwargs.get('collection_name', 'default')
        return self.vector_db.delete_documents(collection_name, document_ids, **kwargs)
    
    def clear(self) -> bool:
        """清空所有文档"""
        try:
            return self.vector_db.clear()
        except Exception as e:
            print(f"清空文档失败: {str(e)}")
            return False
    
    def count(self) -> int:
        """获取文档数量"""
        collection_name = self.config.get('collection_name', 'default')
        return self.vector_db.count(collection_name)
