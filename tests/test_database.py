# tests/test_database.py
import pytest
import logging
from unittest.mock import patch, MagicMock
from src.models import Game, Statistics, Mechanics
from src.schemas import GameRankCreate, GameStatistics, GameMechanic
from src.database import bulk_import_into_database, get_db_session


# ------------ Testing bulk_import_into_database ------------
def test_bulk_import_game_data(in_memory_session):
    data = [
        GameRankCreate(id=1, rank=1, name="Brass: Birmingham"),
        GameRankCreate(id=2, rank=2, name="Ark Nova"),
    ]
    bulk_import_into_database(in_memory_session, Game, data)
    in_memory_session.commit()

    results = in_memory_session.query(Game).all()
    assert len(results) == 2
    assert results[0].name == "Brass: Birmingham"
    assert results[1].name == "Ark Nova"


def test_bulk_import_statistics_data(in_memory_session):
    game = Game(id=1, rank=1, name="Test Game")
    in_memory_session.add(game)
    in_memory_session.commit()

    data = [
        GameStatistics(
            id=1, description="A game", year_published=2020,
            min_players=2, max_players=4, suggested_num_player=3,
            min_age=12, average_rating=7.5, average_weight=3.2,
        )
    ]
    bulk_import_into_database(in_memory_session, Statistics, data)
    in_memory_session.commit()

    results = in_memory_session.query(Statistics).all()
    assert len(results) == 1
    assert results[0].description == "A game"


def test_bulk_import_mechanics_data(in_memory_session):
    game = Game(id=1, rank=1, name="Test Game")
    in_memory_session.add(game)
    in_memory_session.commit()

    data = [
        GameMechanic(id=1, mechanic="Dice Rolling"),
    ]
    bulk_import_into_database(in_memory_session, Mechanics, data)
    in_memory_session.commit()

    results = in_memory_session.query(Mechanics).all()
    assert len(results) == 1
    assert results[0].mechanic == "Dice Rolling"


def test_bulk_import_empty_list(in_memory_session):
    bulk_import_into_database(in_memory_session, Game, [])
    in_memory_session.commit()

    results = in_memory_session.query(Game).all()
    assert len(results) == 0


# ------------ Testing get_db_session ------------
def test_get_db_session_commits_on_success():
    mock_session = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session):
        with get_db_session() as session:
            assert session is mock_session
        mock_session.commit.assert_called_once()


def test_get_db_session_rollback_on_error():
    mock_session = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session):
        with pytest.raises(RuntimeError):
            with get_db_session() as session:
                raise RuntimeError("test error")
        mock_session.rollback.assert_called_once()


def test_get_db_session_logs_error(caplog):
    mock_session = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError):
                with get_db_session():
                    raise RuntimeError("test error")
        assert "DATABASE SESSION ERROR" in caplog.text


def test_get_db_session_reraises_exception():
    mock_session = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session):
        with pytest.raises(ValueError, match="specific error"):
            with get_db_session():
                raise ValueError("specific error")


def test_get_db_session_closes_session():
    mock_session = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session):
        with get_db_session():
            pass
        mock_session.close.assert_called_once()

    # Also verify close is called on error
    mock_session_2 = MagicMock()
    with patch("src.database.SessionLocal", return_value=mock_session_2):
        with pytest.raises(RuntimeError):
            with get_db_session():
                raise RuntimeError("error")
        mock_session_2.close.assert_called_once()
