import google.generativeai as genai
from config import Config
import asyncio
import json
import requests

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def _rewrite_via_groq(texts: list[str]) -> list[str]:
    """Groq fallback using llama-3.3-70b-versatile (14,400 free RPD)."""
    groq_key = Config.GROQ_API_KEY
    if not groq_key:
        return texts
    
    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    prompt = f"""Rewrite the following blocks of text in a completely original, human-sounding way.
Keep the same structural meaning, but ensure high uniqueness.

You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    
    # Strip markdown fences
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    rewritten = json.loads(content.strip())
    if isinstance(rewritten, list) and len(rewritten) == len(texts):
        return [str(item) for item in rewritten]
    return texts


async def rewrite_text_nodes(texts: list[str]) -> list[str]:
    """
    Rewrite Engine — Gemini primary, Groq fallback.
    Takes text nodes, rewrites them for uniqueness, returns same-length array.
    """
    if not texts:
        return []

    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    
    prompt = f"""Rewrite the following blocks of text in a completely original, human-sounding way.
Keep the same structural meaning, but ensure high uniqueness.

You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""

    # Try Gemini first (2 attempts)
    for attempt in range(2):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result_text = response.text.strip()
            rewritten_array = json.loads(result_text)
            
            if isinstance(rewritten_array, list) and len(rewritten_array) == len(texts):
                print("[Rewrite] Gemini succeeded")
                return [str(item) for item in rewritten_array]
            else:
                print(f"[Rewrite] Gemini length mismatch: expected {len(texts)}, got {len(rewritten_array)}")
        except Exception as e:
            print(f"[Rewrite] Gemini error (attempt {attempt+1}): {e}")
            
        await asyncio.sleep(2)
    
    # Fallback to Groq
    try:
        print("[Rewrite] Trying Groq fallback...")
        result = await asyncio.to_thread(_rewrite_via_groq, texts)
        if result != texts:
            print("[Rewrite] Groq succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] Groq fallback failed: {e}")
    
    # Fallback to OpenRouter
    try:
        openrouter_key = Config.OPENROUTER_API_KEY
        if openrouter_key and "sk-or" in openrouter_key:
            print("[Rewrite] Trying OpenRouter fallback...")
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            resp = await asyncio.to_thread(
                requests.post,
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            rewritten = json.loads(content.strip())
            if isinstance(rewritten, list) and len(rewritten) == len(texts):
                print("[Rewrite] OpenRouter succeeded")
                return [str(item) for item in rewritten]
    except Exception as e:
        print(f"[Rewrite] OpenRouter fallback failed: {e}")
    
    print("[Rewrite] All engines failed. Returning originals.")
    return texts
