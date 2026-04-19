import ast
import pytest
from polyglint.checkers.python_checker import (
    _check_func_naming,
    _check_func_params,
    _check_func_length,
    _check_func_count,
)

F = "test.py"


def parse(source):
    return ast.parse(source)


def rules(violations):
    return [v.rule for v in violations]


class TestFuncNaming:
    def test_name_too_short(self):
        tree = parse("def fn(): pass")
        assert "C-F2" in rules(_check_func_naming(tree, F))

    def test_non_snake_case(self):
        tree = parse("def myFunc(): pass")
        assert "C-F2" in rules(_check_func_naming(tree, F))

    def test_valid_name(self):
        tree = parse("def my_func(): pass")
        assert _check_func_naming(tree, F) == []

    def test_async_function_checked(self):
        tree = parse("async def fn(): pass")
        assert "C-F2" in rules(_check_func_naming(tree, F))

    def test_underscore_prefix_valid(self):
        tree = parse("def _my_func(): pass")
        assert _check_func_naming(tree, F) == []


class TestFuncParams:
    def test_five_params_flagged(self):
        tree = parse("def foo(a, b, c, d, e): pass")
        v = _check_func_params(tree, F)
        assert len(v) == 1
        assert v[0].rule == "C-F5"
        assert "5th" in v[0].message

    def test_four_params_ok(self):
        tree = parse("def foo(a, b, c, d): pass")
        assert _check_func_params(tree, F) == []

    def test_six_params_two_violations(self):
        tree = parse("def foo(a, b, c, d, e, f): pass")
        v = _check_func_params(tree, F)
        assert len(v) == 2

    def test_async_params_checked(self):
        tree = parse("async def foo(a, b, c, d, e): pass")
        assert "C-F5" in rules(_check_func_params(tree, F))


class TestFuncLength:
    def test_function_within_limit(self):
        body = "\n".join(["    x = 1"] * 20)
        tree = parse(f"def foo():\n{body}")
        assert _check_func_length(tree, F) == []

    def test_function_exceeds_limit(self):
        body = "\n".join(["    x = 1"] * 21)
        tree = parse(f"def foo():\n{body}")
        v = _check_func_length(tree, F)
        assert len(v) == 1
        assert v[0].rule == "C-F4"
        assert "21st" in v[0].message

    def test_async_function_length_checked(self):
        body = "\n".join(["    x = 1"] * 21)
        tree = parse(f"async def foo():\n{body}")
        assert "C-F4" in rules(_check_func_length(tree, F))


class TestFuncCount:
    def _make_funcs(self, n):
        return "\n".join(f"def func_{i}(): pass" for i in range(n))

    def test_five_module_level_ok(self):
        tree = parse(self._make_funcs(5))
        assert _check_func_count(tree, F) == []

    def test_eleven_functions_flagged(self):
        tree = parse(self._make_funcs(11))
        v = _check_func_count(tree, F)
        assert any(v2.rule == "C-O3" for v2 in v)

    def test_six_non_static_flagged(self):
        funcs = self._make_funcs(6)
        tree = parse(funcs)
        v = _check_func_count(tree, F)
        assert any("non-static" in v2.message for v2 in v)

    def test_five_non_static_ok(self):
        funcs = self._make_funcs(5)
        tree = parse(funcs)
        assert _check_func_count(tree, F) == []
