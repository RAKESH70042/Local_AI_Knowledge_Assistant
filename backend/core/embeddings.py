"""
embeddings.py
-------------
Converts text chunks into vector embeddings using sentence-transformers.
Everything runs locally on your PC — no internet needed after first download.
"""

import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# ── Load model once globally ──────────────────────────────────────────────────
# This avoids reloading the model on every call (slow!)
# The model downloads automatically on first run (~130MB)

logger.info(f"Loading embedding model: {MODEL_NAME}")

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Embedding model ready!")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise


# ── Embed Multiple Texts ──────────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text strings into embeddings.
    Used when indexing document chunks into ChromaDB.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each is a list of floats).
    """
    if not texts:
        return []

    logger.info(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,          # process 32 chunks at a time (low RAM friendly)
        normalize_embeddings=True,  # needed for cosine similarity search
    )
    return embeddings.tolist()


# ── Embed Single Query ────────────────────────────────────────────────────────

def embed_query(query: str) -> list[float]:
    """
    Convert a single query string into an embedding.
    Used at search time when the user asks a question.

    Args:
        query: The user's question string.

    Returns:
        Single embedding vector as a list of floats.
    """
    embedding = model.encode(
        query,
        normalize_embeddings=True,
    )
    return embedding.tolist()


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nModel: {MODEL_NAME}\n")

    test_texts = [
        "What is the company onboarding process?",
        "How do I set up my development environment?",
        "What is our data security policy?",
    ]

    print("Testing embed_texts()...")
    embeddings = embed_texts(test_texts)
    print(f"  ✓ Generated {len(embeddings)} embeddings")
    print(f"  ✓ Each embedding has {len(embeddings[0])} dimensions")

    print("\nTesting embed_query()...")
    query_embedding = embed_query("tell me about onboarding")
    print(f"  ✓ Query embedding has {len(query_embedding)} dimensions")

    print("\nEmbeddings working correctly!")