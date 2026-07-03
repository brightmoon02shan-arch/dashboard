# Zone API 参考

服务：`hr_talent_claw`，通过 mcporter 调用：

```bash
npx mcporter call hr_talent_claw.<工具名> <参数>
```

## 参数规则

- 必填参数不可省略
- `salaryZoneList`、`totalPackageZoneList`、`performanceList`、`jobLevels`、`userOpridList` 均为 `string[]`；无筛选传 `'[]'`
- **勿传空字符串 `""`**（易 500）
- `userOpridList` 无账号筛选时**仍须** `userOpridList='[]'`
- `search-dept` 未用的 `deptName`/`deptId` 传 `""`

---

## search_user

搜索用户，获取 `oprid`、`deptId`。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 姓名、工号、账号 |

```bash
npx mcporter call hr_talent_claw.search_user keyword="张三"
```

**返回（常用）**：`oprid`、`name`、`deptId`、`deptName`

---

## search-dept

搜索部门；下游 `query-department-zone` / `query-zone-employee-list` 的 **`deptId` 参数取值 = 本接口返回的 `deptId`**。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `deptName` | string | 条件 | 按名称搜；否则 `""` |
| `deptId` | string | 条件 | 按 ID 搜；否则 `""` |
| `pageNum` | int | 是 | `1` |
| `pageSize` | int | 是 | `10` |

```bash
npx mcporter call hr_talent_claw.search-dept deptName="信息部" deptId="" pageNum=1 pageSize=10
npx mcporter call hr_talent_claw.search-dept deptId="D001" deptName="" pageNum=1 pageSize=10
```

**返回结构**：`data` 为数组，每项字段如下：

| 字段 | 说明 | 是否用于下游参数 |
|------|------|------------------|
| **`deptId`** | 部门 ID（如 `"IT"`） | **是** → 填入下游 `deptId` |
| `deptName` | 部门名称（如 `"集团信息技术部"`） | 否，仅用于展示/消歧 |
| `deptIdPath` | 部门 ID 全路径（如 `"MI/IT"`） | **否**，勿当作 `deptId` |
| `deptNamePath` | 部门名称全路径 | **否**，仅展示用 |
| `deptLevel`、`authType`、`hasChildren` | 扩展字段 | 否 |

**示例**（节选）：

```json
{
  "code": 200,
  "data": [
    {
      "deptId": "IT",
      "deptName": "集团信息技术部",
      "deptNamePath": "",
      "deptIdPath": "MI/IT"
    }
  ]
}
```

→ 调用 `query-department-zone` / `query-zone-employee-list` 时：`deptId="IT"`（用 **`deptId`**，不是 `deptIdPath` 的 `"MI/IT"`，也不是 `deptName`）。

---

## query-team-accounts

按**汇报线**获取管理者**直接下属**账号，配合 `query-zone-employee-list` 的 `userOpridList` 使用。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `oprid` | string | 条件 | 指定人团队时必填（来自 `search_user`）；查本人团队可省略或传当前登录账号 |

```bash
npx mcporter call hr_talent_claw.query-team-accounts
npx mcporter call hr_talent_claw.query-team-accounts oprid="zhangsan"
```

**返回（常用）**：下属列表，每项含 `oprid`、`name` 等

---

## query-personal-zone

单次调用同时返回现金 Zone 与总包 Zone，**无需** `zoneType` 参数。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `oprid` | string | 是 | 来自 `search_user` |
| `deptId` | string | 是 | 来自 `search_user` |

```bash
npx mcporter call hr_talent_claw.query-personal-zone oprid="zhangsan" deptId="D001"
```

**返回（常用）**：

| 字段 | 说明 |
|------|------|
| `oprid` | 账号 |
| `userName` | 姓名 |
| `jobLevel` | 职级 |
| `positionName` | 职位 |
| `deptName` | 部门 |
| `cashZone` | 现金 Zone |
| `packageZone` | 总包 Zone |

---

## query-department-zone

部门 Zone 分布（组织架构）。单次调用同时返回现金与总包两个维度，**无需** `zoneType`。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `deptId` | string | 是 | **`search-dept` 返回的 `deptId`**（勿用 `deptIdPath` / `deptName`） |
| `distributionMode` | string | 是 | `by_level` / `heat_map` |
| `jobLevels` | string[] | 是 | 无筛选 `'[]'`（如 `["17"]`） |
| `salaryZoneList` | string[] | 是 | **现金** Zone 筛选；无筛选 `'[]'` |
| `totalPackageZoneList` | string[] | 是 | **总包** Zone 筛选；无筛选 `'[]'` |
| `performanceList` | string[] | 是 | 无筛选 `'[]'` |

```bash
npx mcporter call hr_talent_claw.query-department-zone \
  deptId="IT" \
  salaryZoneList='[]' totalPackageZoneList='[]' performanceList='[]' jobLevels='[]' distributionMode="by_level"

npx mcporter call hr_talent_claw.query-department-zone \
  deptId="IT" \
  salaryZoneList='[]' totalPackageZoneList='["ZONE2","ZONE3"]' performanceList='[]' jobLevels='[]' distributionMode="by_level"
```

**返回（常用）**：

| 字段 | 说明 |
|------|------|
| `deptId` / `deptName` | 部门标识与名称 |
| `distributionMode` | 聚合模式 |
| `totalCount` | 总人数（≤19 级） |
| `distribution` | `by_level` 模式：按职级分布，每项含 `level`、`cashZones`、`packageZones`（均为 Zone→人数 Map） |
| `cashHeatMap` | `heat_map` 模式：现金 Zone × 绩效，每项含 `zone`、`performance`、`count` |
| `packageHeatMap` | `heat_map` 模式：总包 Zone × 绩效，结构同上 |

---

## query-zone-employee-list

人员 Zone 明细；每条记录同时含现金与总包 Zone。汇报线团队分布时 `userOpridList` 传直接下属全员。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `deptId` | string | 是 | 部门场景：`search-dept` 的 **`deptId`**；汇报线团队：管理者 `search_user.deptId`（均勿用 `deptIdPath`） |
| `jobLevels` | string[] | 是 | 无筛选 `'[]'` |
| `salaryZoneList` | string[] | 是 | **现金** Zone 筛选；无筛选 `'[]'` |
| `totalPackageZoneList` | string[] | 是 | **总包** Zone 筛选；无筛选 `'[]'` |
| `performanceList` | string[] | 是 | 无筛选 `'[]'` |
| `userOpridList` | string[] | 是 | 无范围 `'[]'`；团队场景传 `query-team-accounts` 全员 `oprid` |
| `pageNum` | int | 否 | 页码，默认 `1` |
| `pageSize` | int | 否 | 每页条数，默认 `10`，**最大 50** |

```bash
npx mcporter call hr_talent_claw.query-zone-employee-list \
  deptId="D001" \
  salaryZoneList='[]' totalPackageZoneList='[]' performanceList='[]' jobLevels='[]' userOpridList='[]'

npx mcporter call hr_talent_claw.query-zone-employee-list \
  deptId="D001" \
  salaryZoneList='[]' totalPackageZoneList='["ZONE1"]' performanceList='[]' jobLevels='["17"]' \
  userOpridList='[]' pageNum=1 pageSize=50

npx mcporter call hr_talent_claw.query-zone-employee-list \
  deptId="D001" \
  salaryZoneList='[]' totalPackageZoneList='[]' performanceList='[]' jobLevels='[]' \
  userOpridList='["sub1","sub2","sub3"]'
```

**返回（常用）**：

| 字段 | 说明 |
|------|------|
| `list` | 员工数组，字段同 `query-personal-zone`（含 `cashZone`、`packageZone`） |
| `pageNum` / `pageSize` / `total` | 分页信息 |

---

## Zone 筛选规则

| 用户意图 | 参数 |
|----------|------|
| 现金 ZONE3 | `salaryZoneList='["ZONE3"]'`，`totalPackageZoneList='[]'` |
| 总包 ZONE3 | `totalPackageZoneList='["ZONE3"]'`，`salaryZoneList='[]'` |
| 仅说 ZONE3、未指明维度 | 默认筛总包：`totalPackageZoneList='["ZONE3"]'`；输出仍可按需展示双维度 |
| 双维度同 Zone 筛选 | 两列表传相同值 |

---

## 字段映射

| 输出占位 | 来源 |
|----------|------|
| 员工姓名 | `search_user.name` 或 `list[].userName` |
| 账号 | `oprid` / `list[].oprid` |
| 现金 Zone | `cashZone` / `distribution[].cashZones` / `cashHeatMap` |
| 总包 Zone | `packageZone` / `distribution[].packageZones` / `packageHeatMap` |
| 部门名（输出展示） | 场景 2/3：`query-department-zone.deptName`（数据归属名，含括号限定，**优先**）；场景 4：`list[0].deptName` 兜底；`search-dept.deptName` 仅用于消歧候选列表，**勿**写入最终输出 |
| 下游 `deptId` | `search-dept.deptId`（**不是** `deptIdPath`、`deptName`） |
| 职级行 | `distribution[].level` 或 `list[].jobLevel` |
| Zone 列 | 固定 6 档：`<ZONE1`、`ZONE1`～`ZONE4`、`>ZONE4`；by_level **表头**不加反引号，人员明细/部门对比数据格以 `>`/`<` 开头须反引号（见 [output/output-zone.md#zone-值转义](../output/output-zone.md#zone-值转义)） |
| 汇报线团队 Zone 汇总表 | `query-zone-employee-list.list` 按 `packageZone`、`cashZone` 分别计数（默认）；各职级时按 `jobLevel` × Zone 聚合 |
| 直接下属账号 | `query-team-accounts` 列表项 `oprid` |

---

## 调用链

| 场景 | 调用链 |
|------|--------|
| 个人 | `search_user` → 自查 → `query-personal-zone`（一次，含双维度） |
| 部门分布 | `search-dept` → `query-department-zone`（一次，含双维度） |
| 汇报线团队分布 | `query-team-accounts`（指定人先 `search_user`）→ 指定人时 `query-personal-zone` → `query-zone-employee-list`（一次）→ Zone 汇总表 |
| 部门对比 | `search-dept` ×2 → 每部门 `query-department-zone` 一次（两部门可同轮并行）→ 汇总 |
| 人员明细（部门） | `search-dept` → `query-zone-employee-list`（`userOpridList='[]'`） |
| 人员明细（下属） | `query-team-accounts` → `query-zone-employee-list`（全员 `userOpridList`） |
