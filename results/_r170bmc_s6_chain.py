"""r170 bm-c S6 chain runner (30 legs + 3 no-new-bar skipped legs).

Same single-loop clean shape as r168/r160. Gating honest: panel latest bar
2026-09-24 (09-25 Mid-Autumn, weekend, Monday 09-28 bar lands post-15:30).
rc=2/3 reported verbatim. bm-c lane legs honest no-op per host guard.
"""
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PY = sys.executable
LEGS = [
    ("compute_audit", [PY, "scripts\\compute_audit.py"]),
    ("py_watermark_probe", [PY, "scripts\\py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts\\update_daily.py"]),
    ("market_regime", [PY, "scripts\\market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts\\update_lhb.py"]),
    ("update_heat", [PY, "scripts\\update_heat.py"]),
    ("update_futures", [PY, "scripts\\update_futures.py"]),
    ("update_repo", [PY, "scripts\\update_repo.py"]),
    ("update_options", [PY, "scripts\\update_options.py"]),
    ("update_moneyflow", [PY, "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts\\update_astock_daily.py"]),
    ("rev_osc_signal_export", [PY, "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_ths_panel", [PY, "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts\\ah_panel_puller.py"]),
    ("update_fund_premium_snapshot", [PY, "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts\\update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("t24_prospect_promotion", [PY, "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", [PY, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", [PY, "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts\\daily_scorecard.py"]),
    ("daily_report", [PY, "scripts\\daily_report.py", "run"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts\\token_meter.py"]),
]
SKIPPED = [
    "live.paper (no new bar; REGIME_GUARD anchor gate)",
    "t35_open_fill_verify (no new bar)",
    "t24_prospect_paper (no new bar)",
]

out = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "legs": {}, "skipped": SKIPPED}
fails = []
for name, cmd in LEGS:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        rc, tail = r.returncode, (r.stdout or "").strip()[-260:]
        err_tail = (r.stderr or "").strip()[-200:]
    except subprocess.TimeoutExpired:
        rc, tail, err_tail = "TIMEOUT", "", ""
    out["legs"][name] = {"rc": rc, "sec": round(time.time() - t0, 1),
                         "tail": tail, "err_tail": err_tail}
    flag = "" if rc == 0 else "  <<<< rc=%s" % rc
    print("[%s] rc=%s (%.1fs)%s" % (name, rc, time.time() - t0, flag))
    if tail:
        print("   | " + tail.replace("\n", " | ")[-(240 if not flag else 320):])
    if err_tail and rc != 0:
        print("   ERR| " + err_tail.replace("\n", " | ")[-200:])
    if rc != 0:
        fails.append("%s rc=%s" % (name, rc))

out["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
out["fails"] = fails
out["total"] = len(LEGS) + len(SKIPPED)
with open(r"results\_r170bmc_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("SUMMARY: %d legs, %d skipped, fails=%s" % (len(LEGS), len(SKIPPED), fails or "NONE"))
