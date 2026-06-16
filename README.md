# Smart Code Reviewer

> AI-powered code review agent: **AST static analysis + GPT-4 semantic review** — detects bugs, security flaws, complexity issues, and suggests fixes

---

## How It Was Built

Two-layer review system:
1. **AST Analyzer** — pure Python AST parsing detects: cyclomatic complexity, security anti-patterns (eval/exec/hardcoded secrets/shell injection), style issues. Zero API calls, instant.
2. **GPT-4 Review Agent** — receives static analysis results + code, performs semantic reasoning about logic bugs, design patterns, performance, and generates a refactored snippet.

## How to Run

```bash
git clone https://github.com/namankudesia/smart-code-reviewer.git
cd smart-code-reviewer
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY
uvicorn main:app --reload --port 8002
```

```bash
curl -X POST http://localhost:8002/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def login(user, pwd):\n  if pwd == \"admin123\":\n    return True", "language": "python"}'
```

> Built by [Naman Kudesia](https://github.com/namankudesia)
