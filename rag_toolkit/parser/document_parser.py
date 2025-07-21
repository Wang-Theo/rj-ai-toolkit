"""
统一文档解析器

支持多种文档格式的统一解析接口的策略管理器。
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from langchain.schema import Document
from .base_parser import ParseConfig
from .text_parser import TextParser
from .pdf_parser import PDFParser
from .word_parser import WordParser
from .markdown_parser import MarkdownParser


class DocumentParser:
    """
    文档解析策略管理器
    
    不是解析器本身，而是管理和选择不同解析器的门面类。
    """
    
    def __init__(self, config: Optional[ParseConfig] = None):
        """
        初始化文档解析策略管理器
        
        Args:
            config: 解析配置
        """
        self.config = config or ParseConfig()
        
        # 初始化各种解析器
        self.parsers = {
            # 文本文件
            'txt': TextParser(self.config),
            'text': TextParser(self.config),
            
            # Markdown文件
            'md': MarkdownParser(self.config),
            'markdown': MarkdownParser(self.config),
            
            # PDF文件
            'pdf': PDFParser(self.config),
            
            # Word文件
            'docx': WordParser(self.config),
            'doc': WordParser(self.config)
        }
    
    def parse_file(self, file_path: Union[str, Path]) -> Document:
        """委托给对应的解析器处理文件"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower().lstrip('.')
        
        if ext not in self.parsers:
            raise ValueError(f"不支持的文件类型: {ext}，支持的类型: {list(self.parsers.keys())}")
        
        parser = self.parsers[ext]
        return parser.parse_file(file_path)
    
    def parse_files(self, file_paths: List[Union[str, Path]]) -> List[Document]:
        """批量解析文件"""
        documents = []
        
        for file_path in file_paths:
            try:
                doc = self.parse_file(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"解析文件失败 {file_path}: {e}")
                continue
        
        return documents
    
    def parse_directory(
        self, 
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_pattern: Optional[str] = None,
        supported_extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """
        解析目录中的所有支持文件
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归搜索子目录
            file_pattern: 文件名模式匹配
            supported_extensions: 限制支持的扩展名
            
        Returns:
            解析后的文档列表
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"目录不存在或不是有效目录: {directory_path}")
        
        # 确定要处理的扩展名
        extensions = supported_extensions or list(self.parsers.keys())
        
        # 收集文件
        files = []
        if recursive:
            for ext in extensions:
                files.extend(directory_path.rglob(f"*.{ext}"))
        else:
            for ext in extensions:
                files.extend(directory_path.glob(f"*.{ext}"))
        
        # 应用文件模式过滤
        if file_pattern:
            import fnmatch
            files = [f for f in files if fnmatch.fnmatch(f.name, file_pattern)]
        
        return self.parse_files(files)
    
    def is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """
        检查是否支持该文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower().lstrip('.')
        return ext in self.parsers
    
    def get_supported_extensions(self) -> List[str]:
        """获取所有支持的文件扩展名"""
        return list(self.parsers.keys())
    
    def add_parser(self, extensions: List[str], parser) -> None:
        """
        添加自定义解析器
        
        Args:
            extensions: 文件扩展名列表
            parser: 解析器实例
        """
        for ext in extensions:
            self.parsers[ext.lower().lstrip('.')] = parser
    
    def get_parser_stats(self) -> Dict[str, Any]:
        """获取解析器统计信息"""
        return {
            "total_parsers": len(self.parsers),
            "supported_extensions": list(self.parsers.keys()),
            "config": self.config.__dict__,
            "parser_details": {
                ext: parser.get_stats() for ext, parser in self.parsers.items()
            }
        }
