# ES 字段与典型 DSL 参考手册

本文档面向按需加载：当需要”构造或修正 ES DSL”，或判断”何种查询类型适合当前条件”时参考。示例均为标准 JSON（可直接作为 search_es 的输入对象）。

## 目录

| 章节 | 内容 | 位置 |
|------|------|------|
| 快速使用指南（决策树） | 根据条件类型选择 term/match/nested/RRF/KNN | §1 |
| 统一约束 | bool 组合、.keyword 规则、size 默认值、性能建议 | §2 |
| 字段词典 | 全字段类型、示例与用法（基础信息→向量字段） | §3 |
| STAR_BACKGROUND 强制规则 | 核心要求摘要 + 替换参数示例，完整规则和模板见 dsl-star-background.md | §4 |
| 通用查询类型与模板 | 8 种查询类型的可复制 DSL 模板（term→boolean 组合） | §5 |
| 强制规则与高级用例 | 向量维度、模型规格、RRF 与 KNN 参数约束 | §6 |
| 枚举字段洞察 | 部门/岗位/岗位序列的聚合探查流程 | §7 |
| 附录：默认业务规则 | size 默认值、权限过滤、敏感数据参数 | §8 |

## 快速使用指南（决策树）
- 精确枚举/ID/短语：
  - ID/数值（emp_id、oprid、supv_level、age、work_age、company_age）→ term/terms（不加 .keyword）
  - 文本枚举或精确短语（sex_label、age_label、location_name、work_age_label、company_age_label、highest_education_name、first_education_name、position_name、real_name、position_seq、highest_education_school_name、first_education_school_name、major_names）→ term/terms（使用 .keyword）或 match_phrase（连续短语）
- 区间比较：age、work_age、company_age、supv_level → range（适度放宽边界以覆盖小数）
- 组织路径：运行时 context 提供的完整路径 → prefix；路径不完整/模糊 → match
- 模糊/全文：优先字段按意图选择（技能/经历/面评/内部履历等）→ match；短语锁定 → match_phrase
- 嵌套字段：talent_info、performance_records（双层 nested→stages）、resume_work_infos、promotion_records、report_with_review_records → nested（固定 path，内部 bool 组合）；probation_detail 为 object 不需要 nested。**注意：STAR_BACKGROUND 模板 B 使用预聚合 `_str` 字段 + `dis_max`，不走 nested 查询，见 [dsl-star-background.md](dsl-star-background.md)**
- 语义与结构混合：优先 RRF（standard 可含 nested；knn 禁止 nested；两侧关键词一致）
- 仅语义：KNN（先用 filter 收紧明确条件）
- 组合策略：把 term/range 放入 filter 提升性能；must 为必要文本匹配；should 为可扩展项。

## 统一约束（DSL Constraints）
- 使用 bool 组合逻辑。
- 文本枚举/短语类字段必须加 .keyword；keyword 类型本身无需 .keyword。
- size 默认设置为 16 以便审查（STAR_BACKGROUND 模板 A 和模板 B 均固定为 100）。
- 性能建议：term 与 range 放入 filter；避免无谓的 wildcard；should 数量适度控制。
- **STAR_STATUS 场景禁止指定 `_source`**：meego_metrics、weekly_report、ai_model_usage 等字段随 hits 自动返回，指定 `_source` 会导致数据丢失。
- **STAR_EVALUATION 场景禁止指定 `_source`**：performance_records、promotion_records、report_with_review_records等敏感字段由服务端通过 `include_sensitive_data=true` 自动补充，指定 `_source` 会导致这些字段丢失。

## 字段词典（索引 Schema 与用途）
- 基础信息
  - emp_id (keyword)：员工 ID（主键）。示例："100116"
  - oprid (keyword)：员工账号。示例："bizhuangyang"
  - real_name (text + keyword)：员工姓名（中文分词）。示例："刘畅"
  - sex_label (text + keyword)：性别（枚举：男/女）
  - age (float)：年龄；age_label (text + keyword)：年龄段（95后、00后…）
  - location_name (text + keyword)：工作地点。示例："北京"
  - last_hire_date (date)：最后入职日期（yyyy-MM-dd）
- 组织与职位
  - dept_name_path (text + keyword)：组织全路径（一级-二级-三级…）；精确路径优先 prefix，模糊用 match
  - position_name (text + keyword)：岗位名称
  - position_seq (text + keyword)：岗位序列
  - supv_level (integer)：职级（≤14 低、≤16 中低、≥17 中高、≥19 高）
  - main_leader_real_name_path (text + keyword)：汇报链（\\雷军\\…\\本人）
  - career_development_str (text)：内部任职与轮岗履历合并文本
- 资历与教育
  - work_age/company_age (float)：工龄/司龄；
  - work_age_label（text + keyword）枚举值：`1-3年/3-5年/5-10年/10年以上/应届生/其他`
  - company_age_label（text + keyword）枚举值：`入职1-3年/入职3-5年/入职1年以内/入职5-8年/入职8-10年/入职10年以上`
  - highest_education_name / first_education_name (text + keyword)：最高/第一学历（枚举）
  - highest_education_school_name / first_education_school_name (text + keyword)：最高/第一学历学校
  - school_names (text + keyword)：所有教育经历学校集合
  - major_names (text + keyword)：所有专业集合
- 简历背景与画像（需语义理解/模糊匹配）
  - tag_info_str (text) [向量：tag_info_embedding]：画像标签文本，可用于以下信息检索
    - 荣誉称号：青年工程师(青工); 黑客马拉松(黑马); 青蓝导师; 繁星计划
    - 教育经历_学校类型: 清北/C9/211/985/QS100/其他学校类型
    - 教育经历_第一(最高)学历学校类型: 清北/C9/211/985/QS100/其他学校类型
    - 海外经历检索:有海外读书经历，具体地点为新加坡。
    - 基本信息_语种:英语
    - 基本信息_过往公司:XX
    - 小语种:俄语/日语/西班牙语/...
    - 外派经历:有/无外派经历
    - 管理职能:非管理者，无直属下级，属于个人贡献者（IC）。
    - 技术成果:有发明专利，专利申请数量在1-5个之间。
  - resume_context (text) [向量：resume_context_embedding]：外部工作履历梗概，仅包含过往任职公司名及职位名（不含内部履历）
  - resume_work_info_str (text)[向量：resume_work_embedding]：外部工作经历合并文本（不含内部履历）
  - resume_work_infos (nested)：工作经历明细（company_name/job_title/job_description/start_date/end_date）
  - interview_info_str (text) [向量：interview_embedding]：面试评价合并文本
- 预聚合文本字段（写入时拼接，用于 STAR_BACKGROUND 模板 B 的 `dis_max` BM25 匹配，替代 nested 查询）
  - outstanding_achievements_str (text)：战功/外功聚合文本（所有 performance_records.stages.data.outstanding_achievements 拼接）
  - internal_contributions_str (text)：内功聚合文本（所有 performance_records.stages.data.internal_contributions 拼接）
  - promotion_str (text)：晋升记录聚合文本（所有 promotion_records.advantage 拼接）
  - review_str (text)：述职记录聚合文本（所有 report_with_review_records.advantage 拼接）
- 人才类型（nested: talent_info）
  - talent_info.talent_type (text + keyword)：人才类型（`应届生人才`=应届入职 / `非应届生人才`=社招入职），用于`STAR_TALENT`场景；用户**未区分**应届/非应届 → 两种均匹配，**明确应届** → 仅匹配`应届生人才`
  - talent_info.score (float)：人才评分，用于排序
- 项目动态（object，含 nested 子字段，随 hits 自动返回）
  - meego_metrics.recent_period：近期周期项目工作项（object）
    - time_range (keyword)：统计时间范围，格式"YYYYMMDD~YYYYMMDD"。示例："20260421~20260504"
    - total_work_items (integer)：总任务数（去重 task_id）
    - total_points (float)：总工时（人天）
    - work_item_groups (nested)：按项目分组的任务集合（每条=一个项目下的所有任务）
      - prj_id (keyword)：项目ID（聚合 key）
      - prj_nm (text + keyword)：项目名称（ik 分词）。示例："组织档案"
      - collaborators (keyword[])：该项目中的合作人姓名列表
      - req_nm (text + keyword)：需求名称（ik 分词）。示例："组织档案/AI问答/算法预研"
      - flow_nm (keyword)：工作流阶段（开发/测试/设计等）
      - task_nm (text + keyword)：子任务名称（ik 分词）
      - priority (keyword)：优先级（P0/P1/P2/P3）
      - status (keyword)：状态
      - points (float)：工时人天
      - bgn_dt (date, yyyyMMdd)：开始日期
      - end_dt (date, yyyyMMdd)：结束日期
  - meego_metrics.previous_period：上一周期项目工作项（结构同 recent_period）
  - **使用说明**：meego_metrics 为普通 object（work_item_groups 为 nested），按人名/部门等条件检索到员工后，数据随 hits 一起返回。STAR_STATUS 场景需要项目动态时，DSL 只需确保命中目标员工即可。若需按项目名/任务名全文检索，需使用 nested 查询 path `meego_metrics.recent_period.work_item_groups`。
  - meego_projects：近 2 年项目工作项汇总（object）
    - time_range (keyword)：时间范围，格式"YYYYMMDD~YYYYMMDD"。示例："20240331~20260331"
    - work_item_groups (object[])：工作项分组列表（包含进行中和已结项）
      - prj_nm (keyword)：项目名称。示例："基础薪酬管理及应用"
      - work_item_status (keyword)：工作项状态（进行中/已结项）
      - req_nm (keyword)：需求名称。示例："薪酬数据提报管理"
      - priority (keyword)：优先级（P0/P1/P2/P3）
      - task_count (integer)：任务数
    - total_work_items (integer)：工作项总数
  - **meego_metrics vs meego_projects 区别**：`meego_metrics` 按近期/上一周期两个时间窗口切分，work_item_groups 为 nested 任务级明细（含工时、日期、合作人），适用于 STAR_STATUS 场景的短期动态对比；`meego_projects` 汇总近 2 年所有项目（含已结项），按项目分组统计，适用于 STAR_BACKGROUND 场景的完整项目经历评估。两者均随 hits 自动返回，无需写入 DSL。
- 周报（nested: weekly_report → nested: work_list）
  - weekly_report[]：周报列表，每项包含一段时间范围内的多周周报
    - report_nm (keyword)：报告类型（枚举：`okr_weekly` OKR 周报 / `ipdworktimepro_wtm` IPD 工时周报）
    - time_range (keyword)：时间范围。示例："20260120~20260218"
    - work_list (nested)：各周周报内容列表
      - year (integer)：年份。示例：2026
      - week_of_year (integer)：年内第几周。示例：17
      - content (text + ik)：周报正文（Markdown 格式），包含质量安全异常、主线里程碑进展、重点项目子项进展、风险点等
  - **使用说明**：weekly_report 为 nested 类型（work_list 也是 nested），但 STAR_STATUS 场景通常按人名检索后数据随 hits 返回，无需在 DSL 中写 nested 查询。若需按周报内容全文检索（如"谁的周报提到了XX"），需使用 nested 查询 path `weekly_report.work_list`，匹配 `weekly_report.work_list.content`。
- AI 模型用量（nested: ai_model_usage）
  - ai_model_usage[]：AI 模型使用统计列表，同一时间范围可能有多条记录（按 is_mitclaw 区分渠道）
    - time_range (keyword)：统计周期，格式"YYYYMMDD~YYYYMMDD"。示例："20260421~20260504"
    - is_mitclaw (boolean)：是否龙虾用量（true=龙虾/内部 MIT 平台，false=非龙虾/外部渠道）
    - total_token_usage (long)：总 Token 消耗量（input + input_cache + output 合计）
    - total_cost_amt (float)：总成本（元）
    - token_usage (object)：Token 用量明细
      - input (long)：新输入 Token（未命中缓存）
      - input_cache (long)：缓存命中 Token
      - output (long)：输出 Token
    - token_amt (object)：费用明细（元）
      - input (float)：输入成本（元）
      - input_cache (float)：缓存成本（元）
      - output (float)：输出成本（元）
    - io_input_ratio (float)：I/O 输入占比（0~1 小数，如 0.75 表示 75%）
    - cache_hit_rate (float)：缓存命中率（0~1 小数，如 0.983 表示 98.3%）
    - mitclaw_conversation_count (integer)：龙虾（mitclaw）平台对话次数（非龙虾记录固定为 0）
    - dept_ai_avg (object)：所在一级部门近两周人均指标
      - per_capita_tokens (long)：人均 Token
      - per_capita_cost (float)：人均成本（元）
    - model_distribution (nested)：模型配比明细
      - model_name (keyword)：模型名称。示例："mimo-v2-pro-mit"
      - ratio (float)：使用占比（0~1）
      - token_usage (long)：该模型消耗 Token 数
  - **使用说明**：ai_model_usage 为 nested 类型，但 STAR_STATUS 场景通常按人名检索后数据随 hits 返回，无需在 DSL 中写 nested 查询。输出时不区分渠道，将所有记录的 total_token_usage 和 total_cost_amt 求和展示，model_distribution 合并后按 token_usage 重算全局占比降序排列，io_input_ratio 和 cache_hit_rate 按各记录 total_token_usage 加权平均后 ×100 转百分比，mitclaw_conversation_count 只取 is_mitclaw=true 记录的值。若需按 is_mitclaw 过滤或按 total_cost_amt 排序，需使用 nested 查询 path `ai_model_usage`。
- 绩效记录（nested: performance_records → nested: stages）
  - stage_name (keyword)：评价阶段（superior_evaluation 为上级评价/预测）
  - data.score (keyword)：绩效评分（S/A/B+/B/B-/C）
  - data.out_score (keyword)：外功评分
  - data.in_score (keyword)：内功评分
  - data.outstanding_achievements (text)：战功/外功项目描述
  - data.internal_contributions (text)：内功项目描述
  - data.advantage (text)：绩效优势评价
  - data.to_be_improved (text)：绩效待改进评价
  - data.collaboration_projects (keyword)：环评/协作项目
  - data.promotion_prediction (keyword)：晋升预测标签（XX年春/XX年秋/待观察/待提升）
  - data.potential_score (float)：晋升潜力分
- 晋升记录（nested: promotion_records）
  - promotion_date (date)：晋升日期
  - promotion_level (integer)：晋升目标职级
  - target_title_name (text)：晋升目标职位名称
  - composite_score (float)：晋升综合评分
  - advantage (text)：晋升优势评价（评委/述职总结的优势点）
  - to_be_improved (text)：晋升待改进评价
- 试用期转正（object: probation_detail，非 nested，随 hits 自动返回）
  - probation_date (date)：转正日期
  - composite_score (integer)：转正综合评分
  - advantage (text)：转正优势评价
  - to_be_improved (text)：转正待改进评价
- 述职/评审记录（nested: report_with_review_records）
  - review_result (keyword)：评审结果
  - discuss_result (keyword)：讨论结果
  - advantage (text)：述职优势评价
  - to_be_improved (text)：述职待改进评价
- **向量字段使用说明**：所有标注 `[向量：xxx_embedding]` 的字段均为 dims=4096 的语义向量，KNN/RRF 查询中 field 填对应 embedding 字段名，model_id 统一用 `qwen3_8b_embedding_endpoint`。根据查询意图选择最相关的 embedding 字段；背景推荐场景建议多 embedding 联合 RRF
  - 其他相关的语义向量字段（dims=4096，用于 KNN/RRF 语义检索）：
    - performance_achievements_embedding：绩效战功/外功向量
    - performance_advantage_embedding：绩效优势向量
    - performance_to_be_improved_embedding：绩效待改进向量
    - probation_advantage_embedding：转正优势向量
    - probation_to_be_improved_embedding：转正待改进向量
    - promotion_advantage_embedding：晋升优势向量
    - promotion_to_be_improved_embedding：晋升待改进向量
    - report_with_review_advantage_embedding：述职优势向量
    - report_with_review_to_be_improved_embedding：述职待改进向量

## 【背景推荐】STAR_BACKGROUND DSL 构造强制规则（最高优先级，违反视为构造失败）

> **⚠️ STAR_BACKGROUND 场景的 DSL 构造必须遵循 [dsl-star-background.md](dsl-star-background.md) 的固定模板和强制规则，不得参考下方"查询类型与模板"章节中的通用示例推导字段组合或权重。**

核心要求（完整规则、9 字段清单、权重定义、模板 DSL 均在 [dsl-star-background.md](dsl-star-background.md) 中）：
- 模板 B 使用 `dis_max`（非 `bool.should`），9 个 BM25 字段全覆盖，权重固定不可改
- 模板 B 包含 3 路 KNN retriever，缺少任何一路即为构造失败
- filter 放硬性条件，所有 retriever 共用相同 filter
- `include_sensitive_data` 必须传 `true`
- 构造后自检：`dis_max.queries` 数量 = 9，权重正确

### 【背景推荐】完整示例（多维度 RRF + 全字段覆盖）

背景推荐场景需要综合检索 内部履历+外部履历 多源数据。以下是典型查询模式：

**示例 A：最近在做培训数字化产品的人有哪些**

> **⚠️ STAR_BACKGROUND 场景必须使用 [dsl-star-background.md](dsl-star-background.md) 的固定模板构造 DSL，禁止自行拼装。**

本例属于"近期动态"，选择模板 A（仅查绩效+内部履历），替换参数如下：

| 占位符 | 替换值 |
|-------|--------|
| `{关键词}` | `培训 数字化 学习平台 课程系统 在线培训 培训产品 课程管理` |
| `{filter条件}` | 无硬性条件，去掉 filter |

meego_projects 随 hits 自动返回，无需写入 DSL。

**示例 B：人力资源部有过IBM等咨询公司背景且薪酬数字化经验最丰富的人**

> **⚠️ STAR_BACKGROUND 场景必须使用 [dsl-star-background.md](dsl-star-background.md) 的固定模板构造 DSL，禁止自行拼装。**

本例属于"背景/经验筛选"，选择模板 B（`dis_max` 扁平结构），替换参数如下：

| 占位符 | 替换值 |
|-------|--------|
| `{领域关键词}` | `薪酬 数字化 HR系统 人力资源信息化 IBM 埃森哲 德勤 麦肯锡` |
| `{filter条件}` | `"match_phrase": { "dept_name_path": "人力资源部" }` |
| `{语义文本}` | `IBM 埃森哲 咨询公司 薪酬数字化 HR系统` |

权重由模板固定：战功/内功=10.0，晋升/述职/转正=4.0，简历概要/简历工作经历/画像/内部履历=3.0。不得修改。

---

## 通用 查询类型与模板（可直接复制）

> **⚠️ 以下通用示例仅适用于非 STAR_BACKGROUND 场景。STAR_BACKGROUND 必须使用上方【背景推荐】章节的规则和模板。**

### 1) 精确匹配：term/terms 与短语匹配：match_phrase
```json
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "location_name.keyword": "北京" } },
        { "term": { "highest_education_name.keyword": "硕士" } },
        { "term": { "supv_level": 18 } },
        { "match_phrase": { "resume_work_info_str": "美团" } }
      ]
    }
  },
  "size": 100
}
```

### 2) 范围查询：range
```json
{ "query": { "range": { "work_age": { "gte": 4, "lte": 11 } } }, "size": 100 }
```
```json
{ "query": { "range": { "age": { "gte": 24, "lte": 41 } } }, "size": 100 }
```

### 3) 组织路径：prefix（运行时 context 有完整路径时）
```json
{
  "query": {
    "prefix": { "dept_name_path.keyword": { "value": "小米公司-人力资源部-人力数字化产品部" } }
  },
  "size": 100
}
```

### 4) 模糊/全文：match（字段优先清单）
- 技能/经历：performance_records.stages.data.outstanding_achievements、resume_context、resume_work_info_str、resume_work_infos.job_description（STAR_BACKGROUND 模板 B 用 `outstanding_achievements_str`、`internal_contributions_str` 替代 nested 字段）
- 优势/能力：performance_records.stages.data.advantage、promotion_records.advantage、probation_detail.advantage、report_with_review_records.advantage（STAR_BACKGROUND 模板 B 用 `promotion_str`、`review_str` 替代 nested 字段）
- 待改进：performance_records.stages.data.to_be_improved、promotion_records.to_be_improved、probation_detail.to_be_improved、report_with_review_records.to_be_improved
- 汇报层级：main_leader_real_name_path
- 标签/集团奖项：tag_info_str
- 面试评价：interview_info_str
- 内部履历：career_development_str
```json
{
  "query": {
    "bool": {
      "should": [
        { "match": { "position_name": "后端开发" } },
        { "match": { "resume_context": "Java" } },
        {
          "nested": {
            "path": "performance_records.stages",
            "query": {
              "match": {
                "performance_records.stages.data.outstanding_achievements": "Java"
              }
            }
          }
        }
      ]
    }
  },
  "size": 100
}
```

### 5) 嵌套：nested（固定 path，内部 bool 组合）
- 人才类型（terms/term），默认按 talent_info.score 降序排序
- "人才"等价词（触发 talent_info 查询）：优秀员工、明星员工、标杆、领军、顶梁柱、杰出贡献者、核心骨干、关键人才、业务楷模、榜样员工、引领者、带头人、中坚、中流砥柱、高潜、顶尖、卓越、杰出、主力、扛把子
- "人才"非等价词（不触发 talent_info 查询）：典范、王牌、功勋、灵魂
```json
// 未区分应届/非应届 → terms 匹配两种类型
{
  "query": {
    "nested": {
      "path": "talent_info",
      "query": {
        "terms": { "talent_info.talent_type.keyword": ["应届生人才", "非应届生人才"] }
      }
    }
  },
  "sort": [
    { "_score": { "order": "desc" } },
    { "talent_info.score": { "order": "desc", "nested": { "path": "talent_info" }, "mode": "max" } }
  ],
  "size": 100
}
// 指定应届生人才 → term 精确匹配单一类型
{
  "query": {
    "nested": {
      "path": "talent_info",
      "query": {
        "term": { "talent_info.talent_type.keyword": "应届生人才" }
      }
    }
  },
  "sort": [
    { "_score": { "order": "desc" } },
    { "talent_info.score": { "order": "desc", "nested": { "path": "talent_info" }, "mode": "max" } }
  ],
  "size": 100
}
```
- 绩效评分（锁定 superior_evaluation）
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "nested": {
            "path": "performance_records",
            "query": {
              "nested": {
                "path": "performance_records.stages",
                "query": {
                  "bool": {
                    "must": [
                      { "term": { "performance_records.stages.stage_name": "superior_evaluation" } },
                      { "terms": { "performance_records.stages.data.score": ["S", "A", "B+"] } }
                    ]
                  }
                }
              }
            }
          }
        }
      ]
    }
  },
  "size": 100
}
```
- 晋升预测 + 按潜力分排序（nested sort）
```json
{
  "query": {
    "nested": {
      "path": "performance_records.stages",
      "query": {
        "bool": {
          "must": [
            { "term": { "performance_records.stages.stage_name": "superior_evaluation" } },
            { "term": { "performance_records.stages.data.promotion_prediction": "2026年春" } }
          ]
        }
      },
      "inner_hits": { "size": 1, "sort": [ { "performance_records.stages.data.potential_score": { "order": "desc" } } ] }
    }
  },
  "sort": [
    {
      "performance_records.stages.data.potential_score": {
        "order": "desc",
        "mode": "max",
        "nested": {
          "path": "performance_records.stages",
          "filter": {
            "bool": {
              "must": [
                { "term": { "performance_records.stages.stage_name": "superior_evaluation" } },
                { "term": { "performance_records.stages.data.promotion_prediction": "2026年春" } }
              ]
            }
          }
        }
      }
    }
  ],
  "size": 100
}
```

### 6) RRF（语义 + 结构混合）
- 关键词两侧一致；standard 可含 nested；knn 禁 nested；统一 model_id: qwen3_8b_embedding_endpoint
```json
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "bool": {
                "should": [
                  {
                    "nested": {
                      "path": "performance_records.stages",
                      "query": {
                        "match": { "performance_records.stages.data.outstanding_achievements": { "query": "AI 测试 人工智能测试 大模型测试 机器学习测试 深度学习测试" } }
                      }
                    }
                  },
                  {
                    "match": { "resume_work_info_str": { "query": "大模型 算法 深度学习 NLP 人工智能 GPT LLM" } }
                  }
                ],
                "filter": [ { "prefix": { "dept_name_path.keyword": "小米公司-集团信息技术部" } } ]
              }
            }
          }
        },
        {
          "knn": {
            "field": "resume_context_embedding",
            "query_vector_builder": {
              "text_embedding": { "model_id": "qwen3_8b_embedding_endpoint", "model_text": "大模型 算法 深度学习 NLP 人工智能 GPT LLM" }
            },
            "k": 50,
            "num_candidates": 1000,
            "filter": { "prefix": { "dept_name_path.keyword": "小米公司-集团信息技术部" } }
          }
        }
      ],
      "rank_window_size": 100,
      "rank_constant": 20
    }
  },
  "size": 100
}
```

### 7) KNN（仅语义）
```json
{
  "knn": {
    "field": "resume_context_embedding",
    "query_vector_builder": {
      "text_embedding": { "model_id": "qwen3_8b_embedding_endpoint", "model_text": "具备深度学习和NLP大模型经验的算法专家" }
    },
    "k": 50,
    "num_candidates": 1000
  },
  "size": 100
}
```

### 8) Boolean 组合
- filter：枚举、ID、精确数值（location_name、sex_label、supv_level 等）
- must：必要文本匹配
- should：可扩展项

## 强制规则与高级用例
- resume_work_infos：查询特定公司/职位/职责时，必须在 nested 中包含 inner_hits，以便下游直接获取命中的经历段。
```json
{
  "query": {
    "nested": {
      "path": "resume_work_infos",
      "query": {
        "bool": {
          "must": [
            { "match": { "resume_work_infos.company_name": "字节跳动" } },
            { "match": { "resume_work_infos.job_description": "大模型" } }
          ]
        }
      },
      "inner_hits": {
        "name": "target_work_experience",
        "_source": ["resume_work_infos.company_name", "resume_work_infos.job_title", "resume_work_infos.job_description"],
        "size": 1
      }
    }
  },
  "size": 100
}
```

- 高级多字段混合检索（STAR_EVALUATION 场景示例，非 STAR_BACKGROUND）：nested 的 boost 必须在 nested 对象内部（不能与 nested 同级）；nested 必须包含 path 与 query。
```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "real_name.keyword": "张三" } }
      ],
      "should": [
        {
          "nested": {
            "path": "performance_records",
            "query": {
              "nested": {
                "path": "performance_records.stages",
                "query": {
                  "bool": {
                    "should": [
                      { "match": { "performance_records.stages.data.outstanding_achievements": "项目管理 团队协作" } },
                      { "match": { "performance_records.stages.data.advantage": "项目管理 团队协作" } }
                    ]
                  }
                }
              }
            },
            "boost": 3.0
          }
        },
        {
          "nested": {
            "path": "promotion_records",
            "query": {
              "match": { "promotion_records.advantage": "项目管理 团队协作" }
            },
            "boost": 2.0
          }
        }
      ]
    }
  },
  "size": 16
}
```

## 枚举字段洞察（构造 DSL 前置步骤）

涉及 `部门`（dept_name_path）、`岗位`（position_name）、`岗位序列`（position_seq）时，**必须先执行聚合查询获取精确检索值**，再用于 DSL 的 terms 过滤。

- **触发条件**：查询拆解条件涉及上述三个枚举字段
- **输出**：每字段一组推荐检索值（≤10 个），用于 `terms` + `.keyword` 过滤
- **详细流程**（关键词提取 → ES 聚合 → 精确值提取 → 输出）：参考 [references/es/field-insight.md](field-insight.md)

## 附录：默认业务规则
- 当用户询问“我团队/我部门”等问题时，无需额外部门检索；默认认为检索到的数据属于用户的团队与部门。
