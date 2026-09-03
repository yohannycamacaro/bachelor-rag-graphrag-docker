from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .pathing import RAW_NOTES_PATH, SOURCES_PATH


SECTION_RE = re.compile(r"^## \[(?P<section_id>[^\]]+)\]\s+(?P<title>.+)$")


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    area: str
    planned_usage: str


@dataclass(frozen=True)
class CorpusSection:
    id: str
    title: str
    text: str
    source_ids: tuple[str, ...]


def load_sources(path: Path = SOURCES_PATH) -> list[Source]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Source(**item) for item in data]


def load_markdown_sections(path: Path = RAW_NOTES_PATH) -> list[CorpusSection]:
    sections: list[CorpusSection] = []
    current_id: str | None = None
    current_title: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, current_lines
        if current_id is None or current_title is None:
            return

        text = "\n".join(current_lines).strip()
        source_ids: tuple[str, ...] = ()
        body_lines: list[str] = []

        for line in text.splitlines():
            if line.startswith("Sources:"):
                raw_sources = line.removeprefix("Sources:").strip()
                source_ids = tuple(
                    source.strip()
                    for source in raw_sources.split(",")
                    if source.strip()
                )
            else:
                body_lines.append(line)

        sections.append(
            CorpusSection(
                id=current_id,
                title=current_title,
                text="\n".join(body_lines).strip(),
                source_ids=source_ids,
            )
        )

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            match = SECTION_RE.match(line.rstrip())
            if match:
                flush()
                current_id = match.group("section_id")
                current_title = match.group("title")
                current_lines = []
            elif current_id is not None:
                current_lines.append(line.rstrip())

    flush()
    return sections

