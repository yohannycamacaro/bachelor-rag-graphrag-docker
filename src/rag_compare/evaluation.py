from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .pathing import QUESTIONS_PATH, REFERENCE_ANSWERS_PATH, RESULTS_DIR


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def load_reference_answers(
    path: Path = REFERENCE_ANSWERS_PATH,
) -> dict[str, dict[str, object]]:
    reference_answers: dict[str, dict[str, object]] = {}
    if not path.exists():
        return reference_answers

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            reference_answers[str(record["question_id"])] = record

    return reference_answers


def validate_reference_answers(
    questions: list[dict[str, object]],
    reference_answers: dict[str, dict[str, object]],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    question_ids = {str(question["id"]) for question in questions}
    reference_ids = set(reference_answers)

    missing = sorted(question_ids - reference_ids)
    unexpected = sorted(reference_ids - question_ids)
    if missing:
        errors.append("Missing reference answers: " + ", ".join(missing))
    if unexpected:
        errors.append("Reference answers without matching questions: " + ", ".join(unexpected))

    for question_id, reference in sorted(reference_answers.items()):
        if not str(reference.get("reference_answer", "")).strip():
            errors.append(f"{question_id} has an empty reference_answer")
        if not reference.get("must_include"):
            warnings.append(f"{question_id} has no must_include entries")
        if not reference.get("scoring_focus"):
            warnings.append(f"{question_id} has no scoring_focus")

    return errors, warnings


def keyword_coverage(answer: str, expected_keywords: Iterable[str]) -> float:
    matched, _ = keyword_match_details(answer, expected_keywords)
    expected = list(expected_keywords)
    if not expected:
        return 0.0
    return len(matched) / len(expected)


def keyword_match_details(
    answer: str,
    expected_keywords: Iterable[str],
) -> tuple[list[str], list[str]]:
    normalized = answer.lower()
    expected = list(expected_keywords)
    matched = [keyword for keyword in expected if keyword.lower() in normalized]
    missing = [keyword for keyword in expected if keyword.lower() not in normalized]
    return matched, missing


def evidence_source_ids(result: dict[str, object]) -> set[str]:
    source_ids: set[str] = set()
    for item in result.get("evidence", []):
        if not isinstance(item, dict):
            continue
        for source_id in item.get("source_ids", []):
            source_ids.add(str(source_id))
    return source_ids


def source_recall_details(
    result: dict[str, object],
    relevant_sources: Iterable[str],
) -> tuple[float, list[str], list[str]]:
    expected = [str(source) for source in relevant_sources]
    if not expected:
        return 0.0, [], []

    retrieved = evidence_source_ids(result)
    matched = [source for source in expected if source in retrieved]
    missing = [source for source in expected if source not in retrieved]
    return len(matched) / len(expected), matched, missing


def graph_relation_details(result: dict[str, object]) -> tuple[int, int, list[str]]:
    relation_types: set[str] = set()
    relation_count = 0

    for item in result.get("evidence", []):
        if not isinstance(item, dict):
            continue
        relation = item.get("relation")
        if relation:
            relation_count += 1
            relation_types.add(str(relation))

    return relation_count, len(relation_types), sorted(relation_types)


def build_result_record(
    question: dict[str, object],
    result: dict[str, object],
) -> dict[str, object]:
    matched_keywords, missing_keywords = keyword_match_details(
        str(result["answer"]),
        question.get("expected_keywords", []),  # type: ignore[arg-type]
    )
    source_recall, matched_sources, missing_sources = source_recall_details(
        result,
        question.get("relevant_sources", []),  # type: ignore[arg-type]
    )
    relation_count, relation_type_count, relation_types = graph_relation_details(
        result
    )
    evidence = result.get("evidence", [])

    return {
        "question_id": question["id"],
        "difficulty": question["difficulty"],
        "category": question.get("category", "uncategorized"),
        "category_label": question.get("category_label", "Uncategorized"),
        "expected_relation_hops": question.get("expected_relation_hops", ""),
        "method": result["method"],
        "keyword_coverage": round(
            len(matched_keywords)
            / max(len(question.get("expected_keywords", [])), 1),  # type: ignore[arg-type]
            3,
        ),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "source_recall": round(source_recall, 3),
        "matched_sources": matched_sources,
        "missing_sources": missing_sources,
        "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "graph_relation_count": relation_count,
        "graph_relation_type_count": relation_type_count,
        "graph_relation_types": relation_types,
        "question": question["question"],
        "question_de": question.get("question_de", ""),
        "expected_keywords": question.get("expected_keywords", []),
        "relevant_sources": question.get("relevant_sources", []),
        "answer": result["answer"],
        "evidence": evidence,
    }


def write_jsonl_results(
    records: list[dict[str, object]],
    method: str,
    results_dir: Path = RESULTS_DIR,
) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = results_dir / f"{method}_results_{timestamp}.jsonl"

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return path


def write_csv_summary(
    records: list[dict[str, object]],
    method: str,
    results_dir: Path = RESULTS_DIR,
) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = results_dir / f"{method}_summary_{timestamp}.csv"

    fieldnames = [
        "question_id",
        "difficulty",
        "category",
        "category_label",
        "expected_relation_hops",
        "method",
        "keyword_coverage",
        "source_recall",
        "evidence_count",
        "graph_relation_count",
        "graph_relation_type_count",
        "matched_keywords",
        "missing_keywords",
        "matched_sources",
        "missing_sources",
        "question",
        "answer",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    key: _csv_value(record.get(key, ""))
                    for key in fieldnames
                }
            )

    return path


def write_category_comparison(
    records: list[dict[str, object]],
    results_dir: Path = RESULTS_DIR,
) -> tuple[Path, Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rows = summarize_by_category(records)

    csv_path = results_dir / f"category_comparison_{timestamp}.csv"
    markdown_path = results_dir / f"category_comparison_{timestamp}.md"

    fieldnames = [
        "category",
        "category_label",
        "question_count",
        "avg_expected_relation_hops",
        "classic_keyword_coverage",
        "graph_keyword_coverage",
        "keyword_delta_graph_minus_classic",
        "classic_source_recall",
        "graph_source_recall",
        "source_delta_graph_minus_classic",
        "classic_evidence_count",
        "graph_evidence_count",
        "graph_relation_count",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    with markdown_path.open("w", encoding="utf-8") as file:
        file.write("# Kategorievergleich: Klassisches RAG vs GraphRAG\n\n")
        file.write(
            "Dieser Bericht gruppiert die Auswertung nach Fragetypen. "
            "Es handelt sich um eine automatische retrieval-basierte "
            "Voranalyse, noch nicht um die finale LLM-basierte Evaluation.\n\n"
        )
        file.write(
            "| Kategorie | n | Ø Hops | Classic Keyword | Graph Keyword | Delta | "
            "Classic Source | Graph Source | Ø Graph-Relationen |\n"
        )
        file.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            file.write(
                "| {category_label} | {question_count} | "
                "{avg_expected_relation_hops:.2f} | "
                "{classic_keyword_coverage:.3f} | "
                "{graph_keyword_coverage:.3f} | "
                "{keyword_delta_graph_minus_classic:.3f} | "
                "{classic_source_recall:.3f} | "
                "{graph_source_recall:.3f} | "
                "{graph_relation_count:.3f} |\n".format(**row)
            )

        file.write("\n## Interpretationsentwurf\n\n")
        file.write(
            "Ein positiver Delta-Wert bedeutet, dass das graphbasierte "
            "Retrieval in dieser Kategorie mehr erwartete Schluesselbegriffe "
            "abgedeckt hat als die klassische Text-Chunk-Baseline. Die Spalte "
            "Ø Graph-Relationen zeigt, wie viele explizite Beziehungen der "
            "GraphRAG-Prototyp im Durchschnitt pro Frage verwendet hat. Fuer "
            "die finale Bachelorarbeit muessen diese automatischen Werte durch "
            "manuelle Bewertungen fuer Korrektheit, Vollstaendigkeit, "
            "Nachvollziehbarkeit und Konsistenz ergaenzt werden.\n"
        )

    return csv_path, markdown_path


def write_manual_scoring_template(
    questions: list[dict[str, object]],
    results_dir: Path = RESULTS_DIR,
) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = results_dir / f"manual_scoring_template_{timestamp}.csv"

    fieldnames = [
        "question_id",
        "category",
        "category_label",
        "expected_relation_hops",
        "method",
        "question",
        "reference_answer",
        "must_include",
        "scoring_focus",
        "correctness_1_5",
        "completeness_1_5",
        "traceability_1_5",
        "consistency_1_5",
        "source_support_1_5",
        "overall_1_5",
        "notes",
    ]
    reference_answers = load_reference_answers()

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in questions:
            reference = reference_answers.get(str(question["id"]), {})
            for method in ("classic", "graph"):
                writer.writerow(
                    {
                        "question_id": question["id"],
                        "category": question.get("category", "uncategorized"),
                        "category_label": question.get(
                            "category_label",
                            "Uncategorized",
                        ),
                        "expected_relation_hops": question.get(
                            "expected_relation_hops",
                            "",
                        ),
                        "method": method,
                        "question": question.get("question", ""),
                        "reference_answer": reference.get("reference_answer", ""),
                        "must_include": _csv_value(reference.get("must_include", [])),
                        "scoring_focus": reference.get("scoring_focus", ""),
                        "correctness_1_5": "",
                        "completeness_1_5": "",
                        "traceability_1_5": "",
                        "consistency_1_5": "",
                        "source_support_1_5": "",
                        "overall_1_5": "",
                        "notes": "",
                    }
                )

    return path


def write_reference_answer_report(
    questions: list[dict[str, object]],
    results_dir: Path = RESULTS_DIR,
) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = results_dir / f"reference_answer_report_{timestamp}.md"
    reference_answers = load_reference_answers()

    with path.open("w", encoding="utf-8") as file:
        file.write("# Referenzantworten fuer die Evaluation\n\n")
        file.write(
            "Dieses Dokument sammelt die Referenzantworten, Mindestinhalte und "
            "Bewertungsschwerpunkte fuer den aktuellen Fragenkatalog.\n\n"
        )

        for question in questions:
            question_id = str(question["id"])
            reference = reference_answers.get(question_id, {})
            file.write(f"## {question_id}: {question.get('category_label', '')}\n\n")
            file.write(f"**Frage:** {question.get('question', '')}\n\n")
            file.write(
                f"**Referenzantwort:** {reference.get('reference_answer', '')}\n\n"
            )
            file.write(
                "**Mindestinhalte:** "
                + _csv_value(reference.get("must_include", []))
                + "\n\n"
            )
            file.write(
                f"**Bewertungsschwerpunkt:** {reference.get('scoring_focus', '')}\n\n"
            )

    return path


def write_candidate_answer_files(
    records: list[dict[str, object]],
    results_dir: Path = RESULTS_DIR,
) -> tuple[Path, Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / f"candidate_answers_{timestamp}.csv"
    markdown_path = results_dir / f"candidate_answers_{timestamp}.md"

    fieldnames = [
        "question_id",
        "category",
        "category_label",
        "expected_relation_hops",
        "method",
        "question",
        "candidate_answer",
        "evidence_summary",
        "reference_answer",
        "must_include",
        "scoring_focus",
        "correctness_1_5",
        "completeness_1_5",
        "traceability_1_5",
        "consistency_1_5",
        "source_support_1_5",
        "overall_1_5",
        "notes",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    key: _csv_value(record.get(key, ""))
                    for key in fieldnames
                }
            )

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("question_id", ""))].append(record)

    with markdown_path.open("w", encoding="utf-8") as file:
        file.write("# Kandidatenantworten fuer die manuelle Evaluation\n\n")
        file.write(
            "Dieses Dokument enthaelt die automatisch erzeugten "
            "Kandidatenantworten des aktuellen Prototyps. Die Antworten sind "
            "evidenzbasiert und deterministisch aus dem jeweiligen Retrieval "
            "abgeleitet. Sie ersetzen noch keine finale LLM-basierte "
            "Antwortgenerierung, eignen sich aber fuer eine erste manuelle "
            "Bewertung der Methoden nach Kategorie.\n\n"
        )

        for question_id in sorted(grouped):
            question_records = grouped[question_id]
            first = question_records[0]
            file.write(
                f"## {question_id}: {first.get('category_label', '')}\n\n"
            )
            file.write(f"**Frage:** {first.get('question', '')}\n\n")
            file.write(
                f"**Referenzantwort:** {first.get('reference_answer', '')}\n\n"
            )
            file.write(
                f"**Bewertungsschwerpunkt:** {first.get('scoring_focus', '')}\n\n"
            )

            for record in sorted(
                question_records,
                key=lambda item: str(item.get("method", "")),
            ):
                file.write(f"### Methode: {record.get('method', '')}\n\n")
                file.write(
                    f"{record.get('candidate_answer', '')}\n\n"
                )
                file.write("**Evidenz:**\n\n")
                evidence = str(record.get("evidence_summary", "")).strip()
                if evidence:
                    for line in evidence.splitlines():
                        file.write(f"- {line}\n")
                else:
                    file.write("- Keine Evidenz gefunden.\n")
                file.write("\n")

    return csv_path, markdown_path


def write_ragchecker_inputs(
    records: list[dict[str, object]],
    results_dir: Path = RESULTS_DIR,
) -> dict[str, Path]:
    """Write one RAGChecker-compatible input file per retrieval method."""
    output_dir = results_dir / "automatic_evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths: dict[str, Path] = {}

    for method in ("classic", "graph"):
        method_records = [
            record for record in records if record.get("method") == method
        ]
        if not method_records:
            continue

        results: list[dict[str, object]] = []
        for record in method_records:
            contexts: list[dict[str, str]] = []
            evidence = record.get("evidence", [])
            if isinstance(evidence, list):
                for index, item in enumerate(evidence, start=1):
                    if not isinstance(item, dict):
                        continue
                    text = str(item.get("text", "")).strip()
                    if not text:
                        continue
                    contexts.append(
                        {
                            "doc_id": str(
                                item.get("id")
                                or item.get("source")
                                or f"{method}-{record['question_id']}-{index}"
                            ),
                            "text": text,
                        }
                    )

            results.append(
                {
                    "query_id": str(record["question_id"]),
                    "query": str(record["question"]),
                    "gt_answer": str(record.get("reference_answer", "")),
                    "response": str(record.get("candidate_answer", "")),
                    "retrieved_context": contexts,
                    "metadata": {
                        "method": method,
                        "category": str(record.get("category", "")),
                        "category_label": str(record.get("category_label", "")),
                        "expected_relation_hops": record.get(
                            "expected_relation_hops", ""
                        ),
                    },
                }
            )

        path = output_dir / f"ragchecker_{method}_{timestamp}.json"
        payload = {"results": results}
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        paths[method] = path

    return paths


def evidence_summary(result: dict[str, object]) -> str:
    evidence = result.get("evidence", [])
    if not isinstance(evidence, list):
        return ""

    lines: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        if "relation" in item:
            lines.append(
                "{source_label} --{relation}--> {target_label} "
                "(sources: {sources})".format(
                    source_label=item.get("source_label", ""),
                    relation=item.get("relation", ""),
                    target_label=item.get("target_label", ""),
                    sources=", ".join(str(source) for source in item.get("source_ids", [])),
                )
            )
        else:
            lines.append(
                "{title} (sources: {sources})".format(
                    title=item.get("title", ""),
                    sources=", ".join(str(source) for source in item.get("source_ids", [])),
                )
            )

    return "\n".join(lines)


def summarize_by_category(records: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("category", "uncategorized"))].append(record)

    rows: list[dict[str, object]] = []
    for category, category_records in sorted(grouped.items()):
        labels = {
            str(record.get("category_label", "Uncategorized"))
            for record in category_records
        }
        question_ids = {
            str(record.get("question_id", ""))
            for record in category_records
        }
        classic = [
            record for record in category_records if record.get("method") == "classic"
        ]
        graph = [
            record for record in category_records if record.get("method") == "graph"
        ]
        avg_hops = _mean(
            float(record.get("expected_relation_hops") or 0)
            for record in category_records
        )
        classic_keyword = _mean(
            float(record.get("keyword_coverage") or 0) for record in classic
        )
        graph_keyword = _mean(
            float(record.get("keyword_coverage") or 0) for record in graph
        )
        classic_source = _mean(
            float(record.get("source_recall") or 0) for record in classic
        )
        graph_source = _mean(
            float(record.get("source_recall") or 0) for record in graph
        )

        rows.append(
            {
                "category": category,
                "category_label": sorted(labels)[0],
                "question_count": len(question_ids),
                "avg_expected_relation_hops": round(avg_hops, 3),
                "classic_keyword_coverage": round(classic_keyword, 3),
                "graph_keyword_coverage": round(graph_keyword, 3),
                "keyword_delta_graph_minus_classic": round(
                    graph_keyword - classic_keyword, 3
                ),
                "classic_source_recall": round(classic_source, 3),
                "graph_source_recall": round(graph_source, 3),
                "source_delta_graph_minus_classic": round(
                    graph_source - classic_source, 3
                ),
                "classic_evidence_count": round(
                    _mean(float(record.get("evidence_count") or 0) for record in classic),
                    3,
                ),
                "graph_evidence_count": round(
                    _mean(float(record.get("evidence_count") or 0) for record in graph),
                    3,
                ),
                "graph_relation_count": round(
                    _mean(
                        float(record.get("graph_relation_count") or 0)
                        for record in graph
                    ),
                    3,
                ),
            }
        )

    return rows


def _mean(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def _csv_value(value: object) -> object:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value
