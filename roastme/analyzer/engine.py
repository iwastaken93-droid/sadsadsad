"""Core static analysis engine."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Sequence


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Category(str, Enum):
    COMPLEXITY = "complexity"
    ANTI_PATTERN = "anti_pattern"
    SECURITY = "security"
    STYLE = "style"
    PERFORMANCE = "performance"
    NAMING = "naming"


@dataclass
class Finding:
    line: int
    end_line: int
    category: Category
    severity: Severity
    message: str
    code_snippet: str = ""
    roast_hint: str = ""


@dataclass
class AnalysisResult:
    file_path: str
    language: str
    findings: list[Finding] = field(default_factory=list)
    lines_of_code: int = 0
    function_count: int = 0
    class_count: int = 0
    avg_complexity: float = 0.0
    imports: list[str] = field(default_factory=list)

    @property
    def shame_score(self) -> int:
        score = 0
        for f in self.findings:
            if f.severity == Severity.CRITICAL:
                score += 15
            elif f.severity == Severity.WARNING:
                score += 8
            else:
                score += 3
        return min(score, 100)

    @property
    def summary(self) -> str:
        cats: dict[str, int] = {}
        for f in self.findings:
            cats[f.category.value] = cats.get(f.category.value, 0) + 1
        return (
            f"{len(self.findings)} findings across {self.lines_of_code} lines | "
            f"Shame Score: {self.shame_score}/100 | "
            + " | ".join(f"{k}: {v}" for k, v in cats.items())
        )


class CodeAnalyzer:
    """Multi-language static analysis with roast-ready hints."""

    SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"}

    def analyze(self, file_path: str, source: str) -> AnalysisResult:
        path = Path(file_path)
        ext = path.suffix.lower()
        self.language = self._detect_language(ext)

        if ext == ".py":
            return self._analyze_python(file_path, source)
        elif ext in {".js", ".ts", ".jsx", ".tsx"}:
            return self._analyze_js(file_path, source)
        else:
            return self._analyze_generic(file_path, source)

    def _detect_language(self, ext: str) -> str:
        return {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".jsx": "jsx", ".tsx": "tsx", ".go": "go",
            ".rs": "rust", ".java": "java",
        }.get(ext, "unknown")

    def _analyze_python(self, file_path: str, source: str) -> AnalysisResult:
        tree = ast.parse(source)
        lines = source.splitlines()
        result = AnalysisResult(file_path=file_path, language="python", lines_of_code=len(lines))

        # Count constructs
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result.function_count += 1
                self._check_function(node, lines, result)
            elif isinstance(node, ast.ClassDef):
                result.class_count += 1
                self._check_class(node, lines, result)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self._check_import(node, result)

        # Global checks
        self._check_security_patterns(source, lines, result)
        self._check_code_smells(source, lines, result)
        result.avg_complexity = self._calc_complexity(tree)
        return result

    def _check_function(self, node: ast.FunctionDef, lines: Sequence[str], result: AnalysisResult):
        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0

        # Too long
        if func_lines > 50:
            result.findings.append(Finding(
                line=node.lineno, end_line=node.end_lineno or node.lineno,
                category=Category.COMPLEXITY, severity=Severity.WARNING,
                message=f"Function '{node.name}' is {func_lines} lines long",
                code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                roast_hint="This function is longer than my patience. And I'm an AI.",
            ))

        # Too many args
        arg_count = len(node.args.args)
        if arg_count > 7:
            result.findings.append(Finding(
                line=node.lineno, end_line=node.lineno,
                category=Category.ANTI_PATTERN, severity=Severity.WARNING,
                message=f"Function '{node.name}' takes {arg_count} arguments",
                roast_hint="More args than a function has no business taking.",
            ))

        # Nested depth
        depth = self._get_max_nesting(node)
        if depth > 4:
            result.findings.append(Finding(
                line=node.lineno, end_line=node.end_lineno or node.lineno,
                category=Category.COMPLEXITY, severity=Severity.CRITICAL,
                message=f"Function '{node.name}' has nesting depth {depth}",
                roast_hint="Inception called. They want their nesting back.",
            ))

        # TODO/FIXME
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                if any(tag in child.value.upper() for tag in ("TODO", "FIXME", "HACK", "XXX")):
                    result.findings.append(Finding(
                        line=child.lineno, end_line=child.end_lineno or child.lineno,
                        category=Category.ANTI_PATTERN, severity=Severity.INFO,
                        message=f"Found TODO/FIXME: {child.value[:60]}",
                        roast_hint="Leaving TODOs like breadcrumbs for future you to cry over.",
                    ))

    def _check_class(self, node: ast.ClassDef, lines: Sequence[str], result: AnalysisResult):
        method_count = sum(1 for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)))
        if method_count > 20:
            result.findings.append(Finding(
                line=node.lineno, end_line=node.lineno,
                category=Category.ANTI_PATTERN, severity=Severity.WARNING,
                message=f"Class '{node.name}' has {method_count} methods",
                roast_hint="This class does everything except your laundry.",
            ))

    def _check_import(self, node, result: AnalysisResult):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.imports.append(node.module)

    def _check_security_patterns(self, source: str, lines: Sequence[str], result: AnalysisResult):
        patterns = [
            (r"eval\s*\(", "Use of eval() — what could go wrong?", "eval is how you give hackers a welcome mat."),
            (r"exec\s*\(", "Use of exec() — living dangerously", "exec() is the 'sure, I'll trust user input' of code."),
            (r"subprocess\..*shell\s*=\s*True", "Shell=True — command injection waiting to happen", "shell=True is basically `sudo rm -rf /` with extra steps."),
            (r"password\s*=\s*['\"]", "Hardcoded password detected", "Hardcoded passwords: because who needs security anyway?"),
            (r"secret\s*=\s*['\"]", "Hardcoded secret detected", "Putting secrets in code is like putting your diary on a billboard."),
            (r"SELECT\s+.*\+.*FROM", "Possible SQL injection — string concat in SQL", "String concatenation in SQL queries. Bobby Tables sends his regards."),
            (r"pickle\.loads?\(", "Pickle usage — arbitrary code execution risk", "pickle.loads() is how you turn your app into a reverse shell."),
            (r"assert\s+", "Assert in production code", "assert statements: great for debugging, great for production crashes too."),
            (r"except\s*:", "Bare except clause — catching everything including KeyboardInterrupt", "Bare except: because why would you ever want to know what went wrong?"),
            (r"import\s+wildcard|from\s+\w+\s+import\s+\*", "Wildcard import — namespace pollution", "Wildcard imports: making everyone's life harder since forever."),
        ]
        for i, line in enumerate(lines, 1):
            for pattern, msg, roast in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result.findings.append(Finding(
                        line=i, end_line=i,
                        category=Category.SECURITY, severity=Severity.CRITICAL,
                        message=msg, code_snippet=line.strip(),
                        roast_hint=roast,
                    ))

    def _check_code_smells(self, source: str, lines: Sequence[str], result: AnalysisResult):
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Line too long
            if len(line) > 120:
                result.findings.append(Finding(
                    line=i, end_line=i,
                    category=Category.STYLE, severity=Severity.INFO,
                    message=f"Line is {len(line)} characters long",
                    code_snippet=stripped[:80],
                    roast_hint="This line is longer than most novels' sentences.",
                ))
            # Magic numbers
            if re.search(r"(?<![.\w])\b(?!0|1\b)\d{2,}\b", stripped) and not stripped.startswith("#"):
                if not any(kw in stripped for kw in ("import", "from", "return", "def", "class")):
                    result.findings.append(Finding(
                        line=i, end_line=i,
                        category=Category.ANTI_PATTERN, severity=Severity.INFO,
                        message="Magic number detected",
                        code_snippet=stripped[:80],
                        roast_hint="Magic numbers: because future you loves a mystery.",
                    ))

    def _calc_complexity(self, tree: ast.AST) -> float:
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        max_lines = max((getattr(n, "end_lineno", None) or 0) for n in ast.walk(tree)) or 1
        return round(complexity / (max_lines / 50), 2)

    def _get_max_nesting(self, node: ast.AST, depth: int = 0) -> int:
        max_d = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.With, ast.Try)):
                max_d = max(max_d, self._get_max_nesting(child, depth + 1))
            else:
                max_d = max(max_d, self._get_max_nesting(child, depth))
        return max_d

    def _analyze_js(self, file_path: str, source: str) -> AnalysisResult:
        lines = source.splitlines()
        result = AnalysisResult(file_path=file_path, language="javascript", lines_of_code=len(lines))

        # Count functions
        func_pattern = re.compile(r"(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>|def\s+\w+)")
        result.function_count = len(func_pattern.findall(source))

        # Count classes
        result.class_count = len(re.findall(r"\bclass\s+\w+", source))

        # Security patterns
        js_patterns = [
            (r"eval\s*\(", "eval() usage — code injection risk"),
            (r"innerHTML\s*=", "innerHTML assignment — XSS vulnerability"),
            (r"document\.write\s*\(", "document.write — deprecated and dangerous"),
            (r"new\s+Function\s*\(", "new Function() — basically eval"),
            (r"setTimeout\s*\(\s*['\"]", "setTimeout with string — implicit eval"),
            (r"setInterval\s*\(\s*['\"]", "setInterval with string — implicit eval"),
        ]
        for i, line in enumerate(lines, 1):
            for pattern, msg in js_patterns:
                if re.search(pattern, line):
                    result.findings.append(Finding(
                        line=i, end_line=i,
                        category=Category.SECURITY, severity=Severity.CRITICAL,
                        message=msg, code_snippet=line.strip()[:80],
                        roast_hint="Security vulnerability detected.",
                    ))

        # TODOs
        for i, line in enumerate(lines, 1):
            if re.search(r"//\s*(TODO|FIXME|HACK|XXX)", line):
                result.findings.append(Finding(
                    line=i, end_line=i,
                    category=Category.ANTI_PATTERN, severity=Severity.INFO,
                    message="TODO/FIXME found", code_snippet=line.strip()[:80],
                    roast_hint="Another TODO for the pile.",
                ))

        return result

    def _analyze_generic(self, file_path: str, source: str) -> AnalysisResult:
        lines = source.splitlines()
        result = AnalysisResult(file_path=file_path, language=self.language, lines_of_code=len(lines))
        result.function_count = len(re.findall(r"\b(def|func|function|fn)\s+\w+", source))
        result.class_count = len(re.findall(r"\b(class|struct|impl)\s+\w+", source))
        return result
