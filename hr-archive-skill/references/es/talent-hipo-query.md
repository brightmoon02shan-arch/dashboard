# 高潜人才名单查询（STAR_TALENT_HIPO）

> **职责**：接收 `routing-es.md` 的 STAR_TALENT_HIPO 意图判定结果，通过 SQL 查询三个高潜人群名单，按梯队分组输出结构化表格。
> 本流程仅使用 `sql_query` 工具，不涉及 ES 查询。

---

## 核心原则

1. **纯 SQL 查询**：所有数据通过 `sql_query` 工具获取，禁止调用 `es_query`
2. **数据驱动**：所有结论基于工具返回的真实数据，禁止编造
3. **单次查询**：三个人群（核心高潜 / 高潜 / 潜力关注）通过 `tag_nm IN (...)` 在**一条 SQL** 中一次性拉取，返回结果按 `tag_nm` 分组组装卡片

---

## 流程总览

1. **预查询 + 部门解析（并发）** — 获取 `MAX(date)` + 按 sql-query.md §五 规则解析部门条件
2. **名单查询（单次）** — 一条 SQL 查询全部三个人群，`tag_nm IN ('核心高潜','高潜','潜力关注')`
3. **分组与输出** — 按 `tag_nm` 分组，核心高潜超 200 条时截断，读取 `output-talent-hipo.md` 按梯队分卡发送

SQL 返回空集时，按部门匹配模糊兜底重试（最多 3 次），仍无果输出无数据话术。

---

## Step 1: 预查询 + 部门解析（并发）

**同一轮**并发执行两个动作：

| 调用 | 内容 | 目的 |
|------|------|------|
| PRE-1 | `SELECT MAX(date) AS max_date FROM ads_ai_qa_emp_df` | 获取最新分区日期 |
| 部门解析 | 按 `sql-query.md` §五 规则解析用户输入的部门名称为 SQL 条件 | 确定部门筛选字段和值 |

### PRE-1 执行

```bash
mcporter call hr_talent_claw.sql_query sql='SELECT MAX(date) AS max_date FROM ads_ai_qa_emp_df' query="查询数据最新日期"
```

### 部门解析规则

部门条件**直接嵌入** Step 2 的主查询 SQL 中，不做单独校验查询。

规则完全遵循 [sql-query.md §五「部门名称匹配」](references/sql/sql-query.md) 第 1~7 条。

---

## Step 2: 名单查询（单次）

使用 Step 1 返回的 `max_date` 硬编码到 SQL 中（此处硬编码合法，因为值来自 PRE-1 动态获取），**一条 SQL** 查询全部三个人群。

### SQL 模板

```sql
SELECT t1.emp_nm, t1.oprid, t1.pos_lvl,
       ROUND(CAST(t1.age_y AS numeric), 1) AS age_y, t1.job_nm,
       t1.dept_nm, t1.late1_pro_dt,
       t1.late_pfm, t1.late_pfm_prd,
       t1.late_late_pfm, t1.late_late_pfm_prd,
       t2.tag_nm, t2.tag_dscr
FROM ads_ai_qa_emp_df t1
JOIN ads_ai_qa_talent_tag_f t2
  ON t1.emp_id = t2.emp_id
WHERE t1.date = {max_date}                 -- 使用 PRE-1 返回值
  AND t1.dept_nm_lvl1 = '{dept_nm_lvl1}'   -- 按需替换层级和名称
  AND t2.tag_dim_nm = '高潜标签'
  AND t1.emp_sts_cd = '{emp_sts_cd}'        -- 默认 'A'（在职），用户明确要求离职时用 'I'
  AND t2.tag_nm IN ('核心高潜', '高潜', '潜力关注')
ORDER BY t2.tag_nm, t1.pos_lvl DESC, t1.age_y ASC
```

### SQL 构建规则

1. **date 分区**：使用 Step 1 PRE-1 返回的 `max_date` 值（禁止自行猜测或硬编码固定日期）
2. **部门条件**：作用于 `t1.dept_nm_lvl1~lvl6`，按 sql-query.md §五 规则精确匹配
3. **员工状态**：根据用户意图动态决定（见下方规则）
4. **标签维度**：`t2.tag_dim_nm = '高潜标签'`（固定值）
5. **人群范围**：`t2.tag_nm IN ('核心高潜', '高潜', '潜力关注')` 一次性拉取全部三个梯队
6. **排序**：`ORDER BY t2.tag_nm, t1.pos_lvl DESC, t1.age_y ASC`（先按梯队分组，组内职级高→年龄小优先）
7. **无 LIMIT**：SQL 不加 LIMIT，截断逻辑在 Step 3 处理

### 员工状态判定规则

| 用户意图 | `emp_sts_cd` 值 | 触发关键词 |
|---------|----------------|-----------|
| 默认（未提及离职） | `'A'`（在职） | 无特殊关键词，或含"在职" |
| 明确查询离职员工 | `'I'`（离职） | "离职"、"已离职"、"离职的高潜"、"流失的高潜" |

**判定原则**：
- **默认在职**：未出现离职相关关键词时，一律使用 `emp_sts_cd = 'A'`
- **用户明确时切换**：仅当用户 query 中出现"离职"、"已离职"、"流失"等明确表达时，切换为 `emp_sts_cd = 'I'`
- **禁止主动询问**：不要反问用户"您要查在职还是离职"，按默认在职执行
- **禁止同时查询**：一次请求只查一种状态，不合并在职+离职结果

### 执行方式

**单次**调用 `sql_query` 工具，一条 SQL 返回全部人群数据。

```bash
mcporter call hr_talent_claw.sql_query sql='SELECT ... WHERE ... AND t2.tag_nm IN (\'核心高潜\', \'高潜\', \'潜力关注\') ORDER BY t2.tag_nm, t1.pos_lvl DESC, t1.age_y ASC' query="查询高潜人才名单"
```

权限注入由 `sql_query` 工具自动处理，无需手动添加权限条件。

---

## Step 3: 分组与输出（单张卡片）

### 结果分组

SQL 返回的结果集按 `tag_nm` 字段分为三组：

| tag_nm 值 | 对应梯队 | 卡片内段落 |
|-----------|---------|-----------|
| `核心高潜` | ⭐核心高潜 | 第一段表格 |
| `高潜` | 🌟高潜 | 第二段表格 |
| `潜力关注` | 📈潜力关注 | 第三段表格 |

### 截断规则

| 人群 | 截断策略 |
|------|---------|
| 核心高潜 | 超过 200 条时，仅保留前 200 条（SQL 已按 pos_lvl DESC, age_y ASC 排序） |
| 高潜 | 全量输出 |
| 潜力关注 | 全量输出 |

截断时在总结说明段注明："核心高潜共 N 人，当前展示前 200 人"。

### 输出格式

**必须先读取** `output/output-talent-hipo.md`，按其规范将三个梯队合并在**一张飞书卡片**中发送。

数据组装：
1. 按 `tag_nm` 将结果集拆分为三组
2. 各组内数据已由 SQL `ORDER BY` 排好序（pos_lvl DESC, age_y ASC），直接使用
3. **高潜标识列**组装规则（单元格内多行，用 `<br>` 换行）：
   - **第 1 行**：`最近两次绩效(半年/年度)：{late_pfm}({late_pfm_prd})、{late_late_pfm}({late_late_pfm_prd})`，绩效为空显示 `--`
   - **第 2 行**：`年龄分位：{从 tag_dscr 中提取 + 号后的分位信息}`，原始格式如 `最近两次绩效：A级及以上 + 序列X职级x年龄Top10%`，提取 `+` 后部分展示为 `年龄分位：序列X职级x年龄Top10%`，为空则跳过此行
   - **第 3 行**：`最近一次晋升时间：{late1_pro_dt 格式化为 YYYY年MM月}`，为空则跳过此行
4. 三个梯队按顺序排列在同一张卡片中，梯队间用 `---` 和三级标题分隔

卡片结构：
- **标题**：`⭐ {部门名称} · 高潜人才名单`
- **内容**：总结段 → `---` → ⭐核心高潜表格 → `---` → 🌟高潜表格 → `---` → 📈潜力关注表格

---

## 错误处理

| 异常 | 处置 |
|------|------|
| SQL 执行失败/超时 | 输出标准错误话术，终止流程 |
| 返回空集（全部梯队无数据） | 输出无数据话术，不发卡片 |
| 部分梯队无数据 | 跳过空梯队卡片，正常输出有数据的梯队 |
| 权限不足 | 输出权限不足话术 |

---

## 禁止事项

1. ❌ 禁止调用 `es_query`
2. ❌ 禁止硬编码 date 值（如 `20260518`）
3. ❌ 禁止在 SQL 中添加 `real_emp_cls_cd` 筛选（标签表已预判定人群）
4. ❌ 禁止在输出中暴露表名、字段名、SQL 语句
5. ❌ 禁止编造不在 SQL 返回中的数据
