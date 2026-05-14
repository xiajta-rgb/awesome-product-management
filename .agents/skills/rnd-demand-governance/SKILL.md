---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动将用户原始需求描述补全为结构化专业文档（基于5W1H/User Story/JTBD/PR-FAQ/SMART），再依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）和RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star等专业PM框架进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。支持需求库管理（自动记录/查询/状态更新）。具备自学习能力，可根据用户纠正自动校准评分策略。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项、需求补全、需求库、查询需求 or wants to automatically score, classify, or generate submission materials for R&D demands.
---

# 研发需求智能治理技能

用户用自然语言描述需求，AI 自动补全→分析→评分→定级→入库→生成材料。支持自学习。

## 执行流程

### Step 0. 识别用户意图

根据用户输入识别意图，执行对应流程：

| 指令关键词 | 执行动作 |
|-----------|----------|
| 查询需求/查看需求/需求列表/所有需求 | 查询需求库 |
| 搜索xxx/查找xxx | 按关键词搜索需求库 |
| 需求统计/统计 | 显示需求库统计 |
| 其他（新需求描述） | 走完整评审流程→入库 |

### Step 1. 读取校准规则

读取 [rules/calibration.yaml](rules/calibration.yaml)，获取从历史反馈中提取的校准规则。评分时若需求文本匹配 trigger，按校准规则调整。

### Step 2. 需求补全与结构化

将用户原始描述补全为结构化需求文档。读取 [rules/demand_refinement.yaml](rules/demand_refinement.yaml) 获取字段定义和质量检查标准。

**补全方法论**（按顺序应用，详见 [references/demand_refinement_guide.md](references/demand_refinement_guide.md)）：

1. **5W1H** — 确保覆盖 Who/What/When/Where/Why/How
2. **User Story** — 生成 `As a... I want... so that...` 标准格式
3. **JTBD** — 识别核心Job vs 边缘Job，评估当前满意度（此分析结果直接复用于Step 3的PM框架分析，不重复执行）
4. **PR-FAQ** — 从客户视角验证需求真实性
5. **SMART** — 预期价值必须具体、可量化、有时限

**补全输出字段**：demand_name, demand_category, background, pain_points, target_users, usage_scenario, user_story, expected_value, cross_department_impact, resource_input, deadline_risk, success_metrics, risks_assumptions

**信息置信度标记**（必须）：
- `confirmed` — 用户明确提供
- `inferred` — AI合理推测
- `assumed` — AI假设，需用户确认

**质量自检**：background、pain_points、target_users、expected_value、usage_scenario 为必须字段。

**补全不合格处理**：当必须字段≥3个缺失（即用户原始描述信息严重不足），AI应暂停评分，主动追问用户补充关键信息，输出格式：
```
⚠️ 需求信息不足，无法进行专业评审。请补充以下关键信息：
1. {缺失字段1}：{引导问题}
2. {缺失字段2}：{引导问题}
...
补充后我将重新进行补全和评审。
```
当必须字段1-2个缺失时，AI可合理推测补全，但必须标记为 `assumed` 并在评审结果中提醒用户确认。

### Step 3. PM框架分析与评分

使用补全后的需求，结合PM框架进行深度分析并评分。读取 [rules/demand_scoring_rules.yaml](rules/demand_scoring_rules.yaml) 获取完整评分规则。

**评分维度**（总分100）：

| 维度 | 权重 | PM框架支撑 |
|------|------|-----------|
| 业务价值 | 25 | RICE Impact + JTBD + North Star + Working Backwards |
| 战略匹配度 | 20 | OKR Alignment + OST |
| 影响范围 | 15 | RICE Reach + Crossing the Chasm + Impact Depth Check |
| 投入产出比 | 15 | RICE Effort & Confidence |
| 紧急程度 | 15 | Time-Sensitive Opportunity |
| 实施复杂度 | 10(反向) | Technical Debt Assessment |

**PM框架分析要点**（详见 [references/pm_frameworks.md](references/pm_frameworks.md)）：

- **JTBD**: 核心Job还是边缘Job？（复用Step 2的分析结论）
- **Working Backwards**: 有客户需求证据还是纯属假设？
- **North Star**: 直接/间接/无关？
- **OKR**: 公司级/部门级/团队级/无对齐？
- **OST**: 主干/分支/脱离？
- **RICE**: 量化 Reach×Impact×Confidence/Effort
- **Crossing the Chasm**: 跨越鸿沟/早期采纳者/滞后期？
- **Impact Depth**: 核心业务场景还是辅助场景？
- **Technical Debt**: 减少/不变/增加？

**框架交叉验证**：多框架一致→高置信；矛盾→在评分理由中说明权衡。

**定级**：A≥80(战略型) | B 60-79(经营优化型) | C 40-59(日常改进型) | D<40(无效)

### Step 4. 输出评审结果

```
📊 需求评审：{demand_name} | {total_score}分 {grade}级{grade_type}

📝 补全摘要：{background} → {user_story} → {expected_value}
   置信度：已确认{N}项 / 推测{N}项 / 待确认{N}项

🔍 框架结论：{JTBD结论} | {OKR层级} | {RICE Score} | {NSM关系} | {Tech Debt影响}

📋 维度评分：
  业务价值 {score}/25 — {reason}
  战略匹配度 {score}/20 — {reason}
  影响范围 {score}/15 — {reason}
  投入产出比 {score}/15 — {reason}
  紧急程度 {score}/15 — {reason}
  实施复杂度 {score}/10 — {reason}

💡 决策：{decision}
📐 校准：{applied_calibrations_or_none}
```

### Step 5. 需求入库

**每次评审完成后，自动向用户确认是否入库**：

```
是否将此需求录入需求库？
- 编号：{demand_id}
- 名称：{demand_name}
- 评分：{total_score}分 {grade}级

回复"是"或"确认"即可入库。
```

用户确认后，将需求记录到 [rules/demand_library.json](rules/demand_library.json)，包含：demand_id, demand_name, raw_description, status, grade, total_score, created_at。

**需求状态流转**：`待评审` → `已评审` → `已立项` / `已驳回` / `已暂缓`

### Step 6. 需求库查询

支持以下查询指令：

| 指令 | 输出 |
|------|------|
| `查询需求` / `需求列表` / `所有需求` | 列出全部需求：`D001  亚马逊侵权专利库自动化采集系统` |
| `搜索xxx` | 按关键词模糊匹配需求名称和描述 |
| `需求统计` | 总需求数 + 各等级数量 + 各状态数量 |
| `查看D001` / `详情D001` | 显示指定需求的完整信息 |

查询输出格式：
```
📋 需求库（共X条）
D001  亚马逊侵权专利库自动化采集系统
D002  数据安全合规平台
D003  客服工单智能分配
...
```

### Step 7. 用户反馈与自学习

评分后主动询问用户是否认可。如有纠正：

1. 记录到 [rules/feedback_history.json](rules/feedback_history.json)
2. 提取校准规则写入 [rules/calibration.yaml](rules/calibration.yaml)
3. 下次评分自动应用

校准规则类型：`force_score`（强制分数）、`adjust_score`（调整分数）、`force_grade`（强制等级）

置信度演进：`initial` → `learning`(<10条) → `calibrated`(10-50条,准确率>70%) → `stable`(50+条,准确率>85%)

### Step 8. 批量处理与材料生成

- 批量需求：逐一补全→评分→按A>B>C>D排序→汇总→逐一确认入库
- 材料生成：参考 [scripts/document_generator.py](scripts/document_generator.py)、[scripts/notice_generator.py](scripts/notice_generator.py)

## 关键约束

1. 评分严格基于 demand_scoring_rules.yaml，校准规则优先于基础规则
2. 补全必做，PM框架分析必做，两者缺一不可
3. JTBD分析在Step 2执行一次，Step 3复用结论，不重复分析
4. 补全信息必须标记confirmed/inferred/assumed
5. 每个维度评分理由必须包含PM框架依据
6. 不编造数据：inferred和assumed内容必须合理
7. 每次评审后必须询问用户是否入库，用户确认后自动记录
8. 查询需求时只显示编号+名称，保持简洁
