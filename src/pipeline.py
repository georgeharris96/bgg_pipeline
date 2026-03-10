# src/pipeline.py
from database import bulk_import_into_database, get_db_session, init_db
from models import Game, Statistics, Mechanics
from schemas import GameRankCreate, GameStatistics, GameMechanic
from sources.html_pages import HTMLPages
from sources.xml_api import XMLAPI
from parsers.html_parsers import parse_html_ranking_page, get_html_last_page_number
from parsers.xml_parsers import parse_xml_page_for_statistics, parse_xml_page_for_game_mechanics
from utils.logging_config import setup_logging
from itertools import chain
from glob import glob
from pathlib import Path


logger = setup_logging()


def gather_game_id_names_ranks_from_html_pages() -> list[GameRankCreate]:
    """
    Brings together the html pages source and the parsers to gather the game ids, names and ranks from the browse page on bgg's website.

    Returns:
        collected_game_ids_names_ranks (list[GameRankCreate]): Returns a list of GameRankCreate objects, which is a pydantic validator.
    """
    html_pages = HTMLPages(
        delay_s=5,
        jitter_s=3
    )
    page_1 = html_pages.fetch_ranking_page(page=1)

    # Checks if page one has been found and if not... 
    if page_1 == None:
        # ...log that it has happend and raise a ValueError!
        logger.error("PAGE 1 HAS NOT BEEN FETCHED CORRECTLY!")
        raise ValueError("Page 1 has not been fetched correctly!")
    
    else:
        max_page_number = get_html_last_page_number(page_1)
        logger.info("FOUND FIRST RANKING PAGE. MOVING ON...")
        max_page_number = 10 # Overide the max page number for a smaller dataset

        # Checks if the max page number has been found....
        if max_page_number != None:
            # ... if it has then fetch the remaining ranking pages and start processing them
            collected_pages = html_pages.fetch_ranking_pages(start=2, stop=max_page_number)
            collected_pages.insert(0, page_1)

            collected_game_ids_names_ranks = []

            for page in collected_pages:
                parsed_page = parse_html_ranking_page(page)
                if parsed_page is not None:
                    collected_game_ids_names_ranks.append(parsed_page)
                else:
                    logger.warning("A page failed to parse, skipping it.")

            # bring these together
            collected_game_ids_names_ranks = list(chain.from_iterable(collected_game_ids_names_ranks))

            return collected_game_ids_names_ranks
        else:
            # ... if not then log the error and raise a ValueError
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
    bgg_api = XMLAPI(
        delay_s=5,
        jitter_s=3
        )
    boardgame_statistics = []

    for id in boardgame_ids:
        # Create request url
        bgg_api.create_request(
            boardgame_id=id,
            stats=True,
        )

        # Get XML
        xml_page = bgg_api.get_request()

        # Check if the xml page has been retrieved correctly...
        if xml_page is None:
            # ...and if not log a warning to inform the user.
            logger.warning(f"Failed to get xml_page for boardgame id: {id} \n moving on")

        else:
            # ... if found, parse the information
            stats = parse_xml_page_for_statistics(
                xml_content=xml_page, boardgame_id=id
            )
            if stats is not None:
                boardgame_statistics.append(stats)
            else:
                logger.warning(f"Failed to parse statistics for boardgame id: {id}")
            bgg_api.save_xml_file(
                file_name=f"{id}.xml",
                xml_content=xml_page,
                ) # Save the xml file for later to save request allocation and to be considerate of BGG

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


def collect_and_store_mechanics(db) -> None:
    """
    Reads saved XML files from disk, extracts game mechanics from each, and stores them in the database.
    """
    logger.info("STARTING TO COLLECT AND STORE GAME MECHANICS")
    xml_file_names = glob("data/raw_xmls/*.xml")
    all_game_mechanics: list[GameMechanic] = []

    for file_name in xml_file_names:
        with open(file_name, "r") as file:
            game_mechanics = parse_xml_page_for_game_mechanics(
                boardgame_id=int(Path(file_name).stem),
                xml_content=file.read(),
            )
            if game_mechanics is not None:
                all_game_mechanics.extend(game_mechanics)

    logger.info("INSERTING GAME MECHANICS INTO DB")
    bulk_import_into_database(
        database_session=db,
        table=Mechanics,
        data_to_import=all_game_mechanics,
    )


def main_pipeline() -> None:
    """
    The main pipeline for collecting BGG boardgame names, ranks and statistics.

    Outputs a sqlite database in the data/ directory.
    """
    init_db()
    with get_db_session() as db:
        game_ranks = collect_and_store_game_ranks(db)
        boardgame_ids = [game.id for game in game_ranks]

    with get_db_session() as db:
        collect_and_store_statistics(db, boardgame_ids)

    with get_db_session() as db:
        collect_and_store_mechanics(db)
    logger.info("THE PIPELINE HAS FINISHED RUNNING")


if __name__ == "__main__":
    main_pipeline()
