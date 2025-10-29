# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
PPT 切块器

专门用于切分 pptx_parser 解析后的 Markdown 格式 PPT 内容。
按照 slides（幻灯片）进行切块，支持 token 上限控制。

特殊性说明:
- 输入格式: pptx_parser 生成的 Markdown 格式 PPT 内容
- 分隔符识别: ## Slide N 格式的标题
- 切分策略: 优先按 slide 切分，超过 token 限制时在 slide 内部按句子切分
- 保留表格: 表格内容作为整体不被切分
- 文件头: Slide 0 表示第一个 slide 之前的文件头内容
"""

import re
from typing import List, Dict, Optional
from pathlib import Path
import tiktoken
from .base_chunker import BaseChunker, ChunkConfig


class PPTXChunker(BaseChunker):
    """
    PPT 切块器
    
    专门用于处理 pptx_parser 输出的 Markdown 格式 PPT 内容。
    按照 slides（幻灯片）进行切块，确保 slide 的完整性。
    
    特点:
    - 识别 "## Slide N" 格式的幻灯片分隔符
    - 优先保持单个 slide 的完整性
    - 超过 token 限制时智能在 slide 内部切分
    - 保护表格内容不被切分
    - 支持文件头内容（第一个 slide 之前的内容）
    """
    
    def __init__(
        self,
        chunk_size: int = 4000,
        length_type: str = "token"
    ):
        """
        初始化 PPT 切块器
        
        Args:
            chunk_size: 切块大小，默认 4000
                - length_type="char": 按字符数
                - length_type="token": 按 token 数
            length_type: 长度计算方式，默认 "token"
                - "char": 按字符数计算
                - "token": 按 token 数计算（使用 GPT-4 tokenizer）
        
        示例:
            # 使用默认配置（按 token 数）
            chunker = PPTXChunker()
            
            # 按字符数切分
            chunker = PPTXChunker(chunk_size=2000, length_type="char")
            
            # 自定义块大小
            chunker = PPTXChunker(chunk_size=2000)
            
            # 按 token 数切分（适合 LLM 输入）
            chunker = PPTXChunker(
                chunk_size=512,      # 512 tokens
                length_type="token"  # 使用 token 计数
            )
        """
        # 创建配置对象
        config = ChunkConfig(
            chunk_size=chunk_size,
            chunk_overlap=0  # PPT 切块不支持重叠
        )
        super().__init__(config)
        
        # 根据 length_type 选择长度函数
        if length_type == "char":
            self._length_function = len
        elif length_type == "token":
            tokenizer = tiktoken.encoding_for_model("gpt-4")
            self._length_function = lambda text: len(tokenizer.encode(text))
        else:
            raise ValueError(f"不支持的 length_type: {length_type}，仅支持 'char' 或 'token'")
    
    def _split_ppt_by_slides(self, markdown_content: str) -> List[Dict[str, str]]:
        """
        将 PPT Markdown 内容按照 slides 切分
        
        Args:
            markdown_content: pptx_parser 生成的 Markdown 格式 PPT 内容
            
        Returns:
            slides 列表，每个元素包含 slide_number 和 content
        """
        # PPT 的 slide 分隔符模式：## Slide N
        slide_pattern = r'^## Slide (\d+)\s*$'
        
        # 找到所有 slide 标记的位置
        slide_positions = []
        for match in re.finditer(slide_pattern, markdown_content, re.MULTILINE):
            slide_positions.append({
                'position': match.start(),
                'slide_number': int(match.group(1)),
                'full_match': match.group(0)
            })
        
        # 如果没有找到任何 slide 标记，返回整个内容
        if not slide_positions:
            return [{'slide_number': 0, 'content': markdown_content}]
        
        slides = []
        
        # 提取文件头部分（第一个 slide 之前的内容）
        if slide_positions[0]['position'] > 0:
            header = markdown_content[:slide_positions[0]['position']].strip()
            if header:
                slides.append({
                    'slide_number': 0,  # 0 表示文件头
                    'content': header
                })
        
        # 提取每个 slide 的内容
        for i, slide_info in enumerate(slide_positions):
            start_pos = slide_info['position']
            
            # 确定结束位置
            if i < len(slide_positions) - 1:
                end_pos = slide_positions[i + 1]['position']
            else:
                end_pos = len(markdown_content)
            
            # 提取 slide 内容
            slide_content = markdown_content[start_pos:end_pos].strip()
            
            if slide_content:
                slides.append({
                    'slide_number': slide_info['slide_number'],
                    'content': slide_content
                })
        
        return slides
    
    def _split_text_by_sentences(self, text: str, max_tokens: int) -> List[str]:
        """
        在单个 slide 内部按句子切分，确保不断句
        
        Args:
            text: 需要切分的文本
            max_tokens: 每个块的最大 token 数
            
        Returns:
            切分后的文本块列表
        """
        # 先提取并保护表格，用占位符替换
        table_pattern = r'<table.*?</table>'
        tables = []
        table_placeholders = {}
        
        for match in re.finditer(table_pattern, text, re.DOTALL):
            table_content = match.group(0)
            placeholder = f"__TABLE_PLACEHOLDER_{len(tables)}__"
            tables.append(table_content)
            table_placeholders[placeholder] = table_content
            text = text.replace(table_content, placeholder, 1)
        
        # 按句子分隔（支持中英文）
        # 句子结束标记：。！？；\n\n（段落）；. ! ? ;
        # 同时保护表格占位符不被切分
        sentence_pattern = r'(__TABLE_PLACEHOLDER_\d+__|[^。！？；.!?\n]+[。！？；.!?]+|\n\n|###[^\n]+\n)'
        sentences = re.findall(sentence_pattern, text, re.DOTALL)
        
        # 将表格占位符还原
        restored_sentences = []
        for sentence in sentences:
            if sentence in table_placeholders:
                restored_sentences.append(table_placeholders[sentence])
            else:
                restored_sentences.append(sentence)
        sentences = restored_sentences
        
        # 如果没有找到句子，按段落切分
        if not sentences:
            sentences = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_tokens = self._length_function(sentence)
            
            # 如果单个句子超过最大 token，需要进一步切分
            if sentence_tokens > max_tokens:
                # 保存当前块
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # 对长句子按词切分（最后的手段）
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self._length_function(word + ' ')
                    if temp_tokens + word_tokens > max_tokens and temp_chunk:
                        chunks.append(' '.join(temp_chunk))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                
                continue
            
            # 检查添加当前句子是否会超过限制
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                # 保存当前块并开始新块
                chunks.append('\n'.join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # 保存最后一个块
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def chunk(self, markdown_text: str) -> List[str]:
        """
        切分 Markdown 格式的 PPT 内容
        
        这是 BaseChunker 要求实现的主要接口方法。
        
        Args:
            markdown_text: pptx_parser 生成的 Markdown 格式 PPT 内容
            
        Returns:
            切块后的文本列表（纯文本，不包含元数据）
        
        示例:
            chunker = PPTXChunker(chunk_size=2000)
            chunks = chunker.chunk(ppt_markdown_content)
            for chunk in chunks:
                print(f"Chunk: {chunk[:100]}...")
        """
        if not markdown_text.strip():
            return []
        
        # 先按 slides 切分
        slides = self._split_ppt_by_slides(markdown_text)
        
        chunks = []
        max_tokens = self.config.chunk_size
        
        for slide in slides:
            slide_content = slide['content']
            slide_tokens = self._length_function(slide_content)
            
            # 如果 slide 未超过限制，直接添加
            if slide_tokens <= max_tokens:
                chunks.append(slide_content)
            else:
                # slide 超过限制，需要在内部切分
                sub_chunks = self._split_text_by_sentences(slide_content, max_tokens)
                chunks.extend(sub_chunks)
        
        return chunks
