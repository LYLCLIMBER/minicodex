"""Run every eval case in an isolated temporary workspace."""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseInputParam

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from main import run_agent

CASES_DIR = Path(__file__).resolve().parent


def run_case(case: Path, client: OpenAI) -> dict:
    result = {"case": case.name, "status": "run_failed", "reason": ""}
    try:
        prompt = (case / "prompt.md").read_text(encoding="utf-8")
        spec = importlib.util.spec_from_file_location(f"eval_check_{case.name}", case / "check.py")
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load checker for {case.name}")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)

        with tempfile.TemporaryDirectory(prefix=f"eval-{case.name}-") as tmp:
            workspace = Path(tmp) / "workspace"
            shutil.copytree(case / "workspace", workspace)
            conversation: ResponseInputParam = [{"role": "user", "content": prompt}]
            result["answer"] = run_agent(conversation, client=client, workspace=workspace)
            verdict = checker.check(workspace)
            if not isinstance(verdict, dict) or type(verdict.get("passed")) is not bool:
                raise ValueError(f"Invalid check result for {case.name}: {verdict!r}")
            result["status"] = "passed" if verdict["passed"] else "task_failed"
            result["reason"] = str(verdict.get("reason", ""))
    except Exception as exc: # noqa: BLE001
        result["reason"] = f"{type(exc).__name__}: {exc}"

    return result


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    cases = sorted(
        path for path in CASES_DIR.iterdir()
        if path.is_dir() and (path / "prompt.md").is_file()
    )
    results = []
    for case in cases:
        result = run_case(case, client)
        results.append(result)
        print(f"{case.name}: {result['status']} ({result['reason']})")

    summary = {
        "total": len(results),
        "passed": sum(item["status"] == "passed" for item in results),
        "run_failed": sum(item["status"] == "run_failed" for item in results),
        "task_failed": sum(item["status"] == "task_failed" for item in results),
    }
    report = {"summary": summary, "results": results}
    output_dir = CASES_DIR / "result"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%fZ")
    output = output_dir / f"{timestamp}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Summary: {summary}")
    print(f"Result: {output}")


if __name__ == "__main__":
    main()
