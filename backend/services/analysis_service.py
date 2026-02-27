import os
import requests
from config import Config
import json
import asyncio

ANALYSIS_PROMPT = """You are an expert plagiarism detection and content quality analysis system, equivalent to Google AdSense's internal content evaluator.

The exact mathematical cosine similarity score between the user's article and the top internet reference is {sim_pct:.1f}%.

USER ARTICLE:
{article}

TOP MATCHING REFERENCE (investigating for plagiarism/duplication):
{reference}

Perform a comprehensive multi-factor analysis across these 9 dimensions:

1. **Semantic Similarity** (Low/Medium/High) — How closely does the text match the reference in meaning?
2. **Idea Similarity** (Low/Medium/High) — Are the core ideas/arguments the same, even if words differ?
3. **Plagiarism Risk** (Low/Medium/High) — Risk of being flagged by automated plagiarism detectors
4. **Originality Score** (0-100) — How original is the user's content overall?
5. **Value Addition** (Low/Medium/High) — Does the user add unique perspectives, examples, or depth?
6. **SEO Quality** (0-100) — Rate the content's SEO strength (headings, structure, keywords, readability)
7. **Trust Score** (1-10) — Overall trustworthiness and publisher credibility signal
8. **AdSense Risk** (Low/Medium/High) — Risk of Google AdSense rejection or thin content penalty
9. **Analysis Summary** — A 2-3 sentence expert summary of the content's strengths and weaknesses

Return ONLY a valid JSON object with these exact keys:
{{"semantic_similarity": "...", "idea_similarity": "...", "plagiarism_risk": "...", "originality_score": "...", "value_addition": "...", "seo_score": "...", "trust_score": "...", "adsense_risk": "...", "analysis_summary": "..."}}"""


def _call_openai_compatible(api_url: str, api_key: str, model: str, prompt: str) -> dict:
    """Generic OpenAI-compatible API caller (works for DeepSeek + Groq + OpenRouter)."""
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
    CRE Multi-Factor Analysis Engine — DeepSeek primary, Groq + OpenRouter fallback.
    Returns 9-dimension analysis for comprehensive CRE scoring.
    """
    ref_dict = top_reference or {}
    prompt = ANALYSIS_PROMPT.format(
        sim_pct=similarity_score * 100,
        article=article[:2000],
        reference=ref_dict.get('content', 'No reference article found.')[:2000]
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
        "semantic_similarity": "Unknown",
        "idea_similarity": "Unknown",
        "plagiarism_risk": "Unknown",
        "originality_score": "50",
        "value_addition": "Unknown",
        "seo_score": "50",
        "trust_score": "5",
        "adsense_risk": "Unknown",
        "analysis_summary": "Analysis unavailable — no LLM API responded."
    }
