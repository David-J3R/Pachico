from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from App.config import DatabaseConfig, config

engine = create_engine(
    DatabaseConfig.get_database_url(),
    echo=DatabaseConfig.ECHO,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager that yields a SQLAlchemy session with commit/rollback handling.

    Honors the DB_FORCE_ROLL_BACK config flag for test isolation.
    """
    session = SessionLocal()
    try:
        yield session
        if config.DB_FORCE_ROLL_BACK:
            session.rollback()
        else:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
