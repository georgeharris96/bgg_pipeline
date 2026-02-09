# src/utils/make_request.py
from utils.throttler import RateLimiter
import httpx

def make_request(limiter: RateLimiter, url: str, bearer_token: str | None = None) -> httpx.Response:
    """
    some text 

    Args:

    Returns:
    
    """
    limiter.wait()
    if bearer_token is not None:
        headers = {
                "Authorization": f"Bearer {bearer_token}"
            }
        response = httpx.get(url, headers=headers)
    else:
        response = httpx.get(url)
    return response
