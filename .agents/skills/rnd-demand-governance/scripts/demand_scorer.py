"""
需求智能评分引擎 v7
- 结构化评分理由（判断依据+扣分原因）
- AI建议8维度生成指令
- company_context集成
- dedup_rules/override_rules引用
"""

import yaml
from datetime import datetime


class DemandScorer:

    def __init__(self, rules_path: str = None, context_path: str = None):
        import os
        if rules_path is None:
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_scoring_rules.yaml')
        if context_path is None:
            context_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'company_context.yaml')

        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

        self.dimensions = self.rules['dimensions']
        self.grade_rules = self.rules['grade_rules']
        self.dedup_rules = self.rules.get('dedup_rules', {})
        self.status_flow = self.rules.get('status_flow', [])
        self.company_context_rules = self.rules.get('company_context_rules', {})

        self.company_context = {}
        if os.path.exists(context_path):
            with open(context_path, 'r', encoding='utf-8') as f:
                self.company_context = yaml.safe_load(f) or {}

    def _build_demand_info_section(self, demand: dict) -> str:
        field_map = [
            ('title', '标题'),
            ('demand_module', '需求模块'),
            ('background', '背景'),
            ('pain_points', '业务痛点'),
            ('description', '需求描述'),
            ('target_users', '目标用户'),
            ('user_story', '用户故事'),
            ('expected_value', '预期价值'),
            ('cross_department_impact', '跨部门影响'),
            ('resource_input', '资源投入'),
            ('deadline_risk', '截止风险'),
            ('success_metrics', '成功指标'),
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

    def _build_context_section(self) -> str:
        if not self.company_context:
            return ""

        parts = ["\n## 公司知识（评分时参考）"]
        systems = self.company_context.get('systems', [])
        if systems:
            parts.append("系统: " + ", ".join([f"{s['name']}({s.get('related_modules', [])})" for s in systems]))
        data_sources = self.company_context.get('data_sources', [])
        if data_sources:
            parts.append("数据源: " + ", ".join([s['name'] for s in data_sources]))
        departments = self.company_context.get('departments', [])
        if departments:
            parts.append("部门: " + ", ".join([d['name'] for d in departments]))
        business_rules = self.company_context.get('business_rules', [])
        if business_rules:
            parts.append("业务规则: " + ", ".join([r['name'] for r in business_rules]))

        return '\n'.join(parts)

    def _build_dimensions_section(self) -> str:
        parts = []
        for dim_key, dim_data in self.dimensions.items():
            weight = dim_data['weight']
            reverse = '，反向计分' if dim_data.get('reverse_score') else ''
            parts.append(f"\n### {dim_data['name']}（{weight}分{reverse}）")

            for rule in dim_data.get('rules', []):
                cond = rule.get('condition', rule.get('description', ''))
                parts.append(f"- {rule['min_score']}-{rule['max_score']}分: {cond}")

            if 'override_rules' in dim_data:
                for ov in dim_data['override_rules']:
                    parts.append(f"  ⚠️ 强制规则: {ov['condition']} → 最高{ov['value']}分（{ov['reason']}）")

            if 'pm_frameworks' in dim_data:
                parts.append("PM框架支撑:")
                for fw in dim_data['pm_frameworks']:
                    parts.append(f"  - {fw['name']}: {fw['scoring_guide']}")

        return '\n'.join(parts)

    def _build_grade_section(self) -> str:
        parts = ["\n### 定级规则（评分→标签→优先级→需求类型 自动映射）"]
        for grade_key, grade_data in self.grade_rules.items():
            label = grade_key.upper()
            min_s = grade_data.get('min', 0)
            max_s = grade_data.get('max', 100)
            gtype = grade_data.get('type', '')
            action = grade_data.get('action', '')
            glbl = grade_data.get('label', '')
            gpri = grade_data.get('priority', '')
            gdtype = grade_data.get('demand_type', '')
            parts.append(f"- {label}({min_s}-{max_s}分): {gtype} | 标签={glbl} | 优先级={gpri} | 类型={gdtype} — {action}")
        return '\n'.join(parts)

    def _build_ai_suggestions_section(self) -> str:
        return """
## AI建议生成（8维度，开发人员视角）

评分完成后，必须逐维度检查并生成AI建议：

1. 【业务价值】是否包含量化指标？当前值vs目标值？→ 建议补充量化指标
2. 【战略匹配度】是否对齐OKR？归属哪个战略目标？→ 建议对齐年度OKR
3. 【影响范围】是否列出直接受益部门/岗位/用户规模？→ 建议补充受益清单
4. 【投入产出比】是否明确技术栈、外部依赖、预估人月？→ 建议明确技术方案
5. 【紧急程度】是否有刚性时间节点？→ 建议补充时间节点
6. 【实施复杂度】是否需要拆分阶段？一次性交付风险？→ 建议拆分阶段交付
7. 【开发视角】开发人员能否直接理解并开始工作？验收标准是否明确？→ 建议补充验收标准
8. 【补充缺失】成功度量指标、技术风险评估、跨部门协同机制是否明确？→ 建议补充缺失项

每条建议格式：①【维度】具体可操作的建议内容
"""

    def _build_scoring_prompt(self, demand: dict, strategy_focus: list = None, calibration_rules: list = None) -> str:
        calibration_section = ""
        if calibration_rules:
            rules_text = "\n".join([
                f"  - \"{r['trigger']}\" → {r['dimension']}: {r['action']}={r.get('value', 'N/A')} ({r['reason']})"
                for r in calibration_rules
            ])
            calibration_section = f"\n## 校准规则（优先级高于基础规则）\n{rules_text}\n"

        demand_info = self._build_demand_info_section(demand)
        context_info = self._build_context_section()
        dimensions = self._build_dimensions_section()
        grades = self._build_grade_section()
        ai_suggestions = self._build_ai_suggestions_section()
        refined_tag = "（已补全优化）" if demand.get('title') or demand.get('background') else "（原始描述）"

        return f"""你是专业需求评审专家。请对以下需求进行PM框架分析、评分、生成AI建议{refined_tag}。

## 需求信息
{demand_info}
{f'- 战略重点: {", ".join(strategy_focus)}' if strategy_focus else ''}
{context_info}
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

{ai_suggestions}

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
    "business_value": {{
      "score": 0,
      "basis": "判断依据：为什么给这个分数",
      "deduction": "扣分原因：具体扣分点"
    }},
    "strategy_alignment": {{
      "score": 0,
      "basis": "判断依据",
      "deduction": "扣分原因"
    }},
    "impact_scope": {{
      "score": 0,
      "basis": "判断依据",
      "deduction": "扣分原因"
    }},
    "roi": {{
      "score": 0,
      "basis": "判断依据",
      "deduction": "扣分原因"
    }},
    "urgency": {{
      "score": 0,
      "basis": "判断依据",
      "deduction": "扣分原因"
    }},
    "implementation_complexity": {{
      "score": 0,
      "basis": "判断依据",
      "deduction": "扣分原因"
    }}
  }},
  "scoring_confidence": "高/中/低（信息充分=高，部分推测=中，大量假设=低）",
  "reject_reason": "D级需求必填：驳回的具体原因和改进建议",
  "ai_suggestions": [
    "①【业务价值】具体建议",
    "②【战略匹配度】具体建议",
    "③【影响范围】具体建议",
    "④【投入产出比】具体建议",
    "⑤【紧急程度】具体建议",
    "⑥【实施复杂度】具体建议",
    "⑦【开发视角】具体建议",
    "⑧【补充缺失】具体建议"
  ]
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
        'title': '磐石系统侵权库重构+自动化侵权素材生成+新人风控培训',
        'demand_module': '营销域',
        'background': '现有侵权库不完善，采集上传流程复杂',
        'pain_points': '效率低，一个一个上传查看；新人缺乏风控培训',
        'description': '用机器人生成核心对标品牌侵权设计素材，搭建全覆盖侵权库',
        'expected_value': '采集效率提升3倍，侵权警告降至0',
        'target_users': '法务3人+运营5人',
        'resource_input': '2人月',
        'deadline_risk': '合规风险，需尽快上线'
    }

    scorer = DemandScorer()
    result = scorer.score_demand(test_demand, strategy_focus=['合规风控'])
    print(result['scoring_prompt'][:800])
