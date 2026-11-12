"""Command-line entry point: ``tpp <command>`` (or ``python -m turning_point.cli``)."""
from __future__ import annotations

import argparse
import json
import sys

from .config import PROJECT_ROOT, get_paths


def cmd_paths(_args) -> int:
    p = get_paths()
    print(json.dumps({"project_root": str(PROJECT_ROOT), "data_dir": str(p.data_dir), "raw": str(p.raw),
                      "processed": str(p.processed), "outputs": str(p.outputs_dir)}, indent=2))
    return 0


def cmd_check_repo(_args) -> int:
    from .validation import git_tracked_data_files
    bad = git_tracked_data_files(PROJECT_ROOT)
    if bad:
        print("Tracked files that look like microdata:\n" + "\n".join(bad))
        return 1
    print("OK: no microdata files are tracked by git.")
    return 0


def cmd_validate(args) -> int:
    from .ingestion import DatasetSpec, load_extract, load_mapping
    from .preprocessing import recode_missing
    from .validation import missingness_table, validate_frame

    spec = DatasetSpec.from_registry(args.dataset)
    mapping = load_mapping(args.dataset)
    paths = get_paths()
    df, manifest = load_extract(args.extract, mapping, dataset=args.dataset, manifest_dir=paths.processed)
    clean, reasons = recode_missing(df, spec.missing_codes)
    report = validate_frame(clean, required=list(mapping), id_col="id" if "id" in mapping else None)
    print(json.dumps({k: v for k, v in manifest.items() if k != "mapping"}, indent=2))
    print(report.to_frame().to_string(index=False) if report.issues else "No validation issues.")
    out = paths.processed / f"{args.dataset}_missingness.csv"
    missingness_table(reasons).to_csv(out, index=False)
    print(f"Missingness by reason written to {out} (git-ignored).")
    return 0 if report.ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tpp", description="Turning Point Project research tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("paths", help="show resolved data/output paths").set_defaults(func=cmd_paths)
    sub.add_parser("check-repo", help="fail if microdata are tracked by git").set_defaults(func=cmd_check_repo)
    v = sub.add_parser("validate", help="load an extract via its verified mapping and validate it")
    v.add_argument("dataset")
    v.add_argument("extract", help="path to the downloaded extract under data/raw/")
    v.set_defaults(func=cmd_validate)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
