---
name: table-info-ai-cost
description: >
  AI Token 调用成本明细表（ads_mify_cost_di）字段定义。日明细表，
  按日期/渠道/模型/人员/部门记录 AI Token 调用成本。
  包含渠道三分法核心字段 channel、核心金额字段 est_cost_amt、
  Token 用量、模型家族、部门层级等字段。AI_COST 子场景的核心数据源。
---

# hr.ads_mify_cost_di

> **数据源**：Hologres `hr` schema。AI Token 调用成本明细，按 日期×渠道×模型×人员 粒度记录。
> **核心金额字段**：`est_cost_amt`（估算成本，含 MiMo 测算），单位为**元**。问数时如需"万元"由展示层换算。
> **日期字段**：`date`，格式 YYYYMMDD（int）。按月聚合用 `CAST(date / 100 AS INTEGER)` 或日期范围条件。

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| date | bigint | 数据日期，格式 YYYYMMDD | 日期 | 20260401 |  |
| oprid | string | 操作人工号（与 emp_df 关联的 key，去重统计 AI活跃人数） | 工号/账号 | wuyijie |  |
| emp_nm | string | 员工姓名 |  | 吴轶杰 |  |
| emp_sts_cd | string | 员工状态码 |  | A | A:在职, I:离职/停用, 空:未维护 |
| dept_id_lvl1 | string | 一级部门 ID |  | HW |  |
| dept_nm_lvl1 | string | 一级部门名称 | 部门 | 手机部 |  |
| dept_id_lvl2 | string | 二级部门 ID |  | HW38 |  |
| dept_nm_lvl2 | string | 二级部门名称 |  | 新业务部 |  |
| dept_id_lvl3 | string | 三级部门 ID |  |  |  |
| dept_nm_lvl3 | string | 三级部门名称 |  |  |  |
| dept_id_lvl4 | string | 四级部门 ID |  |  |  |
| dept_nm_lvl4 | string | 四级部门名称 |  |  |  |
| dept_id_lvl5 | string | 五级部门 ID |  |  |  |
| dept_nm_lvl5 | string | 五级部门名称 |  |  |  |
| channel | string | 调用渠道/入口（**渠道三分法核心字段**） | 渠道 | Claude Code | Claude Code, OpenCode, MiCode, Codex, Cline, Roo Code, Kilo Code, Gemini CLI, MiTClaw(龙虾), Other, 空 |
| mitclaw_flg | bigint | 龙虾标识 |  | 0 |  |
| model_family | string | 模型家族（供应商集中度分析用） |  | claude | claude, gpt, mimo, gemini 等 |
| model_provider | string | 模型供应商 |  | ppio | xiaomi, ppio, azure_openai 等 |
| model | string | 模型名称（原始） |  | claude-opus-4 |  |
| norm_model | string | 标准化模型名称 |  |  |  |
| billing_entity | string | 计费实体 |  | mify | mify, mitClaw, gatewayFree 等 |
| est_cost_amt | double | 估算成本金额（含 MiMo 测算）**← AI月成本/AI成本取此字段** | AI成本/Token成本 | 12.5 |  |
| cost_amt | decimal | 成本金额（账面，备用） |  |  |  |
| input_token_usage | bigint | 输入 Token 用量（判断活跃用） |  | 10240 |  |
| input_cache_token_usage | bigint | 输入缓存 Token 用量（判断活跃用） |  | 2048 |  |
| output_token_usage | bigint | 输出 Token 用量（判断活跃用） |  | 4096 |  |
| token_amt | double | Token 金额（合计） |  |  |  |
| agent_nm | string | Agent 名称 |  |  |  |
| agent_categ | string | Agent 大类 |  |  | 个人虾, 岗位虾, 空(约78%未分类) |
| agent_type | string | Agent 细分类型 |  |  | 个人虾, 岗位虾, 高管虾, 研发岗位虾, 空 |
| cost_dept_id | string | 成本归属部门 ID |  |  |  |
| cost_dept_name | string | 成本归属部门名称 |  |  |  |
| hour | int | 调用发生的小时时段（0-23） |  | 14 |  |

---

## 渠道三分法（Coding / 龙虾 / 其它）

> **核心规则**：基于 `channel` 字段三分。channel 有 NULL（约13%），归入"其它"。

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

| 渠道分组 | channel 取值 | 说明 |
|---------|-------------|------|
| Coding | Claude Code / OpenCode / MiCode / Codex / Cline / Roo Code / Kilo Code / Gemini CLI | 各编程工具合计，占比约 68%~72% |
| 龙虾 | MiTClaw | 米小研/龙虾渠道 |
| 其它 | 除上述以外所有值（含 Other、NULL） | 未分类工具 |

---

## 关键口径与查询注意

1. **金额字段统一用 `est_cost_amt`**（含 MiMo 测算），不要用 `cost_amt`。单位为元。
2. **AI活跃人数 = `COUNT(DISTINCT CASE WHEN est_cost_amt > 0 AND oprid IS NOT NULL AND oprid <> '' THEN oprid END)`**，且 JOIN `ads_ai_qa_emp_df` 仅统计**在职人员**（`emp_sts_cd='A'`）、过滤 oprid 空/空串；**不**排除蓝领/外包A。
3. **按月聚合用日期范围条件**（`date >= 20260401 AND date < 20260501`）而非 `date/100=202604`，可利用分区裁剪、避免全表扫描。
4. **部门过滤/分组用 `dept_id_lvl{N}`** 而非 `dept_nm`，避免重名问题。
5. **AI成本直接从成本表 SUM，不 JOIN 员工表、不过滤在职/oprid**（离职人员历史成本仍计入）。**活跃人数、人均AI成本**通过 JOIN `ads_ai_qa_emp_df` 取部门归属，且仅统计**在职人员**（`emp_sts_cd='A'`）、过滤 oprid 空/空串，但**不**排除蓝领/外包A。**仅 AI渗透率**额外过滤蓝领/外包A（分子活跃人数 + 分母总人数都过滤，条件 `blue_flg = 0 AND NOT (dept_id_lvl1 = 'MW' AND real_emp_cls_cd = '115')`，且分子分母均按 oprid 去重对齐）。详见 intent-ai-cost.md。
6. **人力成本不在本表**：人力成本走 `ads_ai_qa_cost_bgt_anlys_f`，且**不支持问数**（走 cost_report 工具）。
