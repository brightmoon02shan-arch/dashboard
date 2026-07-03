---
name: routing-zone
description: >
  Zone 通道场景路由——薪酬 Zone 区查询（现金 Zone / 总包 Zone）。
  外层 SKILL.md 判定进入 zone 通道后，由本文件完成意图提取、场景路由（个人 / 部门分布 / 汇报线团队 / 对比 / 明细 / 筛选）与异常处理。
  数据源独立：6 个 zone 专用 MCP 工具，与 SQL / ES / 报告通道完全隔离。
  数据口径：19 级及以下（数据源已过滤），输出时附口径说明，不在 Skill 内做职级判断或拦截。
---

# Zone 通道——薪酬 Zone 区路由

> **职责**：意图提取、自查兜底、场景路由（个人 / 部门分布 / 汇报线团队 / 对比 / 明细 / 筛选）、工具调用、异常处理。工具参数与示例下沉至 [zone/zone-api.md](zone/zone-api.md)；输出模板下沉至 [output/output-zone.md](output/output-zone.md)。

> **通道定位**：单源专用通道，与 SQL / ES / 报告 / mixed 互斥。命中后本轮固定本通道，禁止跨通道兜底。

## 范围口径

- **部门名 / 组织**：`search-dept` + `query-department-zone`
- **我团队 / 所辖团队 / {人}的下属**：`query-team-accounts` + `query-zone-employee-list`（`userOpridList`）+ 本地聚合

## 核心约束

| 约束 | 说明 |
|------|------|
| 自查兜底 | 本人不可查看自己的 Zone 区（详见 [§1.1 自查兜底](#11-自查兜底)） |
| Zone 维度 | 接口**单次调用**同时返回现金 + 总包双维度；用户指定单维度时**仅展示**对应字段 |
| 双维度字段 | 个人/明细：`cashZone`（现金）、`packageZone`（总包）；部门分布：`distribution[].cashZones` / `packageZones`；热力图：`cashHeatMap` / `packageHeatMap` |
| Zone 筛选 | `salaryZoneList` 筛**现金** Zone；`totalPackageZoneList` 筛**总包** Zone；详见 [zone/zone-api.md#zone-筛选规则](zone/zone-api.md#zone-筛选规则) |
| 部门 ID | `search-dept` 下游 **`deptId` 只取返回的 `deptId`**（如 `"IT"`），勿用 `deptIdPath`（如 `"MI/IT"`）或 `deptName`；详见 [zone/zone-api.md#search-dept](zone/zone-api.md#search-dept) |
| 参数完整性 | 见 [zone/zone-api.md#参数规则](zone/zone-api.md#参数规则)；`string[]` 无筛选传 `'[]'`，勿传 `""` |
| 结果输出 | 标题固定 `薪酬zone区查询结果`；正文仅模板字段 + 标准异常话术，**禁止发挥** |

## 通道工作流

```
进入 zone 通道（已由 SKILL.md 判定）
  → Step 1: 意图提取 + 自查兜底
  → Step 2: 路由判定（个人 / 部门分布 / 汇报线团队 / 对比 / 明细 / 筛选）
  → Step 3: 场景工作流（工具见 zone/zone-api.md）
  → Step 4: 结果输出（模板见 output/output-zone.md）
```

---

## Step 1: 意图提取 + 自查兜底

### 1.1 自查兜底

> SKILL.md §1.1（D22）已对文本含「我的 zone / 我是什么 zone」的输入做前置拦截并引导到飞书人才档案小程序，不会进入本节。本节为 `search_user` 解析后才能识别本人的兜底场景。

**命中条件**（任一即拦截）：

| 类型 | 示例 |
|------|------|
| 姓名即本人 | `search_user` 唯一结果 `oprid` = 当前登录用户 |
| 上下文延续 | 上一轮已确认查的是用户本人 |

**不拦截**：「我团队」「所辖团队」「我部门」「我管辖的 XX 部」等管理查询（团队走汇报线，部门走组织架构）。

**命中处置**：输出标题固定 `薪酬zone区查询结果`，正文仅 `暂无权限查看自己的 Zone 区`，禁止附加说明。

### 1.2 意图字段

| 字段 | 取值 |
|------|------|
| 查询类型 | 个人 / 部门分布 / 汇报线团队分布 / 部门对比 / 人员明细 |
| 目标实体 | 人名、工号、部门名、部门 ID |
| Zone 维度 | 总包 / 现金 / 双维度（默认展示双维度） |
| 聚合方式 | `by_level`（默认）/ `heat_map` / 部门汇总对比 |
| 筛选条件 | `salaryZoneList`（现金）、`totalPackageZoneList`（总包）、`performanceList`、`jobLevels` |

消歧后**记住序号与实体**，下一轮直接继续。

---

## Step 2: 路由判定

| 用户输入模式 | 路由 | 说明 |
|-------------|------|------|
| 人名/工号 + zone/薪酬 | 场景1 个人 | |
| 部门名 + 分布/各职级 zone | 场景2 部门分布 | `search-dept` |
| 我团队/所辖团队/直接下属 + zone | 场景2b 汇报线团队 | `query-team-accounts`；默认 [Zone 汇总表](output/output-zone.md#汇报线团队-zone-分布) |
| {人名}的团队/所辖团队/下属 + zone | 场景2b | 先 `search_user`；输出含管理者本人 Zone + 所辖团队表 |
| {人名}的团队 + **各职级** | 场景2b | 先 `search_user`；表结构见 [各职级](output/output-zone.md#汇报线团队分布各职级) |
| 我部门 + zone（未强调团队/下属） | 场景2 | `search-dept` |
| A vs B 对比 | 场景3 部门对比 | |
| 明细/人员列表/有谁 | 场景4 人员明细 | |
| ZONE/绩效/职级筛选 | 场景2 / 2b / 4 | 见场景5 |
| 热力图 | 场景2 | `distributionMode="heat_map"` |
| 不确定 | 澄清 | |

---

## Step 3: 场景工作流

> **双维度一次返回（所有场景通用）**：`query-personal-zone`、`query-department-zone`、`query-zone-employee-list` 均已移除 `zoneType`，**单次调用**即含现金 + 总包；按用户意图决定展示一个或两个维度，**禁止**为双维度重复调用同一工具。

### 场景1: 个人 Zone

1. `search_user` → 0/1/多人（见 [异常处理](#异常处理)）
2. 唯一 `oprid` = 当前用户 → [自查兜底](#11-自查兜底)
3. `query-personal-zone(oprid, deptId)` → 从 `cashZone`、`packageZone` 取对应维度

### 场景2: 部门 Zone 分布（组织架构）

1. `search-dept` → 取 `data[].deptId` 作为下游 `deptId`（勿用 `deptIdPath` / `deptName`）
2. `distributionMode`：`by_level`（默认）或 `heat_map`
3. `query-department-zone(deptId, ...)` 一次调用
4. `by_level`：分别用 `distribution[].cashZones`、`distribution[].packageZones` 渲染现金/总包表；`heat_map`：分别用 `cashHeatMap`、`packageHeatMap`；标题中的 `{部门名}` 取 `query-department-zone.deptName`（数据归属名，含括号限定），**勿用** `search-dept.deptName`（仅匹配用户输入文本）

### 场景2b: 汇报线团队 Zone 分布

1. **管理者 `oprid`**：本人团队 → `query-team-accounts` 不传或传登录账号；指定人（如「张三所辖团队」）→ `search_user` 后传其 `oprid`
2. `query-team-accounts` → `userOpridList`（0 人 → 异常处理）
3. `deptId`：管理者 `search_user` 返回的 **`deptId`**（或登录上下文，勿用路径字段）
4. `query-zone-employee-list(deptId, userOpridList=全员, ...)` **一次调用**
5. **默认**：按 `list[]` 汇总各 `packageZone`、`cashZone` 人数 → [汇报线团队 Zone 分布](output/output-zone.md#汇报线团队-zone-分布) 双列汇总表
6. **指定管理者**（非「我的团队」）：再调 `query-personal-zone(管理者 oprid, deptId)`，先输出管理者本人 Zone，再输出所辖团队表（模板 A）
7. **我的团队**：跳过步骤 6，**不输出**团队表上方的人员 Zone 信息（模板 B）
8. 用户明确要求「**各职级**」分布时：改按 `jobLevel` × Zone 聚合 → [汇报线团队分布（各职级）](output/output-zone.md#汇报线团队分布各职级)

> 明确**部门名**走场景2；**团队/下属/汇报线**走场景2b。

### 场景3: 部门对比

1. `search-dept` ×2
2. 每部门 `query-department-zone` **一次**；从 `distribution[].cashZones` / `packageZones` 按 Zone 桶跨职级求和；两部门调用可同轮并行；标题中两部门名各自取自身 `query-department-zone.deptName`（数据归属名，含括号限定），**勿用** `search-dept.deptName`
3. 「按职级对比」→ 两部门 by_level 表并排（现金、总包各一组或按用户指定维度）

### 场景4: 人员明细

- **部门**：`search-dept` → `query-zone-employee-list(deptId, userOpridList='[]', ...)`
- **直接下属**：同场景2b 步骤 1～2 → `query-zone-employee-list`（全员 `userOpridList`）
- 每条记录含 `cashZone`、`packageZone`；分页见 `pageNum`/`pageSize`/`total`（`pageSize` 最大 50）

### 场景5: 带筛选查询

| 筛选 | 参数 |
|------|------|
| 现金 Zone | `salaryZoneList` |
| 总包 Zone | `totalPackageZoneList` |
| 绩效 | `performanceList` |
| 职级 | `jobLevels` |

用户仅说「ZONE3」未指明维度 → 默认 `totalPackageZoneList=['ZONE3']`。部门走场景2，团队走场景2b/4。

---

## Step 4: 结果输出

**输出前必须先读取 [output/output-zone.md](output/output-zone.md)**，按其中模板严格输出。未读取模板直接输出属于严重错误（标题、emoji、Zone 值转义、口径脚注、消歧/异常话术均定义在模板文件中）。

---

## 异常处理

**必须使用下表话术，禁止自拟。** 同名多人/多部门用 [候选消歧](output/output-zone.md#候选消歧) 模板。

### Zone 无权限（403 等）

**触发**：`query-department-zone`、`query-zone-employee-list` 等返回无组织档案查看权限（HTTP 403 或等价业务错误）。

**命中处置**（与 [自查兜底](#11-自查兜底) 同级，**先判定权限再输出结果**）：

- **禁止**输出查询结果小节标题（如 `🏢 {部门名} 各职级 Zone 分布`）、表格
- **禁止**附加解释、原因分析、跨部门对比或申请指引
- 结果标题仍为 `薪酬zone区查询结果`；正文**仅**一行：

```markdown
抱歉，您的权限暂时无法查询到{目标}的全年Zone区数据~
```

`{目标}` = 当前查询对象名称：部门查询用 `deptName`（或用户表述的部门名）；个人查询用员工姓名；团队查询用「我的团队」或「{管理者姓名}所辖团队」。

### 工具非成功响应（含 404 等）

**触发**：工具返回 HTTP 404、非成功 `code`，或明确表示无数据/查不到的**业务错误**（非 403 无权限、非自查）。

**命中处置**：

- **禁止**输出查询结果小节标题或表格
- **禁止**套用「该范围内暂无数据」「数据查询异常，请联系技术支持」等固定话术
- 结果标题仍为 `薪酬zone区查询结果`；正文**仅**使用工具返回中的描述原文（如 `message`、`msg` 等，以接口实际字段为准），不得改写、不得附加说明

| 场景 | 触发 | 输出正文（标准话术） |
|------|------|----------|
| 自查 | search_user 解析为本人 | `暂无权限查看自己的 Zone 区` |
| Zone 无权限 | 403 等无组织档案权限 | 见上文 [Zone 无权限（403 等）](#zone-无权限403-等) |
| 工具非成功（含 404） | 404 或非成功且无权限/自查 | 见上文 [工具非成功响应（含 404 等）](#工具非成功响应含-404-等)，仅用工具返回描述 |
| 人员不存在 | `search_user` 空 | `未找到该人员，请确认姓名` |
| 部门不存在 | `search-dept` 空 | `未找到该部门，请确认名称` |
| 无直接下属 | `query-team-accounts` 空 | `该范围内暂无直接下属` |
| 无数据 | 查询成功（如 code 200）但结果为空 | `该范围内暂无数据` |
| MCP 不可用 | `mcporter config list` 无服务 | 引导执行 SKILL.md 顶部前置条件中的安装命令 |
| MCP 繁忙 | 超时/网络错误 | `系统繁忙，请稍后重试` |
| 接口异常 | 非成功且工具无可用描述；或 401 等（**不含** 403、404） | `数据查询异常，请联系技术支持` |

异常/消歧场景：标题固定 `薪酬zone区查询结果`，正文仅放上表、消歧模板或工具返回描述（404 等），**禁止**附加说明。

`query-department-zone` / `query-zone-employee-list`：403 → [Zone 无权限](#zone-无权限403-等)；404 等 → [工具非成功响应](#工具非成功响应含-404-等)；成功且空列表 → `该范围内暂无数据`。

---

## 外部引用

| 文件 | 何时读取 |
|------|---------|
| [zone/zone-api.md](zone/zone-api.md) | 调工具前：参数、示例、调用链、Zone 筛选规则、字段映射 |
| [output/output-zone.md](output/output-zone.md) | Step 4 输出前：标题、emoji、Zone 值转义、各场景模板、消歧模板、口径脚注 |
