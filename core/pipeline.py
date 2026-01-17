from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.config import ColumnOverrides, Config
from core.io.columns import ColumnMap, resolve_crm_columns, resolve_google_columns
from core.io.read_csv import CsvMeta, iter_csv_rows, prepare_csv
from core.io.write_google_csv import write_google_csv_batches
from core.merge.dedupe import ContactIndex
from core.models import Contact, PhoneEntry
from core.normalize.name import build_fallback_name, clean_name, is_phone_like_name
from core.normalize.phone import normalize_phone
from core.normalize.text import analyze_mojibake


class PipelineCancelled(Exception):
    pass

def _parse_labels(raw: str | None, separator_hint: str) -> set[str]:
    if not raw:
        return set()
    if separator_hint in raw:
        parts = raw.split(separator_hint)
    elif "," in raw:
        parts = raw.split(",")
    else:
        parts = [raw]
    return {part.strip() for part in parts if part.strip()}


def _build_crm_notes(row: dict[str, Any], column_map: ColumnMap) -> list[str]:
    return []


def _split_phone_values(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    parts = [part.strip() for part in raw_value.split(":::")]
    return [part for part in parts if part]


def _normalize_phone_entries(
    raw_values: list[str],
    config: Config,
    ddi_override: str | None = None,
) -> tuple[list[PhoneEntry], int]:
    entries: list[PhoneEntry] = []
    seen: set[str] = set()
    found_total = 0
    for raw in raw_values:
        normalized = normalize_phone(
            raw,
            config.ddi_default,
            config.assume_ddi,
            ddi_override,
            config.min_phone_len,
        )
        if not normalized:
            continue
        found_total += 1
        if normalized in seen:
            continue
        seen.add(normalized)
        entries.append(PhoneEntry(raw=raw, normalized=normalized))
    entries.sort(key=lambda entry: entry.normalized)
    return entries, found_total


def _add_suspect(
    suspects: list[dict[str, Any]],
    reason: str,
    source: str,
    raw_phone: str,
    normalized_phone: str,
    name: str,
    line_num: int,
    extra: dict[str, Any] | None = None,
) -> None:
    item = {
        "reason": reason,
        "source": source,
        "raw_phone": raw_phone,
        "normalized_phone": normalized_phone,
        "name": name,
        "line": line_num,
    }
    if extra:
        item.update(extra)
    suspects.append(item)


def _record_suspects(
    suspects: list[dict[str, Any]],
    source: str,
    raw_phone: str,
    normalized_phone: str,
    name: str,
    line_num: int,
    config: Config,
) -> None:
    if normalized_phone:
        if len(normalized_phone) < config.min_phone_len or len(normalized_phone) > config.max_phone_len:
            _add_suspect(suspects, "phone_length", source, raw_phone, normalized_phone, name, line_num)

    mojibake_result = analyze_mojibake(name)
    if mojibake_result.suspect:
        extra = {
            "suggested_fix": mojibake_result.suggested_fix or "",
            "badness": mojibake_result.badness,
        }
        _add_suspect(suspects, "name_mojibake", source, raw_phone, normalized_phone, name, line_num, extra)


def _emit_progress(
    on_progress: Callable[[int, str], None] | None,
    processed: int,
    total: int,
    stage: str,
) -> None:
    if not on_progress:
        return
    percent = int((processed / total) * 100) if total else 0
    on_progress(percent, f"{stage}: {processed}/{total}")


def _build_input_report(meta: CsvMeta, column_map: ColumnMap) -> dict[str, Any]:
    return {
        "path": str(meta.path),
        "encoding": meta.encoding,
        "delimiter": meta.delimiter,
        "used_fallback": meta.used_fallback,
        "columns": {
            "name": column_map.name,
            "phone": column_map.phone,
            "phones": column_map.phones,
            "ddi": column_map.ddi,
            "tags": column_map.tags,
            "created": column_map.created,
            "notes": column_map.notes,
            "labels": column_map.labels,
            "given_name": column_map.given_name,
            "family_name": column_map.family_name,
        },
    }


def run_pipeline(
    crm_path: str | Path | None,
    out_dir: str | Path,
    config: Config,
    google_path: str | Path | None = None,
    overrides: ColumnOverrides | None = None,
    dry_run: bool = False,
    on_progress: Callable[[int, str], None] | None = None,
    should_cancel: Callable[[], bool] | None = None,
    progress_every: int = 200,
) -> dict[str, Any]:
    if not crm_path and not google_path:
        raise ValueError("At least one input CSV is required.")
    overrides = overrides or ColumnOverrides()
    suspects: list[dict[str, Any]] = []
    counts = {
        "crm_rows": 0,
        "google_rows": 0,
        "total_rows": 0,
        "without_phone": 0,
        "duplicates_merged": 0,
        "suspects": 0,
        "names_rewritten": 0,
        "phones_found_total": 0,
        "phones_unique_total": 0,
        "contacts_exploded_total": 0,
    }
    phones_unique_set: set[str] = set()

    index = ContactIndex(config.treat_dot_as_empty, config.protect_good_name)
    contacts_list: list[Contact] = []

    total_rows = 0
    processed_rows = 0

    google_report = None
    if google_path:
        google_meta = prepare_csv(google_path)
        google_columns = resolve_google_columns(google_meta.headers)
        google_report = _build_input_report(google_meta, google_columns)
        if on_progress:
            total_rows += sum(1 for _ in iter_csv_rows(google_meta.path, google_meta.encoding, google_meta.delimiter))
        for line_num, row in iter_csv_rows(google_meta.path, google_meta.encoding, google_meta.delimiter):
            if should_cancel and should_cancel():
                raise PipelineCancelled("Cancelled by user.")
            counts["google_rows"] += 1
            counts["total_rows"] += 1
            processed_rows += 1
            raw_name = str(row.get(google_columns.name, "")).strip() if google_columns.name else ""
            if not raw_name:
                given = str(row.get(google_columns.given_name, "")).strip() if google_columns.given_name else ""
                family = str(row.get(google_columns.family_name, "")).strip() if google_columns.family_name else ""
                raw_name = " ".join(part for part in (given, family) if part)
            name = clean_name(raw_name, config.treat_dot_as_empty)

            raw_phone_values: list[str] = []
            for phone_column in google_columns.phones:
                raw_value = str(row.get(phone_column, "")).strip()
                raw_phone_values.extend(_split_phone_values(raw_value))
            phone_entries, found_total = _normalize_phone_entries(raw_phone_values, config, None)
            counts["phones_found_total"] += found_total
            for entry in phone_entries:
                phones_unique_set.add(entry.normalized)
            entries_to_use = phone_entries if config.explode_phones else phone_entries[:1]
            counts["contacts_exploded_total"] += len(entries_to_use)

            if not entries_to_use:
                counts["without_phone"] += 1
                if analyze_mojibake(raw_name).suspect:
                    _record_suspects(
                        suspects,
                        "google",
                        "",
                        "",
                        raw_name,
                        line_num,
                        config,
                    )
                continue

            for entry in entries_to_use:
                _record_suspects(suspects, "google", entry.raw, entry.normalized, raw_name, line_num, config)
                contact = Contact(name=name, phone=entry.normalized, notes=[], labels=set(), sources={"google"})
                if config.dedupe_enabled:
                    merged = index.add(contact)
                    if merged:
                        counts["duplicates_merged"] += 1
                else:
                    contacts_list.append(contact)
            if on_progress and processed_rows % progress_every == 0:
                _emit_progress(on_progress, processed_rows, total_rows, "Processando Google")

    crm_report = None
    if crm_path:
        crm_meta = prepare_csv(crm_path)
        crm_columns = resolve_crm_columns(crm_meta.headers, overrides)
        crm_report = _build_input_report(crm_meta, crm_columns)
        if on_progress:
            total_rows += sum(1 for _ in iter_csv_rows(crm_meta.path, crm_meta.encoding, crm_meta.delimiter))
        _emit_progress(on_progress, processed_rows, total_rows, "Processando CRM")
        for line_num, row in iter_csv_rows(crm_meta.path, crm_meta.encoding, crm_meta.delimiter):
            if should_cancel and should_cancel():
                raise PipelineCancelled("Cancelled by user.")
            counts["crm_rows"] += 1
            counts["total_rows"] += 1
            processed_rows += 1
            raw_name = str(row.get(crm_columns.name, "")).strip() if crm_columns.name else ""
            name = clean_name(raw_name, config.treat_dot_as_empty)
            raw_ddi = str(row.get(crm_columns.ddi, "")).strip() if crm_columns.ddi else ""
            raw_phone_values: list[str] = []
            for phone_column in crm_columns.phones:
                raw_phone_values.extend(
                    _split_phone_values(str(row.get(phone_column, "")).strip())
                )
            phone_entries, found_total = _normalize_phone_entries(raw_phone_values, config, raw_ddi)
            counts["phones_found_total"] += found_total
            for entry in phone_entries:
                phones_unique_set.add(entry.normalized)
            entries_to_use = phone_entries if config.explode_phones else phone_entries[:1]
            counts["contacts_exploded_total"] += len(entries_to_use)

            if not entries_to_use:
                counts["without_phone"] += 1
                if analyze_mojibake(raw_name).suspect:
                    _record_suspects(
                        suspects,
                        "crm",
                        "",
                        "",
                        raw_name,
                        line_num,
                        config,
                    )
                continue

            labels = set()
            if config.label:
                labels.add(config.label)
            if crm_columns.labels:
                labels.update(_parse_labels(str(row.get(crm_columns.labels, "")), config.google_group_separator))
            notes = _build_crm_notes(row, crm_columns)

            for entry in entries_to_use:
                _record_suspects(suspects, "crm", entry.raw, entry.normalized, raw_name, line_num, config)
                contact = Contact(name=name, phone=entry.normalized, notes=notes, labels=labels, sources={"crm"})
                if config.dedupe_enabled:
                    merged = index.add(contact)
                    if merged:
                        counts["duplicates_merged"] += 1
                else:
                    contacts_list.append(contact)
            if on_progress and processed_rows % progress_every == 0:
                _emit_progress(on_progress, processed_rows, total_rows, "Processando CRM")

    if config.dedupe_enabled:
        contacts = sorted(index.values(), key=lambda contact: contact.phone)
    else:
        contacts = sorted(contacts_list, key=lambda contact: contact.phone)

    if config.rename_phone_like_names:
        for seq, contact in enumerate(contacts, start=1):
            if is_phone_like_name(contact.name):
                contact.name = build_fallback_name(config.fallback_prefix, seq, contact.phone)
                counts["names_rewritten"] += 1
    output_files: list[Path] = []
    if not dry_run:
        if should_cancel and should_cancel():
            raise PipelineCancelled("Cancelled by user.")
        _emit_progress(on_progress, processed_rows, total_rows, "Escrevendo CSVs")
        output_files = write_google_csv_batches(contacts, out_dir, config)
    _emit_progress(on_progress, total_rows, total_rows, "Concluído")

    warnings: list[str] = []
    if len(contacts) > config.contact_limit_warn:
        warnings.append(
            f"Total contacts {len(contacts)} exceeds warning threshold {config.contact_limit_warn}."
        )

    counts["suspects"] = len(suspects)
    counts["phones_unique_total"] = len(phones_unique_set)

    report = {
        "schema_version": 1,
        "params": {
            "ddi_default": config.ddi_default,
            "assume_ddi": config.assume_ddi,
            "batch_size": config.batch_size,
            "label": config.label,
            "phone_prefix_plus": config.phone_prefix_plus,
            "min_phone_len": config.min_phone_len,
            "max_phone_len": config.max_phone_len,
            "dedupe_enabled": config.dedupe_enabled,
            "treat_dot_as_empty": config.treat_dot_as_empty,
            "protect_good_name": config.protect_good_name,
            "rename_phone_like_names": config.rename_phone_like_names,
            "explode_phones": config.explode_phones,
            "fallback_prefix": config.fallback_prefix,
        },
        "inputs": {
            "crm": crm_report,
            "google": google_report,
        },
        "counts": {
            **counts,
            "deduped_contacts": len(contacts),
            "output_files": len(output_files),
        },
        "outputs": [str(path) for path in output_files],
        "warnings": warnings,
        "suspects": suspects,
    }

    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    report_path = out_dir_path / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report
