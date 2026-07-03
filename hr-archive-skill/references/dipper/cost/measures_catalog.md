# 人力成本与 HC（bizId=119）指标与维度清单

> 指标/维度字典；取数流程见 `query.md`。

| 模块 | `queryKey` | 指标范围 | 维度 |
|------|------------|----------|------|
| **成本金额** | `a3fe268e90104b459919c9f0c95dfbf6` | 预算/实际/结余/使用率/人均金额等 | 19（含职级/序列/城市） |
| **HC** | `d1f192be8da24cc2b0877689551e18c8` | 预算HC/滚测HC/在途/净在职/当月在职等 | 15（无职级/序列/城市） |
| **实际数据边界探查（Step 0）** | `05b5f2a1749c4925bc46955e9776f9b4` | `max_cost_mon`（最新实际月份）、`y_fcst_desc`（全年预测描述） | — |

**模型选型**：measure 须落在对应模型指标表内再选 `queryKey`；**禁止跨模型混用 alias**（如 `ai_qa_cost_amt` ↔ `ai_qa_est_hc`、`max_cost_mon` ↔ 成本/HC 模型）。

**Step 0 探查模型**：用于含 `ai_qa_cost_amt` 的多月查询、双表场景（预测/预计语义），获取 `max_cost_mon` 裁剪 mon 上限；详见 `query.md`「Step 0 实际数据边界探查」。

**fieldType**：`8` = 金额（元）、`2` = 比率（%）、`1` = 人数；展示格式见 `SKILL.md` Output Contract。

---

## 一、成本金额模型

> `queryKey` = **`a3fe268e90104b459919c9f0c95dfbf6`** · `type=1` · 必传 `dates`（东八区毫秒，自然月整月）

### 指标（`measureInfos`）

共 **30** 个（基本 **19** + 组合 **11**）。请求时将 **`alias`** 填入 `measures`。

#### 基本指标（`calculateType=1`）

| alias | 中文名 | 描述摘要 | group2 | id | fieldType |
|-------|--------|----------|--------|-----|-----------|
| `ai_qa_bgt_amt` | 月度总预算-AI问数 | 对ads_ai_qa_cost_bgt_anlys_f表中bgt_amt字段求和 | 预算 | 8155 | 8 |
| `ai_qa_stock_bgt_amt` | 月度股票预算-AI问数 | stock_bgt_amt 求和 | 预算 | 8156 | 8 |
| `ai_qa_cash_bgt_amt` | 月度现金预算-AI问数 | cash_bgt_amt 求和 | 预算 | 8157 | 8 |
| `ai_qa_cost_amt` | 月度总实际成本-AI问数 | cost_amt 求和 | 预算 | 8158 | 8 |
| `ai_qa_stock_cost_amt` | 月度股票实际成本-AI问数 | stock_cost_amt 求和 | 预算 | 8159 | 8 |
| `ai_qa_cash_cost_amt` | 月度现金实际成本-AI问数 | cash_cost_amt 求和 | 预算 | 8160 | 8 |
| `ai_qa_rest_amt` | 月度总结余-AI问数 | SUM(bgt_amt - cost_amt) | 预算 | 8161 | 8 |
| `ai_qa_stock_rest_amt` | 月度股票结余-AI问数 | SUM(stock_bgt_amt - stock_cost_amt) | 预算 | 8162 | 8 |
| `ai_qa_cash_rest_amt` | 月度现金结余-AI问数 | SUM(cash_bgt_amt - cash_cost_amt) | 预算 | 8163 | 8 |
| `ai_qa_fcst_cost_amt` | 预测年成本-AI问数 | fcst_amt 求和 | 预算 | 8164 | 8 |
| `ai_qa_cash_fcst_cost_amt` | 预测年现金成本-AI问数 | cash_fcst_amt 求和 | 预算 | 8165 | 8 |
| `ai_qa_stock_fcst_cost_amt` | 预测年股票成本-AI问数 | stock_fcst_amt 求和 | 预算 | 8166 | 8 |
| `ai_qa_year_avg_fcst_hc` | 预测年均在职人数-AI问数 | hc_fcst_qty 求和后 ÷12 | 预算 | 8167 | 8 |
| `ai_qa_mon_cnt` | 成本月份数-AI问数 | mon 去重计数 | 预算 | 8168 | 1 |
| `ai_qa_bonus_cost_amt` | 年终奖成本-AI问数 | bonus_cost_amt 求和 | 预算 | 8172 | 8 |
| `ai_qa_fix_cost_amt` | 月度固定实际成本-AI问数 | 剔除年终奖、股票后的固定现金实际 | 预算 | 8173 | 8 |
| `ai_qa_fix_bgt_amt` | 累计固定预算-AI问数 | 剔除年终奖、股票后的固定现金预算 | 预算 | 8174 | 8 |
| `ai_qa_fix_est_amt` | 累计固定预估-AI问数 | 剔除年终奖、股票后的固定现金滚测 | 预算 | 8175 | 8 |
| `ai_qa_emp_cnt2` | 当月在职人数(hmc且预算口径)-AI问数 | 当月在职人数(hmc且预算口径)-AI问数 | 预算 | 8358 | 1 |

#### 组合/衍生指标（`calculateType=4`）

| alias | 中文名 | 描述摘要 | group2 | id | fieldType |
|-------|--------|----------|--------|-----|-----------|
| `ai_qa_cost_rate` | 月度总成本使用率-AI问数 | 月度总实际成本 ÷ 月度总预算 ×100% | 预算 | 8176 | 2 |
| `ai_qa_stock_cost_rate` | 月度股票成本使用率-AI问数 | 月度股票实际 ÷ 月度股票预算 ×100% | 预算 | 8177 | 2 |
| `ai_qa_cash_cost_rate` | 月度现金成本使用率-AI问数 | 月度现金实际 ÷ 月度现金预算 ×100% | 预算 | 8178 | 2 |
| `ai_qa_fcst_rest_amt` | 全年预计结余-AI问数 | 全年总预算 − 预测年总成本 | 预算 | 8179 | 8 |
| `ai_qa_fcst_cost_rate` | 预测年成本使用率-AI问数 | 预测年总成本 ÷ 全年总预算 ×100% | 预算 | 8180 | 2 |
| `ai_qa_cash_fcst_cost_rate` | 预测年现金成本使用率-AI问数 | 预测年现金成本 ÷ 全年现金预算 ×100% | 预算 | 8181 | 2 |
| `ai_qa_stock_fcst_cost_rate` | 预测年股票成本使用率-AI问数 | 预测年股票成本 ÷ 全年股票预算 ×100% | 预算 | 8182 | 2 |
| `ai_qa_year_avg_emp_fcst_cost_amt` | 预测年人均成本-AI问数 | 预测年总成本 ÷ 年均在职人数 | 预算 | 8184 | 8 |
| `ai_qa_mon_avg_emp_fcst_cost_amt` | 月度人均预算成本-AI问数 | 月度总预算 ÷ 当月在职人数 | 预算 | 8185 | 8 |
| `ai_qa_mon_avg_emp_cnt` | 累计月均在职人数-AI问数 | 当月在职之和 ÷ 成本月份数 | 预算 | 8189 | 8 |
| `ai_qa_mon_avg_emp_cost_amt2` | 月度人均实际成本(成本报告:全部员工/预算员工)-AI问数 | 月度人均实际成本(成本报告:全部员工/预算员工)-AI问数 | 预算 | 8361 | 8 |

> 复合问法**优先**用上表 alias；无对应组合指标时再按 §六 处理。

### 分析维度（`dimensionInfos`）

共 **19** 个。用于 `dimensions` 或 `condition.field`；**`id` 列**供 `data_search_dimension_values` 的 `dimensionId`。

| alias | 中文名 | 描述 | group2 | id | fieldType | timeFormat |
|-------|--------|------|--------|-----|-----------|------------|
| `dept_id_lvl0` | 零级部门编号 | 零级部门编号 | 组织 | 1449 | 3 | yyyyMMdd |
| `dept_nm_lvl0` | 零级部门名称 | 零级部门名称 | 组织 | 1450 | 3 | yyyyMMdd |
| `dept_id_lvl1` | 一级部门ID | 一级部门ID | 组织 | 879 | 3 | yyyyMMdd |
| `dept_nm_lvl1` | 一级部门名称 | 一级部门名称 | 组织 | 878 | 3 | yyyyMMdd |
| `dept_id_lvl2` | 二级部门ID | 二级部门ID | 组织 | 986 | 3 | yyyyMMdd |
| `dept_nm_lvl2` | 二级部门名称 | 二级部门名称 | 组织 | 1006 | 3 | yyyyMMdd |
| `dept_id_lvl3` | 三级部门ID | 三级部门ID | 组织 | 987 | 3 | yyyyMMdd |
| `dept_nm_lvl3` | 三级部门名称 | 三级部门名称 | 组织 | 1007 | 3 | yyyyMMdd |
| `dept_id_lvl4` | 四级部门ID | 四级部门ID | 组织 | 988 | 3 | yyyyMMdd |
| `dept_nm_lvl4` | 四级部门名称 | 四级部门名称 | 组织 | 1008 | 3 | yyyyMMdd |
| `dept_id_lvl5` | 五级部门ID | 五级部门ID | 组织 | 989 | 3 | yyyyMMdd |
| `dept_nm_lvl5` | 五级部门名称 | 五级部门名称 | 组织 | 1009 | 3 | yyyyMMdd |
| `real_emp_cls_cd` | 员工类型 | 员工类型 | 人员 | 1001 | 3 | yyyyMMdd |
| `emp_cls_cd_desc` | 员工类型描述 | 员工类型描述 | 预算 | 4031 | 3 | yyyyMMdd |
| `pos_lvl_seq` | 职级(整数) | 职级(整数) | 人员 | 2646 | 1 | yyyyMMdd |
| `job_fml_frs_id` | 岗位序列一级分类ID | 岗位序列一级分类ID | 人员 | 1833 | 3 | yyyyMMdd |
| `job_fml_frs_nm` | 岗位序列一级分类名称 | 岗位序列一级分类名称 | 人员 | 1834 | 3 | yyyyMMdd |
| `mon` | 月份yyyyMM01 | 月份yyyyMM01 | 预算 | 4018 | 1 | yyyyMMdd |
| `loc_cty_desc` | 城市区域 | 城市区域 | 预算 | 4021 | 3 | yyyyMMdd |

### 筛选维度（`filterDimensionInfos`）

与上文分析维度 **alias 完全一致**（19 个）。`condition` 筛选字段以上表为准。



---

## 二、HC 模型

> `queryKey` = **`d1f192be8da24cc2b0877689551e18c8`** · `type=1` · 必传 `dates`（东八区毫秒,自然月整月)
>
> ⚠ **部门过滤规则**:HC 模型查询同样适用 `query.md` §部门特殊过滤规则(如手机部排除新业务部、集团/小米公司映射 `dept_id_lvl0='MI'` 等),**不因切换模型而免除**。

### 指标（`measureInfos`）

共 **7** 个（基本 **4** + 组合 **3**）。请求时将 **`alias`** 填入 `measures`。

#### 基本指标（`calculateType=1`）

| alias | 中文名 | 描述摘要 | group2 | id | fieldType |
|-------|--------|----------|--------|-----|-----------|
| `ai_qa_est_hc` | 滚测HC-AI问数 | hc_est_qty 求和 | 预算 | 8169 | 1 |
| `ai_qa_bgt_hc` | 预算HC-AI问数 | hc_bgt_qty 求和 | 预算 | 8170 | 1 |
| `ai_qa_acu_pre_emp_cnt` | 在途人数-AI问数 | 在途入离转组合 | 预算 | 8171 | 1 |
| `ai_qa_emp_cnt1` | 当月在职人数(dwm表而不是hmc)-AI问数 | 当月在职人数(dwm表) | 预算 | 8302 | 1 |

#### 组合/衍生指标（`calculateType=4`）

| alias | 中文名 | 描述摘要 | group2 | id | fieldType |
|-------|--------|----------|--------|-----|-----------|
| `ai_qa_mon_end_emp_cnt` | 月末净在职人数-AI问数 | 当月在职 + 在途 | 预算 | 8186 | 1 |
| `ai_qa_est_rest_hc` | 滚测结余HC-AI问数 | 预算HC − 滚测HC | 预算 | 8187 | 1 |
| `ai_qa_est_hc_rate` | 滚测HC使用率-AI问数 | 滚测HC ÷ 预算HC ×100% | 预算 | 8188 | 2 |

> 复合问法**优先**用上表 alias；无对应组合指标时再按 §六 处理。

### 分析维度（`dimensionInfos`）

共 **15** 个。用于 `dimensions` 或 `condition.field`；**`id` 列**供 `data_search_dimension_values` 的 `dimensionId`。

| alias | 中文名 | 描述 | group2 | id | fieldType | timeFormat |
|-------|--------|------|--------|-----|-----------|------------|
| `dept_id_lvl0` | 零级部门编号 | 零级部门编号 | 组织 | 1449 | 3 | yyyyMMdd |
| `dept_nm_lvl0` | 零级部门名称 | 零级部门名称 | 组织 | 1450 | 3 | yyyyMMdd |
| `dept_id_lvl1` | 一级部门ID | 一级部门ID | 组织 | 879 | 3 | yyyyMMdd |
| `dept_nm_lvl1` | 一级部门名称 | 一级部门名称 | 组织 | 878 | 3 | yyyyMMdd |
| `dept_id_lvl2` | 二级部门ID | 二级部门ID | 组织 | 986 | 3 | yyyyMMdd |
| `dept_nm_lvl2` | 二级部门名称 | 二级部门名称 | 组织 | 1006 | 3 | yyyyMMdd |
| `dept_id_lvl3` | 三级部门ID | 三级部门ID | 组织 | 987 | 3 | yyyyMMdd |
| `dept_nm_lvl3` | 三级部门名称 | 三级部门名称 | 组织 | 1007 | 3 | yyyyMMdd |
| `dept_id_lvl4` | 四级部门ID | 四级部门ID | 组织 | 988 | 3 | yyyyMMdd |
| `dept_nm_lvl4` | 四级部门名称 | 四级部门名称 | 组织 | 1008 | 3 | yyyyMMdd |
| `dept_id_lvl5` | 五级部门ID | 五级部门ID | 组织 | 989 | 3 | yyyyMMdd |
| `dept_nm_lvl5` | 五级部门名称 | 五级部门名称 | 组织 | 1009 | 3 | yyyyMMdd |
| `real_emp_cls_cd` | 员工类型 | 员工类型 | 人员 | 1001 | 3 | yyyyMMdd |
| `emp_cls_cd_desc` | 员工类型描述 | 员工类型描述 | 预算 | 4031 | 3 | yyyyMMdd |
| `mon` | 月份yyyyMM01 | 月份yyyyMM01 | 预算 | 4018 | 1 | yyyyMMdd |

### 筛选维度（`filterDimensionInfos`）

与上文分析维度 **alias 完全一致**（15 个）。`condition` 筛选字段以上表为准。



---

## 三、跨模型说明

| 项 | 说明 |
|----|------|
| 当月在职（成本 vs HC） | 成本模型 `ai_qa_emp_cnt2`（hmc 且预算口径当月在职）；HC 模型 `ai_qa_emp_cnt1`（dwm 当月在职） |
| 维度差异 | HC 模型**无** `pos_lvl_seq`、`job_fml_frs_*`、`loc_cty_desc`；按城市/职级/序列筛选时须走**成本模型**或拒答说明 |
| 预测年均在职 | `ai_qa_year_avg_fcst_hc` 仍在**成本模型**（金额域衍生口径） |

---

## 四、口语 → measure 速查

| 用户问法语义 | 模型 | 优先 measure alias | 备注 |
|--------------|------|-------------------|------|
| 月度总预算 / 实际 / 结余 | 成本 | `ai_qa_bgt_amt` / `ai_qa_cost_amt` / `ai_qa_rest_amt` | 现金、股票：`ai_qa_cash_*`、`ai_qa_stock_*` |
| 月度使用率 | 成本 | `ai_qa_cost_rate` / `ai_qa_cash_cost_rate` / `ai_qa_stock_cost_rate` | 成本模型组合指标 |
| 预测年成本 / 结余 / 使用率 | 成本 | `ai_qa_fcst_cost_amt` / `ai_qa_fcst_rest_amt` / `ai_qa_fcst_cost_rate` 等 | |
| 预算 HC / 滚测 HC | HC | `ai_qa_bgt_hc` / `ai_qa_est_hc` | |
| 滚测 HC 结余 / 使用率 | HC | `ai_qa_est_rest_hc` / `ai_qa_est_hc_rate` | |
| 在途 / 净在职 | HC | `ai_qa_acu_pre_emp_cnt` / `ai_qa_mon_end_emp_cnt` | |
| 当月在职 | HC / 成本 | `ai_qa_emp_cnt1` / `ai_qa_emp_cnt2` | 见 §三（口径差异） |
| 累计月均在职 | 成本 | `ai_qa_mon_avg_emp_cnt` | |
| 人均成本 | 成本 | `ai_qa_mon_avg_emp_cost_amt2` / `ai_qa_year_avg_emp_fcst_cost_amt` | |
| 固定成本（剔年终奖/股票） | 成本 | `ai_qa_fix_cost_amt` / `ai_qa_fix_bgt_amt` / `ai_qa_fix_est_amt` | |
| 年终奖 | 成本 | `ai_qa_bonus_cost_amt` | |

---

## 五、拒答与边界

以下场景 **不发起无意义查询** 或 **`status=failed`**，勿猜数：

| 场景 | 处理 |
|------|------|
| 四五级部门「月度总预算」 | 说明该粒度无预算口径 |
| 到人成本（某员工入职/离职） | 模型无工号/姓名 → 无法回答 |
| 纯权限导致缺数 | `noAuthMeasures` 写入 `warnings`；排障见 `../dipper-api.md` 附录 |
| 口语部门名 | 解析两步法见 `query.md`「部门参数解析（两步法）」；主查询 `condition` 仅 EQ，禁止 LIKE |
| **集团总办、集团总干干部** | **不发起查询**，直接答复：「{该部门名称}不支持查询成本数据」 |
| **三级及以下部门成本** | **不发起查询**，直接答复：「{该部门名称}是三级及以下部门，成本问数查询范围仅限一级部门及二级部门，暂不支持更细粒度的部门查询」 |
| **20级及以上职级成本** | **不发起查询**，直接答复：「20级及以上人员成本数据，不支持查询」 |

**数据时效**：成本为月度数据，**无 T+1 概念**；某月缺数仅在 `warnings` 标注 `total=0`，**禁止**用 T+1 / 未发布 / 未更新 / 数据延迟等措辞解释月度缺数。

---

## 六、特殊问法（无单一 measure 时）

两模型组合指标表已覆盖使用率、结余、预测年、人均、滚测 HC 等；**禁止**为省事拆原子指标手算。仅下列情形允许多步查询或 Agent 侧合成，并在 `warnings` 注明：

| 问法 | 处理方式 |
|------|----------|
| 同比 / 环比 | 两个 `dates` 窗口各查一次同一 `ai_qa_*` measure（**同一 queryKey**） |
| 占比 | 按维度分组拉金额 measure（成本模型），再拉合计后计算 |
| 自定义口径且组合表无对应指标 | 拉对应模型「基本指标」表原子 alias 后按口径合成（极少使用） |

---

## 维护说明

| 章节 | 维护方式 |
|------|----------|
| §一～§二（指标/维度表） | 各 `queryKey` 模型变更后分别拉取 `data_module_meta`（MCP / `data-query`，`bizId=119`，`type=1`）更新 |
| §四～§六 | 测评集 / 产品口径变更时人工更新 |

**元数据**：`data_module_meta` 现网快照（同步：2026-06-04）；底表 `ads_ai_qa_cost_bgt_anlys_f`（AI 问数口径）；明细类问法在对应模型上按维度下钻，无法满足时再降级 `type=3`（见 `SKILL.md` 附录）。

调用约定见 **`SKILL.md`**、**`../dipper-api.md`**、`query.md`。
