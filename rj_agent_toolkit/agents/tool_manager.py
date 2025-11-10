# ┌──────────────────────────────┐
# │ Author:  Renjie Wang         │
# │ Created: Thu Oct 30 2025     │
# └──────────────────────────────┘

"""
Tool 管理模块
提供灵活的 Tool 和 Toolset 双层管理功能
"""

from typing import Dict, List, Optional, Callable


class ToolManager:
    """
    Tool 和 Toolset 双层管理器
    
    管理单个 tool 及其元数据（Tool 层）
    管理工具集组合（Toolset 层）
    
    使用示例:
        >>> manager = ToolManager()
        
        >>> # 1. 注册单个 tool（LangChain tool 自动提取元数据）
        >>> manager.register_tool(
        ...     tool_id='query_db',
        ...     tool_func=query_database,
        ...     category='database'
        ... )
        
        >>> # 2. 注册单个 tool（普通函数需要手动提供描述）
        >>> manager.register_tool(
        ...     tool_id='my_tool',
        ...     tool_func=my_function,
        ...     description='手动提供的描述',
        ...     category='custom'
        ... )
        
        >>> # 3. 注册 toolset（引用 tool_id）
        >>> manager.register_toolset(
        ...     toolset_id='gcm_query',
        ...     user='gcm',
        ...     tool_ids=['query_db', 'my_tool'],
        ...     description='GCM 查询专用工具集'
        ... )
        
        >>> # 4. 获取 toolset 的实际函数列表
        >>> tools = manager.get_toolset('gcm_query')
        
        >>> # 5. 列出所有 tool
        >>> all_tools = manager.list_tools()
        
        >>> # 6. 列出所有 toolset
        >>> all_toolsets = manager.list_toolsets()
    """
    
    def __init__(self):
        """初始化 Tool 管理器"""
        self._tools: Dict[str, Dict[str, any]] = {}  # tool_id -> tool 信息
        self._toolsets: Dict[str, Dict[str, any]] = {}  # toolset_id -> toolset 信息
    
    # ==================== Tool 层：管理单个 tool ====================
    
    def register_tool(
        self,
        tool_id: str,
        tool_func: Callable,
        description: str = "",
        category: str = "",
        update: bool = False
    ) -> None:
        """
        注册单个 tool
        
        Args:
            tool_id: Tool 唯一标识符 (如 'query_db', 'validate_data')
            tool_func: Tool 函数（支持 LangChain tool 自动提取元数据）
            description: Tool 描述（选填，LangChain tool 会自动提取）
            category: Tool 分类（选填，如 'database', 'validation'）
            update: 是否允许更新已存在的 tool，默认 False
        """
        # 检查 tool_id 是否已存在
        if tool_id in self._tools and not update:
            raise ValueError(
                f"Tool ID '{tool_id}' 已存在。"
                f"已注册信息: name='{self._tools[tool_id]['name']}', "
                f"category='{self._tools[tool_id]['category']}'。"
                f"如需更新，请设置 update=True"
            )
        
        # 自动提取元数据（支持 LangChain tool）
        if hasattr(tool_func, 'name'):
            name = tool_func.name
        else:
            name = tool_func.__name__
        
        # 如果没有手动提供 description，尝试从 tool_func 提取
        if not description and hasattr(tool_func, 'description'):
            description = tool_func.description
        
        self._tools[tool_id] = {
            'func': tool_func,
            'name': name,
            'description': description,
            'category': category
        }
    
    def get_tool(self, tool_id: str) -> Callable:
        """
        获取单个 tool 函数
        
        Args:
            tool_id: Tool 唯一标识符
            
        Returns:
            Callable: Tool 函数
        """
        if tool_id not in self._tools:
            raise KeyError(f"Tool ID '{tool_id}' 未注册")
        
        return self._tools[tool_id]['func']
    
    def has_tool(self, tool_id: str) -> bool:
        """
        检查是否已注册指定 tool
        
        Args:
            tool_id: Tool 唯一标识符
            
        Returns:
            bool: 如果已注册返回 True，否则返回 False
        """
        return tool_id in self._tools
    
    def delete_tool(self, tool_id: str) -> None:
        """
        删除指定的 tool
        
        Args:
            tool_id: Tool 唯一标识符
            
        Raises:
            KeyError: 如果 tool_id 未注册
        """
        if tool_id not in self._tools:
            raise KeyError(f"Tool ID '{tool_id}' 未注册")
        
        del self._tools[tool_id]
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """
        列出已注册的 tool
        
        Args:
            category: 可选，按分类过滤。如果为 None，返回所有 tool
            
        Returns:
            List[Dict]: 包含 tool 信息的列表，每个字典包含: tool_id, name, description, category
        """
        tools_list = [
            {
                'tool_id': tool_id,
                'name': info['name'],
                'description': info['description'],
                'category': info['category']
            }
            for tool_id, info in self._tools.items()
        ]
        
        # 如果指定了 category，过滤结果
        if category is not None:
            tools_list = [t for t in tools_list if t['category'] == category]
        
        return tools_list
    
    # ==================== Toolset 层：管理工具集 ====================
    
    def register_toolset(
        self,
        toolset_id: str,
        user: str,
        tool_ids: List[str],
        description: str = "",
        update: bool = False
    ) -> None:
        """
        注册工具集（引用 tool_id 列表）
        
        Args:
            toolset_id: Toolset 唯一标识符 (如 'gcm_query', 'gcm_submit')
            user: 用户类型 (如 'gcm', 'finance')
            tool_ids: Tool ID 列表（必填）
            description: 该工具集的描述信息（选填）
            update: 是否允许更新已存在的工具集，默认 False
        """
        # 检查 toolset_id 是否已存在
        if toolset_id in self._toolsets and not update:
            raise ValueError(
                f"Toolset ID '{toolset_id}' 已存在。"
                f"已注册信息: user='{self._toolsets[toolset_id]['user']}', "
                f"description='{self._toolsets[toolset_id]['description']}'。"
                f"如需更新，请设置 update=True"
            )
        
        # 检查类型
        if not isinstance(tool_ids, list):
            raise TypeError(f"tool_ids 必须是列表")
        
        # 验证所有 tool_id 都已注册
        for tool_id in tool_ids:
            if tool_id not in self._tools:
                raise KeyError(f"Tool ID '{tool_id}' 未注册，请先使用 register_tool() 注册")
        
        self._toolsets[toolset_id] = {
            'user': user,
            'tool_ids': tool_ids,
            'description': description
        }
    
    def get_toolset(self, toolset_id: str) -> List[Callable]:
        """
        获取工具集的实际函数列表
        
        Args:
            toolset_id: Toolset 唯一标识符
            
        Returns:
            List[Callable]: Tool 函数列表
        """
        if toolset_id not in self._toolsets:
            raise KeyError(f"Toolset ID '{toolset_id}' 未注册")
        
        tool_ids = self._toolsets[toolset_id]['tool_ids']
        return [self._tools[tool_id]['func'] for tool_id in tool_ids]
    
    def get_toolset_by_user(self, user: str, toolset_id: str) -> List[Callable]:
        """
        通过用户和 Toolset ID 获取工具集（带用户验证）
        
        Args:
            user: 用户类型
            toolset_id: Toolset 唯一标识符
            
        Returns:
            List[Callable]: Tool 函数列表
            
        Raises:
            KeyError: 如果 toolset_id 未注册
            ValueError: 如果 toolset_id 不属于指定用户
        """
        if toolset_id not in self._toolsets:
            raise KeyError(f"Toolset ID '{toolset_id}' 未注册")
        
        if self._toolsets[toolset_id]['user'] != user:
            raise ValueError(
                f"Toolset ID '{toolset_id}' 不属于用户 '{user}'，"
                f"实际属于用户 '{self._toolsets[toolset_id]['user']}'"
            )
        
        tool_ids = self._toolsets[toolset_id]['tool_ids']
        return [self._tools[tool_id]['func'] for tool_id in tool_ids]
    
    def has_toolset(self, toolset_id: str) -> bool:
        """
        检查是否已注册指定 toolset
        
        Args:
            toolset_id: Toolset 唯一标识符
            
        Returns:
            bool: 如果已注册返回 True，否则返回 False
        """
        return toolset_id in self._toolsets
    
    def delete_toolset(self, toolset_id: str) -> None:
        """
        删除指定的 toolset
        
        Args:
            toolset_id: Toolset 唯一标识符
            
        Raises:
            KeyError: 如果 toolset_id 未注册
        """
        if toolset_id not in self._toolsets:
            raise KeyError(f"Toolset ID '{toolset_id}' 未注册")
        
        del self._toolsets[toolset_id]
    
    def list_toolsets(self, user: Optional[str] = None) -> List[Dict[str, any]]:
        """
        列出已注册的 toolset
        
        Args:
            user: 可选，指定用户类型以过滤结果。如果为 None，返回所有 toolset
            
        Returns:
            List[Dict]: 包含 toolset 信息的列表，每个字典包含: toolset_id, user, description, tool_ids, tool_count
        """
        toolsets_list = [
            {
                'toolset_id': toolset_id,
                'user': info['user'],
                'description': info['description'],
                'tool_ids': info['tool_ids'],
                'tool_count': len(info['tool_ids'])
            }
            for toolset_id, info in self._toolsets.items()
        ]
        
        # 如果指定了 user，过滤结果
        if user is not None:
            toolsets_list = [t for t in toolsets_list if t['user'] == user]
        
        return toolsets_list


# 导出类
__all__ = ['ToolManager']
