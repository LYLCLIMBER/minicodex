import ast
import operator
import subprocess
from pathlib import Path
from typing import TypedDict

# ----------------
# shell
# ----------------

WORKSPACE = Path.cwd().resolve()
MAX_OUTPUT = 20_000
SANDBOX_PATH = "/usr/local/bin:/usr/bin:/bin"

if(WORKSPACE / ".venv" / "bin").is_dir():
    SANDBOX_PATH = f"{WORKSPACE}/.venv/bin:{SANDBOX_PATH}"

class ShellResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int

def truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text

    return text[:MAX_OUTPUT] + "\n... [output truncated]"


def shell(command: str) -> ShellResult:
    sandbox_command = [
        "bwrap",

        # namespace isolation
        "--unshare-all",
        "--die-with-parent",

        # expose system program read-only
        "--ro-bind", "/", "/",
        
        # minimal runtime filesystem
        # procfs 获取沙箱内进程信息
        "--proc", "/proc",
        "--dev", "/dev",
        # 创建一个和沙箱生命周期绑定的临时文件系统
        "--tmpfs", "/tmp",
        "--dir", "/tmp/home",

        # only project directory is writable
        "--bind", str(WORKSPACE), str(WORKSPACE),
        # 把工作目录切换到 DIR
        "--chdir", str(WORKSPACE),

        # do not leak DEEP_SEEK_API etc.
        "--clearenv",
        "--setenv", "HOME", "/tmp/home",
        "--setenv", "PATH", SANDBOX_PATH,
        "--setenv", "LANG", "C.UTF-8",
    ]

    if(WORKSPACE / ".env").exists():
        sandbox_command += [
            "--ro-bind", "/dev/null", f"{WORKSPACE}/.env"
        ]

    # command 应该在参数的后面
    sandbox_command += [
        # actual command
        "/usr/bin/bash",
        "-c",
        command
    ]

    try:
        completed = subprocess.run(
            sandbox_command,
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
