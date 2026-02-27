"""
Fingerprint Index DB Schema

Creates the inverted index tables used by the Fingerprint Engine
for O(1) plagiarism detection lookups.
"""
import sqlite3
import os

INDEX_DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def init_index_tables():
    """Create the fingerprint index tables if they don't exist."""
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Indexed Documents — stores metadata of every crawled/indexed page
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indexed_documents (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            content_snippet TEXT,
            word_count INTEGER DEFAULT 0,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table 2: Fingerprints — the core inverted index
    # Maps each fingerprint hash → the document it belongs to
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            fingerprint_hash INTEGER NOT NULL,
            document_id TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES indexed_documents(id)
        )
    """)
    
    # Critical: Index on fingerprint_hash for O(1) lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fingerprint_hash 
        ON fingerprints(fingerprint_hash)
    """)
    
    # Index on document_id for fast document-level queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fingerprint_doc 
        ON fingerprints(document_id)
    """)
    
    conn.commit()
    conn.close()
    print("[IndexDB] Fingerprint index tables initialized.")


def get_index_stats():
    """Return current index statistics."""
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM indexed_documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        fp_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        doc_count = 0
        fp_count = 0
    
    conn.close()
    return {"documents": doc_count, "fingerprints": fp_count}


if __name__ == "__main__":
    init_index_tables()
    stats = get_index_stats()
    print(f"[IndexDB] Stats: {stats['documents']} documents, {stats['fingerprints']} fingerprints")
