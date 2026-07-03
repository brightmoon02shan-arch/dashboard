---
name: table-info-pre-trsf
description: >
  预转岗表（ads_ai_qa_pre_trsf_f）完整字段定义。
  记录处于预转岗/预调动状态的员工信息，包含转岗日期、转入/转出部门、
  转入/转出岗位、转入/转出职级、转入/转出员工类型等字段。
  预转入/预转出指标需 JOIN dept_df 获取部门层级信息。
  FLOW 子场景中预转岗相关指标的核心数据源。
---

# ads_ai_qa_pre_trsf_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | text | 员工工号 | 调动员工 | 38302 |  |
| data_source | text | 数据源 |  |  |  |
| eft_dt | text | 转入转出日期 | 调动日期、转岗日期 | 2025-01-01 |  |
| in_dept_id | text | 转入部门id |  |  |  |
| in_pos_id | text | 转入岗位 |  |  |  |
| in_pos_lvl | text | 转入职级 |  |  |  |
| out_dept_id | text | 转出部门id |  |  |  |
| out_pos_id | text | 转出岗位 |  |  |  |
| out_pos_lvl | text | 转出职级 |  |  |  |
| out_real_emp_cls_cd | text | 转出员工类型 |  |  |  |
| in_real_emp_cls_cd | text | 转入员工类型 |  |  |  |

_共 11 行 × 6 列_
