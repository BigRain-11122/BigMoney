# -*- coding: utf-8 -*-
"""r683 bm-a merge UU resolver (19 faces, direction = origin-newer-wins).
Routing: 18 S6 regen snapshot faces = whole-face ts-freshness THEIRS-newer
(bm-b S6 wave 15:35 > ours 15:31, r440 S6-renewable origin-newer-wins);
token_usage.json = r456/r679 per-key machines union (side_pick>0 asserted,
r466 whole-face freshness fallback if zero) + newer-generated top-level;
pool_core_samples.jsonl (auto-merged append-only) = line-set zero-loss
containment proof (r656 law family). Writes winner bytes verbatim via
subprocess git show (zero PS pipe, r660 law)."""
import json
import subprocess
import sys

WHOLE_FACE_THEIRS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
TOKEN = "results/token_usage.json"
POOL_SAMPLES = "results/pool_core_samples.jsonl"
report = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show {ref}:{path} rc={r.returncode} {r.stderr[:200]!r}"
    return r.stdout


def ts_norm(v):
    """r461 law: T->space, first 19 chars (tz-suffix safe compare).
    Only accepts date-shaped values (YYYY-MM-DD...); numeric noise
    like elapsed/counts (830 vs 837) is rejected (r641 false-signal law)."""
    if v is None:
        return ""
    s = str(v)
    if len(s) < 10 or s[4] != "-" or s[7] != "-":
        return ""
    return s.replace("T", " ")[:19]


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


TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
decision = {}
for p in WHOLE_FACE_THEIRS:
    if p in TWIN_OF:
        continue  # processed after its json twin
    ours = show("HEAD", p)
    theirs = show("MERGE_HEAD", p)
    do, dt = json.loads(ours), json.loads(theirs)
    o_ts = max(ts_norm(v) for v in _flat_ts(do))
    t_ts = max(ts_norm(v) for v in _flat_ts(dt)) if _flat_ts(dt) else ""
    take_theirs = t_ts >= o_ts
    decision[p] = take_theirs
    with open(p, "wb") as f:
        f.write(theirs if take_theirs else ours)
    report.append(f"{p}: ours {o_ts} vs theirs {t_ts} -> "
                  f"{'THEIRS' if take_theirs else 'OURS'}")
for p, twin in TWIN_OF.items():
    take_theirs = decision[twin]
    with open(p, "wb") as f:
        f.write(show("MERGE_HEAD", p) if take_theirs else show("HEAD", p))
    report.append(f"{p}: follows json twin -> {'THEIRS' if take_theirs else 'OURS'}")

# ---- token_usage.json: r456/r679 per-key machines union ----
ours = json.loads(show("HEAD", TOKEN))
theirs = json.loads(show("MERGE_HEAD", TOKEN))
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
if picks["ours"] + picks["theirs"] == 0:
    # r466 law: per-key union zero side-pick -> whole-face freshness fallback
    o_g, t_g = ts_norm(ours.get("generated")), ts_norm(theirs.get("generated"))
    winner, wref = (ours, "HEAD") if o_g >= t_g else (theirs, "MERGE_HEAD")
    with open(TOKEN, "wb") as f:
        f.write(show(wref, TOKEN))
    report.append(f"{TOKEN}: r466 whole-face fallback {wref} "
                  f"(side_pick=0, picks={picks}; ours gen {o_g} vs theirs gen {t_g})")
else:
    base = ours if ts_norm(ours.get("generated")) >= ts_norm(theirs.get("generated")) \
        else theirs
    merged = dict(base)
    merged["machines"] = union
    with open(TOKEN, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    report.append(f"{TOKEN}: per-key machines union picks={picks} "
                  f"top-level={'ours' if base is ours else 'theirs'} "
                  f"({base.get('generated')})")

# ---- pool_core_samples.jsonl: auto-merged append-only zero-loss proof ----
h_lines = set(show("HEAD", POOL_SAMPLES).decode("utf-8", "replace").splitlines())
m_lines = set(show("MERGE_HEAD", POOL_SAMPLES).decode("utf-8", "replace").splitlines())
merged_lines = set(open(POOL_SAMPLES, encoding="utf-8", errors="replace").read().splitlines())
missing_h = h_lines - merged_lines
missing_m = m_lines - merged_lines
assert not missing_h and not missing_m, \
    f"pool_core_samples zero-loss FAIL: head-missing={len(missing_h)} " \
    f"merge-missing={len(missing_m)}"
report.append(f"{POOL_SAMPLES}: zero-loss containment PASS "
              f"(head={len(h_lines)} mergehead={len(m_lines)} merged={len(merged_lines)})")

print("\n".join(report))
print("RESOLVED", len(WHOLE_FACE_THEIRS) + 1, "UU faces + 1 zero-loss proof; "
      "token picks:", picks)
