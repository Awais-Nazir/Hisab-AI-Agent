from app.db.database import SessionLocal
from app.db.sessions import create_session
from app.db.actions import create_pending_action, get_pending_action
from app.tools.write import confirm_action, reject_action


class FakeClient:
    def get_category_name(self, category_id):
        return "Food"

    def write_expense(
        self,
        amount,
        description,
        category,
        account_id,
        is_personal,
        payments,
        splits,
    ):
        return {
            "id": "fake-expense-id",
            "amount": amount,
            "description": description,
            "category": category,
            "account_id": account_id,
        }


def main():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # Create a real DB session
        # --------------------------------------------------
        session = create_session(db)

        print("SESSION:")
        print(session.id)

        # ==================================================
        # TEST 1: CONFIRM ACTION
        # ==================================================
        action_id = "test-confirm-action"

        proposal = {
            "amount": 500,
            "description": "Test expense",
            "category_id": "test-category",
            "account_id": "test-account",
            "is_personal": True,
            "payments": [
                {
                    "person_id": "self",
                    "amount": 500,
                }
            ],
            "splits": [],
        }

        create_pending_action(
            db=db,
            action_id=action_id,
            session_id=session.id,
            action_type="expense",
            proposal=proposal,
        )

        print("\nBEFORE CONFIRM:")
        action = get_pending_action(
            db=db,
            action_id=action_id,
            session_id=session.id,
        )
        print(action.id)
        print(action.status)

        result = confirm_action(
            db=db,
            action_id=action_id,
            session_id=session.id,
            client=FakeClient(),
        )

        print("\nCONFIRM RESULT:")
        print(result)

        print("\nAFTER CONFIRM:")
        action = get_pending_action(
            db=db,
            action_id=action_id,
            session_id=session.id,
        )

        print(action.id)
        print(action.status)

        # ==================================================
        # TEST 2: REJECT ACTION
        # ==================================================
        reject_id = "test-reject-action"

        create_pending_action(
            db=db,
            action_id=reject_id,
            session_id=session.id,
            action_type="expense",
            proposal=proposal,
        )

        print("\nBEFORE REJECT:")
        action = get_pending_action(
            db=db,
            action_id=reject_id,
            session_id=session.id,
        )
        print(action.id)
        print(action.status)

        result = reject_action(
            db=db,
            action_id=reject_id,
            session_id=session.id,
        )

        print("\nREJECT RESULT:")
        print(result)

        print("\nAFTER REJECT:")
        action = get_pending_action(
            db=db,
            action_id=reject_id,
            session_id=session.id,
        )

        print(action.id)
        print(action.status)

    finally:
        db.close()


if __name__ == "__main__":
    main()
