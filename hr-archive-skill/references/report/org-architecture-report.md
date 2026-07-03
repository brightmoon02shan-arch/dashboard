---
name: org-architecture-report
description: >
  组织架构报告。当 routing-report.md 判定为 ORG_ARCHITECTURE_REPORT 时加载本文件，
  指导 LLM 调用 org_architecture_report MCP 工具获取完整报告数据，
  并按规范输出 Markdown 格式的组织架构报告。
---

# 组织架构报告（ORG_ARCHITECTURE_REPORT）

> **⚠️ 重要：组织架构报告通过 `org_architecture_report` MCP 工具一次调用获取完整数据，禁止编造数据。**

---

## 一、工具调用

调用 `org_architecture_report` MCP 工具，传入部门名称：

```bash
mcporter call hr_talent_claw.org_architecture_report \
  dept_name="{部门名称}"
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `dept_name` | ✅ | 部门名称（任意层级 1~6 级） |

### 返回结构

工具返回 `{code, message, data}` 结构：

- `code = 0`：成功，`data` 包含完整报告数据
- `code = 4031/4032`：权限不足
- `code = 4041`：部门未找到
- `code = 4221`：部门名称歧义（多个候选）
- `code = 5001`：服务异常

`data` 包含两个部分：

```json
{
  "dept_basic": {
    "dept_name": "部门全路径",
    "manager": {"name": "负责人姓名", "oprid": "oprid", "position": "职位", "level": "职级"},
    "total_cnt": 1595,
    "formal_cnt": 1333,
    "outsource_a_cnt": 0,
    "outsource_b_cnt": 262,
    "intern_cnt": 47,
    "fresh_grad_cnt": 378,
    "fresh_grad_pct": "23.7%",
    "recent_grad_cnt": 267,
    "recent_grad_pct": "16.7%"
  },
  "org_tree": {
    "target_dept": "部门名称",
    "path": "部门全路径",
    "total_cnt": 1595,
    "two_level_only": false,
    "children": [
      {
        "dept_name": "子部门名称",
        "emp_cnt": 363,
        "manager": {"name": "负责人", "oprid": "oprid", "position": "职位", "level": "职级"},
        "children": [
          {"dept_name": "孙部门", "emp_cnt": 96, "manager": {"name": "...", "oprid": "...", "position": "...", "level": "..."}}
        ]
      }
    ]
  }
}
```

### 场景识别与参数映射

LLM 必须从用户 query 中提取部门名称：

| # | 示例 query | 提取的部门名称 |
|---|-----------|--------------|
| 1 | "信息部的组织架构" | 信息部 |
| 2 | "查看手机部组织架构" | 手机部 |
| 3 | "帮我看下互联网业务部的组织架构" | 互联网业务部 |
| 4 | "集团信息技术部组织架构" | 集团信息技术部 |

### ⚠️ 自指性表述拒答（最高优先级，必须在调用工具前判断）

**当用户提问中未出现具体部门名称，而是使用自指性表述时，必须直接拒答，禁止调用工具。**

自指性表述包括但不限于："我部门"、"我的部门"、"我所在的部门"、"我们部门"、"我们的部门"、"本部门"、"咱们部门"、"咱部门"、"我管理部门"、"我管的部门"、"我负责的部门"等。

回复话术："组织架构报告不支持"我部门"等自指性表述，请提供具体的部门名称（支持任意层级 1~6 级），例如"信息部组织架构"、"手机部组织架构"。"

**禁止默认使用"中国区"或任何其他部门名称替代。禁止猜测用户所在部门。**

### ⚠️ 多轮对话隔离（必须遵守）

**每次组织架构请求必须独立处理，严禁混入对话历史中其他查询的数据或结论。**

### ⚠️ 权限拒答后禁止自行替换部门（必须遵守）

- 如果工具返回权限拒绝（code=4031/4032），**直接输出拒绝信息，立即停止**
- **禁止**在收到权限拒绝后自行替换为其他部门名称再次调用工具
- **禁止**猜测或编造部门名称调用工具

---

## 二、错误处理（必须遵守）

如果工具返回错误（code ≠ 0），**必须再次调用重试**（最多重试 1 次）。

**绝对禁止**：
- ❌ 在工具返回错误后自行编造数据
- ❌ 自行拼凑报告数据
- ❌ 用历史缓存数据替代

如果重试仍然失败，向用户说明"组织架构查询暂时繁忙，请稍后再试"，不得自行生成替代报告。

---

## 三、LLM 输出规则

> **⚠️ 组织架构报告必须使用 `msg_type=interactive` 发送飞书交互卡片。**

### 发送步骤

1. 调用 `org_architecture_report` 工具获取数据
2. 按下方格式组装 Markdown 内容
3. 组装飞书卡片 JSON 发送（参考 `references/report/send-card.md`）

### 卡片组装

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {
        "template": "blue",
        "title": {"tag": "plain_text", "content": "{path} 组织架构"}
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "BASIC_INFO_CONTENT"
            }
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "TREE_CONTENT"
            }
        },
        {"tag": "hr"}
    ]
}
```

- `path` = 部门全路径（如"集团信息技术部 / 企业智能协同部"），单级部门直接用部门名
- `BASIC_INFO_CONTENT` = 基本信息 Markdown
- `TREE_CONTENT` = 树形结构（**不使用 code fence**，直接用 lark_md 渲染）
- `receive_id` 使用 runtime context 中的 `Chat ID`

### 人名超链接规则

所有人名必须链接到人才档案页面，链接格式：

```
[{manager.name}](https://archive.hr.mioffice.cn/talent-details?userId={manager.oprid})（{manager.level}级）
```

- `oprid` 来自工具返回的 `manager.oprid` 字段
- 当 `oprid` 为空时，人名不加超链接，直接显示纯文本

### 输出格式

报告内容由两部分组成，**中间用 `hr` 分隔线隔开**：

1. **部门基本信息**：负责人信息 + 人员类型分布
2. **组织架构图**：Markdown 树形结构

#### 部门基本信息

> **零值隐藏规则**：指标为 0 时自动隐藏对应行，不展示"0 人"。

基于 `data.dept_basic` 输出（`BASIC_INFO_CONTENT`）：

```
**负责人**：[{manager.name}](https://archive.hr.mioffice.cn/talent-details?userId={manager.oprid})（{manager.position}，{manager.level}级）
**总员工**：{total_cnt} 人（正式 {formal_cnt} + 外包A {outsource_a_cnt} + 外包B {outsource_b_cnt}）
**应届生**：{fresh_grad_cnt} 人（占比 {fresh_grad_pct}），近五年 {recent_grad_cnt} 人（占比 {recent_grad_pct}）
**实习生**：{intern_cnt} 人（未计入总员工数）
```

**字段为空时处理**：
- `manager.name` 为空 → 显示"暂无"（不加超链接）
- `manager.oprid` 为空 → 人名不加超链接，直接显示纯文本
- `manager.position` 为空 → 显示"暂无"
- `manager.level` 为空 → 显示"未知"

#### 组织架构图（Markdown 树）

基于 `data.org_tree` 输出（`TREE_CONTENT`）。**不使用 code fence**，直接用 lark_md 渲染，部门名加粗、人名加超链接：

```
**{org_tree.path}**（{total_cnt}人）| [{manager.name}](链接)（{manager.level}级）
│
├─ **{children[0].dept_name}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
│  ├─ **{grandchildren[0]}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
│  └─ **{grandchildren[1]}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
│
├─ **{children[1].dept_name}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
│
└─ **{children[N].dept_name}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
   ├─ **{grandchildren[0]}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
   └─ **{grandchildren[1]}**（{emp_cnt}人）| [{manager.name}](链接)（{manager.level}级）
```

> 链接 = `https://archive.hr.mioffice.cn/talent-details?userId={oprid}`，oprid 为空时不加链接

**树结构规则**：

1. 根节点为目标部门自身（`org_tree.path` + `total_cnt` + `manager`）
2. 一级部门已按人数降序排列（工具内部已排序），**直接按 children 数组顺序输出**
3. 下辖部门已按人数降序排列（工具内部已排序），**直接按 children 数组顺序输出**
4. 无下辖部门时，树结构仅显示目标部门自身
5. 负责人为空时显示"暂无"，职级为空时显示"未知"
6. 末级用 `└─`，中间用 `├─`
7. **截断规则**：当 `org_tree.two_level_only = true` 时，树结构只展示两级，不展示第三级。用户追问时可展开
8. `org_tree.children` 中每个部门的 `emp_cnt` 是该部门的**汇总人数**（含其下属所有层级的人员）
9. 不使用"子部门"、"孙部门"、"下辖部门"、"直接下属"等层级术语，树形结构本身已表达层级关系
10. **部门名加粗**（`**部门名**`），**人名加超链接**（`[姓名](链接)`）

---

## 四、🔴 红线规则（输出前必须逐条校验）

**红线 1：禁止篡改工具返回的任何数据**

工具返回的所有内容是**唯一权威数据源**，严禁篡改、重新计算或重新格式化。

**红线 2：禁止编造工具未返回的衍生指标**

只能引用工具返回的原始数字和已有指标名称。

**红线 3：禁止跨部门绝对评价**

**红线 4：禁止自动生成图表**

**红线 5：数值精度必须与工具返回的原始数据完全一致**

**红线 6：禁止暴露技术细节**

不得出现表名、字段名、SQL 语句等技术信息。

### ⛔ 输出前红线自查清单

- [ ] **无数据篡改**：每一处数字是否与工具返回的原始数据完全一致？
- [ ] **零值已隐藏**：值为 0 的指标行是否已隐藏？
- [ ] **无技术细节**：是否出现表名、字段名、SQL 等技术信息？
- [ ] **负责人为空已处理**：name/position/level 为空时是否显示"暂无"/"未知"？
- [ ] **无层级术语**：是否避免了"子部门"、"孙部门"、"下辖部门"等术语？

---

## 五、边界情况处理

| 场景 | 处理方式 |
|-|-|
| code=4041 | 输出"未找到部门「{名称}」，请确认部门名称" |
| code=4221 | 展示候选列表让用户选择，禁止自动选择 |
| code=4031/4032 | 输出权限拒绝话术，禁止重试 |
| code=5001 | 重试 1 次，仍失败则提示稍后再试 |
| children 为空 | 树结构仅显示目标部门自身，摘要标注"无下辖子部门" |
