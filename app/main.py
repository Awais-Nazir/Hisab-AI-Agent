import re

from fastapi import FastAPI, HTTPException

from app.tools.api_client import HisabClient

from .db.database import SessionLocal
from .db.messages import (
    create_message,
    get_session_messages,
    messages_to_history,
    save_agent_messages,
)
from .db.sessions import create_session, get_session
from .agent.loop import run_agent
from .schemas import ChatRequest, ChatResponse
from .db.actions import create_pending_action, get_pending_action_for_session
from .tools.write import confirm_action, reject_action
from .schemas import ActionResponse

app = FastAPI(title="Hisab Agent")


CONFIRM_REPLIES = {
    "yes",
    "y",
    "haan",
    "han",
    "ha",
    "ok",
    "okay",
    "confirm",
    "confirmed",
    "sure",
}

REJECT_REPLIES = {
    "no",
    "n",
    "nahin",
    "nahi",
    "na",
    "cancel",
    "reject",
    "rejected",
}

CONFIRM_PHRASES = (
    "confirm kar do",
    "kar do",
    "kardo",
    "kr do",
    "yes confirm",
    "haan confirm",
    "han confirm",
    "ok confirm",
)

REJECT_PHRASES = (
    "cancel kar do",
    "reject kar do",
    "mat karo",
    "mat karna",
    "rehne do",
    "rhne do",
    "nahi karna",
    "nahin karna",
)


def classify_pending_action_reply(message: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9\s]", " ", message.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if not normalized:
        return None

    if normalized in REJECT_REPLIES:
        return "reject"

    if any(phrase in normalized for phrase in REJECT_PHRASES):
        return "reject"

    if normalized in CONFIRM_REPLIES:
        return "confirm"

    if any(phrase in normalized for phrase in CONFIRM_PHRASES):
        return "confirm"

    return None


def pending_action_response(action):
    if not action:
        return None

    return {
        "action_id": action.id,
        "type": action.type,
        "status": action.status,
        "proposal": action.proposal,
    }


@app.get("/")
def test():
    return {
        "message": "welcome to Hisab Agent API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    db = SessionLocal()

    try:
        # 1. Get existing session or create a new one.
        if request.session_id:
            session = get_session(db, request.session_id)

            if not session:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found.",
                )
        else:
            session = create_session(db)

        # 2. Load previous conversation.
        db_messages = get_session_messages(
            db=db,
            session_id=session.id,
        )

        history = messages_to_history(db_messages)
        pending_action = get_pending_action_for_session(
            db=db,
            session_id=session.id,
        )

        if pending_action:
            pending_reply = classify_pending_action_reply(request.message)

            if pending_reply == "confirm":
                hisab_client = HisabClient()

                try:
                    hisab_client.login()

                    confirm_action(
                        db=db,
                        action_id=pending_action.id,
                        session_id=session.id,
                        client=hisab_client,
                    )

                finally:
                    hisab_client.close()

                reply = "Done, I confirmed that action."

                create_message(
                    db=db,
                    session_id=session.id,
                    role="user",
                    content=request.message,
                )
                create_message(
                    db=db,
                    session_id=session.id,
                    role="assistant",
                    content=reply,
                )

                return ChatResponse(
                    session_id=session.id,
                    reply=reply,
                    pending_action=None,
                )

            if pending_reply == "reject":
                reject_action(
                    db=db,
                    action_id=pending_action.id,
                    session_id=session.id,
                )

                reply = "Okay, I rejected that action."

                create_message(
                    db=db,
                    session_id=session.id,
                    role="user",
                    content=request.message,
                )
                create_message(
                    db=db,
                    session_id=session.id,
                    role="assistant",
                    content=reply,
                )

                return ChatResponse(
                    session_id=session.id,
                    reply=reply,
                    pending_action=None,
                )

            reply = (
                "You already have a pending action. "
                "Please confirm or reject it first."
            )

            create_message(
                db=db,
                session_id=session.id,
                role="user",
                content=request.message,
            )
            create_message(
                db=db,
                session_id=session.id,
                role="assistant",
                content=reply,
            )

            return ChatResponse(
                session_id=session.id,
                reply=reply,
                pending_action=pending_action_response(pending_action),
            )

        # 3. Run the agent.
        result = run_agent(
            user_message=request.message,
            history=history,
        )
        pending_action = None

        for tool_call in result["tool_calls"]:
            if tool_call["name"].startswith("propose_"):
                proposal_result = tool_call["result"]

                if "action_id" in proposal_result:
                    pending_action = create_pending_action(
                        db=db,
                        action_id=proposal_result["action_id"],
                        session_id=session.id,
                        action_type=proposal_result["type"],
                        proposal=proposal_result["proposal"],
                    )

                    break

        # 4. Save only messages from this turn.
        save_agent_messages(
            db=db,
            session_id=session.id,
            messages=result["messages"],
            start_index=result["new_messages_start"],
        )

        # 5. Return the response.
        return ChatResponse(
            session_id=session.id,
            reply=result["reply"],
            pending_action=pending_action_response(pending_action),
        )

    finally:
        db.close()


@app.post(
    "/actions/{action_id}/confirm",
    response_model=ActionResponse,
)
def confirm_pending_action(
    action_id: str,
    session_id: str,
):
    db = SessionLocal()

    try:
        hisab_client = HisabClient()
        hisab_client.login()

        result = confirm_action(
            db=db,
            action_id=action_id,
            session_id=session_id,
            client=hisab_client,
        )

        return ActionResponse(
            action_id=result["action_id"],
            status=result["status"],
            type=result["type"],
            result=result["result"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    finally:
        db.close()


@app.post(
    "/actions/{action_id}/reject",
    response_model=ActionResponse,
)
def reject_pending_action(
    action_id: str,
    session_id: str,
):
    db = SessionLocal()

    try:
        result = reject_action(
            db=db,
            action_id=action_id,
            session_id=session_id,
        )

        return ActionResponse(
            action_id=result["action_id"],
            status=result["status"],
            type=result["type"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    finally:
        db.close()
