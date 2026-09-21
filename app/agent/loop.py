from openai import OpenAI
from dotenv import load_dotenv

from .tools_list import tools
from ..tools.read import (
    list_expenses,
    list_contacts,
    get_contact_balance,
    list_categories,
    list_accounts,
)

import json
import os


load_dotenv()

client = OpenAI()

MAX_STEPS = 6

TOOL_REGISTRY = {
    "list_expenses": list_expenses,
    "list_contacts": list_contacts,
    "get_contact_balance": get_contact_balance,
    "list_categories": list_categories,
    "list_accounts": list_accounts,
}

SYSTEM_PROMPT = """You are the Hisab Kitab assistant. You help the user with their own
expenses, balances, contacts and accounts. All amounts are in PKR.

Current date/time: {now} (Asia/Karachi). Use it to resolve "aaj", "kal", "is hafte".
Reply in the language the user writes in (Roman Urdu, Urdu or English).
Only answer about the user's Hisab Kitab data. For anything else, say briefly that
you can only help with their expenses, balances and accounts.
Never state a number that did not come from a tool result. If a name is unclear, ask.
Definitions: your_share = what an expense cost the user; you_paid = cash the user
paid out; amount = the full bill."""


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": "Hamza ka balance batao",
    },
]


print("\n=== USER ===")
print(messages[0]["content"])


for step in range(MAX_STEPS):
    print(f"\n=== STEP {step + 1} ===")

    completion = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=tools,
    )

    message = completion.choices[0].message

    print("\nMODEL RESPONSE:")
    print(message)

    # Add model response to conversation
    messages.append(message)

    # No tool calls = model is done
    if not message.tool_calls:
        print("\nFINAL ANSWER:")
        print(message.content)
        break

    # Execute requested tools
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        raw_arguments = tool_call.function.arguments

        print("\nTOOL REQUEST:")
        print("Name:", tool_name)
        print("Arguments:", raw_arguments)

        try:
            parsed_args = json.loads(raw_arguments)
        except json.JSONDecodeError:
            result = {"error": "Invalid JSON arguments provided by the model."}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

            continue

        tool_function = TOOL_REGISTRY.get(tool_name)

        if not tool_function:
            result = {"error": f"Unknown tool: {tool_name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

            continue

        try:
            result = tool_function(**parsed_args)

        except Exception as e:
            result = {"error": f"Tool '{tool_name}' failed: {str(e)}"}

        print("\nTOOL RESULT:")
        print(result)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

else:
    print("\nERROR: Maximum tool steps reached.")
