"""r484 bm-c MASS_TRIAL_W3 judge-prep: detached + self-log + poll.

Why detached (r324 law + r422/r423 precedent): judge-prep --wave 3 runs
785 survivor leg-L base-face backtests SERIALLY (~13min band per w2's 806
backtest measurement) + passive start points -> past the 5.0min SR
silence-decapitation line; a mid-flight death loses the whole in-memory
pass (zero partial artifacts). Detached child holds its own log file
handle; parent exits immediately (r317 close_fds law). Same protocol as
Tools/_r423bmc_w2_judge_prep.py.

Usage:
  python Tools/_r484bmc_w3_judge_prep.py spawn    # launch detached prep
  python Tools/_r484bmc_w3_judge_prep.py status   # log tail + artifact check
"""
import os
import subprocess
import sys
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r484bmc_w3_judge_prep_log.txt")
ARTIFACTS = ["w3_judge_state.json"]
OUT_DIR = os.path.join(ROOT, "results", "mass_trial")


def spawn():
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with open(LOG, "ab") as lf:
        lf.write(f"\n[spawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"judge-prep --wave 3 detached launch (freeze 2b41a3958)\n"
                 .encode("utf-8"))
        lf.flush()
        subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
             "judge-prep", "--wave", "3"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True)
    print(f"spawned detached w3 judge-prep; poll log: {LOG}")


def status():
    alive = False
    try:
        import psutil  # optional; fall back to log-staleness check
        for p in psutil.process_iter(["pid", "cmdline"]):
            cl = " ".join(p.info["cmdline"] or [])
            if ("mass_trial_w1.py" in cl and "judge-prep" in cl
                    and "--wave 3" in cl):
                alive = True
                break
    except ImportError:
        pass
    print(f"process_alive(psutil)={alive}")
    if os.path.exists(LOG):
        with open(LOG, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", "replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        print(f"log lines={len(lines)} last_write={time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(LOG)))}")
        print("--- tail 6 ---")
        print("\n".join(lines[-6:]))
    else:
        print("(no log yet)")
    for a in ARTIFACTS:
        p = os.path.join(OUT_DIR, a)
        print(f"artifact {a}: {'EXISTS ' + str(os.path.getsize(p)) + 'B' if os.path.exists(p) else 'absent'}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    if mode == "spawn":
        spawn()
    else:
        status()
