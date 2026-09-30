from pathlib import Path

import pytest

import executor


def test_valid_tool_and_arguments_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setitem(executor.tool_handlers, "calculator", lambda expression: 42)

    assert executor.execute_tool(
        "calculator", '{"expression": "6*7"}', workspace=tmp_path
    ) == {
        "ok": True,
        "result": 42,
    }


def test_invalid_json_returns_error(tmp_path: Path):
    result = executor.execute_tool("calculator", "{invalid_json", workspace=tmp_path)

    assert result["ok"] is False


def test_json_must_be_an_object(tmp_path: Path):
    result = executor.execute_tool("calculator", "[]", workspace=tmp_path)

    assert result["ok"] is False


def test_unknown_tool_returns_error(tmp_path: Path):
    result = executor.execute_tool("missing_tool", "{}", workspace=tmp_path)

    assert result["ok"] is False


def test_handler_exception_does_not_escape(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    def failing_handler(**kwargs):
        raise RuntimeError("tool failed")

    monkeypatch.setitem(executor.tool_handlers, "calculator", failing_handler)

    result = executor.execute_tool(
        "calculator", '{"expression": "anything"}', workspace=tmp_path
    )

    assert result == {
        "ok": False,
        "error": "RuntimeError",
        "message": "tool failed",
    }


def test_shell_receives_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    def fake_shell(command: str, *, workspace: Path):
        assert command == "pwd"
        assert workspace == tmp_path
        return {"stdout": str(workspace), "stderr": "", "returncode": 0}

    monkeypatch.setitem(executor.tool_handlers, "shell", fake_shell)

    result = executor.execute_tool(
        "shell", '{"command": "pwd"}', workspace=tmp_path
    )

    assert result["ok"] is True
    assert result["result"]["stdout"] == str(tmp_path)
