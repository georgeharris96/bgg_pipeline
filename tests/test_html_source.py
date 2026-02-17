# tests/test_html_source.py
import pytest
import logging
from unittest.mock import patch, MagicMock, mock_open
from src.sources.html_pages import HTMLPages


def _mock_context(status=200, content="<html>Mocked content</html>"):
    """Helper to build a mock BrowserContext with a mock page and response."""
    mock_response = MagicMock()
    mock_response.status = status

    mock_page = MagicMock()
    mock_page.goto.return_value = mock_response
    mock_page.content.return_value = content

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page
    return mock_ctx


# ------------ Testing fetch_ranking_page ------------
def test_fetch_ranking_page_output():
    html_pages = HTMLPages(delay_s=0.0)
    output = html_pages.fetch_ranking_page(page=1, context=_mock_context())
    assert output == "<html>Mocked content</html>"


def test_fetch_ranking_page_type():
    html_pages = HTMLPages(delay_s=0.0)
    output = html_pages.fetch_ranking_page(page=1, context=_mock_context())
    assert type(output) == str


def test_fetch_ranking_page_on_non_200_status_code(caplog):
    caplog.set_level(logging.ERROR)
    html_pages = HTMLPages(delay_s=0.0)
    output = html_pages.fetch_ranking_page(page=1, context=_mock_context(status=403))
    assert output is None
    assert "returned with a 403 status code" in caplog.text


def test_fetch_ranking_page_on_none_response(caplog):
    caplog.set_level(logging.ERROR)
    html_pages = HTMLPages(delay_s=0.0)

    mock_page = MagicMock()
    mock_page.goto.return_value = None

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page

    output = html_pages.fetch_ranking_page(page=1, context=mock_ctx)
    assert output is None
    assert "Request failed for URL:" in caplog.text


def test_fetch_ranking_page_creates_and_closes_browser():
    html_pages = HTMLPages(delay_s=0.0)

    mock_response = MagicMock()
    mock_response.status = 200

    mock_page = MagicMock()
    mock_page.goto.return_value = mock_response
    mock_page.content.return_value = "<html>standalone</html>"

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_ctx

    mock_pw = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser

    with patch("src.sources.html_pages.sync_playwright") as mock_sync_pw:
        mock_sync_pw.return_value.start.return_value = mock_pw

        output = html_pages.fetch_ranking_page(page=1)

        assert output == "<html>standalone</html>"
        mock_pw.chromium.launch.assert_called_once_with(headless=True)
        mock_page.close.assert_called_once()
        mock_ctx.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_pw.stop.assert_called_once()


# ------------ Testing fetch_ranking_pages ------------
def test_fetch_ranking_pages_type():
    html_pages = HTMLPages(delay_s=0.0)

    with patch.object(html_pages, "_create_browser_context") as mock_create:
        mock_ctx = _mock_context()
        mock_create.return_value = (MagicMock(), MagicMock(), mock_ctx)

        output = html_pages.fetch_ranking_pages(start=1, stop=2)
        assert type(output) == list
        assert len(output) == 2


def test_fetch_ranking_pages_output():
    html_pages = HTMLPages(delay_s=0.0)

    with patch.object(html_pages, "_create_browser_context") as mock_create:
        mock_ctx = _mock_context()
        mock_create.return_value = (MagicMock(), MagicMock(), mock_ctx)

        output = html_pages.fetch_ranking_pages(start=1, stop=2)
        assert output == ["<html>Mocked content</html>", "<html>Mocked content</html>"]


def test_fetch_ranking_pages_error_handling(caplog):
    caplog.set_level(logging.ERROR)
    html_pages = HTMLPages(delay_s=0.0)

    with patch.object(html_pages, "_create_browser_context") as mock_create:
        mock_ctx = _mock_context(status=404)
        mock_create.return_value = (MagicMock(), MagicMock(), mock_ctx)

        output = html_pages.fetch_ranking_pages(start=1, stop=2)
        assert "returned with a 404 status code" in caplog.text


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
