from polyglint.checkers.lua_checker import (
    _parse_funcs,
    _check_func_naming,
    _check_func_params,
    _check_func_count,
    LuaChecker,
)

F = "test.lua"


def rules(violations):
    return [v.rule for v in violations]


class TestParseFuncs:
    def test_detects_simple_function(self):
        lines = ["function foo(a, b)"]
        funcs = _parse_funcs(lines)
        assert len(funcs) == 1
        assert funcs[0][3] == "foo"

    def test_detects_local_function(self):
        lines = ["local function bar()"]
        funcs = _parse_funcs(lines)
        assert len(funcs) == 1

    def test_detects_method(self):
        lines = ["function obj:method(a)"]
        funcs = _parse_funcs(lines)
        assert funcs[0][3] == "method"

    def test_no_function(self):
        lines = ["x = 1", "y = 2"]
        assert _parse_funcs(lines) == []


class TestFuncNaming:
    def test_name_too_short(self):
        funcs = [(1, 1, 5, "fn", [])]
        assert "C-F2" in rules(_check_func_naming(funcs, F))

    def test_non_snake_case(self):
        funcs = [(1, 1, 8, "myFunc", [])]
        assert "C-F2" in rules(_check_func_naming(funcs, F))

    def test_valid_name(self):
        funcs = [(1, 1, 10, "my_func", [])]
        assert _check_func_naming(funcs, F) == []

    def test_message_too_short(self):
        funcs = [(1, 1, 5, "fn", [])]
        v = _check_func_naming(funcs, F)
        assert any("too short" in v2.message for v2 in v)


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


class TestComments:
    def _checker_comments(self, lines):
        return LuaChecker()._check_comments(lines, F)

    def test_inline_comment_flagged(self):
        lines = ["function foo()", "    x = 1  -- bad", "end"]
        v = self._checker_comments(lines)
        assert len(v) == 1
        assert v[0].rule == "C-F8"

    def test_standalone_comment_inside_function_flagged(self):
        lines = ["function foo()", "    -- bad", "end"]
        v = self._checker_comments(lines)
        assert len(v) == 1

    def test_top_level_inline_comment_ok(self):
        lines = ["x = 1  -- top level"]
        assert self._checker_comments(lines) == []

    def test_standalone_comment_top_level_ok(self):
        lines = ["-- top level comment"]
        assert self._checker_comments(lines) == []

    def test_comment_in_string_ignored(self):
        lines = ["function foo()", '    x = "val -- not"', "end"]
        assert self._checker_comments(lines) == []
