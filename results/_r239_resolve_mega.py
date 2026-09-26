# -*- coding: utf-8 -*-
"""R239 mega-resolver: 12 UU shared-state files per skill recipes.
Rebase orientation: stage2=ours=onto side (bm-b ae2e3379), stage3=theirs=my replayed big commit.
Recipes: autofill=mixed-dict+ledger; compute_audit/regime_state=rolling-ledger union;
dashboard.js=js-wrapper take-side whole bytes (pair decided via .json twin); snapshots=take-new by ts key;
daily_scorecard=UNKNOWN->manual: producer-rederived snapshot, take-new by ts key (same family).
Fail-closed: exit 2 on any anomaly. EOL: take-new files = whole bytes (no rewrite); union files = mirror base EOL."""
import json
import subprocess
import sys

def raw_blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"blob fail {stage} {path}: {out.stderr[:150]}")
    return out.stdout

def jblob(stage, path):
    return json.loads(raw_blob(stage, path).decode("utf-8"))

TS_KEYS = ("updated", "ts", "generated", "generated_at", "now", "last_attempt")

def ts_of(d):
    for k in TS_KEYS:
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and len(v) >= 10:
            return v
    return ""

def take_new(path, prefer_on_tie="ours"):
    o, t = jblob(2, path), jblob(3, path)
    to, tt = ts_of(o), ts_of(t)
    if to == tt:
        side = 2 if prefer_on_tie == "ours" else 3
    else:
        side = 2 if to > tt else 3
    data = raw_blob(side, path)
    with open(path, "wb") as f:
        f.write(data)
    json.loads(open(path, encoding="utf-8").read())  # roundtrip validate
    print(f"take-new {path}: side={'ours(bm-b)' if side==2 else 'theirs(bm-a)'} ts={max(to,tt)}")

def union_rows(a, b, key_fields, cap=None):
    seen, out = set(), []
    for row in a + b:
        k = tuple(str(row.get(f)) for f in key_fields)
        if k in seen:
            continue
        seen.add(k)
        out.append(row)
    return out[:cap] if cap else out

def eol_of(data: bytes) -> bytes:
    return b"\r\n" if b"\r\n" in data[:4000] else b"\n"

# ---- 1) autofill_state.json (mixed-dict+ledger)
P = "results/autofill_state.json"
o_raw, t_raw = raw_blob(2, P), raw_blob(3, P)
o, t = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
lt_o = o.get("last_tick") or {}
lt_t = t.get("last_tick") or {}
ts_o = str(lt_o.get("ts", ""))
ts_t = str(lt_t.get("ts", ""))
if ts_t > ts_o:
    base, lt = t, lt_t
elif ts_o > ts_t:
    base, lt = o, lt_o
else:
    base, lt = o, lt_o  # same-second tie -> HEAD side (ours, r140)
la_o = o.get("launches") or []
la_t = t.get("launches") or []
launches = sorted(union_rows(la_o, la_t, ("ts", "shard")), key=lambda r: str(r.get("ts", "")))
if len(launches) > 50:
    launches = launches[-50:]  # rolling window cap 50 (R215)
base["launches"] = launches
base["last_tick"] = lt
assert isinstance(base["last_tick"], dict), "last_tick must stay dict (r203 law)"
with open(P, "wb") as f:
    f.write(json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8").replace(b"\n", eol_of(o_raw)))
json.loads(open(P, encoding="utf-8").read())
print(f"autofill_state: last_tick ts {max(ts_o, ts_t)} | launches union -> {len(launches)} (o={len(la_o)} t={len(la_t)})")

# ---- 2) compute_audit.json (rolling-ledger: history union + latest take-new)
P = "results/compute_audit.json"
o_raw, t_raw = raw_blob(2, P), raw_blob(3, P)
o, t = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
lts_o = str((o.get("latest") or {}).get("ts", ""))
lts_t = str((t.get("latest") or {}).get("ts", ""))
latest = (o if lts_o >= lts_t else t)["latest"]
hist = sorted(union_rows(o.get("history") or [], t.get("history") or [], ("ts",)), key=lambda r: str(r.get("ts", "")))
hist = hist[-200:]  # producer cap (compute_audit.py keeps last 200)
merged = {"latest": latest, "history": hist}
merged.update({k: v for k, v in (o if lts_o >= lts_t else t).items() if k not in ("latest", "history")})
with open(P, "wb") as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8").replace(b"\n", eol_of(o_raw)))
json.loads(open(P, encoding="utf-8").read())
print(f"compute_audit: latest ts {max(lts_o, lts_t)} | history union -> {len(hist)}")

# ---- 3) regime_state.json (rolling-ledger: transitions union + rest take-new)
P = "results/regime_state.json"
o_raw, t_raw = raw_blob(2, P), raw_blob(3, P)
o, t = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
uo, ut = ts_of(o), ts_of(t)
base = o if uo >= ut else t
tr = union_rows(o.get("transitions") or [], t.get("transitions") or [], ("date", "from", "to"))
base["transitions"] = tr
with open(P, "wb") as f:
    f.write(json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8").replace(b"\n", eol_of(o_raw)))
json.loads(open(P, encoding="utf-8").read())
print(f"regime_state: take-new {max(uo, ut)} | transitions union -> {len(tr)}")

# ---- 4) dashboard pair: decide side via .json twin meta/generated key (r226 law), take whole bytes both
PJ, PS = "results/dashboard_status.json", "results/dashboard_status.js"
o_j, t_j = jblob(2, PJ), jblob(3, PJ)
def dash_ts(d):
    meta = d.get("meta") or {}
    return str(meta.get("generated_at") or ts_of(d) or "")
side = 2 if dash_ts(o_j) >= dash_ts(t_j) else 3
for p in (PJ, PS):
    data = raw_blob(side, p)
    with open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.loads(data.decode("utf-8"))
print(f"dashboard pair: side={'ours(bm-b)' if side==2 else 'theirs(bm-a)'} dash_ts={dash_ts(o_j) if side==2 else dash_ts(t_j)}")

# ---- 5) snapshots take-new + daily_scorecard (manual: same snapshot family)
for p in ("results/daily_scorecard.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json"):
    take_new(p)

print("mega-resolver done -- all 12 resolved, validated")
