"""
需求智能评分引擎 v5 - PM框架深度分析版
运用 RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star 等专业框架
"""

import yaml
from datetime import datetime
from typing import Optional


class DemandScorer:
    """需求评分器 v5 - PM框架深度分析"""

    def __init__(self, rules_path: str = None):
        if rules_path is None:
            import os
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_scoring_rules.yaml')

        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

        self.dimensions = self.rules['dimensions']
        self.grade_rules = self.rules['grade_rules']

    def _build_pm_framework_prompt(self, demand: dict) -> str:
        return """
## PM专业框架分析（评分前必做）

在给出分数之前，请先按以下8个PM框架逐一分析需求：

### ① JTBD（Jobs-to-be-Done）分析
- 用户"雇佣"这个功能要完成什么核心任务？
- 是功能性Job、情感性Job还是社会性Job？
- 这是核心Job还是边缘Job？
- 当前解决方案满意度如何？（高/中/低）

### ② Amazon Working Backwards 验证
- 如果为这个需求写一篇新闻稿，标题是什么？
- 有客户需求证据吗？（有明确证据/间接推断/纯属假设）
- 客户体验路径是否清晰？

### ③ North Star（北极星指标）评估
- 这个需求与公司/产品的北极星指标是什么关系？
- 直接影响 / 间接影响 / 无关？

### ④ OKR 对齐判断
- 这个需求支撑哪个层级的OKR？
- 公司级 / 部门级 / 团队级 / 无对齐？

### ⑤ OST（机会解决方案树）定位
- 需求在机会树上的位置？
- 主干机会 / 分支机会 / 脱离机会树？

### ⑥ RICE 量化评估
- Reach: 影响多少用户/客户？（量化数字）
- Impact: 3=大量 / 2=中等 / 1=轻微 / 0.5=极小
- Confidence: 100%=高 / 80%=中 / 50%=低
- Effort: 需要多少人月？
- RICE Score = (Reach × Impact × Confidence) / Effort

### ⑦ Crossing the Chasm（跨越鸿沟）阶段判断
- 需求服务的用户群体处于采纳曲线的哪个阶段？
- 跨越鸿沟阶段 / 早期采纳者阶段 / 滞后期？

### ⑧ Technical Debt（技术债务）评估
- 需求对技术架构的影响？
- 减少技术债 / 不增不减 / 增加技术债？
"""

    def _build_demand_info_section(self, demand: dict) -> str:
        """构建需求信息段，支持补全后的丰富字段"""
        lines = []

        if demand.get('demand_name'):
            lines.append(f"- 需求名称: {demand['demand_name']}")
        if demand.get('demand_id'):
            lines.append(f"- 需求ID: {demand['demand_id']}")
        else:
            lines.append(f"- 需求ID: {demand.get('id', 'unknown')}")
        if demand.get('demand_category'):
            lines.append(f"- 需求分类: {demand['demand_category']}")
        if demand.get('description'):
            lines.append(f"- 需求描述: {demand['description']}")
        if demand.get('background'):
            lines.append(f"- 需求背景: {demand['background']}")
        if demand.get('pain_points'):
            lines.append(f"- 业务痛点: {demand['pain_points']}")
        if demand.get('target_users'):
            lines.append(f"- 目标用户: {demand['target_users']}")
        if demand.get('usage_scenario'):
            lines.append(f"- 使用场景: {demand['usage_scenario']}")
        if demand.get('user_story'):
            lines.append(f"- 用户故事: {demand['user_story']}")
        if demand.get('expected_value'):
            lines.append(f"- 预期价值: {demand['expected_value']}")
        if demand.get('cross_department_impact'):
            lines.append(f"- 跨部门影响: {demand['cross_department_impact']}")
        if demand.get('resource_input'):
            lines.append(f"- 资源投入: {demand['resource_input']}")
        if demand.get('deadline_risk'):
            lines.append(f"- 截止风险: {demand['deadline_risk']}")
        if demand.get('success_metrics'):
            lines.append(f"- 成功指标: {demand['success_metrics']}")
        if demand.get('risks_assumptions'):
            lines.append(f"- 风险与假设: {demand['risks_assumptions']}")

        confidence = demand.get('confidence', {})
        if confidence:
            confirmed = confidence.get('confirmed', [])
            inferred = confidence.get('inferred', [])
            assumed = confidence.get('assumed', [])
            lines.append(f"- 信息置信度: 已确认({len(confirmed)}项) / 推测({len(inferred)}项) / 待确认({len(assumed)}项)")
            if assumed:
                lines.append(f"- 待确认信息: {', '.join(assumed)}")

        return '\n'.join(lines)

    def _build_scoring_prompt(self, demand: dict, strategy_focus: list = None, calibration_rules: list = None) -> str:
        calibration_section = ""
        if calibration_rules:
            rules_text = "\n".join([
                f"  - 触发词: \"{r['trigger']}\" → {r['dimension']}: {r['action']}={r.get('value', 'N/A')} (原因: {r['reason']})"
                for r in calibration_rules
            ])
            calibration_section = f"""
## 校准规则（自学习产出，优先级高于基础规则）
{rules_text}
"""

        demand_info = self._build_demand_info_section(demand)

        pm_framework_details = ""
        for dim_key, dim_data in self.dimensions.items():
            if 'pm_frameworks' in dim_data:
                frameworks = dim_data['pm_frameworks']
                fw_text = "\n".join([
                    f"    - {fw['name']}: {fw['description']} → {fw['scoring_guide']}"
                    for fw in frameworks
                ])
                pm_framework_details += f"""
### {dim_data['name']}（{dim_data['weight']}分{', 反向计分' if dim_data.get('reverse_score') else ''}）
PM框架支撑:
{fw_text}
"""

        refined_note = "（已进行需求描述补全优化）" if demand.get('demand_name') or demand.get('background') else "（原始描述）"

        return f"""你是一个专业的需求评审专家，精通产品管理方法论。请根据以下评分规则和PM专业框架对需求进行深度评分{refined_note}。

## 需求信息
{demand_info}
{f'- 战略重点: {", ".join(strategy_focus)}' if strategy_focus else ''}
{calibration_section}
{self._build_pm_framework_prompt(demand)}

## 评分规则（含PM框架支撑）
{pm_framework_details}

### 评分标准
1. 业务价值 (25分): 21-25分=显著提升收入/降本≥10%,核心Job,直接影响NSM | 16-20分=提升效率≥20%,有客户验证 | 11-15分=局部优化,缺乏验证 | 0-10分=无价值,边缘Job
2. 战略匹配度 (20分): 17-20分=公司级OKR,机会树主干 | 13-16分=部门级OKR,分支 | 9-12分=无OKR对齐 | 0-8分=偏离战略
3. 影响范围 (15分): 13-15分=3+部门,高Reach | 9-12分=2部门,中Reach | 5-8分=单部门,低Reach | 0-4分=个人,极低Reach
4. 投入产出比 (15分): 13-15分=低Effort高Confidence,ROI≥3:1 | 9-12分=中等,ROI 1:1-3:1 | 5-8分=高投入,低Confidence | 0-4分=极低Confidence
5. 紧急程度 (15分): 13-15分=合规/风险/窗口关闭 | 9-12分=业务推进需要 | 5-8分=可延后 | 0-4分=无紧急性
6. 实施复杂度 (10分,反向): 8-10分=简单,减少技术债 | 5-7分=中等 | 2-4分=较难,跨部门 | 0-1分=极难,增加技术债

## 输出格式
请以JSON格式输出评分结果，格式如下：
{{
  "pm_framework_analysis": {{
    "jtbd": {{ "core_job": "核心Job描述", "job_type": "功能性/情感性/社会性", "importance": "核心/边缘", "current_satisfaction": "高/中/低" }},
    "working_backwards": {{ "press_release_title": "新闻稿标题", "customer_evidence": "有明确证据/间接推断/纯属假设", "cx_path_clear": true/false }},
    "north_star": {{ "nsm_relation": "直接影响/间接影响/无关", "detail": "说明" }},
    "okr": {{ "alignment_level": "公司级/部门级/团队级/无对齐", "detail": "说明" }},
    "ost": {{ "position": "主干/分支/脱离", "detail": "说明" }},
    "rice": {{ "reach": 数字, "impact": 数字, "confidence": 百分比, "effort": 人月, "rice_score": 数字 }},
    "crossing_the_chasm": {{ "stage": "跨越鸿沟/早期采纳者/滞后期", "detail": "说明" }},
    "technical_debt": {{ "impact": "减少/不变/增加", "detail": "说明" }}
  }},
  "framework_cross_validation": {{
    "consensus": "多框架一致/存在矛盾",
    "detail": "说明框架交叉验证结论"
  }},
  "scores": {{
    "business_value": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }},
    "strategy_alignment": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }},
    "impact_scope": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }},
    "roi": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }},
    "urgency": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }},
    "implementation_complexity": {{ "score": 分数, "reason": "评分理由(含PM框架依据)" }}
  }}
}}

请仔细分析需求内容，先完成PM框架分析，再基于框架分析结论给出评分。每个维度的评分理由必须包含PM框架分析依据。
"""

    def _parse_llm_score(self, response: str) -> dict:
        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return None

        try:
            return json.loads(json_match.group())
        except:
            return None

    def score_demand(self, demand: dict, strategy_focus: list = None, calibration_rules: list = None) -> dict:
        prompt = self._build_scoring_prompt(demand, strategy_focus, calibration_rules)

        return {
            'id': demand.get('id', 'unknown'),
            'description': demand.get('description', ''),
            'submitter': demand.get('submitter', ''),
            'scoring_prompt': prompt,
            'note': '请将此提示词发送给 AI 进行评分，然后使用 parse_llm_score() 解析结果'
        }

    def score_batch(self, demands: list, strategy_focus: list = None, calibration_rules: list = None) -> list:
        results = []
        for demand in demands:
            result = self.score_demand(demand, strategy_focus, calibration_rules)
            results.append(result)

        return results


def auto_score_demand(demands: list, rules_path: str = None, strategy_focus: list = None, calibration_rules: list = None) -> dict:
    scorer = DemandScorer(rules_path)
    scored_demands = scorer.score_batch(demands, strategy_focus, calibration_rules)

    return {
        'scored_demands': scored_demands,
        'stats': {
            'total': len(scored_demands),
            'note': '实际评分需由 AI Agent 执行'
        },
        'scoring_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    test_demand = {
        'id': 'D001',
        'description': '亚马逊侵权专利库自动化采集脚本，提升采集效率和避免侵权风险',
        'submitter': '研发-张三',
        'usage_scenario': '法务和运营部门日常使用，替代手动采集',
        'expected_value': '提升采集效率3倍，减少侵权风险，已收到2次侵权警告',
        'cross_department_impact': '法务、运营2个部门',
        'resource_input': '1人月开发资源',
        'deadline_risk': '下月底前必须上线，存在合规风险'
    }

    scorer = DemandScorer()
    result = scorer.score_demand(test_demand, strategy_focus=['合规风控', '运营效率提升'])

    print("=== 评分提示词（供 AI Agent 使用） ===\n")
    print(result['scoring_prompt'])
