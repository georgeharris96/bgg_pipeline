# tests/test_logging_config.py
import logging
from unittest.mock import patch
from src.utils.logging_config import setup_logging


# ------------ Testing setup_logging ------------
@patch("src.utils.logging_config.logging.FileHandler")
def test_setup_logging_returns_logger(mock_file_handler):
    result = setup_logging()
    assert isinstance(result, logging.Logger)


@patch("src.utils.logging_config.logging.FileHandler")
def test_setup_logging_calls_basic_config(mock_file_handler):
    """Verify setup_logging configures basicConfig with INFO level.
    Note: basicConfig is a no-op if root logger already has handlers,
    so we patch it to verify the call arguments."""
    with patch("src.utils.logging_config.logging.basicConfig") as mock_config:
        setup_logging()
        mock_config.assert_called_once()
        call_kwargs = mock_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO


def test_httpx_logger_warning_level():
    httpx_logger = logging.getLogger("httpx")
    assert httpx_logger.level == logging.WARNING
