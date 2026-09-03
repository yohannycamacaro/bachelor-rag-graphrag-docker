from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .corpus import CorpusSection
from .text import best_sentences, cosine_like_score, term_frequency, tokenize

DOMAIN_PHRASES = [
    "bind mount",
    "compose file",
    "compose project",
    "container port",
    "docker compose config",
    "docker daemon",
    "docker info",
    "docker network inspect",
    "env_file",
    "environment variable",
    "external dns",
    "external network",
    "healthcheck",
    "host port",
    "network membership",
    "project name",
    "service name",
    "service_healthy",
    "same network",
    "volume",
]


@dataclass(frozen=True)
class Evidence:
    id: str
    title: str
    text: str
    score: float
    source_ids: tuple[str, ...]


class ClassicRagRetriever:
    """Small lexical retriever used as the first document-RAG baseline."""

    def __init__(self, sections: list[CorpusSection]) -> None:
        self.sections = sections
        self.section_tfs = {
            section.id: term_frequency(tokenize(f"{section.title}\n{section.text}"))
            for section in sections
        }
        self.idf = self._build_idf()

    def _build_idf(self) -> dict[str, float]:
        document_count = len(self.sections)
        df: Counter[str] = Counter()

        for tf in self.section_tfs.values():
            for token in tf:
                df[token] += 1

        return {
            token: math.log((document_count + 1) / (count + 1)) + 1
            for token, count in df.items()
        }

    def retrieve(self, question: str, top_k: int = 3) -> list[Evidence]:
        query_tf = term_frequency(tokenize(question))
        scored: list[Evidence] = []

        for section in self.sections:
            score = cosine_like_score(query_tf, self.section_tfs[section.id], self.idf)
            score += phrase_bonus(question, f"{section.title}\n{section.text}")
            if score <= 0:
                continue
            scored.append(
                Evidence(
                    id=section.id,
                    title=section.title,
                    text=section.text,
                    score=score,
                    source_ids=section.source_ids,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def answer(self, question: str, top_k: int = 3) -> dict[str, object]:
        evidence = self.retrieve(question, top_k=top_k)
        selected_sentences: list[str] = []

        for item in evidence:
            selected_sentences.extend(best_sentences(item.text, question, limit=2))

        if not selected_sentences and evidence:
            selected_sentences = [evidence[0].text.splitlines()[0]]

        answer = " ".join(selected_sentences[:4]).strip()
        if not answer:
            answer = "No evidence found in the current Docker support notes."

        return {
            "method": "classic",
            "question": question,
            "answer": answer,
            "evidence": [
                {
                    "id": item.id,
                    "title": item.title,
                    "score": round(item.score, 4),
                    "source_ids": list(item.source_ids),
                }
                for item in evidence
            ],
        }


def phrase_bonus(question: str, candidate_text: str) -> float:
    question_text = question.lower()
    candidate = candidate_text.lower()
    bonus = 0.0

    for phrase in DOMAIN_PHRASES:
        if phrase in question_text and phrase in candidate:
            bonus += 0.25

    return bonus
