# TALENT_PROFILE — 人才档案输出规范（mixed 通道 v0）

## 角色定位

组织档案 AI 问答助手，针对员工个体「档案」类问题，**一次返回**复合 6 段卡片：

| 段位 | 内容 |
|------|------|
| §1 基础信息 | 职位/职级/部门路径/汇报线/管理团队/学历/司龄 |
| §2 绩效 & 优劣势 | 近 2 期绩效（半年/年度 + 季度）行内展示 / 绩效评价（强项 & 待提升项） |
| §3 最近在做什么 | 周报 / Git / Meego / 内功修炼（完整原版） |
| §4 AI 模型用量 | Token 用量 / 费用 |
| §5 外部履历 | 加入小米前工作履历时间线（公司/职位/时间段） |
| §6 小米生涯 | 晋升 / 转正 / 入离职 / 培训 / 奖项 / 岗位调整 时间线（列表） |

---

## 一、工具调用前置校验（**调用前必须全部满足**）

1. **必须提供员工标识**：从用户问句中抽取姓名/工号/oprid 之一作为 `username`。提取不到时**不调用工具**，回复："请提供员工的姓名、工号或 oprid，例如「XXX 的人才档案」。"
2. **自查问句优先 Skill 层拦截**：识别到"我的档案 / 查我自己的档案"等自查问句时直接按 SKILL.md §1.1 输出引导话术，**不调用**工具；若漏判由工具层 `self_query_blocked` 兜底（详见 §2.4）。
3. **多人请求**：每人单独调用一次 `talent_profile`。任一调用返回权限拒绝，立即停止后续调用，已生成的卡片也不发送。

---

## 二、工具返回值结构（消费方契约）

`talent_profile` 返回 JSON 字符串，至少包含以下 4 种顶层结构之一：

### 2.1 锚点失败 — 不渲染卡片

```json
{"card_type": "anchor_fail", "status": "not_found", "msg": "未找到员工: XXX"}
```

```text
{
  "card_type": "anchor_fail",
  "status": "multiple",
  "msg": "找到多名员工，请用工号精确指定（3）",
  "candidates": [
    {"emp_id": "<emp_id>", "emp_nm": "<emp_nm>", "oprid": "<oprid>"}
  ]
}
```

**渲染规则**：
- `not_found` → 直接展示 `msg`，引导用户补充工号
- `multiple` → 列出 `candidates` 让用户选择（**禁止自动挑一个**）

### 2.2 顶层错误 — 重试 1 次后兜底

```json
{"error": "人才档案生成失败: ..."}
```
重试 1 次仍失败回复："人才档案查询暂时繁忙，请稍后再试"。**绝对禁止**用 `sql_query` / `es_query` 自行拼数据替代。

### 2.3 正常卡片 payload

```text
{
  "card_type": "talent_profile",
  "header": {"emp_nm": "XXX", "oprid": "xxx", "emp_id": "10086", "is_self": false},
  "section1": {
    "label": "section1",
    "rows": [{
      "emp_id": "...", "emp_nm": "...", "oprid": "...",
      "pos_nm": "...", "pos_lvl": "...", "hire_pos_lvl": "...",
      "dept_nm": "...", "dept_path_nm": "\\小米公司\\...\\...",
      "dept_nm_lvl1": "...", "dept_nm_lvl2": "...", "dept_nm_lvl3": "...", "dept_nm_lvl4": "...",
      "last_hire_dt": "YYYY-MM-DD", "wrk_age_mi_y": 0, "age_y": 0, "gdr_cd": "M/F",
      "mng_emp_id": "...", "mng_oprid": "...", "mng_emp_nm": "...", "dir_sub_emp_cnt": 0,
      "frs_edu_deg_cd": "本科/硕士/博士", "frs_sch_nm": "...",
      "hi_edu_deg_cd": "...", "hi_sch_nm": "...",
      "cmp_chn_nm": "...", "bas_loc_nm": "...", "emp_sts_cd": "...",
      "new_grdt_flg": "Y/N", "fur_flg": "Y/N", "mng_flg": "Y/N", "yng_eng_flg": "Y/N", "blue_flg": "Y/N"
    }],
    "raw": "<原始 SQL Markdown>"
  },
  "section2": {
    "perf": {
      "label": "section2_1",
      "rows": [
        {"emp_id": "...", "pfm_prd": "2025H2", "pfm": "..."}
      ],
      "raw": "<原始 SQL Markdown>"
    },
    "half_yearly": "B(25H2)、A(25H1)",
    "quarterly": "B(26Q1)、B+(25Q4)",
    "perf_summary": {
      "strengths": [
        {"title": "能力概括标题", "details": ["证据归纳1", "证据归纳2"]},
        {"title": "强项2标题", "details": ["证据归纳3", "证据归纳4"]}
      ],
      "weaknesses": [
        {"title": "待提升项标题", "details": ["证据归纳4", "证据归纳5"]}
      ]
    },
    "llm": "summarized"
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
  "section3": {
    "weekly_report": [
      {"report_nm": "...", "time_range": "...", "work_list": [{"year": 2026, "week_of_year": 24, "content": "..."}]}
    ],
    "meego_metrics": {
      "recent_period": {"time_range": "...", "total_work_items": 10, "total_points": 30, "work_item_groups": [...]}
    },
    "git_metrics": {
      "recent_period": {"commit_cnt": 5, "commit_line_cnt": 200, "cr_cmnt_cnt": 3, "cr_line_cnt": 500},
      "previous_period": {...},
      "ratio": {"commit_ratio": 120, "commit_line_ratio": 80, "cr_line_ratio": 90}
    },
    "ai_focus": null
  },
  "section3_5": {
    "title": "AI 用量（2026-06-01 ~ 2026-06-15）",
    "ai_model_usage": [
      {
        "time_range": "2026-06-01 ~ 2026-06-15",
        "total_token_usage": 34818542,
        "total_cost_amt": 10.85
      }
    ]
  },
  "section4": {
    "label": "section4",
    "rows": [
      {"emp_id": "...", "typ": "晋升/转正/入离职/培训/奖项/岗位调整", "actn_typ": "...", "eft_dt": 20260221, "pos_lvl": "16", "pos_nm": "...", "dept_nm_path": "\\小米公司\\..."}
    ],
    "raw": "<原始 SQL Markdown>"
  },
  "footer_action": {
    "text": "XXX 的人才档案",
    "url": "https://archive.hr.mioffice.cn/talent-details?userId=xxx"
  },
  "_meta": {"version": "v0", "is_self_query": false, "llm_enabled": false}
}
```

**关键字段说明**：

- `section1.rows[0]` 单行字典，**优先用此处 SQL 字段**填 §1。注意命名：`mng_*` 上级三件套、`dir_sub_emp_cnt` 直属下属数、`wrk_age_mi_y` 司龄(年)、`last_hire_dt` 入职日、`frs_*/hi_*` 首/最高学历、`bas_loc_nm` 工作地、`*_flg` 标签位、`job_fml_frs_nm` 一级序列
- `section1.main_leader_real_name_path` 从 ES 提取的汇报线路径（如「CEO → VP → 总监 → 当前员工」），用于 §1 汇报线行渲染
- `section1.tag_info_str` 从 ES 提取的标签文本，用于 §1 管理团队级别、学历学校标签、年龄标签渲染
- `section2.perf.rows` 字段是 `pfm_prd / pfm`（**不是** pfm_period/pfm_score），`pfm` 即等级原值；`section2.perf.raw` 是原始 SQL Markdown（仅供调试，渲染不使用）；`section2.half_yearly` 和 `section2.quarterly` 是工具层已格式化的绩效行字符串（如 `B(25H2)、A(25H1)`），直接渲染即可
- `section2.perf_summary` 是 **绩效评价 LLM 归纳**（v1：多源评价数据经服务端 LLM 总结，原文不对外）。数据来源：转正评语、晋升评语、述职评审、近一年绩效评价、人才标签（含 360 评价标签）。对象结构，包含 `strengths`（强项列表，3~5 条）和 `weaknesses`（待提升项列表，3~5 条），**每条为结构化对象** `{"title": "能力概括标题", "details": ["归纳后的证据内容"]}`，details 为纯内容（无角色前缀），360 标签作为评价素材融入对应的强项或待提升项中。为空对象或两者均空数组时隐藏绩效评价部分。`section2.llm` 为 `"summarized"` 时表示 LLM 归纳成功，`null` 表示降级为 Python 提取（此时 details 为空数组，仅显示 title）。
- `section2_5.resume_work_infos` 是 **加入小米前履历**，数组结构，每个元素包含 `start_date`（开始时间）、`end_date`（结束时间）、`company_name`（公司名称）、`job_title`（职位名称）。为空数组时整段隐藏。
- `section3` 是 **结构化数据**，包含以下子字段：
  - `section3.weekly_report`：周报数组，每个元素包含 `report_nm`、`time_range`、`work_list[]`（`year`、`week_of_year`、`content`）。取最近 1 周按项目拆分展示。
  - `section3.meego_metrics`：Meego 项目管理数据，含 `recent_period`（`time_range`、`total_work_items`、`total_points`、`work_item_groups[]`）。
  - `section3.git_metrics`：Git 研发效能数据，含 `recent_period`（`commit_cnt`、`cr_cmnt_cnt` 等）、`previous_period`、`ratio`。
  - 以上三个子字段为空对象/空数组时对应子项隐藏，全部为空时整段 §3 隐藏。
- `section3_5` 是 **AI 模型用量独立板块**，包含 `title`（预格式化标题，如 `AI 用量（2026-06-01 ~ 2026-06-15）`）和 `ai_model_usage` 数组（工具层已按 `time_range` 合并，ES 原始数据按 `is_mitclaw` 拆分）。每个元素包含 `time_range`（时间范围）、`total_token_usage`（Token 总用量）、`total_cost_amt`（费用）。`ai_model_usage` 为空数组时整段隐藏。
- `section4.rows` 字段是 `typ / actn_typ / eft_dt`（**不是** event_type/event_dt/event_desc）；`typ` 已是中文（晋升/转正/入离职/培训/奖项/岗位调整），`eft_dt` 是 **YYYYMMDD 整数**（如 20260221），渲染时切片为 YYYY-MM；`section4.raw` 是原始 SQL Markdown（仅供调试，渲染不使用）
- `footer_action.url` 用于 §1 更多信息行超链接，**不再渲染底部按钮**

**段位级容错**：任一段位无数据时，该段 key **不出现在输出中**（服务端已过滤，无错误信息透传）。整张卡片仍发送。

### 2.4 自查拦截（D22）

`oprid == sender_id` 时工具直接返回（**不渲染卡片**）：

```json
{
  "card_type": "self_query_blocked",
  "msg": "本人档案查询暂不支持，请移步飞书 HR 人才档案小程序。",
  "applink": "https://applink.feishu.cn/client/mini_program/open?appId=cli_a2b6e4f5cdf8d062"
}
```

**渲染规则**：仅输出以下文案，**禁止**追加任何其他文字：

> 本人信息查询暂请移步至人才档案：https://applink.feishu.cn/client/mini_program/open?appId=cli_a2b6e4f5cdf8d062

---

## 三、飞书卡片发送流程

> **⚠️ 人才档案必须使用 `msg_type=interactive` 发送飞书交互卡片，严禁使用 `msg_type=text`。**

### 发送步骤

1. **拿到** `talent_profile` 工具返回的 JSON
2. **按顺序**填充下方卡片骨架的占位
3. **使用** `send_card()` 函数发送（参考 [references/report/send-card.md](../report/send-card.md)），`receive_id` **必须使用 runtime context 中的 `Chat ID`**

### 段位空数据策略（**总规则，优先级最高**）

> §2~§6 任一段**无数据**（对应 JSON key 不存在或数据为空）时，**整段隐藏**（包括段位标题、主体内容、`hr` 分隔线），**不展示任何"暂无数据"占位文案**。
>
> 例外：**§1 基础信息始终保留**——这是档案的最小可用单元。
>
> 段位内**单字段缺失**（如汇报线缺、标签缺）按各自渲染细则隐藏对应行，**不影响段位整体显示**。
>
> **章节序号连续性**：隐藏某段后，后续章节序号必须**顺延重排**，保证最终输出中章节序号从"一、"开始且连续不间断。例如：若 §3 最近在做什么 整段隐藏，则 AI 用量变为"三、"，外部履历变为"四、"，小米生涯变为"五、"。

### 卡片骨架（schema 2.0）

```yaml
schema: "2.0"
header:
  title:
    tag: "plain_text"
    content: "{emp_nm}({oprid}) · 人才档案"
  subtitle:
    tag: "plain_text"
    content: "{pos_nm} · {pos_lvl}级"
  template: "blue"
body:
  elements:
    # ── §1 基础信息（列表风格）──
    - tag: "markdown"
      content: |
        ##### **一、基本信息**
        - **岗位**：{pos_nm}（{job_fml_frs_nm} · {job_fml_scd_nm}）<!-- job_fml_frs_nm 为空时仅显示 {pos_nm}；job_fml_scd_nm 为空时不显示 · 及后续内容 -->
        - **部门**：{dept_path}
        - **职级/司龄**：{pos_lvl}级（已停留{pos_lvl_stay_years}年） / {wrk_age_mi_y} 年（{last_hire_dt} 入职）
        - **工作地**：{bas_loc_nm}
        - **年龄**：{age_y}岁（{age_tag}）· {gender}<!-- age_y 为空时整行隐藏 -->
        - **汇报线**：{main_leader_real_name_path}
        - **管理团队**：{管理团队行}
        - **最高学历**：{hi_edu_deg_cd}·{hi_school_tag}·{hi_sch_nm}<!-- hi_sch_nm 缺失时整行隐藏；school_tag 从 tag_info_str 提取 211/985，缺失时省略 -->
        - **第一学历**：{frs_edu_deg_cd}·{frs_school_tag}·{frs_sch_nm}<!-- frs_sch_nm 缺失时整行隐藏；hi 与 frs 相同时仍展示两行 -->
        - 更多信息查看 [TA的人才档案]({footer_action_url})
    - tag: "hr"

    # ── §2 绩效 & 优劣势 ──
    - tag: "markdown"
      content: |
        ##### **二、绩效 & 优劣势**
      margin: "0px 0px 4px 0px"
    - tag: "markdown"
      content: |
        - **近四次绩效（半年/年度）**：{half_yearly}（如 B(25H2)、A(25H1)、B(25H1)、A(24H2)）
      margin: "0px 0px 16px 0px"
    # ↓ 仅当 section2.quarterly 非空时输出此块；为空时整块隐藏
    - tag: "markdown"
      content: |
        - **近四次绩效（季度）**：{quarterly}
      margin: "0px 0px 16px 0px"
    - tag: "markdown"
      content: |
        **2.1 核心强项（多维度共识）**
        <font color='grey'>总结来源：总结近一年的转正、晋升、述职、绩效评价信息</font>

        🟢 **{strengths[0].title}**
        　　{strengths[0].details[0]}
        　　{strengths[0].details[1]}

        🟢 **{strengths[1].title}**
        　　{strengths[1].details[0]}
        　　{strengths[1].details[1]}
      margin: "0px 0px 16px 0px"
    - tag: "markdown"
      content: |
        **2.2 待提升项（多次被提及的建议）**
        <font color='grey'>总结来源：总结近一年的转正、晋升、述职、绩效评价信息</font>

        🟡 **{weaknesses[0].title}**
        　　{weaknesses[0].details[0]}
        　　{weaknesses[0].details[1]}
    - tag: "hr"

    # ── §3 最近在做什么（STAR_STATUS 格式一风格）──
    - tag: "markdown"
      content: |
        ##### **三、最近在做什么**
      margin: "0px 0px 4px 0px"
    - tag: "markdown"
      content: |
        **3.1 整体工作情况**
        <font color='grey'>数据来源：meego、OKR周报、米小研周报</font>
        <font color='grey'>统计周期：最近一个月 {meego_metrics.recent_period.time_range}</font>

        | 工作方向 | 投入占比（估算）% | 关键进展/备注 | 主要协同人 |
        |------|------|--------|--------|
        | {方向1} | {XX}% | {关键进展摘要} | {协同人名单} |
      margin: "0px 0px 16px 0px"
    - tag: "markdown"
      content: |
        **3.2 研发产出**
        <font color='grey'>数据来源：Git 代码统计</font>
        <font color='grey'>统计周期：近期 {recent_period.time_range} vs 往期 {previous_period.time_range}</font>

        | 维度 | 近期 | 往期 | 环比 |
        |------|------|------|------|
        | 提交次数 | {recent.commit_cnt} | {previous.commit_cnt} | {ratio.commit_ratio}% |
        | 提交行数 | {recent.commit_line_cnt} | {previous.commit_line_cnt} | {ratio.commit_line_ratio}% |
        | 评审行数 | {recent.cr_line_cnt} | {previous.cr_line_cnt} | {ratio.cr_line_ratio}% |
      margin: "0px 0px 16px 0px"
    - tag: "markdown"
      content: |
        **3.3 AI 项目工时**
        <font color='grey'>数据来源：Meego</font>
        <font color='grey'>统计周期：最近两周</font>

        | AI 类别 | 项目/需求 | 优先级 | 状态 | 任务数 | AI工时(天) |
        |---------|---------|--------|------|--------|------|
        | {emoji 类别} | {prj_nm}/{req_nm} | {priority} | {status} | {聚合后任务条数} | {聚合后points求和} |

        AI 相关工时占比：{ai_hours_sum} / {total_points} = {pct}%，AI工时合计：{ai_hours_sum}天
    - tag: "hr"

    # ── §4 AI 模型用量 ──
    - tag: "markdown"
      content: |
        ##### **四、AI 用量（{time_range}）**

        - 总 Token 用量：{total_token_usage:,}
        - 总费用：{total_cost_amt:.2f} 元
    - tag: "hr"

    # ── §5 外部履历 ──
    - tag: "markdown"
      content: |
        ##### **五、外部履历**

        - {start_date} ~ {end_date}，{company_name}，{job_title}
        - ...
    - tag: "hr"

    # ── §6 小米生涯 ──
    - tag: "markdown"
      content: |
        ##### **六、小米生涯**

        - **{YYYY-MM} [{事件标签}]**，{pos_lvl}级，{pos_nm}，{dept_nm_path（/ 分隔）}
        - **{YYYY-MM} [外派开始]**，外派至{asgn_loc_nm}，{pos_lvl}级，{pos_nm}，{dept_nm_path}
        - ...
```

### §1 渲染细则

0. **岗位行**（[S] pos_nm / job_fml_frs_nm / job_fml_scd_nm）：
   - 主形态：`{pos_nm}（{job_fml_frs_nm} · {job_fml_scd_nm}）`
   - `job_fml_frs_nm` 为空 → 仅显示 `{pos_nm}`
   - `job_fml_scd_nm` 为空 → 不显示 `· ` 及后续内容，退化为 `{pos_nm}（{job_fml_frs_nm}）`

1. **部门路径 dept_path**：
   - 数据源：[S] `dept_nm_lvl1` ~ `dept_nm_lvl4` 顺序拼接（缺失级别跳过），回退 [S] `dept_path_nm` 去前缀
   - 去掉「\小米公司\」前缀，**从一级部门开始**
   - 各级用「 - 」（前后空格）分隔
   - 例：「集团信息技术部 - 企业智能协同部 - 人力协同研发部 - 基础人事研发组」

2. **职级/司龄行**：
   - 主形态：`{pos_lvl}级（已停留{pos_lvl_stay_years}年） / {wrk_age_mi_y} 年（{last_hire_dt} 入职）`
   - `pos_lvl_stay_years` 计算：当前日期与最近一次职级变动日期（section4 中 typ=晋升/降级 的最新 eft_dt）之差，单位年（保留1位小数）；无晋升记录时用 `last_hire_dt` 计算
   - `wrk_age_mi_y` 保留1位小数

3. **工作地行**：
   - 数据源：[S] `bas_loc_nm`（工作地）
   - 缺失时整行隐藏

4. **年龄行**（[S] age_y / gdr_cd + tag_info_str）：
   - 主形态：`{age_y}岁（{age_tag}）· {gender}`
   - `age_tag`：从 `tag_info_str` 中提取年代标签（80后/85后/90后/95后/00后），缺失时省略括号
   - `gender`：`gdr_cd=M` → 男，`gdr_cd=F` → 女，其他 → 隐藏性别部分
   - `age_y` 为空 / 0 → **整行隐藏**

5. **汇报线 main_leader_real_name_path**：
   - 数据源：`section1.main_leader_real_name_path`（从 ES 提取，已合并到 section1）
   - 原文是分隔符串接（含「、」或「\」），先按分隔符拆分为列表，**反转顺序**后用「 → 」拼接
   - 自底向上渲染（当前员工 → 直属上级 → ... → CEO）
   - **无论路径多长，必须完整展示全部层级，禁止截断、省略或用"..."替代**
   - 缺失则隐藏整行

6. **管理团队**（`section1.tag_info_str` + [S] dir_sub_emp_cnt 组合）：
   - 从 `section1.tag_info_str` 中抽取 `管理信息_【最高】管理部门级别:XXX` 的 XXX 值
   - 若 XXX = "非部门管理者" / 为空 / [S] mng_flg=N → **整行隐藏**
   - 否则渲染为 "{XXX}（直接下属{dir_sub_emp_cnt}人）"（注意：是"直接下属X人"不是"共X+直接下属"）

7. **学历行**（[S] frs_*/hi_* + tag_info_str）：
   - 从 `tag_info_str` 中提取学校标签（211/985），插入学历与校名之间
   - 始终展示两行（无论 hi 与 frs 是否相同）：
     - `**最高学历**：{hi_edu_deg_cd}·{hi_school_tag}·{hi_sch_nm}`
     - `**第一学历**：{frs_edu_deg_cd}·{frs_school_tag}·{frs_sch_nm}`
   - hi 缺失时隐藏最高学历行，仅展示第一学历行
   - `school_tag` 从 `tag_info_str` 中匹配（如"211""985""双一流"），缺失时省略该段（不输出 `··`）
   - frs_sch_nm 缺失则隐藏第一学历行

### §2 渲染细则

6. **绩效行内展示**（[S2] section2.half_yearly / section2.quarterly）：
   - 工具层已按期次类型分组并格式化，直接使用 `section2.half_yearly` 和 `section2.quarterly` 字符串
   - 半年度/年度和季度为**两个独立 markdown element**：
     - `**近四次绩效（半年/年度）**：{section2.half_yearly}`（格式如 `B(25H2)、A(25H1)、B(25H1)、A(24H2)`）
     - `**近四次绩效（季度）**：{section2.quarterly}`（格式如 `B(26Q1)、B+(25Q4)、B(25Q3)、A(25Q2)`）
   - `section2.quarterly` 为空串时**整个季度 element 隐藏**（不输出该 markdown 块）
   - `section2.half_yearly` 也为空 → 绩效行隐藏；ES 优劣势也缺 → 整段 §2 隐藏

7. **绩效评价**（[E] section2.perf_summary）：
   - 数据源：`section2.perf_summary` 对象，包含 `strengths`（强项列表）和 `weaknesses`（待提升项列表），已由服务端 LLM 多源归纳（v1：转正评语、晋升评语、述职评审、近一年绩效评价、人才标签综合总结，原文不对外）
   - **数据结构**：每条为结构化对象 `{"title": "能力概括标题", "details": ["证据/归纳1", "证据/归纳2"]}`
     - `title`：精炼的能力概括（加粗显示）
     - `details`：归纳后的证据列表（无角色前缀），360 标签作为评价素材融入对应条目
     - 降级模式（`llm=null`）：`details` 为空数组，仅显示 `title`（原文提取）
   - 渲染格式（全角空格缩进，编号子标题 + 总结来源灰色字体）：
     - details 每条独立一行，用全角空格 `　　` 缩进（不合并为段落）
     - 总结来源使用 `<font color='grey'>` 灰色字体，与 §3 数据来源格式一致
     ```
     **2.1 核心强项（多维度共识）**
     <font color='grey'>总结来源：总结近一年的转正、晋升、述职、绩效评价信息</font>

     🟢 **{title}**
     　　{details[0]}
     　　{details[1]}

     **2.2 待提升项（多次被提及的建议）**
     <font color='grey'>总结来源：总结近一年的转正、晋升、述职、绩效评价信息</font>

     🟡 **{title}**
     　　{details[0]}
     　　{details[1]}
     ```
   - `section2.llm` 为 `"summarized"` 表示 LLM 归纳成功，`null` 表示降级为 Python 提取
   - `strengths` / `weaknesses` 为空数组时对应子标题隐藏；两者均空 → 隐藏绩效评价部分；`perf.rows` 也空 → 整段 §2 隐藏

### §3 渲染细则（STAR_STATUS 格式一风格）

8. **最近在做什么** — **必须包含以下 3 个子标题**（按此顺序），每个子章节独立裁剪（无数据的子章节隐藏，但不得合并或省略子标题结构）：

   ```
   **3.1 整体工作情况**
   **3.2 研发产出**
   **3.3 AI 项目工时**
   ```

   > ⚠️ **输出自检**：§3 渲染完成后必须逐项检查 3 个子标题是否齐全。缺少任何一个子标题 = 格式违规。

   #### 8a. 整体工作情况
   - **数据源**：`section3.meego_metrics` + `section3.weekly_report`
   - **渲染规则**：
     - 工作方向**只能**从 `weekly_report.work_list` 和 `meego_metrics.recent_period.work_item_groups` 中提取，**严禁**基于 git_metrics、ai_model_usage 等其他字段推断或虚构工作方向
     - 按"工作方向"维度聚合（非逐条罗列），按投入占比从高到低排序
     - **投入占比估算**（三维度综合推断，总和约 100%）：
       - **维度一：Meego 任务数（权重最高）**：统计每个方向下的 work_item_groups 条数，同一项目的不同需求应合并为同一方向
       - **维度二：周报连续性**：该方向在 weekly_report 中被提及的周数，连续 3-4 周持续推进 = 高投入，仅偶尔提及 = 极低投入
       - **维度三：优先级**：P0 权重显著高于 P1/P2/P3，有延期的项目实际投入可能低于任务数暗示的量
       - 综合判断示例：4 tasks + 连续4周 + P0 + 新项目 ≈ 40%；周报仅一句话提及 ≈ 5-10%
     - **主要协同人**：从该方向对应的 `work_item_groups` 的 `collaborators` 按出现频次降序取前 5 人，纯姓名顿号串（如"张三、李四、王五"）
     - 若该方向仅来自 `weekly_report`（无对应 meego 任务或 collaborators 为空）→ 填 `—（来自周报，无协同人数据）`
     - **仅展示近期（recent_period），严禁输出往期数据**
   - **数据源标题**：章节标题下方必须有连续 2 行 `<font color='grey'>`：
     - 第 1 行：`<font color='grey'>数据来源：meego、OKR周报、米小研周报</font>`
     - 第 2 行：`<font color='grey'>统计周期：最近一个月 {meego_metrics.recent_period.time_range}</font>`
   - `weekly_report` 不存在且 `meego_metrics.recent_period` 不存在 → **整子章节隐藏**

   #### 8b. 研发产出
   - **数据源**：`section3.git_metrics`（`recent_period` / `previous_period` / `ratio`）
   - **渲染规则**：
     - 表格列：维度 | 近期 | 往期 | 环比
     - 行：提交次数 / 提交行数 / 评审行数
     - 所有数值**必须直接取自** `git_metrics` 原始字段，禁止用文字叙述替代（如"较多"、"活跃"等）
     - 环比直接使用 `ratio` 字段百分比
   - **数据源标题**：连续 2 行 `<font color='grey'>`：
     - 第 1 行：`<font color='grey'>数据来源：Git 代码统计</font>`
     - 第 2 行：`<font color='grey'>统计周期：近期 {recent_period.time_range} vs 往期 {previous_period.time_range}</font>`
   - `git_metrics` 不存在 → **整子章节隐藏**

   #### 8c. AI 项目工时
   - **数据源**：`section3.meego_metrics.recent_period.work_item_groups`
   - **渲染规则**（完整流程）：
     1. **确定最近两周范围**：从 `time_range` 结束日期往前推 15 天
     2. **时间过滤**：只保留 `bgn_dt` 或 `end_dt` 落在该范围内的记录
     3. **AI 关键词匹配**：`prj_nm`/`req_nm`/`task_nm` 命中以下关键词（大小写不敏感）：
        ```
        龙虾|虾米|openclaw|虾塘|虾钳|虾身|虾壳|虾眼|虾|claw|vaf|mcp|skill|cli|agent|大模型|llm|copilot|智能体|ai|chatgpt|claude
        ```
        - 不包含 `智能` 单独关键词（范围太广）
     4. **分类（每条记录只归入一个最高优先级类别）**：按优先级从高到低依次匹配，命中第一个即归类，不再往下判断：
        - 🦞龙虾(1)：命中 `龙虾|虾米|openclaw|虾塘|虾钳|虾身|虾壳|虾眼|虾|claw`
        - 🔧MCP/CLI/Skills(2)：命中 `mcp|skill|cli`（且未命中龙虾）
        - ⚡VAF(3)：命中 `vaf`（且未命中龙虾）
        - 🎯Agent(4)：命中 `agent|智能体`（且未命中龙虾）
        - 🤖其他AI(5)：命中剩余 AI 关键词（且未命中以上任何类别）
     5. **聚合**：按 `prj_nm + req_nm` 聚合，输出明细表格 + 占比总结行
     6. **明细表格**按类别优先级排列，同类别内按 points 降序
     7. **占比总结行**：`AI 相关工时占比：{表格 AI 工时列求和} / {total_points} = {百分比}%，AI工时合计：{求和}天`
   - **数据源标题**：连续 2 行 `<font color='grey'>`：
     - 第 1 行：`<font color='grey'>数据来源：Meego</font>`
     - 第 2 行：`<font color='grey'>统计周期：最近两周 {start_date} ~ {end_date}（当前日期往前推 15 天）</font>`
   - 时间过滤后无 AI 关键词命中 → **整子章节隐藏**

   #### §3 整段裁剪
   - 3 个子章节**全部隐藏** → 整段 §3 隐藏（标题+hr 都不渲染）
   - 任一子章节有数据 → §3 标题保留，仅渲染有数据的子章节

### §4 渲染细则

> **段位编号映射**：JSON key 为 `section3_5`，渲染输出中为 **§4 AI 模型用量**（因 section3 是"最近在做什么"，section3_5 是其后插入的独立板块，渲染时顺延为 §4）。

9. **AI 模型用量**（[E] section3_5）：
   - 数据源：`section3_5.ai_model_usage` 数组，每个元素是一个时间周期的用量数据
   - 标题使用 `section3_5.title`（格式：`### **AI 用量（{time_range}）**`），为空时不渲染标题
   - 仅展示以下字段（取最新周期）：
     - Token 总用量：`{total_token_usage:,}`
     - 费用：`{total_cost_amt:.2f} 元`
   - 渲染格式：
     ```
     ### **AI 用量（{time_range}）**

     - 总 Token 用量：{total_token_usage:,}
     - 总费用：{total_cost_amt:.2f} 元
     ```
   - `section3_5` key 不存在或 `ai_model_usage` 为空数组 → 整段 §4 隐藏

### §5 渲染细则

10. **外部履历**（[E] section2_5.resume_work_infos）：
   - 数据源：`section2_5.resume_work_infos` 数组，每个元素是一个工作经历
   - 渲染为独立板块，标题：`### **外部履历**`
   - 每条履历格式：`- {start_date} ~ {end_date}，{company_name}，{job_title}`
   - 按时间倒序排列（最新在前）
   - `section2_5` key 不存在或 `resume_work_infos` 为空数组 → 整段 §5 隐藏

### §6 渲染细则

11. **小米生涯**（[S4] section4.rows）：
   - **格式约束**：必须使用列表风格（与 §5 外部履历一致），**严禁使用表格**
   - 数据源：`section4.rows`，按 `eft_dt` 倒序
   - 每条格式：`- **{YYYY-MM} [{事件标签}]**，{pos_lvl}级，{pos_nm}，{dept_nm_path}`
   - 时间：`eft_dt` 整数切片为 `YYYY-MM`，**加粗**；事件标签用 **方括号 []** 包裹，与日期同在一个加粗段内
   - 事件标签：`typ=外派` 时直接用 `actn_typ`，`actn_typ=外派开始` 且 `asgn_loc_nm` 存在时追加 `，外派至{asgn_loc_nm}`；`typ=晋升/降级` 时直接用 `actn_typ`（晋升或降级）；其他类型若 `actn_typ ≠ typ` 则拼接 `{typ}·{actn_typ}`，否则只用 `{typ}`
   - 部门：`dept_nm_path` 去掉 `\小米公司\` 前缀，各级用 **`/`** 分隔（如"国际业务部/东南亚地区部"）
   - 缺失字段：该位置留空，不输出占位文字
   - `section4` key 不存在或 `rows` 为空 → 整段 §6 隐藏

---

## 四、红线规则

1. **缺数据不编造**：任一字段缺失，按"段位空数据策略"处理——单字段缺失隐藏对应行，子模块整体无数据则**整段隐藏**（§2/§3/§4/§5/§6）；**严禁**用"暂无数据"占位文案，**严禁**用对话历史/常识/猜测填充。
2. **数据原样**：`tag_info_str`、`performance_records.advantage/to_be_improved` 精简输出，v0 不做 LLM 二次归纳，不做事实改写。
3. **跨员工不串数据**：多人请求时每个人独立一张卡片，**严禁**把员工 A 的字段填进员工 B 的卡片。
4. **绕过工具 = 严重错误**：禁止用 `sql_query` / `es_query` 自行拼接档案卡片替代 `talent_profile` 工具（含 `self_query_blocked` / `anchor_fail` / 顶层 error 等所有兜底场景）。
5. **链接位置**：档案跳转链接放在 §1 更多信息行，**不渲染底部按钮**（飞书 schema 2.0 已废弃 `tag: action`）。
6. **输出前自检清单**（每次输出前必须逐项核对）：
   - [ ] 卡片标题是否为 `{emp_nm}({oprid}) · 人才档案`，副标题是否为 `{pos_nm} · {pos_lvl}级`？
   - [ ] §1 是否包含 **岗位/部门/职级司龄/工作地/年龄/汇报线/管理团队/学历/更多链接** 全部行（缺失字段对应行隐藏）？
   - [ ] §1 汇报线是否自底向上（员工 → ... → CEO）且完整展示全部层级？
   - [ ] §2 优劣势是否使用 **2.1 核心强项（多维度共识）** / **2.2 待提升项（多次被提及的建议）** 编号？每条强项前是否有 🟢 标记？每条待提升项前是否有 🟡 标记？details 是否每条独立一行（全角空格缩进，非 `。` 合并）？
   - [ ] §3「最近在做什么」是否包含 **3.1 整体工作情况**、**3.2 研发产出**、**3.3 AI 项目工时** 三个子标题？缺少任何一个 = 格式违规
   - [ ] §6「小米生涯」是否使用 **列表格式** 且日期加粗 + 事件标签用方括号（`- **{YYYY-MM} [{事件标签}]**，...`）？使用表格 = 格式违规
   - [ ] §5 外部履历和 §6 小米生涯是否格式一致（均为列表）？
   - [ ] 有章节被隐藏时，后续章节序号是否顺延重排（从"一、"开始连续不间断）？

---

## 五、容错与降级速查

| 场景 | 工具返回特征 | 渲染处理 |
|------|------------|---------|
| 锚点未命中 | `card_type=anchor_fail, status=not_found` | 展示 `msg`，引导补工号 |
| 锚点多命中 | `card_type=anchor_fail, status=multiple` | 列 `candidates`，让用户选 |
| 自查兜底 | `card_type=self_query_blocked` | **仅输出**飞书 HR 人才档案 applink |
| 顶层错误 | `{"error": "..."}` | 重试 1 次，仍失败兜底文案 |
| §1 段位失败 | SQL/ES 异常 | §1 始终保留（保底），字段缺失行隐藏 |
| §2 段位空 | `perf.rows=[]` 且 `perf_summary` 为空 | **整段 §2 隐藏** |
| §2 部分空 | rows 空但 strengths/weaknesses 有值 / 仅缺其一 | 隐藏绩效行 / 隐藏对应子标题，段位仍展示 |
| §3 段位空 | 3 子项全缺（weekly_report/meego/git） | **整段 §3 隐藏** |
| §3 部分空 | 子项部分缺失 | 缺失子项隐藏，段位仍展示 |
| §4 段位空 | `section3_5` 不存在或 `ai_model_usage=[]` | **整段 §4 隐藏** |
| §5 段位空 | `section2_5` 不存在或 `resume_work_infos=[]` | **整段 §5 隐藏** |
| §6 段位空 | `section4` 不存在或 `rows=[]` | **整段 §6 隐藏** |
| LLM 归纳降级（v1） | `section2.llm=null` | §2 降级为 Python 提取原文，精简直出；`llm="summarized"` 为正常 LLM 归纳 |
