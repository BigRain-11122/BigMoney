"""r802 bm-c C-20261009-02 @BigMoney dispatch item-1 executor: root per-round
commit-msg scratch quarantine. Law chain = TREASURE_PROTECTION_LAW s2:
treasure_guard prescan (rc3 hard-stop per r483-ii law) -> quarantine (move +
manifest, 7-day observation window) -> assert (manifest identity). Scope =
bm-c-owned tracked root _r*msg*.txt only (257); the 35 other-machine bma/bmb
files are left for their owners (pre-push claw audit.machine ownership gate).
Every subprocess passes CREATE_NO_WINDOW (U060 silence law)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
TG = os.path.join(ROOT, "Tools", "treasure_guard.py")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


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
    mine = [f for f in tracked if "bmc" in f]
    others = [f for f in tracked if "bmc" not in f]
    if not all("/" not in f for f in mine):
        print("ABORT: non-root path in target set")
        return 2
    print("tracked=%d bm-c-owned=%d other-machine(left)=%d" % (
        len(tracked), len(mine), len(others)))

    rc, out = run([PY, TG, "prescan"] + mine)
    print("prescan rc=%d | %s" % (rc, out.strip().splitlines()[-1] if out.strip() else ""))
    if rc != 0:
        print("HARD STOP per r483-ii law: prescan nonzero -- no quarantine, no surgery")
        return rc

    reason = ("C-20261009-02 @BigMoney dispatch item-1: root per-round commit-msg "
              "scratch files, regenerable artifacts, bm-c-owned %d files "
              "(other-machine 35 left to owners per claw ownership gate); "
              "7-day observation window per TREASURE_PROTECTION_LAW s2.2" % len(mine))
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
    print("assert rc=%d | %s" % (rc, out.strip().splitlines()[-1] if out.strip() else ""))
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
    print("DONE dispatch item-1: quarantined=%d manifest=%s" % (len(mine), manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
