"""
需求智能治理主入口
整合评分、文档生成、宣导文案生成，提供统一执行接口
"""

import os
import sys
from typing import Optional

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from demand_scorer import auto_score_demand
from document_generator import generate_submission_package, format_report
from notice_generator import generate_governance_notice


def execute(
    demand_list: list,
    dept_submitter: str,
    is_trial_period: bool,
    strategy_focus: list = None,
    scoring_rules_path: str = None
) -> dict:
    """
    执行需求智能治理流程
    
    Args:
        demand_list: 研发部原始需求列表
        dept_submitter: 研发部需求对接人姓名
        is_trial_period: 是否为试用期
        strategy_focus: 公司当前战略重点方向
        scoring_rules_path: 评分规则文件路径
        
    Returns:
        完整决策报告
    """
    # 1. 加载评分规则并自动打分
    scoring_result = auto_score_demand(
        demand_list,
        rules_path=scoring_rules_path,
        strategy_focus=strategy_focus
    )
    
    scored_demands = scoring_result['scored_demands']
    stats = scoring_result['stats']
    
    # 2. 区分合规/无效需求
    valid_demands = [d for d in scored_demands if d['grade'] != 'D']
    invalid_demands = [d for d in scored_demands if d['grade'] == 'D']
    reject_reasons = {d['id']: d['reject_reason'] for d in invalid_demands}
    
    # 3. 生成提报材料
    submission_package = generate_submission_package(
        scored_demands,
        dept_submitter,
        is_trial_period,
        strategy_focus
    )
    
    # 4. 生成宣导文案
    notice_text = generate_governance_notice(
        dept_submitter,
        is_trial_period,
        scored_demands
    )
    
    # 5. 生成格式化报告
    formatted_report = format_report(submission_package, invalid_demands)
    
    return {
        '需求智能评分报告': scored_demands,
        '预审总览': f"合规需求{stats['valid']}条（A:{stats['A']}、B:{stats['B']}、C:{stats['C']}），无效需求{stats['invalid']}条",
        '无效需求清单与驳回原因': reject_reasons,
        '合规需求优先级排序': [
            {'id': d['id'], 'grade': d['grade'], 'type': d['demand_type'], 'score': d['total_score']}
            for d in valid_demands
        ],
        '标准化提报材料': submission_package,
        '部门宣导文案': notice_text,
        '格式化报告': formatted_report,
        '评分统计': stats,
        '评分时间': scoring_result['scoring_time']
    }


if __name__ == '__main__':
    # 测试示例
    test_demands = [
        {
            'id': 'D001',
            'description': '跨部门订单数据同步系统开发',
            'submitter': '研发-张三',
            'usage_scenario': '供应链、销售、财务跨部门数据协同',
            'expected_value': '减少数据重复录入，提升30%对账效率，降低5%财务差错率',
            'cross_department_impact': '供应链、销售、财务3个部门',
            'resource_input': '2人月开发资源',
            'deadline_risk': '无刚性时间节点，为年度战略重点项目'
        },
        {
            'id': 'D002',
            'description': '个人操作界面按钮位置调整',
            'submitter': '研发-李四',
            'usage_scenario': '仅个人操作习惯优化',
            'expected_value': '无业务效率提升',
            'cross_department_impact': '无跨部门影响',
            'resource_input': '0.5人天资源',
            'deadline_risk': '无紧急性'
        }
    ]
    
    result = execute(
        test_demands,
        dept_submitter='研发部-小夏',
        is_trial_period=True,
        strategy_focus=['跨部门数据协同', '运营效率提升']
    )
    
    print(result['预审总览'])
    print(result['部门宣导文案'])
