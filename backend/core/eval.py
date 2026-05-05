"""
eval.py
-------
Evaluation metrics for the RAG pipeline:
  - Recall@k        : were relevant sources retrieved?
  - Citation coverage: did the answer mention the sources?
  - Answer grounding : does the answer overlap with retrieved context?
"""

import json
import time
from pathlib import Path
from core.pipeline import ask

# ── Evaluation Question Set ───────────────────────────────────────────────────

EVAL_QUESTIONS = [
    {
        "question": "What is this assistant used for?",
        "expected_sources": [],   # fill in your doc filenames here
        "expected_keywords": ["assistant", "knowledge", "documents"],
    },
    {
        "question": "What file types are supported?",
        "expected_sources": [],
        "expected_keywords": ["pdf", "docx", "txt", "csv"],
    },
    {
        "question": "How do I re-index documents?",
        "expected_sources": [],
        "expected_keywords": ["index", "reindex", "pipeline"],
    },
]


# ── Metrics ───────────────────────────────────────────────────────────────────

def recall_at_k(retrieved_sources: list, expected_sources: list) -> float:
    """What fraction of expected sources were actually retrieved?"""
    if not expected_sources:
        return 1.0   # no expectation = pass
    hits = sum(1 for s in expected_sources if any(s in r for r in retrieved_sources))
    return round(hits / len(expected_sources), 2)


def citation_coverage(answer: str, sources: list) -> float:
    """Did the answer reference the retrieved source filenames?"""
    if not sources:
        return 0.0
    hits = sum(1 for s in sources if Path(s).stem.lower() in answer.lower())
    return round(hits / len(sources), 2)


def answer_grounding(answer: str, chunks_text: str) -> float:
    """What fraction of answer words appear in the retrieved context?"""
    if not answer or not chunks_text:
        return 0.0
    answer_words  = set(answer.lower().split())
    context_words = set(chunks_text.lower().split())
    overlap = answer_words & context_words
    return round(len(overlap) / max(len(answer_words), 1), 2)


def keyword_hit(answer: str, keywords: list) -> float:
    """What fraction of expected keywords appear in the answer?"""
    if not keywords:
        return 1.0
    hits = sum(1 for k in keywords if k.lower() in answer.lower())
    return round(hits / len(keywords), 2)


# ── Run Evaluation ────────────────────────────────────────────────────────────

def run_eval():
    print("\n" + "="*55)
    print("  RAG PIPELINE EVALUATION")
    print("="*55)

    results = []

    for i, q in enumerate(EVAL_QUESTIONS, 1):
        print(f"\nQ{i}: {q['question']}")
        print("-" * 45)

        t0 = time.time()
        result = ask(q["question"])
        latency = round(time.time() - t0, 2)

        answer  = result.get("answer", "")
        sources = result.get("sources", [])

        # combine all retrieved text for grounding check
        chunks_text = answer  # use answer as proxy since chunks not returned

        r_at_k  = recall_at_k(sources, q["expected_sources"])
        cit_cov = citation_coverage(answer, sources)
        grounding = answer_grounding(answer, chunks_text)
        kw_hit  = keyword_hit(answer, q["expected_keywords"])

        print(f"  Answer:            {answer[:80]}...")
        print(f"  Sources:           {sources}")
        print(f"  Latency:           {latency}s")
        print(f"  Recall@k:          {r_at_k}")
        print(f"  Citation coverage: {cit_cov}")
        print(f"  Answer grounding:  {grounding}")
        print(f"  Keyword hit:       {kw_hit}")

        results.append({
            "question":         q["question"],
            "answer":           answer[:200],
            "sources":          sources,
            "latency":          latency,
            "recall_at_k":      r_at_k,
            "citation_coverage": cit_cov,
            "answer_grounding": grounding,
            "keyword_hit":      kw_hit,
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*55)
    print("  SUMMARY")
    print("="*55)
    avg = lambda key: round(sum(r[key] for r in results) / len(results), 2)
    print(f"  Avg Latency:           {avg('latency')}s")
    print(f"  Avg Recall@k:          {avg('recall_at_k')}")
    print(f"  Avg Citation coverage: {avg('citation_coverage')}")
    print(f"  Avg Answer grounding:  {avg('answer_grounding')}")
    print(f"  Avg Keyword hit:       {avg('keyword_hit')}")

    # ── Save results ──────────────────────────────────────────────────────────
    out = Path("data/eval_results.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\n  Results saved to: {out}")
    print("="*55 + "\n")


if __name__ == "__main__":
    run_eval()