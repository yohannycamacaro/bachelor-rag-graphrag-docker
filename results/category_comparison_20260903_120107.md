# Category comparison: Classic RAG vs GraphRAG

This report groups the experiment by question category. It is an automatic retrieval-level comparison, not yet a final LLM-based evaluation.

| Category | n | Avg. hops | Classic keyword | Graph keyword | Delta | Classic source | Graph source |
|---|---:|---:|---:|---:|---:|---:|---:|
| Konfigurationskonflikt | 8 | 3.00 | 0.487 | 0.519 | 0.031 | 1.000 | 0.875 |
| Einfache Faktenfrage | 8 | 1.00 | 0.521 | 0.677 | 0.156 | 0.938 | 0.875 |
| Multi-Hop-Frage | 8 | 4.00 | 0.263 | 0.481 | 0.219 | 1.000 | 0.875 |
| Prozedurale Frage | 8 | 1.88 | 0.552 | 0.573 | 0.021 | 1.000 | 1.000 |
| Relationale Troubleshooting-Frage | 8 | 2.88 | 0.500 | 0.812 | 0.312 | 1.000 | 1.000 |
| Nachvollziehbarkeit | 8 | 2.88 | 0.506 | 0.769 | 0.263 | 1.000 | 1.000 |

## Interpretation draft

A positive delta means that the graph-based retrieval covered more expected keywords than the classic text-chunk baseline in this question category. For the final thesis, these automatic values should be complemented with manual ratings for correctness, completeness, traceability and consistency.
