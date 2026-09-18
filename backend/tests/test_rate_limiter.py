import pytest
import time
from unittest.mock import MagicMock, patch


def make_rate_limiter():
    """Create a RateLimiter with a mocked Redis client."""
    from app.services.rate_limiter import RateLimiter
    with patch("app.services.rate_limiter.get_redis") as mock_get_redis:
        limiter = RateLimiter()
        return limiter, mock_get_redis


def test_rate_limiter_allows_under_limit():
    from app.services.rate_limiter import RateLimiter
    limiter = RateLimiter()

    with patch("app.services.rate_limiter.get_redis") as mock_get_redis:
        mock_r = MagicMock()
        mock_get_redis.return_value = mock_r
        # Simulate 2 existing requests (under limit of 5)
        mock_r.pipeline.return_value.__enter__ = MagicMock()
        mock_r.pipeline.return_value.execute.return_value = [None, 2, None, None]
        mock_r.pipeline.return_value.__exit__ = MagicMock(return_value=False)

        pipe = MagicMock()
        pipe.execute.return_value = [None, 2, None, None]
        mock_r.pipeline.return_value = pipe

        allowed, remaining, retry = limiter.is_allowed("test_key")
        assert allowed is True
        assert remaining == 2  # 5 - 2 - 1


def test_rate_limiter_blocks_over_limit():
    from app.services.rate_limiter import RateLimiter
    limiter = RateLimiter()

    with patch("app.services.rate_limiter.get_redis") as mock_get_redis:
        mock_r = MagicMock()
        mock_get_redis.return_value = mock_r

        pipe = MagicMock()
        pipe.execute.return_value = [None, 5, None, None]  # 5 existing = at limit
        mock_r.pipeline.return_value = pipe
        mock_r.zrange.return_value = [("1234567.0", time.time() - 30)]

        allowed, remaining, retry = limiter.is_allowed("test_key")
        assert allowed is False
        assert remaining == 0


def test_rate_limiter_reset():
    from app.services.rate_limiter import RateLimiter
    limiter = RateLimiter()

    with patch("app.services.rate_limiter.get_redis") as mock_get_redis:
        mock_r = MagicMock()
        mock_get_redis.return_value = mock_r
        limiter.reset("test_key")
        mock_r.delete.assert_called_once_with("rate_limit:test_key")
