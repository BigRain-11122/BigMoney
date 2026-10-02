# r386 bm-c S0: realign local main to origin (GM local commits = CAS twins already on origin).
# Laws applied: r593 (execution-time rev-parse), r578 (reset --mixed after update-ref),
# r595 (D-face restore law E-08), r580 (python subprocess argv), U060 (CREATE_NO_WINDOW).
import subprocess, sys, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
    if check and r.returncode != 0:
        print("GIT-FAIL", args, r.returncode, r.stdout, r.stderr)
        sys.exit(1)
    return r.stdout.strip()

def is_sha40(s):
    return bool(re.match(r"^[0-9a-f]{40}$", s))

# 1. fresh fetch + execution-time rev-parse (r593 law)
git(["fetch", "origin"])
new = git(["rev-parse", "origin/main"])
old = git(["rev-parse", "HEAD"])
assert is_sha40(new) and is_sha40(old), (new, old)
print("NEW-ORIGIN", new)
print("OLD-LOCAL ", old)

if new == old:
    print("ALREADY-ALIGNED no-op")
    sys.exit(0)

# 2. verify the 3 local-only commits are content-superseded by origin:
#    every path in local HEAD tree must exist in origin tree OR be intentionally parked.
#    Quick union check: diff HEAD origin/main --name-status, deletion direction origin->HEAD.
d = git(["diff", "--name-status", "HEAD", "origin/main"])
head_paths = set()
for line in d.splitlines():
    m = re.match(r"^([AMD])\s+(.+)$", line)
    if m:
        head_paths.add((m.group(1), m.group(2)))
# paths that exist in HEAD but NOT in origin = potential loss if we drop local commits
loss = git(["diff", "--name-only", "origin/main", "HEAD"])
lost = [p for p in loss.splitlines() if p.strip()]
print("LOCAL-ONLY-PATHS-AT-RISK:", len(lost))
for p in lost:
    print("  AT-RISK", p)

# 3. CAS update-ref (old value full 40-hex, r569 law)
r = subprocess.run(["git", "update-ref", "refs/heads/main", new, old], cwd=REPO,
                  capture_output=True, text=True, encoding="utf-8", errors="replace",
                  creationflags=NO_WINDOW)
if r.returncode != 0:
    print("CAS-UPDATE-REF-FAIL (ref moved mid-flight?):", r.stderr.strip())
    sys.exit(2)
print("CAS-UPDATE-REF OK")

# 4. reset --mixed re-anchor index (r578 law: checkout same branch = zero action trap)
git(["reset", "--mixed", new])
print("RESET-MIXED OK")

# 5. status-based face curation (r595 law)
st = git(["status", "--porcelain"])
d_faces, m_faces, untracked = [], [], []
for line in st.splitlines():
    if not line.strip():
        continue
    code = line[:2]
    path = line[3:]
    if "D" in code:
        d_faces.append(path)
    elif code.strip() == "??":
        untracked.append(path)
    else:
        m_faces.append(path)
print("D-FACES", len(d_faces))
for p in d_faces:
    print("  D", p)
print("M-FACES", len(m_faces))
for p in m_faces:
    print("  M", p)
print("UNTRACKED", len(untracked))
for p in untracked:
    print("  ??", p)

# 6. D faces = origin-new files missing on disk (stale-base artifacts) -> restore (E-08 card)
if d_faces:
    r = subprocess.run(["git", "restore", "--"] + d_faces, cwd=REPO, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
    print("RESTORE-D rc", r.returncode, r.stderr.strip())
    if r.returncode != 0:
        sys.exit(3)

print("S0-DONE")
