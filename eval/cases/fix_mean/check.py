import subprocess
import sys
from pathlib import Path

CHECK_CODE = """
import math
from stats import mean

assert math.isclose(mean([1, 2]), 1.5)
assert math.isclose(mean([1.5, 2.5]), 2.0)
assert math.isclose(mean([-3, 0, 2]), -1 / 3)
assert math.isclose(mean([7]), 7.0)

try:
    mean([])
except ValueError:
    pass
else:
    raise AssertionError("Empty input must raise ValueError")
"""


def check(workspace: Path) -> dict:
    try:
        result = subprocess.run(
            [sys.executable, "-c", CHECK_CODE],
            cwd=workspace,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "reason": "Scoring timed out"}

    return {
        "passed": result.returncode == 0,
        "reason": (
            "All checks passed"
            if result.returncode == 0
            else result.stderr[-2000:]
        ),
    }
