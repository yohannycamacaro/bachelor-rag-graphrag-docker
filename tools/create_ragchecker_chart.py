from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "automatic_evaluation"
OUTPUT = ROOT / "docs" / "ragchecker_results.html"


def load_result(filename: str) -> dict:
    path = RESULTS / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def metric_card(label: str, classic: float, graph: float) -> str:
    def bar(name: str, value: float, css: str) -> str:
        width = max(0.0, min(float(value), 100.0))
        return (
            f'<div class="row"><span>{name}</span><div class="track">'
            f'<div class="bar {css}" style="width:{width:.1f}%"></div>'
            f'<strong>{width:.1f}%</strong></div></div>'
        )

    difference = graph - classic
    winner = "GraphRAG" if difference > 0 else "Classic RAG" if difference < 0 else "Igual"
    return (
        f'<section><div class="metric-heading"><h2>{label}</h2>'
        f'<span>{winner}: {abs(difference):.1f} points</span></div>'
        f'{bar("Classic RAG", classic, "classic")}'
        f'{bar("GraphRAG", graph, "graph")}</section>'
    )


def main() -> None:
    classic_data = load_result("resultados_finales_classic_48.json")
    graph_data = load_result("resultados_finales_graph_48.json")
    classic = classic_data["metrics"]["overall_metrics"]
    graph = graph_data["metrics"]["overall_metrics"]
    classic_meta = classic_data.get("evaluation_metadata", {})
    graph_meta = graph_data.get("evaluation_metadata", {})
    classic_cost = float(
        classic_meta.get(
            "estimated_openai_cost_usd_including_repair",
            classic_meta.get("estimated_openai_cost_usd", 0),
        )
    )
    graph_cost = float(graph_meta.get("estimated_openai_cost_usd", 0))
    total_cost = classic_cost + graph_cost
    cards = "".join(
        metric_card(label, float(classic[key]), float(graph[key]))
        for key, label in (("precision", "Precision"), ("recall", "Recall"), ("f1", "F1"))
    )
    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RAGChecker - Full evaluation</title><style>
*{{box-sizing:border-box}}body{{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f5f7fa;color:#172033;letter-spacing:0}}
main{{max-width:980px;margin:36px auto;padding:0 24px 48px}}header{{margin-bottom:24px}}h1{{font-size:30px;margin:0 0 7px}}
header p{{color:#596579;margin:0}}.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0}}
.summary div{{background:#fff;border:1px solid #dce2e8;border-radius:8px;padding:16px}}.summary span{{display:block;color:#667085;font-size:13px}}
.summary strong{{display:block;font-size:21px;margin-top:5px}}section{{background:#fff;border:1px solid #dce2e8;border-radius:8px;padding:20px;margin:14px 0}}
.metric-heading{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}}h2{{font-size:17px;margin:0}}
.metric-heading span{{font-size:13px;color:#596579}}.row{{display:grid;grid-template-columns:120px 1fr;gap:14px;align-items:center;margin:12px 0}}
.row>span{{font-weight:650}}.track{{height:34px;background:#edf1f5;border-radius:5px;position:relative;overflow:hidden}}.bar{{height:100%}}
.classic{{background:#174a73}}.graph{{background:#0b8f87}}.track strong{{position:absolute;right:10px;top:7px;font-size:14px;color:#111827}}
.legend{{display:flex;gap:20px;margin:18px 0;color:#596579;font-size:14px}}.dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
.note{{margin-top:22px;padding:16px;border-left:4px solid #d59b20;background:#fff9e8;color:#4b5563;line-height:1.5}}
@media(max-width:680px){{.summary{{grid-template-columns:1fr}}.row{{grid-template-columns:1fr}}.metric-heading{{align-items:flex-start;flex-direction:column}}}}
</style></head><body><main><header><h1>RAGChecker: Full Evaluation</h1><p>Automated comparison of Classic RAG and GraphRAG across 48 questions</p></header>
<div class="summary"><div><span>Questions evaluated</span><strong>48 per method</strong></div><div><span>Evaluation model</span><strong>{classic_meta.get('model', 'n/a')}</strong></div><div><span>Estimated total cost</span><strong>${total_cost:.4f} USD</strong></div></div>
<div class="legend"><span><i class="dot classic"></i>Classic RAG</span><span><i class="dot graph"></i>GraphRAG</span></div>{cards}
<div class="note"><strong>Interpretation:</strong> Classic RAG achieves higher precision and F1, while GraphRAG obtains higher recall and therefore covers more information from the reference answers. Neither method dominates every category: the result shows a trade-off between concise supported claims and broader information coverage.</div>
</main></body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
