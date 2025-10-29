# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
检索器基类

定义检索器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseRetriever(ABC):
    """检索器基类
    
    定义所有检索器必须实现的接口。
    检索器采用无状态设计，每次检索时传入内容块列表。
    """
    
    @abstractmethod
    def retrieve(self, 
                query: str,
                chunks: List[Dict[str, Any]],
                top_k: int = 10,
                min_score: Optional[float] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """检索相关内容块
        
        Args:
            query: 查询文本
            chunks: 内容块列表，每个块包含:
                - content: 文本内容 (必需)
                - metadata: 元数据（可选）
                - id: 块ID（可选）
            top_k: 返回结果数量
            min_score: 最小相关性分数阈值（可选）
            **kwargs: 其他参数
            
        Returns:
            检索结果列表，每个结果包含:
                - content: 内容块文本
                - score: 相关性分数
                - metadata: 元数据（如果输入中有）
                - id: 块ID（如果输入中有）
        """
        pass

