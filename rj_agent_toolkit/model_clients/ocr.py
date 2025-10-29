import ollama
import re


def call_ollama_ocr(image_path: str, model: str, base_url: str = "http://localhost:11434", prompt: str = None) -> str:
    """
    从图片中提取所有文字内容，如果包含表格则以 HTML 格式输出
    
    Args:
        image_path: 图像文件的路径
        model: OCR模型名称（例如: "qwen2.5vl:7b", "llava:13b"）
        base_url: Ollama服务地址，默认为 "http://localhost:11434"
        prompt: 自定义提示词，如果为None则使用默认提示词
    
    Returns:
        str: 提取的文字内容，表格以 HTML 格式呈现
        
    Example:
        >>> text = call_ollama_ocr("image.png", model="qwen2.5vl:7b")
        >>> print(text)
    """
    if prompt is None:
        prompt = """Extract all text from the image.

Rules:
- If a table is present, output it as strict HTML using <table>, <tr>, <th>, and <td>.
- Non-table text: output as plain text in original order.
- Output only the extracted content. No explanations, no commentary.
"""
    
    # 创建 Ollama 客户端
    client = ollama.Client(host=base_url)
    
    response = client.chat(
        model=model,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path]
        }]
    )
    
    # 提取响应中的文字内容并做轻量后处理：
    # - 将包含在 ``` 或 ```html 代码块中的 <table>...</table> 解包，保留纯 HTML 表格
    # - 移除残留的三重反引号
    if 'message' in response and 'content' in response['message']:
        content = response['message']['content']

        # 如果模型把表格用代码块包裹（如 ```html 或 ```），提取出其中的 <table>...</table>
        content = re.sub(r"```[^\n]*\s*(<table[\s\S]*?</table>)\s*```",
                         r"\1",
                         content,
                         flags=re.IGNORECASE)

        return content.strip()

    return ""

