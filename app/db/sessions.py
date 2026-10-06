import uuid

from sqlalchemy.orm import Session as DBSession

from .models import Session


def create_session(
    db: DBSession,
    auth_key: str,
) -> Session:
    session = Session(
        id=str(uuid.uuid4()),
        auth_key=auth_key,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(
    db: DBSession,
    session_id: str,
    auth_key: str,
) -> Session | None:
    return (
        db
        .query(Session)
        .filter(
            Session.id == session_id,
            Session.auth_key == auth_key,
        )
        .first()
    )
