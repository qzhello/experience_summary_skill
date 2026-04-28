"""Filter / aggregate entries from .experience/log.md.

Behavior contract: see scripts-contract.md.

  python scripts/query.py --status active --type bug
  python scripts/query.py --severity high,critical
  python scripts/query.py --tag risk --format ids
  python scripts/query.py --version "redis@7.2.4"
  python scripts/query.py --version-prefix "redis@7.2"
  python scripts/query.py --include-archived
  python scripts/query.py --group-by type

Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.parse import (  # noqa: E402
    parse_log, parse_with_archive, find_experience_dir, extract_summary,
)


def _split_csv(s):
    return [x.strip() for x in s.split(",") if x.strip()] if s else None


def filter_entries(entries, *, status, types, severity, tags, version, version_prefix):
    """Filter semantics per contract:
    - between flags: AND
    - within a flag (comma): OR
    """
    out = []
    for e in entries:
        f = e.fields
        if status and f.get("status", "") not in status:
            continue
        if types and e.type not in types:
            continue
        if severity and f.get("severity", "") not in severity:
            continue
        if tags:
            entry_tags = {t.strip() for t in f.get("tags", "").split(",") if t.strip()}
            if not (set(tags) & entry_tags):
                continue
        ver = f.get("version", "")
        if version is not None and ver != version:
            continue
        if version_prefix is not None and not ver.startswith(version_prefix):
            continue
        out.append(e)
    return out


def fmt_table(entries, *, show_source: bool):
    """Contract column order: id, type, status, severity, summary [, source]."""
    if not entries:
        print("(no entries)")
        return
    rows = []
    for e in entries:
        row = [
            e.id,
            e.type or "-",
            e.fields.get("status", "-"),
            e.fields.get("severity", "-"),
            extract_summary(e),
        ]
        if show_source:
            row.insert(0, e.source_kind)
        rows.append(row)

    # column widths for fixed-width prefix columns (all but last)
    n_fixed = len(rows[0]) - 1
    widths = [max(len(r[i]) for r in rows) for i in range(n_fixed)]
    for r in rows:
        prefix = "  ".join(f"{r[i]:<{widths[i]}}" for i in range(n_fixed))
        print(f"{prefix}  {r[-1]}")


def fmt_ids(entries, **_):
    for e in entries:
        print(e.id)


_FORMATTERS = {"table": fmt_table, "ids": fmt_ids}


def main() -> int:
    ap = argparse.ArgumentParser(description="Query .experience/log.md entries.")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--status", help="comma-separated, e.g. active,stale")
    ap.add_argument("--type", dest="types", help="comma-separated")
    ap.add_argument("--severity", help="comma-separated")
    ap.add_argument("--tag", help="comma-separated; matches if any tag overlaps")
    ap.add_argument("--version", help="exact version string match")
    ap.add_argument("--version-prefix", dest="version_prefix",
                    help="prefix match (V1: simple string, no semver)")
    ap.add_argument("--group-by", choices=["type", "status", "severity", "version"])
    ap.add_argument("--format", choices=list(_FORMATTERS.keys()), default="table")
    ap.add_argument("--include-archived", action="store_true",
                    help="Also read details/archive/*.md")
    ap.add_argument("--strict-parse", action="store_true",
                    help="Any parse error → exit 1")
    args = ap.parse_args()

    exp_dir = find_experience_dir(args.root)
    if exp_dir is None:
        print("error: .experience/log.md not found", file=sys.stderr)
        return 2

    if args.include_archived:
        result = parse_with_archive(exp_dir, include_archived=True)
    else:
        result = parse_log(exp_dir / "log.md")

    if result.errors:
        for pe in result.errors:
            print(f"parse error: line {pe.line} [{pe.entry_id or '-'}]: {pe.message}",
                  file=sys.stderr)

    entries = filter_entries(
        result.entries,
        status=_split_csv(args.status),
        types=_split_csv(args.types),
        severity=_split_csv(args.severity),
        tags=_split_csv(args.tag),
        version=args.version,
        version_prefix=args.version_prefix,
    )

    fmt = _FORMATTERS[args.format]
    show_source = args.include_archived

    if args.group_by:
        groups = defaultdict(list)
        for e in entries:
            key = e.type if args.group_by == "type" else e.fields.get(args.group_by, "-")
            groups[key or "-"].append(e)
        for k in sorted(groups.keys()):
            print(f"\n## {args.group_by} = {k}  ({len(groups[k])})")
            fmt(groups[k], show_source=show_source)
    else:
        fmt(entries, show_source=show_source)

    if args.strict_parse and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
