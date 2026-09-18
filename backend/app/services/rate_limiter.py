import time
import redis as redis_lib
from app.config import get_settings

settings = get_settings()

_redis_client: redis_lib.Redis | None = None


def get_redis() -> redis_lib.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis_lib.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _redis_client


class RateLimiter:
    """
    Sliding-window rate limiter using Redis.
    Tracks requests per key (IP or user_id) within a time window.
    """

    def __init__(self):
        self.limit = settings.RATE_LIMIT_ATTEMPTS
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS

    def _key(self, identifier: str) -> str:
        return f"rate_limit:{identifier}"

    def is_allowed(self, identifier: str) -> tuple[bool, int, int]:
        """
        Returns (allowed, remaining_attempts, retry_after_seconds).
        Uses a Redis sorted set for sliding window accuracy.
        """
        r = get_redis()
        key = self._key(identifier)
        now = time.time()
        window_start = now - self.window

        pipe = r.pipeline()
        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count entries in window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set key expiry
        pipe.expire(key, self.window + 1)
        results = pipe.execute()

        count = results[1]  # count BEFORE this request

        if count >= self.limit:
            # Get the oldest entry to calculate retry_after
            oldest = r.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(self.window - (now - oldest[0][1])) + 1
            else:
                retry_after = self.window
            remaining = 0
            return False, remaining, retry_after

        remaining = self.limit - count - 1
        return True, remaining, 0

    def reset(self, identifier: str) -> None:
        """Clear the rate limit for a given identifier (e.g., on successful login)."""
        r = get_redis()
        r.delete(self._key(identifier))


rate_limiter = RateLimiter()
