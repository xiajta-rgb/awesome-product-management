"""
需求描述补全优化器 v1.0
基于产品管理方法论（5W1H / User Story / JTBD / PR-FAQ / SMART）
将用户原始需求描述补全为结构化、专业化的需求文档
"""

import yaml
import json
from datetime import datetime
from typing import Optional


class DemandRefiner:
    """需求描述补全优化器"""

    def __init__(self, rules_path: str = None):
        if rules_path is None:
            import os
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_refinement.yaml')

        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

        self.refinement_fields = self.rules.get('refinement_fields', {})
        self.refinement_methods = self.rules.get('refinement_methods', [])
        self.quality_checks = self.rules.get('quality_checks', [])

    def _build_refinement_prompt(self, demand_raw: dict, demand_id: str = None) -> str:
        """构建需求补全提示词"""
        raw_text = demand_raw.get('description', demand_raw.get('raw_description', ''))
        extra_context = '\n'.join([
            f"- {k}: {v}" for k, v in demand_raw.items()
            if k not in ('description', 'raw_description', 'id') and v
        ])

        methods_desc = '\n'.join([
            f"- {m['name']}: {m['description']} → {m['application']}"
            for m in self.refinement_methods
        ])

        fields_desc = '\n'.join([
            f"- {k}: {v}" for k, v in self.refinement_fields.items()
        ])

        quality_checklist = '\n'.join([
            f"- {'[必须]' if qc['min_requirement'] else '[建议]'} {qc['field']}: {qc['check']}"
            for qc in self.quality_checks
        ])

        return f"""你是一个专业的产品经理，精通需求分析和调研方法论。请将以下用户原始需求描述补全为结构化、专业化的需求文档。

## 用户原始需求描述
{raw_text}
{extra_context if extra_context else ''}

## 补全方法论（按顺序应用）
{methods_desc}

## 需要补全的字段
{fields_desc}

## 补全输出格式

请以JSON格式输出补全后的需求文档：
{{
  "demand_id": "{demand_id or '自动生成'}",
  "demand_name": "简洁可量化的需求名称（基于5W1H的What）",
  "demand_category": "需求分类（产品优化/效率提升/合规风控/基础设施/新功能开发/体验改进）",
  "description": "{raw_text[:100]}（原始描述保留）",
  "background": "补全后的需求背景（当前状况、存在的问题、触发事件）",
  "pain_points": "补全后的业务痛点（具体表现、影响程度、频率）",
  "target_users": "补全后的目标用户（角色、部门、用户规模）",
  "usage_scenario": "补全后的使用场景（典型使用流程、触发条件）",
  "user_story": "As a [角色], I want [功能], so that [价值]",
  "expected_value": "补全后的预期价值（遵循SMART原则，包含可量化指标）",
  "cross_department_impact": "补全后的跨部门影响（涉及部门、影响方式、协同需求）",
  "resource_input": "补全后的资源投入估算（人月、技术栈、外部依赖）",
  "deadline_risk": "补全后的截止风险（时间节点、延期后果）",
  "success_metrics": "补全后的成功度量指标（上线后如何评估是否成功）",
  "risks_assumptions": "补全后的风险与假设（技术风险、业务风险、外部依赖）",
  "confidence": {{
    "confirmed": ["用户明确提供的信息列表"],
    "inferred": ["AI根据上下文合理推测的信息列表"],
    "assumed": ["AI基于经验假设但需用户确认的信息列表"]
  }}
}}

## 补全规则
1. 5W1H: 确保补全内容覆盖Who/What/When/Where/Why/How六要素
2. User Story: 必须生成标准格式"As a... I want... so that..."
3. JTBD深挖: 识别表面需求背后的真实Job，区分核心Job和边缘Job
4. PR-FAQ反推: 从客户视角验证需求真实性
5. SMART量化: 预期价值必须具体、可量化、可实现、相关、有时限
6. 信息标记: 严格区分confirmed（用户说的）/inferred（AI推测的）/assumed（AI假设的）
7. 不编造数据: inferred和assumed的内容要合理，不能无中生有
8. 保留原文: description字段保留用户原始描述

## 质量自检清单
{quality_checklist}

请仔细分析用户原始描述，运用产品管理专业方法论，补全需求文档。
"""

    def refine_demand(self, demand_raw: dict, demand_id: str = None) -> dict:
        """
        补全单个需求描述
        
        Args:
            demand_raw: 原始需求字典
            demand_id: 需求ID（可选）
            
        Returns:
            补全提示词供 AI Agent 执行
        """
        if not demand_id:
            demand_id = demand_raw.get('id', 'unknown')

        prompt = self._build_refinement_prompt(demand_raw, demand_id)

        return {
            'demand_id': demand_id,
            'refinement_prompt': prompt,
            'note': '请将此提示词发送给 AI 进行需求补全，然后解析返回的 JSON 作为补全后的需求文档'
        }

    def refine_batch(self, demands_raw: list) -> list:
        """批量补全需求描述"""
        results = []
        for i, demand in enumerate(demands_raw):
            demand_id = demand.get('id', f'D{i+1:03d}')
            result = self.refine_demand(demand, demand_id)
            results.append(result)
        return results


def refine_demands(demands_raw: list, rules_path: str = None) -> dict:
    """便捷函数：自动对需求列表进行补全"""
    refiner = DemandRefiner(rules_path)
    refined_demands = refiner.refine_batch(demands_raw)

    return {
        'refined_demands': refined_demands,
        'stats': {
            'total': len(refined_demands),
            'note': '实际补全需由 AI Agent 执行'
        },
        'refinement_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    # 测试：展示如何构建补全提示词
    test_demand = {
        'description': '亚马逊侵权专利库自动化采集脚本'
    }

    refiner = DemandRefiner()
    result = refiner.refine_demand(test_demand, 'D001')

    print("=== 需求补全提示词（供 AI Agent 使用） ===\n")
    print(result['refinement_prompt'])
