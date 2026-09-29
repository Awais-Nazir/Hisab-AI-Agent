from app.tools.write import propose_expense, confirm_action
from .api_client import HisabClient


client = HisabClient()
client.login()

proposal = propose_expense(
    amount=100,
    description="Test expense",
    category_id="cmua98y6g0001jp04pd82u2t4",
    account_id="cmu8poi7z0001jw04yr0glune",
    is_personal=True,
    payments=[
        {
            "person_id": "self_id",
            "amount": 100,
        }
    ],
    splits=[],
)

print("=== Proposal ===")
print(proposal)

action_id = proposal["action_id"]

result = confirm_action(action_id, client)

print("\n=== Confirmed ===")
print(result)

client.close()
