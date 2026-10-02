"""r379 bm-c S6 chain driver (r376 driver + daily_scorecard/build_status legs, protocol-full).

Laws: zero-window (CREATE_NO_WINDOW), honest rc reporting (no masking),
dualrun BEFORE compute_audit, lane-guarded legs run as honest no-ops on
this machine per R31 precedent (guards decide host/stale-takeover).
"""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
PY = sys.executable

LEGS = [
    ("dualrun", [PY, "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts\\compute_audit.py"]),
    ("watermark", [PY, "scripts\\py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts\\update_daily.py"]),
    ("market_regime", [PY, "scripts\\market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts\\strategy_scorecard.py"]),
    ("market_clock", [PY, "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts\\update_lhb.py"]),
    ("update_heat", [PY, "scripts\\update_heat.py"]),
    ("update_futures", [PY, "scripts\\update_futures.py"]),
    ("update_repo", [PY, "scripts\\update_repo.py"]),
    ("update_options", [PY, "scripts\\update_options.py"]),
    ("update_moneyflow", [PY, "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", [PY, "scripts\\update_etf_daily.py"]),
    ("rev_osc_export", [PY, "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [PY, "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", [PY, "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts\\ah_panel_puller.py"]),
    ("fund_premium", [PY, "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts\\update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
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


def run_leg(name, args, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(args, cwd=REPO, capture_output=True,
                       creationflags=NO_WINDOW, env=env)
    out = (r.stdout or b"").decode("utf-8", "replace").strip()
    err = (r.stderr or b"").decode("utf-8", "replace").strip()
    tail = (out.splitlines()[-1][:110] if out else (err.splitlines()[-1][:110] if err else ""))
    print(f"LEG {name} rc={r.returncode} | {tail}")
    return r.returncode, out


def main():
    fails = []
    for name, args in LEGS:
        rc, _ = run_leg(name, args)
        if rc not in (0,):
            fails.append((name, rc))
    # paper legs: idempotent no-ops without new bar; REGIME_GUARD enforce per T-21
    guard = {"BIGMONEY_REGIME_GUARD": "enforce"}
    for name, args in [
        ("live.paper", [PY, "-m", "live.paper"]),
        ("t35_open_fill", [PY, "scripts\\t35_open_fill_verify.py"]),
        ("t24_prospect_paper", [PY, "scripts\\t24_prospect_paper.py", "run"]),
        ("t24_prospect_promo", [PY, "scripts\\t24_prospect_promotion.py", "run"]),
    ]:
        rc, _ = run_leg(name, args, env_extra=guard)
        if rc not in (0,):
            fails.append((name, rc))
    print("FAILS:", fails if fails else "none")


if __name__ == "__main__":
    main()
