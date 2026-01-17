# src/pipeline.py
from database import engine, Base, SessionLocal
from models import Game
from schemas import GameRankCreate
from sources.html_pages import HTMLPages
from parsers.html_parsers import parse_html_ranking_page, get_html_last_page_number
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


def main_pipeline() -> None:
    # Initialise the database
    Base.metadata.create_all(bind=engine)

    # Collect and process game ids, names and ranks
    logger.info("STARTING TO GATHER GAME IDS, NAMES AND RANKS")
    collected_game_ids_names_ranks = gather_game_id_names_ranks_from_html_pages()
    logger.info("COMPLETED GATHERING GAME IDS, NAMES AND RANKS")

    logger.info("GETTING LOCAL DB SESSION")
    db = SessionLocal()
    try:
        games = [
            {
                "id": item.id,
                "name": item.name,
                "rank": item.rank
            } for item in collected_game_ids_names_ranks
        ]
        logger.info("INSERTING GAME IDS, NAMES AND RANKS INTO DB")
        db.bulk_insert_mappings(Game, games) # type: ignore
        logger.info("COMMITING TO DB")
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"BULK INSERT OF GAME IDS, NAMES AND RANKS FAILED WITH FOLLOWING ERROR: \n{e}")
        raise e
    
    finally:
        db.close()


main_pipeline()