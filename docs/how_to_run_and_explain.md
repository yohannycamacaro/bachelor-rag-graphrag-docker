# Kurzguide: Projekt ausfuehren und erklaeren

## 1. Projekt oeffnen

Oeffne diese Projektmappe entweder in VS Code oder direkt im Windows Explorer
mit PowerShell:

```text
bachelor_rag_project
```

Die Befehle werden im Terminal aus dieser Mappe ausgefuehrt.

## 2. Status zeigen

```powershell
.\run.ps1 status
```

Damit zeigst du:

- Anzahl der Quellen;
- Anzahl der Docker-Support-Faelle;
- Anzahl der Testfragen;
- Fragekategorien;
- Anzahl der Graph-Knoten und Graph-Relationen.

## 3. Fragekategorien zeigen

```powershell
.\run.ps1 categories
```

Damit kannst du erklaeren, dass die Evaluation nicht nur allgemein vergleicht,
sondern zwischen einfachen, prozeduralen, relationalen und komplexeren Fragen
unterscheidet.

## 4. Dataset validieren

```powershell
.\run.ps1 validate
```

Damit zeigst du, dass Fragen, Quellen und Graph-Relationen konsistent sind.
Das ist hilfreich, wenn gefragt wird, ob der Fragenkatalog sauber aufgebaut ist.

## 5. Graph-Struktur zeigen

```powershell
.\run.ps1 graph-stats
```

Aktuell enthaelt der Graph:

- 94 Knoten;
- 119 Relationen;
- 6 Knotentypen: problem, component, cause, diagnosis, solution, document;
- 8 Relationstypen: affects, may_be_caused_by, diagnosed_by, solved_by,
  requires, documented_in, conflicts_with, distinguished_from.

Die Datei fuer die visuelle Ansicht liegt hier:

```text
docs\docker_support_graph_view.html
```

## 6. Beispiel vergleichen

Klassisches RAG:

```powershell
.\run.ps1 query --method classic --question "Why can my app container not reach the database container by service name?"
```

GraphRAG:

```powershell
.\run.ps1 query --method graph --question "Why can my app container not reach the database container by service name? What should I check?"
```

Erklaerung:

Klassisches RAG findet passende Textabschnitte. GraphRAG zeigt zusaetzlich
explizite Beziehungen, zum Beispiel:

```text
problem -> cause -> diagnosis -> solution
```

## 7. Gesamte Auswertung starten

```powershell
.\run.ps1 compare
```

Danach entstehen Dateien im Ordner:

```text
results
```

Wichtig sind besonders:

- `comparison_summary_*.csv`: Ergebnisse pro Frage und Methode.
- `category_comparison_*.csv`: Zusammenfassung pro Fragekategorie.
- `category_comparison_*.md`: lesbarer Bericht pro Kategorie.

Aktuelle Tendenz der Voranalyse:

- groesste Vorteile fuer GraphRAG bei relationalen Troubleshooting-Fragen;
- deutliche Vorteile bei Nachvollziehbarkeit und Multi-Hop-Fragen;
- kleine Unterschiede bei prozeduralen Fragen und Konfigurationskonflikten.

## 8. Kurze muendliche Erklaerung

> Ich vergleiche klassisches RAG und GraphRAG nicht allgemein, sondern anhand
> technischer Troubleshooting-Fragen. Die zentrale Annahme ist, dass GraphRAG
> vor allem bei relationalen und komplexen Fragen Vorteile bringt, weil
> Beziehungen zwischen Problem, Komponente, Ursache, Diagnose und Loesung
> explizit modelliert werden koennen.

## 9. Wichtige Einschraenkung

Die aktuelle Version ist eine retrieval-basierte Voranalyse. Fuer die finale
Bachelorarbeit muss entschieden werden, ob noch ein echtes LLM und LightRAG als
konkrete Implementierung integriert werden oder ob die Arbeit als kontrollierter
Vergleich von klassischem Retrieval und graphbasiertem Retrieval aufgebaut wird.
