# 研发需求智能治理技能

自动化需求评审：自然语言输入 → 去重检查 → 补全优化 → PM框架分析 → 评分定级 → AI建议 → 入库管理。支持自学习和公司知识记忆。

## 工作流

```
用户输入 → 读取上下文 → 去重检查 → 补全优化(5W1H/User Story/JTBD/PR-FAQ/SMART)
→ PM框架分析(RICE/JTBD/OST/Working Backwards/OKR/North Star/Chasm/Tech Debt)
→ 6维度评分 → 结构化评分理由(判断依据+扣分原因) → AI建议(8维度)
→ 定级(A/B/C/D) → 自动映射(标签/优先级/需求类型) → 入库 → 反馈自学习
```

## 核心功能

- **需求补全**：5W1H → User Story → JTBD → PR-FAQ → SMART，自动补全为结构化文档
- **去重检查**：关键词重叠≥60%自动提示相似需求
- **PM框架评分**：8大PM框架交叉验证，6维度100分制
- **结构化评分理由**：每个维度拆分为"判断依据+扣分原因"
- **AI建议**：8维度开发人员视角优化建议
- **自动映射**：评分→等级→标签→优先级→需求类型，一键推导
- **需求库管理**：自动编号、状态流转（带校验）、变更历史、模糊搜索
- **公司知识记忆**：自动学习公司系统/部门/数据源/业务规则
- **自学习校准**：用户纠正→提取校准规则→下次评分自动应用
- **提报材料生成**：A/B/C级差异化立项/评审/处理材料
- **雷达图可视化**：6维度评分雷达图+对比图

## 评分机制

| 维度 | 权重 | PM框架 |
|------|------|--------|
| 业务价值 | 25 | RICE Impact + JTBD + North Star + Working Backwards |
| 战略匹配度 | 20 | OKR + OST |
| 影响范围 | 15 | RICE Reach + Crossing the Chasm + Impact Depth |
| 投入产出比 | 15 | RICE Effort & Confidence |
| 紧急程度 | 15 | Time-Sensitive Opportunity |
| 实施复杂度 | 10(反向) | Technical Debt |

| 等级 | 分数 | 标签 | 优先级 | 类型 | 决策 |
|------|------|------|--------|------|------|
| A | ≥80 | 战略 | P0 | 价值需求 | 独立立项 |
| B | 60-79 | 经营 | P1 | 价值需求 | 纳入评审 |
| C | 40-59 | 日常 | P2 | 普通需求 | 轻量处理 |
| D | <40 | 无效型 | P3 | 普通需求 | 驳回 |

## 使用示例

```
你：帮我评估，做个亚马逊侵权专利库自动化采集脚本，手动太慢还容易漏，已经两次侵权警告了

AI：[去重检查] → [补全] → [PM框架分析] → 85分 A级战略型 → [AI建议8维度] → 确认入库？
```

## 项目结构

```
├── rules/
│   ├── demand_scoring_rules.yaml   # 评分规则（含PM框架+定级+去重+状态+公司知识规则）
│   ├── demand_refinement.yaml      # 补全优化规则（含AI建议生成规则）
│   ├── calibration.yaml            # 校准规则（自学习产出）
│   ├── company_context.yaml        # 公司知识记忆
│   ├── demand_library.json         # 需求库数据
│   └── feedback_history.json       # 反馈历史
├── references/
│   ├── pm_frameworks.md            # PM框架评分决策参考
│   └── demand_refinement_guide.md  # 补全方法论与示例
├── scripts/
│   ├── demand_scorer.py            # 评分引擎v7（结构化理由+AI建议+公司知识）
│   ├── demand_refiner.py           # 补全引擎v3（对齐标准字段）
│   ├── demand_library.py           # 需求库v4（去重+变更历史+状态校验）
│   ├── document_generator.py       # 提报材料生成v2（对齐标准字段）
│   ├── notice_generator.py         # 宣导文案生成
│   ├── radar_chart.py              # 雷达图可视化v2（修复SVG数学）
│   ├── version_manager.py          # 规则版本控制
│   └── governance.py               # 治理主入口v2
├── SKILL.md
├── LICENSE
└── README.md
```

## 版本

- v10.0 (全面审查修复版) | 2026-05-14 | MIT
