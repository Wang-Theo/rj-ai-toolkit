"""
基础文档解析器

所有文档解析器的基类，定义统一的解析接口。
"""

from abc import ABC, abstractmethod
from typing import List, Union, Optional
from pathlib import Path
from langchain.schema import Document


class BaseParser(ABC):
    """
    基础文档解析器抽象类
    
    所有解析器都需要继承此类并实现抽象方法。
    """
    
    @abstractmethod
    def parse_file(self, file_path: Union[str, Path]) -> Document:
        """
        解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的文档对象
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的扩展名列表
        """
        pass

