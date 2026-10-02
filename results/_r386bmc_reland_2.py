# -*- coding: utf-8 -*-
# r386 bm-c reland step 2: blockers checkout -> FF -> D-restore (r589/r595 laws)
import subprocess, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NW = 0x08000000

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=NW)
    if check and r.returncode != 0:
        print("GIT-FAIL", args, r.returncode, r.stdout[-400:], r.stderr[-400:])
        sys.exit(1)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

rc, base, _ = git(["rev-parse", "HEAD"])
rc, target, _ = git(["rev-parse", "origin/main"])
assert base != target

# 1. origin-changed files
rc, changed, _ = git(["diff", "--name-only", base, target])
origin_changed = set(x for x in changed.splitlines() if x.strip())

# 2. my dirty files
rc, st, _ = git(["status", "--porcelain"])
dirty = []
for l in [x for x in st.splitlines() if x.strip()]:
    code = l[:2]
    path = l[3:]
    if code.strip() == "??":
        continue
    dirty.append(path)

blockers = [p for p in dirty if p in origin_changed]
print("BLOCKERS (%d):" % len(blockers))
for p in sorted(blockers):
    print("  ", p)

# 3. save union-target content (mine) before discarding
codely = open(os.path.join(REPO, "CODELY.md"), "rb").read().decode("utf-8")
metho = open(os.path.join(REPO, "knowledge", "METHODOLOGY_ASSETS.md"), "rb").read().decode("utf-8")
t147 = json.load(open(os.path.join(REPO, "fleet", "tasks", "T-2026-10-02-147-P1.json"), encoding="utf-8"))
saved = {
    "codely_mine_tail": codely.splitlines()[-1],  # my r386 entry (last line)
    "metho_mine": metho,
    "t147_progress_mine": t147.get("progress", ""),
}
json.dump(saved, open(os.path.join(REPO, "results", "_r386bmc_union_saved.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("union content saved")

# 4. discard my versions of blockers (all are shared/origin-verbatim or union-after)
if blockers:
    git(["checkout", "--"] + blockers)
    print("blockers reverted to HEAD (base) versions")

# 5. delete untracked MSG copy (blob-identical to origin tracked copy, verified earlier)
msgp = os.path.join(REPO, "fleet", "inbox", "processed", "MSG-2026-10-02-2200-bmc-ALL-w115-park.md")
if os.path.exists(msgp):
    h1 = git(["hash-object", msgp])[1]
    h2 = git(["rev-parse", "origin/main:fleet/inbox/processed/MSG-2026-10-02-2200-bmc-ALL-w115-park.md"])[1]
    assert h1 == h2, (h1, h2)
    os.remove(msgp)
    print("untracked MSG copy removed (blob-identical, zero loss)")

# 6. FF merge (r593: execution-time rev-parse target)
rc, new2, _ = git(["rev-parse", "origin/main"])
rc, out, err = git(["merge", "--ff-only", "origin/main"], check=False)
print("FF rc", rc, out[:100], err[:200])
if rc != 0:
    sys.exit(2)
rc, head, _ = git(["rev-parse", "HEAD"])
assert head == new2
print("HEAD now", head[:12])

# 7. D faces -> restore (E-08)
rc, st, _ = git(["status", "--porcelain"])
d = []
for l in [x for x in st.splitlines() if x.strip()]:
    if "D" in l[:2]:
        d.append(l[3:])
if d:
    git(["restore", "--"] + d)
    print("restored D faces:", len(d))
    for p in d:
        print("  D-restored", p)

# 8. final status
rc, st, _ = git(["status", "--porcelain"])
m, u, dd = [], [], []
for l in [x for x in st.splitlines() if x.strip()]:
    code = l[:2]
    path = l[3:]
    if code.strip() == "??":
        u.append(path)
    elif "D" in code:
        dd.append(path)
    else:
        m.append(path)
print("FINAL: M=%d ??=%d D=%d" % (len(m), len(u), len(dd)))
assert not dd, "D faces must be zero"
for p in sorted(m):
    print("  M", p)
print("STEP2 DONE")
