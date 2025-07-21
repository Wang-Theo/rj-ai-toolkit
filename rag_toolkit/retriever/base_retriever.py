"""
检索器基类

定义检索器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class BaseRetriever(ABC):
    """检索器基类
    
    定义所有检索器必须实现的接口。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化检索器
        
        Args:
            config: 检索器配置参数
        """
        self.config = config or {}
        self.is_initialized = False
    
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
            检索结果列表，每个结果包含：
                - content: 文档内容
                - score: 相关性分数
                - metadata: 元数据
        """
        pass
    
    @abstractmethod
    def update_documents(self, documents: List[Dict[str, Any]], **kwargs) -> bool:
        """更新文档
        
        Args:
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            更新是否成功
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
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置信息
        
        Returns:
            配置字典
        """
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置信息
        
        Args:
            new_config: 新配置
        """
        self.config.update(new_config)
    
    def is_ready(self) -> bool:
        """检查检索器是否就绪
        
        Returns:
            是否就绪
        """
        return self.is_initialized
    
    def validate_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """验证文档格式
        
        Args:
            documents: 文档列表
            
        Returns:
            验证是否通过
        """
        for doc in documents:
            if not isinstance(doc, dict):
                return False
            
            # 检查必需字段
            if 'content' not in doc:
                return False
            
            # 检查内容是否为字符串
            if not isinstance(doc['content'], str):
                return False
        
        return True
    
    def preprocess_query(self, query: str) -> str:
        """预处理查询文本
        
        Args:
            query: 原始查询文本
            
        Returns:
            预处理后的查询文本
        """
        # 基础预处理：去除首尾空白
        processed_query = query.strip()
        
        # 可以在子类中重写以添加更多预处理逻辑
        return processed_query
    
    def postprocess_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """后处理检索结果
        
        Args:
            results: 原始检索结果
            
        Returns:
            后处理后的检索结果
        """
        # 确保每个结果都有必需的字段
        processed_results = []
        
        for result in results:
            processed_result = {
                'content': result.get('content', ''),
                'score': result.get('score', 0.0),
                'metadata': result.get('metadata', {}),
                'id': result.get('id', '')
            }
            processed_results.append(processed_result)
        
        return processed_results
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 子类可以重写以添加清理逻辑
        pass
