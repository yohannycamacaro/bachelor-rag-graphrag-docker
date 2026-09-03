from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_NOTES_PATH = DATA_DIR / "raw" / "docker_support_notes.md"
SOURCES_PATH = DATA_DIR / "sources.json"
GRAPH_PATH = DATA_DIR / "knowledge" / "docker_support_graph.json"
QUESTIONS_PATH = DATA_DIR / "questions" / "docker_support_questions.jsonl"
RESULTS_DIR = PROJECT_ROOT / "results"

