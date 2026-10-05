#!/usr/bin/env python3
"""cli.py — json-nl-query 命令行入口。

用法：python3 cli.py "评分高于4.5的有哪些"
     python3 cli.py "列出华东地区的名称和价格"
     python3 cli.py "价格大于100且包含键盘"

无 key 即用；内置样例 JSON。
"""
from __future__ import annotations

import argparse
import json
import sys

from jsonquery import SAMPLE_JSON, JsonNLQuery


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="JSON 自然语言查询（规则解析 where/select）")
    p.add_argument("question", nargs="?", help="自然语言问题")
    p.add_argument("--file", help="JSON 文件路径（顶层为记录数组），缺省用内置样例")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = SAMPLE_JSON

    engine = JsonNLQuery(data)
    if not args.question:
        print("未提供问题。示例：python3 cli.py \"评分高于4.5的有哪些\"")
        return 0

    out = engine.query(args.question)
    print(f"问题：{args.question}")
    print(f"过滤条件：{out['filters']}")
    print(f"选择字段：{out['fields']}")
    print(f"命中 {out['count']} 条：")
    for r in out["results"]:
        print("  ", json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
