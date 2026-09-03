# Neue Richtung nach dem Betreuer:innen-Gespraech vom 03.09.2026

## 1. Kernfeedback aus dem Gespraech

Die Idee ist weiterhin geeignet, aber der konkrete Vergleich muss klarer
formuliert werden. Es soll nicht allgemein gezeigt werden, dass GraphRAG immer
besser ist. Die Arbeit soll untersuchen, bei welchen Arten technischer Fragen
ein graphbasierter Ansatz Vorteile gegenueber klassischem RAG hat.

## 2. Praeziseres Problem

Technische Troubleshooting-Fragen in Dokumentationen, zum Beispiel zu Docker
Compose, bestehen haeufig nicht nur aus einer einzelnen Faktensuche. Oft muss
eine Antwort mehrere Elemente verbinden:

- Fehlermeldung oder Symptom;
- betroffene Komponente;
- moegliche Ursache;
- technische Abhaengigkeit;
- Diagnosemoeglichkeit;
- Loesungsschritt.

Klassisches RAG arbeitet typischerweise mit Text-Chunks und semantischer
Aehnlichkeit. Dadurch kann es relevante Fragmente finden, aber Beziehungen
zwischen Komponenten, Ursachen und Loesungen bleiben oft nur implizit im Text.
GraphRAG macht solche Beziehungen explizit als Knoten und Kanten nutzbar.

## 3. Neuer Arbeitstitel

Kurz und gut praesentierbar:

> Vergleich von klassischem RAG und GraphRAG fuer technische
> Troubleshooting-Fragen: Eine Fallstudie zu Docker Compose

Etwas wissenschaftlicher:

> Vergleich von klassischem RAG und GraphRAG bei relationalen und komplexen
> Troubleshooting-Fragen in technischer Dokumentation anhand einer
> kontrollierten Docker-Compose-Wissensbasis

## 4. Forschungsfrage

> Inwieweit verbessert GraphRAG gegenueber klassischem RAG die Antwortqualitaet
> bei technischen Troubleshooting-Fragen, die relationale Zusammenhaenge
> zwischen Problem, Komponente, Ursache und Loesung erfordern?

## 5. Hypothesen

H1:

> GraphRAG erzielt bei relationalen und komplexen Troubleshooting-Fragen eine
> bessere Antwortqualitaet als klassisches RAG, weil relevante technische
> Beziehungen explizit modelliert und abgerufen werden koennen.

H2:

> Bei einfachen Faktenfragen ist der Unterschied zwischen klassischem RAG und
> GraphRAG geringer, weil die Antwort meist in einem einzelnen Dokumentabschnitt
> enthalten ist.

H0:

> Es gibt keinen relevanten Unterschied in der Antwortqualitaet zwischen
> klassischem RAG und GraphRAG.

## 6. Was genau verglichen wird

Verglichen werden nicht Docker, MCP oder Neo4j als Hauptthemen, sondern zwei
Retrieval-Strategien fuer dieselbe technische Wissensbasis:

1. Klassisches RAG: Dokumente werden in Text-Chunks zerlegt, eingebettet und
   nach semantischer Aehnlichkeit abgerufen.
2. GraphRAG: Wissen wird zusaetzlich als Struktur aus Entitaeten und
   Beziehungen modelliert, zum Beispiel als Pfade von Problem zu Ursache und
   Loesung.

## 7. Fragekategorien fuer die Evaluation

### Kategorie A: Einfache Faktenfragen

Diese Fragen haben meist eine direkte Antwort in einem Dokumentabschnitt.

Beispiel:

> What is the role of DOCKER_HOST in Docker daemon connection problems?

Erwartung:

Klassisches RAG sollte hier bereits gut funktionieren.

### Kategorie B: Prozedurale Fragen

Diese Fragen fragen nach einem konkreten Befehl oder Vorgehen.

Beispiel:

> How can I check which environment values Docker Compose uses for
> interpolation?

Erwartung:

Beide Verfahren koennen funktionieren, wenn der relevante Abschnitt gefunden
wird.

### Kategorie C: Relationale Troubleshooting-Fragen

Diese Fragen erfordern Beziehungen zwischen mehreren technischen Elementen.

Beispiel:

> My app container cannot reach the database container by service name in
> Docker Compose. What should I check?

Erwartung:

GraphRAG sollte Vorteile haben, weil Problem, Netzwerk, Service Discovery,
Container-Port und Loesungsschritte als zusammenhaengender Pfad modelliert
werden koennen.

### Kategorie D: Multi-Hop-Fragen

Diese Fragen brauchen mehrere Denk- oder Suchschritte.

Beispiel:

> Why does my web service start before the database is ready although
> depends_on is configured?

Erwartung:

GraphRAG sollte Vorteile haben, weil `depends_on`, `healthcheck`,
`service_started` und `service_healthy` miteinander verbunden werden muessen.

### Kategorie E: Konfigurationskonflikte

Diese Fragen entstehen, wenn mehrere Regeln oder Konfigurationsquellen
miteinander interagieren.

Beispiel:

> Why does Docker Compose use a different environment variable value than the
> one in my .env file?

Erwartung:

GraphRAG kann helfen, wenn Prioritaeten und Abhaengigkeiten zwischen
`.env`, Shell, `environment`, `env_file` und CLI-Optionen explizit abgebildet
werden.

### Kategorie F: Nachvollziehbarkeitsfragen

Diese Fragen bewerten, ob eine Antwort begruenden kann, warum ein
Loesungsschritt empfohlen wird.

Beispiel:

> Why should another Compose service use db:5432 instead of localhost:8001?

Erwartung:

GraphRAG kann die Antwort besser nachvollziehbar machen, wenn der Pfad
`Service -> Compose network -> service name -> container port` sichtbar wird.

## 8. Sinnvolle Graph-Struktur

Moegliche Knotentypen:

- Problem;
- Komponente;
- Ursache;
- Diagnose;
- Loesung;
- Dokumentationsabschnitt.

Moegliche Beziehungstypen:

- `affects`: Problem betrifft Komponente;
- `may_be_caused_by`: Problem kann verursacht werden durch Ursache;
- `diagnosed_by`: Ursache oder Problem kann geprueft werden durch Diagnose;
- `solved_by`: Ursache kann geloest werden durch Loesung;
- `requires`: Loesung benoetigt technische Voraussetzung;
- `conflicts_with`: Konfiguration steht im Konflikt mit anderer Regel;
- `documented_in`: Knoten oder Beziehung ist in Quelle beschrieben;
- `related_to`: Komponente haengt mit anderer Komponente zusammen.

Die Forschungsfrage ist nicht, wie viele Beziehungen GraphRAG maximal verwalten
kann. Wichtiger ist, ob die modellierten Beziehungen fuer bestimmte
Fragekategorien die Antwortqualitaet messbar verbessern.

## 9. Metriken

Empfohlene Bewertungskriterien:

- Korrektheit;
- Vollstaendigkeit;
- Nachvollziehbarkeit;
- Relevanz der Quellen/Evidenz;
- Konsistenz;
- ggf. Laufzeit oder Retrieval-Aufwand.

Bewertungsskala:

1 = falsch oder kaum brauchbar
2 = teilweise korrekt, aber wichtige Punkte fehlen
3 = grundsaetzlich korrekt, aber nicht vollstaendig
4 = korrekt und weitgehend vollstaendig
5 = sehr gut, vollstaendig und nachvollziehbar begruendet

## 10. Literaturanker

Fuer die Grundlagen von RAG:

- Lewis et al. (2020): Retrieval-Augmented Generation for Knowledge-Intensive
  NLP Tasks.
- Gao et al. (2024): Retrieval-Augmented Generation for Large Language Models:
  A Survey.

Fuer GraphRAG:

- Edge et al. (2024): From Local to Global: A Graph RAG Approach to
  Query-Focused Summarization.
- Graph Retrieval-Augmented Generation: A Survey, ACM Transactions on
  Information Systems.
- Zhang et al. (2025): A Survey of Graph Retrieval-Augmented Generation for
  Customized Large Language Models.

Fuer LightRAG:

- HKUDS LightRAG: Simple and Fast Retrieval-Augmented Generation.

Fuer Evaluation:

- RAGAS-Dokumentation und RAG-Evaluationsliteratur zu correctness,
  faithfulness, context precision und answer relevance.

## 11. Naechste konkrete Schritte

1. Fragenkatalog in die Kategorien A-F aufteilen.
2. Pro Kategorie 5 bis 10 Fragen definieren.
3. Fuer jede Frage eine erwartete Musterantwort und erwartete Keywords
   festlegen.
4. Graph-Struktur erweitern: Problem, Komponente, Ursache, Diagnose, Loesung,
   Quelle.
5. Klassisches RAG und GraphRAG/LightRAG mit derselben Datenbasis testen.
6. Ergebnisse tabellarisch bewerten.
7. In der Arbeit nicht behaupten, dass GraphRAG immer besser ist, sondern klar
   zeigen, bei welchen Fragearten es Vorteile bringt.

## 12. Umgesetzter Stand nach der Ueberarbeitung

Nach dem Feedback wurde der Prototyp in folgenden Punkten erweitert:

- Der Fragenkatalog wurde auf 48 Fragen erweitert.
- Jede der sechs Kategorien enthaelt jetzt 8 Fragen.
- Der technische Fallkatalog wurde von 17 auf 23 Docker-Compose-Faelle
  erweitert.
- Der Wissensgraph enthaelt jetzt 94 Knoten und 119 Relationen.
- Neue Knotentypen und Beziehungstypen machen Diagnose, Voraussetzungen,
  Konflikte und Quellenbezug sichtbarer.
- Die Fragen enthalten eine Herkunftsnotiz, damit erklaert werden kann, dass sie
  manuell aus offizieller Docker-Dokumentation und typischen
  Troubleshooting-Situationen abgeleitet wurden.

Die aktuelle automatische Voranalyse zeigt die groessten Vorteile fuer den
graphbasierten Ansatz bei relationalen Troubleshooting-Fragen,
Nachvollziehbarkeitsfragen und Multi-Hop-Fragen. Bei prozeduralen Fragen und
Konfigurationskonflikten ist der Unterschied kleiner. Das passt zur praeziseren
These, dass GraphRAG nicht immer besser ist, sondern vor allem dann hilft, wenn
technische Beziehungen explizit verbunden werden muessen.
