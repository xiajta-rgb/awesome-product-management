"""
需求描述补全优化器 v3
输出字段对齐标准录入字段：title/background/pain_points/description/demand_module
"""

import yaml
from datetime import datetime


class DemandRefiner:

    def __init__(self, rules_path: str = None):
        if rules_path is None:
            import os
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_refinement.yaml')

        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

    def _build_refinement_prompt(self, demand_raw: dict, demand_id: str = None) -> str:
        raw_text = demand_raw.get('description', demand_raw.get('raw_description', ''))
        extra = '\n'.join([f"- {k}: {v}" for k, v in demand_raw.items()
                          if k not in ('description', 'raw_description', 'id') and v])

        output_fields = self.rules.get('output_fields', {})
        fields_text = '\n'.join([
            f"- {data.get('name', key)}: {data.get('description', '')} {'[自动推导]' if data.get('auto_derived') else '[需补全]'}"
            for key, data in output_fields.items()
            if not data.get('auto_derived')
        ])

        checks = '\n'.join([
            f"- {'[必须]' if c['min_requirement'] else '[建议]'} {c['field']}: {c['check']}"
            for c in self.rules.get('quality_checks', [])
        ])

        module_guide = output_fields.get('demand_module', {}).get('derivation_guide', '')

        return f"""你是专业产品经理。请将以下原始需求补全为结构化需求文档。

## 原始需求
{raw_text}
{extra if extra else ''}

## 补全方法论（按顺序应用）
1. 5W1H: 确保覆盖Who/What/When/Where/Why/How
2. User Story: 生成 As a... I want... so that... 格式
3. JTBD: 识别核心Job vs 边缘Job，评估当前满意度（结论复用于后续PM框架评分）
4. PR-FAQ: 从客户视角验证需求真实性
5. SMART: 预期价值必须具体、可量化、有时限

## 需补全字段（仅手动字段，自动字段由评分推导）
{fields_text}

## 需求模块推导参考
{module_guide}

## 输出格式（JSON）
{{
  "demand_id": "{demand_id or '自动生成'}",
  "proposer": "需求提出人姓名",
  "title": "一句话简单描述需求核心内容（≤50字）",
  "demand_module": "仓储与物流域/研发域/供应链与制造域/营销域",
  "background": "问题背景与现状说明",
  "pain_points": "描述当前业务的痛点",
  "description": "需求点补充描述更具体详细",
  "user_story": "As a... I want... so that...",
  "expected_value": "SMART量化价值",
  "target_users": "角色、部门、规模",
  "resource_input": "人月、技术栈、外部依赖",
  "deadline_risk": "时间节点、延期后果",
  "confidence": {{
    "confirmed": ["用户明确提供的信息"],
    "inferred": ["AI合理推测的信息"],
    "assumed": ["AI假设需确认的信息"]
  }}
}}

## 质量自检
{checks}

## 规则
- 不编造数据：inferred和assumed必须合理
- JTBD分析结论将复用于后续PM框架评分，需明确标注核心Job/边缘Job
- 严格区分confirmed/inferred/assumed
- title必须≤50字，简洁描述核心内容
- demand_module根据推导参考判断，需合理
"""

    def refine_demand(self, demand_raw: dict, demand_id: str = None) -> dict:
        if not demand_id:
            demand_id = demand_raw.get('id', 'unknown')
        return {
            'demand_id': demand_id,
            'refinement_prompt': self._build_refinement_prompt(demand_raw, demand_id),
            'note': '将此提示词发送给AI补全，解析返回的JSON'
        }

    def refine_batch(self, demands_raw: list) -> list:
        return [self.refine_demand(d, d.get('id', f'D{i+1:03d}')) for i, d in enumerate(demands_raw)]


if __name__ == '__main__':
    refiner = DemandRefiner()
    result = refiner.refine_demand({'description': '亚马逊侵权专利库自动化采集脚本'}, 'D001')
    print(result['refinement_prompt'])
