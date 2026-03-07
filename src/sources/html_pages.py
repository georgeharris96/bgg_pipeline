# src/sources/html_pages.py
from playwright.sync_api import sync_playwright, BrowserContext
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
            delay_s: float = 2.0,
            jitter_s: float = 1.0,
            ) -> None:
        """Initialises the HTMLPages fetcher.

        Args:
            base_url (str, optional): The base URL for BoardGameGeek.
                Defaults to "https://boardgamegeek.com".
            delay_s (float, optional): The delay in seconds between consecutive
                requests to avoid overloading the server. Defaults to 2.0.
            jitter_s (float, optional): The jitter in seconds to add randomness
                to request timing. Defaults to 1.0.
        """
        self.base_url = base_url.rstrip("/")
        self.limiter = RateLimiter(delay_s=delay_s, jitter_s=jitter_s)

    def _create_browser_context(self) -> tuple:
        """Creates a Playwright instance, browser, and context.

        Returns:
            tuple: (playwright_instance, browser, context)
        """
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/145.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        return pw, browser, context

    def fetch_ranking_page(self, page: int, context: BrowserContext | None = None) -> str | None:
        """Fetches a single ranking page from BoardGameGeek.

        Args:
            page (int): The page number of the rankings to fetch.
            context (BrowserContext, optional): An existing Playwright browser context.
                If None, a new browser will be launched and closed after the request.

        Returns:
            str | None: The raw HTML content of the requested page, or None on failure.
        """
        url = f"{self.base_url}/browse/boardgame/page/{page}"
        pw = browser = browser_page = None
        owns_context = context is None

        try:
            if owns_context:
                pw, browser, context = self._create_browser_context()

            self.limiter.wait()
            assert context is not None
            browser_page = context.new_page()
            logger.info(f"Requesting URL: {url}")
            response = browser_page.goto(url, wait_until="networkidle")

            if response is None:
                logger.error(f"Request failed for URL: {url}")
                return None

            logger.info(f"Landing URL: {response.url} | Status: {response.status}")
            if response.status != 200:
                logger.error(f"The following URL ({url}) returned with a {response.status} status code")
                return None
            else:
                return browser_page.content()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        finally:
            if browser_page:
                browser_page.close()
            if owns_context:
                if context:
                    context.close()
                if browser:
                    browser.close()
                if pw:
                    pw.stop()

    def fetch_ranking_pages(self, start: int, stop: int) -> list[str]:
        """Fetches multiple ranking pages from BoardGameGeek.

        Args:
            start (int): The starting page number (inclusive).
            stop (int): The ending page number (inclusive).

        Returns:
            List[str]: A list of raw HTML content for each requested page.
        """
        html_pages = []
        pw, browser, context = self._create_browser_context()
        try:
            for page_number in range(start, stop + 1):
                html_pages.append(
                    self.fetch_ranking_page(
                        page=page_number,
                        context=context
                    )
                )
        finally:
            context.close()
            browser.close()
            pw.stop()
        return html_pages

    @staticmethod
    def save_html_file(file_name: str, html_content: str, save_location: str = "data/raw_html"):
        """A static method to save a HTML file to a location

        Args:
            file_name (str): The name you wish to call your file
            html_content (str): The raw text of the html you wish to save
            save_location (str): The folder location you wish to save the file to.
                By default this is set to data/raw_html
        """
        with open(f"{save_location}/{file_name}", "w", encoding="utf-8") as file:
            file.write(html_content)
