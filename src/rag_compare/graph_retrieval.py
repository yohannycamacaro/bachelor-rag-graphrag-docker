from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .pathing import GRAPH_PATH
from .text import term_frequency, tokenize

GRAPH_DOMAIN_PHRASES = {
    "bind mount": 3.0,
    "container port": 4.0,
    "docker daemon": 4.0,
    "docker compose config": 4.0,
    "env_file": 3.0,
    "environment variable": 3.0,
    "external network": 4.0,
    "healthcheck": 3.0,
    "host port": 4.0,
    "localhost": 2.0,
    "service name": 5.0,
    "service_healthy": 3.0,
    "same network": 4.0,
    "volume": 3.0,
}

# Equivalent formulations that should contribute to the same retrieval concept.
# Exact phrase matching alone can miss a relevant graph path when a question
# describes the opposite state, for example "different networks" versus
# "services must share a network".
GRAPH_CONCEPTS = {
    "network_membership": {
        "question": (
            "different network",
            "different networks",
            "separate network",
            "separate networks",
            "shared network",
            "same network",
        ),
        "candidate": (
            "different network",
            "different networks",
            "network membership",
            "same network",
            "share a network",
            "shared network",
        ),
        "weight": 5.0,
    },
    "readiness": {
        "question": ("depends_on", "healthcheck", "service_healthy", "startup"),
        "candidate": ("depends_on", "healthcheck", "service_healthy", "readiness"),
        "weight": 3.0,
    },
    "port_scope": {
        "question": ("container port", "host port", "published host port"),
        "candidate": ("container port", "host port", "published host port"),
        "weight": 3.0,
    },
}

# Some graph nodes describe a narrow scenario whose generic words would
# otherwise create false positives. Such nodes are only eligible when the
# question contains at least one discriminating cue.
NODE_REQUIRED_CUES = {
    "problem.scaled_service_port_ambiguous": ("scaled", "replica", "dynamic port"),
    "cause.replica_dynamic_host_ports": ("scaled", "replica", "dynamic port"),
    "solution.inspect_port_with_index": ("scaled", "replica", "--index"),
    "problem.host_network_no_service_dns": ("host network", "network_mode"),
    "cause.host_network_bypasses_compose_dns": ("host network", "network_mode"),
    "problem.required_interpolation_missing": (
        "interpolation",
        "environment variable",
        "variable is required",
        "${",
    ),
}

GENERIC_PROBLEM_TOKENS = {
    "cant",
    "can't",
    "cannot",
    "check",
    "error",
    "failed",
    "fails",
    "fix",
    "get",
    "issue",
    "missing",
    "problem",
    "reach",
    "solve",
    "wrong",
}


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
            if token in GENERIC_PROBLEM_TOKENS:
                continue
            if token in node_tokens:
                score += count * node_tokens[token]
        return score

    def _phrase_score(self, question: str, text: str) -> float:
        question_text = question.lower()
        candidate = text.lower()
        score = 0.0
        for phrase, weight in GRAPH_DOMAIN_PHRASES.items():
            if phrase in question_text and phrase in candidate:
                score += weight
        return score

    def _concept_score(self, question: str, text: str) -> float:
        question_text = question.lower()
        candidate = text.lower()
        score = 0.0
        for concept in GRAPH_CONCEPTS.values():
            question_match = any(
                phrase in question_text for phrase in concept["question"]
            )
            candidate_match = any(
                phrase in candidate for phrase in concept["candidate"]
            )
            if question_match and candidate_match:
                score += float(concept["weight"])
        return score

    def _node_is_eligible(self, question: str, node_id: str) -> bool:
        required_cues = NODE_REQUIRED_CUES.get(node_id)
        if not required_cues:
            return True
        question_text = question.lower()
        return any(cue in question_text for cue in required_cues)

    def retrieve(self, question: str, top_k: int = 6) -> list[dict[str, object]]:
        question_tokens = term_frequency(tokenize(question))
        relation_intent = self._relation_intent(question)
        seed_scores = {
            node_id: (
                self._node_score(question_tokens, node_id)
                + (self._phrase_score(question, self.nodes[node_id].label) * 2.0)
                + (self._concept_score(question, self.nodes[node_id].label) * 2.0)
                + (
                    self._phrase_score(
                        question,
                        " ".join(
                            [
                                self.nodes[node_id].description,
                                " ".join(self.nodes[node_id].keywords),
                            ]
                        ),
                    )
                    * 0.5
                )
                + (
                    self._concept_score(
                        question,
                        " ".join(
                            [
                                self.nodes[node_id].description,
                                " ".join(self.nodes[node_id].keywords),
                            ]
                        ),
                    )
                    * 0.5
                )
            )
            if self._node_is_eligible(question, node_id)
            else 0.0
            for node_id in self.nodes
        }
        top_problem_nodes = self._top_problem_nodes(seed_scores, question)
        focus_nodes = self._focus_nodes(top_problem_nodes)
        seed_nodes = {
            node_id
            for node_id, score in sorted(
                seed_scores.items(), key=lambda item: item[1], reverse=True
            )[:5]
            if score > 0
        }

        edge_scores: list[tuple[float, GraphEdge]] = []
        for edge in self.edges:
            if focus_nodes and edge.source not in focus_nodes and edge.target not in focus_nodes:
                continue
            source_score = seed_scores.get(edge.source, 0.0)
            target_score = seed_scores.get(edge.target, 0.0)
            edge_tf = term_frequency(tokenize(edge.evidence + " " + edge.relation))
            evidence_score = sum(
                count * edge_tf.get(token, 0)
                for token, count in question_tokens.items()
            )
            evidence_score += self._phrase_score(question, edge.evidence)
            evidence_score += self._concept_score(question, edge.evidence)
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

    def _focus_nodes(self, top_problem_nodes: set[str]) -> set[str]:
        if not top_problem_nodes:
            return set()

        focus_nodes = set(top_problem_nodes)
        for edge in self.edges:
            if edge.source in top_problem_nodes:
                focus_nodes.add(edge.target)
            if edge.target in top_problem_nodes:
                focus_nodes.add(edge.source)
        return focus_nodes

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
        ranked = sorted(problem_scores.items(), key=lambda item: item[1], reverse=True)
        return {
            node_id
            for node_id, score in ranked[:3]
            if score >= best_score * 0.4
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
            for item in relations:
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
                    "text": (
                        f"{item['source'].label} --{item['relation']}--> "  # type: ignore[index, union-attr]
                        f"{item['target'].label}. {item['evidence']}"  # type: ignore[index, union-attr]
                    ),
                    "source_ids": list(item["source_ids"]),
                }
                for item in relations
            ],
        }
