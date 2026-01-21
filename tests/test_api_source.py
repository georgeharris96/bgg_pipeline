# tests/test_api_source.py
import pytest
import logging
import httpx
from unittest.mock import patch, mock_open
from src.sources.xml_api import XMLAPI

base_bgg_api_url = "https://boardgamegeek.com/xmlapi2/"

# ------------ Testing request url creation ------------
def test_request_url_creation():
    xml_api = XMLAPI()
    xml_api.create_request(
        boardgame_id=123,
        stats=True,
    )
    assert xml_api.next_request_url == f"{base_bgg_api_url}thing?=123&stats=1"

    xml_api.create_request(
        boardgame_id=456,
    )
    assert xml_api.next_request_url == f"{base_bgg_api_url}thing?456"


# ------------ Testing getting requests from the api ------------
def test_fetching_a_request():
    xml_api = XMLAPI()
    xml_api.create_request(
        boardgame_id=123,
        stats=True,
    )
    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="<xml>Mocked Content<xml>")
        mock_get.return_value = mock_response

        output = xml_api.get_request()
        assert type(output) == str
        assert output == "<xml>Mocked Content<xml>"


# ------------ Testing saving a xml file ------------
def test_save_xml_file():
    mock_content = "<xml>Mocked Content<xml>"

    with patch("builtins.open", mock_open()) as mock_file:
        XMLAPI.save_xml_file(
            file_name="test_file.xml",
            xml_content=mock_content,
            save_location="",
        )

        mock_file.assert_called_once_with("/test_file.xml", "w", encoding="utf-8")

        file_handle = mock_file()
        file_handle.write.assert_called_once_with(mock_content)


# ------------ Testing error handling and logging ------------
def test_getting_a_request_without_a_url(caplog):
    xml_api = XMLAPI()

    with pytest.raises(ValueError):
        xml_api.get_request()


def test_getting_a_non_200_status_code(caplog):
    xml_api = XMLAPI()
    xml_api.create_request(boardgame_id=123)

    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(404, text="Not Found")
        mock_get.return_value = mock_response

        xml_api.get_request()
        assert "The following URL failed:" in caplog.text and "with status code:" in caplog.text
