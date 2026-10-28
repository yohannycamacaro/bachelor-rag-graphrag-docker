from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "results" / "automatic_evaluation"
FULL = AUTO / "resultados_finales_classic_48.json"
REPAIR = AUTO / "ragchecker_classic_repair_6_results.json"
BACKUP = AUTO / "resultados_finales_classic_48_before_excel_repair.json"
METRICS = ("precision", "recall", "f1")


def main() -> None:
    full = json.loads(FULL.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    if not BACKUP.exists():
        shutil.copy2(FULL, BACKUP)

    repaired = {str(item["query_id"]): item for item in repair["results"]}
    if len(repaired) != 6:
        raise ValueError(f"Expected six repaired results, found {len(repaired)}")
    full["results"] = [repaired.get(str(item["query_id"]), item) for item in full["results"]]
    if len(full["results"]) != 48:
        raise ValueError("The merged full result must contain 48 entries")

    overall = {}
    for metric in METRICS:
        mean = sum(float(item["metrics"][metric]) for item in full["results"]) / len(full["results"])
        overall[metric] = round(mean * 100, 1)
    full.setdefault("metrics", {})["overall_metrics"] = overall

    old_meta = full.get("evaluation_metadata", {})
    repair_meta = repair.get("evaluation_metadata", {})
    merged_cost = float(old_meta.get("estimated_openai_cost_usd") or 0) + float(
        repair_meta.get("estimated_openai_cost_usd") or 0
    )
    full["evaluation_metadata"] = {
        **old_meta,
        "repair_evaluation": {
            "reason": "Six Classic RAG responses were restored after spreadsheet formula corruption.",
            "query_ids": sorted(repaired),
            "requests": repair_meta.get("requests"),
            "input_tokens": repair_meta.get("input_tokens"),
            "output_tokens": repair_meta.get("output_tokens"),
            "estimated_openai_cost_usd": repair_meta.get("estimated_openai_cost_usd"),
            "merged_at": datetime.now().isoformat(timespec="seconds"),
        },
        "estimated_openai_cost_usd_including_repair": merged_cost,
    }
    FULL.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Repaired IDs: {', '.join(sorted(repaired))}")
    print(f"Updated overall metrics: {overall}")
    print(f"Additional repair cost: ${float(repair_meta.get('estimated_openai_cost_usd') or 0):.4f}")
    print(f"Classic total including repair: ${merged_cost:.4f}")
    print(FULL)


if __name__ == "__main__":
    main()
