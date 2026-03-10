import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.append(src_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base


@pytest.fixture(autouse=True)
def patch_init_db():
    with patch("src.pipeline.init_db"):
        yield


@pytest.fixture
def in_memory_engine():
    """Creates an in-memory SQLite engine with all tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def in_memory_session(in_memory_engine):
    """Provides a clean SQLAlchemy session for each test."""
    Session = sessionmaker(bind=in_memory_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
