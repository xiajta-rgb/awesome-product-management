---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动将用户原始需求描述补全为结构化专业文档（基于5W1H/User Story/JTBD/PR-FAQ/SMART），按标准字段输出（需求类型/需求模块/标题/背景/业务痛点/需求描述/标签/优先级/AI建议），再依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）和RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star等专业PM框架进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。支持需求库管理（自动记录/查询/状态更新/去重检查/变更历史/软删除）。具备自学习能力，可根据用户纠正自动校准评分策略。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项、需求补全、需求库、查询需求 or wants to automatically score, classify, or generate submission materials for R&D demands.
---

# 研发需求智能治理技能

用户用自然语言描述需求，AI 自动补全→去重→分析→评分→建议→入库→生成材料。支持自学习和公司知识记忆。

## 标准录入字段

| 字段 | 说明 | 自动 |
|------|------|------|
| **需求类型** | 普通需求 / 价值需求 | ✅ 由评分推导 |
| **需求模块** | 仓储与物流域 / 研发域 / 供应链与制造域 / 营销域 | ❌ AI判断+确认 |
| **提出人** | 需求提出人姓名 | ❌ |
| **标题** | 一句话简单描述需求核心内容（≤50字） | ❌ |
| **背景** | 问题背景与现状说明 | ❌ |
| **业务痛点** | 描述当前业务的痛点 | ❌ |
| **需求描述** | 需求点补充描述更具体详细 | ❌ |
| **标签** | 战略 / 经营 / 日常 / 无效型 | ✅ 由评分推导 |
| **优先级** | P0 / P1 / P2 / P3 | ✅ 由评分推导 |
| **AI建议** | 8维度优化迭代建议（开发人员视角） | ✅ 由评分推导 |

### 评分→标签→优先级 自动映射（唯一来源：demand_scoring_rules.yaml）

| 总分 | 等级 | 标签 | 优先级 | 需求类型 | 决策 |
|------|------|------|--------|----------|------|
| 80-100 | A级 | 战略 | P0 | 价值需求 | 独立立项评审 |
| 60-79 | B级 | 经营 | P1 | 价值需求 | 纳入评审流程 |
| 40-59 | C级 | 日常 | P2 | 普通需求 | 轻量快速处理 |
| 0-39 | D级 | 无效型 | P3 | 普通需求 | 驳回并说明原因 |

### 需求模块推导

| 模块 | 典型需求 |
|------|----------|
| 仓储与物流域 | 仓储管理、物流调度、库存优化 |
| 研发域 | 系统开发、技术架构、工具建设、内部平台 |
| 供应链与制造域 | 供应链协同、制造流程、采购管理 |
| 营销域 | 侵权风控、品牌对标、产品上架、市场运营 |

参考 [rules/company_context.yaml](rules/company_context.yaml) 中系统与模块关联。AI推导后向用户确认。

### 需求状态流转

```
待评审 → 已评审 → 已立项 → 开发中 → 已完成
                 → 已驳回
                 → 已暂缓 → 已立项/已驳回
         已立项 → 已取消
```

状态操作指令：`立项D001` / `驳回D001` / `暂缓D001` / `取消D001`
状态流转有校验，不合法的转换会被拒绝并提示允许的目标状态。

## 执行流程

### Step 0. 读取上下文 + 识别意图

读取 [rules/company_context.yaml](rules/company_context.yaml)（公司知识）和 [rules/calibration.yaml](rules/calibration.yaml)（校准规则）。

| 指令 | 动作 |
|------|------|
| 查询需求/需求列表 | 拉取需求库（编号+标题+状态） |
| 搜索xxx | 模糊匹配 |
| 需求统计 | 统计（含状态分布） |
| 查看D001 | 完整卡片（含AI建议+变更历史） |
| 立项/驳回/暂缓/取消 D001 | 状态变更（带校验） |
| 删除D001 | 软删除（标记deleted，可恢复） |
| 其他 | 完整评审流程 |

### Step 1. 需求去重检查

读取 [rules/demand_library.json](rules/demand_library.json)，检查新需求与已有需求是否高度相似（标题或描述关键词重叠≥60%）。已删除的需求不参与去重。

**存在相似需求时**：
```
⚠️ 需求库中已存在相似需求：
D001  磐石系统侵权库重构+自动化侵权素材生成+新人风控培训（相似度: 0.85）
是否：1.合并到已有需求 2.更新已有需求 3.作为新需求继续
```

**无相似需求**：继续Step 2。

### Step 2. 需求补全与标准化

将用户原始描述补全为手动字段（标题/背景/业务痛点/需求描述/需求模块），自动字段由评分推导。

**补全方法论**：5W1H → User Story → JTBD → PR-FAQ → SMART

**公司知识关联**：自动关联 company_context.yaml 中的系统名、部门、数据源。

**学习公司信息**：用户提到的公司系统/部门/数据源/业务规则，按 [rules/demand_scoring_rules.yaml](rules/demand_scoring_rules.yaml) 中的 company_context_rules 判断是否记录。

**质量自检**：标题、背景、业务痛点、需求描述、需求模块为必须字段。缺失≥3项→暂停追问用户。

### Step 3. PM框架分析与评分

读取 [rules/demand_scoring_rules.yaml](rules/demand_scoring_rules.yaml)，6维度评分（100分制）。

| 维度 | 权重 | PM框架 |
|------|------|--------|
| 业务价值 | 25 | RICE Impact + JTBD + North Star + Working Backwards |
| 战略匹配度 | 20 | OKR + OST |
| 影响范围 | 15 | RICE Reach + Chasm + Impact Depth |
| 投入产出比 | 15 | RICE Effort & Confidence |
| 紧急程度 | 15 | Time-Sensitive Opportunity |
| 实施复杂度 | 10(反向) | Technical Debt |

评分完成后自动映射标签、优先级、需求类型。

**评分校验**：AI返回的分数必须通过 validate_score 校验（总分与等级匹配、各维度分数在合法范围内、维度总分与总分一致）。校验不通过时提示AI重新评分。

### Step 4. 生成AI建议

8维度逐项检查，生成开发人员视角的优化建议：

| 维度 | 检查 | 建议 |
|------|------|------|
| 业务价值 | 量化指标？当前vs目标？ | 补充量化指标 |
| 战略匹配度 | 对齐OKR？ | 对齐年度OKR |
| 影响范围 | 受益部门/岗位/规模？ | 补充受益清单 |
| 投入产出比 | 技术栈/外部依赖/人月？ | 明确技术方案 |
| 紧急程度 | 刚性时间节点？ | 补充时间节点 |
| 实施复杂度 | 需要拆分阶段？ | 拆分阶段交付 |
| 开发视角 | 验收标准/接口依赖？ | 补充验收标准 |
| 缺失信息 | 成功指标/风险评估/协同？ | 补充缺失项 |

### Step 5. 输出评审结果

```
📝 需求补全与标准化
- 需求类型：{demand_type}（自动推导）
- 需求模块：{demand_module}
- 提出人：{proposer}
- 标题：{title}
- 背景：{background}
- 业务痛点：{pain_points}
- 需求描述：{description}
- 标签：{label} | 优先级：{priority}（自动推导）

📊 评审结果：{total_score}分 {grade}级 | 评分置信度：{scoring_confidence}

🔍 PM框架分析摘要：
  JTBD: {jtbd结论} | Working Backwards: {wb结论} | North Star: {ns结论}
  OKR: {okr结论} | OST: {ost结论} | RICE Score: {rice_score}
  交叉验证：{cross_validation}

📋 维度评分：
  业务价值 {score}/25 — 判断依据：{basis}（扣分原因：{deduction}）
  战略匹配度 {score}/20 — 判断依据：{basis}（扣分原因：{deduction}）
  影响范围 {score}/15 — 判断依据：{basis}（扣分原因：{deduction}）
  投入产出比 {score}/15 — 判断依据：{basis}（扣分原因：{deduction}）
  紧急程度 {score}/15 — 判断依据：{basis}（扣分原因：{deduction}）
  实施复杂度 {score}/10 — 判断依据：{basis}（扣分原因：{deduction}）

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
🚫 D级驳回理由：{reject_reason}（仅D级需求显示）
```

### Step 6. 需求入库

确认入库：
```
是否将此需求录入需求库？
- 编号：D{next_id:03d}
- 标题：{title}
- 标签：{label} | 优先级：{priority} | 评分：{total_score}分 {grade}级 | 置信度：{scoring_confidence}

回复"是"或"确认"即可入库。
```

### Step 7. 需求库查询

| 指令 | 输出 |
|------|------|
| `查询需求` / `需求列表` | `D001  标题  状态` |
| `搜索关键词` | 模糊匹配 |
| `需求统计` | 总数+标签+优先级+模块+状态分布 |
| `查看D001` | 完整卡片（含AI建议+变更历史） |
| `立项/驳回/暂缓/取消 D001` | 状态变更（带校验） |
| `删除D001` | 软删除（标记deleted） |

**查看需求卡片标准格式**：
```
━━━ D001 需求卡片 ━━━
📋 标题：{title}
👤 提出人：{proposer}
🏷️ 类型：{demand_type} | 模块：{demand_module} | 标签：{label} | 优先级：{priority}
📊 评分：{total_score}分 {grade}级 | 置信度：{scoring_confidence}
📝 背景：{background}
⚡ 痛点：{pain_points}
📄 描述：{description}
💡 AI建议：{ai_suggestions}
📌 状态：{status} | 提交人：{submitter}
🕐 创建：{created_at} | 更新：{updated_at}
📜 变更历史：
  - {timestamp} {action}: {detail}
━━━━━━━━━━━━━━━━━━━
```

### Step 8. 反馈与自学习

评分后询问用户是否认可。纠正→记录 [rules/feedback_history.json](rules/feedback_history.json)→提取校准规则→写入 [rules/calibration.yaml](rules/calibration.yaml)。公司信息更新→写入 [rules/company_context.yaml](rules/company_context.yaml)（更新last_updated字段）。

### Step 9. 批量处理

批量输入时：按段落/编号分隔→逐一补全→评分→建议→按总分降序排列→逐一确认入库。某个需求信息不足时单独追问，不影响其他需求继续评审。支持断点续评：已评审的需求直接跳过，只处理未完成的。

## 关键约束

1. 评分严格基于 demand_scoring_rules.yaml，校准规则优先
2. 补全必做，PM框架分析必做，AI建议必做
3. 标签/优先级/需求类型由评分自动推导（唯一来源：grade_rules）
4. AI建议从开发人员视角生成
5. **新需求必须先去重检查**
6. 查询显示编号+标题+状态
7. 评审后必须询问入库
8. 学习公司信息按 company_context_rules 判断
9. 需求模块AI推导后向用户确认
10. 评分理由拆为"判断依据+扣分原因"
11. 状态流转需校验合法性
12. 所有变更记录到 change_history
13. AI返回的分数必须通过 validate_score 校验
14. D级需求必须给出驳回理由（reject_reason）
15. 评分结果必须包含评分置信度（scoring_confidence）
16. 删除为软删除，已删除需求不参与去重和统计
