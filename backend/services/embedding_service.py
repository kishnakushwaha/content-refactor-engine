import numpy as np
import requests
import asyncio
import time
from config import Config

# The Hugging Face feature extraction pipeline URL for the MiniLM model
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"


def _tfidf_embeddings(texts: list[str]) -> np.ndarray:
    """
    Lightweight TF-IDF fallback that uses only scikit-learn (~20MB RAM).
    This replaces the sentence-transformers local model (~400MB + PyTorch)
    which causes OOM kills on Render's free tier (512MB RAM).
    
    Returns normalized TF-IDF vectors that work with cosine_similarity()
    just like real embeddings.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    print("[Embedding] Using TF-IDF fallback (lightweight, no PyTorch needed)")
    
    vectorizer = TfidfVectorizer(
        max_features=384,      # Match MiniLM embedding dimension
        stop_words="english",
        ngram_range=(1, 2),    # Unigrams + bigrams for better matching
        sublinear_tf=True      # Logarithmic TF for better similarity detection
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        # Convert sparse matrix to dense numpy array
        dense = tfidf_matrix.toarray()
        
        # Pad or truncate to exactly 384 dimensions for compatibility
        if dense.shape[1] < 384:
            padded = np.zeros((dense.shape[0], 384))
            padded[:, :dense.shape[1]] = dense
            dense = padded
        
        # L2 normalize like sentence-transformers does
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Prevent division by zero
        return dense / norms
        
    except Exception as e:
        print(f"[Embedding] TF-IDF also failed: {e}")
        return np.zeros((len(texts), 384))


async def generate_embeddings(texts: list[str]) -> np.ndarray:
    """
    Component 4: Embedding Engine
    Takes a list of texts and returns their semantic vector embeddings.
    
    Strategy:
    1. Try HuggingFace Inference API (best quality, zero RAM)
    2. Fallback to TF-IDF (good quality, ~20MB RAM — works on free tier)
    
    NEVER loads sentence-transformers/PyTorch locally to avoid OOM kills.
    """
    hf_key = Config.HUGGINGFACE_API_KEY
    
    def _fetch_hf_api():
        headers = {"Authorization": f"Bearer {hf_key}"}
        
        for attempt in range(2):
            try:
                response = requests.post(
                    HF_API_URL,
                    headers=headers,
                    json={"inputs": texts},
                    timeout=15
                )
                
                if response.status_code == 503:
                    wait_time = response.json().get("estimated_time", 10)
                    print(f"[Embedding] HF model loading, waiting {min(wait_time, 12):.0f}s...")
                    time.sleep(min(wait_time, 12))
                    continue
                    
                response.raise_for_status()
                result = response.json()
                
                # Validate the response shape
                arr = np.array(result)
                if arr.ndim == 2 and arr.shape[0] == len(texts):
                    print(f"[Embedding] HF API succeeded: {arr.shape}")
                    return arr
                else:
                    print(f"[Embedding] HF API returned unexpected shape: {arr.shape}")
                    raise Exception("Bad response shape")
                    
            except Exception as e:
                print(f"[Embedding] HF API attempt {attempt+1} failed: {e}")
        
        raise Exception("HuggingFace API failed after retries")
        
    # Try HuggingFace API first
    if hf_key and "hf_" in hf_key:
        try:
            return await asyncio.to_thread(_fetch_hf_api)
        except Exception as e:
            print(f"[Embedding] HuggingFace API fully failed: {e}")
            
    # Fallback to lightweight TF-IDF (uses scikit-learn only, ~20MB RAM)
    return await asyncio.to_thread(_tfidf_embeddings, texts)

