# Arbeitsstand fuer Betreuer:innen - 14.09.2026

## Thema

Vergleich von klassischem RAG und GraphRAG bei relationalen und komplexen
Troubleshooting-Fragen in technischer Dokumentation anhand einer kontrollierten
Docker-Compose-Wissensbasis.

## Aktuelle Forschungsfrage

Inwieweit verbessert GraphRAG gegenueber klassischem RAG die Antwortqualitaet
bei technischen Troubleshooting-Fragen, die relationale Zusammenhaenge zwischen
Problem, Komponente, Ursache, Diagnose und Loesung erfordern?

## Konkretisierung des Problems

Der Vergleich wurde nach dem Betreuer:innen-Gespraech staerker auf einen
konkreten Anwendungsfall eingegrenzt. Im Mittelpunkt stehen nicht allgemeine
Fragen zu RAG, sondern technische Troubleshooting-Fragen zu Docker Compose.
Diese Fragen sind oft relational, weil fuer eine brauchbare Antwort mehrere
Elemente verbunden werden muessen:

- Problem oder Fehlersymptom;
- betroffene Docker- oder Compose-Komponente;
- moegliche Ursache;
- Diagnosemoeglichkeit;
- Loesungsschritt;
- Quelle in der technischen Dokumentation.

Die zentrale Annahme ist, dass klassisches RAG bei einfachen Faktenfragen
ausreichen kann, waehrend GraphRAG vor allem bei relationalen, mehrstufigen und
nachvollziehbarkeitsorientierten Fragen Vorteile haben koennte.

## Bisheriger Prototyp

Der aktuelle Prototyp ist noch kein finales produktives RAG-System, sondern ein
kontrolliertes Evaluationssetup zur Vorbereitung der Bachelorarbeit.

Aktueller Stand:

- 12 registrierte Docker-Dokumentationsquellen;
- 23 kontrollierte Docker-Compose-Troubleshooting-Faelle;
- 48 Testfragen;
- 6 Fragekategorien mit jeweils 8 Fragen;
- 94 Graph-Knoten;
- 119 Graph-Relationen;
- automatische Validierung von Fragen, Quellen und Graph-Referenzen;
- automatische Vergleichsauswertung nach Fragekategorien;
- visuelle HTML-Ansicht des Wissensgraphen;
- Diagramm zur Voranalyse der Kategorien.

## Fragekategorien

| Kategorie | Anzahl | Zweck |
|---|---:|---|
| Einfache Faktenfrage | 8 | Prueft, ob klassisches RAG bei direkten Fragen ausreicht. |
| Prozedurale Frage | 8 | Prueft Fragen nach konkreten Befehlen oder Vorgehensweisen. |
| Relationale Troubleshooting-Frage | 8 | Prueft, ob Beziehungen zwischen Problem, Komponente, Ursache und Loesung helfen. |
| Multi-Hop-Frage | 8 | Prueft Fragen mit mehreren Such- oder Argumentationsschritten. |
| Konfigurationskonflikt | 8 | Prueft Interaktionen zwischen Regeln oder Konfigurationsquellen. |
| Nachvollziehbarkeit | 8 | Prueft, ob Antwortpfade und Quellen besser begruendet werden koennen. |

## Herkunft der Fragen

Die Fragen wurden nicht aus einem fertigen Benchmark uebernommen. Sie wurden
manuell aus typischen Troubleshooting-Situationen abgeleitet, die in der
offiziellen Docker-Dokumentation beschrieben werden. Jede Frage enthaelt
erwartete Schluesselbegriffe, relevante Quellen-IDs und eine Herkunftsnotiz.

Verwendete Bereiche der Dokumentation:

- Docker daemon troubleshooting;
- Docker Compose networking;
- Docker Compose startup order;
- Docker Compose environment variable interpolation;
- Docker Compose environment variable precedence;
- Docker Compose predefined variables;
- Docker Compose services reference;
- Docker storage and volumes;
- Docker Compose volumes reference.

## Bisherige Voranalyse

Die bisherige Auswertung ist retrieval-basiert. Sie bewertet also noch nicht die
finale Qualitaet vollstaendig generierter LLM-Antworten, sondern vergleicht, wie
gut die beiden Retrieval-Varianten erwartete Schluesselbegriffe und Quellen
abdecken.

| Kategorie | Classic Keyword | Graph Keyword | Delta |
|---|---:|---:|---:|
| Relationale Troubleshooting-Frage | 0,500 | 0,812 | +0,312 |
| Nachvollziehbarkeit | 0,506 | 0,769 | +0,263 |
| Multi-Hop-Frage | 0,263 | 0,481 | +0,219 |
| Einfache Faktenfrage | 0,521 | 0,677 | +0,156 |
| Konfigurationskonflikt | 0,487 | 0,519 | +0,031 |
| Prozedurale Frage | 0,552 | 0,573 | +0,021 |

## Vorlaeufige Interpretation

Die bisherigen Ergebnisse sprechen dafuer, dass der graphbasierte Ansatz vor
allem bei relationalen Troubleshooting-Fragen, Nachvollziehbarkeitsfragen und
Multi-Hop-Fragen Vorteile zeigen kann. Bei prozeduralen Fragen und
Konfigurationskonflikten ist der Unterschied aktuell deutlich kleiner.

Das ist fuer die Arbeit hilfreich, weil die Hypothese dadurch differenzierter
formuliert werden kann: GraphRAG soll nicht pauschal als bessere Methode
dargestellt werden, sondern als Ansatz, der besonders dann Mehrwert bringen
koennte, wenn technische Beziehungen explizit modelliert und abgerufen werden
muessen.

## Naechste Schritte

1. Literaturrecherche zu RAG, GraphRAG, LightRAG und RAG-Evaluation weiter
   vertiefen.
2. Final entscheiden, ob die Implementierung bei einem kontrollierten
   GraphRAG-Prototyp bleibt oder zusaetzlich LightRAG als konkretes Framework
   integriert wird.
3. Referenzantworten fuer die 48 Fragen erstellen.
4. LLM-basierte Antwortgenerierung ergaenzen oder klar abgrenzen.
5. Manuelle Bewertung mit Skala 1 bis 5 fuer Korrektheit, Vollstaendigkeit,
   Nachvollziehbarkeit und Konsistenz durchfuehren.
6. Ergebnisse in Tabellen und Diagramme fuer die Bachelorarbeit ueberfuehren.

## Offene Fragen an die Betreuer:innen

1. Ist die Forschungsfrage in dieser Form ausreichend konkret eingegrenzt?
2. Ist Docker Compose als kontrollierte technische Troubleshooting-Domaene fuer
   die Bachelorarbeit geeignet?
3. Soll der Fokus eher auf dem systematischen Vergleich des kontrollierten
   Prototyps liegen, oder soll zwingend ein bestehendes Framework wie LightRAG
   integriert werden?
4. Reichen 48 Fragen mit sechs Kategorien und manueller Bewertung fuer den
   Umfang einer Bachelorarbeit aus?
5. Welche Bewertungskriterien sollten fuer die finale Auswertung priorisiert
   werden?
