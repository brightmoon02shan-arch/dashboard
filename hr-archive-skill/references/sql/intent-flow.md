---
name: intent-flow
description: >
  人员流动查询（FLOW）子场景规则——入职/离职/转岗事件统计的完整指南。
  覆盖流动人次、人数、明细清单查询，约占评测集 23% 的查询。
  包含流动表结构（hire_f/tmn_f/trsf_in_f）、流动铁律（铁律A-K）、
  部门关联规则、应届生/校招判定、净增长计算等。
  当 routing-sql.md 判定子场景为 FLOW 时读取本文件。
  RATE 场景也需同时加载本文件（率计算分子遵循流动铁律）。
---

# 人员流动查询（FLOW）

> **适用场景**：入职/离职/转岗事件统计——人次、人数、明细清单。
> 覆盖评测集约 23% 的查询。使用前必须先读取 sql-query.md 通用规则。
>
> **离职率/流失率/闪离率计算** → [references/sql/intent-rate.md](references/sql/intent-rate.md)
> （率计算是独立子场景 RATE，本文件只覆盖流动事件统计。）

**目录**：[〇、部门表概要](#〇部门表概要) · [一、流动表结构](#一流动表结构) · [二、人员流动铁律](#二人员流动铁律每条流动-sql-必须遵守) · [三、时间规则](#三时间规则) · [四、入转调离 SQL 示例](#四入转调离-sql-示例) · [五、指标定义](#五指标定义) · [六、禁止从 emp_df 推断离职](#六禁止从-emp_df-推断离职) · [七、更多 SOP SQL 示例](#七更多-sop-sql-示例)

---

## 〇、部门表概要

### 部门表 ads_ai_qa_dept_df
部门维表。主键：date, dept_id。日快照表。**本文件覆盖的调转入离相关查询必须 JOIN 部门表，但不要过滤 eft_sts_cd='A'**；历史入职/离职/转入/转出/调动事件不能因为当前部门失效而被漏掉（详见 sql-query.md 铁律4）。
完整字段定义见 [references/sql/table-info-dept.md](references/sql/table-info-dept.md)。

---

## 一、流动表结构

### 入职表 ads_ai_qa_trsf_hire_f

无分区，每日全量覆盖。同一员工可能多次入职。
字段：emp_id, hire_dt(入职日期 text), dept_id, real_emp_cls_cd, pos_lvl, actn_rsn_cd(入职类型)

### 离职表 ads_ai_qa_trsf_tmn_f

无分区。
字段：emp_id, tmn_dt(操作日期), tmn_eft_dt(生效日期 text), dept_id, real_emp_cls_cd, psv_tmn_flg(被动离职 1/主动 0), last_hire_dt, pos_lvl, actn_rsn_cd(离职原因代码), tmn_comments(离职备注原因)

### 转岗表 ads_ai_qa_trsf_in_f

字段：emp_id, trsf_dt(转岗日期 text), in_dept_id(转入部门), out_dept_id(转出部门), in_real_emp_cls_cd, out_real_emp_cls_cd, pos_lvl

---

## 二、人员流动铁律（每条流动 SQL 必须遵守）

### 铁律A：流动表必须 INNER JOIN dept_df

第一个 JOIN 必须是 dept_df，通过流动表自身 dept_id 直接关联。**即使没有部门筛选也必须 JOIN**。部门条件必须用 `d.dept_nm_lvl1`，严禁从 emp_df 取。

```sql
SELECT ...
FROM ads_ai_qa_trsf_tmn_f t
INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
  AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
WHERE t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
  AND t.real_emp_cls_cd IN ('101','115','118')
```

### 铁律B：调转入离查询不要过滤有效部门

所有入职、离职、转入、转出、转岗、调入、调出、调动及其派生指标查询，JOIN `ads_ai_qa_dept_df` 时**禁止**添加 `d.eft_sts_cd = 'A'`、`dept_in.eft_sts_cd = 'A'`、`dept_out.eft_sts_cd = 'A'` 等有效部门过滤，**不应该屏蔽失效部门**。历史流动事件必须保留失效部门，否则离职人次、主动/被动离职人次、离职率、主动/被动离职率、闪离人次、闪离率等指标会漏数。

### 铁律C：员工类型从流动表自身取

入职表用 `h.real_emp_cls_cd`，离职表用 `t.real_emp_cls_cd`，转岗表转出用 `trsf.out_real_emp_cls_cd`、转入用 `trsf.in_real_emp_cls_cd`。所有流动查询都必须包含员工类型筛选。

**⚠️ 离职人员名单/明细必须展示员工类型**：查询离职人员名单或明细时，SELECT中**必须包含员工类型列**，并将编码转换为中文展示：

```sql
CASE t.real_emp_cls_cd
    WHEN '101' THEN '正式员工'
    WHEN '115' THEN '外包A'
    WHEN '118' THEN '外部顾问A'
    ELSE t.real_emp_cls_cd
END AS 员工类型
```

### 铁律D：COUNT 规则

- 问「人次」→ `COUNT(1)`
- 问「人数/多少人」→ `COUNT(DISTINCT emp_id)`（同一员工可能多条记录）
- 离职率公式分子统一 `COUNT(1)`
- **'引入'/'新进人员' = 入职**（从公司外部引入/新入职），不是内部"转入"。查询入职表 `ads_ai_qa_trsf_hire_f`，**不能**统计内部"转入"的人数
- **'N+引入'/'N+入职' = 职级>=N 的引入人数**：用户说"20+引入"意为职级20级及以上的入职人数，必须添加 `CAST(NULLIF(pos_lvl, '') AS INTEGER) >= N` 条件。类似地，"N+调入"→转入中 `pos_lvl >= N`。**禁止遗漏职级筛选条件**

### 铁律E：离职日期用 tmn_eft_dt（极其重要）

离职时间过滤必须用 tmn_eft_dt（生效日期），**禁止用 tmn_dt**（操作日期）。tmn_dt 是 HR 系统录入日期，不代表员工实际离职时间。

```sql
-- ❌ WHERE t.tmn_dt >= '2026-01-01'（操作日期，不是实际离职日期）
-- ✅ WHERE t.tmn_eft_dt >= '2026-01-01'（生效日期，正确）
```

日期对应：离职用 tmn_eft_dt，转岗用 trsf_dt，入职用 hire_dt。

### 铁律F：流动统计不限在职状态

统计入职/离职人次时**不要加 emp_sts_cd='A'**。已离职的人也曾经入职过，加在职限制会丢失数据。

### 铁律G：需要员工属性时额外 JOIN emp_df

流动表不含姓名/岗位序列/绩效/学历/应届生/base 地/管理者/蓝领标识。需要时先 JOIN dept_df，再额外 JOIN emp_df。

**⚠️ 入职/离职表 JOIN emp_df**：用最新快照即可（员工已入职/已离职，当前快照有其信息）：
```sql
LEFT JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
  AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
```

**⚠️ 转入转出表 JOIN emp_df**：**必须用转岗前一天的分区**（见铁律 H2），禁止用 MAX(date)：
```sql
LEFT JOIN ads_ai_qa_emp_df e ON trsf.emp_id = e.emp_id
  AND e.date = CAST(TO_CHAR(trsf.trsf_dt::date - INTERVAL '1 day', 'YYYYMMDD') AS INT)
```

注意：流动表 pos_lvl 是事件时快照，emp_df 的 pos_lvl 是当前职级，根据语境选用。

### 铁律H：禁止经由 emp_df 间接关联部门

错误路径：trsf_tmn_f → emp_df → dept_df（离职员工可能已调岗，emp_df 的 dept_id 是当前部门不是离职时部门）。正确：trsf_tmn_f → dept_df（直接用 t.dept_id）。

### 铁律I：转入转出必须两次 JOIN dept_df

查询某部门的转入/转出人数时，**必须同时关联转入部门和转出部门**，并用部门名称做排除条件排除内部调动：
- 查"A部门转入了多少人"：`dept_in.dept_nm_lvl1 = 'A部门' AND dept_out.dept_nm_lvl1 != 'A部门'`
- 查"A部门转出了多少人"：`dept_out.dept_nm_lvl1 = 'A部门' AND dept_in.dept_nm_lvl1 != 'A部门'`

```sql
INNER JOIN ads_ai_qa_dept_df dept_in ON trsf.in_dept_id = dept_in.dept_id
  AND dept_in.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
LEFT JOIN ads_ai_qa_dept_df dept_out ON trsf.out_dept_id = dept_out.dept_id
  AND dept_out.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
WHERE dept_in.dept_nm_lvl1 = 'A' AND dept_out.dept_nm_lvl1 != 'A'  -- 查A部门转入
```

**错误**：只关联一次部门表、只用 `t.in_dept_id != t.out_dept_id` 做排除

### 铁律I2：转入转出 JOIN emp_df 必须用转岗前一天的分区（鉴权+维度正确性）

**强制规则**：转入转出查询中关联 `emp_df` 时，**禁止**使用 `e.date = (SELECT MAX(date) FROM emp_df)`，**必须**使用转岗前一天的分区：

```sql
-- ✅ 正确：关联转岗前一天的快照（正确匹配当时所在部门，正确鉴权）
LEFT JOIN ads_ai_qa_emp_df e
  ON trsf.emp_id = e.emp_id
  AND e.date = CAST(TO_CHAR(trsf.trsf_dt::date - INTERVAL '1 day', 'YYYYMMDD') AS INT)

-- ❌ 错误：关联最新快照（转岗后部门已变，鉴权和维度取值都不对）
LEFT JOIN ads_ai_qa_emp_df e
  ON trsf.emp_id = e.emp_id
  AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
```

**原因**：员工转岗后 emp_df 最新快照已反映新部门，用 MAX(date) 关联会取到转岗后的部门维度，导致：
1. 行级权限鉴权错误（应按转岗前部门判断权限）
2. 部门维度取值错误（统计"A部门转出"时，从 emp_df 取的部门已是 B 部门）

**性能提示**：可加日期范围约束提升性能（根据查询时间窗推导）：
```sql
LEFT JOIN ads_ai_qa_emp_df e
  ON trsf.emp_id = e.emp_id
  AND e.date = CAST(TO_CHAR(trsf.trsf_dt::date - INTERVAL '1 day', 'YYYYMMDD') AS INT)
  AND e.date >= 20250101   -- 查询时间窗开始日-1天对应的分区下限
  AND e.date < 20260101    -- 查询时间窗结束日对应的分区上限
```

### 铁律J：离职原因与离职备注字段选择

离职表有两个容易混淆的字段，必须根据用户问法精确选择：

| 用户问法 | 使用字段 | 字段含义 | 输出示例 |
|---------|---------|---------|---------|
| "离职原因" | `actn_rsn_cd` | 操作原因代码（枚举值） | R20:被动离职-非个人过错-不能胜任工作 |
| "离职备注"/"离职备注原因" | `tmn_comments` | 自由文本备注 | 因个人原因离职，换个工作城市 |

- **未明确提及"备注"时，只输出 `actn_rsn_cd`，禁止输出 `tmn_comments`**
- 两个字段不混用、不同时输出（除非用户明确要求两者都看）

### 铁律K：禁止以 emp_df 为主表反向 LEFT JOIN 流动表统计离职人次

**⚠️ 这是已发生的高频错误。** 当需要同时计算"子群在职人数"和"子群离职人次"时，**禁止**合并到一个查询中用 `emp_df LEFT JOIN trsf_tmn_f` 实现。

```sql
-- ❌ 严禁：emp 为主表 LEFT JOIN 离职表
FROM ads_ai_qa_emp_df e
LEFT JOIN ads_ai_qa_trsf_tmn_f t ON e.emp_id = t.emp_id
WHERE e.emp_sts_cd = 'A'  -- 已离职的人状态='I'，被过滤，永远匹配不到

-- ✅ 正确：分离为两个独立 CTE
-- CTE1: 从 trsf_tmn_f 统计离职人次（以流动表为主表，INNER JOIN dept_df）
-- CTE2: 从 emp_df 统计在职人数
-- 最后 SELECT JOIN 合并
```

**为什么错**：
1. `emp_sts_cd = 'A'` 排除了已离职人员（状态='I'），LEFT JOIN 到离职表永远匹配不到
2. 违反铁律A（流动表必须为 FROM 的第一张表）
3. 违反铁律G（部门从 emp_df 取可能与离职时部门不一致）

**正确做法**：见 [intent-rate.md 的 CTE 结构铁律](#)，分子分母必须分离为独立 CTE。

---

## 三、时间规则

### 默认时间范围

人员流动查询（入/离/转）若用户未指定时间，**默认当前年度**（当年1月1日~今天）。流失率/离职率查询中 tmn 的时间范围也必须加，即使用户只说了率没提时间。

```sql
WHERE t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
```

### 今年/本月只设下界不设上界（极其重要）

```sql
-- 错误：加了上界截断
WHERE tmn_eft_dt >= '2026-01-01' AND tmn_eft_dt < '2026-04-08'
-- 正确：只设下界
WHERE tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
```

只有'上个月'/'去年'/'2025年'等已结束时间段才同时写上下界。

### 时间表述速查

| 表述 | SQL |
|------|-----|
| 本月初 | `DATE_TRUNC('month', CURRENT_DATE)` |
| 上月初 | `DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')` |
| 上月末 | `DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 day'` |
| 去年初 | `DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year')` |
| 本季度初 | `DATE_TRUNC('quarter', CURRENT_DATE)` |
| 去年 | 去年1月1日 ~ 12月31日（自然年） |
| 过去一年 | 去年今天 ~ 今天前一天（滚动12个月） |

**极易混淆**：'去年一年' ≠ '过去一年'，前者自然年，后者滚动12个月。

---

## 四、入转调离 SQL 示例

### 入职统计

```sql
SELECT COUNT(1) AS hire_cnt
FROM ads_ai_qa_trsf_hire_f h
INNER JOIN ads_ai_qa_dept_df d ON h.dept_id = d.dept_id
  AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
WHERE d.dept_nm_lvl1 = '中国区'
  AND h.hire_dt >= '2026-01-01'
  AND h.real_emp_cls_cd IN ('101','115','118')
```

### 离职明细（人员名单必须展示员工类型）

```sql
SELECT e.emp_nm, t.tmn_eft_dt,
  CASE t.real_emp_cls_cd WHEN '101' THEN '正式员工' WHEN '115' THEN '外包A'
    WHEN '118' THEN '外部顾问A' END AS 员工类型
FROM ads_ai_qa_trsf_tmn_f t
INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
  AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
LEFT JOIN ads_ai_qa_emp_df e ON t.emp_id = e.emp_id
  AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE d.dept_nm_lvl1 = '中国区' AND d.dept_nm_lvl2 = '湖北分公司'
  AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
  AND t.real_emp_cls_cd IN ('101','115','118')
```

### 转出统计

```sql
SELECT COUNT(DISTINCT trsf.emp_id)
FROM ads_ai_qa_trsf_in_f trsf
INNER JOIN ads_ai_qa_dept_df dept_out ON trsf.out_dept_id = dept_out.dept_id
  AND dept_out.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
INNER JOIN ads_ai_qa_dept_df dept_in ON trsf.in_dept_id = dept_in.dept_id
  AND dept_in.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
LEFT JOIN ads_ai_qa_emp_df e ON trsf.emp_id = e.emp_id
  AND e.date = CAST(TO_CHAR(trsf.trsf_dt::date - INTERVAL '1 day', 'YYYYMMDD') AS INT)
WHERE dept_out.dept_nm_lvl1 = '中国区' AND dept_in.dept_nm_lvl1 != '中国区'
  AND trsf.trsf_dt >= '2025-01-01' AND trsf.trsf_dt < '2026-01-01'
  AND trsf.out_real_emp_cls_cd IN ('101','115','118')
```

---

## 五、指标定义

| 指标 | 说明 |
|------|------|
| 入职人次 | COUNT(1) from hire_f，口径('101','115','118') |
| 离职人次 | COUNT(1) from tmn_f，口径('101','115','118')，日期用 tmn_eft_dt |
| 主动离职 | psv_tmn_flg=0 |
| 被动离职 | psv_tmn_flg=1 |
| 转入人数 | 以转入部门统计，排除内部调动(in_dept!=out_dept) |
| 转出人数 | 以转出部门统计 |
| 净增长 | 入职+转入-转出-离职 |
| 净增长率 | 净增长人次 / 期初在职人数（期初=统计周期第一天的在职人数） |

---

## 六、禁止从 emp_df 推断离职

```sql
-- 严禁：从员工表推断离职
SELECT COUNT(*) FROM ads_ai_qa_emp_df WHERE emp_sts_cd = 'I'
-- 正确：离职必须从离职表统计
SELECT COUNT(1) FROM ads_ai_qa_trsf_tmn_f t ...
```

emp_sts_cd='I' 只反映当前状态，无法限定时间区间；同一员工可能多次入离职；已离职又入职的不会被统计。

---

## 七、更多 SOP SQL 示例

### 示例1：2025年各月入职和离职人数

```sql
WITH hire AS (
    SELECT TO_CHAR(h.hire_dt::date, 'YYYY-MM') AS month,
           COUNT(1) AS hire_cnt
    FROM ads_ai_qa_trsf_hire_f h
    JOIN ads_ai_qa_dept_df d ON h.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    WHERE h.real_emp_cls_cd IN ('101', '115', '118')
      AND h.hire_dt >= '2025-01-01' AND h.hire_dt < '2026-01-01'
    GROUP BY TO_CHAR(h.hire_dt::date, 'YYYY-MM')
),
tmn AS (
    SELECT TO_CHAR(t.tmn_eft_dt::date, 'YYYY-MM') AS month,
           COUNT(1) AS tmn_cnt
    FROM ads_ai_qa_trsf_tmn_f t
    JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
        AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
    WHERE t.real_emp_cls_cd IN ('101', '115', '118')
      AND t.tmn_eft_dt >= '2025-01-01' AND t.tmn_eft_dt < '2026-01-01'
    GROUP BY TO_CHAR(t.tmn_eft_dt::date, 'YYYY-MM')
)
SELECT COALESCE(h.month, t.month) AS month,
       COALESCE(h.hire_cnt, 0) AS hire_cnt,
       COALESCE(t.tmn_cnt, 0) AS tmn_cnt
FROM hire h
FULL OUTER JOIN tmn t ON h.month = t.month
ORDER BY month
```

### 示例2：某部门主动离职人数

```sql
SELECT COUNT(1) AS tmn_cnt
FROM ads_ai_qa_trsf_tmn_f t
JOIN ads_ai_qa_dept_df d ON d.dept_id = t.dept_id
    AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
WHERE t.psv_tmn_flg = '0'
  AND t.tmn_eft_dt >= '2025-12-01' AND t.tmn_eft_dt < '2026-01-01'
  AND d.dept_nm_lvl1 = '人力资源部'
  AND t.real_emp_cls_cd IN ('101', '115', '118')
```

### 示例3：中国区上月转入人数

```sql
SELECT COUNT(1)
FROM ads_ai_qa_trsf_in_f AS trsf
INNER JOIN ads_ai_qa_dept_df dept_in
    ON trsf.in_dept_id = dept_in.dept_id
    AND dept_in.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
LEFT JOIN ads_ai_qa_dept_df dept_out
    ON trsf.out_dept_id = dept_out.dept_id
    AND dept_out.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
LEFT JOIN ads_ai_qa_emp_df e
    ON trsf.emp_id = e.emp_id
    AND e.date = CAST(TO_CHAR(trsf.trsf_dt::date - INTERVAL '1 day', 'YYYYMMDD') AS INT)
WHERE dept_in.dept_nm_lvl1 = '中国区'
    AND dept_out.dept_nm_lvl1 != '中国区'
    AND trsf.trsf_dt >= TO_CHAR(DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month'), 'YYYY-MM-DD')
    AND trsf.trsf_dt < TO_CHAR(DATE_TRUNC('month', CURRENT_DATE), 'YYYY-MM-DD')
    AND trsf.in_real_emp_cls_cd IN ('101', '115', '118')
```

### 示例4：中国区上月离职的应届生

```sql
SELECT COUNT(1)
FROM ads_ai_qa_trsf_tmn_f AS tmn
INNER JOIN ads_ai_qa_dept_df dept
    ON tmn.dept_id = dept.dept_id
    AND dept.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
INNER JOIN ads_ai_qa_emp_df AS emp
    ON tmn.emp_id = emp.emp_id
    AND emp.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE dept.dept_nm_lvl1 = '中国区'
    AND tmn.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month'), 'YYYY-MM-DD')
    AND tmn.tmn_eft_dt < TO_CHAR(DATE_TRUNC('month', CURRENT_DATE), 'YYYY-MM-DD')
    AND emp.new_grdt_flg = 1
    AND tmn.real_emp_cls_cd IN ('101', '115', '118')
```

---

## 八、预入职 / 预离职 / 预转岗铁律

> **适用表**：`ads_ai_qa_pre_hire_f`、`ads_ai_qa_pre_tmn_f`、`ads_ai_qa_pre_trsf_f`。
> 与正式流动表一样，预表查询**必须**添加员工类型过滤条件，不能遗漏。

### 铁律P1：预表必须限制员工类型（极其重要）

**每条预表 SQL 都必须包含 `real_emp_cls_cd` 过滤条件**，具体取值根据用户查询的目标人群决定：

| 用户查询人群 | 员工类型取值 |
|-------------|-------------|
| 无特殊限定（默认） | `('101','115','118')` |
| 明确问正式员工 | `('101')` |
| 明确问外包员工 | `('115','116')` |
| 明确问实习生 | `('102')` |

各预表的员工类型字段来源不同：

| 预表 | 字段位置 | 过滤方式 |
|------|---------|---------|
| `pre_hire_f`（预入职） | 表自身 `real_emp_cls_cd` | 直接过滤 |
| `pre_trsf_f`（预转岗） | 表自身 `out_real_emp_cls_cd` / `in_real_emp_cls_cd` | 按转出/转入方向选用对应字段 |
| `pre_tmn_f`（预离职） | **表自身无该字段** | 必须 JOIN emp_df，用 `e.real_emp_cls_cd` 过滤 |

### 铁律P2：预离职必须 JOIN emp_df

`pre_tmn_f` 仅有 7 列（emp_id、dept_id、eft_dt、tmn_rsn_cd/nm、psv_tmn_flg、data_source），不含员工类型、姓名、职级、绩效。**任何预离职查询都必须 JOIN emp_df 获取员工类型并过滤**：

```sql
FROM ads_ai_qa_pre_tmn_f pre
INNER JOIN ads_ai_qa_dept_df d ON pre.dept_id = d.dept_id
  AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
INNER JOIN ads_ai_qa_emp_df e ON pre.emp_id = e.emp_id
  AND e.date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
WHERE e.real_emp_cls_cd IN ('101', '115', '118')   -- 铁律P1
```

### 铁律P3：预入职用 COUNT(DISTINCT ofr_id)，预离职/预转岗用 COUNT(DISTINCT emp_id)

- 预入职表主键是 `ofr_id`（一个候选人可能有多个 offer），统计人数用 `COUNT(DISTINCT ofr_id)`
- 预离职/预转岗主键是 `emp_id`，统计人数用 `COUNT(DISTINCT emp_id)`
