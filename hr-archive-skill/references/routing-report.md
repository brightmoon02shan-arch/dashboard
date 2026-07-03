---
name: routing-report
description: >
  报告通道场景路由。外层 SKILL.md 判定进入报告通道后，
  由本文件完成报告类型识别（ORG_HEALTH 组织健康度报告 / COST_REPORT 成本报告 /
  TERMINATION_REPORT 离职报告 / ABNORMAL_STATUS_REPORT 休假关注名单/ ONBOARDING_REPORT 入职报告/ AI_COST_REPORT AI赋能人效分析报告/ ORG_ARCHITECTURE_REPORT 组织架构报告）、
  drill-down 层级人员明细查询，以及下游文件分发。
  当用户问题命中以下关键词时进入本路由：
  (1) 组织健康度报告：组织健康度、组织诊断、组织架构分析、组织健康、管理宽幅、管理配比、组织报告
  (2) 成本报告：成本报告、人力成本、用人成本、成本分析、预算使用率、人均成本、成本结构、全年预测、成本预测
  (3) 离职报告：离职报告、离职分析、人员离职分析、离职率报告、人员流失分析、主动离职分析、绩优流失、离职诊断
  (4) 休假关注名单：特殊休假、休假情况
  (5) 入职报告：入职报告、入职分析、新人入职、入职画像、入职洞察、新人留存、新人分析、入职情况分析、人员入职分析、新人画像分析
  (6) 层级 drill-down：L+数字（L1-L8）、"层级"+"人员/明细/汇报链"、"第N层有哪些人"
  (7) AI赋能人效分析报告：AI人效、AI赋能、AI投入、AI成本对比人力、Token成本分析、AI渗透率、AI成本报告、人效分析报告、AI/人力比、Token/人力、AI成本增长、AI使用分析、AI使用场景、Coding占比
  (8) 层级 drill-down：L+数字（L1-L8）、"层级"+"人员/明细/汇报链"、"第N层有哪些人"
  (9) 组织架构
  触发短语："XX的组织健康度"、"管理宽幅分布"、"成本报告"、"人均成本"、
  "XX部门离职报告"、"离职分析"、"绩优流失"、
  "XX部门的特殊休假"、"XX部门的休假情况"、"高潜的休假情况"、"管理者的休假情况"、"17~19级的休假情况"、
  "生成AI人效分析报告"、"全公司AI赋能分析"、"手机部AI投入分析"、"各部门AI使用情况"、
  "L5有哪些人"、"第3层的汇报链"、"组织诊断报告"、"全年预测"、
  "信息部的组织架构"、"查看手机部组织架构"等。
---

# 报告通道——场景路由 few-shot

> **职责**：外层 SKILL.md 判定进入报告通道后，由本文件识别报告类型，分发到 `references/report/` 下对应文件。

---

## 一、报告类型总览

| # | 报告类型 | 中文名称 | 一句话描述 | 下游文件 |
|---|---------|---------|-----------|---------|
| 1 | `ORG_HEALTH` | 组织健康度报告 | 组织层级深度、管理宽幅分布、管理配比趋势、零下属诊断等组织健康度分析 | `references/report/org-report.md` |
| 2 | `COST_REPORT` | 成本报告 | 组织人力成本相关分析报告 | `references/report/cost-report.md` |
| 3 | `TERMINATION_REPORT` | 离职报告 | 部门粒度（任意 1~6 级 + 集团级）的离职率、主被动结构、绩优流失、预离职预估、按部门/职级下钻分析 | `references/report/termination-report.md` |
| 4 | `ABNORMAL_STATUS_REPORT` | 休假关注名单 | 部门内特殊休假员工名单（V1：仅特殊休假，近 30 天与窗口有交集且按类别累计达标即命中），仅一级部门 HW/AU/HC/IS/IT/HR/TC/FI 支持 | `references/report/abnormal-status-report.md` |
| 5 | `ONBOARDING_REPORT` | 入职报告 | 入职洞察报告 | `references/report/onboarding-report.md` |
| 4 | `AI_COST_REPORT` | AI赋能人效分析报告 | 部门粒度（全公司 + 任意层级）的 AI Token 成本 vs 人力成本交叉分析、AI/人力比、AI渗透率、人均AI成本、月度增长趋势、渠道三分法占比 | `references/report/ai-cost-report.md` |
| 7 | `ORG_ARCHITECTURE_REPORT` | 组织架构报告 | 部门组织架构概览：负责人信息、人员类型分布、三级部门树形结构、要点摘要 | `references/report/org-architecture-report.md` |

---

## 二、路由触发关键词

| 报告类型 | 触发关键词（命中任一即路由） |
|---------|------------------------|
| `ORG_HEALTH` | 组织健康度、组织诊断、组织架构分析、组织健康、管理宽幅、管理配比、组织报告 |
| `COST_REPORT` | 成本报告、人力成本、用人成本、成本分析、预算使用率、人均成本、成本结构、全年预测、成本预测（⚠️ 前置排除：被 **AI/Token/渠道/龙虾/Coding** 修饰的"成本/人均成本/成本分析"不命中本行，见下方说明） |
| `TERMINATION_REPORT` | 离职报告、离职分析、离职画像、预离职、预离职名单、人员离职分析、离职率报告、人员流失分析、主动离职分析、绩优流失、绩优流失画像、离职诊断、离职情况分析、离职原因分析、HC使用率预估、月底人数预估、主动离职画像 |
| `ABNORMAL_STATUS_REPORT` | 特殊休假、特殊休假名单、休假情况、休假 |
| `ONBOARDING_REPORT` | 入职报告、入职分析、新人入职、入职画像、入职洞察、新人留存、新人分析、入职情况分析、人员入职分析、新人画像分析 |
| `AI_COST_REPORT` | AI人效、AI赋能、AI投入、AI成本对比人力、AI和人力成本、Token成本分析、AI渗透率、AI成本报告、人效分析报告、AI/人力比、Token/人力、AI成本增长、AI使用分析、AI使用场景、Coding占比、AI投入产出 |
| `ORG_ARCHITECTURE_REPORT` | 组织架构、架构（⚠️ 前置排除：被"分析/诊断/健康/报告"修饰的"组织架构"不命中本行，见 ORG_HEALTH） |

> **⚠️ AI 成本前置排除（先于 COST_REPORT 关键词判断）**：只要"成本/人均成本/成本分析"被 **AI / Token / 渠道 / 龙虾 / Coding** 修饰，**一律不命中 COST_REPORT**。这类问题按是否含报告词二分：含"报告/分析/投入/人效/渗透率/对比"等 → `AI_COST_REPORT`；其余（含"数据/情况/多少/占比/排名"等中性或数值表述）→ 转问数通道 `AI_COST` 子场景（见第十一节边界表）。
>
> **⚠️ AI_COST_REPORT 与 COST_REPORT 的区分**：凡问题涉及 **AI / Token / 渠道 / 渗透率**，或要求 **AI 成本与人力成本对比**，一律路由 `AI_COST_REPORT`；仅涉及**纯人力成本**（无 AI 维度）时才路由 `COST_REPORT`。

---

## 三、ORG_HEALTH 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "帮我看下互联网业务部的组织健康度" | 组织健康度 | → `references/report/org-report.md` |
| "手机部的组织诊断报告" | 组织诊断 | → `references/report/org-report.md` |
| "分析一下XX部门的组织架构分析" | 组织架构分析 | → `references/report/org-report.md` |
| "我部门的组织健康怎么样" | 组织健康 | → `references/report/org-report.md` |
| "看看研发部的管理宽幅" | 管理宽幅 | → `references/report/org-report.md` |
| "互联网业务部的管理配比是多少" | 管理配比 | → `references/report/org-report.md` |
| "帮我出一份组织报告" | 组织报告 | → `references/report/org-report.md` |
| "XX部门组织健康度诊断" | 组织健康度 | → `references/report/org-report.md` |
| "我团队的管理宽幅分布怎样" | 管理宽幅 | → `references/report/org-report.md` |
| "管理宽幅太大了怎么优化" | 管理宽幅 | → `references/report/org-report.md` |

> **⚠️ 强制要求**：命中 ORG_HEALTH 后，必须读取 `references/report/org-report.md` 全文再执行任何操作。该文件包含输出模板、诊断填充规范和禁止行为清单。跳过读取直接调用 `org_health_report` 工具属于严重错误。

### ORG_HEALTH drill-down（层级人员明细 / 汇报链查询）

当用户问题包含 **L+数字** 或 **"层级"+"人员/明细/汇报链"** 时，路由到 `references/report/org-report.md`（使用 `org_layer_detail` 工具）。可以是组织报告后的追问，也可以是独立提问。

| 场景 | 用户问题 | 匹配模式 | 路由 |
|------|---------|---------|------|
| 追问（刚生成组织报告） | "L8的人员是谁" | L+数字 | → `references/report/org-report.md` |
| 追问（刚生成组织报告） | "第5层有哪些人" | 层级+人员 | → `references/report/org-report.md` |
| 追问（刚生成组织报告） | "L5的汇报链" | L+数字+汇报链 | → `references/report/org-report.md` |
| 独立提问 | "互联网业务部的L1层级是谁" | 部门+L+数字 | → `references/report/org-report.md` |
| 独立提问 | "手机部第3层的汇报链是什么" | 部门+层级+汇报链 | → `references/report/org-report.md` |
| 独立提问 | "研发部L6有哪些人" | 部门+L+数字+人员 | → `references/report/org-report.md` |

---

## 四、COST_REPORT 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "XX部门的成本报告" | 成本报告 | → `references/report/cost-report.md` |
| "看下研发部的人力成本" | 人力成本 | → `references/report/cost-report.md` |
| "互联网业务部的用人成本分析" | 用人成本 | → `references/report/cost-report.md` |
| "帮我做一份成本分析" | 成本分析 | → `references/report/cost-report.md` |
| "中国区的预算使用率" | 预算使用率 | → `references/report/cost-report.md` |
| "手机部人均成本怎么样" | 人均成本 | → `references/report/cost-report.md` |
| "看下成本结构" | 成本结构 | → `references/report/cost-report.md` |
| "全年预测多少" | 全年预测 | → `references/report/cost-report.md` |
| "帮我看下成本预测" | 成本预测 | → `references/report/cost-report.md` |

> **⚠️ 强制要求**：命中 COST_REPORT 后，必须读取 `references/report/cost-report.md` 全文再执行任何操作。该文件包含工具调用前置校验、返回值处理、红线规则、飞书卡片发送流程等关键规则。跳过读取直接调用 `cost_report` 工具属于严重错误。

### COST_REPORT 特殊处理规则

1. **未指定部门或无法识别部门名称**：**不调用工具**，直接回复："请提供具体的部门名称（支持一级部门或二级部门），例如"中国区成本报告"、"手机部3月成本报告"。" **禁止默认使用"中国区"或任何其他部门名称替代。** 包括但不限于"我的部门"、"我所在的部门"、"我们部门"等自指性表述——这些均视为未提供具体部门名称，必须拒答并引导用户提供明确的部门名称。
2. **部门范围限制**：成本报告仅支持集团级、一级部门、二级部门。如果用户查询三级及以下部门的成本报告，**不调用工具**，直接回复："成本报告查询范围仅限一级部门及二级部门，暂不支持更细粒度的部门查询。"
3. **"/"分隔的部门名称必须理解为层级关系**：当用户输入"A/B/C"格式时，**只能理解为"一级部门/二级部门/三级部门"的层级关系**，不能理解为并列的多个部门。例如"人力资源部/中国区/COE"表示三级部门"COE"（隶属于人力资源部→中国区），由于包含三级部门，应按部门范围限制规则拒答。
4. **职级条件忽略**：`cost_report` 工具不支持按职级筛选。若用户提问包含职级条件（如"中国区19+的成本报告"），应忽略职级条件，直接查询该部门整体成本报告。
5. **错误重试**：工具返回错误时，必须再次调用重试（最多 1 次）。重试仍失败则输出"成本报告工具暂时繁忙，请稍后再试"。**绝对禁止**自行编写 SQL 替代。
6. **多轮对话隔离**：每次成本报告请求必须独立处理。填充分析解读时，**只使用当前工具返回的表格数据**，严禁引用对话历史中其他部门/其他查询的数据。
7. **权限拒答后禁止替换部门**：如果工具返回权限拒绝信息（如"没有查到您XX部门的权限"），**直接输出该拒绝信息并立即停止**。禁止自行替换为其他部门名称再次调用工具，禁止猜测或编造部门名称。**多部门查询时，只要其中任何一个部门返回权限拒绝，立即停止所有后续调用，已成功生成的报告也不发送，整体拒答。**

---

## 五、成本报告不支持的意图——直接拒答

**核心原则**：成本报告**唯一支持的操作**是为单个部门生成一份完整报告。只要用户意图不是"生成某部门的成本报告"，就应拒答。

以下问题虽然命中成本报告关键词，但**不属于生成单部门报告的意图**，**不调用工具**，直接拒答：

| 用户问题 | 不支持原因 |
|----------|-----------|
| "X部门武汉的区域成本是多少" | 提取局部数据 |
| "手机部外包人均成本多少" | 提取局部数据 |
| "中国区固定成本占比" | 提取局部数据 |
| "按城市汇总中国区成本" | 自定义维度分析 |
| "各职级的成本分布" | 自定义维度分析 |
| "正式和外包成本分别是多少" | 自定义维度分析 |
| "中国区人均成本乘以人数是多少" | 数据计算/推导 |
| "预算还剩多少" | 数据计算/推导 |
| "超预算了多少钱" | 数据计算/推导 |
**统一拒答话术**："成本报告仅支持为单个部门生成完整的成本报告，暂不支持局部数据提取或自定义计算。如需查看某部门的完整成本报告，请直接说"XX部门的成本报告"。"

**成本报告相关追问**：如果前文上下文中已有该部门的报告内容可见，可以基于报告内容作答（数据必须与报告完全一致，严禁篡改）。如果前文没有该部门报告，直接拒答。严禁先自行生成报告再提取数据作答。详见 `cost-report.md` 的"成本报告相关追问处理"章节。

---

## 六、TERMINATION_REPORT 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "中国区的离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "26年中国区离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "26年中国区3月份离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "26年中国区1-3月份离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "26年中国区3-6月份离职报告"（含未来月）| 离职报告 | → `references/report/termination-report.md` |
| "25年中国区离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "互联网业务部的离职分析" | 离职分析 | → `references/report/termination-report.md` |
| "手机部人员离职分析" | 人员离职分析 | → `references/report/termination-report.md` |
| "深圳分公司的离职情况分析" | 离职情况分析 | → `references/report/termination-report.md` |
| "XX部门的主动离职分析" | 主动离职分析 | → `references/report/termination-report.md` |
| "XX部门的绩优流失" | 绩优流失 | → `references/report/termination-report.md` |
| "XX部门的人员流失分析" | 人员流失分析 | → `references/report/termination-report.md` |
| "XX部门的离职诊断" | 离职诊断 | → `references/report/termination-report.md` |
| "查询信息部的离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "帮我看下中国区的离职分析" | 离职分析 | → `references/report/termination-report.md` |
| "XX部门的离职情况分析" | 离职情况分析 | → `references/report/termination-report.md` |
| "看一下XX的离职报告" | 离职报告 | → `references/report/termination-report.md` |
| "出一份XX部门的离职分析" | 离职分析 | → `references/report/termination-report.md` |
| "XX部门预离职情况" | 预离职 | → `references/report/termination-report.md` |
| "XX部门预离职名单" | 预离职名单 | → `references/report/termination-report.md` |

> **⚠️ 强制要求**：命中 TERMINATION_REPORT 后，必须读取 `references/report/termination-report.md` 全文再执行任何操作。该文件包含场景识别（8 个制式场景 → `start_dt / end_dt / include_forecast` 参数映射）、工具返回值处理、红线规则、飞书卡片发送流程等关键规则。跳过读取直接调用 `termination_report` 工具属于严重错误。

> **⚠️ 模板强制约束**：所有离职报告相关请求的输出必须严格遵循 `references/report/termination-report.md` 定义的模板格式（多卡片分段发送）。**绝对禁止**绕过报告工具，用 `sql_query` 自行查询离职数据后以自由文本格式输出来替代制式报告。离职报告 = 调用 `termination_report` 工具 + 按模板格式化输出，两者缺一不可。

### TERMINATION_REPORT 特殊处理规则

1. **未指定部门或无法识别部门名称**：**不调用工具**，直接回复："请提供具体的部门名称（支持任意层级 1~6 级），例如"中国区离职报告"、"深圳分公司离职分析"、"城市管理部离职情况"。" **禁止默认使用"中国区"或任何其他部门名称替代。** 自指性表述（"我部门"、"我的部门"、"我们部门"等）一律视为未提供部门名称。
2. **部门层级无限制**：离职报告支持集团级、一级到六级（末级）所有部门——与成本报告不同，**不要**因为是三级或末级就拒答。完整名称原样传给工具即可。
3. **"/"分隔的部门名称按层级路径解析**：当用户输入"A/B/C"格式时，理解为"一级部门/二级部门/三级部门..."的层级关系。完整名称传给工具，工具按路径匹配。
4. **职级条件忽略**：若用户提问包含职级条件（如"中国区 13 级及以上的离职报告"），应忽略职级条件，按整体部门报告处理（工具自身会输出职级维度的下钻表）。
5. **错误重试**：工具返回错误时，必须再次调用重试（最多 1 次）。重试仍失败则输出"离职报告工具暂时繁忙，请稍后再试"。**绝对禁止**自行编写 SQL 替代。
6. **多轮对话隔离**：每次离职报告请求必须独立处理。填充分析解读时，**只使用当前工具返回的表格数据**，严禁引用对话历史中其他部门/其他查询的数据。
7. **权限拒答后禁止替换部门**：如果工具返回权限拒绝信息，**直接输出并立即停止**。禁止自行替换为其他部门名称再次调用工具。**多部门查询时，只要任一部门返回权限拒绝，立即停止所有后续调用，已生成的报告也不发送。**
8. **歧义处理**：工具返回 `{"error": ..., "candidates": [...]}` 时，应将候选列表展示给用户选择，**禁止自动挑一个**。

---

## 七、ABNORMAL_STATUS_REPORT 路由示例（对齐 PRD §4.2 query）

| 用户问题（PRD query） | 命中关键词 | scope / pos_lvl | 路由 |
|----------|-----------|-----------------|------|
| "手机部的特殊休假" | 特殊休假 | `scope="default"` | → `references/report/abnormal-status-report.md` |
| "手机部的休假情况" | 休假情况 | `scope="default"` | → `references/report/abnormal-status-report.md` |
| "手机部高潜的休假情况" | 高潜+休假 | `scope="高潜"` | → `references/report/abnormal-status-report.md` |
| "汽车部管理者的休假情况" | 管理者+休假 | `scope="管理者"` | → `references/report/abnormal-status-report.md` |
| "财务部高绩效的休假情况" | 高绩效+休假 | `scope="高绩效"` | → `references/report/abnormal-status-report.md` |
| "集团信息技术部应届生的休假情况" | 应届+休假 | `scope="应届"` | → `references/report/abnormal-status-report.md` |
| "人力资源部 17~19 级的休假情况" | 职级范围+休假 | `pos_lvl="17-19"` | → `references/report/abnormal-status-report.md` |
| "技术委员会 19 级特殊休假" | 单职级+特殊休假 | `pos_lvl="19"` | → `references/report/abnormal-status-report.md` |

> **⚠️ 强制要求**：命中 ABNORMAL_STATUS_REPORT 后，必须读取 `references/report/abnormal-status-report.md` 全文再执行任何操作。该文件包含部门白名单（HW/AU/HC/IS/IT/HR/TC/FI）、scope 参数映射、错误处理、卡片发送流程等关键规则。跳过读取直接调用 `abnormal_status_report` 工具属于严重错误。

### ABNORMAL_STATUS_REPORT 特殊处理规则

1. **未指定部门或自指性表述**：**不调用工具**，直接拒答并引导用户提供白名单内的部门名称（HW/AU/HC/IS/IT/HR/TC/FI）
2. **部门白名单（测试阶段）**：仅支持一级部门 HW、AU、HC、IS、IT、HR、TC、FI 共 8 个。其他部门（如"中国区"、"销售部"、"研发部"）以及二级及更深层级一律由工具拒绝，LLM 直接输出拒绝文案。HW 排除二级「新业务部」，HW/AU/HC 排除「生产制造序列」（工具内已实现）
3. **scope 识别（6 个合法取值，与 PRD §4.2 一一对应）**：
   - 仅 "XXX部门的特殊休假 / 休假情况"（未限定人群）→ `scope="default"`（高潜+管理者互斥单卡片）
   - "XXX部门高潜的休假情况" → `scope="高潜"`
   - "XXX部门管理者的休假情况" → `scope="管理者"`
   - "XXX部门高绩效的休假情况" → `scope="高绩效"`
   - "XXX部门应届生的休假情况" → `scope="应届"`
   - "XXX部门 17~19 级的休假情况" → `pos_lvl="17-19"`（区间分隔符 `-` / `~` / `～` / `到` / `至` 都接受，工具内部统一规范化）；单一职级则 `pos_lvl="19"`。给定 pos_lvl 时无需另传 scope，工具自动归位 `scope="职级"`
4. **错误重试**：工具返回错误时重试 1 次，失败后告知"休假关注名单工具暂时繁忙"。**绝对禁止**自行编写 SQL 替代
5. **多轮对话隔离**：每次报告独立处理，禁止引用对话历史中其他部门的数据
6. **权限拒答后禁止替换部门**：工具返回权限拒绝时直接输出，禁止自行替换部门重试
7. **V1 范围之外的异常类型拒答**：V1 仅支持特殊休假。用户问"出勤工时低位"、"活跃度下滑"等其他异常类型时，回复"该异常类型尚未上线，当前版本仅支持休假关注名单"。**预离职已不再属于本通道**，由 TERMINATION_REPORT 负责（含预离职章节）

### 与 TERMINATION_REPORT 的区分

- 用户问"预离职"、"预离职名单"、"预离职情况"、"绩优流失"、"主动离职"、"离职率"、"离职报告" → **TERMINATION_REPORT**
- 用户问"特殊休假"、"休假情况"（含人群/职级修饰：高潜/管理者/高绩效/应届/N级 的休假情况）→ **ABNORMAL_STATUS_REPORT**
- 单独说"丧假/婚假/产假"等具体假种名单：PRD 未列入触发 query；如用户提问，按 ABNORMAL_STATUS_REPORT 处理（工具会按假种分组输出全部命中员工）

---

## 八、离职报告不支持的意图——直接拒答 / 转 SQL

**核心原则**：离职报告**唯一支持的操作**是为单个部门生成一份完整报告（4 或 5 张卡片）。场景超出 8 个制式场景或需要局部数据计算的，不调用工具。

以下虽然命中"离职"关键词但**不属于制式报告意图**，不调用 `termination_report`：

| 用户问题 | 不支持原因 | 正确处理 |
|----------|-----------|----------|
| "24-25 年离职趋势" | 跨年对比 | 转 `sql_query` 自由回答 |
| "近三年离职率趋势" | 多年趋势 | 转 `sql_query` |
| "上季度离职率" | Q 单位非标时间 | 转 `sql_query` |
| "Q2 离职分析" | Q 单位 | 转 `sql_query` |
| "上半年离职情况" | 非标时间词 | 转 `sql_query` |
| "最近离职了多少人" | 模糊时间词 | 转 `sql_query` |
| "中国区固定离职原因占比" | 提取局部数据 | 转 `sql_query` |
| "按城市汇总离职人数" | 自定义维度 | 转 `sql_query` |


**离职报告相关追问**：若前文上下文中已有该部门的报告内容可见，可基于报告内容作答（数据必须与报告完全一致）。如果前文没有该部门报告，直接拒答，不允许先自行调用 `termination_report` 再提取数据。详见 `termination-report.md` 的"离职报告相关追问处理"章节。


## 九、ONBOARDING_REPORT 路由示例
| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "中国区的入职报告" | 入职报告 | → `references/report/onboarding-report.md` |
| "26年中国区4月入职分析" | 入职分析 | → `references/report/onboarding-report.md` |
| "互联网业务部新人入职洞察" | 入职洞察 | → `references/report/onboarding-report.md` |
| "深圳分公司入职情况分析" | 入职情况分析 | → `references/report/onboarding-report.md` |
| "手机部新人留存怎么样" | 新人留存 | → `references/report/onboarding-report.md` |


> **⚠️ 强制要求**：命中 ONBOARDING_REPORT 后，必须读取 `references/report/onboarding-report.md` 全文再执行任何操作。该文件包含工具调用前置校验、返回值处理、红线规则、飞书卡片发送流程等关键规则。跳过读取直接调用 `onboarding_report` 工具属于严重错误。

### ONBOARDING_REPORT 特殊处理规则

1. **未指定部门或自指性表述**：**不调用工具**。回复："入职报告不支持「我部门」等自指性表述，请提供具体的部门名称（支持任意层级 1~6 级），例如「中国区入职报告」「深圳分公司入职分析」。" **禁止默认使用「中国区」或猜测用户部门。**
2. **部门层级无限制**：支持集团级（小米集团/小米公司）、一级到六级（末级）。将用户提供的部门名称**原样**传给 `onboarding_report`，由工具解析层级。
3. **"/" 分隔的部门名称**：理解为层级路径（如 `人力资源部/中国区/COE`），完整名称传给工具。
4. **职级条件忽略**：工具不支持按职级筛选入职报告。含职级条件时忽略职级，查询部门整体报告。
5. **错误重试**：工具返回 `{"error": ...}` 时，**再次调用** `onboarding_report`（最多 1 次）。仍失败则回复「入职报告工具暂时繁忙，请稍后再试」。**绝对禁止**用 `sql_query` 替代。
6. **多轮对话隔离**：每次请求仅使用**当次**工具返回数据填充分析，禁止引用历史中其他部门的数据。
7. **权限拒答后禁止替换部门**：收到权限拒绝后**直接输出并停止**，禁止换部门重试。
8. **多部门并列查询**：逐个调用；**任一部门权限拒绝则立即停止**，已生成内容也不输出。
9. **部门歧义**：工具返回 `candidates` 时展示列表让用户选择，**禁止自动挑选**。

## 入职报告不支持的意图

**核心原则**：入职报告唯一支持的操作是为**单个部门**生成「基础摘要卡片 + 完整飞书文档」。以下意图不调用 `onboarding_report`：

| 用户问题 | 不支持原因 | 正确处理 |
|----------|-----------|----------|
| "24-25年入职趋势对比" | 跨年非标场景 | 转 `sql_query` |
| "上季度入职多少人" | Q 单位非标时间 | 转 `sql_query` |
| "最近入职了多少人" | 模糊时间词 | 转 `sql_query` |
| "中国区13级入职明细" | 局部提取/职级筛选 | 转 `sql_query` 或引导生成完整报告 |


---

## 十、ORG_ARCHITECTURE_REPORT 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "信息部的组织架构" | 组织架构 | → `references/report/org-architecture-report.md` |
| "查看手机部组织架构" | 组织架构 | → `references/report/org-architecture-report.md` |
| "帮我看下互联网业务部的组织架构" | 组织架构 | → `references/report/org-architecture-report.md` |
| "集团信息技术部组织架构" | 组织架构 | → `references/report/org-architecture-report.md` |
| "查一下汽车部的架构" | 架构 | → `references/report/org-architecture-report.md` |
| "发一下汽车部的组织架构" | 组织架构 | → `references/report/org-architecture-report.md` |
| "查一下我管理部门的架构" | 自指性表述 | → 拒答，引导提供具体部门名称 |

> **⚠️ 强制要求**：命中 ORG_ARCHITECTURE_REPORT 后，必须读取 `references/report/org-architecture-report.md` 全文再执行任何操作。该文件包含工具调用方式、输出格式规范等关键规则。

### ORG_ARCHITECTURE_REPORT 特殊处理规则

1. **未指定部门或自指性表述**：**不调用工具**，直接回复："请提供具体的部门名称（支持任意层级 1~6 级），例如"信息部组织架构"、"手机部组织架构"。" **禁止默认使用"中国区"或任何其他部门名称替代。** 自指性表述（"我部门"、"我的部门"、"我们部门"等）一律视为未提供部门名称，必须拒答并引导用户提供明确的部门名称。
2. **部门层级无限制**：支持集团级、一级到六级（末级）所有部门。完整名称原样传给 `org_architecture_report` 工具。
3. **"/"分隔的部门名称按层级路径解析**：当用户输入"A/B/C"格式时，理解为"一级部门/二级部门/三级部门..."的层级关系。
4. **错误重试**：工具返回错误时，必须再次调用重试（最多 1 次）。重试仍失败则输出"组织架构查询暂时繁忙，请稍后再试"。**绝对禁止**编造数据替代。
5. **多轮对话隔离**：每次组织架构请求必须独立处理。严禁引用对话历史中其他部门的数据。
6. **权限拒答后禁止替换部门**：如果查询返回权限拒绝信息，**直接输出该拒绝信息并立即停止**。禁止自行替换为其他部门名称再次查询。

---

## 十一、易混淆——不进入报告通道的问题

以下问题**不含报告通道关键词**，应走 SQL 或 ES 通道：

| 用户问题 | 原因 | 正确路由 |
|----------|------|---------|
| "XX部门有多少人" | 人数统计，无报告关键词 | SQL |
| "各部门人数分布" | 统计类 | SQL |
| "研发部有哪些管理者" | 结构化条件员工列表 | SQL |
| "帮我看下XX的组织层级" | 不含报告关键词 | SQL |
| "各部门平均管理幅度" | 不含"管理宽幅"/"管理配比" | SQL |
| "XX部门有多少个管理者" | 人数统计 | SQL |
| "帮我诊断一下XX部门的组织" | 不含"组织诊断"完整关键词 | SQL |

---

## 十二、AI_COST_REPORT 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "生成AI人效分析报告" | AI人效 | → `references/report/ai-cost-report.md` |
| "全公司AI赋能分析" | AI赋能 | → `references/report/ai-cost-report.md` |
| "手机部的AI投入分析" | AI投入 | → `references/report/ai-cost-report.md` |
| "帮我看看各部门AI使用情况" | AI使用分析 | → `references/report/ai-cost-report.md` |
| "AI成本对比人力成本" | AI成本对比人力 | → `references/report/ai-cost-report.md` |
| "互联网业务部的AI渗透率分析" | AI渗透率 | → `references/report/ai-cost-report.md` |
| "Token成本分析报告" | Token成本分析 | → `references/report/ai-cost-report.md` |
| "AI/人力比怎么样" | AI/人力比 | → `references/report/ai-cost-report.md` |
| "AI成本增长分析" | AI成本增长 | → `references/report/ai-cost-report.md` |
| "Coding占比多少" | Coding占比 | → `references/report/ai-cost-report.md` |

> **⚠️ 强制要求**：命中 AI_COST_REPORT 后，必须读取 `references/report/ai-cost-report.md` 全文再执行任何操作。该文件包含工具调用、sections 填充规则、飞书文档创建流程、红线规则。**报告生成是两步流程（调用 `ai_cost_report` 工具拿骨架 → 填充分析并创建飞书文档），缺一不可。** 跳过读取直接调用工具、或拿到工具返回值后就停下，均属于严重错误。

### AI_COST_REPORT 特殊处理规则

1. **未指定部门或无法识别部门名称**：**不调用工具**，引导用户提供具体部门名称，例如"全公司AI人效报告"、"手机部AI投入分析"。自指性表述（"我部门"、"我的部门"、"我们部门"等）一律视为未提供部门名称，必须拒答。
2. **部门层级无限制**：支持"全公司"/集团级、一级到末级所有部门，逐级下钻。完整名称原样传给工具即可。
3. **"/"分隔的部门名称按层级路径解析**：当用户输入"A/B/C"格式时，理解为"一级部门/二级部门/三级部门..."的层级关系，完整名称传给工具。
4. **月份自动校正**：工具自动 clamp 到最新可用月份（不拒答），LLM 无需做月份校验。
5. **错误不兜底**：工具返回错误时，**绝对禁止**用 `sql_query` 自行查询替代生成报告。直接输出工具返回的错误信息。
6. **多轮对话隔离**：每次报告请求独立处理，只使用当前工具返回的数据，严禁引用对话历史中其他部门的数据。
7. **歧义/权限处理**：工具返回 `{"error": ..., "candidates": [...]}` 时展示候选列表让用户选择；返回权限拒绝时直接输出并停止，禁止替换部门重试。

### AI_COST_REPORT 边界——转问数通道

以下虽含 AI 成本关键词，但属于**具体指标问数**（非生成完整报告），**不走报告通道**，转通用问数通道（`routing-sql.md` → AI_COST 子场景，查询 `ads_mify_cost_di`）：

| 用户问题 | 不支持原因 | 正确处理 |
|----------|-----------|----------|
| "手机部Token成本多少" | 单指标查询 | 转 `routing-sql.md` → AI_COST |
| "各部门AI渗透率排名" | 排名查询 | 转 `routing-sql.md` → AI_COST |
| "Coding类成本占比多少" | 单指标查询 | 转 `routing-sql.md` → AI_COST |
| "手机部多少人用了AI" | AI活跃人数查询 | 转 `routing-sql.md` → AI_COST |
| "手机部AI成本数据" | 中性表述，非报告 | 转 `routing-sql.md` → AI_COST |
| "看一下XX部门的AI成本" | 中性表述，非报告 | 转 `routing-sql.md` → AI_COST |
| "手机部AI成本是多少" | 单指标查询 | 转 `routing-sql.md` → AI_COST |
| "XX部门AI人均成本" | 单指标查询（"人均成本"被 AI 修饰，不走 COST_REPORT） | 转 `routing-sql.md` → AI_COST |

> **区分要点**：含"报告/分析/对比/投入/人效/整体情况"等报告词 → 报告通道（本文件）；问"多少/占比/排名/几个"等数值，或"数据/情况/看一下/查一下"等中性表述 → 问数通道（AI_COST）。**"AI成本"绝不路由 COST_REPORT**——它要么是 AI_COST_REPORT（含报告词），要么是 AI_COST 问数（其余）。
