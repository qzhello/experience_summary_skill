"""Quick stats over .experience/log.md.

Behavior contract: see scripts-contract.md.

  python scripts/stats.py
  python scripts/stats.py --stale-days 60 --agent-cap 150
  python scripts/stats.py --current-version "redis@7.2.4"
  python scripts/stats.py --include-archived

Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.parse import (  # noqa: E402
    parse_log, parse_with_archive, find_experience_dir,
)


# AGENT.md "当前版本: <value>" line pattern (Chinese or English heading variants)
AGENT_VERSION_RE = re.compile(
    r"\*\*(?:当前版本|current\s*version)\*\*\s*[:：]\s*[`]?([^`\n]+?)[`]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _resolve_current_version(cli_value, agent_md_path):
    """Per contract:
       1. --current-version
       2. AGENT.md '当前版本' line
       3. None → archive candidates not computed
    """
    if cli_value:
        return cli_value, "cli"
    if agent_md_path and agent_md_path.is_file():
        text = agent_md_path.read_text(encoding="utf-8")
        m = AGENT_VERSION_RE.search(text)
        if m:
            v = m.group(1).strip()
            if v and not v.startswith("<TBD"):
                return v, "agent"
    return None, "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description="Stats over .experience/log.md.")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--stale-days", type=int, default=90)
    ap.add_argument("--agent-cap", type=int, default=150)
    ap.add_argument("--current-version", dest="current_version", default=None,
                    help="Current project version for archive-candidate computation")
    ap.add_argument("--include-archived", action="store_true",
                    help="Also count details/archive/*.md")
    ap.add_argument("--strict-parse", action="store_true",
                    help="Any parse error → exit 1")
    args = ap.parse_args()

    exp_dir = find_experience_dir(args.root)
    if exp_dir is None:
        print("error: .experience/log.md not found", file=sys.stderr)
        return 2

    log_path = exp_dir / "log.md"
    if args.include_archived:
        result = parse_with_archive(exp_dir, include_archived=True)
    else:
        result = parse_log(log_path)
    log_lines = len(log_path.read_text(encoding="utf-8").splitlines())

    if result.errors:
        for pe in result.errors:
            print(f"parse error: line {pe.line} [{pe.entry_id or '-'}]: {pe.message}",
                  file=sys.stderr)

    entries = result.entries
    n_log = sum(1 for e in entries if e.source_kind == "log")
    n_archive = sum(1 for e in entries if e.source_kind == "archive")

    by_type = Counter(e.type or "-" for e in entries)
    by_status = Counter(e.fields.get("status", "-") for e in entries)
    by_severity = Counter(
        e.fields.get("severity", "-")
        for e in entries
        if e.type in ("bug", "pitfall")
    )

    def fmt_counter(c):
        return ", ".join(f"{k} {v}" for k, v in sorted(c.items())) if c else "(none)"

    if args.include_archived:
        print(f"log.md: {n_log} entries, {log_lines} lines · archive: {n_archive} entries")
    else:
        print(f"log.md: {n_log} entries, {log_lines} lines")
    print(f"  by type:     {fmt_counter(by_type)}")
    print(f"  by status:   {fmt_counter(by_status)}")
    print(f"  by severity: {fmt_counter(by_severity)}  (bug+pitfall only)")

    # stale candidates: status=active AND last_verified > stale_days ago
    today = date.today()
    stale = []
    for e in entries:
        if e.fields.get("status") != "active":
            continue
        lv = e.fields.get("last_verified", "")
        try:
            d = date.fromisoformat(lv)
        except ValueError:
            continue
        days = (today - d).days
        if days > args.stale_days:
            stale.append((e.id, days))

    if stale:
        print(f"\nStale candidates (active, last_verified > {args.stale_days}d):")
        for eid, days in sorted(stale, key=lambda x: -x[1]):
            print(f"  - {eid} ({days}d)")

    # archive candidates per contract:
    #   status in {stale, fixed} AND version != current_version AND version != 'unknown'
    #   "差异于当前版本",非"早于";V1 不做版本顺序推理。
    #   current_version source order: --current-version > AGENT.md > unknown
    agent_md = exp_dir / "AGENT.md"
    cur_ver, src = _resolve_current_version(args.current_version, agent_md)

    if cur_ver is None:
        print("\narchive candidates: skipped — current version unknown "
              "(use --current-version or fill AGENT.md '当前版本')")
    else:
        archive_cands = []
        for e in entries:
            if e.source_kind != "log":
                continue  # only log.md entries can be archive candidates
            if e.fields.get("status") not in ("stale", "fixed"):
                continue
            v = e.fields.get("version", "").strip()
            if not v or v == "unknown":
                continue
            if v != cur_ver:
                archive_cands.append(e)
        if archive_cands:
            print(f"\nArchive candidates ({len(archive_cands)}, "
                  f"current = {cur_ver!r} from {src}; "
                  f'"差异于当前版本",非"早于"):')
            for e in archive_cands[:10]:
                print(f"  - {e.id}  status={e.fields.get('status')}  "
                      f"version={e.fields.get('version')}")
            if len(archive_cands) > 10:
                print(f"  ... and {len(archive_cands) - 10} more")

    if agent_md.is_file():
        an = len(agent_md.read_text(encoding="utf-8").splitlines())
        marker = "  ← consider 整理" if an >= args.agent_cap - 10 else ""
        print(f"\nAGENT.md: {an} lines (cap {args.agent_cap}){marker}")

    if result.errors:
        print(f"\nParse errors: {len(result.errors)} (run validate.py for details)")
        if args.strict_parse:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
