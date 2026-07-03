---
name: table-info-rpt
description: >
  汇报关系表（ads_ai_qa_rpt_f）完整字段定义。
  包含岗位编号/名称、上级岗位、上级员工、汇报线路径（职位/员工/姓名）等字段。
  CROSS_TABLE 子场景中汇报关系查询使用。
---

# ads_ai_qa_rpt_f

| Name            | Type | Description              | Alias | FewShot                                        | Enum |
| :-------------- | :--- | :----------------------- | :---- | :--------------------------------------------- | :--- |
| pos_seq         | text | 岗位序号(0主岗)          |       | 0                                              |      |
| pos_id          | text | 职位编号                 |       | 10167328                                       |      |
| pos_nm          | text | 中文职位名称             |       | 管理培训生                                     |      |
| emp_id          | text | 员工编号(工号)           |       | 77719                                          |      |
| emp_nm          | text | 员工姓名                 |       | 张三                                           |      |
| oprid           | text | 员工账号(邮箱前缀)       |       | zhangsan9                                      |      |
| rpt_pos_seq     | text | 上级岗位序号(0主岗)      |       | 0                                              |      |
| rpt_pos_id      | text | 上级职位编号             |       | 10167000                                       |      |
| rpt_pos_nm      | text | 上级中文职位名称         |       | 区域运营主管                                   |      |
| rpt_emp_id      | text | 上级员工编号(工号)       |       | 10924                                          |      |
| rpt_emp_nm      | text | 上级员工姓名             |       | 李四                                           |      |
| rpt_oprid       | text | 上级员工账号(邮箱前缀)   |       | lisi4                                          |      |
| rpt_pos_id_path | text | 汇报线职级编号           |       | \10000001\10167000\10167328                    |      |
| rpt_pos_nm_path | text | 汇报线中文职位名称       |       | \创始人集团董事长兼CEO\区域运营主管\管理培训生 |      |
| rpt_emp_id_path | text | 汇报线员工编号(工号)     |       | \1110924\77719                                 |      |
| rpt_emp_nm_path | text | 汇报线员工姓名           |       | \雷军\李四\张三                                |      |
| rpt_oprid_path  | text | 汇报线员工账号(邮箱前缀) |       | \leijun\lisi4\zhangsan9                        |      |
| rpt_emp_nm_path_new | text | 汇报线员工姓名(最新使用) |       | \雷军\李四\张三                                |      |
