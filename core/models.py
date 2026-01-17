from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PhoneEntry:
    raw: str
    normalized: str


@dataclass
class ContactSeed:
    name: str
    phones: list[PhoneEntry]
    notes: list[str] = field(default_factory=list)
    labels: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)


@dataclass
class Contact:
    name: str
    phone: str
    notes: list[str] = field(default_factory=list)
    labels: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)

    def add_note(self, note: str) -> None:
        note_clean = note.strip()
        if note_clean and note_clean not in self.notes:
            self.notes.append(note_clean)

    def add_label(self, label: str) -> None:
        label_clean = label.strip()
        if label_clean:
            self.labels.add(label_clean)

    def add_source(self, source: str) -> None:
        source_clean = source.strip()
        if source_clean:
            self.sources.add(source_clean)
