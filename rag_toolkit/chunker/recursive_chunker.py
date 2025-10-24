"""
递归切块器

基于分隔符的递归文本切分，支持多级分隔符策略。
基于 LangChain 的 RecursiveCharacterTextSplitter。
"""

import uuid
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base_chunker import BaseChunker, ChunkConfig


class RecursiveChunker(BaseChunker):
    """
    递归切块器
    
    使用递归策略和多级分隔符进行文本切分，
    优先使用较大的分隔符（如段落），然后逐级降级。
    """
    
    def __init__(self, config: ChunkConfig):
        """
        初始化递归切块器
        
        Args:
            config: 切块配置
        """
        super().__init__(config)
        
        # 创建 LangChain 的递归切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            keep_separator=config.keep_separator,
            add_start_index=config.add_start_index,
            strip_whitespace=config.strip_whitespace,
            length_function=len
        )
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        将文本切分成块
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            
        Returns:
            切分后的文档块列表
        """
        if not text.strip():
            return []
        
        # 生成源文档ID
        source_doc_id = metadata.get("source_doc_id", str(uuid.uuid4()))
        
        # 使用 LangChain 的切分器
        chunks = self.text_splitter.create_documents([text])
        
        # 转换为我们的格式
        result_chunks = []
        for i, chunk in enumerate(chunks):
            # 计算字符位置
            start_char = chunk.metadata.get("start_index", 0) if hasattr(chunk, "metadata") else i * self.config.chunk_size
            end_char = start_char + len(chunk.page_content)
            
            # 创建切块元数据
            chunk_metadata = self._create_chunk_metadata(
                chunk_id=self._generate_chunk_id(source_doc_id, i),
                source_doc_id=source_doc_id,
                chunk_index=i,
                start_char=start_char,
                end_char=end_char,
                token_count=self._estimate_token_count(chunk.page_content),
                original_metadata=metadata
            )
            
            # 创建新的文档块
            chunk_doc = Document(
                page_content=chunk.page_content,
                metadata=chunk_metadata
            )
            result_chunks.append(chunk_doc)
        
        return result_chunks
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        将文档切分成块
        
        Args:
            document: 要切分的文档
            
        Returns:
            切分后的文档块列表
        """
        return self.chunk_text(document.page_content, document.metadata)
    
    def chunk_with_overlap_strategy(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        dynamic_overlap: bool = True
    ) -> List[Document]:
        """
        使用动态重叠策略切分文本
        
        Args:
            text: 要切分的文本
            metadata: 文档元数据
            dynamic_overlap: 是否使用动态重叠
            
        Returns:
            切分后的文档块列表
        """
        if not dynamic_overlap:
            return self.chunk_text(text, metadata)
        
        # 动态调整重叠大小
        original_overlap = self.config.chunk_overlap
        
        # 根据文本长度调整重叠
        text_length = len(text)
        if text_length < 2000:
            # 短文本使用较小重叠
            self.config.chunk_overlap = min(original_overlap, 50)
        elif text_length > 10000:
            # 长文本使用较大重叠
            self.config.chunk_overlap = min(original_overlap * 1.5, self.config.chunk_size // 3)
        
        # 重新创建切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators,
            keep_separator=self.config.keep_separator,
            add_start_index=self.config.add_start_index,
            strip_whitespace=self.config.strip_whitespace,
            length_function=len
        )
        
        # 执行切分
        result = self.chunk_text(text, metadata)
        
        # 恢复原始配置
        self.config.chunk_overlap = original_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=original_overlap,
            separators=self.config.separators,
            keep_separator=self.config.keep_separator,
            add_start_index=self.config.add_start_index,
            strip_whitespace=self.config.strip_whitespace,
            length_function=len
        )
        
        return result
    
    def get_optimal_separators_for_language(self, language: str = "zh") -> List[str]:
        """
        根据语言获取最优分隔符
        
        Args:
            language: 语言代码 (zh/en)
            
        Returns:
            最优分隔符列表
        """
        if language == "zh":
            return [
                "\n\n", "\n", 
                "。", "！", "？", 
                "；", "：", "，", 
                " ", ""
            ]
        elif language == "en":
            return [
                "\n\n", "\n",
                ". ", "! ", "? ",
                "; ", ": ", ", ",
                " ", ""
            ]
        else:
            return self.config.separators
    
    def update_separators_for_language(self, language: str = "zh") -> None:
        """
        根据语言更新分隔符
        
        Args:
            language: 语言代码 (zh/en)
        """
        self.config.separators = self.get_optimal_separators_for_language(language)
        
        # 重新创建切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators,
            keep_separator=self.config.keep_separator,
            add_start_index=self.config.add_start_index,
            strip_whitespace=self.config.strip_whitespace,
            length_function=len
        )
