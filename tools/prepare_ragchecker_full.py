from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT_DIR = RESULTS / "automatic_evaluation"


def newest_master_csv() -> Path:
    candidates = sorted(
        RESULTS.glob("candidate_answers_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise SystemExit("No candidate_answers_*.csv file was found.")
    return candidates[0]


def read_csv(path: Path) -> list[dict[str, str]]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    return list(csv.DictReader(text.splitlines()))


def contexts_from_summary(row: dict[str, str]) -> list[dict[str, str]]:
    lines = [
        line.strip().removeprefix("- ").strip()
        for line in row.get("evidence_summary", "").splitlines()
        if line.strip()
    ]
    return [
        {"doc_id": f"{row['question_id']}-{row['method']}-{index}", "text": line}
        for index, line in enumerate(lines, start=1)
    ]


def main() -> None:
    source = newest_master_csv()
    rows = read_csv(source)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source: {source}")
    print(f"Rows: {len(rows)}")

    for method in ("classic", "graph"):
        method_rows = [row for row in rows if row.get("method") == method]
        question_ids = {row.get("question_id", "") for row in method_rows}
        if len(method_rows) != 48 or len(question_ids) != 48:
            raise SystemExit(
                f"Expected 48 unique {method} rows, got "
                f"{len(method_rows)} rows and {len(question_ids)} IDs."
            )

        converted = []
        for row in method_rows:
            required = ("question_id", "question", "reference_answer", "candidate_answer")
            missing = [field for field in required if not row.get(field, "").strip()]
            if missing:
                raise SystemExit(
                    f"{row.get('question_id')} {method} is missing: {', '.join(missing)}"
                )
            contexts = contexts_from_summary(row)
            if not contexts:
                raise SystemExit(f"{row['question_id']} {method} has no retrieved context.")
            converted.append(
                {
                    "query_id": row["question_id"],
                    "query": row["question"],
                    "gt_answer": row["reference_answer"],
                    "response": row["candidate_answer"],
                    "retrieved_context": contexts,
                }
            )

        output = OUTPUT_DIR / f"ragchecker_{method}_full.json"
        output.write_text(
            json.dumps({"results": converted}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"{method}: {len(converted)} cases -> {output}")


if __name__ == "__main__":
    main()
