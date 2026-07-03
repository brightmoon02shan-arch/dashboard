---
name: table-info-pfm
description: >
  绩效明细表（ads_ai_qa_pfm_f / ads_ai_qa_pfm_q_f）完整字段定义。
  包含绩效期次（pfm_prd）、绩效等级（pfm）、高绩效/绩优/低绩效标识等字段。
  CROSS_TABLE 子场景中特定绩效期次查询使用。
  pfm_f 仅含年度/半年度绩效；pfm_q_f 额外包含季度绩效（用户明确指定季度时使用）。
---

# ads_ai_qa_pfm_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | string | 员工工号 |  | 38302 |  |
| pfm_prd | string | 绩效期次 |  | 2022H2 |  |
| pfm_bgn_dt | string | 绩效期次开始日期 |  | 2022-07-01 00:00:00 |  |
| pfm_end_dt | string | 绩效期次结束日期 |  | 2022-12-31 00:00:00 |  |
| pfm | string | 绩效 |  | B |  |
| hi_pfm_flg | int | 是否高绩效 |  | 0 |  |
| bb_pfm_flg | int | 是否绩优 |  | 0 |  |
| lo_pfm_flg | int | 是否帝纪晓 |  | 0 |  |
| last_hire_flg | int | 最近一次入职标识 |  | 1 |  |
| etl_tm | string | etl时间 |  |  |  |

_共 10 行 × 6 列_

---

# ads_ai_qa_pfm_q_f（含季度绩效）

> **与 pfm_f 的区别**：pfm_f 仅包含年度和半年度绩效期次；pfm_q_f **额外包含季度绩效**（Q1/Q2/Q3/Q4）。
> **使用时机**：用户明确指定"季度绩效"/"Q1/Q2/Q3/Q4"时使用本表；未指定季度时默认用 pfm_f。

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | string | 员工工号 |  | 38302 |  |
| pfm_prd | string | 绩效期次 |  | 2025Q2 | 格式：年度=2022，半年度=2022H1/2022H2，季度=2022Q1/Q2/Q3/Q4 |
| pfm_bgn_dt | string | 绩效期次开始日期 |  | 2025-04-01 |  |
| pfm_end_dt | string | 绩效期次结束日期 |  | 2025-06-30 |  |
| pfm | string | 绩效 |  | B |  |
| hi_pfm_flg | int | 是否高绩效(A及以上) |  | 0 |  |
| bb_pfm_flg | int | 是否绩优(B+及以上) |  | 0 |  |
| lo_pfm_flg | int | 是否低绩效 |  | 0 |  |
| last_hire_flg | int | 最近一次入职标识 |  | 1 |  |
| etl_tm | string | etl时间 |  |  |  |

_共 10 行 × 6 列_
