"""
AI Code Review Agent: combines AST analysis + GPT-4 semantic review.
Produces structured, actionable code review comments.
"""
from __future__ import annotations
import json, os
from openai import OpenAI
from app.analyzer.ast_analyzer import PythonASTAnalyzer, AnalysisResult

REVIEW_PROMPT = """You are an expert senior software engineer conducting a thorough code review.

Static analysis found these issues:
{static_issues}

Now perform a semantic code review. Analyze for:
1. Logic bugs and edge cases
2. Performance bottlenecks (N+1 queries, unnecessary loops, missing caching)
3. Security vulnerabilities (injection, auth bypass, data exposure)
4. Design pattern violations (SOLID, DRY, YAGNI)
5. Missing error handling and logging
6. Test coverage gaps

Output ONLY valid JSON:
{{
  "overall_score": 0-100,
  "summary": "string",
  "critical_issues": [{{"line": 0, "issue": "string", "fix": "string"}}],
  "improvements": [{{"category": "string", "suggestion": "string"}}],
  "positive_aspects": ["string"],
  "refactored_snippet": "string or null"
}}"""

class CodeReviewAgent:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.analyzer = PythonASTAnalyzer()

    def review(self, code: str, language: str = "python", context: str = "") -> dict:
        static = self.analyzer.analyze(code)
        static_summary = "\n".join([
            f"Line {i.line}: [{i.severity.upper()}] {i.message}" for i in static.issues
        ]) or "No static issues found."

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a senior software engineer. Output only valid JSON."},
                {"role": "user", "content": REVIEW_PROMPT.format(static_issues=static_summary) +
                 f"\n\nCode to review:\n```{language}\n{code[:4000]}\n```\n\nContext: {context}"}
            ],
            temperature=0.2, max_tokens=2000,
            response_format={"type": "json_object"}
        )
        ai_review = json.loads(response.choices[0].message.content)
        return {
            "static_analysis": {
                "issues": [{"line": i.line, "severity": i.severity, "category": i.category,
                           "message": i.message, "suggestion": i.suggestion} for i in static.issues],
                "complexity_score": static.complexity_score,
                "security_score": static.security_score,
                "total_lines": static.total_lines
            },
            "ai_review": ai_review,
            "combined_score": (ai_review.get("overall_score", 50) + static.security_score) // 2
        }
