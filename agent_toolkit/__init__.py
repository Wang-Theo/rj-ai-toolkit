"""
RJ AI Toolkit - Agent Module

企业级LangChain Agent开发工具包，是RJ AI Toolkit的一部分。
提供智能对话代理、工具集成和企业级功能。

Author: Renjie Wang
Version: 0.1.0
"""

from .core.agent import EnterpriseAgent
from .core.config import Config
from .tools.calculator import create_calculator_tool
from .tools.text_analyzer import create_text_analyzer_tool

__version__ = "0.1.0"
__author__ = "Renjie Wang"
__email__ = "renjiewang31@gmail.com"
__description__ = "RJ AI Toolkit - Agent模块"

__all__ = [
    "EnterpriseAgent",
    "Config", 
    "create_calculator_tool",
    "create_text_analyzer_tool"
]

# 包级别的配置
DEFAULT_CONFIG = {
    "version": __version__,
    "package_name": "rj-ai-toolkit",
    "module_name": "agent_toolkit",
    "supported_python": ">=3.8",
}
