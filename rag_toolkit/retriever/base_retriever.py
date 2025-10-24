"""
检索器基类

定义检索器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseRetriever(ABC):
    """检索器基类
    
    定义所有检索器必须实现的接口。
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化检索器
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]], **kwargs) -> List[str]:
        """添加文档到检索器
        
        Args:
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            文档ID列表
        """
        pass
    
    @abstractmethod
    def retrieve(self, 
                query: str,
                top_k: int = 10,
                **kwargs) -> List[Dict[str, Any]]:
        """检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            检索结果列表
        """
        pass
    
    @abstractmethod
    def delete_documents(self, document_ids: List[str], **kwargs) -> bool:
        """删除文档
        
        Args:
            document_ids: 文档ID列表
            **kwargs: 其他参数
            
        Returns:
            删除是否成功
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空所有文档
        
        Returns:
            清空是否成功
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """获取文档数量
        
        Returns:
            文档数量
        """
        pass

