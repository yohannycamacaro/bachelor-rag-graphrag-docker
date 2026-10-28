from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_compare.cli import build_retriever
from rag_compare.evaluation import (
    build_result_record,
    evidence_summary,
    load_questions,
    load_reference_answers,
    validate_reference_answers,
    write_candidate_answer_files,
    write_category_comparison,
    write_ragchecker_inputs,
)


QUESTIONS = PROJECT_ROOT / "data" / "questions" / "docker_support_challenge_questions.jsonl"
REFERENCES = PROJECT_ROOT / "data" / "evaluation" / "challenge_reference_answers.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "results" / "challenge_set"


def write_presentation_examples(records: list[dict[str, object]]) -> Path:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[str(record["category"])].append(record)

    selected: list[tuple[str, list[dict[str, object]], float]] = []
    for category, items in sorted(grouped.items()):
        by_question: dict[str, list[dict[str, object]]] = defaultdict(list)
        for item in items:
            by_question[str(item["question_id"])].append(item)

        candidates: list[tuple[float, str, list[dict[str, object]]]] = []
        for question_id, pair in by_question.items():
            values = {str(item["method"]): float(item["keyword_coverage"]) for item in pair}
            delta = values.get("graph", 0.0) - values.get("classic", 0.0)
            candidates.append((abs(delta), question_id, pair))
        _, _, best_pair = max(candidates, key=lambda value: (value[0], value[1]))
        delta = next(float(x["keyword_coverage"]) for x in best_pair if x["method"] == "graph") - next(
            float(x["keyword_coverage"]) for x in best_pair if x["method"] == "classic"
        )
        selected.append((category, best_pair, delta))

    path = OUTPUT_DIR / "presentation_example_pairs.md"
    with path.open("w", encoding="utf-8") as file:
        file.write("# Konkrete Classic-RAG-/GraphRAG-Beispiele nach Kategorie\n\n")
        file.write(
            "Pro Kategorie wird vorlaeufig das Fragenpaar mit dem groessten absoluten "
            "Unterschied in der Keyword-Abdeckung gezeigt. Fuer die Abschlussprasentation "
            "sollen daraus nach der RAGChecker-Auswertung zwei besonders anschauliche "
            "Beispiele ausgewaehlt werden.\n\n"
        )
        for _, pair, delta in selected:
            first = pair[0]
            file.write(f"## {first['category_label']} - {first['question_id']}\n\n")
            file.write(f"**Frage:** {first['question']}\n\n")
            file.write(f"**Keyword-Delta Graph minus Classic:** {delta:+.3f}\n\n")
            for item in sorted(pair, key=lambda value: str(value["method"])):
                file.write(f"### {str(item['method']).title()} RAG\n\n")
                file.write(f"{item['candidate_answer']}\n\n")
                file.write(f"**Keyword-Abdeckung:** {item['keyword_coverage']}\n\n")
                file.write("**Evidenz:**\n\n")
                for line in str(item["evidence_summary"]).splitlines():
                    file.write(f"- {line}\n")
                file.write("\n")
    return path


def main() -> None:
    questions = load_questions(QUESTIONS)
    references = load_reference_answers(REFERENCES)
    errors, warnings = validate_reference_answers(questions, references)
    if errors:
        raise SystemExit("\n".join(errors))
    for warning in warnings:
        print(f"Warning: {warning}")

    retrievers = {method: build_retriever(method) for method in ("classic", "graph")}
    records: list[dict[str, object]] = []
    for question in questions:
        reference = references[str(question["id"])]
        for method, retriever in retrievers.items():
            result = retriever.answer(str(question["question"]), top_k=8)
            record = build_result_record(question, result)
            record["candidate_answer"] = result["answer"]
            record["evidence_summary"] = evidence_summary(result)
            record["reference_answer"] = reference["reference_answer"]
            record["must_include"] = reference["must_include"]
            record["scoring_focus"] = reference["scoring_focus"]
            records.append(record)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path, markdown_path = write_candidate_answer_files(records, OUTPUT_DIR)
    category_csv, category_markdown = write_category_comparison(records, OUTPUT_DIR)
    ragchecker_paths = write_ragchecker_inputs(records, OUTPUT_DIR)
    examples_path = write_presentation_examples(records)

    manifest = {
        "question_count": len(questions),
        "answers": len(records),
        "questions_per_category": {
            category: sum(1 for q in questions if q["category"] == category)
            for category in sorted({str(q["category"]) for q in questions})
        },
        "candidate_csv": str(csv_path),
        "candidate_markdown": str(markdown_path),
        "category_csv": str(category_csv),
        "category_markdown": str(category_markdown),
        "ragchecker": {key: str(value) for key, value in ragchecker_paths.items()},
        "presentation_examples": str(examples_path),
    }
    manifest_path = OUTPUT_DIR / "challenge_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Challenge questions: {len(questions)}")
    print(f"Candidate answers: {len(records)}")
    print(f"Manifest: {manifest_path}")
    print(f"Presentation examples: {examples_path}")
    for method, path in ragchecker_paths.items():
        print(f"RAGChecker {method}: {path}")


if __name__ == "__main__":
    main()
