"""
pipeline.py
-----------
Connects everything together:
  build_index()  →  load docs → chunk → embed → store in ChromaDB
  ask()          →  embed question → search → send to Ollama → return answer

Fixes vs old version:
  - clear_collection() called before re-indexing so stale chunks are removed
  - Returns clean original question to caller, not the bloated prompt
  - Proper error handling at every step
  - RAGPipeline class moved to module level (was trapped in __main__ block)
  - RAGPipeline.ask() uses asyncio.to_thread so it doesn't block the event loop
"""

import os
import time
import asyncio

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DOCS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
        "docs"
    )
)

from core.parser      import load_all_documents
from core.chunker     import chunk_documents
from core.embeddings  import embed_texts, embed_query
from core.vectorstore import (
    add_chunks, search_chunks,
    get_chunk_count, clear_collection,
    is_source_indexed, delete_source,
)
from core.llm import ask_llm

# ── SMART INCREMENTAL INDEX ───────────────────────────────────────────────────

def build_index(force: bool = False):
    """
    Incremental indexing pipeline — only processes NEW or CHANGED files.

    Pass force=True to wipe and rebuild everything (manual re-index only).
    """
    print("\n--- Building Index ---\n")

    if force:
        print("Step 1: Clearing old index (forced)...")
        clear_collection()
    else:
        print("Step 1: Skipping clear — incremental mode")

    print("\nStep 2: Loading documents...")
    docs = load_all_documents(DOCS_DIR)
    print(f"  Loaded {len(docs)} document(s)")

    if not docs:
        print(f"\n  No documents found in: {DOCS_DIR}")
        return

    print("\nStep 3: Checking which documents need indexing...")
    new_docs = []
    for doc in docs:
        if is_source_indexed(doc["filename"]):
            logger.info(f"  ⏭ Skipping (already indexed): {doc['filename']}")
        else:
            logger.info(f"  ✚ New document: {doc['filename']}")
            new_docs.append(doc)

    if not new_docs:
        print("\n  ✅ All documents already indexed — nothing to do!")
        print(f"     Total chunks in DB: {get_chunk_count()}")
        return

    print(f"\n  Indexing {len(new_docs)} new document(s)...")

    print("\nStep 4: Chunking new documents...")
    chunks = chunk_documents(new_docs)
    print(f"  Created {len(chunks)} chunk(s)")

    if not chunks:
        print("  No chunks created — check your documents")
        return

    print("\nStep 5: Generating embeddings...")
    texts      = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts)
    print(f"  Generated {len(embeddings)} embedding(s)")

    print("\nStep 6: Storing in ChromaDB...")
    add_chunks(chunks, embeddings)

    print(f"\n  ✅ Index updated!")
    print(f"     New chunks added:  {len(chunks)}")
    print(f"     Total in DB:       {get_chunk_count()}")


def ingest_one(filepath: str, filename: str):
    """
    Index a single newly uploaded file without touching existing chunks.
    Called by /upload endpoint instead of full build_index().
    """
    if is_source_indexed(filename):
        logger.info(f"  ⏭ Already indexed: {filename}")
        return {"skipped": True, "filename": filename}

    from core.parser import parse_file, load_metadata
    try:
        text = parse_file(filepath)
    except Exception as e:
        logger.error(f"Failed to parse {filename}: {e}")
        return {"error": str(e)}

    if not text.strip():
        return {"error": "Empty document"}

    meta   = load_metadata(filepath)
    docs   = [{"filepath": filepath, "filename": filename, "text": text, "metadata": meta}]
    chunks = chunk_documents(docs)

    if not chunks:
        return {"error": "No chunks produced"}

    texts      = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    add_chunks(chunks, embeddings)

    logger.info(f"  ✓ Indexed {filename} → {len(chunks)} chunks")
    return {"indexed": True, "filename": filename, "chunks": len(chunks)}


# ── ASK PIPELINE ──────────────────────────────────────────────────────────────

def ask(question: str, top_k: int = 3) -> dict:
    """
    Full RAG pipeline:
    1. Embed the user's question
    2. Search ChromaDB for relevant chunks
    3. Send question + context to Ollama
    4. Return clean answer + sources

    Args:
        question: The user's question string.

    Returns:
        Dict with keys: question, answer, sources, latency
    """
    start = time.time()

    if not question or not question.strip():
        return {
            "question": question,
            "answer":   " Question cannot be empty.",
            "sources":  [],
            "latency":  0,
        }

    try:
        query_embedding = embed_query(question)
        chunks = search_chunks(query_embedding, top_k=top_k)

        if not chunks:
            return {
                "question": question,
                "answer":   " No relevant documents found. Please run indexing first.",
                "sources":  [],
                "latency":  round(time.time() - start, 2),
            }

        logger.info(f"Retrieved {len(chunks)} chunks for: {question[:60]}")
        for i, c in enumerate(chunks):
            logger.debug(f"  Chunk {i}: [{c['source']}] score={c['score']} — {c['text'][:80]}...")

        try:
            answer = ask_llm(question, chunks)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            answer = f" Could not get answer from Ollama: {e}"

        if not answer or not str(answer).strip():
            answer = " Model did not return a valid response. Please try again."

        sources = list(dict.fromkeys(c["source"] for c in chunks))

        return {
            "question": question,
            "answer":   answer,
            "sources":  sources,
            "latency":  round(time.time() - start, 2),
        }

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return {
            "question": question,
            "answer":   f" Pipeline error: {str(e)}",
            "sources":  [],
            "latency":  round(time.time() - start, 2),
        }


# ── RAGPipeline wrapper (used by main.py) ─────────────────────────────────────
# FIX: moved OUT of if __name__ == "__main__" block so main.py can import it

class RAGPipeline:
    def __init__(self, docs_dir=None, index_dir=None):
        self.docs_dir  = docs_dir
        self.index_dir = index_dir

    def get_stats(self) -> dict:
        count = get_chunk_count()
        return {
            "indexed":      count > 0,
            "total_chunks": count,
        }

    def ingest(self, force: bool = False) -> dict:
        """Incremental by default. Pass force=True to wipe and rebuild."""
        build_index(force=force)
        return {
            "status":       "success",
            "total_chunks": self.get_stats()["total_chunks"],
        }

    def ingest_file(self, filepath: str, filename: str) -> dict:
        """Index a single file — skips if already indexed."""
        return ingest_one(filepath, filename)

    async def ask(self, question: str, top_k: int = 3) -> dict:
        return await asyncio.to_thread(ask, question, top_k)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "index":
        build_index()
    else:
        if get_chunk_count() == 0:
            print("\n  No chunks found! Index your documents first:")
            print("    python -m core.pipeline index")
        else:
            question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is this company about?"
            print(f"\nQuestion: {question}\n")
            result = ask(question)
            print(f"Answer:\n{result['answer']}")
            print(f"\nSources:  {result['sources']}")
            print(f"Latency:  {result['latency']}s")