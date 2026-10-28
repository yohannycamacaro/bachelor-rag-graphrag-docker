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
Die Validierung prueft jetzt auch, ob jede Testfrage eine Referenzantwort fuer
die spaetere manuelle Bewertung besitzt.

## 5. Referenzantworten und Bewertungspaket erzeugen

```powershell
.\run.ps1 reference-answers
```

Dieser Befehl prueft, ob alle 48 Fragen eine Referenzantwort haben, und erzeugt
zwei Dateien im Ordner `results`:

- `reference_answer_report_*.md`: lesbare Liste der Referenzantworten;
- `manual_scoring_template_*.csv`: Vorlage fuer die manuelle Bewertung von
  klassischem RAG und GraphRAG.

Die Bewertung kann spaeter mit der Rubrik in `docs\evaluation_rubric.md`
durchgefuehrt werden.

## 6. Graph-Struktur zeigen

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

## 7. Beispiel vergleichen

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

## 8. Gesamte Auswertung starten

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

## 9. Diagramm erzeugen

```powershell
.\run.ps1 chart
```

Dadurch wird ein Bild fuer die aktuelle Kategorieauswertung erzeugt:

```text
docs\category_comparison_chart.png
```

## 10. Dashboard im Browser starten

```powershell
.\run.ps1 ui
```

Oder direkt mit Browser-Start:

```powershell
.\run.ps1 ui --open
```

Danach im Browser oeffnen:

```text
http://127.0.0.1:8765/
```

Im Dashboard kannst du:

- den Projektstatus sehen;
- eine Frage aus dem Katalog auswaehlen;
- klassisches RAG und GraphRAG nebeneinander vergleichen;
- Evidenzen sehen;
- die Referenzantwort anzeigen;
- den aktuellen Kategorievergleich als Diagramm betrachten.

Zum Beenden im Terminal `Ctrl+C` druecken.

## 11. Kurze muendliche Erklaerung

> Ich vergleiche klassisches RAG und GraphRAG nicht allgemein, sondern anhand
> technischer Troubleshooting-Fragen. Die zentrale Annahme ist, dass GraphRAG
> vor allem bei relationalen und komplexen Fragen Vorteile bringt, weil
> Beziehungen zwischen Problem, Komponente, Ursache, Diagnose und Loesung
> explizit modelliert werden koennen.

## 12. Wichtige Einschraenkung

Die aktuelle Version ist eine retrieval-basierte Voranalyse. Fuer die finale
Bachelorarbeit muss entschieden werden, ob noch ein echtes LLM und LightRAG als
konkrete Implementierung integriert werden oder ob die Arbeit als kontrollierter
Vergleich von klassischem Retrieval und graphbasiertem Retrieval aufgebaut wird.

Neu hinzugefuegt wurde die Evaluationsschicht mit Referenzantworten. Damit ist
der naechste Schritt klarer: Antworten beider Methoden generieren, anhand der
Referenzantworten bewerten und die Ergebnisse nach Fragekategorien auswerten.
