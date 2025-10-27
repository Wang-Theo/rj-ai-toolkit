"""
BM25检索器

基于BM25算法的文本检索器，适用于传统的关键词匹配检索。
"""

import json
import pickle
from typing import Dict, Any, List, Optional
from .base_retriever import BaseRetriever

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class BM25Retriever(BaseRetriever):
    """BM25检索器
    
    使用BM25算法进行文档检索，适合传统的关键词匹配场景。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化BM25检索器
        
        Args:
            config: 配置参数，支持以下选项：
                - tokenizer: 分词器 (默认使用简单空格分词)
                - k1: BM25参数k1 (默认: 1.2)
                - b: BM25参数b (默认: 0.75)
                - epsilon: BM25参数epsilon (默认: 0.25)
                - language: 语言设置 (zh/en，默认: zh)
        """
        if not BM25_AVAILABLE:
            raise ImportError(
                "rank-bm25 is required for BM25Retriever. "
                "Install it with: pip install rank-bm25"
            )
        
        super().__init__(config)
        
        # BM25参数
        self.k1 = self.config.get('k1', 1.2)
        self.b = self.config.get('b', 0.75)
        self.epsilon = self.config.get('epsilon', 0.25)
        self.language = self.config.get('language', 'zh')
        
        # 文档存储
        self.documents = []
        self.document_ids = []
        self.document_metadata = []
        
        # BM25模型
        self.bm25_model = None
        self.tokenized_docs = []
        
        # 分词器
        self.tokenizer = self._get_tokenizer()
    
    def _get_tokenizer(self):
        """获取分词器"""
        tokenizer_name = self.config.get('tokenizer', 'jieba')
        
        if tokenizer_name == 'jieba' and self.language == 'zh':
            try:
                import jieba
                return lambda text: list(jieba.cut(text))
            except ImportError:
                print("jieba not available, using simple tokenizer")
                return self._simple_tokenizer
        else:
            return self._simple_tokenizer
    
    def _simple_tokenizer(self, text: str) -> List[str]:
        """简单分词器"""
        # 移除标点符号并转换为小写
        import re
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return text.split()
    
    def initialize(self) -> bool:
        """初始化BM25检索器
        
        Returns:
            初始化是否成功
        """
        try:
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"初始化BM25检索器失败: {str(e)}")
            self.is_initialized = False
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]], **kwargs) -> List[str]:
        """添加文档到BM25检索器
        
        Args:
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            文档ID列表
        """
        if not self.validate_documents(documents):
            return []
        
        try:
            import uuid
            
            document_ids = []
            
            for doc in documents:
                # 生成文档ID
                doc_id = doc.get('id', str(uuid.uuid4()))
                document_ids.append(doc_id)
                
                # 存储文档信息
                self.documents.append(doc['content'])
                self.document_ids.append(doc_id)
                self.document_metadata.append(doc.get('metadata', {}))
                
                # 分词
                tokens = self.tokenizer(doc['content'])
                self.tokenized_docs.append(tokens)
            
            # 重建BM25模型
            self._rebuild_bm25_model()
            
            return document_ids
            
        except Exception as e:
            print(f"添加文档失败: {str(e)}")
            return []
    
    def _rebuild_bm25_model(self):
        """重建BM25模型"""
        if self.tokenized_docs:
            self.bm25_model = BM25Okapi(
                self.tokenized_docs,
                k1=self.k1,
                b=self.b,
                epsilon=self.epsilon
            )
    
    def retrieve(self, 
                query: str,
                top_k: int = 10,
                **kwargs) -> List[Dict[str, Any]]:
        """使用BM25检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
                - min_score: 最小分数阈值
                
        Returns:
            检索结果列表
        """
        if not self.bm25_model or not self.documents:
            return []
        
        try:
            # 预处理查询
            processed_query = self.preprocess_query(query)
            
            # 分词
            query_tokens = self.tokenizer(processed_query)
            
            # BM25检索
            scores = self.bm25_model.get_scores(query_tokens)
            
            # 获取top_k结果
            import numpy as np
            
            # 获取分数排序的索引
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # 构建结果
            results = []
            min_score = kwargs.get('min_score', 0.0)
            
            for idx in top_indices:
                score = scores[idx]
                
                # 应用最小分数阈值
                if score < min_score:
                    continue
                
                result = {
                    'id': self.document_ids[idx],
                    'content': self.documents[idx],
                    'score': float(score),
                    'metadata': self.document_metadata[idx].copy()
                }
                results.append(result)
            
            return self.postprocess_results(results)
            
        except Exception as e:
            print(f"BM25检索失败: {str(e)}")
            return []
    
    def update_documents(self, documents: List[Dict[str, Any]], **kwargs) -> bool:
        """更新文档
        
        Args:
            documents: 文档列表
            **kwargs: 其他参数
            
        Returns:
            更新是否成功
        """
        try:
            # 删除旧文档并添加新文档
            document_ids = [doc.get('id') for doc in documents if doc.get('id')]
            
            if document_ids:
                self.delete_documents(document_ids)
            
            self.add_documents(documents, **kwargs)
            return True
            
        except Exception as e:
            print(f"更新文档失败: {str(e)}")
            return False
    
    def delete_documents(self, document_ids: List[str], **kwargs) -> bool:
        """删除文档
        
        Args:
            document_ids: 文档ID列表
            **kwargs: 其他参数
            
        Returns:
            删除是否成功
        """
        try:
            # 找到要删除的文档索引
            indices_to_remove = []
            
            for i, doc_id in enumerate(self.document_ids):
                if doc_id in document_ids:
                    indices_to_remove.append(i)
            
            # 逆序删除以避免索引问题
            for idx in sorted(indices_to_remove, reverse=True):
                del self.documents[idx]
                del self.document_ids[idx]
                del self.document_metadata[idx]
                del self.tokenized_docs[idx]
            
            # 重建BM25模型
            self._rebuild_bm25_model()
            
            return True
            
        except Exception as e:
            print(f"删除文档失败: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """清空所有文档
        
        Returns:
            清空是否成功
        """
        try:
            self.documents.clear()
            self.document_ids.clear()
            self.document_metadata.clear()
            self.tokenized_docs.clear()
            self.bm25_model = None
            return True
            
        except Exception as e:
            print(f"清空文档失败: {str(e)}")
            return False
    
    def count(self) -> int:
        """获取文档数量
        
        Returns:
            文档数量
        """
        return len(self.documents)
    
    def save_index(self, file_path: str) -> bool:
        """保存BM25索引到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            保存是否成功
        """
        try:
            index_data = {
                'documents': self.documents,
                'document_ids': self.document_ids,
                'document_metadata': self.document_metadata,
                'tokenized_docs': self.tokenized_docs,
                'config': self.config
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(index_data, f)
            
            return True
            
        except Exception as e:
            print(f"保存索引失败: {str(e)}")
            return False
    
    def load_index(self, file_path: str) -> bool:
        """从文件加载BM25索引
        
        Args:
            file_path: 索引文件路径
            
        Returns:
            加载是否成功
        """
        try:
            with open(file_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.documents = index_data['documents']
            self.document_ids = index_data['document_ids']
            self.document_metadata = index_data['document_metadata']
            self.tokenized_docs = index_data['tokenized_docs']
            self.config.update(index_data.get('config', {}))
            
            # 重建BM25模型
            self._rebuild_bm25_model()
            
            return True
            
        except Exception as e:
            print(f"加载索引失败: {str(e)}")
            return False
    
    def get_term_frequencies(self, doc_id: str) -> Dict[str, int]:
        """获取文档的词频统计
        
        Args:
            doc_id: 文档ID
            
        Returns:
            词频字典
        """
        try:
            doc_index = self.document_ids.index(doc_id)
            tokens = self.tokenized_docs[doc_index]
            
            from collections import Counter
            return dict(Counter(tokens))
            
        except ValueError:
            return {}
        except Exception as e:
            print(f"获取词频失败: {str(e)}")
            return {}
