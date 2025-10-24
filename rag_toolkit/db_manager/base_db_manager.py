"""
数据库管理器基类

定义数据库管理器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class BaseDBManager(ABC):
    """数据库管理器基类
    
    定义所有数据库管理器必须实现的接口。
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据库
        
        Returns:
            连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """检查数据库健康状态
        
        Returns:
            数据库是否健康
        """
        pass
    
    @abstractmethod
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建集合/表
        
        Args:
            collection_name: 集合名称
            **kwargs: 其他参数
            
        Returns:
            创建是否成功
        """
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合/表
        
        Args:
            collection_name: 集合名称
            
        Returns:
            删除是否成功
        """
        pass
    
    @abstractmethod
    def list_collections(self) -> List[str]:
        """列出所有集合/表
        
        Returns:
            集合名称列表
        """
        pass
    
    @abstractmethod
    def add_documents(self, 
                     collection_name: str,
                     documents: List[Dict[str, Any]],
                     **kwargs) -> List[str]:
        """添加文档
        
        Args:
            collection_name: 集合名称
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            文档ID列表
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
            
        Returns:
            搜索结果列表
        """
        pass
    
    @abstractmethod
    def count(self, collection_name: str, **kwargs) -> int:
        """统计文档数量
        
        Args:
            collection_name: 集合名称
            **kwargs: 过滤条件
            
        Returns:
            文档数量
        """
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

