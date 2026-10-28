from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_compare.cli import build_retriever
from rag_compare.evaluation import (
    build_result_record,
    evidence_summary,
    keyword_coverage,
    load_questions,
    load_reference_answers,
)


QUESTIONS = PROJECT_ROOT / "data" / "questions" / "docker_support_challenge_questions.jsonl"
REFERENCES = PROJECT_ROOT / "data" / "evaluation" / "challenge_reference_answers.jsonl"
BEFORE = (
    PROJECT_ROOT
    / "results"
    / "challenge_set"
    / "candidate_answers_20261002_120426.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "results" / "challenge_set" / "graph_retrieval_ablation"


def load_before() -> dict[str, dict[str, str]]:
    with BEFORE.open("r", encoding="utf-8-sig", newline="") as file:
        return {
            row["question_id"]: row
            for row in csv.DictReader(file)
            if row["method"] == "graph"
        }


def main() -> None:
    questions = load_questions(QUESTIONS)
    references = load_reference_answers(REFERENCES)
    before = load_before()
    retriever = build_retriever("graph")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    records: list[dict[str, object]] = []
    ragchecker_results: list[dict[str, object]] = []

    for question in questions:
        result = retriever.answer(str(question["question"]), top_k=8)
        record = build_result_record(question, result)
        reference = references[str(question["id"])]
        record["candidate_answer"] = result["answer"]
        record["evidence_summary"] = evidence_summary(result)
        record["reference_answer"] = reference["reference_answer"]
        record["before_keyword_coverage"] = round(
            keyword_coverage(
                before[str(question["id"])]["candidate_answer"],
                question.get("expected_keywords", []),
            ),
            3,
        )
        record["keyword_delta"] = round(
            float(record["keyword_coverage"])
            - float(record["before_keyword_coverage"]),
            3,
        )
        records.append(record)
        ragchecker_results.append(
            {
                "query_id": question["id"],
                "query": question["question"],
                "gt_answer": reference["reference_answer"],
                "response": result["answer"],
                "retrieved_context": [
                    {
                        "doc_id": str(item.get("source", "graph-edge")),
                        "text": str(item.get("text", "")),
                    }
                    for item in result.get("evidence", [])
                ],
                "metadata": {
                    "method": "graph",
                    "category": question.get("category", "uncategorized"),
                    "category_label": question.get("category_label", "Uncategorized"),
                    "expected_relation_hops": question.get("expected_relation_hops", ""),
                    "experiment": "graph_retrieval_ablation",
                },
            }
        )

    csv_path = OUTPUT_DIR / f"graph_ablation_{timestamp}.csv"
    fieldnames = [
        "question_id",
        "category_label",
        "question",
        "before_keyword_coverage",
        "keyword_coverage",
        "keyword_delta",
        "candidate_answer",
        "evidence_summary",
        "reference_answer",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    json_path = OUTPUT_DIR / f"ragchecker_graph_ablation_{timestamp}.json"
    json_path.write_text(
        json.dumps({"results": ragchecker_results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_path = OUTPUT_DIR / f"graph_ablation_report_{timestamp}.md"
    average_before = sum(float(x["before_keyword_coverage"]) for x in records) / len(records)
    average_after = sum(float(x["keyword_coverage"]) for x in records) / len(records)
    with report_path.open("w", encoding="utf-8") as file:
        file.write("# Graph-Retrieval-Ablation\n\n")
        file.write(
            "This run evaluates a general retrieval correction while preserving the "
            "original Challenge-Set outputs. It is not a replacement for the frozen "
            "main result.\n\n"
        )
        file.write(f"- Questions: {len(records)}\n")
        file.write(f"- Mean keyword coverage before: {average_before:.3f}\n")
        file.write(f"- Mean keyword coverage after: {average_after:.3f}\n")
        file.write(f"- Delta: {average_after - average_before:+.3f}\n\n")
        file.write("| ID | Category | Before | After | Delta |\n")
        file.write("|---|---|---:|---:|---:|\n")
        for record in records:
            file.write(
                f"| {record['question_id']} | {record['category_label']} | "
                f"{float(record['before_keyword_coverage']):.3f} | "
                f"{float(record['keyword_coverage']):.3f} | "
                f"{float(record['keyword_delta']):+.3f} |\n"
            )

    print(csv_path)
    print(json_path)
    print(report_path)
    print(f"Mean keyword coverage: {average_before:.3f} -> {average_after:.3f}")


if __name__ == "__main__":
    main()
