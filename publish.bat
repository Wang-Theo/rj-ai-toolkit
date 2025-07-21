@echo off
echo 🚀 Agent LangChain RJ Dev - 快速发布脚本
echo ==========================================

echo.
echo 📦 1. 初始化Git仓库...
git init

echo.
echo 📝 2. 添加所有文件...
git add .

echo.
echo 💾 3. 创建初始提交...
git commit -m "🎉 Initial release: Agent LangChain RJ Dev v0.1.0

- ✨ 企业级LangChain Agent核心实现
- 🛠️ 丰富的内置工具（计算器、文本分析、情感分析）  
- 📝 完整的文档和示例
- 🔧 易于扩展的架构设计

Author: Renjie Wang
Email: renjiewang31@gmail.com"

echo.
echo 🔗 4. 连接到GitHub仓库...
git remote add origin https://github.com/Wang-Theo/rj-ai-toolkit.git

echo.
echo 📤 5. 推送到GitHub...
git branch -M main
git push -u origin main

echo.
echo 🏷️ 6. 创建版本标签...
git tag -a v0.1.0 -m "Release v0.1.0 - 初始版本发布"
git push origin v0.1.0

echo.
echo ✅ 发布完成！
echo.
echo 📋 下一步操作：
echo 1. 访问 https://github.com/Wang-Theo/agent_langchain_RJ_dev
echo 2. 创建GitHub Release（可选）
echo 3. 用户可以通过以下命令安装：
echo    pip install git+https://github.com/Wang-Theo/agent_langchain_RJ_dev.git
echo.
pause
