# RJ AI Toolkit

🚀 **企业级AI工具包集合** - 包含Agent、RAG等多种AI开发工具的完整解决方案

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Package Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/Wang-Theo/rj-ai-toolkit)

## 📦 工具包概览

RJ AI Toolkit 是一个企业级AI开发工具包集合，提供了开发智能应用所需的核心组件。每个工具包都可以独立使用，也可以组合使用来构建复杂的AI应用。

### 🤖 [Agent Toolkit](./agent_toolkit/README.md)
**智能对话代理工具包**
- 基于LangChain框架的企业级智能对话代理
- 深度集成阿里云千问大模型API
- 内置丰富工具：计算器、文本分析、情感分析等
- 支持自定义工具和Agent模板
- 完整的对话记忆和上下文管理

### 📚 [RAG Toolkit](./rag_toolkit/README.md)
**检索增强生成工具包**
- 智能文档切块：递归切块、语义切块等多种策略
- 多格式文档解析：PDF、Word、文本、Markdown等
- 高效向量检索：基于BGE等先进嵌入模型
- 混合检索策略：结合向量检索和BM25算法
- 智能重排序：使用重排序模型提高检索精度
- 完整的数据库管理：文档库和向量库

## 🚀 快速开始

### 安装

#### 从 GitHub 安装（推荐）
```bash
pip install git+https://github.com/Wang-Theo/rj-ai-toolkit.git
```

#### 从源码安装
```bash
git clone https://github.com/Wang-Theo/rj-ai-toolkit.git
cd rj-ai-toolkit
pip install -e .
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### Agent Toolkit 使用示例

```python
from agent_toolkit import EnterpriseAgent, Config
from agent_toolkit.tools import create_calculator_tool, create_text_analyzer_tool

# 设置环境变量
# set DASHSCOPE_API_KEY=your_api_key_here

# 创建Agent
config = Config()
agent = EnterpriseAgent(config)

# 添加工具
agent.add_tools([
    create_calculator_tool(),
    create_text_analyzer_tool()
])

# 构建并运行
agent.build_agent()
result = agent.run("请帮我计算 (25 + 35) * 2 并分析结果")
print(result["output"])
```

### RAG Toolkit 使用示例

```python
from rag_toolkit import RAGApi
from rag_toolkit.chunker import ChunkConfig, ChunkStrategy

# 初始化RAG系统
rag = RAGApi(
    vector_db_config={
        "persist_directory": "./vector_db",
        "collection_name": "my_docs"
    },
    chunk_config=ChunkConfig(chunk_size=500, chunk_overlap=50)
)

# 添加文档
result = rag.add_document("path/to/document.pdf")

# 智能搜索
results = rag.search(
    query="RAG系统如何工作？",
    top_k=5,
    retrieval_method="hybrid",
    rerank=True
)

for result in results:
    print(f"相关度: {result['score']:.3f}")
    print(f"内容: {result['content'][:200]}...")
```

## 📖 详细文档

- **[Agent Toolkit 详细文档](./agent_toolkit/README.md)** - 智能对话代理的完整使用指南
- **[RAG Toolkit 详细文档](./rag_toolkit/README.md)** - 检索增强生成系统的详细说明

## 🔧 示例代码

### Agent 示例
```bash
# Agent完整功能演示
python examples/agent_examples/complete_example.py
```

### RAG 示例
```bash
# RAG快速开始
python examples/rag_examples/quick_start.py

# RAG完整功能演示
python examples/rag_examples/complete_rag_demo.py
```

## 🏗️ 项目结构

```
rj-ai-toolkit/
├── agent_toolkit/                 # 🤖 智能对话代理工具包
│   ├── README.md                  # Agent文档
│   ├── core/                      # 核心模块
│   ├── tools/                     # 内置工具
│   └── utils/                     # 实用工具
├── rag_toolkit/                   # 📚 检索增强生成工具包
│   ├── README.md                  # RAG文档
│   ├── api.py                     # 统一API接口
│   ├── chunker/                   # 文档切块器
│   ├── parser/                    # 文档解析器
│   ├── db_manager/                # 数据库管理器
│   ├── retriever/                 # 检索器
│   └── ranker/                    # 重排序器
├── examples/                      # 📝 使用示例
│   ├── agent_examples/            # Agent示例
│   └── rag_examples/              # RAG示例
├── requirements.txt               # 依赖清单
├── setup.py                      # 包配置
└── README.md                      # 总体文档
```

## ⚙️ 系统要求

- **Python**: 3.8+
- **操作系统**: Windows、Linux、macOS
- **内存**: 建议4GB以上（RAG功能）
- **存储**: 预留2GB空间用于模型缓存

## 🔧 配置说明

### 环境变量
```bash
# Agent Toolkit
DASHSCOPE_API_KEY=your_dashscope_api_key

# RAG Toolkit（可选）
HF_ENDPOINT=https://hf-mirror.com  # 国内镜像加速
```

### 数据库配置
- **向量数据库**: ChromaDB（默认）
- **文档数据库**: SQLite（默认）
- **可选**: Pinecone、Elasticsearch等

## 🚀 性能优化

### GPU加速
```python
# 启用GPU加速（需要CUDA）
vector_config = {
    "embeddings": {
        "model_kwargs": {"device": "cuda"}
    }
}
```

### 批量处理
```python
# 批量添加文档
results = rag.add_documents(file_paths, batch_size=20)
```

## 🤝 扩展开发

### 自定义Agent工具
```python
from langchain_core.tools import Tool

def create_custom_tool():
    def custom_function(input_text: str) -> str:
        return f"自定义处理: {input_text}"
    
    return Tool(
        name="custom_tool",
        description="自定义工具描述",
        func=custom_function
    )

agent.add_tool(create_custom_tool())
```

### 自定义RAG组件
```python
from rag_toolkit.parser import BaseParser

class CustomParser(BaseParser):
    def _get_supported_extensions(self):
        return ["custom"]
    
    def _parse_file_content(self, file_path):
        return "自定义解析结果"
```

## 🐛 故障排除

### 常见问题

1. **API密钥配置**
   - 确保设置了正确的环境变量
   - 检查API密钥格式和权限

2. **依赖安装**
   - 使用虚拟环境避免冲突
   - 确保Python版本兼容

3. **模型下载**
   - 配置镜像源加速下载
   - 检查网络连接和防火墙

4. **内存不足**
   - 调整批处理大小
   - 使用更小的模型

### 技术支持

- 📝 [提交Issue](https://github.com/Wang-Theo/rj-ai-toolkit/issues)
- 💬 [讨论区](https://github.com/Wang-Theo/rj-ai-toolkit/discussions)
- 📧 联系作者：renjiewang31@gmail.com

## 📜 更新日志

### v0.1.0 (2025-01-21)
- ✨ 初始版本发布
- 🤖 Agent Toolkit核心功能
- 📚 RAG Toolkit基础功能
- 📝 完整文档和示例

## 🛣️ 开发路线图

### 短期计划
- [ ] 🌐 **网络工具**: HTTP请求、API调用工具
- [ ] 📊 **数据分析**: Excel处理、图表生成工具
- [ ] 🗄️ **数据库工具**: SQL查询、数据操作工具

### 中期计划
- [ ] 🎨 **多媒体**: 图片处理、音频分析工具
- [ ] 🔗 **集成服务**: 第三方API集成
- [ ] 📱 **Web界面**: 基于Streamlit的可视化界面

### 长期计划
- [ ] 🤖 **更多AI模型**: 支持更多开源和商业模型
- [ ] 🏢 **企业版**: 增强安全性和企业级功能
- [ ] ☁️ **云服务**: 提供云端部署方案

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目的支持：
- [LangChain](https://github.com/langchain-ai/langchain)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)
- [BGE Models](https://github.com/FlagOpen/FlagEmbedding)

---

**RJ AI Toolkit** - 让AI开发更简单 🚀

*Made with ❤️ by Renjie Wang*
