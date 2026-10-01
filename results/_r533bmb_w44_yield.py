"""W44 yield + re-align (r511 five-step + r518 pits; r530 identical-bands law:
later committer yields, cost=zero since no finalize). Steps:
  1. discard local W44 products (engine self-ignited from worktree draft;
     byte-identical science payload to bm-a 48a552d42, audit face differs)
  2. move my W44 prereg draft aside (path collides with bm-a's tracked canonical)
  3. fetch + reset --mixed origin/main + restore pass (checkout origin-owned
     faces; discards my uncommitted W44 canon/config edits = yield step-2
     take-origin; keeps nulls.jsonl + bm-b lane files)
"""
import glob, os, shutil, subprocess, time

def git(args):
    return subprocess.run(["git"] + args, capture_output=True)

# --- 1. discard local W44 products (yield step-3: self-burned shards discarded)
n = 0
for p in glob.glob("results/p2cal_ext/n1_w44/*.json"):
    os.remove(p)
    n += 1
print(f"[yield-3] local n1_w44 products discarded: {n}")
shutil.rmtree("results/p2cal_ext/n1_w44", ignore_errors=True)

# --- 2. move my W44 prereg draft aside (untracked-at-tracked-path collision)
src = "research/PERPETUAL_N1_W44_PREREG.md"
dst = "results/_r533bmb_w44_yielded_prereg_draft.md"
if os.path.exists(src) and not os.path.exists(dst):
    os.rename(src, dst)
    print("[yield-2] prereg draft moved aside ->", dst)
assert not os.path.exists(src), "draft still collides with bm-a canonical path"

# --- 3. re-align
assert git(["fetch", "origin"]).returncode == 0
head = git(["rev-parse", "origin/main"]).stdout.decode().strip()
for i in range(10):
    r = git(["reset", "--mixed", head])
    if r.returncode == 0:
        break
    time.sleep(2)
assert r.returncode == 0, r.stderr
print("[align] HEAD ->", head[:10])

# restore pass: all D/M tracked faces except bm-b lane + nulls.jsonl
st = git(["status", "--porcelain=v1", "-uno"]).stdout.decode()
KEEP = ("results/lowamp_p3/nulls.jsonl", "results/autofill_state.bm-b.json",
        "results/saturation_engine/face_bm-b.json",
        "results/saturation_engine/history_bm-b.jsonl",
        "results/saturation_engine/state_bm-b.json",
        "results/saturation_engine/ledger_bm-b.jsonl")
done = 0
for l in st.splitlines():
    if not l.strip():
        continue
    code, p = l[:2], l[3:].strip().strip('"')
    if p in KEEP or code.strip() not in ("D", "M"):
        continue
    if git(["cat-file", "-e", "HEAD:" + p]).returncode != 0:
        print("[restore SKIP] not in HEAD:", p)
        continue
    if git(["checkout", "HEAD", "--", p]).returncode == 0:
        done += 1
    else:
        print("[restore FAIL]", p)
print(f"[restore] {done} origin-owned faces restored")

# W44 yield verification: canon/config must now be bm-a's (engine_owner=bm-a)
cfg = open("scripts/perpetual_faces.py", encoding="utf-8").read()
assert '44: {"a": (131_004, 133_003), "b_exit": (44_201, 44_400),\n         "engine_owner": "bm-a"}' in cfg, \
    "yield failed: W44 config not bm-a-owned after restore"
canon = open("research/PERPETUAL_FACES.md", encoding="utf-8").read()
assert "N1 波44" in canon and "bm-a" in canon.split("N1 波44")[1][:200], "yield failed: canon W44 row not bm-a"
st2 = git(["status", "--porcelain=v1", "-uno"]).stdout.decode()
print("--- post-yield status ---")
print(st2 if st2.strip() else "(clean)")
