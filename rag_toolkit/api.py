"""
RAG API

企业级RAG系统的统一API接口，整合所有RAG功能组件。
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from langchain.schema import Document
from .chunker import DocumentChunker, ChunkStrategy, ChunkConfig
from .parser import DocumentParser
from .db_manager import VectorDBManager, DocumentDBManager
from .retriever import VectorRetriever, HybridRetriever
from .ranker import DocumentRanker


class RAGApi:
    """
    RAG API 主类
    
    提供完整的RAG功能，包括文档解析、切块、存储、检索、重排序等。
    """
    
    def __init__(
        self,
        vector_db_config: Optional[Dict[str, Any]] = None,
        doc_db_config: Optional[Dict[str, Any]] = None,
        chunk_config: Optional[ChunkConfig] = None,
        **kwargs
    ):
        """
        初始化RAG API
        
        Args:
            vector_db_config: 向量数据库配置
            doc_db_config: 文档数据库配置  
            chunk_config: 切块配置
            **kwargs: 其他配置参数
        """
        # 初始化配置
        self.chunk_config = chunk_config or ChunkConfig()
        
        # 初始化组件
        self.parser = DocumentParser()
        self.chunker = DocumentChunker(config=self.chunk_config)
        
        # 数据库管理器
        self.vector_db = VectorDBManager(vector_db_config or {})
        self.doc_db = DocumentDBManager(doc_db_config or {})
        
        # 检索器
        self.retriever = VectorRetriever(self.vector_db)
        self.hybrid_retriever = HybridRetriever(self.vector_db)
        
        # 重排序器
        self.ranker = DocumentRanker()
        
        # 状态信息
        self.stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "last_updated": None
        }
    
    # ========== 文档处理 ==========
    
    def add_document(
        self, 
        file_path: Union[str, Path],
        chunk_strategy: Union[ChunkStrategy, str] = ChunkStrategy.RECURSIVE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        添加单个文档到RAG系统
        
        Args:
            file_path: 文件路径
            chunk_strategy: 切块策略
            metadata: 额外元数据
            
        Returns:
            处理结果
        """
        try:
            # 1. 解析文档
            document = self.parser.parse_file(file_path)
            
            # 2. 合并元数据
            if metadata:
                document.metadata.update(metadata)
            
            # 3. 文档切块
            chunks = self.chunker.chunk_document(document, strategy=chunk_strategy)
            
            # 4. 存储到文档数据库
            doc_id = self.doc_db.add_document(document)
            
            # 5. 存储块到向量数据库
            chunk_ids = self.vector_db.add_documents(chunks)
            
            # 6. 更新统计
            self.stats["documents_processed"] += 1
            self.stats["chunks_created"] += len(chunks)
            
            return {
                "success": True,
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "chunk_ids": chunk_ids
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_documents(
        self,
        file_paths: List[Union[str, Path]],
        chunk_strategy: Union[ChunkStrategy, str] = ChunkStrategy.RECURSIVE,
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        批量添加文档
        
        Args:
            file_paths: 文件路径列表
            chunk_strategy: 切块策略
            batch_size: 批处理大小
            
        Returns:
            处理结果列表
        """
        results = []
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            for file_path in batch:
                result = self.add_document(file_path, chunk_strategy)
                results.append(result)
        
        return results
    
    def add_directory(
        self,
        directory_path: Union[str, Path],
        chunk_strategy: Union[ChunkStrategy, str] = ChunkStrategy.RECURSIVE,
        recursive: bool = True,
        file_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加目录中的所有文档
        
        Args:
            directory_path: 目录路径
            chunk_strategy: 切块策略
            recursive: 是否递归搜索
            file_pattern: 文件模式匹配
            
        Returns:
            处理结果摘要
        """
        try:
            # 解析目录中的所有文档
            documents = self.parser.parse_directory(
                directory_path, 
                recursive=recursive,
                file_pattern=file_pattern
            )
            
            total_docs = len(documents)
            successful = 0
            total_chunks = 0
            
            for document in documents:
                try:
                    # 切块
                    chunks = self.chunker.chunk_document(document, strategy=chunk_strategy)
                    
                    # 存储
                    self.doc_db.add_document(document)
                    self.vector_db.add_documents(chunks)
                    
                    successful += 1
                    total_chunks += len(chunks)
                    
                except Exception as e:
                    print(f"处理文档失败 {document.metadata.get('file_name', 'unknown')}: {e}")
                    continue
            
            # 更新统计
            self.stats["documents_processed"] += successful
            self.stats["chunks_created"] += total_chunks
            
            return {
                "success": True,
                "total_documents": total_docs,
                "successful_documents": successful,
                "total_chunks": total_chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== 检索功能 ==========
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        retrieval_method: str = "vector",  # vector, hybrid
        rerank: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            retrieval_method: 检索方法
            rerank: 是否重排序
            filters: 过滤条件
            
        Returns:
            搜索结果列表
        """
        try:
            # 选择检索器
            if retrieval_method == "hybrid":
                retriever = self.hybrid_retriever
            else:
                retriever = self.retriever
            
            # 执行检索
            results = retriever.retrieve(query, top_k * 2, filters)  # 取更多结果用于重排序
            
            # 重排序
            if rerank and results:
                results = self.ranker.rerank(query, results, top_k)
            else:
                results = results[:top_k]
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.page_content,
                    "metadata": result.metadata,
                    "score": result.metadata.get("score", 0.0)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值
            
        Returns:
            搜索结果
        """
        results = self.search(query, top_k, "vector", rerank=True)
        
        # 过滤低相似度结果
        filtered_results = [
            r for r in results 
            if r.get("score", 0) >= similarity_threshold
        ]
        
        return filtered_results
    
    # ========== 管理功能 ==========
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档及其所有块
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            # 删除文档数据库中的文档
            self.doc_db.delete_document(doc_id)
            
            # 删除向量数据库中的相关块
            self.vector_db.delete_by_metadata({"source_doc_id": doc_id})
            
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        清空所有数据
        
        Returns:
            是否成功
        """
        try:
            self.doc_db.clear()
            self.vector_db.clear()
            
            # 重置统计
            self.stats = {
                "documents_processed": 0,
                "chunks_created": 0,
                "last_updated": None
            }
            
            return True
        except Exception as e:
            print(f"清空数据失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Returns:
            统计信息
        """
        return {
            **self.stats,
            "vector_db_stats": self.vector_db.get_stats(),
            "doc_db_stats": self.doc_db.get_stats(),
            "chunker_stats": self.chunker.get_stats()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        系统健康检查
        
        Returns:
            健康状态
        """
        health = {
            "status": "healthy",
            "components": {}
        }
        
        try:
            # 检查向量数据库
            health["components"]["vector_db"] = self.vector_db.health_check()
            
            # 检查文档数据库  
            health["components"]["doc_db"] = self.doc_db.health_check()
            
            # 检查组件状态
            failed_components = [
                name for name, status in health["components"].items() 
                if not status.get("healthy", False)
            ]
            
            if failed_components:
                health["status"] = "degraded"
                health["failed_components"] = failed_components
                
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        return health
