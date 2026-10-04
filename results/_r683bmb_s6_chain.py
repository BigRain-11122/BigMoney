# r683 (bm-b) S6 chain driver: sequential regen faces, incremental log, per-leg timeout cap
# r680 law: python -u + flush + incremental log (crash-safe) + 240s cap per leg
# r460 law: no truncating pipeline on live commands; evidence = this log file
# Sunday 17:2x window: no new bar (last 2026-09-30) -> live.paper trigger-legs skipped by design
import subprocess, sys, time, io, os

LEGS = [
    ("dualrun",    ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute",    ["python", "scripts/compute_audit.py"]),
    ("pywm",       ["python", "scripts/py_watermark.py", "probe"]),
    ("daily",      ["python", "scripts/update_daily.py"]),
    ("regime",     ["python", "scripts/market_regime.py"]),
    ("scorecard",  ["python", "scripts/strategy_scorecard.py"]),
    ("clock",      ["python", "scripts/market_clock_call.py", "run"]),
    ("lhb",        ["python", "scripts/update_lhb.py"]),
    ("heat",       ["python", "scripts/update_heat.py"]),
    ("futures",    ["python", "scripts/update_futures.py"]),
    ("repo",       ["python", "scripts/update_repo.py"]),
    ("options",    ["python", "scripts/update_options.py"]),
    ("moneyflow",  ["python", "scripts/update_moneyflow.py"]),
    ("sina_mf",    ["python", "scripts/update_sina_mf.py"]),
    ("astock",     ["python", "scripts/update_astock_daily.py"]),
    ("etf_daily",  ["python", "scripts/update_etf_daily.py"]),
    ("rev_osc",    ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("minute",     ["python", "scripts/update_minute_feed.py"]),
    ("ths",        ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel",   ["python", "scripts/ah_panel_puller.py"]),
    ("fund_prem",  ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental",["python", "scripts/update_fundamental.py"]),
    ("b_layer",    ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_stmt",  ["python", "scripts/update_fund_statements.py"]),
    ("d_score",    ["python", "scripts/daily_scorecard.py"]),
    ("d_report",   ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live",   ["python", "scripts/ceo_live_usage.py"]),
    ("token",      ["python", "scripts/token_meter.py"]),
]

LOG = "results/_r683bmb_s6_log.txt"
results = {}
with io.open(LOG, "w", encoding="utf-8", newline="\n") as lf:
    lf.write("S6 chain start %s legs=%d\n" % (time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), len(LEGS)))
    lf.flush()
    for name, cmd in LEGS:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=240)
            rc = r.returncode
            out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
            err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        except subprocess.TimeoutExpired:
            rc, out, err = 124, [], ["TIMEOUT 240s"]
        dt = round(time.time() - t0, 1)
        results[name] = (rc, dt)
        lf.write("=== %s rc=%d %.1fs\n" % (name, rc, dt))
        for ln in (out[-6:] if len(out) > 6 else out):
            lf.write("  | %s\n" % ln[:200])
        for ln in err[-3:]:
            lf.write("  ! %s\n" % ln[:200])
        lf.flush()

bad = {k: v for k, v in results.items() if v[0] not in (0,)}
print("S6 chain end %s: total=%d bad=%d" % (time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), len(results), len(bad)))
for k, v in sorted(results.items()):
    print("  %-12s rc=%-3d %.1fs" % (k, v[0], v[1]))
if bad:
    print("BAD LEGS:", ",".join("%s(%d)" % kv for kv in bad.items()))
    sys.exit(1)
print("S6 ALL-RC0")
