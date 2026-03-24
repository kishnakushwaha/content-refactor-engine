import numpy as np
import requests
import asyncio
import time
from config import Config

# The Hugging Face feature extraction pipeline URL for the MiniLM model
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

# Lazy-loaded local fallback model
_local_model = None

async def generate_embeddings(texts: list[str]) -> np.ndarray:
    """
    Component 4: Embedding Engine
    Takes a list of texts and returns their semantic vector embeddings.
    First tries Hugging Face Serverless API; falls back to local execution.
    """
    hf_key = Config.HUGGINGFACE_API_KEY
    
    def _fetch_hf_api():
        headers = {"Authorization": f"Bearer {hf_key}"}
        
        # HuggingFace models can be "cold" — they take ~20s to warm up on first call
        # We retry once after a short wait if we get a 503 (model loading)
        for attempt in range(2):
            try:
                response = requests.post(
                    HF_API_URL,
                    headers=headers,
                    json={"inputs": texts},
                    timeout=15  # STRICT 15-second timeout
                )
                
                if response.status_code == 503:
                    # Model is loading on HuggingFace servers
                    wait_time = response.json().get("estimated_time", 10)
                    print(f"[Embedding] HF model loading, waiting {wait_time:.0f}s...")
                    time.sleep(min(wait_time, 15))  # Wait max 15s
                    continue
                    
                response.raise_for_status()
                return np.array(response.json())
            except Exception as e:
                print(f"[Embedding] HF API attempt {attempt+1} failed: {e}")
        
        raise Exception("HuggingFace API failed after retries")
        
    def _run_local():
        global _local_model
        try:
            if _local_model is None:
                from sentence_transformers import SentenceTransformer
                print("[Embedding] Loading local MiniLM model...")
                _local_model = SentenceTransformer('all-MiniLM-L6-v2')
                
            return _local_model.encode(texts, normalize_embeddings=True)
        except Exception as e:
            print(f"[Embedding] Local model failed (likely OOM on free tier): {e}")
            # Return zero vectors as absolute last resort so the pipeline doesn't crash
            return np.zeros((len(texts), 384))
        
    if hf_key and "hf_" in hf_key:
        try:
            return await asyncio.to_thread(_fetch_hf_api)
        except Exception as e:
            print(f"[Embedding] HuggingFace API failed ({e}). Falling back to local model...")
            
    # Fallback executing the lightweight local model in the background thread
    return await asyncio.to_thread(_run_local)
