"""r422 bm-c MASS_TRIAL_W2 generate burn: detached + self-log + poll.

Why detached (r324 law + two dead executors this window): generate --wave 2
is a single-threaded ~20-40min batch (per-family signal builds for cross-wave
dedup), zero artifacts until final write (in-memory accumulation), so inline
SR runs decapitate at 5.0min silence and a mid-flight death loses everything
(PID 34628 precedent: zero w2 artifacts). Detached child holds its own log
file handle; parent exits immediately (r317 close_fds law).

Usage:
  python Tools/_r422bmc_w2_burn.py spawn    # launch detached generate
  python Tools/_r422bmc_w2_burn.py status   # log tail + artifact check
"""
import os
import subprocess
import sys
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r422bmc_w2_gen_log.txt")
ARTIFACTS = ["w2_roster.json", "w2_candidates.json", "w2_generate_summary.json"]
OUT_DIR = os.path.join(ROOT, "results", "mass_trial")


def spawn():
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with open(LOG, "ab") as lf:
        lf.write(f"\n[spawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"generate --wave 2 detached launch\n".encode("utf-8"))
        lf.flush()
        subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
             "generate", "--wave", "2"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True)
    print(f"spawned detached w2 generate; poll log: {LOG}")


def status():
    alive = False
    try:
        import psutil  # optional; fall back to log-staleness check
        for p in psutil.process_iter(["pid", "cmdline"]):
            cl = " ".join(p.info["cmdline"] or [])
            if "mass_trial_w1.py" in cl and "generate" in cl and "--wave 2" in cl:
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
