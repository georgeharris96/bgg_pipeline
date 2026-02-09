# tests/test_xml_parser.py
from src.parsers.xml_parsers import (
    extract_description,
    extract_year_published,
    extract_min_players,
    extract_max_players,
    extract_suggested_num_player,
    extract_min_age,
    extract_average_rating,
    extract_average_weight,
    parse_xml_page,
)
from src.schemas import GameStatistics
from bs4 import BeautifulSoup
import pytest
import logging

valid_mock_xml_content = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="174430">
        <yearpublished value="2015" />
        <minplayers value="2" />
        <maxplayers value="4" />
        <minage value="12" />
        <description value="A strategic board game about building civilizations." />
        <poll name="suggested_numplayers" title="User Suggested Number of Players" totalvotes="100">
            <results numplayers="1">
                <result value="Best" numvotes="5" />
                <result value="Recommended" numvotes="10" />
                <result value="Not Recommended" numvotes="85" />
            </results>
            <results numplayers="2">
                <result value="Best" numvotes="30" />
                <result value="Recommended" numvotes="50" />
                <result value="Not Recommended" numvotes="20" />
            </results>
            <results numplayers="3">
                <result value="Best" numvotes="65" />
                <result value="Recommended" numvotes="30" />
                <result value="Not Recommended" numvotes="5" />
            </results>
            <results numplayers="4">
                <result value="Best" numvotes="40" />
                <result value="Recommended" numvotes="50" />
                <result value="Not Recommended" numvotes="10" />
            </results>
        </poll>
        <statistics>
            <ratings>
                <average value="7.5" />
            </ratings>
            <averageweight value="3.2" />
        </statistics>
    </boardgame>
</boardgames>
"""

invalid_mock_xml_content = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="999999">
        <invalidtag value="invalid" />
    </boardgame>
</boardgames>
"""

xml_content_missing_description = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="174430">
        <yearpublished value="2015" />
    </boardgame>
</boardgames>
"""

xml_content_missing_year = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="174430">
        <description value="A game" />
    </boardgame>
</boardgames>
"""

xml_content_invalid_year = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="174430">
        <yearpublished value="invalid_year" />
    </boardgame>
</boardgames>
"""

xml_content_missing_poll = """
<?xml version="1.0" encoding="utf-8"?>
<boardgames>
    <boardgame objectid="174430">
        <poll name="other_poll" title="Other Poll">
        </poll>
    </boardgame>
</boardgames>
"""

# ------------ Testing extract_description ------------
def test_extract_description_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_description(soup)
    assert isinstance(output, str)


def test_extract_description_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_description(soup)
    assert output == "A strategic board game about building civilizations."


def test_extract_description_missing_tag():
    soup = BeautifulSoup(xml_content_missing_description, "xml")
    with pytest.raises(ValueError, match="Description tag cannot be found!"):
        extract_description(soup)


# ------------ Testing extract_year_published ------------
def test_extract_year_published_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_year_published(soup)
    assert isinstance(output, int)


def test_extract_year_published_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_year_published(soup)
    assert output == 2015


def test_extract_year_published_missing_tag():
    soup = BeautifulSoup(xml_content_missing_year, "xml")
    with pytest.raises(ValueError, match="Year Published tag cannot be found!"):
        extract_year_published(soup)


def test_extract_year_published_invalid_value():
    soup = BeautifulSoup(xml_content_invalid_year, "xml")
    with pytest.raises(ValueError, match="Year Published value is invalid"):
        extract_year_published(soup)


# ------------ Testing extract_min_players ------------
def test_extract_min_players_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_min_players(soup)
    assert isinstance(output, int)


def test_extract_min_players_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_min_players(soup)
    assert output == 2


def test_extract_min_players_missing_tag():
    soup = BeautifulSoup(invalid_mock_xml_content, "xml")
    with pytest.raises(ValueError, match="Min Players tag cannot be found!"):
        extract_min_players(soup)


# ------------ Testing extract_max_players ------------
def test_extract_max_players_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_max_players(soup)
    assert isinstance(output, int)


def test_extract_max_players_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_max_players(soup)
    assert output == 4


def test_extract_max_players_missing_tag():
    soup = BeautifulSoup(invalid_mock_xml_content, "xml")
    with pytest.raises(ValueError, match="Max Players tag cannot be found!"):
        extract_max_players(soup)


# ------------ Testing extract_suggested_num_player ------------
def test_extract_suggested_num_player_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_suggested_num_player(soup)
    assert isinstance(output, int)


def test_extract_suggested_num_player_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_suggested_num_player(soup)
    assert output == 3  # 3 players has 65 "Best" votes, which is the highest


def test_extract_suggested_num_player_missing_poll():
    soup = BeautifulSoup(xml_content_missing_poll, "xml")
    with pytest.raises(ValueError, match="Suggested Number of Players Poll cannot be found!"):
        extract_suggested_num_player(soup)


# ------------ Testing extract_min_age ------------
def test_extract_min_age_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_min_age(soup)
    assert isinstance(output, int)


def test_extract_min_age_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_min_age(soup)
    assert output == 12


def test_extract_min_age_missing_tag():
    soup = BeautifulSoup(invalid_mock_xml_content, "xml")
    with pytest.raises(ValueError, match="Min Age tag cannot be found!"):
        extract_min_age(soup)


# ------------ Testing extract_average_rating ------------
def test_extract_average_rating_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_average_rating(soup)
    assert isinstance(output, float)


def test_extract_average_rating_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_average_rating(soup)
    assert output == 7.5


def test_extract_average_rating_missing_tag():
    soup = BeautifulSoup(invalid_mock_xml_content, "xml")
    with pytest.raises(ValueError, match="Average Rating tag cannot be found!"):
        extract_average_rating(soup)


# ------------ Testing extract_average_weight ------------
def test_extract_average_weight_type():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_average_weight(soup)
    assert isinstance(output, float)


def test_extract_average_weight_output():
    soup = BeautifulSoup(valid_mock_xml_content, "xml")
    output = extract_average_weight(soup)
    assert output == 3.2


def test_extract_average_weight_missing_tag():
    soup = BeautifulSoup(invalid_mock_xml_content, "xml")
    with pytest.raises(ValueError, match="Average Weight tag cannot be found!"):
        extract_average_weight(soup)


# ------------ Testing parse_xml_page ------------
def test_parse_xml_page_type():
    output = parse_xml_page(xml_content=valid_mock_xml_content, boardgame_id=174430)
    assert output is not None
    assert isinstance(output, GameStatistics)


def test_parse_xml_page_output():
    output = parse_xml_page(xml_content=valid_mock_xml_content, boardgame_id=174430)
    assert output is not None
    assert output.id == 174430
    assert output.description == "A strategic board game about building civilizations."
    assert output.year_published == 2015
    assert output.min_players == 2
    assert output.max_players == 4
    assert output.suggested_num_player == 3
    assert output.min_age == 12
    assert output.average_rating == 7.5
    assert output.average_weight == 3.2


def test_parse_xml_page_invalid_xml():
    malformed_xml = "<invalid><xml>content"
    output = parse_xml_page(xml_content=malformed_xml, boardgame_id=999999)
    assert output is None


def test_parse_xml_page_missing_required_fields():
    output = parse_xml_page(xml_content=invalid_mock_xml_content, boardgame_id=999999)
    assert output is None


def test_parse_xml_page_logging(caplog):
    caplog.set_level(logging.ERROR)
    output = parse_xml_page(xml_content=invalid_mock_xml_content, boardgame_id=999999)
    assert output is None
    assert "ValueError for boardgame id = 999999" in caplog.text
