from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ENCODING_CANDIDATES = ("utf-8-sig", "cp1252", "latin-1")


@dataclass(frozen=True)
class CsvMeta:
    path: Path
    encoding: str
    delimiter: str
    headers: list[str]
    used_fallback: bool


def detect_encoding(path: Path) -> tuple[str, bool]:
    for idx, encoding in enumerate(ENCODING_CANDIDATES):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                handle.read(4096)
            return encoding, idx != 0
        except UnicodeDecodeError:
            continue
    return ENCODING_CANDIDATES[-1], True


def detect_delimiter(path: Path, encoding: str) -> str:
    sample_lines: list[str] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        for _ in range(5):
            line = handle.readline()
            if not line:
                break
            if line.strip():
                sample_lines.append(line)
    comma_count = sum(line.count(",") for line in sample_lines)
    semi_count = sum(line.count(";") for line in sample_lines)
    if semi_count > comma_count:
        return ";"
    return ","


def prepare_csv(path: str | Path) -> CsvMeta:
    csv_path = Path(path)
    encoding, used_fallback = detect_encoding(csv_path)
    delimiter = detect_delimiter(csv_path, encoding)
    with csv_path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        headers = reader.fieldnames or []
    return CsvMeta(
        path=csv_path,
        encoding=encoding,
        delimiter=delimiter,
        headers=headers,
        used_fallback=used_fallback,
    )


def iter_csv_rows(path: str | Path, encoding: str, delimiter: str):
    csv_path = Path(path)
    with csv_path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        for line_num, row in enumerate(reader, start=2):
            yield line_num, row
