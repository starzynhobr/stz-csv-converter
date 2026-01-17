from __future__ import annotations

import tempfile
from pathlib import Path

from core.config import Config
from core.pipeline import run_pipeline


def test_explode_phones_dedupe_google_only():
    csv_content = "\n".join(
        [
            "Name,Phone 1 - Value,Phone 2 - Value",
            "Maria,+55 11 91234-5678,11912345678",
            "Joao,5511912345678,",
        ]
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        google_path = temp_path / "google.csv"
        google_path.write_text(csv_content, encoding="utf-8-sig")

        report = run_pipeline(
            crm_path=None,
            google_path=google_path,
            out_dir=temp_path,
            config=Config(),
            dry_run=True,
        )

    counts = report["counts"]
    assert counts["contacts_exploded_total"] == 2
    assert counts["phones_unique_total"] == 1
    assert counts["duplicates_merged"] == 1
    assert counts["deduped_contacts"] == 1
