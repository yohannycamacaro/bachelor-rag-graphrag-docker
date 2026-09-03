# Kategorievergleich: Klassisches RAG vs GraphRAG

Dieser Bericht gruppiert die Auswertung nach Fragetypen. Es handelt sich um eine automatische retrieval-basierte Voranalyse, noch nicht um die finale LLM-basierte Evaluation.

| Kategorie | n | Ø Hops | Classic Keyword | Graph Keyword | Delta | Classic Source | Graph Source | Ø Graph-Relationen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Konfigurationskonflikt | 8 | 3.00 | 0.487 | 0.519 | 0.031 | 1.000 | 0.875 | 6.000 |
| Einfache Faktenfrage | 8 | 1.00 | 0.521 | 0.677 | 0.156 | 0.938 | 0.875 | 6.000 |
| Multi-Hop-Frage | 8 | 4.00 | 0.263 | 0.481 | 0.219 | 1.000 | 0.875 | 5.625 |
| Prozedurale Frage | 8 | 1.88 | 0.552 | 0.573 | 0.021 | 1.000 | 1.000 | 6.000 |
| Relationale Troubleshooting-Frage | 8 | 2.88 | 0.500 | 0.812 | 0.312 | 1.000 | 1.000 | 5.750 |
| Nachvollziehbarkeit | 8 | 2.88 | 0.506 | 0.769 | 0.263 | 1.000 | 1.000 | 5.625 |

## Interpretationsentwurf

Ein positiver Delta-Wert bedeutet, dass das graphbasierte Retrieval in dieser Kategorie mehr erwartete Schluesselbegriffe abgedeckt hat als die klassische Text-Chunk-Baseline. Die Spalte Ø Graph-Relationen zeigt, wie viele explizite Beziehungen der GraphRAG-Prototyp im Durchschnitt pro Frage verwendet hat. Fuer die finale Bachelorarbeit muessen diese automatischen Werte durch manuelle Bewertungen fuer Korrektheit, Vollstaendigkeit, Nachvollziehbarkeit und Konsistenz ergaenzt werden.
