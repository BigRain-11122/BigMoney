"""r583 bm-a post-surgery local alignment (r578 law): reset --mixed to the
surgical commit, then checkout the incoming diff files EXCEPT this machine's
live-writer faces (daemon-owned, re-derived by S6 or committed at wrap)."""
import subprocess, os

NO_WINDOW = 0x08000000

def git(args, timeout=120):
    return subprocess.run(["git"] + args, capture_output=True, timeout=timeout, creationflags=NO_WINDOW)

def out(r):
    return r.stdout.decode("utf-8", errors="replace").strip()

# live-writer faces owned by bm-a daemons: NEVER checkout over these
LIVE = {
    "results/autofill_state.bm-a.json",
    "results/saturation_engine/state_bm-a.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/ledger_bm-a.jsonl",
    "results/saturation_engine/face_bm-a.json",
    "results/pool_dualrun.bm-a.jsonl",
    "results/token_usage.bm-a.json",
    "results/compute_audit.bm-a.json",
    "results/regime_state.bm-a.json",
    "results/dispatcher_state.bm-a.json",
    "results/watermark.jsonl",
    "state-bm-a.json",
    "round_reports-bm-a.md",
    "fleet/machines/bm-a.json",
}

r = git(["fetch", "origin"])
assert r.returncode == 0
tip = out(git(["rev-parse", "origin/main"]))
print("origin/main:", tip)

r = git(["reset", "--mixed", tip])
assert r.returncode == 0, out(r)

old = "f56d61b65dfabd9cd015bbfe9dc56ca3a9958946"
r = git(["diff", "--name-only", old, tip])
files = [l.strip() for l in out(r).splitlines() if l.strip()]
todo = [f for f in files if f not in LIVE]
print("incoming files:", len(files), "checkout targets:", len(todo))

# restore new/changed files from index (skip missing-in-index guards)
restored = 0
for f in todo:
    rr = git(["checkout", "--", f])
    if rr.returncode == 0:
        restored += 1
    else:
        print("SKIP (not in index):", f, out(rr)[:80])
print("restored:", restored)

# finalize-critical verification: live ledger head must include W95 block
import sys, json
sys.path.insert(0, ".")
import scripts.science_gates as sg
head = sg.ledger_head()
print("live ledger head total:", head.get("total"), "file:", head.get("file"))
assert head.get("total") == 573548, "chain head mismatch: %r" % head.get("total")

# sanity: W99 faces present (bm-c freeze)
for p in ("research/PERPETUAL_N1_W99_PREREG.md",):
    print(p, "exists:", os.path.exists(p))
print("ALIGNMENT OK")
