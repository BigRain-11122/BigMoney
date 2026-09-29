"""r436 bm-b rebase conflict resolver (17 UU, canon per bigmoney-conflict-resolve SKILL).

Classification (classifier 9 + 8 manual):
- rolling-ledger: compute_audit.json -> history union by ts (|A∪B|=202 zero loss), latest=take-new(origin)
- regime_state.json: histories byte-identical both sides -> snapshot take-origin (state fields fresher)
- js-wrapper-snapshot: dashboard_status.js -> take-side whole bytes = origin (per R209, no re-emit)
- snapshots (take-new by ts, origin fresher on ALL per probe r436):
  dashboard_status.json, fundamental_b_layer_filter.json, futures_update_status.json,
  lhb_update_status.json, token_usage.json, update_status.json
- manual UNKNOWN->same-day idempotent regenerate faces (T-75/T-105, take-new by generated_at):
  docs/daily_report/REPORT-2026-09-29.{json,md}, docs/live_usage/LIVE-2026-09-29.{json,md}, LIVE-latest.{json,md}
- manual UNKNOWN->per-round re-derived snapshot (take-new by generated; strategy_scorecard host=bm-a origin authoritative):
  results/scorecard_v1.json, results/strategy_scorecard.json

Freshness evidence (probe _r436bmb_conflict_probe.py): origin 17:35:11-17:36:00 vs local 17:30:41-17:34:48, origin wins every file.
"""
import json
import subprocess
import sys

TAKE_OURS = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

UNION_LEDGER = "results/compute_audit.json"


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"blob read fail {stage}:{path}: {r.stderr.decode()[:200]}")
    return json.loads(r.stdout)


def union_audit():
    ours = blob(2, UNION_LEDGER)
    theirs = blob(3, UNION_LEDGER)
    rows = {}
    for r in theirs["history"] + ours["history"]:
        rows[r["ts"]] = r  # same-ts dedupe; identical shared rows collapse
    union = sorted(rows.values(), key=lambda r: r["ts"])
    out = dict(ours)  # state fields take-new = ours (17:35:11 > 17:30:41)
    out["history"] = union
    n_a, n_b = len(ours["history"]), len(theirs["history"])
    assert len(union) == len(set(r["ts"] for r in union))
    # zero-loss check: union superset of both
    ts_u = set(rows)
    assert ts_u >= set(r["ts"] for r in ours["history"]) and ts_u >= set(r["ts"] for r in theirs["history"])
    with open(UNION_LEDGER, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"compute_audit union: |ours|={n_a} |theirs|={n_b} -> |A∪B|={len(union)} latest.ts={out['latest']['ts']}")
    return out


def main():
    union_audit()
    for p in TAKE_OURS:
        subprocess.run(["git", "checkout", "--ours", p], check=True)
    # validate every json parses post-resolution
    for p in [UNION_LEDGER] + [x for x in TAKE_OURS if x.endswith(".json")]:
        json.load(open(p, encoding="utf-8"))
    subprocess.run(["git", "add", UNION_LEDGER] + TAKE_OURS, check=True)
    print(f"resolved+added {len(TAKE_OURS) + 1} files; all JSON validated")


if __name__ == "__main__":
    main()
