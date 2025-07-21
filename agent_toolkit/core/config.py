"""
配置管理模块

定义Agent和相关组件的配置类。
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Agent配置类"""
    
    # 阿里云千问模型配置
    DASHSCOPE_API_KEY: str = ""
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-max"
    LLM_TEMPERATURE: float = 0.01
    MAX_TOKENS: int = 8000
    MAX_ITERATIONS: int = 10
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 内存配置
    MEMORY_K: int = 10  # 保留最近N轮对话
    
    # Agent行为配置
    VERBOSE: bool = True  # 是否显示详细执行过程
    RETURN_INTERMEDIATE_STEPS: bool = True  # 是否返回中间步骤
    HANDLE_PARSING_ERRORS: bool = True  # 是否处理解析错误
    
    def __post_init__(self):
        """初始化后处理，从环境变量获取API密钥"""
        if not self.DASHSCOPE_API_KEY:
            self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
            
        if not self.DASHSCOPE_API_KEY:
            raise ValueError(
                "请设置DASHSCOPE_API_KEY环境变量或在Config中提供API密钥"
            )
    
    @classmethod
    def from_env(cls, **kwargs) -> "Config":
        """从环境变量创建配置"""
        config = cls(**kwargs)
        return config
    
    def validate(self) -> bool:
        """验证配置有效性"""
        if not self.DASHSCOPE_API_KEY:
            return False
        if self.MAX_TOKENS <= 0:
            return False
        if self.MAX_ITERATIONS <= 0:
            return False
        return True