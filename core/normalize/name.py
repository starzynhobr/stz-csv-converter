from __future__ import annotations

import re

PHONE_LIKE_REGEX = re.compile(r"^[0-9\s\-\(\)\+]+$")


def clean_name(value: str | None, treat_dot_as_empty: bool = True) -> str:
    if value is None:
        return ""
    name = value.strip()
    if treat_dot_as_empty and name == ".":
        return ""
    return name


def is_good_name(value: str | None, treat_dot_as_empty: bool = True) -> bool:
    return bool(clean_name(value, treat_dot_as_empty))


def is_phone_like_name(value: str | None) -> bool:
    if value is None:
        return True
    name = value.strip()
    if not name or name == ".":
        return True
    return bool(PHONE_LIKE_REGEX.fullmatch(name))


def build_fallback_name(prefix: str, seq: int, normalized_phone: str) -> str:
    digits = re.sub(r"\D+", "", normalized_phone or "")
    last4 = digits[-4:] if digits else "0000"
    return f"{prefix} {seq:07d} ({last4})"
