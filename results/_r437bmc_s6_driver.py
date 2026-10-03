# -*- coding: utf-8 -*-
"""DEFECTIVE RUN1 DRIVER -- SUPERSEDED, DO NOT REUSE (r437 defect disclosed):
missing env BIGMONEY_REGIME_GUARD=enforce -> live.paper downgraded registered
trader/paper guard faces enforce->shadow (predecessor dead-session regen);
also missing PYTHONUTF8 -> CJK mojibake in run log. Evidence kept in
_r437bmc_s6_log_run1_envdefect.txt. Canon path = Tools/_r428bmc_s6.py via
results/_r437bmc_s6_adapt.py (adapt->run->restore, r429 three-step law).
Original docstring below was inaccurate ("r436 canon pattern" not matched).

r437 bm-c S6 chain driver (r436 canon pattern): 37 legs, CREATE_NO_WINDOW,
per-leg rc + tail-3 output lines to results/_r437bmc_s6_log.txt.
Golden-week Sunday: paper legs honest no-ops; lane-guard legs stdout-only no-op."""
import datetime
import os
import subprocess
import sys

CREATE = 0x08000000
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
LOG = os.path.join(REPO, "results", "_r437bmc_s6_log.txt")

LEGS = [
    ["scripts\\pool_dualrun_reconcile.py", "run"],
    ["scripts\\compute_audit.py"],
    ["scripts\\py_watermark.py", "probe"],
    ["scripts\\update_daily.py"],
    ["scripts\\market_regime.py"],
    ["scripts\\strategy_scorecard.py"],
    ["scripts\\market_clock_call.py", "run"],
    ["scripts\\update_lhb.py"],
    ["scripts\\update_heat.py"],
    ["scripts\\update_futures.py"],
    ["scripts\\update_repo.py"],
    ["scripts\\update_options.py"],
    ["scripts\\update_moneyflow.py"],
    ["scripts\\update_sina_mf.py"],
    ["scripts\\update_astock_daily.py"],
    ["scripts\\update_etf_daily.py"],
    ["scripts\\rev_osc_signal_export.py", "run"],
    ["scripts\\update_minute_feed.py"],
    ["scripts\\update_ths_panel.py"],
    ["scripts\\ah_panel_puller.py"],
    ["scripts\\update_fund_premium.py", "snapshot"],
    ["scripts\\update_fundamental.py"],
    ["-m", "firm.risk.b_layer_filter"],
    ["-m", "live.paper"],
    ["scripts\\t35_open_fill_verify.py"],
    ["scripts\\t24_prospect_paper.py", "run"],
    ["scripts\\t24_prospect_promotion.py", "run"],
    ["scripts\\aggressive_lab.py", "paper"],
    ["scripts\\alloc_paper.py", "run"],
    ["scripts\\grid_paper.py", "run"],
    ["scripts\\system_v1_paper.py", "run"],
    ["scripts\\t35_paper_export.py", "run"],
    ["scripts\\daily_scorecard.py"],
    ["scripts\\daily_report.py", "run"],
    ["scripts\\ceo_live_usage.py"],
    ["-m", "monitor.build_status"],
    ["scripts\\token_meter.py"],
]


def main():
    lines = []
    nonzero = []
    for leg in LEGS:
        if leg[0] == "-m":
            cmd = [PY, "-m", leg[1]]
        else:
            cmd = [PY, os.path.join(REPO, leg[0])] + leg[1:]
        name = " ".join(leg)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            p = subprocess.run(cmd, capture_output=True, creationflags=CREATE,
                               cwd=REPO, timeout=900)
            rc = p.returncode
            out = (p.stdout or b"").decode("utf-8", "replace").splitlines()
            err = (p.stderr or b"").decode("utf-8", "replace").splitlines()
        except Exception as e:
            rc, out, err = -99, [], ["driver-exc: %r" % e]
        lines.append("[%s] %s rc=%d" % (ts, name, rc))
        for l in (out + err)[-3:]:
            lines.append("    | " + l[:200])
        if rc != 0:
            nonzero.append((name, rc))
    lines.append("SUMMARY: %d legs, NON-ZERO=%s" %
                 (len(LEGS), nonzero if nonzero else "none"))
    with open(LOG, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(lines[-1])
    for n, r in nonzero:
        print("NONZERO: %s rc=%d" % (n, r))
    sys.exit(2 if any(r == 2 for _, r in nonzero) else 0)


if __name__ == "__main__":
    main()
