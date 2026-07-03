---
name: table-info-relationships
description: >
  表关联关系定义（Table Relationships）。定义所有表之间的 JOIN 条件、关联类型和使用场景。
  包含 emp↔dept、tmn↔emp、hire↔emp、trsf↔emp、emp 自关联（主管）、
  外派↔emp、标签↔emp、绩效↔emp、教育↔emp 共 9 种关联关系。
  编写跨表 JOIN SQL 时参考本文件确认关联条件。
---

# Table Relationships

| Sequence | Relation Name | Left Table | Right Table | Join Type | Join Condition | Relation Type | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | emp_join_dept | ads_ai_qa_emp_df | ads_ai_qa_dept_df | left_join | ads_ai_qa_emp_df.dept_id = ads_ai_qa_dept_df.dept_id AND ads_ai_qa_emp_df.date = ads_ai_qa_dept_df.date | one_to_one | 当需要通过部门维表获取更详细的组织信息（如部门主管ID、生效状态）时使用。 |
| 2 | tmn_join_emp | ads_ai_qa_trsf_tmn_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_trsf_tmn_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 员工离职后信息不会发生变化，所以可以直接使用最新的快照信息。 |
| 3 | hire_join_emp | ads_ai_qa_trsf_hire_f | ads_ai_qa_emp_df | inner_join | ads_ai_qa_trsf_hire_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_trsf_hire_f.hire_dt = ads_ai_qa_emp_df.date -- 取入职时信息 ads_ai_qa_trsf_hire_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> -- 取最新信息 | many_to_one | 查询新员工入职时的初始职级、初始部门等快照信息，或查询入职员工最新的信息。 |
| 4 | trsf_join_emp | ads_ai_qa_trsf_in_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_trsf_in_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_trsf_in_f.trsf_dt = ads_ai_qa_emp_df.date -- 取转入转出时信息 ads_ai_qa_trsf_in_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> -- 取最新信息 | many_to_one | 用于分析异动当天/最新的员工状态，包含转出部门名称、原职级等。 |
| 5 | emp_join_emp | ads_ai_qa_emp_df (as subordinate) | ads_ai_qa_emp_df (as manager) | left_join | subordinate.mng_emp_id = manager.emp_id AND subordinate.date = manager.date | one_to_one | 当需要查询主管的详细属性（如主管的学历、主管的绩效）时进行自关联。 |
| 6 | asgn_join_emp | ads_ai_qa_asgn_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_asgn_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 当需要查询员工的外派经历，或者当前外派状态时，可以查询该表 |
| 7 | tag_join_emp | ads_ai_qa_talent_tag_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_talent_tag_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 当需要查询员工的人才标签信息时，可以查询该表 |
| 8 | pfm_join_emp | ads_ai_qa_pfm_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_pfm_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 当需要查询员工的历史绩效明细数据时，可以查询该表 |
| 9 | edu_join_emp | ads_ai_qa_edu_f | ads_ai_qa_emp_df | inner_join | ads_ai_qa_edu_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 当需要查询员工的教育经历详情（毕业院校、专业、QS100/985/211/C9/G5/常春藤标签等）时，关联该表。一个员工可能有多条教育经历，统计人数时需 COUNT(DISTINCT emp_id) |
| 10 | pre_hire_join_dept | ads_ai_qa_pre_hire_f | ads_ai_qa_dept_df | inner_join | ads_ai_qa_pre_hire_f.dept_id = ads_ai_qa_dept_df.dept_id AND ads_ai_qa_dept_df.date = <yesterday_yyyymmdd_int> | many_to_one | 预入职关联部门维表，获取部门层级信息用于部门筛选。无分区，每日全量覆盖。 |
| 11 | pre_tmn_join_emp | ads_ai_qa_pre_tmn_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_pre_tmn_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 预离职关联员工主表，获取员工属性（高薪hig_inc_flg、绩效late_pfm、未来星fur_flg、职级pos_lvl等）。指标#103-#109需要此关联。 |
| 12 | pre_trsf_join_dept | ads_ai_qa_pre_trsf_f | ads_ai_qa_dept_df | inner_join | ads_ai_qa_pre_trsf_f.in_dept_id = ads_ai_qa_dept_df.dept_id AND ads_ai_qa_dept_df.date = <yesterday_yyyymmdd_int> -- 转入部门 ads_ai_qa_pre_trsf_f.out_dept_id = ads_ai_qa_dept_df.dept_id AND ads_ai_qa_dept_df.date = <yesterday_yyyymmdd_int> -- 转出部门 | many_to_one | 预转岗关联部门维表。与trsf_in_f类似，预转入/预转出统计需两次JOIN dept_df（转入部门+转出部门），用部门名称排除内部调动。 |

| 13 | pfm_q_join_emp | ads_ai_qa_pfm_q_f | ads_ai_qa_emp_df | left_join | ads_ai_qa_pfm_q_f.emp_id = ads_ai_qa_emp_df.emp_id AND ads_ai_qa_emp_df.date = <yesterday_yyyymmdd_int> | many_to_one | 当需要查询员工的含季度绩效明细数据时使用（pfm_prd含Q1/Q2/Q3/Q4）。仅当用户明确指定季度时使用本表，默认用 pfm_f。 |

_共 13 行 × 8 列_
