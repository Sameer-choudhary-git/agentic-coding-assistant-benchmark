#!/usr/bin/env python3
"""Print descriptive task-success counts from completed run result JSON files."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
counts = defaultdict(lambda: [0, 0])
for result_file in sorted((ROOT / "runs").glob("*/result.json")):
    try:
        result = json.loads(result_file.read_text(encoding="utf8"))
        task_id = result.get("task_id", "unknown")
        run_file = result_file.parent / "run.json"
        run = json.loads(run_file.read_text(encoding="utf8")) if run_file.exists() else {}
        assistant_id = run.get("assistantId", "unknown")
        key = (assistant_id, task_id)
        counts[key][1] += 1
        counts[key][0] += int(bool(result.get("task_success")))
    except (OSError, json.JSONDecodeError):
        continue
print("assistant_id,task_id,successes,valid_runs,success_rate")
for (assistant_id, task_id), (successes, total) in sorted(counts.items()):
    print(f"{assistant_id},{task_id},{successes},{total},{successes / total:.3f}")
