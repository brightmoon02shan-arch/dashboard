---
name: talent-profile
description: >
  人才档案工具使用指南。当 routing-mixed.md 判定为 TALENT_PROFILE 时加载本文件，
  指导 LLM 调用 talent_profile 工具、处理返回值、按 output-talent-profile.md 渲染飞书卡片。
---

# 人才档案（TALENT_PROFILE）

> **🚨 人才档案是两步流程，缺一不可：**
> 1. **调用 `talent_profile` 工具** → 拿到 6 段并行召回的卡片 payload（JSON）
> 2. **按 [output-talent-profile.md](../output/output-talent-profile.md) 骨架渲染并发送一张飞书 interactive 卡片**
>
> 调用工具后必须立即执行第 2 步。禁止仅以纯文本输出工具返回的 JSON、禁止不渲染卡片直接转述、禁止把 6 段拆成多张卡片。

---

## 一、工具调用

```bash
mcporter call --raw-strings hr_talent_claw.talent_profile username="张三"
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `username` | ✅ | 员工标识，接受**中文姓名 / 工号（emp_id 数字串） / oprid（拼音英文）** 三选一 |

> 工具内部 `sender_id` 由 `X-ClawToken` 自动解码注入，LLM **不需要**显式传入；权限边界由 sql_core_v2 / es_core 统一保护。

### 1.1 调用前置校验

| 场景 | 处理 |
|------|------|
| 自指性表述（"我自己/我的档案"等） | 由 SKILL.md §1.1 在 Skill 层拦截，**不调用工具**；工具层 `self_query_blocked` 兜底详见 §三 · 2.2 |
| 未提供员工标识 | **不调用工具**，回复："请提供员工的姓名、工号或 oprid，例如「XXX 的人才档案」。" |
| 多人查询 | 一次只查一个人；多对象时按出现顺序**逐一调用**，每个对象输出一张完整卡片（详见 §五 多人查询规则） |
| 锚点多命中 | 工具返回 `anchor_fail/multiple` → 列 `candidates` 让用户选择，**禁止自动挑选**（详见 §三 · 2.1）|

---

## 二、参数抽取

| 入参 | 来源 | 抽取规则 |
|------|------|---------|
| `username` | 用户问句中的「员工标识」 | 优先级 oprid > emp_id > emp_nm；保留原始大小写、不做拼音转中文 |

**抽取范例**：

| 用户问题 | `username` |
|----------|-----------|
| "XXX 的人才档案"（中文姓名） | `"XXX"` |
| "qiulvyang 的档案"（拼音 oprid） | `"qiulvyang"` |
| "10086 的人才档案"（纯数字工号） | `"10086"` |
| "查下 XXX 和 YYY 的档案" | 两次调用，分别 `"XXX"`、`"YYY"` |

---

## 三、工具返回值

工具返回 **JSON 字符串**，至少包含以下 4 种顶层结构之一。

### 2.1 锚点失败 — 不渲染卡片

```json
{"card_type": "anchor_fail", "status": "not_found", "msg": "未找到员工: XXX"}
```

```json
{
  "card_type": "anchor_fail",
  "status": "multiple",
  "msg": "找到多名员工，请用工号精确指定（3）",
  "candidates": [
    {"emp_id": "<emp_id>", "emp_nm": "<emp_nm>", "oprid": "<oprid>"}
  ]
}
```

**LLM 处理**：
- `not_found` → 直接展示工具的 `msg`，引导用户补充工号
- `multiple` → 列出 `candidates` 让用户选择（**禁止自动挑选**）

### 2.2 自查拦截（D22，覆盖 D20）

锚点 `oprid == sender_id` 时工具直接返回（**不渲染卡片**）：

```json
{
  "card_type": "self_query_blocked",
  "msg": "本人档案查询暂不支持，请移步飞书 HR 人才档案小程序。",
  "applink": "https://applink.feishu.cn/client/mini_program/open?appId=cli_a2b6e4f5cdf8d062"
}
```

**LLM 处理**：仅输出以下文案，**禁止**追加任何其他文字（不要"抱歉"、不要"可能原因"、不要解释）：

> 本人信息查询暂请移步至人才档案：https://applink.feishu.cn/client/mini_program/open?appId=cli_a2b6e4f5cdf8d062

### 2.3 顶层错误

```json
{"error": "人才档案生成失败: ..."}
```

处理流程见 §四 错误处理。

### 2.4 正常卡片 payload

```json
{
  "card_type": "talent_profile",
  "header": {"emp_nm": "XXX", "oprid": "xxx", "emp_id": "10086", "is_self": false},
  "section1": {
    "label": "section1",
    "raw": "<原始 SQL Markdown>",
    "rows": [{
      "emp_id": "...", "emp_nm": "...", "oprid": "...",
      "pos_nm": "...", "pos_lvl": "...", "hire_pos_lvl": "...",
      "dept_nm": "...", "dept_path_nm": "\\小米公司\\...\\...", "dept_nm_lvl1": "...", "dept_nm_lvl2": "...", "dept_nm_lvl3": "...", "dept_nm_lvl4": "...",
      "last_hire_dt": "YYYY-MM-DD", "wrk_age_mi_y": 0, "age_y": 0, "gdr_cd": "...",
      "mng_emp_id": "...", "mng_oprid": "...", "mng_emp_nm": "...", "dir_sub_emp_cnt": 0,
      "frs_edu_deg_cd": "...", "frs_sch_nm": "...", "hi_edu_deg_cd": "...", "hi_sch_nm": "...",
      "cmp_chn_nm": "...", "bas_loc_nm": "...", "emp_sts_cd": "...",
      "new_grdt_flg": "Y/N", "fur_flg": "Y/N", "mng_flg": "Y/N", "yng_eng_flg": "Y/N", "blue_flg": "Y/N"
    }]
  },
  "section2": {
    "perf": {"label": "section2_1", "rows": [{"emp_id": "...", "pfm_prd": "2025H2", "pfm": "B+", "hi_pfm_flg": 0, "bb_pfm_flg": 1, "lo_pfm_flg": 0}], "raw": "<原始 SQL Markdown>"},
    "half_yearly": "B(25H2)、A(25H1)",
    "quarterly": "B(26Q1)、B+(25Q4)",
    "perf_summary": {
      "strengths": ["强项1文本（跨期聚合去重）", "强项2文本"],
      "weaknesses": ["待提升项1文本（跨期聚合去重）"]
    },
    "llm": null
  },
  "section3": {
    "weekly_report": [{"report_nm": "...", "time_range": "...", "work_list": [{"year": 2026, "week_of_year": 24, "content": "..."}]}],
    "meego_metrics": {"recent_period": {"time_range": "20260509~20260609", "total_work_items": 7, "total_points": 7, "work_item_groups": [{"prj_nm": "...", "req_nm": "...", "task_nm": "...", "points": 1, "priority": "P0", "status": "进行中", "bgn_dt": "20260501", "end_dt": "20260601", "collaborators": ["张三", "李四"]}]}},
    "git_metrics": {"recent_period": {"time_range": "...", "commit_cnt": 10, "commit_line_cnt": 500, "cr_line_cnt": 300}, "previous_period": {"time_range": "...", "commit_cnt": 8, "commit_line_cnt": 400, "cr_line_cnt": 250}, "ratio": {"commit_ratio": 25, "commit_line_ratio": 25, "cr_line_ratio": 20}},
    "ai_focus": null
  },
  "section3_5": {
    "title": "AI 用量（20260428~20260512）",
    "ai_model_usage": [
      {
        "time_range": "20260428~20260512",
        "total_token_usage": 34818542,
        "total_cost_amt": 10.85
      }
    ]
  },
  "section2_5": {
    "resume_work_infos": [
      {
        "start_date": "2012-05",
        "end_date": "2014-06",
        "company_name": "三星(中国)投资有限公司",
        "job_title": "销售经理"
      },
      {
        "start_date": "2014-06",
        "end_date": "2019-11",
        "company_name": "三星(中国)投资有限公司",
        "job_title": "大客户经理"
      }
    ]
  },
  "section4": {
    "label": "section4",
    "raw": "<原始 SQL Markdown>",
    "rows": [{"emp_id": "...", "typ": "晋升/转正/入离职/培训/奖项/岗位调整...", "actn_typ": "...细分动作...", "eft_dt": 20260221, "pos_lvl": "16", "pos_nm": "...", "dept_nm_path": "\\小米公司\\..."}]
  },
  "footer_action": {"text": "XXX 的人才档案", "url": "https://archive.hr.mioffice.cn/talent-details?userId=xxx"},
  "_meta": {"version": "v0", "is_self_query": false, "llm_enabled": false}
}
```

**字段说明（与实际工具返回对齐）**：

- `section1.rows[0]` 为单行字典：`dept_path_nm` 已是反斜杠分隔的层级路径，`mng_*` 系列即上级三件套，`dir_sub_emp_cnt` 是直属下属数，`*_flg` 是 Y/N 标签位（应届/外派/管理者/青年工程师/蓝领）。
- `section2.perf.rows` 来自 `ads_ai_qa_pfm_q_f`，按 `pfm_prd DESC LIMIT 10`，**字段名为 `pfm_prd` / `pfm`**（`pfm` 即等级原值，如 "B+"/"A"）；表中无记录时 `rows` 为空数组，整段 §2 隐藏。
- `section2.half_yearly` 是工具层已格式化的半年度/年度绩效行（如 `B(25H2)、A(25H1)`），`section2.quarterly` 是季度绩效行（如 `B(26Q1)、B+(25Q4)`），无季度数据时为空串。直接渲染即可，无需再做格式转换。
- `section3` 是 **结构化数据**（STAR_STATUS 格式一风格），包含以下子字段：
  - `section3.weekly_report`：周报数组，每个元素包含 `report_nm`、`time_range`、`work_list[]`（`year`、`week_of_year`、`content`）。取最近 1 周按项目拆分展示。
  - `section3.meego_metrics`：Meego 项目管理数据，含 `recent_period`（`time_range`、`total_work_items`、`total_points`、`work_item_groups[]`）。用于整体工作情况和 AI 项目工时两个子章节。
  - `section3.git_metrics`：Git 研发效能数据，含 `recent_period`、`previous_period`、`ratio`。
  - 以上三个子字段为空对象/空数组时对应子项隐藏，全部为空时**整段 `section3` 不出现在输出中**（服务端已过滤）。
  - 渲染规则详见 `references/output/output-talent-profile.md` §3 渲染细则。
- `section3_5` **可能不存在**（无 AI 用量数据时服务端已过滤）。存在时：`title` 字段为格式化标题（如 `AI 用量（20260428~20260512）`），`ai_model_usage` 数组按 `time_range` 合并（ES 按 `is_mitclaw` 拆分，工具层已汇总），每个元素包含 `time_range`（时间范围）、`total_token_usage`（Token 总用量）、`total_cost_amt`（费用）。
- `section2_5` **可能不存在**（无外部履历时服务端已过滤）。存在时：`resume_work_infos` 数组，每个元素包含 `start_date`（开始时间）、`end_date`（结束时间）、`company_name`（公司名称）、`job_title`（职位名称）。
- `section4` **可能不存在**（无生涯事件时服务端已过滤）。存在时：`rows` 的 `eft_dt` 是 **YYYYMMDD 整数**（如 `20260221`），渲染时切片为 `YYYY-MM-DD`；`typ` 是事件大类（`晋升 / 转正 / 入离职 / 培训 / 奖项 / 岗位调整`），`actn_typ` 是细分动作（如 `试用转正 / 入职 / 离职`），渲染时按需做中文聚合。

**段位级容错**：任一段位无有效数据时，该段 key **不出现在输出中**（服务端已过滤，无错误信息透传）。LLM **不要**因为某段缺失就重试整个工具或拒答——**整张卡片仍发送**。

---

## 四、错误处理（单一权威来源）

> 本节是 `talent_profile` 工具错误处理的**唯一规范**。所有重试 / 兜底 / 禁止替代规则均以本节为准。

**顶层错误**（`{"error": "..."}`，含超时、查询失败等）：

1. **重试 1 次**：再次调用 `talent_profile`，参数完全不变
2. 仍失败 → 回复："人才档案查询暂时繁忙，请稍后再试"

**绝对禁止**：
- ❌ 在工具返回错误后自行编写 SQL / DSL 查询
- ❌ 自行拼凑档案 6 段数据
- ❌ 调用 `sql_query` / `es_query` 替代 `talent_profile`（含锚点失败、自查拦截等所有兜底场景，详见 §六 红线4）

**段位级失败**：单段无数据时**不重试**整个工具，该段隐藏，整张卡片仍发送（详见 §三 · 2.4）。

**权限拒答**：工具返回权限拒绝（来自 sql_core_v2 / es_core 的标准话术）时**直接输出并立即停止**。禁止换姓名/工号重试，禁止猜测或编造员工标识。

---

## 五、多人查询规则

1. **逐一调用**：`talent_profile` 一次只查一个人，多对象按出现顺序逐一调用
2. **独立填充**：每个员工独立一张卡片，**严禁**把员工 A 的字段填进员工 B 的卡片。逐人核对：每张卡片中出现的姓名/工号/oprid 必须严格等于该次工具返回的 `header.emp_nm` / `header.oprid` / `header.emp_id`
3. **失败终止**：任一员工返回权限拒绝则**立即停止所有后续调用**，已成功生成的卡片也**不发送**
4. **多轮隔离**：每次档案请求**独立处理**。即使用户连续问"再查下 YYY"，YYY 的卡片必须仅基于本轮 `talent_profile` 的返回数据，**不得**引用上一轮 XXX 卡片中的任何字段、结论、上下级关系

---

## 六、红线规则

> 红线适用于卡片所有 markdown 元素，**优先级最高**，输出前必须逐条对照。

**红线1：缺数据不编造**
任一字段缺失，对应行**隐藏**，**严禁**用对话历史/常识/猜测填充。
- ❌ 用对话上文出现过的他人数据填充当前空字段
- ❌ 因 SQL 段失败而用 ES 字段强行兜底（反之亦然）
- ✅ 字段缺失 → 整行隐藏；段位无数据 → 整段隐藏（服务端已过滤，不透传错误信息）

**红线2：数据原样**
`tag_info_str`、`performance_records.advantage / to_be_improved`、周报摘要等文本字段**直出 raw**，v0 不做 LLM 二次归纳，不做事实改写、合并、风格化。
- ❌ "他在 XX 项目表现出色"（原文未出现的总结）
- ❌ 把 raw 优势文本概括为 "沟通能力强、技术扎实"
- ✅ 多条优势用 `；` 分隔逐条输出

**红线3：跨员工不串数据**
详见 §五 多人查询规则 第 2、4 条。

**红线4：绕过工具 = 严重错误（单一权威）**
禁止用 `sql_query` / `es_query` 自行拼接档案卡片替代 `talent_profile` 工具，**包括**所有兜底场景：
- ❌ 锚点失败时改用 `sql_query` 模糊查
- ❌ 顶层 error 时用 `es_query` 拉员工资料拼卡
- ❌ 自查拦截后绕过工具直接渲染目标信息
- ✅ 唯一允许：调用 `talent_profile` → 按本文件 §三 处理返回值

**红线5：底部跳转按钮（D21）**
工具返回的 `footer_action.{text, url}` 必须渲染为卡片底部 action 按钮（多端 `multi_url`）。`url` 为空时按钮**整体隐藏**，**不要**展示空链接或灰按钮。按钮文案固定为「`<emp_nm>` 的人才档案」。

**红线6：敏感信息脱敏**
遵循 SKILL.md §约束与红线 §2 的脱敏规则：
- 绩效等级（S/A/B/C/D）**可作为筛选条件**但**不得逐人展示具体等级**——本档案 §2 的 `pfm` 由工具返回原值，**渲染层直显等级字母**（如 "B+"、"A"），不做映射转换
- 薪资 / 工时具体数值 / 排名名次 / 评价原文：一律不出现在卡片中
- 内部评价（performance_records.advantage / to_be_improved）：v0 直出 raw，但**不得引用上级/同事/下属评价的原文**——若 raw 中出现引号内的他人评价段落，渲染时改为综合归纳描述

**红线7：v0 LLM 归纳缺失**
v0 不接 LLM 归纳层。`section2.llm = null`、`section3.ai_focus = null`，§2 优劣势 / §4 ai_focus / 211/985/M级/管理规模等 LLM 加工字段统一以 raw 形态返回。**渲染层应保持容错**——缺失 LLM 子项不渲染相应行，§2.2 直出 `performance_records` 的 raw 文本。

---

## 七、输出渲染

**强制要求**：拿到工具返回 JSON 后，**必须读取 [output-talent-profile.md](../output/output-talent-profile.md) 全文**，按其卡片骨架（schema 2.0、indigo 配色、§1 ~ §6）填充占位并通过 `send_card()` 发送一张飞书 interactive 卡片，`receive_id` **必须使用 runtime context 中的 `Chat ID`**。

详细字段映射（dept_path / main_leader_real_name_path / 管理团队 / 标签行 / event_type 中文化等）见 output-talent-profile.md。
