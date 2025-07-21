"""
核心Agent实现模块

提供企业级LangChain Agent的核心实现。
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
import logging
from typing import List, Dict, Any, Optional

from .config import Config


class EnterpriseAgent:
    """企业级LangChain Agent核心类"""
 
    def __init__(self, config: Config):
        """
        初始化Agent
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.llm = self._initialize_llm()
        self.memory = self._initialize_memory()
        self.tools: List[Tool] = []
        self.agent: Optional[AgentExecutor] = None
        self.logger = self._setup_logger()
        
        # 验证配置
        if not self.config.validate():
            raise ValueError("配置验证失败，请检查配置参数")
 
    def _initialize_llm(self) -> ChatOpenAI:
        """初始化大语言模型 - 使用阿里云千问模型"""
        return ChatOpenAI(
            api_key=self.config.DASHSCOPE_API_KEY,
            base_url=self.config.BASE_URL,
            model=self.config.LLM_MODEL,
            temperature=self.config.LLM_TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS
        )
 
    def _initialize_memory(self) -> ConversationBufferWindowMemory:
        """初始化对话记忆"""
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=self.config.MEMORY_K,
            return_messages=True,
            output_key="output"
        )
 
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"EnterpriseAgent.{id(self)}")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # 避免重复添加handler
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.config.LOG_FORMAT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
 
    def add_tool(self, tool: Tool) -> None:
        """
        添加工具到Agent
        
        Args:
            tool: LangChain工具对象
        """
        if not isinstance(tool, Tool):
            raise TypeError("工具必须是LangChain Tool类型")
            
        self.tools.append(tool)
        self.logger.info(f"已添加工具: {tool.name}")
    
    def add_tools(self, tools: List[Tool]) -> None:
        """
        批量添加工具
        
        Args:
            tools: 工具列表
        """
        for tool in tools:
            self.add_tool(tool)
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        移除指定名称的工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否成功移除
        """
        for i, tool in enumerate(self.tools):
            if tool.name == tool_name:
                self.tools.pop(i)
                self.logger.info(f"已移除工具: {tool_name}")
                return True
        return False
    
    def list_tools(self) -> List[str]:
        """获取所有工具名称列表"""
        return [tool.name for tool in self.tools]
 
    def build_agent(self, custom_prompt: Optional[str] = None) -> None:
        """
        构建Agent执行器
        
        Args:
            custom_prompt: 自定义提示模板
        """
        if not self.tools:
            raise ValueError("至少需要一个工具才能构建Agent")
 
        # 使用自定义提示或默认提示
        if custom_prompt:
            react_prompt = PromptTemplate.from_template(custom_prompt)
        else:
            react_prompt = self._get_default_prompt()
        
        # 创建React代理
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt
        )
        
        # 创建代理执行器
        self.agent = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            max_iterations=self.config.MAX_ITERATIONS,
            verbose=self.config.VERBOSE,
            return_intermediate_steps=self.config.RETURN_INTERMEDIATE_STEPS,
            handle_parsing_errors=self.config.HANDLE_PARSING_ERRORS
        )
        self.logger.info("Agent构建完成")
    
    def _get_default_prompt(self) -> PromptTemplate:
        """获取默认的React提示模板"""
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        return PromptTemplate.from_template(template)
 
    def run(self, query: str) -> Dict[str, Any]:
        """
        执行Agent查询
        
        Args:
            query: 用户查询
            
        Returns:
            包含结果和元数据的字典
        """
        if not self.agent:
            raise ValueError("请先调用build_agent()构建Agent")
 
        try:
            self.logger.info(f"开始处理查询: {query}")
            result = self.agent.invoke({"input": query})
 
            return {
                "success": True,
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "chat_history": self.memory.chat_memory.messages if self.memory else []
            }
 
        except Exception as e:
            self.logger.error(f"Agent执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": "抱歉，处理您的请求时遇到了问题。"
            }
    
    def reset_memory(self) -> None:
        """重置对话记忆"""
        self.memory.clear()
        self.logger.info("对话记忆已重置")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """获取记忆摘要"""
        messages = self.memory.chat_memory.messages
        return {
            "total_messages": len(messages),
            "recent_messages": [msg.content for msg in messages[-3:]] if messages else []
        }
    
    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            "model": self.config.LLM_MODEL,
            "temperature": self.config.LLM_TEMPERATURE,
            "max_tokens": self.config.MAX_TOKENS,
            "max_iterations": self.config.MAX_ITERATIONS,
            "verbose": self.config.VERBOSE,
            "return_intermediate_steps": self.config.RETURN_INTERMEDIATE_STEPS,
            "handle_parsing_errors": self.config.HANDLE_PARSING_ERRORS,
            "tools": self.list_tools(),
            "memory_k": self.config.MEMORY_K
        }
