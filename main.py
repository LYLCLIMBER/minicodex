"""程序入口和组装"""

import json
import os
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import (
    FunctionToolParam,
    ResponseInputItemParam,
    ResponseInputParam,
)
from prompt_toolkit import prompt

from tools import calculator, shell

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com"
)

# --------------------------
# function definition
# --------------------------

tools: list[FunctionToolParam] = [
    {
        "type": "function",
        "name": "calculator",
        "description": "Calculate a mathematical expression.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to caculate.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "shell",
        "description": (
            "Execute a shell command in the project workspace."
            "Returns stdout, stderr, and the process exit code."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
]

# tool name -> python function
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
                "error": "Tool arguments must be a JSON object"
            }

        handler = tool_handlers.get(name)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")

        result = handler(**parsed)

        return {
            "ok": True,
            "result": result,
        }

    except Exception as e: # noqa: BLE001
        return {
            "ok": False,
            "error": type(e).__name__,
            "message": str(e)
        }

# --------------------------
# agent loop
# --------------------------

MAX_STEPS = 10

def run_agent(input_list: ResponseInputParam) -> str:
    for step in range(MAX_STEPS):
        response = client.responses.create(
            model="deepseek-flash",
            instructions="You are a helpful assistant.",
            input=input_list,
            tools=tools,
        )

        # print(f"\n--- step {step + 1} ---")

        # 把模型本轮的所有输出加入上下文
        for item in response.output:
            # print(type(item))
            # print(item)
            input_list.append(
                cast(
                    ResponseInputItemParam,
                    item.model_dump(exclude_none=True),
                )
            )

        # 找出所有 tool calls；注意 function call 只是 tool call 的一种具体形式
        function_calls = [item for item in response.output if item.type == "function_call"]

        # 如果没有 tool calls，说明模型已经给出最终回答
        if not function_calls:
            return response.output_text

        # 执行所有 tool calls
        for call in function_calls:
            result = execute_tool(call.name, call.arguments)
            # print(f"tool: {call.name}")
            print(f"arguments: {call.arguments}")
            # print(f"result: {result}")

            # 将工具执行结果返回给模型
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )
    raise RuntimeError("Agent exceeded maximum number of steps")

def main():
    input_list: ResponseInputParam = []

    while True:
        try:
            user_input = prompt("you>").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if not user_input:
            continue
        if user_input in {"/exit", "/quit"}:
            break

        input_list.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        answer = run_agent(input_list)
        print(f"\nassistant>{answer}\n")

if __name__ == "__main__":
    main()
