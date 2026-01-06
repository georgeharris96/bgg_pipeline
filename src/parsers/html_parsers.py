# src/parsers/html_parsers.py
from bs4 import BeautifulSoup
from schemas import GameRankCreate
import re


def extract_game_ids_and_names(soup: BeautifulSoup) -> list[tuple[int, str]]:
    """Takes a BeautifulSoup object and extracts the game ids and names
    
    Args:
        soup (BeautifulSoup): The BeautifulSoup object set to html.parser

    Returns:
        game_ids_and_names (list[tuple[int, str]]): A list of tuples containing the game id and name in that order
    """
    a_tags = soup.find_all("a", class_="primary")
    game_ids_and_names = []
    for tag in a_tags:
        game_id = int(tag.get("href").split("/")[2]) # Extract game ID from the href
        game_name = tag.text # Extract game name from text
        game_ids_and_names.append((game_id, game_name))
    return game_ids_and_names


def extract_game_ranks(soup: BeautifulSoup) -> list[int]:
    """Takes a BeautifulSoup object and extracts the game ranks in the same order as the game ids and names
    
    Args:
        soup (BeautifulSoup): The BeautifulSoup object set to html.parser

    Returns:
        game_ids_and_names (list[int]): A list of ints containing the ranks on the parsed html page
    """
    td_tags = soup.find_all("td", class_="collection_rank")
    game_ranks = []
    for tag in td_tags:
        game_ranks.append(int(re.sub("[\n\t]", "", tag.text)))
    return game_ranks



def parse_html_ranking_page(html_content: str) -> list[GameRankCreate]:
    """Takes html content in string format, and using BS4, extracts the game id, name and rank.
    
    Args:
        html_content (str): The html content from BGG that needs to be parsed.

    Returns:
        games (list[GameRankCreate]): A list of pydantic validation objects which contains a games id, rank and name.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    game_ids_and_names = extract_game_ids_and_names(soup=soup)
    game_ranks = extract_game_ranks(soup=soup)

    games = []
    for (game_id, game_name), rank in zip(game_ids_and_names, game_ranks):
        games.append(
            GameRankCreate(
                id=game_id,
                rank=rank,
                name=game_name
            )
        )
    return games


def get_html_last_page_number(html_content:str) -> int:
    """Takes html content in string format, and using BS4, extracts the last page number.
    
    Args:
        html_content (str): The html content from BGG that needs to be parsed.

    Returns:
        page_number (int): The last page number of the bgg browse pages.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    page_number_as_str = soup.find("a", {"title": "last page"}).text
    page_number = int(page_number_as_str[1:-1])
    return page_number

