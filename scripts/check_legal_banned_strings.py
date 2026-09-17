#!/usr/bin/env python3
"""check_legal_banned_strings.py - legal-copy guard for homeowner-facing / public surfaces.

Blocks a commit (exit non-zero) when a line in one of the enforced target paths
contains a banned token. Protects against copy drift into unauthorized
"diagnosis" claims, DEC-088 predictive/superlative bans, superlative
self-claims, and city/geo leaking into PUBLIC copy (geo stays backend-only).

Usage:
  python scripts/check_legal_banned_strings.py [FILE ...]   # scan given files, or the
                                                            # full target set if none given
  python scripts/check_legal_banned_strings.py --self-test  # verify checker catches a bad string

Pre-commit passes the staged filenames as positional args; anything outside the
enforced target paths is ignored, so passing the whole staged set is safe.

Output per violation:  file:line: <token> :: <offending line, trimmed>
Exit 1 if any violation, else prints "OK: no banned strings" and exit 0.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGET_PATHS = [
    "scopesnap-web/app/tech/",
    "scopesnap-web/app/d/",
    "scopesnap-web/app/r/",
    "scopesnap-web/app/methodology/",
    "scopesnap-web/components/FaultResolutionScreen.tsx",
    "scopesnap-api/templates/",
    "scopesnap-api/services/email.py",
    "scopesnap-api/prompts/homeowner_narrative.py",
]

PUBLIC_PATHS = [
    "scopesnap-web/app/tech/",
    "scopesnap-web/app/methodology/",
]

TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".html", ".htm", ".txt", ".md", ".mdx",
    ".json", ".css", ".scss",
}

# Category 1: diagnosis family. Bare diagnos* is flagged UNLESS the same line also
# carries a negation / contractor-subject signal (a disclaimer).
DIAGNOSIS_RE = re.compile(r"\bdiagnos\w*", re.IGNORECASE)
DIAGNOSIS_ALLOW_SIGNALS = [
    "not ",
    "does not",
    "no ",
    "isn't",
    "n't",
    "your contractor",
    "the contractor",
    "the technician",
    "the tech",
    "licensed",
    "certified",
]

# Category 2: DEC-088 predictive / superlative bans (case-insensitive substring).
DEC088_TOKENS = [
    "prevent",
    "guarantee",
    "ensure",
    "will not",
    "lasts",
    "eliminates",
    "stop forever",
    "save you $",
    "bill will drop",
    "5-year savings",
    "issues get worse",
]

# DEC-088 allowances: approved negated/disclaimer phrasings that legitimately
# contain a banned token (counsel-drafted safety guidance / disclaimers).
DEC088_ALLOW_PHRASES = [
    "not a guarantee",
    "no guarantee",
    "without guarantee",
    "ensure a licensed",
    "ensure a qualified",
    "ensure a full",
    "ensure that a licensed",
]

# Category 3: superlative self-claims (case-insensitive substring).
SELF_CLAIM_TOKENS = [
    "honest recommendation",
    "no upsell",
    "most honest",
]

# Category 4: city / geo - PUBLIC files only (case-insensitive substring).
GEO_TOKENS = [
    "houston",
    "katy",
    "sugar land",
    "cypress",
    "pasadena tx",
]


def _norm(path):
    return path.replace("\\", "/")


def _contains_target(path, target):
    path = _norm(path)
    target = _norm(target)
    if target.endswith("/"):
        return path.startswith(target) or ("/" + target) in ("/" + path)
    return path == target or path.endswith("/" + target)


def path_is_targeted(path):
    return any(_contains_target(path, t) for t in TARGET_PATHS)


def path_is_public(path):
    return any(_contains_target(path, t) for t in PUBLIC_PATHS)


def check_line(line, is_public):
    """Return a list of (token, reason) violations found on this line."""
    violations = []
    low = line.lower()

    if DIAGNOSIS_RE.search(line):
        allowed = any(sig in low for sig in DIAGNOSIS_ALLOW_SIGNALS)
        if not allowed:
            m = DIAGNOSIS_RE.search(line)
            violations.append((m.group(0), "diagnosis-family"))

    for tok in DEC088_TOKENS:
        if tok in low:
            if any(tok in allow and allow in low for allow in DEC088_ALLOW_PHRASES):
                continue
            violations.append((tok, "DEC-088"))

    for tok in SELF_CLAIM_TOKENS:
        if tok in low:
            violations.append((tok, "self-claim"))

    if is_public:
        for tok in GEO_TOKENS:
            if tok in low:
                violations.append((tok, "geo-in-public"))

    return violations


def iter_target_files(explicit_files):
    """Yield (abs_path, rel_path) for files to scan."""
    if explicit_files:
        for f in explicit_files:
            abs_f = f if os.path.isabs(f) else os.path.join(REPO_ROOT, f)
            rel = _norm(os.path.relpath(abs_f, REPO_ROOT))
            if not os.path.isfile(abs_f):
                continue
            if path_is_targeted(rel):
                yield abs_f, rel
        return

    seen = set()
    for t in TARGET_PATHS:
        abs_t = os.path.join(REPO_ROOT, t)
        if os.path.isfile(abs_t):
            rel = _norm(os.path.relpath(abs_t, REPO_ROOT))
            if rel not in seen:
                seen.add(rel)
                yield abs_t, rel
        elif os.path.isdir(abs_t):
            for root, _dirs, files in os.walk(abs_t):
                for name in files:
                    ext = os.path.splitext(name)[1].lower()
                    if ext and ext not in TEXT_EXTS:
                        continue
                    abs_f = os.path.join(root, name)
                    rel = _norm(os.path.relpath(abs_f, REPO_ROOT))
                    if rel not in seen:
                        seen.add(rel)
                        yield abs_f, rel


def scan_file(abs_path, rel_path):
    out = []
    is_public = path_is_public(rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
            for lineno, raw in enumerate(fh, start=1):
                line = raw.rstrip("\n")
                for token, _reason in check_line(line, is_public):
                    out.append("{}:{}: {} :: {}".format(rel_path, lineno, token, line.strip()))
    except (OSError, UnicodeError) as exc:  # pragma: no cover
        out.append("{}:0: <read-error> :: {}".format(rel_path, exc))
    return out


def run_scan(explicit_files):
    violations = []
    for abs_f, rel in iter_target_files(explicit_files):
        violations.extend(scan_file(abs_f, rel))

    if violations:
        for v in violations:
            print(v)
        print("\nFAIL: {} banned-string violation(s) found.".format(len(violations)))
        return 1

    print("OK: no banned strings")
    return 0


def self_test():
    """Write a temp file with a known-bad line and assert the checker catches it."""
    bad_line = "This will prevent breakdowns"
    with tempfile.TemporaryDirectory() as tmp:
        hits = check_line(bad_line, is_public=False)
        assert hits, "self-test FAILED: 'prevent' not caught in DEC-088 scan"
        assert any(tok == "prevent" for tok, _ in hits), (
            "self-test FAILED: expected 'prevent' token"
        )

        f = os.path.join(tmp, "sample.tsx")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("const ok = 1;\n")
            fh.write(bad_line + "\n")
        results = scan_file(f, "scopesnap-web/app/tech/sample.tsx")
        assert any("prevent" in r for r in results), (
            "self-test FAILED: scan_file did not flag the offending line"
        )

    print("self-test PASSED: banned string 'prevent' correctly caught")
    return 0


def run_staged():
    """Scan only NEWLY ADDED lines in the git staged diff, within target paths.

    Pre-commit drift-guard: never blocks a commit over pre-existing lines
    (code identifiers, cross-line disclaimers) - only over newly added banned copy.
    """
    import subprocess
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached", "--unified=0", "--no-color"],
            cwd=REPO_ROOT, text=True, errors="replace",
        )
    except Exception as exc:  # pragma: no cover
        print("WARN: could not read staged diff ({}); skipping.".format(exc))
        return 0

    violations = []
    cur_rel = None
    is_public = False
    new_lineno = 0
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            cur_rel = _norm(raw[6:])
            is_public = path_is_public(cur_rel)
            continue
        if raw.startswith("@@"):
            m = re.search(r"[+](\d+)", raw)
            new_lineno = int(m.group(1)) if m else 0
            continue
        if cur_rel is None or not path_is_targeted(cur_rel):
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            line = raw[1:]
            for token, _reason in check_line(line, is_public):
                violations.append("{}:{}: {} :: {}".format(cur_rel, new_lineno, token, line.strip()))
            new_lineno += 1
        elif not raw.startswith("-"):
            new_lineno += 1

    if violations:
        for v in violations:
            print(v)
        print("\nFAIL: {} banned-string violation(s) in newly added lines.".format(len(violations)))
        print("Homeowner-facing/public surfaces. Fix the copy or route via Codie/Alfred.")
        return 1
    print("OK: no banned strings in staged changes")
    return 0


def main(argv):
    args = list(argv[1:])
    if "--self-test" in args:
        return self_test()
    if "--staged" in args:
        return run_staged()
    explicit_files = [a for a in args if not a.startswith("-")]
    return run_scan(explicit_files)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
