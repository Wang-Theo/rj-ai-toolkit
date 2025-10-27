"""
RJ AI Toolkit 完整示例

整合了基本使用、自定义工具、自定义模板和配置演示的综合示例。
运行前请确保设置了 DASHSCOPE_API_KEY 环境变量。
"""

import os
from langchain_core.tools import Tool
from rj_agent_toolkit import EnterpriseAgent, Config
from rj_agent_toolkit.tools import (
    create_calculator_tool, 
    create_text_analyzer_tool,
    create_text_sentiment_tool
)


# ============================================================================
# 1. 自定义工具示例
# ============================================================================

def create_weather_tool() -> Tool:
    """创建天气查询工具（模拟数据）"""
    
    def get_weather(city: str) -> str:
        """获取城市天气信息（模拟数据）"""
        weather_data = {
            "北京": {"temperature": "15°C", "condition": "晴", "humidity": "45%"},
            "上海": {"temperature": "18°C", "condition": "多云", "humidity": "60%"},
            "广州": {"temperature": "25°C", "condition": "阴", "humidity": "75%"},
            "深圳": {"temperature": "26°C", "condition": "小雨", "humidity": "80%"},
        }
        
        city = city.strip()
        if city in weather_data:
            data = weather_data[city]
            return f"🌤️ {city}天气信息:\n- 温度: {data['temperature']}\n- 天气: {data['condition']}\n- 湿度: {data['humidity']}"
        else:
            return f"抱歉，暂不支持查询{city}的天气信息。支持的城市：北京、上海、广州、深圳"
    
    return Tool(
        name="weather_query",
        description="查询指定城市的天气信息。输入城市名称，返回天气详情。",
        func=get_weather
    )


def create_password_tool() -> Tool:
    """创建密码生成工具"""
    import random
    import string
    
    def generate_password(length: str = "12") -> str:
        """生成随机密码"""
        try:
            length = int(length)
            if length < 4:
                length = 8
            elif length > 50:
                length = 50
                
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(random.choice(chars) for _ in range(length))
            return f"生成的{length}位安全密码: {password}"
        except:
            return "密码长度必须是数字，推荐8-16位"
    
    return Tool(
        name="password_generator",
        description="生成指定长度的安全密码。输入长度数字（4-50），返回随机密码。",
        func=generate_password
    )


# ============================================================================
# 2. 自定义模板示例
# ============================================================================

def get_customer_service_template():
    """客服Agent模板"""
    return """你是一个友好专业的客户服务代表。请耐心帮助客户解决问题：

可用服务工具：
{tools}

服务流程：
客户问题：{input}
问题分析：理解客户的具体需求和困难
解决方案：选择合适工具 [{tool_names}] 提供帮助
服务执行：{agent_scratchpad}
客户确认：确保问题得到完美解决
贴心提醒：提供相关的注意事项和建议

我很高兴为您服务！有什么可以帮助您的吗？"""


def get_tutor_template():
    """教学导师Agent模板"""
    return """我是您的专业学习导师，致力于帮助您掌握知识：

教学工具：
{tools}

教学方法：
学习目标：{input}
知识点分析：分解学习内容的重点和难点
实践练习：使用工具 [{tool_names}] 进行实际操作
学习指导：{agent_scratchpad}
知识巩固：总结关键概念和要点
进阶建议：推荐后续学习方向

让我们一起开始学习之旅！"""


# ============================================================================
# 3. 配置演示
# ============================================================================

def demo_configurations():
    """演示不同的配置选项"""
    print("🔧 Agent配置演示")
    print("=" * 50)
    
    # 1. 默认配置
    print("1. 默认配置 (平衡模式):")
    default_config = Config()
    print(f"   详细模式: {default_config.VERBOSE}")
    print(f"   返回步骤: {default_config.RETURN_INTERMEDIATE_STEPS}")
    print(f"   最大迭代: {default_config.MAX_ITERATIONS}")
    
    # 2. 生产环境配置
    print("\n2. 生产环境配置 (静默高效):")
    production_config = Config(
        VERBOSE=False,                      # 不显示执行过程
        RETURN_INTERMEDIATE_STEPS=False,    # 不返回中间步骤
        MAX_ITERATIONS=3,                   # 快速响应
        LLM_TEMPERATURE=0.1                 # 更确定的回答
    )
    print(f"   详细模式: {production_config.VERBOSE}")
    print(f"   返回步骤: {production_config.RETURN_INTERMEDIATE_STEPS}")
    print(f"   最大迭代: {production_config.MAX_ITERATIONS}")
    print(f"   温度参数: {production_config.LLM_TEMPERATURE}")
    
    # 3. 开发调试配置
    print("\n3. 开发调试配置 (详细信息):")
    debug_config = Config(
        VERBOSE=True,                       # 显示详细过程
        RETURN_INTERMEDIATE_STEPS=True,     # 返回所有步骤
        MAX_ITERATIONS=15,                  # 允许复杂推理
        LLM_TEMPERATURE=0.3                 # 稍有创意
    )
    print(f"   详细模式: {debug_config.VERBOSE}")
    print(f"   返回步骤: {debug_config.RETURN_INTERMEDIATE_STEPS}")
    print(f"   最大迭代: {debug_config.MAX_ITERATIONS}")
    print(f"   温度参数: {debug_config.LLM_TEMPERATURE}")
    
    return default_config, production_config, debug_config


# ============================================================================
# 4. 完整功能演示
# ============================================================================

def basic_agent_demo():
    """基础Agent演示"""
    print("\n🤖 基础Agent演示")
    print("=" * 50)
    
    try:
        # 创建配置
        config = Config(VERBOSE=True)
        
        # 创建Agent
        agent = EnterpriseAgent(config)
        
        # 添加工具
        agent.add_tools([
            create_calculator_tool(),
            create_text_analyzer_tool(),
            create_weather_tool(),
            create_password_tool()
        ])
        
        # 构建Agent
        agent.build_agent()
        
        # 测试查询
        queries = [
            "请帮我计算 (25 + 35) * 2 的结果",
            "分析这段文本：人工智能正在改变我们的世界",
            "查询北京的天气情况",
            "生成一个12位的安全密码"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 测试 {i}: {query}")
            print("-" * 40)
            result = agent.run(query)
            print(f"✅ 回答: {result['output']}")
            
    except Exception as e:
        print(f"❌ 基础演示出错: {e}")
        print("请确保已设置 DASHSCOPE_API_KEY 环境变量")


def custom_template_demo():
    """自定义模板演示"""
    print("\n🎨 自定义模板演示")
    print("=" * 50)
    
    try:
        # 客服模板演示
        print("1. 客服Agent演示:")
        config = Config(VERBOSE=False)  # 客服模式，简洁回答
        agent = EnterpriseAgent(config)
        agent.add_tools([
            create_calculator_tool(),
            create_weather_tool()
        ])
        
        # 使用客服模板
        agent.build_agent(custom_prompt=get_customer_service_template())
        
        result = agent.run("我想查询上海的天气，还想计算一下25*4等于多少")
        print(f"客服回答: {result['output']}")
        
        # 教学模板演示
        print("\n2. 教学导师Agent演示:")
        tutor_agent = EnterpriseAgent(config)
        tutor_agent.add_tools([
            create_calculator_tool(),
            create_text_analyzer_tool()
        ])
        
        # 使用教学模板
        tutor_agent.build_agent(custom_prompt=get_tutor_template())
        
        result = tutor_agent.run("请教我如何计算圆的面积，圆的半径是5")
        print(f"导师回答: {result['output']}")
        
    except Exception as e:
        print(f"❌ 模板演示出错: {e}")


def batch_processing_demo():
    """批量处理演示"""
    print("\n📊 批量处理演示")
    print("=" * 50)
    
    try:
        # 使用生产环境配置
        config = Config(
            VERBOSE=False,
            RETURN_INTERMEDIATE_STEPS=False,
            MAX_ITERATIONS=3
        )
        
        agent = EnterpriseAgent(config)
        agent.add_tools([
            create_calculator_tool(),
            create_text_analyzer_tool(),
            create_weather_tool()
        ])
        agent.build_agent()
        
        # 批量任务
        tasks = [
            "计算 2^10 的值",
            "分析文本：今天心情很好，阳光明媚",
            "查询深圳天气",
            "计算 (100-25)*0.8 的结果"
        ]
        
        print("开始批量处理...")
        for i, task in enumerate(tasks, 1):
            result = agent.run(task)
            print(f"任务{i}: {task}")
            print(f"结果: {result['output'][:100]}{'...' if len(result['output']) > 100 else ''}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ 批量处理出错: {e}")


# ============================================================================
# 5. 主程序
# ============================================================================

def main():
    """主程序"""
    print("🚀 RJ AI Toolkit 完整功能演示")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 未找到 DASHSCOPE_API_KEY 环境变量")
        print("请设置环境变量后再运行:")
        print("Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        return
    
    print("✅ 环境配置检查通过")
    
    # 1. 配置演示
    demo_configurations()
    
    # 2. 基础功能演示
    basic_agent_demo()
    
    # 3. 自定义模板演示
    custom_template_demo()
    
    # 4. 批量处理演示
    batch_processing_demo()
    
    print("\n🎉 所有演示完成！")
    print("更多功能请参考项目文档和其他示例文件。")


if __name__ == "__main__":
    main()
