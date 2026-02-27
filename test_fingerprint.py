#!/usr/bin/env python3
"""
Fingerprint Engine Verification Test

Tests the complete pipeline:
  1. Text normalization
  2. Shingling
  3. MurmurHash3 hashing
  4. Document indexing into DB
  5. O(1) lookup and matching
"""
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.index_db import init_index_tables, get_index_stats
from services.fingerprint_engine import (
    normalize_text,
    generate_shingles,
    hash_shingles,
    generate_fingerprints,
    index_document,
    lookup_fingerprints,
)

# ==============================
# Setup
# ==============================
print("=" * 60)
print("FINGERPRINT ENGINE VERIFICATION TEST")
print("=" * 60)

# Initialize tables
init_index_tables()
stats = get_index_stats()
print(f"\n[Setup] Index stats before test: {stats}")

# ==============================
# Test 1: Text Normalization
# ==============================
print("\n--- Test 1: Text Normalization ---")
raw = "  Machine Learning is used in Artificial Intelligence systems!!! "
normalized = normalize_text(raw)
print(f"  Input:      '{raw}'")
print(f"  Normalized: '{normalized}'")
assert normalized == "machine learning is used in artificial intelligence systems"
print("  ✅ PASSED")

# ==============================
# Test 2: Shingle Generation
# ==============================
print("\n--- Test 2: Shingle Generation ---")
shingles = generate_shingles(normalized, n=5)
print(f"  Input words: {len(normalized.split())}")
print(f"  Shingles generated: {len(shingles)}")
for i, s in enumerate(shingles):
    print(f"    [{i}] {s}")
expected_count = len(normalized.split()) - 5 + 1
assert len(shingles) == expected_count, f"Expected {expected_count}, got {len(shingles)}"
print("  ✅ PASSED")

# ==============================
# Test 3: MurmurHash3 Hashing
# ==============================
print("\n--- Test 3: MurmurHash3 Hashing ---")
hashes = hash_shingles(shingles)
print(f"  Hashes generated: {len(hashes)}")
for i, h in enumerate(hashes):
    print(f"    [{i}] {shingles[i]} → {h}")
assert all(isinstance(h, int) for h in hashes)
assert len(set(hashes)) == len(hashes), "Hash collision detected in small set!"
print("  ✅ PASSED")

# ==============================
# Test 4: Full Fingerprint Generation
# ==============================
print("\n--- Test 4: Full Fingerprint Generation ---")
article = """
Machine learning algorithms are increasingly being used in modern artificial intelligence 
systems to automate complex decision-making processes. These algorithms learn from data 
patterns and make predictions without explicit programming. Deep learning, a subset of 
machine learning, uses neural networks with multiple layers to extract higher-level features 
from raw input data. This approach has revolutionized fields such as computer vision, 
natural language processing, and speech recognition.
"""
fps = generate_fingerprints(article)
print(f"  Article word count: {len(article.split())}")
print(f"  Fingerprints generated: {len(fps)}")
assert len(fps) > 0
print("  ✅ PASSED")

# ==============================
# Test 5: Document Indexing
# ==============================
print("\n--- Test 5: Document Indexing ---")
result = index_document("https://example.com/ml-article", article)
print(f"  Result: {result}")
assert result["status"] == "indexed"
assert result["fingerprint_count"] > 0

# Index a second document
article2 = """
Cloud computing provides on-demand availability of computer system resources, especially 
data storage and computing power, without direct active management by the user. Large 
cloud providers offer their services from data centers located around the world. Cloud 
computing enables organizations to consume compute resources as a utility rather than 
building and maintaining computing infrastructure in-house.
"""
result2 = index_document("https://example.com/cloud-article", article2)
print(f"  Doc 2 Result: {result2}")
assert result2["status"] == "indexed"

# Try indexing same URL again (should skip)
result3 = index_document("https://example.com/ml-article", article)
print(f"  Duplicate Result: {result3}")
assert result3["status"] == "skipped"
print("  ✅ PASSED")

# ==============================
# Test 6: O(1) Fingerprint Lookup
# ==============================
print("\n--- Test 6: O(1) Fingerprint Lookup ---")

# Slightly modified version of article 1 — should still match
query_article = """
Machine learning algorithms are increasingly used in modern AI systems to automate 
complex decision-making. These algorithms learn from data patterns and make predictions 
without explicit programming instructions. Deep learning uses neural networks with 
multiple layers to extract higher-level features from raw data input.
"""

start_time = time.time()
matches = lookup_fingerprints(query_article)
lookup_ms = (time.time() - start_time) * 1000

print(f"  Lookup time: {lookup_ms:.2f} ms")
print(f"  Matches found: {len(matches)}")
for m in matches:
    print(f"    URL: {m['url']}")
    print(f"    Match count: {m['match_count']}/{m['total_fingerprints']}")
    print(f"    Similarity: {m['similarity'] * 100:.1f}%")
    print()

assert len(matches) > 0, "No matches found — fingerprint lookup failed!"
assert matches[0]["url"] == "https://example.com/ml-article", "Wrong document matched!"
assert lookup_ms < 500, f"Lookup too slow: {lookup_ms:.2f}ms (target < 500ms)"
print("  ✅ PASSED")

# ==============================
# Final Stats
# ==============================
stats = get_index_stats()
print("\n" + "=" * 60)
print(f"FINAL INDEX STATS: {stats['documents']} documents, {stats['fingerprints']} fingerprints")
print("=" * 60)
print("\n🎉 ALL TESTS PASSED — Fingerprint Engine is operational!")
