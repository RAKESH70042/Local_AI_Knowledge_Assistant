"""
vectorstore.py
--------------
Stores and retrieves embeddings using ChromaDB.
ChromaDB runs fully locally — all data saved in data/chroma_db/ on your PC.

Fixes vs old version:
  - Uses .upsert() instead of .add() so re-indexing never crashes
  - clear_collection() added so build_index() always starts fresh
  - get_all_sources() added to list indexed documents
"""

import os
import chromadb

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

CHROMA_PATH     = os.getenv("CHROMA_PATH", "./data/chroma_db")
COLLECTION_NAME = "knowledge_base"

# ── Singleton client — created once, reused every request ────────────────────
_client:     chromadb.PersistentClient | None = None
_collection: chromadb.Collection       | None = None


# ── Connect to ChromaDB ───────────────────────────────────────────────────────

def get_collection():
    """
    Return the ChromaDB collection, creating a persistent client once
    and reusing it on every subsequent call (no reconnect overhead).
    """
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB connected — {_collection.count()} chunks loaded from disk")
    return _collection


# ── Hash Check — skip already-indexed files ───────────────────────────────────

def is_source_indexed(filename: str) -> bool:
    """
    Return True if at least one chunk from this filename already exists
    in ChromaDB. Used to skip re-indexing unchanged files.
    """
    try:
        collection = get_collection()
        results = collection.get(
            where={"source": filename},
            limit=1,
            include=[],
        )
        return len(results["ids"]) > 0
    except Exception:
        return False


def delete_source(filename: str):
    """Remove all chunks belonging to a specific source file."""
    collection = get_collection()
    results = collection.get(where={"source": filename}, include=[])
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"  ✓ Deleted {len(results['ids'])} chunks for: {filename}")


# ── Store Chunks ──────────────────────────────────────────────────────────────

def add_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """
    Store chunks and their embeddings in ChromaDB.
    Uses upsert() so running this twice never causes duplicate errors.

    Args:
        chunks:     List of chunk dicts from chunker.chunk_documents()
        embeddings: List of embedding vectors from embeddings.embed_texts()
    """
    if not chunks:
        logger.warning("No chunks to store!")
        return

    collection = get_collection()

    ids       = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"]     for chunk in chunks]
    metadatas = [{"source": chunk["source"]} for chunk in chunks]

    # upsert = insert if new, update if exists — safe to call multiple times
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info(f"  ✓ Stored {len(chunks)} chunks in ChromaDB")


# ── Search Chunks ─────────────────────────────────────────────────────────────

def search_chunks(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    """
    Find the most relevant chunks for a query embedding.

    Args:
        query_embedding: Embedding vector of the user's question.
        top_k:           Number of results to return.

    Returns:
        List of chunk dicts with text, source filename, and similarity score.
    """
    collection = get_collection()

    # Make sure we don't ask for more results than exist
    count = collection.count()
    if count == 0:
        logger.warning("ChromaDB is empty — run indexing first!")
        return []

    n = min(top_k, count)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text":   results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "score":  round(results["distances"][0][i], 4),
        })

    return chunks


# ── Utility Functions ─────────────────────────────────────────────────────────

def get_chunk_count() -> int:
    """Return total number of chunks stored in ChromaDB."""
    return get_collection().count()


def clear_collection():
    """
    Delete all chunks from ChromaDB.
    Only call this for a full manual re-index — NOT on every upload.
    """
    global _collection
    collection = get_collection()
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids=ids)
        logger.info(f"  ✓ Cleared {len(ids)} old chunks from ChromaDB")
    else:
        logger.info("  ChromaDB already empty — nothing to clear")
    _collection = None  # reset singleton so next call reconnects cleanly


def get_all_sources() -> list[str]:
    """Return a list of all unique source filenames currently indexed."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    results   = collection.get(include=["metadatas"])
    sources   = list({m["source"] for m in results["metadatas"]})
    return sorted(sources)


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nChroma DB path: {CHROMA_PATH}")
    print(f"Collection:     {COLLECTION_NAME}\n")

    count = get_chunk_count()
    print(f"  ✓ Total chunks in DB: {count}")

    sources = get_all_sources()
    if sources:
        print(f"  ✓ Indexed files: {', '.join(sources)}")
    else:
        print("  No files indexed yet — run pipeline.py first")

    print("\nVectorstore working correctly!")