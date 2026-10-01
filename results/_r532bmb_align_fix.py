# r532 alignment fix v2: robust face list via git diff --name-only HEAD.
import subprocess, os, sys
R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(R)

def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")

LIVE_FILES = {
    "results/lowamp_p3/nulls.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/autofill_state.bm-b.json",
}
rc, out = git("diff", "--name-only", "HEAD")
files = [l for l in out.strip().splitlines() if l]
print("worktree-vs-HEAD differing files:", len(files))
n = 0
skipped = []
for f in files:
    if f in LIVE_FILES:
        skipped.append(f); continue
    rc, out = git("checkout", "--", f)
    if rc != 0:
        print("checkout FAIL:", f, out.strip()[-100:]); sys.exit(1)
    n += 1
print("checked out:", n, "| live skipped:", skipped)
rc, out = git("status", "--porcelain")
print("remaining dirty:")
print(out.strip() or "(clean)")
# presence assertions (r326-III: restored faces must be on disk)
for f in ["results/perpetual_faces/n1_w39_results.json",
          "results/p2cal_ext/n1_w41/shard-2-of-12.json",
          "results/pool_claims/LOWAMP-P3-SENS/lowamp-p3-sens-0of1.bm-a.json",
          "CODELY.md", "research/PERPETUAL_N1_W39_PREREG.md"]:
    print(("PRESENT " if os.path.exists(f) else "ABSENT  ") + f)
rc, out = git("log", "-1", "--format=%h %s")
print("HEAD:", out.strip()[:100])
