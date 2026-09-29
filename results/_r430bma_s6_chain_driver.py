"""r430 bm-a S6 maintenance chain driver (37 legs per iteration prompt S6).

Runs each leg via subprocess, prints leg name + rc + last line; on non-zero rc
prints the last 4 lines so honest failures surface as-is (exit codes are never
masked). Legs ordered exactly per Tools/iteration_prompt.txt S6 sequence.
"""
import subprocess
import sys

LEGS = [
    ["python", "scripts/pool_dualrun_reconcile.py", "run"],
    ["python", "scripts/compute_audit.py"],
    ["python", "scripts/py_watermark.py", "probe"],
    ["python", "scripts/update_daily.py"],
    ["python", "scripts/market_regime.py"],
    ["python", "scripts/strategy_scorecard.py"],
    ["python", "scripts/market_clock_call.py", "run"],
    ["python", "scripts/update_lhb.py"],
    ["python", "scripts/update_heat.py"],
    ["python", "scripts/update_futures.py"],
    ["python", "scripts/update_repo.py"],
    ["python", "scripts/update_options.py"],
    ["python", "scripts/update_moneyflow.py"],
    ["python", "scripts/update_sina_mf.py"],
    ["python", "scripts/update_astock_daily.py"],
    ["python", "scripts/update_etf_daily.py"],
    ["python", "scripts/rev_osc_signal_export.py", "run"],
    ["python", "scripts/update_minute_feed.py"],
    ["python", "scripts/update_ths_panel.py"],
    ["python", "scripts/ah_panel_puller.py"],
    ["python", "scripts/update_fund_premium.py", "snapshot"],
    ["python", "scripts/update_fundamental.py"],
    ["python", "-m", "firm.risk.b_layer_filter"],
    ["python", "-m", "live.paper"],
    ["python", "scripts/t35_open_fill_verify.py"],
    ["python", "scripts/t24_prospect_paper.py", "run"],
    ["python", "scripts/t24_prospect_promotion.py", "run"],
    ["python", "scripts/aggressive_lab.py", "paper"],
    ["python", "scripts/alloc_paper.py", "run"],
    ["python", "scripts/grid_paper.py", "run"],
    ["python", "scripts/system_v1_paper.py", "run"],
    ["python", "scripts/t35_paper_export.py", "run"],
    ["python", "scripts/daily_scorecard.py"],
    ["python", "scripts/daily_report.py", "run"],
    ["python", "scripts/ceo_live_usage.py"],
    ["python", "-m", "monitor.build_status"],
    ["python", "scripts/token_meter.py"],
]


def main() -> int:
    bad = 0
    for i, leg in enumerate(LEGS, 1):
        name = " ".join(leg[1:])
        try:
            p = subprocess.run(
                leg, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=1200,
            )
            rc = p.returncode
            out = (p.stdout or "").strip().splitlines()
            err = (p.stderr or "").strip().splitlines()
            tail = out[-1:] if out else (err[-1:] if err else ["<no output>"])
            print(f"[{i:02d}/37] rc={rc} {name} :: {tail[-1][:180]}")
            if rc != 0:
                bad += 1
                lines = (out + err)[-4:]
                for ln in lines:
                    print(f"    >> {ln[:240]}")
        except subprocess.TimeoutExpired:
            bad += 1
            print(f"[{i:02d}/37] TIMEOUT {name}")
        except Exception as exc:  # driver-level failure, honest
            bad += 1
            print(f"[{i:02d}/37] DRIVER-ERR {name}: {exc}")
    print(f"CHAIN DONE: {len(LEGS)} legs, {bad} non-zero")
    return 0


if __name__ == "__main__":
    sys.exit(main())

