---
name: routing-sql
description: >
  SQL 问数通道的子场景识别与路由分发，将自然语言转换为结构化 SQL 查询。
  当外层路由判定为"问数"通道后加载，完成子场景判定、规则文件加载、SQL 构建与执行。
  覆盖子场景：
  (1) EMP_BASIC — 员工基础查询：人数统计、占比分布、筛选排序（约60%查询）
  (2) FLOW — 人员流动统计：入职/离职/转岗人次、人数、明细
  (3) RATE — 离职率/流失率/闪离率等需公式计算的率值
  (4) CROSS_TABLE — 跨表专项：月度趋势、绩效期次、教育经历(QS100/985/211)、外派
  (5) AI_COST — AI Token 成本问数：单部门AI成本、AI渗透率、Coding/龙虾渠道占比、人均AI成本、AI活跃人数
  触发词："多少人"、"占比"、"趋势"、"离职率"、"入职"、"转岗"、"绩效"、"每月"、"环比"、"Token成本"、"AI成本"、"AI渗透率"、"Coding占比"等。
  包含易混淆场景判定规则。
---

# SQL 通道子场景识别与路由

> **职责**：外层 SKILL.md 判定进入问数通道后，由本文件完成子场景识别、下游文件加载、查询执行和输出格式化。

---

## 一、执行流程（严格按序）

### Step 1: 加载通用规则（必须，禁止跳过）

无论哪个子场景，**必须先读取**：
- [references/sql/sql-query.md](sql/sql-query.md) — 通用铁律、核心表结构、SQL 语法、匹配规则、构建步骤

### Step 2: 识别子场景

在 Thought 中分析用户 query，按下方优先级判定最匹配的**单一子场景**。

### Step 3: 加载子场景专用文件

根据 Step 2 结果，追加读取对应文件：

| 子场景 | 追加读取 | 所需 table-info |
|--------|---------|----------------|
| `EMP_BASIC` | [intent-emp-basic.md](sql/intent-emp-basic.md) | [table-info-emp.md](sql/table-info-emp.md) |
| `FLOW` | [intent-flow.md](sql/intent-flow.md) | [table-info-hire.md](sql/table-info-hire.md), [table-info-termination.md](sql/table-info-termination.md), [table-info-transfer.md](sql/table-info-transfer.md), [table-info-pre-hire.md](sql/table-info-pre-hire.md), [table-info-pre-tmn.md](sql/table-info-pre-tmn.md), [table-info-pre-trsf.md](sql/table-info-pre-trsf.md) |
| `RATE` | [intent-rate.md](sql/intent-rate.md) + [intent-flow.md](sql/intent-flow.md) | 同 FLOW |
| `CROSS_TABLE` | [intent-advanced.md](sql/intent-advanced.md) | 按需加载：[table-info-pfm.md](sql/table-info-pfm.md), [table-info-edu.md](sql/table-info-edu.md), [table-info-expatriate.md](sql/table-info-expatriate.md), [table-info-talent-tag.md](sql/table-info-talent-tag.md), [table-info-rpt.md](sql/table-info-rpt.md) |
| `AI_COST` | [intent-ai-cost.md](sql/intent-ai-cost.md) | [table-info-ai-cost.md](sql/table-info-ai-cost.md)（渗透率查询追加 [table-info-emp.md](sql/table-info-emp.md)） |

### Step 4: 编写 SQL 并执行

```bash
mcporter call hr_talent_claw.sql_query sql="SELECT count(*) AS cnt FROM hr.dim_employee_info WHERE status = '在职'" query="在职员工有多少人"
```

基于通用规则 + 子场景专用规则编写 SQL，调用 `sql_query` 执行。

### Step 5: 格式化输出

按 [references/output/output-sql.md](output/output-sql.md) 格式要求输出结果。**必须严格遵循四章节结构**：

1. **标题 + 摘要**（`##` 二级标题 + 1-2 句关键发现；标题需结合权限信息，权限受限时加括号说明）
2. **查询结果**（Markdown 表格，按查询类型选用：分布类/趋势类/排名类/率类/名单类/单值查询）
3. **结论总结**（围绕用户问题 2-4 句总结，问什么答什么，禁止添加用户未问到的维度）
4. **统计口径**（数据统计时间、回答依据说明、数据权限范围、核心指标说明）

**单值查询例外**：无需"查询结果"和"结论总结"章节，直接在标题下方给出答案 + 统计口径。

**信息脱敏红线**：输出中严禁出现表名、字段名、员工类型编码、SQL 语句、计算公式代码、数据库术语。员工类型编码必须翻译为中文（101→正式员工、115→外包A、116→外包B、118→外部顾问A）。

详细规范、六种查询类型的表格模板、脱敏规则、数值格式、特殊场景处理和完整示例见 [references/output/output-sql.md](output/output-sql.md)。

---

## 二、子场景判定规则（按优先级，命中即停）

### 优先级 1: FLOW（人员流动事件统计）

**触发词**：入职、引入、新进、招聘、离职、离职备注、离开、走了、转入、转出、调动、调岗、净增长、预入职、预离职、预转岗、预调动、offer

> **⚠️ 前置排除**：如果用户问题同时包含"离职报告"、"离职分析"、"离职画像"、"预离职"、"离职诊断"、"离职情况分析"、"人员流失分析"等报告通道关键词，**不进入 FLOW**，应由上游 SKILL.md Step 2.1 路由到报告通道。本文件不应被加载处理这类请求。

**判定要点**：
- 统计入职/离职/转岗的**人次、人数、明细清单**
- 涉及 trsf_hire_f / trsf_tmn_f / trsf_in_f 表
- 涉及预入职/预离职/预转岗的人数统计，涉及 pre_hire_f / pre_tmn_f / pre_trsf_f 表
- "今年入职了多少人" → FLOW
- "今年入职的应届生有多少人" → FLOW（入职事件统计）
- "25年入职和离职总人数" → FLOW
- "预入职人数有多少" → FLOW（预入职统计）
- "预离职中有多少高绩效员工" → FLOW（预离职细分统计）
- "预转出到其他部门的人数" → FLOW（预转岗统计）

**不是 FLOW**（常见易错）：
- "新入职员工有多少人" → EMP_BASIC（按 last_hire_dt 筛选在职员工）
- "入职不满一年的人" → EMP_BASIC（司龄筛选 wrk_age_mi_y）
- "2025年新入职人员绩效与存量员工对比" → EMP_BASIC（对比在职员工属性）
- "XX部门的离职报告" → **报告通道**（不是 FLOW，含"离职报告"关键词）
- "XX部门的离职分析" → **报告通道**（不是 FLOW，含"离职分析"关键词）

### 优先级 2: RATE（离职率/流失率计算）

**触发词**：离职率、流失率、闪离率、被动离职率、主动离职率、绩优离职率、绩优流失率、对比XX离职率、多部门离职率

**判定要点**：
- 需要公式计算（分子/分母）
- RATE 主文件为 intent-rate.md（公式体系），同时加载 intent-flow.md（流动表结构和铁律）
- "高绩效流失率" → RATE
- "各部门离职率排名" → RATE
- "对比销售序列与产品序列的被动离职率" → RATE
- "四部门对比绩优离职率" → RATE（第八节：按维度拆分）
- "手机部和汽车部离职率对比" → RATE
- "各一级部门流失率排名" → RATE

### 优先级 3: CROSS_TABLE（跨表专项查询：需 JOIN pfm_f / pfm_q_f / edu_f / expatriate / talent_tag / rpt 或多日快照）

**触发条件**（命中任一）：
- 月度趋势/按月统计/每月/月末/环比/同比/各年/年度变化/趋势 → 月度趋势（需多日快照）
- 需要查询**特定绩效期次**（如"2025H2绩效"/"2025Q2绩效"/"至少有2次绩效"）或 pfm_f/pfm_q_f 表 → 绩效明细（含季度期次时用 pfm_q_f）
- 涉及 QS100/985/211/双一流/C9/G5/常春藤/毕业院校排名/专业/博士占比 → 教育经历（需 edu_f）
- 涉及外派经历 → 外派（需 exp_asgn_f）
- 部门负责人的绩效明细 → 部门负责人绩效（需 pfm_f）

**不是 CROSS_TABLE**（常见易错）：
- "高绩效的人有哪些" → EMP_BASIC（用 emp_df.hi_pfm_flg）
- "最高学历是博士的人" → EMP_BASIC（用 emp_df.hi_edu_deg_cd）
- "连续高绩效的人" → EMP_BASIC（用 emp_df.late_twi_good_flg）
- "最近两次绩效为B的员工" → EMP_BASIC（用 emp_df.late_pfm + late_late_pfm）

### 优先级 4: AI_COST（AI Token 成本问数）

**触发词**：Token成本、AI成本、AI渗透率、Coding占比、Coding成本、渠道成本、龙虾成本、AI活跃人数、人均AI成本、AI成本环比、Token消耗

> **⚠️ 前置排除**：如果用户问题是要求"生成报告/分析/整体情况/AI赋能分析"（命中报告通道关键词），**不进入 AI_COST**，应由上游 SKILL.md Step 2.1 路由到报告通道（AI_COST_REPORT）。本子场景仅处理**具体指标问数**。

**判定要点**：
- 查询 AI Token 成本相关的**具体数值**（多少/占比/排名/几个人），数据源为 `ads_mify_cost_di`
- 金额取 `est_cost_amt`（含 MiMo 测算）；渠道用 channel 三分法（Coding/龙虾/其它）
- 涉及人数口径时需 JOIN `ads_ai_qa_emp_df` 仅取在职（`emp_sts_cd='A'`）、过滤 oprid 空；**人均/活跃人数不排除蓝领/外包A，仅 AI渗透率**的分子分母才额外过滤蓝领/外包A（详见 intent-ai-cost.md）
- "手机部Token成本多少" → AI_COST
- "各部门AI渗透率排名" → AI_COST（需 JOIN emp_df）
- "Coding类成本占比" → AI_COST（channel 三分法）
- "手机部多少人用了AI" → AI_COST（AI活跃人数）

**不是 AI_COST**（常见易错）：
- "生成AI人效分析报告" / "手机部AI投入分析" → **报告通道**（AI_COST_REPORT，不是问数）
- "XX部门人力成本多少" → 人力成本不支持问数，走报告通道 COST_REPORT 工具
- "XX部门有多少人" → EMP_BASIC（纯人数统计，不涉及 AI）

### 优先级 5: EMP_BASIC（兜底）

所有不符合上述条件的查询，默认为纯 emp_df 查询。这是最常见的场景（约 60%）。

---

## 三、跨场景查询处理

当 query 涉及多个子场景时：

1. **按核心诉求判定主场景**，读取对应文件
2. **如主场景文件缺少所需知识，追加读取另一个文件**
3. 示例：
   - "高绩效流失率" → 主场景 RATE（读 intent-rate.md + intent-flow.md），绩效字段在 sql-query.md 通用规则中已有
   - "2025年入职应届生的第一学历TOP10学校" → 主场景 FLOW + 追加读 intent-advanced.md（教育经历）
   - "各部门每月入职人数" → 主场景 FLOW + 追加读 intent-advanced.md（月度趋势）
   - "25年入职和离职总人数；离职员工中应届生占比" → 主场景 FLOW

---

## 四、易混淆场景判定速查

| 用户 query | 正确 | 易错 | 理由 |
|-----------|------|------|------|
| "今年入职了多少人" | FLOW | ~~EMP~~ | 入职事件统计，需 hire_f |
| "新入职员工有多少人" | EMP | ~~FLOW~~ | 用 emp_df.last_hire_dt 筛在职 |
| "入职不满半年的有多少人" | EMP | ~~FLOW~~ | 用 emp_df.wrk_age_mi_y |
| "中国区2025年从其他部门转入的人数" | FLOW | — | 转入事件统计 |
| "高绩效的人有哪些" | EMP | ~~CROSS~~ | 用 emp_df.hi_pfm_flg |
| "最高学历是博士的人" | EMP | ~~CROSS~~ | 用 emp_df.hi_edu_deg_cd |
| "QS100毕业的人有哪些" | CROSS_TABLE | ~~EMP~~ | 需 edu_f.qs100_flg |
| "2025H2绩效为S的人" | CROSS_TABLE | ~~EMP~~ | 需 pfm_f 特定期次 |
| "连续高绩效的人" | EMP | ~~CROSS~~ | 用 emp_df.late_twi_good_flg |
| "每月月末在职人数" | CROSS_TABLE | ~~EMP~~ | 月度趋势需多快照 |
| "离职率是多少" | RATE | ~~FLOW~~ | 需公式计算 |
| "离职人员清单" | FLOW | ~~RATE~~ | 离职明细，不是率 |
| "预入职人数" | FLOW | ~~EMP~~ | 预入职事件统计，需 pre_hire_f |
| "预离职中高绩效有多少" | FLOW | ~~EMP~~ | 预离职统计，需 pre_tmn_f + emp_df |
| "预转出多少人" | FLOW | ~~EMP~~ | 预转岗统计，需 pre_trsf_f |
| "各部门高绩效流失率排名" | RATE | ~~CROSS~~ | 核心是流失率计算 |
| "去年男女比例变化" | CROSS_TABLE | ~~EMP~~ | 需多快照对比 |
| "中国区2025年月环比增长" | CROSS_TABLE | ~~EMP~~ | 月度趋势 |
| "手机部Token成本多少" | AI_COST | ~~EMP~~ | 查 ads_mify_cost_di.est_cost_amt |
| "各部门AI渗透率排名" | AI_COST | ~~EMP~~ | AI活跃人数/总人数，需 JOIN emp_df |
| "Coding类成本占比" | AI_COST | ~~CROSS~~ | channel 三分法聚合 |
| "手机部多少人用了AI" | AI_COST | ~~EMP~~ | AI活跃去重人数 |
| "生成AI人效分析报告" | 报告通道 | ~~AI_COST~~ | 生成完整报告，非问数 |
