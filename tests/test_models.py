# tests/test_models.py
from sqlalchemy import inspect
from src.models import Game, Statistics, Mechanics


# ------------ Testing Game model ------------
def test_game_table_columns(in_memory_engine):
    inspector = inspect(in_memory_engine)
    columns = {col["name"] for col in inspector.get_columns("Games")}
    assert columns == {"id", "rank", "name"}


def test_game_insert_and_query(in_memory_session):
    game = Game(id=1, rank=1, name="Chess")
    in_memory_session.add(game)
    in_memory_session.flush()

    result = in_memory_session.query(Game).first()
    assert result.id == 1
    assert result.rank == 1
    assert result.name == "Chess"


def test_game_repr():
    game = Game(id=1, name="Chess")
    assert repr(game) == "<Game(id=1, name='Chess')"


# ------------ Testing Statistics model ------------
def test_statistics_table_columns(in_memory_engine):
    inspector = inspect(in_memory_engine)
    columns = {col["name"] for col in inspector.get_columns("Statistics")}
    assert columns == {
        "id", "description", "year_published", "min_players",
        "max_players", "suggested_num_player", "min_age",
        "average_rating", "average_weight",
    }


def test_statistics_insert_and_query(in_memory_session):
    game = Game(id=1, rank=1, name="Chess")
    in_memory_session.add(game)
    in_memory_session.flush()

    stats = Statistics(
        id=1, description="A classic game", year_published=1475,
        min_players=2, max_players=2, suggested_num_player=2,
        min_age=6, average_rating=7.5, average_weight=3.2,
    )
    in_memory_session.add(stats)
    in_memory_session.flush()

    result = in_memory_session.query(Statistics).first()
    assert result.id == 1
    assert result.description == "A classic game"
    assert result.year_published == 1475
    assert result.average_rating == 7.5


def test_statistics_foreign_key(in_memory_session):
    game = Game(id=42, rank=1, name="Go")
    in_memory_session.add(game)
    in_memory_session.flush()

    stats = Statistics(id=42, description="Ancient game", year_published=-2000,
                       min_players=2, max_players=2, suggested_num_player=2,
                       min_age=8, average_rating=8.0, average_weight=4.0)
    in_memory_session.add(stats)
    in_memory_session.flush()

    result = in_memory_session.query(Statistics).filter_by(id=42).first()
    assert result is not None
    assert result.id == game.id


def test_statistics_repr():
    stats = Statistics(id=1)
    assert repr(stats) == "<Statistics object for boardgame of id 1>"


# ------------ Testing Mechanics model ------------
def test_mechanics_table_columns(in_memory_engine):
    inspector = inspect(in_memory_engine)
    columns = {col["name"] for col in inspector.get_columns("Mechanics")}
    assert columns == {"id", "mechanic"}


def test_mechanics_insert_and_query(in_memory_session):
    game = Game(id=1, rank=1, name="Catan")
    in_memory_session.add(game)
    in_memory_session.flush()

    mech = Mechanics(id=1, mechanic="Dice Rolling")
    in_memory_session.add(mech)
    in_memory_session.flush()

    result = in_memory_session.query(Mechanics).first()
    assert result.id == 1
    assert result.mechanic == "Dice Rolling"


def test_mechanics_repr():
    mech = Mechanics(id=1, mechanic="Dice Rolling")
    assert repr(mech) == "<boardgame of id: 1 has the mechanic: Dice Rolling>"
