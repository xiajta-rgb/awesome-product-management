# 需求补全优化方法论

将用户原始描述补全为结构化需求文档的方法论和示例。

---

## 补全方法论

### 1. 5W1H 六要素

| 要素 | 对应字段 | 补全问题 |
|------|----------|----------|
| Who | target_users | 谁受益？谁使用？ |
| What | demand_name, pain_points | 要做什么？解决什么？ |
| When | usage_scenario, deadline_risk | 何时使用？何时截止？ |
| Where | usage_scenario | 在什么场景？什么系统？ |
| Why | background, expected_value | 为什么要做？业务价值？ |
| How | resource_input | 如何实现？资源投入？ |

### 2. User Story

格式：`As a [角色], I want [功能], so that [价值]`

### 3. JTBD

区分表面需求和深层Job，识别核心Job vs 边缘Job。分析结论复用于PM框架评分，不重复执行。

### 4. PR-FAQ

从客户视角验证：新闻稿标题是什么？有客户证据吗？

### 5. SMART

预期价值必须：Specific(具体) / Measurable(可量化) / Achievable(可实现) / Relevant(相关) / Time-bound(有时限)

---

## 补全示例

**输入**：`做个亚马逊侵权专利库的自动化采集脚本`

**输出**：

| 字段 | 补全内容 | 置信度 |
|------|----------|--------|
| demand_name | 亚马逊侵权专利库自动化采集系统 | inferred |
| demand_category | 合规风控 + 效率提升 | inferred |
| background | 当前依赖手动采集，已有2次侵权警告 | inferred |
| pain_points | 采集效率低、容易遗漏、侵权风险正在发生 | inferred |
| target_users | 法务部3人+运营部5人 | assumed |
| usage_scenario | 日常采集、定期报告、上架前排查 | inferred |
| user_story | As a 运营专员, I want 自动检索侵权专利库, so that 规避侵权风险 | inferred |
| expected_value | 采集效率提升3倍，侵权警告降至0，6月30日前上线 | inferred |
| cross_department_impact | 法务、运营2个部门 | inferred |
| resource_input | 1人月开发 | assumed |
| deadline_risk | 下月底前上线，存在合规风险 | assumed |
| success_metrics | 采集效率≥3倍，侵权警告=0，覆盖≥80%专利类型 | inferred |
| risks_assumptions | API可能变更，比对需人工复核 | assumed |
