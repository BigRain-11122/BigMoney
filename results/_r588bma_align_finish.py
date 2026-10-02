# -*- coding: utf-8 -*-
# r588 bm-a post-surgical alignment completion (D-face restore + M-face classifier)
import subprocess, os
REPO = os.getcwd()

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        return None
    return r

head = git(["rev-parse", "HEAD"]).stdout.strip()
base = git(["rev-parse", "origin/main"]).stdout.strip()
assert head == base, ("local head != origin", head, base)

st = git(["status", "--porcelain"]).stdout
d_files, m_files = [], []
for l in st.splitlines():
    if not l.strip(): continue
    code, path = l[:2], l[3:].strip().strip('"')
    if "D" in code: d_files.append(path)
    elif "M" in code: m_files.append(path)
print("D-faces:", len(d_files), "M-faces:", len(m_files))

if d_files:
    r = git(["checkout", "--"] + d_files)
    print("D restore rc=", r.returncode if r else None)

restored, kept = [], []
for f in m_files:
    w = git(["hash-object", f]).stdout.strip()
    h = git(["rev-parse", "HEAD:" + f]).stdout.strip()
    if w == h:
        continue  # clean after EOL normalization
    # find the blob of the pre-reset base (83e32f163 = origin~1 at reset time)
    o = git(["rev-parse", "83e32f163:" + f]).stdout.strip()
    if o and w == o:
        git(["checkout", "--", f]); restored.append(f)
    else:
        kept.append(f)  # local live-write/new content -> keep (next round re-derives)
print("restored stale M-faces:", len(restored), [os.path.basename(x) for x in restored[:6]])
print("kept live M-faces:", len(kept), [os.path.basename(x) for x in kept[:8]])
st2 = git(["status", "--porcelain"]).stdout
nd = sum(1 for l in st2.splitlines() if "D" in l[:2])
nm = sum(1 for l in st2.splitlines() if "M" in l[:2])
uu = sum(1 for l in st2.splitlines() if "U" in l[:2])
print("final: D=%d M=%d U=%d" % (nd, nm, uu))
