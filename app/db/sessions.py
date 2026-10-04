import uuid

from sqlalchemy.orm import Session as DBSession

from .models import Session


def create_session(db: DBSession) -> Session:
    session = Session(
        id=str(uuid.uuid4()),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(
    db: DBSession,
    session_id: str,
) -> Session | None:
    return db.get(Session, session_id)
