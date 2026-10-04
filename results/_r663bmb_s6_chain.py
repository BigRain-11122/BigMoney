"""r663 bm-b S6 chain driver: canon leg list imported from Tools/_r433bmc_s6.py
(zero re-list, per-round file form r442-r459 lineage; bm-b r663 reuse of bm-b
r659 proven pattern). Full log to results/_r663bmb_s6_log.txt.
Golden-week no-new-bar face (last bar 2026-09-30): new-bar legs no-op/veto
honestly per r448 caliber. Env: enforce flag + PYTHONUTF8=1 (r425 fix)."""
import datetime
import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r663bmb_s6_log.txt")

_spec = importlib.util.spec_from_file_location(
    "canon_s6", os.path.join(ROOT, "Tools", "_r433bmc_s6.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PY = sys.executable
LEGS = [(n, [PY] + a[1:]) for n, a in _mod.LEGS]


def main():
    print(f"PARITY PASS {len(LEGS)} legs == canon import", flush=True)
    env = dict(os.environ)
    env["BIGMONEY_REGIME_GUARD"] = "enforce"   # r450 live-proven env face
    env["PYTHONUTF8"] = "1"   # r425 leg-8 GBK console crash fix, persisted
    bad = []
    with open(LOG, "w", encoding="utf-8") as log:
        log.write(f"S6 chain r663 bm-b start {datetime.datetime.now().isoformat()}\n")
        log.flush()
        for name, args in LEGS:
            t0 = datetime.datetime.now()
            try:
                r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                                   text=True, encoding="utf-8", errors="replace",
                                   timeout=600)
                rc = r.returncode
                out = (r.stdout or "") + (r.stderr or "")
            except subprocess.TimeoutExpired:
                rc, out = 99, "TIMEOUT 600s"
            dt = (datetime.datetime.now() - t0).total_seconds()
            if rc != 0:
                bad.append((name, rc))
            tail = out.strip().splitlines()[-3:] if out.strip() else ["(no output)"]
            log.write(f"\n=== {name} rc={rc} {dt:.1f}s\n{out}\n")
            log.flush()
            print(f"{name}: rc={rc} ({dt:.0f}s) | {' | '.join(tail)[:150]}", flush=True)
        log.write(f"\nS6 chain end {datetime.datetime.now().isoformat()} "
                  f"bad={bad}\n")
    print(f"\nNON-ZERO LEGS: {bad if bad else 'none'}")


if __name__ == "__main__":
    main()
