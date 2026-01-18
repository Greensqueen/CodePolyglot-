"""
可视化生成模块 - 基于 Plotly
"""
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any
from datetime import datetime


class Visualizer:
    """基于 Plotly 的可视化生成器"""

    def generate_html_report(self, analysis_results: Dict[str, Any]) -> str:
        """生成完整的HTML分析报告"""

        # 1. 从分析结果中提取关键数据
        score = analysis_results.get('score', 0)
        file_path = analysis_results.get('path', '未知文件')
        lines_of_code = analysis_results.get('lines_of_code', 0)
        function_count = analysis_results.get('function_count', 0)
        comment_ratio = analysis_results.get('comment_ratio', 0)
        languages = analysis_results.get('languages', {})
        issues = analysis_results.get('issues', [])

        # 2. 生成语言分布图表数据
        lang_labels = list(languages.keys()) if languages else ['Python']
        lang_values = list(languages.values()) if languages else [1]

        # 3. 创建图表
        # 图表1：语言分布饼图
        if len(lang_labels) > 0:
            lang_fig = go.Figure(data=[go.Pie(
                labels=lang_labels,
                values=lang_values,
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            )])
            lang_fig.update_layout(
                title_text="语言分布",
                height=300
            )
            lang_chart = lang_fig.to_html(full_html=False)
        else:
            lang_chart = "<p>无多语言数据</p>"

        # 图表2：代码质量评分仪表盘
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "代码质量评分"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        gauge_fig.update_layout(height=300)
        gauge_chart = gauge_fig.to_html(full_html=False)

        # 4. 生成完整HTML报告
        html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodePolyglot 代码分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.6; color: #333; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; 
                  box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                      gap: 1rem; margin: 2rem 0; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 10px; 
                     box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .chart-container {{ background: white; padding: 1.5rem; border-radius: 10px; 
                           margin: 1.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .issue-item {{ padding: 0.75rem; margin: 0.5rem 0; border-left: 4px solid #e74c3c; 
                      background: #fff5f5; }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .danger {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 CodePolyglot 代码分析报告</h1>
            <p>生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>

        <div class="stat-card">
            <h2>📄 分析文件：{file_path}</h2>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>总体评分</h3>
                <div class="{'success' if score >= 70 else 'warning' if score >= 40 else 'danger'}" 
                     style="font-size: 2.5rem; font-weight: bold;">
                    {score}/100
                </div>
            </div>
            <div class="stat-card">
                <h3>代码行数</h3>
                <div style="font-size: 2rem;">{lines_of_code}</div>
            </div>
            <div class="stat-card">
                <h3>函数数量</h3>
                <div style="font-size: 2rem;">{function_count}</div>
            </div>
            <div class="stat-card">
                <h3>注释比例</h3>
                <div style="font-size: 2rem;">{comment_ratio * 100:.1f}%</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📈 代码质量评分</h2>
            <div id="gauge-chart">{gauge_chart}</div>
        </div>

        <div class="chart-container">
            <h2>🌐 语言分布</h2>
            <div id="lang-chart">{lang_chart}</div>
        </div>

        <div class="chart-container">
            <h2>⚠️ 发现的问题 ({len(issues)}个)</h2>
            {self._generate_issues_html(issues) if issues else '<p>🎉 未发现严重问题！</p>'}
        </div>

        <div class="stat-card" style="text-align: center; color: #666; margin-top: 3rem;">
            <p>报告由 CodePolyglot 生成 | 多语言代码分析助手</p>
        </div>
    </div>
</body>
</html>
        '''
        return html_content

    def _generate_issues_html(self, issues):
        """生成问题列表的HTML"""
        if not issues:
            return ""

        html = ""
        for issue in issues:
            severity = issue.get('severity', 'medium')
            border_color = {
                'high': '#e74c3c',
                'medium': '#f39c12',
                'low': '#3498db'
            }.get(severity, '#95a5a6')

            html += f'''
            <div class="issue-item" style="border-left-color: {border_color};">
                <strong>{issue.get('type', '未知').upper()}</strong>
                <p>{issue.get('message', '')}</p>
                <small>建议：{issue.get('suggestion', '无')}</small>
            </div>
            '''
        return html

    def generate_markdown_report(self, analysis_results: Dict[str, Any]) -> str:
        """生成Markdown格式报告（简化版）"""
        score = analysis_results.get('score', 0)
        return f"""# CodePolyglot 分析报告

## 总体评分：{score}/100

### 关键指标
- 分析文件：{analysis_results.get('path', '未知')}
- 代码行数：{analysis_results.get('lines_of_code', 0)}
- 函数数量：{analysis_results.get('function_count', 0)}
- 注释比例：{analysis_results.get('comment_ratio', 0) * 100:.1f}%

### 报告摘要
{'✅ 代码质量良好' if score >= 70 else '⚠️ 代码需要改进' if score >= 40 else '❌ 代码需要重点优化'}

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
