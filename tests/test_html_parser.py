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
import logging

valid_mock_html_content = """
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

invalid_mock_html_content = """
"<html>This html content will fail to parse and will trigger the logging</html>"
"""

# ------------ Testing extract_game_ids_and_names ------------
def test_extract_game_ids_and_names_type():
    output = extract_game_ids_and_names(BeautifulSoup(valid_mock_html_content, "html.parser"))
    assert isinstance(output, list)
    assert all(isinstance(x, tuple) for x in output)


def test_extract_game_ids_and_names_ouput():
    output = extract_game_ids_and_names(BeautifulSoup(valid_mock_html_content, "html.parser"))
    assert len(output) == 2
    assert output[0] == (224517, "Brass: Birmingham")
    assert output[1] == (342942, "Ark Nova")


def test_extract_game_ids_and_names_html_without_correct_tags():
    with pytest.raises(ValueError):
        output = extract_game_ids_and_names(BeautifulSoup(invalid_mock_html_content, "html.parser"))
        print(output)

# ------------ Testing extract_game_ranks ------------
def test_extract_game_ranks_type():
    output = extract_game_ranks(BeautifulSoup(valid_mock_html_content, "html.parser"))
    assert isinstance(output, list)
    assert all(isinstance(x, int) for x in output)


def test_extract_game_ranks_output():
    output = extract_game_ranks(BeautifulSoup(valid_mock_html_content, "html.parser"))
    assert len(output) == 2
    assert output == [1, 2]


def test_extract_game_ranks_error_handling():
    with pytest.raises(ValueError):
        output = extract_game_ranks(BeautifulSoup(invalid_mock_html_content, "html.parser"))

# ------------ Testing parse_html_ranking_page ------------
def test_parse_html_ranking_page_type():
    output = parse_html_ranking_page(html_content=valid_mock_html_content)
    assert isinstance(output, list)
    assert all(item.__class__.__name__ == 'GameRankCreate' for item in output)


def test_parse_html_ranking_page_output():
    output = parse_html_ranking_page(html_content=valid_mock_html_content)
    assert output is not None, "Your mock html hasn't worked!"

    expected_results = [
        (224517, 1, "Brass: Birmingham"),
        (342942, 2, "Ark Nova")
    ]
    for i, (expected_id, expected_rank, expected_name) in enumerate(expected_results):
        assert output[i].id == expected_id
        assert output[i].rank == expected_rank
        assert output[i].name == expected_name


def test_parse_html_ranking_page_logging(caplog):
    caplog.set_level(logging.ERROR)
    output = parse_html_ranking_page(invalid_mock_html_content)
    assert "HTML content failed to parse with error:" in caplog.text


# ------------ Testing get_html_last_page_number ------------
def test_get_html_last_page_number_type():
    assert type(get_html_last_page_number(valid_mock_html_content)) == int


def test_get_html_last_page_number_output():
    assert get_html_last_page_number(valid_mock_html_content) == 1727


def test_get_html_last_page_number_without_correct_tags():
    with pytest.raises(ValueError):
        get_html_last_page_number(invalid_mock_html_content)