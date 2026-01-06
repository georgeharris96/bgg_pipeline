# src/parsers/html_parsers.py
from bs4 import BeautifulSoup
from schemas import GameRankCreate
import re


def extract_game_ids_and_names(soup):
    a_tags = soup.find_all("a", class_="primary")
    game_ids_and_names = []
    for tag in a_tags:
        game_id = int(tag.get("href").split("/")[2]) # Extract game ID from the href
        game_name = tag.text # Extract game name from text
        game_ids_and_names.append((game_id, game_name))
    return game_ids_and_names


def extract_game_ranks(soup):
    td_tags = soup.find_all("td", class_="collection_rank")
    game_ranks = []
    for tag in td_tags:
        game_ranks.append(int(re.sub("[\n\t]", "", tag.text)))
    return game_ranks



def parse_html_ranking_page(html_content: str) -> list[GameRankCreate] | None:
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