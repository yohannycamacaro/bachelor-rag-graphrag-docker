from __future__ import annotations

import csv
import html
import json
import mimetypes
import sys
import webbrowser
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from rag_compare.corpus import load_markdown_sections, load_sources  # noqa: E402
from rag_compare.evaluation import (  # noqa: E402
    build_result_record,
    load_questions,
    load_reference_answers,
)
from rag_compare.graph_retrieval import GraphRagRetriever  # noqa: E402
from rag_compare.pathing import GRAPH_PATH, RESULTS_DIR  # noqa: E402
from rag_compare.retrieval import ClassicRagRetriever  # noqa: E402


HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def latest_category_csv() -> Path | None:
    paths = sorted(
        RESULTS_DIR.glob("category_comparison_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return paths[0] if paths else None


class DashboardState:
    def __init__(self) -> None:
        self.sources = load_sources()
        self.sections = load_markdown_sections()
        self.questions = load_questions()
        self.reference_answers = load_reference_answers()
        with GRAPH_PATH.open("r", encoding="utf-8") as file:
            self.graph = json.load(file)
        self.classic = ClassicRagRetriever(self.sections)
        self.graph_retriever = GraphRagRetriever()

    def status(self) -> dict[str, object]:
        categories = Counter(str(question.get("category")) for question in self.questions)
        node_types = Counter(node["type"] for node in self.graph["nodes"])
        relation_types = Counter(edge["relation"] for edge in self.graph["edges"])
        avg_hops = sum(
            float(question.get("expected_relation_hops") or 0)
            for question in self.questions
        ) / max(len(self.questions), 1)

        return {
            "sources": len(self.sources),
            "support_cases": len(self.sections),
            "questions": len(self.questions),
            "reference_answers": len(self.reference_answers),
            "avg_expected_relation_hops": round(avg_hops, 2),
            "graph_nodes": len(self.graph["nodes"]),
            "graph_relations": len(self.graph["edges"]),
            "categories": dict(sorted(categories.items())),
            "node_types": dict(sorted(node_types.items())),
            "relation_types": dict(sorted(relation_types.items())),
        }

    def categories(self) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = {}
        for question in self.questions:
            grouped.setdefault(str(question.get("category")), []).append(question)

        rows: list[dict[str, object]] = []
        for category, items in sorted(grouped.items()):
            avg_hops = sum(
                float(item.get("expected_relation_hops") or 0) for item in items
            ) / len(items)
            rows.append(
                {
                    "category": category,
                    "label": items[0].get("category_label", category),
                    "count": len(items),
                    "avg_hops": round(avg_hops, 2),
                }
            )
        return rows

    def question_list(self) -> list[dict[str, object]]:
        return [
            {
                "id": question["id"],
                "question": question["question"],
                "question_de": question.get("question_de", ""),
                "category": question.get("category", ""),
                "category_label": question.get("category_label", ""),
                "difficulty": question.get("difficulty", ""),
                "expected_relation_hops": question.get(
                    "expected_relation_hops", ""
                ),
            }
            for question in self.questions
        ]

    def question_by_id(self, question_id: str) -> dict[str, object] | None:
        for question in self.questions:
            if str(question["id"]) == question_id:
                return question
        return None

    def ask_both(
        self,
        question_text: str,
        question_id: str | None = None,
    ) -> dict[str, object]:
        question = self.question_by_id(question_id or "") if question_id else None
        if question is None:
            question = {
                "id": "custom",
                "question": question_text,
                "question_de": "",
                "difficulty": "custom",
                "category": "custom",
                "category_label": "Eigene Frage",
                "expected_relation_hops": "",
                "expected_keywords": [],
                "relevant_sources": [],
            }

        classic_result = self.classic.answer(question_text, top_k=6)
        graph_result = self.graph_retriever.answer(question_text, top_k=6)

        response = {
            "question": question,
            "reference": self.reference_answers.get(str(question.get("id")), {}),
            "classic": classic_result,
            "graph": graph_result,
        }

        if question.get("id") != "custom":
            response["classic_metrics"] = build_result_record(question, classic_result)
            response["graph_metrics"] = build_result_record(question, graph_result)

        return response

    def latest_comparison(self) -> dict[str, object]:
        path = latest_category_csv()
        if path is None:
            return {"source": None, "rows": []}
        with path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
        return {"source": str(path.name), "rows": rows}


STATE = DashboardState()


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "BachelorRagDashboard/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            if path == "/":
                self.send_html(DASHBOARD_HTML)
            elif path == "/api/status":
                self.send_json(STATE.status())
            elif path == "/api/categories":
                self.send_json(STATE.categories())
            elif path == "/api/questions":
                self.send_json(STATE.question_list())
            elif path == "/api/latest-comparison":
                self.send_json(STATE.latest_comparison())
            elif path == "/api/query":
                question_id = first(query, "id")
                question_text = first(query, "question")
                if question_id and not question_text:
                    question = STATE.question_by_id(question_id)
                    question_text = str(question.get("question", "")) if question else ""
                if not question_text:
                    self.send_json({"error": "Frage fehlt."}, status=400)
                    return
                self.send_json(STATE.ask_both(question_text, question_id))
            elif path == "/chart.png":
                self.send_file(PROJECT_ROOT / "docs" / "category_comparison_chart.png")
            elif path == "/graph-view":
                self.send_file(PROJECT_ROOT / "docs" / "docker_support_graph_view.html")
            else:
                self.send_json({"error": "Nicht gefunden."}, status=404)
        except Exception as error:  # pragma: no cover - useful in local UI
            self.send_json({"error": str(error)}, status=500)

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_html(self, text: str, status: int = 200) -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path: Path) -> None:
        if not path.exists():
            self.send_json({"error": f"File not found: {path.name}"}, status=404)
            return
        data = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key, [])
    return values[0] if values else ""


DASHBOARD_HTML = r"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Klassisches RAG und GraphRAG im Vergleich</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #5f6c7b;
      --line: #d8e0ea;
      --blue: #0b5fa5;
      --purple: #6b46c1;
      --green: #2f855a;
      --soft-blue: #eaf3fb;
      --soft-purple: #f1ecff;
      --soft-green: #eaf7ef;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 15px;
      letter-spacing: 0;
    }
    header {
      padding: 24px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 28px;
      line-height: 1.18;
      font-weight: 750;
    }
    .subtitle {
      color: var(--muted);
      font-size: 15px;
    }
    main {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px 28px 40px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(6, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .metric {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      min-height: 78px;
    }
    .metric strong {
      display: block;
      font-size: 25px;
      line-height: 1.1;
      margin-bottom: 6px;
    }
    .metric span { color: var(--muted); font-size: 13px; }
    .grid {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 18px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 18px;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 17px;
      line-height: 1.25;
    }
    label {
      display: block;
      margin: 12px 0 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }
    select, textarea, input[type="search"] {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      font: inherit;
      padding: 10px 12px;
    }
    textarea {
      min-height: 112px;
      resize: vertical;
      line-height: 1.4;
    }
    .question-preview {
      min-height: 92px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fafc;
      line-height: 1.45;
    }
    .question-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    button, a.button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #0b5fa5;
      background: #0b5fa5;
      color: #ffffff;
      border-radius: 8px;
      padding: 10px 14px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      min-height: 40px;
    }
    button.secondary, a.secondary {
      background: #ffffff;
      color: #0b5fa5;
    }
    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }
    .answers {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .answer-panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-height: 280px;
      background: #ffffff;
    }
    .classic { border-top: 5px solid var(--blue); }
    .graph { border-top: 5px solid var(--purple); }
    .answer-panel h3 {
      margin: 0 0 10px;
      font-size: 16px;
    }
    .answer {
      line-height: 1.48;
      white-space: pre-wrap;
    }
    .evidence {
      margin-top: 14px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }
    .evidence-item {
      margin: 8px 0;
      padding: 9px 10px;
      border-radius: 8px;
      background: #f8fafc;
      border: 1px solid #edf1f5;
      font-size: 13px;
      line-height: 1.38;
    }
    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      background: #edf2f7;
      color: #354152;
      font-size: 12px;
      font-weight: 650;
    }
    .reference {
      background: var(--soft-green);
      border: 1px solid #cfead8;
      border-radius: 8px;
      padding: 12px 14px;
      line-height: 1.45;
      margin-bottom: 14px;
    }
    .reference h3 {
      margin: 0 0 8px;
      font-size: 15px;
    }
    .muted { color: var(--muted); }
    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
    }
    th, td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }
    th {
      background: #f0f5fb;
      font-weight: 750;
    }
    tr:last-child td { border-bottom: 0; }
    .chart {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      display: block;
    }
    .small-note {
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }
    details.custom-question {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }
    details.custom-question summary {
      cursor: pointer;
      color: var(--blue);
      font-weight: 700;
    }
    .catalog-filters {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) minmax(220px, 320px);
      gap: 12px;
      margin-bottom: 14px;
    }
    .catalog-filters label { margin-top: 0; }
    .catalog-wrap {
      max-height: 520px;
      overflow: auto;
    }
    .catalog-table th {
      position: sticky;
      top: 0;
      z-index: 1;
    }
    .catalog-table td:nth-child(1) { width: 76px; }
    .catalog-table td:nth-child(2) { width: 210px; }
    .catalog-table td:nth-child(4),
    .catalog-table td:nth-child(5) { width: 110px; }
    button.catalog-select {
      min-height: 34px;
      padding: 6px 10px;
      white-space: nowrap;
    }
    .loading {
      color: var(--muted);
      font-style: italic;
    }
    @media (max-width: 980px) {
      .stats { grid-template-columns: repeat(2, minmax(130px, 1fr)); }
      .grid, .answers { grid-template-columns: 1fr; }
      .catalog-filters { grid-template-columns: 1fr; }
      main { padding: 18px 14px 32px; }
      header { padding: 20px 18px 14px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Klassisches RAG und GraphRAG im Vergleich</h1>
    <div class="subtitle">Interaktiver Versuchsaufbau für Docker-Compose-Troubleshooting</div>
  </header>
  <main>
    <div class="stats" id="stats"></div>
    <div class="grid">
      <aside>
        <section>
          <h2>Katalogfrage auswählen</h2>
          <div class="small-note">Wählen Sie eine der 48 Versuchsfragen aus. Für den Vergleich ist keine Texteingabe erforderlich.</div>
          <label for="questionSelect">Fragenkatalog</label>
          <select id="questionSelect"></select>
          <div id="questionMeta" class="question-meta"></div>
          <label for="selectedQuestion">Ausgewählte Frage</label>
          <div id="selectedQuestion" class="question-preview"></div>
          <div class="actions">
            <button id="askButton">Beide Methoden vergleichen</button>
            <a class="button secondary" href="/graph-view" target="_blank" rel="noreferrer">Wissensgraph öffnen</a>
          </div>
          <div class="small-note">Intern wird die englische Originalfrage aus dem Datensatz verwendet. Dadurch bleibt der dokumentierte Versuchsstand reproduzierbar.</div>
          <details class="custom-question">
            <summary>Eigene Frage testen (optional)</summary>
            <label for="customQuestion">Freie Frage</label>
            <textarea id="customQuestion" placeholder="Eigene Docker- oder Docker-Compose-Frage eingeben"></textarea>
            <div class="actions">
              <button id="customAskButton" class="secondary">Eigene Frage vergleichen</button>
            </div>
            <div class="small-note">Für freie Fragen existiert keine vorbereitete Referenzantwort. Fachbegriffe aus der englischen Docker-Dokumentation verbessern die Suche.</div>
          </details>
        </section>
        <section>
          <h2>Fragekategorien</h2>
          <div id="categories" class="table-wrap"></div>
        </section>
      </aside>
      <div>
        <section>
          <h2>Vergleichsergebnis</h2>
          <div id="reference" class="reference" hidden></div>
          <div class="answers">
            <div class="answer-panel classic">
              <h3>Klassisches RAG</h3>
              <div id="classicAnswer" class="answer loading">Wählen Sie eine Frage aus und starten Sie den Vergleich.</div>
              <div id="classicEvidence" class="evidence"></div>
            </div>
            <div class="answer-panel graph">
              <h3>GraphRAG</h3>
              <div id="graphAnswer" class="answer loading">Wählen Sie eine Frage aus und starten Sie den Vergleich.</div>
              <div id="graphEvidence" class="evidence"></div>
            </div>
          </div>
          <div class="small-note">Die Bedienoberfläche ist deutsch. Antwort- und Evidenztexte bleiben in der englischen Originalsprache der ausgewerteten Docker-Dokumentation.</div>
        </section>
        <section>
          <h2>Gespeicherte Voranalyse</h2>
          <img class="chart" src="/chart.png" alt="Voranalyse nach Fragekategorien">
          <div id="comparisonTable" class="table-wrap" style="margin-top: 14px;"></div>
        </section>
      </div>
    </div>
    <section>
      <h2>Vollständiger Fragenkatalog</h2>
      <div class="catalog-filters">
        <div>
          <label for="questionSearch">Suche nach ID oder Fragetext</label>
          <input id="questionSearch" type="search" placeholder="Zum Beispiel Q017, Netzwerk oder Healthcheck">
        </div>
        <div>
          <label for="categoryFilter">Kategorie</label>
          <select id="categoryFilter"><option value="">Alle Kategorien</option></select>
        </div>
      </div>
      <div id="catalogCount" class="small-note"></div>
      <div id="questionCatalog" class="table-wrap catalog-wrap"></div>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    let questions = [];

    const difficultyLabels = {
      simple: "Einfach",
      procedural: "Prozedural",
      relational: "Relational",
      multi_hop: "Multi-Hop",
      traceability: "Nachvollziehbarkeit"
    };

    const relationLabels = {
      affects: "betrifft",
      conflicts_with: "steht im Konflikt mit",
      diagnosed_by: "wird diagnostiziert durch",
      distinguished_from: "wird unterschieden von",
      documented_in: "ist dokumentiert in",
      may_be_caused_by: "kann verursacht werden durch",
      requires: "erfordert",
      solved_by: "wird gelöst durch"
    };

    const germanTypography = {
      "DNS-Aufloesung": "DNS-Auflösung",
      "Loesung": "Lösung",
      "Namenspraefix": "Namenspräfix",
      "aufgeloeste": "aufgelöste",
      "aufloesen": "auflösen",
      "ausgefuehrt": "ausgeführt",
      "erhaelt": "erhält",
      "fehlschlaegt": "fehlschlägt",
      "frueh": "früh",
      "fuer": "für",
      "hinzufuegen": "hinzufügen",
      "laeuft": "läuft",
      "moechte": "möchte",
      "pruefen": "prüfen",
      "ueber": "über",
      "veraendert": "verändert",
      "verhaelt": "verhält",
      "verlaesslicher": "verlässlicher",
      "veroeffentlicht": "veröffentlicht",
      "zusammenzufuehren": "zusammenzuführen"
    };

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }[char]));
    }

    async function getJson(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    }

    function metric(label, value) {
      return `<div class="metric"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`;
    }

    function displayQuestion(question) {
      let text = question.question_de || question.question || "";
      for (const [plain, localized] of Object.entries(germanTypography)) {
        text = text.replace(new RegExp(`\\b${plain}\\b`, "g"), localized);
      }
      return text;
    }

    function difficultyLabel(value) {
      return difficultyLabels[value] || value || "Nicht angegeben";
    }

    function relationLabel(value) {
      return relationLabels[value] || value || "Relation";
    }

    async function loadStatus() {
      const status = await getJson("/api/status");
      $("stats").innerHTML = [
        metric("Quellen", status.sources),
        metric("Wissensfälle", status.support_cases),
        metric("Katalogfragen", status.questions),
        metric("Referenzantworten", status.reference_answers),
        metric("Knoten", status.graph_nodes),
        metric("Relationen", status.graph_relations),
      ].join("");
    }

    async function loadQuestions() {
      questions = await getJson("/api/questions");
      $("questionSelect").innerHTML = questions.map((q) =>
        `<option value="${esc(q.id)}">${esc(q.id)} · ${esc(q.category_label)} · ${esc(displayQuestion(q))}</option>`
      ).join("");

      const categories = [...new Map(
        questions.map((q) => [q.category, q.category_label])
      ).entries()].sort((a, b) => a[1].localeCompare(b[1], "de"));
      $("categoryFilter").innerHTML = `<option value="">Alle Kategorien</option>${
        categories.map(([value, label]) =>
          `<option value="${esc(value)}">${esc(label)}</option>`
        ).join("")
      }`;

      if (questions.length) {
        $("questionSelect").value = "Q002";
        if (!$("questionSelect").value) $("questionSelect").value = questions[0].id;
        updateSelectedQuestion();
      }
      renderQuestionCatalog();
    }

    function selectedQuestion() {
      return questions.find((q) => q.id === $("questionSelect").value);
    }

    function updateSelectedQuestion() {
      const question = selectedQuestion();
      if (!question) return;
      $("selectedQuestion").textContent = displayQuestion(question);
      $("questionMeta").innerHTML = [
        question.id,
        question.category_label,
        difficultyLabel(question.difficulty),
        `${question.expected_relation_hops} Relationssprünge`
      ].map((item) => `<span class="pill">${esc(item)}</span>`).join("");
    }

    function filteredQuestions() {
      const term = $("questionSearch").value.trim().toLocaleLowerCase("de");
      const category = $("categoryFilter").value;
      return questions.filter((question) => {
        const haystack = [
          question.id,
          question.category_label,
          displayQuestion(question),
          question.question
        ].join(" ").toLocaleLowerCase("de");
        return (!term || haystack.includes(term)) &&
          (!category || question.category === category);
      });
    }

    function renderQuestionCatalog() {
      const visibleQuestions = filteredQuestions();
      $("catalogCount").textContent = `${visibleQuestions.length} von ${questions.length} Fragen angezeigt`;
      if (!visibleQuestions.length) {
        $("questionCatalog").innerHTML = `<div class="small-note">Keine passende Frage gefunden.</div>`;
        return;
      }
      $("questionCatalog").innerHTML = `<table class="catalog-table"><thead><tr><th>ID</th><th>Kategorie</th><th>Frage</th><th>Schwierigkeit</th><th>Sprünge</th><th></th></tr></thead><tbody>${
        visibleQuestions.map((question) => `<tr>
          <td><strong>${esc(question.id)}</strong></td>
          <td>${esc(question.category_label)}</td>
          <td>${esc(displayQuestion(question))}</td>
          <td>${esc(difficultyLabel(question.difficulty))}</td>
          <td>${esc(question.expected_relation_hops)}</td>
          <td><button class="catalog-select" data-question-id="${esc(question.id)}">Vergleichen</button></td>
        </tr>`).join("")
      }</tbody></table>`;

      $("questionCatalog").querySelectorAll("button[data-question-id]").forEach((button) => {
        button.addEventListener("click", async () => {
          $("questionSelect").value = button.dataset.questionId;
          updateSelectedQuestion();
          document.querySelector("main").scrollIntoView({ behavior: "smooth" });
          await askCatalogQuestion();
        });
      });
    }

    async function loadCategories() {
      const rows = await getJson("/api/categories");
      $("categories").innerHTML = `<table><thead><tr><th>Kategorie</th><th>Anzahl</th><th>Ø Sprünge</th></tr></thead><tbody>${
        rows.map((row) => `<tr><td>${esc(row.label)}</td><td>${esc(row.count)}</td><td>${esc(row.avg_hops)}</td></tr>`).join("")
      }</tbody></table>`;
    }

    async function loadComparison() {
      const data = await getJson("/api/latest-comparison");
      if (!data.rows.length) {
        $("comparisonTable").innerHTML = `<div class="small-note">Noch keine gespeicherte Vergleichsauswertung verfügbar.</div>`;
        return;
      }
      $("comparisonTable").innerHTML = `<table><thead><tr><th>Kategorie</th><th>Klassisches RAG</th><th>GraphRAG</th><th>Differenz</th></tr></thead><tbody>${
        data.rows.map((row) => `<tr><td>${esc(row.category_label)}</td><td>${esc(row.classic_keyword_coverage)}</td><td>${esc(row.graph_keyword_coverage)}</td><td>${esc(row.keyword_delta_graph_minus_classic)}</td></tr>`).join("")
      }</tbody></table>`;
    }

    function renderEvidence(target, evidence) {
      if (!Array.isArray(evidence) || !evidence.length) {
        target.innerHTML = `<strong>Abgerufene Evidenz</strong><div class="muted">Keine Evidenz gefunden.</div>`;
        return;
      }
      const items = evidence.map((item, index) => {
        if (item.relation) {
          return `<div class="evidence-item"><strong>${index + 1}. ${esc(item.source_label)}</strong> · ${esc(relationLabel(item.relation))} · <strong>${esc(item.target_label)}</strong><div class="pill-row">${(item.source_ids || []).map((id) => `<span class="pill">${esc(id)}</span>`).join("")}</div></div>`;
        }
        return `<div class="evidence-item"><strong>${index + 1}. ${esc(item.title)}</strong><div class="pill-row">${(item.source_ids || []).map((id) => `<span class="pill">${esc(id)}</span>`).join("")}</div></div>`;
      }).join("");
      target.innerHTML = `<strong>Abgerufene Evidenz</strong>${items}`;
    }

    function renderReference(reference) {
      const panel = $("reference");
      if (!reference || !reference.reference_answer) {
        panel.hidden = true;
        panel.innerHTML = "";
        return;
      }
      panel.hidden = false;
      const includes = (reference.must_include || []).map((item) => `<span class="pill">${esc(item)}</span>`).join("");
      panel.innerHTML = `<h3>Referenzantwort (englischer Originaltext)</h3><div>${esc(reference.reference_answer)}</div><div class="small-note"><strong>Erwartete Inhalte</strong></div><div class="pill-row">${includes}</div><div class="small-note"><strong>Bewertungsschwerpunkt:</strong> ${esc(reference.scoring_focus || "")}</div>`;
    }

    function setLoading() {
      $("classicAnswer").textContent = "Vergleich wird berechnet...";
      $("graphAnswer").textContent = "Vergleich wird berechnet...";
      $("classicAnswer").classList.add("loading");
      $("graphAnswer").classList.add("loading");
      $("classicEvidence").innerHTML = "";
      $("graphEvidence").innerHTML = "";
    }

    function renderResult(data) {
      renderReference(data.reference);
      $("classicAnswer").textContent = data.classic.answer;
      $("graphAnswer").textContent = data.graph.answer;
      $("classicAnswer").classList.remove("loading");
      $("graphAnswer").classList.remove("loading");
      renderEvidence($("classicEvidence"), data.classic.evidence);
      renderEvidence($("graphEvidence"), data.graph.evidence);
    }

    async function askCatalogQuestion() {
      const id = $("questionSelect").value;
      if (!id) return;
      setLoading();
      const data = await getJson(`/api/query?id=${encodeURIComponent(id)}`);
      renderResult(data);
    }

    async function askCustomQuestion() {
      const question = $("customQuestion").value.trim();
      if (!question) {
        $("customQuestion").focus();
        $("customQuestion").setCustomValidity("Bitte geben Sie eine Frage ein.");
        $("customQuestion").reportValidity();
        return;
      }
      $("customQuestion").setCustomValidity("");
      setLoading();
      const data = await getJson(`/api/query?question=${encodeURIComponent(question)}`);
      renderResult(data);
    }

    $("questionSelect").addEventListener("change", () => {
      updateSelectedQuestion();
    });
    $("questionSearch").addEventListener("input", renderQuestionCatalog);
    $("categoryFilter").addEventListener("change", renderQuestionCatalog);
    $("customQuestion").addEventListener("input", () => $("customQuestion").setCustomValidity(""));
    $("askButton").addEventListener("click", askCatalogQuestion);
    $("customAskButton").addEventListener("click", askCustomQuestion);

    Promise.all([loadStatus(), loadQuestions(), loadCategories(), loadComparison()])
      .then(askCatalogQuestion)
      .catch((error) => {
        console.error(error);
        $("classicAnswer").textContent = "Die Oberfläche konnte nicht geladen werden.";
        $("graphAnswer").textContent = String(error);
      });
  </script>
</body>
</html>
"""


def serve(port: int = DEFAULT_PORT, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((HOST, port), DashboardHandler)
    url = f"http://{HOST}:{port}/"
    print("Versuchsoberfläche der Bachelorarbeit")
    print(f"- URL: {url}")
    print("- Mit Ctrl+C beenden.")
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


def main() -> None:
    port = DEFAULT_PORT
    open_browser = False
    args = sys.argv[1:]
    if "--open" in args:
        open_browser = True
        args.remove("--open")
    if args:
        port = int(args[0])
    serve(port=port, open_browser=open_browser)


if __name__ == "__main__":
    main()
