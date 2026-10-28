from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rag_compare.cli import build_retriever
from rag_compare.evaluation import (
    build_result_record,
    evidence_summary,
    load_questions,
    load_reference_answers,
    validate_reference_answers,
)


QUESTIONS = PROJECT_ROOT / "data" / "questions" / "docker_support_holdout_questions.jsonl"
REFERENCES = PROJECT_ROOT / "data" / "evaluation" / "holdout_reference_answers.jsonl"
OUTPUT = PROJECT_ROOT / "results" / "holdout_set"


def write_candidates(records: list[dict[str, object]]) -> tuple[Path, Path]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT / "holdout_candidate_answers.csv"
    md_path = OUTPUT / "holdout_candidate_answers.md"
    fields = [
        "question_id", "category", "category_label", "method", "question",
        "reference_answer", "candidate_answer", "evidence_summary",
        "must_include", "scoring_focus", "keyword_coverage",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            row = {k: r.get(k, "") for k in fields}
            if isinstance(row["must_include"], list):
                row["must_include"] = "; ".join(row["must_include"])
            writer.writerow(row)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Frozen Holdout Set Candidate Answers\n\n")
        for r in records:
            f.write(f"## {r['question_id']} {r['method']}\n\n")
            f.write(f"**Category:** {r['category_label']}\n\n")
            f.write(f"**Question:** {r['question']}\n\n")
            f.write(f"**Reference:** {r['reference_answer']}\n\n")
            f.write(f"**Answer:** {r['candidate_answer']}\n\n")
            f.write(f"**Evidence:**\n\n{r['evidence_summary']}\n\n")
    return csv_path, md_path


def write_ragchecker(records: list[dict[str, object]]) -> dict[str, Path]:
    paths = {}
    for method in ("classic", "graph"):
        results = []
        for r in records:
            if r["method"] != method:
                continue
            evidence = r.get("evidence_summary", "")
            context_text = "".join(
                line.strip("- ") for line in str(evidence).splitlines() if line.strip()
            )
            results.append({
                "query_id": r["question_id"],
                "query": r["question"],
                "gt_answer": r["reference_answer"],
                "response": r["candidate_answer"],
                "retrieved_context": [
                    {"doc_id": f"{r['question_id']}-{method}-1", "text": context_text}
                ],
            })
        payload = {"results": results}
        path = OUTPUT / f"ragchecker_holdout_{method}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        paths[method] = path
    return paths


def write_manifest(records: list[dict[str, object]], rag_paths: dict[str, Path]) -> Path:
    by_category: dict[str, int] = defaultdict(int)
    for r in records:
        if r["method"] == "classic":
            by_category[str(r["category"])] += 1
    manifest = {
        "status": "frozen_before_ragchecker_evaluation",
        "methodological_rule": "No retriever tuning after inspecting holdout results.",
        "question_count": len(records) // 2,
        "candidate_answer_count": len(records),
        "questions_per_category": dict(sorted(by_category.items())),
        "ragchecker_inputs": {k: str(v) for k, v in rag_paths.items()},
    }
    path = OUTPUT / "holdout_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    questions = load_questions(QUESTIONS)
    references = load_reference_answers(REFERENCES)
    errors, warnings = validate_reference_answers(questions, references)
    if errors:
        raise SystemExit("\n".join(errors))
    for warning in warnings:
        print(f"Warning: {warning}")

    retrievers = {m: build_retriever(m) for m in ("classic", "graph")}
    records = []
    for question in questions:
        reference = references[str(question["id"])]
        for method, retriever in retrievers.items():
            result = retriever.answer(str(question["question"]), top_k=8)
            record = build_result_record(question, result)
            record.update({
                "candidate_answer": result["answer"],
                "evidence_summary": evidence_summary(result),
                "reference_answer": reference["reference_answer"],
                "must_include": reference["must_include"],
                "scoring_focus": reference["scoring_focus"],
            })
            records.append(record)

    candidate_paths = write_candidates(records)
    rag_paths = write_ragchecker(records)
    manifest = write_manifest(records, rag_paths)
    print(f"Holdout questions: {len(questions)}")
    print(f"Candidate answers: {len(records)}")
    print(f"Candidate CSV: {candidate_paths[0]}")
    print(f"Candidate Markdown: {candidate_paths[1]}")
    print(f"Manifest: {manifest}")
    for method, path in rag_paths.items():
        print(f"RAGChecker {method}: {path}")


if __name__ == "__main__":
    main()
