from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Message


def get_session_messages(
    db: Session,
    session_id: str,
) -> list[Message]:
    statement = (
        select(Message).where(Message.session_id == session_id).order_by(Message.id)
    )

    return list(db.scalars(statement).all())


def create_message(
    db: Session,
    session_id: str,
    role: str,
    content: str | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
    tool_call_id: str | None = None,
) -> Message:
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def save_agent_messages(
    db: Session,
    session_id: str,
    messages: list[dict],
    start_index: int,
) -> list[Message]:
    saved_messages = []

    for message in messages[start_index:]:
        role = message.get("role")

        if role == "system":
            continue

        saved_message = create_message(
            db=db,
            session_id=session_id,
            role=role,
            content=message.get("content"),
            tool_calls=message.get("tool_calls"),
            tool_call_id=message.get("tool_call_id"),
        )

        saved_messages.append(saved_message)

    return saved_messages


def messages_to_history(
    messages: list[Message],
) -> list[dict]:
    history = []

    for message in messages:
        item = {
            "role": message.role,
        }

        if message.content is not None:
            item["content"] = message.content

        if message.tool_calls is not None:
            item["tool_calls"] = message.tool_calls

        if message.tool_call_id is not None:
            item["tool_call_id"] = message.tool_call_id

        history.append(item)

    return history
