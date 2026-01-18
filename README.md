# CodePolyglot-
CodePolyglot 可以生成代码分析报告
# CodePolyglot-
CodePolyglot 可以生成代码分析报告
# 🌐 CodePolyglot - 智能多语言代码分析助手

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CodePolyglot** 是一个支持多语言的智能代码分析工具。它能够解析 **Python、Java、JavaScript** 等代码，自动评估复杂度、检测代码异味、分析注释质量，并生成可视化报告，旨在帮助开发者和团队提升代码质量。

> 🎯 **项目亮点**：结合**抽象语法树(AST)解析**与**自然语言处理(NLP)**，实现代码结构与注释质量的综合评估。

---

## ✨ 核心功能

- **🔍 多语言分析**：支持 Python、Java、JavaScript 代码的语法解析与指标计算。
- **📊 智能评估**：
  - 计算圈复杂度、代码行数、注释比例等关键指标。
  - 使用 NLP 技术分析注释的清晰度与完整性。
  - 识别 `TODO`/`FIXME` 标记和潜在代码异味。
- **📈 可视化报告**：一键生成**交互式HTML报告**，包含质量评分仪表盘、语言分布饼图与详细改进建议。
- **⚙️ 灵活使用**：提供命令行接口(CLI)与模块化API，易于集成。

---
命令行使用：
# 分析单个文件，输出JSON结果
python main.py analyze path/to/your_code.py --output json

# 分析整个目录，生成HTML报告
python main.py analyze path/to/your_project/ --output html

# 指定报告语言为中文
python main.py analyze example.py --output html --language zh


