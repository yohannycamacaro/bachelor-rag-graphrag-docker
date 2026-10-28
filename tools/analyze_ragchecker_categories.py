from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "results" / "automatic_evaluation"
QUESTIONS = ROOT / "data" / "questions" / "docker_support_questions.jsonl"
CLASSIC = AUTO / "resultados_finales_classic_48.json"
GRAPH = AUTO / "resultados_finales_graph_48.json"
CSV_OUTPUT = AUTO / "ragchecker_metrics_by_category_48.csv"
JSON_OUTPUT = AUTO / "ragchecker_metrics_by_category_48.json"
REPORT_OUTPUT = AUTO / "qualitative_case_analysis_48.md"
HTML_OUTPUT = ROOT / "docs" / "ragchecker_category_results.html"

METRICS = ("precision", "recall", "f1")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_results(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["query_id"]): item for item in data["results"]}


def rounded(value: float) -> float:
    return round(value * 100, 1)


def category_rows(questions: dict[str, dict], classic: dict[str, dict], graph: dict[str, dict]) -> list[dict]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for question_id, question in questions.items():
        grouped[str(question["category"])].append(question_id)

    rows = []
    for category, question_ids in sorted(grouped.items()):
        row = {
            "category": category,
            "category_label": questions[question_ids[0]]["category_label"],
            "question_count": len(question_ids),
        }
        for metric in METRICS:
            classic_mean = sum(float(classic[qid]["metrics"][metric]) for qid in question_ids) / len(question_ids)
            graph_mean = sum(float(graph[qid]["metrics"][metric]) for qid in question_ids) / len(question_ids)
            row[f"classic_{metric}"] = rounded(classic_mean)
            row[f"graph_{metric}"] = rounded(graph_mean)
            row[f"delta_{metric}"] = round(rounded(graph_mean) - rounded(classic_mean), 1)
        rows.append(row)
    return rows


def select_cases(questions: dict[str, dict], classic: dict[str, dict], graph: dict[str, dict]) -> list[tuple[str, str]]:
    deltas = {
        qid: float(graph[qid]["metrics"]["f1"]) - float(classic[qid]["metrics"]["f1"])
        for qid in questions
    }
    selected: list[tuple[str, str]] = []

    def add(label: str, candidates: list[str], key, reverse=False) -> None:
        for qid in sorted(candidates, key=key, reverse=reverse):
            if qid not in {item[1] for item in selected}:
                selected.append((label, qid))
                return

    all_ids = list(questions)
    add("Strongest GraphRAG advantage", all_ids, lambda qid: deltas[qid], reverse=True)
    add("Strongest Classic RAG advantage", all_ids, lambda qid: deltas[qid])
    add("Most similar result", all_ids, lambda qid: abs(deltas[qid]))
    multi_hop = [qid for qid, question in questions.items() if question["category"] == "multi_hop"]
    add("Representative Multi-Hop case", multi_hop, lambda qid: deltas[qid], reverse=True)
    return selected


def interpretation(classic_f1: float, graph_f1: float) -> str:
    delta = graph_f1 - classic_f1
    if delta >= 5:
        return "GraphRAG covers the reference answer more effectively in this case."
    if delta <= -5:
        return "Classic RAG provides the stronger balance of supported and covered claims in this case."
    return "Both methods obtain a similar F1 score; the graph structure provides no clear advantage here."


def write_report(cases, questions, classic, graph) -> None:
    lines = [
        "# Qualitative case analysis",
        "",
        "The cases below were selected from the completed RAGChecker evaluation. They illustrate the largest method differences, a near tie, and a representative Multi-Hop result. This is an explanatory case analysis, not a second manual scoring experiment.",
        "",
    ]
    for label, qid in cases:
        question = questions[qid]
        c = classic[qid]
        g = graph[qid]
        c_metrics = {key: rounded(float(c["metrics"][key])) for key in METRICS}
        g_metrics = {key: rounded(float(g["metrics"][key])) for key in METRICS}
        lines.extend(
            [
                f"## {label}: {qid}",
                "",
                f"**Category:** {question['category_label']}",
                "",
                f"**Question:** {question['question']}",
                "",
                f"**Reference answer:** {c['gt_answer']}",
                "",
                f"**Classic RAG:** Precision {c_metrics['precision']:.1f}%, Recall {c_metrics['recall']:.1f}%, F1 {c_metrics['f1']:.1f}%",
                "",
                c["response"],
                "",
                f"**GraphRAG:** Precision {g_metrics['precision']:.1f}%, Recall {g_metrics['recall']:.1f}%, F1 {g_metrics['f1']:.1f}%",
                "",
                g["response"],
                "",
                f"**Interpretation:** {interpretation(c_metrics['f1'], g_metrics['f1'])}",
                "",
            ]
        )
    REPORT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def metric_block(row: dict, metric: str) -> str:
    classic = float(row[f"classic_{metric}"])
    graph = float(row[f"graph_{metric}"])
    return f"""
    <div class="metric">
      <h3>{metric.upper()}</h3>
      <div class="bar-label"><span>Classic</span><strong>{classic:.1f}%</strong></div>
      <div class="track"><div class="classic" style="width:{classic}%"></div></div>
      <div class="bar-label"><span>Graph</span><strong>{graph:.1f}%</strong></div>
      <div class="track"><div class="graph" style="width:{graph}%"></div></div>
    </div>"""


def write_html(rows: list[dict]) -> None:
    cards = "".join(
        f"""<section><div class="heading"><h2>{html.escape(str(row['category_label']))}</h2><span>{row['question_count']} questions</span></div>
        <div class="metrics">{''.join(metric_block(row, metric) for metric in METRICS)}</div></section>"""
        for row in rows
    )
    best_recall = max(rows, key=lambda row: float(row["delta_recall"]))
    best_f1 = max(rows, key=lambda row: float(row["delta_f1"]))
    content = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RAGChecker results by category</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f5f7fa;color:#172033;font-family:Segoe UI,Arial,sans-serif}}main{{max-width:1120px;margin:36px auto;padding:0 24px 50px}}
h1{{margin:0 0 8px;font-size:30px}}header p{{margin:0;color:#5d6879}}.summary{{margin:24px 0;padding:16px 18px;background:#fff9e8;border-left:4px solid #d59b20;line-height:1.5}}
section{{background:white;border:1px solid #dce2e8;border-radius:8px;padding:20px;margin:14px 0}}.heading{{display:flex;justify-content:space-between;align-items:center}}h2{{font-size:18px;margin:0}}.heading span{{color:#667085;font-size:13px}}
.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:18px}}h3{{font-size:13px;margin:0 0 12px;color:#4b5563}}.bar-label{{display:flex;justify-content:space-between;font-size:13px;margin-top:8px}}
.track{{height:13px;background:#edf1f5;border-radius:3px;overflow:hidden}}.classic,.graph{{height:100%}}.classic{{background:#174a73}}.graph{{background:#0b8f87}}@media(max-width:760px){{.metrics{{grid-template-columns:1fr}}}}
</style></head><body><main><header><h1>RAGChecker results by category</h1><p>Classic RAG versus GraphRAG across six question categories, eight questions per category</p></header>
<div class="summary"><strong>Largest GraphRAG recall advantage:</strong> {html.escape(str(best_recall['category_label']))} ({best_recall['delta_recall']:+.1f} points). <strong>Largest GraphRAG F1 advantage:</strong> {html.escape(str(best_f1['category_label']))} ({best_f1['delta_f1']:+.1f} points).</div>{cards}</main></body></html>"""
    HTML_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUTPUT.write_text(content, encoding="utf-8")


def main() -> None:
    questions = {str(item["id"]): item for item in load_jsonl(QUESTIONS)}
    classic = load_results(CLASSIC)
    graph = load_results(GRAPH)
    if set(questions) != set(classic) or set(questions) != set(graph):
        raise ValueError("Question and result identifiers do not match")

    rows = category_rows(questions, classic, graph)
    AUTO.mkdir(parents=True, exist_ok=True)
    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    JSON_OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    cases = select_cases(questions, classic, graph)
    write_report(cases, questions, classic, graph)
    write_html(rows)

    print("Category metrics")
    for row in rows:
        print(
            f"- {row['category_label']}: "
            f"Classic F1={row['classic_f1']:.1f}%, Graph F1={row['graph_f1']:.1f}%, "
            f"delta={row['delta_f1']:+.1f}"
        )
    print("Selected cases: " + ", ".join(f"{label}={qid}" for label, qid in cases))
    print(CSV_OUTPUT)
    print(REPORT_OUTPUT)
    print(HTML_OUTPUT)


if __name__ == "__main__":
    main()
