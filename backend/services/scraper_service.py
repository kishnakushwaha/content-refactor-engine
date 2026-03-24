import trafilatura
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from utils.url_validator import is_safe_url

# Dedicated thread pool with max 5 workers to prevent resource exhaustion
_scraper_pool = ThreadPoolExecutor(max_workers=5)

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
            print(f"[Scraper] Skipping dangerous URL: {url}")
            return None
            
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_links=False, include_images=False)
                print(f"[Scraper] Scraped {url}, length={len(text) if text else 0}")
                if text and len(text) > 200:
                    return {"url": url, "content": text}
        except Exception as e:
            print(f"[Scraper] Error for {url}: {e}")
        return None

    # Run scrapes concurrently with STRICT 10-second timeout per URL
    async def _scrape_with_timeout(url):
        loop = asyncio.get_running_loop()
        try:
            future = loop.run_in_executor(_scraper_pool, _scrape_single, url)
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            print(f"[Scraper] Timeout after 10s: {url}")
            return None
        except Exception:
            return None
    
    results = await asyncio.gather(*[_scrape_with_timeout(url) for url in urls])
    
    for r in results:
        if r:
            scraped_data.append(r)
            
    return scraped_data

