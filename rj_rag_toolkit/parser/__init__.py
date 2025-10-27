"""
文档解析器模块

支持多种文档格式的解析，包括PDF、Word、EML、PPTX等。
"""

from .base_parser import BaseParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .eml_parser import EMLParser
from .msg_parser import MSGParser
from .pptx_parser import PPTXParser

__all__ = [
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "EMLParser",
    "MSGParser",
    "PPTXParser"
]
