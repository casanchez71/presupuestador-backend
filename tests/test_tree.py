from app.tree import build_tree, get_parent_candidates, normalize_item_code, safe_float


class TestBuildTree:
    def test_empty_list(self):
        assert build_tree([]) == []

    def test_flat_roots(self):
        items = [
            {"id": "a", "parent_id": None, "description": "Root 1"},
            {"id": "b", "parent_id": None, "description": "Root 2"},
        ]
        tree = build_tree(items)
        assert len(tree) == 2
        assert tree[0]["children"] == []

    def test_nested(self, sample_items):
        tree = build_tree(sample_items)
        assert len(tree) == 2  # 2 root sections
        assert tree[0]["code"] == "1"
        assert len(tree[0]["children"]) == 2  # 1.1 and 1.2
        assert tree[1]["code"] == "2"
        assert len(tree[1]["children"]) == 1  # 2.1
        assert len(tree[1]["children"][0]["children"]) == 1  # 2.1.1

    def test_orphan_parent(self):
        items = [
            {"id": "a", "parent_id": "nonexistent", "description": "Orphan"},
        ]
        tree = build_tree(items)
        assert len(tree) == 0  # orphan with invalid parent_id


class TestNormalizeItemCode:
    def test_normal(self):
        assert normalize_item_code("1.1") == "1.1"

    def test_comma(self):
        assert normalize_item_code("1,2") == "1.2"

    def test_spaces(self):
        assert normalize_item_code(" 1. 2 ") == "1.2"

    def test_none(self):
        assert normalize_item_code(None) == ""

    def test_float_nan(self):
        import math
        assert normalize_item_code(float("nan")) == ""

    def test_trailing_dots(self):
        assert normalize_item_code("2.1.") == "2.1"


class TestSafeFloat:
    def test_int(self):
        assert safe_float(42) == 42.0

    def test_float(self):
        assert safe_float(3.14) == 3.14

    def test_string(self):
        assert safe_float("100") == 100.0

    def test_argentine_format(self):
        assert safe_float("1.500,50") == 1500.50

    def test_none(self):
        assert safe_float(None) is None

    def test_empty(self):
        assert safe_float("") is None

    def test_garbage(self):
        assert safe_float("abc") is None


class TestGetParentCandidates:
    def test_simple(self):
        assert get_parent_candidates("1.2.3") == ["1.2", "1"]

    def test_two_parts(self):
        assert get_parent_candidates("1.2") == ["1"]

    def test_single(self):
        assert get_parent_candidates("1") == []

    def test_empty(self):
        assert get_parent_candidates("") == []
