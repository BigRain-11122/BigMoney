"""r687 bm-a S6 maintenance chain (37 legs, canonical order; live.paper
skipped honestly per r660 golden-week no-new-bar precedent, noted in log).
Copy-adapted from _r686bma_s6_chain.py per r461 law (no blind cross-round reuse).
Exit-code contract per gate; nonzero legs surfaced honestly."""
import json
import subprocess
import sys
import time

LEGS = [
    ("pool_dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py",
                                "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py",
                             "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python",
                                "scripts/update_fund_statements.py"]),
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py",
                            "run"]),
    ("t24_prospect_promotion", ["python",
                                "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["python", "scripts/aggressive_lab.py", "paper"]),
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
SKIP_NOTE = ("live.paper SKIPPED: golden week, no new bar (r660 precedent; "
             "REGIME_GUARD not set, anchor registry untouched)")


def main():
    t0 = time.time()
    out = []
    fails = 0
    for name, cmd in LEGS:
        ts = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=240)
            rc = r.returncode
            tail = (r.stdout.decode("utf-8", "replace").strip().splitlines()[-1:]
                    if r.stdout else [""])[0][:160]
            err = ""
        except subprocess.TimeoutExpired:
            rc, tail, err = 124, "TIMEOUT-240s", "leg exceeded 240s cap"
        if rc != 0:
            fails += 1
            err = err or r.stderr.decode("utf-8", "replace").strip()[-200:]
            rec = {"leg": name, "rc": rc, "sec": round(time.time() - ts, 1),
                   "tail": tail, "stderr_tail": err}
            print(f"[{name}] rc={rc} {tail} | {err}", flush=True)
        else:
            rec = {"leg": name, "rc": rc, "sec": round(time.time() - ts, 1),
                   "tail": tail}
            print(f"[{name}] rc=0 {tail}", flush=True)
        out.append(rec)
        # crash-safe incremental log (r680: end-only log lost to harness kill)
        with open("results/_r687bma_s6_log.txt", "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump({"round": "r687", "machine": "bm-a", "n_legs": len(LEGS),
                       "n_fail": fails, "skip_note": SKIP_NOTE,
                       "elapsed_sec": round(time.time() - t0, 1), "legs": out},
                      fh, ensure_ascii=False, indent=1)
    print(f"S6 CHAIN: {len(LEGS)} legs, {fails} nonzero-rc, "
          f"elapsed {time.time() - t0:.1f}s", flush=True)
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

