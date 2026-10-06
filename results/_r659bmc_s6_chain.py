# -*- coding: utf-8 -*-
# S6 chain runner (r659 bm-c) -- 38-item standing chain, r658 bloodline copy (r653/r655/r657-proven order).
# Children inherit the tick console (zero-flash law); output tee'd to log.
# REGIME_GUARD enforce env set from live_paper onward (date gate self-downgrades).
import subprocess, sys, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r659bmc_s6_log.txt")
PY = sys.executable

ITEMS = [
    ("pool_dualrun_reconcile", ["scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["scripts\\compute_audit.py"]),
    ("py_watermark", ["scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["scripts\\update_daily.py"]),
    ("market_regime", ["scripts\\market_regime.py"]),
    ("strategy_scorecard", ["scripts\\strategy_scorecard.py"]),
    ("market_clock_call", ["scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["scripts\\update_lhb.py"]),
    ("update_heat", ["scripts\\update_heat.py"]),
    ("update_futures", ["scripts\\update_futures.py"]),
    ("update_repo", ["scripts\\update_repo.py"]),
    ("update_options", ["scripts\\update_options.py"]),
    ("update_moneyflow", ["scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["scripts\\update_etf_daily.py"]),
    ("rev_osc_signal_export", ["scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["scripts\\update_minute_feed.py"]),
    ("update_ths_panel", ["scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", ["scripts\\ah_panel_puller.py"]),
    ("update_fund_premium", ["scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["scripts\\update_fund_statements.py"]),
    ("live_paper", ["-m", "live.paper"]),
    ("t35_open_fill_verify", ["scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", ["scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", ["scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", ["scripts\\daily_scorecard.py"]),
    ("daily_report", ["scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["scripts\\ceo_live_usage.py"]),
    ("build_status", ["-m", "monitor.build_status"]),
    ("token_meter", ["scripts\\token_meter.py"]),
]

def decode(b):
    if not b:
        return ""
    u = b.decode("utf-8", errors="replace")
    g = b.decode("gbk", errors="replace")
    return u if u.count("\ufffd") <= g.count("\ufffd") else g

def main():
    lines = ["S6 chain r659 bm-c start %s\n" % datetime.datetime.now().isoformat(timespec="microseconds")]
    bad = []
    summary = []
    for name, args in ITEMS:
        if name == "live_paper":
            os.environ["BIGMONEY_REGIME_GUARD"] = "enforce"
        t0 = time.time()
        try:
            p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, timeout=600)
            rc, out = p.returncode, decode(p.stdout) + decode(p.stderr)
        except subprocess.TimeoutExpired:
            rc, out = 124, "TIMEOUT after 600s"
        sec = time.time() - t0
        lines.append("=== %s rc=%d %.1fs\n%s\n" % (name, rc, sec, out.rstrip()))
        if rc != 0:
            bad.append(name)
        summary.append("%s rc=%d %.1fs" % (name, rc, sec))
    lines.append("S6 chain end %s bad=%s" % (datetime.datetime.now().isoformat(timespec="microseconds"), bad))
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("ITEMS=%d BAD=%s" % (len(ITEMS), bad))
    print(" | ".join(summary))

if __name__ == "__main__":
    main()
