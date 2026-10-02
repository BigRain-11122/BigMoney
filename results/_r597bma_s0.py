# r597 bm-a S0 pure-FF integration + dead-r596 estate preservation
# Laws applied: r585/r595 pure-FF sequence, r593 execution-time rev-parse,
# r384 dirty-cap-delta classification, r595 CODELY line-set union,
# r380 porcelain no-strip, r580 python argv (no PS batch git), r373 blob-space accounting.
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def gitb(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        print("GITFAIL", args, r.stderr.decode("utf-8", "replace")[:800])
        sys.exit(1)
    return r.stdout

def gits(*args):
    return gitb(*args).decode("utf-8", "replace")

ORIGIN_SHA = gits("rev-parse", "origin/main").strip()   # execution-time read (r593 law)
HEAD_SHA = gits("rev-parse", "HEAD").strip()
print("HEAD:", HEAD_SHA[:10], "-> FF -> origin:", ORIGIN_SHA[:10])
assert ORIGIN_SHA != HEAD_SHA, "nothing to integrate"
assert gits("merge-base", HEAD_SHA, ORIGIN_SHA).strip() == HEAD_SHA, "not pure-FF (local commits exist)"

# ---- 1. delta (HEAD..origin) ----
raw = gits("diff", "--name-status", "--no-renames", HEAD_SHA, ORIGIN_SHA)
delta = []
for line in raw.splitlines():
    if not line.strip():
        continue
    parts = line.split("\t")
    delta.append((parts[0], parts[1]))
print("delta files:", len(delta))

# ---- 2. local dirty/untracked sets (porcelain, line-raw per r380) ----
raw = gits("status", "--porcelain")
dirty, untracked = set(), set()
for line in raw.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    if st == "??":
        untracked.add(path)
    else:
        dirty.add(path)
print("local dirty:", len(dirty), "untracked:", len(untracked))

UNION_FILES = ["CODELY.md", "knowledge/METHODOLOGY_ASSETS.md"]

# ---- 3. pre-FF line-set probes (blob space, LF) ----
def blob_lines(rev, path):
    b = gitb("show", rev + ":" + path)
    return b.replace(b"\r\n", b"\n").split(b"\n")

def disk_lines(path):
    with open(os.path.join(REPO, path), "rb") as f:
        return f.read().replace(b"\r\n", b"\n").split(b"\n")

probe = {}
for p in UNION_FILES:
    ol, ll = blob_lines(ORIGIN_SHA, p), disk_lines(p)
    oset, lset = set(ol), set(ll)
    only_local = [l for l in ll if l not in oset]
    only_origin = [l for l in ol if l not in lset]
    probe[p] = (ol, only_local, only_origin)
    print(p, "| origin:", len(ol), "local:", len(ll),
          "| only_local:", len(only_local), "only_origin:", len(only_origin))
    for l in only_local:
        print("   LOCAL-ONLY:", l[:110].decode("utf-8", "replace").encode("ascii", "replace").decode())
    for l in only_origin:
        print("   ORIGIN-NEW:", l[:110].decode("utf-8", "replace").encode("ascii", "replace").decode())

# ---- 4. pure FF: reset --mixed to origin (moves branch+index; worktree untouched) ----
subprocess.run(["git", "-C", REPO, "reset", "--mixed", ORIGIN_SHA], check=True)

# ---- 5. checkout clean delta faces from index (materialize/update origin content) ----
checkout = [p for _, p in delta if p not in dirty and p not in untracked and p not in UNION_FILES]
r = subprocess.run(["git", "-C", REPO, "checkout", "--"] + checkout, capture_output=True)
print("checkout faces:", len(checkout), "rc:", r.returncode, r.stderr.decode("utf-8", "replace")[:400])
assert r.returncode == 0

# ---- 6. union writes: origin verbatim + local-only tail append (LF disk) ----
for p in UNION_FILES:
    ol, only_local, only_origin = probe[p]
    if not only_local:
        # pure origin-verbatim restore (nothing of mine to keep)
        data = gitb("show", ORIGIN_SHA + ":" + p)
        with open(os.path.join(REPO, p), "wb") as f:
            f.write(data.replace(b"\r\n", b"\n"))
        print(p, "restored origin-verbatim")
        continue
    body = [l for l in ol if True]
    while body and body[-1] == b"":
        body.pop()
    if body and body[-1].strip():
        body.append(b"")
    body.extend(only_local)
    while body and body[-1] == b"":
        body.pop()
    out = b"\n".join(body) + b"\n"
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(out)
    # zero-loss assertions
    got = set(disk_lines(p))
    miss_o = [l for l in ol if l not in got and l.strip()]
    miss_l = [l for l in only_local if l not in got]
    assert not miss_o and not miss_l, (miss_o[:2], miss_l[:2])
    print(p, "union written:", len(disk_lines(p)), "lines; origin+local-only zero-loss OK")

# ---- 7. post-verify: no unstaged-D of delta files, estate intact ----
raw = gits("status", "--porcelain")
d_lost = []
estate_check = {
    "research/FUND-VALUE-P1.md": "??",
    "fleet/tasks/T-2026-10-02-149-P1.json": "??",
    "fleet/inbox/MSG-2026-10-02-2230-bma-ALL-fund-value-p1.md": "??",
    "results/_r596bma_fund_value_probe.json": "??",
}
for line in raw.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    if st.strip() == "D" and any(path == p for _, p in delta):
        d_lost.append(path)
assert not d_lost, ("delta face left deleted on disk", d_lost)
for p, want in estate_check.items():
    got = None
    for line in raw.splitlines():
        if line.strip() and line[3:] == p:
            got = line[:2]
    assert got == want, (p, got)
print("estate intact; delta D-faces zero")
print("S0 DONE. main == origin ==", ORIGIN_SHA[:10])
