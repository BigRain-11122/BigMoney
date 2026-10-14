# r935 bm-b S6 chain driver - mirrors r934 41-leg order (ASCII-only per repo law)
import subprocess, sys, time, io
from datetime import datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = ROOT + r"\results\_r935bmb_s6_log.txt"
PY = sys.executable

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts\\compute_audit.py"]),
    ("py_watermark", [PY, "scripts\\py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts\\update_daily.py"]),
    ("market_regime", [PY, "scripts\\market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts\\update_lhb.py"]),
    ("update_zt_pool", [PY, "scripts\\update_zt_pool.py"]),
    ("update_heat", [PY, "scripts\\update_heat.py"]),
    ("update_futures", [PY, "scripts\\update_futures.py"]),
    ("update_repo", [PY, "scripts\\update_repo.py"]),
    ("update_options", [PY, "scripts\\update_options.py"]),
    ("update_moneyflow", [PY, "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", [PY, "scripts\\update_etf_daily.py"]),
    ("regime_thermo_build", [PY, "scripts\\regime_thermo_build.py"]),
    ("regime_gate_dualarm", [PY, "scripts\\regime_gate_dualarm.py", "run"]),
    ("rev_osc_signal_export", [PY, "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [PY, "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", [PY, "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts\\ah_panel_puller.py"]),
    ("update_fund_premium", [PY, "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts\\update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [PY, "scripts\\update_fund_statements.py"]),
    ("live_paper", [PY, "-m", "live.paper"]),
    ("t35_open_fill_verify", [PY, "scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [PY, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", [PY, "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts\\daily_scorecard.py"]),
    ("daily_report", [PY, "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", [PY, "scripts\\ceo_live_usage.py"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts\\token_meter.py"]),
]

def main():
    log = io.open(LOG, "w", encoding="utf-8", newline="\n")
    t0 = time.time()
    log.write("S6 chain r935 bm-b start {} ({} legs)\n".format(datetime.now().isoformat(), len(LEGS)))
    log.flush()
    fails = []
    for name, cmd in LEGS:
        ts = time.time()
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        dt = time.time() - ts
        log.write("\n=== {} rc={} {:.1f}s\n".format(name, p.returncode, dt))
        if p.stdout:
            log.write(p.stdout + "\n")
        if p.stderr:
            log.write("[stderr] " + p.stderr[-800:] + "\n")
        log.flush()
        if p.returncode not in (0,):
            fails.append((name, p.returncode))
    log.write("\nS6 chain r935 done in {:.1f}s fails={}\n".format(time.time() - t0, fails))
    log.close()
    print("S6 done, fails:", fails)

if __name__ == "__main__":
    main()
