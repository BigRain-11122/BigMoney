# -*- coding: utf-8 -*-
"""R218 push-collision rebase resolve (11-UU, R208/R212/R216 family same-window dual-machine S6 chain).

Canonical recipes per bigmoney-conflict-resolve skill (first dogfood of the skill built this round):
- autofill_state.json  : launches union -> sort by ts -> cap 50 (rolling window, R215 law);
                         last_tick compare inner ts, same-second tie -> HEAD/ours (r140 law);
                         write-back isinstance(last_tick, dict) assertion (R203 law);
                         mirror working-tree line endings (bm-b r223 CRLF producer-format law).
- compute_audit.json   : history union zero-loss + latest take-new by ts (r188/R208).
- regime_state.json    : history/transitions union + state fields take-new by ts (R208).
- dashboard_status.js  : byte-verbatim take-new side (R209 wrapper preservation law).
- snapshots            : take-new by named ts key (R208).
All JSON parse-verified before write-back (r185 law). Zero-loss counts reported.
"""
import io, json, subprocess, sys

def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True, check=True).stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def rowkey(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

report = []

# ---------- 1. autofill_state.json (mixed-dict+ledger) ----------
p = "results/autofill_state.json"
ours, theirs = jload(blob(2, p)), jload(blob(3, p))
lo, lt = ours.get("launches", []), theirs.get("launches", [])
union = {}
for r in lo + lt:
    union[rowkey(r)] = r
merged_launches = sorted(union.values(), key=lambda r: r.get("ts", ""))
n_union = len(merged_launches)
merged_launches = merged_launches[-50:]  # rolling window cap (R215 law)
tick_o, tick_t = ours.get("last_tick", {}), theirs.get("last_tick", {})
if not isinstance(tick_o, dict) or not isinstance(tick_t, dict):
    sys.exit(f"RED: last_tick not dict: ours={type(tick_o)} theirs={type(tick_t)} (R203 law)")
if tick_t.get("ts", "") > tick_o.get("ts", ""):
    winner, wside = tick_t, "theirs(mine)"
elif tick_t.get("ts", "") < tick_o.get("ts", ""):
    winner, wside = tick_o, "ours(HEAD)"
else:
    winner, wside = tick_o, "ours(HEAD)-same-second-tie (r140)"
res = dict(ours)
res["launches"] = merged_launches
res["last_tick"] = winner
assert isinstance(res["last_tick"], dict), "last_tick must stay dict (R203)"
# line-ending mirror: detect EOL of current conflict-marked working file
wt = open(p, "rb").read()
eol = "\r\n" if wt.count(b"\r\n") > wt.count(b"\n") - wt.count(b"\r\n") else "\n"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(res, ensure_ascii=False, indent=1).replace("\n", eol))
json.load(io.open(p, encoding="utf-8-sig"))  # parse-verify (r185)
report.append(f"{p}: launches {len(lo)}+{len(lt)} -> union {n_union} -> cap {len(merged_launches)}; last_tick tie@{tick_o.get('ts')} -> {wside}; eol={'CRLF' if eol=='\\r\\n' else 'LF'}")

# ---------- 2. compute_audit.json (rolling-ledger) ----------
p = "results/compute_audit.json"
ours, theirs = jload(blob(2, p)), jload(blob(3, p))
ho, ht = ours.get("history", []), theirs.get("history", [])
u = {}
for r in ho + ht:
    u[rowkey(r)] = r
hist = sorted(u.values(), key=lambda r: r.get("ts", r.get("time", "")))
newer = theirs if theirs.get("latest", {}).get("ts", "") >= ours.get("latest", {}).get("ts", "") else ours
res = dict(newer)
res["history"] = hist
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(res, ensure_ascii=False, indent=1))
json.load(io.open(p, encoding="utf-8-sig"))
report.append(f"{p}: history {len(ho)}+{len(ht)} -> union {len(hist)} zero-loss; latest take-new ts={newer.get('latest',{}).get('ts')}")

# ---------- 3. regime_state.json (rolling-ledger) ----------
p = "results/regime_state.json"
ours, theirs = jload(blob(2, p)), jload(blob(3, p))
newer = theirs if theirs.get("updated", "") >= ours.get("updated", "") else ours
res = dict(newer)
for k in ("history", "transitions"):
    if isinstance(ours.get(k), list) and isinstance(theirs.get(k), list):
        u = {}
        for r in ours[k] + theirs[k]:
            u[rowkey(r)] = r
        res[k] = sorted(u.values(), key=lambda r: json.dumps(r.get("ts", r.get("date", "")), ensure_ascii=False))
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(res, ensure_ascii=False, indent=1))
json.load(io.open(p, encoding="utf-8-sig"))
report.append(f"{p}: take-new updated={res.get('updated')}; history {len(ours.get('history',[]))}+{len(theirs.get('history',[]))} -> {len(res.get('history',[]))}; transitions -> {len(res.get('transitions',[]))}")

# ---------- 4. dashboard_status.js (js-wrapper: byte-verbatim take-new) ----------
p = "results/dashboard_status.js"
b2, b3 = blob(2, p), blob(3, p)
def js_inner_ts(b):
    s = b.decode("utf-8-sig")
    d = json.loads(s[s.index("{"): s.rindex("}") + 1])
    return d.get("meta", {}).get("generated_at", "")
t2, t3 = js_inner_ts(b2), js_inner_ts(b3)
win = b3 if t3 >= t2 else b2
with io.open(p, "wb") as f:
    f.write(win)
json.loads(win.decode("utf-8-sig")[win.decode("utf-8-sig").index("{"): win.decode("utf-8-sig").rindex("}") + 1])
report.append(f"{p}: byte-verbatim take {'theirs(mine)' if win is b3 else 'ours'} (generated_at {t2} vs {t3}) wrapper preserved (R209)")

# ---------- 5. snapshot JSONs take-new by named ts key ----------
SNAPS = {
    "results/dashboard_status.json":        lambda d: d.get("health", {}).get("smoke", {}).get("at", ""),
    "results/fundamental_b_layer_filter.json": lambda d: d.get("updated", ""),
    "results/futures_update_status.json":   lambda d: d.get("ts", ""),
    "results/heat_update_status.json":      lambda d: d.get("updated", ""),
    "results/lhb_update_status.json":       lambda d: d.get("updated", ""),
    "results/token_usage.json":             lambda d: d.get("generated", ""),
    "results/update_status.json":           lambda d: d.get("updated", ""),
}
for p, tsget in SNAPS.items():
    o, t = jload(blob(2, p)), jload(blob(3, p))
    to, tt = tsget(o), tsget(t)
    win, side = (t, "theirs(mine)") if tt >= to else (o, "ours(HEAD)")
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(win, ensure_ascii=False, indent=1))
    json.load(io.open(p, encoding="utf-8-sig"))
    report.append(f"{p}: take-new {side} (ts {to} vs {tt})")

print("\n".join(report))
print("ALL 11 FILES RESOLVED + PARSE-VERIFIED (r185 law)")
