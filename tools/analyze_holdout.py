from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "holdout_set"
QUESTIONS = ROOT / "data" / "questions" / "docker_support_holdout_questions.jsonl"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


questions = {
    q["id"]: q
    for q in (json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines() if line.strip())
}
data = {
    "classic": load(OUT / "ragchecker_holdout_classic_results.json"),
    "graph": load(OUT / "ragchecker_holdout_graph_results.json"),
}

per_question = {}
for method, payload in data.items():
    for item in payload["results"]:
        per_question.setdefault(item["query_id"], {})[method] = item

categories = defaultdict(lambda: {"classic": [], "graph": []})
for qid, pair in per_question.items():
    category = questions[qid]["category_label"]
    for method in ("classic", "graph"):
        categories[category][method].append(pair[method]["metrics"])


def avg(rows, key):
    return sum(float(row[key]) for row in rows) / len(rows) * 100


category_rows = []
for category in sorted(categories):
    c = categories[category]["classic"]
    g = categories[category]["graph"]
    category_rows.append({
        "category": category,
        "n": len(c),
        "classic_precision": avg(c, "precision"),
        "classic_recall": avg(c, "recall"),
        "classic_f1": avg(c, "f1"),
        "graph_precision": avg(g, "precision"),
        "graph_recall": avg(g, "recall"),
        "graph_f1": avg(g, "f1"),
        "delta_f1": avg(g, "f1") - avg(c, "f1"),
    })

question_rows = []
for qid in sorted(per_question):
    c = per_question[qid]["classic"]["metrics"]
    g = per_question[qid]["graph"]["metrics"]
    question_rows.append({
        "id": qid,
        "category": questions[qid]["category_label"],
        "question": questions[qid]["question"],
        "classic_f1": float(c["f1"]) * 100,
        "graph_f1": float(g["f1"]) * 100,
        "delta_f1": (float(g["f1"]) - float(c["f1"])) * 100,
    })

with (OUT / "holdout_metrics_by_category.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=category_rows[0].keys())
    writer.writeheader(); writer.writerows(category_rows)

classic = data["classic"]["metrics"]["overall_metrics"]
graph = data["graph"]["metrics"]["overall_metrics"]
cost = sum(data[m]["evaluation_metadata"]["estimated_openai_cost_usd"] for m in data)

md = [
    "# Frozen Holdout Evaluation",
    "",
    "The 12 questions were frozen before RAGChecker evaluation. The retrievers were not changed after result inspection.",
    "",
    "## Overall metrics",
    "",
    "| Method | Precision | Recall | F1 |",
    "|---|---:|---:|---:|",
    f"| Classic RAG | {classic['precision']:.1f} | {classic['recall']:.1f} | {classic['f1']:.1f} |",
    f"| GraphRAG | {graph['precision']:.1f} | {graph['recall']:.1f} | {graph['f1']:.1f} |",
    "",
    f"Estimated OpenAI cost: {cost:.4f} USD.",
    "",
    "## Category metrics",
    "",
    "| Category | n | Classic P | Classic R | Classic F1 | Graph P | Graph R | Graph F1 | Delta |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for r in category_rows:
    md.append(f"| {r['category']} | {r['n']} | {r['classic_precision']:.1f} | {r['classic_recall']:.1f} | {r['classic_f1']:.1f} | {r['graph_precision']:.1f} | {r['graph_recall']:.1f} | {r['graph_f1']:.1f} | {r['delta_f1']:+.1f} |")
md += ["", "## Per-question F1", "", "| ID | Category | Classic F1 | Graph F1 | Delta |", "|---|---|---:|---:|---:|"]
for r in question_rows:
    md.append(f"| {r['id']} | {r['category']} | {r['classic_f1']:.1f} | {r['graph_f1']:.1f} | {r['delta_f1']:+.1f} |")
(OUT / "holdout_evaluation_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

rows_html = "".join(
    f"<tr><td>{html.escape(r['category'])}</td><td>{r['n']}</td><td>{r['classic_precision']:.1f}</td><td>{r['classic_recall']:.1f}</td><td>{r['classic_f1']:.1f}</td><td>{r['graph_precision']:.1f}</td><td>{r['graph_recall']:.1f}</td><td>{r['graph_f1']:.1f}</td><td class={'pos' if r['delta_f1'] >= 0 else 'neg'}>{r['delta_f1']:+.1f}</td></tr>"
    for r in category_rows
)
q_html = "".join(
    f"<tr><td>{r['id']}</td><td>{html.escape(r['category'])}</td><td>{r['classic_f1']:.1f}</td><td>{r['graph_f1']:.1f}</td><td class={'pos' if r['delta_f1'] >= 0 else 'neg'}>{r['delta_f1']:+.1f}</td></tr>"
    for r in question_rows
)
page = f"""<!doctype html><html><head><meta charset='utf-8'><title>Holdout RAG Evaluation</title><style>
body{{font-family:Arial,sans-serif;margin:36px;color:#10274b;background:#f5f7fa}}h1{{font-size:38px}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:18px;max-width:900px}}.card{{background:white;border-top:5px solid #1f77b4;padding:20px;box-shadow:0 2px 8px #ccd}}.metric{{font-size:30px;font-weight:700}}table{{border-collapse:collapse;width:100%;background:white;margin:22px 0}}th{{background:#163f73;color:white}}th,td{{padding:10px;border:1px solid #d7dee8;text-align:right}}th:first-child,td:first-child,td:nth-child(2){{text-align:left}}.pos{{color:#16813d;font-weight:700}}.neg{{color:#b3261e;font-weight:700}}small{{color:#556}}
</style></head><body><h1>Frozen Holdout: Classic RAG vs GraphRAG</h1><p>12 unseen questions, two per category. Retrievers frozen before evaluation.</p><div class='cards'><div class='card'><h2>Classic RAG</h2><div class='metric'>F1 {classic['f1']:.1f}</div><p>Precision {classic['precision']:.1f} · Recall {classic['recall']:.1f}</p></div><div class='card'><h2>GraphRAG</h2><div class='metric'>F1 {graph['f1']:.1f}</div><p>Precision {graph['precision']:.1f} · Recall {graph['recall']:.1f}</p></div></div><h2>By category</h2><table><tr><th>Category</th><th>n</th><th>Classic P</th><th>Classic R</th><th>Classic F1</th><th>Graph P</th><th>Graph R</th><th>Graph F1</th><th>Delta</th></tr>{rows_html}</table><h2>Per question</h2><table><tr><th>ID</th><th>Category</th><th>Classic F1</th><th>Graph F1</th><th>Delta</th></tr>{q_html}</table><small>Estimated OpenAI cost: {cost:.4f} USD.</small></body></html>"""
(ROOT / "docs" / "holdout_ragchecker_results.html").write_text(page, encoding="utf-8")

print("\n".join(md[:22]))
print(f"HTML: {ROOT / 'docs' / 'holdout_ragchecker_results.html'}")
