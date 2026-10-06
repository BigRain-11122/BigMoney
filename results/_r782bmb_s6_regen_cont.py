# r782 bm-b S6 REGEN continuation (post-behead legs 18-39; leg 18 re-run inline rc0 already).
# Lineage: same LEGS table as _r782bmb_s6_regen.py; appends to the same regen log with CONT marker.
import subprocess, sys, time, io

LEGS = [
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

LOG = "results/_r782bmb_s6_regen.log"
log = io.open(LOG, "a", encoding="utf-8")
log.write("== S6 REGEN CONT start (legs 18 done inline rc0; 19-39 here) ==\n")
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
    print("LEG %s RC=%d (%.0fs)" % (name, r.returncode, time.time() - t0), flush=True)

nonzero = [(n, r) for n, r in rcs if r != 0]
print("CONT SUMMARY legs=%d nonzero=%r" % (len(rcs), nonzero))
log.write("== S6 REGEN CONT SUMMARY legs=%d nonzero=%r ==\n" % (len(rcs), nonzero))
log.write("== S6 REGEN CONT end %.0fs ==\n" % (time.time() - t0))
log.close()
sys.exit(1 if nonzero else 0)
