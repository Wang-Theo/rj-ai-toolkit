# Parser 使用说明

## 概述

所有 Parser 遵循统一接口：
- **输入**：文件路径
- **输出**：Markdown 格式文本
- **图片**：保存为 PNG 格式（白底，无透明）

## 基础用法

### 导入

```python
from rag_toolkit.parser import EMLParser, PPTXParser, DOCXParser, PDFParser
```

### 基本解析

```python
# 创建解析器
parser = DOCXParser()

# 解析文件（返回 Markdown 文本）
markdown_text = parser.parse_file("document.docx")
```

## EML Parser

### 输入
- `.eml` 邮件文件

### 输出
- Markdown 格式邮件内容
- 邮件头信息（发件人、收件人、主题、时间）
- 邮件正文（HTML 转 Markdown）
- 附件列表

### 使用

```python
from rag_toolkit.parser import EMLParser

# 基本用法
parser = EMLParser()
markdown = parser.parse_file("email.eml")

# 保存附件和图片
parser = EMLParser(
    save_attachments=True,           # 保存附件
    attachments_dir="./attachments"  # 指定附件目录
)

# 启用 OCR
parser = EMLParser(
    use_ocr=True,
    ocr_func=my_ocr_function,
    image_dpi=300
)
```

### 附件保存结构
```
{filename}_attachments/
├── embedded/     # 邮件内嵌图片（转为 PNG）
└── files/        # 附件文件
```

## PPTX Parser

### 输入
- `.pptx` PowerPoint 文件

### 输出
- Markdown 格式幻灯片内容
- 按幻灯片页编号组织
- 文本内容
- 表格（HTML 格式）
- 图片引用

### 使用

```python
from rag_toolkit.parser import PPTXParser

# 基本用法
parser = PPTXParser()
markdown = parser.parse_file("presentation.pptx")

# 保存图片
parser = PPTXParser(
    save_images=True,
    images_dir="./images"
)

# 启用 OCR
parser = PPTXParser(
    use_ocr=True,
    ocr_func=my_ocr_function,
    save_images=True,
    image_dpi=300
)
```

### 图片保存结构
```
{filename}_images/
├── image_001.png
├── image_002.png
└── ...
```

## DOCX Parser

### 输入
- `.docx` Word 文档文件

### 输出
- Markdown 格式文档内容
- 标题层级（# ## ###）
- 段落文本
- 表格（HTML 格式）
- 图片引用

### 使用

```python
from rag_toolkit.parser import DOCXParser

# 基本用法
parser = DOCXParser()
markdown = parser.parse_file("document.docx")

# 保存图片
parser = DOCXParser(
    save_images=True,
    images_dir="./images"
)

# 启用 OCR
parser = DOCXParser(
    use_ocr=True,
    ocr_func=my_ocr_function,
    save_images=True,
    image_dpi=300
)
```

### 图片保存结构
```
{filename}_images/
├── image_1.png
├── image_2.png
└── ...
```

## PDF Parser

### 输入
- `.pdf` PDF 文件

### 输出
- Markdown 格式 PDF 内容
- 按页编号组织（## 第 N 页）
- 文本内容
- 表格（HTML 格式）
- 图片引用（仅 OCR 模式）

### 使用

```python
from rag_toolkit.parser import PDFParser

# 基本解析（仅提取文本和表格）
parser = PDFParser(save_images=False)
markdown = parser.parse_file("document.pdf")

# OCR 模式（扫描版 PDF）
parser = PDFParser(
    use_ocr=True,
    ocr_func=my_ocr_function,
    save_images=True,
    image_dpi=300
)
markdown = parser.parse_file("scanned.pdf")
```

### 图片保存结构（OCR 模式）
```
{filename}_images/
├── page_1_image_1.png
├── page_2_image_1.png
└── ...
```

## 参数说明

### 通用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_ocr` | bool | False | 是否启用 OCR |
| `ocr_func` | callable | None | OCR 函数，签名: `func(image_path: str) -> str` |
| `image_dpi` | int | 300 | 图片 DPI（分辨率） |

### EML 专用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_attachments` | bool | True | 是否保存附件 |
| `attachments_dir` | str/Path | None | 附件保存目录 |

### PPTX/DOCX/PDF 专用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_images` | bool | True | 是否保存图片 |
| `images_dir` | str/Path | None | 图片保存目录 |

## OCR 函数示例

```python
def my_ocr_function(image_path: str) -> str:
    """
    自定义 OCR 函数
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        识别的文本内容
    """
    # 使用 PaddleOCR
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    result = ocr.ocr(image_path, cls=True)
    text = '\n'.join([line[1][0] for line in result[0]])
    return text

# 使用
parser = DOCXParser(
    use_ocr=True,
    ocr_func=my_ocr_function
)
```

## 图片格式

所有 Parser 保存的图片统一为：
- **格式**：PNG（无损）
- **颜色**：RGB（透明背景自动转为白底）
- **DPI**：可配置（默认 300）

## 获取支持的文件类型

```python
parser = DOCXParser()
extensions = parser.get_supported_extensions()
# 返回: ['.docx']
```
