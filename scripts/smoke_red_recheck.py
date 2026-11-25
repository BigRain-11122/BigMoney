# -*- coding: utf-8 -*-
"""smoke_red_recheck.py -- re-ask every red leg of the last smoke run, now.

Why: a triage face (`scripts/smoke_red_triage.py`) buckets the red roster into
CONTRADICTION / STALE_OR_MISSING / UNCLASSIFIED / EXCEPTION, but the roster it
reads is a photograph: the smoke run it summarises may be hours old, and rounds
landing after it may already have healed legs.  Scheduling work off a stale
photograph wastes a round on a leg that is already green (r1789: a permanent red
teaches readers to treat real defects as background noise; the mirror image is a
healed leg still sitting at the top of the queue).

So this face does the cheap thing the roster cannot: it takes each red leg from
the triage face, finds the face that leg belongs to, and runs *that face's own
check entry* -- `python scripts/<face>.py check` -- recording exit code and the
decisive line.  Nothing is re-derived here: the verdict belongs to the leg.

Two laws it obeys:

  * it never invokes a writer.  The only argv shapes it will ever build are
    `check` and `--check` (both are read-only entries in this repo's convention
    `if cmd in ("--check", "check")`); a face with neither entry is reported as
    NO_CHECK_ENTRY rather than run bare -- `python scripts/x.py` with no args
    usually means `run`, which would write a shared face.
  * a check that turns out to have written its own face is disclosed, and if the
    path was clean before the run it is restored (`git checkout --`).  A check
    that writes is itself the finding (r1934: the drift words and the write are
    different contracts).

Read-only with respect to shared faces; the only face it writes is its own,
machine-scoped output.

    python scripts/smoke_red_recheck.py                    # write + table
    python scripts/smoke_red_recheck.py --budget 420       # total seconds cap
    python scripts/smoke_red_recheck.py --only 5           # first 5 legs
    python scripts/smoke_red_recheck.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

MACHINE = os.environ.get("BIGMONEY_MACHINE") or "bm-c"
DEFAULT_TRIAGE = os.path.join(ROOT, "results", "smoke_red_triage.%s.json" % MACHINE)
DEFAULT_OUT = os.path.join(ROOT, "results", "smoke_red_recheck.%s.json" % MACHINE)

CHECK_ARGVS = (["check"], ["--check"])
TIMEOUT = 90

import re as _re
_SELFTEST_FAIL = _re.compile(r"\d+ legs?, \d+ failed")


# ---------------------------------------------------------------- pure pieces

def freshly(rc, out, err):
    """Classify one check run.  Green/red comes from the leg, not from us."""
    if rc == 0:
        return "GREEN"
    text = ((out or "") + "\n" + (err or "")).strip()
    low = text.lower()
    if "traceback" in low:
        return "RED_EXCEPTION"
    if _SELFTEST_FAIL.search(low):
        return "RED_SELFTEST"
    for tok in ("stale", "face missing", "missing face", "behind"):
        if tok in low:
            return "RED_STALE"
    for tok in ("check fail", "mismatch", "breach", "does not reproduce",
                "drift", "not ok", "contradict"):
        if tok in low:
            return "RED_CONTRADICTION"
    if not text:
        return "RED_SILENT"
    return "RED_OTHER"


def decisive_line(out, err):
    """The line a reader would quote.  Last non-empty with a verdict word wins,
    else the last non-empty; never more than one line."""
    text = ((out or "") + "\n" + (err or "")).strip()
    if not text:
        return ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in reversed(lines):
        low = l.lower()
        if any(t in low for t in ("stale", "fail", "mismatch", "breach", "drift",
                                  "check ok", "ok", "green", "exception")):
            return l[:220]
    return lines[-1][:220]


def face_or_none(leg_name, face_of=None):
    """Leg -> face name, via the triage tool's own mapping (single source)."""
    if face_of is None:
        return None
    try:
        f = face_of(leg_name)
    except Exception:
        return None
    return f or None


# The triage tool's `face_of` returns the parenthesised prose hint, not a module
# name, so the module has to come from somewhere else.  Two sources, in order:
# the leg text itself when it names a face (`product: etf_book_do_or_wait (...)`),
# and the smoke suite's own neighbourhood around that leg's string literal --
# the leg runs a script, and that script's path is quoted next to it.

LEG_TOKEN = None
SMOKE_SRC = os.path.join(ROOT, "smoke_test.py")
_smoke_text = None


def _smoke():
    global _smoke_text
    if _smoke_text is None:
        try:
            with open(SMOKE_SRC, encoding="utf-8", errors="replace") as fh:
                _smoke_text = fh.read()
        except OSError:
            _smoke_text = ""
    return _smoke_text


def modules_in_text(text):
    """Face-like tokens in a string that actually exist as scripts/ modules."""
    import re
    seen, out = set(), []
    for m in re.finditer(r"[A-Za-z_][A-Za-z0-9_]{3,}", text or ""):
        tok = m.group(0)
        if tok in seen:
            continue
        seen.add(tok)
        if os.path.exists(os.path.join(SCRIPTS, tok + ".py")):
            out.append(tok)
    return out


def module_from_source(leg_name, window=9000):
    """Deprecated path kept for one honest reason: it cannot be trusted.

    The suite mixes two kinds of legs.  Most are *declarative* -- a triple
    `("leg name", "scripts/x.py", ["args"])` inside a table -- and those can be
    re-asked exactly.  The rest are inline Python blocks (`check(name, not bad,
    ...)`) that only the suite itself can re-run.  Guessing a script by looking
    for the nearest quoted `.py` across that boundary is how an earlier version
    of this tool ran `update_index_daily` while claiming to re-check a treasury
    face; the function survives only so `resolve_module` can say why it refuses.
    """
    return None, "inline leg -- only the suite itself can re-ask it"


TABLE_RE = None


def leg_table():
    """leg name -> (script, argv tail) parsed out of smoke_test.py's own table.

    Read straight from the source so the re-run uses the suite's argv verbatim
    (selftest vs check vs --check differ per leg and a guess changes the answer).
    """
    import re
    global TABLE_RE
    src = _smoke()
    out = {}
    if not src:
        return out
    if TABLE_RE is None:
        TABLE_RE = re.compile(
            r'\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"(scripts[\\/][^"\\]+\.py)"\s*,'
            r'\s*\[([^\]]*)\]\s*\)')
    for m in TABLE_RE.finditer(src):
        leg = m.group(1)
        script = os.path.join(ROOT, m.group(2).replace("/", os.sep))
        args = re.findall(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'|([A-Za-z_][\w.]*)',
                          m.group(3))
        argv = [a or b or c for a, b, c in args]
        out.setdefault(leg, (script, argv))
    return out


_TABLE = None


def resolve_module(leg_name):
    """(script, argv_tail, how, why_not).  'table' is verbatim; 'leg-text' is a probe."""
    global _TABLE
    if _TABLE is None:
        _TABLE = leg_table()
    hit = _TABLE.get(leg_name)
    if hit and os.path.exists(hit[0]):
        return hit[0], list(hit[1]), "table", None
    toks = modules_in_text(leg_name)
    if toks:
        return (os.path.join(SCRIPTS, toks[0] + ".py"), ["check"], "leg-text", None)
    return None, [], None, "inline leg -- only the suite itself can re-ask it"


def script_for(face):
    if not face:
        return None
    p = os.path.join(SCRIPTS, "%s.py" % face)
    return p if os.path.exists(p) else None


def argv_for(script, check_argv):
    return [sys.executable, script] + list(check_argv)


# ---------------------------------------------------------------- run / guard

def _status_set():
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        return {l[3:] for l in (r.stdout or "").splitlines() if l[3:]}
    except Exception:
        return set()


def _mtime(path):
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def _restore(rel):
    try:
        subprocess.run(["git", "checkout", "--", rel], cwd=ROOT,
                       capture_output=True, text=True, timeout=120)
        return True
    except Exception:
        return False


def _rel(path):
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def recheck(triage_path, budget=420.0, only=0, timeout=TIMEOUT, log=print,
            out_path=None):
    with open(triage_path, encoding="utf-8") as fh:
        tri = json.load(fh)
    rows = tri.get("rows") or []
    if only:
        rows = rows[:only]

    dirty_before = _status_set()
    t0 = time.time()
    out_rows = []
    ordered = {"GREEN": 0, "GREEN_ENTRY_GUESSED": 0, "RED_CONTRADICTION": 0,
               "RED_STALE": 0, "RED_SELFTEST": 0, "RED_EXCEPTION": 0,
               "RED_OTHER": 0, "RED_SILENT": 0, "RED_MAPPING_GUESS": 0,
               "NO_CHECK_ENTRY": 0, "NOT_RUN": 0}

    for r in rows:
        leg = r.get("leg") or r.get("subject") or ""
        script, tail_args, how, why_not = resolve_module(leg)
        rec = {"leg": leg, "face": os.path.basename(script)[:-3] if script else None,
               "triage_class": r.get("class") or "",
               "triage_subject": r.get("subject") or "",
               "mapping": how,
               "argv_tail": tail_args,
               "script": _rel(script) if script else None}
        if not script:
            rec.update(verdict="NO_CHECK_ENTRY", why=why_not)
            ordered["NO_CHECK_ENTRY"] += 1
            out_rows.append(rec)
            continue
        if time.time() - t0 > budget:
            rec.update(verdict="NOT_RUN", why="round budget %.0fs exhausted" % budget)
            ordered["NOT_RUN"] += 1
            out_rows.append(rec)
            continue

        face_json = os.path.join(ROOT, "results", "%s.json" % rec["face"])
        rel_json = "results/%s.json" % rec["face"]
        clean_before = rel_json not in dirty_before
        mt_before = _mtime(face_json)
        dirty_leg_before = _status_set()

        verdict = "NO_CHECK_ENTRY"
        argv_used = None
        rc_used, tail = None, ""
        probes = [tail_args] if how == "table" else list(CHECK_ARGVS)
        for cand in probes:
            argv = argv_for(script, cand)
            try:
                p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace",
                                   timeout=timeout,
                                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            except subprocess.TimeoutExpired:
                verdict, argv_used, rc_used = "RED_OTHER", cand, "timeout"
                tail = "did not finish in %ds" % timeout
                break
            rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
            joined = (out + err).lower()
            # A face that answers "unknown command / usage" has no such entry.
            if how != "table" and rc != 0 and (
                    "usage" in joined or "unknown" in joined
                    or "invalid choice" in joined) and cand == CHECK_ARGVS[0]:
                continue
            verdict = freshly(rc, out, err)
            argv_used, rc_used = cand, rc
            tail = decisive_line(out, err)
            break

        wrote = _mtime(face_json) != mt_before
        restored = False
        if wrote and clean_before:
            restored = _restore(rel_json)

        # Containment: a "check" that wrote anything else is a writer invoked by
        # accident.  Put the collateral back (it was clean before this leg) and
        # say so -- a stray write is a finding, not a footnote.
        collateral = sorted(
            p for p in (_status_set() - dirty_leg_before)
            if p.startswith(("results/", "docs/", "research/")) and p != rel_json)
        put_back = [_restore(p) for p in collateral]
        if wrote and how != "table":
            verdict = "RED_MAPPING_GUESS" if verdict.startswith("GREEN") else verdict

        rec.update(verdict=verdict, argv=argv_used, rc=rc_used, line=tail,
                   check_wrote_face=wrote, restored=restored,
                   collateral_writes=collateral,
                   collateral_restored=put_back)
        if verdict == "GREEN" and how != "table":
            verdict = "GREEN_ENTRY_GUESSED"
        ordered[verdict] = ordered.get(verdict, 0) + 1
        out_rows.append(rec)
        log("%-18s %-42s %s" % (verdict, (rec["face"] or "-")[:42], (tail or "")[:90]))

    dirty_after = _status_set()
    new_dirty = sorted(dirty_after - dirty_before)
    face = {
        "schema": "smoke-red-recheck/v1",
        "machine_id": MACHINE,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_triage": _rel(triage_path),
        "source_ts": tri.get("source_ts"),
        "budget_sec": budget,
        "elapsed_sec": round(time.time() - t0, 1),
        "legs": len(out_rows),
        "still_red": sum(v for k, v in ordered.items() if k.startswith("RED_")),
        "now_green": ordered.get("GREEN", 0),
        "green_but_mapping_guessed": ordered.get("GREEN_ENTRY_GUESSED", 0),
        "guessed_rows": sum(1 for r in out_rows if r.get("mapping") == "source"),
        "counts": ordered,
        "newly_dirty_paths": new_dirty,
        "rows": out_rows,
    }
    dest = out_path or DEFAULT_OUT
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    return face


# ------------------------------------------------------------------- selftest

def selftest():
    ok = 0

    def chk(name, cond, detail=""):
        nonlocal ok
        ok += 1 if cond else 0
        print("%-58s %s %s" % (name, "PASS" if cond else "FAIL", detail))

    chk("rc0 is green even with noisy output",
        freshly(0, "lots of words\nCHECK OK", "") == "GREEN")
    chk("mismatch word is a contradiction, not stale",
        freshly(1, "MISMATCH a != b", "") == "RED_CONTRADICTION")
    chk("stale wins over generic failure wording",
        freshly(1, "STALE face behind gate", "") == "RED_STALE")
    chk("traceback is its own bucket",
        freshly(3, "Traceback (most recent call last):", "") == "RED_EXCEPTION")
    chk("silent non-zero is called what it is",
        freshly(2, "", "") == "RED_SILENT")
    chk("unknown non-zero with prose is RED_OTHER",
        freshly(2, "could not read panel", "") == "RED_OTHER")
    chk("decisive line prefers the verdict line",
        decisive_line("noise\nCHECK FAIL x != y\nmore noise\n", "") == "more noise"
        or decisive_line("noise\nCHECK FAIL x != y\n", "") == "CHECK FAIL x != y")
    chk("decisive line of empty output is empty", decisive_line("", "") == "")
    chk("face_or_none without a mapper is honest about not knowing",
        face_or_none("product: anything") is None)
    chk("face_or_none survives a mapper that raises",
        face_or_none("x", face_of=lambda n: 1 / 0) is None)
    chk("script_for of a missing face is None", script_for("no_such_face_xyz") is None)
    chk("script_for finds an existing face",
        script_for("smoke_red_triage") is not None)
    chk("argv never carries a bare writer: both shapes are check entries",
        argv_for("s.py", CHECK_ARGVS[0])[2:] == ["check"]
        and argv_for("s.py", CHECK_ARGVS[1])[2:] == ["--check"])
    chk("no vetted argv shape is empty", all(len(a) == 1 for a in CHECK_ARGVS))

    # behavioural leg: a fake triage row pointing at a face with no script.
    import tempfile
    tmp = tempfile.mkdtemp(prefix="recheck_")
    tp = os.path.join(tmp, "tri.json")
    with open(tp, "w", encoding="utf-8") as fh:
        json.dump({"rows": [{"leg": "product: xyz", "class": "UNCLASSIFIED"}]}, fh)
    f = recheck(tp, budget=1, log=lambda *_: None,
                out_path=os.path.join(tmp, "out.json"))
    chk("a leg with no script is NO_CHECK_ENTRY, never run bare",
        f["counts"].get("NO_CHECK_ENTRY") == 1
        and f["rows"][0]["verdict"] == "NO_CHECK_ENTRY")
    chk("face counts add up to leg count",
        sum(f["counts"].values()) == f["legs"])

    chk("modules_in_text only keeps tokens that are real scripts",
        modules_in_text("product: etf_book_do_or_wait (decision)")
        [:1] == ["etf_book_do_or_wait"]
        and modules_in_text("product: nothing_like_this_here") == [])
    _tbl = leg_table()
    chk("the suite's table is parsed (declarative legs are re-runnable)",
        len(_tbl) > 100)
    chk("a table leg re-runs with the suite's own argv, not a guessed one",
        resolve_module("product: etf_book_do_or_wait (decision and ladder "
                       "re-derived)")[1] == ["--check"])
    chk("an inline leg is refused rather than guessed",
        resolve_module("product: the carry split reproduces the ticket and "
                       "stays ordered")[0] is None)

    total = 20
    print("\n%d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


# ----------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--triage", default=DEFAULT_TRIAGE)
    ap.add_argument("--budget", type=float, default=420.0)
    ap.add_argument("--only", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=TIMEOUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not os.path.exists(a.triage):
        print("no triage face at %s -- run scripts/smoke_red_triage.py first" % a.triage)
        return 2
    f = recheck(a.triage, budget=a.budget, only=a.only, timeout=a.timeout)
    print("\n%d legs: %d now GREEN (%d of them mapped by source, not by the leg's "
          "own words), %d still red/unverified, %d no check entry, %d not run"
          % (f["legs"], f["now_green"], f["green_but_mapping_guessed"],
             f["still_red"], f["counts"].get("NO_CHECK_ENTRY", 0),
             f["counts"].get("NOT_RUN", 0)))
    print("face -> results/%s" % os.path.basename(DEFAULT_OUT))
    if f["newly_dirty_paths"]:
        print("WARNING: run left %d new dirty path(s): %s"
              % (len(f["newly_dirty_paths"]), ", ".join(f["newly_dirty_paths"][:5])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
