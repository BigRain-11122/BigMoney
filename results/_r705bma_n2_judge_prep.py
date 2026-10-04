"""r705 bm-a: PERPETUAL-N2-W15-JUDGE-PREP session claim + detached spawn.

Chain position: N2-W15 judge step 1 (MSG-2026-10-05-0100-bmb-ALL division:
"任一健康机可接" -- bm-a RAM 55.6GB >> 4GB gate, bm-b honest-refused at
2.9GB while the trio NULLS occupy its RAM until ~10-06T17).

Protocol:
  claim   = Tools/autofill.py _claim_shard canon (r199 launch-claim law:
            the LAUNCHER claims the shard before firing; origin pre-read
            three-state r694-i, lane-authority write + settle, self-commit
            r290, rebase-retry r282 -- zero reimplementation, anti-rebuild
            law).
  spawn   = detached + self-log (r324 law: python 长活分离必 -u 无缓冲;
            r317 close_fds; r423/r484 judge-prep precedent) + BelowNormal
            priority (CEO CPU margin law; serial single-core prep) +
            BLAS thread caps.

Usage:
  python results/_r705bma_n2_judge_prep.py claim   # claim + spawn
  python results/_r705bma_n2_judge_prep.py status  # poll log + artifact
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Tools"))

LOG = os.path.join(ROOT, "results", "_r705bma_n2_judge_prep_log.txt")
STATE = os.path.join(ROOT, "results", "n2_w15", "n2_w15_judge_state.json")
ENTRY = "PERPETUAL-N2-W15-JUDGE-PREP"
SHARD_KEY = "n2w15judge-prep-0of1"
RUNNER = os.path.join(ROOT, "scripts", "perpetual_faces_n2.py")


def claim():
    import autofill  # canon claim protocol (import-safe: path constants only)

    ok = autofill._claim_shard({"key": SHARD_KEY}, "bm-a", ENTRY)
    print(f"claim canon _claim_shard -> {ok}")
    if not ok:
        print("claim lost/deferred (rival fresh, origin gate, or git fault) "
              "-- yield, no spawn")
        return 1
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    env = dict(os.environ)
    # CEO CPU margin law: BLAS thread cap ~26/32 (serial prep, belt+braces)
    env.setdefault("OMP_NUM_THREADS", "26")
    env.setdefault("MKL_NUM_THREADS", "26")
    with open(LOG, "ab") as lf:
        lf.write(f"\n[r705 spawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] "
                 f"n2-w15 judge-prep detached launch (freeze cd192b23f "
                 f"berth 545_500; session launch-claim r199 canon)\n"
                 .encode("utf-8"))
        lf.flush()
        p = subprocess.Popen(
            [sys.executable, "-u", RUNNER, "judge-prep"],
            cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
            creationflags=flags, close_fds=True, env=env)
    try:
        import psutil
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        pri = "BelowNormal"
    except Exception as ex:
        pri = f"nice-skip ({ex})"
    print(f"spawned detached judge-prep pid={p.pid} priority={pri} "
          f"log={LOG}")
    return 0


def status():
    alive = False
    try:
        import psutil
        for q in psutil.process_iter(["pid", "cmdline"]):
            cl = " ".join(q.info["cmdline"] or [])
            if "perpetual_faces_n2.py" in cl and "judge-prep" in cl:
                alive = True
                break
    except ImportError:
        pass
    print(f"process_alive(psutil)={alive}")
    if os.path.exists(LOG):
        raw = open(LOG, "rb").read()
        text = raw.decode("utf-8", "replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        print(f"log lines={len(lines)} "
              f"last_write={time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(LOG)))}")
        print("--- tail 8 ---")
        print("\n".join(lines[-8:]))
    else:
        print("(no log yet)")
    print(f"artifact n2_w15_judge_state.json: "
          f"{'EXISTS ' + str(os.path.getsize(STATE)) + 'B' if os.path.exists(STATE) else 'absent'}")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    sys.exit(claim() if mode == "claim" else status())
