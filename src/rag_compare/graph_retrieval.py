from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .pathing import GRAPH_PATH
from .text import term_frequency, tokenize


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    label: str
    description: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class GraphEdge:
    source: str
    relation: str
    target: str
    evidence: str
    source_ids: tuple[str, ...]


class GraphRagRetriever:
    """A small graph-style retriever before the real LightRAG integration."""

    def __init__(self, graph_path: Path = GRAPH_PATH) -> None:
        with graph_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.nodes = {
            item["id"]: GraphNode(
                id=item["id"],
                type=item["type"],
                label=item["label"],
                description=item["description"],
                keywords=tuple(item.get("keywords", [])),
            )
            for item in data["nodes"]
        }
        self.edges = [
            GraphEdge(
                source=item["source"],
                relation=item["relation"],
                target=item["target"],
                evidence=item["evidence"],
                source_ids=tuple(item.get("source_ids", [])),
            )
            for item in data["edges"]
        ]
        self.node_tfs = {
            node.id: term_frequency(
                tokenize(
                    " ".join(
                        [
                            node.type,
                            node.label,
                            node.description,
                            " ".join(node.keywords),
                        ]
                    )
                )
            )
            for node in self.nodes.values()
        }

    def _node_score(self, question_tokens: Counter[str], node_id: str) -> float:
        node_tokens = self.node_tfs[node_id]
        score = 0.0
        for token, count in question_tokens.items():
            if token in node_tokens:
                score += count * node_tokens[token]
        return score

    def retrieve(self, question: str, top_k: int = 6) -> list[dict[str, object]]:
        question_tokens = term_frequency(tokenize(question))
        relation_intent = self._relation_intent(question)
        seed_scores = {
            node_id: self._node_score(question_tokens, node_id)
            for node_id in self.nodes
        }
        top_problem_nodes = self._top_problem_nodes(seed_scores, question)
        seed_nodes = {
            node_id
            for node_id, score in sorted(
                seed_scores.items(), key=lambda item: item[1], reverse=True
            )[:5]
            if score > 0
        }

        edge_scores: list[tuple[float, GraphEdge]] = []
        for edge in self.edges:
            source_score = seed_scores.get(edge.source, 0.0)
            target_score = seed_scores.get(edge.target, 0.0)
            edge_tf = term_frequency(tokenize(edge.evidence + " " + edge.relation))
            evidence_score = sum(
                count * edge_tf.get(token, 0)
                for token, count in question_tokens.items()
            )
            score = source_score + target_score + evidence_score
            if edge.relation == "diagnosed_by" and "diagnosis" in relation_intent:
                score += target_score
            score += self._problem_focus_boost(edge, top_problem_nodes)
            score += self._relation_boost(
                edge,
                relation_intent,
                top_problem_nodes,
            )
            if edge.source in seed_nodes or edge.target in seed_nodes or score > 0:
                edge_scores.append((score, edge))

        edge_scores.sort(key=lambda item: item[0], reverse=True)
        if edge_scores:
            best_score = edge_scores[0][0]
            minimum_score = max(2.0, best_score * 0.35)
            edge_scores = [
                item for item in edge_scores if item[0] >= minimum_score
            ]
        selected = edge_scores[:top_k]

        return [
            {
                "score": score,
                "source": self.nodes[edge.source],
                "relation": edge.relation,
                "target": self.nodes[edge.target],
                "evidence": edge.evidence,
                "source_ids": edge.source_ids,
            }
            for score, edge in selected
        ]

    def _top_problem_nodes(
        self,
        seed_scores: dict[str, float],
        question: str,
    ) -> set[str]:
        if not self._looks_like_problem_question(question):
            return set()

        problem_scores = {
            node_id: score
            for node_id, score in seed_scores.items()
            if self.nodes[node_id].type == "problem" and score > 0
        }
        if not problem_scores:
            return set()

        best_score = max(problem_scores.values())
        return {
            node_id
            for node_id, score in problem_scores.items()
            if score >= best_score * 0.6
        }

    def _looks_like_problem_question(self, question: str) -> bool:
        text = question.lower()
        problem_terms = [
            "cannot",
            "can't",
            "not",
            "fails",
            "failed",
            "error",
            "missing",
            "unreachable",
            "different",
            "disappear",
            "wrong",
            "problem",
            "issue",
            "unhealthy",
            "why",
        ]
        return any(term in text for term in problem_terms)

    def _problem_focus_boost(
        self,
        edge: GraphEdge,
        top_problem_nodes: set[str],
    ) -> float:
        if edge.source in top_problem_nodes:
            return 5.0
        if edge.target in top_problem_nodes:
            return 3.0
        if self.nodes[edge.source].type == "problem" and top_problem_nodes:
            return -3.0
        return 0.0

    def _relation_intent(self, question: str) -> set[str]:
        text = question.lower()
        intent: set[str] = set()

        diagnosis_terms = [
            "check",
            "debug",
            "diagnos",
            "inspect",
            "verify",
            "pruef",
            "how can",
            "what command",
            "which command",
            "show",
            "find",
        ]
        if any(term in text for term in diagnosis_terms):
            intent.add("diagnosis")
        if any(term in text for term in ["fix", "solve", "solution", "loesung"]):
            intent.add("solution")
        if any(term in text for term in ["why", "cause", "reason", "ursache"]):
            intent.add("cause")
        if any(
            term in text
            for term in [
                "why",
                "explain",
                "prove",
                "source",
                "reliable",
                "nachvollzieh",
                "begruend",
            ]
        ):
            intent.add("traceability")
        if any(
            term in text
            for term in ["different", "difference", "instead", "rather", "distinguish"]
        ):
            intent.add("distinction")
        if any(
            term in text
            for term in ["override", "precedence", "conflict", "different", "ignored"]
        ):
            intent.add("conflict")
        if any(term in text for term in ["required", "must", "need", "requires"]):
            intent.add("requirement")

        return intent

    def _relation_boost(
        self,
        edge: GraphEdge,
        intent: set[str],
        top_problem_nodes: set[str],
    ) -> float:
        if (
            edge.relation == "diagnosed_by"
            and "diagnosis" in intent
            and (not top_problem_nodes or edge.source in top_problem_nodes)
        ):
            return 6.0
        if edge.relation == "solved_by" and "solution" in intent:
            return 4.0
        if edge.relation == "may_be_caused_by" and "cause" in intent:
            return 4.0
        if edge.relation == "documented_in" and "traceability" in intent:
            return 3.0
        if edge.relation == "distinguished_from" and "distinction" in intent:
            return 4.0
        if edge.relation == "conflicts_with" and "conflict" in intent:
            return 4.0
        if edge.relation == "requires" and "requirement" in intent:
            return 3.0
        return 0.0

    def answer(self, question: str, top_k: int = 6) -> dict[str, object]:
        relations = self.retrieve(question, top_k=top_k)

        if not relations:
            answer = "No graph evidence found in the current Docker support graph."
        else:
            answer_parts = []
            for item in relations[:4]:
                source: GraphNode = item["source"]  # type: ignore[assignment]
                target: GraphNode = item["target"]  # type: ignore[assignment]
                answer_parts.append(
                    f"{source.label} --{item['relation']}--> {target.label}. "
                    f"{item['evidence']}"
                )
            answer = " ".join(answer_parts)

        return {
            "method": "graph",
            "question": question,
            "answer": answer,
            "evidence": [
                {
                    "score": round(float(item["score"]), 4),
                    "source": item["source"].id,  # type: ignore[index, union-attr]
                    "source_label": item["source"].label,  # type: ignore[index, union-attr]
                    "relation": item["relation"],
                    "target": item["target"].id,  # type: ignore[index, union-attr]
                    "target_label": item["target"].label,  # type: ignore[index, union-attr]
                    "source_ids": list(item["source_ids"]),
                }
                for item in relations
            ],
        }
