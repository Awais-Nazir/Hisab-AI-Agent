from app.db.actions import (
    create_pending_action,
    get_pending_action_for_session,
)
from app.db.database import SessionLocal
from app.db.sessions import create_session


def main():
    db = SessionLocal()

    try:
        session = create_session(db)

        action = create_pending_action(
            db=db,
            action_id="test-pending-action",
            session_id=session.id,
            action_type="expense",
            proposal={
                "amount": 500,
                "description": "Test expense",
            },
        )

        print("CREATED:")
        print(action.id, action.status)

        pending = get_pending_action_for_session(
            db=db,
            session_id=session.id,
        )

        print("\nFOUND:")
        print(pending.id, pending.status)
        print(pending.proposal)

    finally:
        db.close()


if __name__ == "__main__":
    main()
