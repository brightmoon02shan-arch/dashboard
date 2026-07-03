---
name: table-info-talent-tag
description: >
  人才标签表（ads_ai_qa_talent_tag_f）完整字段定义。
  包含标签目录（管理信息/教育经历/基本信息/晋升绩效/工作信息等）、
  维度（工龄/学历等）、标签名称/描述等字段。
  CROSS_TABLE 子场景中人才标签查询使用。
---

# ads_ai_qa_talent_tag_f

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| emp_id | string | 人员ID |  | 63236 |  |
| tag_categ_id | bigint | 目录ID |  | 1 |  |
| tag_categ_cd | string | 目录code |  | L0001 |  |
| tag_categ_nm | string | 目录名称 |  | 管理信息,教育经历,基本信息,晋升绩效,工作信息,评价信息,重要奖项,集团荣誉 |  |
| tag_dim_id | bigint | 维度ID |  | 12 |  |
| tag_dim_cd | string | 维度code |  | L000012 |  |
| tag_dim_nm | string | 维度名称 |  | 工龄 |  |
| tag_id | bigint | 标签ID |  | 311 |  |
| tag_cd | string | 标签代码 |  | L00000312 |  |
| tag_nm | string | 标签名称 |  | 工龄5-10年 |  |
| tag_dscr | string | 标签描述 |  | 工作 (5,10] 年 |  |
| etl_tm | string | etl时间 |  |  |  |

_共 12 行 × 6 列_
