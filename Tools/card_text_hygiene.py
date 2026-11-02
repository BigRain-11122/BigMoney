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
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORPUS_FILES = ["knowledge/METHODOLOGY_ASSETS.md"]
CORPUS_GLOBS = [("research/digests", ".md")]

# Control characters that must never appear in a card/digest body. Tab, LF and
# CR are ordinary text structure and stay legal.
CTRL = [c for c in range(0x20) if c not in (0x09, 0x0A, 0x0D)] + [0x7F]

# SECOND CLASS (r1235 bm-a): the table below can only repair what still carries
# a control character. A line that ENDED WITH A BACKSLASH followed by a path
# token resolves `\` + `r` into a real CR and eats the token's first letter:
# `... (selftest 19/19) \` + newline + `results/x.json` becomes a legal line
# break plus `esults/x.json`. A byte scan sees nothing wrong (CR is structure),
# yet the pointer no longer resolves for any reader. Repair = put the letter
# back; the proof is the file system (restored path, else restored directory),
# never a guess from spelling. Eleven such sites sat in the registry unnoticed.
PREFIX_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_/])((?:esults|esearch)/[A-Za-z0-9_./<>{}\-]+)")

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


def prefix_proof(root, tok):
    """(restored_token, proof_sentence) for a token whose leading `r` was eaten.

    Empty proof = not reportable: the rule never fires on spelling alone. Two
    tiers are allowed, both measured on the file system:
      * the restored path exists -- the ordinary case;
      * the token is a TEMPLATE (carries <placeholder> braces) and its restored
        directory exists -- a template can never "exist", so its location is
        the only thing there is to check.
    A bare dirname test would fire on every typo'd `esults/foo.json`, because
    `results/` always exists; that is why the template tier is conditioned.
    """
    restored = "r" + tok
    if os.path.exists(os.path.join(root, restored.replace("\\", "/"))):
        return restored, "restored path exists"
    if "<" in tok or "{" in tok:
        parent = os.path.dirname(restored)
        if parent and os.path.isdir(os.path.join(root, parent)):
            return restored, "restored template directory %s/ exists" % parent
    return restored, ""


def _prefix_iter(text, root=ROOT):
    """[(start, token, restored, proof)] over one text body (proof required)."""
    out = []
    for m in PREFIX_TOKEN.finditer(text):
        tok = m.group(1)
        restored, proof = prefix_proof(root, tok)
        if proof:
            out.append((m.start(), tok, restored, proof))
    return out


def prefix_findings(root=ROOT):
    """[(path, line, token, restored, proof)] for every confirmed eaten prefix."""
    hits = []
    for rel in corpus(root):
        text = _read(os.path.join(root, rel))
        for start, tok, restored, proof in _prefix_iter(text, root):
            hits.append({"path": rel,
                         "line": text.count("\n", 0, start) + 1,
                         "token": tok, "restored": restored, "proof": proof})
    return hits


def scan(root=ROOT, verbose=False):
    hits = findings(root)
    for h in hits:
        print("[hygiene] %s:%d %s  ...%s..." % (h["path"], h["line"], h["byte"],
                                                h["context"]))
    phits = prefix_findings(root)
    for h in phits:
        print("[hygiene] %s:%d eaten prefix: %s -> %s (%s)"
              % (h["path"], h["line"], h["token"], h["restored"], h["proof"]))
    files = corpus(root)
    print("[hygiene] %d file(s) scanned, %d control character(s), "
          "%d eaten path prefix(es)" % (len(files), len(hits), len(phits)))
    if verbose:
        for f in files:
            print("[hygiene]   %s" % f)
    return 1 if (hits or phits) else 0


def _apply_prefixes(text, root=ROOT):
    """Repair eaten path prefixes inside one text body.

    Returns (new_text, rows, error). On error the caller must not write, and the
    body is returned unchanged: an ambiguous or irreversible site is refused,
    never guessed. Assertions mirror the frozen-table repair: line count is
    identical, exactly the site lines move, and removing the inserted letter at
    its own column reproduces the original line verbatim.
    """
    sites = _prefix_iter(text, root)
    if not sites:
        return text, [], None
    out = text
    for start, _tok, _restored, _proof in reversed(sites):
        out = out[:start] + "r" + out[start:]
    b_lines, a_lines = text.split("\n"), out.split("\n")
    if len(b_lines) != len(a_lines):
        return text, [], ("prefix repair changed the line count (%d -> %d)"
                          % (len(b_lines), len(a_lines)))
    moved = {i for i, (a, b) in enumerate(zip(b_lines, a_lines)) if a != b}
    expected = {text.count("\n", 0, s) for s, _t, _r, _p in sites}
    if moved != expected:
        return text, [], ("prefix repair touched lines %s, expected %s"
                          % (sorted(moved), sorted(expected)))
    rows = []
    for start, tok, restored, proof in sites:
        ln = text.count("\n", 0, start)
        col = start - (text.rfind("\n", 0, start) + 1)
        after_line = a_lines[ln]
        if (after_line[col:col + len(restored)] != restored
                or after_line[:col] + after_line[col + 1:] != b_lines[ln]):
            return text, [], ("prefix site not reversible on its own line: %r"
                              % tok[:40])
        rows.append({"line": ln + 1, "damaged": tok, "restored": restored,
                     "proof": proof})
    if _prefix_iter(out, root):
        return text, [], "eaten path prefixes survive the repair"
    return out, rows, None


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
        if n == 0 and text.count(rep["restored"]) >= 1:
            # Idempotent re-run: the site was discharged by an earlier pass.
            # The damage is absent AND its repair is present, which is the only
            # reading that is not a guess.
            continue
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
        hit = next((r for r in rows if r["damaged"] == rep["damaged"]), None)
        if hit is None:
            continue  # discharged by an earlier pass: no bytes moved this run
        line_no = hit["line"] - 1
        if after_lines[line_no].replace(rep["restored"], rep["damaged"], 1) \
                != before_lines[line_no]:
            return 3, {"error": "site not reversible on its own line: %r"
                                % rep["damaged"][:40]}
    if any(ord(ch) in CTRL for ch in text):
        return 3, {"error": "control characters survive the repair"}

    # Second class: put the eaten leading `r` back, in the registry and in every
    # other corpus file (a digest carried one too -- the class is not registry-only).
    text, prow, perr = _apply_prefixes(text, root)
    if perr:
        return 3, {"error": perr}
    rows.extend(prow)
    changed_lines = sorted({r["line"] for r in rows})

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
    others = []
    for rel in corpus(root):
        path = os.path.join(root, rel)
        if os.path.abspath(path) == os.path.abspath(target):
            continue
        body = _read(path)
        fixed, orow, oerr = _apply_prefixes(body, root)
        if oerr:
            return 3, {"error": "%s: %s" % (rel, oerr)}
        if orow:
            others.append({"path": rel, "sites": orow})
            if apply:
                _write(path, fixed)

    if apply:
        _write(target, text)
    receipt["files"] = others
    receipt["applied"] = bool(apply)
    receipt["remaining"] = len(findings(root)) + len(prefix_findings(root))
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

        # L12-L15 the second class: a backslash-eaten leading `r` on a path token
        os.makedirs(os.path.join(tmp, "results"))
        _write(os.path.join(tmp, "results", "x.json"), "{}\n")
        eaten = "intro \\\r\nesults/x.json and more\n"
        _write(reg, eaten)
        pf = prefix_findings(tmp)
        leg("L12 a backslash-eaten path prefix is found with its proof",
            len(pf) == 1 and pf[0]["token"] == "esults/x.json"
            and pf[0]["restored"] == "results/x.json",
            str(pf[:1]))

        _write(reg, eaten)
        pf_before = len(prefix_findings(tmp))
        _write(reg, "intro \\\r\nesults/nothing_here.json\n")
        leg("L13 a token with no restored path is never reported",
            pf_before == 1 and prefix_findings(tmp) == [])

        _write(reg, "intro\nresults/x.json\n")
        leg("L14 an intact path is never reported", prefix_findings(tmp) == [])

        _write(reg, body + eaten)
        _n_before = len(_read(reg).split("\n"))
        rc, rec = fix(tmp, apply=True)
        _after = _read(reg)
        leg("L15 fix repairs the eaten prefix and keeps the line count",
            rc == 0 and len(_after.split("\n")) == _n_before
            and prefix_findings(tmp) == []
            and any(r["damaged"] == "esults/x.json" for r in rec.get("sites", [])),
            "rc=%d %s" % (rc, rec.get("error", "")))

    print("[card_text_hygiene] selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "scan"
    if cmd == "scan":
        return scan(verbose="--verbose" in argv)
    if cmd == "fix":
        rc, rec = fix(apply="--dry-run" not in argv)
        print(json.dumps(rec, ensure_ascii=False, indent=1))
        # Only a run that MOVED BYTES is a receipt. A follow-up pass finds
        # nothing to repair, and writing it would replace the record of the
        # repair with the record of not needing one (r1235 lost its own record
        # this way within the same round).
        moved = bool(rec.get("sites") or rec.get("files"))
        if rc == 0 and "--dry-run" not in argv and moved:
            path = os.path.join(ROOT, RECEIPT)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            prior = []
            if os.path.exists(path):
                try:
                    with io.open(path, "r", encoding="utf-8") as f:
                        prior = json.load(f).get("history") or []
                except Exception:
                    prior = []
            rec["history"] = prior + [{"sites": rec.get("sites"),
                                       "files": rec.get("files"),
                                       "before_bytes": rec.get("before_bytes"),
                                       "after_bytes": rec.get("after_bytes")}]
            with io.open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
            print("[hygiene] receipt written to %s" % RECEIPT)
        elif rc == 0:
            print("[hygiene] nothing to repair (receipt left untouched)")
        return rc
    if cmd == "selftest":
        return selftest()
    print("usage: card_text_hygiene.py [scan|fix|selftest] [--verbose|--dry-run]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))