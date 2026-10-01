# r531 bm-b surgical push: W40 freeze claim + LAEDGE product delivery.
# Pattern: r530 close script (temp-index read-tree origin/main + hash-object
# payload + deletion-set leg r519 + payload-count audit + push + local ref align).
# Peak-window: daemon (autofill/engine appenders) pushes every ~60s; blob-unchanged
# retry is cheap (r512). r320 quoting trap avoided: python argv lists, msg via -F file.
import subprocess, os, sys

R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(R)

def git(*a, **kw):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

payload = [
    # W40 freeze four-file canon set + prereg
    "research/PERPETUAL_N1_W40_PREREG.md",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
    "research/PERPETUAL_FACES.md",
    # r531 receipts
    "results/_r531bmb_w40_band_gate.py",
    "results/_r531bmb_land_w40.py",
    "results/_r531bmb_land_w40_part2.py",
    "results/_r531bmb_land_w40_part3.py",
    "results/_r531bmb_s0_repair.py",
    # LAEDGE burn product delivery (completed batches; pool already flipped
    # done+harvested by the daemon -- r310 product-delivery leg)
    "results/lowamp_p3/cells_LA-EDGE_deep_base.jsonl",
    "results/lowamp_p3/cells_LA-EDGE_deep_x2.jsonl",
    "results/lowamp_p3/cells_LA-EDGE_legacy_base.jsonl",
    "results/lowamp_p3/cont_LA-EDGE_deep_base.json",
    "results/lowamp_p3/cont_LA-EDGE_deep_x2.json",
    "results/lowamp_p3/cont_LA-EDGE_legacy_base.json",
]

rc, out = git("rev-parse", "origin/main")
parent = out.strip()
print("parent=", parent)

idx = os.path.join(os.environ["TEMP"], "fg-r531freeze-idx")
if os.path.exists(idx):
    os.remove(idx)
env = dict(os.environ, GIT_INDEX_FILE=idx)
rc, out = git("read-tree", parent)
assert rc == 0, out

staged = 0
for f in payload:
    if not os.path.exists(f):
        print("MISSING", f, "-- ABORT (payload integrity)")
        sys.exit(1)
    rc, out = git("hash-object", "-w", f)
    assert rc == 0, out
    blob = out.strip()
    rc, out = git("update-index", "--add", "--cacheinfo", f"100644,{blob},{f}")
    assert rc == 0, out
    staged += 1
print("staged payload files:", staged, "of", len(payload))

rc, tree = git("write-tree")
assert rc == 0, tree
tree = tree.strip()

msg_path = os.path.join(os.environ["TEMP"], "r531w40-msg.txt")
open(msg_path, "w", encoding="utf-8", newline="\n").write(
    "round 531: W40 FREEZE (THIRTIETH engine wave, bm-b thirteenth-owned, "
    "first-free-number after bm-c's W39 claim; A 123_004..125_003 / B 43_201..43_400 "
    "both arithmetic ZERO-SKIP, W39 row W40+ WARNING projection verified machine-side; "
    "ADMIT receipt _r531bmb_w40_band_gate.py vs 37 registered rows + N3-R1 used-seed leg "
    "+ probe-cluster leg + 161 registry values + origin slot vacancy; banned_direction_gate "
    "rc0 no-banned-direction; selftest PASS incl W40 materializer face + W40 prose; "
    "prereg anchors = W38 finalize measured [merged mu -0.091622 / sigma 0.244915 / "
    "A p95 0.3119 / K-lift -0.0001 @ n_eff 443,940]; engine IGNITION LIVE-VALIDATED "
    "per-tick module re-read zero-restart: shard-0 02:01:38 + shard-1 02:02:38 "
    "product-growth evidence) + S0 integration repair receipts (r530 leftover worktree: "
    "102-path stale-tree sweep restored from origin incl bm-a LOWAMP-P3 cells/claims "
    "+ W39 all-12 bm-c canonical; 2 stale-view duplicate claim commits dropped per "
    "r297 later-arriver yield; bm-b W39 duplicate-burn shards 0-4 discarded "
    "[audit.machine=bm-b verified]; marks family origin-newer taken; pipeline "
    "UNBLOCKED: daemon claim->burn->harvest cycle live same window) + LAEDGE "
    "LOWAMP-P3 cell product delivery (LEGACY-BASE done+harvested 01:54:03, DEEP-X2, "
    "DEEP-BASE; pool-side flipped by daemon, products committed here per r310) [bm-b]\n")
rc, sha = git("commit-tree", tree, "-p", parent, "-F", msg_path)
assert rc == 0, sha
sha = sha.strip()
print("newcommit=", sha)

# r519-family mandatory legs: deletion-set audit + payload presence audit
rc, dels = git("diff", "--name-only", "--diff-filter=D", parent, sha)
if dels.strip():
    print("DELETION DETECTED -- ABORT (r525/r519):")
    print(dels)
    sys.exit(1)
print("deletion-set empty PASS")
present = 0
for f in payload:
    rc, out = git("ls-tree", sha, "--name-only", f)
    if out.strip() == f:
        present += 1
print("payload presence in new tree:", present, "of", len(payload))
assert present == len(payload)

rc, out = git("push", "origin", f"{sha}:refs/heads/main")
print("push rc=", rc, "|", out.strip()[-200:])
if rc == 0:
    rc, out = git("update-ref", "refs/heads/main", sha, parent)
    print("local main aligned:", out.strip() or "OK")
    print("PUSHED_SHA=", sha)
else:
    print("PUSH REJECTED -- peak window; re-run this script (fetch first, blob retry cheap)")
    sys.exit(2)
