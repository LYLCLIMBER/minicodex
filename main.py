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

# --------------------------
# initial input
# --------------------------

input_list: ResponseInputParam = [
    {"role": "user", "content": "请告诉我这个项目下都有什么。"}
]

# --------------------------
# agent loop
# --------------------------

MAX_STEPS = 10

for step in range(MAX_STEPS):
    response = client.responses.create(
        model="deepseek-flash",
        instructions="You are a helpful assistant.",
        input=input_list,
        tools=tools,
    )

    print(f"\n--- step {step + 1} ---")

    # 把模型本轮的所有输出加入上下文
    for item in response.output:
        print(type(item))
        print(item)
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
        print("\nFinal answer:")
        print(response.output_text)
        break

    # 执行所有 tool calls
    for call in function_calls:
        arguments = json.loads(call.arguments)
        handler = tool_handlers[call.name]
        result = handler(**arguments)

        print(f"tool: {call.name}")
        print(f"arguments: {call.arguments}")
        print(f"result: {result}")

        # 将工具执行结果返回给模型
        input_list.append(
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result, ensure_ascii=False),
            }
        )
else:
    raise RuntimeError("Agent exceeded maximum number of steps")
