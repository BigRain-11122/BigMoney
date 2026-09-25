"""Round-report R-line linter.

Task 01 (T-70 pilot): validates the five-field row contract of round
reports -- | <YYYY-MM-DD HH:MM> | <R-number label> | <verdict head> |
<did body> | <next pointer> |. Lint mode never writes files, never touches
the network, and prints ASCII only.

Exit codes: 0 ok / 1 violations or failed assertion / 2 usage or missing file.
"""

import re
import sys

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
# A candidate R line starts a table row with a 4-digit date-ish token;
# strict checks run on candidates only (so separators and headers are skipped).
CANDIDATE_RE = re.compile(r"^\| \d{4}-")
ROUND_RE = re.compile(r"^R\d+")

USAGE = "usage: rr_lint.py selftest | <file.md>"


def is_candidate(line):
    """True if the line starts a table row whose first cell looks like a date."""
    return bool(CANDIDATE_RE.match(line))


def _split_fields(line):
    """Split one table row into stripped cells (leading/trailing pipes removed)."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [p.strip() for p in s.split(" | ")]


def check_line(line):
    """Return a list of ASCII violation strings for one candidate R line."""
    parts = _split_fields(line)
    violations = []
    if len(parts) != 5:
        violations.append("field_count=%d expected=5" % len(parts))
        return violations
    ts, label, f3, f4, f5 = parts
    if not TS_RE.match(ts):
        violations.append("timestamp_format_invalid")
    if not ROUND_RE.match(label):
        violations.append("round_label_missing_R_prefix")
    for name, value in (("field3", f3), ("field4", f4), ("field5", f5)):
        if not value:
            violations.append(name + "_empty")
    return violations


def lint_lines(lines):
    """Yield (line_no, violation) pairs for every R-line violation found."""
    for no, line in enumerate(lines, 1):
        if not is_candidate(line):
            continue
        for v in check_line(line):
            yield no, v


def lint_file(path):
    """Lint a markdown file (utf-8, utf-8-sig tolerated). Returns violations."""
    with open(path, "r", encoding="utf-8-sig") as fh:
        return list(lint_lines(fh))


def _selftest():
    valid = [
        "| 2026-09-25 11:12 | R155 | verdict head | did body text | next pointer |",
        "| 2026-09-24 08:30 | R57 | GREEN verdict | did: S0 pull clean | next: wave slice |",
        "| 2026-09-25 05:47 | R127 (dept:research) | GREEN | S6 legs all green | next: idle watch |",
    ]
    for line in valid:
        assert check_line(line) == [], "valid line flagged: %r" % line
    bad = {
        "| 2026-09-25 11:12 | R155 | head | body |": "field_count=4",
        "| 2026-9-5 11:12 | R155 | head | body | next |": "timestamp_format_invalid",
        "| 2026-09-25 11:12 | 155 | head | body | next |": "round_label_missing_R_prefix",
        "| 2026-09-25 11:12 | R155 | head |  | next |": "field4_empty",
    }
    for line, expect in bad.items():
        got = check_line(line)
        assert any(expect in v for v in got), "violation %r not caught in %r -> %r" % (
            expect, line, got)
    # candidate gate: separators, headers, plain rows are not R lines
    non_candidates = [
        "|---|---|---|---|---|",
        "| timestamp | round | verdict | did | next |",
        "plain text without a table row",
    ]
    for line in non_candidates:
        assert not is_candidate(line), "non-candidate treated as R line: %r" % line
    # lint_lines path (file-mode contract, no files read)
    found = list(lint_lines(["|---|---|---|---|---|", list(bad)[0]]))
    assert found == [(2, "field_count=4 expected=5")], "lint_lines result: %r" % found
    print("selftest: 12 assertions ALL PASS")
    return 0


def main(argv):
    if len(argv) < 2:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    path = argv[1]
    try:
        violations = lint_file(path)
    except FileNotFoundError:
        print("file not found: %s" % path, file=sys.stderr)
        return 2
    for no, v in violations:
        print("L%d: %s" % (no, v))
    print("violations=%d" % len(violations))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
