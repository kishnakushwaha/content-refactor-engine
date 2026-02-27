import requests
from config import Config
import asyncio

async def search_internet(queries: list[str], max_results_per_query: int = 7) -> list[str]:
    """
    Component 2: Internet Retrieval Engine
    Takes a list of search queries and returns a deduplicated list of URLs.
    Uses official Google Custom Search API for production reliability.
    """
    urls = set()
    
    api_key = Config.GOOGLE_API_KEY
    cx = Config.GOOGLE_CX_ID
    
    def _search_google():
        for query in queries:
            try:
                url = f"https://customsearch.googleapis.com/customsearch/v1?cx={cx}&q={query}&key={api_key}&num={max_results_per_query}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    urls.add(item.get("link"))
            except Exception as e:
                print(f"Google Search Error for '{query}': {e}")
                
    def _search_ddg_fallback():
        from duckduckgo_search import DDGS
        print("Falling back to DuckDuckGo Search...")
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = ddgs.text(query, max_results=max_results_per_query)
                    if results:
                        for r in results:
                            urls.add(r.get('href'))
                except Exception as e:
                    print(f"DDGS Search Error for query '{query}': {e}")

    # Use Google API if keys exist, otherwise DDG
    if api_key and cx and "AIza" in api_key:
        await asyncio.to_thread(_search_google)
        
    # If Google failed (e.g. 403 Forbidden) or keys don't exist, fallback to DDG
    if not urls:
        await asyncio.to_thread(_search_ddg_fallback)
        
    return list(urls)
