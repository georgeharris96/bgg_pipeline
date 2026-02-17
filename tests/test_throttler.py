# tests/test_throttler.py
from unittest.mock import patch
from src.utils.throttler import RateLimiter


# ------------ Testing RateLimiter __init__ ------------
def test_init_defaults():
    limiter = RateLimiter(delay_s=1.0)
    assert limiter.delay_s == 1.0
    assert limiter.jitter_s == 0.0
    assert limiter._last_ts == 0.0


def test_init_with_jitter():
    limiter = RateLimiter(delay_s=2.0, jitter_s=0.5)
    assert limiter.delay_s == 2.0
    assert limiter.jitter_s == 0.5


# ------------ Testing RateLimiter wait ------------
@patch("src.utils.throttler.time.sleep")
@patch("src.utils.throttler.time.time")
def test_first_wait_no_sleep(mock_time, mock_sleep):
    mock_time.return_value = 1000.0
    limiter = RateLimiter(delay_s=1.0)

    limiter.wait()

    mock_sleep.assert_not_called()
    assert limiter._last_ts == 1000.0


@patch("src.utils.throttler.time.sleep")
@patch("src.utils.throttler.time.time")
def test_second_wait_sleeps(mock_time, mock_sleep):
    limiter = RateLimiter(delay_s=2.0)

    # First call at t=100
    mock_time.return_value = 100.0
    limiter.wait()

    # Second call at t=100.5 (only 0.5s elapsed, need 2.0s)
    mock_time.return_value = 100.5
    limiter.wait()

    mock_sleep.assert_called_once_with(1.5)


@patch("src.utils.throttler.time.sleep")
@patch("src.utils.throttler.time.time")
def test_no_sleep_after_sufficient_delay(mock_time, mock_sleep):
    limiter = RateLimiter(delay_s=1.0)

    # First call at t=100
    mock_time.return_value = 100.0
    limiter.wait()

    # Second call at t=102 (2s elapsed, only need 1s)
    mock_time.return_value = 102.0
    limiter.wait()

    mock_sleep.assert_not_called()


@patch("src.utils.throttler.time.sleep")
@patch("src.utils.throttler.time.time")
def test_zero_delay_no_sleep(mock_time, mock_sleep):
    mock_time.return_value = 100.0
    limiter = RateLimiter(delay_s=0.0)

    limiter.wait()
    limiter.wait()

    mock_sleep.assert_not_called()
