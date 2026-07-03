---
name: intent-rate
description: >
  离职率/流失率/闪离率计算（RATE）子场景规则——需公式计算的率值查询指南。
  包含离职率 vs 流失率公式区分、主动/被动离职率、闪离率、高绩效流失率、
  B+及以上流失率、高绩效A/S流失率等完整公式体系，
  以及分母取法、时间范围处理、多维度交叉计算模式。
  当 routing-sql.md 判定子场景为 RATE 时读取本文件，同时必须加载 intent-flow.md。
---

# 离职率/流失率/闪离率计算（RATE）

> **适用场景**：离职率、流失率、闪离率、被动离职率、主动离职率等需要公式计算的查询。
> 使用前必须先读取 sql-query.md 通用规则。
>
> **率计算的分子（离职/闪离人次）仍遵循 intent-flow.md 的流动铁律和表结构定义。**
> 编写率 SQL 时必须同时参考 [references/sql/intent-flow.md](references/sql/intent-flow.md)。离职率、主动离职率、被动离职率、闪离率、流失率等调转入离派生指标 JOIN `dept_df` 时，**不要**添加 `eft_sts_cd='A'`，不应该屏蔽失效部门，也不要用 NV 部门名过滤失效部门。

**目录**：[一、离职率 vs 流失率](#一离职率-vs-流失率公式不同严禁混用) · [二、闪离率](#二闪离率含蓝领白领) · [三、绩优应届生流失率](#三绩优应届生流失率) · [三-B、入职不满一年员工流失率](#三-b入职不满一年员工流失率特殊公式) · [三-C、期末在职人数取值规则](#三-c期末在职人数取值规则) · [三-D、子群离职率正反例](#三-d子群离职率-vs-子群流失率正反例) · [四、SOP 示例](#四sop-示例已结束年份离职率) · [五、B+及以上流失率](#五b及以上流失率bp_plus_turnover_rate) · [六、高绩效A/S流失率](#六高绩效as流失率as_perf_turnover_rate) · [七、同比流失率](#七同比流失率最佳实践) · [八、按维度拆分流失率排名](#八按维度拆分流失率排名部门主管)

---

## 一、离职率 vs 流失率（公式不同，严禁混用）

### 公式速查表

| 指标 | 公式 | 分母说明 |
|------|------|---------|
| 离职率 | tmn/(tmn+期末emp) | 分母含全体 tmn |
| 流失率 | tmn/期末emp | 分母不含 tmn |
| 主动离职率 | vlt_tmn/(全体tmn+emp) | 只换分子，分母全体 tmn |
| 被动离职率 | psv_tmn/(全体tmn+emp) | 只换分子，分母全体 tmn |
| 子群离职率 | sub_tmn/(全体tmn+全体emp) | 只换分子，分母全体 |
| 子群流失率 | sub_tmn/sub_emp | 分子分母都限定子群 |
| 闪离率 | quick_tmn/(全体tmn+emp) | 只换分子，分母全体 |

### 公式选择决策树（每次必执行）

1. **离职率 vs 流失率**：说离职率→分母=tmn+emp；说流失率→分母=emp
2. **主动/被动区分**：只换分子，分母不变
3. **属性子群**：子群**离职率**→只换分子为子群 tmn，分母全体 tmn+emp；子群**流失率**→分子分母都限定子群
4. **按维度拆分**（各部门/各序列）：每个维度独立套用完整公式，分子分母都限定各自维度。如销售序列被动离职率=sale_psv_tmn/(sale_tmn+sale_emp)
5. **同比/环比**：用 **1 个 tmn CTE + 条件聚合** 同时算出多年离职人次，禁止写多个 tmn CTE 分别查询。**emp 分母取法取决于离职率 vs 流失率**：离职率同比→每年各取各自期末快照（已结束年用 `date=YYYYMMDD`，未结束年用 `MAX(date)`）；流失率同比→emp 分母共用 MAX(date)（→ 详见[七、同比离职率/流失率](#七同比离职率流失率最佳实践)）

### 流失率分母铁律

流失率分母「在职人数」统一取当前最新快照 MAX(date)，无论计算哪个年份都用 MAX(date)。**同比场景只有 tmn 分子按年份不同，emp 分母共用 MAX(date)**。

**⚠️ 此铁律仅适用于流失率，不适用于离职率。** 离职率同比场景的 emp 分母必须按三-C 的「期末在职人数取值规则」各年各取各自期末快照（已结束年用 `date=YYYYMMDD`，未结束年用 `MAX(date)`），严禁共用 MAX(date)——否则所有年份分母相同，趋势分析失去意义。

### ⚠️ 率计算五步法（复杂率查询必须遵循）

1. **拆解子问题**：明确分子（哪些离职人次）和分母（哪些在职人数）
2. **确定公式类型**：离职率 or 流失率？子群 or 全体？按决策树判定
3. **确定口径和条件**：员工类型口径、绩效字段、时间范围、部门范围
4. **确定涉及的表和关联方式**：CTE 结构、JOIN 顺序（流动铁律）
5. **生成 SQL + 自检**：逐条核对铁律和公式

### ⚠️⚠️⚠️ CTE 结构铁律：分子分母必须分离（极易出错，严禁合并）

**禁止**将离职人次（分子）和在职人数（分母）合并到一个 CTE 中用 `emp_df LEFT JOIN trsf_tmn_f` 的方式同时计算。

**错误模式**（已发生的真实 bug）：
```sql
-- ❌ 严禁：emp 为主表 LEFT JOIN 离职表，试图一次算出在职+离职
SELECT
    COUNT(DISTINCT e.emp_id) AS 绩优在职,
    COUNT(DISTINCT CASE WHEN t.emp_id IS NOT NULL THEN e.emp_id END) AS 绩优离职
FROM ads_ai_qa_emp_df e
LEFT JOIN ads_ai_qa_trsf_tmn_f t ON e.emp_id = t.emp_id
  AND t.tmn_eft_dt >= '2025-01-01' AND t.tmn_eft_dt < '2026-01-01'
WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND e.emp_sts_cd = 'A'    -- ← 致命错误：已离职员工状态为'I'，被过滤掉了
  AND e.late_pfm IN ('B+','A','A+','S','S+')
```

**为什么错**：
1. `emp_sts_cd = 'A'` 只保留当前在职人员，2025年已离职的绩优员工状态已变为 'I'，被 WHERE 过滤——**绩优离职人次严重偏低甚至为 0**
2. 违反铁律A（流动表必须为驱动表 INNER JOIN dept_df）
3. 违反铁律G（禁止经由 emp_df 间接关联部门——离职员工的部门应从离职表 `t.dept_id` 取，不是 emp_df 当前快照的部门）

**正确模式**：分子（tmn CTE）和分母（emp CTE）必须分开写，最后 SELECT 合并：
```sql
-- ✅ 正确：分离 CTE
WITH hi_tmn AS (
    -- 分子：绩优离职人次（以离职表为主表）
    SELECT d.dept_nm_lvl1 AS 部门, COUNT(DISTINCT t.emp_id) AS 绩优离职
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE t.tmn_eft_dt >= '2025-01-01' AND t.tmn_eft_dt < '2026-01-01'
      AND t.real_emp_cls_cd IN ('101','115','118')
      AND e.late_pfm IN ('B+','A','A+','S','S+')
    GROUP BY d.dept_nm_lvl1
),
hi_emp AS (
    -- 分母：绩优在职人数（以员工表为主表）
    SELECT dept_nm_lvl1 AS 部门, COUNT(DISTINCT emp_id) AS 绩优在职
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101','115','118')
      AND late_pfm IN ('B+','A','A+','S','S+')
    GROUP BY dept_nm_lvl1
)
SELECT t.部门, t.绩优离职, e.绩优在职,
       ROUND(t.绩优离职::numeric / NULLIF(t.绩优离职 + e.绩优在职, 0) * 100, 2) AS 绩优离职率
FROM hi_tmn t
JOIN hi_emp e ON t.部门 = e.部门
```

**自检规则**：生成 SQL 后，检查是否存在 `FROM ads_ai_qa_emp_df ... LEFT JOIN ads_ai_qa_trsf_tmn_f` 模式。如有，**必须重写为分离 CTE**。

### SQL 模板

#### 场景A：一般离职率

```sql
WITH tmn AS (
  SELECT COUNT(1) AS tmn_cnt
  FROM ads_ai_qa_trsf_tmn_f t
  INNER JOIN ads_ai_qa_dept_df d ON t.dept_id=d.dept_id
    AND d.date=(SELECT MAX(date) FROM ads_ai_qa_dept_df)
  WHERE t.tmn_eft_dt>='2025-01-01' AND t.tmn_eft_dt<'2026-01-01'
    AND t.real_emp_cls_cd IN('101','115','118')
),
emp AS (
  SELECT COUNT(DISTINCT emp_id) AS emp_cnt FROM ads_ai_qa_emp_df
  WHERE date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
    AND emp_sts_cd='A' AND real_emp_cls_cd IN('101','115','118')
)
SELECT ROUND(t.tmn_cnt::numeric/NULLIF(t.tmn_cnt+e.emp_cnt,0)*100,1) AS 离职率
FROM tmn t, emp e
```

#### 场景B：被动离职率（分母含全部 tmn，不是仅被动）

```sql
WITH tmn AS (
  SELECT COUNT(1) AS tmn_cnt,
    COUNT(CASE WHEN t.psv_tmn_flg=1 THEN 1 END) AS psv_tmn_cnt
  FROM ads_ai_qa_trsf_tmn_f t
  INNER JOIN ads_ai_qa_dept_df d ON t.dept_id=d.dept_id
    AND d.date=(SELECT MAX(date) FROM ads_ai_qa_dept_df)
  WHERE t.tmn_eft_dt>='2025-01-01' AND t.tmn_eft_dt<'2026-01-01'
    AND t.real_emp_cls_cd IN('101','115','118')
),
emp AS (
  SELECT COUNT(DISTINCT emp_id) AS emp_cnt FROM ads_ai_qa_emp_df
  WHERE date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
    AND emp_sts_cd='A' AND real_emp_cls_cd IN('101','115','118')
)
SELECT ROUND(t.psv_tmn_cnt::numeric/NULLIF(t.tmn_cnt+e.emp_cnt,0)*100,1) AS 被动离职率
FROM tmn t, emp e
```

#### 场景C：子群离职率（只换分子，分母全体）

```sql
WITH tmn AS (
  SELECT COUNT(1) AS tmn_cnt,
    COUNT(CASE WHEN e.hi_pfm_flg=1 THEN 1 END) AS sub_tmn_cnt
  FROM ads_ai_qa_trsf_tmn_f t
  INNER JOIN ads_ai_qa_dept_df d ON t.dept_id=d.dept_id
    AND d.date=(SELECT MAX(date) FROM ads_ai_qa_dept_df)
  LEFT JOIN ads_ai_qa_emp_df e ON t.emp_id=e.emp_id
    AND e.date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
  WHERE t.tmn_eft_dt>='2025-01-01'
    AND t.real_emp_cls_cd IN('101','115','118')
),
emp AS (
  SELECT COUNT(DISTINCT emp_id) AS emp_cnt FROM ads_ai_qa_emp_df
  WHERE date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
    AND emp_sts_cd='A' AND real_emp_cls_cd IN('101','115','118')
)
SELECT ROUND(t.sub_tmn_cnt::numeric/NULLIF(t.tmn_cnt+e.emp_cnt,0)*100,1) AS 子群离职率
FROM tmn t, emp e
```

#### 场景D：子群流失率（分子分母都限定子群）

```sql
WITH tmn AS (
  SELECT COUNT(1) AS sub_tmn_cnt
  FROM ads_ai_qa_trsf_tmn_f t
  INNER JOIN ads_ai_qa_dept_df d ON t.dept_id=d.dept_id
    AND d.date=(SELECT MAX(date) FROM ads_ai_qa_dept_df)
  LEFT JOIN ads_ai_qa_emp_df e ON t.emp_id=e.emp_id
    AND e.date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
  WHERE t.tmn_eft_dt>='2025-01-01'
    AND t.real_emp_cls_cd IN('101','115','118')
    AND e.hi_pfm_flg=1
),
emp AS (
  SELECT COUNT(DISTINCT emp_id) AS sub_emp_cnt FROM ads_ai_qa_emp_df
  WHERE date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
    AND emp_sts_cd='A' AND real_emp_cls_cd IN('101','115','118')
    AND hi_pfm_flg=1
)
SELECT ROUND(t.sub_tmn_cnt::numeric/NULLIF(e.sub_emp_cnt,0)*100,1) AS 子群流失率
FROM tmn t, emp e
```

---

## 二、闪离率（含蓝领/白领）

闪离定义：离职日期与最近入职日期相差 <=90 天。
闪离率 = quick_tmn / (emp_cnt + quick_tmn)，与离职率分母逻辑一致。

判断条件：`(t.tmn_eft_dt::date - t.last_hire_dt::date) BETWEEN 0 AND 90`

**必须用 CTE 模式**分开统计 tmn 和 emp，再合并计算。蓝领/白领闪离率用**条件聚合**在一条 SQL 中同时计算（禁止分多条 SQL）。

```sql
WITH tmn AS (
    SELECT
      COUNT(1) AS tmn_cnt,
      COUNT(CASE WHEN (t.tmn_eft_dt::date - t.last_hire_dt::date) BETWEEN 0 AND 90 THEN 1 END) AS quick_tmn_cnt,
      COUNT(CASE WHEN e.blue_flg = 0 THEN 1 END) AS white_tmn_cnt,
      COUNT(CASE WHEN e.blue_flg = 1 THEN 1 END) AS blue_tmn_cnt,
      COUNT(CASE WHEN (t.tmn_eft_dt::date - t.last_hire_dt::date) BETWEEN 0 AND 90 AND e.blue_flg = 0 THEN 1 END) AS quick_white_tmn_cnt,
      COUNT(CASE WHEN (t.tmn_eft_dt::date - t.last_hire_dt::date) BETWEEN 0 AND 90 AND e.blue_flg = 1 THEN 1 END) AS quick_blue_tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = 'XXX部门'
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
),
emp AS (
    SELECT
      COUNT(1) AS emp_cnt,
      COUNT(CASE WHEN blue_flg = 0 THEN 1 END) AS white_emp_cnt,
      COUNT(CASE WHEN blue_flg = 1 THEN 1 END) AS blue_emp_cnt
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101', '115', '118')
      AND dept_nm_lvl1 = 'XXX部门'
)
SELECT
  ROUND(t.quick_tmn_cnt::numeric / NULLIF(e.emp_cnt + t.quick_tmn_cnt, 0), 3) AS 总体闪离率,
  ROUND(t.quick_white_tmn_cnt::numeric / NULLIF(e.white_emp_cnt + t.quick_white_tmn_cnt, 0), 3) AS 白领闪离率,
  ROUND(t.quick_blue_tmn_cnt::numeric / NULLIF(e.blue_emp_cnt + t.quick_blue_tmn_cnt, 0), 3) AS 蓝领闪离率
FROM tmn t, emp e
```

---

## 三、绩优应届生流失率

**⚠️ "绩优"=B+及以上，与"高绩效"(A及以上, hi_pfm_flg)不同，严禁混用！**

**⚠️ 绩优筛选必须用 emp_df 的 `late_pfm`（最近一次绩效），禁止用 pfm_f 的 `bb_pfm_flg`。** 原因：pfm_f 存储历史全部期次绩效，即使加了 `pfm_prd = MAX(pfm_prd)` 限制最近期次，仍可能因为期次对齐问题导致人群口径偏差。`late_pfm` 是 emp_df 的预计算字段，直接表示"最近一次绩效等级"，语义最准确。

```sql
WITH tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = 'XXX部门'
      AND e.new_grdt_grd_cd IN ('2022', '2023', '2024', '2025', '2026')  -- 近5届（届别筛选，不是离职时间！）
      AND e.late_pfm IN ('B+', '*B', 'A', 'A+', 'S', 'S+')  -- ⚠️ 绩优=B+及以上，必须包含 '*B'！
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')  -- ⚠️ 离职时间默认当年，禁止写成 >= '2022-01-01'！
),
emp AS (
    SELECT COUNT(DISTINCT emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101', '115', '118')
      AND dept_nm_lvl1 = 'XXX部门'
      AND new_grdt_grd_cd IN ('2022', '2023', '2024', '2025', '2026')
      AND late_pfm IN ('B+', '*B', 'A', 'A+', 'S', 'S+')
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0), 3) AS 流失率
FROM tmn t, emp e
```

### 6个关键点

1. **"绩优"=B+及以上**，必须用 `late_pfm IN ('B+', '*B', 'A', 'A+', 'S', 'S+')`。**⚠️ 必须包含 `'*B'`（特殊绩效等级，等价于 B+ 档位）。禁止用 `hi_pfm_flg = 1`**（那是"高绩效"=A及以上）。**禁止用 pfm_f 的 `bb_pfm_flg`**（会引入历史全部期次的绩优人员，而非"最近一次是绩优"）
2. **应届生筛选用 `new_grdt_grd_cd IN ('2022','2023','2024','2025','2026')`**（近5届），禁止用司龄反推
3. **离职人次必须从 trsf_tmn_f 统计**，绝对禁止从 emp_df 用 emp_sts_cd='I' 推断
4. **此处是子群流失率**：`tmn_cnt / emp_cnt`（子群离职人次 / 子群在职人数），不是子群离职率
5. **tmn CTE 必须限定离职时间（极易出错）**：用户未指定时间 → 默认**当年至今**，必须写 `t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')`。**⚠️ "近5届"是应届生届别筛选条件（`new_grdt_grd_cd`），不是离职时间范围！禁止把届别年份（2022）套用到离职时间（`tmn_eft_dt >= '2022-01-01'`）——那会把 4 年离职人次全部累加进分子，而分母只有当前快照的在职人数，流失率严重偏高。**
6. **禁止用 pfm_f 方案替代 late_pfm 方案**：pfm_f 的 `bb_pfm_flg = 1` 覆盖历史全部期次绩效，即使加了 `pfm_prd = MAX(pfm_prd)`，仍然是"最近期次中绩优的人"而非"最近一次绩效是绩优的人"（两者口径可能不同）。`late_pfm` 是 emp_df 预计算字段，直接取"最近一次绩效等级"，语义最准确

---

## 三-B："入职不满一年员工流失率"特殊公式

- 分子 = **全部**离职人次（不限制 wrk_age_mi_y）
- 分母 = 入职不满一年的在职人数（wrk_age_mi_y < 1）
- 即：`全量 tmn_cnt / 子群 emp_cnt`
- **分母只有子群在职人数，不包含离职人次**

```sql
WITH tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    WHERE d.dept_nm_lvl1 = '中国区'
      AND t.real_emp_cls_cd IN ('101', '115', '118')
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
),
emp AS (
    SELECT COUNT(DISTINCT emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
      AND e.dept_nm_lvl1 = '中国区'
      AND e.wrk_age_mi_y < 1  -- 分母仅限入职不满一年的在职员工
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0) * 100, 1) AS 流失率
FROM tmn t, emp e
```

---

## 三-C：期末在职人数取值规则

期末在职人数 = 统计区间结束日期**当天的时间切片**：

- **已结束的时间段**（如"2025年"）→ `date = 20251231`（取期末当天快照），**禁止**用 MAX(date) 取最新快照
- **未结束的时间段**（如"今年"/"本月"）→ `date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)`（取最新快照）

**流失率分母铁律（仅适用于流失率，不适用于离职率）**：流失率分母「在职人数」统一取当前最新快照 MAX(date)，无论计算哪个年份都用 MAX(date)。同比场景只有 tmn 分子按年份不同，emp 分母共用 MAX(date)。

**离职率分母规则**：离职率公式 `tmn/(tmn+emp)` 中的 emp 必须遵循上方「期末在职人数取值规则」——已结束年用期末快照（如 `date=20241231`），未结束年用 `MAX(date)`。同比场景每年各取各自期末快照，**禁止共用 MAX(date)**。

---

## 三-D：子群离职率 vs 子群流失率正反例

### 子群离职率（只换分子，分母全体）

**⚠️⚠️⚠️ 分母中的 emp_cnt 和 tmn_cnt 必须是全量口径，禁止限定为子群！这是最常犯的错误。**

```sql
-- ✅ 正确：高绩效子群离职率——分子限高绩效，分母全量
WITH tmn AS (
    SELECT
        COUNT(1) AS tmn_cnt,
        COUNT(CASE WHEN e.hi_pfm_flg = 1 THEN 1 END) AS hi_tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
      AND t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
),
emp AS (
    SELECT COUNT(DISTINCT emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101', '115', '118')
      AND dept_nm_lvl1 = '中国区'
)
SELECT ROUND(t.hi_tmn_cnt::numeric / NULLIF(e.emp_cnt + t.tmn_cnt, 0) * 100, 2) AS 高绩效离职率
FROM tmn t, emp e

-- ❌ 错误：分母也限定了高绩效子群（导致离职率从0.48%偏高到2.8%）
```

### 子群流失率（分子分母都限定子群）

子群流失率 = 子群离职人次 / 子群员工数。分子和分母都限定为该子群。

### 按维度拆分离职率

各部门/各序列独立套用完整公式，分子分母都限定各自维度。如：销售序列被动离职率 = sale_psv_tmn / (sale_tmn + sale_emp)

---

## 四、SOP 示例：已结束年份离职率

**⚠️ 关键**：已结束年份的离职率，期末在职人数必须用 `date = 20251231`（期末当天快照），**禁止用 MAX(date)**。

```sql
WITH tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON d.dept_id = t.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    WHERE t.tmn_eft_dt >= '2025-01-01'
      AND t.tmn_eft_dt < '2026-01-01'
      AND t.real_emp_cls_cd IN ('101', '115', '118')
),
emp AS (
    SELECT COUNT(DISTINCT emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    WHERE e.date = 20251231
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(t.tmn_cnt + e.emp_cnt, 0) * 100, 1) AS 离职率
FROM tmn t, emp e
```

---

## 四-B、季度绩效流失率（用户明确指定季度时）

**触发条件**：用户问题中明确出现"季度绩优离职率"/"Q2高绩效流失率"/"本季度绩效流失率"/"季度绩优流失率"等。

**⚠️ 与默认行为区别**：
- 默认（无季度关键词）→ 使用 emp_df 的 `hi_pfm_flg`/`late_pfm`（年/半年度口径），**不变**
- 明确指定季度 → 使用 `ads_ai_qa_pfm_q_f` 表按季度期次筛选绩效人群

**默认时间范围规则**：
- 用户指定了具体季度（如"Q2绩优离职率"）→ 离职时间范围为该季度
- 用户只说"季度绩优离职率"未指定哪个季度 → 离职时间默认**当前季度至今**：`t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('quarter', CURRENT_DATE), 'YYYY-MM-DD')`
- 此规则与现有"绩优离职率"默认取"当年至今"的逻辑保持一致

**SQL 模板：指定季度绩优流失率**

```sql
WITH pfm_emp AS (
    -- 从季度绩效表取指定季度的绩优员工
    SELECT DISTINCT p.emp_id
    FROM ads_ai_qa_pfm_q_f p
    WHERE p.pfm IN ('B+', 'A', 'A+', 'S', 'S+')
      AND p.pfm_prd = '2025Q2'  -- 用户指定的季度
),
tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN pfm_emp pe ON t.emp_id = pe.emp_id
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
      AND t.tmn_eft_dt >= '2025-04-01' AND t.tmn_eft_dt < '2025-07-01'
),
emp AS (
    SELECT COUNT(DISTINCT e.emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    INNER JOIN pfm_emp pe ON e.emp_id = pe.emp_id
    WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
      AND e.dept_nm_lvl1 = '中国区'
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0) * 100, 2) AS 季度绩优流失率
FROM tmn t, emp e
```

**SQL 模板：未指定季度时默认当前季度至今**

```sql
WITH pfm_emp AS (
    SELECT DISTINCT p.emp_id
    FROM ads_ai_qa_pfm_q_f p
    WHERE p.pfm IN ('B+', 'A', 'A+', 'S', 'S+')
      AND p.pfm_prd = (SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_q_f WHERE pfm_prd LIKE '%Q%')
),
tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN pfm_emp pe ON t.emp_id = pe.emp_id
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
      -- 离职时间默认当前季度至今
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('quarter', CURRENT_DATE), 'YYYY-MM-DD')
),
emp AS (
    SELECT COUNT(DISTINCT e.emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    INNER JOIN pfm_emp pe ON e.emp_id = pe.emp_id
    WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
      AND e.dept_nm_lvl1 = '中国区'
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0) * 100, 2) AS 季度绩优流失率
FROM tmn t, emp e
```

**季度时间范围对应**：

| 季度 | 开始日期 | 结束日期（不含） |
|------|---------|----------------|
| Q1 | YYYY-01-01 | YYYY-04-01 |
| Q2 | YYYY-04-01 | YYYY-07-01 |
| Q3 | YYYY-07-01 | YYYY-10-01 |
| Q4 | YYYY-10-01 | (YYYY+1)-01-01 |

**⚠️ 注意**：季度绩效流失率的绩效人群筛选必须从 `pfm_q_f` 取（因为需要季度粒度的绩效数据），不能用 emp_df 的 `q_hi_pfm_flg`（那是"最近一次含季度绩效"的标识，不一定是用户指定的那个季度）。

---

## 五、B+及以上流失率（bp_plus_turnover_rate）

**⚠️ 必须 JOIN pfm_f 表用 pfm 字段筛选，禁止用 emp_df 的 bb_pfm_flg 替代！**

原因：`bb_pfm_flg` 仅存在于 **pfm_f 表**（emp_df 没有此字段），且只反映最近一次绩效；而 B+流失率要求按特定期次的绩效等级计算，必须从 pfm_f 取原始 pfm 值。

公式：**子群流失率** = B+及以上离职人次 / B+及以上在职人数（分子分母都限定为 B+ 子群）

```sql
WITH pfm_emp AS (
    SELECT DISTINCT p.emp_id
    FROM ads_ai_qa_pfm_f p
    WHERE p.pfm IN ('B+', 'A', 'A+', 'S', 'S+')
      AND p.pfm_prd = (SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_f)
),
tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN pfm_emp pe ON t.emp_id = pe.emp_id
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
),
emp AS (
    SELECT COUNT(DISTINCT e.emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    INNER JOIN pfm_emp pe ON e.emp_id = pe.emp_id
    WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
      AND e.dept_nm_lvl1 = '中国区'
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0) * 100, 2) AS B加及以上流失率
FROM tmn t, emp e
```

---

## 六、高绩效A/S流失率（as_perf_turnover_rate）

**⚠️ 注意：分子是 A/S 子群，分母是 B+ 及以上子群（分子分母范围不同！）**

公式：高绩效A/S流失率 = A/S离职人次 / B+及以上在职人数

```sql
WITH pfm_as AS (
    SELECT DISTINCT emp_id
    FROM ads_ai_qa_pfm_f
    WHERE pfm IN ('A', 'A+', 'S', 'S+')
      AND pfm_prd = (SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_f)
),
pfm_bp AS (
    SELECT DISTINCT emp_id
    FROM ads_ai_qa_pfm_f
    WHERE pfm IN ('B+', 'A', 'A+', 'S', 'S+')
      AND pfm_prd = (SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_f)
),
tmn AS (
    SELECT COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN pfm_as pa ON t.emp_id = pa.emp_id
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
      AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
),
emp AS (
    SELECT COUNT(DISTINCT e.emp_id) AS emp_cnt
    FROM ads_ai_qa_emp_df e
    INNER JOIN pfm_bp pb ON e.emp_id = pb.emp_id
    WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND e.emp_sts_cd = 'A'
      AND e.real_emp_cls_cd IN ('101', '115', '118')
      AND e.dept_nm_lvl1 = '中国区'
)
SELECT ROUND(t.tmn_cnt::numeric / NULLIF(e.emp_cnt, 0) * 100, 2) AS 高绩效AS流失率
FROM tmn t, emp e
```

**与 hi_pfm_flg 的关系**：`hi_pfm_flg = 1` 等价于 A 及以上（A, A+, S, S+），与本指标分子的范围一致。但本指标的分母是 B+ 及以上全量，不是 A 及以上，因此**不能**简单用 `hi_pfm_flg` 同时限定分子分母。

---

## 七、同比离职率/流失率最佳实践

**⚠️ 同比场景必须用 1 个 tmn CTE + 条件聚合，禁止写多个 tmn CTE 分别查询（多次扫描大表，性能差）。**

### 核心规则

1. **1 个 tmn CTE**：WHERE 设大范围覆盖所有对比年份，内部用 `COUNT(CASE WHEN ... THEN 1 END)` 按年拆分
2. **emp 分母取法——离职率 vs 流失率不同（极其重要，最常犯的错误）**：
   - **离职率同比**：每年各取各自期末快照（已结束年 `date=YYYYMMDD`，未结束年 `MAX(date)`），用多个 emp CTE 分别取值，**禁止共用 MAX(date)**
   - **流失率同比**：emp 分母统一取 MAX(date) 最新快照，所有年份共用
   - **严禁将流失率的 MAX(date) 规则套用到离职率**——否则所有年份分母相同，趋势分析失去意义
3. **同比变化用百分点**：`(今年率 - 去年率)` 为百分点变化，不是百分比变化

### SQL 模板：子群流失率同比

```sql
WITH tmn AS (
    SELECT
        COUNT(CASE WHEN s3.hi_pfm_flg = 1 AND s1.tmn_eft_dt >= '2024-01-01' AND s1.tmn_eft_dt < '2025-01-01' THEN 1 END) AS hi_tmn_cnt_2024,
        COUNT(CASE WHEN s3.hi_pfm_flg = 1 AND s1.tmn_eft_dt >= '2025-01-01' AND s1.tmn_eft_dt < '2026-01-01' THEN 1 END) AS hi_tmn_cnt_2025
    FROM ads_ai_qa_trsf_tmn_f s1
    INNER JOIN ads_ai_qa_dept_df s2 ON s1.dept_id = s2.dept_id
        AND s2.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    INNER JOIN ads_ai_qa_emp_df s3 ON s1.emp_id = s3.emp_id
        AND s3.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE s1.real_emp_cls_cd IN ('101', '115', '118')
      AND s2.dept_nm_lvl1 = '中国区'
      AND s1.tmn_eft_dt >= '2024-01-01'
      AND s1.tmn_eft_dt < '2026-01-01'
),
emp AS (
    SELECT COUNT(CASE WHEN hi_pfm_flg = 1 THEN 1 END) AS hi_emp_cnt
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101', '115', '118')
      AND dept_nm_lvl1 = '中国区'
)
SELECT
    ROUND(t.hi_tmn_cnt_2024::numeric / NULLIF(e.hi_emp_cnt, 0) * 100, 2) AS "2024年高绩效流失率",
    ROUND(t.hi_tmn_cnt_2025::numeric / NULLIF(e.hi_emp_cnt, 0) * 100, 2) AS "2025年高绩效流失率",
    ROUND((t.hi_tmn_cnt_2025 - t.hi_tmn_cnt_2024)::numeric / NULLIF(e.hi_emp_cnt, 0) * 100, 2) AS "同比变化(百分点)"
FROM tmn t, emp e
```

### 关键要点

- tmn CTE 的 WHERE 大范围 `>='2024-01-01' AND <'2026-01-01'` 覆盖两年，内部用条件聚合按年拆分
- emp CTE 的子群筛选用条件聚合 `COUNT(CASE WHEN hi_pfm_flg = 1 THEN 1 END)`，不在 WHERE 中直接限定（保留全量扫描以备后续扩展）
- 此示例是**子群流失率**同比：分子分母都限定高绩效子群

---

## 八、按维度拆分流失率排名（+部门主管）

**适用场景**："各二级部门高绩效流失率排名及对应部门主管名单"等复杂查询。

### 核心规则

1. **每个维度独立套用完整公式**：分子分母都按维度 GROUP BY
2. **FULL OUTER JOIN**：tmn 和 emp 用 FULL OUTER JOIN，避免遗漏只有在职无离职或只有离职无在职的部门
3. **部门主管**：此处是流失率排名的辅助维度，属于调转入离派生查询；从 dept_df 的 mng_emp_nm 获取时加 `dept_lvl=对应层级`，但**不要**加 `eft_sts_cd='A'`，JOIN emp_df 时必须加 `emp_sts_cd='A'`

### SQL 模板：各二级部门高绩效流失率排名 + 部门主管

```sql
WITH tmn AS (
    SELECT
        d.dept_nm_lvl2,
        COUNT(1) AS hi_tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    LEFT JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
      AND t.real_emp_cls_cd IN ('101', '115', '118')
      AND d.dept_nm_lvl1 = '中国区'
      AND e.hi_pfm_flg = 1
    GROUP BY d.dept_nm_lvl2
),
emp AS (
    SELECT
        dept_nm_lvl2,
        COUNT(DISTINCT emp_id) AS hi_emp_cnt
    FROM ads_ai_qa_emp_df
    WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
      AND emp_sts_cd = 'A'
      AND real_emp_cls_cd IN ('101', '115', '118')
      AND dept_nm_lvl1 = '中国区'
      AND hi_pfm_flg = 1
    GROUP BY dept_nm_lvl2
),
mng AS (
    SELECT d.dept_nm AS dept_nm_lvl2, d.mng_emp_nm
    FROM ads_ai_qa_dept_df d
    INNER JOIN ads_ai_qa_emp_df e
        ON d.mng_emp_id = e.emp_id
        AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
    WHERE d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
      AND d.dept_lvl = 2
      AND d.dept_nm_lvl1 = '中国区'
      AND e.emp_sts_cd = 'A'
)
SELECT
    COALESCE(e.dept_nm_lvl2, t.dept_nm_lvl2) AS 二级部门,
    COALESCE(t.hi_tmn_cnt, 0) AS 高绩效离职人次,
    COALESCE(e.hi_emp_cnt, 0) AS 高绩效在职人数,
    ROUND(COALESCE(t.hi_tmn_cnt, 0)::numeric / NULLIF(e.hi_emp_cnt, 0) * 100, 2) AS 高绩效流失率,
    m.mng_emp_nm AS 部门主管
FROM emp e
FULL OUTER JOIN tmn t ON e.dept_nm_lvl2 = t.dept_nm_lvl2
LEFT JOIN mng m ON COALESCE(e.dept_nm_lvl2, t.dept_nm_lvl2) = m.dept_nm_lvl2
ORDER BY 高绩效流失率 DESC NULLS LAST
```

### 关键要点

- tmn CTE 中 JOIN emp_df 用 `LEFT JOIN`（离职员工可能找不到在职记录），子群筛选 `e.hi_pfm_flg = 1` 放在 WHERE 中
- emp 和 tmn 用 `FULL OUTER JOIN`，确保所有部门都出现在结果中
- mng CTE 查部门主管时**不要加 `d.eft_sts_cd = 'A'`**（本查询是流失率排名，失效部门也不能被过滤），但必须加 `e.emp_sts_cd = 'A'` 避免已离职负责人出现
- `COALESCE(t.hi_tmn_cnt, 0)` 处理某部门无离职的情况
- `ORDER BY 高绩效流失率 DESC NULLS LAST` 确保无法计算的排在最后
