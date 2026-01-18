from src.core.analyzer import CodeAnalyzer
from src.core.nlp_processor import NLPProcessor

print("1. 测试 CodeAnalyzer...")
analyzer = CodeAnalyzer()
test_code = """
def hello(name):
    # Say hello
    print(f"Hello, {name}!")
"""
result = analyzer.analyze_code(test_code, "python")
print(f"   分析结果: {result['lines_of_code']} 行代码， {result['function_count']} 个函数")

print("\n2. 测试 NLPProcessor...")
nlp = NLPProcessor()
comments = ["这是一个好的注释", "TODO: 这里需要优化"]
nlp_result = nlp.analyze_comments(comments, "zh")
print(f"   注释质量分数: {nlp_result.get('comment_quality_score', 'N/A')}")

print("\n🎉 核心模块测试通过!")