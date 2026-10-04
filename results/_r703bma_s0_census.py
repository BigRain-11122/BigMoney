# r703 bm-a S0 probe 3: full dirty-tree census (M vs ??) before churn-absorb commit
import subprocess

def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout

st = git(["status", "--porcelain"])
mod, untracked, other = [], [], []
for l in st.splitlines():
    if not l.strip():
        continue
    tag = l[:2].strip()
    p = l[3:].strip()
    if tag == "M" or tag == "MM" or tag == "AM":
        mod.append(p)
    elif tag == "??":
        untracked.append(p)
    else:
        other.append((tag, p))
print("MODIFIED tracked:", len(mod))
for p in sorted(mod):
    print("  M:", p)
print("UNTRACKED:", len(untracked))
for p in sorted(untracked):
    print("  ?:", p)
print("OTHER:", len(other))
for t, p in other:
    print("  ", t, p)
