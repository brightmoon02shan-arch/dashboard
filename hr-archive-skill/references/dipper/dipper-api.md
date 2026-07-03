# data-query MCP API 参考

> 北斗（data-query）MCP 协议参考：详述主流程会用到的工具与参数。

## 人力成本固定参数（bizId=119）

| 项 | 值 |
|----|-----|
| `bizId` | **119** |
| `type`（默认） | **1**（聚合） |
| `queryKey` | 成本 **`a3fe268e90104b459919c9f0c95dfbf6`** / HC **`d1f192be8da24cc2b0877689551e18c8`**（见 `cost/measures_catalog.md` 模型选型；禁止更换；勿与 teamquery 的 queryKey 混淆） |
| 指标 / 维度清单 | `references/dipper/cost/measures_catalog.md`（**优先查表**，勿为选路每次调 `data_module_meta`） |
| 请求体示例 | 见下文「data_query — 调用示例」 |

`type=3` 自由查询降级见 `SKILL.md` 附录；`type=2` 明细模型**不在**本域使用。

---

## callContext（强制）

每次 MCP 调用必须携带：

```json
{
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "用户原始输入",
    "userSkill": "hr-cost-query"
  }
}
```

| 字段 | 说明 |
|------|------|
| `messageId` | 飞书消息 ID |
| `userInput` | 用户原文，不翻译、不摘要 |
| `userSkill` | 本技能固定 **`hr-cost-query`**；父技能包装时填父技能名 |

---

## 本技能工具范围

| 优先级 | 工具 | 用途 |
|--------|------|------|
| 必用 | `data_query` | 默认 `type=1` + 固定 `queryKey`；极少数 `type=3` 降级 |
| 按需 | `data_search_measures` | catalog §四 对不上口语时搜指标 **alias**（**不**用于选 queryKey） |
| 按需 | `data_search_dimension_values` | 部门 ID、维度枚举；`dimensionId` 见 `cost/measures_catalog.md` 对应模型「分析维度」表的 `id` 列 |
| 不用 | 见 [附录：未纳入本技能的工具](#附录未纳入本技能的工具) | |

调用方式（示例）：

```bash
mcporter call data-query.data_query --args '{...}' --output json
```

---

## data_query — 统一数据查询

### 入参

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | integer | ✅ | 本技能：**1**（默认）；降级 **3**（不传 `queryKey`） |
| `bizId` | integer | ✅ | **119** |
| `queryKey` | string | type=1 时 ✅ | 固定 `a3fe268e90104b459919c9f0c95dfbf6` |
| `measures` | string[] | | 指标 alias，如 `ai_qa_cost_rate` |
| `dimensions` | string[] | | 维度 alias，如 `dept_id_lvl2`、`mon` |
| `dates` | object | 可选 | 东八区毫秒；自然月须**整月起止**。时间口径以 `condition.mon` 为准；`dates` 已不必传，仅在需覆盖默认全局窗时使用 |
| `dates.startDate` | integer(ms) | 仅当传 `dates` 时必填 | |
| `dates.endDate` | integer(ms) | 仅当传 `dates` 时必填 | |
| `condition` | Condition | | 维度筛选；业务月筛 **`mon`**（`YYYYMM01`） |
| `measureCondition` | Condition | | 指标筛选（少用） |
| `orderBys` | object[] | | `[{ "alias", "desc" }]` |
| `pageParam` | object | | `{ "pageNum", "pageSize" }` |
| `callContext` | object | ✅ | 见上 |

> 本聚合模型**无 `date` 维度**；用户说的「× 月」用 `condition` 约束 **`mon`**（`YYYYMM01`）。`dates` 已不必传——时间口径唯一来源是 `condition.mon`。详见 `SKILL.md`。

### 调用示例（type=1，bizId=119）

```json
{
  "type": 1,
  "bizId": 119,
  "queryKey": "a3fe268e90104b459919c9f0c95dfbf6",
  "measures": ["ai_qa_cost_rate"],
  "dimensions": ["dept_id_lvl2"],
  "condition": {
    "operator": "AND",
    "subConditions": [
      { "field": "dept_id_lvl1", "filterType": 1, "value": "DEPT_ID_PLACEHOLDER" },
      { "field": "mon", "filterType": 10, "value": ["20260101", "20260201"] }
    ]
  },
  "pageParam": { "pageNum": 1, "pageSize": 50 },
  "orderBys": [],
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "查中国区今年1-2月总成本使用率",
    "userSkill": "hr-cost-query"
  }
}
```

### 调用示例（type=1，单月 + 多指标下钻）

```json
{
  "type": 1,
  "bizId": 119,
  "queryKey": "a3fe268e90104b459919c9f0c95dfbf6",
  "measures": ["ai_qa_cost_amt", "ai_qa_bgt_amt"],
  "dimensions": ["dept_id_lvl2", "mon"],
  "condition": {
    "operator": "AND",
    "subConditions": [
      { "field": "dept_id_lvl1", "filterType": 1, "value": "DEPT_ID_PLACEHOLDER" },
      { "field": "mon", "filterType": 1, "value": "20260401" }
    ]
  },
  "pageParam": { "pageNum": 1, "pageSize": 20 },
  "orderBys": [],
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "查信息技术部4月二级部门成本与预算",
    "userSkill": "hr-cost-query"
  }
}
```

### type=3 降级（自由查询）

仅当 `SKILL.md` 附录条件满足时使用；**不传** `queryKey`。

```json
{
  "type": 3,
  "bizId": 119,
  "measures": ["ai_qa_cost_amt", "ai_qa_bgt_amt"],
  "dimensions": ["dept_id_lvl1"],
  "condition": {
    "operator": "AND",
    "subConditions": [
      { "field": "mon", "filterType": 1, "value": "20260401" }
    ]
  },
  "pageParam": { "pageNum": 1, "pageSize": 50 },
  "orderBys": [],
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "查一级部门本月总成本与预算",
    "userSkill": "hr-cost-query"
  }
}
```

---

## data_search_measures — 搜索指标

catalog §四 无法映射口语到 `ai_qa_*` alias 时使用；返回结果中的 queryKey **忽略**，仍以固定聚合 key 取数。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `bizId` | integer | ✅ | **119** |
| `keyword` | string | | 匹配名称/别名/描述 |
| `calculateType` | integer[] | | 1=基本, 4=组合（可筛 `4` 找使用率类） |
| `status` | integer[] | | 1=可用 |
| `pageNum` / `pageSize` | integer | | 默认 1 / 10，最大 100 |
| `callContext` | object | ✅ | |

```json
{
  "bizId": 119,
  "keyword": "使用率",
  "pageNum": 1,
  "pageSize": 20,
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "查总成本使用率",
    "userSkill": "hr-cost-query"
  }
}
```

---

## data_search_dimension_values — 查维度枚举值 / 关键词检索

用于把口语词解析到规范维度值（如部门名 → 完整规范名 / `dept_id_lvl*`），或在本地枚举与线上下发不一致时取最新值。`keyword` 与 `dimensionId` **二选一,不可同时传**。

| 参数 | 类型 | 必填条件 | 说明 |
|------|------|---------|------|
| `bizId` | integer | keyword 模式必填 | 固定 **119** |
| `keyword` | string | 关键词检索模式 | 用户原文核心词（禁止截断,如「湖北分公司」不得写 `"湖北"`）;**部门解析主路径** |
| `dimensionId` | integer | 维度枚举模式 | 维度数字 ID,见 `cost/measures_catalog.md` 对应模型「分析维度」表（如 `dept_id_lvl1` → 879） |
| `pageNum` / `pageSize` | integer | 可选 | keyword 模式默认 1 / 10 |
| `callContext` | object | ✅ | |

部门解析示例（keyword 模式）:

```json
{
  "bizId": 119,
  "keyword": "集团信息技术部",
  "callContext": {
    "messageId": "om_xxx",
    "userInput": "集团信息技术部 成本使用详情",
    "userSkill": "hr-cost-query"
  }
}
```

**响应关键字段**（`data.data[]`，已按 `score` desc 排序）：

| 字段 | 含义 |
|------|------|
| `score` | 向量相似度（值越大越靠前） |
| `value` / `valueLabel` | 维度值文本（部门完整规范名） |
| `dimensionName` | 维度中文名（如「一级部门」「ai 问数-一级部门名称」） |
| `dimensionAlias` | 维度名字段 alias（如 `dept_lvl1_name`） |
| `joinIdAlias` | 维度 ID 字段 alias（如 `dept_lvl1_id`） |
| `joinIdValue` | **部门 ID 值**（如 `IT` / `HW38` / `HW3810`） |

枚举与 `references/dipper/cost/enum.md` 冲突时，**以本接口线上下发为准**。

---

## 复杂参数说明

### Condition 类型

可为单叶子，或 `operator` + `subConditions` 嵌套（AND / OR）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `field` | string | 维度 alias（如 `mon`、`dept_id_lvl1`） |
| `filterType` | FilterType | 操作符 |
| `value` | object | 标量或字符串数组 |
| `operator` | string | AND / OR |
| `subConditions` | Condition[] | 子条件 |

**禁止**使用 `relation` + `conditions` 等非北斗结构。

单业务月（`mon`）：

```json
{ "field": "mon", "filterType": 1, "value": "20260401" }
```

部门 + 多月：

```json
{
  "operator": "AND",
  "subConditions": [
    { "field": "dept_id_lvl1", "filterType": 1, "value": "DEPT_ID_PLACEHOLDER" },
    { "field": "mon", "filterType": 10, "value": ["20260101", "20260201", "20260301"] }
  ]
}
```

### FilterType 枚举（常用）

| 值 | 常量 | 含义 |
|----|------|------|
| 1 | EQ | 等于 |
| 2 | NE | 不等于 |
| 10 | INCLUDE | 包含（多值 IN） |
| 11 | NOT_INCLUDE | 不包含 |
| 12 | LIKE | 模糊匹配 |

完整枚举：

| 值 | 常量 | 含义 |
|----|------|------|
| 3 | GT | 大于 |
| 4 | GE | 大于等于 |
| 5 | LT | 小于 |
| 6 | LE | 小于等于 |
| 7 | BE | 介于 |
| 8 | NU | 为空 |
| 9 | NN | 不为空 |
| 13 | RNU | 相关为空 |
| 14 | RNN | 相关不为空 |
| 15 | LEFT_LIKE | 左模糊 |
| 16 | RIGHT_LIKE | 右模糊 |

---

## 出参规范（data_query）

| 字段 | 说明 |
|------|------|
| `code` | **200** 为成功（与部分文档中的 0 表述并存时，以实际 MCP 返回为准） |
| `data.total` | 记录数；0 表示空结果 |
| `data.records` | 行数据 |
| `data.noAuthMeasures` | 无权限的指标 alias 列表 |
| `extendInfo.sql` | 调试 SQL（type=3 较常见） |
| `extendInfo.traceId` | 链路追踪 |

```json
{
  "code": 200,
  "data": {
    "total": 1,
    "records": [],
    "noAuthMeasures": []
  },
  "message": "",
  "extendInfo": {
    "sql": null,
    "traceId": "..."
  }
}
```

---

## 附录：未纳入本技能的工具

以下工具在 data-query MCP 中存在，**`hr-cost-query` 主流程不调用**。仅平台扩展或排障时参考 One Hub 全量文档。

| 工具 | 原用途 | 本技能替代方式 |
|------|--------|----------------|
| `data_search_dimensions` | 搜维度 alias | 查 `cost/measures_catalog.md` 对应模型「分析维度」表 |
| `data_module_meta` | 拉模型元数据 | 查 `cost/measures_catalog.md` |
| `data_measure_detail_query` | 指标明细下钻 | 同模型加细 `dimensions` + `type=1` |
| `data_measures_support_dimensions` | type=3 时查可用维度 | 查 catalog §一/§二「分析维度」表 |
| `data_teamquery` | SQL 模板同步查询 | 不使用 |
| `data_teamquery_asyn_submit_task` | teamquery 异步提交 | 不使用 |
| `data_teamquery_asyn_fetch_result` | teamquery 异步轮询 | 不使用 |
| `data_auth_measures_dimensions` | 查用户有权限的指标/维度 | 一般用 `noAuthMeasures` + 文案说明；排障时可调 |
