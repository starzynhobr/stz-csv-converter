from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.config import ColumnOverrides, Config
from core.io.columns import resolve_crm_columns, resolve_google_columns
from core.io.read_csv import iter_csv_rows, prepare_csv
from core.normalize.phone import normalize_phone
from core.normalize.text import analyze_mojibake
from core.pipeline import PipelineCancelled, run_pipeline


class PipelineWorker(QObject):
    finished = Signal(dict)
    progress = Signal(int, str)
    log = Signal(str)
    error = Signal(str)
    cancelled = Signal()

    def __init__(
        self,
        crm_path: str | None,
        out_dir: str,
        config: Config,
        overrides: ColumnOverrides,
        google_path: str | None,
        dry_run: bool,
    ) -> None:
        super().__init__()
        self._crm_path = crm_path
        self._google_path = google_path
        self._out_dir = out_dir
        self._config = config
        self._overrides = overrides
        self._dry_run = dry_run
        self._cancelled = False
        self._last_status = ""

    def cancel(self) -> None:
        self._cancelled = True

    def _should_cancel(self) -> bool:
        return self._cancelled

    def _on_progress(self, percent: int, status: str) -> None:
        if status != self._last_status:
            self._last_status = status
            self.log.emit(status)
        self.progress.emit(percent, status)

    def run(self) -> None:
        try:
            self.log.emit("Iniciando processamento...")
            report = run_pipeline(
                crm_path=self._crm_path,
                google_path=self._google_path,
                out_dir=self._out_dir,
                config=self._config,
                overrides=self._overrides,
                dry_run=self._dry_run,
                on_progress=self._on_progress,
                should_cancel=self._should_cancel,
            )
            self.log.emit("Processamento concluído.")
            self.finished.emit(report)
        except PipelineCancelled:
            self.log.emit("Processamento cancelado.")
            self.cancelled.emit()
        except Exception as exc:  # pragma: no cover - GUI error guardrail
            self.error.emit(str(exc))


class ValidationWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(
        self,
        crm_path: str | None,
        google_path: str | None,
        config: Config,
        overrides: ColumnOverrides,
        preview_limit: int,
        fast_scan_limit_bytes: int,
    ) -> None:
        super().__init__()
        self._crm_path = crm_path
        self._google_path = google_path
        self._config = config
        self._overrides = overrides
        self._preview_limit = preview_limit
        self._fast_scan_limit_bytes = fast_scan_limit_bytes

    def run(self) -> None:
        try:
            result = self._validate()
            self.finished.emit(result)
        except Exception as exc:  # pragma: no cover - GUI error guardrail
            self.error.emit(str(exc))

    def _build_meta(self, meta, columns) -> dict[str, Any]:
        return {
            "path": str(meta.path),
            "encoding": meta.encoding,
            "delimiter": meta.delimiter,
            "used_fallback": meta.used_fallback,
            "columns": asdict(columns),
        }

    def _split_phone_values(self, raw_value: str | None) -> list[str]:
        if not raw_value:
            return []
        parts = [part.strip() for part in raw_value.split(":::")]
        return [part for part in parts if part]

    def _normalize_phone_values(
        self,
        raw_values: list[str],
        ddi_override: str | None = None,
    ) -> list[str]:
        normalized_values: list[str] = []
        seen: set[str] = set()
        for raw_phone in raw_values:
            normalized = normalize_phone(
                raw_phone,
                self._config.ddi_default,
                self._config.assume_ddi,
                ddi_override,
                self._config.min_phone_len,
            )
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            normalized_values.append(normalized)
        normalized_values.sort()
        if not self._config.explode_phones:
            return normalized_values[:1]
        return normalized_values

    def _validate(self) -> dict[str, Any]:
        preview_rows: list[dict[str, str]] = []
        has_mojibake = False

        crm_info = None
        crm_line_count = None
        crm_without_phone = None
        crm_duplicates = None

        if self._crm_path:
            crm_meta = prepare_csv(self._crm_path)
            crm_columns = resolve_crm_columns(crm_meta.headers, self._overrides)
            crm_info = self._build_meta(crm_meta, crm_columns)

            file_size = Path(self._crm_path).stat().st_size
            if file_size <= self._fast_scan_limit_bytes:
                total = 0
                missing_phone = 0
                duplicates_count = 0
                seen_phones: set[str] = set()
                for _, row in iter_csv_rows(crm_meta.path, crm_meta.encoding, crm_meta.delimiter):
                    total += 1
                    raw_ddi = str(row.get(crm_columns.ddi, "")).strip() if crm_columns.ddi else ""
                    raw_phone_values: list[str] = []
                    for phone_column in crm_columns.phones:
                        raw_phone_values.extend(
                            self._split_phone_values(str(row.get(phone_column, "")).strip())
                        )
                    normalized_values = self._normalize_phone_values(raw_phone_values, raw_ddi)
                    if not normalized_values:
                        missing_phone += 1
                        continue
                    for normalized in normalized_values:
                        if normalized in seen_phones:
                            duplicates_count += 1
                        else:
                            seen_phones.add(normalized)
                crm_line_count = total
                crm_without_phone = missing_phone
                crm_duplicates = duplicates_count

            for _, row in iter_csv_rows(crm_meta.path, crm_meta.encoding, crm_meta.delimiter):
                if len(preview_rows) >= self._preview_limit:
                    break
                raw_name = str(row.get(crm_columns.name, "")).strip() if crm_columns.name else ""
                raw_phone_values: list[str] = []
                for phone_column in crm_columns.phones:
                    raw_phone_values.extend(
                        self._split_phone_values(str(row.get(phone_column, "")).strip())
                    )
                raw_phone = raw_phone_values[0] if raw_phone_values else ""
                raw_ddi = str(row.get(crm_columns.ddi, "")).strip() if crm_columns.ddi else ""
                raw_tags = str(row.get(crm_columns.tags, "")).strip() if crm_columns.tags else ""
                raw_created = str(row.get(crm_columns.created, "")).strip() if crm_columns.created else ""
                if analyze_mojibake(raw_name).suspect:
                    has_mojibake = True
                preview_rows.append(
                    {
                        "name": raw_name,
                        "ddi": raw_ddi,
                        "phone": raw_phone,
                        "tags": raw_tags,
                        "created": raw_created,
                    }
                )

        google_info = None
        google_line_count = None
        google_without_phone = None
        google_duplicates = None
        if self._google_path:
            google_meta = prepare_csv(self._google_path)
            google_columns = resolve_google_columns(google_meta.headers)
            google_info = self._build_meta(google_meta, google_columns)
            file_size = Path(self._google_path).stat().st_size
            if file_size <= self._fast_scan_limit_bytes or not self._crm_path:
                total = 0
                missing_phone = 0
                duplicates_count = 0
                seen_phones: set[str] = set()
                for _, row in iter_csv_rows(google_meta.path, google_meta.encoding, google_meta.delimiter):
                    total += 1
                    raw_phone_values: list[str] = []
                    for phone_column in google_columns.phones:
                        raw_phone_values.extend(
                            self._split_phone_values(str(row.get(phone_column, "")).strip())
                        )
                    normalized_values = self._normalize_phone_values(raw_phone_values)
                    if not normalized_values:
                        missing_phone += 1
                        continue
                    for normalized in normalized_values:
                        if normalized in seen_phones:
                            duplicates_count += 1
                        else:
                            seen_phones.add(normalized)
                google_line_count = total
                google_without_phone = missing_phone
                google_duplicates = duplicates_count
            if not self._crm_path:
                for _, row in iter_csv_rows(google_meta.path, google_meta.encoding, google_meta.delimiter):
                    if len(preview_rows) >= self._preview_limit:
                        break
                    raw_name = str(row.get(google_columns.name, "")).strip() if google_columns.name else ""
                    if not raw_name:
                        given = str(row.get(google_columns.given_name, "")).strip() if google_columns.given_name else ""
                        family = str(row.get(google_columns.family_name, "")).strip() if google_columns.family_name else ""
                        raw_name = " ".join(part for part in (given, family) if part)
                    raw_phone_values: list[str] = []
                    for phone_column in google_columns.phones:
                        raw_phone_values.extend(
                            self._split_phone_values(str(row.get(phone_column, "")).strip())
                        )
                    raw_phone = raw_phone_values[0] if raw_phone_values else ""
                    if analyze_mojibake(raw_name).suspect:
                        has_mojibake = True
                    preview_rows.append(
                        {
                            "name": raw_name,
                            "ddi": "",
                            "phone": raw_phone,
                            "tags": "",
                            "created": "",
                        }
                    )

        return {
            "crm": crm_info,
            "google": google_info,
            "preview_rows": preview_rows,
            "preview_has_mojibake": has_mojibake,
            "crm_line_count": crm_line_count,
            "crm_without_phone": crm_without_phone,
            "crm_duplicates": crm_duplicates,
            "google_line_count": google_line_count,
            "google_without_phone": google_without_phone,
            "google_duplicates": google_duplicates,
        }
