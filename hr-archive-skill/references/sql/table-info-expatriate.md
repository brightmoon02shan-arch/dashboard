---
name: table-info-expatriate
description: >
  外派经历表（ads_ai_qa_exp_asgn_f）完整字段定义。
  包含外派开始/结束日期、区域、国家、地点、岗位名称等字段。
  CROSS_TABLE 子场景中外派经历查询使用。
---

# ads_ai_qa_exp_asgn_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | string | 工号 |  | 64949 |  |
| bgn_dt | int | 外派开始日期 |  | 20220308 |  |
| end_dt | int | 外派结束日期 |  | 20240308 |  |
| area_cd | string | 外派区域代码 |  | 18 |  |
| area_desc | string | 外派区域描述 |  | 独联体地区 |  |
| cnr_id | string | 外派国家代码 |  | RUS |  |
| cnr_desc | string | 外派国家描述 |  | 俄罗斯联邦 |  |
| loc_id | string | 外派地代码 |  | RUS001 |  |
| loc_desc | string | 外派地描述 |  | 俄罗斯-莫斯科 |  |
| pos_nm | string | 岗位名称 | 外派岗位 | 渠道财经 |  |
| etl_tm | string | etl时间 |  | 2026-03-04 07:06:07 |  |

_共 11 行 × 6 列_
