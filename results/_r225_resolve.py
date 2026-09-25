# -*- coding: utf-8 -*-
"""r225 (bm-b) S0 stash-pop 11-UU resolver (bigmoney-conflict-resolve dogfood #3).
Ours(stage2)=HEAD=bm-a r221 outputs (~05:2x); Theirs(stage3)=stashed dead-session
05:02 S6 outputs (this machine). Recipes per classifier output:
- mixed-dict+ledger autofill_state: launches union -> sort ts -> cap50 (R215);
  last_tick inner-ts compare -> WHOLE dict assign, tie->ours (r140); isinstance assert.
- rolling-ledger compute_audit/regime_state: history/transitions union zero-loss,
  scalar state take-new.
- js-wrapper-snapshot dashboard_status.js: take-side whole bytes (ours, newer).
- snapshots: take-new by internal ts else ours.
- CRLF mirror per-file from ours blob raw bytes (bm-b r223 law).
Parse-verify every JSON before write-back (r185 law)."""
import json
import subprocess
import sys

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {stage}:{path} failed: {r.stderr[:200]}")
    return r.stdout

def crlf_of(raw):
    return b"\r\n" in raw

def write_mirror(path, obj, crlf):
    out = json.dumps(obj, ensure_ascii=False, indent=1)
    data = out.replace("\n", "\r\n").encode("utf-8") if crlf else out.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)

def ts_of(entry):
    for k in ("ts", "updated_at", "updated", "time", "generated", "when"):
        if isinstance(entry, dict) and k in entry:
            return entry[k]
    return None

def union_list(ours, theirs, cap=None):
    seen = set()
    merged = []
    for e in ours + theirs:
        key = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        merged.append(e)
    tss = [ts_of(e) for e in merged]
    if all(t is not None for t in tss):
        merged = sorted(merged, key=lambda e: ts_of(e))
    if cap is not None:
        merged = merged[-cap:]
    return merged, len(ours), len(theirs)

report = []

# 1) autofill_state.json (mixed-dict+ledger)
p = "results/autofill_state.json"
o_raw, t_raw = blob(2, p), blob(3, p)
o, t = json.loads(o_raw), json.loads(t_raw)
launch, lo, lt = union_list(o["launches"], t["launches"], cap=50)
lt_o = ts_of(o["last_tick"]) if isinstance(o["last_tick"], dict) else None
lt_t = ts_of(t["last_tick"]) if isinstance(t["last_tick"], dict) else None
if lt_t is not None and (lt_o is None or lt_t > lt_o):
    last_tick = t["last_tick"]
elif lt_t is not None and lt_t == lt_o:
    last_tick = o["last_tick"]  # tie -> ours (r140)
else:
    last_tick = o["last_tick"]
assert isinstance(last_tick, dict), "last_tick must stay dict (r203 law)"
res = dict(o)
res["launches"] = launch
res["last_tick"] = last_tick
write_mirror(p, res, crlf_of(o_raw))
chk = json.load(open(p, encoding="utf-8"))
assert isinstance(chk["last_tick"], dict) and len(chk["launches"]) <= 50
report.append(f"autofill_state: launches {lo}+{lt}->union {len(launch)} cap50, "
              f"last_tick ours={lt_o} theirs={lt_t} -> {'theirs' if last_tick is t['last_tick'] and lt_t != lt_o else 'ours/tie'}")

# 2) compute_audit.json (rolling-ledger history + latest take-new)
p = "results/compute_audit.json"
o_raw, t_raw = blob(2, p), blob(3, p)
o, t = json.loads(o_raw), json.loads(t_raw)
hist, ho, ht = union_list(o["history"], t["history"])
res = dict(o)
res["history"] = hist
for cand in ("latest",):
    if cand in t and ts_of(t[cand]) and (ts_of(o.get(cand)) is None or ts_of(t[cand]) > ts_of(o[cand])):
        res[cand] = t[cand]
write_mirror(p, res, crlf_of(o_raw))
chk = json.load(open(p, encoding="utf-8"))
assert len(chk["history"]) >= max(ho, ht)
report.append(f"compute_audit: history {ho}+{ht}->union {len(hist)} (zero-loss), latest take-new")

# 3) regime_state.json (rolling-ledger history/transitions + state take-new)
p = "results/regime_state.json"
o_raw, t_raw = blob(2, p), blob(3, p)
o, t = json.loads(o_raw), json.loads(t_raw)
res = dict(o)
for k in ("history", "transitions"):
    if k in o and k in t:
        merged, a, b = union_list(o[k], t[k])
        res[k] = merged
        report.append(f"regime_state.{k}: {a}+{b}->union {len(merged)}")
# scalar state fields take-new by 'updated'
if ts_of(t) and (ts_of(o) is None or ts_of(t) > ts_of(o)):
    for k in t:
        if k not in ("history", "transitions"):
            res[k] = t[k]
    report.append("regime_state: scalar fields take-new (theirs newer)")
write_mirror(p, res, crlf_of(o_raw))
chk = json.load(open(p, encoding="utf-8"))
report.append(f"regime_state resolved: state={chk.get('state')} updated={chk.get('updated')}")

# 4) dashboard_status.js (js-wrapper-snapshot: take-side whole bytes, ours newer)
p = "results/dashboard_status.js"
o_raw, t_raw = blob(2, p), blob(3, p)
with open(p, "wb") as f:
    f.write(o_raw)
assert o_raw.startswith(b"window.DASH_DATA") or b"window.DASH_DATA" in o_raw[:200]
report.append(f"dashboard_status.js: take-side ours whole bytes ({len(o_raw)}B, wrapper intact)")

# 5) plain snapshots: take-new by internal ts else ours
for p in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json"]:
    o_raw, t_raw = blob(2, p), blob(3, p)
    o, t = json.loads(o_raw), json.loads(t_raw)
    to, tt = ts_of(o), ts_of(t)
    if tt is not None and (to is None or tt > to):
        pick, side = t, "theirs"
        pick_raw = t_raw
    else:
        pick, side = o, "ours"
        pick_raw = o_raw
    write_mirror(p, pick, crlf_of(o_raw))
    json.load(open(p, encoding="utf-8"))  # parse-verify
    report.append(f"{p}: take-new -> {side} (ours={to} theirs={tt})")

print("\n".join(report))
print("RESOLVE OK: 11 files written, parse-verify PASS")
