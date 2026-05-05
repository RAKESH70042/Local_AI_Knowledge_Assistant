"""
visualize.py
------------
Reads eval_results.json and query_log.jsonl and produces
summary charts using Matplotlib.
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path

LOG_FILE  = Path("data/query_log.jsonl")
EVAL_FILE = Path("data/eval_results.json")
OUT_DIR   = Path("data/charts")
OUT_DIR.mkdir(exist_ok=True)


def load_log():
    if not LOG_FILE.exists():
        return []
    out = []
    for line in LOG_FILE.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except:
            pass
    return out


def load_eval():
    if not EVAL_FILE.exists():
        return []
    return json.loads(EVAL_FILE.read_text())


def chart_latency(entries):
    if not entries:
        print("  No query log data — skipping latency chart")
        return
    latencies = [e.get("latency_ms", 0) for e in entries]
    indices   = list(range(1, len(latencies) + 1))
    fig, ax   = plt.subplots(figsize=(10, 4))
    ax.plot(indices, latencies, marker='o', color='#2563eb', linewidth=1.5, markersize=4)
    ax.fill_between(indices, latencies, alpha=0.1, color='#2563eb')
    ax.set_title("Query Latency Over Time", fontsize=13, fontweight='bold')
    ax.set_xlabel("Query #")
    ax.set_ylabel("Latency (ms)")
    ax.grid(True, alpha=0.3)
    avg = sum(latencies) / len(latencies)
    ax.axhline(y=avg, color='red', linestyle='--', alpha=0.5, label=f"Avg: {round(avg,1)} ms")
    ax.legend()
    plt.tight_layout()
    path = OUT_DIR / "latency_over_time.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def chart_eval_metrics(results):
    if not results:
        print("  No eval data — run make.bat eval first")
        return
    questions = [f"Q{i+1}" for i in range(len(results))]
    metrics   = ["recall_at_k", "citation_coverage", "answer_grounding", "keyword_hit"]
    labels    = ["Recall@k", "Citation Coverage", "Answer Grounding", "Keyword Hit"]
    colors    = ["#2563eb", "#16a34a", "#d97706", "#9333ea"]
    x         = range(len(questions))
    width     = 0.2
    fig, ax   = plt.subplots(figsize=(10, 5))
    for i, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
        values = [r.get(metric, 0) for r in results]
        offset = (i - 1.5) * width
        bars   = ax.bar([xi + offset for xi in x], values, width, label=label, color=color, alpha=0.85)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{val:.2f}", ha='center', va='bottom', fontsize=8)
    ax.set_title("RAG Evaluation Metrics per Question", fontsize=13, fontweight='bold')
    ax.set_xticks(list(x))
    ax.set_xticklabels(questions)
    ax.set_ylabel("Score (0 - 1)")
    ax.set_ylim(0, 1.2)
    ax.legend(loc='upper right')
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    path = OUT_DIR / "eval_metrics.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def chart_sources(entries):
    if not entries:
        return
    source_counts = {}
    for e in entries:
        for s in e.get("sources", []):
            source_counts[s] = source_counts.get(s, 0) + 1
    if not source_counts:
        print("  No source data — skipping sources chart")
        return
    names  = list(source_counts.keys())
    counts = list(source_counts.values())
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(names, counts, color='#2563eb', alpha=0.8)
    ax.set_title("Most Referenced Sources", fontsize=13, fontweight='bold')
    ax.set_xlabel("Times Referenced")
    ax.grid(True, axis='x', alpha=0.3)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9)
    plt.tight_layout()
    path = OUT_DIR / "sources_usage.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


if __name__ == "__main__":
    print("\n" + "="*45)
    print("  GENERATING CHARTS")
    print("="*45)
    entries = load_log()
    results = load_eval()
    print(f"\n  Query log entries: {len(entries)}")
    print(f"  Eval results:      {len(results)}\n")
    if not entries and not results:
        print("  No data found! Ask questions in the UI first.")
    else:
        chart_latency(entries)
        chart_eval_metrics(results)
        chart_sources(entries)
        print(f"\n  All charts saved to: {OUT_DIR.resolve()}")
    print("="*45 + "\n")