# -*- coding: utf-8 -*-
# r380 bm-c S6 maintenance chain driver (whole-batch discipline; per-leg rc; no paper block -- no new bar, bm-b r588 precedent)
import subprocess, sys

CWD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
PY = sys.executable

LEGS = [
    ("dualrun",   ["scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["scripts\\compute_audit.py"]),
    ("py_watermark", ["scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["scripts\\update_daily.py"]),
    ("market_regime", ["scripts\\market_regime.py"]),
    ("strategy_scorecard", ["scripts\\strategy_scorecard.py"]),
    ("market_clock", ["scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["scripts\\update_lhb.py"]),
    ("update_heat", ["scripts\\update_heat.py"]),          # bm-a lane -> honest no-op here
    ("update_futures", ["scripts\\update_futures.py"]),    # bm-a lane
    ("update_repo", ["scripts\\update_repo.py"]),         # bm-a lane
    ("update_options", ["scripts\\update_options.py"]),  # bm-a lane
    ("update_moneyflow", ["scripts\\update_moneyflow.py"]),  # bm-a lane
    ("update_sina_mf", ["scripts\\update_sina_mf.py"]),   # bm-a lane
    ("update_astock_daily", ["scripts\\update_astock_daily.py"]),  # bm-b lane
    ("update_etf_daily", ["scripts\\update_etf_daily.py"]),  # bm-b lane
    ("rev_osc_export", ["scripts\\rev_osc_signal_export.py", "run"]),  # bm-b lane
    ("minute_feed", ["scripts\\update_minute_feed.py"]),  # bm-b lane
    ("ths_panel", ["scripts\\update_ths_panel.py"]),      # bm-a lane
    ("ah_panel", ["scripts\\ah_panel_puller.py"]),        # bm-a lane
    ("fund_premium", ["scripts\\update_fund_premium.py", "snapshot"]),  # bm-c OWN lane
    ("fundamental", ["scripts\\update_fundamental.py"]),
    ("b_layer", ["-m", "firm.risk.b_layer_filter"]),
    ("daily_scorecard", ["scripts\\daily_scorecard.py"]),  # host bm-a -> guard skip
    ("daily_report", ["scripts\\daily_report.py", "run"]),
    ("ceo_live", ["scripts\\ceo_live_usage.py"]),
    ("build_status", ["-m", "monitor.build_status"]),      # host bm-a -> guard skip
    ("token_meter", ["scripts\\token_meter.py"]),
]

results = []
for name, args in LEGS:
    try:
        r = subprocess.run([PY] + args, cwd=CWD, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", creationflags=CNW, timeout=600)
        tail = (r.stdout or "").strip().split("\n")
        tail = [t for t in tail if t.strip()]
        last = tail[-1][:110] if tail else (r.stderr or "").strip()[:110]
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc, last = "TIMEOUT", ">600s"
    flag = "OK" if rc == 0 else "RC=" + str(rc)
    results.append((name, rc, last))
    print(f"[{name}] {flag} | {last}")

bad = [(n, rc) for n, rc, _ in results if rc != 0]
print("---")
print("BAD LEGS:", bad if bad else "none -- all rc0")
