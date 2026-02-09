# src/pipeline.py
from database import bulk_import_into_database, get_db_session
from models import Game, Statistics
from schemas import GameRankCreate, GameStatistics
from sources.html_pages import HTMLPages
from sources.xml_api import XMLAPI
from parsers.html_parsers import parse_html_ranking_page, get_html_last_page_number
from parsers.xml_parsers import parse_xml_page
from utils.logging_config import setup_logging
from itertools import chain


logger = setup_logging()


def gather_game_id_names_ranks_from_html_pages() -> list[GameRankCreate]:
    """
    Brings together the html pages source and the parsers to gather the game ids, names and ranks from the browse page on bgg's website.

    Returns:
        collected_game_ids_names_ranks (list[GameRankCreate]): Returns a list of GameRankCreate objects, which is a pydantic validator.
    """
    html_pages = HTMLPages()
    page_1 = html_pages.fetch_ranking_page(page=1)

    if page_1 == None:
        logger.error("PAGE 1 HAS NOT BEEN FETCHED CORRECTLY!")
        raise ValueError("Page 1 has not been fetched correctly!")
    
    else:
        max_page_number = get_html_last_page_number(page_1)

        if max_page_number != None:
            collected_pages = html_pages.fetch_ranking_pages(start=2, stop=max_page_number)
            collected_pages.insert(0, page_1)

            collected_game_ids_names_ranks = []

            for page in collected_pages:
                collected_game_ids_names_ranks.append(parse_html_ranking_page(page))
            
            # bring these together
            collected_game_ids_names_ranks = list(chain.from_iterable(collected_game_ids_names_ranks))

            return collected_game_ids_names_ranks
        else:
            logger.error("COUILD NOT FIND A MAX PAGE NUMBER FROM PAGE 1!")
            raise ValueError("Could not find a max page number from page 1!")


def gather_statistics_from_ids(boardgame_ids: list[int]) -> list[GameStatistics]:
    """
    Brings together the api data source and the xml parsers to gather the statistics about each game.
    
    Args:
        boardgame_ids (list[int]): A list of boardgame ids which you want to gather statistics on. 
    Returns:
        boardgame_statistics (list[GameStatistics]): Returns a list of GameStatistic objects, which is a pydantic validator.
    """
    bgg_api = XMLAPI()
    boardgame_statistics = []

    for id in boardgame_ids:
        # Create request url
        bgg_api.create_request(
            boardgame_id=id,
            stats=True,
        )

        # Get XML
        xml_page = bgg_api.get_request()

        if xml_page is None:
            logger.warning(f"Failed to get xml_page for boardgame id: {id} \n moving on")

        else:
            # Parse infomation
            boardgame_statistics.append(
                parse_xml_page(
                    xml_content=xml_page, boardgame_id=id
                    )
            )

    return boardgame_statistics


def collect_and_store_game_ranks(db) -> list[GameRankCreate]:
    """
    Gathers game ids, names and ranks from BGG HTML pages and stores them in the database.

    Returns:
        collected_game_ids_names_ranks (list[GameRankCreate]): The collected game data, for extracting IDs for the next phase.
    """
    logger.info("STARTING TO GATHER GAME IDS, NAMES AND RANKS")
    collected_game_ids_names_ranks = gather_game_id_names_ranks_from_html_pages()
    logger.info("COMPLETED GATHERING GAME IDS, NAMES AND RANKS")

    logger.info("INSERTING GAME IDS, NAMES AND RANKS INTO DB")
    bulk_import_into_database(
        database_session=db,
        table=Game,
        data_to_import=collected_game_ids_names_ranks
    )

    return collected_game_ids_names_ranks


def collect_and_store_statistics(db, boardgame_ids: list[int]) -> None:
    """
    Gathers statistics for each game from the BGG XML API and stores them in the database.
    """
    logger.info("STARTING TO GATHER XML DOCUMENTS")
    boardgame_statistics = gather_statistics_from_ids(boardgame_ids=boardgame_ids)

    logger.info("INSERTING GAME STATISTICS INTO DB")
    bulk_import_into_database(
        database_session=db,
        table=Statistics,
        data_to_import=boardgame_statistics
    )


def main_pipeline() -> None:
    """
    The main pipeline for collecting BGG boardgame names, ranks and statistics.

    Outputs a sqlite database in the data/ directory.
    """
    with get_db_session() as db:
        game_ranks = collect_and_store_game_ranks(db)
        boardgame_ids = [game.id for game in game_ranks]
        collect_and_store_statistics(db, boardgame_ids)


if __name__ == "__main__":
    main_pipeline()
