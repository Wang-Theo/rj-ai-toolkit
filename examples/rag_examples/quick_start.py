"""
RAG Toolkit 快速开始示例

展示如何快速使用RAG功能。
"""

from rag_toolkit import RAGApi
from rag_toolkit.chunker import ChunkConfig, ChunkStrategy
import tempfile
import os


def quick_start_demo():
    """RAG快速开始演示"""
    print("🚀 RAG Toolkit 快速开始")
    print("=" * 40)
    
    # 1. 初始化RAG系统
    print("1. 初始化RAG系统...")
    
    rag = RAGApi(
        vector_db_config={
            "persist_directory": "./quick_demo/vector_db",
            "collection_name": "quick_demo"
        },
        doc_db_config={
            "db_path": "./quick_demo/docs.db"
        },
        chunk_config=ChunkConfig(
            chunk_size=300,
            chunk_overlap=50
        )
    )
    
    print("✅ RAG系统初始化完成")
    
    # 2. 创建临时文档
    print("\n2. 添加文档...")
    
    # 创建临时目录和文档
    with tempfile.TemporaryDirectory() as temp_dir:
        # 写入示例文档
        doc_content = """
        Python是一种高级编程语言，具有简洁的语法和强大的功能。
        Python广泛应用于Web开发、数据科学、人工智能、自动化等领域。
        
        Python的主要特点：
        1. 简单易学：语法简洁，接近自然语言
        2. 跨平台：可在Windows、Linux、macOS上运行
        3. 丰富的库：拥有庞大的第三方库生态系统
        4. 开源免费：完全开源，社区活跃
        
        在数据科学领域，Python有pandas、numpy、matplotlib等优秀库。
        在AI领域，有tensorflow、pytorch、sklearn等强大工具。
        """
        
        doc_path = os.path.join(temp_dir, "python_intro.txt")
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        # 添加文档到RAG系统
        result = rag.add_document(
            file_path=doc_path,
            chunk_strategy=ChunkStrategy.RECURSIVE,
            metadata={"topic": "programming", "language": "python"}
        )
        
        if result["success"]:
            print(f"✅ 文档添加成功，创建了 {result['chunk_count']} 个文档块")
        else:
            print(f"❌ 文档添加失败: {result['error']}")
            return
    
    # 3. 搜索测试
    print("\n3. 搜索测试...")
    
    test_queries = [
        "Python有什么特点？",
        "Python在哪些领域应用？",
        "数据科学相关的Python库",
        "Python是否开源？"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        
        results = rag.search(
            query=query,
            top_k=2,
            retrieval_method="vector",
            rerank=True
        )
        
        if results:
            for i, result in enumerate(results, 1):
                score = result["score"]
                content = result["content"][:100] + "..."
                print(f"   {i}. (相关度: {score:.3f}) {content}")
        else:
            print("   未找到相关结果")
    
    # 4. 系统信息
    print("\n4. 系统统计...")
    stats = rag.get_statistics()
    print(f"📊 处理文档: {stats['documents_processed']} 个")
    print(f"📊 文档块数: {stats['chunks_created']} 个")
    
    print("\n🎉 快速演示完成！")


if __name__ == "__main__":
    try:
        quick_start_demo()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保安装了RAG相关依赖：")
        print("pip install sentence-transformers chromadb")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
