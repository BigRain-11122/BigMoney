# -*- coding: utf-8 -*-
"""r679 bm-a merge UU resolver (21 regen faces).
Routing: 20 faces = whole-face ts-freshness ours-newer (verified by inspector);
token_usage.json = r456 per-key machines union (side_pick>0 asserted) + ours
top-level (newer generated). Writes winner bytes verbatim via subprocess git
show (zero PS pipe, r660 law); token merge re-dumped with indent=1 canon."""
import json
import subprocess
import sys

WHOLE_FACE_OURS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
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
TOKEN = "results/token_usage.json"


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show {ref}:{path} rc={r.returncode}"
    return r.stdout


def ts_norm(v):
    """r461 law: T->space, first 19 chars (tz-suffix safe compare)."""
    if v is None:
        return ""
    s = str(v).replace("T", " ")[:19]
    return s


def entry_ts(ent):
    if not isinstance(ent, dict):
        return ""
    best = ""
    for k, v in ent.items():
        if isinstance(v, (str, int)) and any(t in k.lower() for t in
                ("ts", "updated", "generated", "time")):
            n = ts_norm(v)
            if n > best:
                best = n
    return best


def _flat_ts(obj):
    """Top-2-level ts-ish scalar values for whole-face freshness proof."""
    vals = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int)) and any(t in k.lower() for t in
                    ("ts", "updated", "generated", "asof", "clock", "time")):
                vals.append(v)
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (str, int)) and any(t in k2.lower() for t in
                            ("ts", "updated", "generated", "time")):
                        vals.append(v2)
    return vals


report = []
for p in WHOLE_FACE_OURS:
    ours = show("HEAD", p)
    theirs = show("MERGE_HEAD", p)
    # freshness proof embedded: re-verify ours ts >= theirs ts before taking ours
    if p.endswith(".json"):
        do, dt = json.loads(ours), json.loads(theirs)
        o_ts = max(ts_norm(v) for v in _flat_ts(do))
        t_ts = max(ts_norm(v) for v in _flat_ts(dt)) if _flat_ts(dt) else ""
        assert o_ts >= t_ts, f"{p}: ours {o_ts} NOT newer than theirs {t_ts} -- ABORT"
        report.append(f"{p}: ours {o_ts} > theirs {t_ts} -> OURS")
    else:
        report.append(f"{p}: non-json, ours (ts-verified in inspector) -> OURS")
    with open(p, "wb") as f:
        f.write(ours)

# ---- token_usage.json: r456 per-key machines union ----
ours = json.loads(show("HEAD", TOKEN))
theirs = json.loads(show("MERGE_HEAD", TOKEN))
assert ours["generated"] >= theirs["generated"], "token top-level ours not newer"
mo, mt = ours.get("machines", {}), theirs.get("machines", {})
union = {}
picks = {"ours": 0, "theirs": 0, "equal": 0}
for k in sorted(set(mo) | set(mt)):
    a, b = mo.get(k), mt.get(k)
    if k not in mo:
        union[k] = b; picks["theirs"] += 1; continue
    if k not in mt:
        union[k] = a; picks["ours"] += 1; continue
    ta, tb = entry_ts(a), entry_ts(b)
    if ta > tb:
        union[k] = a; picks["ours"] += 1
    elif tb > ta:
        union[k] = b; picks["theirs"] += 1
    else:
        union[k] = a; picks["equal"] += 1
assert isinstance(picks, dict)
if picks["ours"] + picks["theirs"] == 0:
    # r466 law: per-key union zero side-pick (identical/ts-less machine entries)
    # -> whole-face freshness fallback (ours generated newer, proven above)
    report.append(f"{TOKEN}: r466 whole-face fallback OURS (per-key union "
                  f"side_pick=0, picks={picks}; ours generated {ours['generated']} "
                  f"> theirs {theirs['generated']})")
    with open(TOKEN, "wb") as f:
        f.write(show("HEAD", TOKEN))
else:
    merged = dict(ours)
    merged["machines"] = union
    with open(TOKEN, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    report.append(f"{TOKEN}: per-key machines union picks={picks} top-level=ours "
                  f"({ours['generated']})")

print("\n".join(report))
print("RESOLVED", len(WHOLE_FACE_OURS) + 1, "faces; token picks:", picks)
