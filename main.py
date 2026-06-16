from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.agents.review_agent import CodeReviewAgent

app = FastAPI(title="Smart Code Reviewer", version="1.0.0",
              description="AI-powered code review: AST analysis + GPT-4 semantic review")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ReviewRequest(BaseModel):
    code: str
    language: str = "python"
    context: Optional[str] = ""

@app.post("/review")
async def review(req: ReviewRequest):
    agent = CodeReviewAgent()
    return agent.review(req.code, req.language, req.context or "")

@app.get("/")
async def root():
    return {"service": "Smart Code Reviewer", "docs": "/docs"}
