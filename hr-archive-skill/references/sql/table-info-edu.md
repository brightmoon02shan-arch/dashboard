---
name: table-info-edu
description: >
  教育经历表（ads_ai_qa_edu_f）完整字段定义。
  包含学历、学位、学校名称、专业、QS100/985/211/C9/G5/常春藤标签、
  第一学历/最终学历/最高学历标识等字段。CROSS_TABLE 子场景中教育经历查询使用。
---

# ads_ai_qa_edu_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| edu_id | numeric(20,0) | 教育经历主键 |  |  |  |
| emp_id | text | 员工工号 |  |  |  |
| edu_seq | int4 | 教育经历序号 |  | 1 |  |
| edu_deg_cd | text | 教育程度编码(学历) |  | E07 |  |
| edu_deg_dscr | text | 教育程度描述(学历) |  | 本科 | 博士研究生,博士,高中,其他,印度HSC,硕士研究生,印度 Master,中专,职高,印度 Diploma,印度 CA,印度 PHD,本科,印尼 Diploma-3,印度 Post Graduation Diploma,印度 Pre-university/+1,印尼 Senior High School,unknown,大专,印尼 Bachelor,印尼 Diploma-1,印尼 Master,技校,博士后,印度 Bachelor |
| deg_cd | text | 学位编码 |  |  |  |
| deg_dscr | text | 学位描述 |  | 1-学士 | -99999,1-学士,2-双学士,8-MBA,7-博士后,3-硕士,9-无学位,5-博士,4-双硕士 |
| hi_edu_flg | int4 | 是否高等教育经历 |  | 1 | 0-否, 1-是 |
| frs_edu_deg_flg | int4 | 是否第一学历 |  | 1 | 0-否, 1-是 |
| fnl_edu_deg_flg | text | 是否最终学历 |  | 1 | 0-否, 1-是 |
| hi_edu_deg_flg | int4 | 是否最高学历 |  | 1 | 0-否, 1-是 |
| start_dt | text | 入校日期 |  | 2017-09-01 |  |
| end_dt | text | 毕业日期 |  | 2017-09-01 |  |
| sch_nm | text | 学校名称 |  |  |  |
| sch_nm_std | text | 学校名称修正后 |  |  |  |
| mjr_nm | text | 专业名称 |  |  |  |
| scd_mjr_nm | text | 第二专业名称 |  |  |  |
| cnr_id | text | 国家编码 |  | CHN |  |
| loc_dscr | text | 学校所在地 |  |  |  |
| dbl_frs_cls_flg | int4 | 是否双一流，[1-是0-否] |  | 1 | 0:否, 1:是 |
| is_985_flg | int4 | 是否985，[1-是0-否] |  | 1 | 0:否, 1:是 |
| is_211_flg | int4 | 是否211，[1-是0-否] |  | 1 | 0:否, 1:是 |
| c9_flg | int4 | 是否c9, [1-是0-否] |  | 1 | 0:否, 1:是 |
| ivy_league_flg | int4 | 是否常春藤大学，[1-是，0-否] |  | 1 | 0:否, 1:是 |
| g5_flg | int4 | 是否g5, [1-是0-否] |  | 1 | 0:否, 1:是 |
| qs100_flg | int4 | 是否qs100, [1-是0-否] |  | 1 | 0:否, 1:是 |
| qs_rank | text | QS排名，如无，为unknown |  |  |  |
| etl_tm | text | etl时间 |  |  |  |

_共 28 行 × 6 列_
