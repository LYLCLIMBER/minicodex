import subprocess
import sys
from pathlib import Path


def check(workspace: Path) -> dict:
    for cwd, script in ((workspace, "app/report.py"), (workspace / "app", "report.py")):
        try:
            result = subprocess.run(
                [sys.executable, script],
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            return {"passed": False, "reason": f"Scoring timed out from {cwd}"}

        if result.returncode != 0 or result.stdout.strip() != "total: 17":
            return {
                "passed": False,
                "reason": f"Incorrect result from {cwd}: {result.stdout!r} {result.stderr[-2000:]}",
            }

    return {"passed": True, "reason": "All checks passed"}
