---
name: intent-emp-basic
description: >
  员工基础查询（EMP_BASIC）子场景规则——纯 emp_df 表查询的完整指南。
  覆盖人数统计、占比分布、条件筛选名单、排序查询、极值查询、平均值计算等，
  约占评测集 60% 的查询。包含绩效预计算字段规则、常见查询模式、易错陷阱。
  当 routing-sql.md 判定子场景为 EMP_BASIC 时读取本文件。
---

# 员工基础查询（EMP_BASIC）

> **适用场景**：纯 emp_df 查询——人数统计、占比分布、条件筛选名单、排序查询、极值查询、平均值计算等。
> 覆盖评测集约 60% 的查询。使用前必须先读取 sql-query.md 通用规则。

---

## 〇、主表概要

### 员工表 ads_ai_qa_emp_df
员工全量日快照主表。主键：date, emp_id。每日全量快照。
完整字段定义见 [references/sql/table-info-emp.md](references/sql/table-info-emp.md)。

### 部门表 ads_ai_qa_dept_df
部门维表。主键：date, dept_id。日快照表。**非调转入离场景查询部门表时默认过滤 eft_sts_cd='A'**；入职、离职、转入、转出、转岗、调入、调出、调动及其派生指标不要过滤有效部门（详见 sql-query.md 铁律4）。
完整字段定义见 [references/sql/table-info-dept.md](references/sql/table-info-dept.md)。

---

## 一、绩效预计算字段规则（极其重要）

emp_df 已包含绩效预计算字段，以下场景**直接用 emp_df，禁止 JOIN pfm_f**：

### 绩效标志字段完整映射

| 用户说法 | 预计算字段 | 含义 | 绩效等级范围 |
|---------|-----------|------|------------|
| 高绩效 / 绩效优秀 / 绩效突出 | `hi_pfm_flg = 1` | 当前绩效A及以上 | A, A+, S, S+ |
| 绩优 / 绩效不错 / 绩效B+以上 / 绩效好 | `late_pfm IN ('B+','*B','A','A+','S','S+')`（emp_df）或 `bb_pfm_flg = 1`（仅pfm_f） | 当前绩效B+及以上 | B+, *B, A, A+, S, S+ |
| 低绩效 / 绩效差 | `lo_pfm_flg = 1` | 当前绩效C或D | C, D |
| 连续高绩效 | `late_twi_good_flg = 1` | 最近两次均A及以上 | — |
| 连续绩优 / 连续两次B+及以上 | `late_twi_bb_flg = 1` | 最近两次均B+及以上 | — |
| 连续低绩效 / 连续绩效无改善 | `late_twi_bad_flg = 1` | 最近两次均为低绩效 | — |
| 绩效差两档 / 绩效差异大于2档 | `two_lvl_dif_flg = 1` | 禁止从 pfm_f 手动计算 | — |
| 最近绩效等级 | `late_pfm` | 文本如 'A'/'B+' | — |
| 倒数第二次绩效 | `late_late_pfm` | — | — |

### ⚠️ 绩效语义映射（必须严格区分，最常犯的错误）

| 用户说法 | 正确字段 | 错误字段 | 说明 |
|---------|---------|---------|------|
| "绩优" / "绩效不错" / "绩效好" | emp_df: `late_pfm IN ('B+','*B','A','A+','S','S+')`；pfm_f: `bb_pfm_flg = 1` | ~~hi_pfm_flg~~ | "绩优"=B+及以上，**不是**A及以上。**⚠️ emp_df 无 bb_pfm_flg** |
| "高绩效" / "绩效优秀" / "绩效突出" | `hi_pfm_flg = 1` | ~~bb_pfm_flg~~ | "高绩效"=A及以上 |
| "绩优应届生流失率" | emp_df: `late_pfm IN ('B+','*B','A','A+','S','S+')`；pfm_f: `bb_pfm_flg = 1` | ~~hi_pfm_flg~~ | "绩优"=B+及以上。**⚠️ emp_df 无 bb_pfm_flg，必须用 late_pfm** |
| "连续绩优" | `late_twi_bb_flg = 1` | ~~从pfm_f动态计算~~ | 必须用预计算字段 |
| "连续低绩效" | `late_twi_bad_flg = 1` | ~~从pfm_f动态计算~~ | 必须用预计算字段 |

### 预计算字段强制规则

凡涉及"连续绩优"/"连续高绩效"/"连续两次B+及以上"，**必须使用** emp_df 的预计算标志字段。**绝对禁止**从 pfm_f 表通过 ROW_NUMBER/窗口函数动态计算连续绩效。

```sql
-- ❌ 禁止：从 pfm_f 动态计算连续绩效
WITH ranked AS (
    SELECT emp_id, pfm, ROW_NUMBER() OVER (...) AS rn
    FROM ads_ai_qa_pfm_f ...
)
SELECT emp_id FROM ranked WHERE rn <= 2 AND pfm IN ('B+','A','A+','S','S+')

-- ✅ 正确：直接使用 emp_df 预计算字段
SELECT emp_id FROM ads_ai_qa_emp_df
WHERE late_twi_bb_flg = 1  -- 连续绩优
  AND date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
```

### 季度绩效预计算字段（用户明确指定"季度"时使用）

当用户明确提及"季度绩效"、"Q1/Q2/Q3/Q4绩效"、"本季度绩效"时，使用以下 `q_*` 前缀字段替代对应的年/半年度字段：

| 年/半年度字段 | 季度字段（含季度） | 使用场景 |
|-------------|------------------|---------|
| late_pfm | q_late_pfm | 最近一次绩效（含季度） |
| late_pfm_prd | q_late_pfm_prd | 最近一次绩效期次（含季度） |
| hi_pfm_flg | q_hi_pfm_flg | 高绩效标识（含季度） |
| lo_pfm_flg | q_lo_pfm_flg | 低绩效标识（含季度） |
| late_twi_good_flg | q_late_twi_good_flg | 连续高绩效（含季度） |
| late_twi_bb_flg | q_late_twi_bb_flg | 连续绩优（含季度） |
| late_twi_bad_flg | q_late_twi_bad_flg | 连续绩效无改善（含季度） |

**⚠️ 路由规则（极其重要）**：
- 用户未指定绩效粒度 → **默认**使用年/半年度字段（`late_pfm`、`hi_pfm_flg` 等），不变
- 用户明确说"季度绩效"/"Q1绩效"/"本季度绩效"/"季度高绩效" → 使用 `q_*` 前缀字段
- "XX部门绩优离职率" → 默认年/半年度（不变）
- "XX部门季度绩优离职率"/"Q2绩优离职率" → 使用季度字段

```sql
-- ✅ 用户问"季度高绩效员工有哪些"
SELECT emp_id, emp_nm FROM ads_ai_qa_emp_df
WHERE q_hi_pfm_flg = 1
  AND date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A' AND real_emp_cls_cd IN ('101','115','118')

-- ✅ 用户问"高绩效员工有哪些"（无季度关键词，用默认字段）
SELECT emp_id, emp_nm FROM ads_ai_qa_emp_df
WHERE hi_pfm_flg = 1
  AND date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A' AND real_emp_cls_cd IN ('101','115','118')
```

### 绩效分布与排序

- 绩效分布必须包含未评绩效：`COALESCE(NULLIF(late_pfm,''),'未出绩效')`。**禁止**用 `WHERE late_pfm IS NOT NULL` 过滤掉未评绩效员工
- 绩效等级从高到低排序：S+ > S > A+ > A > B+ > B > B- > C > D

### 最近N次绩效禁止硬编码期次

```sql
-- ❌ WHERE p1.pfm_prd = '2025H1' AND p2.pfm_prd = '2025H2'（硬编码，严禁！）
-- ✅ 动态取最近N次
WITH ranked AS (
    SELECT emp_id, pfm, pfm_prd,
           ROW_NUMBER() OVER (PARTITION BY emp_id ORDER BY pfm_end_dt DESC) AS rn
    FROM ads_ai_qa_pfm_f
    WHERE pfm_end_dt <= '2025-12-31'
)
SELECT emp_id FROM ranked WHERE rn <= 2
```

### 绩效期次回退规则

当用户指定的期次无数据时（如 2026H1），**直接回退到上一个半年度**（→ 2025H2），禁止执行 `SELECT DISTINCT pfm_prd` 等探索性查询。

回退规则：`2026H1` → `2025H2`，`2026H2` → `2026H1`，`2025H1` → `2024H2`

### 必须 JOIN pfm_f 的场景（详见 intent-advanced.md）

查询**特定期次**绩效（如"2025H2绩效"）、历史绩效变化趋势、至少有N次绩效且其中有X等级。

---

## 二、应届生规则

- 应届生筛选：`new_grdt_flg=1 AND real_emp_cls_cd IN('101','115','118') AND emp_sts_cd='A'`
- 按届别筛选用 new_grdt_grd_cd（string 类型如 '2025'），不用司龄反推
- 近5届：`new_grdt_grd_cd IN ('2022','2023','2024','2025','2026')`
- 问「各届应届生」「近N届占比」时必须用 new_grdt_grd_cd 分组，不能只用 new_grdt_flg=1 汇总

---

## 三、新入职定义（极其重要）

| 用户表述 | 正确做法 | 错误做法 |
|---------|---------|---------|
| "XX年新入职" | emp_df 筛选 `last_hire_dt>='XXXX-01-01'` | ~~查 trsf_hire_f~~ |
| "新入职"（未指定年份） | `last_hire_dt>=TO_CHAR(CURRENT_DATE-INTERVAL '1 year','YYYY-MM-DD')` | — |
| "入职不满X年" | `wrk_age_mi_y<X` | ~~last_hire_dt 手动算日期差~~ |
| "新员工" | `wrk_age_mi_y>=0 AND wrk_age_mi_y<=1` | — |

**禁止多余 JOIN hire_f**：emp_df 已有 last_hire_dt 和 mi_hire_dt。仅统计入职**人次** COUNT(1)、查入职事件明细（按月统计入职人数）时才需要 hire_f（→ 走 FLOW 子场景）。

**入职日期字段区分**：hire_dt=入职表入职日期，last_hire_dt=emp_df 最近入职日期，mi_hire_dt=小米首次入职日期。

---

## 四、学历字段规则

emp_df 已包含学历字段，以下场景**直接用 emp_df，禁止 JOIN edu_f**：
- 按最高学历筛选（如'硕士以上'）→ hi_edu_deg_cd
- 查第一学历和院校 → frs_edu_deg_cd + frs_sch_nm
- "最高学历是博士的人" → hi_edu_deg_cd

**必须 JOIN edu_f 的场景**（→ 走 CROSS_TABLE 子场景）：
QS100/985/211/C9/G5/常春藤标识、专业 mjr_nm、sch_nm 按学校分组排名、最高学历院校名称、博士占比计算。

**学历结构标准映射**（统计学历分布时必须含 ELSE 兜底）：
- 博士：`IN('A07','B07','E09','E10','E13','G06')`
- 硕士：`IN('A06','B06','E08','G05')`
- 本科：`IN('A04','B05','E07','G04')`
- 大专：`IN('A03','B04','E06')`
- ELSE '其他'

注意：'最高学历是博士'不含博士后 E13，'博士及以上'含 E13。

---

## 五、职级规则

- pos_lvl 是 string，比较时转整数：`NULLIF(pos_lvl,'')::int`
- 职级数字越大越高
- 高阶专家：`NULLIF(pos_lvl,'')::int>=19`
- 各职级人数分布用 `NULLIF(pos_lvl,'')::int`
- 在职员工的职级从 emp_df 取，不从流动表取（流动表是事件时快照）
- **多条件禁止添加多余上界**：每个"N级以上"条件独立翻译为 `>= N`，禁止受其他并列条件影响而添加上界

```sql
-- 用户问"18级以上和17级以上"
-- ❌ 给17级以上加了上界变成仅17级
WHERE NULLIF(pos_lvl,'')::int >= 17 AND NULLIF(pos_lvl,'')::int < 18
-- ✅ 两个独立条件
COUNT(CASE WHEN NULLIF(pos_lvl,'')::int >= 18 THEN 1 END) AS 职级18级以上人数,
COUNT(CASE WHEN NULLIF(pos_lvl,'')::int >= 17 THEN 1 END) AS 职级17级以上人数
```

---

## 六、部门负责人查询

从 dept_df 的 mng_emp_id/mng_emp_nm 获取。需加 dept_lvl=对应层级（二级 dept_lvl=2）。JOIN emp_df 时**必须加 emp_sts_cd='A'**（负责人可能已离职）。

```sql
SELECT d.dept_nm, d.mng_emp_nm, e.pos_lvl
FROM ads_ai_qa_dept_df d
INNER JOIN ads_ai_qa_emp_df e
  ON d.mng_emp_id = e.emp_id AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
  AND d.eft_sts_cd = 'A' AND d.dept_lvl = 2
  AND d.dept_nm_lvl1 = '中国区'
  AND e.emp_sts_cd = 'A'
```

---

## 七、标准分布划分（禁止自创）

**年龄段**（7档）和**司龄段**（7档）的标准 CASE SQL 表达式见 sql-query.md 八、标准分布划分。

**学历结构标准映射**（统计学历分布时必须含 ELSE 兜底）：

```sql
CASE
    WHEN hi_edu_deg_cd IN ('A07','B07','E09','E10','E13','G06') THEN '博士'
    WHEN hi_edu_deg_cd IN ('A06','B06','E08','G05') THEN '硕士'
    WHEN hi_edu_deg_cd IN ('A04','B05','E07','G04') THEN '本科'
    WHEN hi_edu_deg_cd IN ('A03','B04','E06') THEN '大专'
    ELSE '其他'  -- ⚠️ 必须有 ELSE 兜底，不能省略！
END AS 学历分类
```

注意：'最高学历是博士'不含博士后 E13，'博士及以上'含 E13。

---

## 八、其他标识字段与常用查询模式

| 字段/场景 | 用法 |
|----------|------|
| 未来星 | fur_flg=1 |
| 青年工程师 | yng_eng_flg=1 |
| 高薪 offer | hig_inc_flg=1 |
| 预离职 | pre_tmn_flg=1 |
| 职级停留天数 | pos_stay_days（如"停留超过3年"→pos_stay_days>1095） |
| 晋升次数 | pro_cnt |
| 近1次晋升日期 | late1_pro_dt |
| 合同到期 | ctr_end_dt |
| 生日 | bth_dt（text 'YYYY-MM-DD'，统计特定日期生日需提取月日） |

**晋升判定示例**：2025年晋升到18级 → `late1_pro_dt>='2025-01-01' AND late1_pro_dt<'2026-01-01' AND NULLIF(pos_lvl,'')::int=18`

### 生日/周年查询规则

**口径**：`('101','115','118')`

**闰年2月29日处理**：非闰年的 2/29 生日按 2/28 计算。

```sql
-- 查某月生日员工（PostgreSQL 语法）
SELECT emp_id, emp_nm, bth_dt
FROM ads_ai_qa_emp_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A'
  AND real_emp_cls_cd IN ('101', '115', '118')
  AND (
    CASE
      WHEN SUBSTRING(bth_dt, 6, 5) = '02-29'
        AND NOT (EXTRACT(YEAR FROM CURRENT_DATE)::int % 4 = 0
                 AND (EXTRACT(YEAR FROM CURRENT_DATE)::int % 100 != 0
                      OR EXTRACT(YEAR FROM CURRENT_DATE)::int % 400 = 0))
      THEN SUBSTRING(bth_dt, 6, 5) = '02-28'
      ELSE SUBSTRING(bth_dt, 6, 5) = TO_CHAR(CURRENT_DATE, 'MM-DD')
    END
  )
```

**周年查询**：用 `last_hire_dt`（最近一次入职日期），不是 `mi_hire_dt`。

```sql
-- 查本月入职周年员工
SELECT emp_id, emp_nm, last_hire_dt
FROM ads_ai_qa_emp_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A'
  AND real_emp_cls_cd IN ('101', '115', '118')
  AND SUBSTRING(last_hire_dt, 6, 2) = TO_CHAR(CURRENT_DATE, 'MM')
  AND last_hire_dt < TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD')
```

---

## 九、指标定义

| 指标 | 公式/说明 | 口径 |
|------|---------|------|
| 员工数 | COUNT(DISTINCT emp_id) | ('101','115','116') |
| 正式员工数 | real_emp_cls_cd='101' | — |
| 外包员工数 | IN('115','116') | — |
| 实习生 | IN('102') | — |
| 正式员工占比 | 正式员工数 / 员工数 | ('101','115','116') |
| 平均年龄 | AVG(age_y) | ('101','115','118') |
| 平均司龄 | AVG(wrk_age_mi_y) | ('101','115','118') |
| 管理者人数 | mng_flg=1 | ('101','115','116') |
| 管理幅度 | emp_cnt / mng_emp_cnt | — |
| 组织管理者人数 | org_mng_flg=1 | ('101','115','116') |
| 组织管理者幅度 | emp_cnt / org_mng_emp_cnt | — |
| 组织个数 | COUNT(DISTINCT dept_id)，排除智米、顾问群 | — |
| 组织平均人数 | emp_cnt / org_cnt | — |
| 大陆员工数 | substr(bas_loc_id,1,3)='CHN' | ('101','115','116') |
| 海外员工数 | substr(bas_loc_id,1,3)<>'CHN' | — |
| 非北京大陆员工数 | substr(bas_loc_id,1,3)='CHN' AND bas_loc_nm NOT LIKE '%北京%' | ('101','115','116') |
| 非京区域占比 | 非北京大陆员工数 / 大陆员工数 | ('101','115','116') |
| 月均在职人数 | 对日快照求均值（见下方模板），不是月末取值 | ('101','115','116') |
| 新员工人数 | wrk_age_mi_y>=0 AND wrk_age_mi_y<=1（司龄不满1年） | ('101','115','118') |
| 新员工离职人数 | 从 tmn_f 统计，JOIN emp_df 取 wrk_age_mi_y<1 | ('101','115','118') |

### 组织个数 / 组织平均人数 SQL 模板

查询组织个数和组织平均人数时，必须排除"智米"和"顾问群"，且部门条件需覆盖多层级：

```sql
-- 组织个数 + 组织平均人数（以某一级部门为例）
SELECT
    COUNT(DISTINCT dept_id) AS org_cnt,
    COUNT(DISTINCT emp_id) AS emp_cnt,
    ROUND(COUNT(DISTINCT emp_id)::numeric / NULLIF(COUNT(DISTINCT dept_id), 0), 1) AS org_avg_emp_cnt
FROM ads_ai_qa_emp_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A'
  AND real_emp_cls_cd IN ('101', '115', '116')
  AND dept_nm_lvl1 NOT IN ('智米', '顾问群')
  AND dept_nm_lvl1 = '中国区'  -- 按需替换部门层级和名称
```

### 组织管理者幅度 SQL 模板

```sql
-- 组织管理者人数 + 组织管理者幅度
SELECT
    COUNT(DISTINCT emp_id) AS emp_cnt,
    COUNT(DISTINCT CASE WHEN org_mng_flg = 1 THEN emp_id END) AS org_mng_emp_cnt,
    ROUND(COUNT(DISTINCT emp_id)::numeric
        / NULLIF(COUNT(DISTINCT CASE WHEN org_mng_flg = 1 THEN emp_id END), 0), 1) AS org_mng_span
FROM ads_ai_qa_emp_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND emp_sts_cd = 'A'
  AND real_emp_cls_cd IN ('101', '115', '116')
  AND dept_nm_lvl1 = '中国区'
```

### 月均在职人数 SQL 模板

月均在职人数 = 对日快照求均值，**不是月末取值**。公式：当月在职人天数 / 当月有在职人员的天数。

```sql
-- 某月月均在职人数（以2026年3月为例）
SELECT
    ROUND(
        COUNT(DISTINCT (date::text || '_' || emp_id))::numeric
        / NULLIF(COUNT(DISTINCT date), 0),
    1) AS avg_emp_cnt
FROM ads_ai_qa_emp_df
WHERE date >= 20260301 AND date < 20260401
  AND emp_sts_cd = 'A'
  AND real_emp_cls_cd IN ('101', '115', '116')
  AND dept_nm_lvl1 NOT IN ('智米', '顾问群')
  AND dept_nm_lvl1 = '中国区'  -- 按需替换
```

---

## 十、last_emp_id 跨身份关联

last_emp_id = 上一次入职工号（身份变更前的旧工号）。当员工身份变更（如外部顾问转正式员工），用离职表.emp_id = 员工表.last_emp_id 关联。

```sql
SELECT s3.emp_id, s3.emp_nm
FROM ads_ai_qa_trsf_tmn_f s1
INNER JOIN ads_ai_qa_dept_df s2 ON s1.dept_id=s2.dept_id
  AND s2.date=(SELECT MAX(date) FROM ads_ai_qa_dept_df)
INNER JOIN ads_ai_qa_emp_df s3 ON s1.emp_id=s3.last_emp_id
  AND s3.date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE s1.real_emp_cls_cd IN ('118')
  AND s1.tmn_eft_dt>='2026-01-01' AND s3.real_emp_cls_cd='101'
```
