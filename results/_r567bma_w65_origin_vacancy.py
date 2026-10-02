import subprocess
src = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
print("65 in origin N1_BANDS:", "65: {" in src)
print("64 row on origin:", "64: {" in src and "171_004" in src)
print("engine_owner count (rows):", src.count("engine_owner"))
log = subprocess.check_output(
    ["git", "log", "origin/main", "--oneline", "--grep=W65", "-5"],
    encoding="utf-8").strip()
print("origin log grep W65:", log if log else "(zero)")
ls = subprocess.check_output(
    ["git", "ls-tree", "origin/main", "research/", "--name-only"],
    encoding="utf-8")
w65 = [l for l in ls.splitlines() if "W65" in l]
print("origin research W65 files:", w65 if w65 else "(zero)")
