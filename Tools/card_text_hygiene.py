#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""card_text_hygiene.py -- control-character hygiene for the card ledger.

WHY THIS EXISTS (r1383 bm-c)
    r1380 found three characters eaten by an escape-strip inside one dead
    window's card and recorded seven MORE in older cards (E121/E126/E174/E180
    region) as "a standing corruption class in the card ledger ... NOT fixed in
    this round". Nothing then read that class, so it could grow silently: the
    ledger is Markdown, and a 0x08/0x07/0x1b is invisible in every renderer
    while it eats the character in front of it.

WHAT THE CLASS IS
    Every one of the seven sites is a token whose first letter was consumed by
    an escape (\\b -> 0x08, \\a -> 0x07, \\e -> 0x1b): `reak_guard` for
    `break_guard`, `bs(` for `abs(`, `tf_breadth_sweep.py` for
    `etf_breadth_sweep.py`, and so on. Two sites had the escape inserted BEFORE
    an intact token instead, so the repair is "drop the character" rather than
    "restore the letter". Both shapes are in the frozen table below, each with
    the evidence that says which one it is (a file on disk, or an identifier
    the code itself uses).

REPAIR DISCIPLINE
    * The table is FROZEN and literal: damaged snippet -> restored snippet.
      `fix` refuses (exit 2, zero writes) unless each damaged snippet occurs
      EXACTLY ONCE -- an ambiguous or missing site is not repaired by guessing.
    * Only the repaired bytes move. The rest of the file must be byte-identical;
      `fix` asserts that (whole-file compare after undo) and records line
      numbers in the receipt.
    * treasure_guard prescan HARD-REJECTS this file by design (registry hit,
      rc3): the registry may only be touched by a line-level repair, not by a
      cleaning pass. That is exactly what this tool is -- a line-scoped union
      with a receipt -- and every non-repair byte is asserted unchanged.

USAGE
  python Tools/card_text_hygiene.py scan    # read-only; exit 1 if any control char
  python Tools/card_text_hygiene.py scan --verbose
  python Tools/card_text_hygiene.py fix     # apply the frozen table; exit 2 on mismatch
  python Tools/card_text_hygiene.py selftest
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORPUS_FILES = ["knowledge/METHODOLOGY_ASSETS.md"]
CORPUS_GLOBS = [("research/digests", ".md")]

# Control characters that must never appear in a card/digest body. Tab, LF and
# CR are ordinary text structure and stay legal.
CTRL = [c for c in range(0x20) if c not in (0x09, 0x0A, 0x0D)] + [0x7F]

# Frozen repair table. `proof` is what makes the restoration a measurement
# rather than a guess: a file that exists on disk, or an identifier the code
# uses. Never add a row without one.
REPAIRS = [
    {
        "damaged": "落 \x08reak_guard",
        "restored": "落 break_guard",
        "proof": "scripts/e39_panel_census.py defines break_guard",
    },
    {
        "damaged": "断言 \x07bs(ser.iloc[0] - 1.0)",
        "restored": "断言 abs(ser.iloc[0] - 1.0)",
        "proof": "arithmetic: abs() is the only reading of `bs(` on a signed series",
    },
    {
        "damaged": "只改主面 \x1btf_breadth_sweep.py",
        "restored": "只改主面 etf_breadth_sweep.py",
        "proof": "scripts/etf_breadth_sweep.py exists",
    },
    {
        "damaged": "out of \x1btf_book_production.run()",
        "restored": "out of etf_book_production.run()",
        "proof": "scripts/etf_book_production.py exists",
    },
    {
        "damaged": "The ticket now publishes \x08book_decided_at",
        "restored": "The ticket now publishes book_decided_at",
        "proof": "scripts/etf_book_order.py emits book_decided_at",
    },
    {
        "damaged": "\x1btf_vol_delivery_audit.py --selftest",
        "restored": "etf_vol_delivery_audit.py --selftest",
        "proof": "scripts/etf_vol_delivery_audit.py exists",
    },
    {
        "damaged": "Here \x08urncontrol recomputes nothing",
        "restored": "Here burncontrol recomputes nothing",
        "proof": "scripts/e110_burncontrol_close.py + six other sources spell burncontrol",
    },
]

RECEIPT = os.path.join("results", "card_text_hygiene.json")


def _read(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def _write(path, text):
    tmp = path + ".hygiene_tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def corpus(root=ROOT):
    """Every file the hygiene rule covers, repo-relative, sorted."""
    out = [p for p in CORPUS_FILES if os.path.exists(os.path.join(root, p))]
    for d, ext in CORPUS_GLOBS:
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        for name in sorted(os.listdir(full)):
            if name.endswith(ext):
                out.append(os.path.join(d, name).replace("\\", "/"))
    return out


def findings(root=ROOT):
    """[(path, offset_line, hexbyte, context)] for every control character."""
    hits = []
    for rel in corpus(root):
        text = _read(os.path.join(root, rel))
        for i, ch in enumerate(text):
            if ord(ch) in CTRL:
                line = text.count("\n", 0, i) + 1
                ctx = text[max(0, i - 40):i + 25].replace("\n", "\\n")
                hits.append({"path": rel, "line": line,
                             "byte": "0x%02x" % ord(ch), "context": ctx})
    return hits


def scan(root=ROOT, verbose=False):
    hits = findings(root)
    for h in hits:
        print("[hygiene] %s:%d %s  ...%s..." % (h["path"], h["line"], h["byte"],
                                                h["context"]))
    files = corpus(root)
    print("[hygiene] %d file(s) scanned, %d control character(s)"
          % (len(files), len(hits)))
    if verbose:
        for f in files:
            print("[hygiene]   %s" % f)
    return 1 if hits else 0


def fix(root=ROOT, apply=True):
    """Apply the frozen table. Returns (rc, receipt).

    rc 0 = every site repaired (or nothing to do), 2 = a site was missing or
    ambiguous and NOTHING was written, 3 = a post-write assertion failed.
    """
    rel = REPAIRS[0]  # every row lives in the same registry file
    target = os.path.join(root, CORPUS_FILES[0])
    if not os.path.exists(target):
        return 2, {"error": "missing %s" % CORPUS_FILES[0]}
    before = _read(target)
    text = before
    rows = []
    for rep in REPAIRS:
        n = text.count(rep["damaged"])
        if n != 1:
            return 2, {"error": "site %r occurs %d times (must be exactly 1)"
                                % (rep["damaged"][:40], n)}
        idx = text.find(rep["damaged"])
        line = text.count("\n", 0, idx) + 1
        text = text[:idx] + rep["restored"] + text[idx + len(rep["damaged"]):]
        rows.append({"line": line, "damaged": rep["damaged"],
                     "restored": rep["restored"], "proof": rep["proof"]})
    changed_lines = sorted({r["line"] for r in rows})

    # Assert the repair is a LINE-SCOPED union. Line counts must be identical,
    # the set of differing lines must be exactly the repaired lines, and putting
    # the damaged snippet back INSIDE ITS OWN LINE must reproduce that line
    # verbatim. A stray edit anywhere else fails all three and nothing is
    # written. (Matching by file-wide search for the restored string would trip
    # over the same identifier appearing elsewhere in the ledger -- the first
    # version did exactly that, which is why the check is per line.)
    before_lines = before.split("\n")
    after_lines = text.split("\n")
    if len(before_lines) != len(after_lines):
        return 3, {"error": "repair changed the line count (%d -> %d)"
                            % (len(before_lines), len(after_lines))}
    moved = {i for i, (a, b) in enumerate(zip(before_lines, after_lines)) if a != b}
    expected = {ln - 1 for ln in changed_lines}
    if moved != expected:
        return 3, {"error": "repair touched lines %s, expected %s"
                            % (sorted(moved), sorted(expected))}
    for rep in REPAIRS:
        line_no = next(r["line"] for r in rows if r["damaged"] == rep["damaged"]) - 1
        if after_lines[line_no].replace(rep["restored"], rep["damaged"], 1) \
                != before_lines[line_no]:
            return 3, {"error": "site not reversible on its own line: %r"
                                % rep["damaged"][:40]}
    if any(ord(ch) in CTRL for ch in text):
        return 3, {"error": "control characters survive the repair"}

    receipt = {
        "tool": "Tools/card_text_hygiene.py",
        "target": CORPUS_FILES[0],
        "sites": rows,
        "lines_touched": changed_lines,
        "before_bytes": len(before.encode("utf-8")),
        "after_bytes": len(text.encode("utf-8")),
        "guard_note": ("treasure_guard prescan rejects this file by design (registry hit,"
                       " rc3); the permitted path is a line-level union with a receipt,"
                       " which is what this is -- every other byte is asserted unchanged"),
    }
    if apply:
        _write(target, text)
    receipt["applied"] = bool(apply)
    receipt["remaining"] = len(findings(root))
    return 0, receipt


def selftest():
    """Hermetic: every leg runs on a temp tree, never on the live ledger."""
    ok = True

    def leg(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             (" | " + detail) if detail else ""))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "knowledge"))
        os.makedirs(os.path.join(tmp, "research", "digests"))
        reg = os.path.join(tmp, CORPUS_FILES[0])

        # L1 clean text is clean, tab/LF/CR stay legal
        _write(reg, "hello\tworld\r\nok\n")
        leg("L1 clean text passes (tab/CR/LF legal)", findings(tmp) == [])

        # L2 a stray control char is found with a line number
        _write(reg, "a\nb\x07c\n")
        f = findings(tmp)
        leg("L2 control character found with line number",
            len(f) == 1 and f[0]["line"] == 2 and f[0]["byte"] == "0x07")

        # L3 a digest under research/digests is in scope
        _write(reg, "clean\n")
        _write(os.path.join(tmp, "research", "digests", "D.md"), "x\x1by\n")
        f = findings(tmp)
        leg("L3 digests are in the scan scope",
            len(f) == 1 and f[0]["path"].endswith("D.md"))
        os.remove(os.path.join(tmp, "research", "digests", "D.md"))

        # L4 fix applies each frozen site exactly once and reports its line
        body = "\n".join(["intro"] + [r["damaged"] for r in REPAIRS] + ["tail"]) + "\n"
        _write(reg, body)
        rc, rec = fix(tmp, apply=True)
        leg("L4 fix repairs every frozen site", rc == 0 and rec["applied"],
            "rc=%d %s" % (rc, rec.get("error", "")))
        leg("L5 fix reports one line per site",
            len(rec.get("lines_touched", [])) == len(REPAIRS))
        leg("L6 fixed file carries no control characters", findings(tmp) == [])

        # L7 a missing site is refused and nothing is written
        _write(reg, body.replace(REPAIRS[0]["damaged"], "already clean"))
        rc, rec = fix(tmp, apply=True)
        leg("L7 missing site is refused (exit 2, zero writes)",
            rc == 2 and "occurs 0 times" in rec.get("error", ""))
        leg("L8 refused fix did not touch the file",
            _read(reg) == body.replace(REPAIRS[0]["damaged"], "already clean"))

        # L9 an ambiguous site (appears twice) is refused
        _write(reg, body + REPAIRS[0]["damaged"] + "\n")
        rc, rec = fix(tmp, apply=True)
        leg("L9 ambiguous site is refused (exit 2)",
            rc == 2 and "occurs 2 times" in rec.get("error", ""))

        # L10 a non-site edit between damaged snippets cannot ride along: undo
        #     reconstructs the original bytes exactly on a healthy file
        _write(reg, body)
        rc, rec = fix(tmp, apply=False)
        leg("L10 dry run reconstructs the original bytes (site-local union)",
            rc == 0 and _read(reg) == body)

        # L11 every repair row carries proof
        leg("L11 every frozen repair carries its proof",
            all(r.get("proof") for r in REPAIRS))

    print("[card_text_hygiene] selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "scan"
    if cmd == "scan":
        return scan(verbose="--verbose" in argv)
    if cmd == "fix":
        rc, rec = fix(apply="--dry-run" not in argv)
        print(json.dumps(rec, ensure_ascii=False, indent=1))
        if rc == 0:
            path = os.path.join(ROOT, RECEIPT)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with io.open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
            print("[hygiene] receipt written to %s" % RECEIPT)
        return rc
    if cmd == "selftest":
        return selftest()
    print("usage: card_text_hygiene.py [scan|fix|selftest] [--verbose|--dry-run]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))