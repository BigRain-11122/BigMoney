"""r531 bm-a: W18 freeze surgical replay onto moved origin (23667218e bm-b W19 v3).

Three colliding files (both sides pure-additive wave registrations, DISJOINT
bands: W18 A 78_001..80_000 / B 38_300..38_499 [bm-a] vs W19 A 80_001..82_000
/ B 38_500..38_699 [bm-b re-band v3]) -> 3-way merge-file, conflict hunks
resolved as union (mine-block then theirs-block: wave order 18 then 19).
Output to temp dir for inspection; NO working-tree touch (surgical law).
"""
import subprocess, os, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
BASE = "c0c632b22"
MINE = subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"]).decode().strip()
THEIRS = subprocess.check_output(["git", "-C", REPO, "rev-parse", "origin/main"]).decode().strip()
OUT = os.path.join(os.environ["TEMP"], "r531_surgical")
os.makedirs(OUT, exist_ok=True)

COLLIDE = ["scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py",
           "research/PERPETUAL_FACES.md"]

def show(rev, path):
    return subprocess.check_output(["git", "-C", REPO, "show", f"{rev}:{path}"])

def resolve_union(text):
    """Order within each conflict hunk: mine then theirs."""
    lines = text.split("\n")
    out, i, conflicts = [], 0, 0
    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            mine_blk, theirs_blk, mode = [], [], 0
            i += 1
            while i < len(lines) and not lines[i].startswith(">>>>>>>"):
                if lines[i].startswith("======="):
                    mode = 1
                elif mode == 0:
                    mine_blk.append(lines[i])
                else:
                    theirs_blk.append(lines[i])
                i += 1
            i += 1  # skip >>>>>>>
            conflicts += 1
            out.extend(mine_blk)
            out.extend(theirs_blk)
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), conflicts

report = []
for path in COLLIDE:
    b = os.path.join(OUT, "b_" + path.replace("/", "__"))
    m = os.path.join(OUT, "m_" + path.replace("/", "__"))
    t = os.path.join(OUT, "t_" + path.replace("/", "__"))
    for p, rev in ((b, BASE), (m, MINE), (t, THEIRS)):
        with open(p, "wb") as f:
            f.write(show(rev, path))
    r = os.path.join(OUT, "merged_" + path.replace("/", "__"))
    rc = subprocess.run(["git", "-C", REPO, "merge-file", "-p", "-L", "mine",
                          "-L", "base", "-L", "theirs", m, b, t],
                         capture_output=True)
    merged, n = resolve_union(rc.stdout.decode("utf-8"))
    with open(r, "w", encoding="utf-8", newline="") as f:
        f.write(merged)
    report.append(f"{path}: merge-file rc={rc.returncode} conflicts_resolved={n}")

for line in report:
    print(line)
print("MINE=", MINE[:12], "THEIRS=", THEIRS[:12])
print("OUT_DIR=", OUT)
