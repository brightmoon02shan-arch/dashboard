---
name: routing-es
description: >
  ES 问人通道场景路由。外层 SKILL.md 判定进入问人通道后，
  由本文件完成 5+1 意图识别（STAR_EVALUATION / STAR_STATUS / STAR_BACKGROUND / STAR_TALENT / STAR_TALENT_HIPO / OUT_OF_SCOPE）、
  短路判定和下游实现文件分发。
  当用户问题涉及以下场景时进入本路由：
  (1) 员工个体评价：面评/绩效/360/晋升评价、优缺点分析、多人对比评价
  (2) 员工状态监测：近期工作状态、项目动态、离职倾向/稳定性、最近在做什么
  (3) 员工背景筛查：学历/履历/行业经验/技能/语言/认证/项目经历等硬性条件筛选
  (4) 人才识别：明星/顶尖/标杆/领军/骨干/关键人才识别
  (5) 高潜人才识别：高潜/核心高潜/潜力员工识别（三阶段混合流程）
  触发短语："XX表现怎么样"、"XX的优缺点"、"大家觉得XX如何"、
  "XX最近状态怎么样"、"XX最近在做什么"、"XX是不是要离职"、
  "谁有XX经验/背景"、"有XX行业经历的人"、"谁会说日语"、
  "明星员工有谁"、"谁是高潜"、"团队里谁最有潜力"等。
---

# ES 通道意图识别与场景路由

> **职责**：外层 SKILL.md 判定进入 ES 通道后，由本文件完成 4+1 意图识别、短路判定、下游分发。
> 意图识别在 Thought 中完成，识别结果决定后续执行路径。

---

## 一、意图判定步骤

在 Thought 中按以下步骤推理（禁止引用 ES 字段英文名与 DSL）：

1. **先排除 OUT_OF_SCOPE**：检查是否违反业务规则（聚合统计、超出范围、被评价人为"我"等）
2. **按核心分类原则判定最匹配的单一意图**
3. **简要说明分类理由**（边界模糊时参考对应 `references/es/intent-*.md` 中的 few-shot 与易混淆案例）
4. **按短路规则决定下一步动作**

---

## 二、ES 通道意图总览

| # | 意图标识 | 中文名称 | 一句话描述 |
|---|---------|---------|-----------|
| 1 | `STAR_EVALUATION` | 员工个体评价 | 基于面评/绩效/360等数据对具体员工进行主观定性评价 |
| 2 | `STAR_STATUS` | 员工状态监测 | 基于工作行为数据/项目动态归纳具体员工的近期工作状态、表现、以及参与项目 |
| 3 | `STAR_BACKGROUND` | 员工背景筛查 | 按硬性资质条件筛选满足特定背景的目标人选 |
| 4 | `STAR_TALENT` | 人才识别 | 基于综合表现识别团队中的明星/顶尖/领军/标杆人才（ES 检索流程） |
| 5 | `STAR_TALENT_HIPO` | 高潜人才识别 | 基于绩效×年龄分位矩阵识别高潜/核心高潜员工（SQL+ES 混合流程）⚠️ 豁免 Route-Lock |
| 6 | `OUT_OF_SCOPE` | 业务范畴外 | 不属于 5 大明星场景的所有问题 |

---

## 三、核心分类原则

1. **只识别 5 大明星场景**：不属于 5 大场景的一律归为 OUT_OF_SCOPE（包括通用基础信息查询、聚合统计分析）
2. **先排除 OUT_OF_SCOPE**：检查是否违反业务规则（聚合统计、超出范围等）
3. **时间暗示区分 EVALUATION vs STATUS**：含"最近/近期/这季度"等时间词 → STATUS；无时间暗示的主观评价 → EVALUATION
4. **个体 vs 群体**：针对具体个人的评价 → EVALUATION/STATUS；针对群体筛选 → BACKGROUND/TALENT/TALENT_HIPO
5. **硬性条件 vs 软性标准**：客观可验证的背景条件 → BACKGROUND；基于表现/潜力的主观标准 → TALENT/TALENT_HIPO
6. **TALENT vs TALENT_HIPO**：含"高潜/核心高潜/潜力"触发词 → STAR_TALENT_HIPO；含"明星/顶尖/领军/标杆/骨干"等触发词 → STAR_TALENT。两类同时出现时优先 STAR_TALENT_HIPO

---

## 四、短路规则与下游分发

| 意图 | 处置 | 下游路径 |
|------|------|---------|
| `OUT_OF_SCOPE` | **立即停止 ES 流程** | 不进入检索，直接读 `references/output/output-out-of-scope.md` 输出引导话术 |
| `STAR_EVALUATION` | **跳过查询拆解** | → `references/es/es-talent-query.md`（编排）→ `references/es/es-retrieval.md` → `references/output/output-star-evaluation.md` |
| `STAR_STATUS` | **跳过查询拆解** | → `references/es/es-talent-query.md`（编排）→ `references/es/es-retrieval.md` → `references/output/output-star-status.md` |
| `STAR_BACKGROUND` | **进入查询拆解** | → `references/es/es-talent-query.md`（拆解+编排）→ `references/es/es-retrieval.md` + `references/es/dsl-star-background.md` → `references/output/output-star-background.md` |
| `STAR_TALENT` | **进入查询拆解** | → `references/es/es-talent-query.md`（拆解+编排）→ `references/es/es-retrieval.md` → `references/output/output-star-talent.md` |
| `STAR_TALENT_HIPO` | **独立混合流程（SQL+ES）** | → `references/es/talent-hipo-query.md`（编排）→ `references/output/output-talent-hipo.md` ⚠️ 豁免 Route-Lock |

---

## 五、各意图详细定义

### STAR_EVALUATION — 员工个体评价

基于面评/绩效/360/晋升/述职/奖项等数据对「具体员工」进行主观定性评价。
典型范式：【泛指评价人】觉得【具体员工姓名】怎么样？

- **红线规则**：被评价人必须是具体员工姓名，不能是"我/本人" → 违反即判 OUT_OF_SCOPE
- **评价主语**：可以是泛指/代词（大家/主管/下属/同事），也可以是具体人名（如"张三觉得李四怎么样"——以李四为查询对象，尽力从评价数据中提取与张三相关的信息）
- **多人对比**：允许多人对比评价（如"张三和李四谁表现更好"），分别查询后对比输出
- **合法视角**：他人评价、指定评价人评价（张三觉得李四怎么样）、被动评价、综合评价、多人对比（张三和李四谁更强）
- **判断要点**：通常不含时间暗示；涉及主观判断词（怎么样、优缺点、评价如何、强项）
- **vs STATUS**：不强调"最近/近期"，强调已有评价数据
- **vs OUT_OF_SCOPE**：客观事实查询或违反红线规则 → OUT_OF_SCOPE

### STAR_STATUS — 员工状态监测

基于 OKR/项目负载/代码产出/项目动态等行为数据，并结合考勤趋势信号（如工时变化、请假频次波动）对「具体员工」进行近期工作状态综合归纳。
典型范式：【具体员工】最近的状态怎么样？/ 【具体员工】最近在做什么？/ 【具体员工】近期项目有哪些？

- **多人对比**：允许多人状态对比（如"张三和李四最近谁更忙"），分别查询后对比输出
- **离职倾向**：允许离职倾向/稳定性问询（如"XX是不是要离职"、"XX最近状态是否异常"），基于考勤/绩效/行为等数据信号综合分析，尽力回答；若数据不足以判断则如实告知
- **判断要点**：通常含时间暗示（最近/近期/这季度）；关注状态变化、行为表现；离职/稳定性/异常状态类问询也归入本场景
- **vs EVALUATION**：聚焦近期工作状态而非整体能力评价
- **vs OUT_OF_SCOPE**：关注状态变化而非静态基础信息

### STAR_BACKGROUND — 员工背景筛查

按硬性资质条件（学历/履历/行业经验/技能/认证/语言/项目经历/人才标签）筛选满足特定背景的目标人选。
典型范式：【团队/部门】里，谁有【公司背景/院校/行业经验/技能】？

- **判断要点**：面向群体；硬性筛选条件；询问词"谁有/哪些人/谁符合"
- **常用维度**：语言能力、教育背景、留学经历、公司背景、行业经验、项目经历、年龄/职级/司龄
- **vs TALENT**：基于客观背景条件而非主观潜力/表现
- **vs OUT_OF_SCOPE**：要求列出具体人员而非统计数字

### STAR_TALENT — 人才识别

识别团队中的明星/标杆/领军/顶尖/骨干人才。
典型范式：【团队/部门】里，哪些人是【明星/顶尖/领军】员工？

- **判断要点**：使用人才识别词（明星/顶尖/领军/标杆/骨干/关键人才/杰出）；比较性词语（最/Top/谁最强）；基于表现而非仅背景
- **人才标签**：顶尖人才、领军人才
- **vs BACKGROUND**：基于表现/潜力评价而非仅背景条件
- **vs EVALUATION**：针对群体识别而非个体评价
- **vs TALENT_HIPO**：不含"高潜/潜力"等高潜专属词

### STAR_TALENT_HIPO — 高潜人才识别

基于绩效等级×年龄分位矩阵，识别团队中的高潜/核心高潜/潜力关注员工。采用 SQL+ES 三阶段混合流程。
典型范式：【团队/部门】里，谁是高潜员工？/ 高潜有谁？/ 团队里谁最有潜力？

- **触发词**：高潜、核心高潜、潜力、高潜员工、高潜有谁
- **判断要点**：明确使用"高潜/潜力"等词汇；关注成长潜力而非已有成就；面向群体识别
- **vs STAR_TALENT**：TALENT 侧重"明星/顶尖/领军"等已有成就标识，TALENT_HIPO 侧重"高潜/潜力"等成长性标识
- **vs BACKGROUND**：基于绩效+潜力评价而非仅背景条件
- **⚠️ 特殊规则**：本意图豁免 Route-Lock，允许在同一轮中同时使用 sql_query 和 es_query

### OUT_OF_SCOPE — 业务范畴外

不属于 4 大明星场景的所有问题，直接输出引导话术。子类别：

| 子类别 | 说明 |
|-------|------|
| 通用基础信息查询 | 工号/姓名/职级/部门/工作地点等客观档案信息 |
| 聚合统计分析 | 人数/比例/平均值/分布/排名等量化统计 |
| 业务无关 | 闲聊、个人隐私、产品推荐、行政事务 |
| 违反业务规则 | 被评价人为"我"、薪酬查询 |
| 超出能力范围 | 主观无法量化（最努力/最卷） |
| 攻击性内容 | 辱骂、攻击、骚扰 |

### 参考文档：few-shot 与易混淆案例

> **按需加载**：仅在意图分类存在疑义或边界模糊时读取对应文件，正常可明确分类的查询无需加载。

| 参考文件 | 读取时机 |
|---------|---------|
| [references/es/intent-star-evaluation.md](references/es/intent-star-evaluation.md) | 无法判断是 EVALUATION 还是 STATUS 时；涉及指定评价人或多人对比的边界判断时 |
| [references/es/intent-star-status.md](references/es/intent-star-status.md) | 无法判断是 STATUS 还是 EVALUATION 时；不确定"近期行为"与"基础信息查询"的界限时 |
| [references/es/intent-star-background.md](references/es/intent-star-background.md) | 无法判断是 BACKGROUND 还是 TALENT 时；不确定"背景条件"与"能力评价"的界限时 |
| [references/es/intent-star-talent.md](references/es/intent-star-talent.md) | 无法判断是 TALENT 还是 BACKGROUND / EVALUATION 时 |
| [references/es/intent-out-of-scope.md](references/es/intent-out-of-scope.md) | 不确定是否应归入 OUT_OF_SCOPE 时；需区分基础查询/聚合统计与 4 大场景的边界时 |

---

## 六、错误与歧义处理

- 用户问题同时符合多个意图 → 选择最匹配的单一意图
- 多人对比评价 → 按主题归入 STAR_EVALUATION 或 STAR_STATUS
- 离职倾向/稳定性问询 → 归入 STAR_STATUS
- 通用基础信息查询（工号、职级、部门等客观事实）→ OUT_OF_SCOPE
- 聚合统计分析（人数、比例、分布等量化统计）→ OUT_OF_SCOPE
- 待确认项非空时，es-retrieval 首轮采用保守检索获取画像依据
- es-retrieval 无法合成有效 DSL 时，可回退调整查询拆解的覆盖面后重试

---

## 七、技能清单

- 意图确认后，将识别结果传递给 `references/es/es-talent-query.md` 执行后续编排
- `references/es/es-retrieval.md`（Pipeline 检索 + DSL 构造 + 质量门）
- `references/output/output-format.md`（场景化输出）
