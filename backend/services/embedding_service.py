import numpy as np
import requests
import asyncio
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
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": texts})
        response.raise_for_status()
        return np.array(response.json())
        
    def _run_local():
        global _local_model
        if _local_model is None:
            from sentence_transformers import SentenceTransformer
            print("Loading local MiniLM model for embeddings...")
            _local_model = SentenceTransformer('all-MiniLM-L6-v2')
            
        return _local_model.encode(texts, normalize_embeddings=True)
        
    if hf_key and "hf_" in hf_key:
        try:
            return await asyncio.to_thread(_fetch_hf_api)
        except Exception as e:
            print(f"HuggingFace API failed ({e}). Falling back to local model computation...")
            
    # Fallback executing the lightweight local model in the background thread
    return await asyncio.to_thread(_run_local)
