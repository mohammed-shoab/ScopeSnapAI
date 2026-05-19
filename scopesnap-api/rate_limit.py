"""
Shared rate limiter instance.

Kept in its own module (instead of main.py) so that individual API modules
can import `limiter` without causing a circular import with main.py.

Protects expensive Gemini Vision calls from abuse/runaway costs.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
