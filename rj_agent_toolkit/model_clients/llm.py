"""
LLM模块 - 用于调用本地Ollama部署的大语言模型 (使用LangChain v0.3)
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate


def call_ollama_llm(system_prompt: str, user_input: str, model: str, base_url: str = "http://localhost:11434/v1", temperature: float = 0.01) -> str:
    """
    使用LangChain v0.3和OpenAI格式调用本地Ollama部署的大语言模型
    
    Args:
        system_prompt: 系统提示词，定义模型的行为和角色
        user_input: 用户输入的问题或指令
        model: 模型名称（例如: "qwen3:8b", "llama3:8b"）
        base_url: Ollama服务地址，默认为 "http://localhost:11434/v1"
        temperature: 温度参数，控制生成的随机性，默认为 0.01
        
    Returns:
        str: 模型生成的回复内容
        
    Example:
        >>> response = call_ollama_llm(
        ...     system_prompt="你是一个专业的助手",
        ...     user_input="如何使用这个工具?",
        ...     model="qwen3:8b"
        ... )
    """
    # 初始化ChatOpenAI客户端,指向本地Ollama服务
    llm = ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key="ollama",  # Ollama不需要真实的API key,但需要提供一个值
        temperature=temperature
    )
    
    try:
        # 构建消息列表
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # 调用模型并获取响应
        response = llm.invoke(messages)
        
        # 返回模型的回复内容
        return response.content
        
    except Exception as e:
        raise Exception(f"调用LLM时发生错误: {str(e)}")


def call_qwen_llm_api(input_json: dict, input_variables_list: list, template: str, model: str, api_key: str = None, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1", temperature: float = 0.01) -> str:
    """
    调用通义千问API生成结果，不使用流式输出
    
    Args:
        input_json: 包含输入数据的 JSON 对象，键值对的内容需要与 input_variables_list 中的变量名对应
        input_variables_list: 提示模板中使用的变量名列表，确保与 input_json 的键一致
        template: 提示模板，定义了模型的输入格式和期望的输出格式。模板中使用 {变量名} 占位符来动态填充输入数据
        model: 模型名称（例如: "qwen-max", "qwen-plus", "qwen-turbo"）
        api_key: API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
        base_url: 通义千问API地址，默认为 "https://dashscope.aliyuncs.com/compatible-mode/v1"
        temperature: 温度参数，控制生成的随机性，默认为 0.01
        
    Returns:
        str: 模型生成的结果字符串，格式由 template 定义
        
    Example:
        >>> response = call_qwen_llm_api(
        ...     input_json={"text": "返利率: 5%", "field": "rebate_rate"},
        ...     input_variables_list=["text", "field"],
        ...     template="从文本中提取{field}: {text}",
        ...     model="qwen-max"
        ... )
    """
    try:
        # 初始化通义千问模型 - 使用OpenAI兼容接口
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            streaming=False,
            temperature=temperature,
        )

        # 创建提示模板
        prompt = PromptTemplate(
            input_variables=input_variables_list,
            template=template,
        )

        # 使用新的 RunnableSequence 方法替代已废弃的 LLMChain
        chain = prompt | llm
        
        # 使用 invoke 方法替代已废弃的 run 方法
        result = chain.invoke(input_json)
        
        # 提取文本内容
        if hasattr(result, 'content'):
            return result.content
        else:
            return str(result)
            
    except Exception as e:
        raise Exception(f"调用阿里云LLM时发生错误: {str(e)}")