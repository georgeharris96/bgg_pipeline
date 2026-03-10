#src/database.py
from contextlib import contextmanager
from collections.abc import Sequence
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from utils.logging_config import setup_logging

logger = setup_logging()

# Create the SQLite engine
DATABASE_URL = "sqlite:///./data/bgg_data.db"
engine = create_engine(DATABASE_URL)

# Create a configured Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Creates all database tables. Call this explicitly before running the pipeline."""
    Base.metadata.create_all(bind=engine)


def bulk_import_into_database(database_session: Session, table: type[Base], data_to_import: Sequence[BaseModel]) -> None:
    """Bulk inserts pydantic model data into a database table.

    Args:
        database_session: An active SQLAlchemy session.
        table: The SQLAlchemy model class to insert into.
        data_to_import: A sequence of pydantic models to insert.
    """
    database_session.bulk_insert_mappings(
        table, # type: ignore
        [game_object.model_dump() for game_object in data_to_import]
    )


@contextmanager
def get_db_session():
    """Provides a transactional database session as a context manager.

    Yields:
        Session: An active SQLAlchemy session.

    Raises:
        Exception: Re-raises any exception after rolling back the session and logging the error.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DATABASE SESSION ERROR: {e}")
        raise
    finally:
        db.close()

