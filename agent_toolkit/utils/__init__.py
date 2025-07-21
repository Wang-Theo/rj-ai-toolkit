"""
实用工具模块

提供各种辅助功能和工具。
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


class Logger:
    """统一的日志管理器"""
    
    @staticmethod
    def get_logger(name: str, level: str = "INFO") -> logging.Logger:
        """
        获取配置好的日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            
        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger


class ConfigManager:
    """配置文件管理器"""
    
    @staticmethod
    def save_config(config: Dict[str, Any], filepath: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_config(filepath: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载配置
        
        Args:
            filepath: 文件路径
            
        Returns:
            配置字典或None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


class TextFormatter:
    """文本格式化工具"""
    
    @staticmethod
    def format_dict_as_table(data: Dict[str, Any], title: str = "") -> str:
        """
        将字典格式化为表格形式的字符串
        
        Args:
            data: 要格式化的字典
            title: 表格标题
            
        Returns:
            格式化后的字符串
        """
        if not data:
            return "无数据"
        
        lines = []
        if title:
            lines.append(f"📋 {title}")
            lines.append("=" * (len(title) + 4))
        
        max_key_len = max(len(str(k)) for k in data.keys())
        
        for key, value in data.items():
            lines.append(f"{str(key).ljust(max_key_len)} : {value}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_list_as_numbered(items: List[Any], title: str = "") -> str:
        """
        将列表格式化为编号列表
        
        Args:
            items: 要格式化的列表
            title: 列表标题
            
        Returns:
            格式化后的字符串
        """
        if not items:
            return "无项目"
        
        lines = []
        if title:
            lines.append(f"📝 {title}")
            lines.append("=" * (len(title) + 4))
        
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item}")
        
        return "\n".join(lines)


class TimeUtils:
    """时间相关工具"""
    
    @staticmethod
    def get_timestamp() -> str:
        """获取当前时间戳字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_date_string() -> str:
        """获取当前日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")


class ValidationUtils:
    """验证工具"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名中的非法字符"""
        import re
        # 移除或替换非法字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除首尾空格和点
        sanitized = sanitized.strip(' .')
        return sanitized or "unnamed_file"


def create_file_tool() -> Any:
    """
    创建文件操作工具
    
    Returns:
        文件操作工具
    """
    from langchain_core.tools import Tool
    
    def file_operations(command: str) -> str:
        """
        执行文件操作命令
        
        支持的操作：
        - read:filepath - 读取文件内容
        - write:filepath:content - 写入文件
        - list:dirpath - 列出目录内容
        
        Args:
            command: 操作命令
            
        Returns:
            操作结果
        """
        try:
            parts = command.split(':', 2)
            if len(parts) < 2:
                return "错误：命令格式不正确。格式：operation:path 或 operation:path:content"
            
            operation = parts[0].lower()
            filepath = parts[1]
            
            if operation == "read":
                if not os.path.exists(filepath):
                    return f"错误：文件不存在 - {filepath}"
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"文件内容 ({len(content)} 字符):\n{content}"
            
            elif operation == "write":
                if len(parts) < 3:
                    return "错误：写入操作需要提供内容。格式：write:filepath:content"
                content = parts[2]
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"文件已写入: {filepath} ({len(content)} 字符)"
            
            elif operation == "list":
                if not os.path.exists(filepath):
                    return f"错误：目录不存在 - {filepath}"
                items = os.listdir(filepath)
                return f"目录内容 ({len(items)} 项):\n" + "\n".join(items)
            
            else:
                return f"错误：不支持的操作 - {operation}。支持：read, write, list"
                
        except Exception as e:
            return f"文件操作错误: {str(e)}"
    
    return Tool(
        name="file_operations",
        description="文件操作工具。支持读取文件(read:filepath)、写入文件(write:filepath:content)、列出目录(list:dirpath)。",
        func=file_operations,
        args_schema=None
    )
