from __future__ import annotations

import csv
from pathlib import Path

from core.config import Config
from core.models import Contact
from core.normalize.phone import format_phone

GOOGLE_HEADERS = [
    "First Name",
    "Middle Name",
    "Last Name",
    "Phonetic First Name",
    "Phonetic Middle Name",
    "Phonetic Last Name",
    "Name Prefix",
    "Name Suffix",
    "Nickname",
    "File As",
    "Organization Name",
    "Organization Title",
    "Organization Department",
    "Birthday",
    "Notes",
    "Photo",
    "Labels",
    "Phone 1 - Label",
    "Phone 1 - Value",
]


def _contact_to_row(contact: Contact, config: Config) -> list[str]:
    row = [""] * len(GOOGLE_HEADERS)
    row[0] = contact.name
    row[17] = "Mobile"
    row[18] = format_phone(contact.phone, config.phone_prefix_plus)
    return row


def write_google_csv_batches(contacts: list[Contact], out_dir: str | Path, config: Config) -> list[Path]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[Path] = []
    if not contacts:
        return output_files

    total = len(contacts)
    batch_size = max(1, config.batch_size)
    batches = (total + batch_size - 1) // batch_size

    for index in range(batches):
        start = index * batch_size
        end = min(start + batch_size, total)
        file_path = output_dir / f"saida_{index + 1:03d}.csv"
        with file_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(GOOGLE_HEADERS)
            for contact in contacts[start:end]:
                writer.writerow(_contact_to_row(contact, config))
        output_files.append(file_path)

    return output_files
