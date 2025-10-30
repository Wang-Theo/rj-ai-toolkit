# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Thu Oct 30 2025     │
# └──────────────────────────────┘

"""
Agent 核心模块
负责创建和配置 LangChain Agent
"""

from typing import Dict, List, Optional
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

class ChatAgent:
    """
    Rebate Deal AI Agent
    
    负责处理用户查询、调用工具、管理对话上下文
    """
    
    def __init__(
        self,
        llm,
        system_prompt: str = "You are a helpful assistant with access to various tools.",
        max_history_messages: int = 20,
        tools: Optional[List] = None
    ):
        """
        初始化 Agent
        
        Args:
            llm: LangChain LLM 实例
            system_prompt: 系统提示词
            max_history_messages: 最大历史消息数量(保留最近N条)
            tools: 工具列表,默认为 None,使用时需要传入
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages
        self.tools = tools if tools is not None else []
        
        # 创建持久化检查点器
        self.checkpointer = MemorySaver()
        
        # 创建 Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            checkpointer=self.checkpointer
        )
        
        print(f"[INFO] Agent 初始化成功")
        print(f"[INFO] 已加载工具数: {len(self.tools)}")
    
    def chat(
        self,
        user_input: str,
        thread_id: str,
        history_messages: Optional[List] = None
    ) -> Dict:
        """
        处理用户输入并返回 AI 回复
        
        Args:
            user_input: 用户输入的文本
            thread_id: 会话线程 ID
            history_messages: 历史消息列表(可选)
        
        Returns:
            Dict: 包含 AI 回复和更新后的历史消息
            {
                'response': str,        # AI 的回复文本
                'messages': List,       # 更新后的完整消息历史
                'thread_id': str        # 会话 ID
            }
        """
        # 初始化消息列表
        messages = history_messages.copy() if history_messages else []
        
        # 添加用户输入
        messages.append({"role": "user", "content": user_input})
        
        # 限制历史消息数量
        if len(messages) > self.max_history_messages:
            messages = messages[-self.max_history_messages:]
            print(f"[INFO] 历史消息过多,已截断至最近 {self.max_history_messages} 条")
        
        print(f"[DEBUG] 处理消息, thread_id: {thread_id}")
        print(f"[DEBUG] 当前消息数量: {len(messages)}")
        
        # 配置会话
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # 调用 Agent
            response = self.agent.invoke(
                {"messages": messages},
                config=config
            )
            
            # 提取 AI 回复
            ai_response = response['messages'][-1].content
            
            print(f"[DEBUG] AI 回复长度: {len(ai_response)} 字符")
            
            return {
                'response': ai_response,
                'messages': response['messages'],
                'thread_id': thread_id
            }
        
        except Exception as e:
            print(f"[ERROR] Agent 处理失败: {str(e)}")
            raise
    
    def get_tools_info(self) -> List[Dict]:
        """
        获取已加载的工具信息
        
        Returns:
            List[Dict]: 工具信息列表
        """
        return [
            {
                'name': tool.name,
                'description': tool.description
            }
            for tool in self.tools
        ]