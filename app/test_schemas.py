from app.schemas import (
    ExpenseProposal,
    SettlementProposal,
    UdharProposal,
    UdharSettleProposal,
)


print("=== Expense ===")

expense = ExpenseProposal(
    amount=1000,
    description="Dinner",
    category_id="category123",
    account_id="account123",
    is_personal=False,
    payments=[
        {"person_id": "self", "amount": 500},
        {"person_id": "kaif123", "amount": 500},
    ],
    splits=[
        {"person_id": "self", "amount": 500},
        {"person_id": "kaif123", "amount": 500},
    ],
)

print(expense.model_dump())


print("\n=== Settlement ===")

settlement = SettlementProposal(
    from_person_id="self",
    to_person_id="kaif123",
    amount=500,
    account_id="account123",
    note="Dinner settlement",
)

print(settlement.model_dump())


print("\n=== Udhar ===")

udhar = UdharProposal(
    type="BORROW",
    person_id="kaif123",
    amount=20000,
    account_id="account123",
    note="Loan to Kaif",
)

print(udhar.model_dump())


print("\n=== Udhar Settlement ===")

udhar_settle = UdharSettleProposal(
    udhar_id="udhar123",
    account_id="account123",
)

print(udhar_settle.model_dump())
