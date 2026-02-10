# tests/test_pipeline.py
import pytest
import logging
from unittest.mock import patch, MagicMock, mock_open
from src.schemas import GameRankCreate, GameStatistics, GameMechanic
from src.pipeline import (
    gather_game_id_names_ranks_from_html_pages,
    gather_statistics_from_ids,
    collect_and_store_game_ranks,
    collect_and_store_statistics,
    collect_and_store_mechanics,
    main_pipeline,
)

mock_game_rank_1 = GameRankCreate(id=1, rank=1, name="Brass: Birmingham")
mock_game_rank_2 = GameRankCreate(id=2, rank=2, name="Ark Nova")
mock_game_stats = GameStatistics(
    id=1, description="A game", year_published=2020,
    min_players=2, max_players=4, suggested_num_player=3,
    min_age=12, average_rating=7.5, average_weight=3.2,
)
mock_game_mechanic = GameMechanic(id=1, mechanic="Dice Rolling")


# ------------ Testing gather_game_id_names_ranks_from_html_pages ------------
@patch("src.pipeline.parse_html_ranking_page")
@patch("src.pipeline.get_html_last_page_number")
@patch("src.pipeline.HTMLPages")
def test_gather_ranks_happy_path(MockHTMLPages, mock_last_page, mock_parse):
    instance = MockHTMLPages.return_value
    instance.fetch_ranking_page.return_value = "<html>page1</html>"
    instance.fetch_ranking_pages.return_value = ["<html>page2</html>"]
    mock_last_page.return_value = 2
    mock_parse.return_value = [mock_game_rank_1]

    result = gather_game_id_names_ranks_from_html_pages()

    assert len(result) == 2
    assert all(isinstance(r, GameRankCreate) for r in result)


@patch("src.pipeline.HTMLPages")
def test_gather_ranks_page1_none_raises(MockHTMLPages):
    instance = MockHTMLPages.return_value
    instance.fetch_ranking_page.return_value = None

    with pytest.raises(ValueError, match="Page 1 has not been fetched correctly"):
        gather_game_id_names_ranks_from_html_pages()


@patch("src.pipeline.HTMLPages")
def test_gather_ranks_page1_none_logs_error(MockHTMLPages, caplog):
    instance = MockHTMLPages.return_value
    instance.fetch_ranking_page.return_value = None

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            gather_game_id_names_ranks_from_html_pages()
    assert "PAGE 1 HAS NOT BEEN FETCHED CORRECTLY" in caplog.text


@patch("src.pipeline.get_html_last_page_number")
@patch("src.pipeline.HTMLPages")
def test_gather_ranks_max_page_none_raises(MockHTMLPages, mock_last_page):
    instance = MockHTMLPages.return_value
    instance.fetch_ranking_page.return_value = "<html>page1</html>"
    mock_last_page.return_value = None

    with pytest.raises(ValueError, match="Could not find a max page number"):
        gather_game_id_names_ranks_from_html_pages()


@patch("src.pipeline.parse_html_ranking_page")
@patch("src.pipeline.get_html_last_page_number")
@patch("src.pipeline.HTMLPages")
def test_gather_ranks_flattens_pages(MockHTMLPages, mock_last_page, mock_parse):
    instance = MockHTMLPages.return_value
    instance.fetch_ranking_page.return_value = "<html>page1</html>"
    instance.fetch_ranking_pages.return_value = ["<html>page2</html>", "<html>page3</html>"]
    mock_last_page.return_value = 3
    mock_parse.side_effect = [
        [mock_game_rank_1],
        [mock_game_rank_2],
        [GameRankCreate(id=3, rank=3, name="Spirit Island")],
    ]

    result = gather_game_id_names_ranks_from_html_pages()

    assert len(result) == 3
    assert result[0].name == "Brass: Birmingham"
    assert result[1].name == "Ark Nova"
    assert result[2].name == "Spirit Island"


# ------------ Testing gather_statistics_from_ids ------------
@patch("src.pipeline.XMLAPI")
@patch("src.pipeline.parse_xml_page_for_statistics")
def test_gather_statistics_happy_path(mock_parse, MockXMLAPI):
    instance = MockXMLAPI.return_value
    instance.get_request.return_value = "<xml>content</xml>"
    mock_parse.return_value = mock_game_stats

    result = gather_statistics_from_ids([1, 2])

    assert len(result) == 2
    assert all(isinstance(r, GameStatistics) for r in result)
    assert instance.create_request.call_count == 2
    assert instance.save_xml_file.call_count == 2


@patch("src.pipeline.XMLAPI")
def test_gather_statistics_skips_failed_ids(MockXMLAPI, caplog):
    instance = MockXMLAPI.return_value
    instance.get_request.return_value = None

    with caplog.at_level(logging.WARNING):
        result = gather_statistics_from_ids([1])

    assert len(result) == 0
    assert "Failed to get xml_page for boardgame id: 1" in caplog.text


@patch("src.pipeline.XMLAPI")
def test_gather_statistics_empty_ids(MockXMLAPI):
    result = gather_statistics_from_ids([])
    assert result == []


@patch("src.pipeline.XMLAPI")
@patch("src.pipeline.parse_xml_page_for_statistics")
def test_gather_statistics_saves_xml_files(mock_parse, MockXMLAPI):
    instance = MockXMLAPI.return_value
    instance.get_request.return_value = "<xml>content</xml>"
    mock_parse.return_value = mock_game_stats

    gather_statistics_from_ids([1])

    instance.save_xml_file.assert_called_once_with(
        file_name="1.xml",
        xml_content="<xml>content</xml>",
    )


# ------------ Testing collect_and_store_game_ranks ------------
@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.gather_game_id_names_ranks_from_html_pages")
def test_collect_store_ranks_calls_gather_and_import(mock_gather, mock_import):
    mock_gather.return_value = [mock_game_rank_1]
    mock_db = MagicMock()

    collect_and_store_game_ranks(mock_db)

    mock_gather.assert_called_once()
    mock_import.assert_called_once()
    # Verify the correct table is passed
    call_args = mock_import.call_args
    assert call_args.kwargs["table"].__tablename__ == "Games"


@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.gather_game_id_names_ranks_from_html_pages")
def test_collect_store_ranks_returns_data(mock_gather, mock_import):
    mock_gather.return_value = [mock_game_rank_1, mock_game_rank_2]
    mock_db = MagicMock()

    result = collect_and_store_game_ranks(mock_db)

    assert len(result) == 2
    assert result[0].name == "Brass: Birmingham"


# ------------ Testing collect_and_store_statistics ------------
@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.gather_statistics_from_ids")
def test_collect_store_statistics_calls_gather_and_import(mock_gather, mock_import):
    mock_gather.return_value = [mock_game_stats]
    mock_db = MagicMock()

    collect_and_store_statistics(mock_db, boardgame_ids=[1])

    mock_gather.assert_called_once_with(boardgame_ids=[1])
    mock_import.assert_called_once()
    call_args = mock_import.call_args
    assert call_args.kwargs["table"].__tablename__ == "Statistics"


# ------------ Testing collect_and_store_mechanics ------------
@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.parse_xml_page_for_game_mechanics")
@patch("src.pipeline.glob")
def test_collect_store_mechanics_happy_path(mock_glob, mock_parse, mock_import):
    mock_glob.return_value = ["data/raw_xml/123.xml"]
    mock_parse.return_value = [mock_game_mechanic]
    mock_db = MagicMock()

    with patch("builtins.open", mock_open(read_data="<xml>content</xml>")):
        collect_and_store_mechanics(mock_db)

    mock_import.assert_called_once()
    call_args = mock_import.call_args
    assert call_args.kwargs["table"].__tablename__ == "Mechanics"
    assert len(call_args.kwargs["data_to_import"]) == 1


@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.parse_xml_page_for_game_mechanics")
@patch("src.pipeline.glob")
def test_collect_store_mechanics_extracts_id_from_filename(mock_glob, mock_parse, mock_import):
    mock_glob.return_value = ["data/raw_xml/456.xml"]
    mock_parse.return_value = [mock_game_mechanic]
    mock_db = MagicMock()

    with patch("builtins.open", mock_open(read_data="<xml>content</xml>")):
        collect_and_store_mechanics(mock_db)

    mock_parse.assert_called_once_with(
        boardgame_id=456,
        xml_content="<xml>content</xml>",
    )


@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.parse_xml_page_for_game_mechanics")
@patch("src.pipeline.glob")
def test_collect_store_mechanics_skips_none(mock_glob, mock_parse, mock_import):
    mock_glob.return_value = ["data/raw_xml/123.xml"]
    mock_parse.return_value = None
    mock_db = MagicMock()

    with patch("builtins.open", mock_open(read_data="<xml>content</xml>")):
        collect_and_store_mechanics(mock_db)

    call_args = mock_import.call_args
    assert len(call_args.kwargs["data_to_import"]) == 0


@patch("src.pipeline.bulk_import_into_database")
@patch("src.pipeline.glob")
def test_collect_store_mechanics_no_files(mock_glob, mock_import):
    mock_glob.return_value = []
    mock_db = MagicMock()

    collect_and_store_mechanics(mock_db)

    mock_import.assert_called_once()
    call_args = mock_import.call_args
    assert len(call_args.kwargs["data_to_import"]) == 0


# ------------ Testing main_pipeline ------------
@patch("src.pipeline.collect_and_store_mechanics")
@patch("src.pipeline.collect_and_store_statistics")
@patch("src.pipeline.collect_and_store_game_ranks")
@patch("src.pipeline.get_db_session")
def test_main_pipeline_orchestration(mock_session, mock_ranks, mock_stats, mock_mechs):
    mock_db = MagicMock()
    mock_session.return_value.__enter__ = MagicMock(return_value=mock_db)
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    mock_ranks.return_value = [mock_game_rank_1]

    main_pipeline()

    mock_ranks.assert_called_once_with(mock_db)
    mock_stats.assert_called_once()
    mock_mechs.assert_called_once_with(mock_db)


@patch("src.pipeline.collect_and_store_mechanics")
@patch("src.pipeline.collect_and_store_statistics")
@patch("src.pipeline.collect_and_store_game_ranks")
@patch("src.pipeline.get_db_session")
def test_main_pipeline_passes_ids(mock_session, mock_ranks, mock_stats, mock_mechs):
    mock_db = MagicMock()
    mock_session.return_value.__enter__ = MagicMock(return_value=mock_db)
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    mock_ranks.return_value = [mock_game_rank_1, mock_game_rank_2]

    main_pipeline()

    # collect_and_store_statistics(db, boardgame_ids) uses positional args
    call_args = mock_stats.call_args
    assert call_args[0][1] == [1, 2]


@patch("src.pipeline.collect_and_store_mechanics")
@patch("src.pipeline.collect_and_store_statistics")
@patch("src.pipeline.collect_and_store_game_ranks")
@patch("src.pipeline.get_db_session")
def test_main_pipeline_logs_completion(mock_session, mock_ranks, mock_stats, mock_mechs, caplog):
    mock_db = MagicMock()
    mock_session.return_value.__enter__ = MagicMock(return_value=mock_db)
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    mock_ranks.return_value = []

    with caplog.at_level(logging.INFO):
        main_pipeline()

    assert "THE PIPELINE HAS FINISHED RUNNING" in caplog.text
