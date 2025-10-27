"""
EML 邮件解析模块
使用 mail-parser 库解析 EML 文件，提取邮件内容并转换为 Markdown 格式
"""

import mailparser
from datetime import datetime
from pathlib import Path
from typing import List, Union, Optional
import html2text
import base64
from bs4 import BeautifulSoup
import mdformat
import tempfile
from PIL import Image
from io import BytesIO
import re
from .base_parser import BaseParser


class EMLParser(BaseParser):
    """EML 邮件解析器"""
    
    def __init__(
        self, 
        use_ocr: bool = False, 
        ocr_func = None,
        save_attachments: bool = True,
        attachments_dir: Optional[Union[str, Path]] = None,
        image_dpi: int = 300
    ):
        """
        初始化 EML 解析器
        
        Args:
            use_ocr: 是否使用OCR功能，默认False
            ocr_func: OCR处理函数，接收图片路径返回文本。签名: func(image_path: str) -> str
            save_attachments: 是否保存附件（包括嵌入图片和附件文件），默认True
            attachments_dir: 附件保存目录，默认为None（与EML文件同目录创建attachments文件夹）
            image_dpi: 图片 DPI，默认300
        """
        super().__init__(use_ocr, ocr_func)
        self.save_attachments = save_attachments
        self.attachments_dir = Path(attachments_dir) if attachments_dir else None
        self.image_dpi = image_dpi
    
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        解析 EML 文件为 Markdown 格式文本
        
        Args:
            file_path: EML 文件路径
            
        Returns:
            Markdown 格式的文本内容（包含附件列表）
        """
        file_path = Path(file_path)
        
        # 如果未指定附件目录，使用EML文件同目录下的attachments文件夹
        if self.attachments_dir is None:
            attachments_base_dir = file_path.parent / f"{file_path.stem}_attachments"
        else:
            attachments_base_dir = self.attachments_dir
        
        # 解析 EML 文件
        mail = mailparser.parse_from_file(str(file_path))
        
        # 处理附件并保存
        embedded_images, attachment_files = self._save_attachments(mail, attachments_base_dir)
        
        # 获取邮件内容（Markdown 格式）
        content_markdown = self._extract_content_as_markdown(mail, embedded_images, attachments_base_dir)
        
        # 在 Markdown 末尾添加附件列表
        if attachment_files:
            # 检查是否保存了附件
            is_saved = attachment_files[0].get('saved', True)
            if is_saved:
                content_markdown += "\n\n---\n\n## 📎 附件列表\n\n"
            else:
                content_markdown += "\n\n---\n\n## 📎 附件列表（未保存）\n\n"
            
            for att_info in attachment_files:
                size_str = self._format_file_size(att_info['size'])
                if att_info.get('saved', True):
                    rel_path = att_info['saved_path'].replace('\\', '/')
                    content_markdown += f"- [{att_info['filename']}]({rel_path}) ({size_str})\n"
                else:
                    content_markdown += f"- {att_info['filename']} ({size_str})\n"
        
        return content_markdown
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的扩展名列表
        """
        return ['.eml']
    
    def _save_attachments(self, mail, attachments_base_dir: Path) -> tuple:
        """
        处理邮件附件，区分嵌入图片和附件文件
        根据 save_attachments 参数决定是否保存文件
        
        Args:
            mail: mailparser 解析后的邮件对象
            attachments_base_dir: 附件保存基础目录
            
        Returns:
            tuple: (embedded_images, attachment_files)
                - embedded_images: dict {content_id: saved_path 或 filename}
                - attachment_files: list [{'filename': str, 'saved_path': str, 'size': int, 'saved': bool}]
        """
        embedded_images = {}
        attachment_files = []
        
        if not mail.attachments:
            return embedded_images, attachment_files
        
        # 创建子目录（仅在需要保存时）
        embedded_dir = attachments_base_dir / "embedded"
        files_dir = attachments_base_dir / "files"
        
        for attachment in mail.attachments:
            attachment_filename = attachment.get('filename', 'unknown_attachment')
            content_id = attachment.get('content-id', '').strip('<>')
            content_disposition = attachment.get('content-disposition', '')
            payload = attachment.get('payload')
            
            if not payload:
                continue
            
            # 判断是嵌入图片还是附件文件
            is_embedded_image = bool(content_id) and 'attachment' not in content_disposition.lower()
            
            if is_embedded_image:
                if self.save_attachments:
                    # 保存嵌入图片
                    embedded_dir.mkdir(parents=True, exist_ok=True)
                    saved_path = embedded_dir / attachment_filename
                    
                    # 检查是否是图片文件
                    is_img = attachment_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'))
                    actual_path = self._save_attachment_file(payload, saved_path, is_image=is_img)
                    
                    if actual_path:
                        # 记录实际保存路径（可能文件名被修改）
                        rel_path = f"{attachments_base_dir.name}/embedded/{actual_path.name}"
                        embedded_images[content_id] = {
                            'path': rel_path,
                            'saved_path': actual_path
                        }
                else:
                    # 不保存，只记录文件名
                    embedded_images[content_id] = {
                        'path': attachment_filename,
                        'saved_path': None
                    }
            else:
                # 计算文件大小
                file_size = 0
                if isinstance(payload, str):
                    file_size = len(base64.b64decode(payload)) if payload else 0
                elif isinstance(payload, bytes):
                    file_size = len(payload)
                
                if self.save_attachments:
                    # 保存附件文件
                    files_dir.mkdir(parents=True, exist_ok=True)
                    saved_path = files_dir / attachment_filename
                    
                    # 检查是否是图片文件
                    is_img = attachment_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'))
                    actual_path = self._save_attachment_file(payload, saved_path, is_image=is_img)
                    
                    if actual_path:
                        # 记录实际保存路径
                        rel_path = f"{attachments_base_dir.name}/files/{actual_path.name}"
                        attachment_files.append({
                            'filename': actual_path.name,
                            'saved_path': rel_path,
                            'size': file_size,
                            'saved': True
                        })
                else:
                    # 不保存，只记录信息
                    attachment_files.append({
                        'filename': attachment_filename,
                        'saved_path': '',
                        'size': file_size,
                        'saved': False
                    })
        
        return embedded_images, attachment_files
    
    def _save_attachment_file(self, payload, save_path: Path, is_image: bool = False):
        """
        保存附件到文件，如果是图片则转换为 PNG 格式（白底，无透明）
        
        Args:
            payload: 附件内容（str 或 bytes）
            save_path: 保存路径
            is_image: 是否是图片文件
        """
        try:
            # 解码数据
            if isinstance(payload, str):
                decoded_data = base64.b64decode(payload)
            elif isinstance(payload, bytes):
                decoded_data = payload
            else:
                return
            
            # 如果是图片，转换为 PNG（白底）
            if is_image:
                try:
                    # 尝试用 PIL 打开图片
                    img = Image.open(BytesIO(decoded_data))
                    
                    # 转换为 RGB 模式（透明背景转为白底）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 修改文件扩展名为 .png
                    save_path = save_path.with_suffix('.png')
                    
                    # 保存为 PNG 格式
                    img.save(save_path, 'PNG', dpi=(self.image_dpi, self.image_dpi))
                    return save_path  # 返回实际保存路径
                except Exception:
                    # 如果 PIL 处理失败，直接保存原始数据
                    save_path.write_bytes(decoded_data)
                    return save_path
            else:
                # 非图片文件直接保存
                save_path.write_bytes(decoded_data)
                return save_path
        except Exception:
            # 保存失败时静默处理
            return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化后的字符串，如 "1.2 MB"
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _format_date(self, date_obj) -> str:
        """
        格式化日期对象为字符串
        
        Args:
            date_obj: 日期对象
            
        Returns:
            格式化后的日期字符串
        """
        if date_obj is None:
            return "Unknown Date"
        
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        return str(date_obj)
    
    def _clean_html_table(self, table) -> str:
        """
        清理 HTML 表格，移除所有样式和属性，只保留基本结构
        保留 rowspan 和 colspan 属性
        
        Args:
            table: BeautifulSoup 的 table 对象
            
        Returns:
            清理后的 HTML 表格字符串
        """
        soup = BeautifulSoup('<table></table>', 'html.parser')
        new_table = soup.find('table')
        
        for row in table.find_all('tr'):
            new_row = soup.new_tag('tr')
            
            for cell in row.find_all(['td', 'th']):
                cell_name = cell.name
                new_cell = soup.new_tag(cell_name)
                
                # 只保留 rowspan 和 colspan 属性
                if cell.get('rowspan'):
                    new_cell['rowspan'] = cell.get('rowspan')
                if cell.get('colspan'):
                    new_cell['colspan'] = cell.get('colspan')
                
                # 获取单元格内容（纯文本）
                cell_text = cell.get_text(separator=' ', strip=True)
                cell_text = cell_text.replace('\xa0', ' ').replace('　', ' ')
                new_cell.string = cell_text
                
                new_row.append(new_cell)
            
            new_table.append(new_row)
        
        return str(new_table)
    
    def _mark_email_chain(self, markdown_content: str) -> str:
        """
        在邮件链中标记每封邮件
        识别转发和回复邮件的标准格式，添加 ## Email N 标记
        
        最简单直接的识别规则(必须在行首):
        - 英文: **From:**
        - 简体中文: **发件人**
        - 繁体中文: **寄件者**
        
        Args:
            markdown_content: Markdown 格式的邮件内容
            
        Returns:
            添加了邮件标记的 Markdown 内容
        """
        email_number = 2  # 从 Email 2 开始（Email 1 已在主邮件头添加）
        lines = markdown_content.split('\n')
        result_lines = []
        
        for line in lines:
            # 检测邮件头起始行(必须在行首)
            is_email_start = False
            stripped_line = line.lstrip()
            
            if stripped_line.startswith('**From:**'):
                is_email_start = True
            elif stripped_line.startswith('**发件人'):
                is_email_start = True
            elif stripped_line.startswith('**寄件者'):
                is_email_start = True
            
            # 如果检测到邮件头，添加标记
            if is_email_start:
                result_lines.append(f"\n## Email {email_number}\n")
                email_number += 1
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _extract_content_as_markdown(self, mail, embedded_images: dict, attachments_base_dir: Path) -> str:
        """
        从邮件对象中提取内容并转换为 Markdown 格式
        保留表格格式，并为邮件链中的每封邮件添加标记
        
        Args:
            mail: mailparser 解析后的邮件对象
            embedded_images: content-id 到保存路径的映射字典
            attachments_base_dir: 附件保存基础目录
            
        Returns:
            Markdown 格式的邮件内容
        """
        content_parts = []
        
        # 添加主邮件标记（Email 1）
        content_parts.append(f"## Email 1\n\n")
        
        # 添加邮件头信息
        content_parts.append(f"# {mail.subject or 'No Subject'}\n\n")
        content_parts.append(f"**From:** {mail.from_[0][1] if mail.from_ else 'Unknown'}  \n")
        content_parts.append(f"**To:** {', '.join([addr[1] for addr in mail.to]) if mail.to else 'Unknown'}  \n")
        
        if mail.cc:
            content_parts.append(f"**CC:** {', '.join([addr[1] for addr in mail.cc])}  \n")
        
        content_parts.append(f"**Date:** {self._format_date(mail.date)}  \n")
        content_parts.append("\n---\n\n")
        
        # 提取邮件正文内容
        if mail.text_html:
            for html_content in mail.text_html:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 替换所有 cid: 图片引用
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if src.startswith('cid:'):
                        cid = src[4:]
                        if cid in embedded_images:
                            img_info = embedded_images[cid]
                            if self.save_attachments:
                                # 使用保存的相对路径
                                img['src'] = img_info['path']
                                
                                # 如果启用OCR，添加OCR识别内容
                                if self.use_ocr and img_info['saved_path']:
                                    ocr_text = self._call_ocr(str(img_info['saved_path']))
                                    if ocr_text:
                                        # 在图片后添加OCR文本
                                        img.insert_after(f"\n\n**[OCR Content]:** {ocr_text}\n\n")
                            else:
                                # 未保存，标记为嵌入图片
                                img['src'] = f"[embedded-image: {img_info['path']}]"
                        else:
                            # 未找到图片，标记为缺失
                            img['src'] = f"[missing-image: {cid}]"
                
                # 处理所有表格
                tables = soup.find_all('table')
                table_placeholders = {}
                for idx, table in enumerate(tables):
                    cleaned_table_html = self._clean_html_table(table)
                    if cleaned_table_html:
                        placeholder = f"\n\n___TABLE_{idx}___\n\n"
                        table_placeholders[placeholder] = cleaned_table_html
                        table.replace_with(placeholder)
                
                # 使用 html2text 转换其余内容
                h = html2text.HTML2Text()
                h.body_width = 0
                h.ignore_links = False
                h.ignore_images = False
                h.ignore_emphasis = False
                h.unicode_snob = True
                
                markdown_content = h.handle(str(soup))
                
                # 将占位符替换回 HTML 表格
                for placeholder, table_html in table_placeholders.items():
                    markdown_content = markdown_content.replace(placeholder.strip(), f"\n\n{table_html}\n\n")
                
                # 使用 mdformat 清理和规范化 Markdown 内容
                try:
                    markdown_content = mdformat.text(markdown_content, options={"wrap": "no"})
                except Exception:
                    markdown_content = markdown_content.strip()
                
                # 标记邮件链中的其他邮件
                markdown_content = self._mark_email_chain(markdown_content)
                
                content_parts.append(markdown_content)
        
        elif mail.text_plain:
            for text_content in mail.text_plain:
                content_parts.append(text_content)
        
        return "".join(content_parts)
