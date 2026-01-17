from __future__ import annotations

import argparse
import sys

from core.config import ColumnOverrides, Config
from core.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSV converter for Google Contacts")
    parser.add_argument("--input-crm", help="Path to CRM CSV")
    parser.add_argument("--input-google", help="Path to Google Contacts CSV (optional)")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--ddi", default="55", help="Default DDI")
    parser.add_argument("--no-assume-ddi", action="store_true", help="Do not assume DDI when missing")
    parser.add_argument("--batch-size", type=int, default=3000, help="Contacts per output CSV")
    parser.add_argument("--label", default="CRM_2025", help="Label to apply to CRM contacts")
    parser.add_argument("--phone-prefix-plus", action="store_true", help="Prefix + in output phones")
    parser.add_argument("--min-phone-len", type=int, default=12, help="Min length for suspicious phones")
    parser.add_argument("--max-phone-len", type=int, default=13, help="Max length for suspicious phones")
    parser.add_argument("--no-rename-phone-like", action="store_true", help="Do not rename phone-like names")
    parser.add_argument("--no-explode-phones", action="store_true", help="Do not explode multiple phones")
    parser.add_argument("--fallback-prefix", default="Cliente", help="Prefix for fallback names")
    parser.add_argument("--dry-run", action="store_true", help="Generate report only")

    parser.add_argument("--col-name", help="Override CRM name column")
    parser.add_argument("--col-phone", help="Override CRM phone column")
    parser.add_argument("--col-ddi", help="Override CRM DDI column")
    parser.add_argument("--col-tags", help="Override CRM tags column")
    parser.add_argument("--col-created", help="Override CRM created column")
    parser.add_argument("--col-notes", help="Override CRM notes column")
    parser.add_argument("--col-labels", help="Override CRM labels column")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.input_crm and not args.input_google:
        parser.error("Provide --input-crm or --input-google.")

    config = Config(
        ddi_default=args.ddi,
        assume_ddi=not args.no_assume_ddi,
        batch_size=args.batch_size,
        label=args.label,
        phone_prefix_plus=args.phone_prefix_plus,
        min_phone_len=args.min_phone_len,
        max_phone_len=args.max_phone_len,
        rename_phone_like_names=not args.no_rename_phone_like,
        explode_phones=not args.no_explode_phones,
        fallback_prefix=args.fallback_prefix,
    )
    overrides = ColumnOverrides(
        name=args.col_name,
        phone=args.col_phone,
        ddi=args.col_ddi,
        tags=args.col_tags,
        created=args.col_created,
        notes=args.col_notes,
        labels=args.col_labels,
    )

    try:
        run_pipeline(
            crm_path=args.input_crm,
            google_path=args.input_google,
            out_dir=args.out_dir,
            config=config,
            overrides=overrides,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
