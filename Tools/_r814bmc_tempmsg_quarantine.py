"""r814 bm-c C-20261009-02 @BigMoney dispatch item-2 re-accumulated face:
root per-round commit-msg scratch quarantine, SECOND batch (r802 first
batch = 257 files at 12:50; these 5 re-accumulated from rounds r807/r808
the same afternoon). Law chain = TREASURE_PROTECTION_LAW s2: treasure_guard
prescan (rc3 hard-stop per r483-ii law) -> quarantine (move + manifest,
7-day observation window) -> assert (manifest identity).
EXCLUSION LAW (r811): _r_bmc_s0msg.txt is the LIVE tracked S0 scratch
msg file rewritten every S0 run -- absorbed same-window by the S0 helper,
NEVER quarantined. Scope = bm-c-owned tracked root _r*msg*.txt only;
other-machine files left for their owners (pre-push claw ownership gate).
1-gen clone of _r802bmc_tempmsg_quarantine.py. CREATE_NO_WINDOW (U060)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
TG = os.path.join(ROOT, "Tools", "treasure_guard.py")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
LIVE_KEEP = "_r_bmc_s0msg.txt"


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, creationflags=CNW)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    return p.returncode, out


def main():
    rc, out = run(["git", "ls-files", "--", "_r*msg*.txt"])
    if rc != 0:
        print("git ls-files failed:", out[:300])
        return 2
    tracked = [f for f in out.split() if f]
    mine = [f for f in tracked if "bmc" in f and f != LIVE_KEEP]
    others = [f for f in tracked if "bmc" not in f]
    if not all("/" not in f for f in mine):
        print("ABORT: non-root path in target set")
        return 2
    print("tracked=%d bm-c-owned(target)=%d live-kept=%s other-machine(left)=%d"
          % (len(tracked), len(mine),
             LIVE_KEEP if LIVE_KEEP in tracked else "untracked",
             len(others)))
    if not mine:
        print("NOTHING TO QUARANTINE (already clean)")
        return 0

    rc, out = run([PY, TG, "prescan"] + mine)
    print("prescan rc=%d | %s" % (rc, out.strip().splitlines()[-1]
                                  if out.strip() else ""))
    if rc != 0:
        print("HARD STOP per r483-ii law: prescan nonzero -- no quarantine")
        return rc

    reason = ("C-20261009-02 @BigMoney dispatch item-2 second batch (r814): "
              "root per-round commit-msg scratch files re-accumulated from "
              "r807/r808, regenerable artifacts, bm-c-owned %d files; live "
              "S0 scratch _r_bmc_s0msg.txt excluded per r811 law; 7-day "
              "observation window per TREASURE_PROTECTION_LAW s2.2" % len(mine))
    rc, out = run([PY, TG, "quarantine"] + mine + ["--reason", reason])
    print("quarantine rc=%d" % rc)
    if rc != 0:
        print(out[:400])
        return rc
    manifest = None
    for line in out.splitlines():
        if line.startswith("manifest:"):
            manifest = line.split(":", 1)[1].strip()
    qdir = os.path.dirname(os.path.join(ROOT, manifest)) if manifest else None
    print(out.strip().splitlines()[0] if out.strip() else "")
    if not manifest:
        print("ABORT: manifest path not found in quarantine output")
        return 2

    rc, out = run([PY, TG, "assert", "--manifest", manifest])
    print("assert rc=%d | %s" % (rc, out.strip().splitlines()[-1]
                                 if out.strip() else ""))
    if rc != 0:
        return rc

    # stage: deletions (root) + quarantine dir additions
    rc, out = run(["git", "add", "-A", "--"] + mine)
    if rc != 0:
        print("git add deletions failed:", out[:300])
        return 2
    qrel = os.path.relpath(qdir, ROOT).replace("\\", "/")
    rc, out = run(["git", "add", qrel])
    if rc != 0:
        print("git add quarantine dir failed:", out[:300])
        return 2
    rc, out = run(["git", "diff", "--staged", "--numstat"])
    adds = sum(1 for l in out.splitlines() if l.strip())
    print("staged numstat lines=%d (expected ~%d renames)" % (adds, len(mine)))
    print("DONE dispatch item-2 batch2: quarantined=%d manifest=%s"
          % (len(mine), manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
