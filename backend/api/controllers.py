from bs4 import BeautifulSoup
from services.query_generator import generate_search_queries
from services.similarity_service import calculate_similarity
from services.analysis_service import analyze_originality
from services.rewrite_service import rewrite_text_nodes
from services.scoring_service import generate_cre_report
import asyncio
import json
import sqlite3
import os

REWRITE_TAGS = ["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"]
MIN_TEXT_LENGTH = 40
DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def extract_rewriteable_nodes(html: str):
    soup = BeautifulSoup(html, "lxml")
    nodes = []

    for tag in soup.find_all(REWRITE_TAGS):
        text = tag.get_text(strip=True)
        if not text:
            continue
        if len(text) < MIN_TEXT_LENGTH:
            continue
            
        nodes.append({
            "element": tag,
            "text": text
        })

    return soup, nodes


def save_article_to_db(user_id: str, original: str, rewritten: str, similarity: float):
    """Save processed article to database for history tracking."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO articles (user_id, original_content, rewritten_content, semantic_similarity_score) VALUES (?, ?, ?, ?)",
            (user_id, original[:5000], rewritten[:5000], f"{int(similarity * 100)}%")
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Failed to save article: {e}")


def get_user_history(user_id: str, limit: int = 20):
    """Retrieve user's processing history."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, original_content, rewritten_content, semantic_similarity_score, created_at FROM articles WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[DB] History query failed: {e}")
        return []


async def process_article_controller(html_content: str, user_id: str = None, progress_callback=None) -> dict:
    """
    The Ultimate Multi-Model CRE Pipeline (SaaS MVP).
    Now with progress callbacks for live frontend updates.
    """
    import re
    
    # Step 1: Extract text
    if progress_callback:
        await progress_callback("extracting", "Breaking down your text for in-depth analysis...")
    
    if not bool(re.search(r'<(p|div|h[1-6]|li|article|section|blockquote)[^>]*>', html_content, re.IGNORECASE)):
        paragraphs = [p.strip() for p in html_content.split('\n') if p.strip()]
        html_content = "".join([f"<p>{p}</p>" for p in paragraphs])
        
    soup, nodes = extract_rewriteable_nodes(html_content)
    if not nodes:
        return {"status": "skipped", "message": "No rewriteable text found."}
        
    full_text = "\n".join([n["text"] for n in nodes])
    
    # Step 2: Retrieval
    if progress_callback:
        await progress_callback("searching", "Analyzing billions of web pages for matching content...")
    
    from services.retrieval_engine import retrieve_candidate_sources
    references = await retrieve_candidate_sources(full_text, generate_search_queries)
    
    # Step 3: Similarity
    if progress_callback:
        await progress_callback("comparing", "Scanning millions of publications for potential matches...")
    
    top_match, all_scores = await calculate_similarity(full_text, references)
    similarity_score = top_match["score"] if top_match else 0.0
    
    # Step 4: Analysis
    if progress_callback:
        await progress_callback("analyzing", "Ensuring your content is uniquely yours...")
    
    analysis = await analyze_originality(full_text, top_match, similarity_score)
    
    # Step 5: Reference-Aware Rewrite
    if progress_callback:
        await progress_callback("rewriting", "Rewriting with maximum semantic distance from matched references...")
    
    # Pass the matched reference text so the LLM can actively differentiate
    reference_content = top_match.get("content", "") if top_match else None
    texts_to_rewrite = [n["text"] for n in nodes]
    rewritten_texts = await rewrite_text_nodes(texts_to_rewrite, reference_text=reference_content)
    
    for node, new_text in zip(nodes, rewritten_texts):
        node["element"].string = new_text
        
    final_html = str(soup)
    
    # Step 6: Report
    if progress_callback:
        await progress_callback("finalizing", "Generating your comprehensive report...")
    
    report = generate_cre_report(similarity_score, analysis)
    report["urls_scanned"] = len(references)
    if top_match:
        report["top_match_url"] = top_match["url"]
    
    # Add top 5 matched reference URLs for richer frontend display
    report["matched_references"] = [
        {"url": ref["url"], "score": f"{int(ref['score'] * 100)}%"}
        for ref in all_scores[:5]
    ] if all_scores else []

    # Save to DB for history
    if user_id:
        save_article_to_db(user_id, full_text, "\n".join(rewritten_texts), similarity_score)
        
    return {
        "status": "success",
        "report": report,
        "final_html": final_html
    }
