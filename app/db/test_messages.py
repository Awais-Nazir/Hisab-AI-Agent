from app.db.database import SessionLocal
from app.db.messages import get_session_messages, save_agent_messages
from app.db.sessions import create_session


def main():
    db = SessionLocal()

    try:
        session = create_session(db)

        messages = [
            {
                "role": "system",
                "content": "You are Hisab AI.",
            },
            {
                "role": "user",
                "content": "Maine Ali ko 500 diye.",
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "propose_udhar",
                            "arguments": '{"amount":500}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "content": '{"action_id":"abc"}',
                "tool_call_id": "call_123",
            },
            {
                "role": "assistant",
                "content": "Action ready hai. Confirmation ka wait hai.",
            },
        ]

        saved = save_agent_messages(
            db=db,
            session_id=session.id,
            messages=messages,
            start_index=0,
        )

        print("SAVED:")
        for message in saved:
            print(
                message.id,
                message.role,
                message.content,
                message.tool_calls,
                message.tool_call_id,
            )

        print("\nDATABASE:")
        db_messages = get_session_messages(
            db=db,
            session_id=session.id,
        )

        for message in db_messages:
            print(
                message.id,
                message.role,
                message.content,
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
