# -*- coding: utf-8 -*-
# r997 own-face surgery push on fresh origin tip (r982/r983 bloodline: explicit-faces-only)
import subprocess, sys, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
IDX = os.path.join(ROOT, ".git", "tmp_index_r997")

ADD_FACES = [
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "fleet/inbox/MSG-20261017-2356-bmb-dramaredrop.md",
    "fleet/inbox/processed/MSG-20261017-2203-bm-b-drama-taildrop-pickup.md",
    "fleet/inbox/processed/MSG-20261017-2216-bma-uuremote.md",
    "results/_orphan_face_probe.bm-b.json",
    "results/_r686bmb_d19_check.json",
    "results/_r686bmb_orders_fresh.md",
    "results/astock_daily_update_status.json",
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/etf_daily_pull_status.json",
    "results/futures_update_status.bm-b.json",
    "results/idle_trigger.bm-b.json",
    "results/idle_trigger_state.bm-b.json",
    "results/lhb_update_status.bm-b.json",
    "results/orders_ack_scan.bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/token_usage.bm-b.json",
    "results/update_status.bm-b.json",
    "results/d19_watermark.json",
    "results/watermark_red.json",
    "_r996bmb_closeout.py",
    "_r996bmb_s6chain.ps1",
    "_r997bmb_closeout.py",
    "results/_r995bmb_ep_speakers.txt",
    "results/_r996bmb_s6_log.txt",
]
REMOVE_FACES = [
    "fleet/inbox/MSG-20261017-2216-bma-uuremote.md",  # moved to processed/ this round
]

def run(args, env_extra=None, input_bytes=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([GIT] + args, cwd=ROOT, env=env, capture_output=True, input=input_bytes)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

# 0. safety: origin last toucher of round_reports.md must not be foreign
rc, out, err = run(["log", "origin/main", "--oneline", "-2", "--", "logs/iteration-loop/round_reports.md"])
print("round_reports last touchers:", out.strip())
rc, out, err = run(["fetch", "origin"])
if rc != 0:
    print("FETCH_FAIL", err[:400]); sys.exit(2)
rc, tip, err = run(["rev-parse", "origin/main"])
tip = tip.strip()
print("origin tip:", tip)

# 1. fresh temp index from origin tip
if os.path.exists(IDX):
    os.remove(IDX)
env_idx = {"GIT_INDEX_FILE": IDX}
rc, out, err = run(["read-tree", tip], env_extra=env_idx)
if rc != 0:
    print("READ_TREE_FAIL", err[:400]); sys.exit(2)

# 2. add own faces (disk content wins for own faces)
for face in ADD_FACES:
    p = os.path.join(ROOT, face.replace("/", os.sep))
    if not os.path.exists(p):
        print("MISSING_FACE", face); sys.exit(3)
    rc, sha, err = run(["hash-object", "-w", p])
    if rc != 0 or len(sha.strip()) != 40:
        print("HASH_FAIL", face, err[:200]); sys.exit(4)
    rc, out, err = run(["update-index", "--add", "--cacheinfo", "100644," + sha.strip() + "," + face], env_extra=env_idx)
    if rc != 0:
        print("UPDATE_INDEX_FAIL", face, err[:200]); sys.exit(5)
print("added faces:", len(ADD_FACES))

# 3. remove moved-away inbox path
for face in REMOVE_FACES:
    rc, out, err = run(["update-index", "--force-remove", face], env_extra=env_idx)
    if rc != 0:
        print("REMOVE_FAIL", face, err[:200]); sys.exit(6)
print("removed faces:", len(REMOVE_FACES))

# 4. write tree + commit on origin tip
rc, tree, err = run(["write-tree"], env_extra=env_idx)
tree = tree.strip()
if rc != 0 or len(tree) != 40:
    print("WRITE_TREE_FAIL", tree, err[:400]); sys.exit(7)
msg = ("round r997: drama pilot 5-file taildrop re-queue delivered (tx +18.6MB byte-verified, MSG-2356) + "
       "dead r995/r996 estate absorbed (S6 43-leg rc0 + d19 orders->0b991d78 advance) + O-2207 ack + "
       "IndexTTS lane yielded to live interactive window + smoke 49/49 + S7 green")
msg_file = os.path.join(ROOT, "_r997bmb_commitmsg.txt")
with open(msg_file, "w", encoding="utf-8", newline="") as f:
    f.write(msg)
rc, commit, err = run(["commit-tree", tree, "-p", tip, "-F", "_r997bmb_commitmsg.txt"])
commit = commit.strip()
if rc != 0 or len(commit) != 40:
    print("COMMIT_TREE_FAIL", commit, err[:400]); sys.exit(8)
print("commit:", commit)

# 5. push (non-ff safety: parent is origin tip)
rc, out, err = run(["push", "origin", commit + ":refs/heads/main"])
print("push rc:", rc)
print(out[-300:] if out else "", err[-400:] if err else "")
if rc != 0:
    print("PUSH_FAIL"); sys.exit(9)

# 6. verify by sha change (bm-b r985 law: never trust substring match)
rc, remote, err = run(["ls-remote", "origin", "refs/heads/main"])
remote_sha = remote.split()[0] if remote else ""
if remote_sha == commit:
    print("PUSH_VERIFIED:", remote_sha)
else:
    print("PUSH_MISMATCH remote=", remote_sha, "local=", commit); sys.exit(10)
