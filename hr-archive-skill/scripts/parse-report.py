#!/usr/bin/env python3
# AIGC START
"""将 onboarding_report JSON 拆分为 meta + D1~D5 单独文件，避免单次 read 超限。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DIMENSION_KEYS = (
    "d1_overall",
    "dep_impact",
    "d2_profile",
    "d3_probation",
    "d4_retention",
    "d5_attribution",
)
META_KEYS = ("dept_id", "dept_name", "dept_field", "time_range")


def _load_data(payload: dict) -> dict:
    if isinstance(payload.get("data"), dict):
        return payload["data"]
    if any(k in payload for k in DIMENSION_KEYS):
        return payload
    raise ValueError("未找到 data 或 D1~D5 维度块，请确认输入为 onboarding_report 成功响应")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: parse-report.py <input.json> [output_dir]\n"
            "  output_dir 默认 /tmp/report-parts",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/report-parts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with input_file.open(encoding="utf-8-sig") as f:
        data = _load_data(json.load(f))

    meta = {k: data.get(k) for k in META_KEYS if k in data}
    meta_path = output_dir / "_meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"_meta: {len(json.dumps(meta, ensure_ascii=False))} chars → {meta_path}")

    for key in DIMENSION_KEYS:
        part = data.get(key, {})
        out_path = output_dir / f"{key}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(part, f, ensure_ascii=False, indent=2)
        size = len(json.dumps(part, ensure_ascii=False))
        print(f"{key}: {size} chars → {out_path}")


if __name__ == "__main__":
    main()
# AIGC END
