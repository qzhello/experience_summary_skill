"""log.md parser. Stdlib only, Python 3.9+ compatible.

Returns two layers:
- entries: successfully parsed entries (may still violate rules — that's validate.py's job)
- errors:  parse-level errors (malformed structure, YAML separators inside body)

Also provides:
- extract_summary(entry):  unified one-line summary used by query.py / stats.py
- find_experience_dir():   walk up cwd to locate .experience/ root
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


VALID_TYPES = {"bug", "pitfall", "decision", "note"}
VALID_STATUSES = {"active", "stale", "fixed"}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}

ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
HEADING_RE = re.compile(r"^##\s+(\S.*?)\s*$")
KV_RE = re.compile(r"^([a-z_]+):\s*(.*)$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

META_KEYS = {
    "type", "version", "status", "severity",
    "anchor", "last_verified", "supersedes", "tags",
}


@dataclass
class Entry:
    id: str
    type: str
    fields: dict
    body: str
    body_bullets: list
    line_start: int
    line_end: int
    source: str
    source_kind: str = "log"  # "log" | "archive"


@dataclass
class ParseError:
    line: int
    entry_id: Optional[str]
    message: str


@dataclass
class ParseResult:
    entries: list
    errors: list
    file: str


def _strip_comments(text: str) -> str:
    """Remove HTML comments so example entries inside <!-- ... --> don't get parsed."""
    return COMMENT_RE.sub("", text)


def parse_log(path: Path) -> ParseResult:
    """Parse a log.md file. Never raises — bad blocks become ParseError entries."""
    raw = path.read_text(encoding="utf-8")
    text = _strip_comments(raw)
    lines = text.split("\n")
    entries: list = []
    errors: list = []

    heading_indices: list = []
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            heading_indices.append((i, m.group(1).strip()))

    for idx, (start_line, raw_id) in enumerate(heading_indices):
        end_line = (
            heading_indices[idx + 1][0] if idx + 1 < len(heading_indices) else len(lines)
        )
        block = lines[start_line:end_line]
        entry_id = raw_id

        meta: dict = {}
        body_lines: list = []
        body_bullets: list = []
        in_meta = True
        for li, line in enumerate(block[1:], start=1):
            stripped = line.strip()
            # `---` is forbidden anywhere inside an entry, in meta OR body phase
            if stripped == "---":
                errors.append(ParseError(
                    line=start_line + li + 1,
                    entry_id=entry_id,
                    message="YAML '---' separator inside entry",
                ))
                continue
            if in_meta:
                if stripped == "":
                    in_meta = False
                    continue
                m = KV_RE.match(stripped)
                if m and m.group(1) in META_KEYS:
                    meta[m.group(1)] = m.group(2).strip()
                    continue
                # First non-meta line ends the meta block; reprocess as body
                in_meta = False
            body_lines.append(line)
            if stripped.startswith("- "):
                bullet = stripped[2:].strip()
                if bullet:  # skip empty "- " lines
                    body_bullets.append(bullet)

        entries.append(Entry(
            id=entry_id,
            type=meta.get("type", ""),
            fields=meta,
            body="\n".join(body_lines).strip(),
            body_bullets=body_bullets,
            line_start=start_line + 1,
            line_end=end_line,
            source=str(path),
        ))

    return ParseResult(entries=entries, errors=errors, file=str(path))


def extract_summary(entry: Entry) -> str:
    """Single source of truth for one-line summaries.

    bug/pitfall: trigger > fix > cause > <no summary>
    decision:    rationale > context > <no summary>
    note:        first non-meta bullet > <no summary>
    """
    bullets = entry.body_bullets

    def find_kv(key: str):
        prefix = f"{key}:"
        for b in bullets:
            if b.startswith(prefix):
                val = b[len(prefix):].strip()
                if val:
                    return val
        return None

    if entry.type in ("bug", "pitfall"):
        return find_kv("trigger") or find_kv("fix") or find_kv("cause") or "<no summary>"
    if entry.type == "decision":
        return find_kv("rationale") or find_kv("context") or "<no summary>"
    if entry.type == "note":
        for b in bullets:
            if b.startswith("details:"):
                continue
            return b if len(b) <= 200 else b[:197] + "..."
        return "<no summary>"
    return "<no summary>"


def parse_with_archive(exp_dir: Path, *, include_archived: bool) -> ParseResult:
    """Parse log.md and (optionally) details/archive/*.md.

    Each Entry is tagged via .source_kind ('log' | 'archive').
    Errors from archive files are merged into the result.errors list.
    """
    log_path = exp_dir / "log.md"
    result = parse_log(log_path)
    for e in result.entries:
        e.source_kind = "log"

    if include_archived:
        archive_dir = exp_dir / "details" / "archive"
        if archive_dir.is_dir():
            for f in sorted(archive_dir.glob("*.md")):
                ar = parse_log(f)
                for e in ar.entries:
                    e.source_kind = "archive"
                result.entries.extend(ar.entries)
                result.errors.extend(ar.errors)
    return result


def find_experience_dir(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from start (default cwd) until we find .experience/log.md.
    Returns the .experience/ directory or None.
    """
    cur = (start or Path.cwd()).resolve()
    while True:
        candidate = cur / ".experience" / "log.md"
        if candidate.is_file():
            return cur / ".experience"
        if cur.parent == cur:
            return None
        cur = cur.parent
