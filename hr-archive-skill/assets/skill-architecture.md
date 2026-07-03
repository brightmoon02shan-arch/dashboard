# hr-archive-skill-test 目录结构与架构说明

## 目录树

```
.claude/skills/hr-archive-skill-test/
├── SKILL.md                              ← 【总路由】意图识别 + 数据源路由
├── assets/
│   ├── card-examples.md                  ← 飞书卡片输出示例
│   └── skill-architecture.md             ← 本文件：架构说明
└── references/
    ├── routing-examples.md               ← 【路由辅助】路由判断示例集
    ├── routing-es.md                     ← 【场景路由】ES 路由规则细化
    ├── routing-sql.md                    ← 【场景路由】SQL 路由规则细化
    ├── routing-report.md                 ← 【场景路由】组织健康报告路由规则
    ├── es/
    │   └── es-talent-query.md            ← 【具体实现】ES DSL 构建规范、字段 schema、查询模式
    ├── sql/
    │   └── sql-query.md                  ← 【具体实现】SQL 查询规范、表结构、指标定义
    ├── report/
    │   └── org-report.md                 ← 【具体实现】组织健康度报告生成逻辑
    └── output/
        └── output-format.md              ← 【具体实现】输出格式模板（各场景结果格式化规则）

## 命名格式：
- 路由命名 统一 routing
- 数据表相关统一 data_es/holo
- 查询语句相关统一 dsl/sql_
- Output 输出格式 统一到外层，按照场景分类output-star-evaluation
```




## 三层架构

| 层级 | 文件 | 职责 |
|------|------|------|
| **总路由** | `SKILL.md` | 入口。意图识别 → 5 步决策树（前置拦截 → 问人/问数 → 标签细分 → 特殊字段 → 兜底）→ 选定数据源后锁定（Route-Lock） |
| **场景路由** | `routing-*.md` | 细化各数据源（ES / SQL / 组织报告）的路由判断规则和示例 |
| **具体实现** | `es/`、`sql/`、`report/`、`output/` | 查询构建（DSL / SQL / 报告工具调用）和结果格式化的具体规范 |

## 请求处理流程

```
用户提问
  → SKILL.md 总路由
    → Step 1: 前置拦截（个人自查 / 团队查询规则）
    → Step 2: 问人 vs 问数（ES / SQL / 组织报告）
    → Step 3: 标签类查询细分（教育标签→SQL / 人才标签→ES / 小米标签→SQL）
    → Step 4: 特殊字段覆盖（仅 ES 有的字段强制走 ES）
    → Step 5: 兜底
    → Route-Lock 锁定数据源
  → 读取对应场景路由（routing-*.md）
  → 读取具体实现（es/ 或 sql/ 或 report/）
  → 构造查询 → 调用 MCP 工具（es_query / sql_query / org_health_report）
  → 读取 output/output-format.md → 格式化输出
```
