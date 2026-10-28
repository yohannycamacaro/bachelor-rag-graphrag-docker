# Curated final results

This directory contains the compact result set required to inspect the thesis findings without publishing raw evaluator traces.

- `main_metrics_by_category.csv`: 48-question main evaluation.
- `challenge_metrics_by_category.csv`: 12 difficult questions, two per category.
- `holdout_metrics_by_category.csv`: 12 unseen questions, two per category.
- `manual_vs_ragchecker_by_category.csv`: qualitative cross-check against automated metrics.
- `evaluation_metadata.json`: evaluator versions, parameters, token use and cost.

All values originate from the corresponding generated files under `results/`. The raw and intermediate files are excluded from the release repository to keep it reviewable.

