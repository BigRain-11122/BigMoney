# r703 bm-a OSS harvest anti-dup gate (3-face, per OH-20260929-bigmoney precedent)
import subprocess, os

cands = ["polars", "vectorbt", "pandas-ta", "pandas-ta-classic"]

def grep_count(path, patterns):
    try:
        txt = open(path, encoding="utf-8", errors="replace").read().lower()
        return {p: txt.count(p) for p in patterns}
    except FileNotFoundError:
        return {p: "FILE-ABSENT" for p in patterns}

patterns = [c.lower() for c in cands]

# face 1: cph4 README capability registry (origin blob, zero tree touch)
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
r = subprocess.run(["git", "-C", GRP, "show", "origin/main:cph4/README.md"], capture_output=True)
reg = r.stdout.decode("utf-8", errors="replace").lower()
print("FACE1 cph4/README.md registry hits:")
for p in patterns:
    print(f"  {p}: {reg.count(p)}")

# face 2: in-repo faces (requirements.txt / PLAN.md / scripts imports)
print("FACE2 in-repo hits:")
for f in ("requirements.txt", "PLAN.md", "README.md"):
    print(f"  {f}:", grep_count(f, patterns))
r = subprocess.run(["git", "grep", "-il", "polars"], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("  git grep -il polars (tracked):", (r.stdout or "(zero)").splitlines()[:5])
r2 = subprocess.run(["git", "grep", "-il", "vectorbt"], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("  git grep -il vectorbt (tracked):", (r2.stdout or "(zero)").splitlines()[:5])
r3 = subprocess.run(["git", "grep", "-il", "pandas.ta"], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("  git grep -il pandas.ta (tracked):", (r3.stdout or "(zero)").splitlines()[:8])

# face 3: sister OH files (this window's candidates vs prior OH corpus)
r = subprocess.run(["git", "-C", GRP, "ls-tree", "--name-only", "origin/main", "cph4/oss-harvest/"], capture_output=True, text=True, encoding="utf-8", errors="replace")
oh_files = [l for l in r.stdout.splitlines() if l.strip()]
hits = {}
for f in oh_files:
    blob = subprocess.run(["git", "-C", GRP, "show", f"origin/main:{f}"], capture_output=True).stdout.decode("utf-8", errors="replace").lower()
    for p in patterns:
        if p in blob:
            hits.setdefault(p, []).append(os.path.basename(f))
print("FACE3 sister OH corpus mentions:")
for p in patterns:
    print(f"  {p}: {hits.get(p, '(zero)')}")
