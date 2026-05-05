"""
llm.py
------
Sends retrieved context + question to Ollama and returns an answer.
Everything runs locally on your PC via Ollama.
"""

import os
import ollama

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")


# ── Build Prompt ──────────────────────────────────────────────────────────────

def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}"
        for c in context_chunks
    )
    return f"""You are a helpful assistant. Use the context below to answer the question.
Keep your answer clear and concise. If the answer is not in the context, say so honestly.

Context:
{context}

Question:
{question}

Answer:"""


# ── Ask LLM (normal) ──────────────────────────────────────────────────────────

def ask_llm(question: str, context_chunks: list[dict]) -> str:
    prompt = build_prompt(question, context_chunks)
    logger.info(f"Sending prompt to Ollama model: {MODEL}")

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.message.content

        if not answer or not answer.strip():
            logger.warning("Ollama returned empty response")
            return "⚠️ The model returned an empty response. Please try again."

        return answer.strip()

    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise RuntimeError(
            f"Could not reach Ollama. Make sure it is running.\n"
            f"Run: ollama serve\n"
            f"Error: {e}"
        )


# ── Ask LLM (streaming) ───────────────────────────────────────────────────────

def ask_llm_stream(question: str, context_chunks: list[dict]):
    """Stream answer from Ollama token by token."""
    prompt = build_prompt(question, context_chunks)
    logger.info(f"Streaming from Ollama model: {MODEL}")

    try:
        stream = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            token = chunk['message']['content']
            if token:
                yield token

    except Exception as e:
        logger.error(f"Ollama stream error: {e}")
        yield f"⚠️ Stream error: {e}"
    # ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nModel: {MODEL}\n")

    test_chunks = [
        {
            "source": "test.txt",
            "text": "Acme Corp was founded in 2015 in Bangalore. "
                    "Our mission is to make data workflows simple and reliable.",
        }
    ]

    question = "When was Acme Corp founded and where?"
    print(f"Question: {question}\n")
    print("Asking Ollama...\n")

    try:
        answer = ask_llm(question, test_chunks)
        print(f"Answer: {answer}")
        print("\nLLM working correctly!")
    except RuntimeError as e:
        print(f"\n❌ {e}")
        print("Make sure Ollama is running: ollama serve")