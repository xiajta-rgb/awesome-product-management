"""
需求提报材料生成器 v2
对齐标准录入字段：title/background/pain_points/description/demand_module/label/priority/ai_suggestions
"""

from datetime import datetime


def generate_submission_package(
    scored_demands: list,
    dept_submitter: str,
    is_trial_period: bool,
    strategy_focus: list = None
) -> dict:
    now = datetime.now()

    a_demands = [d for d in scored_demands if d.get('grade') == 'A']
    b_demands = [d for d in scored_demands if d.get('grade') == 'B']
    c_demands = [d for d in scored_demands if d.get('grade') == 'C']

    overview = _generate_overview(scored_demands, dept_submitter, is_trial_period)

    a_materials = [_generate_a_grade_material(d, strategy_focus) for d in a_demands]
    b_materials = [_generate_b_grade_material(d) for d in b_demands]
    c_materials = [_generate_c_grade_material(d) for d in c_demands]

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
    total = len(scored_demands)
    valid = len([d for d in scored_demands if d.get('grade') != 'D'])
    a_count = len([d for d in scored_demands if d.get('grade') == 'A'])
    b_count = len([d for d in scored_demands if d.get('grade') == 'B'])
    c_count = len([d for d in scored_demands if d.get('grade') == 'C'])

    return f"""研发部需求提报总览
{'='*50}
提报部门：研发部
提报对接人：{dept_submitter}
提报阶段：{'试用期' if is_trial_period else '正式期'}
提报时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

需求统计：
- 有效需求总数：{valid}条
  - A级（战略型）：{a_count}条
  - B级（经营优化型）：{b_count}条
  - C级（日常改进型）：{c_count}条

评分标准：业务价值(25) + 战略匹配度(20) + 影响范围(15) + 投入产出比(15) + 紧急程度(15) + 实施复杂度(10)
总分≥80=A级 | 60-79=B级 | 40-59=C级 | <40=D级
"""


def _generate_a_grade_material(demand: dict, strategy_focus: list = None) -> dict:
    material = {
        '需求ID': demand.get('id', ''),
        '标题': demand.get('title', demand.get('description', '')),
        '需求模块': demand.get('demand_module', ''),
        '等级': f"A级 - {demand.get('demand_type', '战略型需求')}",
        '标签': demand.get('label', '战略'),
        '优先级': demand.get('priority', 'P0'),
        '总分': demand.get('total_score', 0),
        '评分详情': demand.get('dimension_scores', {}),
        'AI建议': demand.get('ai_suggestions', ''),
        '立项建议': f"""
【立项建议】
该需求评分为{demand.get('total_score', 0)}分，达到A级（战略型需求）标准。
建议：
1. 独立立项评审，组建专项小组
2. 优先保障资源投入
3. 制定详细实施计划和时间节点
4. 定期向管理层汇报进展
"""
    }

    if strategy_focus:
        material['战略匹配说明'] = f"该需求与公司当前战略重点方向（{', '.join(strategy_focus)}）高度契合，建议优先推进。"

    return material


def _generate_b_grade_material(demand: dict) -> dict:
    return {
        '需求ID': demand.get('id', ''),
        '标题': demand.get('title', demand.get('description', '')),
        '需求模块': demand.get('demand_module', ''),
        '等级': f"B级 - {demand.get('demand_type', '经营优化型需求')}",
        '标签': demand.get('label', '经营'),
        '优先级': demand.get('priority', 'P1'),
        '总分': demand.get('total_score', 0),
        '评分详情': demand.get('dimension_scores', {}),
        'AI建议': demand.get('ai_suggestions', ''),
        '评审建议': f"""
【评审建议】
该需求评分为{demand.get('total_score', 0)}分，达到B级（经营优化型需求）标准。
建议：
1. 纳入常规评审流程
2. 按价值得分排序后安排资源
3. 可与同类型需求合并处理，提升效率
"""
    }


def _generate_c_grade_material(demand: dict) -> dict:
    return {
        '需求ID': demand.get('id', ''),
        '标题': demand.get('title', demand.get('description', '')),
        '需求模块': demand.get('demand_module', ''),
        '等级': f"C级 - {demand.get('demand_type', '日常改进型需求')}",
        '标签': demand.get('label', '日常'),
        '优先级': demand.get('priority', 'P2'),
        '总分': demand.get('total_score', 0),
        '评分详情': demand.get('dimension_scores', {}),
        'AI建议': demand.get('ai_suggestions', ''),
        '处理建议': f"""
【处理建议】
该需求评分为{demand.get('total_score', 0)}分，达到C级（日常改进型需求）标准。
建议：
1. 走轻量快速处理通道
2. 可利用碎片时间或迭代间隙完成
3. 简化审批流程，快速落地
"""
    }


def format_report(submission_package: dict, rejected_demands: list = None) -> str:
    report = submission_package['提报总览']

    if submission_package['A级战略型需求立项材料']:
        report += "\n\n" + "=" * 60 + "\n"
        report += "A级战略型需求立项材料\n"
        report += "=" * 60 + "\n"
        for mat in submission_package['A级战略型需求立项材料']:
            report += f"\n【{mat['需求ID']}】{mat['标题']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']} | 标签：{mat['标签']} | 优先级：{mat['优先级']}\n"
            report += mat['立项建议']

    if submission_package['B级经营优化型需求评审材料']:
        report += "\n\n" + "=" * 60 + "\n"
        report += "B级经营优化型需求评审材料\n"
        report += "=" * 60 + "\n"
        for mat in submission_package['B级经营优化型需求评审材料']:
            report += f"\n【{mat['需求ID']}】{mat['标题']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']} | 标签：{mat['标签']} | 优先级：{mat['优先级']}\n"
            report += mat['评审建议']

    if submission_package['C级日常改进型需求快速清单']:
        report += "\n\n" + "=" * 60 + "\n"
        report += "C级日常改进型需求快速清单\n"
        report += "=" * 60 + "\n"
        for mat in submission_package['C级日常改进型需求快速清单']:
            report += f"\n【{mat['需求ID']}】{mat['标题']}\n"
            report += f"评分：{mat['总分']}分 | 等级：{mat['等级']} | 标签：{mat['标签']} | 优先级：{mat['优先级']}\n"
            report += mat['处理建议']

    if rejected_demands:
        report += "\n\n" + "=" * 60 + "\n"
        report += "D级无效/暂不支持需求清单\n"
        report += "=" * 60 + "\n"
        for d in rejected_demands:
            report += f"\n【{d.get('id', '')}】{d.get('title', d.get('description', ''))}\n"
            report += f"评分：{d.get('total_score', 0)}分 | 等级：{d.get('grade', '')}\n"
            report += f"驳回原因：{d.get('reject_reason', '')}\n"

    return report


if __name__ == '__main__':
    test_demands = [
        {
            'id': 'D001',
            'title': '磐石系统侵权库重构+自动化侵权素材生成+新人风控培训',
            'demand_module': '营销域',
            'description': '用机器人生成核心对标品牌侵权设计素材，搭建全覆盖侵权库',
            'submitter': '研发-用户',
            'total_score': 85,
            'grade': 'A',
            'demand_type': '价值需求',
            'label': '战略',
            'priority': 'P0',
            'decision_action': '独立立项评审',
            'dimension_scores': {
                '业务价值': 23,
                '战略匹配度': 19,
                '影响范围': 14,
                '投入产出比': 14,
                '紧急程度': 10,
                '实施复杂度': 8
            },
            'ai_suggestions': '①【业务价值】建议补充量化指标'
        }
    ]

    package = generate_submission_package(test_demands, '研发部-小夏', True, ['合规风控'])
    report = format_report(package)
    print(report)
