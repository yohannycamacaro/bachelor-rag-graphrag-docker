from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable


TOKEN_RE = re.compile(r"[a-zA-Z0-9_./:-]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "name",
    "of",
    "or",
    "should",
    "the",
    "to",
    "what",
    "when",
    "where",
    "why",
    "with",
    "you",
    "your",
    "app",
    "application",
    "inside",
    "running",
    "run",
    "runs",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS and len(token) > 1
    ]


def term_frequency(tokens: Iterable[str]) -> Counter[str]:
    return Counter(tokens)


def cosine_like_score(
    query_tf: Counter[str],
    doc_tf: Counter[str],
    idf: dict[str, float],
) -> float:
    score = 0.0
    query_norm = 0.0
    doc_norm = 0.0

    for token, count in query_tf.items():
        weight = count * idf.get(token, 1.0)
        query_norm += weight * weight

    for token, count in doc_tf.items():
        weight = count * idf.get(token, 1.0)
        doc_norm += weight * weight

    for token, q_count in query_tf.items():
        if token in doc_tf:
            score += q_count * doc_tf[token] * (idf.get(token, 1.0) ** 2)

    if query_norm == 0 or doc_norm == 0:
        return 0.0

    return score / (math.sqrt(query_norm) * math.sqrt(doc_norm))


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    return re.split(r"(?<=[.!?])\s+", cleaned)


def best_sentences(text: str, query: str, limit: int = 3) -> list[str]:
    query_tokens = set(tokenize(query))
    scored: list[tuple[float, str]] = []

    for sentence in split_sentences(text):
        tokens = set(tokenize(sentence))
        overlap = len(query_tokens & tokens)
        if overlap:
            scored.append((overlap / max(len(tokens), 1), sentence))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [sentence for _, sentence in scored[:limit]]
