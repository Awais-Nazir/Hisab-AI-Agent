import uuid

from .database import SessionLocal
from .models import Session
from .actions import (
    create_pending_action,
    get_pending_action,
    update_action_status,
)


def main():
    db = SessionLocal()

    try:
        session_id = str(uuid.uuid4())
        action_id = str(uuid.uuid4())

        session = Session(
            id=session_id,
        )

        db.add(session)
        db.commit()

        proposal = {
            "amount": 500,
            "description": "Test expense",
            "category_id": "test-category",
            "account_id": "test-account",
        }

        # Create
        action = create_pending_action(
            db=db,
            action_id=action_id,
            session_id=session_id,
            action_type="expense",
            proposal=proposal,
        )

        print("CREATED:")
        print(action.id)
        print(action.status)
        print(action.proposal)
        print(action.created_at)
        print(action.updated_at)

        # Read
        action = get_pending_action(
            db=db,
            action_id=action_id,
            session_id=session_id,
        )

        print("\nREAD:")
        print(action.id)
        print(action.status)

        # Update
        action = update_action_status(
            db=db,
            action=action,
            status="confirmed",
        )

        print("\nUPDATED:")
        print(action.id)
        print(action.status)
        print(action.updated_at)

    finally:
        db.close()


if __name__ == "__main__":
    main()
