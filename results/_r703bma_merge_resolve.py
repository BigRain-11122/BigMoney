# r703 bm-a merge resolver: 17 UU regen faces -> per-face ts-newer-wins (r437/r690 canon)
# + token_usage.json per-key union (r466) + twins locked to json side pick
import subprocess, json, sys

UU = [
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
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout

def ts_of(data, path):
    """Extract a comparable timestamp string from a face blob."""
    try:
        d = json.loads(data.decode("utf-8", errors="replace"))
    except Exception:
        # md/js twins: no ts inside -- locked to twin decision elsewhere
        return None
    for k in ("generated", "generated_at", "ts", "as_of", "updated_at", "last_update"):
        if isinstance(d, dict) and k in d and isinstance(d[k], str):
            return d[k]
    if isinstance(d, dict):
        for k in ("generated", "generated_at"):
            v = d.get(k)
            if isinstance(v, dict):
                for kk in ("iso", "ts", "at"):
                    if isinstance(v.get(kk), str):
                        return v[kk]
    return None

decisions = {}
for p in UU:
    ours = blob(":2", p)
    theirs = blob(":3", p)
    if p == "results/token_usage.json":
        decisions[p] = "UNION"
        continue
    to, tt = ts_of(ours, p), ts_of(theirs, p)
    if to and tt:
        decisions[p] = "ours" if to >= tt else "theirs"
        decisions[p] += f" (ours_ts={to} theirs_ts={tt})"
    else:
        # md/js twin or no ts: defer to twin pairing
        decisions[p] = "TWIN-DEFER"

# twins locked to json side
twins = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
for md, js in twins.items():
    base = decisions.get(js, "theirs (no ts)")
    side = "ours" if base.startswith("ours") else "theirs"
    decisions[md] = f"{side} (twin-locked to {js})"

print("== DECISIONS ==")
for p in UU:
    print(f"  {p}: {decisions.get(p)}")

# apply non-union, non-defer decisions
for p in UU:
    dec = decisions.get(p, "")
    if dec.startswith("ours"):
        subprocess.run(["git", "checkout", "--ours", p], capture_output=True)
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"RESOLVED ours: {p}")
    elif dec.startswith("theirs"):
        subprocess.run(["git", "checkout", "--theirs", p], capture_output=True)
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"RESOLVED theirs: {p}")
    elif dec == "UNION":
        print(f"DEFER UNION: {p}")
    else:
        print(f"DEFER: {p} ({dec})")
