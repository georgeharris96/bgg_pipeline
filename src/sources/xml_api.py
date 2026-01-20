# src/sources/xml_api.py
import httpx
from utils.logging_config import setup_logging
from utils.throttler import RateLimiter
from utils.api_auth import get_bgg_auth


logger = setup_logging()

class XMLAPI:
    """Fetches XML documents from BoardGameGeek's XML2 API.

    This class provides the methods to get raw XML from BoardGameGeek's XML2 API, 
    with built-in rate limiting to avoid overwhelming the servber
    """

    def __init__(
            self,
            base_url: str = "https://boardgamegeek.com/xmlapi2/",
            user_agent: str = "xml_api_scraper/0.1",
            delay_s: float = 2.0,
            ) -> None:
        """Initialises the XMLAPI fetcher.

        Args:
            base_url (str, optional): The base URL for the XML2 API.
                Defaults to "https://boardgamegeek.com/xmlapi2/".
            user_agent (str, optional): The User-Agent string to use in requests.
                Defaults to "xml_api_scraper/0.1",
            delay_s (float, optional): The delay in seconds between consecutive requests
                to avoid overloading the server. Defaults to 2.0
        """
        self.base_url = base_url
        self.user_agent = user_agent
        self.limiter = RateLimiter(delay_s=delay_s)
        self.next_request_url = ""

    
    def create_request(self, boardgame_id: int, stats: bool = False) -> None:
        """Creates the URL for an upcoming api request. 

        Args:
            boardgame_id (int): The id of the boardgame you are looking to gather 
                information on.
            stats (bool, optional): A flag used to mark your desire to gather the 
                stats of the boardgame. Defaults to False. 
        """
        contents = [f"thing?={boardgame_id}"]
        if stats:
            contents.append("&stats=1")

        self.next_request_url: str = self.base_url.join(contents)


    def get_request(self) -> str | None:
        """Uses `self.next_request_url` to get the response from the next request.

        Returns:
            respons.text (str): The raw xml assoicated with the request.
            None: If the request fails to yeild a 200 status or you have not used the
                create_request method it will fail.
        """
        if self.next_request_url != "":
            headers = {
                "Authorization": f"Bearer {get_bgg_auth()}"
            }
            self.limiter.wait()
            response = httpx.get(self.next_request_url, headers=headers)
            if response.status_code != 200:
                logger.error(f"The following URL failed: '{self.base_url}'\nwith status code: {response.status_code}")
            else:
                return response.text
        else:
            raise ValueError("Please create a request before")
        

    @staticmethod
    def save_xml_file(file_name: str, xml_content: str, save_location: str = "data/raw_xmls"):
        """A static method to save a XML file to a location
        
        Args:
            file_name (str): The name you wish to call your file
            xml_content (str): The raw text of the html you wish to save
            save_location (str): The folder location you wish to save the file to.
                By default this is set to data/raw_html
        """
        with open(f"{save_location}/{file_name}", "w", encoding="utf-8") as file:
            file.write(xml_content)
            
            