"""r486 bm-c MASS_TRIAL_W3 judge-finalize: detached + self-log + poll.

r426 W2 lineage law (r324 + r422 two-dead-executor precedent + r425
evidence: a non-detached finalize spawn died with a 0-byte log before any
output): judge-finalize aggregates judged cells (G1'v2 + DSR per cell +
family CSCV PBO) with zero stdout until the final summary line -- silence
is NOT liveness; psutil alive-check + log + artifact faces are the poll
truth. Ledger append is chain-linear INSIDE the product json, so a
mid-flight death writes nothing; rerun is clean.

Usage:
  python results/_r486bmc_w3_judge_finalize.py spawn   # launch detached
  python results/_r486bmc_w3_judge_finalize.py status   # poll faces
"""
import os
import subprocess
import sys
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r486bmc_w3_judge_finalize_log.txt")
ARTIFACTS = ["w3_judge.json"]
OUT_DIR = os.path.join(ROOT, "results", "mass_trial")


def spawn():
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with open(LOG, "ab") as lf:
        lf.write(f"\n[spawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"judge-finalize --wave 3 detached launch "
                 f"(4/4 shards done 777/777 rows, 195/194/194/194; "
                 f"freeze 2b41a3958; prefinalize probe PASS)\n"
                 .encode("utf-8"))
        lf.flush()
        subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
             "judge-finalize", "--wave", "3"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True)
    print(f"spawned detached w3 judge-finalize; poll log: {LOG}")


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
