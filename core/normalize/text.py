from __future__ import annotations

from dataclasses import dataclass
import re

try:  # Optional dependency
    import ftfy  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ftfy = None

REPLACEMENT_CHAR = "\ufffd"
MOJIBAKE_REGEXES = (
    re.compile(r"Ã[\u0080-\u00BF]"),
    re.compile(r"Â[\u0080-\u00BF]"),
    re.compile(r"â€"),
)
FTFY_BADNESS_THRESHOLD = 1.0


@dataclass(frozen=True)
class MojibakeResult:
    suspect: bool
    reason: str | None
    suggested_fix: str | None
    badness: float | None


def analyze_mojibake(value: str | None) -> MojibakeResult:
    if not value:
        return MojibakeResult(False, None, None, None)

    reason = None
    if REPLACEMENT_CHAR in value:
        reason = "replacement_char"
    elif any(regex.search(value) for regex in MOJIBAKE_REGEXES):
        reason = "pattern"

    badness_score = None
    if ftfy is not None:
        try:
            badness_score = float(ftfy.badness(value))
        except Exception:
            badness_score = None
        if badness_score is not None and badness_score >= FTFY_BADNESS_THRESHOLD:
            reason = reason or "ftfy_badness"

    suspect = reason is not None
    suggested_fix = None
    if suspect and ftfy is not None:
        try:
            fixed = ftfy.fix_text(value)
        except Exception:
            fixed = None
        if fixed and fixed != value:
            suggested_fix = fixed

    return MojibakeResult(suspect, reason, suggested_fix, badness_score)
