---
name: intent-advanced
description: >
  跨表专项查询（CROSS_TABLE）子场景规则——需 JOIN 非主表或多日快照的查询指南。
  覆盖月度趋势/同比环比、特定绩效期次（pfm_f）、教育经历与院校排名（edu_f）、
  外派经历（exp_asgn_f）、人才标签（talent_tag_f）、汇报关系（rpt_f）等，
  约占评测集 17% 的查询。
  当 routing-sql.md 判定子场景为 CROSS_TABLE 时读取本文件。
---

# 跨表专项查询（CROSS_TABLE）

> **适用场景**：需要 JOIN 非主表（pfm_f/edu_f/exp_asgn_f/talent_tag_f/rpt_f）或多日快照的查询。
> 包括：月度趋势/同比环比、特定期次绩效明细、教育经历（院校排名）、外派、人才标签、汇报关系。
> 覆盖评测集约 17% 的查询。使用前必须先读取 sql-query.md 通用规则。

**目录**：[一、月度趋势与同比环比](#一月度趋势与同比环比) · [二、绩效明细查询](#二绩效明细查询pfm_f-表) · [三、教育经历查询](#三教育经历查询edu_f-表) · [四、外派经历](#四外派经历exp_asgn_f-表) · [五、人才标签](#五人才标签talent_tag_f-表) · [六、汇报关系与组织诊断](#六汇报关系与组织诊断) · [七、部门负责人绩效查询](#七部门负责人绩效查询) · [八、XX年入职+院校查询](#八xx年入职院校查询) · [九、博士占比/博士人数查询](#九博士占比博士人数查询) · [十、绩效期次回退规则](#十绩效期次回退规则) · [十一、外派经历查询](#十一外派经历查询)

---

## 一、月度趋势与同比环比

### 月末快照取法铁律

date 是 int 类型 yyyymmdd，每天一个全量快照。按月/年统计趋势时**必须动态获取每月最后快照日**，禁止硬编码 `date IN (20250131, 20250228, ...)`。

```sql
-- 获取每月末快照日期
SELECT date/100 AS ym, MAX(date) AS month_end_date
FROM ads_ai_qa_emp_df GROUP BY date/100
```

**禁止** `GROUP BY date/100` 后直接 `COUNT(DISTINCT emp_id)`（累积全月所有日快照导致人数偏大）。正确：先 JOIN 月末快照子查询限定到单日，再 COUNT。

**铁律**：季度末人数只取该季度最后一个月的单个快照，禁止累积季度内多个月再去重。Q1=3月末，Q2=6月末，Q3=9月末，Q4=12月末。

### 上月末/上上月末快照日取法

```sql
-- 上月末快照
SELECT MAX(date) FROM ads_ai_qa_emp_df
WHERE date/100 = CAST(TO_CHAR(CURRENT_DATE - INTERVAL '1 month', 'YYYYMM') AS INT)
-- 上上月末快照
SELECT MAX(date) FROM ads_ai_qa_emp_df
WHERE date/100 = CAST(TO_CHAR(CURRENT_DATE - INTERVAL '2 month', 'YYYYMM') AS INT)
```

环比场景必须用此方式动态取月末快照日，禁止用 `ORDER BY date DESC LIMIT 2` 取最近两天。

### 季度末人数

```sql
SELECT MAX(date) FROM ads_ai_qa_emp_df WHERE date/100 = 202603  -- Q1末
```

### 同比环比基准日期规则（极其重要）

同比/环比查询中两个时间点必须用**相同基准派生**（如以 CURRENT_DATE-1 为基准同时算出当期和去年同日的 date 值），禁止当期用 MAX(date) 而去年用 CURRENT_DATE-INTERVAL（两者可能不一致导致对比偏差）。

### 时间定义补充

| 表述 | 定义 |
|------|------|
| 本月 | 本月第一天 ~ 今天（只设下界） |
| 上个月 | 上月第一天 ~ 上月最后一天（设上下界） |
| 去年/去年一年 | 去年1月1日 ~ 12月31日（自然年） |
| 过去一年/最近一年 | 去年今天 ~ 今天前一天（滚动12个月） |
| 近X个月 | 今天往前推X个月 |
| 本季度 | 本季度第一天 ~ 今天 |

**极易混淆**：'去年一年' ≠ '过去一年'。

---

## 二、绩效明细查询（pfm_f 表）

### 表结构 ads_ai_qa_pfm_f

字段：emp_id, pfm_prd(绩效期次如'2025H2'), pfm_bgn_dt(期次开始), pfm_end_dt(期次结束), pfm(绩效等级), hi_pfm_flg, bb_pfm_flg, lo_pfm_flg

绩效等级排序：S+ > S > A+ > A > B+ > B > B- > C > D

### 何时用 pfm_f vs emp_df

| 场景 | 用什么 |
|------|--------|
| 最近绩效/高绩效/低绩效/连续绩效 | emp_df 预计算字段（详见 intent-emp-basic.md） |
| 特定期次绩效（如"2025H2绩效为S的人"） | pfm_f |
| 历史绩效变化趋势 | pfm_f |
| 至少有N次绩效且其中有X等级 | pfm_f |
| 绩效差两档 | emp_df.two_lvl_dif_flg=1（禁止从 pfm_f 手动算） |
| 最近两次绩效 | emp_df.late_pfm + late_late_pfm |

### 禁止硬编码绩效期次

查「最近N次绩效」用 ROW_NUMBER：

```sql
WITH ranked AS (
  SELECT emp_id, pfm_prd, pfm,
    ROW_NUMBER() OVER(PARTITION BY emp_id ORDER BY pfm_prd DESC) AS rn
  FROM ads_ai_qa_pfm_f
)
SELECT * FROM ranked WHERE rn <= 2
```

### 期次回退规则

用户指定的期次（如 2026H1）可能尚未出绩效：
1. 先查实际最大期次：`SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_f`
2. 不存在则回退到上一个半年度（2026H1 → 2025H2）
3. 或直接用 emp_df 的 late_pfm 等字段避免期次问题

### 何时用 pfm_q_f（季度绩效表 ads_ai_qa_pfm_q_f）

> pfm_q_f 包含年度+半年度+季度所有绩效期次，pfm_prd 格式：`2022`(年度)、`2022H1`(半年度)、`2022Q1`(季度)。

| 场景 | 用什么 |
|------|--------|
| 最近绩效（默认，不指定粒度） | emp_df 预计算字段（late_pfm 等） |
| 特定半年度期次绩效（如"2025H2绩效为S的人"） | pfm_f |
| **特定季度期次绩效（如"2025Q2绩效为A的人"）** | **pfm_q_f** |
| **季度绩效变化趋势** | **pfm_q_f** |
| **季度绩效流失率（如"Q2绩优离职率"）** | **pfm_q_f**（详见 intent-rate.md 四-B） |
| 历史绩效变化趋势（年/半年度） | pfm_f |

**⚠️ pfm_f vs pfm_q_f 选择铁律**：
- **默认用 pfm_f**：用户未明确说"季度"时，绩效明细查询一律使用 `ads_ai_qa_pfm_f`
- **仅当用户明确指定季度时用 pfm_q_f**：问题中出现"季度绩效"、"Q1/Q2/Q3/Q4"、"本季度绩效"等明确季度意图时，使用 `ads_ai_qa_pfm_q_f`

### pfm_q_f SQL 模板

```sql
-- 查某部门 2025Q2 绩效为A及以上的员工
SELECT e.emp_nm, p.pfm_prd, p.pfm
FROM ads_ai_qa_pfm_q_f p
INNER JOIN ads_ai_qa_emp_df e ON p.emp_id = e.emp_id
    AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE p.pfm_prd = '2025Q2'
    AND p.pfm IN ('A', 'A+', 'S', 'S+')
    AND e.emp_sts_cd = 'A'
    AND e.real_emp_cls_cd IN ('101', '115', '118')
    AND e.dept_nm_lvl1 = '中国区'
```

### pfm_q_f 期次回退规则

季度期次回退：用户指定的季度（如 2026Q2）可能尚未出绩效：
1. 先查实际最大季度期次：`SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_q_f WHERE pfm_prd LIKE '%Q%'`
2. 不存在则回退到上一个季度（2026Q2 → 2026Q1 → 2025Q4）

---

## 三、教育经历查询（edu_f 表）

### 表结构 ads_ai_qa_edu_f

字段：emp_id, edu_deg_cd(学历编码), edu_deg_dscr(学历描述), sch_nm(学校名称-统计排名用 GROUP BY), sch_nm_std(标准化学校名-仅合并同校不同写法), mjr_nm(专业), frs_edu_deg_flg(是否第一学历), hi_edu_deg_flg(是否最高学历), qs100_flg, is_985_flg, is_211_flg, c9_flg, g5_flg, ivy_league_flg(常春藤), dbl_frs_cls_flg(双一流)

### 何时必须 JOIN edu_f

- QS100/985/211/C9/G5/常春藤/双一流标识
- 专业 mjr_nm
- sch_nm 按学校分组统计排名
- 最高学历院校名称（emp_df 只有 frs_sch_nm 第一学历）
- 博士占比计算（需完整编码集）

简单学历筛选（如'硕士以上'）直接用 emp_df.hi_edu_deg_cd，不需要 JOIN edu_f。

### sch_nm vs sch_nm_std（严禁混用）

- **sch_nm**（原始学校名）→ 统计学校人数分布、查特定院校，**默认使用**
- **sch_nm_std**（标准化学校名）→ 仅在需要合并同校不同写法时用

TOP10院校排名必须使用 sch_nm，禁止用 sch_nm_std。

### 去重规则（极其重要）

edu_f 一人可能多条教育经历，直接 JOIN 导致人数膨胀。统计人数/占比**必须去重**：

```sql
-- 方案1: EXISTS
WHERE EXISTS (SELECT 1 FROM ads_ai_qa_edu_f edu
  WHERE edu.emp_id = e.emp_id AND edu.qs100_flg = 1)

-- 方案2: 子查询先去重
INNER JOIN (SELECT DISTINCT emp_id FROM ads_ai_qa_edu_f
  WHERE qs100_flg = 1) edu ON e.emp_id = edu.emp_id
```

禁止直接 JOIN edu_f 后 COUNT(*) 统计人数。

### 特定院校精确匹配

查特定院校必须精确匹配 `sch_nm='清华大学'`，**禁止 ILIKE 模糊匹配**（会匹配到附属中学等）。
清北 = `sch_nm IN ('清华大学', '北京大学')`。

### 博士占比

博士编码完整集（禁止只用 E09/E10，会遗漏海外博士）：
`edu_deg_cd IN ('E09','E10','E13','A07','B07','G06')`

```sql
SELECT
  COUNT(DISTINCT CASE WHEN edu.emp_id IS NOT NULL THEN e.emp_id END) AS 博士人数,
  COUNT(DISTINCT e.emp_id) AS 总人数,
  ROUND(COUNT(DISTINCT CASE WHEN edu.emp_id IS NOT NULL THEN e.emp_id END)::numeric
    / NULLIF(COUNT(DISTINCT e.emp_id), 0) * 100, 1) AS 博士占比
FROM ads_ai_qa_emp_df e
LEFT JOIN (
  SELECT DISTINCT emp_id FROM ads_ai_qa_edu_f
  WHERE edu_deg_cd IN ('E09','E10','E13','A07','B07','G06')
) edu ON e.emp_id = edu.emp_id
WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND e.emp_sts_cd = 'A' AND e.real_emp_cls_cd IN ('101','115','118')
```

---

## 四、外派经历（exp_asgn_f 表）

### 表结构 ads_ai_qa_exp_asgn_f

字段：emp_id, bgn_dt(开始日期), end_dt(结束日期), area_desc(区域), cnr_desc(国家), loc_desc(地点), pos_nm(岗位)

**表名必须是 ads_ai_qa_exp_asgn_f**，禁止使用其他错误表名。该表可能存在权限限制，报权限不足时告知用户联系管理员。

```sql
FROM ads_ai_qa_exp_asgn_f ea
INNER JOIN ads_ai_qa_emp_df e ON ea.emp_id = e.emp_id
  AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE e.emp_sts_cd = 'A'
```

---

## 五、人才标签（talent_tag_f 表）

字段：emp_id, tag_categ_nm(目录名称), tag_dim_nm(维度名称), tag_nm(标签名称), tag_dscr(标签描述)

同一员工可能多条标签，统计人数用 COUNT(DISTINCT emp_id)。

---

## 六、汇报关系与组织诊断

### 汇报关系表 ads_ai_qa_rpt_f_tmp

字段：pos_id(职位编号), emp_id, emp_nm, rpt_pos_id(上级职位), rpt_emp_id(上级工号), rpt_emp_nm(上级姓名), rpt_emp_nm_path(汇报线姓名路径), rpt_emp_id_path(汇报线工号路径), pos_seq(岗位序号 0=主岗)

### 组织健康度诊断

涉及组织健康度、组织诊断、管理宽幅、管理配比时，**必须调用 `org_health_report` 工具**，**禁止自行编写 SQL**。

| 触发关键词 | 说明 |
|-----------|------|
| 组织健康度、组织诊断、组织架构分析、组织健康、管理宽幅、管理配比、组织报告 | 调用 org_health_report 工具 |

**使用方式**：
1. 从用户问题中提取部门名称
2. 调用 `org_health_report(dept_name="部门名称", sender_id=sender_id)` 工具
3. 工具返回**预渲染的完整 Markdown 报告**

**支持范围**：支持任意层级部门（一级~六级），不限于 12 个一级部门。

**⚠️ 输出规则（最高优先级）**：
- **原样输出工具返回的 Markdown 报告**，禁止重新组织格式、删除表格、改写章节结构
- **仅替换 `[请根据...]` 占位符**为基于报告数据的诊断和建议
- **禁止将表格数据转为纯文字描述**
- **禁止自行编写 SQL**
- **禁止自行发明分析维度**：组织健康度只包含管理宽幅、管理配比两项
- 当 `show_layer_depth=true` 时，必须输出"各层级人数分布"表格
- 仅一级部门展示"组织层级深度"（`show_layer_depth=true`），非一级部门不展示

**口径**：管理者统一用 mng_flg=1，仅零下属人数用 org_mng_flg=1。直接下属数用 bgt_main_pos_dir_sub_emp_cnt。**口径例外**：组织健康度诊断使用 ('101','115','116') 而非 118

---

## 七、部门负责人绩效查询

当需要查部门负责人的绩效明细时，结合 dept_df + emp_df + pfm_f：

```sql
SELECT d.dept_nm, d.mng_emp_nm, p.pfm_prd, p.pfm
FROM ads_ai_qa_dept_df d
INNER JOIN ads_ai_qa_emp_df e
  ON d.mng_emp_id = e.emp_id AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
INNER JOIN ads_ai_qa_pfm_f p ON e.emp_id = p.emp_id
WHERE d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
  AND d.eft_sts_cd = 'A' AND e.emp_sts_cd = 'A'
  AND d.dept_nm_lvl1 = '中国区' AND d.dept_nm_lvl2 = '广东分公司'
ORDER BY p.pfm_prd DESC
```

---

## 八、"XX年入职+院校"查询

涉及"入职"的院校查询，**必须从入职表(trsf_hire_f)出发**关联教育经历表，不能从 emp_df 查（因为已离职的入职人员会被遗漏）。

```sql
SELECT edu.sch_nm, COUNT(DISTINCT h.emp_id) AS cnt
FROM ads_ai_qa_trsf_hire_f h
INNER JOIN ads_ai_qa_dept_df d ON h.dept_id = d.dept_id
    AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
INNER JOIN ads_ai_qa_emp_df e ON h.emp_id = e.emp_id
    AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
INNER JOIN (
    SELECT emp_id, sch_nm FROM ads_ai_qa_edu_f
    WHERE frs_edu_deg_flg = 1
    GROUP BY 1, 2
) edu ON h.emp_id = edu.emp_id
WHERE h.real_emp_cls_cd IN ('101', '115', '118')
  AND d.dept_nm_lvl1 = '中国区'
  AND e.new_grdt_flg = 1
  AND h.hire_dt >= '2025-01-01' AND h.hire_dt < '2026-01-01'
GROUP BY edu.sch_nm
ORDER BY cnt DESC
```

---

## 九、博士占比/博士人数查询

**必须 LEFT JOIN 教育经历表(edu_f)**，禁止仅用 emp_df 的 hi_edu_deg_cd（结果会偏低）。

```sql
SELECT
  COUNT(DISTINCT e.emp_id) AS 总人数,
  COUNT(DISTINCT CASE WHEN edu.emp_id IS NOT NULL THEN e.emp_id END) AS 博士人数,
  ROUND(
    COUNT(DISTINCT CASE WHEN edu.emp_id IS NOT NULL THEN e.emp_id END)::numeric
    / NULLIF(COUNT(DISTINCT e.emp_id), 0) * 100, 2) AS 博士占比
FROM ads_ai_qa_emp_df e
LEFT JOIN (
    SELECT emp_id FROM ads_ai_qa_edu_f
    WHERE edu_deg_cd IN ('E09','E10','E13','A07','B07','G06')
    GROUP BY 1
) edu ON e.emp_id = edu.emp_id
WHERE e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND e.emp_sts_cd = 'A' AND e.real_emp_cls_cd IN ('101','115','118')
```

**3个关键点**：
1. **必须 LEFT JOIN edu_f**，禁止退化为 hi_edu_deg_cd
2. **博士编码必须完整**：E09=博士研究生, E10=博士, E13=博士后, A07=印度PHD, B07=印尼PHD, G06=其他博士
3. 如需按区域分组，加标准区域 CASE WHEN 和 GROUP BY

---

## 十、绩效期次回退规则

当用户指定的期次无数据时（如 2026H1），**直接回退到上一个半年度**（2026H1→2025H2），禁止执行探索性查询。

```sql
-- ⚠️ 2026H1 无数据，直接用 2025H2
INNER JOIN ads_ai_qa_pfm_f p ON e.emp_id = p.emp_id
    AND p.pfm_prd = '2025H2'

-- ❌ 禁止先探索再决定：
-- SELECT DISTINCT pfm_prd FROM ads_ai_qa_pfm_f ORDER BY pfm_prd DESC  ← 浪费步骤！
```

---

## 十一、外派经历查询

**表名必须是 ads_ai_qa_exp_asgn_f**，禁止使用其他错误表名。

```sql
SELECT COUNT(DISTINCT ea.emp_id) AS 外派员工数
FROM ads_ai_qa_exp_asgn_f ea
INNER JOIN ads_ai_qa_emp_df e ON ea.emp_id = e.emp_id
    AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE e.emp_sts_cd = 'A'
  AND e.real_emp_cls_cd IN ('101', '115', '118')
```

**⚠️ 该表可能存在权限限制**，如查询报权限不足，必须告知用户"该数据表暂无查询权限，请联系管理员申请"。禁止静默放弃或返回空结果。
