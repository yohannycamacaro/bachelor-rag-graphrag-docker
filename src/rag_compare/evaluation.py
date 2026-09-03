from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .pathing import QUESTIONS_PATH, RESULTS_DIR


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


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
        "correctness_1_5",
        "completeness_1_5",
        "traceability_1_5",
        "consistency_1_5",
        "notes",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in questions:
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
                        "correctness_1_5": "",
                        "completeness_1_5": "",
                        "traceability_1_5": "",
                        "consistency_1_5": "",
                        "notes": "",
                    }
                )

    return path


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
