import subprocess
import sys
from pathlib import Path

CHECK_CODE = """
from dedupe import dedupe

items = [3, 1, 3, 2, 1, 4]
assert dedupe(items) == [3, 1, 2, 4]
assert items == [3, 1, 3, 2, 1, 4]
assert dedupe([]) == []
assert dedupe(["a", "a", "b", "a"]) == ["a", "b"]
assert dedupe([7, 7, 7]) == [7]
assert dedupe([5]) == [5]

unhashable = [{"id": 1}, {"id": 2}, {"id": 1}]
assert dedupe(unhashable) == [{"id": 1}, {"id": 2}]
assert unhashable == [{"id": 1}, {"id": 2}, {"id": 1}]
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
        "reason": "All checks passed" if result.returncode == 0 else result.stderr[-2000:],
    }
