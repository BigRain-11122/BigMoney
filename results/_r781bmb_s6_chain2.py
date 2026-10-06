# r781 bm-b S6 chain resume (legs 08-39; legs 01-07 already rc0 in _r781bmb_s6_chain.log before 5-min watchdog kill)
# detached-spawn run per pit-spawn law (long legs must not inline under the 5-min shell cancel)
import subprocess, sys, time, io

LEGS = [
    ("08_lhb", ["scripts/update_lhb.py"]),
    ("09_heat", ["scripts/update_heat.py"]),
    ("10_futures", ["scripts/update_futures.py"]),
    ("11_repo", ["scripts/update_repo.py"]),
    ("12_options", ["scripts/update_options.py"]),
    ("13_moneyflow", ["scripts/update_moneyflow.py"]),
    ("14_sina_mf", ["scripts/update_sina_mf.py"]),
    ("15_astock_daily", ["scripts/update_astock_daily.py"]),
    ("16_etf_daily", ["scripts/update_etf_daily.py"]),
    ("17_rev_osc", ["scripts/rev_osc_signal_export.py", "run"]),
    ("18_minute_feed", ["scripts/update_minute_feed.py"]),
    ("19_ths_panel", ["scripts/update_ths_panel.py"]),
    ("20_ah_panel", ["scripts/ah_panel_puller.py"]),
    ("21_fund_premium", ["scripts/update_fund_premium.py", "snapshot"]),
    ("22_fundamental", ["scripts/update_fundamental.py"]),
    ("23_b_layer", ["-m", "firm.risk.b_layer_filter"]),
    ("24_fund_statements", ["scripts/update_fund_statements.py"]),
    # legs 25-28: golden-week no-new-bar honest skip
    ("29_aggr_paper", ["scripts/aggressive_lab.py", "paper"]),
    ("30_alloc_paper", ["scripts/alloc_paper.py", "run"]),
    ("31_grid_paper", ["scripts/grid_paper.py", "run"]),
    ("32_system_v1", ["scripts/system_v1_paper.py", "run"]),
    ("33_t35_export", ["scripts/t35_paper_export.py", "run"]),
    ("34_daily_scorecard", ["scripts/daily_scorecard.py"]),
    ("35_daily_report", ["scripts/daily_report.py", "run"]),
    ("36_ceo_live", ["scripts/ceo_live_usage.py"]),
    ("37_build_status", ["-m", "monitor.build_status"]),
    ("38_token_meter", ["scripts/token_meter.py"]),
    ("39_trio_readiness", ["scripts/finalize_trio_readiness.py"]),
]

LOG = "results/_r781bmb_s6_chain.log"
log = io.open(LOG, "a", encoding="utf-8")
log.write("== S6 chain resume r781 bm-b (legs 08-39) ==\n")
log.flush()
rcs = []
t0 = time.time()
for name, args in LEGS:
    r = subprocess.run([sys.executable] + args, capture_output=True)
    rcs.append((name, r.returncode))
    log.write("== LEG %s RC=%d ==\n" % (name, r.returncode))
    if r.returncode != 0:
        log.write(r.stdout.decode("utf-8", "replace")[-1500:] + "\n")
        log.write(r.stderr.decode("utf-8", "replace")[-1500:] + "\n")
    log.flush()

nonzero = [(n, r) for n, r in rcs if r != 0]
print("SUMMARY legs=%d nonzero=%r" % (len(rcs), nonzero))
log.write("== S6 RESUME SUMMARY legs=%d nonzero=%r ==\n" % (len(rcs), nonzero))
log.write("== S6 chain resume end %.0fs ==\n" % (time.time() - t0))
log.close()
sys.exit(1 if nonzero else 0)
