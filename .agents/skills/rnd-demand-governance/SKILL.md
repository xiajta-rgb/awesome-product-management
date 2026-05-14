---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动将用户原始需求描述补全为结构化专业文档（基于5W1H/User Story/JTBD/PR-FAQ/SMART），按标准字段输出（需求类型/需求模块/标题/背景/业务痛点/需求描述/标签/优先级），再依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）和RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star等专业PM框架进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。支持需求库管理（自动记录/查询/状态更新）。具备自学习能力，可根据用户纠正自动校准评分策略。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项、需求补全、需求库、查询需求 or wants to automatically score, classify, or generate submission materials for R&D demands.
---

# 研发需求智能治理技能

用户用自然语言描述需求，AI 自动补全→分析→评分→定级→入库→生成材料。支持自学习。

## 标准录入字段

每个需求最终录入以下字段：

| 字段 | 说明 | 可选值 |
|------|------|--------|
| **需求类型** | 普通需求 / 价值需求 | `普通需求`、`价值需求` |
| **需求模块** | 所属业务域 | `仓储与物流域`、`研发域`、`供应链与制造域`、`营销域` |
| **标题** | 一句话简单描述需求核心内容 | 不限 |
| **背景** | 问题背景与现状说明 | 不限 |
| **业务痛点** | 描述当前业务的痛点 | 不限 |
| **需求描述** | 需求点补充描述更具体详细 | 不限 |
| **标签** | 需求类型标签（与定级对应） | `战略`、`经营`、`日常`、`无效型` |
| **优先级** | 需求优先级 | `P0`、`P1`、`P2`、`P3` |

优先级与等级/标签对应关系：
- P0 ← A级战略型（标签：战略）— 紧急致命，立即处理
- P1 ← B级经营优化型（标签：经营）— 重要高优，本周处理
- P2 ← C级日常改进型（标签：日常）— 中等优先，迭代内处理
- P3 ← D级无效型（标签：无效型）— 低优先级，排期处理

## 执行流程

### Step 0. 识别用户意图

根据用户输入识别意图，执行对应流程：

| 指令关键词 | 执行动作 |
|-----------|----------|
| 查询需求/查看需求/需求列表/所有需求 | 查询需求库 |
| 搜索xxx/查找xxx | 按关键词搜索需求库 |
| 需求统计/统计 | 显示需求库统计 |
| 查看D001/详情D001 | 显示指定需求完整信息 |
| 其他（新需求描述） | 走完整评审流程→入库 |

### Step 1. 读取校准规则

读取 [rules/calibration.yaml](rules/calibration.yaml)，获取从历史反馈中提取的校准规则。评分时若需求文本匹配 trigger，按校准规则调整。

### Step 2. 需求补全与标准化

将用户原始描述补全为标准录入字段。读取 [rules/demand_refinement.yaml](rules/demand_refinement.yaml) 获取字段定义和质量检查标准。

**补全方法论**（按顺序应用）：

1. **5W1H** — 确保覆盖 Who/What/When/Where/Why/How
2. **User Story** — 生成 `As a... I want... so that...` 标准格式
3. **JTBD** — 识别核心Job vs 边缘Job，用于判断需求类型和标签
4. **PR-FAQ** — 从客户视角验证需求真实性
5. **SMART** — 预期价值必须具体、可量化、有时限

**补全质量自检**（6项必须）：标题、背景、业务痛点、需求描述、需求类型、需求模块、标签、优先级 — 缺失≥3项则暂停评分并追问用户。

**补全不合格处理**：输出格式
```
⚠️ 需求信息不足，无法进行专业评审。请补充以下关键信息：
1. {缺失字段}：{引导问题}
补充后我将重新进行补全和评审。
```

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
JTBD → Working Backwards → North Star → OKR → OST → RICE → Crossing the Chasm → Impact Depth → Technical Debt

**定级与映射**：
| 总分 | 等级 | 标签 | 优先级 | 决策 |
|------|------|------|--------|------|
| ≥80 | A级 | 战略 | P0 | 独立立项评审 |
| 60-79 | B级 | 经营 | P1 | 纳入评审流程 |
| 40-59 | C级 | 日常 | P2 | 轻量快速处理 |
| <40 | D级 | 无效型 | P3 | 驳回并说明原因 |

### Step 4. 输出评审结果

```
📝 需求补全与标准化
- 需求类型：{demand_type}
- 需求模块：{demand_module}
- 标题：{title}
- 背景：{background}
- 业务痛点：{pain_points}
- 需求描述：{description}
- 标签：{label}
- 优先级：{priority}

📊 评审结果：{total_score}分 {grade}级

📋 维度评分：
  业务价值 {score}/25 — {reason}
  战略匹配度 {score}/20 — {reason}
  影响范围 {score}/15 — {reason}
  投入产出比 {score}/15 — {reason}
  紧急程度 {score}/15 — {reason}
  实施复杂度 {score}/10 — {reason}

💡 决策：{decision}
```

### Step 5. 需求入库

**每次评审完成后，自动向用户确认是否入库**：

```
是否将此需求录入需求库？
- 编号：D{next_id:03d}
- 标题：{title}
- 标签：{label} | 优先级：{priority} | 评分：{total_score}分 {grade}级

回复"是"或"确认"即可入库。
```

用户确认后，将需求记录到 [rules/demand_library.json](rules/demand_library.json)。自动标注编号和加入时间。

**需求状态流转**：`待评审` → `已评审` → `已立项` / `已驳回` / `已暂缓`

### Step 6. 需求库查询

| 指令 | 输出 |
|------|------|
| `查询需求` / `需求列表` / `所有需求` | `D001  标题`（仅显示编号+标题） |
| `搜索关键词` | 模糊匹配标题/描述/背景 |
| `需求统计` | 总数 + 各标签数量 + 各优先级数量 + 各模块数量 |
| `查看D001` / `详情D001` | 显示完整字段信息 |

查询输出格式：
```
📋 需求库（共X条）
D001  标题1
D002  标题2
...
```

### Step 7. 用户反馈与自学习

评分后主动询问用户是否认可。如有纠正，记录到 [rules/feedback_history.json](rules/feedback_history.json)，提取校准规则写入 [rules/calibration.yaml](rules/calibration.yaml)。

### Step 8. 批量处理与材料生成

- 批量需求：逐一补全→评分→按A>B>C>D排序→汇总→逐一确认入库
- 材料生成：参考 [scripts/document_generator.py](scripts/document_generator.py)、[scripts/notice_generator.py](scripts/notice_generator.py)

## 关键约束

1. 评分严格基于 demand_scoring_rules.yaml，校准规则优先于基础规则
2. 补全必做，PM框架分析必做
3. 补全输出必须匹配8个标准字段
4. 标签和优先级必须与评分等级对应
5. 每次评审后必须询问用户是否入库
6. 查询需求时只显示编号+标题
7. 学习并记忆用户提到的公司信息（系统名、部门、人员等），用于后续需求补全
