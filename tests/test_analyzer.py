"""Tests for the static analysis engine."""
import pytest
from roastme.analyzer.engine import CodeAnalyzer, Category, Severity


@pytest.fixture
def analyzer():
    return CodeAnalyzer()


class TestPythonAnalysis:
    def test_detects_long_function(self, analyzer):
        source = """
def long_function():
""" + "\n    x = 1" * 60

        result = analyzer.analyze("test.py", source)
        assert any(
            f.category == Category.COMPLEXITY and "lines long" in f.message
            for f in result.findings
        )

    def test_detects_eval(self, analyzer):
        source = 'eval(user_input)\n'
        result = analyzer.analyze("test.py", source)
        assert any(f.category == Category.SECURITY for f in result.findings)

    def test_detects_hardcoded_password(self, analyzer):
        source = 'password = "super_secret_123"\n'
        result = analyzer.analyze("test.py", source)
        assert any(f.category == Category.SECURITY for f in result.findings)

    def test_detects_bare_except(self, analyzer):
        source = "try:\n    pass\nexcept:\n    pass\n"
        result = analyzer.analyze("test.py", source)
        assert any("Bare except" in f.message for f in result.findings)

    def test_detects_todo(self, analyzer):
        source = "# TODO: fix this later\nx = 1\n"
        result = analyzer.analyze("test.py", source)
        assert any("TODO" in f.message for f in result.findings)

    def test_counts_functions(self, analyzer):
        source = """
def foo():
    pass

def bar():
    pass

class Baz:
    def method(self):
        pass
"""
        result = analyzer.analyze("test.py", source)
        assert result.function_count == 3
        assert result.class_count == 1

    def test_clean_code_no_findings(self, analyzer):
        source = """
def greet(name: str) -> str:
    return f"Hello, {name}!"
"""
        result = analyzer.analyze("test.py", source)
        assert len(result.findings) == 0

    def test_shame_score_zero_for_clean(self, analyzer):
        source = "x = 1\n"
        result = analyzer.analyze("test.py", source)
        assert result.shame_score == 0

    def test_long_line_detected(self, analyzer):
        source = "x = " + "'a'" + " + 'b'" * 60 + "\n"
        result = analyzer.analyze("test.py", source)
        assert any("characters long" in f.message for f in result.findings)


class TestJSAnalysis:
    def test_detects_eval_js(self, analyzer):
        source = "eval(userInput);\n"
        result = analyzer.analyze("test.js", source)
        assert any(f.category == Category.SECURITY for f in result.findings)

    def test_detects_innerhtml(self, analyzer):
        source = "document.getElementById('x').innerHTML = userInput;\n"
        result = analyzer.analyze("test.html", source)
        assert any("XSS" in f.message for f in result.findings)

    def test_detects_todo_js(self, analyzer):
        source = "// TODO: refactor this mess\nconst x = 1;\n"
        result = analyzer.analyze("test.js", source)
        assert any("TODO" in f.message for f in result.findings)


class TestGenericAnalysis:
    def test_unknown_extension(self, analyzer):
        source = "fn main() {}\n"
        result = analyzer.analyze("test.rs", source)
        assert result.language == "rust"
        assert result.lines_of_code == 1
