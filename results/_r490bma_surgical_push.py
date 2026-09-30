# r490 bm-a surgical push: deliver stranded r487-489 lane content + r490 outputs to origin/main
# via temporary-index commit on top of origin/main (GM 19:01 canonical recipe, ahead>0 extension).
# Zero working-tree touch, zero stash, zero rebase, zero GM-session-file contact.
# Lane-file-ONLY file list: 30 intersection shared faces deliberately EXCLUDED (remote newer versions stand).
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def git(*args, env=None, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit(f"[surgical] GIT FAIL {args}: {r.stderr.strip()[:500]}")
    return r.stdout.strip()

# Intended delivery: bm-a lane files + critical stranded artifacts ONLY.
LANE_FILES = [
    "Tools/autofill.py",                      # r487 O-1858 fullburn window wiring (fleet-visible on main)
    "fleet/inbox/MSG-20260930-2108-bma-bmc-d41-berth-zero-collision.md",  # r489 berth reply (bm-c consumption path)
    "fleet/machines/bm-a.json",               # heartbeat (epoch int)
    "round_reports-bm-a.md",                  # r487-490 lines
    "state-bm-a.json",                        # round_no 490
    "research/HANDOVER.md",                  # r490 5x entry
    "results/pool_dualrun.bm-a.jsonl",
    "results/token_usage.bm-a.json",
    "results/autofill_state.bm-a.json",
    "results/compute_audit.bm-a.json",
    "results/regime_state.bm-a.json",
    "results/update_status.bm-a.json",
    "results/heat_update_status.bm-a.json",
    "results/lhb_update_status.bm-a.json",
    "results/futures_update_status.bm-a.json",
    "results/ah_panel_status.json",           # bm-a lane (R31)
    "results/moneyflow_update_status.json",  # bm-a lane (R31)
    "results/options_update_status.json",    # bm-a lane (R31)
    "results/repo_update_status.json",       # bm-a lane (T-88)
    "results/sina_mf_update_status.json",     # bm-a lane (T-72)
    "results/_r489bma_s6.txt",
    "results/_r489bma_swallow_fix.py",
    "results/_r490bma_closeout.py",
    "results/_r490bma_surgical_push.py",     # self-evidence
]

# Hard guard: never touch concurrent-session in-flight files or shared intersection faces
FORBIDDEN = {"CODELY.md", "Money02/CODELY.md", "research/PREREG_TEMPLATE.md", "research/BANNED_DIRECTIONS.json"}
for f in LANE_FILES:
    assert f not in FORBIDDEN, f"forbidden file in list: {f}"
    assert os.path.exists(f), f"missing working-tree file: {f}"

git("fetch", "origin")
origin_main = git("rev-parse", "origin/main")
parent_count_behind = int(git("rev-list", "--count", f"HEAD..{origin_main}"))
print(f"[surgical] parent=origin/main {origin_main[:9]} (behind {parent_count_behind})")

# Temporary index: never touches .git/index (concurrent-session-safe)
tmp_index = os.path.join(ROOT, ".git", "tmpidx_r490")
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
git("read-tree", origin_main, env=env)
for f in LANE_FILES:
    git("update-index", "--add", "--replace", f, env=env)  # hashes working-tree content into temp index
tree = git("write-tree", env=env)
print(f"[surgical] tree={tree}")

msg_path = os.path.join(ROOT, ".git", "R490_SURGICAL_MSG.txt")
with open(msg_path, "w", encoding="utf-8", newline="\n") as mf:
    mf.write(
        "round 490 surgical lane-delivery: stranded r487-489 content pushed to main (temp-index path, ahead=3 window)\n\n"
        "- Tools/autofill.py: O-1858 sec.1 holiday fullburn window wiring (r487, date-based 10-01..re-open-10-09, "
        "launch nice NORMAL in-window, fullburn_window launch record, selftest S21 x3) now fleet-visible on main\n"
        "- MSG-20260930-2108 bma->bmc: D-41 #1 berth zero-collision reply (r489, was stranded on machine branch)\n"
        "- bm-a lane ledgers/evidence r487-490: round_reports-bm-a.md, state-bm-a.json (round_no 490), heartbeat, "
        "pool_dualrun.bm-a.jsonl, *_status.bm-a.json, HANDOVER r490 5x entry\n"
        "- 30 intersection shared faces deliberately zero-touch (remote newer versions stand; local regen faces "
        "reconcile at next full-sync window)\n"
        "- concurrent-session in-flight files (CODELY.md / Money02/CODELY.md / PREREG_TEMPLATE staged / "
        "BANNED_DIRECTIONS untracked) untouched; zero stash, zero rebase, zero working-tree contact [via bm-a]"
    )
commit = git("commit-tree", tree, "-p", origin_main, "-F", msg_path)
print(f"[surgical] commit={commit}")

# Verify: diff of surgical commit vs origin/main must ONLY touch intended lane files
changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", origin_main, commit).splitlines()
unexpected = [c for c in changed if c not in LANE_FILES]
assert not unexpected, f"UNEXPECTED files in surgical diff: {unexpected}"
missing = [f for f in LANE_FILES if f not in changed]
print(f"[surgical] diff file count={len(changed)} (intended subset; identical-to-origin skipped: {len(missing)})")

r = subprocess.run(["git", "push", "origin", f"{commit}:refs/heads/main"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode != 0:
    print(f"[surgical] PUSH REJECTED (origin moved?): {r.stderr.strip()[:300]}")
    print("[surgical] one retry with fresh fetch follows")
    git("fetch", "origin")
    origin_main2 = git("rev-parse", "origin/main")
    if origin_main2 == origin_main:
        sys.exit(f"[surgical] push failed but origin unchanged -- abort, investigate: {r.stderr[:300]}")
    commit2 = git("commit-tree", tree, "-p", origin_main2, "-F", msg_path)
    r2 = subprocess.run(["git", "push", "origin", f"{commit2}:refs/heads/main"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r2.returncode != 0:
        sys.exit(f"[surgical] RETRY PUSH FAIL: {r2.stderr[:300]}")
    commit = commit2
    print(f"[surgical] retry push landed commit={commit[:9]}")
print(f"[surgical] PUSH LANDED {commit[:9]} -> origin/main")
print(f"[surgical] rc=0 files={len(changed)} parent={origin_main[:9]}")
