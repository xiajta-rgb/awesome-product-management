---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动将用户原始需求描述补全为结构化专业文档（基于5W1H/User Story/JTBD/PR-FAQ/SMART），按标准字段输出（需求类型/需求模块/标题/背景/业务痛点/需求描述/标签/优先级/AI建议），再依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）和RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star等专业PM框架进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。支持需求库管理（自动记录/查询/状态更新）。具备自学习能力，可根据用户纠正自动校准评分策略。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项、需求补全、需求库、查询需求 or wants to automatically score, classify, or generate submission materials for R&D demands.
---

# 研发需求智能治理技能

用户用自然语言描述需求，AI 自动补全→分析→评分→定级→建议→入库→生成材料。支持自学习和公司知识记忆。

## 标准录入字段

| 字段 | 说明 | 自动推导 |
|------|------|----------|
| **需求类型** | 普通需求 / 价值需求 | ✅ 评分推导 |
| **需求模块** | 仓储与物流域 / 研发域 / 供应链与制造域 / 营销域 | ❌ AI判断+用户确认 |
| **标题** | 一句话简单描述需求核心内容 | ❌ AI提取 |
| **背景** | 问题背景与现状说明 | ❌ AI补全 |
| **业务痛点** | 描述当前业务的痛点 | ❌ AI补全 |
| **需求描述** | 需求点补充描述更具体详细 | ❌ AI补全 |
| **标签** | 战略 / 经营 / 日常 / 无效型 | ✅ 评分推导 |
| **优先级** | P0 / P1 / P2 / P3 | ✅ 评分推导 |
| **AI建议** | 各维度优化迭代建议，助力开发人员理解和推进 | ✅ 评分后生成 |

### 评分→标签→优先级 自动映射

| 总分 | 等级 | 标签 | 优先级 | 需求类型 | 决策 |
|------|------|------|--------|----------|------|
| ≥80 | A级 | 战略 | P0 | 价值需求 | 独立立项评审 |
| 60-79 | B级 | 经营 | P1 | 价值需求 | 纳入评审流程 |
| 40-59 | C级 | 日常 | P2 | 普通需求 | 轻量快速处理 |
| <40 | D级 | 无效型 | P3 | 普通需求 | 驳回并说明原因 |

### 需求模块推导指引

| 模块 | 典型需求 |
|------|----------|
| 仓储与物流域 | 仓储管理、物流调度、库存优化 |
| 研发域 | 系统开发、技术架构、工具建设、内部平台 |
| 供应链与制造域 | 供应链协同、制造流程、采购管理 |
| 营销域 | 侵权风控、品牌对标、产品上架、市场运营、客户服务 |

**注意**：参考 [rules/company_context.yaml](rules/company_context.yaml) 中已记录的系统与模块关联。AI推导模块后应向用户确认。

## 执行流程

### Step 0. 识别意图 + 读取公司知识

读取 [rules/company_context.yaml](rules/company_context.yaml)，获取公司系统、部门、数据源等信息，用于需求补全时自动关联。

| 指令 | 动作 |
|------|------|
| 查询需求/需求列表 | 拉取需求库列表 |
| 搜索xxx | 模糊匹配需求库 |
| 需求统计 | 显示统计 |
| 查看D001 | 显示完整卡片 |
| 其他 | 走完整评审流程→入库 |

### Step 1. 读取校准规则

读取 [rules/calibration.yaml](rules/calibration.yaml)。

### Step 2. 需求补全与标准化

将用户原始描述补全为**手动字段**（标题/背景/业务痛点/需求描述/需求模块），自动字段（标签/优先级/需求类型/AI建议）由评分推导。

**补全方法论**：5W1H → User Story → JTBD → PR-FAQ → SMART

**公司知识关联**：补全时自动关联 company_context.yaml 中的系统名、部门、数据源等信息。

**质量自检**：标题、背景、业务痛点、需求描述、需求模块为必须字段。缺失≥3项则暂停追问用户。

**学习公司信息**：用户提到的公司系统、部门、人员、业务规则等，自动记录到 company_context.yaml，后续复用。

### Step 3. PM框架分析与评分

读取 [rules/demand_scoring_rules.yaml](rules/demand_scoring_rules.yaml)，进行6维度评分（100分制）。

| 维度 | 权重 | PM框架支撑 |
|------|------|-----------|
| 业务价值 | 25 | RICE Impact + JTBD + North Star + Working Backwards |
| 战略匹配度 | 20 | OKR Alignment + OST |
| 影响范围 | 15 | RICE Reach + Crossing the Chasm + Impact Depth Check |
| 投入产出比 | 15 | RICE Effort & Confidence |
| 紧急程度 | 15 | Time-Sensitive Opportunity |
| 实施复杂度 | 10(反向) | Technical Debt Assessment |

评分完成后，**自动映射**标签、优先级、需求类型。

### Step 4. 生成AI建议

基于评分维度逐项检查，生成开发人员视角的优化建议：

| 检查维度 | 检查内容 | 建议方向 |
|----------|----------|----------|
| 业务价值 | 是否包含量化指标？当前值vs目标值？ | 补充量化指标 |
| 战略匹配度 | 是否对齐OKR？ | 对齐年度OKR |
| 影响范围 | 是否列出受益部门/岗位/规模？ | 补充受益清单 |
| 投入产出比 | 是否明确技术栈、外部依赖、人月？ | 明确技术方案 |
| 紧急程度 | 是否有刚性时间节点？ | 补充时间节点 |
| 实施复杂度 | 是否需要拆分阶段？ | 拆分阶段交付 |
| 开发视角 | 开发人员能否直接理解？验收标准？ | 补充验收标准、接口依赖 |
| 缺失信息 | 成功指标、风险评估、协同机制？ | 补充缺失项 |

### Step 5. 输出评审结果

```
📝 需求补全与标准化
- 需求类型：{demand_type}（自动推导）
- 需求模块：{demand_module}
- 标题：{title}
- 背景：{background}
- 业务痛点：{pain_points}
- 需求描述：{description}
- 标签：{label} | 优先级：{priority}（自动推导）

📊 评审结果：{total_score}分 {grade}级

📋 维度评分：
  业务价值 {score}/25 — {reason}
  战略匹配度 {score}/20 — {reason}
  影响范围 {score}/15 — {reason}
  投入产出比 {score}/15 — {reason}
  紧急程度 {score}/15 — {reason}
  实施复杂度 {score}/10 — {reason}

💡 AI建议（助力开发推进）：
  ①【业务价值】{suggestion}
  ②【战略匹配度】{suggestion}
  ③【影响范围】{suggestion}
  ④【投入产出比】{suggestion}
  ⑤【紧急程度】{suggestion}
  ⑥【实施复杂度】{suggestion}
  ⑦【开发视角】{suggestion}
  ⑧【补充缺失】{suggestion}

💡 决策：{decision}
```

### Step 6. 需求入库

**每次评审完成后，自动向用户确认是否入库**：

```
是否将此需求录入需求库？
- 编号：D{next_id:03d}
- 标题：{title}
- 标签：{label} | 优先级：{priority} | 评分：{total_score}分 {grade}级

回复"是"或"确认"即可入库。
```

用户确认后，记录到 [rules/demand_library.json](rules/demand_library.json)，自动标注编号和加入时间。

### Step 7. 需求库查询

| 指令 | 输出 |
|------|------|
| `查询需求` / `需求列表` | `D001  标题`（仅编号+标题） |
| `搜索关键词` | 模糊匹配标题/描述/背景 |
| `需求统计` | 总数 + 各标签/优先级/模块数量 |
| `查看D001` | 显示完整卡片（含AI建议） |

### Step 8. 用户反馈与自学习

评分后询问用户是否认可。如有纠正：
1. 记录到 [rules/feedback_history.json](rules/feedback_history.json)
2. 提取校准规则写入 [rules/calibration.yaml](rules/calibration.yaml)
3. 公司信息更新到 [rules/company_context.yaml](rules/company_context.yaml)

### Step 9. 批量处理与材料生成

- 批量：逐一补全→评分→建议→排序→入库
- 材料：参考 [scripts/document_generator.py](scripts/document_generator.py)、[scripts/notice_generator.py](scripts/notice_generator.py)

## 关键约束

1. 评分严格基于 demand_scoring_rules.yaml，校准规则优先
2. 补全必做，PM框架分析必做，AI建议必做
3. **标签、优先级、需求类型由评分自动推导，不单独判断**
4. **AI建议从开发人员视角生成，助力需求被更好理解和推进**
5. 查询需求时只显示编号+标题
6. 每次评审后必须询问用户是否入库
7. **学习并记忆公司信息**：系统名、部门、数据源、业务规则等自动记录到 company_context.yaml
8. 需求模块AI推导后应向用户确认
