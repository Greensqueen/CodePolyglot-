"""
代码分析器模块
"""

import re
from typing import Dict, List, Tuple, Any
import ast
import javalang  # 需要安装: pip install javalang
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    lines_of_code: int = 0
    comment_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    cyclomatic_complexity: int = 0
    comment_ratio: float = 0.0
    imports: List[str] = None
    functions: List[Dict] = None
    classes: List[Dict] = None
    comments: List[str] = None

    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.functions is None:
            self.functions = []
        if self.classes is None:
            self.classes = []
        if self.comments is None:
            self.comments = []


class CodeAnalyzer:
    """代码分析器基类"""

    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """分析代码"""
        if language == 'python':
            return self._analyze_python(code)
        elif language == 'java':
            return self._analyze_java(code)
        elif language == 'javascript':
            return self._analyze_javascript(code)
        else:
            return self._analyze_generic(code)

    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """分析Python代码"""
        try:
            tree = ast.parse(code)

            result = AnalysisResult()
            result.lines_of_code = len(code.splitlines())

            # 统计注释
            comment_lines = 0
            comments = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result.function_count += 1
                    func_complexity = self._calculate_cyclomatic_complexity(node)
                    result.cyclomatic_complexity = max(result.cyclomatic_complexity, func_complexity)

                    result.functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': func_complexity,
                        'args': len(node.args.args)
                    })

                elif isinstance(node, ast.ClassDef):
                    result.class_count += 1
                    result.classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })

                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    if isinstance(node, ast.Import):
                        result.imports.extend([alias.name for alias in node.names])
                    else:
                        module = node.module or ""
                        result.imports.extend([f"{module}.{alias.name}" for alias in node.names])

            # 提取注释
            lines = code.splitlines()
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('#') and not line_stripped.startswith('#' * 70):
                    comment_lines += 1
                    comment_text = line_stripped[1:].strip()
                    if comment_text:
                        comments.append(comment_text)

            result.comment_lines = comment_lines
            result.comment_ratio = comment_lines / result.lines_of_code if result.lines_of_code > 0 else 0
            result.comments = comments

            return result.__dict__

        except Exception as e:
            # 如果AST解析失败，使用通用分析
            return self._analyze_generic(code)

    def _analyze_java(self, code: str) -> Dict[str, Any]:
        """分析Java代码"""
        try:
            result = AnalysisResult()
            lines = code.splitlines()
            result.lines_of_code = len(lines)

            # 统计注释和提取注释内容
            comment_lines = 0
            comments = []
            in_block_comment = False
            block_comment_content = []

            for line in lines:
                stripped = line.strip()

                # 处理块注释
                if in_block_comment:
                    if '*/' in line:
                        in_block_comment = False
                        end_idx = line.find('*/')
                        comment_text = line[:end_idx].strip()
                        if comment_text:
                            block_comment_content.append(comment_text)

                        if block_comment_content:
                            comments.append(' '.join(block_comment_content))
                            block_comment_content = []
                    else:
                        comment_text = line.replace('*', '').strip()
                        if comment_text:
                            block_comment_content.append(comment_text)
                    comment_lines += 1
                    continue

                # 单行注释
                if stripped.startswith('//'):
                    comment_lines += 1
                    comment_text = stripped[2:].strip()
                    if comment_text:
                        comments.append(comment_text)

                # 块注释开始
                elif stripped.startswith('/*'):
                    in_block_comment = True
                    comment_lines += 1
                    start_idx = stripped.find('/*') + 2
                    if '*/' in stripped:
                        in_block_comment = False
                        end_idx = stripped.find('*/')
                        comment_text = stripped[start_idx:end_idx].strip()
                        if comment_text:
                            comments.append(comment_text)
                    else:
                        comment_text = stripped[start_idx:].strip()
                        if comment_text:
                            block_comment_content.append(comment_text)

            # 简单的函数和类检测
            function_pattern = r'(public|private|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{'
            class_pattern = r'(public|private|protected)?\s*(class|interface|enum)\s+\w+'

            result.function_count = len(re.findall(function_pattern, code))
            result.class_count = len(re.findall(class_pattern, code))
            result.comment_lines = comment_lines
            result.comment_ratio = comment_lines / result.lines_of_code if result.lines_of_code > 0 else 0
            result.comments = comments

            return result.__dict__

        except Exception as e:
            return self._analyze_generic(code)

    def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """分析JavaScript代码"""
        result = AnalysisResult()
        lines = code.splitlines()
        result.lines_of_code = len(lines)

        # 统计注释
        comment_lines = 0
        comments = []
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            if in_block_comment:
                if '*/' in line:
                    in_block_comment = False
                    end_idx = line.find('*/')
                    comment_text = line[:end_idx].strip()
                    if comment_text:
                        comments.append(comment_text)
                comment_lines += 1
            elif stripped.startswith('//'):
                comment_lines += 1
                comment_text = stripped[2:].strip()
                if comment_text:
                    comments.append(comment_text)
            elif stripped.startswith('/*'):
                in_block_comment = True
                comment_lines += 1
                start_idx = stripped.find('/*') + 2
                if '*/' in stripped:
                    in_block_comment = False
                    end_idx = stripped.find('*/')
                    comment_text = stripped[start_idx:end_idx].strip()
                    if comment_text:
                        comments.append(comment_text)
                else:
                    comment_text = stripped[start_idx:].strip()
                    if comment_text:
                        comments.append(comment_text)

        # 函数检测
        function_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>|\w+\s*\([^)]*\)\s*\{)'
        class_pattern = r'(class\s+\w+|function\s+\w+\s*\([^)]*\)\s*\{)'

        result.function_count = len(re.findall(function_pattern, code))
        result.class_count = len(re.findall(class_pattern, code))
        result.comment_lines = comment_lines
        result.comment_ratio = comment_lines / result.lines_of_code if result.lines_of_code > 0 else 0
        result.comments = comments

        return result.__dict__

    def _analyze_generic(self, code: str) -> Dict[str, Any]:
        """通用代码分析"""
        result = AnalysisResult()
        lines = code.splitlines()
        result.lines_of_code = len(lines)

        # 基本统计
        comment_lines = sum(1 for line in lines if line.strip().startswith(('//', '#', '/*', '*')))
        result.comment_lines = comment_lines
        result.comment_ratio = comment_lines / result.lines_of_code if result.lines_of_code > 0 else 0

        return result.__dict__

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """计算圈复杂度（简化版）"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith,
                                  ast.Try, ast.ExceptHandler, ast.Assert, ast.BoolOp)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity