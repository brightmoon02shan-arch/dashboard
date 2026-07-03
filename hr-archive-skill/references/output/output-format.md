---
name: output-format
description: >
  智能选才助手的场景化输出格式技能。引导 Agent 根据不同意图场景生成规范化的回答，
  覆盖 5 大场景：STAR_EVALUATION（员工评价报告）、STAR_STATUS（状态分析报告）、
  STAR_BACKGROUND（背景筛查人才卡片）、STAR_TALENT（高潜人才卡片）、
  OUT_OF_SCOPE（业务范畴外引导）。
  当需要格式化 Agent 输出、生成人才卡片、编写分析报告、处理无权限/无数据兜底回复时使用此技能。
---

# 输出格式技能（Output Format）

引导 Agent 根据用户意图场景，按照规范模板生成结构化回答。每个场景有独立的输出规范和示例。

## 何时使用此 skill

- 由 es-talent-query-skills 编排调用，作为流程最后一步生成面向用户的最终回答
- 输入：intent-json（必有）+ review-json（仅经过 es-retrieval 的场景）

## 通用输出规则

所有场景共享以下规则，各场景 reference 中不再重复：

### 1. 姓名展示规范
所有人名必须使用链接格式：`[{real_name}（{oprid}）](https://archive.hr.mioffice.cn/talent-details?userId={oprid})`
示例：`[张三（zhangsan1）](https://archive.hr.mioffice.cn/talent-details?userId=zhangsan1)`

### 2. 回答约束：敏感信息脱敏
输出中**禁止直接展示**以下类型的原始数值或明文内容，必须用脱敏的趋势/相对描述代替：

| 类别 | 禁止展示                                            | 允许的替代表达                                |
|------|-------------------------------------------------|----------------------------------------|
| 薪资 | 任何薪资/薪酬/收入绝对值                                   | **禁止展示薪资信息** |
| 考勤数据 | 工作时长、加班时长、请假时长、出勤天数、请假次数等**具体数值**，以及具体排名名次（如"排名第14位"） | 环比/同比变化、趋势描述（上升/下降/波动）、部门内相对位置（前X%、分位）；禁止出现"平均工作时长XX小时"、"排名第X位"等具体数字 |
| 绩效数据 | 绩效等级字母/标签（S/A/B/C/D）、绩效评级、绩效评分、绩效标签、绩效变化描述（如"下降X档"）、人才评分、人才画像分、晋升预测分、晋升综合评分、人才得分等**一切绩效相关的具体等级值和数值** | 综合表现描述（优秀/良好/待提升）、趋势变化（持续优秀/有所提升）、相对位置；**严禁输出 S/A/B/C/D 等具体等级字母，严禁输出"评级为B"、"同事评价A/S级"、"下降两档"等包含具体等级的表述** |
| 代码与产出 | 代码提交行数、commit 数量、commit 占比、工作量统计                | 产出活跃度描述（高/中/低）、趋势变化                    |
| 人才得分 | 人才得分、人才评分、面试打分、转正得分、晋升综合评分、综合评价得分等所有关于人才职业发展的得分**具体数值** | **严禁展示具体分值**，仅允许使用相对描述（如"综合评价较高"、"表现突出"）；输出中不得出现"得分 XXX"、"评分 X.XX"、"打分 XXX"、"综合评分X.XX"等数字 |
| 内部评价 | 面试官评价、上级/主管评价、同事/peer 评价、下属评价、晋升评价的**原文**       | 综合归纳总结，不得直接引用评价原文                      |

### 3. 字段名脱敏
最终回答中禁止暴露 ES 字段名，一律使用中文业务术语描述。

### 4. 检索路径说明
简要说明最后一次检索的核心逻辑，不提及 DSL/字段名。

### 5. 员工识别与澄清
每个场景的第一步都是识别用户问询的员工，匹配失败时统一输出澄清话术：
```
抱歉，您的权限暂时无法查询到相关信息~
可能原因：1.查询内容涉及本人信息，目前不支持个人自查；2.查询范围超出了您当前的数据权限范围。
```

### 6. talent-card 规范（违反视为输出失败）

**STAR_BACKGROUND**：**必须按分组 + 表格输出，禁止平铺排序，禁止纯文本描述。** 每组用 `###` 标题，组内用 markdown 表格：

```markdown
### {分组名称}

| 姓名 | 部门 | 职级 | 推荐理由 |
|------|------|------|---------|
| [{real_name}（{oprid}）](https://archive.hr.mioffice.cn/talent-details?userId={oprid}) | {dept_name} | {supv_level}级 | {司内匹配点}；{司外匹配点} |
```

**推荐理由格式（强制）**：先内后外，只写有数据支撑的部分，没有的跳过。
- 内外都有：`近两期战功均涉及薪酬数字化项目；曾在IBM从事HR咨询5年`
- 仅有内部：`晋升评审认可其AI领域专业度，当前参与智能客服大模型项目`
- 仅有外部：`曾在科大讯飞负责大模型微调与验证`

所有候选人都必须出现，不得丢弃。分组名称灵活拟定。详细规则见 [references/output/output-star-background.md](output-star-background.md)。

**STAR_TALENT**：每张人才卡片使用 blockquote 格式，卡片之间用 `---` 分隔：

```markdown
> **[{real_name}（{oprid}）](https://archive.hr.mioffice.cn/talent-details?userId={oprid})** · {supv_level}级
>
> {position_name} · {dept_name} · {position_seq} · 工号 {emp_id}
>
> *{核心优势一句话描述，不超过50字}*

---
```

- 第一行：姓名链接、职级，以 `·` 分隔
- 第二行：岗位、部门、序列、工号，以 `·` 分隔
- 第三行：核心优势描述，斜体显示
- 默认最多输出 TOP 16 张卡片，用户指定数量时按指定输出
- 核心优势描述：具体有数据支撑，避免空洞词；不重复卡片中已有的基本信息
- 最后一张卡片后不需要 `---` 分隔线

## ⚠️ 前置必读（生成输出前必须完成）

根据意图类别，**必须先 read_file 对应的输出规范文件**，再生成最终回答。未读取规范文件直接输出属于严重违规——历史上多次出现因未读取规范文件导致格式错误（无分组、无表格、推荐理由缺失内部数据）。

## 场景路由

根据意图类别选择对应的输出规范：

| 意图类别 | 输出类型 | 规范文件 |
|---------|---------|---------|
| STAR_EVALUATION | 评价分析报告 | [references/output/output-star-evaluation.md](output-star-evaluation.md) |
| STAR_STATUS | 状态监测报告 | [references/output/output-star-status.md](output-star-status.md) |
| STAR_BACKGROUND | 背景筛查卡片 | [references/output/output-star-background.md](output-star-background.md) |
| STAR_TALENT | 高潜人才卡片 | [references/output/output-star-talent.md](output-star-talent.md) |
| OUT_OF_SCOPE | 引导回复 | [references/output/output-out-of-scope.md](output-out-of-scope.md) |

## 示例索引

| 场景 | 示例文件 |
|------|---------|
| STAR_EVALUATION | [assets/example-star-evaluation.md](assets/example-star-evaluation.md) |
| STAR_BACKGROUND / STAR_TALENT | [assets/card-examples.md](assets/card-examples.md) |
