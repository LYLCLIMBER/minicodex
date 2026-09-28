import ast
import operator
import subprocess
from pathlib import Path
from typing import TypedDict


# ----------------
# shell
# ----------------
class ShellResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int


WORKSPACE = Path.cwd()
MAX_OUTPUT = 20_000


def truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text

    return text[:MAX_OUTPUT] + "\n... [output truncated]"


def shell(command: str) -> ShellResult:
    try:
        completed = subprocess.run(
            ["bash", "-c", command],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

        return {
            "stdout": truncate(completed.stdout),
            "stderr": truncate(completed.stderr),
            "returncode": completed.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Command timed out after 30 seconds.",
            "returncode": 124,
        }


# ----------------
# calculator
# ----------------
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def calculator(expression: str) -> int | float:
    def evaluate(node) -> int | float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are supported")

        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            return OPERATORS[type(node.op)](left, right)

        raise ValueError("Unsupported expression")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)
