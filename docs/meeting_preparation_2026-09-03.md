# Vorbereitung fuer das Treffen am 03.09.2026

Dieses Dokument sammelt die Punkte vom Dienstag, 25.08.2026, und Mittwoch,
26.08.2026, damit der aktuelle Arbeitsstand klar praesentiert werden kann.

## 1. Aktueller Arbeitstitel

Deutsch:

> Vergleich von klassischem RAG und GraphRAG bei relationalen und komplexen
> Troubleshooting-Fragen in technischer Dokumentation anhand einer
> kontrollierten Docker-Compose-Wissensbasis.

Spanisch:

> Comparacion entre RAG clasico y GraphRAG para preguntas relacionales y
> complejas de troubleshooting tecnico usando una base controlada de Docker
> Compose.

## 2. Konkretes Problem

Deutsch:

Technische Support-Anfragen zu Docker bestehen oft nicht nur aus einer einfachen
Faktensuche. Viele Fragen verbinden mehrere Elemente: Fehlermeldung,
betroffene Komponente, moegliche Ursache, Diagnose und Loesungsschritt.

Spanisch:

Las preguntas de soporte tecnico sobre Docker muchas veces no se responden con
un solo fragmento de texto. Para responder bien hay que conectar error,
componente afectado, causa posible, diagnostico y solucion.

## 3. Forschungsfrage

Kurze Version:

> Verbessert GraphRAG gegenueber klassischem RAG die Antwortqualitaet bei
> komplexen Docker-Compose-Troubleshooting-Fragen?

Praezisere Version:

> Inwieweit verbessert GraphRAG gegenueber klassischem RAG die
> Antwortqualitaet bei technischen Troubleshooting-Fragen, die relationale
> Zusammenhaenge zwischen Problem, Komponente, Ursache, Diagnose und Loesung
> erfordern?

## 4. Abgrenzung des Scopes

Im Projekt werden nur ausgewaehlte Bereiche aus der offiziellen
Docker-Dokumentation verwendet:

- Docker daemon troubleshooting;
- Docker Compose networking;
- Docker Compose environment variables;
- Docker Compose variable interpolation and precedence;
- Docker storage and volumes;
- Docker Compose startup order and healthchecks.

Nicht im Scope:

- MCP;
- Neo4j als eigenes Hauptthema;
- LightRAG als verpflichtendes Hauptthema;
- Datenschutzkritische Studiendaten;
- ein vollstaendiges Produktivsystem;
- alle Docker-Funktionen.

## 5. Datenbasis

Als Datenbasis wird eine kleine, kontrollierte technische Wissensbasis erstellt.
Die Inhalte werden aus offizieller Docker-Dokumentation abgeleitet und in
eigene Worte ueberfuehrt.

Struktur pro Fall:

- Problem;
- betroffene Komponente;
- typische Ursachen;
- Diagnose;
- erwartete Loesung;
- Quellen.

## 6. Bisheriger Projektstand

Bereits angelegt:

- Mini-Wissensbasis in `data/raw/docker_support_notes.md`;
- Quellenliste in `data/sources.json` mit 12 offiziellen Docker-Quellen;
- graphartige Wissensstruktur in `data/knowledge/docker_support_graph.json`;
- Fragenkatalog in `data/questions/docker_support_questions.jsonl` mit 48 Testfragen;
- Fallkatalog in `docs/docker_case_catalog.md` mit 23 technischen Support-Faellen;
- Methodiknotiz zur Herkunft der Fragen in `docs/question_design_methodology.md`;
- 94 Graph-Knoten und 119 Graph-Relationen;
- erstes Vergleichsskript fuer Classic Retrieval vs Graph Retrieval;
- Plan fuer die acht Wochen.

## 7. Was am 03.09. gezeigt werden kann

- Thema und Motivation;
- konkrete Forschungsfrage;
- Scope und Quellen;
- Beispiel: Docker Compose service discovery;
- Beispiel: `.env` variable ist nicht im Container sichtbar;
- erster Prototyp mit zwei Retrieval-Varianten;
- naechste Schritte bis zur offiziellen Anmeldung.

## 8. Fragen an die Professorin

1. Ist der Anwendungsfall "technische Support-Wissensbasis zu Docker" konkret
   genug fuer die Bachelorarbeit?
2. Ist die Forschungsfrage ausreichend eingegrenzt?
3. Ist es sinnvoll, Classic RAG und GraphRAG anhand einfacher und relationaler
   Supportfragen zu vergleichen?
4. Reicht eine manuelle Bewertung mit 48 Testfragen und klaren Kriterien
   fuer den Umfang einer Bachelorarbeit aus?
5. Sollte die Implementierung eher als Proof of Concept oder als systematisches
   Evaluationssetup im Fokus stehen?

## 9. Satz fuer die muendliche Erklaerung

> Ich moechte nicht allgemein zeigen, dass GraphRAG immer besser ist. Stattdessen
> moechte ich untersuchen, bei welchen technischen Supportfragen ein
> graphbasierter Ansatz gegenueber klassischem RAG Vorteile bringt, insbesondere
> wenn mehrere technische Zusammenhaenge fuer die Antwort kombiniert werden
> muessen.
