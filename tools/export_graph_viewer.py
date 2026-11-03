from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = PROJECT_ROOT / "data" / "knowledge" / "docker_support_graph.json"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "docker_support_graph_view.html"


HTML_TEMPLATE = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Docker-Support-Wissensgraph</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: light-dark(#f7f9fc, #101418);
      --panel: light-dark(#ffffff, #171d24);
      --text: light-dark(#172033, #edf3fb);
      --muted: light-dark(#5c687a, #9aa7b8);
      --line: light-dark(#ccd6e4, #354252);
      --problem: #d14d44;
      --component: #2f78c4;
      --cause: #b7791f;
      --diagnosis: #6b46c1;
      --solution: #2f855a;
      --document: #64748b;
      --selected: #805ad5;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
    }

    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 340px;
      gap: 16px;
      min-height: 100vh;
      padding: 16px;
    }

    .workspace,
    aside {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }

    .workspace {
      min-width: 0;
      overflow: hidden;
    }

    header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
    }

    h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }

    .stats {
      color: var(--muted);
      font-size: 13px;
    }

    .controls {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px 14px;
      padding: 12px 16px;
      border-bottom: 1px solid var(--line);
    }

    label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
      cursor: pointer;
    }

    input[type="search"] {
      min-width: 260px;
      flex: 1;
      max-width: 460px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--bg);
      color: var(--text);
      font: inherit;
    }

    svg {
      display: block;
      width: 100%;
      height: calc(100vh - 106px);
      min-height: 620px;
    }

    .edge {
      stroke: var(--line);
      stroke-width: 1.4;
      marker-end: url(#arrow);
    }

    .edge-label {
      fill: var(--muted);
      font-size: 11px;
      paint-order: stroke;
      stroke: var(--panel);
      stroke-width: 4px;
    }

    .node circle {
      stroke: var(--panel);
      stroke-width: 2;
      cursor: pointer;
    }

    .node text {
      fill: var(--text);
      font-size: 12px;
      pointer-events: none;
      paint-order: stroke;
      stroke: var(--panel);
      stroke-width: 4px;
    }

    .node.selected circle {
      stroke: var(--selected);
      stroke-width: 4;
    }

    .hidden {
      display: none;
    }

    aside {
      padding: 16px;
      overflow: auto;
      max-height: calc(100vh - 32px);
    }

    aside h2 {
      margin: 0 0 8px;
      font-size: 16px;
      font-weight: 600;
    }

    .pill {
      display: inline-block;
      margin-bottom: 10px;
      padding: 4px 8px;
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
    }

    .detail {
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }

    .edge-list {
      display: grid;
      gap: 10px;
    }

    .edge-card {
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }

    .edge-card strong {
      display: block;
      margin-bottom: 4px;
      font-size: 13px;
    }

    .edge-card p {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    @media (max-width: 900px) {
      main {
        grid-template-columns: 1fr;
      }

      aside {
        max-height: none;
      }

      svg {
        height: 720px;
      }
    }
  </style>
</head>
<body>
  <main>
    <section class="workspace" aria-label="Wissensgraph">
      <header>
        <h1>Docker-Support-Wissensgraph</h1>
        <div class="stats" id="stats"></div>
      </header>
      <div class="controls">
        <input id="search" type="search" placeholder="Knoten, Beschreibung oder Schlüsselwort suchen">
        <label><input type="checkbox" data-type="problem" checked> Probleme</label>
        <label><input type="checkbox" data-type="component" checked> Komponenten</label>
        <label><input type="checkbox" data-type="cause" checked> Ursachen</label>
        <label><input type="checkbox" data-type="diagnosis" checked> Diagnosen</label>
        <label><input type="checkbox" data-type="solution" checked> Lösungen</label>
        <label><input type="checkbox" data-type="document" checked> Dokumente</label>
      </div>
      <svg id="graph" role="img" aria-label="Graph aus Docker-Support-Problemen, Ursachen, Komponenten und Lösungen">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path>
          </marker>
        </defs>
      </svg>
    </section>
    <aside aria-live="polite">
      <h2 id="detail-title">Knoten auswählen</h2>
      <span class="pill" id="detail-type" style="background: var(--muted)">Graph</span>
      <p class="detail" id="detail-text">Klicken Sie auf einen Kreis, um Beschreibung, Schlüsselwörter und verbundene Relationen anzuzeigen.</p>
      <div class="edge-list" id="edge-list"></div>
    </aside>
  </main>

  <script>
    const graph = GRAPH_DATA_PLACEHOLDER;
    const svg = document.getElementById("graph");
    const stats = document.getElementById("stats");
    const search = document.getElementById("search");
    const typeInputs = Array.from(document.querySelectorAll("input[data-type]"));
    const detailTitle = document.getElementById("detail-title");
    const detailType = document.getElementById("detail-type");
    const detailText = document.getElementById("detail-text");
    const edgeList = document.getElementById("edge-list");

    const colors = {
      problem: "var(--problem)",
      component: "var(--component)",
      cause: "var(--cause)",
      diagnosis: "var(--diagnosis)",
      solution: "var(--solution)",
      document: "var(--document)"
    };

    const typeLabels = {
      problem: "Problem",
      component: "Komponente",
      cause: "Ursache",
      diagnosis: "Diagnose",
      solution: "Lösung",
      document: "Dokument"
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

    const order = ["problem", "component", "cause", "diagnosis", "solution", "document"];
    const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
    let selectedId = graph.nodes[0]?.id || null;

    stats.textContent = `${graph.nodes.length} Knoten · ${graph.edges.length} Relationen`;

    function activeTypes() {
      return new Set(typeInputs.filter(input => input.checked).map(input => input.dataset.type));
    }

    function matchesSearch(node) {
      const query = search.value.trim().toLowerCase();
      if (!query) return true;
      const haystack = [
        node.id,
        node.type,
        node.label,
        node.description,
        ...(node.keywords || [])
      ].join(" ").toLowerCase();
      return haystack.includes(query);
    }

    function visibleNodeSet() {
      const types = activeTypes();
      return new Set(
        graph.nodes
          .filter(node => types.has(node.type) && matchesSearch(node))
          .map(node => node.id)
      );
    }

    function layout(width, height, visibleIds) {
      const grouped = new Map(order.map(type => [type, []]));
      for (const node of graph.nodes) {
        if (visibleIds.has(node.id)) grouped.get(node.type)?.push(node);
      }

      const columns = new Map();
      const left = 120;
      const right = Math.max(width - 120, left + 240);
      const step = (right - left) / Math.max(order.length - 1, 1);

      order.forEach((type, index) => {
        columns.set(type, left + step * index);
      });

      const positions = new Map();
      for (const type of order) {
        const nodes = grouped.get(type) || [];
        const gap = height / (nodes.length + 1);
        nodes.forEach((node, index) => {
          positions.set(node.id, {
            x: columns.get(type),
            y: gap * (index + 1)
          });
        });
      }
      return positions;
    }

    function clearSvg() {
      Array.from(svg.querySelectorAll("g")).forEach(group => group.remove());
    }

    function shorten(text, max = 28) {
      return text.length <= max ? text : text.slice(0, max - 1) + "…";
    }

    function render() {
      clearSvg();
      const box = svg.getBoundingClientRect();
      const width = Math.max(box.width, 720);
      const height = Math.max(box.height, 620);
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

      const visibleIds = visibleNodeSet();
      if (!visibleIds.has(selectedId)) {
        selectedId = Array.from(visibleIds)[0] || null;
      }

      const positions = layout(width, height, visibleIds);
      const edges = graph.edges.filter(edge => visibleIds.has(edge.source) && visibleIds.has(edge.target));

      const edgeLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const nodeLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
      svg.append(edgeLayer, nodeLayer);

      for (const edge of edges) {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        if (!source || !target) continue;
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const distance = Math.hypot(dx, dy) || 1;
        const offset = 24;
        const x1 = source.x + dx / distance * offset;
        const y1 = source.y + dy / distance * offset;
        const x2 = target.x - dx / distance * offset;
        const y2 = target.y - dy / distance * offset;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("class", "edge");
        line.setAttribute("x1", x1);
        line.setAttribute("y1", y1);
        line.setAttribute("x2", x2);
        line.setAttribute("y2", y2);
        if (edge.source === selectedId || edge.target === selectedId) {
          line.setAttribute("stroke-width", "2.6");
          line.setAttribute("stroke", "var(--selected)");
        }
        edgeLayer.appendChild(line);

        if (edge.source === selectedId || edge.target === selectedId) {
          const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
          label.setAttribute("class", "edge-label");
          label.setAttribute("x", (x1 + x2) / 2);
          label.setAttribute("y", (y1 + y2) / 2 - 4);
          label.setAttribute("text-anchor", "middle");
          label.textContent = relationLabels[edge.relation] || edge.relation;
          edgeLayer.appendChild(label);
        }
      }

      for (const node of graph.nodes) {
        if (!visibleIds.has(node.id)) continue;
        const pos = positions.get(node.id);
        if (!pos) continue;

        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.setAttribute("class", `node${node.id === selectedId ? " selected" : ""}`);
        group.setAttribute("role", "button");
        group.setAttribute("aria-label", node.label);
        group.addEventListener("click", () => {
          selectedId = node.id;
          render();
          renderDetail();
        });

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", pos.x);
        circle.setAttribute("cy", pos.y);
        circle.setAttribute("r", "20");
        circle.setAttribute("fill", colors[node.type] || "var(--muted)");
        group.appendChild(circle);

        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", pos.x);
        label.setAttribute("y", pos.y + 34);
        label.setAttribute("text-anchor", "middle");
        label.textContent = shorten(node.label);
        group.appendChild(label);

        nodeLayer.appendChild(group);
      }

      renderDetail();
    }

    function renderDetail() {
      const node = selectedId ? nodeById.get(selectedId) : null;
      if (!node) {
        detailTitle.textContent = "Kein Knoten ausgewählt";
        detailType.textContent = "keiner";
        detailType.style.background = "var(--muted)";
        detailText.textContent = "Kein sichtbarer Knoten entspricht den aktuellen Filtern.";
        edgeList.innerHTML = "";
        return;
      }

      detailTitle.textContent = node.label;
      detailType.textContent = typeLabels[node.type] || node.type;
      detailType.style.background = colors[node.type] || "var(--muted)";
      detailText.textContent = `${node.description} Schlüsselwörter: ${(node.keywords || []).join(", ")}`;

      const connected = graph.edges.filter(edge => edge.source === node.id || edge.target === node.id);
      edgeList.innerHTML = "";
      for (const edge of connected) {
        const source = nodeById.get(edge.source);
        const target = nodeById.get(edge.target);
        const card = document.createElement("section");
        card.className = "edge-card";
        const title = document.createElement("strong");
        title.textContent = `${source?.label || edge.source} · ${relationLabels[edge.relation] || edge.relation} · ${target?.label || edge.target}`;
        const text = document.createElement("p");
        text.textContent = `${edge.evidence} Quellen: ${(edge.source_ids || []).join(", ")}`;
        card.append(title, text);
        edgeList.appendChild(card);
      }
    }

    search.addEventListener("input", render);
    typeInputs.forEach(input => input.addEventListener("change", render));
    window.addEventListener("resize", render);
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    graph_json = json.dumps(graph, ensure_ascii=False, indent=2)
    html = HTML_TEMPLATE.replace("GRAPH_DATA_PLACEHOLDER", graph_json)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Graphansicht geschrieben nach: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
