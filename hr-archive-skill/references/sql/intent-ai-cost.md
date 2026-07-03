---
name: intent-ai-cost
description: >
  AI Token 成本问数（AI_COST）子场景规则。指导将 AI 成本相关的自然语言问题
  转换为查询 ads_mify_cost_di 的 SQL。包含渠道三分法 CASE WHEN、
  AI活跃人数/渗透率/人均AI成本/渠道占比/环比等指标公式、
  JOIN ads_ai_qa_emp_df 取部门归属、蓝领/外包A 口径区分（活跃人数不排除、渗透率排除）、SQL 模板与 few-shot。
  当 routing-sql.md 判定子场景为 AI_COST 时读取本文件。
---

# AI Token 成本问数（AI_COST）

> **适用场景**：AI成本、Token成本、AI渗透率、Coding/龙虾渠道占比、人均AI成本、AI活跃人数等**具体指标查询**。
> 使用前必须先读取 sql-query.md 通用规则、table-info-ai-cost.md 表结构。
>
> **⚠️ 边界**：本子场景只处理"问数"（多少/占比/排名/几个）。若用户要"生成报告/分析/整体情况" → 报告通道 AI_COST_REPORT，不在此处理。

---

## 一、核心口径（与 AI 人效报告保持一致）

| 指标 | 公式 | 说明 |
|------|------|------|
| AI成本 | `SUM(est_cost_amt)` | 单位元，含 MiMo 测算；**单表查询**，不 JOIN 员工表、不过滤在职状态、不过滤 oprid（离职人员历史成本仍计入），展示万元时 /10000 |
| AI活跃人数 | `COUNT(DISTINCT CASE WHEN est_cost_amt > 0 AND e.oprid IS NOT NULL AND e.oprid <> '' THEN oprid END)` | **LEFT JOIN emp_df**，仅统计**在职人员**（`emp_sts_cd='A'`）、过滤 oprid 空/空串；排除离职/不在职；**包含蓝领和外包A（不排除）** |
| 部门总人数 | `COUNT(DISTINCT CASE WHEN oprid IS NOT NULL AND oprid <> '' THEN oprid END)`（查 emp_df 最新快照，在职 + 排除蓝领/外包A） | **仅作渗透率分母**，按 oprid 去重与分子对齐 |
| AI渗透率 | AI活跃人数 / 部门总人数 × 100% | 分子分母均仅在职、过滤 oprid 空、排除蓝领、中国区排除外包A |
| 人均AI成本 | AI成本 / AI活跃人数（单位元） | 分子全量成本，分母仅在职活跃人数 |
| 渠道占比 | 某渠道 cost / 总 cost × 100% | channel 三分法 |
| 月环比 | (当月 - 上月) / 上月 × 100% | 按月聚合后计算 |

> **⚠️ 人数口径铁律**：
> - **AI成本**：单表查成本表 `SUM(est_cost_amt)`，不 JOIN 员工表，不过滤在职状态、不过滤 oprid（离职人员历史成本仍计入）。
> - **AI活跃人数**：LEFT JOIN `ads_ai_qa_emp_df`，仅统计**在职人员**（`emp_sts_cd='A'`）、过滤 oprid 空/空串，排除离职/不在职；**包含蓝领和外包A（不排除）**。部门归属取 emp_df。与报告展示列口径一致。
> - **人均AI成本**：分子=全量成本，分母=仅在职活跃人数（口径同 AI活跃人数，**包含蓝领和外包A**）。
> - **AI渗透率**：分子（活跃人数）和分母（部门总人数）都**额外排除蓝领、中国区排除外包A**：`emp_sts_cd='A' AND oprid <> '' AND blue_flg = 0 AND NOT (dept_id_lvl1='MW' AND real_emp_cls_cd='115')`，且分子分母均按 **oprid** 去重对齐。即：渗透率分子 < 活跃人数展示值，属正常口径差异。

---

## 二、渠道三分法 CASE WHEN

```sql
CASE
  WHEN channel IN ('Claude Code','OpenCode','MiCode','Codex',
                   'Cline','Roo Code','Kilo Code','Gemini CLI')
    THEN 'Coding'
  WHEN channel = 'MiTClaw'
    THEN '龙虾'
  ELSE '其它'
END AS channel_group
```

channel 有 NULL（约13%），归入"其它"。

---

## 三、查询铁律

1. **金额取 `est_cost_amt`**（含 MiMo），不用 `cost_amt`。单位元。
2. **按月聚合用日期范围条件**：`date >= 20260401 AND date < 20260501`，禁止 `date/100=202604`（全表扫描）。
3. **部门过滤/分组用 `dept_id_lvl{N}`**，不用 `dept_nm`（重名风险）。
4. **活跃人数判断**用 `est_cost_amt > 0`，AI 成本大于 0 即算活跃。
5. **AI成本**单表查成本表 `SUM(est_cost_amt)`，**不 JOIN 员工表**，不过滤在职状态。**活跃人数** LEFT JOIN `ads_ai_qa_emp_df`，仅统计**在职人员**（`emp_sts_cd='A'`），**包含蓝领和外包A（不排除）**，部门归属取 emp_df。**AI渗透率**的分子和分母**额外排除蓝领、中国区排除外包A**（`blue_flg=0 AND NOT (dept_id_lvl1='MW' AND real_emp_cls_cd='115')`），分子分母均按 oprid 去重对齐。渠道占比直接从成本表查，**无需 JOIN**。
6. **人力成本不在本表**：用户若问人力成本，告知走成本报告（cost_report），本子场景不查 `ads_ai_qa_cost_bgt_anlys_f`。
7. **默认月份**：用户未指定时取最新可用月（`SELECT MAX(date) FROM hr.ads_mify_cost_di` 取月份）。
8. **手机部默认排除新业务部**：用户问"手机部"时，默认查询手机部（排除新业务部），SQL 需加 `AND dept_id_lvl2 <> 'HW38'`。仅当用户**明确说"手机部含新业务部"或"手机部整体"**时才不排除。新业务部（`dept_id_lvl1='HW38'` 或 `dept_id_lvl2='HW38'`）可单独查询。与报告口径保持一致。

---

## 四、SQL 模板

### 模板1：单部门 AI 成本

```sql
SELECT SUM(est_cost_amt) AS ai_cost
FROM hr.ads_mify_cost_di
WHERE date >= 20260401 AND date < 20260501
  AND dept_id_lvl1 = 'HW'          -- 用 dept_id，先解析部门名→id
  AND dept_id_lvl2 <> 'HW38'       -- 手机部默认排除新业务部
```
示例问法："手机部4月Token成本多少"（默认排除新业务部）

### 模板1b：个人 AI 成本

```sql
SELECT SUM(est_cost_amt) AS ai_cost
FROM hr.ads_mify_cost_di
WHERE date >= 20260610 AND date < 20260611
  AND oprid = 'zhangsan'             -- 先通过 resolve 解析姓名→oprid
```
示例问法："张三昨天消耗的AI成本"、"李四6月的Token成本多少"

### 模板2：渠道三分法成本占比

```sql
SELECT CASE
         WHEN channel IN ('Claude Code','OpenCode','MiCode','Codex',
                          'Cline','Roo Code','Kilo Code','Gemini CLI')
           THEN 'Coding'
         WHEN channel = 'MiTClaw' THEN '龙虾'
         ELSE '其它'
       END AS channel_group,
       SUM(est_cost_amt) AS cost
FROM hr.ads_mify_cost_di
WHERE date >= 20260401 AND date < 20260501
GROUP BY 1
ORDER BY cost DESC
```
示例问法："Coding类成本占比多少"（占比 = 各组 cost / 总 cost，展示层计算）

### 模板3：AI活跃人数（单部门，在职，INNER JOIN emp_df 取部门归属）

```sql
SELECT COUNT(DISTINCT CASE
         WHEN a.est_cost_amt > 0
         THEN a.oprid END) AS ai_active_cnt
FROM hr.ads_mify_cost_di a
INNER JOIN hr.ads_ai_qa_emp_df e
  ON a.oprid = e.oprid
  AND e.date = (SELECT MAX(date) FROM hr.ads_ai_qa_emp_df WHERE date >= 20260401 AND date < 20260501)
  AND e.emp_sts_cd = 'A'
WHERE a.date >= 20260401 AND a.date < 20260501
  AND e.dept_id_lvl1 = 'HW'
  AND e.dept_id_lvl2 <> 'HW38'       -- 手机部默认排除新业务部
```
示例问法："手机部多少人用了AI"（仅统计在职人员、过滤 oprid 空，部门归属以 emp_df 为准；**包含蓝领和外包A**；默认排除新业务部）

### 模板4：各部门 AI 渗透率排名

```sql
WITH active AS (
  SELECT e.dept_id_lvl1 AS dept_id,
         e.dept_nm_lvl1 AS dept_name,
         COUNT(DISTINCT CASE
           WHEN a.est_cost_amt > 0
           THEN a.oprid END) AS active_cnt
  FROM hr.ads_mify_cost_di a
  INNER JOIN hr.ads_ai_qa_emp_df e
    ON a.oprid = e.oprid
    AND e.date = (SELECT MAX(date) FROM hr.ads_ai_qa_emp_df WHERE date >= 20260401 AND date < 20260501)
    AND e.emp_sts_cd = 'A'
    AND e.blue_flg = 0
    AND NOT (e.dept_id_lvl1='MW' AND e.real_emp_cls_cd='115')
  WHERE a.date >= 20260401 AND a.date < 20260501
  GROUP BY e.dept_id_lvl1, e.dept_nm_lvl1
),
total AS (
  SELECT dept_id_lvl1 AS dept_id,
         COUNT(DISTINCT CASE WHEN oprid IS NOT NULL AND oprid <> ''
                             THEN oprid END) AS total_hc
  FROM hr.ads_ai_qa_emp_df
  WHERE date = (SELECT MAX(date) FROM hr.ads_ai_qa_emp_df WHERE date >= 20260401 AND date < 20260501)
    AND emp_sts_cd = 'A'
    AND blue_flg = 0
    AND NOT (dept_id_lvl1='MW' AND real_emp_cls_cd='115')
  GROUP BY dept_id_lvl1
)
SELECT a.dept_name,
       a.active_cnt,
       t.total_hc,
       ROUND(a.active_cnt::numeric / NULLIF(t.total_hc,0) * 100, 1) AS penetration_rate
FROM active a JOIN total t ON a.dept_id = t.dept_id
ORDER BY penetration_rate DESC
```
示例问法："各部门AI渗透率排名"

### 模板5：人均 AI 成本（INNER JOIN，成本全量，活跃人数仅在职）

```sql
SELECT e.dept_nm_lvl1 AS dept_name,
       SUM(a.est_cost_amt) AS ai_cost,
       COUNT(DISTINCT CASE
         WHEN a.est_cost_amt > 0
         THEN a.oprid END) AS active_cnt,
       ROUND(SUM(a.est_cost_amt) / NULLIF(COUNT(DISTINCT CASE
         WHEN a.est_cost_amt > 0
         THEN a.oprid END),0)) AS per_capita_ai_cost
FROM hr.ads_mify_cost_di a
INNER JOIN hr.ads_ai_qa_emp_df e
  ON a.oprid = e.oprid
  AND e.date = (SELECT MAX(date) FROM hr.ads_ai_qa_emp_df WHERE date >= 20260401 AND date < 20260501)
  AND e.emp_sts_cd = 'A'
WHERE a.date >= 20260401 AND a.date < 20260501
GROUP BY e.dept_nm_lvl1
ORDER BY per_capita_ai_cost DESC
```
示例问法："各部门人均AI成本排名"（分子=全量成本，分母=仅在职活跃人数，部门归属以 emp_df 为准）

### 模板6：AI 成本月环比

```sql
SELECT CAST(date / 100 AS INTEGER) AS month,
       SUM(est_cost_amt) AS ai_cost
FROM hr.ads_mify_cost_di
WHERE date >= 20260301 AND date < 20260501
  AND dept_id_lvl1 = 'HW'
  AND dept_id_lvl2 <> 'HW38'       -- 手机部默认排除新业务部
GROUP BY date / 100
ORDER BY month
```
示例问法："手机部AI成本环比多少"（环比 = (当月-上月)/上月，展示层计算；默认排除新业务部）

---

## 五、few-shot 速查

| 用户问题 | 模板 | JOIN emp_df | 蓝领/外包A口径 | 手机部排除新业务部 |
|----------|------|------------|---------------|------------------|
| "手机部Token成本多少" | 模板1 | 否 | —（单表） | ✅ 加 `dept_id_lvl2 <> 'HW38'` |
| "手机部含新业务部的Token成本" | 模板1 | 否 | —（单表） | ❌ 不排除（用户明确要求） |
| "新业务部AI成本多少" | 模板1 | 否 | —（单表） | N/A（单独查新业务部，`dept_id_lvl2='HW38'`） |
| "张三昨天消耗的AI成本" | 模板1b | 否 | —（单表） | N/A |
| "Coding类成本占比" | 模板2 | 否 | —（单表） | N/A |
| "龙虾渠道花了多少" | 模板2（取龙虾行） | 否 | —（单表） | N/A |
| "手机部多少人用了AI" | 模板3 | INNER JOIN | **包含蓝领/外包A（不排除）** | ✅ 加 `e.dept_id_lvl2 <> 'HW38'` |
| "各部门AI渗透率排名" | 模板4 | INNER JOIN | **排除蓝领/外包A**（分子分母都排除） | N/A（按一级部门分组） |
| "各部门人均AI成本排名" | 模板5 | INNER JOIN | **包含蓝领/外包A（不排除）** | N/A（按一级部门分组） |
| "手机部AI成本环比多少" | 模板6 | 否 | —（单表） | ✅ 加 `dept_id_lvl2 <> 'HW38'` |

---

## 六、红线

1. **金额单位统一**：内部以元计算，展示按需换算"万"，禁止亿元换算。
2. **禁止编造**：所有数值来自 SQL 查询结果，不得推算。
3. **人力成本拒答转报告**：用户问人力成本，告知"人力成本请查看成本报告"，不查本表。
4. **数据保密**：AI 成本属敏感数据，输出遵循 output-sql.md 脱敏红线（禁止暴露表名/字段名/SQL）。
