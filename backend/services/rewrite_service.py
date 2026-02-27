import google.generativeai as genai
from config import Config
import asyncio
import json
import requests

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def _build_rewrite_prompt(texts: list[str], reference_text: str = None) -> str:
    """Build the reference-aware, SEO-optimized rewrite prompt."""
    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    
    ref_section = ""
    if reference_text:
        ref_section = f"""
CRITICAL CONTEXT — The text below was flagged as semantically similar to the following reference.
You MUST actively increase the semantic distance from this reference while preserving the core meaning.

MATCHED REFERENCE TEXT (avoid resembling this):
{reference_text[:2000]}

DIFFERENTIATION STRATEGY:
- Use completely different sentence structures and reasoning patterns
- Replace generic phrasing with original insights and unique examples
- Restructure the logical flow and argument ordering
- Add value through original analysis the reference lacks
"""

    return f"""You are a professional content rewriter specializing in originality and SEO optimization.

Rewrite the following blocks of text so that they:
1. Are HIGHLY ORIGINAL — use different reasoning structures, vocabulary, and flow
2. Sound naturally human-written — no robotic or formulaic patterns
3. Improve SEO ranking — use clear headings, transition words, and scannable structure
4. Improve reader engagement and clarity
5. Improve AdSense approval probability — add depth and value
6. Preserve the core factual meaning accurately
{ref_section}
You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""


def _parse_llm_json(content: str, expected_len: int) -> list[str] | None:
    """Parse JSON array from LLM response, handling markdown fences."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    parsed = json.loads(content.strip())
    if isinstance(parsed, list) and len(parsed) == expected_len:
        return [str(item) for item in parsed]
    return None


def _rewrite_via_groq(texts: list[str], reference_text: str = None) -> list[str]:
    """Groq fallback using llama-3.3-70b-versatile."""
    groq_key = Config.GROQ_API_KEY
    if not groq_key:
        return texts
    
    prompt = _build_rewrite_prompt(texts, reference_text)
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    
    result = _parse_llm_json(content, len(texts))
    return result if result else texts


def _rewrite_via_openrouter(texts: list[str], reference_text: str = None) -> list[str]:
    """OpenRouter fallback using free llama model."""
    openrouter_key = Config.OPENROUTER_API_KEY
    if not openrouter_key or "sk-or" not in openrouter_key:
        return texts
    
    prompt = _build_rewrite_prompt(texts, reference_text)
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75
    }
    
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    
    result = _parse_llm_json(content, len(texts))
    return result if result else texts


async def rewrite_text_nodes(texts: list[str], reference_text: str = None) -> list[str]:
    """
    Reference-Aware Rewrite Engine — Gemini primary, Groq + OpenRouter fallback.
    Takes text nodes + matched reference, rewrites for maximum originality.
    """
    if not texts:
        return []

    prompt = _build_rewrite_prompt(texts, reference_text)

    # Try Gemini first (2 attempts)
    for attempt in range(2):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result = _parse_llm_json(response.text, len(texts))
            if result:
                print("[Rewrite] Gemini succeeded")
                return result
            else:
                print(f"[Rewrite] Gemini length mismatch on attempt {attempt+1}")
        except Exception as e:
            print(f"[Rewrite] Gemini error (attempt {attempt+1}): {e}")
            
        await asyncio.sleep(2)
    
    # Fallback to Groq
    try:
        print("[Rewrite] Trying Groq fallback...")
        result = await asyncio.to_thread(_rewrite_via_groq, texts, reference_text)
        if result != texts:
            print("[Rewrite] Groq succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] Groq fallback failed: {e}")
    
    # Fallback to OpenRouter
    try:
        print("[Rewrite] Trying OpenRouter fallback...")
        result = await asyncio.to_thread(_rewrite_via_openrouter, texts, reference_text)
        if result != texts:
            print("[Rewrite] OpenRouter succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] OpenRouter fallback failed: {e}")
    
    print("[Rewrite] All engines failed. Returning originals.")
    return texts
