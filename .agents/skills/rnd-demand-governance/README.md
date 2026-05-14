# 研发需求智能治理技能

一个专为研发部门打造的自动化需求评审工具，基于公司评分规则 + 产品管理专业框架，实现「一段话描述 → PM框架深度分析 → AI 智能评审 → 自动打分 → 定级分类 → 材料生成」的全流程自动化。**支持自学习**，根据用户纠正不断优化评分准确性。

## 核心工作流

```
用户输入：一段话描述需求
       ↓
AI 读取校准规则（自学习产出）
       ↓
AI 自动提取：痛点/收益/影响/投入/紧急程度
       ↓
需求描述补全优化：5W1H → User Story → JTBD → PR-FAQ → SMART
       ↓
PM框架深度分析：JTBD → Working Backwards → North Star → OKR → OST → RICE → Crossing the Chasm → Tech Debt
       ↓
AI 智能评分：6维度打分 + PM框架交叉验证 + 定级 + 决策
       ↓
输出结果：补全报告 + 评分报告 + PM框架分析 + 优先级 + 提报材料
       ↓
用户反馈纠正 → 自动校准 → 下次更准确
```

---

## 使用方式

### 一句话提交需求（推荐）

直接描述你的需求，AI 自动提取关键信息、进行PM框架分析并评分：

```
你：帮我评估这个需求，我们要做一个亚马逊侵权专利库的自动化采集脚本，
现在手动采集太慢了还容易漏，已经收到两次侵权警告了，法务和运营都在用，
大概1人月能搞定，下个月底前必须上线。

AI：[PM框架分析]
  - JTBD: 核心Job="避免侵权风险"，当前满意度极低
  - Working Backwards: 客户强需求，已有2次侵权警告作为证据
  - North Star: 直接关联"采集任务完成数"
  - OKR: 支撑部门级OKR"提升合规效率"
  - RICE: Reach=高, Impact=3, Confidence=80%, Effort=1人月 → 高优先级
  [自动评分] → 85分 A级 → 独立立项评审
```

### 批量需求评审

```
你：帮我评审这批需求：

1. 跨部门数据中台，把销售财务供应链数据整合，提升40%效率，3个部门用，3人月，年度战略项目
2. 个人界面按钮改颜色，就我习惯用，无业务价值，半天搞定，不急
3. 客服系统智能回复，减少30%人工量，客服和技术部用，2人月，老板希望尽快上线

AI：[批量PM框架分析+评分]
- D001: 88分 A级战略型 → 独立立项
- D002: 12分 D级无效 → 驳回（JTBD边缘Job, 无OKR对齐, RICE极低）
- D003: 65分 B级经营优化 → 纳入评审
```

### 用户纠正与自学习

```
AI：D002 评分 54分 C级日常改进型

你：不对，这个完全是个人习惯，无任何业务价值，应该是D级驳回

AI：[记录反馈] → [提取校准规则] → [更新PM框架分析模式] → 已学习！
    下次遇到"仅个人习惯"类需求，将自动降低评分。
```

---

## PM专业框架

本技能融入8大产品管理专业框架，为评分提供专业判断依据：

| 框架 | 来源 | 评分映射 | 核心作用 |
|------|------|----------|----------|
| **5W1H** | 经典需求分析 | → 需求补全 | 六要素完整性检查 |
| **User Story** | 敏捷开发 | → 需求补全 | 角色-功能-价值标准化 |
| **JTBD** | Clayton Christensen | → 需求补全 + 业务价值 | 识别真实需求 |
| **PR-FAQ** | Amazon | → 需求补全 + 业务价值 | 客户视角验证 |
| **SMART** | 目标管理 | → 需求补全 | 价值量化标准化 |
| **RICE** | Intercom | Reach→影响范围, Impact→业务价值, Confidence→投入产出比, Effort→实施复杂度 | 量化优先级 |
| **OST** | Teresa Torres | → 战略匹配度 | 系统化机会探索 |
| **OKR** | Intel/Google | → 战略匹配度 | 战略目标对齐 |
| **North Star** | Sean Ellis | → 业务价值 | 核心指标驱动 |
| **Crossing the Chasm** | Geoffrey Moore | → 影响范围 | 市场阶段判断 |
| **Technical Debt** | Ward Cunningham | → 实施复杂度 | 技术影响评估 |

### 框架交叉验证

当多个框架指向相同结论时，评分置信度高：
- JTBD核心Job + North Star直接关联 + OKR公司级对齐 → 确认A级战略型
- RICE高Score + Working Backwards通过验证 → 确认高优先级
- JTBD边缘Job + OST脱离 + 无OKR对齐 → 确认D级无效

---

## 自学习机制

| 阶段 | 条件 | 说明 |
|------|------|------|
| `initial` | 无反馈 | 使用基础规则评分 |
| `learning` | <10条反馈 | 开始校准，逐步优化 |
| `calibrated` | 10-50条反馈，准确率>70% | 评分显著改善 |
| `stable` | 50+条反馈，准确率>85% | 评分稳定可靠 |

校准规则存储在 `rules/calibration.yaml`，反馈历史存储在 `rules/feedback_history.json`。

---

## 评分机制

| 维度 | 权重 | PM框架支撑 | 说明 |
|------|------|-----------|------|
| 业务价值 | 25分 | RICE Impact + JTBD + North Star + Working Backwards | 收入提升/降本增效/核心Job/NSM关联 |
| 战略匹配度 | 20分 | OKR Alignment + OST | OKR对齐/机会树定位 |
| 影响范围 | 15分 | RICE Reach + Crossing the Chasm | 跨部门/市场阶段 |
| 投入产出比 | 15分 | RICE Effort & Confidence | ROI评估/信心度 |
| 紧急程度 | 15分 | Time-Sensitive Opportunity | 合规/风险/窗口 |
| 实施复杂度 | 10分 | Technical Debt Assessment | 反向计分/技术债影响 |

| 总分 | 等级 | 类型 | 决策 |
|------|------|------|------|
| ≥80分 | A级 | 战略型需求 | 独立立项评审 |
| 60-79分 | B级 | 经营优化型需求 | 纳入评审流程 |
| 40-59分 | C级 | 日常改进型需求 | 轻量快速处理 |
| <40分 | D级 | 无效型需求 | 驳回并说明原因 |

---

## 项目结构

```
rnd-demand-skills/
├── rules/
│   ├── demand_scoring_rules.yaml   # 基础评分规则 v2.0（含PM框架引用）
│   ├── demand_refinement.yaml      # 需求补全优化规则 v1.0
│   ├── calibration.yaml            # 校准规则（自学习产出）
│   └── feedback_history.json       # 反馈历史（自学习数据）
├── references/
│   ├── pm_frameworks.md            # PM专业框架详细说明
│   ├── demand_refinement_guide.md  # 需求补全方法论详细说明
│   └── scoring_dimensions.md       # 评分维度详细说明（含PM框架视角）
├── scripts/
│   ├── demand_scorer.py            # LLM 评分提示词构建器 v5
│   ├── demand_refiner.py           # LLM 需求补全优化器 v1
│   ├── document_generator.py       # 提报材料生成
│   ├── notice_generator.py         # 宣导文案生成
│   ├── radar_chart.py              # 雷达图可视化
│   └── version_manager.py          # 规则版本控制
├── LICENSE
└── README.md
```

---

## 自定义配置

- `rules/demand_scoring_rules.yaml` - 调整权重、分档、关键词、PM框架引用
- `rules/calibration.yaml` - 由 AI 自动维护，也可手动添加校准规则
- `references/pm_frameworks.md` - PM框架详细说明，可扩展新框架

---

## 版本信息

- **版本**: 5.0 (需求补全优化版)
- **更新日期**: 2026-05-14
- **许可证**: MIT
