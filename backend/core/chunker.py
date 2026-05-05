"""
chunker.py
----------
Splits long document text into smaller overlapping chunks
so the embedding model and LLM can process them efficiently.
"""

import os
import hashlib

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE",    312))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP",  50))


# ── Core Chunking ─────────────────────────────────────────────────────────────

def chunk_text(
    text:       str,
    chunk_size: int = CHUNK_SIZE,
    overlap:    int = CHUNK_OVERLAP,
) -> list[str]:
    if not text or not text.strip():
        return []

    words  = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        end   = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        step = max(chunk_size - overlap, 1)
        start += step

    return chunks


def make_chunk_id(filename: str, chunk_index: int, text: str) -> str:
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    base = os.path.splitext(filename)[0]
    return f"{base}_chunk{chunk_index:04d}_{text_hash}"


# ── Document Chunker ─

def chunk_documents(
    documents:  list[dict],
    chunk_size: int = CHUNK_SIZE,
    overlap:    int = CHUNK_OVERLAP,
) -> list[dict]:
    all_chunks = []

    for doc in documents:
        filename = doc.get("filename", "unknown")
        text     = doc.get("text", "")
        metadata = doc.get("metadata", {})

        if not text.strip():
            logger.warning(f"  ⚠ Skipping empty document: {filename}")
            continue

        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "chunk_id": make_chunk_id(filename, i, chunk),
                "text":     chunk,
                "source":   filename,
                "metadata": metadata,
            })

        logger.info(f"  ✓ Chunked: {filename}  →  {len(chunks)} chunks")

    return all_chunks


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nChunk size:    {CHUNK_SIZE} words")
    print(f"Chunk overlap: {CHUNK_OVERLAP} words\n")

    sample_text = " ".join([f"word{i}" for i in range(1500)])
    chunks = chunk_text(sample_text)

    print(f"Input:  1,500 words")
    print(f"Output: {len(chunks)} chunks\n")
    print(f"Chunk 1 words: {len(chunks[0].split())}")
    print(f"Chunk 2 words: {len(chunks[1].split())}")

    last_words  = chunks[0].split()[-CHUNK_OVERLAP:]
    first_words = chunks[1].split()[:CHUNK_OVERLAP]
    print(f"Overlap correct: {last_words == first_words}")

    id1 = make_chunk_id("report.pdf", 0, chunks[0])
    id2 = make_chunk_id("report.pdf", 0, chunks[0])
    print(f"Stable IDs:      {id1 == id2}")
    print(f"\nChunker working correctly!")