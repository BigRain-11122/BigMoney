# r240 bm-c S6 chain runner (37 legs, r239 mirror; no new bar since 09-29 20:36 klc2 landing -> no REGIME_GUARD enforce) (37 legs, r238 mirror)
# GBK-console law (r236): reconfigure stdout utf-8 + child capture utf-8
# errors=replace + snip re-encode double insurance. Evidence ->
# results/_r240bmc_s6_chain.json (per-leg rc + tail, non-green surfaced).
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    "python scripts/pool_dualrun_reconcile.py run",
    "python scripts/compute_audit.py",
    "python scripts/py_watermark.py probe",
    "python scripts/update_daily.py",
    "python scripts/market_regime.py",
    "python scripts/strategy_scorecard.py",
    "python scripts/market_clock_call.py run",
    "python scripts/update_lhb.py",
    "python scripts/update_heat.py",
    "python scripts/update_futures.py",
    "python scripts/update_repo.py",
    "python scripts/update_options.py",
    "python scripts/update_moneyflow.py",
    "python scripts/update_sina_mf.py",
    "python scripts/update_astock_daily.py",
    "python scripts/update_etf_daily.py",
    "python scripts/rev_osc_signal_export.py run",
    "python scripts/update_minute_feed.py",
    "python scripts/update_ths_panel.py",
    "python scripts/ah_panel_puller.py",
    "python scripts/update_fund_premium.py snapshot",
    "python scripts/update_fundamental.py",
    "python -m firm.risk.b_layer_filter",
    "python -m live.paper",
    "python scripts/t35_open_fill_verify.py",
    "python scripts/t24_prospect_paper.py run",
    "python scripts/t24_prospect_promotion.py run",
    "python scripts/aggressive_lab.py paper",
    "python scripts/alloc_paper.py run",
    "python scripts/grid_paper.py run",
    "python scripts/system_v1_paper.py run",
    "python scripts/t35_paper_export.py run",
    "python scripts/daily_scorecard.py",
    "python scripts/daily_report.py run",
    "python scripts/ceo_live_usage.py",
    "python -m monitor.build_status",
    "python scripts/token_meter.py",
]


def run_leg(cmd):
    # live.paper enforce env is set ONLY when a new bar landed (protocol);
    # r239 face: 09-29 bar klc2 night-publish still pending -> no enforce.
    cp = subprocess.run(
        cmd.split(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    tail = ((cp.stdout or "") + (cp.stderr or "")).strip().splitlines()
    snip = tail[-1] if tail else ""
    snip = snip.encode("utf-8", "replace").decode("utf-8", "replace")[:400]
    return {"rc": cp.returncode, "tail": snip}


out = {
    "runner": "_r240bmc_s6_chain.py",
    "machine": "bm-c",
    "round": "r240",
    "legs": {},
}
non_green = []
for cmd in LEGS:
    r = run_leg(cmd)
    out["legs"][cmd] = r
    if r["rc"] != 0:
        non_green.append((cmd, r["rc"], r["tail"]))
    print(f"rc={r['rc']} | {cmd}")

with open("results/_r240bmc_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("non_green:", json.dumps(non_green, ensure_ascii=False)[:800])
