# -*- coding: utf-8 -*-
# r998 S6 chain (bm-b) -- leg list replicated from results/_r996bmb_s6_log.txt proven sequence
import io, subprocess, sys, time

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = ROOT + r"\results\_r998bmb_s6_log.txt"
PY = sys.executable


def log(s):
    with io.open(LOG, "a", encoding="utf-8", newline="") as f:
        f.write(s + "\n")


def run(tag, args):
    t0 = time.time()
    try:
        p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, timeout=600)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 99
    tail = b""
    try:
        p2 = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, timeout=1) if False else None
    except Exception:
        pass
    log("rc=%d %s :: %s" % (rc, tag, tail))
    return rc


def main():
    io.open(LOG, "w", encoding="utf-8").close()
    log("chain start %s (r998)" % time.strftime("%H:%M:%S"))
    bad = 0
    legs = [
        ("orphan_probe", [r"Tools\orphan_face_probe.py"]),
        ("smoke_test", ["-m", "smoke_test"]),
        ("sat_engine_status", [r"scripts\saturation_engine.py", "status"]),
        ("idle_worked", [r"Tools\idle_trigger.py", "--worked"]),
        ("pool_dualrun", [r"scripts\pool_dualrun_reconcile.py", "run"]),
        ("compute_audit", [r"scripts\compute_audit.py"]),
        ("py_watermark", [r"scripts\py_watermark.py", "probe"]),
        ("update_daily", [r"scripts\update_daily.py"]),
        ("market_regime", [r"scripts\market_regime.py"]),
        ("strategy_scorecard", [r"scripts\strategy_scorecard.py"]),
        ("market_clock_call", [r"scripts\market_clock_call.py", "run"]),
        ("update_lhb", [r"scripts\update_lhb.py"]),
        ("update_zt_pool", [r"scripts\update_zt_pool.py"]),
        ("update_heat", [r"scripts\update_heat.py"]),
        ("update_futures", [r"scripts\update_futures.py"]),
        ("update_repo_panel", [r"scripts\update_repo.py"]),
        ("update_options", [r"scripts\update_options.py"]),
        ("update_moneyflow", [r"scripts\update_moneyflow.py"]),
        ("update_sina_mf", [r"scripts\update_sina_mf.py"]),
        ("update_astock_daily", [r"scripts\update_astock_daily.py"]),
        ("update_etf_daily", [r"scripts\update_etf_daily.py"]),
        ("regime_thermo", [r"scripts\regime_thermo_build.py"]),
        ("regime_gate_dualarm", [r"scripts\regime_gate_dualarm.py", "run"]),
        ("rev_osc_signal", [r"scripts\rev_osc_signal_export.py", "run"]),
        ("update_minute_feed", [r"scripts\update_minute_feed.py"]),
        ("update_ths_panel", [r"scripts\update_ths_panel.py"]),
        ("ah_panel_puller", [r"scripts\ah_panel_puller.py"]),
        ("update_fund_premium", [r"scripts\update_fund_premium.py", "snapshot"]),
        ("update_fundamental", [r"scripts\update_fundamental.py"]),
        ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"]),
        ("update_fund_statements", [r"scripts\update_fund_statements.py"]),
        ("aggressive_lab", [r"scripts\aggressive_lab.py", "paper"]),
        ("alloc_paper", [r"scripts\alloc_paper.py", "run"]),
        ("grid_paper", [r"scripts\grid_paper.py", "run"]),
        ("system_v1_paper", [r"scripts\system_v1_paper.py", "run"]),
        ("t35_paper_export", [r"scripts\t35_paper_export.py", "run"]),
        ("daily_scorecard", [r"scripts\daily_scorecard.py"]),
        ("daily_report", [r"scripts\daily_report.py", "run"]),
        ("ceo_live_usage", [r"scripts\ceo_live_usage.py"]),
        ("build_status", ["-m", "monitor.build_status"]),
        ("token_meter", [r"scripts\token_meter.py"]),
    ]
    # Sunday: no new bar -> paper legs skipped (r996 Saturday precedent)
    log("SKIP live.paper (Sunday no new bar)")
    log("SKIP t35_open_fill_verify (Sunday no new bar)")
    log("SKIP t24_prospect_paper (Sunday no new bar)")
    log("SKIP t24_prospect_promotion (Sunday no new bar)")
    for tag, args in legs:
        rc = run(tag, args)
        if rc != 0:
            bad += 1
    log("chain end %s elapsed=%dmin nonzero_rc=%d" % (time.strftime("%H:%M:%S"), 0, bad))
    print("S6 chain done nonzero_rc=%d" % bad)
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
