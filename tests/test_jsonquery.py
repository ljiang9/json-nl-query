import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jsonquery import JsonNLQuery, SAMPLE_JSON  # noqa: E402


class TestJsonNLQuery(unittest.TestCase):
    def setUp(self):
        self.engine = JsonNLQuery(SAMPLE_JSON)

    def test_greater_than(self):
        out = self.engine.query("价格大于100的有哪些")
        names = [r["name"] for r in out["results"]]
        self.assertIn("机械键盘", names)
        self.assertIn("显示器", names)
        self.assertNotIn("USB 线", names)

    def test_less_than(self):
        out = self.engine.query("评分低于4的")
        self.assertEqual(out["count"], 1)
        self.assertEqual(out["results"][0]["name"], "USB 线")

    def test_equality_region(self):
        out = self.engine.query("地区是华东")
        names = [r["name"] for r in out["results"]]
        self.assertEqual(set(names), {"机械键盘", "显示器"})

    def test_contains(self):
        out = self.engine.query("包含键盘")
        self.assertEqual(out["count"], 1)
        self.assertEqual(out["results"][0]["name"], "机械键盘")

    def test_select_fields(self):
        out = self.engine.query("列出华东地区的名称和价格")
        self.assertIsNotNone(out["fields"])
        for r in out["results"]:
            self.assertIn("name", r)
            self.assertIn("price", r)

    def test_no_filter_returns_all(self):
        out = self.engine.query("列出所有商品")
        self.assertEqual(out["count"], len(SAMPLE_JSON))

    def test_rejects_non_list(self):
        with self.assertRaises(ValueError):
            JsonNLQuery({"a": 1})


if __name__ == "__main__":
    unittest.main()
