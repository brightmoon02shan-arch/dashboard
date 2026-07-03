---
name: table-info-emp
description: >
  员工主表（ads_ai_qa_emp_df）完整字段定义。日快照表，主键 date+emp_id。
  包含工号、姓名、部门层级、职级、员工类型、性别、年龄、司龄、学历、绩效预计算标记、
  base地等全量字段。EMP_BASIC 子场景的核心数据源。
---

# ads_ai_qa_emp_df

| Name | Type | Description | Alias | FewShot | Enum |
| --- | --- | --- | --- | --- | --- |
| date | int | 数据日期 |  | 20260223 |  |
| emp_id | string | 员工编号(工号) | 工号 | 38302 |  |
| last_emp_id | string | 变更前工号（上一次入职时的员工id，用于外部顾问转正等身份变更场景的关联） |  |  |  |
| oprid | string | 员工账号(邮箱前缀) | 邮箱前缀 | wuyijie |  |
| emp_eml_adr | string | 员工邮箱地址 |  | wuyijie@xiaomi.com |  |
| emp_nm | string | 员工姓名 |  | 吴轶杰 |  |
| emp_nm_dsp | string | 花名，展示名称 |  | 吴轶杰 |  |
| emp_sts_cd | string | 员工状态代码 |  | A | 在职:A, 离职:I |
| emp_cls_cd | string | 员工类别代码 | 用工类型 | 101 |  |
| real_emp_cls_cd | string | 真实员工类型代码 |  | 101 | 101: 正式员工,102: 实习生,103: 兼职,104: 派遣,105: 外包,106: 实习生 - 小时制,107: 外部顾问,108: 外包 - 项目外包,109: 派遣A,110: 派遣B,111: 派遣C,112: 兼职A,113: 兼职B,114: 兼职C,115: 外包A,116: 外包B,117: 外包C,118: 外部顾问A,119: 外部顾问B,120: 外部顾问C,122: 外包P |
| mrg_sts_cd | string | 员工婚姻状况代码 |  | S | D: 离异,M: 已婚,P: ,S: 单身,U: 未知,空: 未维护 |
| gdr_cd | string | 员工性别代码 | 性别 | M | F: 女,M: 男,P: 双性,U: 未知 |
| ntn_grp_cd | string | 民族代码 |  | HAN |  |
| cmp_id | string | 公司编号 |  | 321 |  |
| cmp_chn_nm | string | 公司中文名称 |  | 天津小米景明科技有限公司 |  |
| cmp_cnr_id | string | 公司国家(天数) |  | CHN |  |
| cmp_cnr_nm | string | 国家名称 |  | 中国 |  |
| emp_cst_cntr_id | string | 个人成本中心编码 |  | CL190Z1062 |  |
| emp_cst_cntr_nm | string | 个人成本中心名称 |  | 天津市X0596零售中心 |  |
| dept_cst_cntr_id | string | 部门成本中心编码 |  | C8800Z1062 |  |
| dept_cst_cntr_nm | string | 部门成本中心名称 |  | 天津市X0596零售中心 |  |
| bth_dt | string | 出生日期 |  | 2002-11-21 |  |
| frs_wrk_dt | string | 首次参加工作日期 |  | 2025-07-04 |  |
| last_hire_dt | string | 最后入职日期 |  | 2025-07-04 |  |
| mi_hire_dt | string | 小米承认入职时间 |  | 2025-07-04 |  |
| tmn_dt | string | 离职日期 |  | 2025-04-05 |  |
| tmn_eft_dt | string | 离职生效日期 |  | 2025-04-06 |  |
| prc_dt | string | 转正日期 |  | 2026-01-04 |  |
| cnr_id | string | 国家代码 |  | CHN |  |
| bas_loc_id | string | base工作地所在区域编号 |  | CHN018 |  |
| bas_loc_nm | string | base工作地所在区域名称 | base地 | 天津 |  |
| pos_id | string | 职位编号 |  | 10277477 |  |
| pos_nm | string | 职位名称 |  | 零售顾问 |  |
| pos_lvl | string | 职级 | 级别 | 13 |  |
| hi_pos_lvl_flg | int | 高职级标识(19+) |  | 0 |  |
| lo_pos_lvl_flg | int | 低职级标识(19-) |  | 1 |  |
| job_id | string | 岗位编号 |  | ZD040301K1 |  |
| job_nm | string | 岗位名称 |  | 零售主管 |  |
| job_fml_frs_id | string | 岗位序列一级分类编号 |  | ZD |  |
| job_fml_frs_nm | string | 岗位序列一级分类名称 |  | 终端序列 |  |
| job_fml_scd_id | string | 岗位序列二级分类编号 |  | ZD04 |  |
| job_fml_scd_nm | string | 岗位序列二级分类名称 |  | 终端零售类（汽车） |  |
| job_fml_thd_id | string | 岗位序列三级分类编号 |  | ZD0403 |  |
| job_fml_thd_nm | string | 岗位序列三级分类名称 |  | 终端零售专员子类 |  |
| job_fml_four_id | string | 岗位序列四级分类编号 |  | ZD040301 |  |
| job_fml_four_nm | string | 岗位序列四级分类名称 |  | 汽车销售方向 |  |
| mng_emp_id | string | 直属主管员工编号 | 领导工号 | 81325 |  |
| mng_oprid | string | 直属主管员工账号 |  | zhangdejian |  |
| mng_emp_nm | string | 直属主管员工姓名 |  | 张德健 |  |
| dept_id | string | 部门编号 |  | MWA3061102 |  |
| dept_nm | string | 部门名称 |  | 小米之家天津市南开区大悦城店 |  |
| dept_path_id | string | 部门全路径编号 |  | \MI\MW\MW81\MW8111\MWA30611\MWA3061102 |  |
| dept_path_nm | string | 部门全路径名称 |  | \小米公司\中国区\京津分公司\汽车销售部\天津零售中心\小米之家天津市南开区大悦城店 |  |
| dept_id_lvl1 | string | 一级部门编号 |  | MW |  |
| dept_nm_lvl1 | string | 一级部门名称 |  | 中国区 |  |
| dept_id_lvl2 | string | 二级部门编号 |  | MW81 |  |
| dept_nm_lvl2 | string | 二级部门名称 |  | 京津分公司 |  |
| dept_id_lvl3 | string | 三级部门编号 |  | MW8111 |  |
| dept_nm_lvl3 | string | 三级部门名称 |  | 汽车销售部 |  |
| dept_id_lvl4 | string | 四级部门编号 |  | MWA30611 |  |
| dept_nm_lvl4 | string | 四级部门名称 |  | 天津零售中心 |  |
| dept_id_lvl5 | string | 五级部门编号 |  | MWA3061102 |  |
| dept_nm_lvl5 | string | 五级部门名称 |  | 小米之家天津市南开区大悦城店 |  |
| dept_id_lvl6 | string | 六级部门编号 |  |  |  |
| dept_nm_lvl6 | string | 六级部门名称 |  |  |  |
| new_grdt_typ_cd | string | 应届生类型代码 |  | A |  |
| new_grdt_grd_cd | string | 应届生届别代码 | 哪一届 | 2025 |  |
| new_grdt_end_dt | string | 应届生失效日期 |  |  |  |
| new_grdt_flg | int | 是否应届生 |  | 1 |  |
| fur_flg | int | 未来星标志 |  | 0 | 1: 属于未来星标识 0/-1: 非未来星标识 |
| age_y | double | 年龄（年） |  | 23.2739726027397 |  |
| wrk_age_y | double | 工龄（年） |  | 0.641095890410959 |  |
| wrk_age_mi_y | double | 司龄（年） |  | 0.641095890410959 |  |
| frs_edu_deg_cd | string | 第一学历代码（大专及以上） |  | E07 | A01: 印度HSC, A02: 印度 Diploma, A03: 印度 Pre-university/+1, A04: 印度 Bachelor, A05: 印度 Post Graduation Diploma, A06: 印度 Master, A07: 印度 PHD, A08: 印度 CA, B01: 印尼 Junior High School, B02: 印尼 Senior High School, B03: 印尼 Diploma-1, B04: 印尼 Diploma-3, B05: 印尼 Bachelor, B06: 印尼 Master, B07: 印尼 PHD, E01: 其他, E02: 高中, E03: 职高, E04: 技校, E05: 中专, E06: 大专, E07: 本科, E08: 硕士研究生, E09: 博士研究生, E10: 博士, E11: 其他, E12: 专业学位, E13: 博士后, G01: 其他 高中, G02: 其他 大学毕业文凭, G03: 其他 准学士, G04: 其他 学士, G05: 其他 硕士, G06: 其他 博士, G07: 其他 |
| frs_sch_nm | string | 第一学历学校 |  | 天津仁爱学院 |  |
| frs_mjr_nm | string | 第一学历专业 |  | 电气工程及其自动化 |  |
| frs_edu_tags | string | 第一学历标签 逗号分割 |  | 本科 |  |
| frs_sch_uni_typ | string | 第一学历学校唯一类型 |  |  |  |
| last_edu_deg_cd | string | 最终学历代码 |  | E07 | A01: 印度HSC, A02: 印度 Diploma, A03: 印度 Pre-university/+1, A04: 印度 Bachelor, A05: 印度 Post Graduation Diploma, A06: 印度 Master, A07: 印度 PHD, A08: 印度 CA, B01: 印尼 Junior High School, B02: 印尼 Senior High School, B03: 印尼 Diploma-1, B04: 印尼 Diploma-3, B05: 印尼 Bachelor, B06: 印尼 Master, B07: 印尼 PHD, E01: 其他, E02: 高中, E03: 职高, E04: 技校, E05: 中专, E06: 大专, E07: 本科, E08: 硕士研究生, E09: 博士研究生, E10: 博士, E11: 其他, E12: 专业学位, E13: 博士后, G01: 其他 高中, G02: 其他 大学毕业文凭, G03: 其他 准学士, G04: 其他 学士, G05: 其他 硕士, G06: 其他 博士, G07: 其他 |
| last_sch_nm | string | 最终学历学校 | 毕业学校 | 天津仁爱学院 |  |
| last_mjr_nm | string | 最终学历专业 | 学历背景 | 电气工程及其自动化 |  |
| last_edu_tags | string | 最终学历标签 逗号分割 |  | 本科 |  |
| last_sch_uni_typ | string | 最终学历学校唯一类型 |  |  |  |
| hi_edu_deg_cd | string | 最高学历代码，多个相同学历取最后一个 |  | E07 | A01: 印度HSC, A02: 印度 Diploma, A03: 印度 Pre-university/+1, A04: 印度 Bachelor, A05: 印度 Post Graduation Diploma, A06: 印度 Master, A07: 印度 PHD, A08: 印度 CA, B01: 印尼 Junior High School, B02: 印尼 Senior High School, B03: 印尼 Diploma-1, B04: 印尼 Diploma-3, B05: 印尼 Bachelor, B06: 印尼 Master, B07: 印尼 PHD, E01: 其他, E02: 高中, E03: 职高, E04: 技校, E05: 中专, E06: 大专, E07: 本科, E08: 硕士研究生, E09: 博士研究生, E10: 博士, E11: 其他, E12: 专业学位, E13: 博士后, G01: 其他 高中, G02: 其他 大学毕业文凭, G03: 其他 准学士, G04: 其他 学士, G05: 其他 硕士, G06: 其他 博士, G07: 其他 |
| hi_sch_nm | string | 最高学历学校 |  | 天津仁爱学院 |  |
| hi_mjr_nm | string | 最高学历专业 |  | 电气工程及其自动化 |  |
| hi_edu_tags | string | 最高学历标签 逗号分割 |  | 本科 |  |
| hi_sch_uni_typ | string | 最高学历学校唯一类型 |  |  |  |
| mng_flg | bigint | 是否管理者（即有实线汇报下属） | 是否带人 | 0 |  |
| org_mng_flg | bigint | 是否组织管理者（即是部门主管） |  | 0 |  |
| senior_mng_flg | bigint | 是否高管（即集团总办-高管组） |  | 0 |  |
| leaf_mng_flg | bigint | 是否末级部门管理者 |  | 0 |  |
| mng_lvl | bigint | 管理层级（即最高管理的部门级别） |  | -1 |  |
| mng_lvls | string | 所有管理层级 |  |  |  |
| mng_depth | bigint | 管理深度（即最深的管理部门层级） |  | -1 |  |
| s_mng_lvl | bigint | S级部门管理层级 |  | -1 |  |
| non_s_mng_lvl | bigint | 非S级部门管理层级 |  | -1 |  |
| bgt_dir_sub_emp_cnt | bigint | 预算口径-直接下属人数 |  | 0 |  |
| bgt_main_pos_dir_sub_emp_cnt | bigint | 预算口径-主岗直接下属人数 |  | 0 |  |
| bgt_conc_pos_dir_sub_emp_cnt | bigint | 预算口径-兼岗直接下属人数 |  | 0 |  |
| bgt_all_sub_emp_cnt | bigint | 预算口径-全部下属人数 |  | 0 |  |
| bgt_main_pos_all_sub_emp_cnt | bigint | 预算口径-主岗直接下属人数 |  | 0 |  |
| bgt_conc_pos_all_sub_emp_cnt | bigint | 预算口径-兼岗直接下属人数 |  | 0 |  |
| own_dir_sub_emp_cnt | bigint | 自有员工口径-直接下属人数 |  | 0 |  |
| own_main_pos_dir_sub_emp_cnt | bigint | 自有员工口径-主岗直接下属人数 |  | 0 |  |
| own_conc_pos_dir_sub_emp_cnt | bigint | 自有员工口径-兼岗直接下属人数 |  | 0 |  |
| own_all_sub_emp_cnt | bigint | 自有员工口径-全部下属人数 |  | 0 |  |
| own_main_pos_all_sub_emp_cnt | bigint | 自有员工口径-主岗直接下属人数 |  | 0 |  |
| own_conc_pos_all_sub_emp_cnt | bigint | 自有员工口径-兼岗直接下属人数 |  | 0 |  |
| dir_sub_emp_cnt | bigint | 无口径-直接下属人数 |  | 0 |  |
| main_pos_dir_sub_emp_cnt | bigint | 无口径-主岗直接下属人数 |  | 0 |  |
| conc_pos_dir_sub_emp_cnt | bigint | 无口径-兼岗直接下属人数 |  | 0 |  |
| all_sub_emp_cnt | bigint | 无口径-所有下属人数 |  | 0 |  |
| main_pos_all_sub_emp_cnt | bigint | 无口径-主岗所有下属人数 |  | 0 |  |
| conc_pos_all_sub_emp_cnt | bigint | 无口径-兼岗所有下属人数 |  | 0 |  |
| tag_dir_sub_emp_cnt | bigint | 选人标签-直接下属人数（正式+外包A） |  | 0 |  |
| max_all_sub_emp_cnt | bigint | 无口径-历史最大所有下属人数 |  | 0 |  |
| hire_pos_lvl | string | 入职职级 |  | 13 |  |
| pos_stay_days | int | 当前职级停留时长 |  | 234 |  |
| pro_cnt | bigint | 晋升次数 |  | 3 |  |
| late1_pro_dt | string | 近1次晋升日期 |  | 2025-01-01 |  |
| late2_pro_dt | string | 近2次晋升日期 |  | 2024-01-01 |  |
| late3_pro_dt | string | 近3次晋升日期 |  | 2023-01-01 |  |
| late_pfm_prd | string | 最近一次绩效期次 |  | 2025H2 |  |
| late_pfm | string | 最近一次绩效 | 绩效 | A |  |
| late_late_pfm_prd | string | 上上一次绩效期次 |  | 2026H1 |  |
| late_late_pfm | string | 上上一次绩效 |  | S |  |
| late_twi_good_flg | int | 连续高绩效标志 |  | 0 |  |
| late_twi_bb_flg | int | 连续绩优标志(两次都要有) |  | 0 |  |
| late_twi_bad_flg | int | 连续绩效无改善标志 |  | 0 |  |
| hi_pfm_flg | int | 高绩效标识(最近一次绩效) |  | 0 |  |
| lo_pfm_flg | int | 低绩效标识(最近一次绩效) |  | 0 |  |
| two_lvl_dif_flg | int | 差两档标志 |  | 0 |  |
| q_late_pfm_prd | string | 最近一次绩效期次(包含季度绩效) |  | 2025Q4 |  |
| q_late_pfm | string | 最近一次绩效(包含季度绩效) |  | A |  |
| q_late_late_pfm_prd | string | 上上一次绩效期次(包含季度绩效) |  | 2025Q3 |  |
| q_late_late_pfm | string | 上上一次绩效(包含季度绩效) |  | S |  |
| q_late_twi_good_flg | int | 连续高绩效标志(包含季度绩效) |  | 0 |  |
| q_late_twi_bb_flg | int | 连续绩优标志(两次都要有)(包含季度绩效) |  | 0 |  |
| q_late_twi_bad_flg | int | 连续绩效无改善标志(包含季度绩效) |  | 0 |  |
| q_hi_pfm_flg | int | 高绩效标识(最近一次绩效,含季度) |  | 0 |  |
| q_lo_pfm_flg | int | 低绩效标识(最近一次绩效,含季度) |  | 0 |  |
| yng_eng_flg | int | 青年工程师标识 |  | 0 |  |
| blue_flg | int | 蓝领标识 |  | 0 | 0:白领, 1:蓝领 |
| pre_tmn_flg | int | 预离职标识 |  | 0 | 1:预离职中, 0:非预离职中 |
| hig_inc_flg | int | 高薪offer标识 |  | 0 | 1:是高薪offer, 0:非高薪offer |
| ctr_prc_dt | string | 合同转正日期 |  | 2024-01-01 |  |
| ctr_end_dt | string | 合同到期日期 |  | 2027-01-01 |  |
| mi_ind_line_tag_nm | string | 小米行业线标签名称 |  | 销售 |  |

_共 140 行 × 6 列_
