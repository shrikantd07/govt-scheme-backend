import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from engine import evaluate_eligibility, generate_conversational_explanation

app = FastAPI(
    title="Govt Scheme Matching Engine",
    description="Deterministic rule matching + Near-miss detection + LLM explanation layer"
)

# User Profile Schema
class UserProfile(BaseModel):
    age: int
    gender: str
    category: str
    occupation: str
    annual_income: int

@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Government Scheme Matching API is running smoothly!"
    }

@app.post("/match-schemes")
def match_schemes(profile: UserProfile):
    profile_dict = profile.model_dump()

    # 1. Deterministic Rule Matching & Near-Miss Evaluator
    qualified, near_misses = evaluate_eligibility(profile_dict)

    # 2. LLM Reasoning Layer
    ai_explanation = "LLM explanation disabled. Set GEMINI_API_KEY to activate."
    if os.environ.get("GEMINI_API_KEY"):
        try:
            ai_explanation = generate_conversational_explanation(
                user_profile=profile_dict,
                qualified=qualified,
                near_misses=near_misses
            )
        except Exception as e:
            ai_explanation = f"LLM generation failed: {str(e)}"

    return {
        "user_profile": profile_dict,
        "qualified_count": len(qualified),
        "near_miss_count": len(near_misses),
        "qualified_schemes": qualified,
        "near_miss_schemes": near_misses,
        "ai_reasoning": ai_explanation
    }