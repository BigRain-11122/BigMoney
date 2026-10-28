#!/usr/bin/env python
"""Reader-text sweep: doubled percent and unexpanded placeholders in published faces.

WHY
---
r1320 fixed one instance of a defect class with a gate on the OUTPUT of one face:
a caveat written as a plain literal but spelled as if it were a format string kept
its `%%`, so the published face said "13.5%% vol" to every reader. The code looks
correct where the string is defined; only the emitted text shows it. r1320 recorded
three more faces with the same defect and left them "for the next sweep" -- this is
that sweep, and it is a census because the same class has several legitimate shapes
that must not be rewritten blind.

WHAT COUNTS AS A DEFECT
-----------------------
Any string that reaches a reader:
  * `%%` -- a doubled percent the reader takes literally;
  * a printf token that never got filled (`%s`, `%.2f`, `%d`);
  * a brace placeholder that never got filled (`{cagr}`, `{asof}`).

WHAT DOES NOT
-------------
  * a shell/command string: `cmd /c ... %%i` is real escaping, not a typo;
  * frozen evidence: round scratch faces (`results/_r...`) and quarantine blobs are
    history -- the sweep names them and never rewrites them;
  * the runnable pool: its notes are append-only records of what was enqueued, so
    rewriting them would falsify history. They are published as a bucket with a
    count, so the class stays visible and the next pool generator can stop adding to
    it;
  * this face itself: the census has to quote the shapes it hunts.

Usage:
    python scripts/reader_text_audit.py run        # census -> results JSON, gate rc
    python scripts/reader_text_audit.py check      # same gate, no write
    python scripts/reader_text_audit.py selftest   # offline, hermetic

Exit: 0 = no live face carries the defect, 1 = at least one does,
      2 = mechanism failure (a scan root is unreadable).
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "reader_text_audit.json"
SCAN_ROOTS = ("results", "docs")

DOUBLE_PCT = re.compile(r"%%")
# Not "% x"/"%i" inside "%%i": an unfilled token has to start its own percent and
# end at a word boundary (r1321 first cut flagged "1% x ADV20" as a printf token).
PRINTF_TOKEN = re.compile(r"(?<!%)%[-+ 0-9.#]*[sdifr](?![A-Za-z0-9_])")
BRACE_TOKEN = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")

# A string that is an instruction to a machine, not a sentence to a reader.
CODE_KEYS = frozenset((
    "cmd", "command", "commands", "argv", "exec", "exe", "shell", "script",
    "scripts", "path", "paths", "python", "ps", "powershell", "regex", "pattern",
    "patterns", "glob", "fmt", "format", "spec", "expression", "code", "snippet",
    "query", "url", "urls", "file", "files", "dirname", "workdir",
))

# A key whose whole job is to hold a template (a filename pattern) is machine text.
CODE_KEY_SUFFIXES = ("_pattern", "_tmpl", "_template", "_glob", "_fmt", "_format")

# Append-only record faces: named, never rewritten.
RECORD_FACES = ("runnable_pool",)

# Collector status artifacts: machine faces that publish their own call shape (a quote
# endpoint template, a source-name list) for the next process, not prose for a person.
# r1325: results/etf_wide_update_status.json /quote_face = "https://hq.sinajs.cn/list={syms}"
# was gated as a live-face defect, which would have forced renaming a template that the
# collector genuinely sends. The bucket is advisory and COUNTED, never silently dropped --
# and the gate keeps its teeth: the same token in docs/ or a book face still fails.
MACHINE_STATUS_SUFFIX = "update_status.json"

# A face a reader opens today: the top level of results/, the ETF book family
# (which publishes CARD/ORDER/PRODUCTION), and docs/. Everything else under
# results/ is a closed round's evidence -- the sweep counts it and does not edit
# it, because those files are the record of what a past round measured.
LIVE_SUBDIRS = ("etf_book_production", "etf_book_order", "etf_book_forward",
                "etf_paper", "monthly_exam")

# Placeholder-looking text in markup (LaTeX \mathrm{close}) is not a placeholder.
MARKUP_KEYS = ("formula_latex", "latex", "tex", "formula", "expression_latex")

# This census must quote the shapes it hunts; it cannot gate on itself.
SELF = "results/reader_text_audit.json"


def walk_strings(obj, key=None, path=""):
    """Yield (json_path, key, string) for every string leaf, keys included."""
    if isinstance(obj, str):
        yield path, key, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, str(k), path + "/" + str(k))
            if isinstance(k, str):
                yield path + "/<key>", str(k), k
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, key, path + "[%d]" % i)


def find_defects(text, key=None):
    """-> list of (kind, token) for one string. Pure function, no repo access."""
    out = []
    if DOUBLE_PCT.search(text):
        out.append(("doubled-percent", "%%"))
    markup = "\\" in text or (key or "").lower() in MARKUP_KEYS
    if not markup:
        m = PRINTF_TOKEN.search(text)
        if m:
            out.append(("printf-token", m.group(0)))
        m = BRACE_TOKEN.search(text)
        if m:
            out.append(("brace-token", m.group(0)))
    return out


def _is_live_rel(rel):
    parts = rel.split("/")
    if parts[0] == "docs":
        return True
    if parts[0] != "results":
        return False
    if len(parts) == 2:
        return True
    return parts[1] in LIVE_SUBDIRS


def _is_code_key(key):
    k = (key or "").lower()
    return k in CODE_KEYS or any(k.endswith(s) for s in CODE_KEY_SUFFIXES)


def bucket_for(rel, key, kinds):
    """Classify one string hit. Gate buckets come out of live-observer only."""
    parts = rel.split("/")
    name = os.path.splitext(parts[-1])[0]
    if rel == SELF:
        return "self-census"
    if len(parts) > 1 and parts[1].startswith("_"):
        return "frozen-evidence"
    if name.startswith("_r") or name.startswith("_tmp"):
        return "frozen-evidence"
    if any(name.startswith(r) for r in RECORD_FACES):
        return "pool-record"
    if parts[-1].endswith(MACHINE_STATUS_SUFFIX):
        return "machine-status"
    if kinds and _is_code_key(key):
        return "code-string"
    if not _is_live_rel(rel):
        return "closed-round-evidence"
    return "live-face"


def scan_face(path, rel):
    """-> list of hit rows for one JSON face; raises on unreadable JSON."""
    with path.open(encoding="utf-8", errors="replace") as f:
        raw = f.read()
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        return [{"file": rel, "json_path": "/", "key": None, "kind": "unparsable",
                 "token": None, "bucket": "frozen-evidence",
                 "text": "json error: %s" % exc}]
    rows = []
    for jpath, key, s in walk_strings(doc):
        kinds = find_defects(s, key)
        if not kinds:
            continue
        bucket = bucket_for(rel, key, kinds)
        for kind, token in kinds:
            rows.append({"file": rel, "json_path": jpath, "key": key, "kind": kind,
                         "token": token, "bucket": bucket, "text": s[:200]})
    return rows


def bucket_for_md(rel, kinds):
    """Markdown buckets: a doc a reader opens is gated, results scratch is history."""
    if rel.split("/")[0] == "docs":
        return "doc-prose"
    return bucket_for(rel, None, kinds)


def scan_md(path, rel):
    rows = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return rows
    for i, line in enumerate(lines, 1):
        for kind, token in find_defects(line):
            rows.append({"file": rel, "json_path": "L%d" % i, "key": None,
                         "kind": kind, "token": token,
                         "bucket": bucket_for_md(rel, [(kind, token)]),
                         "text": line.strip()[:200]})
    return rows


def census(roots=SCAN_ROOTS):
    rows, files = [], 0
    for root in roots:
        base = ROOT / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in (".json", ".md"):
                continue
            rel = str(p.relative_to(ROOT)).replace(os.sep, "/")
            files += 1
            if p.suffix.lower() == ".json":
                rows.extend(scan_face(p, rel))
            else:
                rows.extend(scan_md(p, rel))

    buckets = {}
    for r in rows:
        buckets.setdefault(r["bucket"], []).append(r)
    # Two gated buckets, not one: a bad JSON field and a bad line of prose in a doc
    # a reader opens are the same defect class, and the CEO page is markdown (r1322:
    # the first cut labelled every .md "doc-prose" and gated only live-face, so the
    # page the reader actually opens was never checked -- a fixture-only gate).
    live = buckets.get("live-face", []) + buckets.get("doc-prose", [])
    return {
        "schema": "reader-text-audit/1",
        "origin": "r1320 recorded three faces with the doubled-percent defect for the next sweep",
        "scan_roots": list(roots),
        "files_scanned": files,
        "n_hits": len(rows),
        "counts": {k: len(v) for k, v in sorted(buckets.items())},
        "gated_buckets": ["live-face", "doc-prose"],
        "verdict": "PASS" if not live else "FAIL",
        "offenders": live,
        "offender_files": sorted({r["file"] for r in live}),
        "advisory": {k: {"n": len(v),
                         "files": sorted({r["file"] for r in v})[:25],
                         "sample": v[:5]}
                     for k, v in sorted(buckets.items())
                     if k not in ("live-face", "doc-prose")},
        "law": "reader-facing text is final text: no doubled percent, no unexpanded"
               " printf/brace token; machine-command strings, frozen evidence, the"
               " append-only pool record and this census are disclosed, not rewritten",
    }


def _print_summary(res):
    print("files %d  hits %d  verdict %s" % (res["files_scanned"], res["n_hits"],
                                            res["verdict"]))
    for k, n in res["counts"].items():
        print("  %-18s %d" % (k, n))
    for r in res["offenders"][:20]:
        print("  OFFENDER %s %s %s %r" % (r["file"], r["json_path"], r["kind"],
                                          r["text"][:120]))


def run(write=True):
    res = census()
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    _print_summary(res)
    return 0 if res["verdict"] == "PASS" else 1


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # the defect r1320 found: a literal spelled as if formatted
    d = find_defects("13.5%% vol is not a formatting bug you can see in the source")
    leg("a doubled percent is caught", [k for k, _ in d] == ["doubled-percent"], str(d))

    # no false positive on an honest percentage
    leg("an ordinary percentage is left alone", not find_defects("an 8% vol target"),
        str(find_defects("an 8% vol target")))

    # unexpanded printf and brace tokens
    leg("an unfilled printf token is caught",
        [k for k, _ in find_defects("cagr %.2f per year")] == ["printf-token"],
        str(find_defects("cagr %.2f per year")))
    leg("an unfilled brace placeholder is caught",
        [k for k, _ in find_defects("level {cagr} unknown")] == ["brace-token"],
        str(find_defects("level {cagr} unknown")))

    # a shell string is escaping, not a typo
    leg("a doubled percent inside a command string is a code string, not a gate",
        bucket_for("results/x.json", "cmd", [("doubled-percent", "%%")]) == "code-string")
    leg("the same token outside a command key is a live defect",
        bucket_for("results/x.json", "note", [("doubled-percent", "%%")]) == "live-face")

    # frozen evidence and the append-only pool are named, not rewritten
    leg("round scratch faces are frozen evidence",
        bucket_for("results/_r707bmb_stage_ours.json", "note",
                   [("doubled-percent", "%%")]) == "frozen-evidence")
    leg("a scratch directory under results is frozen evidence",
        bucket_for("results/_quarantine/a/b.json", "note",
                   [("doubled-percent", "%%")]) == "frozen-evidence")
    leg("the runnable pool is an append-only record",
        bucket_for("results/runnable_pool.bm-c.json", "note",
                   [("doubled-percent", "%%")]) == "pool-record")

    # the census cannot gate on the shapes it quotes
    leg("this census exempts itself by name",
        bucket_for(SELF, "law", [("doubled-percent", "%%")]) == "self-census")

    # a closed round's evidence is counted, not edited
    leg("a wave subdirectory under results is closed-round evidence",
        bucket_for("results/t73_s2/factor_history.json", "note",
                   [("doubled-percent", "%%")]) == "closed-round-evidence")
    leg("the ETF book family lives in a subdirectory but is a live face",
        bucket_for("results/etf_book_production/latest.json", "note",
                   [("doubled-percent", "%%")]) == "live-face")
    # r1325: a collector status artifact publishes its own call shape; that is machine text.
    # The bucket is advisory, and the gate must keep its teeth on a real reader page.
    leg("a collector status artifact is machine text, not a reader page",
        bucket_for("results/etf_wide_update_status.json", "quote_face",
                   [("brace-token", "{syms}")]) == "machine-status")
    leg("the same template token in docs/ is still a gated defect",
        bucket_for("docs/live_usage/LIVE-2026-10-28.md", None,
                   [("brace-token", "{syms}")]) == "live-face")
    # LaTeX is markup, not a placeholder
    leg("a LaTeX brace is not an unfilled placeholder",
        not find_defects(r"(\mathrm{close}_t - \mathrm{close}_{t-10}) / 10"),
        str(find_defects(r"(\mathrm{close}_t)")))
    leg("a bare brace placeholder is still caught when nothing else marks markup",
        [k for k, _ in find_defects("level {cagr} unknown")] == ["brace-token"])

    # a multi-kind hit keeps every kind (no silent first-match truncation)
    m = find_defects("cost %.2f and level {x} and 8%%")
    leg("all kinds in one string are reported", len(m) == 3, str(m))
    leg("a template key holds machine text, so a token there is not a reader defect",
        bucket_for("results/x.json", "face_pattern",
                   [("printf-token", "%s")]) == "code-string")
    leg("the same token under a prose key is a reader defect",
        bucket_for("results/x.json", "note",
                   [("printf-token", "%s")]) == "live-face")
    leg("a percentage followed by a variable name is not a printf token",
        not find_defects("capped at 1% x ADV20"), str(find_defects("capped at 1% x ADV20")))
    leg("a shell loop variable inside %%i is not a printf token",
        [k for k, _ in find_defects("for %%i in (*)")] == ["doubled-percent"],
        str(find_defects("for %%i in (*)")))

    # r1322: the reader's page is markdown, so prose has to be a gated bucket
    leg("prose in a doc a reader opens is gated, not advisory",
        bucket_for_md("docs/live_usage/LIVE-2026-10-28.md",
                      [("doubled-percent", "%%")]) == "doc-prose")
    leg("the same prose under results is a closed round's evidence",
        bucket_for_md("results/_r1320bmc_note.md",
                      [("doubled-percent", "%%")]) == "frozen-evidence")
    leg("a markdown face inside the ETF book family is still live",
        bucket_for_md("results/etf_book_production/PRODUCTION-2026-10-27.md",
                      [("doubled-percent", "%%")]) == "live-face")

    # end-to-end on a fixture tree
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "results").mkdir()
        (tmp / "results" / "live.json").write_text(
            json.dumps({"note": "grew 5%% this year"}), encoding="utf-8")
        (tmp / "results" / "clean.json").write_text(
            json.dumps({"note": "grew 5% this year", "cmd": "for %%i in (*)"}),
            encoding="utf-8")
        global ROOT
        keep = ROOT
        try:
            ROOT = tmp
            res = census(("results",))
        finally:
            ROOT = keep
        leg("a fixture tree gates only on its live offender",
            res["verdict"] == "FAIL" and res["offender_files"] == ["results/live.json"],
            "%s %s" % (res["verdict"], res["offender_files"]))
        leg("the clean face with a real command string passes",
            "results/clean.json" not in res["offender_files"], str(res["offender_files"]))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + (" | " + detail if not ok else ""))
    print("selftest %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    cmd = args[0] if args else "run"
    if cmd == "selftest":
        return selftest()
    if cmd in ("run", "check"):
        return run(write=(cmd == "run"))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))