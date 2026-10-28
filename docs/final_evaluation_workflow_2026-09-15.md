# Workflow fuer die finale Evaluation

Stand: 15.09.2026

Dieses Dokument beschreibt den aktuellen naechsten Schritt des Projekts: aus
den Retrieval-Ergebnissen werden Kandidatenantworten erzeugt, die danach
manuell bewertet werden koennen.

## Warum dieser Schritt wichtig ist

Die bisherigen Vergleichswerte messen vor allem, welche erwarteten Begriffe und
Quellen durch klassisches RAG und GraphRAG abgedeckt werden. Fuer die
Bachelorarbeit reicht das allein noch nicht aus. Die finale Untersuchung muss
auch zeigen, wie gut die Antworten fuer einen technischen Support-Kontext
wirklich sind.

Deshalb erzeugt der Prototyp jetzt fuer jede Frage zwei Kandidatenantworten:

- eine Antwort auf Basis des klassischen dokumentenbasierten Retrievals;
- eine Antwort auf Basis des graphbasierten Retrievals.

Beide Antworten werden zusammen mit Referenzantwort, Mindestinhalten,
Bewertungsschwerpunkt und Evidenz exportiert.

## Neuer Befehl

```powershell
.\run.ps1 candidate-answers
```

Der Befehl erzeugt:

- eine CSV-Datei fuer die manuelle Bewertung;
- eine Markdown-Datei zum Lesen und Vergleichen der Antworten.

Optional kann der Umfang eingeschraenkt werden:

```powershell
.\run.ps1 candidate-answers --limit 6
.\run.ps1 candidate-answers --category relational_troubleshooting
.\run.ps1 candidate-answers --method graph
```

## Aktueller Output

Aktuell werden 48 Fragen mit zwei Methoden ausgewertet. Dadurch entstehen 96
Kandidatenantworten:

- 48 Antworten fuer klassisches RAG;
- 48 Antworten fuer GraphRAG.

Die aktuelle Datei fuer die manuelle Bewertung ist:

`results/candidate_answers_20260915_125921.csv`

Die lesbare Markdown-Version ist:

`results/candidate_answers_20260915_125921.md`

## Bewertungsdimensionen

Die manuelle Bewertung soll mit einer Skala von 1 bis 5 erfolgen:

| Kriterium | Bedeutung |
|---|---|
| Korrektheit | Ist die technische Aussage richtig? |
| Vollstaendigkeit | Werden die wichtigsten Aspekte der Referenzantwort abgedeckt? |
| Nachvollziehbarkeit | Ist der Weg von Problem zu Ursache und Loesung erkennbar? |
| Konsistenz | Widerspricht sich die Antwort nicht? |
| Quellenbezug | Passt die Evidenz zu den relevanten Quellen? |
| Gesamtbewertung | Gesamteindruck der Antwortqualitaet |

## Wie Yohanny damit weiterarbeitet

1. Die CSV-Datei oeffnen.
2. Pro Frage zuerst die Referenzantwort lesen.
3. Dann die Antwort von `classic` bewerten.
4. Danach die Antwort von `graph` bewerten.
5. Notizen eintragen, wenn eine Antwort falsche oder irrelevante Evidenz
   enthaelt.
6. Am Ende Mittelwerte pro Kategorie berechnen.

## Warum das wissenschaftlich besser ist

Dieser Schritt verhindert, dass die Arbeit nur anhand von Keyword-Treffern
argumentiert. Die automatische Voranalyse bleibt hilfreich, aber die manuelle
Bewertung prueft naeher an der eigentlichen Forschungsfrage, ob die Antworten
fuer einen technischen Support-Fall wirklich nuetzlich sind.

## Aktuelle Vergleichswerte nach dem Retrieval-Update

Stand: `results/category_comparison_20260915_125921.md`

| Kategorie | Klassisches RAG | GraphRAG | Delta |
|---|---:|---:|---:|
| Relationale Troubleshooting-Frage | 0,500 | 0,938 | +0,438 |
| Multi-Hop-Frage | 0,263 | 0,569 | +0,306 |
| Nachvollziehbarkeit | 0,600 | 0,825 | +0,225 |
| Einfache Faktenfrage | 0,521 | 0,656 | +0,135 |
| Konfigurationskonflikt | 0,487 | 0,575 | +0,087 |
| Prozedurale Frage | 0,552 | 0,604 | +0,052 |

## Interpretation fuer die Thesis

Die neuen Werte stuetzen weiterhin eine differenzierte Hypothese. GraphRAG
zeigt den groessten Vorteil bei relationalen Troubleshooting-Fragen,
Multi-Hop-Fragen und Nachvollziehbarkeit. Bei prozeduralen Fragen bleibt der
Vorteil sehr klein. Genau daraus kann spaeter argumentiert werden, dass ein
Graphansatz vor allem dann nuetzlich ist, wenn technische Beziehungen explizit
modelliert und abgerufen werden muessen.
