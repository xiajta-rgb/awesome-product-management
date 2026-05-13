"""
需求提报材料生成器
根据评分结果生成标准化的提报材料
"""

from datetime import datetime
from typing import Optional


def generate_submission_package(
    scored_demands: list,
    dept_submitter: str,
    is_trial_period: bool,
    strategy_focus: list = None
) -> dict:
    """
    生成标准化提报材料
    
    Args:
        scored_demands: 已评分的需求列表（已排序）
        dept_submitter: 研发部需求对接人
        is_trial_period: 是否为试用期
        strategy_focus: 公司战略重点
        
    Returns:
        提报材料字典
    """
    now = datetime.now()
    
    # 分离不同等级的需求
    a_demands = [d for d in scored_demands if d['grade'] == 'A']
    b_demands = [d for d in scored_demands if d['grade'] == 'B']
    c_demands = [d for d in scored_demands if d['grade'] == 'C']
    
    # 生成提报总览
    overview = _generate_overview(scored_demands, dept_submitter, is_trial_period)
    
    # 生成A级需求立项材料
    a_materials = []
    for demand in a_demands:
        material = _generate_a_grade_material(demand, strategy_focus)
        a_materials.append(material)
    
    # 生成B级需求评审材料
    b_materials = []
    for demand in b_demands:
        material = _generate_b_grade_material(demand)
        b_materials.append(material)
    
    # 生成C级需求快速处理清单
    c_materials = []
    for demand in c_demands:
        material = _generate_c_grade_material(demand)
        c_materials.append(material)
    
    return {
        '提报总览': overview,
        'A级战略型需求立项材料': a_materials,
        'B级经营优化型需求评审材料': b_materials,
        'C级日常改进型需求快速清单': c_materials,
        '提报日期': now.strftime('%Y-%m-%d'),
        '提报人': dept_submitter,
        '阶段标识': '试用期' if is_trial_period else '正式期'
    }


def _generate_overview(scored_demands: list, dept_submitter: str, is_trial_period: bool) -> str:
    """生成提报总览文本"""
    total = len(scored_demands)
    valid = len([d for d in scored_demands if d['grade'] != 'D'])
    a_count = len([d for d in scored_demands if d['grade'] == 'A'])
    b_count = len([d for d in scored_demands if d['grade'] == 'B'])
    c_count = len([d for d in scored_demands if d['grade'] == 'C'])
    
    stage = '试用期（即日起至2026年4月30日）' if is_trial_period else '正式期（2026年5月1日起）'
    
    overview = f"""研发部需求提报总览
{'='*50}
提报部门：研发部
提报对接人：{dept_submitter}
提报阶段：{stage}
提报时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

需求统计：
- 有效需求总数：{valid}条
  - A级（战略型）：{a_count}条
  - B级（经营优化型）：{b_count}条
  - C级（日常改进型）：{c_count}条

评分标准说明：
本批需求依据公司《需求评审评分规则》进行自动评分，评分维度包括：
1. 业务价值（25分）- 评估需求对收入、效率、核心业务的贡献
2. 战略匹配度（20分）- 评估需求与公司战略重点的契合度
3. 影响范围（15分）- 评估需求的跨部门/跨岗位影响
4. 投入产出比（15分）- 评估资源投入与预期收益的比例
5. 紧急程度（15分）- 评估需求的时间紧迫性
6. 实施复杂度（10分）- 评估技术实现难度和依赖关系（反向计分）

总分≥80分为A级，60-79分为B级，40-59分为C级，<40分为D级（已过滤）
"""
    return overview


def _generate_a_grade_material(demand: dict, strategy_focus: list = None) -> dict:
    """生成A级需求立项材料"""
    material = {
        '需求ID': demand['id'],
        '需求名称': demand['description'],
        '等级': f"A级 - {demand['demand_type']}",
        '优先级': demand['priority'],
        '决策动作': demand['decision_action'],
        '总分': demand['total_score'],
        '评分详情': demand['dimension_scores'],
        '立项建议': f"""
【立项建议】
该需求评分为{demand['total_score']}分，达到A级（战略型需求）标准。
建议：
1. 独立立项评审，组建专项小组
2. 优先保障资源投入
3. 制定详细实施计划和时间节点
4. 定期向管理层汇报进展
"""
    }
    
    # 添加战略匹配说明
    if strategy_focus:
        material['战略匹配说明'] = f"该需求与公司当前战略重点方向（{', '.join(strategy_focus)}）高度契合，建议优先推进。"
    
    return material


def _generate_b_grade_material(demand: dict) -> dict:
    """生成B级需求评审材料"""
    material = {
        '需求ID': demand['id'],
        '需求名称': demand['description'],
        '等级': f"B级 - {demand['demand_type']}",
        '优先级': demand['priority'],
        '决策动作': demand['decision_action'],
        '总分': demand['total_score'],
        '评分详情': demand['dimension_scores'],
        '评审建议': f"""
【评审建议】
该需求评分为{demand['total_score']}分，达到B级（经营优化型需求）标准。
建议：
1. 纳入常规评审流程
2. 按价值得分排序后安排资源
3. 可与同类型需求合并处理，提升效率
"""
    }
    return material


def _generate_c_grade_material(demand: dict) -> dict:
    """生成C级需求快速处理清单"""
    material = {
        '需求ID': demand['id'],
        '需求名称': demand['description'],
        '等级': f"C级 - {demand['demand_type']}",
        '优先级': demand['priority'],
        '决策动作': demand['decision_action'],
        '总分': demand['total_score'],
        '处理建议': f"""
【处理建议】
该需求评分为{demand['total_score']}分，达到C级（日常改进型需求）标准。
建议：
1. 走轻量快速处理通道
2. 可利用碎片时间或迭代间隙完成
3. 简化审批流程，快速落地
"""
    }
    return material


def format_report(submission_package: dict, rejected_demands: list = None) -> str:
    """将提报材料格式化为可读报告"""
    report = submission_package['提报总览']
    
    # A级需求
    if submission_package['A级战略型需求立项材料']:
        report += "\n\n" + "="*60 + "\n"
        report += "A级战略型需求立项材料\n"
        report += "="*60 + "\n"
        for mat in submission_package['A级战略型需求立项材料']:
            report += f"\n【{mat['需求ID']}】{mat['需求名称']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']}\n"
            report += mat['立项建议']
    
    # B级需求
    if submission_package['B级经营优化型需求评审材料']:
        report += "\n\n" + "="*60 + "\n"
        report += "B级经营优化型需求评审材料\n"
        report += "="*60 + "\n"
        for mat in submission_package['B级经营优化型需求评审材料']:
            report += f"\n【{mat['需求ID']}】{mat['需求名称']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']}\n"
            report += mat['评审建议']
    
    # C级需求
    if submission_package['C级日常改进型需求快速清单']:
        report += "\n\n" + "="*60 + "\n"
        report += "C级日常改进型需求快速清单\n"
        report += "="*60 + "\n"
        for mat in submission_package['C级日常改进型需求快速清单']:
            report += f"\n【{mat['需求ID']}】{mat['需求名称']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']}\n"
            report += mat['处理建议']
    
    # 驳回需求
    if rejected_demands:
        report += "\n\n" + "="*60 + "\n"
        report += "D级无效/暂不支持需求清单\n"
        report += "="*60 + "\n"
        for d in rejected_demands:
            report += f"\n【{d['id']}】{d.get('description', '')}\n"
            report += f"评分：{d['total_score']}分 | 等级：{d['grade']}\n"
            report += f"驳回原因：{d['reject_reason']}\n"
    
    return report


if __name__ == '__main__':
    # 测试
    test_demands = [
        {
            'id': 'D001',
            'description': '跨部门订单数据同步系统开发',
            'submitter': '研发-张三',
            'total_score': 88,
            'grade': 'A',
            'demand_type': '战略型需求',
            'decision_action': '独立立项评审',
            'priority': '高优先级',
            'dimension_scores': {
                '业务价值': 23,
                '战略匹配度': 19,
                '影响范围': 14,
                '投入产出比': 14,
                '紧急程度': 10,
                '实施复杂度': 8
            }
        }
    ]
    
    package = generate_submission_package(test_demands, '研发部-小夏', True, ['跨部门数据协同'])
    report = format_report(package)
    print(report)
