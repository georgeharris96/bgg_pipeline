# src/utils/make_request.py
from utils.throttler import RateLimiter
import httpx
import logging

logger = logging.getLogger(__name__)

def make_request(limiter: RateLimiter, url: str, bearer_token: str | None = None) -> httpx.Response | None:
    """
    Makes a rate-limited HTTP GET request.

    Args:
        limiter (RateLimiter): Rate limiter to throttle requests.
        url (str): The URL to request.
        bearer_token (str | None): Optional bearer token for authentication.

    Returns:
        httpx.Response | None: The response, or None if the request failed.
    """
    limiter.wait()
    headers = {}
    if bearer_token is not None:
        headers["Authorization"] = f"Bearer {bearer_token.strip()}"

    try:
        response = httpx.get(url, headers=headers, timeout=30.0)
        return response
    except httpx.HTTPError as e:
        logger.error(f"HTTP request failed for {url}: {e}")
        return None
