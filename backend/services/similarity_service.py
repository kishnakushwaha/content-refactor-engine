from sklearn.metrics.pairwise import cosine_similarity
from services.embedding_service import generate_embeddings
import numpy as np
import re

def _chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    """Splits text into chunks of roughly `chunk_size` words."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

async def calculate_similarity(user_article: str, reference_articles: list[dict]) -> tuple[dict, list[dict]]:
    """
    Component 5: Chunk-Based Similarity Engine
    Calculates the exact math-based cosine similarity between the user's article
    and the scraped internet references.
    
    Uses paragraph-level chunking to detect localized plagiarism and prevent score dilution.
    """
    if not reference_articles:
        return None, []
        
    user_chunks = _chunk_text(user_article)
    
    scored_references = []
    
    # We will compute each reference independently against all user chunks
    for ref in reference_articles:
        ref_chunks = _chunk_text(ref["content"])
        if not ref_chunks: continue
        
        # We need embeddings for all user_chunks + all ref_chunks
        texts_to_embed = user_chunks + ref_chunks
        embeddings = await generate_embeddings(texts_to_embed)
        
        user_vectors = embeddings[:len(user_chunks)]
        ref_vectors = embeddings[len(user_chunks):]
        
        # Calculate O(N x M) similarity matrix
        similarity_matrix = cosine_similarity(user_vectors, ref_vectors)
        
        # Find the absolute highest similarity between ANY user chunk and ANY reference chunk
        max_score = float(np.max(similarity_matrix))
        
        print(f"Similarity Matrix Math: {ref['url']} scored {max_score:.4f}")
        
        scored_references.append({
            "url": ref["url"],
            "score": max_score,
            "content": ref["content"] # Pass this back so the Analysis service can read it
        })
        
    # Sort descending
    scored_references.sort(key=lambda x: x["score"], reverse=True)
    
    highest_match = scored_references[0] if scored_references else None
    
    return highest_match, scored_references
