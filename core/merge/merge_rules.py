from __future__ import annotations

from core.models import Contact
from core.normalize.name import clean_name, is_phone_like_name


def merge_name(
    existing: str | None,
    incoming: str | None,
    treat_dot_as_empty: bool = True,
    protect_good_name: bool = True,
) -> str:
    existing_clean = clean_name(existing, treat_dot_as_empty)
    incoming_clean = clean_name(incoming, treat_dot_as_empty)
    existing_phone_like = is_phone_like_name(existing_clean)
    incoming_phone_like = is_phone_like_name(incoming_clean)

    if protect_good_name and existing_clean and not existing_phone_like:
        return existing_clean
    if incoming_clean and not incoming_phone_like:
        return incoming_clean
    return existing_clean or incoming_clean


def merge_notes(existing: list[str], incoming: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for note in existing:
        note_clean = note.strip()
        if note_clean and note_clean not in seen:
            result.append(note_clean)
            seen.add(note_clean)
    for note in incoming:
        note_clean = note.strip()
        if note_clean and note_clean not in seen:
            result.append(note_clean)
            seen.add(note_clean)
    return result


def merge_contacts(
    existing: Contact,
    incoming: Contact,
    treat_dot_as_empty: bool = True,
    protect_good_name: bool = True,
) -> Contact:
    merged = Contact(
        name=merge_name(existing.name, incoming.name, treat_dot_as_empty, protect_good_name),
        phone=existing.phone,
        notes=merge_notes(existing.notes, incoming.notes),
        labels=existing.labels | incoming.labels,
        sources=existing.sources | incoming.sources,
    )
    return merged
