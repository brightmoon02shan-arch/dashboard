---
name: routing-mixed
description: >
  Mixed 通道场景路由——跨数据源（SQL + ES）综合信息组装通道。
  外层 SKILL.md 判定进入 mixed 通道后，由本文件完成子意图识别与下游实现文件分发。
  与 ES / SQL / 报告三个业务通道互斥：本通道由后端工具一次完成多源召回与定型卡片渲染，
  适用于"单次回答需要同时融合结构化事实与语义文本"的综合信息组装场景。
  当前承载子意图：TALENT_PROFILE（人才档案）、ORG_PROFILE_CARD（组织档案跳转卡片）。
---

# Mixed 通道——综合信息组装路由

> **职责**：识别子意图、判定命中条件、分发到 `references/mixed/` 下对应实现文件。工具调用规范、返回值处理、红线规则、卡片渲染等下沉到下游文件。

> **通道定位**：跨数据源（SQL + ES）综合信息组装——单次回答需要同时融合结构化事实（人事维度、绩效、组织架构）与语义文本（评价、周报、AI 用量、项目动态），由后端工具一次完成多源召回与成品卡片渲染。

> **与单源通道的互斥**：纯结构化统计走 SQL；纯语义检索/单维评价走 ES；预定义统计骨架走报告。本通道唯一区别在于"一次返回某个对象的多维全貌"。

---

## 一、子意图总览

| 子意图 | 中文名 | 触发关键词 | 后端工具 | 下游文件 |
|--------|--------|-----------|---------|---------|
| `TALENT_PROFILE` | 人才档案 | 人才档案 / 个人档案 / 员工档案 / XX的档案 | `talent_profile` | [mixed/talent-profile.md](mixed/talent-profile.md) |
| `ORG_PROFILE_CARD` | 组织档案跳转卡片 | 组织档案 / XX的组织档案 | `es_query`（锚点解析） | [mixed/org-profile-card.md](mixed/org-profile-card.md) |

> **⚠️ "组织档案" ≠ "人才档案"**：含"组织档案"的问句（如"XX的组织档案"）**不**命中 TALENT_PROFILE，应路由至 `ORG_PROFILE_CARD` 子意图，按 [mixed/org-profile-card.md](mixed/org-profile-card.md) 发送跳转卡片。

> 后续扩展占位：团队画像（TEAM_PROFILE）、汇报线全景（REPORT_LINE_VIEW）、业务线人才矩阵（TALENT_MATRIX）等。新增意图时在本表追加，并补对应识别规则即可。

---

## 二、TALENT_PROFILE 路由

### 2.1 命中条件（同时满足）

1. 含 **"人才档案 / 个人档案 / 员工档案"** 关键词，或含 **"档案"** 且上下文明确指向**个人**（如"XX的档案"、"看下XXX档案"）
2. 指向**单个员工**（姓名 / 工号 / oprid，含自指）
3. **不**是聚合 / 统计（"档案完整度"等 → SQL）
4. **不**是群体筛选（"明星员工的档案" → ES `STAR_TALENT`）
5. **不**是"组织档案"（含"组织档案"的问句 → **排除**，不进入本意图）

### 2.1a 组织档案跳转卡片

若查询进入 mixed 通道但命中"组织档案"意图（含"组织档案"关键词），**不得尝试跨通道回退**（Route-Lock 生效），按 [mixed/org-profile-card.md](mixed/org-profile-card.md) 流程处理：

1. 解析员工锚点（复用 talent_profile 逻辑）
2. 发送一张飞书交互卡片（绿色标题 + 跳转按钮）
3. 按钮链接自动携带 `userId={oprid}`

> **⚠️ 命中后必须读取 [mixed/org-profile-card.md](mixed/org-profile-card.md) 全文再执行任何操作。**

es_query 调用失败时降级为纯文本引导：

> 组织档案查询请移步至：https://archive.hr.mioffice.cn/organize-profile
>
> 如需查看个人人才档案，请使用"XX的人才档案"。

### 2.2 与其他通道 / 意图的互斥

- 含「档案」词但仅问单一维度（如"XXX 的绩效"、"XXX 在做什么"）→ **不**走本意图，按 ES `STAR_EVALUATION / STAR_STATUS` 处理
- 含「档案」词但问"人员档案数量 / 部门档案完整度"等聚合问题 → 走 SQL 通道
- 报告类关键词（组织健康度 / 成本 / 离职 / 休假 / 入职）优先级高于本通道
- **自查拦截优先**：用户查询自己的人才档案（"我的人才档案"等）必须先在 SKILL.md §1.1 拦截，**不**进入本意图

### 2.3 路由示例

| 用户问题 | 命中关键词 | 路由 |
|----------|-----------|------|
| "XXX 的人才档案" | 人才档案 | → `mixed/talent-profile.md` |
| "看下 XXX 的档案" | 档案 | → `mixed/talent-profile.md` |
| "10086 的个人档案" | 个人档案 | → `mixed/talent-profile.md` |
| "qiulvyang 的员工档案" | 员工档案 | → `mixed/talent-profile.md` |
| "查下 XXX 和 YYY 的档案"（多人）| 档案 | → `mixed/talent-profile.md`（逐人调用） |
| "XXX 是谁，他绩效怎么样、最近在做什么、什么时候入职的？"（≥3 维并列）| 综合多维 | → `mixed/talent-profile.md`（兜底） |

> **⚠️ 命中后必须读取 [mixed/talent-profile.md](mixed/talent-profile.md) 全文再执行任何操作**。该文件包含工具调用、参数抽取、返回值结构、错误处理、红线规则等全部规范，跳过读取直接调用工具属于严重错误。

---

## 三、不进入 mixed 通道的问题（易混淆）

| 用户问题 | 原因 | 正确路由 |
|----------|------|---------|
| "XXX 最近在做什么" | 单维度（近期状态） | ES `STAR_STATUS` |
| "XXX 表现怎么样" | 单维度（评价） | ES `STAR_EVALUATION` |
| "XXX 是哪个部门的" | 单维度（基础信息） | SQL 通道 |
| "XXX 的绩效" | 单维度（绩效） | SQL 通道 |
| "互联网业务部的人才档案完整度" | 聚合统计 | SQL 通道 |
| "明星员工的档案" | 群体筛选 | ES `STAR_TALENT` |
| "我们部门的离职报告" | 报告通道 | TERMINATION_REPORT |

> **判定要点**：是否需要"一次返回某个具体对象的多维全貌（结构化事实 + 语义文本）"决定是否进入本通道。单一维度即使带"档案"二字也不进入；多人 / 群体筛选即使问综合表现也不进入（走 ES TALENT）。
