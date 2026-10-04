from .database import SessionLocal
from .sessions import create_session, get_session


def main():
    db = SessionLocal()

    try:
        # Create
        session = create_session(db)

        print("CREATED:")
        print("id:", session.id)
        print("created_at:", session.created_at)
        print("updated_at:", session.updated_at)

        # Read
        loaded = get_session(
            db=db,
            session_id=session.id,
        )

        print("\nREAD:")
        print("id:", loaded.id)
        print("created_at:", loaded.created_at)
        print("updated_at:", loaded.updated_at)

    finally:
        db.close()


if __name__ == "__main__":
    main()
