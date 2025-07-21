"""
文本分析工具模块

提供各种文本分析功能，支持中英文混合文本。
"""

import re
from typing import Dict, List, Tuple
from langchain_core.tools import Tool
from collections import Counter


class TextAnalyzer:
    """文本分析器类"""
    
    @staticmethod
    def analyze_basic_stats(text: str) -> Dict[str, int]:
        """
        分析文本基础统计信息
        
        Args:
            text: 要分析的文本
            
        Returns:
            包含统计信息的字典
        """
        if not text or not text.strip():
            return {}
        
        # 基础统计
        total_chars = len(text)
        chars_no_spaces = len(text.replace(' ', ''))
        lines = text.split('\n')
        line_count = len(lines)
        
        # 词汇分析
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        english_words = re.findall(r'[a-zA-Z]+', text)
        numbers = re.findall(r'\d+', text)
        
        # 句子统计
        sentence_endings = ['。', '！', '？', '.', '!', '?']
        sentence_count = sum(text.count(ending) for ending in sentence_endings)
        
        # 段落统计（连续非空行为一段）
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        return {
            'total_chars': total_chars,
            'chars_no_spaces': chars_no_spaces,
            'line_count': line_count,
            'chinese_char_count': len(chinese_chars),
            'english_word_count': len(english_words),
            'number_count': len(numbers),
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
        }
    
    @staticmethod
    def analyze_word_frequency(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        分析词频
        
        Args:
            text: 要分析的文本
            top_n: 返回前N个高频词
            
        Returns:
            词频列表
        """
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        # 提取中文字符（简单按字符分词）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        # 合并所有词汇
        all_words = english_words + chinese_chars
        
        # 统计词频
        word_freq = Counter(all_words)
        return word_freq.most_common(top_n)
    
    @staticmethod
    def detect_language(text: str) -> Dict[str, float]:
        """
        检测文本语言比例
        
        Args:
            text: 要分析的文本
            
        Returns:
            语言比例字典
        """
        if not text:
            return {}
        
        total_chars = len(re.sub(r'\s', '', text))  # 不计空格
        if total_chars == 0:
            return {}
        
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        numbers = len(re.findall(r'\d', text))
        punctuation = len(re.findall(r'[^\w\s\u4e00-\u9fff]', text))
        
        return {
            'chinese_ratio': chinese_chars / total_chars,
            'english_ratio': english_chars / total_chars,
            'number_ratio': numbers / total_chars,
            'punctuation_ratio': punctuation / total_chars
        }


def create_text_analyzer_tool() -> Tool:
    """
    创建文本分析工具
    
    Returns:
        LangChain Tool对象
    """
    def analyze_text(text: str) -> str:
        """
        分析文本的统计信息，支持中英文混合文本
        
        Args:
            text: 要分析的文本
            
        Returns:
            格式化的分析结果
        """
        if not text or not text.strip():
            return "错误：请提供有效的文本内容"
        
        try:
            # 基础统计
            stats = TextAnalyzer.analyze_basic_stats(text)
            
            # 词频分析
            word_freq = TextAnalyzer.analyze_word_frequency(text, 5)
            
            # 语言检测
            lang_ratios = TextAnalyzer.detect_language(text)
            
            # 计算平均值
            total_words = stats['chinese_char_count'] + stats['english_word_count']
            avg_word_length = stats['chars_no_spaces'] / total_words if total_words > 0 else 0
            
            # 格式化输出
            result = f"""📊 文本分析结果:

🔢 基础统计:
- 总字符数: {stats['total_chars']}
- 字符数(不含空格): {stats['chars_no_spaces']}
- 行数: {stats['line_count']}
- 段落数: {stats['paragraph_count']}
- 句子数: {stats['sentence_count']}

📝 词汇统计:
- 中文字符: {stats['chinese_char_count']} 个
- 英文单词: {stats['english_word_count']} 个
- 数字: {stats['number_count']} 个
- 总词汇单元: {total_words} 个
- 平均词汇长度: {avg_word_length:.2f}

🌐 语言构成:
- 中文比例: {lang_ratios.get('chinese_ratio', 0):.1%}
- 英文比例: {lang_ratios.get('english_ratio', 0):.1%}
- 数字比例: {lang_ratios.get('number_ratio', 0):.1%}
- 标点比例: {lang_ratios.get('punctuation_ratio', 0):.1%}"""

            # 添加高频词
            if word_freq:
                result += "\n\n🔥 高频词汇 (前5位):\n"
                for i, (word, count) in enumerate(word_freq, 1):
                    result += f"- {i}. '{word}': {count}次\n"
            
            return result
            
        except Exception as e:
            return f"分析错误: {str(e)}"
    
    return Tool(
        name="text_analyzer",
        description="分析文本的详细统计信息，支持中英文混合文本。包括字符数、词汇数、句子数、语言比例、高频词等。输入要分析的文本内容。",
        func=analyze_text,
        args_schema=None
    )


def create_text_sentiment_tool() -> Tool:
    """
    创建文本情感分析工具（简单版本）
    
    Returns:
        LangChain Tool对象
    """
    def analyze_sentiment(text: str) -> str:
        """
        简单的情感分析
        
        Args:
            text: 要分析的文本
            
        Returns:
            情感分析结果
        """
        if not text or not text.strip():
            return "错误：请提供有效的文本内容"
        
        # 简单的情感词典（实际使用中可以使用更专业的情感分析库）
        positive_words = [
            '好', '棒', '优秀', '喜欢', '爱', '美', '赞', '完美', '满意', '开心',
            'good', 'great', 'excellent', 'love', 'like', 'amazing', 'perfect', 'happy'
        ]
        
        negative_words = [
            '坏', '差', '糟糕', '讨厌', '恨', '难看', '失望', '愤怒', '悲伤', '烦恼',
            'bad', 'terrible', 'awful', 'hate', 'ugly', 'disappointed', 'angry', 'sad'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # 简单的情感判断
        if positive_count > negative_count:
            sentiment = "积极 😊"
            confidence = positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            sentiment = "消极 😔"
            confidence = negative_count / (positive_count + negative_count + 1)
        else:
            sentiment = "中性 😐"
            confidence = 0.5
        
        return f"""🎭 情感分析结果:

📊 统计:
- 积极词汇: {positive_count} 个
- 消极词汇: {negative_count} 个

💭 整体情感: {sentiment}
📈 置信度: {confidence:.1%}

注：这是基于简单词典的情感分析，结果仅供参考。"""
    
    return Tool(
        name="sentiment_analyzer",
        description="分析文本的情感倾向，支持中英文。返回积极、消极或中性的情感判断及置信度。",
        func=analyze_sentiment,
        args_schema=None
    )
