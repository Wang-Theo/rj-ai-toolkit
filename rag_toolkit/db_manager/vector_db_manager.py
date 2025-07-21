"""
向量数据库管理器

基于Chroma的向量数据库管理，支持文档存储和检索。
"""

from typing import List, Dict, Any, Optional, Union
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .base_db_manager import BaseDBManager


class VectorDBManager(BaseDBManager):
    """向量数据库管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化向量数据库管理器
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 初始化嵌入模型
        embeddings_config = config.get("embeddings", {})
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_config.get("model_name", "BAAI/bge-small-zh-v1.5"),
            model_kwargs=embeddings_config.get("model_kwargs", {'device': 'cpu'}),
            encode_kwargs=embeddings_config.get("encode_kwargs", {'normalize_embeddings': True})
        )
        
        # 向量存储实例
        self.vectorstore = None
    
    def connect(self) -> bool:
        """连接数据库"""
        try:
            persist_directory = self.config.get("persist_directory", "./chroma_db")
            collection_name = self.config.get("collection_name", "rag_collection")
            
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接向量数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        self.vectorstore = None
        self.is_connected = False
    
    def is_healthy(self) -> bool:
        """检查数据库健康状态"""
        try:
            if self.vectorstore:
                # 简单的连接测试
                self.vectorstore.similarity_search("test", k=1)
                return True
            return False
        except Exception:
            return False
    
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建集合/表"""
        try:
            # 更新配置并重新连接
            self.config['collection_name'] = collection_name
            return self.connect()
        except Exception as e:
            print(f"创建集合失败: {str(e)}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合/表"""
        try:
            if self.vectorstore:
                self.vectorstore.delete_collection()
            return True
        except Exception as e:
            print(f"删除集合失败: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """列出所有集合/表"""
        return [self.config.get("collection_name", "rag_collection")]
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[Dict[str, Any]],
                     **kwargs) -> List[str]:
        """添加文档"""
        try:
            if not self.vectorstore:
                self.connect()
            
            # 转换为LangChain Document格式
            langchain_docs = []
            for doc in documents:
                langchain_doc = Document(
                    page_content=doc.get('content', ''),
                    metadata=doc.get('metadata', {})
                )
                langchain_docs.append(langchain_doc)
            
            return self.vectorstore.add_documents(langchain_docs)
        except Exception as e:
            print(f"添加文档失败: {str(e)}")
            return []
    
    def update_documents(self, 
                        collection_name: str,
                        documents: List[Dict[str, Any]],
                        **kwargs) -> bool:
        """更新文档"""
        # Chroma不支持直接更新，先删除再添加
        try:
            document_ids = [doc.get('id') for doc in documents if doc.get('id')]
            if document_ids:
                self.delete_documents(collection_name, document_ids)
            
            result_ids = self.add_documents(collection_name, documents, **kwargs)
            return len(result_ids) > 0
        except Exception as e:
            print(f"更新文档失败: {str(e)}")
            return False
    
    def delete_documents(self, 
                        collection_name: str,
                        document_ids: List[str],
                        **kwargs) -> bool:
        """删除文档"""
        try:
            if self.vectorstore:
                self.vectorstore.delete(ids=document_ids)
            return True
        except Exception as e:
            print(f"删除文档失败: {str(e)}")
            return False
    
    def search(self, 
              collection_name: str,
              query: Union[str, List[float]],
              top_k: int = 10,
              **kwargs) -> List[Dict[str, Any]]:
        """搜索文档"""
        try:
            if not self.vectorstore:
                self.connect()
            
            # 只支持文本查询，不支持向量查询
            if isinstance(query, list):
                raise ValueError("VectorDBManager不支持向量查询，请使用文本查询")
            
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            formatted_results = []
            for doc, score in results:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': 1 - score  # 转换为相似度分数
                }
                formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return []
    
    def count(self, collection_name: str, **kwargs) -> int:
        """统计文档数量"""
        try:
            if not self.vectorstore:
                self.connect()
            
            # Chroma的get方法可以获取所有文档信息
            result = self.vectorstore.get()
            return len(result.get('ids', []))
        except Exception:
            return 0
    
    # 保留原有的便捷方法
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """相似性搜索"""
        if not self.vectorstore:
            self.connect()
        return self.vectorstore.similarity_search(query, k=k, filter=filter)
    
    def clear(self) -> bool:
        """清空数据库"""
        try:
            if self.vectorstore:
                self.vectorstore.delete_collection()
            return True
        except Exception:
            return False
