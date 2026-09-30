import json

from tools import calculator, shell

tool_handlers = {
    "calculator": calculator,
    "shell": shell,
}


def execute_tool(name: str, arguments: str):
    try:
        parsed = json.loads(arguments)

        if not isinstance(parsed, dict):
            return {
                "ok": False,
                "error": "InvalidArguments",
                "message": "Tool arguments must be a JSON object",
            }

        handler = tool_handlers.get(name)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")

        result = handler(**parsed)

        return {
            "ok": True,
            "result": result,
        }

    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "error": type(e).__name__,
            "message": str(e),
        }

# print(execute_tool("calculator", '{"expression": "1/0"}'))
# print(execute_tool("calculator", "{invalid_json"))
