# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Mon Nov 04 2025     │
# └──────────────────────────────┘

"""
Prompt 管理模块
提供灵活的 Prompt 注册和管理功能
"""

from typing import Dict, List, Optional


class PromptManager:
    """
    Prompt 管理类
    
    用于注册和管理不同用户角色的 System Prompt
    支持一个 user 拥有多个 prompt 用于不同用途
    
    使用示例:
        >>> manager = PromptManager()
        >>> # 为 gcm 用户注册查询专用 prompt
        >>> manager.register(
        ...     prompt_id='gcm_query',
        ...     user='gcm',
        ...     prompt_content='你是负责查询的助手...',
        ...     description='GCM 查询数据专用'
        ... )
        >>> # 为 gcm 用户注册提交专用 prompt
        >>> manager.register(
        ...     prompt_id='gcm_submit',
        ...     user='gcm',
        ...     prompt_content='你是负责提交的助手...',
        ...     description='GCM 提交 Deal 专用'
        ... )
        >>> # 获取特定 prompt
        >>> prompt = manager.get_prompt('gcm_query')
        >>> # 检查 prompt 是否存在
        >>> if manager.has_prompt('gcm_query'):
        ...     print('存在')
        >>> # 删除 prompt
        >>> manager.delete_prompt('gcm_query')
        >>> # 列出所有 prompt
        >>> all_prompts = manager.list_prompts()
        >>> # 列出 gcm 用户的所有 prompt
        >>> gcm_prompts = manager.list_prompts(user='gcm')
    """
    
    def __init__(self):
        """初始化 Prompt 管理器"""
        self._prompts: Dict[str, Dict[str, any]] = {}
    
    def register(
        self, 
        prompt_id: str,
        user: str,
        prompt_content: str,
        description: str = "",
        update: bool = False
    ) -> None:
        """
        注册一个 Prompt
        
        Args:
            prompt_id: Prompt 唯一标识符 (如 'gcm_query', 'gcm_submit')
            user: 用户类型 (如 'gcm', 'finance')
            prompt_content: Prompt 内容字符串（必填）
            description: 该 Prompt 的描述信息（选填）
            update: 是否允许更新已存在的 prompt，默认 False
        """
        # 检查 prompt_id 是否已存在
        if prompt_id in self._prompts and not update:
            raise ValueError(
                f"Prompt ID '{prompt_id}' 已存在。"
                f"已注册信息: user='{self._prompts[prompt_id]['user']}', "
                f"description='{self._prompts[prompt_id]['description']}'。"
                f"如需更新，请设置 update=True"
            )
        
        # 检查类型
        if not isinstance(prompt_content, str):
            raise TypeError(f"prompt_content 必须是字符串")
        
        self._prompts[prompt_id] = {
            'user': user,
            'content': prompt_content,
            'description': description
        }
    
    def get_prompt(self, prompt_id: str) -> str:
        """
        获取指定 Prompt 的内容
        
        Args:
            prompt_id: Prompt 唯一标识符
            
        Returns:
            str: System Prompt 内容
        """
        if prompt_id not in self._prompts:
            raise KeyError(f"Prompt ID '{prompt_id}' 未注册")
        
        return self._prompts[prompt_id]['content']
    
    def get_prompt_by_user(self, user: str, prompt_id: str) -> str:
        """
        通过用户和 Prompt ID 获取内容（带用户验证）
        
        Args:
            user: 用户类型
            prompt_id: Prompt 唯一标识符
            
        Returns:
            str: System Prompt 内容
            
        Raises:
            KeyError: 如果 prompt_id 未注册
            ValueError: 如果 prompt_id 不属于指定用户
        """
        if prompt_id not in self._prompts:
            raise KeyError(f"Prompt ID '{prompt_id}' 未注册")
        
        if self._prompts[prompt_id]['user'] != user:
            raise ValueError(
                f"Prompt ID '{prompt_id}' 不属于用户 '{user}'，"
                f"实际属于用户 '{self._prompts[prompt_id]['user']}'"
            )
        
        return self._prompts[prompt_id]['content']
    
    def has_prompt(self, prompt_id: str) -> bool:
        """
        检查是否已注册指定 Prompt
        
        Args:
            prompt_id: Prompt 唯一标识符
            
        Returns:
            bool: 如果已注册返回 True，否则返回 False
        """
        return prompt_id in self._prompts
    
    def delete_prompt(self, prompt_id: str) -> None:
        """
        删除指定的 Prompt
        
        Args:
            prompt_id: Prompt 唯一标识符
            
        Raises:
            KeyError: 如果 prompt_id 未注册
        """
        if prompt_id not in self._prompts:
            raise KeyError(f"Prompt ID '{prompt_id}' 未注册")
        
        del self._prompts[prompt_id]
    
    def list_prompts(self, user: Optional[str] = None) -> List[Dict[str, str]]:
        """
        列出已注册的 Prompt
        
        Args:
            user: 可选，指定用户类型以过滤结果。如果为 None，返回所有 prompt
            
        Returns:
            List[Dict]: 包含 Prompt 信息的列表，每个字典包含: prompt_id, user, description
        """
        prompts = [
            {
                'prompt_id': prompt_id,
                'user': info['user'],
                'description': info['description']
            }
            for prompt_id, info in self._prompts.items()
        ]
        
        # 如果指定了 user，过滤结果
        if user is not None:
            prompts = [p for p in prompts if p['user'] == user]
        
        return prompts


# 导出类
__all__ = ['PromptManager']
