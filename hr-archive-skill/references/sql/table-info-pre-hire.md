---
name: table-info-pre-hire
description: >
  预入职表（ads_ai_qa_pre_hire_f）完整字段定义。
  记录 offer 状态为预入职的员工信息，包含预入职日期、职级、员工类型、
  招聘类型（校招/实习/社招/内部活水）、未来星标识、高薪offer标识等字段。
  FLOW 子场景中预入职相关指标的核心数据源。
---

# ads_ai_qa_pre_hire_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| ofr_id | text | offer id |  | 38302 |  |
| data_source | text | 数据源 |  |  |  |
| dept_id | text | 部门id |  |  |  |
| eft_dt | text | 预入职日期 |  | 2025-01-01 |  |
| pos_lvl | text | 职级 |  | 13 |  |
| real_emp_cls_cd | text | 员工类型 |  | 101 |  |
| psn_typ | int | 候选人类型（招聘渠道） | 招聘类型 | 1 | 1-校招 2-实习 3-社招 4-内部活水 |
| fur_flg | int | 未来星标识 |  | 1 | 0-非未来星 1-是未来星 |
| hig_inc_flg | int | 高薪offer标识 |  | 1 | 0-非高薪 1-是高薪 |

_共 9 行 × 6 列_
