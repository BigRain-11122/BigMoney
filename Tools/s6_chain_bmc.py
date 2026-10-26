"""bm-c S6 chain runner (reusable).

Runs the 42 S6 data/panel maintenance legs in the order fixed by the round
prompt, records {leg, rc, elapsed} for each into
results/_r<round>bmc_s6_chain.json and prints a compact tail summary.

Usage: python Tools\\s6_chain_bmc.py <round_no>
Exit 0 always (legs are recorded; non-zero legs are reported, not fatal) --
the round report must surface any rc!=0 leg verbatim.

Why a shared runner: the per-round chain used to be an ad-hoc script rebuilt
every window (r1179..r1182 clones) which cost most of the round's wall time in
generation rather than measurement.
"""
import json
import subprocess
import sys
import time
from datetime import datetime

LEGS = [
    ("dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts/update_zt_pool.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    # Both panel lanes are bm-b's (R31 lane law). bm-b's heartbeat has been silent
    # for days while these legs ran, so the chain passes the standing --takeover
    # consent r1276 established: the flag is only half the gate -- each script still
    # refuses unless the owner heartbeat is stale by >= TAKEOVER_STALE_MIN, so a
    # healthy bm-b keeps ownership and this machine just prints its honest no-op.
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py",
                             "--takeover"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py", "--takeover"]),
    # The production book's two live faces ride right behind the panel leg they read.
    # etf_book_forward appends one mark per new bar (idempotent; exit 3 freezes the
    # ledger instead of rewriting history) and etf_book_order re-emits the executable
    # ticket. Both were hand-run only until r1275, so the accrual depended on a session
    # remembering to call them -- r1267, r1269 and r1273 each named that as owed.
    ("etf_book_forward", ["python", "scripts/etf_book_forward.py"]),
    ("etf_book_order", ["python", "scripts/etf_book_order.py", "run"]),
    ("regime_thermo", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel", ["python", "scripts/ah_panel_puller.py"]),
    ("fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("t24_paper", ["python", "scripts/t24_prospect_paper.py", "run"]),
    ("t24_promote", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("aggr_paper", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t35_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("scorecard_daily", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
    # O-20261026-0810-bm-a 4 handed this side the fix: the heartbeat carried 25 GPU
    # keys from a dozen per-round closeouts, disagreeing by up to 13 GB, with
    # gpu_util_pct pinned to a literal 0 -- a fleet audit was reading a random
    # round's snapshot. gpu_face re-probes once and rewrites every alias from that
    # one reading, so the face is consistent without a session remembering to do it.
    ("gpu_face", ["python", "Tools/gpu_face.py", "apply"]),
]


def main():
    round_no = sys.argv[1] if len(sys.argv) > 1 else "0"
    out = []
    for name, cmd in LEGS:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            rc = r.returncode
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc = 124
            tail = ["TIMEOUT"]
        el = round(time.time() - t0, 1)
        out.append({"leg": name, "rc": rc, "elapsed_sec": el,
                    "tail": tail[0][:220]})
        print(f"{rc:3d} {name:18s} {el:7.1f}s {tail[0][:120]}", flush=True)

    path = f"results/_r{round_no}bmc_s6_chain.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    bad = [o for o in out if o["rc"] != 0]
    print(f"chain: {len(out)-len(bad)}/{len(out)} rc0 -> {path} "
          f"({datetime.now().isoformat(timespec='seconds')})")
    if bad:
        print("NONZERO: " + ", ".join(f"{o['leg']}={o['rc']}" for o in bad))


if __name__ == "__main__":
    main()