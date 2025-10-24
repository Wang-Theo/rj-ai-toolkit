"""
RAG Toolkit

企业级检索增强生成(RAG)工具包，基于LangChain v0.3构建。
提供完整的文档处理、向量检索、重排序等RAG功能。
"""

# Chunker imports
from .chunker.base_chunker import BaseChunker
from .chunker.recursive_chunker import RecursiveChunker
from .chunker.semantic_chunker import SemanticChunker
from .chunker.hybrid_chunker import HybridChunker

# Parser imports
from .parser.base_parser import BaseParser
from .parser.pdf_parser import PDFParser
from .parser.docx_parser import DOCXParser
from .parser.eml_parser import EMLParser
from .parser.pptx_parser import PPTXParser

# DB Manager imports
from .db_manager.base_db_manager import BaseDBManager
from .db_manager.vector_db_manager import VectorDBManager
from .db_manager.document_db_manager import DocumentDBManager
from .db_manager.chroma_manager import ChromaManager
from .db_manager.pinecone_manager import PineconeManager

# Retriever imports
from .retriever.base_retriever import BaseRetriever
from .retriever.vector_retriever import VectorRetriever
from .retriever.hybrid_retriever import HybridRetriever
from .retriever.bm25_retriever import BM25Retriever

# Ranker imports
from .ranker.base_ranker import BaseRanker
from .ranker.bge_ranker import BGERanker
from .ranker.cohere_ranker import CohereRanker
from .ranker.cross_encoder_ranker import CrossEncoderRanker

__version__ = "0.1.0"
__all__ = [
    # Chunker exports
    "BaseChunker",
    "RecursiveChunker",
    "SemanticChunker",
    "HybridChunker",
    # Parser exports
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "EMLParser",
    "PPTXParser",
    # DB Manager exports
    "BaseDBManager",
    "VectorDBManager",
    "DocumentDBManager",
    "ChromaManager",
    "PineconeManager",
    # Retriever exports
    "BaseRetriever",
    "VectorRetriever",
    "HybridRetriever",
    "BM25Retriever",
    # Ranker exports
    "BaseRanker",
    "CohereRanker",
    "BGERanker",
    "CrossEncoderRanker"
]
