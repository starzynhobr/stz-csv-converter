from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from core.config import ColumnOverrides


@dataclass(frozen=True)
class ColumnMap:
    name: str | None
    phone: str | None
    phones: list[str]
    ddi: str | None
    tags: str | None
    created: str | None
    notes: str | None
    labels: str | None
    given_name: str | None
    family_name: str | None


def normalize_header(value: str) -> str:
    value = value.strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def find_column(headers: list[str], candidates: list[str]) -> str | None:
    normalized = {normalize_header(header): header for header in headers}
    for candidate in candidates:
        header = normalized.get(candidate)
        if header:
            return header
    return None


def _resolve_override(headers: list[str], override: str | None, field: str) -> str | None:
    if not override:
        return None
    override_normalized = normalize_header(override)
    for header in headers:
        if normalize_header(header) == override_normalized:
            return header
    raise ValueError(f"Override for {field} not found in CSV headers: {override}")


def resolve_crm_columns(headers: list[str], overrides: ColumnOverrides) -> ColumnMap:
    name_override = _resolve_override(headers, overrides.name, "name")
    phone_override = _resolve_override(headers, overrides.phone, "phone")
    ddi_override = _resolve_override(headers, overrides.ddi, "ddi")
    tags_override = _resolve_override(headers, overrides.tags, "tags")
    created_override = _resolve_override(headers, overrides.created, "created")
    notes_override = _resolve_override(headers, overrides.notes, "notes")
    labels_override = _resolve_override(headers, overrides.labels, "labels")

    name = name_override or find_column(
        headers,
        [
            "nome",
            "name",
            "contato",
            "cliente",
            "razaosocial",
            "responsavel",
            "fullname",
        ],
    )
    phone = phone_override or find_column(
        headers,
        [
            "telefone",
            "fone",
            "celular",
            "whatsapp",
            "numero",
            "numerotelefone",
            "phone",
            "mobile",
        ],
    )
    ddi = ddi_override or find_column(headers, ["ddi", "ddicode", "countrycode"])
    tags = tags_override or find_column(headers, ["tags", "tag", "categoria", "segmento", "grupo"])
    created = created_override or find_column(headers, ["criadoem", "createdat", "datacriacao", "datacadastro"])
    notes = notes_override or find_column(headers, ["notas", "observacoes", "obs", "notes", "comentarios"])
    labels = labels_override or find_column(headers, ["labels", "label", "grupo"])

    if not phone:
        raise ValueError("Phone column not found in CRM CSV. Use --col-phone to override.")

    return ColumnMap(
        name=name,
        phone=phone,
        phones=[phone],
        ddi=ddi,
        tags=tags,
        created=created,
        notes=notes,
        labels=labels,
        given_name=None,
        family_name=None,
    )


def resolve_google_columns(headers: list[str]) -> ColumnMap:
    name = find_column(headers, ["name", "nome"])
    given_name = find_column(headers, ["givenname", "primeironome"])
    family_name = find_column(headers, ["familyname", "sobrenome"])
    normalized_headers = {normalize_header(header): header for header in headers}
    phone_candidates: list[tuple[int, str]] = []
    for normalized, header in normalized_headers.items():
        match = re.fullmatch(r"phone(\d+)value", normalized)
        if match:
            phone_candidates.append((int(match.group(1)), header))
    phone_candidates.sort(key=lambda item: item[0])
    phones = [header for _, header in phone_candidates]
    phone = phones[0] if phones else find_column(headers, ["phone1value", "telefone", "phone"])
    if phone and not phones:
        phones = [phone]
    notes = find_column(headers, ["notes", "notas", "observacoes", "obs"])
    labels = find_column(headers, ["groupmembership", "labels", "label", "grupo"])

    if not phone and not phones:
        raise ValueError("Phone column not found in Google CSV.")

    return ColumnMap(
        name=name,
        phone=phone,
        phones=phones,
        ddi=None,
        tags=None,
        created=None,
        notes=notes,
        labels=labels,
        given_name=given_name,
        family_name=family_name,
    )
