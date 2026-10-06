import os
import re

from fastapi import Depends, FastAPI, Header, HTTPException, status

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
from .run_logs import log_chat_run
from .schemas import ChatRequest, ChatResponse
from .db.actions import create_pending_action, get_pending_action_for_session
from .tools.write import confirm_action, reject_action
from .schemas import ActionResponse

app = FastAPI(title="Hisab Agent")

AGENT_SECRET = os.getenv("AGENT_SECRET")


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


def pending_action_response(action, client: HisabClient | None = None):
    if not action:
        return None

    proposal = dict(action.proposal)

    if client and action.type == "expense":
        category_id = proposal.get("category_id")
        account_id = proposal.get("account_id")

        if category_id:
            try:
                proposal["category_name"] = client.get_category_name(category_id)
            except Exception:
                proposal["category_name"] = category_id

        if account_id:
            try:
                proposal["account_name"] = client.get_account_name(account_id)
            except Exception:
                proposal["account_name"] = account_id

    return {
        "action_id": action.id,
        "type": action.type,
        "status": action.status,
        "proposal": proposal,
    }


def require_agent_secret(
    x_agent_secret: str | None = Header(default=None, alias="X-Agent-Secret"),
):
    if not AGENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AGENT_SECRET is not configured.",
        )

    if x_agent_secret != AGENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Agent-Secret.",
        )


def require_hisab_auth(
    authorization: str | None = Header(default=None, alias="Authorization"),
    cookie: str | None = Header(default=None, alias="Cookie"),
) -> dict:
    if not authorization and not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Hisab user auth.",
        )

    return {
        "authorization": authorization,
        "cookie": cookie,
    }


def tool_log_entries(tool_calls: list[dict]) -> list[dict]:
    return [
        {
            "name": tool_call.get("name"),
            "arguments": tool_call.get("arguments"),
        }
        for tool_call in tool_calls
    ]


@app.get("/")
def test():
    return {
        "message": "welcome to Hisab Agent API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(require_agent_secret)],
)
def chat(
    request: ChatRequest,
    hisab_auth: dict = Depends(require_hisab_auth),
):
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
                hisab_client = HisabClient(**hisab_auth)

                try:
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
                log_chat_run(
                    session_id=session.id,
                    user_message=request.message,
                    tools_called=[
                        {
                            "name": "confirm_action",
                            "arguments": {"action_id": pending_action.id},
                        }
                    ],
                    final_reply=reply,
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
                log_chat_run(
                    session_id=session.id,
                    user_message=request.message,
                    tools_called=[
                        {
                            "name": "reject_action",
                            "arguments": {"action_id": pending_action.id},
                        }
                    ],
                    final_reply=reply,
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
            log_chat_run(
                session_id=session.id,
                user_message=request.message,
                tools_called=[],
                final_reply=reply,
            )

            display_client = HisabClient(**hisab_auth)

            try:
                pending_action = pending_action_response(
                    pending_action,
                    client=display_client,
                )
            finally:
                display_client.close()

            return ChatResponse(
                session_id=session.id,
                reply=reply,
                pending_action=pending_action,
            )

        # 3. Run the agent.
        result = run_agent(
            user_message=request.message,
            history=history,
            hisab_authorization=hisab_auth["authorization"],
            hisab_cookie=hisab_auth["cookie"],
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
        log_chat_run(
            session_id=session.id,
            user_message=request.message,
            tools_called=tool_log_entries(result["tool_calls"]),
            final_reply=result["reply"],
        )

        # 5. Return the response.
        display_client = HisabClient(**hisab_auth)

        try:
            pending_action = pending_action_response(
                pending_action,
                client=display_client,
            )
        finally:
            display_client.close()

        return ChatResponse(
            session_id=session.id,
            reply=result["reply"],
            pending_action=pending_action,
        )

    finally:
        db.close()


@app.post(
    "/actions/{action_id}/confirm",
    response_model=ActionResponse,
    dependencies=[Depends(require_agent_secret)],
)
def confirm_pending_action(
    action_id: str,
    session_id: str,
    hisab_auth: dict = Depends(require_hisab_auth),
):
    db = SessionLocal()

    try:
        hisab_client = HisabClient(**hisab_auth)

        try:
            result = confirm_action(
                db=db,
                action_id=action_id,
                session_id=session_id,
                client=hisab_client,
            )

        finally:
            hisab_client.close()

        log_chat_run(
            session_id=session_id,
            user_message="[confirm endpoint]",
            tools_called=[
                {
                    "name": "confirm_action",
                    "arguments": {"action_id": action_id},
                }
            ],
            final_reply="Action confirmed via endpoint.",
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
    dependencies=[Depends(require_agent_secret)],
)
def reject_pending_action(
    action_id: str,
    session_id: str,
    hisab_auth: dict = Depends(require_hisab_auth),
):
    db = SessionLocal()

    try:
        result = reject_action(
            db=db,
            action_id=action_id,
            session_id=session_id,
        )
        log_chat_run(
            session_id=session_id,
            user_message="[reject endpoint]",
            tools_called=[
                {
                    "name": "reject_action",
                    "arguments": {"action_id": action_id},
                }
            ],
            final_reply="Action rejected via endpoint.",
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
