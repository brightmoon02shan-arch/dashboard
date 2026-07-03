---
name: table-info-pre-tmn
description: >
  预离职表（ads_ai_qa_pre_tmn_f）完整字段定义。
  记录处于预离职状态的员工信息，包含生效日期、离职原因代码/文本、被动离职标识等字段。
  部分预离职指标（高薪/高绩效/未来星/职级19+）需 JOIN emp_df 获取员工属性。
  FLOW 子场景中预离职相关指标的核心数据源。
---

# ads_ai_qa_pre_tmn_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | text | 员工工号 |  | 38302 |  |
| data_source | text | 数据源 |  |  |  |
| dept_id | text | 部门id |  |  |  |
| eft_dt | text | 生效日期 |  | 2025-01-01 |  |
| tmn_rsn_cd | text | 离职原因code |  | R29 |  |
| tmn_rsn_nm | text | 离职原因文本 |  |  |  |
| psv_tmn_flg | int | 被动离职标识 |  |  |  |

_共 7 行 × 6 列_
