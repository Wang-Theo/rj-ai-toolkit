"""
Pinecone管理器

基于Pinecone的向量数据库管理实现。
"""

import uuid
from typing import Dict, Any, List, Optional, Union
from .base_db_manager import BaseDBManager

try:
    import pinecone
    from pinecone import Pinecone, PodSpec, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False


class PineconeManager(BaseDBManager):
    """Pinecone管理器
    
    提供基于Pinecone的向量数据库管理功能。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Pinecone管理器
        
        Args:
            config: 配置参数，支持以下选项：
                - api_key: Pinecone API密钥
                - environment: 环境名称
                - dimension: 向量维度
                - metric: 距离度量 (cosine, euclidean, dotproduct)
                - pod_type: Pod类型 (p1, s1等)
                - replicas: 副本数量
                - shards: 分片数量
        """
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "pinecone-client is required for PineconeManager. "
                "Install it with: pip install pinecone-client"
            )
        
        super().__init__(config)
        
        self.api_key = self.config.get('api_key')
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        self.environment = self.config.get('environment', 'us-west1-gcp-free')
        self.dimension = self.config.get('dimension', 768)
        self.metric = self.config.get('metric', 'cosine')
        self.pod_type = self.config.get('pod_type', 'p1')
        self.replicas = self.config.get('replicas', 1)
        self.shards = self.config.get('shards', 1)
        
        self.pc = None
        self.indexes = {}
    
    def connect(self) -> bool:
        """连接Pinecone
        
        Returns:
            连接是否成功
        """
        try:
            self.pc = Pinecone(api_key=self.api_key)
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"连接Pinecone失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开Pinecone连接"""
        if self.pc:
            self.indexes.clear()
            self.pc = None
            self.is_connected = False
    
    def is_healthy(self) -> bool:
        """检查Pinecone健康状态
        
        Returns:
            数据库是否健康
        """
        if not self.is_connected or not self.pc:
            return False
        
        try:
            self.pc.list_indexes()
            return True
        except Exception:
            return False
    
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建索引
        
        Args:
            collection_name: 索引名称
            **kwargs: 其他参数
                - dimension: 向量维度
                - metric: 距离度量
                - spec: 索引规格
                
        Returns:
            创建是否成功
        """
        if not self.is_connected:
            return False
        
        try:
            dimension = kwargs.get('dimension', self.dimension)
            metric = kwargs.get('metric', self.metric)
            
            # 创建索引规格
            spec = kwargs.get('spec')
            if not spec:
                # 默认使用Pod规格
                spec = PodSpec(
                    environment=self.environment,
                    pod_type=self.pod_type,
                    pods=1,
                    replicas=self.replicas,
                    shards=self.shards
                )
            
            # 创建索引
            self.pc.create_index(
                name=collection_name,
                dimension=dimension,
                metric=metric,
                spec=spec
            )
            
            return True
            
        except Exception as e:
            print(f"创建索引失败 {collection_name}: {str(e)}")
            return False
    
    def get_index(self, collection_name: str):
        """获取索引对象
        
        Args:
            collection_name: 索引名称
            
        Returns:
            索引对象
        """
        if collection_name in self.indexes:
            return self.indexes[collection_name]
        
        try:
            index = self.pc.Index(collection_name)
            self.indexes[collection_name] = index
            return index
            
        except Exception as e:
            print(f"获取索引失败 {collection_name}: {str(e)}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除索引
        
        Args:
            collection_name: 索引名称
            
        Returns:
            删除是否成功
        """
        if not self.is_connected:
            return False
        
        try:
            self.pc.delete_index(collection_name)
            self.indexes.pop(collection_name, None)
            return True
            
        except Exception as e:
            print(f"删除索引失败 {collection_name}: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """列出所有索引
        
        Returns:
            索引名称列表
        """
        if not self.is_connected:
            return []
        
        try:
            indexes = self.pc.list_indexes()
            return [idx.name for idx in indexes]
        except Exception as e:
            print(f"列出索引失败: {str(e)}")
            return []
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[Dict[str, Any]],
                     **kwargs) -> List[str]:
        """添加文档
        
        Args:
            collection_name: 索引名称
            documents: 文档列表，每个文档应包含：
                - content: 文档内容
                - embedding: 向量 (必需)
                - metadata: 元数据 (可选)
            **kwargs: 其他参数
                - namespace: 命名空间
                
        Returns:
            文档ID列表
        """
        index = self.get_index(collection_name)
        if not index:
            return []
        
        try:
            # 准备向量数据
            vectors = []
            document_ids = []
            
            for doc in documents:
                if 'embedding' not in doc:
                    continue
                
                doc_id = doc.get('id', str(uuid.uuid4()))
                document_ids.append(doc_id)
                
                metadata = doc.get('metadata', {})
                # 添加内容到元数据
                if 'content' in doc:
                    metadata['content'] = doc['content']
                
                vector_data = {
                    'id': doc_id,
                    'values': doc['embedding'],
                    'metadata': metadata
                }
                vectors.append(vector_data)
            
            # 批量插入
            namespace = kwargs.get('namespace', '')
            batch_size = kwargs.get('batch_size', 100)
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch, namespace=namespace)
            
            return document_ids
            
        except Exception as e:
            print(f"添加文档失败 {collection_name}: {str(e)}")
            return []
    
    def update_documents(self, 
                        collection_name: str,
                        documents: List[Dict[str, Any]],
                        **kwargs) -> bool:
        """更新文档
        
        Args:
            collection_name: 索引名称
            documents: 文档列表
            **kwargs: 其他参数
                - namespace: 命名空间
                
        Returns:
            更新是否成功
        """
        # Pinecone使用upsert操作，与添加文档相同
        result_ids = self.add_documents(collection_name, documents, **kwargs)
        return len(result_ids) > 0
    
    def delete_documents(self, 
                        collection_name: str,
                        document_ids: List[str],
                        **kwargs) -> bool:
        """删除文档
        
        Args:
            collection_name: 索引名称
            document_ids: 文档ID列表
            **kwargs: 其他参数
                - namespace: 命名空间
                
        Returns:
            删除是否成功
        """
        index = self.get_index(collection_name)
        if not index:
            return False
        
        try:
            namespace = kwargs.get('namespace', '')
            index.delete(ids=document_ids, namespace=namespace)
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
            collection_name: 索引名称
            query: 查询向量 (必须是向量，不支持文本查询)
            top_k: 返回结果数量
            **kwargs: 其他参数
                - namespace: 命名空间
                - filter: 元数据过滤条件
                - include_metadata: 是否包含元数据
                - include_values: 是否包含向量值
                
        Returns:
            搜索结果列表
        """
        index = self.get_index(collection_name)
        if not index:
            return []
        
        if isinstance(query, str):
            raise ValueError("Pinecone需要向量查询，不支持文本查询")
        
        try:
            # 构建查询参数
            query_params = {
                'vector': query,
                'top_k': top_k,
                'include_metadata': kwargs.get('include_metadata', True),
                'include_values': kwargs.get('include_values', False),
                'namespace': kwargs.get('namespace', '')
            }
            
            # 添加过滤条件
            if 'filter' in kwargs:
                query_params['filter'] = kwargs['filter']
            
            # 执行查询
            results = index.query(**query_params)
            
            # 格式化结果
            formatted_results = []
            for match in results.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata if match.metadata else {},
                }
                
                # 从元数据中提取内容
                if 'content' in result['metadata']:
                    result['content'] = result['metadata']['content']
                else:
                    result['content'] = ''
                
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"搜索失败 {collection_name}: {str(e)}")
            return []
    
    def count(self, collection_name: str, **kwargs) -> int:
        """统计文档数量
        
        Args:
            collection_name: 索引名称
            **kwargs: 其他参数
                - namespace: 命名空间
                
        Returns:
            文档数量
        """
        index = self.get_index(collection_name)
        if not index:
            return 0
        
        try:
            namespace = kwargs.get('namespace', '')
            stats = index.describe_index_stats()
            
            if namespace:
                namespace_stats = stats.namespaces.get(namespace, {})
                return namespace_stats.get('vector_count', 0)
            else:
                return stats.total_vector_count
                
        except Exception as e:
            print(f"统计文档数量失败 {collection_name}: {str(e)}")
            return 0
    
    def get_index_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取索引统计信息
        
        Args:
            collection_name: 索引名称
            
        Returns:
            统计信息字典
        """
        index = self.get_index(collection_name)
        if not index:
            return {}
        
        try:
            stats = index.describe_index_stats()
            return {
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'total_vector_count': stats.total_vector_count,
                'namespaces': dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            print(f"获取索引统计信息失败 {collection_name}: {str(e)}")
            return {}
