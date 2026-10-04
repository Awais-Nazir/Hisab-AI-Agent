from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import PendingAction


def create_pending_action(
    db: Session,
    action_id: str,
    session_id: str,
    action_type: str,
    proposal: dict[str, Any],
) -> PendingAction:
    action = PendingAction(
        id=action_id,
        session_id=session_id,
        type=action_type,
        proposal=proposal,
        status="pending",
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action


def get_pending_action(
    db: Session,
    action_id: str,
    session_id: str,
) -> PendingAction | None:
    return (
        db
        .query(PendingAction)
        .filter(
            PendingAction.id == action_id,
            PendingAction.session_id == session_id,
        )
        .first()
    )


def update_action_status(
    db: Session,
    action: PendingAction,
    status: str,
) -> PendingAction:
    action.status = status
    db.commit()
    db.refresh(action)

    return action


def get_pending_action_for_session(
    db: Session,
    session_id: str,
) -> PendingAction | None:
    return (
        db
        .query(PendingAction)
        .filter(
            PendingAction.session_id == session_id,
            PendingAction.status == "pending",
        )
        .order_by(PendingAction.created_at.desc())
        .first()
    )
