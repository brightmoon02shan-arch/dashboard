# STAR_BACKGROUND DSL 模板

STAR_BACKGROUND 场景的 DSL 构造必须使用本文件中的模板，仅替换关键词和 filter 条件，不得自行设计字段组合或权重。

---

## 一、选择模板

| 判断条件 | 选择 | 说明 |
|---------|------|------|
| 用户问的是"最近/近期在做什么"、"目前参与什么项目"等**近期动态** | **模板 A** | 仅查时效字段（绩效+内部履历），不需要 RRF 和 KNN |
| 用户问的是"有XX背景/经验/技能的人"、"做过XX的人"等**背景/经验筛选** | **模板 B** | 全字段覆盖 + RRF 多路召回 |
| 不确定 | **模板 B** | 默认走全覆盖，宁可多查不可漏查 |

---

## 二、构造强制规则

1. **禁止使用 `"field^boost"` 语法**
2. **权重固定不得修改**：战功/内功=10.0，晋升/述职/转正=4.0，其余=3.0
3. **字段不得省略**：模板 B 的 `dis_max.queries` 必须覆盖全部 9 个字段：`outstanding_achievements_str`、`internal_contributions_str`、`promotion_str`、`review_str`、`probation_detail.advantage`、`career_development_str`、`resume_context`、`resume_work_info_str`、`tag_info_str`
4. **模板 B 使用 `dis_max`**：不使用 `bool.should`，不使用 nested 查询。所有 BM25 匹配通过顶层 `_str` 字段完成
5. **KNN retriever 语义召回**：模板 B 默认使用 3 路 KNN（`resume_context_embedding` + `resume_work_embedding` + `performance_advantage_embedding`），可根据查询侧重调整常用组合：
   - 内部能力为主：`performance_achievements_embedding` + `performance_advantage_embedding`
   - 外部背景为主：`resume_context_embedding` + `resume_work_embedding`
   - 综合背景：`resume_context_embedding` + `performance_advantage_embedding` + `tag_info_embedding`
6. **filter 放硬性条件**：部门/职级/工作地等精确条件放 filter，所有 retriever（standard + 3 路 knn）共用相同 filter
7. **include_sensitive_data**：必须传 `true`，以获取晋升评分/日期、绩效评分、述职评分等补充数据
8. **构造后自检**：确认 `dis_max.queries` 数量 = 9，权重正确，KNN = 3 路。不满足则补全后再调用 es_query

---

## 三、模板 A：近期动态查询

适用场景：查特定人或团队的近期项目动态、当前工作内容。

仅查绩效（战功+内功）和内部履历。`meego_projects` 随 hits 自动返回，无需写入 DSL。

**替换说明**：将 `{关键词}` 替换为用户问题的关键词及同/近义词展开，将 `{filter条件}` 替换为部门/职级等硬性条件（无硬性条件则去掉 filter）。

```json
{
  "query": {
    "bool": {
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
                      { "match": { "performance_records.stages.data.outstanding_achievements": "{关键词}" } },
                      { "match": { "performance_records.stages.data.internal_contributions": "{关键词}" } }
                    ]
                  }
                }
              }
            },
            "boost": 10.0
          }
        },
        { "match": { "career_development_str": { "query": "{关键词}", "boost": 3.0 } } }
      ],
      "filter": [ {filter条件} ],
      "minimum_should_match": 1
    }
  },
  "size": 100
}
```

---

## 四、模板 B：背景/经验筛选查询（全字段 RRF）

适用场景：按背景、经验、技能筛选候选人。**这是最常用的模板。**

### 9 个 BM25 字段

模板 B 通过顶层预聚合 `_str` 字段进行 BM25 匹配，消除所有 nested 查询。以下 4 个字段需在**数据写入管道**中聚合生成（写入时拼接，非 ES copy_to），加上已有的 5 个字段共 9 个 BM25 字段：

| 新增字段 | 类型 | 数据来源 | 对应权重 |
|---------|------|---------|---------|
| `outstanding_achievements_str` | text | 所有 `performance_records.stages.data.outstanding_achievements` 拼接 | 10.0 |
| `internal_contributions_str` | text | 所有 `performance_records.stages.data.internal_contributions` 拼接 | 10.0 |
| `promotion_str` | text | 所有 `promotion_records.advantage` 拼接 | 4.0 |
| `review_str` | text | 所有 `report_with_review_records.advantage` 拼接 | 4.0 |

已有可直接使用的字段：`resume_context`(3.0)、`resume_work_info_str`(3.0)、`tag_info_str`(3.0)、`career_development_str`(3.0)、`probation_detail.advantage`(4.0)。

### 替换说明

- `{领域关键词}`：用户问题的核心领域关键词及同/近义词（**适当扩展，总数量控制在 5-8 个之间**，如"数字人 虚拟人 Avatar 3D建模 虚拟形象"）。若用户指定了公司名，将公司关键词一并合入（如"数字人 虚拟人 Avatar 百度 度小满"）。公司名会同时送入所有 9 个字段匹配，但因 `dis_max` 取最高分子句 + `tie_breaker` 加权，真正命中公司名的字段（`resume_context`、`resume_work_info_str`）会获得主导得分，其他字段未命中不会产生噪声
- `{filter条件}`：替换为完整的 JSON filter 对象。standard 的 filter 是数组，knn 的 filter 是对象，替换后效果如下：
  - standard: `"filter": [ { "prefix": { "dept_name_path.keyword": { "value": "小米公司-信息部" } } } ]`
  - knn: `"filter": { "prefix": { "dept_name_path.keyword": { "value": "小米公司-信息部" } } }`
- `{语义文本}`：KNN 向量检索的自然语言描述

### 模板 DSL

```json
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "bool": {
                "must": {
                  "dis_max": {
                    "queries": [
                      { "match": { "outstanding_achievements_str": { "query": "{领域关键词}", "boost": 10.0 } } },
                      { "match": { "internal_contributions_str": { "query": "{领域关键词}", "boost": 10.0 } } },
                      { "match": { "promotion_str": { "query": "{领域关键词}", "boost": 4.0 } } },
                      { "match": { "review_str": { "query": "{领域关键词}", "boost": 4.0 } } },
                      { "match": { "probation_detail.advantage": { "query": "{领域关键词}", "boost": 4.0 } } },
                      { "match": { "resume_context": { "query": "{领域关键词}", "boost": 3.0 } } },
                      { "match": { "resume_work_info_str": { "query": "{领域关键词}", "boost": 3.0 } } },
                      { "match": { "tag_info_str": { "query": "{领域关键词}", "boost": 3.0 } } },
                      { "match": { "career_development_str": { "query": "{领域关键词}", "boost": 3.0 } } }
                    ],
                    "tie_breaker": 0.3
                  }
                },
                "filter": [
                  {filter条件}
                ]
              }
            }
          }
        },
        // ⚠️ 以下 3 路 KNN retriever 是模板 B 的必要组成部分
        // 缺少任何一路即为构造失败（必须 = 3 个 knn 对象）
        {
          "knn": {
            "field": "performance_advantage_embedding",
            "query_vector_builder": {
              "text_embedding": { "model_id": "qwen3_8b_embedding_endpoint", "model_text": "{语义文本}" }
            },
            "k": 50, "num_candidates": 1000,
            "filter": {filter条件}
          }
        },
        {
          "knn": {
            "field": "resume_context_embedding",
            "query_vector_builder": {
              "text_embedding": { "model_id": "qwen3_8b_embedding_endpoint", "model_text": "{语义文本}" }
            },
            "k": 50, "num_candidates": 1000,
            "filter": {filter条件}
          }
        },
        {
          "knn": {
            "field": "resume_work_embedding",
            "query_vector_builder": {
              "text_embedding": { "model_id": "qwen3_8b_embedding_endpoint", "model_text": "{语义文本}" }
            },
            "k": 50, "num_candidates": 1000,
            "filter": {filter条件}
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

---

## 五、反模式自检（构造 DSL 后对照此表，命中任何一行则必须修正）

| 正确做法 | 错误模式 | 为什么错 |
|---------|---------|---------|
| 严格使用模板原文，只替换 `{关键词}` 和 `{filter条件}` 占位符 | 自行设计结构（如 `multi_match`、`bool.must` + `bool.should` 混合等） | 不是模板 A 也不是模板 B，`field^boost` 语法被禁止 |
| 必须包含全部 9 个 BM25 字段（战功/内功/晋升/述职/转正/简历/画像/内部履历），逐个核对 | `dis_max.queries` 少于 9 个字段 | 违反字段全覆盖规则 |
| 使用 `outstanding_achievements_str`/`internal_contributions_str` 等顶层字段 | 模板 B 使用 nested 查询 performance_records | 模板 B 通过预聚合 `_str` 字段消除了 nested |
| 模板 B 的 3 个 KNN retriever 已覆盖，BM25 的 `dis_max` 只查文本字段（`_str` 后缀）| 对 embedding 字段使用 `match`/`term` 查询 | embedding 字段（`*_embedding`）是向量类型，只能用 `knn` 查询 |
| 必须包含完整 RRF 结构：`rank_window_size: 100`、`rank_constant: 20`、3 个 KNN retriever | 模板 B 缺少 `retriever.rrf` 或 KNN 部分 | 模板 B 是 RRF 多路召回（1 个 standard + 3 个 knn），缺失任何一路即为构造失败 |
| `"size": 100` 放在与 `"retriever"` 同级的最外层 | `"size"` 放在 `standard` retriever 内部 | size 是顶层参数，不属于 retriever 内部 |
