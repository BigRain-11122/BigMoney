# r594 bm-b S0 pure-FF integration driver (bm-a 3000e02a0 landed mid-round).
# Laws applied: r585/r589 pure-FF with dirty tree (no rebase, live writers);
# bm-a r593 new pit law -- reset target rev-parse'd AT EXECUTION TIME;
# r580 python subprocess argv for batch git path ops (PS array = silent no-op);
# r381 twin-yield -- origin verbatim for host/superseded derive faces;
# keep: product increment (scripts/daily_report.py + REPORT superset w/
# engine-wave face) + own-machine lane faces (.bm-b) + new round files.
import subprocess
import sys

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

# 1) execution-time rev-parse of the integration target (never a cached sha)
rc, target, err = git("rev-parse", "origin/main")
target = target.strip()
if rc != 0 or len(target) != 40:
    print("FATAL rev-parse origin/main:", rc, target, err)
    sys.exit(1)
rc, head, _ = git("rev-parse", "HEAD")
head = head.strip()
rc2, parent, _ = git("rev-parse", "origin/main~1")
parent = parent.strip()
print("target=%s head=%s parent-of-target=%s head-is-parent:%s"
      % (target[:9], head[:9], parent[:9], head == parent))
if head != parent:
    print("FATAL: local HEAD is not the direct parent of origin/main -- "
          "not a pure-FF window, abort for manual adjudication")
    sys.exit(1)
# 2) reset --mixed to execution-time target (index/HEAD move, tree kept)
rc, out, err = git("reset", "--mixed", target)
print("reset --mixed rc=%d" % rc)
if rc != 0:
    print(err)
    sys.exit(1)
# 3) origin-canonical faces: checkout from new HEAD (host bm-a fresher writes
#    supersede my stale-takeover re-derives; deterministic same-day faces)
TAKE_ORIGIN = [
    "CODELY.md",
    "docs/live_usage/LIVE-2026-10-02.json",
    "docs/live_usage/LIVE-2026-10-02.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
]
rc, out, err = git("checkout", "--", *TAKE_ORIGIN)
print("checkout %d files rc=%d" % (len(TAKE_ORIGIN), rc))
if rc != 0:
    print(err)
    sys.exit(1)
# 4) remaining status = kept local faces (verify no stray origin-only files
#    show as deleted: working tree must be a superset of the new HEAD).
#    r594 claw catch: BOTH prefixes -- staged deletions ("D ") AND worktree
#    deletions (" D"): origin-tree adds never materialized on local disk
#    read as " D" and a later git add -A stages them as deletions; checking
#    only "D " was a false green (pre-push claw stopped it, zero loss).
rc, out, _ = git("status", "--porcelain")
dels = [l for l in out.splitlines() if l.startswith("D ") or l.startswith(" D")]
print("post-integration status lines=%d deletions=%d"
      % (len(out.splitlines()), len(dels)))
if dels:
    print("DELETION LINES (abort review):", dels[:10])
    sys.exit(1)
print("INTEGRATE_OK")
