"""r426 bm-c MASS_TRIAL_W2 judge-finalize: detached + self-log + poll.

Why detached (r324 law + r422 window two-dead-executor precedent +
r425 evidence: a 19:14:48 non-detached finalize spawn died with a 0-byte
log before any output): judge-finalize --wave 2 aggregates 805 judged
cells (G1'v2 + DSR per cell + family CSCV PBO) with zero stdout until the
final summary line -- silence is NOT liveness; psutil alive-check + log +
artifact faces are the poll truth. Ledger append is chain-linear INSIDE
the product json (science_gates.append_ledger dict -> w2_judge.json), so a
mid-flight death writes nothing; rerun is clean.

Usage:
  python Tools/_r426bmc_w2_judge_finalize.py spawn   # launch detached
  python Tools/_r426bmc_w2_judge_finalize.py status  # poll faces
"""
import os
import subprocess
import sys
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r426bmc_w2_judge_finalize_log.txt")
ARTIFACTS = ["w2_judge.json"]
OUT_DIR = os.path.join(ROOT, "results", "mass_trial")


# TREASURE-CAPTURE (O-20261003-2030 s2.2 five-collection-point weld, r434 bm-c):
# at this finalize's closeout ask "any new treasure in this batch?" -- yes ->
# append one row to knowledge/TREASURE_REGISTRY.md; new methodology ->
# METHODOLOGY_ASSETS.md card (O-2100 same-window step). Registry is
# append-only; deleting a listed face = redline P0 (TREASURE_PROTECTION_LAW s5).
def spawn():
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with open(LOG, "ab") as lf:
        lf.write(f"\n[spawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"judge-finalize --wave 2 detached launch "
                 f"(4/4 shards done 805/805 rows on origin; freeze 4796399f3)\n"
                 .encode("utf-8"))
        lf.flush()
        subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
             "judge-finalize", "--wave", "2"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True)
    print(f"spawned detached w2 judge-finalize; poll log: {LOG}")


def status():
    alive = False
    pid = None
    try:
        import psutil  # optional; fall back to log/artifact faces
        for p in psutil.process_iter(["pid", "cmdline"]):
            cl = " ".join(p.info["cmdline"] or [])
            if ("mass_trial_w1.py" in cl and "judge-finalize" in cl
                    and "--wave" in cl):
                alive = True
                pid = p.info["pid"]
                break
    except ImportError:
        pass
    print(f"process_alive(psutil)={alive} pid={pid}")
    if os.path.exists(LOG):
        with open(LOG, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", "replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        print(f"log lines={len(lines)} "
              f"last_write={time.strftime('%m-%d %H:%M:%S', time.localtime(os.path.getmtime(LOG)))}")
        print("--- tail 8 ---")
        print("\n".join(lines[-8:]))
    else:
        print("(no log yet)")
    for a in ARTIFACTS:
        p = os.path.join(OUT_DIR, a)
        if os.path.exists(p):
            print(f"artifact {a}: EXISTS {os.path.getsize(p)}B "
                  f"mtime={time.strftime('%m-%d %H:%M:%S', time.localtime(os.path.getmtime(p)))}")
        else:
            print(f"artifact {a}: absent")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    if mode == "spawn":
        spawn()
    else:
        status()
