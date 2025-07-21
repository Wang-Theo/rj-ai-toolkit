"""
基础文档解析器

所有文档解析器的基类，定义统一的解析接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import hashlib
import uuid
from datetime import datetime
from langchain.schema import Document


@dataclass
class ParseConfig:
    """解析配置"""
    extract_metadata: bool = True
    preserve_structure: bool = True
    extract_images: bool = False
    extract_tables: bool = True
    language: str = "auto"  # auto, zh, en
    encoding: str = "utf-8"
    max_file_size: int = 100 * 1024 * 1024  # 100MB


@dataclass
class DocumentMetadata:
    """文档元数据"""
    doc_id: str
    source_path: str
    file_name: str
    file_type: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    page_count: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = None
    encoding: Optional[str] = None
    hash_md5: Optional[str] = None


class BaseParser(ABC):
    """
    基础文档解析器抽象类
    
    所有解析器都需要继承此类并实现抽象方法。
    """
    
    def __init__(self, config: Optional[ParseConfig] = None):
        """
        初始化解析器
        
        Args:
            config: 解析配置
        """
        self.config = config or ParseConfig()
        self.supported_extensions = self._get_supported_extensions()
    
    @abstractmethod
    def _get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的扩展名列表
        """
        pass
    
    @abstractmethod
    def _parse_file_content(self, file_path: Union[str, Path]) -> str:
        """
        解析文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的文本内容
        """
        pass
    
    def parse_file(self, file_path: Union[str, Path]) -> Document:
        """
        解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的文档对象
        """
        file_path = Path(file_path)
        
        # 验证文件
        self._validate_file(file_path)
        
        # 提取元数据
        metadata = self._extract_metadata(file_path)
        
        # 解析内容
        content = self._parse_file_content(file_path)
        
        # 创建文档对象
        document = Document(
            page_content=content,
            metadata=metadata.__dict__
        )
        
        return document
    
    def parse_files(self, file_paths: List[Union[str, Path]]) -> List[Document]:
        """
        批量解析文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            解析后的文档列表
        """
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
        file_pattern: Optional[str] = None
    ) -> List[Document]:
        """
        解析目录中的所有支持文件
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归搜索子目录
            file_pattern: 文件名模式匹配
            
        Returns:
            解析后的文档列表
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"目录不存在或不是有效目录: {directory_path}")
        
        # 收集文件
        files = []
        if recursive:
            for ext in self.supported_extensions:
                files.extend(directory_path.rglob(f"*.{ext}"))
        else:
            for ext in self.supported_extensions:
                files.extend(directory_path.glob(f"*.{ext}"))
        
        # 应用文件模式过滤
        if file_pattern:
            import fnmatch
            files = [f for f in files if fnmatch.fnmatch(f.name, file_pattern)]
        
        return self.parse_files(files)
    
    def _validate_file(self, file_path: Path) -> None:
        """
        验证文件
        
        Args:
            file_path: 文件路径
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"不是有效文件: {file_path}")
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > self.config.max_file_size:
            raise ValueError(f"文件过大: {file_size} bytes, 最大支持: {self.config.max_file_size} bytes")
        
        # 检查扩展名
        ext = file_path.suffix.lower().lstrip('.')
        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件类型: {ext}, 支持: {self.supported_extensions}")
    
    def _extract_metadata(self, file_path: Path) -> DocumentMetadata:
        """
        提取文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档元数据
        """
        stat = file_path.stat()
        
        # 计算文件哈希
        hash_md5 = None
        if self.config.extract_metadata:
            hash_md5 = self._calculate_file_hash(file_path)
        
        metadata = DocumentMetadata(
            doc_id=str(uuid.uuid4()),
            source_path=str(file_path.absolute()),
            file_name=file_path.name,
            file_type=file_path.suffix.lower().lstrip('.'),
            file_size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            hash_md5=hash_md5,
            encoding=self.config.encoding
        )
        
        return metadata
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件MD5哈希
        
        Args:
            file_path: 文件路径
            
        Returns:
            MD5哈希值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 文本内容
            
        Returns:
            语言代码
        """
        if self.config.language != "auto":
            return self.config.language
        
        # 简单的语言检测
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        total_chars = len(text)
        
        if total_chars == 0:
            return "unknown"
        
        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.3:
            return "zh"
        else:
            return "en"
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
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
        return ext in self.supported_extensions
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取解析器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "parser_type": self.__class__.__name__,
            "supported_extensions": self.supported_extensions,
            "config": self.config.__dict__,
            "version": "1.0.0"
        }
