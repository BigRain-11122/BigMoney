"""r390 bm-b S6 chain runner (r171 precedent pattern, per-leg rc capture).

Writes results/_r390bmb_s6_chain.json evidence. Honest: leg rc recorded
as-is; nonzero rc(2/3) legs are reported verbatim per law (never masked).
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
OUT = os.path.join(ROOT, "results", "_r390bmb_s6_chain.json")

LEGS = [
    ("compute_audit", ["scripts/compute_audit.py"], None),
    ("py_watermark_probe", ["scripts/py_watermark.py", "probe"], None),
    ("update_daily", ["scripts/update_daily.py"], None),
    ("market_regime", ["scripts/market_regime.py"], None),
    ("strategy_scorecard", ["scripts/strategy_scorecard.py"], None),
    ("market_clock_call", ["scripts/market_clock_call.py", "run"], None),
    ("update_lhb", ["scripts/update_lhb.py"], None),
    ("update_heat", ["scripts/update_heat.py"], None),
    ("update_futures", ["scripts/update_futures.py"], None),
    ("update_repo", ["scripts/update_repo.py"], None),
    ("update_options", ["scripts/update_options.py"], None),
    ("update_moneyflow", ["scripts/update_moneyflow.py"], None),
    ("update_sina_mf", ["scripts/update_sina_mf.py"], None),
    ("update_astock_daily", ["scripts/update_astock_daily.py"], None),
    ("rev_osc_signal_export", ["scripts/rev_osc_signal_export.py", "run"], None),
    ("update_minute_feed", ["scripts/update_minute_feed.py"], None),
    ("update_ths_panel", ["scripts/update_ths_panel.py"], None),
    ("ah_panel_puller", ["scripts/ah_panel_puller.py"], None),
    ("update_fund_premium", ["scripts/update_fund_premium.py", "snapshot"], None),
    ("update_fundamental", ["scripts/update_fundamental.py"], None),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"], None),
    ("live_paper", ["-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", ["scripts/t35_open_fill_verify.py"], None),
    ("t24_prospect_paper", ["scripts/t24_prospect_paper.py", "run"], None),
    ("t24_prospect_promotion", ["scripts/t24_prospect_promotion.py", "run"], None),
    ("aggressive_lab", ["scripts/aggressive_lab.py", "paper"], None),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"], None),
    ("grid_paper", ["scripts/grid_paper.py", "run"], None),
    ("system_v1_paper", ["scripts/system_v1_paper.py", "run"], None),
    ("t35_paper_export", ["scripts/t35_paper_export.py", "run"], None),
    ("daily_scorecard", ["scripts/daily_scorecard.py"], None),
    ("daily_report", ["scripts/daily_report.py", "run"], None),
    ("build_status", ["-m", "monitor.build_status"], None),
    ("token_meter", ["scripts/token_meter.py"], None),
]


def main():
    rows = []
    for name, args, extra_env in LEGS:
        cmd = [PY] + args
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        t0 = time.time()
        try:
            p = subprocess.run(
                cmd, cwd=ROOT, env=env, capture_output=True,
                text=True, encoding="utf-8", errors="replace",
                timeout=900)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = 99, "TIMEOUT after 900s"
        tail = "\n".join(out.strip().splitlines()[-6:])
        rows.append({"leg": name, "rc": rc, "sec": round(time.time() - t0, 1),
                     "tail": tail})
        flag = "OK " if rc == 0 else f"RC={rc} ***"
        print(f"[{flag}] {name} ({rows[-1]['sec']}s)")
    payload = {"runner": "results/_r390bmb_s6_chain.py", "machine": "bm-b",
               "round": 390, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
               "legs": rows,
               "n_ok": sum(1 for r in rows if r["rc"] == 0),
               "n_bad": sum(1 for r in rows if r["rc"] != 0)}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"S6 chain: {payload['n_ok']}/{len(rows)} rc=0, "
          f"{payload['n_bad']} nonzero -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
