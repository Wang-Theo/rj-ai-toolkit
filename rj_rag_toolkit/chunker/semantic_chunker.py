# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
语义切块器

基于语义相似度的智能文本切分，保持语义完整性。
使用句子embedding和相似度计算来确定切分点。
"""

import numpy as np
from typing import List, Optional, Callable
from .base_chunker import BaseChunker, ChunkConfig
import re
import tiktoken


class SemanticChunker(BaseChunker):
    """
    语义切块器
    
    基于句子间的语义相似度进行切分，
    确保语义相关的内容在同一个块中。
    """
    
    def __init__(
        self, 
        config: Optional[ChunkConfig] = None,
        embedding_func: Callable[[List[str]], List[List[float]]] = None,
        similarity_threshold: float = 0.5,
        min_chunk_size: int = 100,
        length_type: str = "char"
    ):
        """
        初始化语义切块器
        
        Args:
            config: 切块配置
            embedding_func: embedding处理函数（必需），接收文本列表返回向量列表。
                          签名: func(texts: List[str]) -> List[List[float]]
            similarity_threshold: 相似度阈值，低于此值将切分
            min_chunk_size: 最小块大小
                - length_type="char": 按字符数
                - length_type="token": 按 token 数
            length_type: 长度计算方式，默认 "char"
                - "char": 按字符数计算
                - "token": 按 token 数计算（使用 GPT-4 tokenizer）
        
        Raises:
            ValueError: 如果未提供 embedding_func
        """
        super().__init__(config)
        
        if embedding_func is None:
            raise ValueError("语义切块器必须提供 embedding_func 参数")
        
        self.embedding_func = embedding_func
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        
        # 根据 length_type 选择长度函数
        if length_type == "char":
            self._length_function = len
        elif length_type == "token":
            tokenizer = tiktoken.encoding_for_model("gpt-4")
            self._length_function = lambda text: len(tokenizer.encode(text))
        else:
            raise ValueError(f"不支持的 length_type: {length_type}，仅支持 'char' 或 'token'")
    
    def _call_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        调用embedding函数处理文本
        
        Args:
            texts: 文本列表
            
        Returns:
            文本向量列表
            
        Raises:
            RuntimeError: 如果embedding处理失败
        """
        try:
            return self.embedding_func(texts)
        except Exception as e:
            raise RuntimeError(f"Embedding 处理失败: {str(e)}")
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 中英文句子分割正则
        pattern = r'[。！？.!?]+(?=\s|$|[A-Z\u4e00-\u9fff])'
        sentences = re.split(pattern, text)
        
        # 清理空句子和过短句子
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _calculate_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """
        计算句子间的相似度矩阵
        
        Args:
            sentences: 句子列表
            
        Returns:
            相似度矩阵
        """
        if len(sentences) <= 1:
            return np.array([[1.0]])
        
        # 获取句子嵌入
        embeddings = self._call_embedding(sentences)
        embeddings = np.array(embeddings)
        
        # 计算余弦相似度矩阵
        similarity_matrix = np.dot(embeddings, embeddings.T)
        
        return similarity_matrix
    
    def _find_breakpoints(self, sentences: List[str], similarity_matrix: np.ndarray) -> List[int]:
        """
        基于相似度找到切分点
        
        Args:
            sentences: 句子列表
            similarity_matrix: 相似度矩阵
            
        Returns:
            切分点索引列表
        """
        breakpoints = [0]  # 起始点
        
        current_chunk_start = 0
        current_chunk_size = 0
        
        for i in range(1, len(sentences)):
            # 计算与当前块起始点的平均相似度
            similarity_scores = []
            for j in range(current_chunk_start, i):
                similarity_scores.append(similarity_matrix[i][j])
            
            avg_similarity = np.mean(similarity_scores) if similarity_scores else 1.0
            current_chunk_size += self._length_function(sentences[i])
            
            # 判断是否需要切分
            should_break = False
            
            # 相似度低于阈值
            if avg_similarity < self.similarity_threshold:
                should_break = True
            
            # 块大小超过限制
            if current_chunk_size > self.config.chunk_size:
                should_break = True
            
            # 执行切分
            if should_break and current_chunk_size >= self.min_chunk_size:
                breakpoints.append(i)
                current_chunk_start = i
                current_chunk_size = self._length_function(sentences[i])
        
        # 添加结束点
        if breakpoints[-1] != len(sentences):
            breakpoints.append(len(sentences))
        
        return breakpoints
    
    def _create_chunks_from_breakpoints(
        self, 
        sentences: List[str], 
        breakpoints: List[int]
    ) -> List[str]:
        """
        根据切分点创建文本块
        
        Args:
            sentences: 句子列表
            breakpoints: 切分点列表
            
        Returns:
            文本块列表
        """
        chunks = []
        
        for i in range(len(breakpoints) - 1):
            start_idx = breakpoints[i]
            end_idx = breakpoints[i + 1]
            
            # 合并句子
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = "".join(chunk_sentences)
            
            if not chunk_text.strip():
                continue
            
            # 添加重叠内容
            if i > 0 and self.config.chunk_overlap > 0:
                overlap_sentences = self._get_overlap_sentences(
                    sentences, start_idx, self.config.chunk_overlap
                )
                chunk_text = "".join(overlap_sentences) + chunk_text
            
            chunks.append(chunk_text)
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], start_idx: int, overlap_size: int) -> List[str]:
        """
        获取重叠句子
        
        Args:
            sentences: 句子列表
            start_idx: 当前块起始索引
            overlap_size: 重叠大小（字符数或 token 数，取决于 length_type）
            
        Returns:
            重叠句子列表
        """
        overlap_sentences = []
        current_size = 0
        
        for i in range(start_idx - 1, -1, -1):
            sentence = sentences[i]
            sentence_length = self._length_function(sentence)
            if current_size + sentence_length <= overlap_size:
                overlap_sentences.insert(0, sentence)
                current_size += sentence_length
            else:
                break
        
        return overlap_sentences
    
    def chunk(self, markdown_text: str) -> List[str]:
        """
        切分 Markdown 文本
        
        Args:
            markdown_text: 输入的 Markdown 文本
            
        Returns:
            切块后的文本列表
        """
        if not markdown_text.strip():
            return []
        
        # 分割成句子
        sentences = self._split_into_sentences(markdown_text)
        
        if len(sentences) <= 1:
            # 只有一个句子，直接返回
            return [markdown_text]
        
        # 计算相似度矩阵
        similarity_matrix = self._calculate_similarity_matrix(sentences)
        
        # 找到切分点
        breakpoints = self._find_breakpoints(sentences, similarity_matrix)
        
        # 创建文本块
        chunks = self._create_chunks_from_breakpoints(sentences, breakpoints)
        
        return chunks
