import google.generativeai as genai
from config import Config
import json

genai.configure(api_key=Config.GEMINI_API_KEY)

# Use Gemini 2.0 Flash — highest free-tier limit (1500 RPD)
model = genai.GenerativeModel('gemini-2.0-flash')

async def generate_search_queries(article_text: str, num_queries: int = 3) -> list[str]:
    """
    Extracts the core themes of an article and generates targeted search queries
    to find similar content on the internet.
    """
    # Truncate text just in case it's massive to save tokens
    preview_text = article_text[:2000]
    
    prompt = f"""
    Analyze the following article text and generate exactly {num_queries} specific, highly relevant Google search queries that would lead someone to an article with exactly the same content or ideas.
    
    Output the queries as a valid JSON array of strings. Do not include markdown formatting or ANY other text, just the raw JSON array like this: ["query 1", "query 2", "query 3"]
    
    ARTICLE TEXT:
    {preview_text}
    """
    
    try:
        import asyncio
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        text_response = response.text.strip().replace("```json", "").replace("```", "")
        queries = json.loads(text_response)
        if isinstance(queries, list):
            return queries
        return [queries] if isinstance(queries, str) else []
    except Exception as e:
        print(f"Error generating queries: {e}")
        return []
