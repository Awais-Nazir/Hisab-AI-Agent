from typing import Literal

from pydantic import BaseModel, model_validator


class ExpensePayment(BaseModel):
    person_id: str
    amount: float


class ExpenseSplit(BaseModel):
    person_id: str
    amount: float


class ExpenseProposal(BaseModel):
    amount: float
    description: str
    category_id: str
    account_id: str
    is_personal: bool
    payments: list[ExpensePayment]
    splits: list[ExpenseSplit] = []

    @model_validator(mode="after")
    def check_sums(self):
        if abs(sum(p.amount for p in self.payments) - self.amount) > 0.01:
            raise ValueError("payments must sum to amount")

        if self.splits and abs(sum(s.amount for s in self.splits) - self.amount) > 0.01:
            raise ValueError("splits must sum to amount")

        return self


class SettlementProposal(BaseModel):
    from_person_id: str
    to_person_id: str
    amount: float
    account_id: str | None = None
    note: str | None = None


class UdharProposal(BaseModel):
    type: Literal["LENA", "DENA"]
    person_id: str
    amount: float
    account_id: str
    note: str | None = None


class UdharSettleProposal(BaseModel):
    udhar_id: str
    account_id: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    pending_action: dict | None = None


class ActionResponse(BaseModel):
    action_id: str
    status: str
    type: str
    result: dict | None = None
