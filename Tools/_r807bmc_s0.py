# -*- coding: utf-8 -*-
"""r807 bm-c S0 absorb + rebase (1-gen clone canon; python subprocess git with
CREATE_NO_WINDOW per U060/2026-10-01 silence law; message via -F file per r512
quote-swallowing law; clean-tree-then-rebase per r642 net-tree law):
1) git status -> classify dirty faces (own daemon live-face = targeted add+commit;
   foreign half-done faces = skip commit, report);
2) fetch origin + pull --rebase (no autostash on clean tree);
3) print absorb/rebase summary + UU faces if any."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "_r_bmc_s0msg.txt")

OWN_PATTERNS = (
    "state-bm-c.json", "fleet/machines/bm-c.json", "fleet/machines/bm-a.json",
    "fleet/machines/bm-b.json", "results/crash_fuse.json",
    "results/runnable_pool.json",     "results/saturation", "results/idle_trigger",
    "results/autofill_state", "results/dispatcher_state",
    "Tools/_r807bmc",
    "results/_orphan_face_probe", "logs/autofill_", "logs/dispatcher_",
    "results/watermark_red.json", "results/marks", "results/watermark.jsonl",
    "results/_r806bmc", "results/_r807bmc", "results/_attrition_guard_scan",
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
)


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out, err


def main():
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
    for l in lines:
        print("  " + l)
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
            f.write("round 807 S0: absorb own daemon live faces (%d files)\n"
                    % len(own))
        rc, out, err = git(["commit", "-F", MSG])
        if rc == 0:
            rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
            print("ABSORB-COMMIT %s" % head.strip())
        else:
            print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:300]))
    rc, out, err = git(["fetch", "origin"])
    print("FETCH rc=%d %s" % (rc, (err or out).strip()[:150]))
    rc, out, err = git(["pull", "--rebase", "origin", "main"])
    tail = (err or out).strip()
    print("PULL-REBASE rc=%d %s" % (rc, tail[-400:] if tail else "up-to-date"))
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
