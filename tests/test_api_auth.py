# tests/test_api_auth.py
import pytest
from unittest.mock import patch, mock_open
from src.utils.api_auth import get_bgg_auth


# ------------ Testing get_bgg_auth ------------
def test_get_bgg_auth_reads_token():
    with patch("builtins.open", mock_open(read_data="my_secret_token\n")):
        result = get_bgg_auth()
        assert result == "my_secret_token\n"


def test_get_bgg_auth_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            get_bgg_auth()


def test_get_bgg_auth_empty_file():
    with patch("builtins.open", mock_open(read_data="")):
        result = get_bgg_auth()
        assert result == ""
