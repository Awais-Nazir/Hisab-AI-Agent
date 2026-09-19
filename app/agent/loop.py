from openai import OpenAI
from dotenv import load_dotenv
from .tools_list import tools
from ..tools.read import get_balance

import json
import os


load_dotenv()

client = OpenAI()


messages = [
    {
        "role": "user",
        "content": "Ahmed aur Razaq ka total balance kitna hai?",
    }
]


# 1. Ask the model what to do
completion = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages,
    tools=tools,
)

print("\n=== USER ===")
print(messages[0]["content"])


message = completion.choices[0].message

print("MODEL RESPONSE:")
print(message)


# 2. Add model's response to conversation
messages.append(message)


# 3. Execute requested tools
if message.tool_calls:
    for tool_call in message.tool_calls:
        print("\nTOOL REQUEST:")
        print(tool_call.function.name)
        print(tool_call.function.arguments)

        parsed_args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "get_balance":
            result = get_balance(**parsed_args)
        else:
            result = {"error": "Unknown tool"}

        print("\nTOOL RESULT:")
        print(result)

        # 4. Give tool result back to model
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })


# 5. Ask model for final natural-language response
final_completion = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages,
    tools=tools,
)


print("\nFINAL ANSWER:")
print(final_completion.choices[0].message.content)

print("\n=== USER ===")
print(messages[0]["content"])
