# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
邮件切块器

专门用于切分 eml_parser 解析后的 Markdown 格式邮件内容。
按照邮件链（每封邮件）进行切块，支持 token 上限控制。

特殊性说明:
- 输入格式: eml_parser 生成的 Markdown 格式邮件内容，包含 ## Email N 标记
- 分隔符识别: ## Email N 标记（由 eml_parser 自动添加）
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
    按照邮件链（每封邮件）进行切块，使用 ## Email N 标记识别邮件边界。
    
    特点:
    - 识别 eml_parser 添加的 ## Email N 标记
    - 优先保持单封邮件的完整性
    - 超过 token 限制时智能在邮件内部切分
    - 保护表格内容不被切分
    """
    
    def __init__(
        self,
        chunk_size: int = 4000,
        length_type: str = "token",
        remove_emails: bool = True
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
            remove_emails: 是否删除邮箱地址，默认 True
                - True: 删除所有邮箱地址以节省 token
                - False: 保留邮箱地址
        
        示例:
            # 使用默认配置（按 token 数，删除邮箱）
            chunker = EMLChunker()
            
            # 按字符数切分
            chunker = EMLChunker(chunk_size=2000, length_type="char")
            
            # 保留邮箱地址
            chunker = EMLChunker(remove_emails=False)
            
            # 按 token 数切分（适合 LLM 输入）
            chunker = EMLChunker(
                chunk_size=512,      # 512 tokens
                length_type="token",  # 使用 token 计数
                remove_emails=True   # 删除邮箱地址
            )
        """
        # 创建配置对象
        config = ChunkConfig(
            chunk_size=chunk_size,
            chunk_overlap=0  # 邮件切块不支持重叠
        )
        super().__init__(config)
        
        # 保存配置
        self.remove_emails = remove_emails
        
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
        将邮件 Markdown 内容按照 ## Email N 标记切分
        
        Args:
            markdown_content: eml_parser 生成的 Markdown 格式邮件内容
            
        Returns:
            邮件消息列表，每个元素是一封单独的邮件
        """
        # 识别 ## Email N 标记
        pattern = r'^## Email (\d+)\s*$'
        
        # 找到所有邮件标记的位置
        message_positions = []
        for match in re.finditer(pattern, markdown_content, re.MULTILINE):
            message_positions.append(match.start())
        
        # 如果没有找到任何标记，返回整个内容
        if not message_positions:
            return [markdown_content]
        
        # 按照标记位置切分
        messages = []
        
        # 第一封邮件（从开始到第一个标记之前）
        first_message = markdown_content[:message_positions[0]].strip()
        if first_message:
            messages.append(first_message)
        
        # 中间的邮件
        for i in range(len(message_positions) - 1):
            message = markdown_content[message_positions[i]:message_positions[i+1]].strip()
            if message:
                messages.append(message)
        
        # 最后一封邮件
        last_message = markdown_content[message_positions[-1]:].strip()
        if last_message:
            messages.append(last_message)
        
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
    
    def _remove_email_addresses(self, text: str) -> str:
        """
        删除文本中的所有邮箱地址,但保留原有的换行结构
        
        Args:
            text: 输入文本
            
        Returns:
            删除邮箱地址后的文本
        """
        # 匹配邮箱地址的正则表达式
        # 支持常见格式: user@domain.com, <user@domain.com>, [user@domain.com](mailto:user@domain.com)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # 先删除 Markdown 链接格式的邮箱: [xxx@xxx.com](mailto:xxx@xxx.com)
        text = re.sub(r'\[' + email_pattern + r'\]\(mailto:' + email_pattern + r'\)', '', text)
        
        # 删除尖括号包裹的邮箱: <xxx@xxx.com>
        text = re.sub(r'<' + email_pattern + r'>', '', text)
        
        # 删除普通的邮箱地址
        text = re.sub(email_pattern, '', text)
        
        # 清理同一行内的多余空格(不跨行)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 多个空格合并为一个
            line = re.sub(r' +', ' ', line)
            # 清理连续的逗号分号
            line = re.sub(r'\s*[,;]\s*[,;]+', ',', line)
            # 清理 ": ," 这样的情况
            line = re.sub(r':\s*,', ':', line)
            # 清理行首行尾空格
            line = line.strip()
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def chunk(self, markdown_text: str) -> List[str]:
        """
        切分 Markdown 格式的邮件内容
        
        这是 BaseChunker 要求实现的主要接口方法。
        根据 remove_emails 参数决定是否删除邮箱地址。
        
        Args:
            markdown_text: eml_parser 生成的 Markdown 格式邮件内容
            
        Returns:
            切块后的文本列表（纯文本，不包含元数据，可选删除邮箱地址）
        
        示例:
            # 默认删除邮箱地址
            chunker = EMLChunker(chunk_size=2000)
            chunks = chunker.chunk(email_markdown_content)
            
            # 保留邮箱地址
            chunker = EMLChunker(chunk_size=2000, remove_emails=False)
            chunks = chunker.chunk(email_markdown_content)
        """
        if not markdown_text.strip():
            return []
        
        # 根据配置决定是否删除邮箱地址
        if self.remove_emails:
            markdown_text = self._remove_email_addresses(markdown_text)
        
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
