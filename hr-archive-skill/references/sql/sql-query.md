---
name: sql-query
description: >
  SQL 查询通用规则——所有 SQL 子场景（EMP_BASIC/FLOW/RATE/CROSS_TABLE）的共用基座。
  包含核心表索引、通用铁律、SQL 语法规范、业务常识、模糊匹配规则、SQL 构建步骤。
  无论路由到哪个子场景，都必须先读取本文件，再读取对应 intent-*.md。
  当需要了解 HR 数据表结构总览、通用查询约束、date 快照机制、
  员工类型过滤、部门层级匹配、职级映射等基础规则时读取。
---

# SQL 查询通用规则

> **本文件是所有 SQL 子场景的共用基座。无论路由到哪个子场景，都必须先读取本文件。**
> 包含：核心表结构、通用铁律、SQL 语法、业务常识、匹配规则、构建步骤。
> 子场景专用规则在对应 intent 文件中：
> - 员工基础查询 → [references/sql/intent-emp-basic.md](references/sql/intent-emp-basic.md)
> - 人员流动查询 → [references/sql/intent-flow.md](references/sql/intent-flow.md)
> - 离职率/流失率 → [references/sql/intent-rate.md](references/sql/intent-rate.md)
> - 跨表专项查询 → [references/sql/intent-advanced.md](references/sql/intent-advanced.md)
>
> 各表完整字段定义见 table-info-*.md 文件。

**目录**：[一、核心表索引](#一核心表索引) · [二、通用铁律](#二通用铁律每条-sql-必须遵守) · [三、PostgreSQL 语法准则](#三postgresql-语法准则) · [四、业务常识速查](#四业务常识速查) · [五、匹配规则](#五匹配规则) · [六、查询安全](#六查询安全) · [七、SQL 构建步骤与自检](#七sql-构建步骤与自检) · [八、标准分布划分](#八标准分布划分禁止自创) · [九、反面教材](#九反面教材务必避免) · [十、输出格式要求](#十输出格式要求) · [十一、拒答场景](#十一拒答场景)

---

## 一、核心表索引

| 表名 | 用途 | 核心字段 | 意图路由 | 完整字段 |
|------|------|---------|---------|---------|
| ads_ai_qa_emp_df | 员工全量日快照主表（主键 date,emp_id） | emp_id, emp_nm, dept_id, dept_nm_lvl1~6, pos_lvl, real_emp_cls_cd, emp_sts_cd | [references/sql/intent-emp-basic.md](references/sql/intent-emp-basic.md) | [references/sql/table-info-emp.md](references/sql/table-info-emp.md) |
| ads_ai_qa_dept_df | 部门维表（主键 date,dept_id；非调转入离场景默认过滤 eft_sts_cd='A'，调转入离及其派生指标不加该过滤，见铁律4） | dept_id, dept_nm, dept_nm_lvl1~6, mng_emp_id, eft_sts_cd | [references/sql/intent-emp-basic.md](references/sql/intent-emp-basic.md) | [references/sql/table-info-dept.md](references/sql/table-info-dept.md) |
| ads_ai_qa_trsf_hire_f | 入职事实明细 | hire_dt(入职日期), actn_rsn_cd(入职类型/原因), dept_id(入职部门), real_emp_cls_cd(员工类型), pos_lvl(职级) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-hire.md](references/sql/table-info-hire.md) |
| ads_ai_qa_trsf_tmn_f | 离职事实明细 | tmn_dt(离职日期), actn_rsn_cd(离职原因:主动/被动等), psv_tmn_flg(被动离职标识), dept_id(离职部门), tmn_comments(离职备注原因) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-termination.md](references/sql/table-info-termination.md) |
| ads_ai_qa_trsf_in_f | 转入转出明细 | trsf_dt(异动日期), actn_rsn_cd(调动原因), in_dept_id/out_dept_id(转入/转出部门), in_pos_id/out_pos_id(转入/转出职位) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-transfer.md](references/sql/table-info-transfer.md) |
| ads_ai_qa_pfm_f | 绩效明细（多期次） | pfm_prd(绩效期次如2022H2), pfm(绩效等级), hi_pfm_flg(高绩效), bb_pfm_flg(绩优), lo_pfm_flg(低绩效) | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-pfm.md](references/sql/table-info-pfm.md) |
| ads_ai_qa_pfm_q_f | 绩效明细（含季度，多期次） | pfm_prd(绩效期次如2025Q2/2025H2), pfm(绩效等级), hi_pfm_flg(高绩效), bb_pfm_flg(绩优)。**仅当用户明确指定季度时使用** | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-pfm.md](references/sql/table-info-pfm.md) |
| ads_ai_qa_edu_f | 教育经历明细 | edu_deg_dscr(学历), sch_nm(学校), mjr_nm(专业), qs100_flg/is_985_flg/is_211_flg/dbl_frs_cls_flg(院校档次标识) | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-edu.md](references/sql/table-info-edu.md) |
| ads_ai_qa_exp_asgn_f | 外派经历 | bgn_dt/end_dt(外派起止日期), cnr_desc(外派国家), loc_desc(外派地), pos_nm(外派岗位) | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-expatriate.md](references/sql/table-info-expatriate.md) |
| ads_ai_qa_talent_tag_f | 人才标签 | tag_categ_nm(标签目录), tag_dim_nm(标签维度), tag_nm(标签名称), tag_dscr(标签描述) | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-talent-tag.md](references/sql/table-info-talent-tag.md) |
| ads_ai_qa_rpt_f_tmp | 汇报关系 | rpt_emp_nm(上级姓名), rpt_emp_nm_path(完整汇报链路径), pos_nm(职位), pos_seq(0=主岗) | [references/sql/intent-advanced.md](references/sql/intent-advanced.md) | [references/sql/table-info-rpt.md](references/sql/table-info-rpt.md) |
| ads_ai_qa_pre_hire_f | 预入职（offer状态为预入职） | ofr_id(offer id), eft_dt(预入职日期), pos_lvl(职级), real_emp_cls_cd(员工类型), psn_typ(招聘类型:1校招/2实习/3社招/4内部活水), fur_flg(未来星), hig_inc_flg(高薪offer) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-pre-hire.md](references/sql/table-info-pre-hire.md) |
| ads_ai_qa_pre_tmn_f | 预离职 | emp_id(员工工号), eft_dt(生效日期), dept_id(部门), tmn_rsn_cd(离职原因code), tmn_rsn_nm(离职原因文本), psv_tmn_flg(被动离职标识) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-pre-tmn.md](references/sql/table-info-pre-tmn.md) |
| ads_ai_qa_pre_trsf_f | 预转岗/预调动 | emp_id(员工工号), eft_dt(转岗日期), in_dept_id/out_dept_id(转入/转出部门), in_pos_lvl/out_pos_lvl(转入/转出职级), out_real_emp_cls_cd/in_real_emp_cls_cd(转出/转入员工类型) | [references/sql/intent-flow.md](references/sql/intent-flow.md) | [references/sql/table-info-pre-trsf.md](references/sql/table-info-pre-trsf.md) |
| ads_mify_cost_di | AI Token 调用成本明细日表（主键 date+oprid+渠道+模型） | date, oprid, dept_id_lvl1~5/dept_nm_lvl1~5, channel(渠道三分法核心), est_cost_amt(AI成本核心金额), input/output_token_usage, model_family | [references/sql/intent-ai-cost.md](references/sql/intent-ai-cost.md) | [references/sql/table-info-ai-cost.md](references/sql/table-info-ai-cost.md) |

---

## 二、通用铁律（每条 SQL 必须遵守）

### 铁律1：日快照表 date 禁止硬编码

emp_df 和 dept_df 的 date 必须用子查询取快照，严禁硬编码如 date=20260319，也禁止用 CURRENT_DATE 计算。

- **无时间范围时**：`date = (SELECT MAX(date) FROM 对应表)`
- **有时间范围时（按月/按季/指定月份查询）**：必须限定在用户指定的时间范围内取快照，如 `date = (SELECT MAX(date) FROM 对应表 WHERE date >= {月起} AND date < {月下月起})`，**禁止**忽略时间范围直接取全局 MAX(date)（否则会把未来月份的在职状态混入历史月份的统计，导致人数/渗透率失真）
- **唯一例外**：计算离职率需取已结束时间段的期末在职人数时可硬编码（如 date=20251231）

**时间范围未指定时**：用户未明确时间范围时，使用动态日期（如 `TO_CHAR(CURRENT_DATE - INTERVAL '1 year', 'YYYY-MM-DD')`），**禁止凭假设硬编码具体年份**。

### 铁律2：员工类型口径——先判断场景再选口径（极其重要）

**每条查询 emp_df 的 SQL 都必须包含 `emp_sts_cd='A'` 筛选在职员工。**

> **例外：率计算中 tmn CTE 内的 emp_df JOIN 不加 `emp_sts_cd='A'`。** 当 emp_df 作为离职表（trsf_tmn_f）的辅助 JOIN 表（用于获取 `late_pfm`、`hi_pfm_flg` 等属性筛选离职子群）时，**不过滤 emp_sts_cd**——因为已离职人员在最新快照中状态为 'I'，加此条件会导致离职人次为 0。详见 intent-flow.md 铁律 E 和 intent-rate.md CTE 结构铁律。

> **⚠️ 铁律2的优先级高于 `metrics.md` 的 Force Filter。** 只要查询涉及性别、年龄、司龄、工龄、职级、学历、生日、周年、高薪、青年工程师、未来星、部门负责人、应届生、管理者、高管、蓝领、白领中的**任何一个**，员工类型口径**必须用 `('101','115','118')`**，即使 `metrics.md` 中对应指标的 Force Filter 写的是 `(101,115,116)` 也必须覆盖。

#### 场景口径对照表

| 业务场景 | 典型问题示例 | 筛选条件 |
|---------|------------|---------|
| **组织概况** — 人数规模、base地分布（**不涉及**任何人员属性） | "有多少人"、"北京有多少员工"、"各部门人数" | `('101','115','116')` |
| **人员结构** — 性别/年龄/司龄/职级/学历/蓝领/白领/管理者等 | "平均年龄"、"男女比例"、"蓝领员工数" | `('101','115','118')` |
| **人员流动** — 入职/离职/转入/转出/闪离/净增长 | "今年入职了多少人"、"离职人次" | `('101','115','118')` |
| **人员绩效** — 绩效等级、高/低绩效、绩效分布 | "绩效B-的人"、"高绩效员工" | `('101','115','118')` |
| **人才盘点** — 高薪/高潜/未来星/青年工程师 | "高潜应届生"、"未来星名单" | `('101','115','118')` |
| **管理者** — 管理者人数、部门主管、高管 | "管理者有多少"、"高管有多少" | `('101','115','118')` |
| **组织健康度诊断** — 管理配比、管理宽幅 | "组织诊断"、"管理配比" | `('101','115','116')` |

#### 组合查询口径判定

| 组合情况 | 口径 | 示例 |
|---------|------|------|
| 组织概况 × 组织概况 | `('101','115','116')` | "各部门人数按base地分布" |
| 组织概况 × 非组织概况 | `('101','115','118')` | "北京员工的平均年龄" |
| 非组织概况 × 非组织概况 | `('101','115','118')` | "高绩效离职人员" |

**判断口诀**：只有"纯组织概况"交叉才用 `116`，一旦出现任何非组织概况要素，一律用 `118`。

#### 用户显式指定员工类型时

| 用户说法 | 筛选条件 |
|---------|---------|
| "正式员工" | `real_emp_cls_cd = '101'` |
| "外包员工" / "外包" | `real_emp_cls_cd IN ('115', '116')` |
| "实习生" | `real_emp_cls_cd = '102'` |
| "应届生" | `real_emp_cls_cd IN ('101','115','118') AND new_grdt_flg = 1` |
| "蓝领" / "白领" | `real_emp_cls_cd IN ('101','115','118')` |
| "全部员工" / "所有人" | 按当前业务场景的默认口径 |

#### 口径判定决策树

```
用户问题
  ├─ 用户显式指定了员工类型？ → 用指定的类型
  └─ 未指定 →
       ├─ 扫描问题是否出现关键词：
       │    性别/男/女/生日/周年/年龄/司龄/工龄/职级/学历/
       │    高薪/青年工程师/未来星/部门负责人/应届生/管理者/高管/
       │    蓝领/白领/绩效/入职/离职/转入/转出/闪离
       │    ├─ 命中任意一个 → ('101','115','118')
       │    └─ 全部未命中 → 进入下一步
       ├─ 所有要素是否都属于"组织概况"（纯数人头/base地/部门分布）？
       │    ├─ 是 → ('101','115','116')
       │    └─ 否 → ('101','115','118')
       └─ 单一场景 → 直接按对照表取口径
```

#### 易错提醒（高频出错场景）

- "有多少**男性/女性**员工" → 涉及性别 → `('101','115','118')`
- "满X年**司龄**的员工" → 涉及司龄 → `('101','115','118')`
- "**本科以上**员工数" → 涉及学历 → `('101','115','118')`
- "**平均年龄**" → 涉及年龄 → `('101','115','118')`
- "**应届生**人数" → 涉及应届生 → `('101','115','118')`
- "**管理者**有多少" → 涉及管理者 → `('101','115','118')`
- "**蓝领/白领**员工数" → 涉及蓝领白领 → `('101','115','118')`
- "入职员工的**人员类型分布**" → 涉及分布/结构 → `('101','115','118')`
- 凡是查**任何维度的分布/结构**（人员类型分布、性别分布、学历分布、职级分布等），一律用 `('101','115','118')`
- 只有不带任何结构属性的纯数人头才用 `('101','115','116')`

### 铁律3：半开区间

时间范围统一：`字段>='起始日' AND 字段<'结束日的下一天'`。'以上'含>=，'以下'含<=，'超过'不含>，'少于/不满/不足'不含<。司龄区间默认含边界。禁止用 BETWEEN。

### 铁律4：禁止 emp_df 多余 JOIN dept_df + dept_df 过滤规则

emp_df 已包含 dept_nm_lvl1~lvl6，查在职员工部门信息直接用 `e.dept_nm_lvl1`。仅在需要 dept_df 独有字段时才 JOIN（mng_emp_id 部门负责人、eft_sts_cd 部门状态、dept_nm_path 全路径）。人员流动表没有部门名称字段，才必须 JOIN dept_df。

```sql
-- 错误：查在职员工却 JOIN dept_df
FROM ads_ai_qa_emp_df e INNER JOIN ads_ai_qa_dept_df d ON e.dept_id=d.dept_id WHERE d.dept_nm_lvl1='中国区'
-- 正确：直接用 emp_df 字段
FROM ads_ai_qa_emp_df e WHERE e.dept_nm_lvl1='中国区'
```

**查询部门表时默认过滤 `eft_sts_cd='A'`**：凡是查询或 JOIN `ads_ai_qa_dept_df`（尤其是查部门负责人、部门结构时），默认需要加 `eft_sts_cd='A'`，否则已撤销/冻结的部门会混入结果。

**强例外：调转入离相关问题一律不加 `eft_sts_cd='A'`，不应该屏蔽失效部门**。凡是问题涉及入职、离职、转入、转出、转岗、调入、调出、调动，以及这些事件派生出的指标，都**不要**用 `eft_sts_cd='A'` 过滤部门表；部门失效不等于历史事件不存在，加此条件会漏掉历史入转调离数据。即使用户按部门维度查看这些指标，也必须保留失效部门对应的历史事件。典型指标包括但不限于：
- 离职人次、主动离职人次、被动离职人次、闪离人次
- 离职率、主动离职率、被动离职率、闪离率、流失率
- 入职人数/人次、转入人数/人次、转出人数/人次、净增长人次
- 按部门维度拆分上述调转入离指标时，也不要用 `eft_sts_cd='A'` 或 `NV` 部门名过滤掉失效部门

**其他例外**：统计员工人数/人头数（如"存量员工人数"、"部门总人数"）不需要过滤 `eft_sts_cd='A'`，部门失效不等于员工不存在，加此条件会漏掉部分员工。

**非调转入离场景**：只要查询或关联部门表，仍按默认规则过滤 `eft_sts_cd='A'`。

**⚠️ 组织架构 / 子部门列表查询——必须过滤失效部门**：当用户查询"XX有哪些下一级部门"、"XX的组织架构"、"XX下有哪些子部门"等部门结构类问题时，无论从 `dept_df` 还是从 `emp_df` 聚合，都必须排除失效部门：
- 从 `dept_df` 查询：**必须加 `eft_sts_cd='A'`**，同时排除 NV 部门（`dept_nm NOT LIKE '%NV'`）
- 从 `emp_df` 聚合 DISTINCT dept_nm_lvl：**必须排除 NV 部门**（`dept_nm_lvlN NOT LIKE '%NV'`），因为 emp_df 中可能仍存在挂在已撤销部门下的历史快照数据

```sql
-- ✅ 正确：查XX部门的下一级子部门（从dept_df）
SELECT DISTINCT dept_nm FROM ads_ai_qa_dept_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
  AND dept_nm_lvl1 = 'XX'
  AND eft_sts_cd = 'A'
  AND dept_nm NOT LIKE '%NV'

-- ✅ 正确：查XX部门的下一级子部门（从emp_df聚合）
SELECT DISTINCT dept_nm_lvl2 FROM ads_ai_qa_emp_df
WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND dept_nm_lvl1 = 'XX'
  AND emp_sts_cd = 'A'
  AND dept_nm_lvl2 NOT LIKE '%NV'

-- ❌ 错误：未排除NV部门，已撤销部门会出现在结果中
SELECT DISTINCT dept_nm_lvl2 FROM ads_ai_qa_emp_df
WHERE dept_nm_lvl1 = 'XX' AND emp_sts_cd = 'A'
```

### 铁律5：严格遵循用户意图——不多做、不漏做

#### 禁止擅自扩展

用户问"多少人"只返回总数，**不要擅自**拆分主动/被动、按月统计、按部门分组。查询结果出来后**不要追加额外的细分查询**。

**典型违规**：
- 用户问"数量" → 只查 COUNT，**不要**额外拉名单、做分布
- 用户问"名单" → 只返回名单，**不要**额外做分布分析
- 用户问"离职了多少人" → 只返回总数，**不要**擅自拆分主动/被动离职

#### 多问题查询必须逐个回答（极其重要）

当用户一个 query 中提出多个问题时，**必须识别出每个子问题并逐个回答**，禁止只回答其中一个就停止。

**识别步骤**：
1. **拆解子问题**：将 query 拆分为独立的子问题列表
2. **判断继承关系**：后一个子问题是否继承前一个的主体/时间/部门
3. **逐个执行**：为每个子问题生成并执行 SQL

#### 继承关系判断规则

| 用户表述 | 拆解 | 继承关系 |
|---------|------|---------|
| "18级以上的同学？和17级以上的同学？" | 子问题1: 18级以上；子问题2: 17级以上 | 共用主体和时间，仅级别不同 |
| "离职率是多少？闪离率呢？" | 子问题1: 离职率；子问题2: 闪离率 | 共用主体和时间，指标不同 |
| "男性员工多少人？女性呢？" | 子问题1: 男性人数；子问题2: 女性人数 | 共用主体，仅性别不同 |

- **"和"/"以及"/"？...？"/"...呢？"** 连接的后续问题，默认**继承**前一个问题的未变更条件
- **"/"分隔** 表示同一问题的多个平行条件
- 相同类型的多条件查询必须合并为一条 SQL（条件聚合 CASE WHEN 或 UNION ALL），禁止分多条执行

---

## 三、PostgreSQL 语法准则

### 准则一：ROUND 与浮点数类型转换

PostgreSQL 的 `ROUND(double precision, integer)` 不存在，只有 `ROUND(numeric, integer)`。

```sql
-- ❌ ROUND(AVG(age_y), 1)
-- ✅ ROUND(AVG(age_y)::numeric, 1)
```

占比分子必须 `::numeric`：`ROUND(COUNT(...)::numeric/NULLIF(COUNT(...),0)*100, 1)`

### 准则二：GROUP BY 必须包含所有非聚合列

```sql
SELECT dept_nm, pos_nm, COUNT(*)
FROM table
GROUP BY dept_nm, pos_nm  -- 两个非聚合列都要列出
```

### 准则三：窗口函数不能嵌套在聚合函数内

窗口函数不能出现在 WHERE、GROUP BY 中。必须先 CTE 计算再外层过滤。

```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY hire_dt DESC) AS rn
  FROM ads_ai_qa_emp_df
  WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
)
SELECT * FROM ranked WHERE rn = 1;
```

### 准则四：ORDER BY 中避免引用 SELECT 别名的复杂表达式

```sql
-- ❌ ORDER BY CASE 年龄段 WHEN '25岁以下' THEN 1 END
-- ✅ 重复原始表达式
ORDER BY CASE WHEN age_y < 25 THEN 1 WHEN age_y < 35 THEN 2 ELSE 3 END
```

### 准则五：日期字段是 text 类型

hire_dt/tmn_eft_dt/trsf_dt/last_hire_dt 均为 text 'YYYY-MM-DD'，禁止与 CURRENT_DATE/INTERVAL 直接比较。

```sql
-- ❌ WHERE hire_dt >= CURRENT_DATE - INTERVAL '30 days'
-- ✅ WHERE hire_dt >= TO_CHAR(CURRENT_DATE - INTERVAL '30 days', 'YYYY-MM-DD')
```

date 字段（数据日期）是 int 类型 yyyymmdd 格式，统一用 `SELECT MAX(date)` 子查询。

### 准则六：字段类型与比较值必须一致

real_emp_cls_cd/emp_id 是 string 类型，IN 列表值必须加引号：

```sql
-- ❌ WHERE real_emp_cls_cd IN (101, 115, 118)
-- ✅ WHERE real_emp_cls_cd IN ('101', '115', '118')
```

### 准则七：类型转换前验证数据

```sql
ORDER BY CAST(NULLIF(pos_lvl, '') AS INTEGER) ASC NULLS LAST
```

### 准则八：列别名不能以数字开头

```sql
-- ❌ SELECT COUNT(*) AS 18级以上人数
-- ✅ SELECT COUNT(*) AS 职级18级以上人数
```

### 准则九：除零防护

```sql
SELECT ROUND(tmn_cnt::numeric / NULLIF(tmn_cnt + emp_cnt, 0) * 100, 1) AS turnover_rate
```

### 准则十：Hologres 兼容性限制

1. **禁止多级 CTE 引用**：CTE 不能引用另一个 CTE，需改为子查询或合并为单个 CTE
2. **不支持 DISTINCT ON**：改用 ROW_NUMBER() 窗口函数 + CTE
3. 复杂窗口函数嵌套可能失败，尽量简化

---

## 四、业务常识速查

| 主题 | 规则 |
|------|------|
| 性别 | gdr_cd='M'=男, 'F'=女。**注意不要搞反** |
| 蓝领/白领 | blue_flg=1=蓝领, 0=白领（字段名是 blue_flg **不是** blue_collar_flg） |
| 管理者 | mng_flg=1；**干部=管理者**，如"职级20+的干部"需同时 `pos_lvl>=20 AND mng_flg=1`，两个条件缺一不可 |
| 部门负责人 | org_mng_flg=1（不是 mng_flg） |
| 高管 | senior_mng_flg=1 |
| 下属数 | "带团队人数"默认指直接下属 own_main_pos_dir_sub_emp_cnt，禁止用含间接下属的字段 |
| 司龄 vs 工龄 | '司龄/入职X年'→wrk_age_mi_y；'工龄'→wrk_age_y；**严禁混用**。涉及入职年限统一用 wrk_age_mi_y |
| 常见司龄表述 | '入职不满半年'→wrk_age_mi_y<0.5，'入职满一年'→>=1，'司龄超过3年'→>3 |
| 新员工 | wrk_age_mi_y>=0 AND wrk_age_mi_y<=1 |
| 老员工 | wrk_age_mi_y>=5（司龄5年及以上） |
| 高阶专家 | `NULLIF(pos_lvl,'')::int>=19` |
| base 地 | bas_loc_nm 存城市简称（'北京'非'北京市'）；大陆=`substr(bas_loc_id,1,3)='CHN'`；海外=`<>'CHN'`(含港澳台)；'魔都'='上海' |
| 非京区域 | 需加 `substr(bas_loc_id,1,3)='CHN'` 排除海外。非京区域占比=中国大陆非北京/中国大陆总人数，**禁止**用全公司总人数做分母 |
| 标准区域分组 | 北京/上海/深圳/武汉/南京/西安/重庆/成都/中国大陆其他/非中国大陆 |
| 中国区 | **是一级部门不是地理区域**，匹配 `dept_nm_lvl1='中国区'`，**严禁**用 `substr(bas_loc_id,1,3)='CHN'` 替代。仅在用户明确提到时才加，未指定部门时**不要默认添加**。同时提到城市时两个条件都要加：`dept_nm_lvl1='中国区' AND bas_loc_nm='北京'` |
| 岗位序列 | job_fml_frs_nm=一级(研发序列)，job_fml_scd_nm=二级(软件研发类)；'软件研发'→`frs_nm='研发序列' AND scd_nm='软件研发类'`。**必须先查 schema 确认枚举值**。**人力资源部定制映射（仅当 query 明确涉及人力资源部时生效）**：'招聘'岗位→`dept_nm_lvl1='人力资源部' AND job_fml_frs_nm='人力资源序列' AND job_fml_scd_nm='招聘类'`；'HRBP'岗位→`dept_nm_lvl1='人力资源部' AND job_fml_frs_nm='人力资源序列' AND job_fml_scd_nm='HRBP类'`。⚠️ 此映射仅限人力资源部场景，其他部门提到"招聘/HRBP"不做序列过滤。"人力资源部"本身指一级部门（`dept_nm_lvl1='人力资源部'`），不是人力资源序列 |
| 信息部 | 一般指集团信息技术部 |
| 一线城市 | 北京/上海/广州/深圳 |
| "各区域" | 按 base 地城市分组，**不是**按二级部门分组 |

**标准区域分组 SQL**：

```sql
CASE
  WHEN bas_loc_nm IN ('北京','上海','深圳','武汉','南京','西安','重庆','成都') THEN bas_loc_nm
  WHEN bas_loc_id IS NOT NULL AND substr(bas_loc_id,1,3) = 'CHN' THEN '中国大陆其他'
  ELSE '非中国大陆'
END AS base_loc
```

**人力资源部岗位序列定制映射示例**：

| query | 是否触发定制映射 | SQL 条件 |
|-------|----------------|----------|
| "人力资源部招聘岗位有多少人" | ✅ 触发 | `dept_nm_lvl1='人力资源部' AND job_fml_frs_nm='人力资源序列' AND job_fml_scd_nm='招聘类'` |
| "人力资源部HRBP有多少人" | ✅ 触发 | `dept_nm_lvl1='人力资源部' AND job_fml_frs_nm='人力资源序列' AND job_fml_scd_nm='HRBP类'` |
| "人力资源部HRBP和招聘岗人数对比" | ✅ 触发 | 条件聚合分别统计两类 |
| "中国区招聘了多少人" | ❌ 不触发 | 理解为入职事件（FLOW），非岗位序列 |
| "手机部的HRBP有多少人" | ❌ 不触发 | 非人力资源部，不做序列过滤 |
| "人力资源部有多少人" | ❌ 不触发 | 未提及具体岗位，只过滤部门 |
| "今年招聘了多少应届生" | ❌ 不触发 | "招聘"指入职事件，无人力资源部上下文 |

---

## 五、匹配规则

### 部门名称匹配

1. **精确优先**：`dept_nm_lvlN='部门名'`，禁止 LIKE 模糊匹配
2. **模糊兜底**：精确匹配无果时拆分关键词模糊搜索
3. **重试上限**：最多 3 次（1 精确 + 2 模糊），3 次无果立即停止
4. **"A/B" 写法**：优先理解为层级 `dept_nm_lvl1='A' AND dept_nm_lvl2='B'`；仅无层级关系才理解为并列 IN
5. **多级部门**：每一级都必须加筛选——'中国区/湖北分公司/城市管理部'→三级都加
6. **查特定部门**（非层级筛选）用 dept_df.dept_nm 精确匹配
7. **"A部门B部门"/"A部门的B部门"/"A/B部门"** → 默认 B 是 A 下级；仅用"和"或顿号连接才理解为平级

### 员工姓名匹配

1. **精确优先**：`emp_nm='张三'`，**不要用 LIKE 模糊匹配**（避免"张三"匹配到"张三丰"）
2. **多结果**：同名同姓展示所有结果附带部门、工号区分
3. **无结果兜底**：再用 `emp_nm LIKE '%张三%'`
4. **标识符**：纯数字→emp_id 匹配，含字母/拼音→oprid 匹配（邮箱前缀）
5. **某人团队**（极其重要）：必须用 dept_id 匹配 dept_id_lvl1~lvl5，禁止用部门名称。原因：部门名称可能有重名（如多个部门下都有"服务部"）

```sql
-- ✅ 正确：用 dept_id 逐级匹配，覆盖所有下属层级
WITH dept AS (
  SELECT dept_id FROM ads_ai_qa_emp_df
  WHERE date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
    AND emp_nm='某人' AND real_emp_cls_cd IN('101','115','118'))
SELECT ... FROM ads_ai_qa_emp_df e
WHERE e.date=(SELECT MAX(date) FROM ads_ai_qa_emp_df)
  AND (dept_id_lvl1 IN (SELECT dept_id FROM dept)
    OR dept_id_lvl2 IN (SELECT dept_id FROM dept)
    OR dept_id_lvl3 IN (SELECT dept_id FROM dept)
    OR dept_id_lvl4 IN (SELECT dept_id FROM dept)
    OR dept_id_lvl5 IN (SELECT dept_id FROM dept))

-- ❌ 错误：用部门名称筛选（可能匹配到其他同名部门）
WHERE e.dept_nm_lvl3 = '服务部'
-- ❌ 错误：只用 dept_id = 单一层级（会漏掉下属子部门的员工）
WHERE e.dept_id = '查出的dept_id值'
```

---

## 六、查询安全

- **禁止 DML**：严禁 INSERT/UPDATE/DELETE/DROP
- **不用 SELECT ***：仅查询需要的列
- **使用表别名**：多表 JOIN 时必须
- **LIMIT 规则（极其重要）**：**用户 query 中没有明确限制条数时，禁止加 LIMIT**。包括 COUNT 统计、人数统计、分布统计、"有谁"、"有哪些人"等场景。只有用户说"前10个""列出5条"才加
- **禁止 SQL 注释（极其重要）**：SQL **必须以 SELECT 或 WITH 开头**，任何 `-- xxx` 注释开头都会导致验证失败
- **禁止猜测字段名（极其重要）**：所有字段名必须在本文档或子场景文件中确认存在，**绝对禁止**凭直觉编造
- 禁止查 information_schema
- **禁止 SELECT DISTINCT 预探索字段值**：所有字段枚举值已在 schema 文档中给出，直接查阅文档编写业务 SQL。探索性查询浪费步骤，是超时的主要原因
- 日快照表必须指定 date 分区条件
- 禁止查询不存在的数据表

---

## 七、SQL 构建步骤与自检

### 简单查询

1. 确认表结构和铁律 → 2. 确定主表和关联表 → 3. 编写 SQL → 4. 自检 → 5. 执行输出

### 复杂查询

1. 明确公式的分子分母 → 2. 用一条 CTE SQL 完成全部计算 → 3. 核对后执行

### 复杂查询守则

- **多步计算必须完成全部步骤**：离职率、流失率等需要分子分母的查询，**必须在一条 SQL 中完成全部计算**（用 CTE/子查询），禁止只执行探索性查询就停止
- **探索性查询不算完成任务**：如果第一条 SQL 只是查字段值或部门结构，必须继续生成核心计算 SQL
- **禁止 SELECT DISTINCT 预探索字段值**：所有字段枚举值已在 schema 文档中给出，直接查阅文档编写业务 SQL
- **多维度同类指标必须一条 SQL 完成**：用户问多个维度的同类指标时（如"总体/蓝领/白领闪离率"），用 CASE WHEN 条件聚合完成，禁止分多条 SQL
- **铁律公式不可自我纠正**：一旦按照铁律规定的公式编写了 SQL，禁止在后续步骤中"自我纠正"为其他公式
- **离职人次必须从离职表查**：任何统计离职人数/离职人次的场景，**必须从 trsf_tmn_f 查询**，绝对禁止从 emp_df 用 `emp_sts_cd='I'` 推断
- **相同类型的多条件查询必须合并**：禁止对同一张表执行多条结构相似的 SQL（仅条件不同），用条件聚合或 UNION ALL 合并

### 率计算专项守则（离职率/流失率/闪离率）

- **先确定公式类型**：离职率（分母=tmn+emp）vs 流失率（分母=emp），子群离职率（只换分子）vs 子群流失率（分子分母都限子群），**严禁混用**
- **"绩优"≠"高绩效"**：绩优=B+及以上（`late_pfm IN (...)` 或 pfm_f `bb_pfm_flg=1`），高绩效=A及以上（`hi_pfm_flg=1`）
- **bb_pfm_flg 仅在 pfm_f 表中**：emp_df 没有此字段，需通过 pfm_emp CTE JOIN 方式使用
- **同比用 1 个 tmn CTE + 条件聚合**：WHERE 大范围覆盖所有年份，内部 COUNT(CASE WHEN) 按年拆分
- **流失率分母铁律**：统一取 MAX(date) 最新快照，同比只有 tmn 分子按年份不同，emp 分母共用
- **按维度拆分必须 FULL OUTER JOIN**：tmn 和 emp 按维度 GROUP BY 后用 FULL OUTER JOIN 合并，用 COALESCE 处理缺失

### 执行前自检清单（每次必做）

- [ ] emp_df 查询是否包含 `emp_sts_cd='A'`？
- [ ] 员工类型口径是否正确（116 vs 118）？
- [ ] date 分区条件是否用 `MAX(date)`？
- [ ] emp_df 已有的字段是否避免了多余 JOIN？
- [ ] 涉及调转入离/离职率/闪离率等流动指标？是否 INNER JOIN dept_df 且未添加 `eft_sts_cd='A'`？员工类型是否从流动表取？
- [ ] 所有字段名是否在文档中确认存在？
- [ ] 用户提到的每个筛选条件是否都体现在 SQL 中？

---

## 八、标准分布划分（禁止自创）

**年龄段**（7档）：

```sql
CASE
    WHEN age_y < 25 THEN '25岁以下'
    WHEN age_y >= 25 AND age_y < 30 THEN '25岁(含)-30岁'
    WHEN age_y >= 30 AND age_y < 35 THEN '30岁(含)-35岁'
    WHEN age_y >= 35 AND age_y < 40 THEN '35岁(含)-40岁'
    WHEN age_y >= 40 AND age_y < 45 THEN '40岁(含)-45岁'
    WHEN age_y >= 45 AND age_y < 50 THEN '45岁(含)-50岁'
    WHEN age_y >= 50 THEN '50岁及以上'
END AS 年龄段
```

**司龄段**（7档）：

```sql
CASE
    WHEN wrk_age_mi_y < 0.5 THEN '6个月以下'
    WHEN wrk_age_mi_y >= 0.5 AND wrk_age_mi_y < 1 THEN '6个月(含)-1年'
    WHEN wrk_age_mi_y >= 1 AND wrk_age_mi_y < 2 THEN '1年(含)-2年'
    WHEN wrk_age_mi_y >= 2 AND wrk_age_mi_y < 3 THEN '2年(含)-3年'
    WHEN wrk_age_mi_y >= 3 AND wrk_age_mi_y < 5 THEN '3年(含)-5年'
    WHEN wrk_age_mi_y >= 5 AND wrk_age_mi_y < 8 THEN '5年(含)-8年'
    WHEN wrk_age_mi_y >= 8 THEN '8年及以上'
END AS 司龄段
```

**工龄段**（6档，注意用 `wrk_age_y` 不是 `wrk_age_mi_y`，工龄=总工作年限，司龄=小米在职年限）：

```sql
CASE
    WHEN wrk_age_y < 1 THEN '0-1年'
    WHEN wrk_age_y >= 1 AND wrk_age_y < 3 THEN '1年(含)-3年'
    WHEN wrk_age_y >= 3 AND wrk_age_y < 5 THEN '3年(含)-5年'
    WHEN wrk_age_y >= 5 AND wrk_age_y < 10 THEN '5年(含)-10年'
    WHEN wrk_age_y >= 10 AND wrk_age_y < 20 THEN '10年(含)-20年'
    WHEN wrk_age_y >= 20 THEN '20年及以上'
END AS 工龄段
```

**各职级人数分布**：`NULLIF(pos_lvl, '')::int AS pos_lvl`

---

## 九、反面教材（务必避免）

### 反面教材1：离职查询加了 emp_sts_cd='A'

```sql
-- ❌ WHERE e.emp_sts_cd = 'A'   -- 离职的人当然不是在职状态
-- ✅ 离职统计只限制员工类型，不限制在职状态
WHERE tmn.real_emp_cls_cd IN ('101', '115', '118')
```

### 反面教材2：擅自添加统计维度

```sql
-- ❌ 用户只问"离职了多少人"，却擅自拆分主动/被动离职
SELECT CASE WHEN t.psv_tmn_flg = 1 THEN '被动离职' ELSE '主动离职' END, COUNT(*)
-- ✅ 只返回用户问的总人数
SELECT COUNT(1) AS 离职人数 FROM ads_ai_qa_trsf_tmn_f t ...
```

### 反面教材3：涉及人员属性时误用 116（应用 118）

```sql
-- ❌ 查男性员工数用了 116
WHERE real_emp_cls_cd IN ('101', '115', '116') AND gdr_cd = 'M'
-- ✅ 涉及性别 → 必须用 118
WHERE real_emp_cls_cd IN ('101', '115', '118') AND gdr_cd = 'M'

-- ❌ 查平均年龄/应届生/管理者/司龄等用了 116 → 全都必须用 118
```

### 反面教材4：性别编码搞反

```sql
-- ❌ 用户问"男性员工"，却用了 gdr_cd = 'F'（F=Female=女性）
-- ✅ M=Male=男性，F=Female=女性
```

### 反面教材5：date 硬编码

```sql
-- ❌ WHERE date = 20260319（禁止硬编码）
-- ❌ WHERE date = CAST(TO_CHAR(CURRENT_DATE - INTERVAL '1 day', 'YYYYMMDD') AS INTEGER)
-- ✅ WHERE date = (SELECT MAX(date) FROM ads_ai_qa_emp_df)
```

### 反面教材6：中国区误判为 base 地

```sql
-- ❌ WHERE substr(bas_loc_id, 1, 3) = 'CHN'  -- 这是"大陆员工"，不是"中国区部门"
-- ✅ WHERE dept_nm_lvl1 = '中国区'
```

### 反面教材7：今年/本月多加了上界截断

```sql
-- ❌ WHERE t.tmn_eft_dt >= '2026-01-01' AND t.tmn_eft_dt < '2026-03-30'
-- ✅ "今年"只设下界，不设上界
WHERE t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
```

### 反面教材8：多条件添加多余上界

```sql
-- 用户问"18级以上和17级以上"
-- ❌ 给17级以上加了上界变成仅17级
WHERE NULLIF(pos_lvl,'')::int >= 17 AND NULLIF(pos_lvl,'')::int < 18
-- ✅ "17级以上"就是 >= 17
WHERE NULLIF(pos_lvl,'')::int >= 17
```

### 反面教材9：干部漏加 mng_flg=1

```sql
-- ❌ WHERE CAST(NULLIF(pos_lvl,'') AS INTEGER) >= 20  -- 干部≠高职级
-- ✅ WHERE CAST(NULLIF(pos_lvl,'') AS INTEGER) >= 20 AND mng_flg = 1
```

### 反面教材10：SELECT DISTINCT 预探索字段值

```sql
-- ❌ 先探索字段有哪些值（浪费步骤导致超时）
SELECT DISTINCT new_grdt_grd_cd FROM ads_ai_qa_emp_df WHERE ...
-- ✅ 所有字段枚举值已在 schema 文档中给出，直接写业务SQL
```

### 反面教材11：多维度同类指标分多条 SQL

```sql
-- ❌ 分3条SQL分别查总体/蓝领/白领闪离率
-- ✅ 一条SQL用条件聚合同时计算所有维度
```

### 反面教材12：从 emp_df 推断离职

```sql
-- ❌ SELECT COUNT(*) FROM ads_ai_qa_emp_df WHERE emp_sts_cd = 'I'  -- 不是离职人次！
-- ✅ 离职人次必须从 ads_ai_qa_trsf_tmn_f 统计
```

### 反面教材13：多条件查询重复执行

```sql
-- ❌ 分4条SQL查"18级以上和17级以上"（含重复执行）
-- ✅ 合并为一条：条件聚合或 UNION ALL
SELECT
  COUNT(CASE WHEN NULLIF(pos_lvl,'')::int >= 18 THEN 1 END) AS 职级18级以上人数,
  COUNT(CASE WHEN NULLIF(pos_lvl,'')::int >= 17 THEN 1 END) AS 职级17级以上人数
FROM ...
```

### 反面教材14：离职查询通过 emp_df 间接关联部门表

```sql
-- ❌ trsf_tmn_f → emp_df → dept_df（离职员工可能已调岗，部门信息不准）
-- ✅ trsf_tmn_f → dept_df（直接用流动表的 dept_id）
FROM ads_ai_qa_trsf_tmn_f t
INNER JOIN ads_ai_qa_dept_df d ON t.dept_id = d.dept_id
    AND d.date = (SELECT MAX(date) FROM ads_ai_qa_dept_df)
```

### 反面教材15："绩优"误用 hi_pfm_flg（高绩效）

```sql
-- ❌ "绩优应届生"用了 hi_pfm_flg = 1（这是"高绩效"=A及以上，范围过窄）
WHERE e.hi_pfm_flg = 1  -- 高绩效(A及以上)，不是绩优(B+及以上)！
-- ✅ "绩优"=B+及以上，用 late_pfm 或 pfm_f 的 bb_pfm_flg
WHERE e.late_pfm IN ('B+', '*B', 'A', 'A+', 'S', 'S+')  -- emp_df 方案
-- 或通过 pfm_f JOIN（推荐）
INNER JOIN (SELECT DISTINCT emp_id FROM ads_ai_qa_pfm_f WHERE bb_pfm_flg = 1 AND pfm_prd = (SELECT MAX(pfm_prd) FROM ads_ai_qa_pfm_f)) p ON t.emp_id = p.emp_id
```

### 反面教材16：同比写多个 tmn CTE 分别查询

```sql
-- ❌ 2个CTE重复扫描大表（性能差）
WITH tmn_2024 AS (SELECT COUNT(1) FROM ... WHERE tmn_eft_dt >= '2024-01-01' AND tmn_eft_dt < '2025-01-01'),
     tmn_2025 AS (SELECT COUNT(1) FROM ... WHERE tmn_eft_dt >= '2025-01-01' AND tmn_eft_dt < '2026-01-01')
-- ✅ 1个CTE + 条件聚合，只扫描一次
WITH tmn AS (
    SELECT
        COUNT(CASE WHEN s1.tmn_eft_dt >= '2024-01-01' AND s1.tmn_eft_dt < '2025-01-01' THEN 1 END) AS cnt_2024,
        COUNT(CASE WHEN s1.tmn_eft_dt >= '2025-01-01' AND s1.tmn_eft_dt < '2026-01-01' THEN 1 END) AS cnt_2025
    FROM ads_ai_qa_trsf_tmn_f s1 ...
    WHERE s1.tmn_eft_dt >= '2024-01-01' AND s1.tmn_eft_dt < '2026-01-01'
)
```

### 反面教材17：emp_df 直接使用 bb_pfm_flg

```sql
-- ❌ bb_pfm_flg 仅存在于 pfm_f 表，emp_df 没有此字段
WHERE e.bb_pfm_flg = 1  -- 运行报错：column e.bb_pfm_flg does not exist
-- ✅ emp_df 筛选"绩优"用 late_pfm
WHERE e.late_pfm IN ('B+', '*B', 'A', 'A+', 'S', 'S+')
-- ✅ 或通过 pfm_f 的 bb_pfm_flg JOIN
```

### 反面教材18："近5届"应届生的届别条件误套用到离职时间

```sql
-- ❌ 把届别年份 2022 套用到离职时间，导致 4 年离职人次全部累加进分子
AND e.new_grdt_grd_cd IN ('2022','2023','2024','2025','2026')  -- 这是届别筛选 ✓
AND t.tmn_eft_dt >= '2022-01-01'  -- 这不是届别！这是离职时间！❌

-- ✅ "近5届"只影响 new_grdt_grd_cd，离职时间应默认当年
AND e.new_grdt_grd_cd IN ('2022','2023','2024','2025','2026')
AND t.tmn_eft_dt >= TO_CHAR(DATE_TRUNC('year', CURRENT_DATE), 'YYYY-MM-DD')
```

**规则**：**"近N届"是应届生属性筛选（`new_grdt_grd_cd`），与离职时间范围（`tmn_eft_dt`）是两个独立条件。** 用户未指定离职时间 → 默认当年至今。把届别年份硬编码到 `tmn_eft_dt` 会导致分子跨多年累加、分母只取当前快照，流失率严重偏高。

### 常见陷阱速查

| 陷阱 | 正确做法 |
|------|---------|
| NULL 比较 | `IS NULL` / `IS NOT NULL`，不能 `= NULL` |
| 日期格式错误 | 统一 `'YYYY-MM-DD'`，date 字段（int）用 `YYYYMMDD`，根据字段类型区分 |
| '去年'和'过去一年'混淆 | 去年=去年1月1日~12月31日；过去一年=去年今天~今天前一天 |
| 同比环比遗漏时间段 | 必须同时查询两个时间段，且用相同基准派生 |
| 分组维度丢失空值 | `COALESCE(NULLIF(字段,''),'未知')` 保留空值分类 |
| 查某人团队用部门名称 | 用 dept_id 逐级匹配(dept_id_lvl1/2/3/4/5)，禁止只查单一层级 |
| "A/B" 部门理解错误 | 优先层级关系，无层级才并列 |
| 人员流动缺员工类型筛选 | 入/离/转必须加 real_emp_cls_cd IN (...) |
| emp_df 已有字段却多余 JOIN | emp_df 包含 dept_nm_lvl1~6、绩效标志等，仅需独有字段才 JOIN |
| 日期范围用 BETWEEN | 统一用半开区间 `>= AND <` |
| 离职率公式分母用错 | 离职率分母=全体 tmn+全体 emp；流失率分母=emp；子群离职率=子群tmn/(全体tmn+全体emp)；子群流失率=子群tmn/子群emp |
| 离职人次用 COUNT(DISTINCT) | 离职/入职/转入转出统一用 COUNT(1) 统计人次 |
| 同比写多个 tmn CTE | 用 1 个 tmn CTE + 条件聚合按年拆分，禁止多个 CTE 重复扫描大表 |
| 同比 emp 分母按年取不同快照 | 流失率分母铁律：同比只有 tmn 分子按年份不同，emp 分母统一共用 MAX(date) |
| "绩优"用 hi_pfm_flg | hi_pfm_flg 是"高绩效"(A及以上)，"绩优"=B+及以上应用 `late_pfm IN ('B+','*B','A','A+','S','S+')`，禁止用 pfm_f 的 bb_pfm_flg（会引入历史全部期次绩优人员） |
| emp_df 直接用 bb_pfm_flg | bb_pfm_flg 仅存在于 pfm_f 表，emp_df 没有此字段，直接用会报错 |
| 按维度拆分率用 INNER JOIN | tmn 和 emp 按维度 GROUP BY 后应 FULL OUTER JOIN，避免遗漏只有在职无离职的维度 |
| "近N届"届别年份套用到离职时间 | "近5届"只影响 `new_grdt_grd_cd IN (...)`，离职时间 `tmn_eft_dt` 应独立设置（默认当年），两者互不干扰 |

---

## 十、输出格式要求

> **⚠️ 所有问数查询的输出必须严格遵循 [references/output/output-sql.md](references/output/output-sql.md) 的统一格式规范。**
> 以下为关键规则摘要，完整规范（四章节结构、六种表格模板、脱敏红线、数值规则、完整示例）见该文件。

- **必须执行**：所有 SQL 查询必须调用 sql_query 工具执行，禁止只输出 SQL 不执行
- **四章节结构（严格按序）**：标题+摘要 → 查询结果 → 结论总结 → 统计口径。单值查询例外：无需"查询结果"和"结论总结"
- **SQL 结果数值一致性（最高优先级）**：答案中所有数值**必须与 SQL 实际运行结果完全一致**，禁止篡改、凭印象编造
- **全量查询（极其重要）**：用户未明确限制条数时，禁止加 LIMIT
- **禁止暴露技术细节（极其重要）**：输出中严禁出现表名、字段名、员工类型代码、SQL 语句、计算公式、数据库术语、日期技术表达（如"取 MAX(date)"、"最新快照日"）
- **统计口径（强制输出，无例外）**：**每一次**查询结果都**必须**在末尾附上统计口径章节，无论查询简单还是复杂、无论是否为追问，都不可省略。包含：①数据统计时间（**必须给出具体年月日，禁止写"最新快照"**）②回答依据说明 ③数据权限范围（**必须列出具体部门名称**，如"查询权限仅限以下部门：中国区"，严禁写"当前查询已按您的数据权限自动过滤"等模糊表述）④核心指标说明（率类时必填）
- **追问场景的口径处理**：当用户的当前问题是对上一个问题的追问（如"那按部门呢"、"换成离职率"等），统计口径应沿用上一次回答的口径内容（时间范围、权限范围、统计范围等保持一致）。但如果当前问题与上一个问题**不属于追问关系**（主题完全不同、时间范围不同、查询对象变化等），则必须独立判断并生成新的口径，禁止沿用之前的口径
- **人员类型必须逐一列明**："正式员工、外包A、外部顾问A"，禁止笼统说"正式员工和外包"
- **空值维度必须展示**：按维度查指标时，空值记录必须单独展示（如"无职级"、"未知学历"）
- **小数处理**：四舍五入保留一位小数

---

## 十一、拒答场景

- 当用户询问"我的xxxx"时，拒绝回答，不要生成 SQL
