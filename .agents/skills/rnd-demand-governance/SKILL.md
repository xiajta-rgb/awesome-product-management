---
name: rnd-demand-governance
description: 研发需求智能评审与治理技能。当用户需要提交研发需求、评估需求优先级、进行需求评审打分、区分战略型/经营优化型/日常改进型/无效需求时触发。自动将用户原始需求描述补全为结构化专业文档（基于5W1H/User Story/JTBD/PR-FAQ/SMART），再依据公司评分规则（业务价值、战略匹配度、影响范围、投入产出比、紧急程度、实施复杂度）和RICE/JTBD/OST/Amazon Working Backwards/OKR/North Star等专业PM框架进行多维度打分、定级分类（A/B/C/D四级）、生成提报材料和部门宣导文案。具备自学习能力，可根据用户纠正自动校准评分策略。Make sure to use this skill whenever the user mentions 需求评审、需求打分、需求定级、需求优先级、研发需求、需求治理、demand review、需求提报、需求评估、需求分类、需求审批、需求立项、需求补全 or wants to automatically score, classify, or generate submission materials for R&D demands.
---

# 研发需求智能治理技能

用户只需用**自然语言**描述需求，AI 自动提取信息、运用PM专业框架深度分析、评分、定级、生成材料。**支持自学习**，根据用户纠正不断优化评分准确性。

## 使用流程

### 1. 用户输入需求（自然语言）

用户可能会用以下方式提交需求：
- 一段话描述："帮我评估这个需求，我们要做..."
- 多个需求编号列举："1. xxx 2. xxx 3. xxx"
- 简单描述："评估：xxx"

### 2. AI 读取校准规则（自学习核心）

评分前，先读取 [rules/calibration.yaml](rules/calibration.yaml)，该文件包含从历史用户反馈中提取的校准规则。

校准规则示例：
```yaml
dimension_calibrations:
  - trigger: "仅个人使用"
    dimension: "影响范围"
    action: "force_score"
    value: 0
    reason: "用户纠正：个人需求影响范围应为0分"
    learned_from: "D002"
```

评分时，如果需求文本匹配到 trigger，则按校准规则调整对应维度的评分。

### 3. AI 自动提取关键信息

从用户描述中提取以下维度信息：

| 提取维度 | 对应评分项 | 提取线索 |
|----------|-----------|----------|
| 业务痛点 | 业务价值 | "太慢"、"容易漏"、"侵权警告"、"客户投诉" |
| 预期收益 | 业务价值、投入产出比 | "提升效率"、"减少成本"、"降低差错率"、百分比数字 |
| 影响范围 | 影响范围 | "X个部门"、"法务和运营"、"全公司" |
| 资源投入 | 投入产出比、实施复杂度 | "X人月"、"半天"、"X人周" |
| 紧急程度 | 紧急程度 | "下月底必须上线"、"不急"、"有截止日" |
| 战略匹配 | 战略匹配度 | "年度战略项目"、"老板要求的"、"合规" |

### 3. 需求描述补全优化（专业化重构）

**原始需求描述往往碎片化、不完整，直接评分会失真。** 必须先调用产品经理需求分析方法论，将原始描述补全为结构化、专业化的需求文档。

读取 [rules/demand_refinement.yaml](rules/demand_refinement.yaml) 获取补全规则，参考 [references/demand_refinement_guide.md](references/demand_refinement_guide.md) 获取方法论说明。

#### 3.1 补全方法论（按顺序应用）

```
5W1H 六要素 → User Story 标准格式 → JTBD 深挖 → PR-FAQ 反推 → SMART 量化
```

**① 5W1H 六要素补全**

| 要素 | 补全内容 | 对应字段 |
|------|----------|----------|
| Who | 谁受益？谁使用？ | target_users |
| What | 要做什么？解决什么？ | demand_name, pain_points |
| When | 何时使用？何时截止？ | usage_scenario, deadline_risk |
| Where | 在什么场景？什么系统？ | usage_scenario |
| Why | 为什么要做？业务价值？ | background, expected_value |
| How | 如何实现？资源投入？ | resource_input |

**② User Story 标准格式**

将需求转化为标准用户故事：
```
作为 [目标用户角色]
我想要 [具体功能/改变]
以便 [实现的业务价值]
```

**③ JTBD 深挖**

- 区分表面需求和深层Job
- 识别核心Job vs 边缘Job
- 评估当前解决方案满意度

**④ PR-FAQ 反推**

- 新闻稿标题：这个需求如果成功，标题是什么？
- 客户证据：有多少客户需要？当前如何解决？
- 技术可行性：我们能做到吗？

**⑤ SMART 量化**

- Specific：具体描述
- Measurable：可量化指标
- Achievable：可实现
- Relevant：与业务相关
- Time-bound：有明确时限

#### 3.2 补全输出格式

补全完成后，每个需求应包含以下完整结构：

```json
{
  "demand_id": "D001",
  "demand_name": "简洁可量化的需求名称",
  "demand_category": "需求分类（产品优化/效率提升/合规风控/基础设施/新功能开发/体验改进）",
  "description": "原始描述",
  "background": "补全后的背景描述",
  "pain_points": "补全后的痛点列表",
  "target_users": "补全后的目标用户",
  "usage_scenario": "补全后的使用场景",
  "user_story": "As a... I want... So that...",
  "expected_value": "补全后的SMART量化价值",
  "cross_department_impact": "补全后的跨部门影响",
  "resource_input": "补全后的资源投入",
  "deadline_risk": "补全后的紧急程度",
  "success_metrics": "补全后的成功指标",
  "risks_assumptions": "补全后的风险与假设",
  "confidence": {
    "confirmed": ["用户明确提供的信息"],
    "inferred": ["AI合理推测的信息"],
    "assumed": ["AI假设但需确认的信息"]
  }
}
```

#### 3.3 补全质量自检

补全后自检以下必须字段：
- [ ] background: 描述了当前状况和问题
- [ ] pain_points: 至少1个具体痛点
- [ ] target_users: 明确目标用户
- [ ] expected_value: 包含可量化价值
- [ ] usage_scenario: 描述了使用场景

#### 3.4 信息标记

- **confirmed**: 用户明确说的（高置信）
- **inferred**: AI根据上下文推测的（中置信）
- **assumed**: AI基于经验假设的，需用户确认（低置信）

### 4. PM 专业框架深度分析（核心深化层）

**使用补全后的需求描述，运用PM专业框架进行深度分析。** 读取 [references/pm_frameworks.md](references/pm_frameworks.md) 获取框架详细说明。

#### 4.1 框架分析顺序

按以下顺序逐层分析，每一层都为评分提供专业判断依据：

```
JTBD 分析 → Working Backwards 验证 → North Star 评估 → OKR 对齐 → OST 定位 → RICE 量化 → Crossing the Chasm 阶段判断 → Technical Debt 评估
```

#### 4.2 各框架分析要点

**① JTBD（Jobs-to-be-Done）分析**
- 识别需求背后的核心Job：用户"雇佣"这个功能要完成什么任务？
- 区分功能性Job（完成什么）、情感性Job（感受什么）、社会性Job（被如何看待）
- 评估Job重要性：核心Job（高分信号）vs 边缘Job（低分信号）
- 评估当前满意度：当前解决方案满意度低 → 机会大 → 加分

**② Amazon Working Backwards 验证**
- 从客户视角反推：如果为这个需求写一篇新闻稿，标题是什么？
- 客户是否真的需要？有客户需求证据（高分）vs 基于内部假设（低分）
- 是否有客户访谈/调研/投诉数据支撑？
- 客户体验路径是否清晰？

**③ North Star（北极星指标）评估**
- 识别公司/产品的北极星指标
- 需求与NSM的关系：直接影响（高分）> 间接影响（中等）> 无关（低分）
- 是否驱动Input Metrics？

**④ OKR 对齐判断**
- 需求支撑哪个层级的OKR：公司级（17-20分）> 部门级（13-16分）> 团队级（9-12分）> 无对齐（0-8分）
- 是否直接贡献于某个Key Result？

**⑤ OST（机会解决方案树）定位**
- 需求在机会树上的位置：主干机会（高分）> 分支机会（中等）> 脱离机会树（低分）
- 是否服务于当前最重要的期望结果？

**⑥ RICE 量化评估**
- Reach：影响多少用户/客户？量化为具体数字
- Impact：对每个用户的影响程度？3=大量/2=中等/1=轻微/0.5=极小
- Confidence：对Reach和Impact估计的信心度？100%=高/80%=中/50%=低
- Effort：需要多少人月？
- 计算 RICE Score = (Reach × Impact × Confidence) / Effort

**⑦ Crossing the Chasm（跨越鸿沟）阶段判断**
- 需求服务的用户群体处于采纳曲线的哪个阶段？
- 跨越鸿沟阶段（高分）：帮助产品进入主流市场
- 早期采纳者阶段（中等）：有价值但需验证
- 滞后期（低分）：差异化价值有限

**⑧ Technical Debt（技术债务）评估**
- 需求对技术架构的影响：减少技术债（高分）> 不增不减（中等）> 增加技术债（低分）
- 是否引入新的维护成本？
- 是否存在更优雅的替代方案？

#### 4.3 框架交叉验证

当多个框架指向相同结论时，评分置信度高：
- JTBD核心Job + North Star直接关联 + OKR公司级对齐 → 确认A级战略型
- RICE高Score + Working Backwards通过验证 → 确认高优先级
- JTBD边缘Job + OST脱离 + 无OKR对齐 → 确认D级无效

当框架结论矛盾时，需深入分析并在评分理由中说明：
- JTBD重要但RICE Score低 → 可能是重要但资源不足，考虑分期实施
- OKR对齐但Working Backwards未通过 → 可能是战略正确但执行方案有误

### 5. AI 根据规则评分

读取 [rules/demand_scoring_rules.yaml](rules/demand_scoring_rules.yaml)，严格按规则评分，同时应用校准规则修正和PM框架分析结论。

#### 评分维度

| 维度 | 权重 | PM框架支撑 | 高分标准 | 低分标准 |
|------|------|-----------|----------|----------|
| 业务价值 | 25分 | RICE Impact + JTBD + North Star + Working Backwards | 显著提升收入/降本≥10%，核心Job，直接影响NSM | 无明确价值，边缘Job，与NSM无关 |
| 战略匹配度 | 20分 | OKR Alignment + OST | 公司级OKR，机会树主干 | 无OKR对齐，脱离机会树 |
| 影响范围 | 15分 | RICE Reach + Crossing the Chasm | 3+部门，高Reach，跨越鸿沟阶段 | 仅个人，低Reach，滞后期 |
| 投入产出比 | 15分 | RICE Effort & Confidence | 低Effort高Confidence，ROI≥3:1 | 高Effort低Confidence，无明确收益 |
| 紧急程度 | 15分 | Time-Sensitive Opportunity | 合规/风险/窗口关闭 | 无紧急性 |
| 实施复杂度 | 10分 | Technical Debt Assessment | 简单快速，减少技术债 | 极难，增加技术债 |

#### 定级规则

| 总分 | 等级 | 类型 | 决策 |
|------|------|------|------|
| ≥80分 | A级 | 战略型需求 | 独立立项评审 |
| 60-79分 | B级 | 经营优化型需求 | 纳入评审流程 |
| 40-59分 | C级 | 日常改进型需求 | 轻量快速处理 |
| <40分 | D级 | 无效型需求 | 驳回并说明原因 |

### 6. 输出评审结果

输出格式（包含补全信息 + PM框架分析）：

```
📝 需求描述补全优化

【原始描述】xxx
【补全后需求名称】xxx
【需求分类】xxx
【用户故事】As a... I want... So that...
【补全内容】背景/痛点/目标用户/场景/价值/资源/紧急度/成功指标/风险
【信息置信度】已确认: [...] | 推测: [...] | 待确认: [...]

📊 需求评审报告

【需求名称】xxx
【总分】XX分
【等级】X级（类型）
【决策】xxx

📋 维度评分：
- 业务价值：XX/25分（理由）
- 战略匹配度：XX/20分（理由）
- 影响范围：XX/15分（理由）
- 投入产出比：XX/15分（理由）
- 紧急程度：XX/15分（理由）
- 实施复杂度：XX/10分（理由）

🔍 PM框架分析：
- JTBD: [核心Job/边缘Job] - [分析结论]
- Working Backwards: [通过/未通过] - [分析结论]
- North Star: [直接关联/间接关联/无关] - [分析结论]
- OKR: [公司级/部门级/团队级/无对齐] - [分析结论]
- OST: [主干/分支/脱离] - [分析结论]
- RICE: Reach=X, Impact=X, Confidence=X%, Effort=X人月 → Score=X
- Crossing the Chasm: [阶段判断] - [分析结论]
- Technical Debt: [减少/不变/增加] - [分析结论]

📐 框架交叉验证：[多框架一致/存在矛盾] - [说明]

💡 建议：xxx

📐 校准规则应用：[如有应用校准规则，说明应用了哪些]
```

### 7. 用户反馈与自学习

**这是确保评分越来越准确的关键环节。**

#### 7.1 收集用户反馈

评分输出后，主动询问用户是否认可评分结果：

```
请问评分结果是否准确？如有异议请指出：
- 哪个维度评分偏高/偏低？
- 你认为正确的等级应该是？
- 理由是什么？
- PM框架分析是否有遗漏或误判？
```

#### 7.2 记录反馈

将用户反馈写入 [rules/feedback_history.json](rules/feedback_history.json)：

```json
{
  "feedbacks": [
    {
      "demand_id": "D002",
      "demand_description": "个人操作界面按钮位置调整",
      "original_scores": {
        "业务价值": 15,
        "影响范围": 8,
        "total": 54,
        "grade": "C"
      },
      "user_correction": {
        "grade": "D",
        "reason": "这完全是个人习惯，无任何业务价值，应该驳回"
      },
      "pm_analysis_correction": {
        "jtbd": "边缘Job，当前满意度已高",
        "working_backwards": "无客户需求证据"
      },
      "timestamp": "2026-05-13T15:30:00"
    }
  ]
}
```

#### 7.3 提取校准规则

从用户反馈中提取可复用的校准规则，写入 [rules/calibration.yaml](rules/calibration.yaml)：

提取逻辑：
1. 分析用户纠正了什么（哪个维度偏高/偏低）
2. 找到需求文本中导致误判的关键词/模式
3. 结合PM框架分析，提取框架层面的校准规则
4. 生成校准规则：当未来需求包含相同模式时，自动修正评分

校准规则类型：
- **force_score**: 强制设定某维度分数（如"仅个人使用"→影响范围=0）
- **adjust_score**: 调整某维度分数（如"无业务价值"→业务价值-10）
- **force_grade**: 强制设定等级（如"纯属个人习惯"→D级）

#### 7.4 校准规则应用

下次评分时，先检查需求文本是否匹配已有校准规则的 trigger，如果匹配则应用校准。

#### 7.5 置信度追踪

根据历史反馈统计准确率，更新 calibration.yaml 中的 confidence_level：
- `initial`: 无反馈数据
- `learning`: 少于10条反馈
- `calibrated`: 10-50条反馈，准确率>70%
- `stable`: 50+条反馈，准确率>85%

### 8. 批量需求处理

如果用户提交多个需求：
1. 逐一进行PM框架分析+评分（应用校准规则）
2. 按 A>B>C>D 排序
3. 汇总统计
4. 过滤D级无效需求，生成驳回原因
5. 输出提报材料

### 9. 生成提报材料

用户确认后，生成：
- 标准化提报材料
- 部门宣导文案

参考脚本：
- [scripts/document_generator.py](scripts/document_generator.py) - 提报材料生成
- [scripts/notice_generator.py](scripts/notice_generator.py) - 宣导文案生成

## 自学习机制总结

```
评分输出 → 用户纠正 → 记录反馈（含PM框架纠正）→ 提取校准规则 → 写入 calibration.yaml
    ↑                                                              ↓
    └────── 下次评分时读取校准规则 ←────────────────────────────────┘
```

| 文件 | 作用 |
|------|------|
| `rules/demand_refinement.yaml` | 需求补全优化规则 |
| `rules/calibration.yaml` | 存储从反馈中提取的校准规则 |
| `rules/feedback_history.json` | 存储所有用户反馈历史 |
| `rules/demand_scoring_rules.yaml` | 基础评分规则（含PM框架引用） |
| `references/demand_refinement_guide.md` | 需求补全方法论详细说明 |
| `references/pm_frameworks.md` | PM专业框架详细说明 |
| `references/scoring_dimensions.md` | 评分维度详细说明（含PM框架视角） |

## 注意事项

1. **严格遵循规则文件**：评分必须基于 `rules/demand_scoring_rules.yaml` 中的标准
2. **校准规则优先**：当校准规则与基础规则冲突时，校准规则优先
3. **补全必做**：评分前必须先补全需求描述，补全质量直接影响评分准确性
4. **PM框架必做**：评分前必须完成PM框架分析，框架分析结论直接影响评分
5. **框架交叉验证**：当多个框架指向一致结论时，评分置信度更高
6. **语义理解**：自然语言描述可能不完整，AI 需要理解上下文进行合理推断
7. **否定词识别**：注意"无"、"不"、"仅个人"等否定/低价值词汇
8. **量化优先**：优先使用用户提供的量化数据（如"提升30%"、"1人月"）
9. **透明解释**：每个维度的评分必须有明确的理由说明，包含PM框架分析依据
10. **主动收集反馈**：评分后主动询问用户是否认可，推动自学习循环
11. **RICE量化**：尽可能将模糊描述转化为RICE可量化指标
12. **信息标记**：补全后的需求必须标记confirmed/inferred/assumed，让用户知道哪些需要确认
