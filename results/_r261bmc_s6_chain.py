# -*- coding: utf-8 -*-
# r261 bm-c: S6 maintenance chain driver (39-leg house sequence, per-leg rc log).
# Detached launch (r462 bm-a paradigm): order law preserved, dualrun precedes
# compute_audit; bar-gated legs honest-skip pre-15:30 (no new bar landed).
# Host-guarded legs (scorecard/daily_scorecard/build_status = bm-a host per
# r378; lane-guarded collectors) self-skip with honest stdout on bm-c.
import subprocess, sys, io, time

LOG = r"logs\iteration-loop\s6_r261_bmc_chain.log"

LEGS = [
    ("dualrun",   ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("audit",     ["python", "scripts\\compute_audit.py"]),
    ("wm_probe",  ["python", "scripts\\py_watermark.py", "probe"]),
    ("daily",     ["python", "scripts\\update_daily.py"]),
    ("regime",    ["python", "scripts\\market_regime.py"]),
    ("scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("clock",     ["python", "scripts\\market_clock_call.py", "run"]),
    ("lhb",       ["python", "scripts\\update_lhb.py"]),
    ("heat",      ["python", "scripts\\update_heat.py"]),
    ("futures",   ["python", "scripts\\update_futures.py"]),
    ("repo",      ["python", "scripts\\update_repo.py"]),
    ("options",   ["python", "scripts\\update_options.py"]),
    ("moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("sinamf",    ["python", "scripts\\update_sina_mf.py"]),
    ("astock",    ["python", "scripts\\update_astock_daily.py"]),
    ("etfdaily",  ["python", "scripts\\update_etf_daily.py"]),
    ("revosc",    ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minfeed",   ["python", "scripts\\update_minute_feed.py"]),
    ("ths",       ["python", "scripts\\update_ths_panel.py"]),
    ("ah",        ["python", "scripts\\ah_panel_puller.py"]),
    ("fundprem",  ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundam",    ["python", "scripts\\update_fundamental.py"]),
    ("blayer",    ["python", "-m", "firm.risk.b_layer_filter"]),
    # bar-gated family: no new bar pre-15:30 -> honest skip (same law as live.paper trigger)
    ("t24paper",  ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24promo",  ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr",      ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc",     ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid",      ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1",     ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35exp",    ["python", "scripts\\t35_paper_export.py", "run"]),
    ("dailysc",   ["python", "scripts\\daily_scorecard.py"]),
    ("dayrep",    ["python", "scripts\\daily_report.py", "run"]),
    ("ceolive",   ["python", "scripts\\ceo_live_usage.py"]),
    ("buildstat", ["python", "-m", "monitor.build_status"]),
    ("token",     ["python", "scripts\\token_meter.py"]),
]

def main():
    log = io.open(LOG, "w", encoding="utf-8")
    log.write("S6 chain r261 bm-c start %s legs=%d\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), len(LEGS)))
    log.flush()
    bad = []
    for name, cmd in LEGS:
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=600,
                               encoding="utf-8", errors="replace")
            rc = p.returncode
            out = (p.stdout or "").strip()
            err = (p.stderr or "").strip()
        except Exception as e:
            rc, out, err = -99, "", repr(e)
        dt = time.time() - t0
        tail_out = out[-700:] if out else ""
        log.write("[%s] rc=%d %.1fs %s\n" % (name, rc, dt, tail_out.replace("\n", " | ")[:700]))
        if err:
            log.write("[%s] stderr: %s\n" % (name, err[-300:].replace("\n", " | ")))
        log.flush()
        if rc not in (0,):
            bad.append((name, rc))
    log.write("S6 chain done %s non_green=%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), bad))
    log.close()
    print("chain done non_green=", bad)

if __name__ == "__main__":
    main()

