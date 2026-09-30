from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest

from tools import shell


@pytest.fixture
def workspace() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def selected_workspace(workspace: Path):
    # The sandbox replaces /tmp with tmpfs, so create the directory under the project.
    with TemporaryDirectory(dir=workspace) as directory:
        yield Path(directory)


def test_workspace_is_writable(workspace: Path):
    filename = f"sandbox_write_test_{uuid4().hex}.tmp"

    try:
        result = shell(f"echo hello > {filename}", workspace=workspace)
        assert result["returncode"] == 0
        assert (workspace / filename).read_text() == "hello\n"
    finally:
        (workspace / filename).unlink(missing_ok=True)


def test_env_cannot_be_read(workspace: Path):
    if not (workspace / ".env").is_file():
        pytest.skip(".env does not exist")

    result = shell(f"cat {workspace}/.env", workspace=workspace)

    assert result["returncode"] != 0
    assert result["stdout"] == ""


def test_cannot_write_outside_workspace(workspace: Path):
    target = workspace.parent / f"sandbox_write_test_{uuid4().hex}.tmp"
    target.unlink(missing_ok=True)

    try:
        result = shell(f"touch {target}", workspace=workspace)

        assert result["returncode"] != 0
    finally:
        target.unlink(missing_ok=True)


def test_cannot_connect_to_external_network(workspace: Path):
    result = shell(
        "python -c \"import socket; "
        "socket.create_connection(('1.1.1.1', 53), timeout=2)\"",
        workspace=workspace,
    )

    assert result["returncode"] != 0


def test_uses_explicit_workspace(selected_workspace: Path):
    result = shell("pwd", workspace=selected_workspace)

    assert result["returncode"] == 0
    assert result["stdout"].strip() == str(selected_workspace)


def test_explicit_workspace_is_writable(selected_workspace: Path):
    result = shell("echo hello > created.txt", workspace=selected_workspace)

    assert result["returncode"] == 0
    assert (selected_workspace / "created.txt").read_text() == "hello\n"


def test_cannot_write_outside_explicit_workspace(selected_workspace: Path):
    target = selected_workspace.parent / f"sandbox_write_test_{uuid4().hex}.tmp"

    try:
        # First confirm the sandbox started; otherwise a failed command proves nothing.
        assert shell("true", workspace=selected_workspace)["returncode"] == 0

        result = shell(f"touch {target}", workspace=selected_workspace)

        assert result["returncode"] != 0
        assert not target.exists()
    finally:
        target.unlink(missing_ok=True)
