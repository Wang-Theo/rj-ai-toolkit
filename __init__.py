"""
RJ AI Toolkit

企业级AI工具包集合，包含Agent、RAG等多种AI开发工具。

Author: Renjie Wang
Version: 0.1.0
"""

# Agent Toolkit
from .rj_agent_toolkit import (
    EnterpriseAgent, 
    Config,
    create_calculator_tool,
    create_text_analyzer_tool
)

# RAG Toolkit
try:
    from .rj_rag_toolkit import (
        RecursiveChunker,
        SemanticChunker,
        EMLChunker,
        PPTXChunker,
        PDFParser,
        DOCXParser,
        EMLParser,
        MSGParser,
        PPTXParser,
        BaseDBManager,
        ChromaManager,
        VectorRetriever,
        HybridRetriever,
        BM25Retriever,
        Reranker
    )
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Renjie Wang"
__email__ = "renjiewang31@gmail.com"
__description__ = "RJ AI Toolkit - 企业级AI工具包集合"

# 导出列表
__all__ = [
    # Agent模块
    "EnterpriseAgent",
    "Config", 
    "create_calculator_tool",
    "create_text_analyzer_tool"
]

# 如果RAG模块可用，添加到导出列表
if RAG_AVAILABLE:
    __all__.extend([
        # Chunker
        "RecursiveChunker",
        "SemanticChunker",
        "EMLChunker",
        "PPTXChunker",
        # Parser
        "PDFParser",
        "DOCXParser",
        "EMLParser",
        "MSGParser",
        "PPTXParser",
        # DB Manager
        "BaseDBManager",
        "ChromaManager",
        # Retriever
        "VectorRetriever",
        "HybridRetriever",
        "BM25Retriever",
        # Reranker
        "Reranker"
    ])

def get_available_modules():
    """获取可用的模块列表"""
    modules = ["rj_agent_toolkit"]
    if RAG_AVAILABLE:
        modules.append("rj_rag_toolkit")
    return modules

def print_toolkit_info():
    """打印工具包信息"""
    print(f"🚀 {__description__}")
    print(f"📦 版本: {__version__}")
    print(f"👨‍💻 作者: {__author__}")
    print(f"📧 邮箱: {__email__}")
    print(f"🔧 可用模块: {', '.join(get_available_modules())}")
    
    if not RAG_AVAILABLE:
        print("⚠️  RAG模块不可用，请安装相关依赖：pip install -r requirements.txt")
