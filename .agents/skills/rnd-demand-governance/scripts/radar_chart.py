"""
雷达图生成器 v2
修复SVG坐标计算，使用cos/sin替代错误的线性乘法
"""

import math
from datetime import datetime


class RadarChartGenerator:

    DIMENSION_NAMES = {
        '业务价值': 'business_value',
        '战略匹配度': 'strategy_alignment',
        '影响范围': 'impact_scope',
        '投入产出比': 'roi',
        '紧急程度': 'urgency',
        '实施复杂度': 'implementation_complexity'
    }

    MAX_SCORES = {
        '业务价值': 25,
        '战略匹配度': 20,
        '影响范围': 15,
        '投入产出比': 15,
        '紧急程度': 15,
        '实施复杂度': 10
    }

    def generate_radar_html(self, demand_result: dict, width: int = 600, height: int = 400) -> str:
        scores = demand_result.get('dimension_scores', {})
        dimensions = list(self.MAX_SCORES.keys())
        max_scores = list(self.MAX_SCORES.values())
        actual_scores = [scores.get(dim, 0) for dim in dimensions]
        explanation = self._generate_explanation(demand_result)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
.chart-container {{ max-width: {width}px; margin: 0 auto; }}
.chart-title {{ text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
.explanation {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #007bff; }}
.explanation h3 {{ margin-top: 0; color: #333; }}
.explanation p {{ margin: 5px 0; color: #555; }}
.explanation .highlight {{ color: #007bff; font-weight: bold; }}
.explanation .warning {{ color: #dc3545; font-weight: bold; }}
svg {{ display: block; margin: 0 auto; }}
</style>
</head>
<body>
<div class="chart-container">
<div class="chart-title">需求 {demand_result.get('id', 'unknown')} - 评分雷达图</div>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
{self._generate_svg_polygons(dimensions, actual_scores, max_scores, width, height)}
</svg>
<div class="explanation">
<h3>📊 评分解读</h3>
{explanation}
</div>
</div>
</body>
</html>"""
        return html

    def _generate_svg_polygons(self, dimensions, actual_scores, max_scores, width, height) -> str:
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 2 - 50
        n = len(dimensions)
        angle_step = 2 * math.pi / n

        grid_lines = []
        for level in range(1, 6):
            level_radius = radius * level / 5
            points = []
            for i in range(n):
                angle = angle_step * i - math.pi / 2
                x = cx + level_radius * math.cos(angle)
                y = cy + level_radius * math.sin(angle)
                points.append(f"{x:.1f},{y:.1f}")
            grid_lines.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="#ddd" stroke-width="1"/>')

        axes = []
        for i in range(n):
            angle = angle_step * i - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>')

        data_points = []
        for i in range(n):
            angle = angle_step * i - math.pi / 2
            normalized = actual_scores[i] / max_scores[i] if max_scores[i] > 0 else 0
            r = radius * normalized
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            data_points.append(f"{x:.1f},{y:.1f}")

        data_polygon = f'<polygon points="{" ".join(data_points)}" fill="rgba(0,123,255,0.2)" stroke="#007bff" stroke-width="2"/>'

        data_circles = []
        for i in range(n):
            angle = angle_step * i - math.pi / 2
            normalized = actual_scores[i] / max_scores[i] if max_scores[i] > 0 else 0
            r = radius * normalized
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            data_circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#007bff"/>')

        labels = []
        for i in range(n):
            angle = angle_step * i - math.pi / 2
            label_r = radius + 30
            x = cx + label_r * math.cos(angle)
            y = cy + label_r * math.sin(angle)

            if x < cx - 10:
                anchor = "end"
            elif x > cx + 10:
                anchor = "start"
            else:
                anchor = "middle"

            dy = "-0.3em" if y < cy else "1em"

            labels.append(f'<text x="{x:.1f}" y="{y:.1f}" dy="{dy}" text-anchor="{anchor}" font-size="12" fill="#333">{dimensions[i]} ({actual_scores[i]}/{max_scores[i]})</text>')

        center_text = f'<text x="{cx}" y="{cy}" dy="0.3em" text-anchor="middle" font-size="16" font-weight="bold" fill="#007bff">{sum(actual_scores)}分</text>'

        return "\n".join(grid_lines + axes + [data_polygon] + data_circles + labels + [center_text])

    def _generate_explanation(self, demand_result: dict) -> str:
        scores = demand_result.get('dimension_scores', {})
        grade = demand_result.get('grade', 'unknown')
        total_score = demand_result.get('total_score', 0)

        parts = []
        parts.append(f'<p><span class="highlight">总分: {total_score}分，等级: {grade}</span></p>')

        sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_dim = sorted_dims[0]
        worst_dim = sorted_dims[-1]

        parts.append(f'<p>🟢 <strong>最强维度</strong>: {best_dim[0]} ({best_dim[1]}分)</p>')
        parts.append(f'<p>🔴 <strong>最弱维度</strong>: {worst_dim[0]} ({worst_dim[1]}分)</p>')

        parts.append('<p><strong>维度分析:</strong></p>')
        parts.append('<ul>')

        for dim, score in scores.items():
            max_score = self.MAX_SCORES.get(dim, 100)
            pct = score / max_score if max_score > 0 else 0

            if pct >= 0.8:
                status, color = '优秀', '#28a745'
            elif pct >= 0.6:
                status, color = '良好', '#17a2b8'
            elif pct >= 0.4:
                status, color = '一般', '#ffc107'
            else:
                status, color = '不足', '#dc3545'

            parts.append(f'<li>{dim}: <span style="color:{color}">{status}</span> ({score}/{max_score})</li>')

        parts.append('</ul>')

        if worst_dim[1] < self.MAX_SCORES.get(worst_dim[0], 100) * 0.4:
            parts.append(f'<p><span class="warning">💡 改进建议</span>: 重点提升"{worst_dim[0]}"维度，这是影响总分的短板。</p>')

        return "\n".join(parts)

    def generate_comparison_html(self, demands_results: list, width: int = 800, height: int = 500) -> str:
        dimensions = list(self.MAX_SCORES.keys())

        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body { font-family: Arial, sans-serif; margin: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
th { background-color: #007bff; color: white; }
.grade-A { color: #28a745; font-weight: bold; }
.grade-B { color: #17a2b8; font-weight: bold; }
.grade-C { color: #ffc107; font-weight: bold; }
.grade-D { color: #dc3545; font-weight: bold; }
</style>
</head>
<body>
<h2>需求评分对比表</h2>
<table>
<tr>
<th>需求 ID</th>
<th>总分</th>
<th>等级</th>
"""

        for dim in dimensions:
            html += f"<th>{dim}</th>"
        html += "</tr>\n"

        for result in demands_results:
            scores = result.get('dimension_scores', {})
            grade = result.get('grade', 'unknown')
            total = result.get('total_score', 0)
            id_ = result.get('id', 'unknown')

            html += f"""<tr>
<td>{id_}</td>
<td>{total}</td>
<td class="grade-{grade}">{grade}</td>"""

            for dim in dimensions:
                score = scores.get(dim, 0)
                max_score = self.MAX_SCORES.get(dim, 100)
                pct = score / max_score if max_score > 0 else 0
                bar_width = pct * 100
                color = '#28a745' if pct >= 0.8 else '#17a2b8' if pct >= 0.6 else '#ffc107' if pct >= 0.4 else '#dc3545'

                html += f'<td><div style="width:100px;height:20px;background:#f0f0f0;border-radius:3px;overflow:hidden;"><div style="width:{bar_width}%;height:100%;background:{color};"></div></div><small>{score}/{max_score}</small></td>'

            html += "</tr>\n"

        html += """</table>
</body>
</html>"""

        return html


def generate_radar_chart(demand_result: dict, output_path: str = None) -> str:
    gen = RadarChartGenerator()
    html = gen.generate_radar_html(demand_result)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    return html


if __name__ == '__main__':
    test_result = {
        'id': 'D001',
        'total_score': 88,
        'grade': 'A',
        'dimension_scores': {
            '业务价值': 23,
            '战略匹配度': 19,
            '影响范围': 14,
            '投入产出比': 14,
            '紧急程度': 10,
            '实施复杂度': 8
        }
    }

    gen = RadarChartGenerator()
    html = gen.generate_radar_html(test_result)

    output_path = '/tmp/radar_chart_D001.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"雷达图已保存到: {output_path}")
    print("\n=== 解释性输出 ===")
    print(gen._generate_explanation(test_result))
