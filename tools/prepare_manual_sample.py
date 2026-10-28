from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTED_IDS = ["H001", "H003", "H005", "H007", "H008", "H009", "H010", "H011"]
QUESTIONS = ROOT / "data" / "questions" / "docker_support_challenge_questions.jsonl"
REFERENCES = ROOT / "data" / "evaluation" / "challenge_reference_answers.jsonl"
CANDIDATES = ROOT / "results" / "challenge_set" / "candidate_answers_20261002_120426.csv"
OUTPUT = ROOT / "experiments" / "manual_evaluation_sample_2026-10-07.json"


def load_jsonl(path: Path, key: str) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            rows[str(item[key])] = item
    return rows


def main() -> None:
    questions = load_jsonl(QUESTIONS, "id")
    references = load_jsonl(REFERENCES, "question_id")
    candidates: dict[tuple[str, str], dict[str, str]] = {}
    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            candidates[(row["question_id"], row["method"])] = row

    result: list[dict[str, object]] = []
    for question_id in SELECTED_IDS:
        question = questions[question_id]
        reference = references[question_id]
        for method in ("classic", "graph"):
            candidate = candidates[(question_id, method)]
            result.append(
                {
                    "question_id": question_id,
                    "category": question["category_label"],
                    "expected_hops": question["expected_relation_hops"],
                    "method": "Classic RAG" if method == "classic" else "GraphRAG",
                    "question": question["question"],
                    "reference_answer": reference["reference_answer"],
                    "must_include": ", ".join(reference["must_include"]),
                    "scoring_focus": reference["scoring_focus"],
                    "candidate_answer": candidate["candidate_answer"],
                    "evidence": candidate["evidence_summary"],
                }
            )

    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
