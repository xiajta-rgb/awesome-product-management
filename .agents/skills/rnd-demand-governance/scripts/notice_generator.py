"""
研发部需求提报规则宣导文案生成器
根据阶段和评分结果自动生成适配的宣导文案
"""

from datetime import datetime


def generate_governance_notice(
    dept_submitter: str,
    is_trial_period: bool,
    scored_demands: list = None
) -> str:
    """
    生成部门宣导文案
    
    Args:
        dept_submitter: 研发部需求对接人姓名
        is_trial_period: 是否为试用期
        scored_demands: 评分结果列表（可选，用于生成具体数据引用）
        
    Returns:
        宣导文案字符串
    """
    now = datetime.now()
    
    # 根据阶段生成不同文案
    if is_trial_period:
        notice = _generate_trial_notice(dept_submitter, scored_demands)
    else:
        notice = _generate_formal_notice(dept_submitter, scored_demands)
    
    return notice


def _generate_trial_notice(dept_submitter: str, scored_demands: list = None) -> str:
    """生成试用期宣导文案"""
    notice = f"""📢【研发部需求提报通知 - 试用期】

各位小伙伴好！

我是研发部需求对接人 {dept_submitter}。为提升需求评审效率和质量，公司已启用智能需求评审机制。现将相关规则宣导如下：

📋 提报规则
✅ 所有需求由我汇总后，系统将按评分规则自动定级
✅ 评分维度：业务价值(25分)、战略匹配度(20分)、影响范围(15分)、投入产出比(15分)、紧急程度(15分)、实施复杂度(10分)
✅ 总分≥80分为A级（战略型），60-79分为B级（经营优化型），40-59分为C级（日常改进型），<40分为D级（驳回）

⚡ 优先级规则
A级（战略型需求）> B级（经营优化型需求）> C级（日常改进型需求）
D级需求将自动驳回并说明原因

📅 时间节点
试用期：即日起至2026年4月30日
正式期：2026年5月1日起，仅支持通过工单系统提报

💡 提报前自查建议
1. 明确业务价值：需求能带来什么收益？提升多少效率？
2. 评估跨部门影响：是否涉及多部门协同？受益范围多大？
3. 对齐战略重点：是否匹配公司当前核心战略方向？
4. 合理估算投入：资源投入与预期收益是否匹配？

❓ 有疑问随时沟通~
"""
    
    # 如果有评分结果，添加本次数据
    if scored_demands:
        stats = _calculate_stats(scored_demands)
        notice += f"\n📊 本次提报数据\n"
        notice += f"本次共收到需求 {stats['total']} 条\n"
        notice += f"- 合规需求：{stats['valid']} 条（A级:{stats['A']}、B级:{stats['B']}、C级:{stats['C']}）\n"
        notice += f"- 无效需求：{stats['invalid']} 条（已驳回）\n"
    
    return notice


def _generate_formal_notice(dept_submitter: str, scored_demands: list = None) -> str:
    """生成正式期宣导文案"""
    notice = f"""📢【研发部需求提报通知 - 正式期】

各位同事：

我是研发部需求对接人 {dept_submitter}。根据公司研发管理规范，自2026年5月1日起，所有需求提报统一通过工单系统进行。

📋 提报流程
1. 通过工单系统提交需求（必填：需求描述、预期价值、影响范围、资源估算）
2. 系统自动评分定级
3. 按等级进入相应评审流程

⚡ 评分标准
- A级（≥80分）：战略型需求，独立立项评审
- B级（60-79分）：经营优化型需求，纳入评审流程
- C级（40-59分）：日常改进型需求，轻量快速处理
- D级（<40分）：无效/暂不支持型，自动驳回

📌 注意事项
- 请确保需求信息完整，信息不全可能影响评分
- 低价值需求将被自动驳回，请提报前充分评估
- 如有疑问，请联系研发部需求对接人 {dept_submitter}
"""
    
    # 如果有评分结果，添加本次数据
    if scored_demands:
        stats = _calculate_stats(scored_demands)
        notice += f"\n📊 本次提报数据\n"
        notice += f"本次共处理需求 {stats['total']} 条\n"
        notice += f"- 合规需求：{stats['valid']} 条\n"
        notice += f"- 无效需求：{stats['invalid']} 条\n"
    
    return notice


def _calculate_stats(scored_demands: list) -> dict:
    """计算评分统计信息"""
    return {
        'total': len(scored_demands),
        'A': len([d for d in scored_demands if d['grade'] == 'A']),
        'B': len([d for d in scored_demands if d['grade'] == 'B']),
        'C': len([d for d in scored_demands if d['grade'] == 'C']),
        'D': len([d for d in scored_demands if d['grade'] == 'D']),
        'valid': len([d for d in scored_demands if d['grade'] != 'D']),
        'invalid': len([d for d in scored_demands if d['grade'] == 'D'])
    }


if __name__ == '__main__':
    # 测试
    notice = generate_governance_notice('研发部-小夏', True)
    print(notice)
