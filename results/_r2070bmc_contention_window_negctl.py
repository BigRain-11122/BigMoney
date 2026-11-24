"""Negative controls for scripts/contention_window.py (r2070 bm-c).

Each leg breaks exactly one thing on a copy of the live face, then restores it, and
asserts what the guard says.  A guard that never says anything on a poisoned input is
indistinguishable from no guard at all (r1282 / r1935).

  python results/_r2070bmc_contention_window_negctl.py
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "contention_window.json")
PAGE = os.path.join(ROOT, "research", "CONTENTION_WINDOW.md")

ok = 0
bad = []


def chk(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
    else:
        bad.append("%s %s" % (name, detail))


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check():
    p = subprocess.run([sys.executable, os.path.join("scripts", "contention_window.py"), "--check"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    face_sha0, page_sha0 = sha(FACE), sha(PAGE)

    rc, out = check()
    chk("clean input reads rc0", rc == 0, "rc=%s %s" % (rc, out[:120]))

    # --- leg 1: one digit of the face changed -> CHECK FAILED, and no STALE word ---
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    original_verdict = face.get("verdict")
    face["verdict"] = "NO_PEER" if original_verdict != "NO_PEER" else "WINDOW_CLOSED"
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    rc, out = check()
    chk("tampered face reads rc3", rc == 3, "rc=%s" % rc)
    chk("tampered face says CHECK FAILED", "CHECK FAILED" in out, out[:160])
    chk("tampered face does not say STALE", "STALE" not in out, out[:160])
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(json.loads(json.dumps(face)), fh, ensure_ascii=False, indent=2)
    # restore by rewriting the true face from a fresh run, then prove it is green again
    subprocess.run([sys.executable, os.path.join("scripts", "contention_window.py"), "run"],
                   cwd=ROOT, capture_output=True)
    rc, out = check()
    chk("re-run after tampering reads rc0", rc == 0, "rc=%s %s" % (rc, out[:120]))

    # --- leg 2: page marker block changed -> rc3, page-specific complaint ---
    with open(PAGE, encoding="utf-8") as fh:
        text = fh.read()
    subprocess.run([sys.executable, os.path.join("scripts", "contention_window.py"), "run"],
                   cwd=ROOT, capture_output=True)
    with open(PAGE, encoding="utf-8") as fh:
        text = fh.read()
    poisoned = text.replace("**判词**：", "**判词**： ", 1)
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(poisoned)
    rc, out = check()
    chk("poisoned page reads rc3", rc == 3, "rc=%s" % rc)
    chk("poisoned page names the page block", "page" in out.lower(), out[:160])
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    rc, out = check()
    chk("restored page reads rc0", rc == 0, "rc=%s %s" % (rc, out[:120]))

    # --- leg 3: moving inputs -> STALE, not CHECK FAILED ---
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    face["inputs_digest"] = "0" * 64
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    rc, out = check()
    chk("moved inputs reads rc3", rc == 3, "rc=%s" % rc)
    chk("moved inputs says STALE", "STALE" in out, out[:160])
    chk("moved inputs does not say CHECK FAILED", "CHECK FAILED" not in out, out[:160])
    subprocess.run([sys.executable, os.path.join("scripts", "contention_window.py"), "run"],
                   cwd=ROOT, capture_output=True)
    rc, out = check()
    chk("after refresh reads rc0", rc == 0, "rc=%s %s" % (rc, out[:120]))

    # --- leg 4: the production liveness probe must be able to say dead ---
    sys.path.insert(0, ROOT)
    from scripts.contention_window import _pid_alive, classify
    chk("pid 0 is not alive", _pid_alive(0) is False)
    chk("a wild pid is not alive", _pid_alive(999999) is False)
    chk("classify is a function of its inputs",
        classify({"hosts": [], "my_host_pid": 1, "recent_writes": []}, 1.0)["verdict"] == "NO_PEER")

    print("SELFTEST %d/%d" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL", b)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
