# Methodik des Fragenkatalogs

Stand: 03.09.2026

## Ziel

Der Fragenkatalog dient dazu, klassisches RAG und GraphRAG nicht nur allgemein,
sondern nach konkreten Fragetypen zu vergleichen. Damit reagiert das Projekt auf
das Feedback der Betreuer:innen: Die Arbeit soll klarer zeigen, bei welchem
praktischen Problem GraphRAG einen Vorteil bringen kann.

## Herkunft der Fragen

Die Fragen wurden nicht aus einem fertigen Benchmark heruntergeladen. Sie wurden
manuell aus typischen Troubleshooting-Situationen abgeleitet, die in der
offiziellen Docker-Dokumentation beschrieben werden.

Verwendete Dokumentationsbereiche:

- Docker daemon troubleshooting;
- Docker Compose networking;
- Docker Compose startup order;
- Docker Compose environment variable interpolation;
- Docker Compose environment variable precedence;
- Docker Compose predefined variables;
- Docker Compose services reference;
- Docker storage and volumes;
- Docker Compose volumes reference.

Jede Frage enthaelt:

- eine eindeutige ID;
- eine englische Frage;
- eine deutsche Frage;
- eine Kategorie;
- eine Schwierigkeit;
- erwartete Schluesselbegriffe;
- relevante Quellen-IDs;
- eine kurze Notiz zur Herkunft.

## Warum Kategorien?

Die Kategorien verhindern, dass die Arbeit nur eine globale Aussage macht wie
"GraphRAG ist besser". Stattdessen kann die Bachelorarbeit zeigen, bei welchen
Fragetypen ein graphbasierter Ansatz sinnvoll ist und bei welchen Fragetypen
klassisches RAG ausreichen kann.

Aktuelle Kategorien:

| Kategorie | Anzahl | Idee |
|---|---:|---|
| Einfache Faktenfrage | 8 | Direkte Antwort, oft in einem Dokumentabschnitt enthalten. |
| Prozedurale Frage | 8 | Frage nach Befehl oder Vorgehen. |
| Relationale Troubleshooting-Frage | 8 | Problem, Komponente, Ursache und Loesung muessen verbunden werden. |
| Multi-Hop-Frage | 8 | Mehrere Such- oder Denkschritte sind notwendig. |
| Konfigurationskonflikt | 8 | Mehrere Regeln oder Konfigurationsquellen interagieren. |
| Nachvollziehbarkeit | 8 | Die Antwort soll begruenden, warum eine Loesung gilt. |

## Warum Docker Compose?

Docker Compose eignet sich als kontrollierter technischer Anwendungsfall, weil
viele reale Support-Probleme relational sind. Beispiele:

- Ein Service erreicht einen anderen nur, wenn beide in einer gemeinsamen
  Netzwerkstruktur liegen.
- Host-Port und Container-Port haben unterschiedliche Bedeutungen.
- `depends_on` beschreibt Startreihenfolge, aber nicht automatisch
  Dienstbereitschaft.
- `.env`-Werte fuer Interpolation sind nicht automatisch Runtime-Variablen im
  Container.
- Environment-Variablen koennen aus mehreren Quellen kommen und nach Prioritaet
  ueberschrieben werden.
- Volumes, Bind Mounts und tmpfs haben unterschiedliche Persistenz-Eigenschaften.

## Warum koennte GraphRAG helfen?

Klassisches RAG sucht passende Textabschnitte. GraphRAG kann zusaetzlich
explizite Beziehungen nutzen, zum Beispiel:

`Problem -> Komponente -> Ursache -> Diagnose -> Loesung -> Quelle`

Dadurch ist GraphRAG besonders interessant fuer Fragen, bei denen die Antwort
nicht nur ein einzelner Fakt ist, sondern eine Kette technischer Zusammenhaenge.

## Aktuelle Wissensgraph-Struktur

Knotentypen:

- `problem`;
- `component`;
- `cause`;
- `diagnosis`;
- `solution`;
- `document`.

Relationstypen:

- `affects`: Ein Problem betrifft eine Komponente.
- `may_be_caused_by`: Ein Problem kann durch eine Ursache entstehen.
- `diagnosed_by`: Ein Problem oder eine Ursache kann durch einen Schritt
  geprueft werden.
- `solved_by`: Eine Ursache oder ein Problem kann durch eine Loesung behoben
  werden.
- `requires`: Eine Loesung oder Diagnose benoetigt eine technische Voraussetzung.
- `conflicts_with`: Zwei Erklaerungen oder Konfigurationen koennen miteinander
  in Konflikt stehen.
- `distinguished_from`: Zwei Konzepte muessen voneinander unterschieden werden.
- `documented_in`: Ein Wissenselement ist in einer Quelle dokumentiert.

## Verwendung in der Bachelorarbeit

Diese Datei kann spaeter in der Methodik verwendet werden, um zu erklaeren:

1. warum der Datensatz klein und kontrolliert ist;
2. warum die Fragen manuell erstellt wurden;
3. warum die Kategorien wichtig sind;
4. wie die Quellenbindung hergestellt wurde;
5. warum die Evaluation nicht nur global, sondern nach Fragetypen erfolgt.
