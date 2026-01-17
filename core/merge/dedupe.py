from __future__ import annotations

from core.merge.merge_rules import merge_contacts
from core.models import Contact


class ContactIndex:
    def __init__(self, treat_dot_as_empty: bool = True, protect_good_name: bool = True) -> None:
        self._by_phone: dict[str, Contact] = {}
        self.duplicates_merged = 0
        self._treat_dot_as_empty = treat_dot_as_empty
        self._protect_good_name = protect_good_name

    def add(self, contact: Contact) -> bool:
        existing = self._by_phone.get(contact.phone)
        if existing is None:
            self._by_phone[contact.phone] = contact
            return False
        self._by_phone[contact.phone] = merge_contacts(
            existing,
            contact,
            self._treat_dot_as_empty,
            self._protect_good_name,
        )
        self.duplicates_merged += 1
        return True

    def values(self) -> list[Contact]:
        return list(self._by_phone.values())

    def __len__(self) -> int:
        return len(self._by_phone)
