from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    ddi_default: str = "55"
    assume_ddi: bool = True
    batch_size: int = 3000
    label: str = "CRM_2025"
    phone_prefix_plus: bool = False
    min_phone_len: int = 12
    max_phone_len: int = 13
    google_group_separator: str = " ::: "
    contact_limit_warn: int = 25000
    dedupe_enabled: bool = True
    treat_dot_as_empty: bool = True
    protect_good_name: bool = True
    rename_phone_like_names: bool = True
    explode_phones: bool = True
    fallback_prefix: str = "Cliente"


@dataclass(frozen=True)
class ColumnOverrides:
    name: str | None = None
    phone: str | None = None
    ddi: str | None = None
    tags: str | None = None
    created: str | None = None
    notes: str | None = None
    labels: str | None = None
