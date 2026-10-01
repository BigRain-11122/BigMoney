# r532 bm-b surgical push: r531-crash salvage superset delivery.
# Pattern: _r531bmb_push_w40.py (r530/r512/r519 net path family).
# Why surgical not rebase: nulls.jsonl burn ACTIVE (runner appends ~0.4s)
# -> tracked-file continuous growth = rebase structurally refused (r523).
# Payload: W40 12/12 products (first delivery, r310) + nulls checkpoint +
# bm-b lane files + pool_core_samples UNION (r524/r314) + r531 tools.
# Skipped: 20 shared same-day regen faces -> origin side kept (r505 newer-wall-
# clock law); my S6 chain re-derives them this round on fresh base.
import subprocess, os, sys

R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(R)

def git(*a, **kw):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

# fresh parent per r531-III law (origin moves every ~60s in fleet window)
rc, out = git("fetch", "origin")
if rc != 0:
    print("fetch failed (non-fatal, using last known):", out.strip()[-120:])
rc, parent = git("rev-parse", "origin/main")
assert rc == 0, parent
parent = parent.strip()
print("parent=", parent)

A_FILES = [
    "results/_r530bmb_close.ps1",
    "results/_r531bmb_inspect.py",
    "results/_r531bmb_inspect2.py",
    "results/_r531bmb_inspect3.py",
    "results/_r531bmb_push_w40.py",
    "results/_r532bmb_s0_surgical.py",
    "results/lowamp_p3/nulls.jsonl",
] + [f"results/p2cal_ext/n1_w40/shard-{i}-of-12.json" for i in range(12)]
LANE_FILES = [
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/futures_update_status.bm-b.json",
    "results/lhb_update_status.bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/token_usage.bm-b.json",
    "results/update_status.bm-b.json",
]
UNION_FILE = "results/pool_core_samples.jsonl"
# live-writer files NEVER touched by post-push local alignment checkout
LIVE_FILES = {
    "results/lowamp_p3/nulls.jsonl",          # runner appends continuously
    "results/saturation_engine/state_bm-b.json",  # engine 60s tick buffer
    "results/autofill_state.bm-b.json",       # daemon tick rewrite
}

idx = os.path.join(os.environ["TEMP"], "fg-r532surg-idx")
if os.path.exists(idx):
    os.remove(idx)
env = dict(os.environ, GIT_INDEX_FILE=idx)
rc, out = git("read-tree", parent)
assert rc == 0, out

staged = 0
for f in A_FILES + LANE_FILES:
    if not os.path.exists(f):
        print("MISSING", f, "-- ABORT (payload integrity)")
        sys.exit(1)
    rc, out = git("hash-object", "-w", f)
    assert rc == 0, out
    blob = out.strip()
    rc, out = git("update-index", "--add", "--cacheinfo", f"100644,{blob},{f}")
    assert rc == 0, out
    staged += 1
print("staged plain payload:", staged)

# union leg (r524/r314): origin lines + mine-unique, EOF-append convention
org = subprocess.check_output(
    ["git", "show", f"{parent}:{UNION_FILE}"]).decode("utf-8").splitlines()
mine = open(UNION_FILE, encoding="utf-8").read().splitlines()
org_set = set(org)
extra = [l for l in mine if l not in org_set]
union = org + extra
print(f"union: origin={len(org)} + mine-unique={len(extra)} = {len(union)}")
assert len(union) == len(org) + len(extra)
assert len(set(union)) == len(union), "union dedupe failed"
tmp = os.path.join(os.environ["TEMP"], "fg-r532-pcs-union.jsonl")
open(tmp, "w", encoding="utf-8", newline="").write("\n".join(union) + "\n")
rc, out = git("hash-object", "-w", tmp)
assert rc == 0, out
rc, out = git("update-index", "--add", "--cacheinfo",
              f"100644,{out.strip()},{UNION_FILE}")
assert rc == 0, out
staged += 1
payload = A_FILES + LANE_FILES + [UNION_FILE]
print("total staged:", staged, "of", len(payload))
assert staged == len(payload)

rc, tree = git("write-tree")
assert rc == 0, tree
tree = tree.strip()

msg_path = os.path.join(os.environ["TEMP"], "r532surg-msg.txt")
open(msg_path, "w", encoding="utf-8", newline="\n").write(
    "round 532 S0 surgical: r531-crash salvage superset (r471/r529 recovery; "
    "state round_no stuck 530 vs git self-label r531 = session died post-commit "
    "pre-S5/S6/S7) -- W40 12/12 engine products FIRST delivery to origin (r310; "
    "sole-copy rescue, audit.machine=bm-b verified, ledger 10 rows + 2 in "
    "state-buffer orphan-reconciled per r522 face, flush due 10-20min window) + "
    "LOWAMP-P3-NULLS in-flight checkpoint nulls.jsonl partial snapshot (burn "
    "ACTIVE pid36968 since 01:58:25 ~2.7 rows/s, K=2000, ETA ~02:28; pool entry "
    "stays ready, NO flip -- runner has r497 claim handshake, fires at "
    "completion) + bm-b lane superset (r523: engine face/history/ledger/state, "
    "autofill, dualrun, token, marks lane views) + pool_core_samples UNION "
    "(origin 470 + mine-unique 16 = 486; bm-a W40 cross-burn records preserved "
    "-- r530 deterministic-band collision family, byte-identical products, "
    "bm-a fixup ac9c9bad8 already yielded canon to bm-b r531) + 20 shared "
    "same-day regen faces yielded to origin side (r505 newer-wall-clock law; "
    "this round S6 re-derives on fresh base) [bm-b]\n")
rc, sha = git("commit-tree", tree, "-p", parent, "-F", msg_path)
assert rc == 0, sha
sha = sha.strip()
print("newcommit=", sha)

# r519-family mandatory legs
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
print("payload presence:", present, "of", len(payload))
assert present == len(payload)
# payload-count audit: changed-file set == payload set exactly
rc, changed = git("diff", "--name-only", parent, sha)
chg = set(x for x in changed.strip().splitlines() if x)
assert chg == set(payload), ("EXTRA CHANGES", sorted(chg - set(payload)))
print("payload-count audit PASS (changed==payload)")

rc, out = git("push", "origin", f"{sha}:refs/heads/main")
print("push rc=", rc, "|", out.strip()[-160:])
if rc != 0:
    print("PUSH REJECTED -- fleet peak window; re-run this script (r512 cheap retry)")
    sys.exit(2)

# delivery self-verify (O-20261001-1108: push+fetch+ls-tree)
rc, out = git("fetch", "origin")
rc, out = git("rev-parse", "origin/main")
assert out.strip() == sha, ("origin/main not at sha", out.strip(), sha)
print("delivery self-verify PASS origin/main==sha")

# local alignment: move main, reset index, checkout origin-owned stale faces
# EXCEPT live-writer files (r314-V race law: never revert in-flight writers)
rc, out = git("update-ref", "refs/heads/main", sha)
assert rc == 0, out
rc, out = git("reset", "--mixed", "HEAD")
assert rc == 0, out
rc, out = git("status", "--porcelain")
lines = [l for l in out.strip().splitlines() if l]
checkout_n = 0
skipped_live = []
for l in lines:
    st, _, path = l.partition(" ")  # e.g. " M path" / " D path" / "?? path"
    path = path.strip()
    if st.endswith("?") or not path:
        continue
    if path in LIVE_FILES:
        skipped_live.append(path)
        continue
    rc, out = git("checkout", "--", path)
    if rc != 0:
        print("checkout FAIL:", path, out.strip()[-100:])
        sys.exit(1)
    checkout_n += 1
print(f"local alignment: checked-out {checkout_n} stale faces; "
      f"live-writer left dirty: {skipped_live}")
rc, out = git("status", "--porcelain")
print("post-align status:")
print(out.strip() or "(clean)")
print("PUSHED_SHA=", sha)
