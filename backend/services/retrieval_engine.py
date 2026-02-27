import re
import asyncio
import requests
from bs4 import BeautifulSoup
from services.scraper_service import scrape_urls
from utils.url_validator import is_safe_url

# ==============================
# 1. Fingerprint Extractor
# ==============================

def extract_fingerprints(text: str, max_fingerprints=12):
    """
    Extract exact phrases from the article for plagiarism search.
    Uses sentence-based extraction (60-200 chars) as primary strategy.
    
    CRITICAL: Do NOT wrap in quotes — googlesearch-python returns 0 for quoted queries.
    CRITICAL: Preserve hyphens/slashes — stripping turns Scikit-Learn into Scikit Learn.
    """
    # Only strip newlines and tabs, preserve all other punctuation
    clean_text = re.sub(r'[\n\t\r]+', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]', clean_text)
    
    fingerprints = []
    for s in sentences:
        s = s.strip()
        if len(s) < 60 or len(s) > 200:
            continue
        # Raw unquoted phrase — search engines naturally rank exact matches higher
        fingerprints.append(s)
        if len(fingerprints) >= max_fingerprints:
            break
    
    # If not enough sentence-based fingerprints, add sliding window fingerprints
    if len(fingerprints) < 3:
        words = clean_text.split()
        for i in range(0, max(1, len(words) - 8 + 1), 20):
            chunk = words[i:i+8]
            if len(chunk) < 5:
                continue
            fingerprints.append(" ".join(chunk))
            if len(fingerprints) >= max_fingerprints:
                break
    
    return fingerprints


# ==============================
# 2. Semantic Query Generator Fusion
# ==============================

async def fuse_queries(article_text, semantic_generator):
    """Combines fingerprint queries + semantic queries."""
    fingerprints = extract_fingerprints(article_text)
    semantic_queries = await semantic_generator(article_text)
    return list(set(fingerprints + semantic_queries))


# ==============================
# 3. Multi-Engine Retrieval
# ==============================

async def search_ddg_html(queries):
    """
    Uses DuckDuckGo's HTML endpoint directly.
    The duckduckgo_search pip library is dead (returns [] for everything).
    The HTML POST endpoint works reliably.
    """
    urls = set()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    def _search():
        import time
        for q in queries:
            try:
                resp = requests.post(
                    "https://html.duckduckgo.com/html/",
                    data={"q": q},
                    headers=headers,
                    timeout=10
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.select("a.result__url"):
                    link = a.get("href")
                    if link and link.startswith("http") and is_safe_url(link):
                        urls.add(link)
                time.sleep(0.5)  # Rate limit protection
            except Exception as e:
                print(f"DDG HTML error: {e}")
    
    await asyncio.to_thread(_search)
    return list(urls)


async def search_google(queries):
    """
    Uses googlesearch-python (scrapes Google).
    This is the engine that successfully retrieved amanxai.com at 85% similarity.
    """
    urls = set()
    
    def _search():
        try:
            from googlesearch import search
            for q in queries:
                try:
                    for url in search(q, num_results=10, lang="en"):
                        if is_safe_url(url):
                            urls.add(url)
                except Exception as e:
                    print(f"Google search error on query: {e}")
        except ImportError:
            print("googlesearch-python not installed")
    
    await asyncio.to_thread(_search)
    return list(urls)


async def search_bing(queries):
    """
    Bing HTML scraper — best-effort fallback.
    Often CAPTCHA-blocked but worth trying.
    """
    urls = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    def _search():
        for q in queries:
            try:
                resp = requests.get(
                    f"https://www.bing.com/search?q={q}",
                    headers=headers,
                    timeout=10
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("http") and "bing.com" not in link and "microsoft.com" not in link:
                        if is_safe_url(link):
                            urls.add(link)
            except Exception:
                pass
    
    await asyncio.to_thread(_search)
    return list(urls)


# ==============================
# 4. URL Ranking Engine
# ==============================

def rank_urls(urls, article_text):
    """Rank URLs based on domain quality + keyword overlap."""
    keywords = set(article_text.lower().split()[:50])
    ranked = []
    
    for url in urls:
        score = 0
        url_lower = url.lower()
        for k in keywords:
            if k in url_lower:
                score += 1
        if any(x in url_lower for x in ["blog", "article", "post"]):
            score += 3
        ranked.append((url, score))
    
    ranked.sort(key=lambda x: x[1], reverse=True)
    return [u[0] for u in ranked]


# ==============================
# 5. Adaptive Scraping Controller
# ==============================

async def adaptive_scrape(urls, max_scrape=15):
    """Scrapes highest ranked URLs first."""
    scraped = []
    for url in urls[:max_scrape]:
        try:
            data = await scrape_urls([url])
            if data:
                scraped.extend(data)
        except:
            pass
    return scraped


# ==============================
# 6. Master Retrieval Pipeline
# ==============================

async def retrieve_candidate_sources(article_text, semantic_generator):
    # Step 1: Query fusion
    queries = await fuse_queries(article_text, semantic_generator)
    print("\n[RETRIEVAL] Queries:", queries)

    # Step 2: Multi-engine search (all run, results merged)
    ddg_urls = await search_ddg_html(queries)
    google_urls = await search_google(queries)
    bing_urls = await search_bing(queries)
    
    all_urls = list(set(ddg_urls + google_urls + bing_urls))
    print(f"[RETRIEVAL] URLs found: DDG={len(ddg_urls)} Google={len(google_urls)} Bing={len(bing_urls)} Total={len(all_urls)}")

    # Step 3: Ranking
    ranked_urls = rank_urls(all_urls, article_text)
    print(f"[RETRIEVAL] Top candidates: {ranked_urls[:5]}")

    # Step 4: Adaptive scrape
    scraped = await adaptive_scrape(ranked_urls)
    print(f"[RETRIEVAL] Scraped sources: {len(scraped)}")

    return scraped
