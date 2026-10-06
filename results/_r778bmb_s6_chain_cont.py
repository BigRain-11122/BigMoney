# r778 bm-b S6 chain continuation (legs 18-39 after 5-min shell cancel killed ps1 at leg 17/18 boundary)
# Lineage: results/_r778bmb_s6_chain.ps1 (adopted r777) legs verbatim; python driver = per-leg
# stdout progress keeps shell alive + UTF-8 log (PS *> wrote UTF-16 face).
# Legs 25-28 (live.paper/t35_open_fill/t24 pair) = golden-week no-new-bar honest skip (cutoff 09-30).
import subprocess, sys, time, io

LEGS = [
    ("18_minute_feed", ["scripts/update_minute_feed.py"]),
    ("19_ths_panel", ["scripts/update_ths_panel.py"]),
    ("20_ah_panel", ["scripts/ah_panel_puller.py"]),
    ("21_fund_premium", ["scripts/update_fund_premium.py", "snapshot"]),
    ("22_fundamental", ["scripts/update_fundamental.py"]),
    ("23_b_layer", ["-m", "firm.risk.b_layer_filter"]),
    ("24_fund_statements", ["scripts/update_fund_statements.py"]),
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

log = io.open("results/_r778bmb_s6_chain_cont.log", "a", encoding="utf-8")
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
    print("LEG %s RC=%d (%.0fs)" % (name, r.returncode, time.time() - t0), flush=True)

nonzero = [(n, r) for n, r in rcs if r != 0]
print("SUMMARY cont legs=%d nonzero=%r" % (len(rcs), nonzero))
log.write("== S6 SUMMARY cont legs=%d nonzero=%r ==\n" % (len(rcs), nonzero))
log.write("== chain cont end %.0fs ==\n" % (time.time() - t0))
log.close()
sys.exit(1 if nonzero else 0)
