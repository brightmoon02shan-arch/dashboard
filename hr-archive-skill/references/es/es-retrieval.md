---
name: es-retrieval
description: >
  由 es-talent-query 编排调用，从查询拆解条件出发完成 ES 检索闭环。
  触发关键词：检索、ES查询、retrieval。
---

# 检索执行技能卡

本技能整合了查询分析、DSL 构造执行、结果评估三个环节。目标：作为 Elasticsearch 检索专家，从查询拆解条件出发完成检索闭环。全程遵循"分析阶段不暴露字段名与 DSL"的安全与紧凑输出要求。

## ⚠️ 前置必读（在构造第一个 DSL 之前必须完成）

在构造第一个 DSL 之前，**必须**先 read_file 以下文件：
- [references/es/dsl-manual.md](dsl-manual.md) — 字段 schema、DSL 模板、**STAR_BACKGROUND 强制规则与权重**（**不读此文件直接构造 DSL 将导致字段名错误、字段遗漏、权重错误**）

**未读取以上文件就构造 DSL 属于严重违规。** 历史上多次出现因未读取 dsl-manual.md 导致遗漏绩效/晋升/述职/转正字段、权重自行编造的严重错误。必须先读取，再构造。

## 流程总览（Pipeline）

1. **查询分析** — 解析拆解条件，选择检索策略
2. **DSL 构造与执行** — **必须**参考 DSL 手册构造查询并调用 es_query
3. **结果评估** — 错误检查 → 召回质量评估
4. **质量门** — 通过 → 步骤 5；未通过 → 回到步骤 1（最多 3 轮）
5. **检索结束** — 输出结论，交由 output-format 技能

最多 3 轮迭代。

---

## 步骤一：查询分析

任务：分析查询拆解条件，规划 DSL 策略。**严禁输出任何 DSL 或索引字段英文名。**

### 查询分析（Search-Analysis）

1) **意图接入**
   - 直接读取 es-talent-query 的查询拆解结果
   - 以必须满足项 / 可扩展项 / 待确认项为唯一依据，规划 DSL 策略与覆盖面
   - 若必须满足项中包含"人才类型"条件，**必须**参考 [DSL 手册](references/es/dsl-manual.md) 的 talent_info 章节构造 nested 查询；用户未区分应届/非应届时使用 terms 同时匹配两种类型

2) **关键词分类处理**
   - 若涉及`部门`、`岗位`、`岗位序列`，**必须**参考 [DSL 手册 - 枚举字段洞察](references/es/dsl-manual.md) 执行聚合获取精确检索值；详细流程见 [references/es/field-insight.md](field-insight.md)
   - 若存在待确认项：禁止直接理解含义；通过查询背景/画像数据获取依据，再据此推导可扩展项
   - 若不存在待确认项：直接对可扩展项进行语义泛化；生成 5-10 个同/近义词集合
   - **在分析阶段即补全可扩展项的同/近义词集合；DSL 构造阶段不再生成或修改同/近义词，仅使用已补全集合**

3) **策略选择与打分（0-1）**
   - 三种候选：关键字段查询（精确）、RRF（语义+结构混合）、KNN（仅语义）
   - 选择预判得分最高的策略
   - 规则：非 STAR_BACKGROUND 场景的 RRF 中，nested 仅放在 standard 内；KNN 禁止 nested；STAR_BACKGROUND 模板 A 使用双层 nested 查询绩效；STAR_BACKGROUND 模板 B 使用 `dis_max` + 预聚合 `_str` 字段，不含 nested；避免使用 or，改用 bool+should
   - **覆盖面自检**：策略选定后，逐项核对必须满足项和可扩展项是否都有对应的查询子句覆盖；遗漏项须补齐后再进入步骤二。STAR_BACKGROUND 场景下，额外参照下方"字段覆盖规则"示例表判断应查字段范围
   - 待确认项分支（首轮保守检索）：当待确认项非空时，首轮采用"保守 must-only 检索"（不使用 knn/RRF/nested），以尽快得到样本画像

### 字段脱敏要求
- 使用中文含义指代字段（如"工作地点""职级""最高学历"）

---

## 步骤二：DSL 构造与执行

任务：基于步骤一的策略，参考 [DSL 手册](references/es/dsl-manual.md) 构造 ES 查询 DSL 并执行。

### 通用规则（所有场景）

- 检查 DSL 的层级结构与字段正确性；确保括号/花括号配对
- es_query 的 dsl 参数必须是 JSON 字符串（将对象转为字符串）
- user_id 由 MCP server 从请求上下文自动注入，**无需手动传参**
- include_sensitive_data 参数：**必须传 `true`**（STAR_EVALUATION、STAR_STATUS、STAR_BACKGROUND 场景均必须；其余场景可省略，默认 false）
- ES 连接配置由 MCP server 运行环境自动注入，技能中**禁止硬编码**具体值

### 工具调用示例（es_query）
> 仅在步骤二中构造与展示 DSL；步骤一严禁出现字段英文名与 DSL。
```bash
mcporter call hr_talent_claw.es_query dsl='{"query":{"prefix":{"dept_name_path.keyword":{"value":"小米公司-人力资源部-人力数字化产品部"}}},"size":10}' include_sensitive_data=true
```
执行后在步骤三中评估 ES 查询结果（可按需截断展示 took/total/hits 子集）。

### ⛔ STAR_BACKGROUND 专属规则

**STAR_BACKGROUND 场景构造 DSL 前，必须先读取 [references/es/dsl-star-background.md](dsl-star-background.md)**，按其中的前置判断选择模板 A（近期动态）或模板 B（背景/经验筛选），然后**只替换关键词和 filter 条件，不得修改模板结构、字段组合或权重**。

#### 构造前强制 Checklist（必须在 Thought 中逐条确认，缺一不可）

**在写出任何 JSON 之前，必须在 Thought 中依次回答以下问题，全部回答"是"后才可开始构造 DSL：**

1. ✅ 是否已 read_file 读取了 `references/es/dsl-star-background.md`？（未读取 → 立即读取）
2. ✅ 选择了模板 A 还是模板 B？判断依据是什么？
3. ✅ 是否从模板原文**复制**了完整 JSON 骨架？（禁止凭记忆手写）
4. ✅ `{领域关键词}` 替换为了什么？（列出具体值）
5. ✅ `{filter条件}` 替换为了什么？（列出具体 JSON）
6. ✅ `{语义文本}` 替换为了什么？（模板 B 专用，列出具体值）
7. ✅ 【模板 B 专用】`dis_max.queries` 数量是否 = 9？（逐个列出字段名核对）
8. ✅ 【模板 B 专用】是否包含 3 路 KNN？逐个列出 field 名核对：① `resume_context_embedding` ② `performance_advantage_embedding` ③ `resume_work_embedding`（数量必须 = 3，缺少任何一路即为构造失败）

**如果任何一条回答"否"，必须修正后重新回答全部 checklist，不得跳过直接构造 DSL。**

#### 强制执行规则（违反视为严重构造失败）

**STAR_BACKGROUND 的 DSL 构造必须严格遵守 [dsl-manual.md](references/es/dsl-manual.md) 的 STAR_BACKGROUND 强制规则，以及 [dsl-star-background.md](references/es/dsl-star-background.md) 的固定模板。禁止偷懒、禁止省略字段、禁止自行编造权重。违反以下任何一条视为严重构造失败，必须重新构造：**

1. **背景/经验筛选类查询（模板 B）的 `dis_max.queries` 必须覆盖全部 9 个字段**：`outstanding_achievements_str`、`internal_contributions_str`、`promotion_str`、`review_str`、`probation_detail.advantage`、`resume_context`、`resume_work_info_str`、`tag_info_str`、`career_development_str`。**少一个就是构造失败。**
2. **权重固定不可改**：战功（`outstanding_achievements_str`）=10.0，内功（`internal_contributions_str`）=10.0，晋升/述职/转正=4.0，简历概要/简历工作经历/画像/内部履历=3.0。不得以任何理由自行调整。
3. **禁止因为"关键词看起来只和简历相关"就省略绩效、晋升、述职、转正字段**——候选人的战功里可能写了相关项目成果，晋升评价里可能提到了该领域能力，你无法预判数据分布在哪个字段。
4. **近期动态类查询（模板 A）** 仅需绩效+内部履历，不要求全覆盖。
5. **模板 B 使用 `dis_max` 而非 `bool.should`**：所有 BM25 匹配通过顶层预聚合 `_str` 字段完成，不使用 nested 查询。

9 个必查字段（顺序与模板 DSL 一致）：`outstanding_achievements_str`（战功/外功，10.0）、`internal_contributions_str`（内功，10.0）、`promotion_str`（晋升优势，4.0）、`review_str`（述职优势，4.0）、`probation_detail.advantage`（转正优势，4.0）、`resume_context`（简历概要，3.0）、`resume_work_info_str`（简历工作经历，3.0）、`tag_info_str`（画像，3.0）、`career_development_str`（内部履历，3.0）
meego_projects 随 hits 自动返回，无需写入 DSL。

**示例**：

| 用户问题 | 模板 | 应查字段 | 说明 |
|---------|------|---------|------|
| "张三最近在做什么项目" | A | 战功+内功+内部履历+meego_projects | 近期动态，meego_projects 自动返回 |
| "有百度经历且做HR数字化的人" | B | 9字段全覆盖 | "百度"查简历，"HR数字化"必须同时查战功/内功/晋升/转正/述职/简历/画像/内部履历 |
| "信息部AI领域经验最丰富的人" | B | 9字段全覆盖 | "AI领域"不只在简历里，战功可能有"AI模型落地"、晋升优势可能有"AI技术引领" |
| "做过协同办公且有轮岗经历的管理者" | B | 9字段全覆盖 | "协同办公"必须同时查全部字段 |
| "有数字人背景的算法同学" | B | 9字段全覆盖 | "数字人"不只在简历里，战功可能有相关项目，晋升评价可能提到该能力 |

DSL 构造必须使用 [dsl-star-background.md 模板](references/es/dsl-star-background.md)，只替换关键词和 filter，不得修改结构。

---

## 步骤三：结果评估

任务：分析查询结果，评估匹配程度。

### DSL 构造后自检（调用 es_query 前必须完成）

1. **JSON 格式校验**：逐层检查括号 `{}`、方括号 `[]`、引号 `""` 是否配对。模板 B 使用 `dis_max` 扁平结构，无 nested 嵌套
2. **STAR_BACKGROUND 场景（模板 B）**：
   - `dis_max.queries` 数量必须 = 9 个：`outstanding_achievements_str`、`internal_contributions_str`、`promotion_str`、`review_str`、`probation_detail.advantage`、`resume_context`、`resume_work_info_str`、`tag_info_str`、`career_development_str`。数量不足则补齐后再调用
   - 权重：`outstanding_achievements_str`/`internal_contributions_str` = 10.0，`promotion_str`/`review_str`/`probation_detail.advantage` = 4.0，其余 = 3.0
3. **STAR_STATUS / STAR_EVALUATION 场景（绩效数据源）**：
   - 绩效数据必须且只能使用 `performance_records.stages.data.score`（各期实际等级 S/A/B+/B/B-/C）
   - 禁止从 `tag_info_str` 提取绩效信息——它是画像标签摘要，不是绩效数据
   - 若 `performance_records` 为空，输出"暂无绩效评价记录"，禁止回退到 `tag_info_str`

### 系统错误检查

- 运行报错（DSL 语法错误、字段不存在）：依据错误信息重新检视 DSL 结构与字段
- ES 查询超时：减少高开销操作；必须满足项禁止 wildcard；控制 should 条目数量
- **⚠️ 禁止静默降级（STAR_BACKGROUND场景 模板 B）**：如果 es_query 工具报错（如 RRF 不支持、JSON 解析失败等），**必须在 Thought 中明确说明错误原因和降级方案**，然后重新按模板修正 DSL 再次调用。降级后的底线要求：
  1. **9 个 BM25 字段全部不可减少**：`outstanding_achievements_str`（战功）、`internal_contributions_str`（内功）、`promotion_str`、`review_str`、`probation_detail.advantage`、`resume_context`、`resume_work_info_str`、`tag_info_str`、`career_development_str`。不得以"该查询偏向外部经历""该字段与查询无关"等理由省略任何一个
  2. **降级后必须重新自检**：校验 `dis_max.queries` 数量 = 9、权重正确（战功/内功=10.0，晋升/述职/转正=4.0，其余=3.0），通过后才可调用 es_query

### 召回质量评估
- **结果较少**：
  - 无召回：条件过严；考虑将 filter+prefix 退化为 must+match（使用 match 而非 match_phrase）
  - 存在不符合意图的召回：核查必须满足项是否完整覆盖；可扩展项累计匹配度须 ≥70%
  - 注意：存在可扩展项时，不要退化为"仅关键字段查询"，对于公司/职位等经历验证时必须核对实际工作经历记录，而非关键词匹配
- **结果规模正常**：若仍有不符项，识别歧义来源的泛化词，增限定或替换

### 人名强制规则（红线）

- **无人名时**：禁止模型虚构、联想、补全任何人名
- **有人名时**：仅允许**完全匹配**的记录；禁止同音匹配（张三≠张山）、部分匹配（张三≠张三丰）、姓氏匹配（张三≠张四）
- **输出自检**：输出姓名前必须确认真实存在于查询结果中且未被上述规则排除，有任何幻觉或不确定 → 一律丢弃

### 观察输出规范
- **绝对禁止**出现具体阿拉伯数字（如"查询到 5 人/0 个结果"）
- 使用定性量词：如"召回了一定规模的""发现了一批""未发现匹配实体"

### 边缘情况
- 模棱两可的语义匹配 → 一律保留
- ES 查询结果为空 → 返回空列表，不虚构候选人

---

## 步骤四：质量门

目标：综合召回质量评估，决定是否完成/继续迭代/失败。

### 校验规则（仅核对查询拆解中出现的条件）

- **必须满足项**：姓名精确一致；组织/部门路径对齐；数值/枚举/日期/状态类条件的值或区间一致
- **范围约束**：仅必须满足项/可扩展项/待确认项中明确表达的范围/阈值参与检验
- **待确认项**：若非空，需在本轮说明"已获得支撑/已澄清"的依据；否则不通过
- **可扩展项**：基于同/近义集合计算累计匹配度（建议阈值 ≥70%）
### 通过标准（定性表述）

存在"一定规模的"候选，且必须满足项均满足；可扩展项累计匹配度达标；不存在明显与意图相悖的命中。

### 未通过时的迭代路径

- 召回极少/为空：放松策略（filter+prefix → must/match；term → match；扩展同/近义集合）
- 不符项较多：补齐必须满足项覆盖；剔除歧义词
- 待确认项未澄清：先做保守关键字段检索获取依据，再迭代

### 质量门输出
质量门结论：通过 / 未通过（定性原因，使用中文语义，不出现具体人数/字段英文名/DSL）。

---

## 步骤五：检索结束

- **成功**：召回质与量在核心特征上与用户意图对齐；输出"检索已完成，数据已找到"
- **持续迭代**：若质量门未通过，返回步骤一继续
- **失败**：3 次尝试仍未找到符合条件的候选；输出"经过多次尝试，未找到符合条件的数据"
- **排序信任原则**（STAR_BACKGROUND）：RRF 融合排序已综合结构化匹配与语义相似度，output-format 阶段的评分应视为微调而非重排。若评分与 RRF 排序差异超过 3 个位次，需在 Thought 中说明调整理由。
- 检索结束后立即交由 output-format 技能生成最终回答

### 总结输出规范
- 禁止输出具体数据细节与统计数
- 简洁说明与检索条件相关的核心匹配点
- 引导建议（如有）：以"[匹配度低的具体条件]，建议增加/明确/调整 [方向]"格式输出

## 参考文件

- [references/es/dsl-manual.md](dsl-manual.md)（DSL 参考手册：字段/模板/规则，含枚举字段洞察入口）
- [references/es/dsl-star-background.md](dsl-star-background.md)（**STAR_BACKGROUND 专用 DSL 模板**，构造前必须读取，只替换关键词和 filter）
- [references/es/field-insight.md](field-insight.md)（枚举字段洞察详细流程，涉及部门/岗位/岗位序列时读取）
