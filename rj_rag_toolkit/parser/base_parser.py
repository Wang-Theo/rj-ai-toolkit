"""
基础文档解析器

所有文档解析器的基类，定义统一的解析接口。
文件传入，Markdown格式文字传出。
"""

from abc import ABC, abstractmethod
from typing import List, Union, Optional
from pathlib import Path


class BaseParser(ABC):
    """
    基础文档解析器抽象类
    
    所有解析器都需要继承此类并实现抽象方法。
    解析器接收文件路径，返回Markdown格式的文本内容。
    """
    
    def __init__(self, use_ocr: bool = False, ocr_func=None):
        """
        初始化解析器
        
        Args:
            use_ocr: 是否使用OCR功能,默认False
            ocr_func: OCR处理函数,接收图片路径返回文本。签名: func(image_path: str) -> str
        """
        self.use_ocr = use_ocr
        self.ocr_func = ocr_func
        self.image_dpi = 300  # 图片 DPI (dots per inch)
    
    def _call_ocr(self, image_path: str) -> str:
        """
        调用OCR函数处理图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            OCR识别的文本内容，如果未配置OCR或识别失败返回空字符串
        """
        if not self.use_ocr or not self.ocr_func:
            return ""
        
        try:
            return self.ocr_func(image_path)
        except Exception:
            return ""
    
    @abstractmethod
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        解析文件为Markdown格式文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            Markdown格式的文本内容
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的扩展名列表，例如: ['.pdf', '.txt']
        """
        pass

