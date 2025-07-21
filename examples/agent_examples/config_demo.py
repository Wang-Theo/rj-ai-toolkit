"""
Agent配置示例

演示如何自定义Agent的行为配置参数。
"""

from agent_toolkit import EnterpriseAgent, Config
from agent_toolkit.tools import create_calculator_tool
import os


def main():
    """主函数 - 简单配置演示"""
    print("� Agent配置演示")
    print("=" * 30)
    
    # 1. 默认配置
    print("1. 默认配置:")
    default_config = Config()
    print(f"   详细模式: {default_config.VERBOSE}")
    print(f"   返回步骤: {default_config.RETURN_INTERMEDIATE_STEPS}")
    
    # 2. 静默模式 - 适合生产环境
    print("\n2. 静默模式 (生产环境):")
    silent_config = Config(
        VERBOSE=False,                    # 不显示执行过程
        RETURN_INTERMEDIATE_STEPS=False   # 不返回中间步骤
    )
    print(f"   详细模式: {silent_config.VERBOSE}")
    print(f"   返回步骤: {silent_config.RETURN_INTERMEDIATE_STEPS}")
    
    # 3. 调试模式 - 适合开发环境  
    print("\n3. 调试模式 (开发环境):")
    debug_config = Config(
        VERBOSE=True,                     # 显示详细过程
        RETURN_INTERMEDIATE_STEPS=True,   # 返回所有步骤
        MAX_ITERATIONS=15                 # 允许更多迭代
    )
    print(f"   详细模式: {debug_config.VERBOSE}")
    print(f"   返回步骤: {debug_config.RETURN_INTERMEDIATE_STEPS}")
    print(f"   最大迭代: {debug_config.MAX_ITERATIONS}")
    
    # 4. 实际测试（如果有API密钥）
    if os.getenv("DASHSCOPE_API_KEY"):
        print("\n4. 实际测试:")
        try:
            agent = EnterpriseAgent(silent_config)
            agent.add_tool(create_calculator_tool())
            agent.build_agent()
            
            result = agent.run("计算 10 + 5")
            print(f"   计算结果: {result['output']}")
            print(f"   是否成功: {result['success']}")
            
        except Exception as e:
            print(f"   测试失败: {str(e)}")
    else:
        print("\n💡 设置 DASHSCOPE_API_KEY 环境变量可测试实际效果")
    
    print("\n✅ 配置演示完成！")


if __name__ == "__main__":
    main()
