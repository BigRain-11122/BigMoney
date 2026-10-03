# -*- coding: utf-8 -*-
"""r642 bm-a S6 maintenance-chain runner: sequential legs, rc capture,
evidence file results/_r642bma_s6_evidence.txt (r640/r641 lineage)."""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r642bma_s6_evidence.txt")

LEGS = [
    ("pool_dualrun_reconcile", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark_probe", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_repo", [sys.executable, "scripts/update_repo.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("monitor_build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]


def main():
    lines = ["r642 bm-a S6 chain evidence", time.strftime("%Y-%m-%d %H:%M:%S")]
    bad = []
    for name, cmd in LEGS:
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        dt = time.time() - t0
        tail = (r.stdout or b"").decode("utf-8", errors="replace").strip().splitlines()
        last = tail[-1][:150] if tail else ""
        rc = r.returncode
        status = "rc0" if rc == 0 else f"rc={rc} !!"
        lines.append(f"{name:24s} {status:9s} {dt:6.1f}s | {last}")
        if rc != 0:
            err = (r.stderr or b"").decode("utf-8", errors="replace").strip().splitlines()
            bad.append((name, rc, last, err[-1][:200] if err else ""))
    n_ok = len(LEGS) - len(bad)
    lines.append(f"SUMMARY: {n_ok}/{len(LEGS)} rc0, {len(bad)} non-zero")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[-3:]))
    for b in bad:
        print("BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
