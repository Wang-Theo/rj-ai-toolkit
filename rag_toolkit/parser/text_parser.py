"""
文本解析器

处理纯文本文件(.txt)的解析。
"""

from typing import List
from pathlib import Path
from .base_parser import BaseParser


class TextParser(BaseParser):
    """文本文件解析器"""
    
    def _get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return ["txt", "text"]
    
    def _parse_file_content(self, file_path: Path) -> str:
        """解析文本文件内容"""
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                content = f.read()
            
            # 清理文本
            content = self._clean_text(content)
            
            return content
            
        except UnicodeDecodeError:
            # 尝试其他编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return self._clean_text(content)
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"无法解析文件编码: {file_path}")


class MarkdownParser(BaseParser):
    """Markdown文件解析器"""
    
    def _get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return ["md", "markdown"]
    
    def _parse_file_content(self, file_path: Path) -> str:
        """解析Markdown文件内容"""
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                content = f.read()
            
            if self.config.preserve_structure:
                # 保留Markdown结构
                return content
            else:
                # 移除Markdown语法，只保留文本
                import re
                # 移除标题标记
                content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
                # 移除链接语法
                content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
                # 移除加粗和斜体
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                content = re.sub(r'\*(.*?)\*', r'\1', content)
                # 移除代码块
                content = re.sub(r'```[\s\S]*?```', '', content)
                content = re.sub(r'`([^`]+)`', r'\1', content)
                
                return self._clean_text(content)
                
        except Exception as e:
            raise ValueError(f"解析Markdown文件失败: {e}")


class DocumentParser:
    """统一文档解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.parsers = {
            'txt': TextParser(),
            'text': TextParser(), 
            'md': MarkdownParser(),
            'markdown': MarkdownParser()
        }
    
    def parse_file(self, file_path):
        """解析文件"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower().lstrip('.')
        
        if ext in self.parsers:
            return self.parsers[ext].parse_file(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
    
    def parse_directory(self, directory_path, recursive=True, file_pattern=None):
        """解析目录"""
        documents = []
        directory_path = Path(directory_path)
        
        for ext, parser in self.parsers.items():
            try:
                docs = parser.parse_directory(directory_path, recursive, file_pattern)
                documents.extend(docs)
            except:
                continue
        
        return documents
