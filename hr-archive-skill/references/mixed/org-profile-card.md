---
name: org-profile-card
description: >
  组织档案跳转卡片。当 routing-mixed.md §2.1a 命中"组织档案"意图时加载本文件，
  指导 LLM 解析员工锚点并发送一张带跳转按钮的飞书交互卡片。
---

# 组织档案跳转卡片（ORG_PROFILE_CARD）

> **职责**：用户查询"XX的组织档案"时，解析员工锚点，发送一张飞书交互卡片，引导用户跳转至组织档案系统。

---

## 一、员工锚点解析

从用户问句中提取员工标识，调用 `es_query` 获取 `real_name` 和 `oprid`。

### 1.1 识别员工标识

| 用户输入 | 标识类型 | 示例 |
|---------|---------|------|
| 中文姓名 | `real_name` | "张冰的组织档案" → `"张冰"` |
| 英文账号 | `oprid` | "zhangbing5的组织档案" → `"zhangbing5"` |
| 数字工号 | `emp_id` | "35136的组织档案" → `"35136"` |

### 1.2 调用 es_query 解析

根据标识类型选择对应的 DSL：

**中文姓名**：
```bash
mcporter call hr_talent_claw_test_v1.es_query \
  dsl='{"query":{"bool":{"filter":[{"term":{"real_name.keyword":"张冰"}}]}},"_source":["real_name","oprid"],"size":3}' \
  include_sensitive_data=false
```

**英文账号（oprid）**：
```bash
mcporter call hr_talent_claw_test_v1.es_query \
  dsl='{"query":{"bool":{"filter":[{"term":{"oprid":"zhangbing5"}}]}},"_source":["real_name","oprid"],"size":1}' \
  include_sensitive_data=false
```

**数字工号（emp_id）**：
```bash
mcporter call hr_talent_claw_test_v1.es_query \
  dsl='{"query":{"bool":{"filter":[{"term":{"emp_id":"35136"}}]}},"_source":["real_name","oprid"],"size":1}' \
  include_sensitive_data=false
```

### 1.3 解析返回结果

从 ES 返回的 hits 中提取：
- `hits[0]._source.real_name` → 用于卡片标题和按钮文案
- `hits[0]._source.oprid` → 用于 URL 参数

### 1.4 异常处理

| 场景 | 处理 |
|------|------|
| `hits.total.value == 0` | 展示"未找到员工: XXX"，引导检查姓名 |
| `hits.total.value > 1` | 列出候选让用户选择（禁止自动挑选） |
| `oprid == sender_id` | 引导至人才档案小程序（D22 自查拦截） |

---

## 二、卡片模板

使用飞书卡片 **schema 1.0**（schema 2.0 不支持 action 按钮）。

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "{real_name}的组织档案"},
    "template": "green"
  },
  "elements": [
    {
      "tag": "markdown",
      "content": "当前暂不支持组织档案查询，详情请移步至组织档案系统。"
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {"tag": "plain_text", "content": "{real_name}的组织档案"},
          "type": "primary",
          "url": "https://archive.hr.mioffice.cn/organize-profile?source=ai&userId={oprid}"
        }
      ]
    }
  ]
}
```

### 占位符说明

| 占位符 | 来源 | 说明 |
|--------|------|------|
| `{real_name}` | es_query 返回的员工中文姓名 | 卡片标题 + 按钮文案 |
| `{oprid}` | es_query 返回的员工英文账号 | URL 参数，非 emp_id 数字 |

---

## 三、发送流程

使用 `feishu_im_message` 工具直接发送卡片（与报告通道一致）：

1. 按 §二 模板组装卡片 JSON，填充 `{real_name}` 和 `{oprid}` 占位符
2. 将卡片 dict 序列化为 JSON 字符串
3. 调用 `feishu_im_message`：
   ```
   feishu_im_message(
     action="send",
     msg_type="interactive",
     receive_id=<runtime Chat ID>,
     content=<上一步组装的卡片 JSON 字符串>
   )
   ```

- `receive_id` 必须使用 runtime context 中的 Chat ID
- `content` 传完整的卡片 JSON 字符串（含 `config`、`header`、`elements`），不是裸 markdown

---

## 四、异常处理

| 场景 | 处理方式 |
|------|---------|
| es_query 调用失败 | 降级为纯文本引导：组织档案查询请移步至 https://archive.hr.mioffice.cn/organize-profile |
| `feishu_im_message` 发送失败 | 降级为纯文本引导 |
