from polyglint.checkers.js_checker import (
    _parse_funcs,
    _check_func_naming,
    _check_func_params,
    _check_func_count,
)

F = "test.js"


def rules(violations):
    return [v.rule for v in violations]


class TestParseFuncs:
    def test_detects_function_declaration(self):
        lines = ["function foo(a, b) {"]
        funcs = _parse_funcs(lines)
        assert len(funcs) == 1
        assert funcs[0][3] == "foo"

    def test_detects_arrow_function(self):
        lines = ["const bar = (a, b) => {"]
        funcs = _parse_funcs(lines)
        assert len(funcs) == 1
        assert funcs[0][3] == "bar"

    def test_detects_async_function(self):
        lines = ["async function baz() {"]
        funcs = _parse_funcs(lines)
        assert len(funcs) == 1

    def test_no_function(self):
        lines = ["const x = 1;", "let y = 2;"]
        assert _parse_funcs(lines) == []


class TestFuncNaming:
    def test_name_too_short(self):
        funcs = [(1, 1, 5, "fn", [])]
        assert "C-F2" in rules(_check_func_naming(funcs, F))

    def test_non_camel_case(self):
        funcs = [(1, 1, 8, "my_func", [])]
        assert "C-F2" in rules(_check_func_naming(funcs, F))

    def test_valid_camel_case(self):
        funcs = [(1, 1, 10, "myFunc", [])]
        assert _check_func_naming(funcs, F) == []

    def test_message_non_camel(self):
        funcs = [(1, 1, 8, "my_func", [])]
        v = _check_func_naming(funcs, F)
        assert any("camelCase" in v2.message for v2 in v)


class TestFuncParams:
    def test_five_params_flagged(self):
        funcs = [(1, 1, 5, "foo", ["a", "b", "c", "d", "e"])]
        v = _check_func_params(funcs, F)
        assert len(v) == 1
        assert v[0].rule == "C-F5"

    def test_four_params_ok(self):
        funcs = [(1, 1, 5, "foo", ["a", "b", "c", "d"])]
        assert _check_func_params(funcs, F) == []

    def test_six_params_two_violations(self):
        funcs = [(1, 1, 5, "foo", ["a", "b", "c", "d", "e", "f"])]
        assert len(_check_func_params(funcs, F)) == 2


class TestFuncCount:
    def _make_funcs(self, n):
        return [(i, 1, 5, f"func_{i}", []) for i in range(1, n + 1)]

    def test_ten_functions_ok(self):
        assert _check_func_count(self._make_funcs(10), F) == []

    def test_eleven_functions_flagged(self):
        v = _check_func_count(self._make_funcs(11), F)
        assert len(v) == 1
        assert v[0].rule == "C-O3"
        assert "11th" in v[0].message
