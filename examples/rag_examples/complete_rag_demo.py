"""
RAG Toolkit 完整示例

演示如何使用RAG toolkit进行文档处理、检索和问答。
"""

import os
from pathlib import Path
from rag_toolkit import RAGApi
from rag_toolkit.chunker import ChunkConfig, ChunkStrategy
from rag_toolkit.parser import ParseConfig


def main():
    """主函数 - RAG系统完整演示"""
    print("🚀 RAG Toolkit 完整演示")
    print("=" * 60)
    
    # 1. 初始化RAG系统
    print("1. 初始化RAG系统...")
    
    # 配置
    chunk_config = ChunkConfig(
        chunk_size=500,
        chunk_overlap=50,
        add_start_index=True
    )
    
    parse_config = ParseConfig(
        extract_metadata=True,
        preserve_structure=True,
        extract_tables=True
    )
    
    vector_db_config = {
        "persist_directory": "./rag_demo/chroma_db",
        "collection_name": "demo_collection",
        "embeddings": {
            "model_name": "BAAI/bge-small-zh-v1.5",
            "model_kwargs": {"device": "cpu"}
        }
    }
    
    doc_db_config = {
        "db_path": "./rag_demo/documents.db"
    }
    
    # 初始化RAG API
    rag = RAGApi(
        vector_db_config=vector_db_config,
        doc_db_config=doc_db_config,
        chunk_config=chunk_config
    )
    
    print("✅ RAG系统初始化完成")
    
    # 2. 创建示例文档
    print("\n2. 创建示例文档...")
    demo_dir = Path("./rag_demo/documents")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建示例文本文件
    sample_docs = {
        "人工智能概述.txt": """
人工智能（Artificial Intelligence，AI）是计算机科学的一个重要分支。
它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。

AI的主要应用领域包括：
1. 机器学习和深度学习
2. 自然语言处理
3. 计算机视觉
4. 语音识别和合成
5. 专家系统

当前，人工智能技术正在快速发展，在医疗、金融、教育、交通等多个领域都有重要应用。
""",
        
        "机器学习基础.txt": """
机器学习是人工智能的一个子领域，它使计算机系统能够自动学习和改进，而无需明确的编程。

主要的机器学习类型：
1. 监督学习：使用标记数据训练模型
2. 无监督学习：从无标记数据中发现模式
3. 强化学习：通过与环境交互学习最优策略

常用的机器学习算法包括：
- 线性回归和逻辑回归
- 决策树和随机森林
- 支持向量机（SVM）
- 神经网络和深度学习
- K-means聚类算法

机器学习在推荐系统、图像识别、语音处理等领域有广泛应用。
""",
        
        "深度学习技术.txt": """
深度学习是机器学习的一个重要分支，基于人工神经网络进行学习。

深度学习的核心概念：
1. 神经网络：模拟人脑神经元的数学模型
2. 反向传播：训练神经网络的关键算法
3. 卷积神经网络（CNN）：在图像处理中表现优异
4. 循环神经网络（RNN）：适合处理序列数据
5. 变压器（Transformer）：在NLP领域取得突破

深度学习的优势：
- 自动特征提取
- 处理高维数据的能力强
- 在大数据上性能优异

深度学习推动了计算机视觉、自然语言处理、语音识别等领域的重大突破。
"""
    }
    
    # 写入示例文档
    for filename, content in sample_docs.items():
        file_path = demo_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ 创建了 {len(sample_docs)} 个示例文档")
    
    # 3. 批量添加文档
    print("\n3. 批量添加文档到RAG系统...")
    
    result = rag.add_directory(
        directory_path=demo_dir,
        chunk_strategy=ChunkStrategy.RECURSIVE,
        recursive=False
    )
    
    if result["success"]:
        print(f"✅ 成功处理 {result['successful_documents']} 个文档")
        print(f"   总共创建 {result['total_chunks']} 个文档块")
    else:
        print(f"❌ 处理文档失败: {result['error']}")
        return
    
    # 4. 搜索演示
    print("\n4. 搜索演示...")
    
    queries = [
        "什么是人工智能？",
        "机器学习的主要类型有哪些？",
        "深度学习与传统机器学习的区别",
        "CNN和RNN的应用场景",
        "人工智能在哪些领域有应用？"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 查询 {i}: {query}")
        print("-" * 40)
        
        # 向量搜索
        results = rag.search(
            query=query,
            top_k=3,
            retrieval_method="vector",
            rerank=True
        )
        
        if results:
            print("📄 搜索结果:")
            for j, result in enumerate(results, 1):
                content = result["content"][:150] + "..." if len(result["content"]) > 150 else result["content"]
                score = result["score"]
                source = result["metadata"].get("file_name", "未知来源")
                
                print(f"   {j}. [{source}] (相关度: {score:.3f})")
                print(f"      {content}")
                print()
        else:
            print("   ❌ 未找到相关结果")
    
    # 5. 混合检索演示
    print("\n5. 混合检索演示...")
    
    test_query = "深度学习的应用"
    print(f"🔍 查询: {test_query}")
    
    # 对比不同检索方法
    vector_results = rag.search(test_query, top_k=3, retrieval_method="vector")
    hybrid_results = rag.search(test_query, top_k=3, retrieval_method="hybrid")
    
    print("📊 检索方法对比:")
    print(f"向量检索结果数: {len(vector_results)}")
    print(f"混合检索结果数: {len(hybrid_results)}")
    
    # 6. 语义搜索演示
    print("\n6. 语义搜索演示...")
    
    semantic_results = rag.semantic_search(
        query="AI技术的发展趋势",
        top_k=3,
        similarity_threshold=0.5
    )
    
    print(f"🧠 语义搜索结果数: {len(semantic_results)}")
    if semantic_results:
        for i, result in enumerate(semantic_results, 1):
            source = result["metadata"].get("file_name", "未知")
            score = result["score"]
            print(f"   {i}. {source} (相似度: {score:.3f})")
    
    # 7. 系统统计信息
    print("\n7. 系统统计信息...")
    
    stats = rag.get_statistics()
    print("📈 RAG系统统计:")
    print(f"   处理文档数: {stats['documents_processed']}")
    print(f"   创建块数: {stats['chunks_created']}")
    print(f"   向量数据库: {stats['vector_db_stats']}")
    print(f"   文档数据库: {stats['doc_db_stats']}")
    
    # 8. 健康检查
    print("\n8. 系统健康检查...")
    
    health = rag.health_check()
    print(f"🏥 系统状态: {health['status']}")
    if health['status'] != 'healthy':
        print(f"   问题组件: {health.get('failed_components', [])}")
    
    print("\n🎉 RAG Toolkit 演示完成！")
    print("\n💡 使用提示:")
    print("   - 可以继续添加更多文档到系统中")
    print("   - 尝试不同的切块策略和检索方法")
    print("   - 调整相似度阈值来优化搜索效果")
    print("   - 使用混合检索来提高准确率")


def advanced_demo():
    """高级功能演示"""
    print("\n🔬 高级功能演示")
    print("=" * 60)
    
    # 演示不同切块策略
    from rag_toolkit.chunker import DocumentChunker, ChunkStrategy, ChunkConfig
    
    chunk_config = ChunkConfig(chunk_size=300, chunk_overlap=30)
    chunker = DocumentChunker(config=chunk_config)
    
    sample_text = """
    人工智能技术正在快速发展。机器学习是AI的重要分支。
    深度学习通过神经网络模拟人脑工作方式。CNN适合图像处理。
    RNN适合序列数据处理。Transformer在NLP领域表现优异。
    AI应用于医疗、金融、教育等多个领域。
    """
    
    print("📊 切块策略对比:")
    
    # 对比不同策略
    comparison = chunker.compare_strategies(sample_text)
    
    for strategy, result in comparison.items():
        if "error" not in result:
            print(f"   {strategy}: {result['chunk_count']} 块, 平均大小: {result['avg_chunk_size']:.1f}")
        else:
            print(f"   {strategy}: 错误 - {result['error']}")


if __name__ == "__main__":
    try:
        main()
        advanced_demo()
    except KeyboardInterrupt:
        print("\n👋 演示已中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("请检查依赖是否正确安装：")
        print("pip install -r requirements.txt")
