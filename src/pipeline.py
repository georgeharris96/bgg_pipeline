# src/pipeline.py
from database import engine, Base, SessionLocal
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
            logger.warning("Failed to get xml_page for boardgame id: {id} \n moving on")

        else:
            # Parse infomation
            boardgame_statistics.append(
                parse_xml_page(
                    xml_content=xml_page, boardgame_id=id
                    )
            )

    return boardgame_statistics


def main_pipeline() -> None:
    """
    The main pipeline for collecting BGG boardgame names, ranks and statistics. 
    
    This function creates the sqlite database, collects game ids, names and ranks

    This function outputs a sqlite database in the 
    """

    # Initialise the database
    Base.metadata.create_all(bind=engine)

    # Collect and process game ids, names and ranks
    logger.info("STARTING TO GATHER GAME IDS, NAMES AND RANKS")
    collected_game_ids_names_ranks = gather_game_id_names_ranks_from_html_pages()
    logger.info("COMPLETED GATHERING GAME IDS, NAMES AND RANKS")

    # Create db local session
    logger.info("GETTING LOCAL DB SESSION")
    db = SessionLocal()

    # Try to insert game ids, names and ranks into db...
    try:
        logger.info("INSERTING GAME IDS, NAMES AND RANKS INTO DB")
        db.bulk_insert_mappings(
            Game, # type: ignore
            [game_object.model_dump() for game_object in collected_game_ids_names_ranks]
        )
        logger.info("COMMITING GAME IDS, NAMES AND RANKS TO DB")
        db.commit()
    # If there is an error... Log the error, rollback, close the db and raise the error.
    except Exception as e:
        db.rollback()
        logger.error(f"BULK INSERT OF GAME IDS, NAMES AND RANKS FAILED WITH FOLLOWING ERROR: \n{e}")
        db.close()
        raise e

    # Collect and process game statistics
    boardgame_ids = [game_object.id for game_object in collected_game_ids_names_ranks]
    logger.info("STARTING TO GATHER XML DOCUMENTS")
    boardgame_statistics = gather_statistics_from_ids(
        boardgame_ids=boardgame_ids
        )
    
    # Try to insert game statistics into db..
    try:
        logger.info("INSERTING GAME STATISTICS INTO DB")
        db.bulk_insert_mappings(
            Statistics, # type: ignore
            [stats_object.model_dump() for stats_object in boardgame_statistics]
        )
        logger.info("COMMITING STATS TO DB")
        db.commit()
    # If there is an error... Log the error, rollback, close the db and raise the error.
    except Exception as e:
        db.rollback()
        logger.error(f"BULK INSERT OF GAME STATISTICS FAILED WITH THE FOLLOWING ERROR: \n {e}")
        db.close()
        raise e

    # Finally close the database session
    finally:
        db.close()


if __name__ == "__main__":
    main_pipeline()
