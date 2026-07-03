# 飞书卡片发送函数

通过 `exec` 工具执行以下 Python 代码发送飞书交互卡片。

```python
import json, subprocess, os

def get_feishu_token():
    body = json.dumps({"app_id": os.environ.get("FEISHU_APP_ID"), "app_secret": os.environ.get("FEISHU_APP_SECRET")})
    r = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', body
    ], capture_output=True, text=True)
    return json.loads(r.stdout)["tenant_access_token"]

def send_card(card: dict, receive_id: str, token: str) -> dict:
    receive_id_type = "chat_id" if receive_id.startswith("oc_") else "open_id"
    payload = json.dumps({"receive_id": receive_id, "msg_type": "interactive", "content": json.dumps(card)})
    r = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', payload
    ], capture_output=True, text=True)
    return json.loads(r.stdout)
```

## 完整调用示例（每张卡片都按此模式发送）

假设 `cost_report` 工具返回的某个 section 为：
- `title`: "Q1：花了多少钱？超预算了吗？"
- `content`: "### 核心结论\n\n💰 26年累计总成本 100万...\n\n### 分析解读\n\n📌 1. ..."

则 `exec` 工具中的代码应为：

```python
token = get_feishu_token()

# card 的 body.elements[0].content 必须是填充后的纯 Markdown 文本
# 不是 JSON，不是 sections 原始数据，而是 section["content"] 经过填充占位提示后的 Markdown 字符串
card = {
    "schema": "2.0",
    "header": {
        "title": {"tag": "plain_text", "content": "Q1：花了多少钱？超预算了吗？"},
        "template": "purple"
    },
    "body": {
        "elements": [
            {"tag": "markdown", "content": "### 核心结论\n\n💰 26年累计总成本 100万...\n\n### 年度成本对比\n\n| 指标 | 当年 | 去年 |\n|...|...|...|\n\n### 分析解读\n\n📌 1. 累计总成本同比+5.3%..."}
        ]
    }
}

result = send_card(card, "oc_xxx", token)
print(json.dumps(result, ensure_ascii=False))
```

> **⚠️ 关键：`body.elements[0].content` 的值必须是一个包含完整报告内容的 Markdown 字符串。**
> 如果这个字段为空字符串 `""`、为 JSON 对象、或为 `"FILLED_CONTENT"` 占位符原文，则卡片发送后内容会显示为空或 JSON 乱码。

> **⚠️ 常见报错：`content is not a string in json format`**
> 飞书 API 要求请求体中的 `content` 字段是 **JSON 字符串**（双重序列化），不是 JSON 对象。
> `send_card` 函数中 `json.dumps(card)` 负责第一次序列化（卡片 dict → 字符串），外层 `json.dumps(...)` 负责第二次序列化（整个请求体 → 字符串）。
> 如果漏掉内层的 `json.dumps(card)`，直接把 card dict 放进 payload，就会触发此报错。
> **必须严格按照上方 `send_card` 函数的写法，不要自行修改 payload 的构造方式。**
