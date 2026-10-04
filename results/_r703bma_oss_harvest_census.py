# r703 bm-a probe: group-tree oss-harvest face census (D-20261005-05① consumption)
import subprocess, os

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

def gshow(rev, path):
    r = subprocess.run(["git", "-C", GRP, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def gls(rev, path):
    r = subprocess.run(["git", "-C", GRP, "ls-tree", "--name-only", rev, path], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").splitlines()

# 1. working tree state (clean? behind?)
st = subprocess.run(["git", "-C", GRP, "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
print("group worktree dirty files:", len([l for l in st.splitlines() if l.strip()]))
for l in st.splitlines()[:8]:
    print("  ", l[:120])
behind = subprocess.run(["git", "-C", GRP, "rev-list", "--count", "HEAD..origin/main"], capture_output=True, text=True).stdout.strip()
ahead = subprocess.run(["git", "-C", GRP, "rev-list", "--count", "origin/main..HEAD"], capture_output=True, text=True).stdout.strip()
print(f"group tree HEAD: behind origin={behind} ahead={ahead}")

# 2. oss-harvest dir on origin
entries = gls("origin/main", "cph4/oss-harvest/")
print("cph4/oss-harvest on origin:", entries if entries else "(absent -> first company file = BigMoney creates)")
for e in entries[:10]:
    print("  O:", e)
