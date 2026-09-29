from openai import OpenAI
from dotenv import load_dotenv

from app.tools.api_client import HisabClient

from .tools_list import tools
from ..tools.write import (
    propose_udhar,
    propose_expense,
    propose_settlement,
    propose_udhar_settle,
    confirm_action,
)
from ..tools.read import (
    list_expenses,
    list_contacts,
    get_contact_balance,
    list_categories,
    list_accounts,
    list_udhar,
)

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


load_dotenv()

client = OpenAI()

MAX_STEPS = 6

TOOL_REGISTRY = {
    "list_expenses": list_expenses,
    "list_contacts": list_contacts,
    "get_contact_balance": get_contact_balance,
    "list_categories": list_categories,
    "list_accounts": list_accounts,
    "list_udhar": list_udhar,
    "propose_udhar": propose_udhar,
    "propose_expense": propose_expense,
    "propose_settlement": propose_settlement,
    "propose_udhar_settle": propose_udhar_settle,
    "confirm_action": confirm_action,
}

SYSTEM_PROMPT = """You are the Hisab Kitab assistant. You help the user with their own
expenses, balances, contacts and accounts. All amounts are in PKR.

Current date/time: {now} (Asia/Karachi). Use it to resolve "aaj", "kal", "is hafte".

Reply in the language the user writes in (Roman Urdu, Urdu or English).

Only answer about the user's Hisab Kitab data. For anything else, say briefly that
you can only help with their expenses, balances and accounts.

Never state a number that did not come from a tool result. If a name is unclear, ask.

Definitions:
- your_share = what an expense cost the user
- you_paid = cash the user paid out
- amount = the full bill
  
Udhar vs shared-expense balance:
- Shared-expense balance and udhar are separate concepts.
- get_contact_balance is only for shared-expense balances.
- list_udhar is for actual udhar entries.
- If the user explicitly says "udhar", "lena", or "dena" in an udhar context, use list_udhar.
- LENA means the user should receive money from that person.
- DENA means the user owes money to that person.

Account rules:
- When creating an expense, udhar entry, or settlement, never assume which account was used.
- If the user does not name an account for one of these actions, use list_accounts and ask them to choose.

Payment rules:
- If a person has both a shared-expense balance and an open udhar entry,
  ask which one the payment is settling.

"""


def run_agent(user_message: str, history: list | None = None) -> dict:
    """
    Run the Hisab Kitab agent for one user message.

    Args:
        user_message: The new message from the user.
        history: Previous conversation messages.

    Returns:
        {
            "reply": str,
            "tool_calls": list,
            "messages": list
        }
    """

    history = history or []

    hisab_client = HisabClient()
    hisab_client.login()

    now = datetime.now(ZoneInfo("Asia/Karachi"))

    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT.format(now=now.strftime("%Y-%m-%d %H:%M:%S")),
    }

    messages = [
        system_message,
        *history,
        {
            "role": "user",
            "content": user_message,
        },
    ]

    tool_calls = []

    for _ in range(MAX_STEPS):
        completion = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=tools,
        )

        message = completion.choices[0].message

        messages.append(message)

        if not message.tool_calls:
            return {
                "reply": message.content or "",
                "tool_calls": tool_calls,
                "messages": messages,
            }

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            raw_arguments = tool_call.function.arguments

            try:
                parsed_args = json.loads(raw_arguments)

            except json.JSONDecodeError:
                result = {"error": "Invalid JSON arguments provided by the model."}

                tool_calls.append({
                    "name": tool_name,
                    "arguments": raw_arguments,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

                continue

            tool_function = TOOL_REGISTRY.get(tool_name)

            if not tool_function:
                result = {"error": f"Unknown tool: {tool_name}"}

                tool_calls.append({
                    "name": tool_name,
                    "arguments": parsed_args,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

                continue

            try:
                if tool_name == "confirm_action":
                    result = confirm_action(
                        action_id=parsed_args["action_id"],
                        client=hisab_client,
                    )
                else:
                    result = tool_function(**parsed_args)

            except Exception as e:
                result = {"error": f"Tool '{tool_name}' failed: {str(e)}"}

            tool_calls.append({
                "name": tool_name,
                "arguments": parsed_args,
                "result": result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

    return {
        "reply": (
            "I couldn't complete the request because the maximum "
            "number of tool steps was reached."
        ),
        "tool_calls": tool_calls,
        "messages": messages,
    }


# result = run_agent(
#     # "Maine Kaif ko 5000 PKR udhar diye hain. NayaPay se. Note mein 'Lunch ke liye' likh do."
#     "Maine NayaPay se 250 PKR ka breakfast kiya hai. Category Breakfast hai."
#     # "Kaif ka 20,000 wala udhar settle kar do"
# )

# print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

first = run_agent(
    "kaif ne mujhe 3000 jo cash advnace lia tha wapis kr dia nayapay main, settle kr do."
)

print("=== FIRST ===")
print(json.dumps(first, indent=2, ensure_ascii=False, default=str))

second = run_agent(
    "haan, confirm kar do",
    history=first["messages"],
)

print("\n=== SECOND ===")
print(json.dumps(second, indent=2, ensure_ascii=False, default=str))
