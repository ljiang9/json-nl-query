# json-nl-query

零第三方依赖的 JSON 自然语言查询：对记录数组（`list[dict]`）按规则解析**过滤条件（where）**与**选择字段（select）**并返回结果。

## 功能简介

- **数值过滤**：`价格大于100`、`评分低于4`、`数量少于50` → `>` / `<`；
- **相等过滤**：`地区是华东`、`类别=外设` → `=`；
- **包含过滤**：`包含键盘` → 子串匹配；
- **字段选择**：`列出...的名称和价格`、`只要 name price` → 只投影指定字段；
- 同时打印解析出的过滤条件与选择字段，规则透明可调试。

## 快速开始

```bash
# 内置样例 JSON（商品记录）
python3 cli.py "价格大于100的有哪些"
python3 cli.py "列出华东地区的名称和价格"
python3 cli.py "评分高于4.5"
python3 cli.py "包含键盘"

# 用自己的 JSON（顶层为记录数组）
python3 cli.py "价格大于100" --file data.json
```

代码调用：

```python
from jsonquery import JsonNLQuery
engine = JsonNLQuery([{"name": "a", "price": 10}, ...])
out = engine.query("价格大于5的名称")  # {filters, fields, count, results}
```

## 无 API key 如何运行

本项目**完全不需要 API key**，解析与查询全部本地完成。

## 目录说明

```
json-nl-query/
├── jsonquery.py            # 核心库：JsonNLQuery（parse_filters / parse_fields / query）
├── cli.py                  # 命令行入口（内置样例 JSON）
├── tests/test_jsonquery.py # unittest 测试
└── README.md
```

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT License，Copyright (c) 2026 ljiang9
