"""r586 bm-b S0 pure-FF face-by-face checkout (r578/r580 law).
Origin advanced e77cad0bb -> e79dcf6b4 (bm-c r377 wrap x2 + bm-a r587 wrap).
Working tree classification:
  KEEP LOCAL (bm-b live-writer faces, will ride this round's commit):
    autofill_state.bm-b.json / saturation_engine {face,history,ledger,state}_bm-b
    pool_core_samples.jsonl (= origin verbatim + 12 pure-append local burn samples, already the union)
  TAKE ORIGIN (shared derive / other-machine faces, local copies stale vs newer pushes)
  RESTORE D files (bm-c work scripts + W106 seat MSG archived on origin)
  DELETE untracked inbox MSG copy (blob-identical to origin processed copy e157a48e2)
"""
import os
import subprocess

TAKE_ORIGIN = [
    "docs/daily_report/REPORT-2026-10-02.json",
    "docs/daily_report/REPORT-2026-10-02.md",
    "docs/live_usage/LIVE-2026-10-02.json",
    "docs/live_usage/LIVE-2026-10-02.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "fleet/inbox/processed/MSG-20261002-1733-bmb-w106-seat.md",
    "fleet/machines/bm-a.json",
    "fleet/machines/bm-c.json",
    "fleet/tasks/T-2026-09-30-126-P1.json",
    "results/_attrition_guard_scan.json",
    "results/_r377bmc_reparent.py",
    "results/_r377bmc_reparent2.py",
    "results/_r377bmc_wrap.py",
    "results/autofill_state.bm-c.json",
    "results/compute_audit.bm-a.json",
    "results/compute_audit.bm-c.json",
    "results/compute_audit.json",
    "results/daily_scorecard.html",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/dispatcher_state.bm-c.json",
    "results/fund_premium_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-a.json",
    "results/futures_update_status.bm-c.json",
    "results/futures_update_status.json",
    "results/heat_update_status.bm-a.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.bm-a.json",
    "results/lhb_update_status.bm-c.json",
    "results/lhb_update_status.json",
    "results/options_update_status.json",
    "results/p1d_gates.json",
    "results/pool_dualrun.bm-a.jsonl",
    "results/pool_dualrun.bm-c.jsonl",
    "results/regime_state.bm-a.json",
    "results/regime_state.bm-c.json",
    "results/regime_state.json",
    "results/repo_update_status.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/scorecard_v1.json",
    "results/sina_mf_update_status.json",
    "results/strategy_scorecard.json",
    "results/token_usage.bm-a.json",
    "results/token_usage.bm-c.json",
    "results/token_usage.json",
    "results/update_status.bm-a.json",
    "results/update_status.bm-c.json",
    "results/update_status.json",
    "round_reports-bm-a.md",
    "round_reports-bm-c.md",
    "state-bm-a.json",
    "state-bm-c.json",
]

r = subprocess.run(["git", "checkout", "--"] + TAKE_ORIGIN, capture_output=True, text=True)
if r.returncode != 0:
    print("CHECKOUT FAIL:", r.stderr)
    raise SystemExit(1)

inbox_copy = "fleet/inbox/MSG-20261002-1733-bmb-w106-seat.md"
if os.path.exists(inbox_copy):
    os.remove(inbox_copy)
    print("removed untracked inbox MSG copy (blob-identical to origin processed)")

print("checkout-ok", len(TAKE_ORIGIN), "faces")
