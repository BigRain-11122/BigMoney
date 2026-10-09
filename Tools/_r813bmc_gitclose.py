# -*- coding: utf-8 -*-
"""r813 bm-c git closeout: classify dirty faces with the S0 OWN_PATTERNS
classifier + explicit round extras (qa/ pack, ledger, helpers), targeted add
(never -A on a dirtied-at-open tree), commit via -F msg file, push, fetch,
rev-list 0/0 self-verify (O-20261001-1108 delivery gate). Push-rejected ->
pull --rebase once -> retry once; still rejected -> origin machine/bm-c-r813
lane branch per D-20260925-01(c). Every git leg CREATE_NO_WINDOW + timeout."""
import subprocess
import io
import os

CNW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = os.path.join(ROOT, "_r813bmc_commitmsg.txt")
log = io.open(os.path.join(ROOT, "results", "_r813bmc_gitclose.log"), "w",
              encoding="utf-8")
w = lambda s: (log.write(s + "\n"), log.flush())


def g(args, t=90):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CNW, timeout=t)
        return r.returncode, r.stdout.decode("utf-8", "replace"), \
            r.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


OWN_PATTERNS = (
    "_r_bmc_s0msg.txt", "_r813bmc_commitmsg.txt",
    "state-bm-c.json", "fleet/machines/bm-c.json",
    "results/saturation", "results/idle_trigger", "results/autofill_state",
    "results/dispatcher_state", "results/_orphan_face_probe",
    "Tools/_r813bmc", "results/_r813bmc", "qa/smoke-r813-bm-c",
    "qa/equity-curve-r813-bm-c",
    "logs/iteration-loop/round_reports-bm-c.md",
    "logs/autofill_", "logs/dispatcher_",
    "results/watermark_red.json", "results/marks", "results/watermark.jsonl",
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
    "data/", "results/crash_fuse.json", "results/runnable_pool.json",
)

rc, st, _ = g(["status", "--porcelain"])
lines = [l for l in st.splitlines() if l.strip()]
own, foreign = [], []
for l in lines:
    path = l[3:].strip().strip('"')
    if any(p in path for p in OWN_PATTERNS):
        own.append(path)
    else:
        foreign.append(path)
w("dirty=%d own=%d foreign=%d" % (len(lines), len(own), len(foreign)))
for p in foreign:
    w("  FOREIGN(no add): " + p)

if own:
    rc, o, e = g(["add", "--"] + own)
    w("ADD rc=%d %s" % (rc, (e or o).strip()[:200]))

with io.open(MSG, "w", encoding="utf-8", newline="\n") as f:
    f.write("round 813: O-1750 FleetLink v1.1 upgrade (/health 1.1 receipt) + "
            "C-03 workspace audit PASS (group-tree sync + zero-loss union push) "
            "+ O-1746 MiniMax-H3 order consumed (preconditions recon) + "
            "S6 40/40 rc0 + QA r813 5/5 (det-99th first-write)\n")
rc, o, e = g(["commit", "-F", MSG])
w("COMMIT rc=%d %s" % (rc, (e or o).strip()[:300]))
rc, o, e = g(["rev-parse", "--short", "HEAD"])
head = o.strip()
w("HEAD=%s" % head)

rc, o, e = g(["push", "origin", "main"])
w("PUSH rc=%d %s" % (rc, (e or o).strip()[-300:]))
if rc != 0:
    rc2, o2, e2 = g(["pull", "--rebase", "origin", "main"])
    w("PULL-REBASE rc=%d %s" % (rc2, (e2 or o2).strip()[-200:]))
    if rc2 == 0:
        rc, o, e = g(["push", "origin", "main"])
        w("PUSH-RETRY rc=%d %s" % (rc, (e or o).strip()[-300:]))
    if rc != 0:
        rc3, o3, e3 = g(["push", "origin", "HEAD:refs/heads/machine/bm-c-r813"])
        w("LANE-PUSH rc=%d %s" % (rc3, (e3 or o3).strip()[-300:]))

rc, o, e = g(["fetch", "origin"])
w("FETCH rc=%d" % rc)
rc, o, e = g(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
w("AHEAD-BEHIND after push: %s" % o.strip())
rc, o, e = g(["status", "--porcelain"])
rest = [l.strip() for l in o.splitlines() if l.strip()]
w("STATUS after: %d faces %s" % (len(rest), " | ".join(rest[:8])))
try:
    os.remove(MSG)
except OSError:
    pass
log.close()
print("git close done head=%s" % head)
