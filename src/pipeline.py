# src/pipeline.py
from schemas import GameRankCreate
from sources.html_pages import HTMLPages
from parsers.html_parsers import parse_html_ranking_page, get_html_page_number
from itertools import chain


def gather_game_id_names_ranks_from_html_pages() -> list[GameRankCreate]:
    """
    Brings together the html pages source and the parsers to gather the game ids, names and ranks from the browse page on bgg's website.

    Returns:
        collected_game_ids_names_ranks (list[GameRankCreate]): Returns a list of GameRankCreate objects, which is a pydantic validator.
    """
    html_pages = HTMLPages()

    page_1 = html_pages.fetch_ranking_page(page=1)
    max_page_number = get_html_page_number(page_1)

    collected_pages = html_pages.fetch_ranking_pages(start=2, stop=max_page_number)
    collected_pages.insert(0, page_1)

    collected_game_ids_names_ranks = []

    for page in collected_pages:
        collected_game_ids_names_ranks.append(parse_html_ranking_page(page))
    
    # bring these together
    collected_game_ids_names_ranks = list(chain.from_iterable(collected_game_ids_names_ranks))

    return collected_game_ids_names_ranks


