# 研发需求智能治理技能

自动化需求评审：自然语言输入 → 补全优化 → PM框架分析 → 评分定级 → 材料生成。支持自学习。

## 工作流

```
用户输入 → 读取校准规则 → 补全优化(5W1H/User Story/JTBD/PR-FAQ/SMART)
→ PM框架分析(RICE/JTBD/OST/Working Backwards/OKR/North Star/Chasm/Tech Debt)
→ 6维度评分 → 定级(A/B/C/D) → 输出报告 → 反馈自学习
```

## 使用示例

```
你：帮我评估，做个亚马逊侵权专利库自动化采集脚本，手动太慢还容易漏，已经两次侵权警告了

AI：[补全] → [PM框架分析] → 85分 A级战略型 → 独立立项评审
```

## 评分机制

| 维度 | 权重 | PM框架 |
|------|------|--------|
| 业务价值 | 25 | RICE Impact + JTBD + North Star + Working Backwards |
| 战略匹配度 | 20 | OKR + OST |
| 影响范围 | 15 | RICE Reach + Crossing the Chasm |
| 投入产出比 | 15 | RICE Effort & Confidence |
| 紧急程度 | 15 | Time-Sensitive Opportunity |
| 实施复杂度 | 10(反向) | Technical Debt |

| 等级 | 分数 | 类型 | 决策 |
|------|------|------|------|
| A | ≥80 | 战略型 | 独立立项 |
| B | 60-79 | 经营优化型 | 纳入评审 |
| C | 40-59 | 日常改进型 | 轻量处理 |
| D | <40 | 无效型 | 驳回 |

## 项目结构

```
├── rules/
│   ├── demand_scoring_rules.yaml   # 评分规则（含PM框架引用）
│   ├── demand_refinement.yaml      # 补全优化规则
│   ├── calibration.yaml            # 校准规则（自学习产出）
│   └── feedback_history.json       # 反馈历史
├── references/
│   ├── pm_frameworks.md            # PM框架评分决策参考
│   └── demand_refinement_guide.md  # 补全方法论与示例
├── scripts/
│   ├── demand_scorer.py            # 评分提示词构建器
│   ├── demand_refiner.py           # 补全提示词构建器
│   ├── document_generator.py       # 提报材料生成
│   ├── notice_generator.py         # 宣导文案生成
│   ├── radar_chart.py              # 雷达图可视化
│   └── version_manager.py          # 规则版本控制
├── SKILL.md
├── LICENSE
└── README.md
```

## 版本

- v6.0 (精简优化版) | 2026-05-14 | MIT
