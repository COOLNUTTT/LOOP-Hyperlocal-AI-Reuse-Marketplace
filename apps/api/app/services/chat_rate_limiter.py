# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""In-memory sliding-window rate limiter for chat messaging.

Enforces roadmap constraint: max 60 messages per minute per user.
"""

import time
from collections import defaultdict
from typing import Dict, List


class ChatRateLimiter:
    def __init__(self, max_messages: int = 60, window_seconds: int = 60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check_and_record(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit.

        Returns True if allowed, False if limit exceeded.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean timestamps older than window
        timestamps = [ts for ts in self._history[user_id] if ts > cutoff]
        self._history[user_id] = timestamps

        if len(timestamps) >= self.max_messages:
            return False

        self._history[user_id].append(now)
        return True

    def reset(self, user_id: str = None):
        """Reset limits for testing."""
        if user_id:
            self._history.pop(user_id, None)
        else:
            self._history.clear()


chat_rate_limiter = ChatRateLimiter(max_messages=60, window_seconds=60)
