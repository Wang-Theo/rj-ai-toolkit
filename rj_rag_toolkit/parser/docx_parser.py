# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
DOCX 文档解析模块
解析 Word 文档，将内容转换为 Markdown 格式，支持图片提取和 OCR
"""

from docx import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from pathlib import Path
from typing import List, Union, Optional
from io import BytesIO
from PIL import Image
from .base_parser import BaseParser

# Office Open XML 命名空间
OFFICE_NS = {
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}


class DOCXParser(BaseParser):
    """Word 文档解析器"""
    
    def __init__(
        self, 
        use_ocr: bool = False, 
        ocr_func = None,
        save_images: bool = True,
        images_dir: Optional[Union[str, Path]] = None,
        image_dpi: int = 300
    ):
        """
        初始化 DOCX 解析器
        
        Args:
            use_ocr: 是否使用OCR功能，默认False
            ocr_func: OCR处理函数，接收图片路径返回文本。签名: func(image_path: str) -> str
            save_images: 是否保存图片，默认True
            images_dir: 图片保存目录，默认为None（与DOCX文件同目录创建images文件夹）
            image_dpi: 图片 DPI，默认300
        """
        super().__init__(use_ocr, ocr_func)
        self.save_images = save_images
        self.images_dir = Path(images_dir) if images_dir else None
        self.image_counter = 0
        self.image_dpi = image_dpi
    
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        解析 DOCX 文件为 Markdown 格式
        
        Args:
            file_path: DOCX 文件路径
            
        Returns:
            Markdown 格式的文本内容
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 重置图片计数器
        self.image_counter = 0
        
        # 设置图片保存目录
        if self.images_dir is None:
            self.images_dir = file_path.parent / f"{file_path.stem}_images"
        
        # 如果需要保存图片，创建目录
        if self.save_images:
            self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析文档
        doc = DocxDocument(str(file_path))
        
        markdown_content = []
        
        # 遍历文档中的所有元素（段落、表格等）
        for element in doc.element.body:
            if isinstance(element, CT_P):
                # 处理段落
                paragraph = Paragraph(element, doc)
                para_md = self._parse_paragraph(paragraph)
                if para_md.strip():
                    markdown_content.append(para_md)
            elif isinstance(element, CT_Tbl):
                # 处理表格
                table = Table(element, doc)
                table_md = self._parse_table(table)
                if table_md.strip():
                    markdown_content.append(table_md)
        
        return "\n\n".join(markdown_content)
    
    def _parse_paragraph(self, paragraph: Paragraph) -> str:
        """
        解析段落
        
        Args:
            paragraph: python-docx 段落对象
            
        Returns:
            Markdown 格式的段落文本
        """
        # 检查是否包含图片
        images_md = []
        for run in paragraph.runs:
            # 检查 run 中的图片
            if hasattr(run.element, 'xpath'):
                images = run.element.xpath('.//a:blip')
                for image in images:
                    image_md = self._parse_image(run, image)
                    if image_md:
                        images_md.append(image_md)
        
        # 提取文本
        text = paragraph.text.strip()
        
        # 处理标题样式
        if paragraph.style.name.startswith('Heading'):
            level = paragraph.style.name.replace('Heading ', '')
            try:
                level = int(level)
                text = f"{'#' * level} {text}"
            except ValueError:
                pass
        
        # 组合文本和图片
        result = []
        if text:
            result.append(text)
        if images_md:
            result.extend(images_md)
        
        return "\n".join(result)
    
    def _parse_image(self, run, blip) -> str:
        """
        解析图片
        
        Args:
            run: python-docx run 对象
            blip: 图片 blip 元素
            
        Returns:
            Markdown 格式的图片引用
        """
        try:
            # 获取图片关系 ID（从 XML 属性中提取）
            rId = blip.get(f'{{{OFFICE_NS["r"]}}}embed')
            
            # 获取图片数据
            image_part = run.part.related_parts[rId]
            image_bytes = image_part.blob
            
            # 保存或处理图片
            self.image_counter += 1
            image_filename = f"image_{self.image_counter}.png"
            
            if self.save_images:
                # 保存图片
                image_path = self.images_dir / image_filename
                
                # 使用 PIL 转换图片格式以确保兼容性（透明背景转白底）
                image = Image.open(BytesIO(image_bytes))
                
                # 转换为 RGB 模式
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                image.save(image_path, 'PNG', dpi=(self.image_dpi, self.image_dpi))
                
                # OCR 处理
                ocr_text = ""
                if self.use_ocr:
                    ocr_text = self._call_ocr(str(image_path))
                
                # 返回 Markdown 图片引用（使用相对路径）
                relative_path = f"{self.images_dir.name}/{image_filename}"
                result = f"![{image_filename}]({relative_path})"
                if ocr_text:
                    result += f"\n\n**图片文字识别：**\n{ocr_text}"
                
                return result
            else:
                # 不保存图片，仅标注位置
                return f"[图片位置: {image_filename}]"
                
        except Exception:
            return ""
    
    def _parse_table(self, table: Table) -> str:
        """
        解析表格为 HTML 格式（保留在 Markdown 中）
        
        Args:
            table: python-docx 表格对象
            
        Returns:
            HTML 格式的表格
        """
        html_lines = ["<table>"]
        
        for i, row in enumerate(table.rows):
            html_lines.append("  <tr>")
            
            # 第一行作为表头
            tag = "th" if i == 0 else "td"
            
            for cell in row.cells:
                cell_text = cell.text.strip().replace("\n", "<br>")
                html_lines.append(f"    <{tag}>{cell_text}</{tag}>")
            
            html_lines.append("  </tr>")
        
        html_lines.append("</table>")
        
        return "\n".join(html_lines)
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return ['.docx']
