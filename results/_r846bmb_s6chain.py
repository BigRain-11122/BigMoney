# -*- coding: utf-8 -*-
# r846 bm-b S6 chain driver: 41 legs (r845 set, no new bar this Saturday -> live.paper
# anchor + t35_open_fill_verify legs honestly skipped per trigger condition).
# Byte-capture with utf-8->gbk fallback decode (pit-encoding domain), LEG log format.
import subprocess
import sys
import time

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
    ("aggressive_lab", [PY, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts\\grid_paper.py", "run"]),
    ("t24_prospect_paper", [PY, "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts\\t24_prospect_promotion.py", "run"]),
    ("system_v1_paper", [PY, "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts\\daily_scorecard.py"]),
    ("daily_report", [PY, "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", [PY, "scripts\\ceo_live_usage.py"]),
    ("monitor_build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts\\token_meter.py"]),
    ("attrition_ledger_guard", [PY, "scripts\\attrition_ledger_guard.py", "scan"]),
]

LOG = "results\\_r846bmb_s6chain.log"


def dec(b):
    for enc in ("utf-8", "gbk"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", "replace")


def main():
    open(LOG, "wb").close()
    for name, argv in LEGS:
        t0 = time.time()
        try:
            p = subprocess.run(argv, capture_output=True, timeout=900)
            rc = p.returncode
            txt = dec(p.stdout or b"") + dec(p.stderr or b"")
        except subprocess.TimeoutExpired:
            rc = -1
            txt = "TIMEOUT after 900s"
        lines = [l for l in txt.splitlines() if l.strip()]
        tail = " ~ ".join(lines[-3:])
        msg = "LEG %s | exit=%s | %.1fs | %s\n" % (name, rc, time.time() - t0, tail)
        with open(LOG, "ab") as f:
            f.write(msg.encode("utf-8", "replace"))
    print("S6 chain done: %d legs" % len(LEGS))


if __name__ == "__main__":
    main()
