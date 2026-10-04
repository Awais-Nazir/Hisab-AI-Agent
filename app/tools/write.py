import uuid

from ..schemas import (
    SettlementProposal,
    UdharProposal,
    UdharSettleProposal,
    ExpenseProposal,
)

from sqlalchemy.orm import Session as DBSession

from ..db.actions import get_pending_action, update_action_status


def propose_udhar(
    type: str,
    person_id: str,
    amount: float,
    account_id: str,
    note: str | None = None,
):
    proposal = UdharProposal(
        type=type,
        person_id=person_id,
        amount=amount,
        account_id=account_id,
        note=note,
    )

    action_id = str(uuid.uuid4())

    direction = "lene" if proposal.type == "LENA" else "dene"

    return {
        "action_id": action_id,
        "type": "udhar",
        "proposal": proposal.model_dump(),
        "summary": (
            f"Proposed udhar: {proposal.amount} PKR "
            f"{direction} from person {proposal.person_id}."
        ),
    }


def propose_expense(
    amount: float,
    description: str,
    category_id: str,
    account_id: str,
    is_personal: bool,
    payments: list[dict],
    splits: list[dict] | None = None,
):
    proposal = ExpenseProposal(
        amount=amount,
        description=description,
        category_id=category_id,
        account_id=account_id,
        is_personal=is_personal,
        payments=payments,
        splits=splits or [],
    )

    action_id = str(uuid.uuid4())

    return {
        "action_id": action_id,
        "type": "expense",
        "proposal": proposal.model_dump(),
        "summary": (
            f"Proposed expense: {proposal.amount} PKR for '{proposal.description}'."
        ),
    }


def propose_settlement(
    from_person_id: str,
    to_person_id: str,
    amount: float,
    account_id: str | None = None,
    note: str | None = None,
):
    proposal = SettlementProposal(
        from_person_id=from_person_id,
        to_person_id=to_person_id,
        amount=amount,
        account_id=account_id,
        note=note,
    )

    action_id = str(uuid.uuid4())

    return {
        "action_id": action_id,
        "type": "settlement",
        "proposal": proposal.model_dump(),
        "summary": (
            f"Proposed settlement of {proposal.amount} PKR "
            f"from {proposal.from_person_id} "
            f"to {proposal.to_person_id}."
        ),
    }


def propose_udhar_settle(
    udhar_id: str,
    account_id: str,
):
    proposal = UdharSettleProposal(
        udhar_id=udhar_id,
        account_id=account_id,
    )

    action_id = str(uuid.uuid4())

    return {
        "action_id": action_id,
        "type": "udhar_settle",
        "proposal": proposal.model_dump(),
        "summary": (f"Proposed settlement of udhar {proposal.udhar_id}."),
    }


def confirm_action(
    db: DBSession,
    action_id: str,
    session_id: str,
    client,
):
    action = get_pending_action(
        db=db,
        action_id=action_id,
        session_id=session_id,
    )

    if not action:
        raise ValueError("Action not found or already completed.")

    if action.status != "pending":
        raise ValueError("Action is no longer pending.")

    proposal = action.proposal

    if action.type == "expense":
        category_name = client.get_category_name(proposal["category_id"])

        result = client.write_expense(
            amount=proposal["amount"],
            description=proposal["description"],
            category=category_name,
            account_id=proposal["account_id"],
            is_personal=proposal["is_personal"],
            payments=proposal["payments"],
            splits=proposal["splits"],
        )

    elif action.type == "udhar":
        result = client.write_udhar(
            type=proposal["type"],
            person_id=proposal["person_id"],
            amount=proposal["amount"],
            account_id=proposal["account_id"],
            note=proposal["note"],
        )

    elif action.type == "udhar_settle":
        result = client.settle_udhar(
            udhar_id=proposal["udhar_id"],
            account_id=proposal["account_id"],
        )

    elif action.type == "settlement":
        result = client.write_global_settlement(
            from_person_id=proposal["from_person_id"],
            to_person_id=proposal["to_person_id"],
            amount=proposal["amount"],
            account_id=proposal["account_id"],
            note=proposal["note"],
        )

    else:
        raise ValueError(f"Unsupported action type: {action.type}")

    # Only mark confirmed after the real Hisab API operation succeeds.
    update_action_status(
        db=db,
        action=action,
        status="confirmed",
    )

    return {
        "action_id": action.id,
        "status": "confirmed",
        "type": action.type,
        "result": result,
    }


def reject_action(
    db: DBSession,
    action_id: str,
    session_id: str,
):
    action = get_pending_action(
        db=db,
        action_id=action_id,
        session_id=session_id,
    )

    if not action:
        raise ValueError("Action not found or already completed.")

    if action.status != "pending":
        raise ValueError("Action is no longer pending.")

    update_action_status(
        db=db,
        action=action,
        status="rejected",
    )

    return {
        "action_id": action.id,
        "status": "rejected",
        "type": action.type,
    }
