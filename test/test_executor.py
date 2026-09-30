import pytest

import executor


def test_valid_tool_and_arguments_succeeds(
    monkeypatch: pytest.MonkeyPatch, 
) -> None:
    monkeypatch.setitem(executor.tool_handlers, "calculator", lambda expression: 42)

    assert executor.execute_tool("calculator", '{"expression": "6*7"}') == {
        "ok": True,
        "result": 42,
    }

def test_invalid_json_returns_error():
    result = executor.execute_tool("calculator", "{invalid_json")

    assert result["ok"] is False

def test_json_must_be_an_object():
    result = executor.execute_tool("calculator", "[]")

    assert result["ok"] is False

def test_unknown_tool_returns_error():
    result = executor.execute_tool("missing_tool", "{}")

    assert result["ok"] is False

def test_handler_exception_does_not_escape(monkeypatch):
    def failing_handler(**kwargs):
        raise RuntimeError("tool failed")

    monkeypatch.setitem(executor.tool_handlers, "calculator", failing_handler)

    result = executor.execute_tool("calculator", '{"expression": "anything"}')

    assert result == {
        "ok": False,
        "error": "RuntimeError",
        "message": "tool failed"
    }
