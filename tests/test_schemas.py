# tests/test_schemas.py
from src.schemas import GameRankCreate, GameStatistics, GameMechanic
from pydantic import ValidationError
from datetime import datetime
import pytest

# ------------ Testing GameRankCreate ------------
def test_valid_GameRankCreate():
    game = GameRankCreate(id=1, name="Chess", rank=1)
    assert game.id == 1
    assert game.name == "Chess"
    assert game.rank == 1


def test_invalid_GameRankCreate():
    with pytest.raises(ValidationError):
        GameRankCreate(id=-1, name="Chess", rank=1) # Test if the id validation works.
    with pytest.raises(ValidationError):
        GameRankCreate(id=1, name="Chess", rank=-1) # Test if the rank validation works.
    with pytest.raises(ValidationError):
        GameRankCreate(id=1, name=123, rank=1) # type: ignore Test if the name validation works.
    with pytest.raises(ValidationError):
        GameRankCreate() # type: ignore Test if the schema rejects empty values.
   

# ------------ Testing GameMechanic ------------
def test_valid_GameMechanic():
    game_mechanic = GameMechanic(id=1, mechanic_name="Grid Movement")
    assert game_mechanic.id == 1
    assert game_mechanic.mechanic_name == "Grid Movement"


def test_invalid_GameMechanic():
    with pytest.raises(ValidationError):
        GameMechanic() # type: ignore Test if schema rejects empty values.
    with pytest.raises(ValidationError):
        GameMechanic(id=-1, mechanic_name="Grid Movement") # Test if the id validation works.


# ------------ Testing GameStatistics ------------
def test_valid_GameStatistics():
    stat = GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
    )
    assert stat.id == 1
    assert stat.description == "Checkmate your opponent in this timeless abstract"
    assert stat.year_published == 1475
    assert stat.min_players == 2
    assert stat.max_players == 2
    assert stat.suggested_num_player == 2
    assert stat.min_age == 6
    assert stat.average_rating == 7.2
    assert stat.average_weight == 3.64


def test_invalid_GameStatistics():
    with pytest.raises(ValidationError):
        GameStatistics() # type: ignore Test if schema rejects empty values.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=-1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        ) # Test if id validation works.
    
    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description=1, # type: ignore
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if description validation works.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=-1,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if year_published won't accept negative numbers.
    
    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=datetime.now().year+1,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if year_published won't accept a future year.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1457,
        min_players=-2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if min_players won't accept a negative number.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1457,
        min_players=2,
        max_players=-2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if max_players won't accept a negative number.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1457,
        min_players=3,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        )  # Test if max_players can't be lower than min_players.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=-2,
        min_age=6,
        average_rating=7.2,
        average_weight=3.64,
        ) # Test if suggested_num_players validation works.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=-6,
        average_rating=7.2,
        average_weight=3.64,
        ) # Test if min_age validation works.

    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=-7.2,
        average_weight=3.64,
        ) # Test if average_rating validation works.
    
    with pytest.raises(ValidationError):
        GameStatistics(
        id=1,
        description="Checkmate your opponent in this timeless abstract",
        year_published=1475,
        min_players=2,
        max_players=2,
        suggested_num_player=2,
        min_age=6,
        average_rating=7.2,
        average_weight=-3.64,
        ) # Test if average_weight validation works.
    