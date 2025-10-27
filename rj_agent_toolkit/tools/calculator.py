"""
计算器工具模块

提供简单安全的数学计算功能。
"""

from langchain_core.tools import Tool
import re


def create_calculator_tool() -> Tool:
    """
    创建简单的计算器工具
    
    Returns:
        LangChain Tool对象
    """
    def calculate(expression: str) -> str:
        """
        计算数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果
        """
        if not expression or not expression.strip():
            return "错误：请提供数学表达式"
        
        try:
            # 简单的安全检查：只允许数字、基本运算符和括号
            if not re.match(r'^[0-9+\-*/().\s]+$', expression):
                return "错误：只支持基本数学运算"
            
            # 计算表达式
            result = eval(expression)
            
            # 格式化结果
            if isinstance(result, float) and result.is_integer():
                return f"结果: {int(result)}"
            else:
                return f"结果: {result}"
                
        except ZeroDivisionError:
            return "错误：不能除以零"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    return Tool(
        name="calculator",
        description="计算数学表达式，支持 +、-、*、/、括号。例如：(10 + 5) * 2",
        func=calculate
    )
