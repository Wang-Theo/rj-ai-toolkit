# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Wed Oct 29 2025     │
# └──────────────────────────────┘

"""
PDF 文档解析模块
使用 pdfplumber 解析 PDF 文件，将内容转换为 Markdown 格式，支持图片提取和 OCR
"""

import pdfplumber
from pathlib import Path
from typing import List, Union, Optional
from io import BytesIO
from PIL import Image
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """PDF 文档解析器"""
    
    def __init__(
        self, 
        use_ocr: bool = False, 
        ocr_func = None,
        save_images: bool = True,
        images_dir: Optional[Union[str, Path]] = None,
        image_dpi: int = 300
    ):
        """
        初始化 PDF 解析器
        
        Args:
            use_ocr: 是否使用OCR功能，默认False
            ocr_func: OCR处理函数，接收图片路径返回文本。签名: func(image_path: str) -> str
            save_images: 是否保存图片，默认True
            images_dir: 图片保存目录，默认为None（与PDF文件同目录创建images文件夹）
            image_dpi: 图片 DPI，默认300
        """
        super().__init__(use_ocr, ocr_func)
        self.save_images = save_images
        self.images_dir = Path(images_dir) if images_dir else None
        self.image_counter = 0
        self.image_dpi = image_dpi
    
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        解析 PDF 文件为 Markdown 格式
        
        Args:
            file_path: PDF 文件路径
            
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
        
        markdown_content = []
        
        # 使用 pdfplumber 解析 PDF
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # 添加页码标记
                markdown_content.append(f"## 第 {page_num} 页")
                
                # 提取文本
                text = page.extract_text()
                if text and text.strip():
                    markdown_content.append(text.strip())
                
                # 提取表格
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        table_md = self._parse_table(table)
                        if table_md:
                            markdown_content.append(table_md)
                
                # 提取图片
                if hasattr(page, 'images') and page.images:
                    for img_info in page.images:
                        image_md = self._parse_image(page, img_info, page_num)
                        if image_md:
                            markdown_content.append(image_md)
        
        return "\n\n".join(markdown_content)
    
    def _parse_table(self, table: List[List]) -> str:
        """
        解析表格为 HTML 格式（保留在 Markdown 中）
        
        Args:
            table: pdfplumber 提取的表格数据（二维列表）
            
        Returns:
            HTML 格式的表格
        """
        if not table:
            return ""
        
        html_lines = ["<table>"]
        
        for i, row in enumerate(table):
            if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                continue
            
            html_lines.append("  <tr>")
            
            # 第一行作为表头
            tag = "th" if i == 0 else "td"
            
            for cell in row:
                cell_text = str(cell).strip() if cell is not None else ""
                cell_text = cell_text.replace("\n", "<br>")
                html_lines.append(f"    <{tag}>{cell_text}</{tag}>")
            
            html_lines.append("  </tr>")
        
        html_lines.append("</table>")
        
        return "\n".join(html_lines)
    
    def _parse_image(self, page, img_info: dict, page_num: int) -> str:
        """
        解析图片
        
        Args:
            page: pdfplumber 页面对象
            img_info: 图片信息字典
            page_num: 页码
            
        Returns:
            Markdown 格式的图片引用
        """
        try:
            # pdfplumber 的图片提取比较复杂，这里使用简化方案
            # 将整个页面转为图片（适合扫描版PDF或需要OCR的场景）
            if self.use_ocr:
                # 生成图片文件名
                self.image_counter += 1
                image_filename = f"page_{page_num}_image_{self.image_counter}.png"
                
                if self.save_images:
                    # 将页面转为图片
                    pil_image = page.to_image(resolution=self.image_dpi).original
                    
                    # 保存图片
                    image_path = self.images_dir / image_filename
                    
                    # 转换为RGB模式（透明背景转白底）
                    if pil_image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        if pil_image.mode == 'P':
                            pil_image = pil_image.convert('RGBA')
                        background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ('RGBA', 'LA') else None)
                        pil_image = background
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    pil_image.save(image_path, 'PNG', dpi=(self.image_dpi, self.image_dpi))
                    
                    # OCR 处理
                    ocr_text = self._call_ocr(str(image_path))
                    
                    # 返回 Markdown 图片引用（使用相对路径）
                    relative_path = f"{self.images_dir.name}/{image_filename}"
                    result = f"![{image_filename}]({relative_path})"
                    if ocr_text:
                        result += f"\n\n**图片文字识别：**\n{ocr_text}"
                    
                    return result
                else:
                    # 不保存图片，仅标注位置
                    return f"[图片位置: 第{page_num}页, {image_filename}]"
            
            return ""
                
        except Exception:
            return ""
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return ['.pdf']
