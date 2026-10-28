from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results" / "challenge_set"
BEFORE = RESULTS / "automatic_evaluation" / "challenge_results_graph_12.json"
AFTER = (
    RESULTS
    / "graph_retrieval_ablation"
    / "ragchecker_graph_ablation_result_20261002.json"
)
OUTPUT = RESULTS / "graph_retrieval_ablation" / "ragchecker_ablation_comparison.md"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric(result: dict[str, object], name: str) -> float:
    metrics = result.get("metrics", {})
    return float(metrics.get(name, 0.0))  # type: ignore[union-attr]


def main() -> None:
    before = load(BEFORE)
    after = load(AFTER)
    before_rows = {str(row["query_id"]): row for row in before["results"]}
    after_rows = {str(row["query_id"]): row for row in after["results"]}

    before_overall = before["metrics"]["overall_metrics"]
    after_overall = after["metrics"]["overall_metrics"]

    with OUTPUT.open("w", encoding="utf-8") as file:
        file.write("# RAGChecker comparison of the Graph-Retrieval ablation\n\n")
        file.write(
            "The original Challenge-Set remains the frozen main result. This ablation "
            "tests whether concept-aware matching and scenario gates repair the H010 "
            "retrieval failure without assuming a general improvement.\n\n"
        )
        file.write("## Overall metrics\n\n")
        file.write("| Run | Precision | Recall | F1 |\n")
        file.write("|---|---:|---:|---:|\n")
        file.write(
            f"| Original GraphRAG | {float(before_overall['precision']):.1f} | "
            f"{float(before_overall['recall']):.1f} | {float(before_overall['f1']):.1f} |\n"
        )
        file.write(
            f"| Retrieval ablation | {float(after_overall['precision']):.1f} | "
            f"{float(after_overall['recall']):.1f} | {float(after_overall['f1']):.1f} |\n\n"
        )
        file.write("## Per-question F1\n\n")
        file.write("| ID | Before | After | Delta |\n")
        file.write("|---|---:|---:|---:|\n")
        for question_id in sorted(before_rows):
            old = metric(before_rows[question_id], "f1") * 100
            new = metric(after_rows[question_id], "f1") * 100
            file.write(f"| {question_id} | {old:.1f} | {new:.1f} | {new-old:+.1f} |\n")

        h010_before = metric(before_rows["H010"], "f1") * 100
        h010_after = metric(after_rows["H010"], "f1") * 100
        file.write("\n## Interpretation\n\n")
        file.write(
            f"H010 improves from {h010_before:.1f} to {h010_after:.1f} F1 because the "
            "retriever no longer confuses a published host port with the unrelated "
            "scaled-service scenario. It now retrieves readiness, port-scope and "
            "network-membership relations.\n\n"
        )
        file.write(
            "The global F1 does not improve. Recall rises slightly, while precision "
            "falls because broader retrieval adds claims that are not required by "
            "every reference answer. The change therefore repairs one failure mode "
            "but is not a general quality improvement. A future routing or pruning "
            "step should select a compact set of complementary relations.\n\n"
        )
        file.write(
            "Because the same Challenge-Set informed the correction, this experiment "
            "is an exploratory ablation rather than an unbiased final evaluation. Any "
            "further tuning should be evaluated on a separate holdout set.\n"
        )

    print(OUTPUT)


if __name__ == "__main__":
    main()
