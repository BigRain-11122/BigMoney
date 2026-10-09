# -*- coding: utf-8 -*-
"""r815 bm-c S0 (1-gen clone of _r814bmc_s0.py canon, r814 delta kept):
r814/r811 law: after fetch run `git rebase origin/main` DIRECTLY (no
pull --rebase) -- pull re-fetches inside the CRLF fake-dirty window and a
live daemon can rewrite a face between fetch and rebase, causing the
double-reject loop; on unstaged-changes rejection, normalize the drift
faces (git checkout -- <M faces>) and retry rebase once.
1) wall-clock stamp; 2) sequencer-state check (r868 half-open rebase law);
3) git status -> classify dirty faces (own daemon live-face = targeted
add+commit; foreign half-done faces = skip commit, report); 4) fetch
origin (SSH primary; HTTPS explicit-URL fallback WITHOUT touching remote
config) + rebase origin/main + one-shot drift-normalize retry; 5) absorb/
rebase summary + UU faces if any. Every git leg carries a 75s timeout
jacket (r807 s05 jacket law family). CREATE_NO_WINDOW per U060 silence
law. Scratch msg file committed same-window (r811 CRLF fake-dirty loop
law ①)."""
import os
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "_r_bmc_s0msg.txt")
HTTPS_URL = "https://github.com/BigRain-11122/BigMoney.git"

OWN_PATTERNS = (
    "_r_bmc_s0msg.txt",
    "state-bm-c.json", "fleet/machines/bm-c.json", "fleet/machines/bm-a.json",
    "fleet/machines/bm-b.json", "results/crash_fuse.json",
    "results/runnable_pool.json", "results/saturation", "results/idle_trigger",
    "results/autofill_state", "results/dispatcher_state",
    "Tools/_r807bmc", "Tools/_r808bmc", "Tools/_r809bmc", "Tools/_r810bmc",
    "Tools/_r811bmc", "Tools/_r812bmc", "Tools/_r813bmc", "Tools/_r814bmc",
    "Tools/_r815bmc",
    "results/_orphan_face_probe", "logs/autofill_", "logs/dispatcher_",
    "results/watermark_red.json", "results/marks", "results/watermark.jsonl",
    "results/_r806bmc", "results/_r807bmc", "results/_r808bmc",
    "results/_r809bmc", "results/_r810bmc", "results/_r811bmc",
    "results/_r812bmc", "results/_r813bmc", "results/_r814bmc",
    "results/_r815bmc",
    "results/_attrition_guard_scan",
    "results/pool_dualrun", "results/regime_state.json",
    "results/compute_audit", "results/market_clock", "results/token_usage.json",
    "results/prospect_g2", "results/rev_osc_live", "results/aggr_paper",
    "results/alloc_paper", "results/grid_paper", "results/paper_export",
    "results/system_v1_paper", "results/cta_p1_paper", "results/strategy_scorecard",
    "results/scorecard_v1", "docs/daily_report/REPORT-2026", "docs/live_usage/LIVE-2026",
    "results/daily_scorecard", "results/dashboard_status", "monitor/dashboard",
    "results/fund_premium", "results/lhb_status", "results/zt_pool_status",
    "results/futures_status", "results/repo_panel", "results/options_status",
    "results/moneyflow_status", "results/sina_mf_status", "results/astock_daily_status",
    "results/etf_daily_status", "results/minute_feed_status", "results/ths_status",
    "results/ah_status", "results/fund_statement_status", "results/daily_panel",
    "data/", "results/science_audit", "results/self_review", "results/briefings",
    "results/_quarantine",
)


def git(args, timeout=75):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREATE, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "leg timeout after %ss" % timeout


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    print("NOW=%s" % now.isoformat())
    for sq in ("rebase-merge", "rebase-apply"):
        p = os.path.join(ROOT, ".git", sq)
        print("SEQ:%s=%s" % (sq, "OPEN" if os.path.isdir(p) else "closed"))
    rc, st, _ = git(["status", "--porcelain"])
    lines = [l for l in st.splitlines() if l.strip()]
    print("DIRTY_N=%d" % len(lines))
    own, foreign = [], []
    for l in lines:
        path = l[3:].strip().strip('"')
        if any(p in path for p in OWN_PATTERNS):
            own.append(path)
        else:
            foreign.append(path)
    for l in lines[:20]:
        print("  " + l)
    if len(lines) > 20:
        print("  ...(+%d more)" % (len(lines) - 20))
    if foreign:
        print("FOREIGN_FACES (no add):")
        for p in foreign:
            print("  " + p)
    if not own and not foreign:
        print("CLEAN-TREE no absorb needed")
    elif own:
        args = ["add", "--"]
        args += own
        rc, out, err = git(args)
        print("ADD-OWN rc=%d %s" % (rc, (err or out).strip()[:200]))
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 815 S0: absorb own daemon live faces (%d files)\n"
                    % len(own))
        rc, out, err = git(["commit", "-F", MSG])
        if rc == 0:
            rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
            print("ABSORB-COMMIT %s" % head.strip())
        else:
            print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:300]))
    rc, out, err = git(["fetch", "origin"])
    print("FETCH-SSH rc=%d %s" % (rc, (err or out).strip()[:150]))
    if rc != 0:
        rc, out, err = git(["fetch", HTTPS_URL, "main"])
        print("FETCH-HTTPS rc=%d %s" % (rc, (err or out).strip()[:150]))
    # r814 law: rebase directly, no pull (shrink the CRLF fake-dirty window)
    rc, out, err = git(["rebase", "origin/main"])
    tail = (err or out).strip()
    print("REBASE rc=%d %s" % (rc, tail[-400:] if tail else "up-to-date"))
    if rc != 0:
        # drift-normalize leg: CRLF/daemon-rewrite faces -> checkout, retry once
        rc2, st2, _ = git(["status", "--porcelain"])
        drift = [l[3:].strip().strip('"') for l in st2.splitlines()
                 if l.strip() and l[:2] in (" M", "MM", " M", "MT")]
        if drift:
            rc3, o3, e3 = git(["checkout", "--"] + drift)
            print("DRIFT-NORMALIZE rc=%d faces=%d" % (rc3, len(drift)))
            rc, out, err = git(["rebase", "origin/main"])
            tail = (err or out).strip()
            print("REBASE-RETRY rc=%d %s" % (rc, tail[-300:] if tail else "ok"))
        else:
            print("DRIFT-NORMALIZE skipped (no M faces)")
    if rc != 0:
        rc2, uu, _ = git(["ls-files", "-u"])
        faces = sorted({l.split("\t", 1)[1].strip()
                        for l in uu.splitlines() if "\t" in l})
        print("UU-FACES %d" % len(faces))
        for p in faces:
            print("UU %s" % p)
    rc, cnt, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())


if __name__ == "__main__":
    main()
