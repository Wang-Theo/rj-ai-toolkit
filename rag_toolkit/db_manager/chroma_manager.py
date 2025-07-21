"""
ChromaDB管理器

基于ChromaDB的向量数据库管理实现。
"""

import os
import uuid
from typing import Dict, Any, List, Optional, Union
from .base_db_manager import BaseDBManager

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ChromaManager(BaseDBManager):
    """ChromaDB管理器
    
    提供基于ChromaDB的向量数据库管理功能。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化ChromaDB管理器
        
        Args:
            config: 配置参数，支持以下选项：
                - persist_directory: 数据持久化目录
                - host: 服务器地址 (HTTP客户端模式)
                - port: 服务器端口 (HTTP客户端模式)
                - anonymized_telemetry: 是否启用匿名遥测
        """
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "chromadb is required for ChromaManager. "
                "Install it with: pip install chromadb"
            )
        
        super().__init__(config)
        
        self.persist_directory = self.config.get('persist_directory', './chroma_db')
        self.host = self.config.get('host')
        self.port = self.config.get('port', 8000)
        
        self.client = None
        self.collections = {}
    
    def connect(self) -> bool:
        """连接ChromaDB
        
        Returns:
            连接是否成功
        """
        try:
            if self.host:
                # HTTP客户端模式
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port
                )
            else:
                # 本地持久化模式
                os.makedirs(self.persist_directory, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=self.config.get('anonymized_telemetry', False)
                    )
                )
            
            # 测试连接
            self.client.heartbeat()
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"连接ChromaDB失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开ChromaDB连接"""
        if self.client:
            self.collections.clear()
            self.client = None
            self.is_connected = False
    
    def is_healthy(self) -> bool:
        """检查ChromaDB健康状态
        
        Returns:
            数据库是否健康
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False
    
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建集合
        
        Args:
            collection_name: 集合名称
            **kwargs: 其他参数
                - embedding_function: 嵌入函数
                - metadata: 集合元数据
                
        Returns:
            创建是否成功
        """
        if not self.is_connected:
            return False
        
        try:
            embedding_function = kwargs.get('embedding_function')
            metadata = kwargs.get('metadata', {})
            
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata=metadata
            )
            
            self.collections[collection_name] = collection
            return True
            
        except Exception as e:
            print(f"创建集合失败 {collection_name}: {str(e)}")
            return False
    
    def get_or_create_collection(self, collection_name: str, **kwargs):
        """获取或创建集合
        
        Args:
            collection_name: 集合名称
            **kwargs: 创建参数
            
        Returns:
            集合对象
        """
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        try:
            embedding_function = kwargs.get('embedding_function')
            metadata = kwargs.get('metadata', {})
            
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata=metadata
            )
            
            self.collections[collection_name] = collection
            return collection
            
        except Exception as e:
            print(f"获取或创建集合失败 {collection_name}: {str(e)}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            删除是否成功
        """
        if not self.is_connected:
            return False
        
        try:
            self.client.delete_collection(name=collection_name)
            self.collections.pop(collection_name, None)
            return True
            
        except Exception as e:
            print(f"删除集合失败 {collection_name}: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """列出所有集合
        
        Returns:
            集合名称列表
        """
        if not self.is_connected:
            return []
        
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"列出集合失败: {str(e)}")
            return []
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[Dict[str, Any]],
                     **kwargs) -> List[str]:
        """添加文档
        
        Args:
            collection_name: 集合名称
            documents: 文档列表，每个文档应包含：
                - content: 文档内容
                - metadata: 元数据 (可选)
                - embedding: 向量 (可选)
            **kwargs: 其他参数
            
        Returns:
            文档ID列表
        """
        collection = self.get_or_create_collection(collection_name, **kwargs)
        if not collection:
            return []
        
        try:
            # 准备数据
            ids = []
            contents = []
            embeddings = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get('id', str(uuid.uuid4()))
                ids.append(doc_id)
                contents.append(doc.get('content', ''))
                
                if 'embedding' in doc:
                    embeddings.append(doc['embedding'])
                
                metadata = doc.get('metadata', {})
                metadatas.append(metadata)
            
            # 添加到集合
            add_params = {
                'ids': ids,
                'documents': contents,
                'metadatas': metadatas
            }
            
            if embeddings:
                add_params['embeddings'] = embeddings
            
            collection.add(**add_params)
            return ids
            
        except Exception as e:
            print(f"添加文档失败 {collection_name}: {str(e)}")
            return []
    
    def update_documents(self, 
                        collection_name: str,
                        documents: List[Dict[str, Any]],
                        **kwargs) -> bool:
        """更新文档
        
        Args:
            collection_name: 集合名称
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            更新是否成功
        """
        collection = self.get_or_create_collection(collection_name, **kwargs)
        if not collection:
            return False
        
        try:
            # 准备数据
            ids = []
            contents = []
            embeddings = []
            metadatas = []
            
            for doc in documents:
                if 'id' not in doc:
                    continue
                
                ids.append(doc['id'])
                contents.append(doc.get('content', ''))
                
                if 'embedding' in doc:
                    embeddings.append(doc['embedding'])
                
                metadata = doc.get('metadata', {})
                metadatas.append(metadata)
            
            # 更新集合
            update_params = {
                'ids': ids,
                'documents': contents,
                'metadatas': metadatas
            }
            
            if embeddings:
                update_params['embeddings'] = embeddings
            
            collection.update(**update_params)
            return True
            
        except Exception as e:
            print(f"更新文档失败 {collection_name}: {str(e)}")
            return False
    
    def delete_documents(self, 
                        collection_name: str,
                        document_ids: List[str],
                        **kwargs) -> bool:
        """删除文档
        
        Args:
            collection_name: 集合名称
            document_ids: 文档ID列表
            **kwargs: 其他参数
            
        Returns:
            删除是否成功
        """
        collection = self.get_or_create_collection(collection_name, **kwargs)
        if not collection:
            return False
        
        try:
            collection.delete(ids=document_ids)
            return True
            
        except Exception as e:
            print(f"删除文档失败 {collection_name}: {str(e)}")
            return False
    
    def search(self, 
              collection_name: str,
              query: Union[str, List[float]],
              top_k: int = 10,
              **kwargs) -> List[Dict[str, Any]]:
        """搜索文档
        
        Args:
            collection_name: 集合名称
            query: 查询内容或向量
            top_k: 返回结果数量
            **kwargs: 其他参数
                - where: 元数据过滤条件
                - where_document: 文档内容过滤条件
                
        Returns:
            搜索结果列表
        """
        collection = self.get_or_create_collection(collection_name, **kwargs)
        if not collection:
            return []
        
        try:
            # 构建查询参数
            query_params = {
                'n_results': top_k,
                'include': ['documents', 'metadatas', 'distances']
            }
            
            if isinstance(query, str):
                query_params['query_texts'] = [query]
            else:
                query_params['query_embeddings'] = [query]
            
            # 添加过滤条件
            if 'where' in kwargs:
                query_params['where'] = kwargs['where']
            
            if 'where_document' in kwargs:
                query_params['where_document'] = kwargs['where_document']
            
            # 执行查询
            results = collection.query(**query_params)
            
            # 格式化结果
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i] if results['documents'] else '',
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1 - results['distances'][0][i] if results['distances'] else 0.0  # 转换为相似度
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"搜索失败 {collection_name}: {str(e)}")
            return []
    
    def count(self, collection_name: str, **kwargs) -> int:
        """统计文档数量
        
        Args:
            collection_name: 集合名称
            **kwargs: 过滤条件
            
        Returns:
            文档数量
        """
        collection = self.get_or_create_collection(collection_name, **kwargs)
        if not collection:
            return 0
        
        try:
            return collection.count()
        except Exception as e:
            print(f"统计文档数量失败 {collection_name}: {str(e)}")
            return 0
