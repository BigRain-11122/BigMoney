# r602 bm-b closeout: targeted staging (r580 python-argv law), staged-set self-proof (r385),
# -F commit (r375), push, delivery self-verify (O-20261001-1108).
import subprocess, sys

FILES = [
    # bookkeeping (round report + state + heartbeat; CODELY zero-new-lesson this round)
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    # S6 derive faces (this round's chain outputs; golden-week no-op faces byte-stable)
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/astock_daily_update_status.json",
    "results/compute_audit.bm-b.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/etf_daily_pull_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-b.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.bm-b.json",
    "results/lhb_update_status.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.bm-b.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.bm-b.json",
    "results/token_usage.json",
    "results/update_status.bm-b.json",
    "results/update_status.json",
    # round artifacts/receipts
    "results/_r602bmb_s6_runner.ps1",
    "results/_r602bmb_s6_verdicts.py",
    "results/_r602bmb_bookkeep.py",
]
# EXCLUDED by design: autofill_state.bm-b.json / p1d_gates.json / pool_core_samples.jsonl /
# saturation_engine/* (daemon live-writes, tick self-commits per r290);
# fund_value_p1/nulls.jsonl (IN-FLIGHT burn live-write, r532);
# _r603bmb_sens_partial_killed.jsonl (superseded duplicate awaiting bm-a canonical).

def run(args):
    p = subprocess.run(["git"] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr

rc, out, err = run(["add"] + FILES)
print("add rc:", rc, err.decode("utf-8", "replace")[:400] if rc else "")
if rc != 0:
    sys.exit(1)

# staged-set self-proof: bookkeeping trio present, no live-write faces staged, no deletions
rc, out, _ = run(["diff", "--cached", "--name-status"])
staged = out.decode("utf-8", "replace").splitlines()
kinds = {}
for ln in staged:
    parts = ln.split("\t")
    kinds.setdefault(parts[0], []).append(parts[-1])
must = {"state.json", "fleet/machines/bm-b.json", "logs/iteration-loop/round_reports.md"}
have = set(kinds.get("A", []) + kinds.get("M", []))
missing = must - have
print("staged files:", len(staged), "| kinds:", {k: len(v) for k, v in kinds.items()})
print("bookkeeping trio staged:", not missing, "| missing:", missing or "none")
d_lines = [ln for ln in staged if "\tD" in ln or ln.startswith("D")]
print("deletion rows in staged:", len(d_lines))
bad = [f for f in ("autofill_state.bm-b.json", "p1d_gates.json", "pool_core_samples.jsonl",
                  "fund_value_p1/nulls.jsonl", "_r603bmb_sens_partial_killed.jsonl")
       if f in have or any(f in v for v in kinds.values())]
print("forbidden live-write faces staged:", bad or "none")
if missing or d_lines or bad:
    print("ABORT closeout: staged-set self-proof failed")
    sys.exit(2)

rc, out, err = run(["commit", "-F", r".codely-cli\scratch\r602_closeout_msg.txt"])
print("commit rc:", rc)
print(out.decode("utf-8", "replace")[:600])
if rc != 0:
    print(err.decode("utf-8", "replace")[:600])
    sys.exit(3)
