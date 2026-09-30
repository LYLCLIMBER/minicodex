from pathlib import Path
from uuid import uuid4

from tools import WORKSPACE, shell


def test_workspace_is_writable():
    filename = f"sandbox_write_test_{uuid4().hex}.tmp"

    try:
        shell(f"echo hello > {filename}")
        assert (WORKSPACE / filename).read_text() == "hello\n"
    finally:
        (WORKSPACE / filename).unlink(missing_ok=True)


def test_env_cannot_be_read():
    result = shell(f"cat {WORKSPACE}/.env > /dev/null")

    assert result["returncode"] != 0


def test_cannot_write_outside_workspace():
    target = Path("/etc") / f"sandbox_write_test_{uuid4().hex}.tmp"
    try:
        result = shell(f"touch {target}")

        assert result["returncode"] != 0
    finally:
        target.unlink(missing_ok=True)


def test_cannot_connect_to_external_network():
    result = shell(
            "python -c \"import socket; "
            "socket.create_connection(('1.1.1.1', 53), timeout=2)\""
        )
    
    assert result["returncode"] != 0
