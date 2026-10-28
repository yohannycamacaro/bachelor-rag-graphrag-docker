from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTION_PATH = ROOT / "data" / "questions" / "docker_support_challenge_questions.jsonl"
RESULT_DIR = ROOT / "results" / "challenge_set" / "automatic_evaluation"
CLASSIC_PATH = RESULT_DIR / "challenge_results_classic_12.json"
GRAPH_PATH = RESULT_DIR / "challenge_results_graph_12.json"
CSV_PATH = RESULT_DIR / "challenge_ragchecker_by_category.csv"
MD_PATH = RESULT_DIR / "challenge_ragchecker_report.md"
HTML_PATH = ROOT / "docs" / "challenge_ragchecker_results.html"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    questions = {
        item["id"]: item
        for item in (
            json.loads(line)
            for line in QUESTION_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    datasets = {
        "classic": json.loads(CLASSIC_PATH.read_text(encoding="utf-8")),
        "graph": json.loads(GRAPH_PATH.read_text(encoding="utf-8")),
    }

    by_id: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    by_category: dict[str, dict[str, list[dict[str, float]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for method, dataset in datasets.items():
        for result in dataset["results"]:
            question_id = str(result["query_id"])
            metrics = {key: float(result["metrics"][key]) * 100 for key in ("precision", "recall", "f1")}
            by_id[question_id][method] = {"result": result, "metrics": metrics}
            category = str(questions[question_id]["category"])
            by_category[category][method].append(metrics)

    category_rows: list[dict[str, object]] = []
    for category, methods in sorted(by_category.items()):
        row: dict[str, object] = {
            "category": category,
            "category_label": next(
                str(q["category_label"]) for q in questions.values() if q["category"] == category
            ),
            "question_count": len(methods["classic"]),
        }
        for method in ("classic", "graph"):
            for metric in ("precision", "recall", "f1"):
                row[f"{method}_{metric}"] = round(
                    mean([values[metric] for values in methods[method]]), 1
                )
        row["f1_delta_graph_minus_classic"] = round(
            float(row["graph_f1"]) - float(row["classic_f1"]), 1
        )
        category_rows.append(row)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(category_rows[0]))
        writer.writeheader()
        writer.writerows(category_rows)

    question_rows: list[dict[str, object]] = []
    for question_id, question in questions.items():
        classic = by_id[question_id]["classic"]
        graph = by_id[question_id]["graph"]
        delta = round(float(graph["metrics"]["f1"]) - float(classic["metrics"]["f1"]), 1)
        question_rows.append(
            {
                "question_id": question_id,
                "category_label": question["category_label"],
                "question": question["question"],
                "classic_f1": round(float(classic["metrics"]["f1"]), 1),
                "graph_f1": round(float(graph["metrics"]["f1"]), 1),
                "delta": delta,
                "classic_response": classic["result"]["response"],
                "graph_response": graph["result"]["response"],
                "reference": classic["result"]["gt_answer"],
            }
        )

    graph_example = max(question_rows, key=lambda row: float(row["delta"]))
    classic_example = min(question_rows, key=lambda row: float(row["delta"]))

    classic_meta = datasets["classic"].get("evaluation_metadata", {})
    graph_meta = datasets["graph"].get("evaluation_metadata", {})
    total_cost = float(classic_meta.get("estimated_openai_cost_usd") or 0) + float(
        graph_meta.get("estimated_openai_cost_usd") or 0
    )

    with MD_PATH.open("w", encoding="utf-8") as file:
        file.write("# Challenge-Set: RAGChecker-Auswertung\n\n")
        file.write("## Gesamtergebnis\n\n")
        file.write("| Methode | Precision | Recall | F1 |\n|---|---:|---:|---:|\n")
        for method, label in (("classic", "Classic RAG"), ("graph", "GraphRAG")):
            overall = datasets[method]["metrics"]["overall_metrics"]
            file.write(
                f"| {label} | {overall['precision']:.1f} % | {overall['recall']:.1f} % | {overall['f1']:.1f} % |\n"
            )
        file.write(f"\nGeschaetzte OpenAI-Kosten: {total_cost:.4f} USD.\n\n")
        file.write("## Ergebnisse nach Kategorie\n\n")
        file.write("| Kategorie | n | Classic P | Classic R | Classic F1 | Graph P | Graph R | Graph F1 | F1 Delta |\n")
        file.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in category_rows:
            file.write(
                "| {category_label} | {question_count} | {classic_precision:.1f} | "
                "{classic_recall:.1f} | {classic_f1:.1f} | {graph_precision:.1f} | "
                "{graph_recall:.1f} | {graph_f1:.1f} | {f1_delta_graph_minus_classic:+.1f} |\n".format(**row)
            )
        file.write("\n## Konkrete Beispiele fuer die Abschlussprasentation\n\n")
        for title, row in (("Staerkster GraphRAG-Vorteil", graph_example), ("Staerkster Classic-RAG-Vorteil", classic_example)):
            file.write(f"### {title}: {row['question_id']}\n\n")
            file.write(f"**Kategorie:** {row['category_label']}\n\n")
            file.write(f"**Frage:** {row['question']}\n\n")
            file.write(
                f"**F1:** Classic {row['classic_f1']:.1f} %, Graph {row['graph_f1']:.1f} %, Delta {row['delta']:+.1f}.\n\n"
            )
            file.write(f"**Referenzantwort:** {row['reference']}\n\n")
            file.write(f"**Classic RAG:** {row['classic_response']}\n\n")
            file.write(f"**GraphRAG:** {row['graph_response']}\n\n")

    category_html = "".join(
        f"<tr><td>{html.escape(str(row['category_label']))}</td><td>{row['classic_precision']:.1f}</td>"
        f"<td>{row['classic_recall']:.1f}</td><td>{row['classic_f1']:.1f}</td>"
        f"<td>{row['graph_precision']:.1f}</td><td>{row['graph_recall']:.1f}</td>"
        f"<td>{row['graph_f1']:.1f}</td><td class={'pos' if float(row['f1_delta_graph_minus_classic']) > 0 else 'neg'}>"
        f"{row['f1_delta_graph_minus_classic']:+.1f}</td></tr>"
        for row in category_rows
    )
    cards = "".join(
        f"<article><h2>{title}</h2><h3>{row['question_id']} · {html.escape(str(row['category_label']))}</h3>"
        f"<p><strong>Frage:</strong> {html.escape(str(row['question']))}</p>"
        f"<p class='score'>Classic F1 {row['classic_f1']:.1f} % · Graph F1 {row['graph_f1']:.1f} % · Delta {row['delta']:+.1f}</p>"
        f"<h4>Classic RAG</h4><p>{html.escape(str(row['classic_response']))}</p>"
        f"<h4>GraphRAG</h4><p>{html.escape(str(row['graph_response']))}</p></article>"
        for title, row in (("Staerkster GraphRAG-Vorteil", graph_example), ("Staerkster Classic-RAG-Vorteil", classic_example))
    )
    HTML_PATH.write_text(
        f"""<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Challenge-Set RAGChecker</title><style>
body{{font-family:Arial,sans-serif;margin:0;background:#f5f7fa;color:#17233b}}main{{max-width:1180px;margin:auto;padding:32px}}
h1{{font-size:36px;margin-bottom:8px}}.lead{{color:#4b5870}}table{{width:100%;border-collapse:collapse;background:white;margin:24px 0}}
th,td{{padding:12px;border:1px solid #d9dee8;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{background:#173b67;color:white}}
.pos{{color:#087b48;font-weight:bold}}.neg{{color:#b22b2b;font-weight:bold}}.examples{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
article{{background:white;padding:22px;border:1px solid #d9dee8;border-radius:6px}}article p{{line-height:1.5}}.score{{font-weight:bold;color:#006f8a}}
@media(max-width:800px){{.examples{{grid-template-columns:1fr}}table{{font-size:12px}}th,td{{padding:6px}}}}
</style></head><body><main><h1>Challenge-Set: Classic RAG vs GraphRAG</h1>
<p class='lead'>12 anspruchsvolle Fragen, zwei pro Kategorie. Finale RAGChecker-Auswertung.</p>
<table><thead><tr><th>Kategorie</th><th>Classic P</th><th>Classic R</th><th>Classic F1</th><th>Graph P</th><th>Graph R</th><th>Graph F1</th><th>F1 Delta</th></tr></thead><tbody>{category_html}</tbody></table>
<section class='examples'>{cards}</section></main></body></html>""",
        encoding="utf-8",
    )

    print(f"Saved CSV: {CSV_PATH}")
    print(f"Saved report: {MD_PATH}")
    print(f"Saved dashboard: {HTML_PATH}")
    print(f"Graph example: {graph_example['question_id']} ({graph_example['delta']:+.1f} F1)")
    print(f"Classic example: {classic_example['question_id']} ({classic_example['delta']:+.1f} F1)")
    print(f"Total estimated cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
