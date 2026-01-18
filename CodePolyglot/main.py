"""
CodePolyglot - 多语言代码分析助手
Author: [你的名字]
Date: 2024
License: MIT
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('codepolyglot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CodePolyglot:
    """主分析类"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化分析器"""
        self.supported_languages = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'cpp': '.cpp',
            'go': '.go'
        }

        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化组件
        from src.core.analyzer import CodeAnalyzer
        from src.core.nlp_processor import NLPProcessor
        from src.visualization.plotter import Visualizer

        self.analyzer = CodeAnalyzer()
        self.nlp_processor = NLPProcessor()
        self.visualizer = Visualizer()

        logger.info("CodePolyglot 初始化完成")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            'max_file_size': 1024 * 1024,  # 1MB
            'complexity_threshold': 10,
            'enable_nlp': True,
            'output_format': 'html',
            'language': 'en'  # 界面语言
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"配置文件加载失败: {e}")

        return default_config

    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        分析整个目录的代码
        """
        results = {
            'total_files': 0,
            'languages': {},
            'complexity_stats': {},
            'issues': [],
            'recommendations': []
        }

        try:
            directory = Path(directory_path)

            if not directory.exists():
                raise FileNotFoundError(f"目录不存在: {directory_path}")

            # 递归遍历所有文件
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    # 检查文件扩展名
                    ext = file_path.suffix.lower()
                    language = self._get_language_by_extension(ext)

                    if language:
                        try:
                            file_analysis = self.analyze_file(str(file_path))
                            results['total_files'] += 1

                            # 更新语言统计
                            if language not in results['languages']:
                                results['languages'][language] = 0
                            results['languages'][language] += 1

                            # 收集问题
                            if file_analysis['issues']:
                                results['issues'].extend(file_analysis['issues'])

                            # 收集建议
                            if file_analysis['recommendations']:
                                results['recommendations'].extend(file_analysis['recommendations'])

                        except Exception as e:
                            logger.error(f"分析文件失败 {file_path}: {e}")

            # 生成统计信息
            results['complexity_stats'] = self._calculate_complexity_stats(results)

            return results

        except Exception as e:
            logger.error(f"目录分析失败: {e}")
            raise

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 获取文件信息
            file_info = {
                'path': file_path,
                'size': os.path.getsize(file_path),
                'language': self._detect_language(file_path),
                'content': content
            }

            # 代码分析
            code_analysis = self.analyzer.analyze_code(content, file_info['language'])

            # NLP分析（如果有注释）
            nlp_analysis = {}
            if self.config['enable_nlp'] and 'comments' in code_analysis:
                nlp_analysis = self.nlp_processor.analyze_comments(
                    code_analysis['comments'],
                    self.config['language']
                )

            # 合并结果
            analysis_result = {
                **file_info,
                **code_analysis,
                'nlp_analysis': nlp_analysis,
                'issues': self._identify_issues(code_analysis),
                'recommendations': self._generate_recommendations(code_analysis, nlp_analysis),
                'score': self._calculate_code_score(code_analysis, nlp_analysis)
            }

            return analysis_result

        except Exception as e:
            logger.error(f"文件分析失败 {file_path}: {e}")
            raise

    def _get_language_by_extension(self, extension: str) -> Optional[str]:
        """通过扩展名获取语言"""
        for lang, ext in self.supported_languages.items():
            if extension == ext:
                return lang
        return None

    def _detect_language(self, file_path: str) -> str:
        """检测编程语言"""
        ext = Path(file_path).suffix.lower()
        for lang, lang_ext in self.supported_languages.items():
            if ext == lang_ext:
                return lang
        return 'unknown'

    def _identify_issues(self, analysis: Dict) -> List[Dict]:
        """识别代码问题"""
        issues = []

        # 复杂度问题
        if analysis.get('cyclomatic_complexity', 0) > self.config['complexity_threshold']:
            issues.append({
                'type': 'complexity',
                'severity': 'high',
                'message': f"圈复杂度过高: {analysis['cyclomatic_complexity']}",
                'suggestion': '考虑重构函数，拆分为更小的函数'
            })

        # 行数问题
        if analysis.get('lines_of_code', 0) > 200:
            issues.append({
                'type': 'length',
                'severity': 'medium',
                'message': f"文件过长: {analysis['lines_of_code']} 行",
                'suggestion': '考虑将文件拆分为多个模块'
            })

        return issues

    def _generate_recommendations(self, code_analysis: Dict, nlp_analysis: Dict) -> List[Dict]:
        """生成改进建议"""
        recommendations = []

        # 基于代码分析的建议
        if code_analysis.get('comment_ratio', 0) < 0.2:
            recommendations.append({
                'category': 'documentation',
                'priority': 'medium',
                'message': '代码注释比例较低',
                'action': '为关键函数和复杂逻辑添加注释'
            })

        # 基于NLP分析的建议
        if nlp_analysis.get('comment_quality_score', 0) < 0.6:
            recommendations.append({
                'category': 'documentation',
                'priority': 'low',
                'message': '注释质量有待提高',
                'action': '确保注释清晰、准确，使用完整的句子'
            })

        return recommendations

    def _calculate_code_score(self, code_analysis: Dict, nlp_analysis: Dict) -> float:
        """计算代码质量分数"""
        base_score = 100

        # 复杂度扣分
        complexity = code_analysis.get('cyclomatic_complexity', 0)
        if complexity > 20:
            base_score -= 30
        elif complexity > 10:
            base_score -= 15

        # 注释比例加分
        comment_ratio = code_analysis.get('comment_ratio', 0)
        if comment_ratio > 0.3:
            base_score += 10
        elif comment_ratio < 0.1:
            base_score -= 10

        # NLP质量加分
        if nlp_analysis:
            quality_score = nlp_analysis.get('comment_quality_score', 0)
            base_score += quality_score * 20

        return max(0, min(100, base_score))

    def _calculate_complexity_stats(self, results: Dict) -> Dict:
        """计算复杂度统计"""
        # 这里简化为示例，实际应该从所有文件的分析中计算
        return {
            'average_complexity': 5.2,
            'max_complexity': 15,
            'high_complexity_files': 3,
            'low_complexity_files': 10
        }

    def generate_report(self, analysis_results: Dict, output_format: str = 'html') -> str:
        """生成分析报告"""
        if output_format == 'html':
            return self.visualizer.generate_html_report(analysis_results)
        elif output_format == 'json':
            return json.dumps(analysis_results, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            return self.visualizer.generate_markdown_report(analysis_results)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='CodePolyglot - 多语言代码分析助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s analyze my_project/
  %(prog)s analyze --output html --language zh
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析代码')
    analyze_parser.add_argument('path', help='要分析的目录或文件路径')
    analyze_parser.add_argument('--output', '-o', default='html',
                                choices=['html', 'json', 'markdown'],
                                help='输出格式')
    analyze_parser.add_argument('--language', '-l', default='en',
                                choices=['en', 'zh'],
                                help='报告语言')
    analyze_parser.add_argument('--config', '-c', help='配置文件路径')

    # version 命令
    subparsers.add_parser('version', help='显示版本信息')

    args = parser.parse_args()

    if args.command == 'analyze':
        try:
            # 初始化分析器
            polyglot = CodePolyglot(args.config)

            # 设置语言
            polyglot.config['language'] = args.language

            # 分析
            if os.path.isdir(args.path):
                results = polyglot.analyze_directory(args.path)
            else:
                results = polyglot.analyze_file(args.path)

            # 生成报告
            report = polyglot.generate_report(results, args.output)

            # 输出报告
            if args.output == 'html':
                output_file = 'code_analysis_report.html'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"报告已生成: {output_file}")
            else:
                print(report)

        except Exception as e:
            logger.error(f"分析失败: {e}")
            sys.exit(1)

    elif args.command == 'version':
        print("CodePolyglot v1.0.0")
        print("多语言代码分析助手")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()