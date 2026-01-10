# src/sources/html_pages.py
import httpx
from utils.logging_config import setup_logging
from utils.throttler import RateLimiter

logger = setup_logging()

class HTMLPages:
    """Fetches HTML ranking pages without parsing the HTML.

    This class provides the methods to download raw HTML from BoardGameGeeek (BGG)
    ranking pages, with built-in rate limiting to avoid overwhelming the server
    """

    def __init__(
            self,
            base_url: str = "https://boardgamegeek.com",
            user_agent: str = "bgg-kaggle-scrapper/0.1",
            delay_s: float = 2.0,
            ) -> None:
        """Initialises the HTMLPages fetcher.

        Args:
            base_url (str, optional): The base URL for BoardGameGeek. 
                Defaults to "https://boardgamegeek.com".
            user_agent (str, optional): The User-Agent string to use in requests.
                Defaults to "bgg-kaggle-scraper/0.1".
            delay_s (float, optional): The delay in seconds between consecutive 
                requests to avoid overloading the server. Defaults to 2.0.
        """
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.limiter = RateLimiter(delay_s=delay_s)

    def fetch_ranking_page(self, page: int) -> str | None:
        """Fetches a single ranking page from BoardGameGeek.

        Args:
            page (int): The page number of the rankings to fetch.

        Returns:
            str: The raw HTML content of the requested page.
        """
        url = f"{self.base_url}/browse/boardgame/page/{page}"
        self.limiter.wait()
        response = httpx.get(url)
        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"The following URL failed to return status code 200: {url}")

    def fetch_ranking_pages(self, start:int, stop: int) -> list[str]:
        """Fetches multiple ranking pages from BoardGameGeek.

        Args:
            start (int): The starting page number (inclusive).
            stop (int): The ending page number (inclusive).

        Returns:
            List[str]: A list of raw HTML content for each requested page.
        """
        html_pages = []
        for page_number in range(start, stop+1):
            html_pages.append(self.fetch_ranking_page(page = page_number))
        return html_pages
    
    @staticmethod
    def save_html_file(self, file_name: str, html_content: str, save_location:str = "data/raw_html"):
        """A static method to save a HTML file to a location
        
        Args:
            file_name (str): The name you wish to call your file
            html_content (str): The raw text of the html you wish to save
            save_location (str): The folder location you wish to save the file to.
                By default this is set to data/raw_html
        """
        with open(f"{save_location}/{file_name}", "w", encoding="utf-8") as file:
            file.write(html_content)

