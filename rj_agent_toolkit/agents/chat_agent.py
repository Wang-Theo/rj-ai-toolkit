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
        tools: Optional[List] = None,
        debug: bool = False
    ):
        """
        初始化 Agent
        
        Args:
            llm: LangChain LLM 实例
            system_prompt: 系统提示词
            max_history_messages: 最大历史消息数量(保留最近N条)
            tools: 工具列表,默认为 None,使用时需要传入
            debug: 是否启用调试模式,显示 Agent 内部思考过程
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages
        self.tools = tools if tools is not None else []
        self.debug = debug
        
        # 创建持久化检查点器
        self.checkpointer = MemorySaver()
        
        # 创建 Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            checkpointer=self.checkpointer,
            debug=self.debug
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

    def get_history(self, thread_id: str) -> List[Dict]:
        """
        获取指定线程的完整历史对话
        
        从 MemorySaver 中读取该线程的最新 checkpoint，
        返回完整的消息列表（包含角色、内容等信息）

        Args:
            thread_id: 会话线程 ID

        Returns:
            List[Dict]: 对话消息列表，每条消息包含 role 和 content 等字段
                       若无历史或读取失败则返回空列表
        
        示例返回格式:
            [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
                ...
            ]
        """
        try:
            # 构造配置以读取最新的 checkpoint
            config = {"configurable": {"thread_id": thread_id}}
            
            # 从 checkpointer 获取最新的 checkpoint
            checkpoint_tuple = self.checkpointer.get_tuple(config)
            
            if checkpoint_tuple is None:
                return []
            
            # 从 checkpoint 中提取 messages
            checkpoint = checkpoint_tuple.checkpoint
            if 'channel_values' in checkpoint and 'messages' in checkpoint['channel_values']:
                messages = checkpoint['channel_values']['messages']
                
                # 转换为标准格式
                result = []
                for msg in messages:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        # LangChain Message 对象
                        result.append({
                            'role': 'assistant' if msg.type == 'ai' else msg.type,
                            'content': msg.content
                        })
                    elif isinstance(msg, dict):
                        # 已经是字典格式
                        result.append(msg)
                
                return result
            
            return []
            
        except Exception as e:
            print(f"[WARNING] 获取历史对话失败: {str(e)}")
            return []

    def clear_history(self, thread_id: str) -> None:
        """
        清除指定线程的历史对话
        
        删除 MemorySaver 中该线程的所有 checkpoint 和相关数据

        Args:
            thread_id: 会话线程 ID
        """
        try:
            self.checkpointer.delete_thread(thread_id)
            print(f"[INFO] 已清除线程 {thread_id} 的历史对话")
        except Exception as e:
            print(f"[WARNING] 清除历史对话失败: {str(e)}")