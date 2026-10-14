# -*- coding: utf-8 -*-
# r988 bm-a rebase resolver: shared regen faces -- canon laws (r907/r910/r943)
# 13 UU: compute_audit(history-union) / regime_state(union) / token_usage(per-machine union)
#        REPORT+LIVE twins(take-newer=stage3 mine 14:05-14:09 vs bm-b ~13:5x)
#        futures/lhb/update_status/fundamental_b_layer_filter (snapshot take-newer)
import json, subprocess, sys, os

G = r"C:\Program Files\Git\cmd\git.exe"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def show(rev, path):
    r = subprocess.run([G, "show", f"{rev}:{path}"], capture_output=True, cwd=ROOT)
    return r.stdout

def side(which, path):
    # which 2 = ours (origin/bm-b side, the new base), 3 = theirs (my replayed commit)
    r = subprocess.run([G, "show", f":{which}:{path}"], capture_output=True, cwd=ROOT)
    return r.stdout

faces_union_hist = ["results/compute_audit.json"]
faces_union_state = ["results/regime_state.json"]
faces_union_token = ["results/token_usage.json"]
faces_twins = [
    "docs/daily_report/REPORT-2026-10-14.json", "docs/daily_report/REPORT-2026-10-14.md",
    "docs/live_usage/LIVE-2026-10-14.json", "docs/live_usage/LIVE-2026-10-14.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
]
faces_snapshot = [
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/update_status.json", "results/fundamental_b_layer_filter.json",
]

report = []

# 1) history-union faces: union list rows by ts, dedupe, keep latest-per-ts
for p in faces_union_hist:
    a = json.loads(side(2, p).decode("utf-8-sig"))   # ours = origin/bm-b
    b = json.loads(side(3, p).decode("utf-8-sig"))   # theirs = mine
    key = "ts"
    if isinstance(a, dict) and "history" in a and isinstance(a["history"], list):
        ha, hb = a["history"], b["history"]
        seen, merged = {}, []
        for row in ha + hb:
            k = row.get(key)
            if k not in seen:
                seen[k] = row; merged.append(row)
        merged.sort(key=lambda r: r.get(key, ""))
        a["history"] = merged
        out = a
        note = f"history-union {len(ha)}+{len(hb)}->{len(merged)}"
    else:
        # whole-file union fallback: take list rows dedupe
        la = a if isinstance(a, list) else []
        lb = b if isinstance(b, list) else []
        seen, merged = set(), []
        for row in la + lb:
            k = row.get(key)
            if k not in seen:
                seen.add(k); merged.append(row)
        merged.sort(key=lambda r: r.get(key, ""))
        out = merged
        note = f"list-union {len(la)}+{len(lb)}->{len(merged)}"
    with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, note))

# 2) regime_state: dict with history-ish keys -> union each list by ts, scalars take-newer-ish (both same source)
for p in faces_union_state:
    a = json.loads(side(2, p).decode("utf-8-sig"))
    b = json.loads(side(3, p).decode("utf-8-sig"))
    out = a if len(json.dumps(a)) >= len(json.dumps(b)) else b
    # union any list-of-dicts with ts keys found at top level
    for k in out:
        va, vb = a.get(k), b.get(k)
        if isinstance(va, list) and isinstance(vb, list) and va and isinstance(va[0], dict) and "ts" in va[0]:
            seen, merged = {}, []
            for row in va + vb:
                t = row.get("ts")
                if t not in seen:
                    seen[t] = row; merged.append(row)
            merged.sort(key=lambda r: r.get("ts", ""))
            out[k] = merged
    with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, "regime_state union-lists+bigger-base"))

# 3) token_usage: per-machine sections union (keep both machines' rows)
for p in faces_union_token:
    a = json.loads(side(2, p).decode("utf-8-sig"))
    b = json.loads(side(3, p).decode("utf-8-sig"))
    if isinstance(a, list) and isinstance(b, list):
        seen, merged = set(), []
        for row in a + b:
            k = (row.get("ts"), row.get("machine"), row.get("cmd"))
            if k not in seen:
                seen.add(k); merged.append(row)
        merged.sort(key=lambda r: str(r.get("ts", "")))
        out = merged
        note = f"list-union {len(a)}+{len(b)}->{len(out)}"
    else:
        out = b if len(json.dumps(b)) >= len(json.dumps(a)) else a
        note = "dict-take-bigger"
    with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, note))

# 4) twins + snapshots: take stage3 (mine, newer 14:05-14:09) whole bytes
for p in faces_twins + faces_snapshot:
    data = side(3, p)
    with open(os.path.join(ROOT, p), "wb") as f:
        f.write(data)
    report.append((p, "take-stage3(mine newer regen)"))

for p, note in report:
    print(f"RESOLVED {p}: {note}")
print("resolver done", len(report), "faces")
