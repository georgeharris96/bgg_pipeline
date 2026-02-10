# tests/test_make_requests.py
from unittest.mock import patch, MagicMock
import httpx
from src.utils.make_requests import make_request


# ------------ Testing make_request ------------
def test_make_request_without_token():
    mock_limiter = MagicMock()
    with patch("src.utils.make_requests.httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="OK")
        mock_get.return_value = mock_response

        result = make_request(limiter=mock_limiter, url="http://example.com")

        mock_get.assert_called_once_with("http://example.com")


def test_make_request_with_token():
    mock_limiter = MagicMock()
    with patch("src.utils.make_requests.httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="OK")
        mock_get.return_value = mock_response

        make_request(limiter=mock_limiter, url="http://example.com", bearer_token="my_token")

        mock_get.assert_called_once_with(
            "http://example.com",
            headers={"Authorization": "Bearer my_token"},
        )


def test_make_request_calls_limiter_wait():
    mock_limiter = MagicMock()
    with patch("src.utils.make_requests.httpx.get") as mock_get:
        mock_get.return_value = httpx.Response(200, text="OK")

        make_request(limiter=mock_limiter, url="http://example.com")

        mock_limiter.wait.assert_called_once()


def test_make_request_returns_response():
    mock_limiter = MagicMock()
    with patch("src.utils.make_requests.httpx.get") as mock_get:
        mock_response = httpx.Response(200, text="OK")
        mock_get.return_value = mock_response

        result = make_request(limiter=mock_limiter, url="http://example.com")

        assert result is mock_response
