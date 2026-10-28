# Bewertungsrubrik fuer die finale Evaluation

Stand: 14.09.2026

Diese Rubrik beschreibt, wie die Antworten von klassischem RAG und GraphRAG in
der Bachelorarbeit manuell bewertet werden koennen. Sie ergaenzt die bisherige
automatische Voranalyse mit Keyword-Abdeckung und Quellenabdeckung.

## Ziel

Die finale Evaluation soll nicht nur messen, ob ein System erwartete
Schluesselwoerter findet. Sie soll bewerten, ob die Antwort fuer einen
technischen Support-Fall tatsaechlich brauchbar ist.

## Bewertungsdimensionen

Jede Antwort wird pro Dimension auf einer Skala von 1 bis 5 bewertet.

| Kriterium | Bedeutung |
|---|---|
| Korrektheit | Ist die technische Aussage fachlich richtig? |
| Vollstaendigkeit | Deckt die Antwort die wichtigen Punkte der Referenzantwort ab? |
| Nachvollziehbarkeit | Erklaert die Antwort den Weg von Problem zu Ursache und Loesung? |
| Konsistenz | Widerspricht sich die Antwort nicht und bleibt sie bei der technischen Situation? |
| Quellenbezug | Passt die Antwort zu den relevanten Docker-Quellen und Evidenzen? |

## Skala

| Score | Bedeutung |
|---:|---|
| 1 | falsch, kaum brauchbar oder ohne Bezug zur Frage |
| 2 | teilweise passend, aber wichtige technische Punkte fehlen oder sind unklar |
| 3 | grundsaetzlich korrekt, aber unvollstaendig oder nur teilweise nachvollziehbar |
| 4 | korrekt, weitgehend vollstaendig und technisch brauchbar |
| 5 | sehr gut, vollstaendig, nachvollziehbar und klar mit Evidenz begruendet |

## Rolle der Referenzantworten

Die Datei `data/evaluation/reference_answers.jsonl` enthaelt fuer jede der 48
Testfragen:

- eine Referenzantwort;
- wichtige Mindestinhalte;
- einen Bewertungsschwerpunkt.

Die Referenzantworten sind keine perfekte Musterloesung im Sinne einer einzigen
erlaubten Antwort. Sie dienen als Vergleichsbasis, damit klassische RAG-
Antworten und GraphRAG-Antworten konsistent bewertet werden koennen.

## Wichtige Auswertungslogik

Die zentrale These der Arbeit ist differenziert:

GraphRAG soll nicht pauschal als immer bessere Methode dargestellt werden.
Stattdessen wird geprueft, ob GraphRAG besonders bei relationalen,
mehrstufigen und nachvollziehbarkeitsorientierten Fragen Vorteile zeigt.

Daher sollte die Auswertung nach Kategorien erfolgen:

- Einfache Faktenfrage;
- Prozedurale Frage;
- Relationale Troubleshooting-Frage;
- Multi-Hop-Frage;
- Konfigurationskonflikt;
- Nachvollziehbarkeit.

## Erwartete Interpretation

Wenn GraphRAG vor allem bei relationalen Troubleshooting-Fragen,
Multi-Hop-Fragen und Nachvollziehbarkeitsfragen besser abschneidet, waere das
ein starkes Ergebnis fuer die Forschungsfrage.

Wenn klassisches RAG bei einfachen Faktenfragen oder prozeduralen Fragen
aehnlich gut abschneidet, ist das kein Problem. Im Gegenteil: Es wuerde zeigen,
dass der Nutzen von GraphRAG vom Fragetyp abhaengt.
