#!/usr/bin/env python3
"""Fail CI if a NEW Alembic migration creates a table in `public` without enabling RLS.

WHY THIS EXISTS (DEC-135):
Supabase's default grants hand `anon` and `authenticated` full DML on every new
table in `public`, and neither role has BYPASSRLS. So a table created without
`ENABLE ROW LEVEL SECURITY` is not merely readable by the internet -- it is
INSERT / UPDATE / DELETE / TRUNCATE-able by anyone holding the publishable anon
key, which ships inside the frontend bundle and is public by construction.

This has now happened TWICE in this repo:
  * migration 042 -> `processed_webhook_events`, remediated by 044 (2026-06-24)
  * migration 046 -> 10 Tier A threshold tables, remediated by 048 (2026-08-06)
After the first occurrence a written rule was added. The rule did not prevent the
second occurrence five weeks later. That is why this check is mechanical.

DEFENCE IN DEPTH -- this is layer 2 of 2:
  Layer 1: the `rls_auto_enable_trg` event trigger installed by migration 048.
           It enables RLS automatically, at the database level, on any CREATE
           TABLE in `public`. Stronger, because it cannot be forgotten.
  Layer 2: this script. It exists because an event trigger can be dropped,
           disabled, or simply absent on a newly provisioned environment -- and
           a red CI run is visible, whereas a missing event trigger is silent.

SCOPE: only migrations numbered ABOVE `CUTOFF` are enforced. Everything at or
below it predates the guard and is grandfathered -- justified by direct
verification on 2026-08-06 that ZERO tables in `public` had relrowsecurity=false
on either snapai-staging-use1 or snapai-prod-use1. The legacy files are not
statically checkable anyway: 001 enables RLS through an f-string loop over a
table list, which no regex can resolve reliably. Enforcing forward-only keeps the
signal honest instead of drowning it in grandfathered noise.

Exit 0 = clean. Exit 1 = violation. Exit 2 = ran from the wrong directory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VERSIONS_DIR = Path("scopesnap-api/db/migrations/versions")

# Migrations numbered <= CUTOFF predate this guard. See SCOPE above.
# Raising this number to silence a failure defeats the entire point of the file.
CUTOFF = 48

RAW_CREATE = re.compile(
    r"""CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["']?([A-Za-z_][\w.]*)["']?""",
    re.IGNORECASE,
)
OP_CREATE = re.compile(r"""op\.create_table\(\s*["']([A-Za-z_]\w*)["']""")
RLS_ENABLE = re.compile(r"""ENABLE\s+ROW\s+LEVEL\s+SECURITY""", re.IGNORECASE)
TABLE_IN_RLS_STMT = re.compile(
    r"""ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?["']?(?:public\.)?["']?([A-Za-z_]\w*)["']?"""
    r"""\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY""",
    re.IGNORECASE,
)

NON_PUBLIC_PREFIXES = ("research.", "auth.", "storage.", "extensions.", "cron.")
PARSE_ARTEFACTS = {"if", "not", "exists", "as", "into", "select"}
LEADING_NUM = re.compile(r"^(\d+)")


def migration_number(name: str) -> int | None:
    m = LEADING_NUM.match(name)
    return int(m.group(1)) if m else None


def tables_created(text: str) -> set[str]:
    found: set[str] = set()
    for m in RAW_CREATE.finditer(text):
        raw = m.group(1)
        if raw.lower().startswith(NON_PUBLIC_PREFIXES):
            continue
        name = raw.split(".")[-1].lower()
        if name in PARSE_ARTEFACTS:
            continue
        found.add(name)
    for m in OP_CREATE.finditer(text):
        found.add(m.group(1).lower())
    return found


def main() -> int:
    if not VERSIONS_DIR.is_dir():
        print(f"ERROR: {VERSIONS_DIR} not found -- run this from the repo root.", file=sys.stderr)
        return 2

    violations: list[tuple[str, str]] = []
    enforced = skipped = 0

    for path in sorted(VERSIONS_DIR.glob("*.py")):
        num = migration_number(path.name)
        if num is None or num <= CUTOFF:
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        created = tables_created(text)
        if not created:
            continue
        enforced += 1
        named = {m.group(1).lower() for m in TABLE_IN_RLS_STMT.finditer(text)}
        # A loop like `for t in [...]: op.execute(f"ALTER TABLE {t} ENABLE ...")`
        # cannot be resolved statically. If the file enables RLS at all but names
        # no table literally, treat it as intentional and let review catch it.
        if RLS_ENABLE.search(text) and not named:
            continue
        for tbl in sorted(created - named):
            violations.append((path.name, tbl))

    if violations:
        print("RLS GUARD FAILED -- migration(s) create public tables without enabling RLS.\n")
        for fname, tbl in violations:
            print(f"  {fname}: table '{tbl}' -- no ENABLE ROW LEVEL SECURITY in the same migration")
        print(
            "\nThis blocks the build because Supabase grants anon/authenticated full DML on\n"
            "new public tables and neither role has BYPASSRLS. Without RLS the table is\n"
            "readable AND writable by anyone holding the public anon key. See DEC-135.\n"
            "\nFix -- add to the SAME migration, once per table:\n"
            '    op.get_bind().execute(text(\n'
            '        "ALTER TABLE IF EXISTS public.<table> ENABLE ROW LEVEL SECURITY"))\n'
        )
        return 1

    print(f"RLS guard passed -- {enforced} enforced migration(s) checked, "
          f"{skipped} at or below cutoff {CUTOFF}, 0 violations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
