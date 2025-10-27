"""
邮件切块器

专门用于切分 eml_parser 解析后的 Markdown 格式邮件内容。
按照邮件链（每次发送/接收的邮件）进行切块，支持 token 上限控制。

特殊性说明:
- 输入格式: eml_parser 生成的 Markdown 格式邮件内容
- 分隔符识别: 
  * 英文邮件头格式: **From:** ... **Sent:** ... **To:**
  * 简体中文格式: **发件人****: ... **发送时间**: ... **收件人**:
  * 繁体中文格式: **寄件者****: ... **寄件日期**: ... **收件者**:
  * 水平线分隔符: ---, * * *, ___
- 切分策略: 优先按邮件消息切分，超过 token 限制时在邮件内部按句子切分
- 保留表格: 表格内容作为整体不被切分
"""

import re
from typing import List, Dict, Optional
from pathlib import Path
import tiktoken
from .base_chunker import BaseChunker, ChunkConfig


class EMLChunker(BaseChunker):
    """
    邮件切块器
    
    专门用于处理 eml_parser 输出的 Markdown 格式邮件内容。
    按照邮件链（每次发送/接收的邮件）进行切块，确保邮件的完整性。
    
    特点:
    - 识别多种语言的邮件头格式（英文、简体中文、繁体中文）
    - 优先保持单封邮件的完整性
    - 超过 token 限制时智能在邮件内部切分
    - 保护表格内容不被切分
    """
    
    def __init__(
        self,
        chunk_size: int = 4000,
        length_type: str = "token"
    ):
        """
        初始化邮件切块器
        
        Args:
            chunk_size: 切块大小，默认 4000
                - length_type="char": 按字符数
                - length_type="token": 按 token 数
            length_type: 长度计算方式，默认 "token"
                - "char": 按字符数计算
                - "token": 按 token 数计算（使用 GPT-4 tokenizer）
        
        示例:
            # 使用默认配置（按 token 数）
            chunker = EMLChunker()
            
            # 按字符数切分
            chunker = EMLChunker(chunk_size=2000, length_type="char")
            
            # 自定义块大小
            chunker = EMLChunker(chunk_size=2000)
            
            # 按 token 数切分（适合 LLM 输入）
            chunker = EMLChunker(
                chunk_size=512,      # 512 tokens
                length_type="token"  # 使用 token 计数
            )
        """
        # 创建配置对象
        config = ChunkConfig(
            chunk_size=chunk_size,
            chunk_overlap=0  # 邮件切块不支持重叠
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
    
    def _split_email_by_messages(self, markdown_content: str) -> List[str]:
        """
        将邮件 Markdown 内容按照单个邮件消息切分
        
        Args:
            markdown_content: eml_parser 生成的 Markdown 格式邮件内容
            
        Returns:
            邮件消息列表，每个元素是一封单独的邮件
        """
        # 识别邮件分隔模式
        # 1. 水平线分隔符: ---, * * *, ___
        # 2. 邮件头格式: **From:** ... **Sent:** ... **To:**
        
        # 先按主邮件头（第一部分）和后续邮件分隔
        parts = []
        
        # 提取第一个邮件头（通常是最新的邮件）
        first_header_pattern = r'^#\s+.*?\n\n\*\*From:\*\*.*?\n.*?\*\*Date:\*\*.*?\n\n---\n\n'
        first_match = re.search(first_header_pattern, markdown_content, re.MULTILINE | re.DOTALL)
        
        if first_match:
            # 保存第一封邮件的头部
            header_end = first_match.end()
            current_pos = header_end
        else:
            current_pos = 0
        
        # 查找所有邮件分隔符和邮件头
        # 支持两种邮件头格式：
        # 1. 英文格式：**From:** ... **Sent:** ... **To:**
        # 2. 中文格式：**发件人****: ... **发送时间 **: ... **收件人 **:
        
        # 英文邮件头模式
        en_header_pattern = r'\*\*From:\*\*\s+.*?<.*?>\s*\n\*\*Sent:\*\*\s+.*?\n\*\*To:\*\*\s+.*?(?:\n\*\*Cc:\*\*.*?)?\n(?:\*\*Subject:\*\*.*?\n)?'
        
        # 中文邮件头模式：**发件人****:
        cn_header_pattern = r'\*\*发件人\*\*\*\*:\s*.*?<.*?>\s*\n\*\*(?:发送时间|已发送)\s*\*\*\*\*:\s*.*?\n\*\*收件人\s*\*\*\*\*:\s*.*?(?:\n\*\*抄送\s*\*\*\*\*:.*?)?\n(?:\*\*主题\s*\*\*\*\*:.*?\n)?'
        
        # 繁体中文邮件头模式：**寄件者****:
        tw_header_pattern = r'\*\*寄件[者人]\*\*\*\*:\s*.*?<.*?>\s*\n\*\*寄件日期\*\*\*\*:\s*.*?\n\*\*收件[者人]\s*\*\*\*\*:\s*.*?(?:\n\*\*副本\s*\*\*\*\*:.*?)?\n(?:\*\*主[题旨]\s*\*\*\*\*:.*?\n)?'
        
        # 找到所有邮件头的位置
        message_positions = []
        
        # 查找所有英文格式的邮件头
        for match in re.finditer(en_header_pattern, markdown_content, re.MULTILINE):
            message_positions.append(match.start())
        
        # 查找所有简体中文格式的邮件头
        for match in re.finditer(cn_header_pattern, markdown_content, re.MULTILINE):
            message_positions.append(match.start())
        
        # 查找所有繁体中文格式的邮件头
        for match in re.finditer(tw_header_pattern, markdown_content, re.MULTILINE):
            message_positions.append(match.start())
        
        # 去重并排序
        message_positions = sorted(set(message_positions))
        
        # 如果没有找到任何邮件头，返回整个内容
        if not message_positions:
            return [markdown_content]
        
        # 按照邮件头位置切分
        messages = []
        
        # 第一封邮件（从开始到第一个邮件头之前）
        if message_positions:
            first_message = markdown_content[:message_positions[0]].strip()
            if first_message:
                messages.append(first_message)
        
        # 中间的邮件
        for i in range(len(message_positions) - 1):
            message = markdown_content[message_positions[i]:message_positions[i+1]].strip()
            # 移除前后的水平线分隔符
            message = re.sub(r'^[-*_\s]+\n', '', message)
            message = re.sub(r'\n[-*_\s]+$', '', message)
            if message:
                messages.append(message)
        
        # 最后一封邮件
        last_message = markdown_content[message_positions[-1]:].strip()
        last_message = re.sub(r'^[-*_\s]+\n', '', last_message)
        last_message = re.sub(r'\n[-*_\s]+$', '', last_message)
        if last_message:
            messages.append(last_message)
        
        # 如果切分后只有一个部分，可能是简单邮件，直接返回
        if len(messages) <= 1:
            return [markdown_content]
        
        return messages
    
    def _split_text_by_sentences(self, text: str, max_tokens: int) -> List[str]:
        """
        在单个邮件内部按句子切分，确保不断句
        
        Args:
            text: 需要切分的文本
            max_tokens: 每个块的最大 token 数
            
        Returns:
            切分后的文本块列表
        """
        # 先提取并保护表格，用占位符替换
        table_pattern = r'<table>.*?</table>'
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
        sentence_pattern = r'(__TABLE_PLACEHOLDER_\d+__|[^。！？；.!?\n]+[。！？；.!?]+|\n\n)'
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
        切分 Markdown 格式的邮件内容
        
        这是 BaseChunker 要求实现的主要接口方法。
        
        Args:
            markdown_text: eml_parser 生成的 Markdown 格式邮件内容
            
        Returns:
            切块后的文本列表（纯文本，不包含元数据）
        
        示例:
            chunker = EMLChunker(chunk_size=2000)
            chunks = chunker.chunk(email_markdown_content)
            for chunk in chunks:
                print(f"Chunk: {chunk[:100]}...")
        """
        if not markdown_text.strip():
            return []
        
        # 先按邮件消息切分
        messages = self._split_email_by_messages(markdown_text)
        
        chunks = []
        max_tokens = self.config.chunk_size
        
        for message in messages:
            message_tokens = self._length_function(message)
            
            # 如果邮件未超过限制，直接添加
            if message_tokens <= max_tokens:
                chunks.append(message)
            else:
                # 邮件超过限制，需要在内部切分
                sub_chunks = self._split_text_by_sentences(message, max_tokens)
                chunks.extend(sub_chunks)
        
        return chunks
