---
name: table-info-dept
description: >
  部门维表（ads_ai_qa_dept_df）完整字段定义。日快照表，主键 date+dept_id。
  包含部门名称、英文名称、生效状态、部门层级（1-6级）、父部门、主管工号等字段。
  非调转入离场景查询时默认过滤 eft_sts_cd='A'；入职、离职、转入、转出、转岗、调入、调出、调动及其派生指标不要过滤有效部门（例外见 sql-query.md 铁律4）。
---

# ads_ai_qa_dept_df

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| date | int | 数据日期 | 数据日期, 统计日期 | 20260223 |  |
| dept_id | string | 部门编号 | 部门ID, 部门编码 | AM1510 |  |
| dept_nm | string | 部门名称 |  | 上海利枝路工厂物业 |  |
| dept_en_nm | string | 部门英文名称 |  | Shanghai Lizhi Road Factory Property |  |
| eft_sts_cd | string | 生效状态代码 |  | A |  |
| dept_lvl | int | 部门级别 | 层级, 级别 | 4 |  |
| prn_dept_id | string | 父部门ID | 上级部门 | AM000006 |  |
| dept_id_lvl1 | string | 一级部门编号 |  | AM |  |
| dept_nm_lvl1 | string | 一级部门名称 |  | 行政部 |  |
| dept_id_lvl2 | string | 二级部门编号 |  | AM15 |  |
| dept_nm_lvl2 | string | 二级部门名称 |  | ODC |  |
| dept_id_lvl3 | string | 三级部门编号 |  | AM000006 |  |
| dept_nm_lvl3 | string | 三级部门名称 |  | 物业 |  |
| dept_id_lvl4 | string | 四级部门编号 |  | AM1510 |  |
| dept_nm_lvl4 | string | 四级部门名称 |  | 上海利枝路工厂物业 |  |
| dept_id_lvl5 | string | 五级部门编号 |  |  |  |
| dept_nm_lvl5 | string | 五级部门名称 |  |  |  |
| dept_id_lvl6 | string | 六级部门编号 |  |  |  |
| dept_nm_lvl6 | string | 六级部门名称 |  |  |  |
| dept_id_path | string | 部门全路径编号 |  | \MI\AM\AM15\AM000006\AM1510 |  |
| dept_nm_path | string | 部门全路径名称 | 部门路径, 组织全名 | \小米公司\行政部\ODC\物业\上海利枝路工厂物业 |  |
| mng_emp_id | string | 部门主管工号 | 部门负责人, 主管ID | 73804 |  |
| mng_emp_nm | string | 部门主管姓名 |  | 刘宏刚 |  |
| mng_oprid | string | 部门主管账号(邮箱前缀) |  | liuhonggang |  |
| eft_dt | string | 生效日期 |  | 20240201 |  |
| crt_tm | string | 创建时间 |  | 2024-02-06 12:58:38 |  |
| upd_tm | string | 更新时间 |  | 2025-02-07 16:19:53 |  |
| org_sys_cd | string | 组织体系代码 |  | FUNC |  |

_共 28 行 × 6 列_
