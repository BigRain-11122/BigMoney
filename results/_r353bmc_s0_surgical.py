"""r353 bm-c S0 surgical: selective restore + W53 heritage adoption (CAS push).

Laws applied: r296-3 (restore-to-HEAD for shared regen faces, keep live lanes),
r530 (diff-based payload staging, deletion-set asserted empty), r512 (CAS retry
on push rejection -- blobs already in store, recommit cheap), r525 (rogue W55
shard ownership pre-verified audit.machine=bm-c before discard).
Python subprocess arg lists throughout (zero CRT quoting, r330/r503 laws).
"""
import os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\r353a_msg.txt"
TMPIDX = os.path.join(REPO, ".git", "_r353_tmpindex")

KEEP = {
    "research/PERPETUAL_N1_W53_PREREG.md",       # my payload (worktree newer)
    "results/autofill_state.bm-c.json",          # live daemon lane
    "results/dispatcher_state.bm-c.json",       # live daemon lane
    "results/saturation_engine_state.bm-c.json",# live engine lane
    "results/saturation_engine/face_bm-c.json", # live engine lane
    "results/fund_history_status.json",         # live T-131 collector lane
}
PAYLOAD = [
    "research/PERPETUAL_N1_W53_PREREG.md",
    "results/perpetual_faces/n1_w53_results.json",
    "results/_r352bmc_w53_extract.py",
    "results/_r352bmc_w55_band_gate.py",
]

def git(args, env=None, check=True):
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, env=env)
    out = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace").strip()
    if check and r.returncode != 0:
        print("GIT_FAIL", args[:3], "rc=%d" % r.returncode)
        print(err[:800])
        sys.exit(1)
    return r.returncode, out, err

# ---------- phase 1: selective restore ----------
rc, out, _ = git(["status", "--porcelain"])
entries = []
for line in out.splitlines():
    if len(line) < 4:
        continue
    xy, path = line[:2], line[2:].lstrip()
    if xy == "??":
        continue
    if path in KEEP:
        continue
    if xy[0] in "MD" or xy[1] in "MD":
        entries.append(path)
print("PHASE1 restore paths =", len(entries))
if entries:
    git(["checkout", "--"] + entries)
# verify: remaining M/D must be subset of KEEP
rc, out, _ = git(["status", "--porcelain"])
residual = [l for l in out.splitlines()
            if l[:2] != "??" and l[2:].lstrip() not in KEEP]
print("PHASE1 residual non-keep entries =", len(residual))
for l in residual[:12]:
    print("  RES:", l[:120])
if residual:
    print("PHASE1 FAIL: non-keep dirty entries remain")
    sys.exit(2)

# ---------- phase 2: surgical CAS push of W53 heritage ----------
rc, _, _ = git(["fetch", "origin"])
for attempt in range(1, 4):
    _, parent, _ = git(["rev-parse", "origin/main"])
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = TMPIDX
    git(["read-tree", parent], env=env)
    for p in PAYLOAD:
        _, blob, _ = git(["hash-object", "-w", p])
        git(["update-index", "--add", "--cacheinfo",
             "100644,%s,%s" % (blob, p)], env=env)
    rc, diff, _ = git(["diff-index", "--cached", "--name-status", parent], env=env)
    adds, mods, dels = [], [], []
    for l in diff.splitlines():
        parts = l.split("\t")
        if len(parts) < 2:
            continue
        (dels if parts[0].startswith("D") else
         (mods if parts[0].startswith("M") else adds)).append(parts[-1])
    print("ATTEMPT %d payload: A=%d M=%d D=%d" % (attempt, len(adds), len(mods), len(dels)))
    if dels:
        print("FAIL: deletion set non-empty -- abort per r530/r531 law")
        sys.exit(3)
    expect = set(PAYLOAD)
    got = set(adds) | set(mods)
    if got != expect:
        print("FAIL: payload set mismatch", sorted(expect ^ got))
        sys.exit(3)
    _, tree, _ = git(["write-tree"], env=env)
    rc, sha, err = git(["commit-tree", tree, "-p", parent, "-F", MSG], env=env, check=False)
    if rc != 0:
        print("commit-tree FAIL:", err[:400]); sys.exit(4)
    rc, _, err = git(["push", "origin", sha + ":refs/heads/main"], check=False)
    print("PUSH rc=%d attempt=%d" % (rc, attempt))
    if rc == 0:
        break
    git(["fetch", "origin"])
else:
    print("FAIL: 3 push attempts rejected")
    sys.exit(5)

# delivery verification (O-1108 law)
git(["fetch", "origin"])
_, tip, _ = git(["rev-parse", "origin/main"])
print("origin/main =", tip, "== pushed:", tip == sha)
_, ls, _ = git(["ls-tree", "origin/main", "--name-only",
                "results/perpetual_faces/n1_w53_results.json"])
print("delivery ls-tree hit:", ls)
if tip != sha or not ls:
    print("FAIL: delivery not verified")
    sys.exit(6)

# local re-anchor + temp index cleanup
git(["reset", "--mixed", "origin/main"])
if os.path.exists(TMPIDX):
    os.remove(TMPIDX)
rc, out, _ = git(["status", "--porcelain"])
print("FINAL status lines:", len(out.splitlines()))
for l in out.splitlines()[:14]:
    print("  ST:", l[:120])
print("OK r353 S0 surgical complete")
