# 需求补全优化方法论

将用户原始描述补全为结构化需求文档的方法论和示例。

---

## 补全方法论

### 1. 5W1H 六要素

| 要素 | 对应字段 | 补全问题 |
|------|----------|----------|
| Who | target_users | 谁受益？谁使用？ |
| What | title, pain_points | 要做什么？解决什么？ |
| When | deadline_risk | 何时截止？有无时间节点？ |
| Where | demand_module, background | 在什么场景？什么系统？哪个业务域？ |
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

**输出**（标准录入字段）：

| 字段 | 补全内容 | 置信度 |
|------|----------|--------|
| proposer | 戴玉婷 | confirmed |
| title | 亚马逊侵权专利库自动化采集系统 | inferred |
| demand_module | 营销域 | inferred |
| background | 当前依赖手动采集USPTO专利网站，流程复杂效率低，已有2次侵权警告 | inferred |
| pain_points | 采集效率低需逐个上传查看、容易遗漏导致侵权风险、侵权判断流程不完善 | inferred |
| description | 搭建自动化侵权专利采集系统，通过USPTO接口或鸥鹭/卖家精灵数据库自动检索采集专利PDF，实现侵权自动比对和预警 | inferred |

**输出**（辅助字段，不录入需求库但用于评分）：

| 字段 | 补全内容 | 置信度 |
|------|----------|--------|
| user_story | As a 运营专员, I want 自动检索侵权专利库, so that 规避侵权风险 | inferred |
| expected_value | 采集效率提升3倍，侵权警告降至0，6月30日前上线 | inferred |
| target_users | 法务部3人+运营部5人 | assumed |
| resource_input | 1人月开发 | assumed |
| deadline_risk | 下月底前上线，存在合规风险 | assumed |

**说明**：标准录入字段（title/background/pain_points/description/demand_module）为必须补全项；辅助字段用于评分参考，不直接入库。标签/优先级/需求类型/AI建议由评分自动推导，不在补全阶段生成。
