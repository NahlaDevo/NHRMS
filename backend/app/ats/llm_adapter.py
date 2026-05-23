"""
LLM scoring adapter — hot-swappable with the rule-based scorer.

Set LLM_PROVIDER env var to "openai", "anthropic", or leave unset for rule-based.
"""

import os
import json
import re
from typing import Optional, List

from backend.app.ats.ai_scoring import extract_skills, extract_experience_years, compute_keywords_match

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def score_cv_with_llm(cv_text: str, job_keywords: Optional[List[str]] = None) -> dict:
    """Score a CV using the configured LLM provider, falling back to rule-based."""
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return _score_with_openai(cv_text, job_keywords)
    elif LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        return _score_with_anthropic(cv_text, job_keywords)
    else:
        from backend.app.ats.ai_scoring import score_cv
        return score_cv(cv_text, job_keywords)


def _score_with_openai(cv_text: str, job_keywords: Optional[List[str]] = None) -> dict:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        prompt = _build_llm_prompt(cv_text, job_keywords)
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        return _parse_llm_response(content, cv_text, job_keywords)
    except Exception as e:
        from backend.app.utils.helpers import logger
        logger.warning(f"OpenAI scoring failed, falling back to rule-based: {e}")
        from backend.app.ats.ai_scoring import score_cv
        return score_cv(cv_text, job_keywords)


def _score_with_anthropic(cv_text: str, job_keywords: Optional[List[str]] = None) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = _build_llm_prompt(cv_text, job_keywords)
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.content[0].text
        return _parse_llm_response(content, cv_text, job_keywords)
    except Exception as e:
        from backend.app.utils.helpers import logger
        logger.warning(f"Anthropic scoring failed, falling back to rule-based: {e}")
        from backend.app.ats.ai_scoring import score_cv
        return score_cv(cv_text, job_keywords)


def _build_llm_prompt(cv_text: str, job_keywords: Optional[List[str]] = None) -> str:
    prompt = (
        "You are an expert HR evaluator. Analyze this CV and return a JSON object with:\n"
        '- "score": number 0-100 overall fit,\n'
        '- "skills": array of strings (top skills found),\n'
        '- "experience_years": number (estimated years of experience),\n'
        '- "strengths": array of strings (key strengths),\n'
        '- "gaps": array of strings (missing qualifications),\n'
        '- "recommendation": "strong_hire" | "hire" | "maybe" | "pass"\n\n'
        f"CV TEXT:\n{cv_text[:8000]}\n"
    )
    if job_keywords:
        prompt += f"\nJOB KEYWORDS: {', '.join(job_keywords)}\n"
    prompt += "\nRespond with ONLY valid JSON."
    return prompt


def _parse_llm_response(content: str, cv_text: str, job_keywords: Optional[List[str]] = None) -> dict:
    try:
        result = json.loads(content)
        return {
            "score": round(min(float(result.get("score", 0)), 100), 2),
            "skills": result.get("skills", extract_skills(cv_text)),
            "experience_years": float(result.get("experience_years", extract_experience_years(cv_text))),
            "tech_skills_match": 0.0,
            "keywords_match": compute_keywords_match(cv_text, job_keywords or []) * 100,
            "experience_score": 0.0,
            "strengths": result.get("strengths", []),
            "gaps": result.get("gaps", []),
            "recommendation": result.get("recommendation", "maybe"),
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        from backend.app.ats.ai_scoring import score_cv
        return score_cv(cv_text, job_keywords)
