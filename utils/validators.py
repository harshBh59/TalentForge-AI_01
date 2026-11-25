"""
Simple validation helpers shared across pages/forms.
"""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def is_valid_username(username: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username or ""))


def is_strong_enough_password(password: str) -> bool:
    return len(password or "") >= 6
