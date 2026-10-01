"""W44 freeze one-commit push (r533 bm-b). Surgical diff-based payload on
origin/main: 5 files (canon row + prereg + band gate + N1_BANDS row +
WAVE_CONFIGS/selftest face). r511 tail-lock: fetch+slot-vacancy re-check
immediately before every push attempt; r530 collision: if origin moved on
any payload file since our base -> ABORT (yield/adjudicate, never clobber).
r525/r530: deletion-set must be EMPTY; payload count == 5 (r343 --cached).
"""
import os, subprocess, time

R = os.getcwd()

def git(args, env=None, **kw):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["git"] + args, capture_output=True, env=e, **kw)

FILES = [
    "research/PERPETUAL_FACES.md",
    "research/PERPETUAL_N1_W44_PREREG.md",
    "results/_r533bmb_w44_band_gate.py",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
]
MSG = ("W44 FREEZE one-commit product (THIRTY-FOURTH wave, bm-b fourteenth-owned, "
       "first-free after bm-c W43 landed claim, zero-gap relay per de-throttle "
       "O-20261001-2355 sec.2; r532 closed the W40 full lifecycle, W41/W42 bm-c "
       "finalized, W43 bm-c burn-in-flight coexists by band disjointness r531 "
       "law): both-sides arithmetic zero-skip A 131_004..133_003 / B 44_201.."
       "44_400 == W43 row W44+ WARNING projection (machine-derived); ADMIT "
       "receipt results/_r533bmb_w44_band_gate.py leg0-leg3 + N3-R1 + "
       "probe-cluster + origin slot vacancy (42-row scan face); banned gate "
       "ADMIT; selftest PASS incl W44 materializer face (dep=W17..W42 all "
       "landed, W43 two-state in-flight FAIL-CLOSED at finalize runtime); "
       "W45+ projection both CLEAN machine-derived (A 133_004..135_003 / B "
       "44_401..44_600); K projection 94,720 / ledger prev 454,940 live head "
       "(W43 finalize pending, consumed live at finalize) [bm-b r533]")

assert git(["fetch", "origin"]).returncode == 0
new_commit = None
for attempt in range(4):
    base = git(["rev-parse", "origin/main"]).stdout.decode().strip()
    # --- collision guard (r530): origin must not have moved on payload files
    for f in FILES:
        o = git(["show", f"origin/main:{f}"]).stdout
        h = git(["show", f"HEAD:{f}"]).stdout
        if o != h and f != "research/PERPETUAL_N1_W44_PREREG.md" \
                and f != "results/_r533bmb_w44_band_gate.py":
            print(f"[ABORT] origin moved on payload file: {f} -- collision "
                  f"window, yield/adjudicate per r511/r530 (never clobber)")
            raise SystemExit(2)
    # --- slot vacancy on the fresh origin (r511 tail-lock)
    cfg = git(["show", "origin/main:scripts/perpetual_faces.py"]).stdout.decode("utf-8", "replace")
    canon = git(["show", "origin/main:research/PERPETUAL_FACES.md"]).stdout.decode("utf-8", "replace")
    assert '44: {"a": (131_004, 133_003)' not in cfg, "W44 slot TAKEN on origin (yield per r511)"
    assert "N1 波44" not in canon, "W44 canon row TAKEN on origin (yield per r511)"
    # --- build temp index from origin/main + 5-file payload
    idx = os.path.join(R, ".git", f"w44idx_{int(time.time())}")
    assert git(["read-tree", base], env={"GIT_INDEX_FILE": idx}).returncode == 0
    for f in FILES:
        h = git(["hash-object", "-w", "--", os.path.join(R, f)]).stdout.decode().strip()
        r = git(["update-index", "--add", "--cacheinfo", f"100644,{h},{f}"],
                env={"GIT_INDEX_FILE": idx})
        assert r.returncode == 0, r.stderr
    tree = git(["write-tree"], env={"GIT_INDEX_FILE": idx}).stdout.decode().strip()
    # --- assertion legs (r525/r530/r343)
    df = git(["diff", "--name-only", "--diff-filter=D", "--no-renames", base, tree]).stdout.decode().split()
    assert df == [], f"deletion-set gate FAIL: {df}"
    di = git(["diff-index", "--cached", "--name-status", "--no-renames", base],
             env={"GIT_INDEX_FILE": idx}).stdout.decode()
    changed = [l.split("\t", 1)[1].strip() for l in di.splitlines() if l.strip()]
    assert sorted(changed) == sorted(FILES), f"payload drift: {changed}"
    print(f"[assert] payload == 5 files, deletion-set empty (base {base[:10]})")
    commit = subprocess.run(
        ["git", "commit-tree", tree, "-p", base, "-m", MSG], capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "bm-b", "GIT_AUTHOR_EMAIL": "bm-b@fleet.local",
             "GIT_COMMITTER_NAME": "bm-b", "GIT_COMMITTER_EMAIL": "bm-b@fleet.local"}
    ).stdout.decode().strip()
    r = git(["push", "origin", f"{commit}:refs/heads/main"])
    if r.returncode == 0:
        new_commit = commit
        print(f"[push] PASS attempt {attempt+1} -> {commit[:10]}")
        break
    print(f"[push] rejected attempt {attempt+1}: {r.stderr.decode()[:180]}")
    git(["fetch", "origin"])

assert new_commit, "W44 freeze push failed after 4 attempts"
# --- delivery self-check (r531 mirror leg)
git(["fetch", "origin"])
head = git(["rev-parse", "origin/main"]).stdout.decode().strip()
assert head == new_commit, f"delivery mismatch {head[:10]} != {new_commit[:10]}"
for f in FILES:
    assert git(["cat-file", "-e", f"origin/main:{f}"]).returncode == 0, f"delivery missing {f}"
print("[deliver] ls-tree payload presence PASS")
# --- re-align local HEAD (reset --mixed with index.lock retry)
for i in range(10):
    r = git(["reset", "--mixed", new_commit])
    if r.returncode == 0:
        break
    time.sleep(2)
assert r.returncode == 0, f"reset failed: {r.stderr}"
st = git(["status", "--porcelain=v1", "-uno"]).stdout.decode()
dirty5 = [l for l in st.splitlines() if any(f in l for f in FILES)]
print("[post-align] payload files dirty (should be none):", dirty5 if dirty5 else "NONE-clean")
print("[W44 FREEZE PUSHED]", new_commit)
