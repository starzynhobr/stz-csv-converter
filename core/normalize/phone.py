from __future__ import annotations

import re


def normalize_phone(
    value: str | None,
    ddi_default: str,
    assume_ddi: bool,
    ddi_override: str | None = None,
    min_len: int | None = None,
) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D+", "", value)
    if not digits:
        return ""

    ddi_digits = re.sub(r"\D+", "", ddi_override or "")
    if ddi_digits:
        if min_len and digits.startswith(ddi_digits) and len(digits) >= min_len:
            return digits
        return ddi_digits + digits

    if assume_ddi and ddi_default:
        if not digits.startswith(ddi_default):
            digits = ddi_default + digits

    return digits


def format_phone(value: str, prefix_plus: bool) -> str:
    if not value:
        return ""
    if prefix_plus:
        return "+" + value
    return value
