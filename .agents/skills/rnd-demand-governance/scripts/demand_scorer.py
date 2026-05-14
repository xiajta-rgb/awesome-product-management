"""
需求智能评分引擎 v6 - 精简版
从YAML规则动态构建评分提示词，消除硬编码
"""

import yaml
from datetime import datetime


class DemandScorer:

    def __init__(self, rules_path: str = None):
        if rules_path is None:
            import os
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_scoring_rules.yaml')

        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

        self.dimensions = self.rules['dimensions']
        self.grade_rules = self.rules['grade_rules']

    def _build_demand_info_section(self, demand: dict) -> str:
        field_map = [
            ('demand_name', '需求名称'),
            ('demand_id', '需求ID'), ('id', '需求ID'),
            ('demand_category', '需求分类'),
            ('description', '需求描述'),
            ('background', '需求背景'),
            ('pain_points', '业务痛点'),
            ('target_users', '目标用户'),
            ('usage_scenario', '使用场景'),
            ('user_story', '用户故事'),
            ('expected_value', '预期价值'),
            ('cross_department_impact', '跨部门影响'),
            ('resource_input', '资源投入'),
            ('deadline_risk', '截止风险'),
            ('success_metrics', '成功指标'),
            ('risks_assumptions', '风险与假设'),
        ]
        lines = []
        for key, label in field_map:
            val = demand.get(key)
            if val:
                lines.append(f"- {label}: {val}")

        confidence = demand.get('confidence', {})
        if confidence:
            c = len(confidence.get('confirmed', []))
            i = len(confidence.get('inferred', []))
            a = len(confidence.get('assumed', []))
            lines.append(f"- 信息置信度: 已确认{c}项 / 推测{i}项 / 待确认{a}项")
            assumed = confidence.get('assumed', [])
            if assumed:
                lines.append(f"- 待确认: {', '.join(assumed)}")

        return '\n'.join(lines)

    def _build_dimensions_section(self) -> str:
        parts = []
        for dim_key, dim_data in self.dimensions.items():
            weight = dim_data['weight']
            reverse = '，反向计分' if dim_data.get('reverse_score') else ''
            parts.append(f"\n### {dim_data['name']}（{weight}分{reverse}）")

            for rule in dim_data.get('rules', []):
                cond = rule.get('condition', rule.get('description', ''))
                parts.append(f"- {rule['min_score']}-{rule['max_score']}分: {cond}")

            if 'pm_frameworks' in dim_data:
                parts.append("PM框架支撑:")
                for fw in dim_data['pm_frameworks']:
                    parts.append(f"  - {fw['name']}: {fw['scoring_guide']}")

        return '\n'.join(parts)

    def _build_grade_section(self) -> str:
        parts = ["\n### 定级规则"]
        for grade_key, grade_data in self.grade_rules.items():
            label = grade_key.upper()
            min_s = grade_data.get('min', grade_data.get('min_score', 0))
            max_s = grade_data.get('max', grade_data.get('max_score', 100))
            gtype = grade_data.get('type', '')
            action = grade_data.get('action', '')
            parts.append(f"- {label}({min_s}-{max_s}分): {gtype} — {action}")
        return '\n'.join(parts)

    def _build_scoring_prompt(self, demand: dict, strategy_focus: list = None, calibration_rules: list = None) -> str:
        calibration_section = ""
        if calibration_rules:
            rules_text = "\n".join([
                f"  - \"{r['trigger']}\" → {r['dimension']}: {r['action']}={r.get('value', 'N/A')} ({r['reason']})"
                for r in calibration_rules
            ])
            calibration_section = f"\n## 校准规则（优先级高于基础规则）\n{rules_text}\n"

        demand_info = self._build_demand_info_section(demand)
        dimensions = self._build_dimensions_section()
        grades = self._build_grade_section()
        refined_tag = "（已补全优化）" if demand.get('demand_name') or demand.get('background') else "（原始描述）"

        return f"""你是专业需求评审专家。请对以下需求进行PM框架分析并评分{refined_tag}。

## 需求信息
{demand_info}
{f'- 战略重点: {", ".join(strategy_focus)}' if strategy_focus else ''}
{calibration_section}
## PM框架分析（评分前必做）

依次分析，每个框架给出一句结论：
1. JTBD: 核心Job还是边缘Job？当前满意度？
2. Working Backwards: 有客户证据还是纯属假设？
3. North Star: 直接/间接/无关？
4. OKR: 公司级/部门级/团队级/无对齐？
5. OST: 主干/分支/脱离？
6. RICE: Reach=? Impact=? Confidence=? Effort=? → Score=?
7. Crossing the Chasm: 跨越鸿沟/早期采纳者/滞后期？
8. Technical Debt: 减少/不变/增加？

框架交叉验证：多框架一致→高置信；矛盾→说明权衡。

## 评分规则
{dimensions}
{grades}

## 输出格式（JSON）
{{
  "pm_analysis": {{
    "jtbd": "结论",
    "working_backwards": "结论",
    "north_star": "结论",
    "okr": "结论",
    "ost": "结论",
    "rice": {{"reach": 0, "impact": 0, "confidence": "0%", "effort": "0人月", "score": 0}},
    "crossing_the_chasm": "结论",
    "technical_debt": "结论",
    "cross_validation": "一致/矛盾-说明"
  }},
  "scores": {{
    "business_value": {{"score": 0, "reason": "含PM框架依据"}},
    "strategy_alignment": {{"score": 0, "reason": "含PM框架依据"}},
    "impact_scope": {{"score": 0, "reason": "含PM框架依据"}},
    "roi": {{"score": 0, "reason": "含PM框架依据"}},
    "urgency": {{"score": 0, "reason": "含PM框架依据"}},
    "implementation_complexity": {{"score": 0, "reason": "含PM框架依据"}}
  }}
}}
"""

    def score_demand(self, demand: dict, strategy_focus: list = None, calibration_rules: list = None) -> dict:
        prompt = self._build_scoring_prompt(demand, strategy_focus, calibration_rules)
        return {
            'id': demand.get('id', demand.get('demand_id', 'unknown')),
            'description': demand.get('description', ''),
            'scoring_prompt': prompt,
            'note': '将此提示词发送给AI评分，解析返回的JSON'
        }

    def score_batch(self, demands: list, strategy_focus: list = None, calibration_rules: list = None) -> list:
        return [self.score_demand(d, strategy_focus, calibration_rules) for d in demands]


if __name__ == '__main__':
    test_demand = {
        'id': 'D001',
        'description': '亚马逊侵权专利库自动化采集脚本，提升采集效率和避免侵权风险',
        'background': '手动采集效率低，已有2次侵权警告',
        'target_users': '法务3人+运营5人',
        'expected_value': '采集效率提升3倍，侵权警告降至0',
        'cross_department_impact': '法务、运营2个部门',
        'resource_input': '1人月',
        'deadline_risk': '下月底前上线，存在合规风险'
    }

    scorer = DemandScorer()
    result = scorer.score_demand(test_demand, strategy_focus=['合规风控'])
    print(result['scoring_prompt'])
