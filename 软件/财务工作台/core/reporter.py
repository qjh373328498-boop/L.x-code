"""
FinCopilot - 报表生成器
Jinja2 + WeasyPrint 生成 PDF 报告
"""
from jinja2 import Template
from typing import Dict, List, Any
import os


def generate_html_report(data: Dict[str, Any], template_name: str = 'default') -> str:
    """
    生成 HTML 格式报告
    
    参数:
        data: 报告数据
        template_name: 模板名称
    """
    # 默认模板
    template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>财务报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .metric { font-size: 24px; font-weight: bold; color: #2980b9; }
        .warning { color: #e74c3c; }
        .success { color: #27ae60; }
    </style>
</head>
<body>
    <h1>财务分析报告</h1>
    
    <h2>核心指标</h2>
    <table>
        {% for key, value in metrics.items() %}
        <tr>
            <td>{{ key }}</td>
            <td class="metric">{{ "%.2f"|format(value) }}</td>
        </tr>
        {% endfor %}
    </table>
    
    {% if analysis %}
    <h2>分析总结</h2>
    <div>
        {% for item in analysis %}
        <p class="{{ 'success' if item.type == 'positive' else 'warning' }}">
            {{ item.content }}
        </p>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if tables %}
    <h2>详细数据</h2>
    {% for table_name, table_data in tables.items() %}
    <h3>{{ table_name }}</h3>
    <table>
        <thead>
            <tr>
                {% for col in table_data.columns %}
                <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table_data.rows %}
            <tr>
                {% for cell in row %}
                <td>{{ cell }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endfor %}
    {% endif %}
    
    <hr>
    <p style="color: #95a5a6; font-size: 12px;">
        报告生成时间：{{ generated_at }}
    </p>
</body>
</html>
    """
    
    template = Template(template_str)
    html = template.render(data)
    return html


def generate_pdf_report(html_content: str, output_path: str) -> bool:
    """
    将 HTML 转为 PDF
    
    参数:
        html_content: HTML 内容
        output_path: 输出路径
    
    返回:
        是否成功
    """
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_path)
        return True
    except ImportError:
        print("weasyprint 未安装，尝试备用方案...")
        # 备用方案：保存为 HTML
        try:
            with open(output_path.replace('.pdf', '.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"备用方案失败：{e}")
            return False
    except Exception as e:
        print(f"生成 PDF 失败：{e}")
        return False


def format_number(n: float, decimals: int = 2) -> str:
    """格式化数字"""
    if n is None:
        return '-'
    return f"{n:,.{decimals}f}"


def create_analysis_summary(metrics: Dict[str, float]) -> List[Dict]:
    """
    创建分析总结
    
    参数:
        metrics: 指标字典
    """
    analysis = []
    
    # 毛利率分析
    gross_margin = metrics.get('gross_margin', 0)
    if gross_margin > 30:
        analysis.append({
            'type': 'positive',
            'content': f'毛利率 {gross_margin:.1f}%，处于较高水平，盈利能力良好'
        })
    elif gross_margin < 10:
        analysis.append({
            'type': 'warning',
            'content': f'毛利率 {gross_margin:.1f}%，低于行业平均水平，需关注成本控制'
        })
    
    # 流动比率分析
    current_ratio = metrics.get('current_ratio', 0)
    if current_ratio > 2:
        analysis.append({
            'type': 'positive',
            'content': f'流动比率 {current_ratio:.2f}，短期偿债能力较强'
        })
    elif current_ratio < 1:
        analysis.append({
            'type': 'warning',
            'content': f'流动比率 {current_ratio:.2f}，短期偿债压力较大'
        })
    
    return analysis
