# Aktueller Projektstand - 03.09.2026

## Thema

Vergleich von klassischem RAG und GraphRAG fuer technische
Troubleshooting-Fragen: Eine Fallstudie zu Docker Compose.

## Problem

Technische Troubleshooting-Fragen in Dokumentationen werden oft nicht durch
eine einzelne Textstelle beantwortet. Haeufig muessen mehrere Informationen
verbunden werden, zum Beispiel:

- Problem oder Symptom;
- betroffene Docker- oder Compose-Komponente;
- moegliche Ursache;
- Diagnosemoeglichkeit;
- Loesungsschritt.

Der zentrale Vergleich ist daher:

- Klassisches RAG: findet relevante Text-Chunks.
- GraphRAG: nutzt zusaetzlich explizite Beziehungen zwischen technischen
  Elementen.

## Forschungsfrage

Inwieweit verbessert GraphRAG gegenueber klassischem RAG die Antwortqualitaet
bei technischen Troubleshooting-Fragen, die relationale Zusammenhaenge zwischen
Problem, Komponente, Ursache, Diagnose und Loesung erfordern?

## Hypothese

GraphRAG erzielt vor allem bei relationalen und komplexen Troubleshooting-
Fragen bessere Ergebnisse als klassisches RAG, weil relevante technische
Beziehungen explizit modelliert und abgerufen werden koennen.

Bei einfachen Faktenfragen oder rein prozeduralen Fragen wird ein geringerer
Unterschied erwartet.

## Aktueller Datenstand

- 12 Quellen aus der Docker-Dokumentation.
- 23 kontrollierte Docker-Support-Faelle.
- 48 Testfragen.
- 6 Fragekategorien mit jeweils 8 Fragen.
- 94 Graph-Knoten.
- 119 Graph-Relationen.

## Fragekategorien

| Kategorie | Anzahl | Erwartete Rolle im Vergleich |
|---|---:|---|
| Einfache Faktenfrage | 8 | Classic RAG sollte oft ausreichen. |
| Prozedurale Frage | 8 | Beide Verfahren koennen funktionieren. |
| Relationale Troubleshooting-Frage | 8 | GraphRAG sollte Vorteile zeigen. |
| Multi-Hop-Frage | 8 | GraphRAG sollte Vorteile zeigen. |
| Konfigurationskonflikt | 8 | GraphRAG kann Abhaengigkeiten sichtbar machen. |
| Nachvollziehbarkeit | 8 | GraphRAG kann Antwortpfade besser erklaeren. |

## Graph-Struktur

Knotentypen:

- problem: 20;
- component: 16;
- cause: 18;
- diagnosis: 11;
- solution: 20;
- document: 9.

Relationstypen:

- affects: 20;
- may_be_caused_by: 18;
- diagnosed_by: 22;
- solved_by: 23;
- requires: 13;
- documented_in: 21;
- conflicts_with: 1;
- distinguished_from: 1.

## Erste automatische Auswertung

Die aktuelle Auswertung ist eine retrieval-basierte Voranalyse. Sie ersetzt
noch keine manuelle Bewertung der finalen Antworten.

| Kategorie | Classic Keyword Coverage | Graph Keyword Coverage | Delta |
|---|---:|---:|---:|
| Konfigurationskonflikt | 0.487 | 0.519 | +0.031 |
| Einfache Faktenfrage | 0.521 | 0.677 | +0.156 |
| Multi-Hop-Frage | 0.263 | 0.481 | +0.219 |
| Prozedurale Frage | 0.552 | 0.573 | +0.021 |
| Relationale Troubleshooting-Frage | 0.500 | 0.812 | +0.312 |
| Nachvollziehbarkeit | 0.506 | 0.769 | +0.263 |

## Vorlaeufige Interpretation

Der graphbasierte Ansatz zeigt die groessten Vorteile bei relationalen
Troubleshooting-Fragen, Nachvollziehbarkeitsfragen und Multi-Hop-Fragen.
Das passt zur Hypothese, weil diese Kategorien mehrere technische
Zusammenhaenge erfordern.

Bei prozeduralen Fragen und Konfigurationskonflikten ist der Vorteil kleiner.
Das ist methodisch wichtig, weil die Arbeit dadurch nicht behauptet, dass
GraphRAG immer besser ist. Stattdessen kann sie untersuchen, bei welchen
Fragetypen ein graphbasierter Ansatz sinnvoll ist und bei welchen Fragetypen
klassisches RAG ausreichen kann.

## Wichtige Befehle

Projektstatus:

```powershell
.\run.ps1 status
```

Fragekategorien anzeigen:

```powershell
.\run.ps1 categories
```

Graph-Statistiken anzeigen:

```powershell
.\run.ps1 graph-stats
```

Eine Frage mit klassischem RAG testen:

```powershell
.\run.ps1 query --method classic --question "Why can my app container not reach the database container by service name?"
```

Dieselbe Frage mit GraphRAG testen:

```powershell
.\run.ps1 query --method graph --question "Why can my app container not reach the database container by service name?"
```

Komplette Vergleichsauswertung:

```powershell
.\run.ps1 compare
```

## Naechste Implementierungsschritte

1. Echte LLM-Antwortgenerierung ergaenzen oder bewusst als optionalen
   Folgeschritt abgrenzen.
2. Entscheiden, ob die finale Implementierung den eigenen kontrollierten
   GraphRAG-Prototyp nutzt oder zusaetzlich LightRAG integriert.
3. Referenzantworten und manuelle Bewertung mit einer 1-bis-5-Skala ergaenzen.
4. Ergebnisse in Tabellen und Diagramme fuer die Bachelorarbeit ueberfuehren.
5. Die Fragekategorien und die Herkunft der Fragen im Methodik-Kapitel
   dokumentieren.
