"""
语义切块器

基于语义相似度的智能文本切分，保持语义完整性。
使用句子embedding和相似度计算来确定切分点。
"""

import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from .base_chunker import BaseChunker, ChunkConfig
import re


class SemanticChunker(BaseChunker):
    """
    语义切块器
    
    基于句子间的语义相似度进行切分，
    确保语义相关的内容在同一个块中。
    """
    
    def __init__(
        self, 
        config: ChunkConfig,
        embeddings: Optional[Embeddings] = None,
        similarity_threshold: float = 0.5,
        min_chunk_size: int = 100
    ):
        """
        初始化语义切块器
        
        Args:
            config: 切块配置
            embeddings: 嵌入模型，默认使用BGE
            similarity_threshold: 相似度阈值，低于此值将切分
            min_chunk_size: 最小块大小
        """
        super().__init__(config)
        
        # 初始化嵌入模型
        if embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文语义模型
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        else:
            self.embeddings = embeddings
            
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
    
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
        embeddings = self.embeddings.embed_documents(sentences)
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
            current_chunk_size += len(sentences[i])
            
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
                current_chunk_size = len(sentences[i])
        
        # 添加结束点
        if breakpoints[-1] != len(sentences):
            breakpoints.append(len(sentences))
        
        return breakpoints
    
    def _create_chunks_from_breakpoints(
        self, 
        sentences: List[str], 
        breakpoints: List[int],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        根据切分点创建文档块
        
        Args:
            sentences: 句子列表
            breakpoints: 切分点列表
            metadata: 元数据
            
        Returns:
            文档块列表
        """
        chunks = []
        source_doc_id = metadata.get("source_doc_id", str(uuid.uuid4())) if metadata else str(uuid.uuid4())
        
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
            
            # 计算字符位置
            start_char = sum(len(s) for s in sentences[:start_idx])
            end_char = start_char + len(chunk_text)
            
            # 创建元数据
            chunk_metadata = self._create_chunk_metadata(
                chunk_id=self._generate_chunk_id(source_doc_id, i),
                source_doc_id=source_doc_id,
                chunk_index=i,
                start_char=start_char,
                end_char=end_char,
                token_count=self._estimate_token_count(chunk_text),
                original_metadata=metadata
            )
            
            # 添加语义切块特有的元数据
            chunk_metadata.update({
                "chunk_type": "semantic",
                "sentence_count": len(chunk_sentences),
                "semantic_chunker_version": "1.0.0"
            })
            
            # 创建文档块
            chunk_doc = Document(
                page_content=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk_doc)
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], start_idx: int, overlap_size: int) -> List[str]:
        """
        获取重叠句子
        
        Args:
            sentences: 句子列表
            start_idx: 当前块起始索引
            overlap_size: 重叠字符数
            
        Returns:
            重叠句子列表
        """
        overlap_sentences = []
        current_size = 0
        
        for i in range(start_idx - 1, -1, -1):
            sentence = sentences[i]
            if current_size + len(sentence) <= overlap_size:
                overlap_sentences.insert(0, sentence)
                current_size += len(sentence)
            else:
                break
        
        return overlap_sentences
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        将文本切分成语义块
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            
        Returns:
            切分后的文档块列表
        """
        if not text.strip():
            return []
        
        # 分割成句子
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            # 只有一个句子，直接返回
            source_doc_id = metadata.get("source_doc_id", str(uuid.uuid4())) if metadata else str(uuid.uuid4())
            chunk_metadata = self._create_chunk_metadata(
                chunk_id=self._generate_chunk_id(source_doc_id, 0),
                source_doc_id=source_doc_id,
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                token_count=self._estimate_token_count(text),
                original_metadata=metadata
            )
            return [Document(page_content=text, metadata=chunk_metadata)]
        
        # 计算相似度矩阵
        similarity_matrix = self._calculate_similarity_matrix(sentences)
        
        # 找到切分点
        breakpoints = self._find_breakpoints(sentences, similarity_matrix)
        
        # 创建文档块
        chunks = self._create_chunks_from_breakpoints(sentences, breakpoints, metadata)
        
        return chunks
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        将文档切分成语义块
        
        Args:
            document: 要切分的文档
            
        Returns:
            切分后的文档块列表
        """
        return self.chunk_text(document.page_content, document.metadata)
    
    def analyze_semantic_structure(self, text: str) -> Dict[str, Any]:
        """
        分析文本的语义结构
        
        Args:
            text: 要分析的文本
            
        Returns:
            语义结构分析结果
        """
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return {
                "sentence_count": len(sentences),
                "semantic_complexity": "low",
                "recommended_chunks": 1
            }
        
        similarity_matrix = self._calculate_similarity_matrix(sentences)
        
        # 计算语义复杂度
        avg_similarity = np.mean(similarity_matrix)
        similarity_variance = np.var(similarity_matrix)
        
        # 语义复杂度评估
        if avg_similarity > 0.7:
            complexity = "low"  # 高相似度，结构简单
        elif avg_similarity > 0.4:
            complexity = "medium"
        else:
            complexity = "high"  # 低相似度，结构复杂
        
        # 推荐块数
        breakpoints = self._find_breakpoints(sentences, similarity_matrix)
        recommended_chunks = len(breakpoints) - 1
        
        return {
            "sentence_count": len(sentences),
            "avg_similarity": float(avg_similarity),
            "similarity_variance": float(similarity_variance),
            "semantic_complexity": complexity,
            "recommended_chunks": recommended_chunks,
            "total_length": len(text)
        }
