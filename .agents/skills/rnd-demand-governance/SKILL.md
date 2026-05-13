---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）对需求进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项 or wants to automatically score, classify, or generate submission materials for R&D demands.
compatibility: Requires Python 3.7+ with PyYAML library
---

# 研发需求智能治理技能

专为研发部打造的自动化需求评审与治理工具，基于公司《需求评审评分规则》，实现「需求输入→自动打分→定级分类→智能决策→材料生成」的全流程自动化。

## 何时使用此技能

Load this skill when:
- 研发部收集到原始需求，需要按公司规则自动完成评分定级
- 需快速区分战略型/经营优化型/日常改进型/无效需求
- 需依据评分结果生成优先级排序，辅助跨部门沟通排期
- 需批量处理需求，自动过滤低质/无效需求
- 需根据评分结果生成标准化提报材料与部门宣导文案
- 用户提到需求评审、需求打分、需求优先级、需求提报等关键词

## 评分机制

### 六大维度（总分100分）

| 维度 | 权重 | 说明 |
|------|------|------|
| 业务价值 | 25分 | 收入提升/降本增效/核心业务贡献 |
| 战略匹配度 | 20分 | 与公司当前战略重点的契合度 |
| 影响范围 | 15分 | 跨部门/多岗位受益的复用价值 |
| 投入产出比 | 15分 | ROI评估，避免资源浪费 |
| 紧急程度 | 15分 | 合规/风险/客户影响类高紧急需求 |
| 实施复杂度 | 10分 | 反向计分，技术难度越低得分越高 |

### 四级判定规则

| 总分区间 | 等级 | 需求类型 | 决策动作 |
|----------|------|----------|----------|
| ≥80分 | A级 | 战略型需求 | 独立立项评审 |
| 60-79分 | B级 | 经营优化型需求 | 纳入评审流程，按价值排序 |
| 40-59分 | C级 | 日常改进型需求 | 轻量快速处理 |
| <40分 | D级 | 无效/暂不支持型 | 驳回/暂缓，说明原因 |

详细评分维度说明见 [references/scoring_dimensions.md](file:///workspace/.agents/skills/rnd-demand-governance/references/scoring_dimensions.md)

## 执行步骤

### 1. 收集需求信息

从用户处获取以下信息：
- **demand_list**: 需求列表，每个需求需包含：
  - `id`: 需求编号
  - `description`: 需求描述
  - `submitter`: 提交人
  - `usage_scenario`: 使用场景
  - `expected_value`: 预期价值
  - `cross_department_impact`: 跨部门影响
  - `resource_input`: 资源投入估算
  - `deadline_risk`: 截止风险/紧急性
- **dept_submitter**: 研发部需求对接人姓名
- **is_trial_period**: 是否为试用期（2026.4.30前为True，5.1后为False）
- **strategy_focus** (可选): 公司当前战略重点方向列表

### 2. 执行评分与治理

使用内置脚本执行完整治理流程：

```bash
cd /workspace/.agents/skills/rnd-demand-governance
python -m scripts.governance
```

或在 Python 中调用：

```python
from scripts.governance import execute

result = execute(
    demand_list=[...],           # 需求列表
    dept_submitter='姓名',       # 对接人
    is_trial_period=True,        # 是否试用期
    strategy_focus=['方向1', ...]  # 战略重点（可选）
)
```

### 3. 输出结果

返回完整的决策报告，包含：
- **需求智能评分报告**: 每个需求的详细评分（各维度得分+总分）、等级、类型、决策动作
- **预审总览**: 合规/无效需求数量统计
- **无效需求清单与驳回原因**: D级需求列表及具体驳回原因
- **合规需求优先级排序**: 按A>B>C排序的合规需求
- **标准化提报材料**: 可直接提交的评审材料
- **部门宣导文案**: 适配当前阶段的宣导通知
- **格式化报告**: 可读性强的完整文本报告

## 输入示例

```python
{
    "demand_list": [
        {
            "id": "D001",
            "description": "跨部门订单数据同步系统开发",
            "submitter": "研发-张三",
            "usage_scenario": "供应链、销售、财务跨部门数据协同",
            "expected_value": "减少数据重复录入，提升30%对账效率，降低5%财务差错率",
            "cross_department_impact": "供应链、销售、财务3个部门",
            "resource_input": "2人月开发资源",
            "deadline_risk": "无刚性时间节点，为年度战略重点项目"
        }
    ],
    "dept_submitter": "研发部-小夏",
    "is_trial_period": True,
    "strategy_focus": ["跨部门数据协同", "运营效率提升"]
}
```

## 输出示例

```python
{
    "需求智能评分报告": [
        {
            "id": "D001",
            "total_score": 88,
            "grade": "A",
            "demand_type": "战略型需求",
            "decision_action": "独立立项评审",
            "dimension_scores": {
                "业务价值": 23,
                "战略匹配度": 19,
                "影响范围": 14,
                "投入产出比": 14,
                "紧急程度": 10,
                "实施复杂度": 8
            }
        }
    ],
    "预审总览": "合规需求1条（A:1），无效需求0条",
    "部门宣导文案": "📢【研发部需求提报通知 - 试用期】..."
}
```

## 评分规则文件

核心评分规则存储于 [rules/demand_scoring_rules.yaml](file:///workspace/.agents/skills/rnd-demand-governance/rules/demand_scoring_rules.yaml)，包含：
- 分级判定规则
- 各维度权重与分档条件
- 关键词匹配规则

可通过修改此文件调整评分逻辑，无需修改脚本代码。

## 注意事项

1. **规则可配置**: 修改 `rules/demand_scoring_rules.yaml` 可调整权重、分档条件
2. **自动决策**: 完全基于规则文件执行打分，无人工主观判断，结果透明可解释
3. **评审适配**: 提报材料自动包含各维度评分说明，直接对齐委员会评审标准
4. **数据安全**: 规则文件本地读取，不涉及外部数据交互
5. **依赖安装**: 需要 `PyYAML` 库，如未安装请运行 `pip install pyyaml`

## 脚本说明

- [scripts/governance.py](file:///workspace/.agents/skills/rnd-demand-governance/scripts/governance.py): 主入口，整合评分、文档生成、宣导文案
- [scripts/demand_scorer.py](file:///workspace/.agents/skills/rnd-demand-governance/scripts/demand_scorer.py): 核心评分引擎
- [scripts/document_generator.py](file:///workspace/.agents/skills/rnd-demand-governance/scripts/document_generator.py): 提报材料生成
- [scripts/notice_generator.py](file:///workspace/.agents/skills/rnd-demand-governance/scripts/notice_generator.py): 宣导文案生成
