"""
Fingerprint Engine — The Core CRE Proprietary Index Technology

Converts text → normalized shingles → MurmurHash3 integers.
Provides O(1) database insertion and lookup for instant plagiarism detection.

Industry standard: 5-word shingling + MurmurHash3 (same as Elasticsearch internals).
"""
import re
import hashlib
import sqlite3
import os
import mmh3

INDEX_DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

# ==============================
# 1. Text Normalization
# ==============================

def normalize_text(text: str) -> str:
    """
    Normalize text for consistent fingerprinting.
    - Lowercase
    - Strip all punctuation except hyphens (preserve compound words)
    - Collapse whitespace
    """
    text = text.lower()
    # Remove everything except letters, digits, hyphens, and spaces
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ==============================
# 2. Shingling (N-Gram Generation)
# ==============================

def generate_shingles(text: str, n: int = 5) -> list[str]:
    """
    Generate overlapping N-word shingles from normalized text.
    
    Example (n=5):
      "machine learning is used in artificial intelligence systems"
      → ["machine learning is used in",
         "learning is used in artificial",
         "is used in artificial intelligence",
         "used in artificial intelligence systems"]
    """
    words = text.split()
    if len(words) < n:
        # If text is too short for n-grams, return the whole thing as one shingle
        return [text] if text else []
    
    shingles = []
    for i in range(len(words) - n + 1):
        shingle = " ".join(words[i:i + n])
        shingles.append(shingle)
    
    return shingles


# ==============================
# 3. MurmurHash3 Fingerprinting
# ==============================

def hash_shingles(shingles: list[str]) -> list[int]:
    """
    Convert string shingles into 32-bit MurmurHash3 integers.
    
    MurmurHash3 is:
    - Non-cryptographic (fast, not for security)
    - Excellent distribution (minimal collisions)
    - Industry standard for inverted indexes (Elasticsearch uses it)
    """
    return [mmh3.hash(shingle, signed=False) for shingle in shingles]


# ==============================
# 4. Master Fingerprint Generator
# ==============================

def generate_fingerprints(text: str) -> list[int]:
    """
    The core function: Text → Fingerprints.
    
    Pipeline:
      Raw text → normalize → shingle (5-word) → MurmurHash3 → integer list
    
    Returns: list of 32-bit unsigned integers (fingerprint hashes)
    """
    normalized = normalize_text(text)
    shingles = generate_shingles(normalized)
    fingerprints = hash_shingles(shingles)
    return fingerprints


# ==============================
# 5. Document Indexing (DB Insert)
# ==============================

def index_document(url: str, text: str) -> dict:
    """
    Index a single document into the fingerprint database.
    
    Steps:
      1. Generate a unique document ID from the URL
      2. Check if already indexed (skip if yes)
      3. Generate fingerprints from the text
      4. Bulk insert (hash, doc_id) pairs into the inverted index
    
    Returns: {"status": "indexed"|"skipped", "fingerprint_count": N}
    """
    # Generate deterministic document ID from URL
    doc_id = hashlib.md5(url.encode()).hexdigest()
    
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if already indexed
        cursor.execute("SELECT id FROM indexed_documents WHERE id = ?", (doc_id,))
        if cursor.fetchone():
            conn.close()
            return {"status": "skipped", "fingerprint_count": 0, "doc_id": doc_id}
        
        # Generate fingerprints
        fingerprints = generate_fingerprints(text)
        
        if not fingerprints:
            conn.close()
            return {"status": "skipped", "fingerprint_count": 0, "doc_id": doc_id}
        
        # Insert document metadata
        word_count = len(text.split())
        cursor.execute(
            "INSERT INTO indexed_documents (id, url, content_snippet, word_count) VALUES (?, ?, ?, ?)",
            (doc_id, url, text[:500], word_count)
        )
        
        # Bulk insert fingerprints into inverted index
        fp_rows = [(fp, doc_id) for fp in fingerprints]
        cursor.executemany(
            "INSERT INTO fingerprints (fingerprint_hash, document_id) VALUES (?, ?)",
            fp_rows
        )
        
        conn.commit()
        conn.close()
        
        return {"status": "indexed", "fingerprint_count": len(fingerprints), "doc_id": doc_id}
    
    except Exception as e:
        conn.close()
        print(f"[FingerprintEngine] Indexing error: {e}")
        return {"status": "error", "fingerprint_count": 0, "doc_id": doc_id}


# ==============================
# 6. Fingerprint Lookup (O(1) Match)
# ==============================

def lookup_fingerprints(text: str, top_k: int = 5) -> list[dict]:
    """
    The O(1) matching engine.
    
    Steps:
      1. Generate fingerprints from the user's article
      2. Query the inverted index for matching document IDs
      3. Count overlapping hashes per document
      4. Rank by overlap percentage (Jaccard-like similarity)
    
    Returns: list of {"doc_id", "url", "content_snippet", "match_count", "similarity"}
    """
    user_fingerprints = generate_fingerprints(text)
    
    if not user_fingerprints:
        return []
    
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Build the IN clause with parameterized placeholders
        placeholders = ",".join(["?" for _ in user_fingerprints])
        
        query = f"""
            SELECT 
                f.document_id,
                d.url,
                d.content_snippet,
                COUNT(*) as match_count
            FROM fingerprints f
            JOIN indexed_documents d ON f.document_id = d.id
            WHERE f.fingerprint_hash IN ({placeholders})
            GROUP BY f.document_id
            ORDER BY match_count DESC
            LIMIT ?
        """
        
        cursor.execute(query, user_fingerprints + [top_k])
        rows = cursor.fetchall()
        conn.close()
        
        total_user_fps = len(user_fingerprints)
        
        results = []
        for row in rows:
            doc_id, url, snippet, match_count = row
            # Similarity = overlapping fingerprints / total user fingerprints
            similarity = round(match_count / total_user_fps, 4) if total_user_fps > 0 else 0
            results.append({
                "doc_id": doc_id,
                "url": url,
                "content_snippet": snippet,
                "match_count": match_count,
                "total_fingerprints": total_user_fps,
                "similarity": similarity
            })
        
        return results
    
    except Exception as e:
        conn.close()
        print(f"[FingerprintEngine] Lookup error: {e}")
        return []
