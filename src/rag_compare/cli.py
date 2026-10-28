from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from pprint import pprint

from .corpus import load_markdown_sections, load_sources
from .evaluation import (
    build_result_record,
    evidence_summary,
    load_reference_answers,
    load_questions,
    summarize_by_category,
    validate_reference_answers,
    write_category_comparison,
    write_candidate_answer_files,
    write_ragchecker_inputs,
    write_csv_summary,
    write_jsonl_results,
    write_manual_scoring_template,
    write_reference_answer_report,
)
from .graph_retrieval import GraphRagRetriever
from .pathing import GRAPH_PATH
from .retrieval import ClassicRagRetriever


def build_retriever(method: str):
    if method == "classic":
        return ClassicRagRetriever(load_markdown_sections())
    if method == "graph":
        return GraphRagRetriever()
    raise ValueError(f"Unknown method: {method}")


def command_sources(_: argparse.Namespace) -> None:
    for source in load_sources():
        print(f"- {source.id}: {source.title}")
        print(f"  {source.url}")
        print(f"  Usage: {source.planned_usage}")


def command_questions(_: argparse.Namespace) -> None:
    for question in load_questions():
        print(
            f"{question['id']} "
            f"[{question['difficulty']} / {question.get('category', 'uncategorized')}] "
            f"{question['question']}"
        )
        print(f"  DE: {question['question_de']}")


def command_status(_: argparse.Namespace) -> None:
    sources = load_sources()
    sections = load_markdown_sections()
    questions = load_questions()

    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    categories: dict[str, int] = {}
    hop_sum = 0.0
    for question in questions:
        category = str(question.get("category", "uncategorized"))
        categories[category] = categories.get(category, 0) + 1
        hop_sum += float(question.get("expected_relation_hops") or 0)

    print("Bachelorarbeit project status")
    print(f"- Sources: {len(sources)}")
    print(f"- Docker support cases: {len(sections)}")
    print(f"- Test questions: {len(questions)}")
    if questions:
        print(f"- Average expected relation hops: {hop_sum / len(questions):.2f}")
    print("- Question categories:")
    for category, count in sorted(categories.items()):
        print(f"  - {category}: {count}")
    print(f"- Graph nodes: {len(graph['nodes'])}")
    print(f"- Graph relations: {len(graph['edges'])}")
    print("- Graph relation types:")
    for relation_type, count in sorted(
        Counter(edge["relation"] for edge in graph["edges"]).items()
    ):
        print(f"  - {relation_type}: {count}")


def command_graph_overview(_: argparse.Namespace) -> None:
    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    print("Nodes")
    for node in graph["nodes"]:
        print(f"- {node['id']} [{node['type']}] {node['label']}")

    print("\nRelations")
    for edge in graph["edges"]:
        print(f"- {edge['source']} --{edge['relation']}--> {edge['target']}")


def command_graph_stats(_: argparse.Namespace) -> None:
    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    node_types = Counter(node["type"] for node in graph["nodes"])
    relation_types = Counter(edge["relation"] for edge in graph["edges"])
    source_ids = {
        source_id
        for edge in graph["edges"]
        for source_id in edge.get("source_ids", [])
    }

    print("Graph statistics")
    print(f"- Nodes total: {len(graph['nodes'])}")
    for node_type, count in sorted(node_types.items()):
        print(f"  - {node_type}: {count}")
    print(f"- Relations total: {len(graph['edges'])}")
    for relation_type, count in sorted(relation_types.items()):
        print(f"  - {relation_type}: {count}")
    print(f"- Source links on relations: {len(source_ids)} unique sources")
    problem_count = node_types.get("problem", 0)
    if problem_count:
        print(f"- Average relations per problem node: {len(graph['edges']) / problem_count:.2f}")
    print("")
    print("Interpretation")
    print(
        "The graph models technical support knowledge as explicit links between "
        "problems, components, causes, diagnosis steps, solutions and source "
        "documents. Relation types such as requires, conflicts_with and "
        "documented_in make dependencies and traceability visible."
    )


def command_query(args: argparse.Namespace) -> None:
    retriever = build_retriever(args.method)
    result = retriever.answer(args.question, top_k=args.top_k)
    if args.raw:
        pprint(result, sort_dicts=False)
    else:
        print_query_result(result)


def print_query_result(result: dict[str, object]) -> None:
    print(f"Method: {result['method']}")
    print(f"Question: {result['question']}")
    print("")
    print("Answer:")
    print(result["answer"])
    print("")
    print("Evidence:")

    evidence = result.get("evidence", [])
    if not isinstance(evidence, list) or not evidence:
        print("- No evidence")
        return

    for index, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            continue
        if "relation" in item:
            print(
                f"{index}. {item['source_label']} --{item['relation']}--> "
                f"{item['target_label']} "
                f"(score={item['score']}, sources={', '.join(item['source_ids'])})"
            )
        else:
            print(
                f"{index}. {item['title']} "
                f"(score={item['score']}, sources={', '.join(item['source_ids'])})"
            )


def command_run_testset(args: argparse.Namespace) -> None:
    retriever = build_retriever(args.method)
    questions = load_questions()
    if args.limit:
        questions = questions[: args.limit]

    records: list[dict[str, object]] = []
    for question in questions:
        result = retriever.answer(str(question["question"]), top_k=args.top_k)
        records.append(build_result_record(question, result))

    jsonl_path = write_jsonl_results(records, args.method)
    csv_path = write_csv_summary(records, args.method)

    print(f"Saved JSONL results: {jsonl_path}")
    print(f"Saved CSV summary: {csv_path}")

    avg_coverage = sum(float(row["keyword_coverage"]) for row in records) / len(records)
    print(f"Average keyword coverage: {avg_coverage:.3f}")


def command_categories(_: argparse.Namespace) -> None:
    questions = load_questions()
    categories: dict[str, list[dict[str, object]]] = {}
    for question in questions:
        category = str(question.get("category", "uncategorized"))
        categories.setdefault(category, []).append(question)

    for category, items in sorted(categories.items()):
        label = items[0].get("category_label", "Uncategorized")
        avg_hops = sum(
            float(item.get("expected_relation_hops") or 0) for item in items
        ) / len(items)
        print(f"{category}: {label} ({len(items)} questions, avg hops {avg_hops:.2f})")
        for item in items:
            print(f"  - {item['id']}: {item['question']}")


def command_compare(args: argparse.Namespace) -> None:
    questions = load_questions()
    if args.limit:
        questions = questions[: args.limit]

    retrievers = {
        "classic": build_retriever("classic"),
        "graph": build_retriever("graph"),
    }
    records: list[dict[str, object]] = []

    for question in questions:
        for method, retriever in retrievers.items():
            result = retriever.answer(str(question["question"]), top_k=args.top_k)
            records.append(build_result_record(question, result))

    jsonl_path = write_jsonl_results(records, "comparison")
    csv_path = write_csv_summary(records, "comparison")
    category_csv_path, category_md_path = write_category_comparison(records)

    print(f"Saved JSONL comparison: {jsonl_path}")
    print(f"Saved CSV comparison: {csv_path}")
    print(f"Saved category CSV: {category_csv_path}")
    print(f"Saved category report: {category_md_path}")
    print("")
    print("Category summary")
    for row in summarize_by_category(records):
        print(
            "- {category_label}: classic={classic_keyword_coverage:.3f}, "
            "graph={graph_keyword_coverage:.3f}, "
            "delta={keyword_delta_graph_minus_classic:.3f}".format(**row)
        )


def command_manual_template(_: argparse.Namespace) -> None:
    path = write_manual_scoring_template(load_questions())
    print(f"Saved manual scoring template: {path}")


def command_reference_answers(_: argparse.Namespace) -> None:
    questions = load_questions()
    reference_answers = load_reference_answers()
    errors, warnings = validate_reference_answers(questions, reference_answers)

    print("Reference answers")
    print(f"- Questions: {len(questions)}")
    print(f"- Reference answers: {len(reference_answers)}")

    if warnings:
        print("")
        print("Warnings")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("")
        print("Errors")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    report_path = write_reference_answer_report(questions)
    template_path = write_manual_scoring_template(questions)
    print("")
    print("Validation passed: every question has a reference answer.")
    print(f"Saved reference answer report: {report_path}")
    print(f"Saved manual scoring template: {template_path}")


def command_candidate_answers(args: argparse.Namespace) -> None:
    questions = load_questions()
    reference_answers = load_reference_answers()

    if args.category:
        questions = [
            question
            for question in questions
            if str(question.get("category", "")) == args.category
        ]

    if args.limit:
        questions = questions[: args.limit]

    if not questions:
        raise SystemExit("No questions matched the requested filter.")

    if args.method == "both":
        methods = ["classic", "graph"]
    else:
        methods = [args.method]

    retrievers = {
        method: build_retriever(method)
        for method in methods
    }

    records: list[dict[str, object]] = []
    for question in questions:
        question_id = str(question["id"])
        reference = reference_answers.get(question_id, {})
        for method in methods:
            result = retrievers[method].answer(str(question["question"]), top_k=args.top_k)
            record = build_result_record(question, result)
            record["candidate_answer"] = result["answer"]
            record["evidence_summary"] = evidence_summary(result)
            record["reference_answer"] = reference.get("reference_answer", "")
            record["must_include"] = reference.get("must_include", [])
            record["scoring_focus"] = reference.get("scoring_focus", "")
            record["correctness_1_5"] = ""
            record["completeness_1_5"] = ""
            record["traceability_1_5"] = ""
            record["consistency_1_5"] = ""
            record["source_support_1_5"] = ""
            record["overall_1_5"] = ""
            record["notes"] = ""
            records.append(record)

    csv_path, markdown_path = write_candidate_answer_files(records)

    print("Candidate answers for manual evaluation")
    print(f"- Questions: {len(questions)}")
    print(f"- Methods: {', '.join(methods)}")
    print(f"- Records: {len(records)}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved Markdown: {markdown_path}")


def command_prepare_auto_evaluation(args: argparse.Namespace) -> None:
    questions = load_questions()
    reference_answers = load_reference_answers()
    if args.limit:
        questions = questions[: args.limit]

    retrievers = {
        method: build_retriever(method)
        for method in ("classic", "graph")
    }
    records: list[dict[str, object]] = []
    for question in questions:
        question_id = str(question["id"])
        reference = reference_answers.get(question_id, {})
        if not reference.get("reference_answer"):
            raise SystemExit(f"Missing reference answer for {question_id}")

        for method, retriever in retrievers.items():
            result = retriever.answer(str(question["question"]), top_k=args.top_k)
            record = build_result_record(question, result)
            record["candidate_answer"] = result["answer"]
            record["reference_answer"] = reference["reference_answer"]
            records.append(record)

    paths = write_ragchecker_inputs(records)
    print("RAGChecker input preparation")
    print(f"- Questions: {len(questions)}")
    print(f"- Candidate answers: {len(records)}")
    for method, path in paths.items():
        print(f"- {method}: {path}")


def command_manual_summary(args: argparse.Namespace) -> None:
    path = Path(args.input).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Manual evaluation file not found: {path}")

    raw_data = path.read_bytes()
    try:
        csv_text = raw_data.decode("utf-8-sig")
    except UnicodeDecodeError:
        csv_text = raw_data.decode("cp1252")
    rows = list(csv.DictReader(csv_text.splitlines()))

    score_fields = [
        "correctness_1_5",
        "completeness_1_5",
        "traceability_1_5",
        "consistency_1_5",
        "source_support_1_5",
        "overall_1_5",
    ]
    scored_rows = [row for row in rows if str(row.get("overall_1_5", "")).strip()]
    invalid: list[str] = []
    for row in scored_rows:
        for field in score_fields:
            raw_value = str(row.get(field, "")).strip()
            try:
                value = float(raw_value)
            except ValueError:
                invalid.append(f"{row.get('question_id')} {row.get('method')}: {field}={raw_value!r}")
                continue
            if not 1 <= value <= 5:
                invalid.append(f"{row.get('question_id')} {row.get('method')}: {field}={raw_value!r}")

    if invalid:
        print("Invalid scores")
        for item in invalid:
            print(f"- {item}")
        raise SystemExit(1)

    print("Manual evaluation summary")
    print(f"- File: {path}")
    print(f"- Total candidate answers: {len(rows)}")
    print(f"- Scored candidate answers: {len(scored_rows)}")
    completion = 100 * len(scored_rows) / len(rows) if rows else 0
    print(f"- Completion: {completion:.1f}%")
    print(
        "- Scored questions: "
        f"{len({str(row.get('question_id', '')) for row in scored_rows})}"
    )

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scored_rows:
        grouped[str(row.get("method", "unknown"))].append(row)

    if grouped:
        print("")
        print("Averages by method")
    for method, method_rows in sorted(grouped.items()):
        print(f"- {method} (n={len(method_rows)})")
        for field in score_fields:
            values = [float(row[field]) for row in method_rows]
            print(f"  - {field}: {sum(values) / len(values):.3f}")

    paired_questions: dict[str, set[str]] = defaultdict(set)
    for row in scored_rows:
        paired_questions[str(row.get("question_id", ""))].add(
            str(row.get("method", ""))
        )
    complete_pairs = [
        question_id
        for question_id, methods in paired_questions.items()
        if {"classic", "graph"}.issubset(methods)
    ]
    print("")
    print(f"- Complete classic/graph pairs: {len(complete_pairs)}")
    if complete_pairs:
        print(f"- Paired question IDs: {', '.join(sorted(complete_pairs))}")


def command_validate(_: argparse.Namespace) -> None:
    sources = load_sources()
    source_ids = {source.id for source in sources}
    questions = load_questions()
    reference_answers = load_reference_answers()

    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    errors: list[str] = []
    warnings: list[str] = []

    node_ids = [node["id"] for node in graph["nodes"]]
    duplicated_nodes = [
        node_id for node_id, count in Counter(node_ids).items() if count > 1
    ]
    if duplicated_nodes:
        errors.append(f"Duplicated graph node IDs: {', '.join(duplicated_nodes)}")

    node_id_set = set(node_ids)
    for edge in graph["edges"]:
        if edge["source"] not in node_id_set:
            errors.append(f"Edge source does not exist: {edge['source']}")
        if edge["target"] not in node_id_set:
            errors.append(f"Edge target does not exist: {edge['target']}")
        for source_id in edge.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(
                    f"Unknown source on edge {edge['source']} -> {edge['target']}: "
                    f"{source_id}"
                )

    question_ids = [str(question["id"]) for question in questions]
    duplicated_questions = [
        question_id
        for question_id, count in Counter(question_ids).items()
        if count > 1
    ]
    if duplicated_questions:
        errors.append(
            f"Duplicated question IDs: {', '.join(duplicated_questions)}"
        )

    for question in questions:
        if not question.get("expected_keywords"):
            warnings.append(f"{question['id']} has no expected keywords")
        if not question.get("relevant_sources"):
            warnings.append(f"{question['id']} has no relevant sources")
        if not question.get("origin_note"):
            warnings.append(f"{question['id']} has no origin_note")
        for source_id in question.get("relevant_sources", []):
            if source_id not in source_ids:
                errors.append(f"{question['id']} references unknown source {source_id}")

    reference_errors, reference_warnings = validate_reference_answers(
        questions,
        reference_answers,
    )
    errors.extend(reference_errors)
    warnings.extend(reference_warnings)

    categories = Counter(str(question.get("category")) for question in questions)
    category_sizes = sorted(categories.values())
    if category_sizes and category_sizes[0] != category_sizes[-1]:
        warnings.append(
            "Question categories are not balanced: "
            + ", ".join(f"{name}={count}" for name, count in sorted(categories.items()))
        )

    print("Dataset validation")
    print(f"- Sources: {len(sources)}")
    print(f"- Questions: {len(questions)}")
    print(f"- Reference answers: {len(reference_answers)}")
    print(f"- Graph nodes: {len(graph['nodes'])}")
    print(f"- Graph relations: {len(graph['edges'])}")
    print(f"- Categories: {', '.join(f'{name}={count}' for name, count in sorted(categories.items()))}")

    if warnings:
        print("")
        print("Warnings")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("")
        print("Errors")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("")
    print("Validation passed: questions, sources and graph references are consistent.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bachelorarbeit experiment: classic RAG vs graph-style retrieval."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sources_parser = subparsers.add_parser("sources", help="List planned sources")
    sources_parser.set_defaults(func=command_sources)

    questions_parser = subparsers.add_parser("questions", help="List test questions")
    questions_parser.set_defaults(func=command_questions)

    categories_parser = subparsers.add_parser(
        "categories",
        help="List question categories and their questions",
    )
    categories_parser.set_defaults(func=command_categories)

    status_parser = subparsers.add_parser("status", help="Show project dataset status")
    status_parser.set_defaults(func=command_status)

    graph_parser = subparsers.add_parser("graph", help="List graph nodes and relations")
    graph_parser.set_defaults(func=command_graph_overview)

    graph_stats_parser = subparsers.add_parser(
        "graph-stats",
        help="Show graph node and relation statistics",
    )
    graph_stats_parser.set_defaults(func=command_graph_stats)

    query_parser = subparsers.add_parser("query", help="Ask one question")
    query_parser.add_argument("--method", choices=["classic", "graph"], required=True)
    query_parser.add_argument("--question", required=True)
    query_parser.add_argument("--top-k", type=int, default=4)
    query_parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw Python dictionary result",
    )
    query_parser.set_defaults(func=command_query)

    testset_parser = subparsers.add_parser(
        "run-testset",
        help="Run all or part of the question set and save results",
    )
    testset_parser.add_argument("--method", choices=["classic", "graph"], required=True)
    testset_parser.add_argument("--limit", type=int, default=None)
    testset_parser.add_argument("--top-k", type=int, default=6)
    testset_parser.set_defaults(func=command_run_testset)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Run classic and graph retrieval on the same question set",
    )
    compare_parser.add_argument("--limit", type=int, default=None)
    compare_parser.add_argument("--top-k", type=int, default=6)
    compare_parser.set_defaults(func=command_compare)

    manual_template_parser = subparsers.add_parser(
        "manual-template",
        help="Create a manual scoring CSV for the current question set",
    )
    manual_template_parser.set_defaults(func=command_manual_template)

    reference_answers_parser = subparsers.add_parser(
        "reference-answers",
        help="Validate reference answers and create evaluation files",
    )
    reference_answers_parser.set_defaults(func=command_reference_answers)

    candidate_answers_parser = subparsers.add_parser(
        "candidate-answers",
        help="Create candidate answers and a manual scoring file",
    )
    candidate_answers_parser.add_argument(
        "--method",
        choices=["classic", "graph", "both"],
        default="both",
    )
    candidate_answers_parser.add_argument("--limit", type=int, default=None)
    candidate_answers_parser.add_argument("--top-k", type=int, default=6)
    candidate_answers_parser.add_argument(
        "--category",
        choices=[
            "configuration_conflict",
            "factual_simple",
            "multi_hop",
            "procedural",
            "relational_troubleshooting",
            "traceability",
        ],
        default=None,
        help="Optional category filter",
    )
    candidate_answers_parser.set_defaults(func=command_candidate_answers)

    manual_summary_parser = subparsers.add_parser(
        "manual-summary",
        help="Summarize a partially or fully scored candidate-answer CSV",
    )
    manual_summary_parser.add_argument(
        "--input",
        required=True,
        help="Path to the manual evaluation CSV",
    )
    manual_summary_parser.set_defaults(func=command_manual_summary)

    automatic_parser = subparsers.add_parser(
        "prepare-auto-evaluation",
        help="Export Classic RAG and GraphRAG results in RAGChecker JSON format",
    )
    automatic_parser.add_argument("--limit", type=int, default=None)
    automatic_parser.add_argument("--top-k", type=int, default=6)
    automatic_parser.set_defaults(func=command_prepare_auto_evaluation)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate questions, sources and graph references",
    )
    validate_parser.set_defaults(func=command_validate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
