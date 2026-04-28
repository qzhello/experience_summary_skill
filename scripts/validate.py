"""Validate .experience/log.md against conventions.md.

Behavior contract: see scripts-contract.md.

Defaults:
- only checks log.md
- --check-agent extends to AGENT.md (W003 + W005)
- error → exit 1
- --strict: warning → exit 1 too
- --strict-parse: any parse-level error → exit 1 too

Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.parse import (  # noqa: E402
    parse_log, find_experience_dir, ParseResult,
    VALID_TYPES, VALID_STATUSES, VALID_SEVERITIES, ID_RE,
)


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
AGENT_LINK_RE = re.compile(r"log\.md#([a-z0-9-]+)")

# W006: secret-like patterns in entry body. Conservative set — high signal, low false positive.
# Each entry: (compiled_regex, human_label).
SECRET_PATTERNS = [
    (re.compile(r"\bghp_[A-Za-z0-9_]{30,}"), "GitHub PAT (ghp_)"),
    (re.compile(r"\bgh[osu]_[A-Za-z0-9_]{30,}"), "GitHub OAuth/server token"),
    (re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}"), "API key (sk-…)"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bxox[bposa]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"), "JWT"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{30,}"), "Bearer token"),
    (re.compile(
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_!@#$%^&*+=./\-]{8,}"
    ), "credential assignment"),
]


def _scan_secrets(text: str) -> list:
    """Return [(label, redacted_snippet), ...] for any secret-like patterns hit."""
    hits = []
    for pattern, label in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            snippet = m.group(0)
            redacted = (snippet[:4] + "***") if len(snippet) > 6 else "***"
            hits.append((label, redacted))
    return hits


@dataclass
class Issue:
    level: str   # "error" | "warning"
    code: str
    entry_id: str
    message: str


def _check_anchor(anchor: str) -> bool:
    if not anchor:
        return False
    parts = [p.strip() for p in anchor.split(",")]
    if len(parts) > 3:
        return False
    for p in parts:
        if ":" not in p:
            return False
        path_part, sym = p.split(":", 1)
        if not path_part.strip() or not sym.strip():
            return False
    return True


def _detect_supersedes_cycles(entries) -> list:
    """Return list of (entry_id, cycle_chain_str) for any supersedes cycles."""
    sup_map = {}
    for e in entries:
        v = e.fields.get("supersedes", "").strip()
        if v:
            sup_map[e.id] = v

    reported = set()
    cycles = []
    for start in list(sup_map.keys()):
        if start in reported:
            continue
        seen = []
        cur = start
        while cur in sup_map:
            if cur in seen:
                cycle = seen[seen.index(cur):]
                chain = " → ".join(cycle + [cur])
                for c in cycle:
                    reported.add(c)
                cycles.append((cycle[0], chain))
                break
            seen.append(cur)
            cur = sup_map[cur]
    return cycles


def validate(
    result: ParseResult,
    *,
    stale_days: int,
    agent_cap_warn: int,
    log_lines: int,
    check_agent: bool,
    agent_md_path,
    secret_scan: bool,
) -> list:
    issues: list = []
    entries = result.entries
    today = date.today()

    # E001 duplicate id
    seen: dict = {}
    for e in entries:
        seen[e.id] = seen.get(e.id, 0) + 1
    for eid, cnt in seen.items():
        if cnt > 1:
            issues.append(Issue("error", "E001", eid, f"duplicate id ({cnt} occurrences)"))

    ids_set = set(seen.keys())

    for e in entries:
        f = e.fields

        if not ID_RE.match(e.id):
            issues.append(Issue("error", "E002", e.id,
                                "id format must be YYYY-MM-DD-<kebab-slug>"))

        if e.type not in VALID_TYPES:
            issues.append(Issue("error", "E003", e.id, f"invalid type: {e.type!r}"))

        ver = f.get("version", "").strip()
        if not ver:
            issues.append(Issue("error", "E004", e.id, "version field empty or missing"))
        elif ver == "unknown":
            issues.append(Issue("warning", "W001", e.id, "version is 'unknown' — consider filling in"))

        st = f.get("status", "").strip()
        if st not in VALID_STATUSES:
            issues.append(Issue("error", "E005", e.id, f"invalid status: {st!r}"))

        if st == "fixed" and e.type != "bug":
            issues.append(Issue("error", "E013", e.id,
                                f"status=fixed only allowed for type=bug (got type={e.type!r})"))

        sev = f.get("severity", "").strip()
        if e.type in ("bug", "pitfall"):
            if not sev:
                issues.append(Issue("error", "E006", e.id, "bug/pitfall must have severity"))
            elif sev not in VALID_SEVERITIES:
                issues.append(Issue("error", "E007", e.id, f"invalid severity: {sev!r}"))
        else:
            if sev:
                issues.append(Issue("error", "E008", e.id,
                                    f"{e.type} must NOT have severity field"))

        anchor = f.get("anchor", "").strip()
        if e.type in ("bug", "pitfall"):
            if not anchor:
                issues.append(Issue("error", "E009", e.id, "bug/pitfall must have anchor"))
            elif not _check_anchor(anchor):
                issues.append(Issue("error", "E010", e.id,
                                    f"anchor format invalid: {anchor!r} (need path:line or path:symbol)"))
        elif anchor and not _check_anchor(anchor):
            issues.append(Issue("error", "E010", e.id,
                                f"anchor format invalid: {anchor!r}"))

        bullet_keys = {b.split(":", 1)[0].strip() for b in e.body_bullets if ":" in b}

        if e.type in ("bug", "pitfall"):
            for k in ("trigger", "cause", "fix"):
                if k not in bullet_keys:
                    issues.append(Issue("error", "E011", e.id,
                                        f"bug/pitfall body missing '{k}:' bullet"))

        if e.type == "decision":
            for k in ("alternatives", "rationale"):
                if k not in bullet_keys:
                    issues.append(Issue("error", "E012", e.id,
                                        f"decision body missing '{k}:' bullet"))

        lv = f.get("last_verified", "").strip()
        if not lv:
            issues.append(Issue("error", "E016", e.id, "last_verified missing"))
        elif not DATE_RE.match(lv):
            issues.append(Issue("error", "E016", e.id,
                                f"last_verified format invalid: {lv!r}"))
        else:
            try:
                d = date.fromisoformat(lv)
                if st == "active" and (today - d).days > stale_days:
                    issues.append(Issue("warning", "W002", e.id,
                                        f"active entry not verified for {(today - d).days} days "
                                        f"(threshold {stale_days})"))
            except ValueError:
                issues.append(Issue("error", "E016", e.id, f"last_verified not a real date: {lv!r}"))

        sup = f.get("supersedes", "").strip()
        if sup and sup not in ids_set:
            issues.append(Issue("error", "E014", e.id,
                                f"supersedes points to nonexistent id: {sup!r}"))

        # W006 secret-like patterns in entry body
        if secret_scan and e.body:
            for label, redacted in _scan_secrets(e.body):
                issues.append(Issue("warning", "W006", e.id,
                                    f"possible {label} in body: {redacted} — "
                                    f"check before commit / consider redacting"))

    # E017 supersedes cycle
    for start_id, chain in _detect_supersedes_cycles(entries):
        issues.append(Issue("error", "E017", start_id, f"supersedes cycle: {chain}"))

    # E015 from parse-level errors
    for pe in result.errors:
        if "---" in pe.message or "YAML" in pe.message:
            issues.append(Issue("error", "E015", pe.entry_id or "-",
                                f"line {pe.line}: {pe.message}"))

    # AGENT.md only when --check-agent
    if check_agent and agent_md_path is not None and agent_md_path.is_file():
        agent_text = agent_md_path.read_text(encoding="utf-8")
        agent_lines = len(agent_text.splitlines())

        # W006 also scans AGENT.md when --check-agent is on
        if secret_scan:
            for label, redacted in _scan_secrets(agent_text):
                issues.append(Issue("warning", "W006", "-",
                                    f"possible {label} in AGENT.md: {redacted}"))
        if agent_lines > agent_cap_warn:
            issues.append(Issue("warning", "W003", "-",
                                f"AGENT.md is {agent_lines} lines (warn at {agent_cap_warn})"))

        # W005: AGENT.md links non-active entries
        status_by_id = {e.id: e.fields.get("status", "") for e in entries}
        for m in AGENT_LINK_RE.finditer(agent_text):
            ref = m.group(1)
            st = status_by_id.get(ref)
            if st is None:
                issues.append(Issue("warning", "W005", "-",
                                    f"AGENT.md links unknown id: {ref!r}"))
            elif st != "active":
                issues.append(Issue("warning", "W005", "-",
                                    f"AGENT.md links non-active id: {ref!r} (status={st})"))

    # W004 log.md size hint (always on; pure size signal)
    if log_lines > 300:
        issues.append(Issue("warning", "W004", "-",
                            f"log.md is {log_lines} lines — consider 整理"))

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate .experience/log.md against conventions.")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--strict", action="store_true",
                    help="Treat warnings as errors")
    ap.add_argument("--strict-parse", action="store_true",
                    help="Any parse-level error → exit 1")
    ap.add_argument("--stale-days", type=int, default=90)
    ap.add_argument("--agent-cap", type=int, default=140)
    ap.add_argument("--check-agent", action="store_true",
                    help="Also validate AGENT.md (size + non-active links + secret scan)")
    ap.add_argument("--no-secret-scan", action="store_true",
                    help="Disable W006 secret-pattern scan in entry bodies")
    ap.add_argument("--format", choices=["table", "json"], default="table")
    args = ap.parse_args()

    exp_dir = find_experience_dir(args.root)
    if exp_dir is None:
        print("error: .experience/log.md not found (use --root or run inside project)",
              file=sys.stderr)
        return 2

    log_path = exp_dir / "log.md"
    result = parse_log(log_path)
    log_lines = len(log_path.read_text(encoding="utf-8").splitlines())
    agent_md = exp_dir / "AGENT.md"

    issues = validate(
        result,
        stale_days=args.stale_days,
        agent_cap_warn=args.agent_cap,
        log_lines=log_lines,
        check_agent=args.check_agent,
        agent_md_path=agent_md,
        secret_scan=not args.no_secret_scan,
    )
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if args.format == "json":
        out = {
            "log_path": str(log_path),
            "entries_parsed": len(result.entries),
            "parse_errors": len(result.errors),
            "errors": [asdict(i) for i in errors],
            "warnings": [asdict(i) for i in warnings],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for i in errors + warnings:
            print(f"{i.level.upper():7} {i.code} [{i.entry_id}] {i.message}")
        if not issues:
            print("(no issues)")
        print(f"\n{len(result.entries)} entries · "
              f"{len(errors)} errors · {len(warnings)} warnings · "
              f"{len(result.errors)} parse errors")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    if args.strict_parse and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
