"""AST-based static code analysis: detects complexity, dead code, and anti-patterns."""
import ast
import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class CodeIssue:
    line: int
    severity: str   # error | warning | info
    category: str   # complexity | security | style | performance
    message: str
    suggestion: str = ""

@dataclass
class AnalysisResult:
    language: str
    total_lines: int
    issues: List[CodeIssue] = field(default_factory=list)
    complexity_score: int = 0
    security_score: int = 100

class PythonASTAnalyzer:
    MAX_FUNCTION_LINES = 50
    MAX_COMPLEXITY = 10

    def analyze(self, code: str) -> AnalysisResult:
        result = AnalysisResult(language="python", total_lines=len(code.splitlines()))
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result.issues.append(CodeIssue(line=e.lineno or 0, severity="error",
                category="syntax", message=f"Syntax error: {e.msg}", suggestion="Fix syntax before reviewing"))
            return result

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function(node, result)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                pass  # could check for magic numbers

        self._check_security_patterns(code, result)
        result.complexity_score = len([i for i in result.issues if i.category == "complexity"])
        return result

    def _check_function(self, node, result: AnalysisResult):
        lines = (node.end_lineno or node.lineno) - node.lineno
        if lines > self.MAX_FUNCTION_LINES:
            result.issues.append(CodeIssue(
                line=node.lineno, severity="warning", category="complexity",
                message=f"Function '{node.name}' is {lines} lines long (max {self.MAX_FUNCTION_LINES})",
                suggestion="Break into smaller, focused functions following Single Responsibility Principle"))

        complexity = self._cyclomatic_complexity(node)
        if complexity > self.MAX_COMPLEXITY:
            result.issues.append(CodeIssue(
                line=node.lineno, severity="warning", category="complexity",
                message=f"Cyclomatic complexity of '{node.name}' is {complexity} (max {self.MAX_COMPLEXITY})",
                suggestion="Simplify branching logic or extract sub-functions"))

    def _cyclomatic_complexity(self, node) -> int:
        count = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                   ast.With, ast.Assert, ast.BoolOp)):
                count += 1
        return count

    def _check_security_patterns(self, code: str, result: AnalysisResult):
        patterns = [
            (r"eval\s*\(", "Dangerous eval() usage", "Use ast.literal_eval() or safer alternatives", "error", "security"),
            (r"exec\s*\(", "Dangerous exec() usage", "Avoid dynamic code execution", "error", "security"),
            (r"subprocess\.call\s*\(.*shell=True", "Shell injection risk with shell=True", "Use shell=False with list args", "error", "security"),
            (r"password\s*=\s*["']\S+["']", "Hardcoded password detected", "Use environment variables or secrets manager", "error", "security"),
            (r"SECRET.*=.*["']\S+["']", "Hardcoded secret detected", "Use os.getenv() or a secrets vault", "error", "security"),
            (r"TODO|FIXME|HACK", "Unresolved TODO/FIXME comment", "Address before production", "info", "style"),
        ]
        for pattern, msg, suggestion, severity, category in patterns:
            for i, line in enumerate(code.splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    result.issues.append(CodeIssue(line=i, severity=severity, category=category,
                                                     message=msg, suggestion=suggestion))
                    if category == "security":
                        result.security_score = max(0, result.security_score - 20)
