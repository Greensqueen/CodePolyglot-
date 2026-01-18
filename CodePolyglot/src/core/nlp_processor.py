"""
NLP处理模块 - 分析代码注释质量
"""

import re
from typing import Dict, List, Tuple, Any  # 这是你需要添加的关键行
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string

# 下载NLTK数据（首次运行时需要）
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)


class NLPProcessor:
    """NLP处理器"""

    def __init__(self):
        # 定义技术术语
        self.technical_terms = {
            'en': {
                'function', 'class', 'method', 'variable', 'parameter', 'return',
                'algorithm', 'complexity', 'optimization', 'recursion', 'iteration',
                'database', 'api', 'framework', 'library', 'synchronization'
            },
            'zh': {
                '函数', '类', '方法', '变量', '参数', '返回', '算法', '复杂度',
                '优化', '递归', '迭代', '数据库', '接口', '框架', '库', '同步'
            }
        }

        # 质量指标的关键词
        self.quality_keywords = {
            'en': {
                'good': ['explains', 'describes', 'clear', 'concise', 'helpful', 'complete'],
                'bad': ['todo', 'fixme', 'hack', 'temp', 'temporary', 'workaround']
            },
            'zh': {
                'good': ['解释', '描述', '清晰', '简洁', '有用', '完整'],
                'bad': ['待办', '修复', '临时', '绕过', '补丁']
            }
        }

    def analyze_comments(self, comments: List[str], language: str = 'en') -> Dict[str, Any]:
        """分析注释质量"""
        if not comments:
            return {
                'comment_count': 0,
                'average_length': 0,
                'comment_quality_score': 0,
                'issues': [],
                'suggestions': []
            }

        # 合并所有注释
        all_comments = ' '.join(comments)

        # 基本统计
        word_count = len(word_tokenize(all_comments))
        sentence_count = len(sent_tokenize(all_comments))

        # 计算质量分数
        quality_score = self._calculate_quality_score(comments, language)

        # 检测问题
        issues = self._detect_comment_issues(comments, language)

        # 生成建议
        suggestions = self._generate_suggestions(comments, language, quality_score)

        return {
            'comment_count': len(comments),
            'total_words': word_count,
            'total_sentences': sentence_count,
            'average_length': word_count / len(comments) if comments else 0,
            'comment_quality_score': quality_score,
            'issues': issues,
            'suggestions': suggestions,
            'technical_terms_used': self._extract_technical_terms(all_comments, language)
        }

    def _calculate_quality_score(self, comments: List[str], language: str) -> float:
        """计算注释质量分数"""
        if not comments:
            return 0.0

        scores = []

        for comment in comments:
            comment_score = 1.0  # 基础分

            # 检查长度
            words = word_tokenize(comment)
            if 5 <= len(words) <= 50:  # 适中长度
                comment_score += 0.2
            elif len(words) > 50:  # 太长
                comment_score -= 0.1
            else:  # 太短
                comment_score -= 0.1

            # 检查句子结构
            sentences = sent_tokenize(comment)
            if len(sentences) > 0:
                # 检查是否以大写字母开头，以句号结尾
                if sentences[0][0].isupper() and any(sentences[-1].endswith(p) for p in ['.', '!', '?']):
                    comment_score += 0.2

            # 检查技术术语使用
            technical_terms = self._count_technical_terms(comment, language)
            if technical_terms > 0:
                comment_score += 0.1 * min(technical_terms, 3)  # 最多加0.3分

            # 检查质量问题关键词
            for keyword in self.quality_keywords[language]['good']:
                if keyword.lower() in comment.lower():
                    comment_score += 0.1

            for keyword in self.quality_keywords[language]['bad']:
                if keyword.lower() in comment.lower():
                    comment_score -= 0.2

            # 检查TODO/FIXME
            if any(marker in comment.upper() for marker in ['TODO', 'FIXME', 'HACK', 'XXX']):
                comment_score -= 0.3

            scores.append(max(0, min(1, comment_score)))  # 限制在0-1之间

        return sum(scores) / len(scores)

    def _detect_comment_issues(self, comments: List[str], language: str) -> List[Dict]:
        """检测注释问题"""
        issues = []

        for i, comment in enumerate(comments):
            words = word_tokenize(comment)

            # 检查注释是否太短
            if len(words) < 3:
                issues.append({
                    'type': 'too_short',
                    'comment_index': i,
                    'message': '注释太短，可能没有提供足够的信息',
                    'severity': 'low'
                })

            # 检查注释是否太长
            if len(words) > 100:
                issues.append({
                    'type': 'too_long',
                    'comment_index': i,
                    'message': '注释太长，考虑拆分为多个注释或添加文档字符串',
                    'severity': 'low'
                })

            # 检查是否有TODO/FIXME
            if 'TODO' in comment.upper() or 'FIXME' in comment.upper():
                issues.append({
                    'type': 'todo_fixme',
                    'comment_index': i,
                    'message': '包含TODO或FIXME标记',
                    'severity': 'medium'
                })

            # 检查是否有拼写错误（简单版本）
            if self._has_potential_spelling_errors(comment, language):
                issues.append({
                    'type': 'spelling',
                    'comment_index': i,
                    'message': '可能存在拼写错误',
                    'severity': 'low'
                })

        return issues

    def _generate_suggestions(self, comments: List[str], language: str, quality_score: float) -> List[Dict]:
        """生成改进建议"""
        suggestions = []

        if quality_score < 0.6:
            suggestions.append({
                'priority': 'high',
                'message': '注释质量有待提高',
                'action': '检查并改进注释的清晰度和完整性'
            })

        # 检查是否有足够的注释
        if len(comments) < 5:
            suggestions.append({
                'priority': 'medium',
                'message': '注释数量较少',
                'action': '为复杂逻辑和关键函数添加更多注释'
            })

        # 检查TODO/FIXME
        todo_count = sum(1 for comment in comments if 'TODO' in comment.upper() or 'FIXME' in comment.upper())
        if todo_count > 0:
            suggestions.append({
                'priority': 'medium',
                'message': f'发现{todo_count}个TODO/FIXME标记',
                'action': '处理或移除TODO/FIXME标记'
            })

        return suggestions

    def _count_technical_terms(self, text: str, language: str) -> int:
        """统计技术术语数量"""
        text_lower = text.lower()
        count = 0

        for term in self.technical_terms[language]:
            if term.lower() in text_lower:
                count += 1

        return count

    def _extract_technical_terms(self, text: str, language: str) -> List[str]:
        """提取使用的技术术语"""
        found_terms = []
        text_lower = text.lower()

        for term in self.technical_terms[language]:
            if term.lower() in text_lower:
                found_terms.append(term)

        return found_terms

    def _has_potential_spelling_errors(self, text: str, language: str) -> bool:
        """检查潜在拼写错误（简化版）"""
        # 这是一个简化的检查，实际项目中可以使用拼写检查库
        words = word_tokenize(text)

        # 检查连续大写字母（可能是缩写）
        consecutive_upper = 0

        for word in words:
            if len(word) > 1 and word.isalpha():
                # 检查单词中是否有多个大写字母（不是首字母大写）
                if sum(1 for c in word if c.isupper()) > 1 and not word.isupper():
                    return True

                # 检查奇怪的字符组合
                if 'xx' in word.lower() or 'aaa' in word.lower():
                    return True

        return False