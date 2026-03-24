import requests
from config import Config
import json
import asyncio

async def generate_search_queries(article_text: str, num_queries: int = 3) -> list[str]:
    """
    Extracts the core themes of an article and generates targeted search queries
    to find similar content on the internet. Uses the Gemini REST API directly
    to prevent SDK freezing/hanging issues.
    """
    preview_text = article_text[:2000]
    
    prompt = f"""
    Analyze the following article text and generate exactly {num_queries} specific, highly relevant Google search queries that would lead someone to an article with exactly the same content or ideas.
    
    Output the queries as a valid JSON array of strings. Do not include markdown formatting or ANY other text, just the raw JSON array like this: ["query 1", "query 2", "query 3"]
    
    ARTICLE TEXT:
    {preview_text}
    """
    
    def _call_gemini_api():
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            print("[QueryGen] No Gemini API key found")
            return []
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            # STRICT 10-second timeout to prevent the pipeline from hanging at 30% forever
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            text_response = data["candidates"][0]["content"]["parts"][0]["text"]
            text_response = text_response.strip().replace("```json", "").replace("```", "")
            
            queries = json.loads(text_response)
            if isinstance(queries, list):
                return queries
            return [queries] if isinstance(queries, str) else []
            
        except Exception as e:
            print(f"[QueryGen] REST API error: {e}")
            return []

    return await asyncio.to_thread(_call_gemini_api)
