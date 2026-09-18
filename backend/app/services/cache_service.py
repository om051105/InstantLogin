import json
from typing import Any, Optional
from app.services.rate_limiter import get_redis


class CacheService:
    """Redis-backed cache with TTL support."""

    DEFAULT_TTL = 300  # 5 minutes

    def get(self, key: str) -> Optional[Any]:
        r = get_redis()
        value = r.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
        r = get_redis()
        r.setex(key, ttl, json.dumps(value, default=str))

    def delete(self, key: str) -> None:
        r = get_redis()
        r.delete(key)

    def delete_pattern(self, pattern: str) -> None:
        r = get_redis()
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)

    # ─── Convenience Methods ──────────────────────────────────────────────────

    def get_user(self, user_id: int) -> Optional[dict]:
        return self.get(f"user:{user_id}")

    def set_user(self, user_id: int, user_data: dict, ttl: int = 600) -> None:
        self.set(f"user:{user_id}", user_data, ttl)

    def invalidate_user(self, user_id: int) -> None:
        self.delete(f"user:{user_id}")

    def blacklist_token(self, jti: str, ttl: int) -> None:
        """Add a JWT ID to the blacklist (used on logout)."""
        r = get_redis()
        r.setex(f"blacklist:{jti}", ttl, "1")

    def is_token_blacklisted(self, jti: str) -> bool:
        r = get_redis()
        return r.exists(f"blacklist:{jti}") == 1


cache_service = CacheService()
