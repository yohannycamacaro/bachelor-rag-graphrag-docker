from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def load_manual(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, list[float]]]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["category"]][row["method"]].append(float(row["overall"]) * 20.0)
    return rows, grouped


def load_automatic(path: Path) -> dict[str, dict[str, float | str]]:
    result: dict[str, dict[str, float | str]] = {}
    for row in csv.DictReader(path.open(encoding="utf-8-sig", newline="")):
        result[row["category_label"]] = {
            "question_count": float(row["question_count"]),
            "classic": float(row["classic_f1"]),
            "graph": float(row["graph_f1"]),
            "delta": float(row["f1_delta_graph_minus_classic"]),
        }
    return result


def bar(value: float, color: str) -> str:
    width = max(0.0, min(100.0, value))
    return (
        "<div class='bar-track'><div class='bar-fill' "
        f"style='width:{width:.1f}%;background:{color}'></div></div>"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", type=Path, required=True)
    parser.add_argument("--automatic", type=Path, required=True)
    parser.add_argument("--classic-json", type=Path, required=True)
    parser.add_argument("--graph-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.html.parent.mkdir(parents=True, exist_ok=True)

    manual_rows, manual = load_manual(args.manual)
    automatic = load_automatic(args.automatic)
    categories = list(automatic)

    comparison_rows: list[dict[str, object]] = []
    for category in categories:
        classic_manual_values = manual[category]["Classic RAG"]
        graph_manual_values = manual[category]["GraphRAG"]
        classic_manual = mean(classic_manual_values)
        graph_manual = mean(graph_manual_values)
        comparison_rows.append(
            {
                "category": category,
                "automatic_n_questions": int(automatic[category]["question_count"]),
                "automatic_classic_f1": automatic[category]["classic"],
                "automatic_graph_f1": automatic[category]["graph"],
                "automatic_delta": automatic[category]["delta"],
                "manual_n_question_pairs": len(classic_manual_values),
                "manual_classic_percent": round(classic_manual, 1),
                "manual_graph_percent": round(graph_manual, 1),
                "manual_delta": round(graph_manual - classic_manual, 1),
            }
        )

    csv_path = args.output_dir / "manual_vs_ragchecker_by_category.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(comparison_rows[0]))
        writer.writeheader()
        writer.writerows(comparison_rows)

    classic_manual_all = [float(row["overall"]) * 20.0 for row in manual_rows if row["method"] == "Classic RAG"]
    graph_manual_all = [float(row["overall"]) * 20.0 for row in manual_rows if row["method"] == "GraphRAG"]
    manual_overall_classic = mean(classic_manual_all)
    manual_overall_graph = mean(graph_manual_all)

    classic_data = json.loads(args.classic_json.read_text(encoding="utf-8"))
    graph_data = json.loads(args.graph_json.read_text(encoding="utf-8"))
    auto_overall_classic = float(classic_data["metrics"]["overall_metrics"]["f1"])
    auto_overall_graph = float(graph_data["metrics"]["overall_metrics"]["f1"])

    md_path = args.output_dir / "manual_vs_ragchecker_report.md"
    with md_path.open("w", encoding="utf-8") as file:
        file.write("# Vergleich der manuellen Evaluation mit RAGChecker\n\n")
        file.write("## Gesamtergebnis\n\n")
        file.write("| Evaluation | Classic RAG | GraphRAG | Delta Graph - Classic |\n")
        file.write("|---|---:|---:|---:|\n")
        file.write(
            f"| RAGChecker F1 (12 Fragen) | {auto_overall_classic:.1f} % | "
            f"{auto_overall_graph:.1f} % | {auto_overall_graph-auto_overall_classic:+.1f} |\n"
        )
        file.write(
            f"| Manuelle Bewertung (8 Fragenpaare, auf 0-100 normiert) | "
            f"{manual_overall_classic:.1f} % | {manual_overall_graph:.1f} % | "
            f"{manual_overall_graph-manual_overall_classic:+.1f} |\n\n"
        )
        file.write(
            "Die Prozentwerte dienen nur der gemeinsamen Darstellung. Die beiden Verfahren messen "
            "unterschiedliche Konstrukte: RAGChecker bewertet die Abdeckung referenzbasierter Claims, "
            "waehrend die manuelle Evaluation Korrektheit, Vollstaendigkeit, Nachvollziehbarkeit, "
            "Konsistenz und Quellenbezug beurteilt.\n\n"
        )
        file.write("## Vergleich nach Kategorie\n\n")
        file.write("| Kategorie | Auto C | Auto G | Auto Delta | n | Manuell C | Manuell G | Manuell Delta | n |\n")
        file.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in comparison_rows:
            file.write(
                f"| {row['category']} | {row['automatic_classic_f1']:.1f} | "
                f"{row['automatic_graph_f1']:.1f} | {row['automatic_delta']:+.1f} | "
                f"{row['automatic_n_questions']} | {row['manual_classic_percent']:.1f} | "
                f"{row['manual_graph_percent']:.1f} | {row['manual_delta']:+.1f} | "
                f"{row['manual_n_question_pairs']} |\n"
            )
        file.write("\n## Interpretation\n\n")
        file.write(
            "Beide Evaluationen zeigen Vorteile von GraphRAG bei relationalen Troubleshooting-Fragen "
            "und bei der Nachvollziehbarkeit. Gleichzeitig zeigen die Fehlfaelle H005 und H010, dass "
            "GraphRAG bei einer unpassenden Graphroute eine in sich plausible, aber fachlich falsche "
            "Antwort erzeugen kann. Daher ist GraphRAG kein allgemeiner Gewinner. Sein Nutzen haengt von "
            "der Qualitaet, Vollstaendigkeit und Fragepassung der modellierten Beziehungen ab.\n\n"
        )
        file.write(
            "Abweichungen zwischen den Verfahren sind erwartbar. Besonders bei einfachen Fakten- und "
            "prozeduralen Fragen bewertet die manuelle Stichprobe einzelne Antworten positiver, waehrend "
            "RAGChecker fehlende Referenz-Claims strenger bestraft. Aufgrund der kleinen manuellen "
            "Stichprobe sind die Werte als qualitative Plausibilisierung und nicht als zweite "
            "statistisch gleichwertige Messung zu interpretieren.\n"
        )

    rows_html = "".join(
        "<tr>"
        f"<td>{html.escape(str(row['category']))}</td>"
        f"<td>{row['automatic_classic_f1']:.1f}{bar(float(row['automatic_classic_f1']), '#183b67')}</td>"
        f"<td>{row['automatic_graph_f1']:.1f}{bar(float(row['automatic_graph_f1']), '#0d9bb7')}</td>"
        f"<td class='delta {'positive' if float(row['automatic_delta']) > 0 else 'negative'}'>{row['automatic_delta']:+.1f}</td>"
        f"<td>{row['manual_classic_percent']:.1f}{bar(float(row['manual_classic_percent']), '#183b67')}</td>"
        f"<td>{row['manual_graph_percent']:.1f}{bar(float(row['manual_graph_percent']), '#0d9bb7')}</td>"
        f"<td class='delta {'positive' if float(row['manual_delta']) > 0 else 'negative'}'>{row['manual_delta']:+.1f}</td>"
        "</tr>"
        for row in comparison_rows
    )

    args.html.write_text(
        f"""<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Manuelle Evaluation und RAGChecker</title><style>
:root{{--navy:#183b67;--cyan:#0d9bb7;--ink:#15233b;--muted:#59667a;--line:#d9e0e8;--paper:#fff;--bg:#f4f7fa}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Arial,sans-serif}}main{{max-width:1240px;margin:auto;padding:34px}}
h1{{font-size:38px;margin:0 0 8px}}.lead{{color:var(--muted);font-size:18px;margin-bottom:28px}}.summary{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:24px}}
.panel{{background:var(--paper);border:1px solid var(--line);padding:22px;border-radius:6px}}.panel h2{{margin:0 0 16px;font-size:19px}}.metric{{display:grid;grid-template-columns:1fr auto;gap:10px;margin:12px 0}}.metric strong{{font-size:24px}}
.classic{{color:var(--navy)}}.graph{{color:var(--cyan)}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid var(--line);padding:11px;text-align:right;vertical-align:top}}th:first-child,td:first-child{{text-align:left}}th{{background:var(--navy);color:white;font-size:13px}}td{{font-variant-numeric:tabular-nums}}
.bar-track{{height:5px;background:#e7ecf2;margin-top:6px;min-width:90px}}.bar-fill{{height:100%}}.delta{{font-weight:bold}}.positive{{color:#087b48}}.negative{{color:#b52b2b}}.note{{margin-top:22px;background:#eaf6f8;border-left:5px solid var(--cyan);padding:18px;line-height:1.55}}.warning{{background:#fff4df;border-left-color:#d79015}}
@media(max-width:850px){{main{{padding:18px}}.summary{{grid-template-columns:1fr}}table{{font-size:11px}}th,td{{padding:6px}}h1{{font-size:30px}}}}
</style></head><body><main><h1>Manuelle Evaluation und RAGChecker</h1>
<p class='lead'>Classic RAG und GraphRAG im Docker-Compose-Challenge-Set</p>
<section class='summary'><div class='panel'><h2>RAGChecker · 12 Fragen</h2><div class='metric'><span>Classic RAG F1</span><strong class='classic'>{auto_overall_classic:.1f} %</strong></div><div class='metric'><span>GraphRAG F1</span><strong class='graph'>{auto_overall_graph:.1f} %</strong></div><div class='metric'><span>Delta</span><strong>{auto_overall_graph-auto_overall_classic:+.1f}</strong></div></div>
<div class='panel'><h2>Manuelle Stichprobe · 8 Fragenpaare</h2><div class='metric'><span>Classic RAG</span><strong class='classic'>{manual_overall_classic:.1f} %</strong></div><div class='metric'><span>GraphRAG</span><strong class='graph'>{manual_overall_graph:.1f} %</strong></div><div class='metric'><span>Delta</span><strong>{manual_overall_graph-manual_overall_classic:+.1f}</strong></div></div></section>
<table><thead><tr><th rowspan='2'>Kategorie</th><th colspan='3'>RAGChecker F1</th><th colspan='3'>Manuell, normiert</th></tr><tr><th>Classic</th><th>Graph</th><th>Delta</th><th>Classic</th><th>Graph</th><th>Delta</th></tr></thead><tbody>{rows_html}</tbody></table>
<div class='note'><strong>Kernaussage:</strong> Beide Evaluationen bestaetigen GraphRAG-Vorteile bei relationalem Troubleshooting und Nachvollziehbarkeit. H005 und H010 zeigen jedoch, dass eine falsche Graphroute zu plausibel klingenden, aber fachlich falschen Antworten fuehren kann.</div>
<div class='note warning'><strong>Methodischer Hinweis:</strong> Die Werte sind nicht direkt gleichzusetzen. RAGChecker misst referenzbasierte Claim-Abdeckung; die manuelle Bewertung beurteilt fuenf qualitative Kriterien. Die Normalisierung auf 0-100 dient nur der gemeinsamen Visualisierung.</div>
</main></body></html>""",
        encoding="utf-8",
    )

    print(f"Saved CSV: {csv_path}")
    print(f"Saved report: {md_path}")
    print(f"Saved dashboard: {args.html}")
    print(f"Manual overall: Classic={manual_overall_classic:.1f}, Graph={manual_overall_graph:.1f}")
    print(f"Automatic overall: Classic={auto_overall_classic:.1f}, Graph={auto_overall_graph:.1f}")


if __name__ == "__main__":
    main()
