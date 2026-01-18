"""
Web界面 - Flask应用
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any
import threading

# 导入分析器
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import CodePolyglot

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# 全局分析器实例
polyglot = CodePolyglot()


class AnalysisTask:
    """分析任务类"""

    def __init__(self):
        self.tasks = {}
        self.task_id_counter = 0
        self.lock = threading.Lock()

    def create_task(self, path: str, language: str = 'en') -> int:
        """创建分析任务"""
        with self.lock:
            self.task_id_counter += 1
            task_id = self.task_id_counter

            # 创建任务线程
            thread = threading.Thread(
                target=self._run_analysis,
                args=(task_id, path, language)
            )

            self.tasks[task_id] = {
                'id': task_id,
                'path': path,
                'language': language,
                'status': 'pending',
                'progress': 0,
                'result': None,
                'error': None,
                'start_time': datetime.now(),
                'end_time': None,
                'thread': thread
            }

            thread.start()
            return task_id

    def _run_analysis(self, task_id: int, path: str, language: str):
        """运行分析"""
        task = self.tasks[task_id]

        try:
            task['status'] = 'running'
            task['progress'] = 10

            # 设置语言
            polyglot.config['language'] = language

            # 分析
            task['progress'] = 30
            if os.path.isdir(path):
                results = polyglot.analyze_directory(path)
            else:
                results = polyglot.analyze_file(path)

            task['progress'] = 70

            # 生成报告
            report = polyglot.generate_report(results, 'json')
            task['result'] = json.loads(report)

            task['progress'] = 100
            task['status'] = 'completed'

        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)

        finally:
            task['end_time'] = datetime.now()

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """获取任务信息"""
        return self.tasks.get(task_id)


analysis_task = AnalysisTask()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """分析代码"""
    try:
        # 检查是否有文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # 保存上传的文件
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                path = filename
            else:
                return jsonify({'error': 'No file selected'}), 400
        elif 'path' in request.form:
            path = request.form['path']
            if not os.path.exists(path):
                return jsonify({'error': 'Path does not exist'}), 400
        else:
            return jsonify({'error': 'No file or path provided'}), 400

        # 获取语言设置
        language = request.form.get('language', 'en')

        # 创建分析任务
        task_id = analysis_task.create_task(path, language)

        return jsonify({
            'task_id': task_id,
            'message': 'Analysis started'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/task/<int:task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    task = analysis_task.get_task(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    response = {
        'id': task['id'],
        'status': task['status'],
        'progress': task['progress'],
        'start_time': task['start_time'].isoformat() if task['start_time'] else None,
        'end_time': task['end_time'].isoformat() if task['end_time'] else None,
        'error': task['error']
    }

    if task['status'] == 'completed':
        response['result'] = task['result']

    return jsonify(response)


@app.route('/quick-analyze', methods=['POST'])
def quick_analyze():
    """快速分析（直接返回结果，适合小文件）"""
    try:
        if 'code' not in request.form:
            return jsonify({'error': 'No code provided'}), 400

        code = request.form['code']
        language = request.form.get('language', 'python')

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # 分析文件
            polyglot.config['language'] = request.form.get('ui_language', 'en')
            results = polyglot.analyze_file(temp_path)

            return jsonify({
                'success': True,
                'results': results
            })

        finally:
            # 清理临时文件
            os.unlink(temp_path)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/languages')
def get_supported_languages():
    """获取支持的语言列表"""
    return jsonify({
        'programming_languages': list(polyglot.supported_languages.keys()),
        'ui_languages': ['en', 'zh']
    })


@app.route('/example/<language>')
def get_example_code(language):
    """获取示例代码"""
    examples = {
        'python': '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

class MathUtils:
    """A collection of mathematical utilities."""

    @staticmethod
    def factorial(n):
        """Calculate factorial of n."""
        if n == 0:
            return 1
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
        ''',

        'java': '''
import java.util.List;
import java.util.ArrayList;

/**
 * A class for mathematical calculations.
 */
public class MathUtils {

    /**
     * Calculates the Fibonacci number at position n.
     * @param n The position in the Fibonacci sequence
     * @return The Fibonacci number
     */
    public static int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n-1) + fibonacci(n-2);
    }

    /**
     * Calculates the factorial of n.
     * @param n The number to calculate factorial for
     * @return The factorial result
     */
    public static int factorial(int n) {
        if (n == 0) {
            return 1;
        }
        int result = 1;
        for (int i = 1; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}
        ''',

        'javascript': '''
/**
 * Mathematical utility functions.
 */
class MathUtils {

    /**
     * Calculates the Fibonacci number at position n.
     * @param {number} n - The position in the Fibonacci sequence
     * @returns {number} The Fibonacci number
     */
    static fibonacci(n) {
        if (n <= 1) {
            return n;
        }
        return this.fibonacci(n-1) + this.fibonacci(n-2);
    }

    /**
     * Calculates the factorial of n.
     * @param {number} n - The number to calculate factorial for
     * @returns {number} The factorial result
     */
    static factorial(n) {
        if (n === 0) {
            return 1;
        }
        let result = 1;
        for (let i = 1; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}

// TODO: Add more mathematical functions
// FIXME: Optimize recursive functions
        '''
    }

    return examples.get(language.lower(), examples['python'])


if __name__ == '__main__':
    # 创建模板目录
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)

    # 创建基本模板
    index_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CodePolyglot - Multi-language Code Analyzer</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #2563eb, #7c3aed); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
            .tabs { display: flex; gap: 1rem; margin-bottom: 2rem; }
            .tab { padding: 1rem 2rem; background: #f3f4f6; border-radius: 8px; cursor: pointer; }
            .tab.active { background: #2563eb; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .code-editor { width: 100%; height: 300px; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; padding: 1rem; border: 1px solid #d1d5db; border-radius: 8px; }
            .results { margin-top: 2rem; padding: 2rem; background: #f9fafb; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 CodePolyglot</h1>
                <p>Multi-language Code Analysis Tool</p>
            </div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('quick')">Quick Analysis</div>
                <div class="tab" onclick="switchTab('upload')">Upload Files</div>
                <div class="tab" onclick="switchTab('directory')">Directory Analysis</div>
            </div>

            <div id="quick" class="tab-content active">
                <h2>Quick Code Analysis</h2>
                <select id="language">
                    <option value="python">Python</option>
                    <option value="java">Java</option>
                    <option value="javascript">JavaScript</option>
                </select>
                <button onclick="loadExample()">Load Example</button>
                <textarea id="code" class="code-editor" placeholder="Paste your code here..."></textarea>
                <button onclick="analyzeCode()">Analyze Code</button>
            </div>

            <div id="upload" class="tab-content">
                <h2>Upload Files</h2>
                <input type="file" id="fileUpload" multiple>
                <button onclick="uploadFiles()">Upload and Analyze</button>
            </div>

            <div id="directory" class="tab-content">
                <h2>Analyze Directory</h2>
                <input type="text" id="directoryPath" placeholder="/path/to/your/code">
                <button onclick="analyzeDirectory()">Analyze Directory</button>
            </div>

            <div id="results" class="results" style="display: none;">
                <h2>Analysis Results</h2>
                <div id="resultsContent"></div>
            </div>
        </div>

        <script>
            function switchTab(tabName) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById(tabName).classList.add('active');
            }

            async function loadExample() {
                const lang = document.getElementById('language').value;
                const response = await fetch('/example/' + lang);
                const code = await response.text();
                document.getElementById('code').value = code;
            }

            async function analyzeCode() {
                const code = document.getElementById('code').value;
                const lang = document.getElementById('language').value;

                const formData = new FormData();
                formData.append('code', code);
                formData.append('language', lang);
                formData.append('ui_language', 'en');

                const response = await fetch('/quick-analyze', {
                    method: 'POST',
                    body: formData
                });

                const results = await response.json();
                displayResults(results);
            }

            function displayResults(data) {
                document.getElementById('results').style.display = 'block';
                const content = document.getElementById('resultsContent');

                if (data.error) {
                    content.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }

                const results = data.results;
                let html = `
                    <h3>File: ${results.path}</h3>
                    <p>Language: ${results.language}</p>
                    <p>Score: ${results.score}/100</p>
                    <p>Lines of Code: ${results.lines_of_code}</p>
                    <p>Comment Ratio: ${(results.comment_ratio * 100).toFixed(1)}%</p>
                `;

                if (results.issues && results.issues.length > 0) {
                    html += '<h4>Issues:</h4><ul>';
                    results.issues.forEach(issue => {
                        html += `<li>${issue.message}</li>`;
                    });
                    html += '</ul>';
                }

                content.innerHTML = html;
            }

            // Load Python example by default
            window.onload = loadExample;
        </script>
    </body>
    </html>
    '''

    # 保存模板
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)

    # 运行Flask应用
    app.run(debug=True, port=5000)