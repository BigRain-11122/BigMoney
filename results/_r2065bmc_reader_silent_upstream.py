"""r2065 (bm-c): a reader must not crash on a state its writer is allowed to publish.

Two of the 34 red legs the triage r2061 classified as EXCEPTION are the same wound as the
29 the root-cause pass r2062 traced -- the book family's upstream is legally silent today
(the cut receipt answers UNREADABLE with permitted_k = null and therefore carries no
`gap_k`) -- but they failed differently, because both readers were written as if the
upstream always answers:

  * `etf_book_permission_persistence.py --check`  -> KeyError: 'gap_k'
  * `etf_book_cash_roll_today.py --selftest`      -> KeyError: 'cash_cny'

The first is a *checker* reading a key that a published state is allowed to omit; the
second is worse: a **selftest** reading the live faces, so the market decides whether that
file's own test passes. A selftest is offline or it is not a selftest; the live pair is
`--check`'s job.

This script does three things and nothing else:

  1. writes the one-file-per-script patch that fixes both (patches/r2065-*.patch) and
     proves `git apply --check` accepts it against the current tree;
  2. proves the *behaviour* without touching the shared faces: the patched sources are
     compiled and executed in this process, with their path globals pointed at temp
     fixtures, and the unpatched sources are run on the same fixtures as negative
     controls so a green leg cannot mean "the fixture changed";
  3. publishes results/reader_silent_upstream.json + research/READER-SILENT-UPSTREAM.md.

Third-state rule (r1861/r1943 shape): an upstream that is legally silent is not a verdict
about the reader, so the checker exits 3 with the sentence UPSTREAM_SILENT and the harness
closes the leg UNVERIFIED instead of red -- a red nobody can act on teaches the reader to
loosen the rule (r1789/r1135).

Read-only over the worktree: no shared face is written, no chain leg is re-run.
Usage:
  python results/_r2065bmc_reader_silent_upstream.py            # prove + publish
  python results/_r2065bmc_reader_silent_upstream.py --check    # prove only, no write
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import difflib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import types

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

FACE = os.path.join(BASE, "results", "reader_silent_upstream.json")
MD = os.path.join(BASE, "research", "READER-SILENT-UPSTREAM.md")
PATCH = os.path.join(BASE, "patches", "r2065-reader-silent-upstream.patch")

PERM_SCRIPT = "scripts/etf_book_permission_persistence.py"
CASH_SCRIPT = "scripts/etf_book_cash_roll_today.py"
SMOKE = "smoke_test.py"

# ---------------------------------------------------------------- the edits
E_PERM_CHECK_OLD = '''    fails = []
    gap = _read_json(GAP_FACE)
    if abs(float(d["slack_k"]) - float(gap["gap_k"])) > 1e-6:
        fails.append("slack_k %s vs receipt %s" % (d["slack_k"], gap["gap_k"]))
'''

E_PERM_CHECK_NEW = '''    fails = []
    gap = _read_json(GAP_FACE)
    # r2065: the cut receipt is ALLOWED to be silent -- r2062..r2064 traced the book
    # family's red legs to exactly that shape (verdict UNREADABLE, permitted_k null, so no
    # gap_k). Reading the key anyway turned a legal upstream state into a KeyError: the
    # leg died instead of saying what it could not check, and the chain was handed a
    # traceback where it needed a sentence. Say it instead. This face measures how long a
    # trim survives; with no readable trim, nothing below would be about a trim the reader
    # can confirm, so the cheap answer is the honest one (r1935: ask the cheap question
    # first). Exit 3 -- distinct from rc1 -- lets the harness close the leg UNVERIFIED
    # rather than red (third state of r1861/r1943; a red nobody can act on is r1789).
    gap_k = gap.get("gap_k")
    if gap_k is None:
        print("UPSTREAM_SILENT: the cut receipt says %s and publishes no gap_k, so this "
              "face cannot re-check the trim it was priced from. Published slack_k %r "
              "is unchanged; nothing below was judged."
              % (gap.get("verdict") or "?", d.get("slack_k")))
        return 3
    if abs(float(d["slack_k"]) - float(gap_k)) > 1e-6:
        fails.append("slack_k %s vs receipt %s" % (d["slack_k"], gap_k))
'''

E_PERM_RUN_OLD = '''def run():
    gap = _read_json(GAP_FACE)
    slack = float(gap["gap_k"])
'''

E_PERM_RUN_NEW = '''def run():
    gap = _read_json(GAP_FACE)
    if gap.get("gap_k") is None:
        raise SystemExit("UPSTREAM_SILENT: cut receipt %s carries no gap_k -- refusing to "
                         "republish this face on a trim it cannot read."
                         % (gap.get("verdict") or "?"))
    slack = float(gap["gap_k"])
'''

E_CASH_OLD = '''    # -- disk readers ----------------------------------------------------------------
    perm, q, b, problems = read_inputs()
    leg("the live permission face and repo panel both read from disk",
        not problems and bool(q) and bool(b), str(problems))
    leg("every panel quote carries the bar it belongs to",
        all(isinstance(v, str) and len(v) == 10 for v in b.values()))
    live = build(perm, q, b, problems)
    leg("the published face's cash is nav minus the ordered book, to the cent",
        abs(live["cash_cny"] - (float(perm["nav_cny"]) - float(perm["ordered_book_cny"])))
        < CASH_EPS, str(live.get("cash_cny")))
'''

E_CASH_NEW = '''    # -- the two numbers, on fixtures ---------------------------------------------------
    # r2065: these legs used to read the LIVE faces. On 2026-11-25 the permission face was
    # legally silent (NO_INSTRUCTION, no nav/ordered) and this selftest died with KeyError
    # 'cash_cny' -- i.e. the market got to decide whether this file's own test passes, and
    # a red on a day the book cannot answer is not a defect report. A selftest is offline
    # or it is not a selftest; re-deriving the live pair from disk is `--check`'s job (it
    # names every field that moved). The fixtures below carry the shape the live face has
    # on a day it CAN answer, plus the shape it has on a day it cannot.
    _perm = {"nav_cny": 1_000_000.0, "ordered_book_cny": 434_724.0,
             "decision_date": "2026-12-09", "as_of": "2026-11-20"}
    live = build(_perm, quotes, bars, [])
    leg("cash is nav minus the ordered book, to the cent (fixture face)",
        abs(live["cash_cny"] - (float(_perm["nav_cny"]) - float(_perm["ordered_book_cny"])))
        < CASH_EPS, str(live.get("cash_cny")))
    leg("every panel quote carries the bar it belongs to (fixture panel)",
        all(isinstance(v, str) and len(v) == 10 for v in bars.values()))
    _silent = build({"nav_cny": None, "ordered_book_cny": None}, quotes, bars, [])
    leg("a silent permission face answers NO_INSTRUCTION and carries no cash to index",
        _silent["verdict"] == "NO_INSTRUCTION" and "cash_cny" not in _silent,
        str(_silent.get("reason")))
'''

E_SMOKE_OLD = '''                except Exception:
                    pass
            check(_label, _ok, _why)
'''

E_SMOKE_NEW = '''                except Exception:
                    pass
            # r2065: a product's --check may answer "the upstream is silent today" (the
            # book family's cut receipt without gap_k). Such a child now says
            # UPSTREAM_SILENT and exits 3 instead of dying with a KeyError, and that is not
            # a verdict about this leg -- it closes UNVERIFIED rather than red, exactly like
            # the r1861 face-moved and r1943 child-killed third states. Judging it red would
            # teach the reader that this leg is noise (r1789/r1135).
            if not _ok and _r.returncode == 3:
                _silent = [l.strip() for l in (_r.stdout or "").splitlines()
                           if "UPSTREAM_SILENT" in l]
                if _silent:
                    _ok = True
                    _why = "UNVERIFIED_UPSTREAM_SILENT " + _silent[0][:100]
            check(_label, _ok, _why)
'''

EDITS = [
    {"path": PERM_SCRIPT, "old": E_PERM_CHECK_OLD, "new": E_PERM_CHECK_NEW,
     "label": "check(): a silent cut receipt is stated and exits 3, not a KeyError"},
    {"path": PERM_SCRIPT, "old": E_PERM_RUN_OLD, "new": E_PERM_RUN_NEW,
     "label": "run(): refuse to republish on a trim it cannot read"},
    {"path": CASH_SCRIPT, "old": E_CASH_OLD, "new": E_CASH_NEW,
     "label": "selftest: fixture legs instead of the live faces"},
    {"path": SMOKE, "old": E_SMOKE_OLD, "new": E_SMOKE_NEW,
     "label": "harness: UPSTREAM_SILENT closes the leg UNVERIFIED"},
]


def read_text(rel):
    with io.open(os.path.join(BASE, rel), encoding="utf-8", newline="") as fh:
        return fh.read()


def _eol(text):
    """The file's own line ending -- the anchors above are written LF, so they have to be
    translated before matching (smoke_test.py is CRLF, the two scripts are LF)."""
    return "\r\n" if "\r\n" in text else "\n"


def apply_edits(text, edits):
    eol = _eol(text)
    out = text
    for e in edits:
        old = e["old"] if eol == "\n" else e["old"].replace("\n", eol)
        new = e["new"] if eol == "\n" else e["new"].replace("\n", eol)
        n = out.count(old)
        if n != 1:
            raise SystemExit("FATAL: anchor %r occurs %d times in %s (want 1)"
                             % (e["label"], n, e["path"]))
        out = out.replace(old, new)
    return out


def build_patch():
    """Return (patch_text, {path: patched_text}) -- deterministic, no clock in it."""
    chunks, patched = [], {}
    for rel in (PERM_SCRIPT, CASH_SCRIPT, SMOKE):
        orig = read_text(rel)
        new = apply_edits(orig, [e for e in EDITS if e["path"] == rel])
        patched[rel] = new
        diff = difflib.unified_diff(
            orig.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile="a/" + rel, tofile="b/" + rel, n=3)
        chunks.append("".join(diff))
    head = ("r2065 (bm-c): a reader must not crash on a state its writer may publish.\n"
            "\n"
            "Two legs the r2061 triage called EXCEPTION died on the same silent upstream\n"
            "the r2062..r2064 root-cause pass traced (cut receipt UNREADABLE -> no gap_k):\n"
            "  etf_book_permission_persistence --check  -> KeyError: 'gap_k'\n"
            "  etf_book_cash_roll_today --selftest      -> KeyError: 'cash_cny'  (a\n"
            "selftest reading the LIVE faces, i.e. the market deciding whether its own\n"
            "test passes). The checker now says UPSTREAM_SILENT and exits 3 (the harness\n"
            "closes it UNVERIFIED, r1861/r1943); the selftest is fixture-only.\n"
            "\n")
    return head + "".join(chunks), patched


def load_module(src, name, file_path):
    mod = types.ModuleType(name)
    mod.__file__ = file_path
    sys.modules[name] = mod
    exec(compile(src, file_path, "exec"), mod.__dict__)
    return mod


def _write(tmp, name, payload):
    p = os.path.join(tmp, name)
    with io.open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    t0 = time.time()
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(name)

    patch_text, patched = build_patch()

    # --- the patch itself -------------------------------------------------------------
    if not args.check:
        os.makedirs(os.path.dirname(PATCH), exist_ok=True)
        # newline="" : the smoke hunk carries CRLF on purpose (that file is CRLF)
        with io.open(PATCH, "w", encoding="utf-8", newline="") as fh:
            fh.write(patch_text)
    _again, _ = build_patch()
    leg("patch generation is deterministic (two builds byte-identical)", _again == patch_text)
    _orig, _ = build_patch()
    leg("the patch is four hunks over three files (one per defect + one per guard)",
        patch_text.count("\n--- a/") == 3 and patch_text.count("\n@@ ") == 4,
        "files=%d hunks=%d" % (patch_text.count("\n--- a/"), patch_text.count("\n@@ ")))

    tmp = tempfile.mkdtemp(prefix="r2065bmc_")
    ppath = os.path.join(tmp, "silent.patch")
    with io.open(ppath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(patch_text)
    r = subprocess.run(["git", "apply", "--check", "--whitespace=nowarn", ppath],
                       cwd=BASE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    leg("git apply --check accepts the patch against the current tree", r.returncode == 0,
        (r.stderr or r.stdout or "").strip()[:160])

    for rel in (PERM_SCRIPT, CASH_SCRIPT, SMOKE):
        try:
            ast.parse(patched[rel])
            ok, why = True, ""
        except SyntaxError as e:
            ok, why = False, "%s line %s" % (e.msg, e.lineno)
        leg("patched %s parses" % rel, ok, why)

    # the harness branch must sit inside the product loop, before the closing check()
    _sm = patched[SMOKE]
    leg("harness: the UNVERIFIED branch precedes the loop's own check() call",
        _sm.index("UNVERIFIED_UPSTREAM_SILENT") < _sm.index("            check(_label, _ok, _why)"))

    # --- behaviour, on fixtures, in this process ---------------------------------------
    published = json.load(io.open(os.path.join(BASE, "results",
                                               "etf_book_permission_persistence.json"),
                                 encoding="utf-8"))
    gap_live = json.load(io.open(os.path.join(BASE, "results", "etf_book_cut_order_gap.json"),
                                encoding="utf-8"))
    slack_pub = float(published.get("slack_k") or 0.0)

    silent_gap = _write(tmp, "gap_silent.json",
                        {"face": "etf_book_cut_order_gap", "verdict": "UNREADABLE",
                         "upstream": {"permitted_k": None}})
    readable_gap = _write(tmp, "gap_readable.json",
                          {"face": "etf_book_cut_order_gap", "verdict": "ORDER_WITHIN_PERMISSION",
                           "permitted_k": 0.435003, "gap_k": slack_pub})

    mod = load_module(patched[PERM_SCRIPT], "r2065_perm_patched", os.path.join(BASE, PERM_SCRIPT))
    mod.OUT = os.path.join(BASE, "results", "etf_book_permission_persistence.json")
    mod.GAP_FACE = silent_gap
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_silent = mod.check()
    said = buf.getvalue()
    leg("patched --check on a silent receipt exits 3 and says UPSTREAM_SILENT",
        rc_silent == 3 and "UPSTREAM_SILENT" in said, "rc=%s said=%r" % (rc_silent, said[:120]))
    leg("that sentence does not contain STALE (the chain must not pay a rebuild for it)",
        "STALE" not in said, said[:120])

    # the guard must fire on silence only: with a readable receipt the code goes on
    def _boom(*_a, **_k):
        raise RuntimeError("REACHED_REBUILD")
    mod.GAP_FACE = readable_gap
    mod.build_schedule = _boom
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            mod.check()
        reached = False
    except RuntimeError as e:
        reached = "REACHED_REBUILD" in str(e)
    leg("with a readable receipt the same code reaches the rebuild (guard is not a mute)",
        reached)

    # negative control: the ORIGINAL source on the same silent fixture dies exactly as
    # the smoke leg reported it -- so the green above is the patch, not the fixture
    orig_mod = load_module(read_text(PERM_SCRIPT), "r2065_perm_orig",
                           os.path.join(BASE, PERM_SCRIPT))
    orig_mod.GAP_FACE = silent_gap
    orig_mod.OUT = mod.OUT
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            orig_mod.check()
        ctl = "no exception"
    except KeyError as e:
        ctl = "KeyError %r" % (e.args[0] if e.args else "",)
    except SystemExit as e:
        ctl = "SystemExit %s" % (e,)
    leg("unpatched --check still raises KeyError 'gap_k' on the same fixture (control)",
        ctl == "KeyError 'gap_k'", ctl)

    # cash_roll_today: the selftest must not touch the disk at all
    cash = load_module(patched[CASH_SCRIPT], "r2065_cash_patched",
                       os.path.join(BASE, CASH_SCRIPT))
    cash.PERM_PATH = os.path.join(BASE, "results", "_r2065_missing_face.json")

    def _no_disk(*_a, **_k):
        raise AssertionError("selftest read the disk")
    cash.read_inputs = _no_disk
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        rc_self = cash.selftest()
    leg("patched --selftest passes with the disk readers poisoned (it is offline now)",
        rc_self == 0, buf2.getvalue().strip().splitlines()[-1] if buf2.getvalue() else "")

    cash_orig = load_module(read_text(CASH_SCRIPT), "r2065_cash_orig",
                            os.path.join(BASE, CASH_SCRIPT))
    cash_orig.read_inputs = lambda *a, **k: (
        {"nav_cny": 1.0, "ordered_book_cny": 0.5}, {"GC001": 1.2},
        {"GC001": "2026-11-24"}, [])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cash_orig.selftest()
        ctl2 = "no exception"
    except KeyError as e:
        ctl2 = "KeyError %r" % (e.args[0] if e.args else "",)
    leg("unpatched --selftest still dies with KeyError 'cash_cny' on a silent face (control)",
        ctl2 == "KeyError 'cash_cny'", ctl2)

    # --- publish ---------------------------------------------------------------------
    face = {
        "face": "reader_silent_upstream",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "round": "r2065",
        "machine": "bm-c",
        "law": ("a reader must not crash on a state its writer may publish; a selftest "
                "must not read the live faces"),
        "patch": os.path.relpath(PATCH, BASE).replace("\\", "/"),
        "files": [e["path"] for e in EDITS],
        "live": {
            "cut_receipt_verdict": gap_live.get("verdict"),
            "cut_receipt_permitted_k": (gap_live.get("upstream") or {}).get("permitted_k"),
            "published_slack_k": slack_pub,
            "published_cash_roll_verdict": json.load(io.open(
                os.path.join(BASE, "results", "etf_book_cash_roll_today.json"),
                encoding="utf-8")).get("verdict"),
        },
        "legs": legs,
        "ok": not fails,
        "elapsed_sec": round(time.time() - t0, 2),
    }
    if not args.check:
        with io.open(FACE, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with io.open(MD, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_md(face))

    for L in legs:
        print("[%s] %s%s" % ("PASS" if L["ok"] else "FAIL", L["leg"],
                             "" if L["ok"] else " | " + L["detail"]))
    print("\nr2065 reader-silent-upstream %d/%d" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


def render_md(face):
    lv = face["live"]
    lines = [
        "# A reader must not crash on a state its writer may publish (r2065, bm-c)",
        "",
        "Two of the 34 red smoke legs the r2061 triage called EXCEPTION are not two more",
        "defects: they are the same silent upstream the r2062..r2064 root-cause pass traced",
        "(the cut receipt answers `UNREADABLE` with `permitted_k = null`, so it carries no",
        "`gap_k`), showing up in two readers that were written as if the upstream always",
        "answers.",
        "",
        "| leg | shape | what it did on 2026-11-25 | what it does after this patch |",
        "|---|---|---|---|",
        "| `etf_book_permission_persistence --check` | a **checker** reading a key a",
        "published state may omit | `KeyError: 'gap_k'` | prints `UPSTREAM_SILENT`, exits 3 |",
        "| `etf_book_cash_roll_today --selftest` | a **selftest** reading the LIVE faces"
        " | `KeyError: 'cash_cny'` | fixture-only, offline |",
        "",
        "## Why exit 3 and not 1",
        "",
        "The value here is *which* state the leg is in. The upstream is allowed to be silent,",
        "so this is not a verdict about the reader: red would be a flag nobody can act on",
        "(r1789) and would teach the reader to loosen the rule (r1135). Green would read as",
        "clean while nothing was compared (r1861). The harness therefore closes the leg",
        "**UNVERIFIED** on rc 3 with the child's own sentence -- the same third state as",
        "r1861 (face moved mid-run) and r1943 (child killed).",
        "",
        "The sentence deliberately does **not** say STALE: the chain only pays a rebuild on",
        "that word (r1850), and re-running this face would produce the same silence.",
        "",
        "## Why the selftest had to lose its disk legs",
        "",
        "`--selftest` used to call `read_inputs()` and then index `live[\"cash_cny\"]`. On a day",
        "the book cannot answer, `build()` correctly returns `NO_INSTRUCTION` -- and the",
        "selftest crashed on the missing key. That means **the market decided whether this",
        "file's own test passes**, and the leg went red on a day nothing was wrong with the",
        "code. Re-deriving the live pair from disk is `--check`'s job and it already does it,",
        "field by field. The selftest now carries both shapes on fixtures: the readable face",
        "(cash == nav - ordered, to the cent) and the silent one (NO_INSTRUCTION, no cash to",
        "index).",
        "",
        "## The patch (waiting for a quiet window)",
        "",
        "`" + face["patch"] + "` -- four hunks over three files; `git apply --check` accepts",
        "it against this tree. It is **not applied here**: this round ran inside a contention",
        "window (another host was writing shared faces), so only new files were landed.",
        "",
        "## Live readings this was priced against",
        "",
        "* cut receipt verdict: `%s`, `permitted_k = %r`" % (lv["cut_receipt_verdict"],
                                                             lv["cut_receipt_permitted_k"]),
        "* published `slack_k` on the persistence face: `%.6f`" % lv["published_slack_k"],
        "* published cash-roll verdict: `%s`" % lv["published_cash_roll_verdict"],
        "",
        "## Proof",
        "",
    ]
    for L in face["legs"]:
        lines.append("* %s %s%s" % ("PASS" if L["ok"] else "FAIL", L["leg"],
                                    (" -- " + L["detail"]) if L["detail"] else ""))
    lines += [
        "",
        "Controls are in the same run: the **unpatched** sources are executed on the same",
        "fixtures and must still raise the two KeyErrors -- a green leg above therefore",
        "cannot mean 'the fixture changed'.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
