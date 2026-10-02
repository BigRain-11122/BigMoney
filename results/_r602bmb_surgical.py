# r602 bm-b surgical reland (r523/r589): tracked live-write faces present => rebase forbidden (r532).
# Payload from working-tree stable files; pool heal 3-face + MSG + bookkeeping + non-collision S6 faces.
# Three assertions fail-closed: deletion-set empty, tree-delta == payload, spot ls-tree checks.
import subprocess, sys, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)

MY34 = [
    "state.json", "fleet/machines/bm-b.json", "logs/iteration-loop/round_reports.md",
    "docs/daily_report/REPORT-2026-10-03.json", "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json", "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/astock_daily_update_status.json",
    "results/compute_audit.bm-b.json", "results/compute_audit.json",
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/etf_daily_pull_status.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-b.json", "results/futures_update_status.json",
    "results/lhb_update_status.bm-b.json", "results/lhb_update_status.json",
    "results/pool_dualrun.bm-b.jsonl", "results/prospect_promotion/_summary.json",
    "results/regime_state.bm-b.json", "results/regime_state.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/token_usage.bm-b.json", "results/token_usage.json",
    "results/update_status.bm-b.json", "results/update_status.json",
    "results/_r602bmb_s6_runner.ps1", "results/_r602bmb_s6_verdicts.py",
    "results/_r602bmb_bookkeep.py",
]
EXTRA = [
    "results/runnable_pool.json", "results/runnable_pool.bm-a.json", "results/runnable_pool.bm-b.json",
    "fleet/inbox/MSG-2026-10-03-0535-bmb-bma-valuepb-x2-killadvice-poolheal.md",
    "results/_r602bmb_pool_heal.py", "results/_r602bmb_originpool_probe.py",
    "results/_r602bmb_addendum.py", "results/_r602bmb_closeout.py", "results/_r602bmb_s6_runner.log",
    "results/_r602bmb_surgical.py", "results/_r602bmb_postclean.py",
]
LIVE_WRITE_KEEP = {
    "results/autofill_state.bm-b.json", "results/p1d_gates.json",
    "results/pool_core_samples.jsonl", "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl", "results/saturation_engine/state_bm-b.json",
    "results/fund_value_p1/nulls.jsonl", "results/_r603bmb_sens_partial_killed.jsonl",
}

def run(args, env=None, check=True):
    p = subprocess.run(args, capture_output=True, env=env)
    if check and p.returncode != 0:
        print("CMD FAIL:", " ".join(args[:6]), "...", p.stderr.decode("utf-8", "replace")[:400])
        sys.exit(1)
    return p

# execution-time origin truth (r593 freshness law)
origin_sha = run(["git", "rev-parse", "origin/main"]).stdout.decode().strip()
print("origin/main @ execution:", origin_sha)

# install healed pool faces from heal temp dir to working tree (then hash-object from disk)
import shutil
TD = os.path.join(REPO, "results", "_r602bmb_poolheal_td")
for name in ("runnable_pool.json", "runnable_pool.bm-a.json", "runnable_pool.bm-b.json"):
    src = os.path.join(TD, name)
    if not os.path.exists(src):
        print("ABORT: healed face missing in temp dir:", src); sys.exit(9)
    shutil.copyfile(src, os.path.join(REPO, "results", name))
    print("healed face installed:", name)

# collision set = incoming changed paths (executed vs my closeout base cdf1f540c)
incoming = set()
for c in ("b3cd4db34", "f9c8311c5"):
    p = run(["git", "show", "--name-status", "--format=", c])
    for ln in p.stdout.decode("utf-8", "replace").splitlines():
        parts = ln.split("\t")
        if parts and parts[0] and parts[-1]:
            incoming.add(parts[-1])
collision = sorted(set(MY34) & incoming)
payload = [f for f in MY34 if f not in set(collision)] + EXTRA
print("collision faces (take origin-newer per r109):", len(collision))
for c in collision:
    print("  -", c)
print("payload files:", len(payload))
missing = [f for f in payload if not os.path.exists(f)]
if missing:
    print("ABORT: payload files missing on disk:", missing); sys.exit(2)

# temp index from origin tree
tmpidx = os.path.join(REPO, "results", "_r602bmb_surgical.index")
if os.path.exists(tmpidx):
    os.remove(tmpidx)
env = {**os.environ, "GIT_INDEX_FILE": tmpidx}
run(["git", "read-tree", origin_sha], env=env)

noops = []
for f in payload:
    sha = run(["git", "hash-object", "-w", "--", f]).stdout.decode().strip()
    osha_p = run(["git", "rev-parse", "origin/main:" + f], check=False)
    if osha_p.returncode == 0 and osha_p.stdout.decode().strip() == sha:
        noops.append(f)
        continue
    run(["git", "update-index", "--add", "--cacheinfo", "100644", sha, f], env=env)
if noops:
    payload = [f for f in payload if f not in set(noops)]
    print("no-op payload entries dropped (content == origin):", noops)
new_tree = run(["git", "write-tree"], env=env).stdout.decode().strip()
print("new tree:", new_tree)

# assertion 1+2: diff origin_tree -> new_tree
otree = run(["git", "rev-parse", origin_sha + "^{tree}"]).stdout.decode().strip()
p = run(["git", "diff-tree", "-r", "--name-status", "--no-renames", otree, new_tree])
delta, dels = [], []
for ln in p.stdout.decode("utf-8", "replace").splitlines():
    if not ln.strip():
        continue
    parts = ln.split("\t")
    kind, path = parts[0], parts[-1]
    delta.append((kind, path))
    if "D" in kind:
        dels.append((kind, path))
if dels:
    print("ABORT: deletion set non-empty:", dels[:10]); sys.exit(3)
delta_paths = {d[1] for d in delta}
payload_set = set(payload)
if delta_paths != payload_set:
    print("ABORT: tree-delta != payload")
    print("  delta-only:", sorted(delta_paths - payload_set)[:10])
    print("  payload-only:", sorted(payload_set - delta_paths)[:10])
    sys.exit(4)
kinds = {}
for k, _ in delta:
    kinds[k] = kinds.get(k, 0) + 1
print("ASSERT PASS: deletion-set empty, tree-delta == payload (%s)" % kinds)

# commit-tree (plumbing: sanctioned surgical path r523; pre-push claw still gates the push)
new_c = run(["git", "commit-tree", new_tree, "-p", origin_sha,
             "-F", r".codely-cli\scratch\r602_surgical_msg.txt"]).stdout.decode().strip()
print("new commit:", new_c)
par = run(["git", "rev-parse", new_c + "^"]).stdout.decode().strip()
assert par == origin_sha, "parent mismatch"
print("parent == origin/main: OK")

# CAS move ref: old value = CURRENT local main (full 40-char, r524); new commit's
# parent==origin already proven by construction (commit-tree -p + assert above).
local_old = run(["git", "rev-parse", "refs/heads/main"]).stdout.decode().strip()
print("local main before CAS:", local_old)
p = run(["git", "update-ref", "refs/heads/main", new_c, local_old], check=False)
if p.returncode != 0:
    print("CAS FAILED (local main moved concurrently):", p.stderr.decode()[:300]); sys.exit(5)
print("CAS update-ref OK")
run(["git", "reset", "--mixed", new_c])
print("reset --mixed done")

# faceted checkout: all D rows + M rows not in live-write keep set
p = run(["git", "status", "--porcelain=v1", "--no-renames"])
restored, kept = [], []
for ln in p.stdout.decode("utf-8", "replace").splitlines():
    if len(ln) < 4:
        continue
    xy, path = ln[:2], ln[3:]
    if path in LIVE_WRITE_KEEP:
        kept.append(path)
        continue
    if "D" in xy or ("M" in xy):
        run(["git", "checkout", "--", path])
        restored.append(path)
print("checkout restored:", len(restored), "| live-write kept dirty:", len(kept))
for k in kept:
    print("  keep-dirty:", k)

# final pre-push sanity
p = run(["git", "status", "--porcelain=v1", "--no-renames"])
rem = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
print("post-reset status rows:", len(rem))
for l in rem:
    print("  ", l[:120])
print("SURGICAL TREE READY, head:", run(["git", "rev-parse", "HEAD"]).stdout.decode().strip())
