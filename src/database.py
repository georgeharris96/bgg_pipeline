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

# Create all tables defined in your models.
Base.metadata.create_all(bind=engine)


def bulk_import_into_database(database_session: Session, table: type[Base], data_to_import: Sequence[BaseModel]) -> None:
    database_session.bulk_insert_mappings(
        table, # type: ignore
        [game_object.model_dump() for game_object in data_to_import]
    )


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

