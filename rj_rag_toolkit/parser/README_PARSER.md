# Parser 使用说明

## 概述

所有 Parser 遵循统一接口：
- **输入**：文件路径
- **输出**：Markdown 格式文本
- **图片**：保存为 PNG 格式（白底，无透明）

## EML Parser

### 输入
- `.eml` 邮件文件

### 输出
- Markdown 格式邮件内容
- 邮件头信息（发件人、收件人、主题、时间）
- 邮件正文（HTML 转 Markdown）
- 附件列表

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_attachments` | bool | True | 是否保存附件 |
| `attachments_dir` | str/Path | None | 附件保存目录 |
| `use_ocr` | bool | False | 是否启用 OCR |
| `ocr_func` | callable | None | OCR 函数，签名: `func(image_path: str) -> str` |
| `image_dpi` | int | 300 | 图片 DPI（分辨率） |

### OCR 识别范围

**EML Parser 的 OCR 仅识别邮件正文中的内嵌图片**：
- ✅ **会识别**：HTML 邮件正文中通过 `<img src="cid:...">` 引用的内嵌图片
- ❌ **不会识别**：附件列表中的图片文件（即使是 PNG、JPG 等格式）
- 📝 **输出格式**：OCR 文本会紧跟在图片引用后，格式为 `**[OCR Content]:** {识别文本}`

### 使用

```python
from rj_rag_toolkit.parser import EMLParser

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

如未指定 `attachments_dir`，默认在 EML 文件同目录下创建：

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

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_images` | bool | True | 是否保存图片 |
| `images_dir` | str/Path | None | 图片保存目录 |
| `use_ocr` | bool | False | 是否启用 OCR |
| `ocr_func` | callable | None | OCR 函数，签名: `func(image_path: str) -> str` |
| `image_dpi` | int | 300 | 图片 DPI（分辨率） |

### OCR 识别范围

**PPTX Parser 的 OCR 识别幻灯片中的所有图片**：
- ✅ **会识别**：所有幻灯片页面中的图片对象
- 📝 **输出格式**：图片以 Markdown 格式引用，OCR 文本作为图片描述

### 使用

```python
from rj_rag_toolkit.parser import PPTXParser

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

如未指定 `images_dir`，默认在 PPTX 文件同目录下创建：

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

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_images` | bool | True | 是否保存图片 |
| `images_dir` | str/Path | None | 图片保存目录 |
| `use_ocr` | bool | False | 是否启用 OCR |
| `ocr_func` | callable | None | OCR 函数，签名: `func(image_path: str) -> str` |
| `image_dpi` | int | 300 | 图片 DPI（分辨率） |

### OCR 识别范围

**DOCX Parser 的 OCR 识别文档正文中的所有图片**：
- ✅ **会识别**：Word 文档内容中嵌入的所有图片
- 📝 **输出格式**：图片以 Markdown 格式引用，OCR 文本作为图片描述

### 使用

```python
from rj_rag_toolkit.parser import DOCXParser

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

如未指定 `images_dir`，默认在 DOCX 文件同目录下创建：

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

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_images` | bool | True | 是否保存图片 |
| `images_dir` | str/Path | None | 图片保存目录 |
| `use_ocr` | bool | False | 是否启用 OCR |
| `ocr_func` | callable | None | OCR 函数，签名: `func(image_path: str) -> str` |
| `image_dpi` | int | 300 | 图片 DPI（分辨率） |

### OCR 识别范围

**PDF Parser 的 OCR 识别模式**：
- ✅ **OCR 模式**：将 PDF 每页转换为图片后进行 OCR 识别（适合扫描版 PDF）
- ❌ **非 OCR 模式**：仅提取 PDF 中的文本和表格，不进行 OCR
- 📝 **使用场景**：扫描版 PDF、图片型 PDF 需要启用 OCR 模式

### 使用

```python
from rj_rag_toolkit.parser import PDFParser

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

如未指定 `images_dir`，默认在 PDF 文件同目录下创建：

```
{filename}_images/
├── page_1_image_1.png
├── page_2_image_1.png
└── ...
```

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

## 附件和图片目录

如果不指定保存目录，各 Parser 会自动创建：
- **EML Parser**：`{filename}_attachments/` （附件和嵌入图片）
- **PPTX Parser**：`{filename}_images/` （图片）
- **DOCX Parser**：`{filename}_images/` （图片）
- **PDF Parser**：`{filename}_images/` （OCR 模式下的图片）

## OCR 使用说明

启用 OCR 时：
- 必须提供 `ocr_func` 参数
- OCR 函数签名：`func(image_path: str) -> str`
- 图片会先保存到临时文件，然后传给 OCR 函数
- 建议配合 `image_dpi` 参数调整识别精度

## 获取支持的文件类型

```python
parser = DOCXParser()
extensions = parser.get_supported_extensions()
# 返回: ['.docx']
```
