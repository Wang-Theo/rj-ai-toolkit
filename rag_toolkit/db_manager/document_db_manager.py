"""
文档数据库管理器

管理原始文档的存储，支持SQLite的策略管理器。
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from langchain.schema import Document
from .vector_db_manager import VectorDBManager


class DocumentDBManager:
    """
    文档数据库策略管理器
    
    不是数据库管理器本身，而是管理和选择不同数据库管理器的门面类。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文档数据库策略管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.db_path = config.get("db_path", "./documents.db")
        self.conn = None
        
        # 初始化向量数据库管理器（用于混合功能）
        self.vector_manager = None
        if config.get("enable_vector_db", False):
            self.vector_manager = VectorDBManager(config.get("vector_config", {}))
    
    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
            self._init_database()
            self.is_connected = True
            
            # 连接向量数据库（如果启用）
            if self.vector_manager:
                self.vector_manager.connect()
                
            return True
        except Exception as e:
            print(f"连接文档数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.vector_manager:
            self.vector_manager.disconnect()
        self.is_connected = False
    
    def is_healthy(self) -> bool:
        """检查数据库健康状态"""
        try:
            if self.conn:
                self.conn.execute("SELECT 1")
                return True
            return False
        except Exception:
            return False
    
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建集合/表"""
        try:
            if not self.conn:
                self.connect()
            
            # 为每个集合创建一个表
            create_sql = f"""
                CREATE TABLE IF NOT EXISTS {collection_name} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            self.conn.execute(create_sql)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"创建集合失败 {collection_name}: {str(e)}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合/表"""
        try:
            if not self.conn:
                self.connect()
            
            self.conn.execute(f"DROP TABLE IF EXISTS {collection_name}")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除集合失败 {collection_name}: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """列出所有集合/表"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"列出集合失败: {str(e)}")
            return []
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[Dict[str, Any]],
                     **kwargs) -> List[str]:
        """添加文档"""
        try:
            if not self.conn:
                self.connect()
            
            # 确保表存在
            self.create_collection(collection_name)
            
            document_ids = []
            for doc in documents:
                doc_id = doc.get('id', f"doc_{len(document_ids)}")
                content = doc.get('content', '')
                metadata = json.dumps(doc.get('metadata', {}), ensure_ascii=False)
                
                self.conn.execute(f"""
                    INSERT OR REPLACE INTO {collection_name} (id, content, metadata, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (doc_id, content, metadata, datetime.now().isoformat()))
                
                document_ids.append(doc_id)
            
            self.conn.commit()
            return document_ids
        except Exception as e:
            print(f"添加文档失败: {str(e)}")
            return []
    
    def update_documents(self, 
                        collection_name: str,
                        documents: List[Dict[str, Any]],
                        **kwargs) -> bool:
        """更新文档"""
        try:
            if not self.conn:
                self.connect()
            
            for doc in documents:
                if 'id' not in doc:
                    continue
                
                doc_id = doc['id']
                content = doc.get('content', '')
                metadata = json.dumps(doc.get('metadata', {}), ensure_ascii=False)
                
                self.conn.execute(f"""
                    UPDATE {collection_name} 
                    SET content = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (content, metadata, datetime.now().isoformat(), doc_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新文档失败: {str(e)}")
            return False
    
    def delete_documents(self, 
                        collection_name: str,
                        document_ids: List[str],
                        **kwargs) -> bool:
        """删除文档"""
        try:
            if not self.conn:
                self.connect()
            
            placeholders = ','.join(['?'] * len(document_ids))
            self.conn.execute(f"DELETE FROM {collection_name} WHERE id IN ({placeholders})", document_ids)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除文档失败: {str(e)}")
            return False
    
    def search(self, 
              collection_name: str,
              query: Union[str, List[float]],
              top_k: int = 10,
              **kwargs) -> List[Dict[str, Any]]:
        """搜索文档（简单的文本搜索）"""
        try:
            if not self.conn:
                self.connect()
            
            if isinstance(query, list):
                raise ValueError("DocumentDBManager不支持向量查询")
            
            # 简单的LIKE搜索
            cursor = self.conn.execute(f"""
                SELECT id, content, metadata FROM {collection_name}
                WHERE content LIKE ? 
                LIMIT ?
            """, (f'%{query}%', top_k))
            
            results = []
            for row in cursor.fetchall():
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                result = {
                    'id': row['id'],
                    'content': row['content'],
                    'metadata': metadata,
                    'score': 1.0  # 简单搜索，固定分数
                }
                results.append(result)
            
            return results
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return []
    
    def count(self, collection_name: str, **kwargs) -> int:
        """统计文档数量"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {collection_name}")
            return cursor.fetchone()[0]
        except Exception:
            return 0
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_document(self, document: Document) -> str:
        """添加文档"""
        doc_id = document.metadata.get("doc_id", "")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO documents (doc_id, content, metadata, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                doc_id,
                document.page_content,
                json.dumps(document.metadata, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            conn.commit()
        
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, metadata FROM documents WHERE doc_id = ?
            """, (doc_id,))
            row = cursor.fetchone()
            
            if row:
                content, metadata_json = row
                metadata = json.loads(metadata_json)
                return Document(page_content=content, metadata=metadata)
        
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
                conn.commit()
            return True
        except:
            return False
    
    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出文档"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT doc_id, metadata, created_at, updated_at 
                FROM documents 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                doc_id, metadata_json, created_at, updated_at = row
                metadata = json.loads(metadata_json)
                results.append({
                    "doc_id": doc_id,
                    "metadata": metadata,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            return results
    
    def clear(self) -> bool:
        """清空数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM documents")
                conn.commit()
            return True
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            
            return {
                "document_count": count,
                "db_path": self.db_path
            }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
