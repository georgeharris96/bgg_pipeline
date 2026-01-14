# tests/test_parsers.py
from src.parsers.html_parsers import (
    extract_game_ids_and_names, 
    extract_game_ranks, 
    parse_html_ranking_page,
    get_html_last_page_number,
    )
from src.schemas import GameRankCreate
from bs4 import BeautifulSoup
import pytest

mock_html_content = """
<!DOCTYPE html>
<html>
<body>
    <div id="maincontent">
        <div class="infobox">
            <a href="/browse/boardgame/page/1727" title="last page">[1727]</a>
        </div>

        <table id="collectionitems">
            <tr id="row_">
                <td class="collection_rank">
                    1
                </td>
                <td class="collection_objectname">
                    <a href="/boardgame/224517/brass-birmingham" class="primary">Brass: Birmingham</a>
                </td>
            </tr>
            <tr id="row_">
                <td class="collection_rank">
                    2
                </td>
                <td class="collection_objectname">
                    <a href="/boardgame/342942/ark-nova" class="primary">Ark Nova</a>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""

# ------------ Testing extract_game_ids_and_names ------------
def test_extract_game_ids_and_names_type():
    output = extract_game_ids_and_names(BeautifulSoup(mock_html_content, "html.parser"))
    assert isinstance(output, list)
    assert all(isinstance(x, tuple) for x in output)

def test_extract_game_ids_and_names_ouput():
    output = extract_game_ids_and_names(BeautifulSoup(mock_html_content, "html.parser"))
    assert len(output) == 2
    assert output[0] == (224517, "Brass: Birmingham")
    assert output[1] == (342942, "Ark Nova")

# TODO create test for the logging


# ------------ Testing extract_game_ranks ------------
def test_extract_game_ranks_type():
    output = extract_game_ranks(BeautifulSoup(mock_html_content, "html.parser"))
    assert isinstance(output, list)
    assert all(isinstance(x, int) for x in output)

def test_extract_game_ranks_output():
    output = extract_game_ranks(BeautifulSoup(mock_html_content, "html.parser"))
    assert len(output) == 2
    assert output == [1, 2]

# TODO create test for the logging

# ------------ Testing parse_html_ranking_page ------------
def test_parse_html_ranking_page_type():
    output = parse_html_ranking_page(html_content=mock_html_content)
    assert isinstance(output, list)
    assert all(item.__class__.__name__ == 'GameRankCreate' for item in output)

def test_parse_html_ranking_page_output():
    output = parse_html_ranking_page(html_content=mock_html_content)
    assert output is not None, "Your mock html hasn't worked!"

    expected_results = [
        (224517, 1, "Brass: Birmingham"),
        (342942, 2, "Ark Nova")
    ]
    for i, (expected_id, expected_rank, expected_name) in enumerate(expected_results):
        assert output[i].id == expected_id
        assert output[i].rank == expected_rank
        assert output[i].name == expected_name

# TODO create test for the logging


# ------------ Testing get_html_last_page_number ------------
def test_get_html_last_page_number_type():
    assert type(get_html_last_page_number(mock_html_content)) == int

def test_get_html_last_page_number_output():
    assert get_html_last_page_number(mock_html_content) == 1727

# TODO create test for the logging
