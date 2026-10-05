"""jsonquery.py — 对 JSON 数据做规则化自然语言查询（零第三方依赖）。

数据约定：顶层是 list[dict]（记录数组）。
支持的简单意图：
- 过滤（where）：
    价格大于100 / 评分高于4 / 数量<5 / 地区是华东 / name等于apple / 包含键盘
- 选择（select）：
    只列出 title、只要 name price、返回 name 和 price
解析成 (filters, fields)，对记录数组过滤后投影字段。
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

# 字段中文名 -> 记录里的键名
FIELD_ALIASES = {
    "名称": "name", "名字": "name", "标题": "title", "title": "title",
    "价格": "price", "售价": "price", "price": "price",
    "评分": "rating", "rating": "rating",
    "数量": "qty", "库存": "qty", "qty": "qty",
    "地区": "region", "区域": "region", "region": "region",
    "类别": "category", "category": "category",
}


def _resolve_field(token: str) -> str | None:
    token = token.strip()
    return FIELD_ALIASES.get(token)  # 未知词不视为字段


class JsonNLQuery:
    def __init__(self, data: List[Dict[str, Any]]) -> None:
        if not isinstance(data, list):
            raise ValueError("顶层数据必须是记录数组（list[dict]）")
        self.data = data

    # ---------- 过滤条件解析 ----------
    def parse_filters(self, q: str) -> List[Tuple[str, str, Any]]:
        """返回 [(field, op, value), ...]。op ∈ {>,<,>=,<=,=,contains}。"""
        conds: List[Tuple[str, str, Any]] = []
        # 数值比较：字段 大于/高于/超过/>=/> number
        for m in re.finditer(
            r"(价格|售价|评分|数量|库存|price|rating|qty)\s*(大于|高于|超过|>=|>)\s*(\d+(?:\.\d+)?)",
                q):
            conds.append((FIELD_ALIASES.get(m.group(1), m.group(1)), ">", float(m.group(3))))
        for m in re.finditer(
            r"(价格|售价|评分|数量|库存|price|rating|qty)\s*(小于|低于|少于|<=|<)\s*(\d+(?:\.\d+)?)",
                q):
            conds.append((FIELD_ALIASES.get(m.group(1), m.group(1)), "<", float(m.group(3))))
        # 相等/包含：字段 是/等于/为 值；或 值在前：华东地区 / 华东
        for m in re.finditer(
            r"(地区|区域|类别)\s*(是|等于|为|=)\s*([一-鿿A-Za-z0-9]+)",
                q):
            field = FIELD_ALIASES.get(m.group(1), m.group(1))
            conds.append((field, "=", m.group(3)))
        for m in re.finditer(r"([一-鿿]{2})地区", q):
            conds.append(("region", "=", m.group(1)))
        m = re.search(r"包含([一-鿿A-Za-z0-9]+)", q)
        if m:
            conds.append(("name", "contains", m.group(1)))
        return conds

    @staticmethod
    def _match(record: Dict[str, Any], conds) -> bool:
        for field, op, value in conds:
            rv = record.get(field)
            if rv is None:
                return False
            if op in (">", "<"):
                try:
                    rv_num = float(rv)
                except (TypeError, ValueError):
                    return False
                if op == ">" and not (rv_num > value):
                    return False
                if op == "<" and not (rv_num < value):
                    return False
            elif op == "=":
                if str(rv) != str(value):
                    return False
            elif op == "contains":
                if str(value) not in str(rv):
                    return False
        return True

    # ---------- 选择字段解析 ----------
    def parse_fields(self, q: str) -> List[str] | None:
        """若问题要求只列某些字段，返回字段列表；否则 None 表示整行。
        取动词（列出/只要/返回/显示）之后、且尽量在"的"之后的部分作为字段。"""
        vm = re.search(r"(列出|列出|只要|只取|返回|显示)\s*(.+)", q)
        if not vm:
            return None
        tail = vm.group(2)
        if "的" in tail:
            tail = tail.split("的", 1)[1]
        tokens = re.split(r"[和,，、\s]+", tail.strip())
        fields = [f for f in (_resolve_field(t) for t in tokens) if f]
        return fields or None

    def query(self, q: str) -> Dict:
        conds = self.parse_filters(q)
        fields = self.parse_fields(q)
        matched = [r for r in self.data if self._match(r, conds)]
        if fields:
            projected = [{f: r.get(f) for f in fields} for r in matched]
        else:
            projected = matched
        return {"filters": conds, "fields": fields, "count": len(projected),
                "results": projected}


# 内置样例 JSON（无 key 即可跑）。
SAMPLE_JSON = [
    {"name": "机械键盘", "price": 299, "rating": 4.6, "qty": 50, "region": "华东", "category": "外设"},
    {"name": "无线鼠标", "price": 89, "rating": 4.2, "qty": 160, "region": "华南", "category": "外设"},
    {"name": "显示器", "price": 1299, "rating": 4.8, "qty": 10, "region": "华东", "category": "显示"},
    {"name": "USB 线", "price": 19, "rating": 3.9, "qty": 300, "region": "华南", "category": "配件"},
]
