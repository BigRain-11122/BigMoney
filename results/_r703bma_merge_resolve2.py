# r703 bm-a merge resolver leg-2: TWIN-DEFER faces ts decision (updated/meta.generated/latest keys)
import subprocess, json

FACES = {
    "results/compute_audit.json": lambda d: (d.get("latest") or {}).get("generated") or (d.get("latest") or {}).get("ts"),
    "results/dashboard_status.json": lambda d: (d.get("meta") or {}).get("generated"),
    "results/fundamental_b_layer_filter.json": lambda d: d.get("updated"),
    "results/lhb_update_status.json": lambda d: d.get("updated"),
    "results/regime_state.json": lambda d: d.get("updated"),
    "results/update_status.json": lambda d: d.get("updated"),
}

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout

for p, get_ts in FACES.items():
    try:
        o = json.loads(blob(":2", p).decode("utf-8", errors="replace"))
        t = json.loads(blob(":3", p).decode("utf-8", errors="replace"))
        to, tt = get_ts(o), get_ts(t)
        side = "ours" if (to or "") >= (tt or "") else "theirs"
        print(f"{p}: ours_ts={to} theirs_ts={tt} -> {side}")
        subprocess.run(["git", "checkout", "--" + side, p], capture_output=True)
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"RESOLVED {side}: {p}")
    except Exception as e:
        print(f"{p}: ERROR {e}")

# token_usage.json per-key union (r466): side_pick by per-key generated ts, union keys
import io
p = "results/token_usage.json"
o = json.loads(blob(":2", p).decode("utf-8", errors="replace"))
t = json.loads(blob(":3", p).decode("utf-8", errors="replace"))
side_picks = {"ours": 0, "theirs": 0}
merged = {}
for k in set(list(o.keys()) + list(t.keys())):
    ov, tv = o.get(k), t.get(k)
    if isinstance(ov, dict) and isinstance(tv, dict):
        og = str(ov.get("generated", ""))
        tg = str(tv.get("generated", ""))
        if og >= tg:
            merged[k] = ov
            side_picks["ours"] += 1
        else:
            merged[k] = tv
            side_picks["theirs"] += 1
    elif ov is not None and tv is None:
        merged[k] = ov
        side_picks["ours"] += 1
    elif tv is not None and ov is None:
        merged[k] = tv
        side_picks["theirs"] += 1
    else:
        merged[k] = ov
        side_picks["ours"] += 1
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
subprocess.run(["git", "add", p], capture_output=True)
print(f"token_usage UNION keys={len(merged)} side_pick={side_picks}")

# dashboard_status.js twin alignment with dashboard_status.json decision (json = ours? align)
js = "results/dashboard_status.js"
jn = "results/dashboard_status.json"
jn_ours = json.loads(blob(":2", jn).decode("utf-8", errors="replace"))
jn_added = json.loads(open(jn, encoding="utf-8").read()) if True else None
jn_side_ours = str((jn_ours.get("meta") or {}).get("generated")) == str((jn_added.get("meta") or {}).get("generated"))
side = "ours" if jn_side_ours else "theirs"
subprocess.run(["git", "checkout", "--" + side, js], capture_output=True)
subprocess.run(["git", "add", js], capture_output=True)
print(f"dashboard_status.js twin-aligned {side}")
