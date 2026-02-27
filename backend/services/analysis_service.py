import os
import requests
from config import Config
import json
import asyncio

ANALYSIS_PROMPT = """You are an expert Google AdSense Evaluator.
Evaluate the following user article against the top-matching internet reference article.
The exact vector mathematical similarity score is {sim_pct:.1f}%.

USER ARTICLE:
{article}

TOP REFERENCE (investigating for plagiarism/duplication):
{reference}

Analyze:
1. Idea Similarity (Low, Medium, High)
2. Value Addition (Does the user's article add unique perspectives or examples?)
3. AdSense Risk (Low, Medium, High)

Return ONLY a JSON dictionary with these keys: "idea_similarity", "value_addition", "adsense_risk", "analysis_summary"."""


def _call_openai_compatible(api_url: str, api_key: str, model: str, prompt: str) -> dict:
    """Generic OpenAI-compatible API caller (works for DeepSeek + Groq)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return json.loads(content.strip())


async def analyze_originality(article: str, top_reference: dict, similarity_score: float) -> dict:
    """
    CRE Analysis Engine — DeepSeek primary, Groq fallback.
    Uses both to deeply analyze Idea Similarity and Value Addition.
    """
    ref_dict = top_reference or {}
    prompt = ANALYSIS_PROMPT.format(
        sim_pct=similarity_score * 100,
        article=article[:1500],
        reference=ref_dict.get('content', 'No reference article found.')[:1500]
    )

    # Try DeepSeek first
    deepseek_key = Config.DEEPSEEK_API_KEY
    if deepseek_key and "YOUR" not in deepseek_key:
        try:
            print("[Analysis] Trying DeepSeek...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://api.deepseek.com/v1/chat/completions",
                deepseek_key,
                "deepseek-chat",
                prompt
            )
            print("[Analysis] DeepSeek succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] DeepSeek failed: {e}")

    # Fallback to Groq
    groq_key = Config.GROQ_API_KEY
    if groq_key and "gsk_" in groq_key:
        try:
            print("[Analysis] Trying Groq fallback...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://api.groq.com/openai/v1/chat/completions",
                groq_key,
                "llama-3.3-70b-versatile",
                prompt
            )
            print("[Analysis] Groq succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] Groq failed: {e}")

    # Fallback to OpenRouter
    openrouter_key = Config.OPENROUTER_API_KEY
    if openrouter_key and "sk-or" in openrouter_key:
        try:
            print("[Analysis] Trying OpenRouter fallback...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://openrouter.ai/api/v1/chat/completions",
                openrouter_key,
                "meta-llama/llama-3.3-70b-instruct:free",
                prompt
            )
            print("[Analysis] OpenRouter succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] OpenRouter failed: {e}")

    print("[Analysis] All LLMs failed — returning basic analysis")
    return {
        "idea_similarity": "Unknown",
        "value_addition": "Unknown",
        "adsense_risk": "Unknown",
        "analysis_summary": "Analysis unavailable — no LLM API responded."
    }
