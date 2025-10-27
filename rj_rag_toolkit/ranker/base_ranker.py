"""
重排序器基类

定义重排序器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseRanker(ABC):
    """重排序器基类
    
    定义所有重排序器必须实现的接口。
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化重排序器
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def rank(self, 
            query: str,
            documents: List[Dict[str, Any]],
            top_k: Optional[int] = None,
            **kwargs) -> List[Dict[str, Any]]:
        """对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前K个结果
            **kwargs: 其他参数
            
        Returns:
            重排序后的文档列表
        """
        pass
    
    @abstractmethod
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
        pass

