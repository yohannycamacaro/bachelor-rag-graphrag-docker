# Release candidate summary

## Included

- reproducible classic-RAG and GraphRAG retrieval;
- main, challenge and holdout evaluation sets;
- complete reference answers and source assignments;
- automated dataset and graph validation;
- curated category-level RAGChecker results;
- qualitative manual cross-check;
- evaluator configuration, token use and cost.

## Central finding

GraphRAG is not universally superior. Classic RAG has the higher global F1 score in all three evaluation sets, while GraphRAG retrieves a larger share of relevant reference information. GraphRAG is particularly useful when evidence follows explicit relational or traceability chains. The findings therefore favour question-dependent method selection or a hybrid design rather than a universal winner.

