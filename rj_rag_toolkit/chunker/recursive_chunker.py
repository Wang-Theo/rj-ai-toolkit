# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
递归切块器

基于分隔符的递归文本切分，支持多级分隔符策略。
基于 LangChain 的 RecursiveCharacterTextSplitter。
"""

from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
from .base_chunker import BaseChunker, ChunkConfig

class RecursiveChunker(BaseChunker):
    """
    递归切块器
    
    使用递归策略和多级分隔符进行 Markdown 文本切分，
    优先使用较大的分隔符（如段落），然后逐级降级。
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        keep_separator: bool = False,
        add_start_index: bool = True,
        strip_whitespace: bool = True,
        length_type: str = "char"
    ):
        """
        初始化递归切块器
        
        Args:
            chunk_size: 切块大小，默认 1000
                - length_type="char": 按字符数
                - length_type="token": 按 token 数
            chunk_overlap: 切块重叠大小，默认 200
            separators: 分隔符列表，优先级从高到低，默认 ["\n\n", "\n", " ", ""]
            keep_separator: 是否保留分隔符，默认 False
            add_start_index: 是否添加起始索引到元数据，默认 True
            strip_whitespace: 是否去除每个块首尾的空白字符，默认 True
            length_type: 长度计算方式，默认 "char"
                - "char": 按字符数计算（默认）
                - "token": 按 token 数计算（使用 GPT-4 tokenizer）
        
        示例:
            # 使用默认配置（按字符数）
            chunker = RecursiveChunker()
            
            # 自定义块大小
            chunker = RecursiveChunker(chunk_size=500, chunk_overlap=50)
            
            # 自定义分隔符（适合中文文本）
            chunker = RecursiveChunker(
                chunk_size=800, 
                separators=["\\n\\n", "\\n", "。", "！", "？", " "],
                keep_separator=True
            )
            
            # 按 token 数切分（适合 LLM 输入）
            chunker = RecursiveChunker(
                chunk_size=512,      # 512 tokens
                chunk_overlap=50,    # 50 tokens
                length_type="token"  # 使用 token 计数
            )
            
            # 完全自定义
            chunker = RecursiveChunker(
                chunk_size=1200,
                chunk_overlap=100,
                separators=["\\n\\n", "\\n"],
                keep_separator=False,
                add_start_index=True,
                strip_whitespace=True,
                length_type="char"
            )
        """
        # 创建配置对象
        config = ChunkConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=keep_separator,
            add_start_index=add_start_index,
            strip_whitespace=strip_whitespace
        )
        
        super().__init__(config)
        
        # 根据 length_type 选择长度函数
        if length_type == "char":
            self.length_function = len
        elif length_type == "token":
            tokenizer = tiktoken.encoding_for_model("gpt-4")
            self.length_function = lambda text: len(tokenizer.encode(text))
        else:
            raise ValueError(f"不支持的 length_type: {length_type}，仅支持 'char' 或 'token'")
        
        # 创建 LangChain 的递归切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators,
            keep_separator=self.config.keep_separator,
            add_start_index=self.config.add_start_index,
            strip_whitespace=self.config.strip_whitespace,
            length_function=self.length_function
        )
    
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
        
        # 使用 LangChain 的切分器切分文本
        chunks = self.text_splitter.split_text(markdown_text)
        
        return chunks
