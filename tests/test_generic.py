from polyglint.checkers.generic_checks import (
    _check_empty_lines,
    _check_trailing_whitespace,
    _check_line_endings,
    _check_line_issues,
    _check_indentation,
)
from polyglint.checkers.paren_checks import _check_space_before_paren

F = "test.py"


def rules(violations):
    return [v.rule for v in violations]


def messages(violations):
    return [v.message for v in violations]


class TestEmptyLines:
    def test_leading_empty_line(self):
        lines = ["", "x = 1"]
        assert "C-G8" in rules(_check_empty_lines(lines, F))

    def test_trailing_empty_line(self):
        lines = ["x = 1", ""]
        assert "C-G8" in rules(_check_empty_lines(lines, F))

    def test_no_violation(self):
        lines = ["x = 1", "y = 2"]
        assert _check_empty_lines(lines, F) == []

    def test_all_empty_no_duplicate(self):
        lines = ["", "", ""]
        violations = _check_empty_lines(lines, F)
        assert len(violations) == 3
        assert all(v.line != violations[0].line or i == 0
                   for i, v in enumerate(violations))

    def test_leading_col_is_one(self):
        lines = ["", "x = 1"]
        v = _check_empty_lines(lines, F)[0]
        assert v.col == 1


class TestTrailingWhitespace:
    def test_single_trailing_space(self):
        lines = ["x = 1 "]
        v = _check_trailing_whitespace(lines, F)
        assert len(v) == 1
        assert v[0].message == "trailing space"

    def test_multiple_trailing_spaces(self):
        lines = ["x = 1   "]
        v = _check_trailing_whitespace(lines, F)
        assert v[0].message == "3 trailing spaces"

    def test_no_trailing_whitespace(self):
        lines = ["x = 1"]
        assert _check_trailing_whitespace(lines, F) == []

    def test_col_points_to_first_trailing(self):
        lines = ["abc  "]
        v = _check_trailing_whitespace(lines, F)[0]
        assert v.col == 4


class TestLineEndings:
    def test_cr_detected(self):
        content = "x = 1\r\ny = 2\n"
        v = _check_line_endings(content, F)
        assert len(v) == 1
        assert v[0].rule == "C-G6"

    def test_col_is_line_relative(self):
        content = "abc\r\n"
        v = _check_line_endings(content, F)
        assert v[0].col == 4

    def test_no_cr(self):
        content = "x = 1\ny = 2\n"
        assert _check_line_endings(content, F) == []

    def test_cr_on_second_line(self):
        content = "abc\ndef\r\n"
        v = _check_line_endings(content, F)
        assert v[0].line == 2
        assert v[0].col == 4


class TestLineIssues:
    def test_line_too_long(self):
        lines = ["x" * 81]
        content = "x" * 81 + "\n"
        v = _check_line_issues(lines, content, F)
        assert any(v2.rule == "C-F3" for v2 in v)

    def test_exactly_80_chars_ok(self):
        lines = ["x" * 80]
        content = "x" * 80 + "\n"
        v = _check_line_issues(lines, content, F)
        assert not any(v2.rule == "C-F3" for v2 in v)

    def test_missing_newline_eof(self):
        lines = ["x = 1"]
        content = "x = 1"
        v = _check_line_issues(lines, content, F)
        assert any(v2.rule == "C-A3" for v2 in v)

    def test_newline_eof_ok(self):
        lines = ["x = 1"]
        content = "x = 1\n"
        v = _check_line_issues(lines, content, F)
        assert not any(v2.rule == "C-A3" for v2 in v)

    def test_long_line_message(self):
        lines = ["x" * 85]
        content = "x" * 85 + "\n"
        v = _check_line_issues(lines, content, F)
        assert v[0].message == "85-character line"


class TestIndentation:
    def test_tab_indentation(self):
        lines = ["\tx = 1"]
        v = _check_indentation(lines, F)
        assert len(v) == 1
        assert "tab" in v[0].message

    def test_non_multiple_of_4(self):
        lines = ["   x = 1"]
        v = _check_indentation(lines, F)
        assert len(v) == 1
        assert "groups of 4" in v[0].message

    def test_valid_4_spaces(self):
        lines = ["    x = 1"]
        assert _check_indentation(lines, F) == []

    def test_valid_8_spaces(self):
        lines = ["        x = 1"]
        assert _check_indentation(lines, F) == []

    def test_no_indent_ok(self):
        lines = ["x = 1"]
        assert _check_indentation(lines, F) == []


class TestSpaceBeforeParen:
    def test_space_before_closing_paren(self):
        lines = ["foo( x )"]
        v = _check_space_before_paren(lines, F)
        assert len(v) == 1
        assert v[0].rule == "C-L3"

    def test_closing_paren_own_line_ok(self):
        lines = ["foo(", "    x", "    )"]
        assert _check_space_before_paren(lines, F) == []

    def test_no_space_before_paren_ok(self):
        lines = ["foo(x)"]
        assert _check_space_before_paren(lines, F) == []

    def test_space_in_comment_ignored(self):
        lines = ["x = 1  # foo( x )"]
        assert _check_space_before_paren(lines, F) == []

    def test_space_in_string_ignored(self):
        lines = ['x = "foo( x )"']
        assert _check_space_before_paren(lines, F) == []

    def test_col_points_to_space(self):
        lines = ["foo( x )"]
        v = _check_space_before_paren(lines, F)
        assert v[0].col == 7
