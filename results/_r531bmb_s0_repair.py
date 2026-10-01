# r531 bm-b S0 integration repair (post-mortem of r530 leftover worktree)
# Facts (verified 01:44-01:50):
#  - origin/main intact & complete (W39 12/12 by bm-c, LOWAMP-P3 cells/claims by bm-a, tools, MSGs)
#  - local branch: 2 ahead (stale-view duplicate claims c3cc6f9b2/aa8ad887b of bm-a's
#    LAREP-DEEP-BASE batch, claimed 01:30/01:32 AFTER bm-a's 01:17 harvest flip => later-arriver
#    yield per r297/r511 => DROP), 9 behind.
#  - worktree: swept to a stale tree at ~01:15:46 (deletions + reverts of other-machine faces);
#    W39 shards 0-4 = bm-b duplicate burns of yielded wave (audit.machine=bm-b verified) => discard.
#  - marks family: origin newer (paper ts 01:15:34 vs local 23:07) => origin wins.
# Rule: M/D files with mtime > 2026-10-02 01:16:00 = post-sweep local writes => KEEP worktree;
#       everything else => checkout origin. Explicit overrides below.
import json, os, subprocess, sys, time

R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(R)

def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")

CUT = time.mktime(time.strptime("2026-10-02 01:16:00", "%Y-%m-%d %H:%M:%S"))

# explicit keep (bm-b live lane / r530 fresh evidence / same-day derives my S6 regenerates anyway)
KEEP = {
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/token_usage.bm-b.json",
    "results/saturation_engine/state_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl",
    "results/saturation_engine/face_bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json",
    "results/_attrition_guard_scan.json",
}
# explicit checkout (origin wins even if post-sweep mtime)
FORCE_ORIGIN = {
    "results/p2cal_ext/n1_w39",  # all 12 shards = bm-c canonical; discard bm-b dup burns 0-4
}
# marks family -> origin (verified newer)
MARKS_DIRS = ["firm/traders", "results/paper", "results/paper_export"]

rc, out = git("reset", "--mixed", "origin/main")
print("RESET rc=%d" % rc)
print(out.strip()[:300])
rc, out = git("log", "-1", "--format=%h")
print("HEAD now:", out.strip())

rc, st = git("status", "--porcelain")
lines = [l for l in st.splitlines() if l.strip()]
keep_files, checkout_files = [], []
for l in lines:
    code, path = l[:2], l[3:].strip().strip('"')
    if code.strip() == "??":
        continue  # untracked handled separately
    full = os.path.join(R, path)
    if any(path.startswith(d) for d in MARKS_DIRS):
        checkout_files.append(path); continue
    if any(path.startswith(d) for d in FORCE_ORIGIN):
        checkout_files.append(path); continue
    if path in KEEP:
        keep_files.append(path); continue
    try:
        m = os.path.getmtime(full)
    except OSError:
        m = 0
    if code.strip() == "D" or m <= CUT:
        checkout_files.append(path)
    else:
        keep_files.append(path)

print("\n== KEEP (worktree newer / live lane) ==")
for f in keep_files: print("  K", f)
print("== CHECKOUT (origin wins) ==")
for f in checkout_files: print("  C", f)

# append-only union check for shared jsonl evidence faces
def union_check(path):
    full = os.path.join(R, path)
    rc, o = git("show", "origin/main:" + path)
    if rc != 0: return "origin-missing"
    olines = [l for l in o.splitlines() if l.strip()]
    try:
        with open(full, encoding="utf-8") as fh: ll = [x for x in fh.read().splitlines() if x.strip()]
    except OSError:
        return "local-missing"
    os_set, ll_set = set(olines), set(ll)
    if os_set <= ll_set:
        return "SUPERSET(+%d)" % len(ll_set - os_set)
    if ll_set <= os_set:
        return "SUBSET(-%d)" % len(os_set - ll_set)
    return "DIVERGENT(+%d/-%d)" % (len(ll_set - os_set), len(os_set - ll_set))

for jl in ["results/pool_core_samples.jsonl", "results/x2_watch_log.jsonl"]:
    v = union_check(jl)
    print("APPEND-CHECK", jl, v)
    if v.startswith(("SUBSET", "DIVERGENT")):
        checkout_files.append(jl)
        keep_files = [f for f in keep_files if f != jl]
    elif v.startswith("SUPERSET"):
        if jl not in keep_files: keep_files.append(jl)

# execute checkouts (batch, quiet)
if checkout_files:
    rc, out = git("checkout", "--", *checkout_files)
    print("\nCHECKOUT rc=%d n=%d" % (rc, len(checkout_files)))
    if rc != 0: print(out[:2000]); sys.exit(1)

rc, st2 = git("status", "--porcelain")
print("\n== POST-REPAIR STATUS ==")
print(st2 if st2.strip() else "(clean)")

# verify: W39 12/12 restored & machine=bm-c
n_ok, m_ok = 0, 0
for i in range(12):
    p = r"results/p2cal_ext/n1_w39/shard-%d-of-12.json" % i
    try:
        d = json.load(open(os.path.join(R, p), encoding="utf-8"))
        n_ok += 1
        if d.get("audit", {}).get("machine") == "bm-c": m_ok += 1
    except Exception:
        pass
print("W39 verify: files=%d/12 machine=bm-c=%d/12" % (n_ok, m_ok))

# verify: lowamp_p3 cells restored (10 cells + 5 cont + probe)
import glob
n = len(glob.glob(r"results/lowamp_p3/*"))
print("lowamp_p3 files restored:", n, "(expect 26)")
# verify: bm-a claim files restored
n = len(glob.glob(r"results/pool_claims/LOWAMP-P3-CELL-*/*.bm-a.json"))
print("bm-a LOWAMP-P3 claim files restored:", n, "(expect >=9)")
# sanity: pool parses + LOWAMP-P3 not claimed by bm-b locally anymore
try:
    pool = json.load(open(r"results/runnable_pool.json", encoding="utf-8"))
    s = json.dumps(pool)
    print("pool parses OK; bm-b LAREP-DEEP-BASE claim present:", "lowamp-p3-cell-larep-deep-base" in s and '"bm-b"' in s)
except Exception as e:
    print("POOL PARSE FAIL", e)
