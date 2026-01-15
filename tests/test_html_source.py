# tests/test_html_source.py
import pytest
import httpx
from unittest.mock import patch, mock_open
from src.sources.html_pages import HTMLPages


# ------------ Testing test_fetch_ranking_page ------------
def test_fetch_ranking_page_output():
    html_pages = HTMLPages(delay_s=0.0)

    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="<html>Mocked content</html>")
        mock_get.return_value = mock_response

        output = html_pages.fetch_ranking_page(page=1)
        assert output == "<html>Mocked content</html>"


def test_fetch_ranking_page_type():
    html_pages = HTMLPages(delay_s=0.0)

    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="<html>Mocked content</html>")
        mock_get.return_value = mock_response

        output = html_pages.fetch_ranking_page(page=1)
        assert type(output) == str
    
# TODO test logging on a non 200 status code request


# ------------ Testing test_fetch_ranking_page ------------
def test_fetch_ranking_pages_type():
    html_pages = HTMLPages(delay_s=0.0)

    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="<html>Mocked content</html>")
        mock_get.return_value = mock_response

        output = html_pages.fetch_ranking_pages(start=1, stop=2)
        assert type(output) == list
        assert len(output) == 2


def test_fetch_ranking_pages_output():
    html_pages = HTMLPages(delay_s=0.0)
    correct_output = ["<html>Mocked content</html>", "<html>Mocked content</html>"]

    with patch("httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="<html>Mocked content</html>")
        mock_get.return_value = mock_response

        output = html_pages.fetch_ranking_pages(start=1, stop=2)
        assert output == correct_output

# TODO test logging on a non 200 status code request


# ------------ Testing save_html_file ------------
def test_save_html_file():
    mock_content = "<html>Mocked content</html>"

    with patch("builtins.open", mock_open()) as mock_file:
        HTMLPages.save_html_file(
            file_name="test_file.html", 
            html_content=mock_content,
            save_location="",
            )

        mock_file.assert_called_once_with("/test_file.html", "w", encoding="utf-8")

        file_handle = mock_file()
        file_handle.write.assert_called_once_with(mock_content)