import trafilatura
import asyncio
from utils.url_validator import is_safe_url

async def scrape_urls(urls: list[str]) -> list[dict]:
    """
    Component 3: Content Scraper Engine
    Takes a list of URLs and uses trafilatura to extract raw, clean article text 
    (stripping ads, navbars, and boilerplate).
    Returns a list of dictionaries with url and content.
    """
    scraped_data = []

    def _scrape_single(url):
        # SSRF Protection: Prevent scanning localhost or private API networks
        if not is_safe_url(url):
            print(f"Skipping dangerous URL target: {url}")
            return None
            
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # include_links=False keeps the text purely semantic
                text = trafilatura.extract(downloaded, include_links=False, include_images=False)
                print(f"Scraped {url}, length={len(text) if text else 0}")
                if text and len(text) > 200: # Only keep substantial articles
                    return {"url": url, "content": text}
        except Exception as e:
            print(f"Trafilatura Scrape Error for {url}: {e}")
        return None

    # Run scrapes concurrently
    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, _scrape_single, url)
        for url in urls
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Filter out None results
    for r in results:
        if r:
            scraped_data.append(r)
            
    return scraped_data
