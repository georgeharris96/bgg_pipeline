# src/parsers/xml_parsers.py
import re
from bs4 import BeautifulSoup
from src.schemas import GameStatistics
from utils.logging_config import setup_logging


logger = setup_logging()


def extract_description(soup: BeautifulSoup) -> str:
    """
    Extracts the description from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the description.

    Returns:
        str: The description text, or None if not found or if there's an error in extraction.
    """
    description_tag = soup.find_all("description")
    if description_tag is None:
        raise ValueError("Description tag cannot be found!")
    
    value = description_tag.value
    if isinstance(value, str):
        return value
    else:
        raise ValueError(f"Description value is the wrong type: {value}")



def extract_year_published(soup: BeautifulSoup) -> int:
    """
    Extracts the year published from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the year published.

    Returns:
        int: The year published, or None if not found or if there's an error in extraction.
    """
    year_published_tag = soup.find("yearpublished")

    if year_published_tag is None:
        raise ValueError("Year Published tag cannot be found!")
    
    value = year_published_tag.value
    if isinstance(value, str) and bool(re.match(r"^[0-9]+$", value)):
        return int(value)
    else:
        raise ValueError(f"Year Published value is invalid: {value}")


def extract_min_players(soup: BeautifulSoup) -> int:
    """
    Extracts the minimum number of players from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the minimum number of players.

    Returns:
        int: The minimum number of players, or None if not found or if there's an error in extraction.
    """
    min_players_tag = soup.find("minplayers")

    if min_players_tag is None:
        raise ValueError("Min Players tag cannot be found!")
    
    value = min_players_tag.value
    if isinstance(value, str) and bool(re.match(r"^[0-9]+$", value)):
        return int(value)
    else:
        raise ValueError(f"Min Players value is invalid: {value}")


def extract_max_players(soup: BeautifulSoup) -> int:
    """
    Extracts the maximum number of players from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the maximum number of players.

    Returns:
        int: The maximum number of players, or None if not found or if there's an error in extraction.
    """
    max_players_tag = soup.find("maxplayers")

    if max_players_tag is None:
        raise ValueError("Max Players tag cannot be found!")
    
    value = max_players_tag.value
    if isinstance(value, str) and bool(re.match(r"^[0-9]+$", value)):
        return int(value)
    else:
        raise ValueError(f"Max Players value is invalid: {value}")


def extract_suggested_num_player(soup: BeautifulSoup) -> int:
    """
    Extracts the suggested number of players from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the suggested number of players.

    Returns:
        int: The suggested number of players, or None if not found or if there's an error in extraction.
    """
    suggested_num_player_poll = soup.find("poll", {"name": "suggested_numplayers"})
    if suggested_num_player_poll is None:
        raise ValueError("Suggested Number of Players Poll cannot be found!")

    max_votes = -1
    best_num_players = None

    poll_results = suggested_num_player_poll.find_all("results")

    for result in poll_results:
        num_players = result.get("numplayers")
        best_result = result.find("result", {"value": "Best"})

        if best_result is None or num_players is None:
            raise ValueError("Failed to get results from poll!")

        num_votes_str = best_result.get("numvotes")
        if num_votes_str is None:
            raise ValueError("Failed to get numvotes from best result!")

        try:
            num_votes = int(num_votes_str) # type: ignore ignoring so pyright doesn't have a fit.
        except ValueError:
            raise ValueError(f"Invalid numvotes value: {num_votes_str}")

        if num_votes > max_votes:
            max_votes = num_votes
            best_num_players = num_players

    if best_num_players is None:
        raise ValueError("Failed to determine the best number of players!")

    try:
        return int(best_num_players) # type: ignore ignoring so pyright doesn't have a fit.
    except ValueError:
        raise ValueError(f"Invalid best_num_players value: {best_num_players}")

def extract_min_age(soup: BeautifulSoup) -> int:
    """
    Extracts the minimum age recommendation from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the minimum age.

    Returns:
        int: The minimum age recommendation, or None if not found or if there's an error in extraction.
    """
    min_age_tag = soup.find("minage")
    
    if min_age_tag is None:
        raise ValueError("Min Age tag cannot be found!")
    
    value = min_age_tag.value
    if isinstance(value, str) and re.match(r"^[0-9]+$", value):
        return int(value)
    else:
        raise ValueError(f"Min Age value is invalid: {value}")
    

def extract_average_rating(soup: BeautifulSoup) -> float:
    """
    Extracts the average rating from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the average rating.

    Returns:
        float: The average rating, or None if not found or if there's an error in extraction.
    """
    average_rating_tag = soup.find("average")

    if average_rating_tag is None:
        raise ValueError("Average Rating tag cannot be found!")
    
    value = average_rating_tag.value
    if isinstance(value, str) and re.match(r"^[0-9]+$", value):
        return float(value)
    else:
        raise ValueError(f"Average Rating value is invalid: {value}")


def extract_average_weight(soup: BeautifulSoup) -> float:
    """
    Extracts the average weight from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the average weight.

    Returns:
        float: The average weight, or None if not found or if there's an error in extraction.
    """
    average_weight_tag = soup.find("averageweight")
    
    if average_weight_tag is None:
        raise ValueError("Average Weight tag cannot be found!")
    
    value = average_weight_tag.value
    if isinstance(value, str) and re.match(r"^[0-9]+$", value):
        return float(value)
    else:
        raise ValueError(f"Average Weight value is invalid: {value}")


def parse_xml_page(xml_content: str, boardgame_id: int) -> GameStatistics | None:
    """
    Parses the XML content to extract board game statistics.

    Args:
        xml_content (str): The XML content to parse.
        boardgame_id (int): The ID of the board game.

    Returns:
        GameStatistics: An object containing various statistics about the board game, or None if there's an error in parsing.
    """
    try:
        soup = BeautifulSoup(xml_content, "xml")
    except Exception as e:
        logger.error(f"Failed to parse XML content for boardgame id = {boardgame_id}: {e}")
        return None
    
    try:
        boardgame_statistics = GameStatistics(
            id=boardgame_id,
            description=extract_description(soup),
            year_published=extract_year_published(soup),
            min_players=extract_min_players(soup),
            max_players=extract_max_players(soup),
            suggested_num_player=extract_suggested_num_player(soup),
            min_age=extract_min_age(soup),
            average_rating=extract_average_rating(soup),
            average_weight=extract_average_weight(soup),
        )
        return boardgame_statistics
    except TypeError as e:
        logger.error(f"TypeError for boardgame id = {boardgame_id}: {e}")
        return None
    except ValueError as e:
        logger.error(f"ValueError for boardgame id = {boardgame_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for boardgame id = {boardgame_id}: {e}")
        return None
    
    