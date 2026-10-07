"""r801 bm-b: FUND-QUALITY-P1 nulls heal ignition (12-key re-burn).

Root cause (r800 forensics): the 4-day Q burn (single process, ignited
2026-10-03 07:26:44, DONE 2000/2000 at 2026-10-07 07:16:30, pid 57116)
appended all 2000 rows, but rebase/checkout replays of live-append
nulls.jsonl (dead r800 session line-union cycles only union COMMITTED
rows) silently clobbered 12 live rows -> file terminal at 1988/2000.
Missing keys (machine-derived, sorted):
[178, 179, 226, 236, 297, 1476, 1588, 1589, 1590, 1674, 1715, 1992]

Heal = runner's own checkpoint done-key skip (todo=12) re-burn; seeds
frozen per key (prereg rng([20510000,k])) -> deterministic re-derivation
of the SAME rows the lost appends carried; line-level completion of an
append-only ledger (treasure_guard rc3 class -- line-union path legal,
origin-blob restore forbidden, not used). Guard passed 08:4x rc3
recorded; crash_fuse bm-b face clean (bm-a OFF-CALIBER keep-block is
bm-a-local, bm-b = correct-caliber rightful burner per r615/r617).

Detached ignition per r705/r737 canon: DETACHED_PROCESS zero-window
(U060), BelowNormal priority (CEO margin law), both-redirect to log.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "scripts", "fund_quality_p1.py")
LOG = os.path.join(ROOT, "results", "_r801bmb_q_heal_ignite.log")
NULLS = os.path.join(ROOT, "results", "fund_quality_p1", "nulls.jsonl")
PRE_STATE = os.path.join(ROOT, "results", "_r801bmb_q_heal_pre.json")


def snapshot():
    keys = set()
    n = 0
    for ln in open(NULLS, encoding="utf-8-sig"):
        if ln.strip():
            keys.add(json.loads(ln)["k"])
            n += 1
    return n, sorted(set(range(2000)) - keys)


def main():
    n, missing = snapshot()
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": n,
           "missing_keys": missing, "missing_count": len(missing)}
    with open(PRE_STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1)
    print(f"pre-state: rows={n} missing={len(missing)} -> {PRE_STATE}")
    if not missing:
        print("nothing to heal -- no ignition")
        return 0
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    env = dict(os.environ)
    with open(LOG, "ab") as lf:
        lf.write(f"\n[r801 heal-ignite {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"fund_quality_p1 run --nulls detached heal burn "
                 f"todo={len(missing)} (checkpoint done-key skip; 12-key "
                 f"line-union completion, rebase-clobber loss forensics "
                 f"in module docstring)\n".encode("utf-8"))
        lf.flush()
        p = subprocess.Popen(
            [sys.executable, "-u", RUNNER, "run", "--nulls"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True, env=env)
    try:
        import psutil
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        pri = "BelowNormal"
    except Exception as ex:
        pri = f"nice-skip ({ex})"
    print(f"spawned detached heal burn pid={p.pid} priority={pri} log={LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
