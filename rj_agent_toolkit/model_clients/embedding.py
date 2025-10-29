# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
Embedding模块 - 用于调用本地Ollama部署的embedding模型 (使用LangChain v0.3)
"""
from langchain_ollama import OllamaEmbeddings
from typing import List


def get_ollama_embedding(text: str, model: str, base_url: str = "http://localhost:11434") -> List[float]:
    """
    使用LangChain v0.3调用本地Ollama部署的embedding模型，将文本转换为向量
    
    Args:
        text: 需要转换为向量的文本
        model: embedding模型名称（例如: "bge-m3:latest", "nomic-embed-text"）
        base_url: Ollama服务地址，默认为 "http://localhost:11434"
        
    Returns:
        List[float]: 文本的向量表示
        
    Example:
        >>> vector = get_ollama_embedding("这是一段测试文本", model="bge-m3:latest")
        >>> print(f"向量维度: {len(vector)}")
    """
    try:
        # 初始化OllamaEmbeddings客户端
        embeddings = OllamaEmbeddings(
            model=model,
            base_url=base_url
        )
        
        # 调用embed_query方法获取单个文本的向量
        vector = embeddings.embed_query(text)
        
        return vector
        
    except Exception as e:
        raise Exception(f"调用Embedding模型时发生错误: {str(e)}")