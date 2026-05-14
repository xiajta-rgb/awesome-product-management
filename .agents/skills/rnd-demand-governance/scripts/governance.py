"""
需求智能治理主入口 v2
整合补全、评分、文档生成、宣导文案生成，提供统一执行接口
与DemandScorer v6 + DemandRefiner v2 + DemandLibrary v4 兼容
"""

import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))

from demand_scorer import DemandScorer
from demand_refiner import DemandRefiner
from demand_library import DemandLibrary
from document_generator import generate_submission_package, format_report
from notice_generator import generate_governance_notice


def execute(
    demand_list: list,
    dept_submitter: str,
    is_trial_period: bool,
    strategy_focus: list = None,
    scoring_rules_path: str = None,
    refinement_rules_path: str = None,
    library_path: str = None
) -> dict:
    scorer = DemandScorer(rules_path=scoring_rules_path)
    refiner = DemandRefiner(rules_path=refinement_rules_path)
    library = DemandLibrary(lib_path=library_path)

    refined_results = []
    scoring_results = []

    for demand in demand_list:
        refined = refiner.refine_demand(demand, demand.get('id'))
        refined_results.append(refined)

        scored = scorer.score_demand(
            demand,
            strategy_focus=strategy_focus
        )
        scoring_results.append(scored)

    scored_demands = []
    for result in scoring_results:
        scored_demands.append({
            'id': result['id'],
            'description': result['description'],
            'scoring_prompt': result['scoring_prompt'],
            'note': result['note']
        })

    submission_package = generate_submission_package(
        scored_demands,
        dept_submitter,
        is_trial_period,
        strategy_focus
    )

    notice_text = generate_governance_notice(
        dept_submitter,
        is_trial_period,
        scored_demands
    )

    formatted_report = format_report(submission_package)

    return {
        '补全结果': refined_results,
        '评分结果': scoring_results,
        '标准化提报材料': submission_package,
        '部门宣导文案': notice_text,
        '格式化报告': formatted_report
    }


if __name__ == '__main__':
    test_demands = [
        {
            'id': 'D001',
            'description': '磐石系统侵权库重构+自动化侵权素材生成+新人风控培训',
            'background': '现有侵权库不完善，采集上传流程复杂',
            'pain_points': '效率低，一个一个上传查看；新人缺乏风控培训',
            'expected_value': '采集效率提升3倍，侵权警告降至0',
        }
    ]

    result = execute(
        test_demands,
        dept_submitter='研发部-小夏',
        is_trial_period=True,
        strategy_focus=['合规风控']
    )

    print("=== 评分提示词（前500字）===")
    print(result['评分结果'][0]['scoring_prompt'][:500])
