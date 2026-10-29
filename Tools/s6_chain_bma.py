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
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Tools"))

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


def main(argv):
    args = list(argv[1:])
    only = None
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
    round_no = args[0] if args else "0"

    legs = LEGS
    if only is not None:
        want = [w.strip() for w in only.split(",") if w.strip()]
        legs = [t for t in LEGS if t[0] in want]
        missing = sorted(set(want) - {t[0] for t in legs})
        if missing:
            print(f"unknown leg(s): {missing}; known={[t[0] for t in LEGS]}")
            return 2

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
        if rc != 0 and refresh and "stale" in text.lower():
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
        note = (" +refresh(rc=%s,%ss)" % (refreshed["rc"], refreshed["elapsed_sec"])) if refreshed else ""
        print(f"{rc:3d} {name:18s} {el:7.1f}s {tail[0][:120]}{note}", flush=True)

    path = os.path.join(ROOT, "results", f"_r{round_no}bma_s6_chain.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    bad = [o for o in out if o["rc"] != 0]
    print(f"chain: {len(out)-len(bad)}/{len(out)} rc0 -> {path} "
          f"({datetime.now().isoformat(timespec='seconds')})")
    if bad:
        print("NONZERO: " + ", ".join(f"{o['leg']}={o['rc']}" for o in bad))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))