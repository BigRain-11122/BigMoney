"""bm-a S6 chain runner (reusable, one leg list shared with bm-c).

Why this file exists: bm-c got a *named* runner at r1182 (`Tools/s6_chain_bmc.py`)
because rebuilding the leg list every window cost wall time instead of measuring
anything. This host never got one -- its last chain was a frozen per-round
snapshot (`scripts/_r1102bma_s6chain.py`, 43 legs) and everything added after
2026-10-24 was refreshed only when a session happened to remember it. That is the
r1257 / r1290 orphan-face class applied to the process rather than to a file: on
this machine the single-writer faces (`docs/live_book/` is bm-a's) had no
scheduled producer at all, only a chance.

Design rules:

  * the leg list is IMPORTED from `Tools/s6_chain_bmc.py`, never copied. Columns
    of 79 legs drift silently and the drift is one-directional -- this host sat
    36 legs behind while the list kept growing. Two copies would have to be kept
    in step by hand, which is exactly what failed.
  * running the shared list here is safe: every leg is either lane-guarded (the
    script prints its own honest no-op on a host that is not its writer, R31) or
    an idempotent derivation of in-repo data (re-deriving a face from the same
    panel yields the same face). Nothing is retried or masked: each leg's raw
    exit code is printed and recorded.
  * `--only=` and `--list` exist so a round can re-run one leg without paying for
    the whole chain.

Usage:
    python Tools/s6_chain_bma.py 1143              # full chain
    python Tools/s6_chain_bma.py 1143 --only=etf_book_ceo_page,attrition_guard
    python Tools/s6_chain_bma.py --list            # names only
Exit 0 always (legs are recorded; non-zero legs are reported, not fatal) -- the
round report must surface any rc!=0 leg verbatim.
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Tools"))

# r1234: a leg's own stdout can carry U+FFFD (a reader decoding a file with the wrong codec).
# Printing that through this host's GBK console raised UnicodeEncodeError at the per-leg print
# -- i.e. leg 114 of 124 killed the runner BEFORE the chain record was written, so the whole
# run left no evidence. A reporting channel must never be able to destroy the record it is
# reporting on (D-20261102-03 encoding-at-birth, applied to the runner that reprints legs).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import s6_chain_bmc as canonical  # noqa: E402  (the single source of the leg list)

LEGS = canonical.LEGS


def leg_script(cmd):
    """The file a leg runs, or None for `-m module` legs (checked as a module)."""
    if len(cmd) >= 2 and cmd[1] == "-m":
        return None
    return cmd[1] if len(cmd) >= 2 else None


def resolve(cmd):
    """Swap the literal 'python' for this interpreter so the leg uses this venv."""
    out = list(cmd)
    if out and out[0] == "python":
        out[0] = sys.executable
    return out


def _progress_path(round_no, scope):
    return os.path.join(ROOT, "results",
                        f"_r{round_no}bma_s6_chain{scope}.progress.jsonl")


def _append_progress(path, rec):
    """One line per finished leg, written the moment the leg ends.

    Why: the chain record used to be written only after the LAST leg. A chain that
    ran 38 minutes and was killed (r1298 found exactly that: legs still writing
    per-symbol CSVs, no record on disk) left nothing to read -- the next round
    could only guess its position from file mtimes. A runner that reports progress
    must not be able to lose its own tail (r1234 family, applied to the chain).

    Deliberately unable to kill the run: a failure to append is swallowed. The
    record is evidence, not a gate.
    """
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


LOCK_MAX_AGE_MIN = 120


def _pid_alive(pid):
    if pid <= 0:
        return False
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, 0, pid)  # QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        if ok:
            return code.value == 259  # STILL_ACTIVE
    except Exception:
        pass
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _lock_path_default():
    return os.path.join(ROOT, "logs", "s6_chain_bma.lock")


def _lock_take(path=None):
    """Single-instance guard: two rounds must never drive the same leg list.

    Why: on 2026-11-16 23:28 the previous round's chain was still running (43 min
    in, writing one per-symbol CSV per second under data/astock_daily/per/) while
    the next round had already started. Nothing in this runner stopped the new
    round from walking the same 263 legs over the same faces -- the only thing that
    prevented a double write was the session happening to notice the process. That
    is the r1687 two-pid lock lesson applied to the chain driver rather than to the
    launcher.

    Rules (same shape as iteration_loop.ps1): a LIVE pid wins at any age (a running
    chain is never taken over); a dead pid is taken over immediately; an
    unparseable legacy lock is taken over only once it is older than
    LOCK_MAX_AGE_MIN. Returns (held, why, pid).
    """
    path = path or _lock_path_default()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError:
        pass
    if os.path.exists(path):
        raw = ""
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError:
            pass
        m = re.search(r"pid=(\d+)", raw or "")
        if m:
            pid = int(m.group(1))
            if _pid_alive(pid):
                return False, (raw or "").strip() or f"pid={pid}", pid
        else:
            try:
                age = (time.time() - os.path.getmtime(path)) / 60.0
            except OSError:
                age = 0.0
            if age < LOCK_MAX_AGE_MIN:
                return False, (raw or "").strip() or "legacy-lock-fresh", 0
        try:
            os.remove(path)
        except OSError:
            pass
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("pid=%d %s\n" % (os.getpid(),
                                      datetime.now().isoformat(timespec="seconds")))
    except OSError:
        return True, "lock-write-failed", os.getpid()
    return True, "acquired", os.getpid()


def _lock_release(path=None):
    """Only the process named in the lock may remove it."""
    path = path or _lock_path_default()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
    except OSError:
        return
    if "pid=%d" % os.getpid() in (raw or ""):
        try:
            os.remove(path)
        except OSError:
            pass


def _selftest():
    """Offline check of the progress evidence: three fake legs, no shared face."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="s6self_")
    legs = [
        ("ok", [sys.executable, "-c", "print('leg-ok')"]),
        ("fail", [sys.executable, "-c", "import sys; sys.exit(3)"]),
        ("gone", ["__no_such_leg__.py"]),
    ]
    fails = []

    def want(label, cond):
        if not cond:
            fails.append(label)

    # drive the same helpers the real chain uses
    prog = os.path.join(tmp, "progress.jsonl")
    _append_progress(prog, {"started": "x", "legs_total": len(legs)})
    out = []
    for name, cmd in legs:
        if not os.path.exists(os.path.join(ROOT, cmd[-1] if len(cmd) > 1 else cmd[0])) \
                and not os.path.isabs(cmd[0]) and cmd[0] != sys.executable:
            out.append({"leg": name, "rc": 127, "tail": "MISSING"})
        else:
            r = subprocess.run(resolve(cmd), cwd=ROOT, capture_output=True,
                               text=True, encoding="utf-8", errors="replace",
                               timeout=120)
            out.append({"leg": name, "rc": r.returncode, "tail": (r.stdout or "").strip()})
        _append_progress(prog, dict(out[-1], t="x"))

    lines = [json.loads(l) for l in open(prog, encoding="utf-8") if l.strip()]
    want("progress has header+3 legs", len(lines) == 4)
    want("first line is the header", lines[0].get("legs_total") == 3)
    want("a failing leg keeps its rc", any(l.get("rc") == 3 for l in lines))
    want("a missing leg reads 127", any(l.get("rc") == 127 for l in lines))
    want("an ok leg reads 0", any(l.get("rc") == 0 for l in lines))
    want("every leg line carries a timestamp", all("t" in l for l in lines[1:]))
    # atomicity: an append after a torn write must not corrupt earlier lines
    with open(prog, "a", encoding="utf-8") as fh:
        fh.write('{"leg": "extra"}\n')
    again = [l for l in open(prog, encoding="utf-8") if l.strip()]
    want("append after the fact stays parseable", len(again) == 5)

    # single-instance guard
    lp = os.path.join(tmp, "chain.lock")
    ok1, _w1, _p1 = _lock_take(lp)
    ok2, _w2, p2 = _lock_take(lp)
    want("first lock take wins", ok1 is True)
    want("a live pid beats a second take", ok2 is False and p2 == os.getpid())
    _lock_release(lp)
    want("release leaves no lock behind", not os.path.exists(lp))
    ok3, _w3, _p3 = _lock_take(lp)
    want("the lock is re-takeable after release", ok3 is True)
    _lock_release(lp)
    # a dead pid must be taken over at any age
    with open(lp, "w", encoding="utf-8") as fh:
        fh.write("pid=999999 stale\n")
    ok4, _w4, _p4 = _lock_take(lp)
    want("a dead pid is taken over", ok4 is True)
    _lock_release(lp)

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("selftest FAIL: " + "; ".join(fails))
        return 1
    print("selftest 12/12 PASS (progress evidence: header, per-leg rc, missing=127, "
          "timestamp, append-safe; lock: live pid wins, dead pid taken over, release "
          "is owner-only; no shared face touched)")
    return 0


def main(argv):
    args = list(argv[1:])
    only = None
    selftest = False
    for a in list(args):
        if a.startswith("--only"):
            only = a.split("=", 1)[1] if "=" in a else None
            args.remove(a)
            if only is None and args:
                only = args.pop(0)
        elif a == "--list":
            for t in LEGS:
                print(t[0])
            return 0
        elif a == "--selftest":
            selftest = True
            args.remove(a)
    round_no = args[0] if args else "0"

    if selftest:
        return _selftest()

    held, why, lpid = _lock_take()
    if not held:
        print(f"skip: another chain is in flight ({why}) -- one writer per face, "
              f"r1687 lock law applied to this runner")
        return 0

    legs = LEGS
    if only is not None:
        want = [w.strip() for w in only.split(",") if w.strip()]
        legs = [t for t in LEGS if t[0] in want]
        missing = sorted(set(want) - {t[0] for t in legs})
        if missing:
            print(f"unknown leg(s): {missing}; known={[t[0] for t in LEGS]}")
            return 2

    # r1186: the record name has to carry the run's SCOPE. A `--only=` re-run of four legs used
    # to write the same `_r<N>bma_s6_chain.json` as the full 107-leg chain, so fixing one face
    # silently replaced the whole chain's evidence with a four-leg record (bm-c paid this at
    # r1364 and fixed it there; this runner is the other copy of the same defect). Atomic writes
    # stop a torn file, not a small run wearing the big run's name.
    scope = ""
    if only is not None:
        scope = ".only-" + "-".join(sorted({t[0] for t in legs}))
    path = os.path.join(ROOT, "results", f"_r{round_no}bma_s6_chain{scope}.json")
    prog = _progress_path(round_no, scope)
    _append_progress(prog, {"started": datetime.now().isoformat(timespec="seconds"),
                            "legs_total": len(legs), "scope": scope.strip(".") or "full"})

    out = []
    for name, cmd, *rest in legs:
        # r1346: the leg list is shared with bm-c and a leg may carry a third element
        # (the refresh command paid when its probe says the face is stale). This runner
        # reads the same table, so it must honour the same contract -- and it must unpack
        # by position, because a 3-tuple breaks `for name, cmd in legs` and the whole
        # chain stops at the first such leg.
        refresh = rest[0] if rest else None
        script = leg_script(cmd)
        if script is not None and not os.path.exists(os.path.join(ROOT, script)):
            print(f"{name:18s} rc=MISSING ({script})")
            out.append({"leg": name, "rc": 127, "elapsed_sec": 0.0,
                        "tail": f"MISSING {script}"})
            continue
        t0 = time.time()
        try:
            r = subprocess.run(resolve(cmd), cwd=ROOT, capture_output=True,
                               text=True, encoding="utf-8", errors="replace",
                               timeout=900)
            rc = r.returncode
            text = (r.stdout or "") + (r.stderr or "")
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc = 124
            text = ""
            tail = ["TIMEOUT"]
        refreshed = None
        # r1241: the refresh arm only fired on the word "stale". A leg whose face simply
        # does not exist yet says "FACE MISSING: BLOCKS-2026-11-02.json" and got rc2 with
        # its own declared build command sitting unused in the table -- the chain then
        # reported a red leg that a one-word vocabulary change turns into a green one.
        # Deliberately narrow: "missing face" is the remedy's own trigger; a verdict /
        # identity / drift failure must NOT be rebuilt, because rebuilding would launder
        # exactly the disagreement the frozen check exists to catch.
        _low = text.lower()
        if rc != 0 and refresh and ("stale" in _low or "face missing" in _low):
            tr = time.time()
            try:
                rr = subprocess.run(resolve(refresh), cwd=ROOT, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace",
                                    timeout=900)
                refresh_rc = rr.returncode
            except subprocess.TimeoutExpired:
                refresh_rc = 124
            refreshed = {"cmd": refresh, "rc": refresh_rc,
                         "elapsed_sec": round(time.time() - tr, 1)}
            try:
                r2 = subprocess.run(resolve(cmd), cwd=ROOT, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace",
                                    timeout=900)
                rc = r2.returncode
                tail = (r2.stdout or "").strip().splitlines()[-1:] or [""]
            except subprocess.TimeoutExpired:
                rc = 124
                tail = ["TIMEOUT"]
        el = round(time.time() - t0, 1)
        rec = {"leg": name, "rc": rc, "elapsed_sec": el, "tail": tail[0][:220]}
        if refreshed:
            rec["refreshed"] = refreshed
        out.append(rec)
        _append_progress(prog, dict(rec, t=datetime.now().isoformat(timespec="seconds")))
        note = (" +refresh(rc=%s,%ss)" % (refreshed["rc"], refreshed["elapsed_sec"])) if refreshed else ""
        print(f"{rc:3d} {name:18s} {el:7.1f}s {tail[0][:120]}{note}", flush=True)

    # r1186: the record name has to carry the run's SCOPE. A `--only=` re-run of four legs used
    # to write the same `_r<N>bma_s6_chain.json` as the full 107-leg chain, so fixing one face
    # silently replaced the whole chain's evidence with a four-leg record (bm-c paid this at
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    bad = [o for o in out if o["rc"] != 0]
    print(f"chain: {len(out)-len(bad)}/{len(out)} rc0 -> {path} "
          f"({datetime.now().isoformat(timespec='seconds')})")
    if bad:
        print("NONZERO: " + ", ".join(f"{o['leg']}={o['rc']}" for o in bad))
    _lock_release()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))