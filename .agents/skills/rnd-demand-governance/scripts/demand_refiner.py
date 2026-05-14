"""
需求描述补全优化器 v2 - 精简版
基于5W1H/User Story/JTBD/PR-FAQ/SMART将原始描述补全为结构化需求文档
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

        fields = '\n'.join([f"- {k}: {v}" for k, v in self.rules.get('refinement_fields', {}).items()])
        checks = '\n'.join([
            f"- {'[必须]' if c['min_requirement'] else '[建议]'} {c['field']}: {c['check']}"
            for c in self.rules.get('quality_checks', [])
        ])

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

## 补全字段
{fields}

## 输出格式（JSON）
{{
  "demand_id": "{demand_id or '自动生成'}",
  "demand_name": "简洁可量化的名称",
  "demand_category": "产品优化/效率提升/合规风控/基础设施/新功能开发/体验改进",
  "description": "原始描述保留",
  "background": "当前状况、问题、触发事件",
  "pain_points": "具体表现、影响程度",
  "target_users": "角色、部门、规模",
  "usage_scenario": "典型流程、触发条件",
  "user_story": "As a... I want... so that...",
  "expected_value": "SMART量化价值",
  "cross_department_impact": "涉及部门、影响方式",
  "resource_input": "人月、技术栈、外部依赖",
  "deadline_risk": "时间节点、延期后果",
  "success_metrics": "上线后评估标准",
  "risks_assumptions": "技术/业务风险、假设",
  "confidence": {{
    "confirmed": ["用户明确提供"],
    "inferred": ["AI合理推测"],
    "assumed": ["AI假设需确认"]
  }}
}}

## 质量自检
{checks}

## 规则
- 不编造数据：inferred和assumed必须合理
- JTBD分析结论将复用于后续PM框架评分，需明确标注核心Job/边缘Job
- 严格区分confirmed/inferred/assumed
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
