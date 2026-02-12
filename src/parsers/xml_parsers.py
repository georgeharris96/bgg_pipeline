# src/parsers/xml_parsers.py
import re
from bs4 import BeautifulSoup
from schemas import GameStatistics, GameMechanic
from utils.logging_config import setup_logging


logger = setup_logging()


def _extract_int_value(soup: BeautifulSoup, tag_name: str, display_name: str) -> int:
    """Extracts an integer value from an XML tag's 'value' attribute.

    Args:
        soup: The parsed XML content.
        tag_name: The name of the XML tag to find.
        display_name: A human-readable name for error messages.

    Returns:
        int: The extracted integer value.

    Raises:
        ValueError: If the tag is not found or the value is not a valid integer.
    """
    tag = soup.find(tag_name)
    if tag is None:
        raise ValueError(f"{display_name} tag cannot be found!")

    value = tag.get("value")
    if isinstance(value, str) and re.match(r"^[0-9]+$", value):
        return int(value)
    else:
        raise ValueError(f"{display_name} value is invalid: {value}")


def _extract_float_value(soup: BeautifulSoup, tag_name: str, display_name: str) -> float:
    """Extracts a float value from an XML tag's 'value' attribute.

    Args:
        soup: The parsed XML content.
        tag_name: The name of the XML tag to find.
        display_name: A human-readable name for error messages.

    Returns:
        float: The extracted float value.

    Raises:
        ValueError: If the tag is not found or the value is not a valid number.
    """
    tag = soup.find(tag_name)
    if tag is None:
        raise ValueError(f"{display_name} tag cannot be found!")

    value = tag.get("value")
    if isinstance(value, str) and re.match(r"^[0-9]+(\.[0-9]+)?$", value):
        return float(value)
    else:
        raise ValueError(f"{display_name} value is invalid: {value}")


def extract_description(soup: BeautifulSoup) -> str:
    """
    Extracts the description from the parsed XML/HTML content.

    Args:
        soup (BeautifulSoup): The parsed XML/HTML content from which to extract the description.

    Returns:
        str: The description text, or None if not found or if there's an error in extraction.
    """
    description_tag = soup.find("description")
    if description_tag is None:
        raise ValueError("Description tag cannot be found!")

    value = description_tag.text
    if isinstance(value, str):
        return value
    else:
        raise ValueError(f"Description value is the wrong type: {value}")



def extract_year_published(soup: BeautifulSoup) -> int:
    """Extracts the year published from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        int: The year published.

    Raises:
        ValueError: If the tag is not found or the value is not a valid integer.
    """
    return _extract_int_value(soup, "yearpublished", "Year Published")


def extract_min_players(soup: BeautifulSoup) -> int:
    """Extracts the minimum number of players from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        int: The minimum number of players.

    Raises:
        ValueError: If the tag is not found or the value is not a valid integer.
    """
    return _extract_int_value(soup, "minplayers", "Min Players")


def extract_max_players(soup: BeautifulSoup) -> int:
    """Extracts the maximum number of players from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        int: The maximum number of players.

    Raises:
        ValueError: If the tag is not found or the value is not a valid integer.
    """
    return _extract_int_value(soup, "maxplayers", "Max Players")


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
    """Extracts the minimum age recommendation from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        int: The minimum age recommendation.

    Raises:
        ValueError: If the tag is not found or the value is not a valid integer.
    """
    return _extract_int_value(soup, "minage", "Min Age")


def extract_average_rating(soup: BeautifulSoup) -> float:
    """Extracts the average rating from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        float: The average rating.

    Raises:
        ValueError: If the tag is not found or the value is not a valid number.
    """
    return _extract_float_value(soup, "average", "Average Rating")


def extract_average_weight(soup: BeautifulSoup) -> float:
    """Extracts the average weight from the parsed XML content.

    Args:
        soup: The parsed XML content.

    Returns:
        float: The average weight.

    Raises:
        ValueError: If the tag is not found or the value is not a valid number.
    """
    return _extract_float_value(soup, "averageweight", "Average Weight")


def parse_xml_page_for_statistics(xml_content: str, boardgame_id: int) -> GameStatistics | None:
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


def parse_xml_page_for_game_mechanics(xml_content: str, boardgame_id: int) -> list[GameMechanic] | None:
    try:
        soup = BeautifulSoup(xml_content, "xml")
    except Exception as e:
        logger.error(f"Failed to parse XML content for boardgame id = {boardgame_id}: {e}")
        return None
    
    # Find all the mechanics
    mechanic_tags = soup.find_all("boardgamemechanic")

    if mechanic_tags is None:
        logger.warning(f"Boardgame id = {boardgame_id} has no mechanics")
        return None
    
    else:
        game_mechanics = []
        for tag in mechanic_tags:
            tag_value = tag.get("value")
            if isinstance(tag_value, str):
                game_mechanics.append(GameMechanic(id=boardgame_id, mechanic=tag_value))
            else:
                pass
        return game_mechanics
