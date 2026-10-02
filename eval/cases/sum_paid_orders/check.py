import json
import subprocess
import sys
from pathlib import Path


def check(workspace: Path) -> dict:
    try:
        result = subprocess.run(
            [sys.executable, "aggregate.py"],
            cwd=workspace,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "reason": "Scoring timed out"}

    if result.returncode != 0:
        return {"passed": False, "reason": result.stderr[-2000:]}

    try:
        summary = json.loads((workspace / "summary.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"passed": False, "reason": f"Cannot read valid summary.json: {exc}"}

    valid = (
        isinstance(summary, dict)
        and type(summary.get("paid_order_count")) is int
        and summary["paid_order_count"] == 3
        and type(summary.get("total_amount")) in (int, float)
        and summary["total_amount"] == 235
    )
    return {
        "passed": valid,
        "reason": "All checks passed" if valid else f"Incorrect summary: {summary!r}",
    }
