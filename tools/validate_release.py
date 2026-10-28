from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_set(question_file: str, reference_file: str, expected: int) -> None:
    questions = read_jsonl(ROOT / question_file)
    references = read_jsonl(ROOT / reference_file)
    assert len(questions) == expected, f"{question_file}: expected {expected}, got {len(questions)}"
    assert len(references) == expected, f"{reference_file}: expected {expected}, got {len(references)}"
    qids = {item["id"] for item in questions}
    rids = {item["question_id"] for item in references}
    assert len(qids) == expected and qids == rids, f"Question/reference mismatch in {question_file}"
    assert len({item["category"] for item in questions}) == 6, f"Expected six categories in {question_file}"
    for item in references:
        missing = {"reference_answer", "must_include", "scoring_focus"}.difference(item)
        assert not missing, f"{item['question_id']}: missing {sorted(missing)}"


def main() -> None:
    check_set("data/questions/docker_support_questions.jsonl", "data/evaluation/reference_answers.jsonl", 48)
    check_set("data/questions/docker_support_challenge_questions.jsonl", "data/evaluation/challenge_reference_answers.jsonl", 12)
    check_set("data/questions/docker_support_holdout_questions.jsonl", "data/evaluation/holdout_reference_answers.jsonl", 12)

    graph = json.loads((ROOT / "data/knowledge/docker_support_graph.json").read_text(encoding="utf-8"))
    nodes, edges = graph["nodes"], graph["edges"]
    node_ids = {node["id"] for node in nodes}
    assert len(nodes) == 94, f"Expected 94 graph nodes, got {len(nodes)}"
    assert len(edges) == 119, f"Expected 119 graph edges, got {len(edges)}"
    for edge in edges:
        assert edge["source"] in node_ids and edge["target"] in node_ids, f"Dangling edge: {edge}"

    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    assert len(sources) == 12, f"Expected 12 sources, got {len(sources)}"

    for relative in (
        "results/final/main_metrics_by_category.csv",
        "results/final/challenge_metrics_by_category.csv",
        "results/final/holdout_metrics_by_category.csv",
        "results/final/evaluation_metadata.json",
    ):
        assert (ROOT / relative).is_file(), f"Missing final output: {relative}"

    metadata = json.loads((ROOT / "results/final/evaluation_metadata.json").read_text(encoding="utf-8"))
    assert metadata["evaluator"]["model"] == "gpt-4.1-mini"
    print("Release check passed: datasets, graph, sources and curated outputs are consistent.")


if __name__ == "__main__":
    main()
