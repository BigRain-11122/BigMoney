"""r611 bm-b off-caliber re-burn chain driver (detached, BelowNormal).

Sequential single-runner-at-a-time chain per the MSG-0909 sec.2 division:
bm-b takes VALUE-PE-X2 + VALUE-PB-X1 + VALUE-SENS re-burns on the
correct-caliber copy.  Each leg runs the runner with --redo (AA-replace at
same keys, provenance annotated).  Launched detached by session r611
because the autofill no-double-run gate (runner-path needle) would hold
these faces until the in-flight VALUE-NULLS burn (ETA 10-06) finishes --
the daemon cannot launch them; this chain is the designed workaround with
identical BelowNormal priority discipline.

Children inherit the driver's priority class (Windows default), so one
psutil.Popen with BELOW_NORMAL_PRIORITY_CLASS governs the whole chain.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
RUNNER = os.path.join(ROOT, "scripts", "fund_value_p1.py")

CMDS = [
    ["run", "--cell", "VALUE-PE", "--face", "x2", "--redo"],
    ["run", "--cell", "VALUE-PB", "--face", "x1", "--redo"],
    ["run", "--sensitivity", "--redo"],
]


def main() -> int:
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
    log_path = os.path.join(ROOT, "logs", "r611_reburn_chain.log")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] chain start "
                  f"pid={os.getpid()}\n")
        for args in CMDS:
            log.write(f"[{time.strftime('%H:%M:%S')}] START "
                      f"fund_value_p1.py {' '.join(args)}\n")
            log.flush()
            r = subprocess.run([PY, RUNNER] + args, cwd=ROOT,
                               stdout=log, stderr=subprocess.STDOUT)
            log.write(f"[{time.strftime('%H:%M:%S')}] rc={r.returncode} "
                      f"({' '.join(args)})\n")
            log.flush()
            if r.returncode != 0:
                log.write("[chain] leg failed -- stopping chain "
                          "(fail-fast, fuse-visible)\n")
                return r.returncode
        log.write(f"[{time.strftime('%H:%M:%S')}] CHAIN DONE 3/3\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
