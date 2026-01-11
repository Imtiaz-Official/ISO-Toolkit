"""
Rate limiting utilities for API endpoints.
"""

import time
from typing import Dict
from collections import defaultdict
from datetime import datetime, timedelta

# Simple in-memory rate limiter
# For production, consider using Redis or a dedicated rate limiting service
class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    """

    def __init__(self):
        # Store request timestamps per key
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
        """
        Check if a request is allowed based on rate limit.

        Args:
            key: Unique identifier (IP address, username, etc.)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - window_seconds

        # Clean old requests from the key's history
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if timestamp > window_start
        ]

        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True

        return False

    def get_retry_after(self, key: str, window_seconds: int = 60) -> int:
        """
        Get seconds until next request is allowed.

        Args:
            key: Unique identifier
            window_seconds: Time window in seconds

        Returns:
            Seconds until retry is allowed
        """
        if not self.requests[key]:
            return 0

        oldest_request = self.requests[key][0]
        retry_after = int(oldest_request + window_seconds - time.time())
        return max(0, retry_after)


# Global rate limiter instances
login_rate_limiter = RateLimiter()
general_rate_limiter = RateLimiter()


def check_login_rate_limit(identifier: str) -> tuple[bool, int | None]:
    """
    Check login rate limit for an identifier.

    Args:
        identifier: IP address or username

    Returns:
        (is_allowed, retry_after_seconds)
    """
    max_attempts = 5
    window_seconds = 300  # 5 minutes

    if login_rate_limiter.is_allowed(identifier, max_attempts, window_seconds):
        return True, None

    retry_after = login_rate_limiter.get_retry_after(identifier, window_seconds)
    return False, retry_after
