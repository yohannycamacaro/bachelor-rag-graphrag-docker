from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
AUTO = RESULTS / "automatic_evaluation"
SOURCE_MD = RESULTS / "candidate_answers_20260915_125921.md"
CLASSIC_INPUT = AUTO / "ragchecker_classic_full.json"
OUTPUT = AUTO / "ragchecker_classic_repair_6.json"


def extract_classic_answers(text: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    blocks = re.split(r"(?=^## Q\d{3}:)", text, flags=re.MULTILINE)
    for block in blocks:
        match = re.match(r"^## (Q\d{3}):", block)
        if not match:
            continue
        question_id = match.group(1)
        answer_match = re.search(
            r"### Methode: classic\s*\n\s*(.*?)\s*\n\s*\*\*Evidenz:\*\*",
            block,
            flags=re.DOTALL,
        )
        if answer_match:
            answers[question_id] = answer_match.group(1).strip()
    return answers


def main() -> None:
    source_answers = extract_classic_answers(SOURCE_MD.read_text(encoding="utf-8"))
    payload = json.loads(CLASSIC_INPUT.read_text(encoding="utf-8"))
    damaged = []
    for result in payload["results"]:
        response = str(result.get("response", ""))
        if "NOMBRE" in response.upper() or "NAME?" in response.upper():
            question_id = str(result["query_id"])
            replacement = source_answers.get(question_id)
            if not replacement:
                raise ValueError(f"Missing source answer for {question_id}")
            result["response"] = replacement
            damaged.append(question_id)
    if len(damaged) != 6:
        raise ValueError(f"Expected 6 damaged answers, found {len(damaged)}: {damaged}")
    payload["results"] = [item for item in payload["results"] if item["query_id"] in damaged]
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Repaired: {', '.join(damaged)}")
    print(OUTPUT)


if __name__ == "__main__":
    main()
