# src/utils/throttler.py
import time


class RateLimiter:
    """
    Ensure at least `delay_s` seconds elapse between successive `wait()` calls.
    """

    def __init__(self, delay_s: float, jitter_s: float = 0.0) -> None:
        """
        Sleep- if the last call was too recent. Call this right before a request.
        """
        self.delay_s = float(delay_s)
        self.jitter_s = float(jitter_s)
        self._last_ts: float = 0.0

    def wait(self) -> None:
        """
        Checks the time elasped between previous and current calls.
        if the time is less than required wait till it is. Else, it carries on and sets new time.
        """
        now = time.time()
        elapsed = now - self._last_ts
        needed = self.delay_s - elapsed
        if needed > 0:
            time.sleep(needed + (self.jitter_s * 0.5)) # tiny fixed jitter if set
        self._last_ts = time.time()
