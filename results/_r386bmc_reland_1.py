# -*- coding: utf-8 -*-
# r386 bm-c push-rejection handling: unwind-FF-reland loop (r589/r595 law).
# Local r386 commit unpushed + origin advanced 2 (bm-a f54b87cef + bm-b e3b3f8d9b).
# Shared-face conflicts make rebase dirty -> unwind commit, FF to origin, per-face
# curation (union for append-only books, origin-verbatim for foreign/shared regen
# faces, keep mine for bm-c-owned), amend books with bm-b T-147 handover facts,
# re-commit, push.
import subprocess, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NW = 0x08000000

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=NW)
    if check and r.returncode != 0:
        print("GIT-FAIL", args, r.returncode, r.stdout[-400:], r.stderr[-400:])
        sys.exit(1)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# ---- 1. unwind: reset --mixed HEAD~1 (files stay in worktree) ----
rc, mine_sha, _ = git(["rev-parse", "HEAD"])
git(["reset", "--mixed", "HEAD~1"])
rc, base, _ = git(["rev-parse", "HEAD"])
print("UNWOUND", mine_sha, "-> base", base)

# ---- 2. execution-time FF to origin/main (r593 law) ----
git(["fetch", "origin"])
rc, new, _ = git(["rev-parse", "origin/main"])
rc, o1, _ = git(["merge", "--ff-only", "origin/main"])
print("FF to", new, "rc", rc, o1[:80])
rc, head, _ = git(["rev-parse", "HEAD"])
assert head == new, (head, new)

# ---- 3. status-based curation ----
rc, st, _ = git(["status", "--porcelain"])
lines = [l for l in st.splitlines() if l.strip()]
# NOTE: do NOT whole-strip (r380); parse per line, first char may be space
def split_stat(l):
    code = l[:2]
    path = l[3:]
    return code, path
d_faces = []
m_faces = []
untracked = []
for l in lines:
    code, path = split_stat(l)
    if code.strip() == "??":
        untracked.append(path)
    elif "D" in code:
        d_faces.append(path)
    else:
        m_faces.append(path)
print("D", len(d_faces), "M", len(m_faces), "??", len(untracked))
for p in d_faces:
    print("  D-FACE", p)

# D faces = origin-new files missing on disk (post-FF artifacts) -> restore (E-08)
if d_faces:
    rc, o, e = git(["restore", "--"] + d_faces, check=False)
    print("restore D rc", rc, e[:200])
    if rc != 0:
        sys.exit(3)

# foreign/shared regen faces -> origin-verbatim; bm-c-owned -> keep mine
SHARED_ORIGIN = [
    "docs/daily_report/REPORT-2026-10-02.json", "docs/daily_report/REPORT-2026-10-02.md",
    "docs/live_usage/LIVE-2026-10-02.json", "docs/live_usage/LIVE-2026-10-02.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/update_status.json",
    "results/regime_state.json", "results/token_usage.json", "results/compute_audit.json",
    "results/lhb_update_status.json", "results/futures_update_status.json",
    "results/fund_premium_status.json", "results/fundamental_b_layer_filter.json",
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/p1d_gates.json", "results/market_regime_state.json",
    "results/minute_feed_status.json", "results/etf_daily_pull_status.json",
    "results/astock_daily_update_status.json", "results/autofill_state.bm-b.json",
    "fleet/machines/bm-a.json", "fleet/machines/bm-b.json",
    "fleet/tasks/T-2026-10-02-146-P1.json", "fleet/tasks/T-2026-10-02-145-P1.json",
    "logs/iteration-loop/round_reports.md", "state.json",
    "knowledge/METHODOLOGY_ASSETS.md",  # union handled below (restore first, then union)
    "CODELY.md",                        # union handled below
    "fleet/tasks/T-2026-10-02-147-P1.json",  # json-merge below
]
# market_clock regen files (CALL-2026-09-30 + call_latest) -> origin
MC = []
for p in m_faces:
    if p.startswith("results/market_clock/"):
        MC.append(p)
restore_set = [p for p in SHARED_ORIGIN if p in m_faces] + MC
if restore_set:
    rc, o, e = git(["restore", "--"] + restore_set, check=False)
    print("restore shared rc", rc, e[:200])
    if rc != 0:
        sys.exit(3)
print("restored shared faces:", len(restore_set))
rem_m = []
rc, st2, _ = git(["status", "--porcelain"])
for l in [x for x in st2.splitlines() if x.strip()]:
    code, path = split_stat(l)
    if "D" in code:
        print("  STILL-D", path)
    elif code.strip() != "??":
        rem_m.append(path)
print("remaining M faces (bm-c-owned, keep mine):")
for p in rem_m:
    print("  M", p)
rc, st3, _ = git(["status", "--porcelain"])
assert not any("D" in l[:2] for l in st3.splitlines() if l.strip()), "D faces must be zero (E-08)"
print("D-FACE COUNT ZERO OK")
