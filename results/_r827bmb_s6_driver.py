# r827 bm-b S6 chain driver: r826 driver clone (round-token rename only, legs
# identical 41). Saturday 2026-10-10: no-new-bar legs legitimately no-op;
# lane-guarded legs (bm-a/bm-c hosts) run and self-guard to honest no-op on
# this machine (R31 precedent).
import subprocess, sys, io

LEGS = [
    ("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts/update_zt_pool.py"]),
    ("zt_pool_crosscheck", ["python", "scripts/zt_pool_crosscheck.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    ("regime_thermo_build", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]

log = io.open("results/_r827bmb_s6_log.txt", "w", encoding="utf-8", newline="\n")
# resume support + GBK-console crash fix (pit-encoding family): sanitize tail to
# ASCII before printing; argv[1] = number of leading legs already completed this
# round (r827 run-1: legs 0-6 rc0 evidenced in session console, driver died at
# the update_lhb print, log buffer unflushed -> rewritten fresh from leg 7).
SKIP = int(sys.argv[1]) if len(sys.argv) > 1 else 0
rcs = []
for idx, (name, cmd) in enumerate(LEGS):
    if idx < SKIP:
        print("%s SKIPPED(resume)" % name)
        continue
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                           encoding="utf-8", errors="replace")
        rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        rc, out = 99, "driver-exception: %r" % e
    tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or ["(no output)"]
    rcs.append((name, rc))
    log.write("=== %s rc=%d\n%s\n" % (name, rc, out[-4000:]))
    log.flush()
    safe = tail[0][:130].encode("ascii", "replace").decode("ascii")
    print("%s rc=%d | %s" % (name, rc, safe))

bad = [n for n, rc in rcs if rc != 0]
print("S6 legs=%d bad=%s" % (len(rcs), bad if bad else "NONE(all rc0)"))
log.close()
