from polyglint.checkers.js_checker import (
    _parse_funcs,
    _check_func_naming,
    _check_func_params,
    _check_func_count,
    JsChecker,
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

    def test_non_snake_case(self):
        funcs = [(1, 1, 8, "myFunc", [])]
        assert "C-F2" in rules(_check_func_naming(funcs, F))

    def test_valid_snake_case(self):
        funcs = [(1, 1, 10, "my_func", [])]
        assert _check_func_naming(funcs, F) == []

    def test_message_non_snake(self):
        funcs = [(1, 1, 8, "myFunc", [])]
        v = _check_func_naming(funcs, F)
        assert any("snake" in v2.message for v2 in v)


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
        return JsChecker()._check_comments(lines, F)

    def test_inline_comment_flagged(self):
        lines = ["function foo() {", "    x = 1;  // bad", "}"]
        v = self._checker_comments(lines)
        assert len(v) == 1
        assert v[0].rule == "C-F8"

    def test_standalone_comment_inside_function_flagged(self):
        lines = ["function foo() {", "    // bad", "}"]
        v = self._checker_comments(lines)
        assert len(v) == 1

    def test_top_level_inline_comment_ok(self):
        lines = ["const x = 1;  // top level"]
        assert self._checker_comments(lines) == []

    def test_standalone_comment_top_level_ok(self):
        lines = ["// top level comment"]
        assert self._checker_comments(lines) == []

    def test_comment_in_string_ignored(self):
        lines = ["function foo() {", '    x = "val // not";', "}"]
        assert self._checker_comments(lines) == []


class TestCurlyBrackets:
    def _check(self, lines):
        return JsChecker()._check_curly_brackets(lines, F)

    def test_closing_brace_not_alone_flagged(self):
        lines = ["function foo()", "{", "    return 1;", "} return 0;"]
        v = self._check(lines)
        assert any(v2.rule == "C-L4" for v2 in v)

    def test_closing_brace_alone_ok(self):
        lines = ["function foo()", "{", "    return 1;", "}"]
        assert self._check(lines) == []

    def test_closing_else_ok(self):
        lines = ["} else {"]
        assert self._check(lines) == []

    def test_closing_catch_ok(self):
        lines = ["} catch (e) {"]
        assert self._check(lines) == []

    def test_closing_finally_ok(self):
        lines = ["} finally {"]
        assert self._check(lines) == []

    def test_function_brace_same_line_flagged(self):
        lines = ["function foo() {"]
        v = self._check(lines)
        assert any(v2.rule == "C-L4" for v2 in v)

    def test_function_brace_own_line_ok(self):
        lines = ["function foo()", "{"]
        assert self._check(lines) == []


class TestFuncLength:
    def _check(self, lines):
        return JsChecker()._check_func_length(lines, F)

    def test_function_within_limit_ok(self):
        lines = ["function foo()", "{"] + ["    x = 1;"] * 20 + ["}"]
        assert self._check(lines) == []

    def test_function_over_limit_flagged(self):
        lines = ["function foo()", "{"] + ["    x = 1;"] * 21 + ["}"]
        v = self._check(lines)
        assert any(v2.rule == "C-F4" for v2 in v)

    def test_violation_at_21st_body_line(self):
        lines = ["function foo() {"] + ["    x = 1;"] * 21 + ["}"]
        v = self._check(lines)
        assert v[0].line == 22


class TestFuncSeparation:
    def _check(self, lines):
        return JsChecker()._check_func_separation(lines, F)

    def test_missing_empty_line_flagged(self):
        lines = [
            "function foo()", "{", "    return 1;", "}",
            "function bar()", "{", "    return 2;", "}",
        ]
        v = self._check(lines)
        assert any(v2.rule == "C-G2" for v2 in v)

    def test_empty_line_between_ok(self):
        lines = [
            "function foo()", "{", "    return 1;", "}",
            "",
            "function bar()", "{", "    return 2;", "}",
        ]
        assert self._check(lines) == []

    def test_single_function_ok(self):
        lines = ["function foo()", "{", "    return 1;", "}"]
        assert self._check(lines) == []
