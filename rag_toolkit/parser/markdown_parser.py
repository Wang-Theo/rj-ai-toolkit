"""
Markdown文档解析器

解析Markdown格式文档，支持提取文本内容和结构信息。
"""

import os
import re
from typing import Dict, Any, Optional, List
from .base_parser import BaseParser

try:
    import markdown
    from markdown.extensions import toc, tables, codehilite
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class MarkdownParser(BaseParser):
    """Markdown文档解析器
    
    支持解析.md和.markdown格式的文档，提取文本内容和结构信息。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Markdown解析器
        
        Args:
            config: 配置参数，支持以下选项：
                - include_code: 是否包含代码块内容 (默认: True)
                - include_links: 是否保留链接文本 (默认: True)
                - preserve_structure: 是否保留标题结构 (默认: True)
        """
        super().__init__(config)
        self.include_code = self.config.get('include_code', True)
        self.include_links = self.config.get('include_links', True)
        self.preserve_structure = self.config.get('preserve_structure', True)
        
        # 初始化Markdown处理器
        if MARKDOWN_AVAILABLE:
            self.md = markdown.Markdown(
                extensions=['toc', 'tables', 'codehilite', 'fenced_code']
            )
    
    def _get_supported_extensions(self) -> list:
        """获取支持的文件扩展名"""
        return ['.md', '.markdown']
    
    def _parse_file_content(self, file_path: str) -> str:
        """解析Markdown文档内容
        
        Args:
            file_path: Markdown文档路径
            
        Returns:
            解析后的文本内容
            
        Raises:
            FileNotFoundError: 文件不存在
            Exception: 解析失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if MARKDOWN_AVAILABLE:
                # 使用markdown库解析
                html_content = self.md.convert(content)
                # 简单的HTML标签清理
                clean_content = self._clean_html(html_content)
            else:
                # 基础的Markdown解析
                clean_content = self._basic_markdown_parse(content)
            
            return clean_content
            
        except Exception as e:
            raise Exception(f"解析Markdown文档失败 {file_path}: {str(e)}")
    
    def _clean_html(self, html_content: str) -> str:
        """清理HTML标签，提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            清理后的文本内容
        """
        # 移除HTML标签
        import re
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # 处理HTML实体
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")
        
        # 清理多余的空白
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        clean_text = re.sub(r' +', ' ', clean_text)
        
        return clean_text.strip()
    
    def _basic_markdown_parse(self, content: str) -> str:
        """基础的Markdown解析（不依赖markdown库）
        
        Args:
            content: Markdown内容
            
        Returns:
            解析后的文本内容
        """
        lines = content.split('\n')
        parsed_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                parsed_lines.append('')
                continue
            
            # 处理标题
            if line.startswith('#'):
                if self.preserve_structure:
                    # 保留标题结构
                    level = len(line) - len(line.lstrip('#'))
                    title = line.lstrip('# ').strip()
                    parsed_lines.append(f"{'  ' * (level-1)}{title}")
                else:
                    # 只保留标题文本
                    title = line.lstrip('# ').strip()
                    parsed_lines.append(title)
                continue
            
            # 处理代码块
            if line.startswith('```'):
                if not self.include_code:
                    continue
            
            # 处理链接
            if not self.include_links:
                # 移除链接，只保留文本
                line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
            
            # 处理粗体和斜体
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # 粗体
            line = re.sub(r'\*([^*]+)\*', r'\1', line)      # 斜体
            line = re.sub(r'`([^`]+)`', r'\1', line)        # 行内代码
            
            # 处理列表
            line = re.sub(r'^[\*\-\+]\s+', '', line)  # 无序列表
            line = re.sub(r'^\d+\.\s+', '', line)     # 有序列表
            
            parsed_lines.append(line)
        
        return '\n'.join(parsed_lines)
    
    def extract_headers(self, file_path: str) -> List[Dict[str, Any]]:
        """提取Markdown文档的标题结构
        
        Args:
            file_path: Markdown文档路径
            
        Returns:
            标题列表，每个标题包含级别、文本和行号
        """
        headers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line_no, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    text = line.lstrip('# ').strip()
                    headers.append({
                        'level': level,
                        'text': text,
                        'line': line_no
                    })
                    
        except Exception as e:
            raise Exception(f"提取标题失败 {file_path}: {str(e)}")
        
        return headers
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取Markdown文档元数据
        
        Args:
            file_path: Markdown文档路径
            
        Returns:
            文档元数据
        """
        metadata = super().get_metadata(file_path)
        
        try:
            headers = self.extract_headers(file_path)
            
            # 统计信息
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 添加Markdown特有的元数据
            metadata.update({
                "headers_count": len(headers),
                "lines_count": len(content.split('\n')),
                "words_count": len(content.split()),
                "chars_count": len(content),
                "headers": headers[:10]  # 只返回前10个标题
            })
            
        except Exception as e:
            metadata["error"] = f"获取元数据失败: {str(e)}"
        
        return metadata
