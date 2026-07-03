# onboarding_report 返回结构与模板映射

> **命名**：接口以 **snake_case** 为准（如 `dept_name`）。部分环境可能返回 camelCase 别名（`deptName`），含义相同。  
> **填表**：路径 → 模板章节；数值原样输出，禁止 LLM 重算归因残差。  
> **列表顺序**：所有 `[]` 保序、截断与允许加工的规则以 `onboarding-report.md` [§4.4 红线 1](../onboarding-report.md#44-红线规则输出前逐条校验) 为准。  
> **缺失填 0**：列表缺项、`null`、无记录时人数填 `0`、比率填 `0.0`；禁止 `-`/空单元格（除非本节另有说明）。

---

## 一、响应信封

| 字段 | 类型 | 含义 | LLM 处置 |
|------|------|------|----------|
| `code` | int | `0` 成功；`4031` 无报告权限；`4221` 部门多候选；`4032` 部门无权限；`4041` 部门未找到/越权；`5001` 内部异常 | 非 `0` 不填模板，输出 `message` |
| `message` | string | 业务消息或异常文案 | 成功为 `"success"` |
| `data` | object\|null | 报告主体；失败为 `null` 或含 `candidates` | 仅 `code=0` 时使用 |

---

## 二、data 元信息

| 字段 | 类型 | 含义 | 模板占位符 |
|------|------|------|------------|
| `dept_id` | string | 解析后的部门 ID（集团常为 `"MI"`） | — |
| `dept_name` | string | 部门展示名；剔除子部门时为 `"XX(除YY)"` | `{dept_display_name}`、飞书文档标题、摘要 `header.title` |
| `dept_field` | string\|null | 命中层级字段 `dept_id_lvl1`~`lvl6`；集团全量为 `null` | — |
| `time_range` | string | 统计窗口 `start_dt~end_dt`（**无空格**，半开区间语义以工具为准） | 拆为 `{start_dt}`、`{end_dt}`；展示见下 |

**标题与时间窗（SSOT；`onboarding-report.md` §4.3 摘要卡片与飞书文档标题均须与本节一致）**

| 占位符 | 推导 |
|--------|------|
| `{start_dt}` / `{end_dt}` | `time_range` 按 `~` 拆分；或与 `onboarding_report` 入参 `start_dt`、`end_dt` 相同（`YYYY-MM-DD`） |
| `{time_window_display}` | `{start_dt} ~ {end_dt}`（`~` 两侧各一空格） |
| 飞书文档标题 / 摘要 `header.title` | `【官方精选报告】{dept_display_name} · 新人入职报告（{time_window_display}）` |

> **禁止**将时间窗写成 `2025全年`、`2025.05~2026.05`、仅年月、自然语言等；模板正文与标题中的日期必须与 `{start_dt}`、`{end_dt}` 一致。
>
> **部门展示名强约束**：凡对外展示部门名（文档标题、卡片标题、正文 `{dept_name}` 占位符）均使用 `data.dept_name`（即 `{dept_display_name}`），**禁止**使用用户原始入参 `dept_name` 回填。

---

## 二-B、dep_impact（字段有值时用于 IM 卡片"数据说明"）

**路径**：`data.dep_impact`  
**条件**：仅当 `dep_impact` 存在且非 `null` 时输出数据说明；若缺失或为 `null` 则不输出。  
**用途**：不在报告正文中单独成节，仅用于 IM 摘要卡片的"数据说明"行。

| 字段 | 类型 | 含义 |
|------|------|------|
| `dep_hire_cnt` | int | 该部门入职人数 |
| `non_dep_hire_cnt` | int | 非该部门入职人数 |
| `total_hire_cnt` | int | 全公司总入职人数 |
| `dep_pct` | float | 该部门人数占比（0~100，保留 1 位小数） |

**IM 数据说明派生字段**：
| 占位符 | 推导方式 |
|--------|----------|
| `{adjusted_hire_rate}` | LLM 基于 `dep_impact` 计算剔除 DEP 后占集团入职占比 = `non_dep_hire_cnt / total_hire_cnt * 100`，保留 1 位小数（等价于 `100 - dep_pct`） |

> `dep_impact` 为 `null` 时不输出数据说明行。`Q%` 仅依赖 `dep_impact` 推导，不需要再依赖 `d1_overall`。

---

## 三、D1 整体规模与流入 → 第1章

**路径**：`data.d1_overall`  
**口径**：正式员工 + 外包A + 外包B + 外部顾问A（非仅正式）

### 3.1 `monthly_numbers_list[]` → §1.2 月度入职趋势

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `mon` | string | 年月 `YYYY-MM` | 月份 |
| `hire_count` | int | 当月入职人数 | 入职人数 |

> 无同比字段；勿编造同比列。

### 3.2 `by_emp_type` → §1.1、§1.3

五个子列表独立查询，单项失败时该子列表为 `[]`。

#### `hire_list[]`（D1-2a 入职）

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `emp_type` | string | `正式员工` / `外包A` / `外包B` / `外部顾问A` | §1.1 列名 |
| `hire_count` | int | 入职人数 | 行「入职人数」 |

#### `active_list[]`（D1-2b 在职，`emp_sts_cd='A'`）

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `emp_type` | string | 员工类型 | §1.1 列名 |
| `active_count` | int | 在职人数 | 行「在职人数」 |

#### `tmn_list[]`（D1-2c 离职，`emp_sts_cd='I'`）

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `emp_type` | string | 员工类型 | §1.1 列名 |
| `tmn_count` | int | 离职人数 | 行「离职人数」 |

#### `tmn_rate_list[]`（D1-2d 离职率）

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `emp_type` | string | 员工类型 | §1.1 列名 |
| `hire_count` | int | 同期入职人数（**分母**） | — |
| `tmn_count` | int | 同期离职人数（**分子**） | — |
| `tmn_rate_pct` | float | 离职率百分比（**已 ×100**，保留 1 位；工具按 `tmn_count/hire_count×100` 计算） | 行「离职率(%)」 |

#### §1.1 填表

- 四行数据：分别取自 `hire_list` / `active_list` / `tmn_list` / `tmn_rate_list`，按 `emp_type` 对齐模板四列；合计列为各 list 对应字段之和（离职率除外）。
- 某类型无记录或 null → 人数 **0**、离职率 **0.0**（遵守文首「缺失填 0」）。
- 各类型离职率：原样输出 `tmn_rate_pct`（分母=同期 `hire_count`；hire=0 时为 0.0%）；禁止 LLM 重算。
- 合计离职率：`round(Σtmn_count / Σhire_count × 100, 1)`；禁止对四列离职率算术平均（同 `{tmn_rate_all_pct}`）。

#### `psv_active_list[]`（D1-2e 主/被动）

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `resign_type` | string | `主动` / `被动` / `未知` | §1.3 主被动离职 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（**已 ×100**） | 占比 |

### 3.3 D1 汇总占位符（LLM 可推导）

| 占位符 | 推导 |
|--------|------|
| `{hire_cnt_all}` | `hire_list` 各项 `hire_count` 之和 |
| `{hire_cnt_fte}` | `emp_type==="正式员工"` 的 `hire_count` |
| `{hire_fte_pct}` | `{hire_cnt_fte}/{hire_cnt_all}×100` |
| `{active_cnt_all}` | `active_list` 之和 |
| `{tmn_cnt_all}` | `tmn_list` 之和 |
| `{tmn_rate_all_pct}` | 同 §1.1 合计离职率公式 |
| `{tmn_cnt_fte}` / `{tmn_rate_fte_pct}` | 正式员工行 `tmn_count` / `tmn_rate_pct` |
| `{passive_cnt}` | `d1_overall.by_resign_type` 中 `resign_type==="被动离职"` 的 `cnt` |
| `{passive_pct}` | `passive_cnt / tmn_cnt_all × 100`，保留整数 |
| `{active_cnt}` | `d1_overall.by_resign_type` 中 `resign_type==="主动离职"` 的 `cnt` |
| `{active_pct}` | `active_cnt / tmn_cnt_all × 100`，保留整数 |
| `{report_period}` | 查询参数中的时间范围，如"25年"、"2025年1-6月" |
| `{ch1_breakdown_by_type}` | **动态生成**：遍历 `hire_list` 中除正式员工外的所有 `emp_type`，仅输出离职率。格式为 `[类型]离职率X%`，多类型用顿号 `、` 分隔。示例：`外包B离职率63.1%、外部顾问A离职率100%`。不输出入职/在职/离职人数（这些已在第1章表格中展示）。 |
| `{ch1_breakdown_tmn_by_type}` | **动态生成**：遍历非正式 `emp_type` 的离职人数，格式为 `外包B X人、外部顾问A Y人`，用顿号分隔。仅输出实际存在的类型。 |

> D1 **无**全口径校招/社招；见 D2 `by_recruit_type`。

---

## 四、D2 新人画像 → 第2章

**路径**：`data.d2_profile`  
**口径**：仅正式员工 `real_emp_cls_cd='101'`

### 4.1 按模板章节顺序（§2.1～§2.11）

#### `by_dept[]` → §2.1 部门分布

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `sub_dept` | string | 子部门名（动态下钻：查 lvlK 展示 lvlK+1，封顶 lvl6） | 子部门 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

#### `by_location[]` → §2.2 工作地分布

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `work_loc` | string | 工作地点 | 工作地 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

#### `by_manager[]` → §2.3 管理者分布

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `is_manager` | int | `0` 非管理者，`1` 管理者（`all_sub_emp_cnt>0`） | 是否管理者 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

#### `by_pos_lvl_recruit[]` → §2.4 职级 × 校社招交叉

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `pos_lvl` | int | 职级数字 | 职级 |
| `cam_cnt` | int | 校招人数 | 校招 |
| `soc_cnt` | int | 社招人数 | 社招 |
| `cnt` | int | 总数（校招+社招） | 合计 |
| `pct` | float | 占比（已 ×100） | 占比 |

**填表规则**

| 规则 | 说明 |
|------|------|
| 行顺序 | 按 `pos_lvl` 升序排列 |
| 列顺序 | 固定 `职级` → `校招` → `社招` → `合计` → `占比` |
| 禁止 | 表尾合计行；合计和占比直接取字段值，禁止自行计算 |

#### `by_work_age` → §2.5 社招工龄分布（仅社招 `new_grdt_flg=0`）

| 路径 | 字段 | 类型 | 含义 |
|------|------|------|------|
| `buckets[]` | `work_age_bucket` | string | `[0,3)`/`[3,5)`/…/`[12,+inf)` |
| `stats` | `scoped_cnt` | int | 参与统计的社招人数 |
| | `mean_v` / `median_v` | float | 平均 / 中位工龄（年） |

#### `by_gender[]` → §2.6 性别分布

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `gender` | string | `男` / `女` / `未知` | 性别 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

#### `by_age` → §2.7 年龄分布

| 路径 | 字段 | 类型 | 含义 |
|------|------|------|------|
| `buckets[]` | `age_bucket` | string | `[0,25)`/`[25,30)`/…/`[45,+inf)` |
| | `cnt` / `pct` | int / float | 人数 / 占比 |
| `stats` | `min_age` | float | 最小年龄 |
| | `max_age` | float | 最大年龄 |
| | `mean_age` | float | 平均年龄 |
| | `median_age` | float | 中位数年龄 |

无样本时 `stats` 为 `{}`。

#### `by_education` → §2.8 学历分布

| 路径 | 字段 | 类型 | 含义 |
|------|------|------|------|
| `highest[]` | `edu_lvl` | string | 最高学历名 |
| | `cnt` / `pct` | int / float | 人数 / 占比 |
| `first[]` | `first_edu_lvl` | string | 第一学历名 |
| | `cnt` / `pct` | int / float | 人数 / 占比 |

#### `by_school_type` → §2.9 学校类型分布

优先级：**清北 > C9 > 985 > 211 > QS100 > 其他**（及「其他学校类型」等返回值原样展示）

| 路径 | 字段 | 类型 | 含义 |
|------|------|------|------|
| `highest[]` | `hi_sch_type` | string | 最高学历学校类型 |
| `first[]` | `first_sch_type` | string | 第一学历学校类型 |

#### `by_overseas_edu[]` → §2.10 海外教育背景分布

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `is_overseas_edu` | int | `0` 无海外教育背景，`1` 有海外教育背景 | 海外教育背景 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

#### `by_prev_company[]` → §2.11 前公司 Top15

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `prev_company` | string | 前公司名（`talent_tag_f`，标签「过往公司」） | 前公司 |
| `cnt` | int | 人数 | 人数 |

> 最多 15 行，按接口返回顺序完整输出。

### 4.2 第2章小结 Top 项

| 占位符 | 来源 |
|--------|------|
| `{top_dept_name}` 等 | `by_dept` 按 `cnt` 最大项 |
| 职级 Top | `by_level` 最大 `cnt` 的 `pos_lvl` |
| 工作地 Top | `by_location[0]` |

---

## 五、D3 转正分析 → 第3章（§3.1~3.4）

**路径**：`data.d3_probation`  
**口径**：仅正式；答辩记录取每人最近一条

| 字段 | 类型 | 含义 |
|------|------|------|
| `fail_list_cnt` | int | 答辩建议不通过员工实际总人数（列表 `fail_list` 仅返回 Top 20） |
| `psv_within_90d_list_cnt` | int | 转正后 90 天内被动离职实际总人数（列表 `psv_within_90d_list` 仅返回 Top 20） |

### 5.1 `status_distribution[]` → §3.1

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `prc_status` | string | 转正/答辩状态；空值兜底 `"缺失"` | 状态 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

### 5.2 `score_stats` → §3.2

| 字段                 | 类型 | 含义        | 模板行     |
|--------------------|------|-----------|---------|
| `scored_cnt`       | int | 有效打分人数    | 员工数     |
| `mean_v`           | float | 平均分       | 平均分     |
| `std_v`            | float | 标准差       | 分数波动幅度    |
| `p10`              | float | 10分位      | P10（后 10% 水平）|
| `p25`              | float | 25分位      | P25（后 25% 水平） |
| `p50`              | float | 50分位      | P50（中位数）|
| `p75`              | float | 75分位      | P75（前 25% 水平）|
| `p90`              | float | 90分位      | P90（前 10% 水平）|
| `pass_active_mean` | float | 通过且在职转正均分 | 通过且在职转正均分|

无样本时为 `{}`。

### 5.3 `fail_list[]` → §3.3（≤5000）

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `emp_id` | string | 员工 ID | — |
| `name` | string | 姓名 | 姓名（账号）→ `{name}（{oprid}）` |
| `oprid` | string | 工号/账号 | 同上 |
| `dept_l1` | string | 一级部门 | 一级部门 |
| `dept_l2` | string | 二级部门 | 二级部门 |
| `position` | string | 岗位名 | — |
| `pos_lvl` | string | 职级（原始字符串） | 职级 |
| `manager` | string | 直接主管 | — |
| `hire_dt` | string | 入职日 `YYYY-MM-DD` | 入职日期 |
| `prc_dt` | string | 转正/答辩日 | 答辩日期 |
| `score` | float | 答辩分数 | 分数 |
| `prc_status` | string | 转正/答辩状态 | 转正状态 |
| `emp_status` | string | `A` 在职 / `I` 离职 | —（模板未展示，勿写入正文） |

`{fail_list_count}` = `d3_probation.fail_list_cnt`（接口返回的实际总人数，列表仅展示 Top 20）

### 5.4 `psv_within_90d_list[]` → §3.4（转正后 90 天内被动离职，≤5000）

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `emp_id` | string | 员工 ID | — |
| `name` | string | 姓名 | 姓名（账号）→ `{name}（{oprid}）` |
| `oprid` | string | 工号/账号 | 同上 |
| `dept_l1` | string | 一级部门 | 一级部门 |
| `dept_l2` | string | 二级部门 | 二级部门 |
| `position` | string | 岗位名 | — |
| `pos_lvl` | string | 职级（原始字符串） | 职级 |
| `manager` | string | 直接主管 | — |
| `hire_dt` | string | 入职日 `YYYY-MM-DD` | — |
| `ctr_prc_dt` | string | 转正生效日 | 转正日期 |
| `tmn_eft_dt` | string\|null | 离职生效日 | 离职日期 |
| `days_after_ctr_prc` | int | 转正后第几天离职（0~90） | 距转正天数 |
| `tmn_reason` | string\|null | 离职原因 | 离职原因 |
| `prc_status` | string\|null | 转正/答辩状态 | — |
| `prc_score` | float\|null | 答辩分数 | 转正分 |
| `prc_rvw` | string\|null | 答辩评语（JSON 字符串数组） | — |

> 模板 §3.4 展示 9 列（含姓名（账号）、一级部门）；`prc_status`/`prc_rvw`/`hire_dt` 等未展示字段勿写入正文。

`{blind_cnt}` = `d3_probation.psv_within_90d_list_cnt`（接口返回的实际总人数，列表仅展示 Top 20）

### 5.5 D3 推导占位符

| 占位符 | 推导 |
|--------|------|
| `{defense_pass_cnt}` | `defense_status` 中 `答辩建议通过` 的 `cnt` |
| `{defense_pass_pct}` | `defense_pass_cnt` / `hire_cnt_fte` ×100 |
| `{defense_fail_cnt}` | `defense_status` 中 `答辩建议不通过` 的 `cnt` |
| `{defense_fail_pct}` | `defense_fail_cnt` / `hire_cnt_fte` ×100 |
| `{defense_pending_cnt}` | `defense_status` 中 `待安排` 的 `cnt` |
| `{defense_pending_pct}` | `defense_pending_cnt` / `hire_cnt_fte` ×100 |
| `{defense_score_avg}` | `score_stats.mean_v` |
| `{defense_score_median}` | `score_stats.p50` |
| `{defense_pass_active_avg}` | `score_stats` 中通过且在职的均分（若接口无单独字段则 LLM 从得分分布数据推算） |
| `{pre_confirm_tmn_cnt}` | `before_after_prc_list.before_tmn` 各项 `cnt` 之和 |
| `{pre_confirm_active_cnt}` | `before_after_prc_list.before_tmn` 中 `主动离职` 的 `cnt` |
| `{pre_confirm_passive_cnt}` | `before_after_prc_list.before_tmn` 中 `被动离职` 的 `cnt` |
| `{post_confirm_tmn_cnt}` | `before_after_prc_list.after_tmn` 各项 `cnt` 之和 |
| `{post_confirm_passive_cnt}` | `before_after_prc_list.after_tmn` 中 `被动离职` 的 `cnt` |
| `{post_confirm_active_cnt}` | `before_after_prc_list.after_tmn` 中 `主动离职` 的 `cnt` |


---

## 六、D4 留存与流失 → 第3章（§3.5~3.6）

**路径**：`data.d4_retention`

### 6.1 `before_after_prc_list` → §3.5（已聚合对象）

**路径**：`data.d4_retention.before_after_prc_list`（**object**，非员工明细数组）

| 路径 | 类型 | 含义 |
|------|------|------|
| `before_tmn` | list | 转正**前**离职，按主被动汇总 |
| `after_tmn` | list | 转正**后**离职，按主被动汇总 |

`before_tmn[]` / `after_tmn[]` 每项：

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `resign_type` | string | `主动` / `被动`（及接口可能返回的 `未知`） | 列「主动」「被动」 |
| `cnt` | int | 人数 | 对应单元格 |

**§3.5 填表**（2 行 × 3 列，行顺序固定）：

| 模板行 | 数据来源 |
|--------|----------|
| 转正前 | `before_tmn[]`：按 `resign_type` 匹配填「主动」「被动」；无匹配填 `0` |
| 转正后 | `after_tmn[]`：同上 |

| 模板列 | 规则 |
|--------|------|
| 主动 / 被动 | 取同 `resign_type` 的 `cnt`；`resign_type` 为 `未知` 时**不**并入主动/被动，勿自行归类 |
| 合计 | 该行「主动」+「被动」（**仅**允许的行内加法；禁止改 `cnt` 原值） |

> `before_tmn` / `after_tmn` 内各项**保序**输出到编排理解即可；填表按列名匹配，不按数组顺序重排行。

**占位符推导**（允许加工）：

| 占位符 | 公式 |
|--------|------|
| `{pre_prc_tmn_pct}` | `sum(before_tmn[].cnt)` ÷ (`sum(before_tmn[].cnt)` + `sum(after_tmn[].cnt)`) × 100；分母为 0 → `—` |

`before_after_prc_list` 为 `null` 或两子列表均为空时：§3.5 表填 `0` 或按模板说明写「本期无转正前/后离职分布数据」。

### 6.2 `tmn_reason_top12[]` → §3.6

| 字段 | 类型 | 含义 | 模板列 |
|------|------|------|--------|
| `reason` | string | 离职原因 | 原因 |
| `cnt` | int | 人数 | 人数 |
| `pct` | float | 占比（已 ×100） | 占比 |

> 全量逐行填表，**按接口返回顺序**输出（工具侧已按 `cnt` 降序）；保序规则见 `onboarding-report.md` 红线 1。

---

## 七、D5 关键分群三层归因 → 第4章

**路径**：`data.d5_attribution`

| 字段 | 类型 | 含义 | 模板 |
|------|------|------|------|
| `score_attribution_list` | list | 兼容字段，默认 `[]` | **勿用于填表** |
| `score_attribution_layered` | object\|null | 转正分归因（y=`prc_score`，连续值） | §4.1 |
| `resign_attribution_layered` | object\|null | 离职率归因（y=`is_resigned`，由 `tmn_eft_dt` 派生；metric **已 ×100** 为百分点） | §4.2 |

### 7.1 归因对象统一结构

#### `overall`

| 字段 | 类型 | 含义 |
|------|------|------|
| `n` | int | 参与归因的有效样本数 |
| `metric` | float | 整体均值（分数）或整体离职率（**百分点**） |

#### `layer1`（object，key = 维度名）

每组为 list，按 |dev| Top5，**组内 n≥3**。

| 字段 | 类型 | 含义 |
|------|------|------|
| `group` | string | 该维度下的取值（如 `17`、`社招`、`是`）；填表时写入对应维度表**首列**（首列列名 = `layer1` 的 key，勿写「分组」） |
| `n` | int | 该组样本数 |
| `metric` | float | 该组均值或离职率（%） |
| `dev` | float | 偏离 = metric − overall.metric |

**layer1 常见维度键**：

| 键名 | 含义 | 备注 |
|------|------|------|
| `dept_nm_lvl1`~`dept_nm_lvl6` | 动态部门层级 | 随查询部门变化 |
| `职级` | 职级 | |
| `招聘类型` | 校招/社招 | |
| `是否高薪offer` | 高薪 OFFER | 取值常为 `是`/`否` |
| `是否获奖` | 是否获奖 | |
| `是否管理者` | 是否管理者 | 取值 `是`/`否` |
| `是否未来星` | 未来星 | |
| `蓝/白领` | 蓝领/白领 | |
| `离职类型` | 主动/被动等 | **仅 score 归因**；resign 归因**自动剔除**（防标签泄漏） |

#### `layer2[]`（双因子异常对 Top5）

| 字段 | 类型 | 含义 |
|------|------|------|
| `x_col` / `x_val` | string | 因子 X 名 / 取值 |
| `z_col` / `z_val` | string | 因子 Z 名 / 取值 |
| `n` | int | 组合样本数 |
| `actual` | float | 实际值 |
| `predicted` | float | 加性预测 = overall + eff(X) + eff(Z) |
| `residual` | float | actual − predicted |

**引擎筛选阈值**（报告只描述现象，勿重算）：分数 **0.10 分**；离职率 **1.5 百分点**。

#### `layer3[]`（在 layer2 异常子集内下钻）

继承 layer2 各字段，另增：

| 字段 | 类型 | 含义 |
|------|------|------|
| `subset_metric` | float | 该 (X,Z) 子集均值 |
| `drilldowns[]` | list | 按候选 W 维 Top3 |
| `drilldowns[].w_col` | string | 下钻维度名 |
| `drilldowns[].w_val` | string | 下钻取值 |
| `drilldowns[].n` | int | 样本数 |
| `drilldowns[].metric` | float | 该组指标 |
| `drilldowns[].dev` | float | 相对 **subset_metric** 的偏离 |

### 7.2 §4.1 转正分数归因 → 模板映射

| 模板小节 | 数据来源 |
|----------|----------|
| §4.1.1 整体水平 | `score_attribution_layered.overall.n` / `.metric` |
| §4.1.2 单维度对比 | `layer1` **逐 key 全部展开**，每维一表；小标题与表头首列 = `layer1` 的 key，行首列 = `group`；`转正均分` 列 = `metric`，`与整体偏离(分)` 列 = `dev` |
| §4.1.3 两维度交叉看 | `layer2[]` 全量行 |
| §4.1.4 三维度细分 | `layer3[]` 展平 `drilldowns[]`；X 组合列：`{x_val} × {z_val}`；`均分` 列 = `drilldowns[].metric`，`与整体偏离(分)` 列 = `drilldowns[].dev` |

**空数据时的正文文案**（与模板 `[LLM:…]` 一致，禁止输出空表）：

| 条件 | 填写位置 | 正文一句 |
|------|----------|----------|
| `score_attribution_layered` 为 `null` | §4.1 开篇 | 有效打分员工数不足，暂无转正分数归因结论（跳过 §4.1.1～4.1.4 各表） |
| `layer1` 为空对象 `{}` | §4.1.2 下 | 单维度对比：暂无满足样本量要求的维度 |
| 某 `layer1` 维度下 `[]` | 该维小标题下 | 该维度暂无足够样本（不建表） |
| `layer2` 为 `[]` | §4.1.3 下 | 暂未发现显著的两维度交叉异常。 |
| `layer3` 为 `[]` | §4.1.4 下 | 暂无可做的三维度细分（需先存在显著的两维度交叉异常）。 |

### 7.3 §4.2 离职率归因 → 模板映射

结构同 §4.1；`离职率(%)` 列 = `metric`，`与整体偏离(百分点)` 列 = `dev`，`residual` 映射到交叉表的「实际 - 预测(百分点)」列。所有值均为**百分点**，禁止再 ×100。

**空数据时的正文文案**：

| 条件 | 填写位置 | 正文一句 |
|------|----------|----------|
| `resign_attribution_layered` 为 `null` | §4.2 开篇 | 有效员工数不足，暂无离职率归因结论（跳过 §4.2.1～4.2.4 各表） |
| `layer1` 为空对象 `{}` | §4.2.2 下 | 单维度对比：暂无满足样本量要求的维度 |
| `layer2` 为 `[]` | §4.2.3 下 | 暂未发现显著的两维度交叉异常。 |
| `layer3` 为 `[]` | §4.2.4 下 | 暂无可做的三维度细分（需先存在显著的两维度交叉异常）。 |

### 7.4 第4章占位符

| 占位符 | 来源 |
|--------|------|
| `{score_attr_n}` | `score_attribution_layered.overall.n` — 转正分归因涉及人数 |
| `{score_attr_metric}` | `score_attribution_layered.overall.metric` — 整体均分 |
| `{resign_attr_n}` | `resign_attribution_layered.overall.n` — 离职率归因涉及人数 |
| `{resign_attr_metric}` | `resign_attribution_layered.overall.metric` — 整体离职率（已×100，直接输出为百分比） |

### 7.5 正文展示名（勿暴露 JSON 键名）

| 维度键 | 正文展示 |
|--------|----------|
| `dept_nm_lvl1` | 一级部门 |
| `dept_nm_lvl2` | 二级部门 |
| `dept_nm_lvl3` | 三级部门 |
| `dept_nm_lvl4` | 四级部门 |
| `dept_nm_lvl5` | 五级部门 |
| `dept_nm_lvl6` | 六级部门 |
| `职级` | 如 `17级` |
| `是否高薪offer` | 高薪 OFFER：是/否 |
| `是否管理者` | 管理者：是/否 |

### 7.6 D5 填表规则

1. 禁止用 `score_attribution_list` 做旧版固定分群表。
2. `layer1`：接口有几个维度键就几张表，行数与接口一致。
3. `layer2`/`layer3`：有几行输出几行；空则按 §7.2/§7.3 空数据文案（与「两维度交叉看」「三维度细分」标题一致），勿输出空表。
4. 数值原样引用；禁止 LLM 重算 residual。
5. `>` 结论用业务语言，禁止出现 `x_col`、`layer2` 等字段名。

---

## 八、摘要卡片字段映射

版式与**摘录流程**见 `onboarding-report.md` §4.3；发送见 `send-card.md`。

> **SSOT**：卡片全部正文（除 DEP「数据说明」、文档链接固定文案）来自步骤 A 的 `FILLED_MARKDOWN`，禁止独立撰写。

**卡片结构（自上而下，版式 demo）**：

| 区块 | `FILLED_MARKDOWN` 来源 | 说明 |
|------|------------------------|------|
| `#### **整体数据概览**` | 模板占位符 + 固定 3 条 | D1 填表；卡片原样复制 3 条 |
| `#### 💡 **分析解读**` | LLM §7.1 | **4-5 条** TOP（整体 callout；卡片原样复制整节）；各章 `💡 **分析解读**` 为 2-3 条 |
| `#### ⚠️ **重点关注**` | LLM | 2-3 条；卡片原样复制整节 |
| `> 数据口径`（整体） | 整体 callout blockquote | 原样 |
| `---` | — | 分隔 |
| `#### **第1章 · …**`（仅卡片） | `## 第1章 …` + 第 1 章 callout | 标题 C-2 生成；正文 callout 原样 |
| `#### **第2章 · …**` | `## 第2章 …` + 第 2 章 callout | 同上 |
| `#### **第3章 · …**` | `## 第3章 …` + 第 3 章 callout | 同上 |
| `#### **第4章 · …**` | `## 第4章 …` + 第 4 章 callout | 同上 |
| 数据说明 | `dep_impact` | 仅当 `dep_impact` 非空；放末段链接前 |
| 📄 文档链接 | `doc_url` | `[更多详细内容查看完整报告]({doc_url})` |

**摘录原则**：从 `FILLED_MARKDOWN` 原文复制；版式见 `onboarding-report.md` §4.3 demo；**禁止**独立撰写或改写。超长时裁各章分析解读条数，不改写。组装时机见 §十步骤 7。

| 段落（历史参考） | 来源 |
|------|------|
| 🔢 入职/在职/离职 | D1 合计 → 整体 callout「整体数据概览」3 条 |
| 整体洞察 | callout「分析解读」 | 卡片 `#### 💡 **分析解读**` |
| 重点关注 | callout「重点关注」 | 卡片 `#### ⚠️ **重点关注**` |
| 【规模与节奏】 | 第 1 章 callout 全文 | 卡片原样复制 |
| 【新人画像】 | 第 2 章 callout 全文 | 同上 |
| 【转正与留存】 | 第 3 章 callout 全文 | 同上 |
| 【分群异常】 | 第 4 章 callout 全文 | 同上 |
| 完整归因表格 | 仅文档 §4.1/§4.2，不进卡片 |

---

## 九、模板章节快查

| 模板章节 | 数据块 | 状态 |
|----------|--------|------|
| 口径/整体 callout | 整体数据概览 + 分析解读 + 重点关注 | ✅ |
| §1.1 | `d1_overall.by_emp_type` | ✅ |
| §1.2 | `monthly_numbers_list` | ✅ |
| §1.3 主被动 | `psv_active_list` | ✅ |
| §2.1~2.11 | `d2_profile` | ✅ |
| §3.1~3.4 | `d3_probation` | ✅ |
| §3.5~3.6 | `d4_retention` | ✅ |
| §4.1 / §4.2 | `*_attribution_layered` | ✅ |
| 附说明 | `dept_name`、`time_range` | ✅ |

---

## 十、填充顺序（推荐）

1. 校验 `code === 0`；用 `scripts/parse-report.py` 拆分落盘 JSON，**逐个 read** `_meta.json` 与 D1~D5 分片（见 `onboarding-report.md` §一 Step 2~3）
2. 写入 `dept_name`、`time_range`
3. D1 → D2 → D3 → D4：原样填表 + 各表 `>` 结论
4. D5：`layer1` 逐维全部展开 + layer2/3 表 + §4 结论
5. 整体 callout（整体数据概览 3 条 + 分析解读 + 重点关注）、各章分析解读
6. ③ feishu_update_doc 写入全文
7. 摘要卡片：对照 FILLED_MARKDOWN 按 §4.3 demo 组装
8. 飞书四步收尾确认（见 onboarding-report §五）
