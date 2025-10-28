"""
RAG Toolkit

企业级检索增强生成(RAG)工具包，基于LangChain v0.3构建。
提供完整的文档处理、向量检索、重排序等RAG功能。
"""

# Chunker imports
from .chunker.base_chunker import BaseChunker
from .chunker.recursive_chunker import RecursiveChunker
from .chunker.semantic_chunker import SemanticChunker
from .chunker.eml_chunker import EMLChunker
from .chunker.pptx_chunker import PPTXChunker

# Parser imports
from .parser.base_parser import BaseParser
from .parser.pdf_parser import PDFParser
from .parser.docx_parser import DOCXParser
from .parser.eml_parser import EMLParser
from .parser.msg_parser import MSGParser
from .parser.pptx_parser import PPTXParser

# DB Manager imports
from .db_manager.base_db_manager import BaseDBManager
from .db_manager.chroma_manager import ChromaManager

# Retriever imports
from .retriever.base_retriever import BaseRetriever
from .retriever.vector_retriever import VectorRetriever
from .retriever.hybrid_retriever import HybridRetriever
from .retriever.bm25_retriever import BM25Retriever

# Reranker imports
from .reranker.reranker import Reranker

__version__ = "0.1.0"
__all__ = [
    # Chunker exports
    "BaseChunker",
    "RecursiveChunker",
    "SemanticChunker",
    "EMLChunker",
    "PPTXChunker",
    # Parser exports
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "EMLParser",
    "MSGParser",
    "PPTXParser",
    # DB Manager exports
    "BaseDBManager",
    "ChromaManager",
    # Retriever exports
    "BaseRetriever",
    "VectorRetriever",
    "HybridRetriever",
    "BM25Retriever",
    # Reranker exports
    "Reranker"
]
