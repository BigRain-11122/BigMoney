"""r452 bm-c merge-resolve: 21 UU faces per r449/r450 recipe.

Classification (ts-honest per r450 take-new-by-ts; ours 07:41-43 > theirs 07:38-39
across all regen faces, both derived from same evidence cutoff 2026-09-30):
- 19 regen/snapshot faces -> checkout --ours (snapshot files, no live appenders;
  r630 marker-surgery prohibition applies to append-only ledgers only)
- compute_audit.json -> cross-machine union by entry identity, latest=newest ts
- token_usage.json -> per-machine union (machines dict merge, per-machine ts)
Guards: post-resolve zero-marker scan on all 21 + JSON reparse + union asserts.
Receipt printed to stdout (committed alongside).
"""
import json
import subprocess

TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
UNION_AUDIT = "results/compute_audit.json"
UNION_TOKEN = "results/token_usage.json"
ALL = TAKE_OURS + [UNION_AUDIT, UNION_TOKEN]


def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL {args}: {r.stderr.decode('utf-8', 'replace')[:300]}")


def show(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL show {stage}:{path}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def main():
    receipt = {"round": "r452 bm-c merge-resolve", "take_ours": len(TAKE_OURS), "resolutions": {}}

    for p in TAKE_OURS:
        run(["git", "checkout", "--ours", "--", p])
        receipt["resolutions"][p] = "ours (newer-ts regen 07:41-43 > bm-a 07:38-39)"

    # compute_audit.json cross-machine union
    ours = json.loads(show(2, UNION_AUDIT).decode("utf-8"))
    theirs = json.loads(show(3, UNION_AUDIT).decode("utf-8"))
    oh, th = ours.get("history", []), theirs.get("history", [])
    seen, union = set(), []
    for e in th + oh:  # theirs first so ours entries win identity ties on later ts sort
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            union.append(e)
    union.sort(key=lambda e: str(e.get("ts", "")))
    latest = union[-1] if union else ours.get("latest")
    merged = dict(ours)
    merged["history"] = union
    merged["latest"] = latest
    with open(UNION_AUDIT, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    receipt["resolutions"][UNION_AUDIT] = f"union hist {len(oh)}+{len(th)}->{len(union)} latest={str(latest.get('ts'))[:19]}"
    assert len(union) >= max(len(oh), len(th)), "union must cover both sides"

    # token_usage.json per-machine union
    ours = json.loads(show(2, UNION_TOKEN).decode("utf-8"))
    theirs = json.loads(show(3, UNION_TOKEN).decode("utf-8"))
    om, tm = ours.get("machines", {}), theirs.get("machines", {})
    merged_m = dict(om)
    for k, v in tm.items():
        if k not in merged_m:
            merged_m[k] = v
        else:
            # per-machine newer-ts wins
            def ts(x):
                return str(x.get("ts", x.get("updated", x.get("generated", ""))))
            if ts(v) > ts(merged_m[k]):
                merged_m[k] = v
    merged = dict(ours)  # ours top-level (newest generated 07:43:09)
    merged["machines"] = merged_m
    with open(UNION_TOKEN, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    receipt["resolutions"][UNION_TOKEN] = f"per-machine union machines ours={sorted(om.keys())} +theirs-keys={sorted(tm.keys())}"

    # stage all
    for p in ALL:
        run(["git", "add", "--", p])

    # guards: zero markers + JSON reparse
    marker_hits = []
    for p in ALL:
        raw = open(p, "rb").read()
        for line in raw.split(b"\n"):
            if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>"):
                marker_hits.append(p)
                break
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8").read())
    assert not marker_hits, f"markers remain: {marker_hits}"
    receipt["guards"] = "zero-marker 21/21 + JSON reparse PASS"
    print(json.dumps(receipt, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
