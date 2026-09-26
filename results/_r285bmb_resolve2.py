# -*- coding: utf-8 -*-
"""r285 bm-b rebase step-2 resolver: 14 UU vs bm-a r281 wrap window (6041ae5b).

Direction: :2 = origin base (bm-a side, S6 ran ~00:55-56), :3 = bm-b
replayed side (mine, S6 ran 00:53-54). Same-window S6 dual-producer race
(r283 lineage). Side = per-file recursive ts probe (r267/r277 law:
two-level flatten, producer wall-clock keys, constant milestone keys
excluded), tie -> origin side (r140). Pairs take same side (r265 md+json
twin governs; r148 dashboard js+json cross-check).

Resolution map (classifier 11 classified + 4 manual = snapshot family,
r283 precedent verbatim):
- CODELY.md: base-anchored memory union = :1 + bm-a suffix + bm-b suffix
  byte-concat (r281 law: prefix-identity asserted, NO naive line dedup)
- compute_audit.json: history union by ts (zero-loss) + latest take-new
- regime_state.json: probe -> transitions/history union if present, else
  take-new whole-byte
- dashboard_status.js/.json: same-side whole bytes (js wrapper R209)
- daily_report md+json: same-side whole bytes (json twin governs)
- token_usage.json: probe structure -> machines-key union newest-ts if
  per-machine sections, else take-new whole-byte
- all other *_status.json / scorecard*.json / update_status: take-new
Post-write: json.loads parse gate on every resolved json (r185 law).
"""
import io
import json
import subprocess


def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}: rc={r.returncode}")
    return r.stdout


CONST_KEYS = {"first_check", "ACTIVE_FROM", "active_from", "deadline", "monday_deadline"}


def flat_ts(obj, depth=0, acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and ("ts" in k.lower() or "generated" in k.lower()
                                       or "updated" in k.lower()) and k not in CONST_KEYS:
                acc.append((k, v))
            if depth < 2 and isinstance(v, (dict, list)):
                flat_ts(v, depth + 1, acc)
    elif isinstance(obj, list):
        for it in obj[:5] + (obj[-3:] if len(obj) > 5 else []):
            if depth < 2 and isinstance(it, (dict, list)):
                flat_ts(it, depth + 1, acc)
    return acc


def side_of(path):
    """Return 'ours'(:2 origin) or 'theirs'(:3 mine) by max ts, tie -> origin."""
    a = blob(":2:" + path)
    b = blob(":3:" + path)
    try:
        da = json.loads(a.decode("utf-8-sig"))
        db = json.loads(b.decode("utf-8-sig"))
    except Exception:
        return "ours", None, None, a, b       # non-json: byte-take ours? (none here)
    ta = sorted((v for _, v in flat_ts(da)), reverse=True)
    tb = sorted((v for _, v in flat_ts(db)), reverse=True)
    ma = ta[0] if ta else ""
    mb = tb[0] if tb else ""
    side = "theirs" if mb > ma else "ours"     # tie/empty -> ours (origin, r140)
    return side, ma, mb, a, b


def take(path, side, a, b):
    data = a if side == "ours" else b
    with io.open(path, "wb") as f:
        f.write(data)
    if path.endswith(".json"):
        json.loads(data.decode("utf-8-sig"))
    print(f"  take-{side}({len(data)}B): {path}")


# ---- 1) CODELY.md: base-anchored union (r281 law)
base = blob(":1:CODELY.md")
ours = blob(":2:CODELY.md")
theirs = blob(":3:CODELY.md")
assert ours.startswith(base), "CODELY origin side not base+suffix"
assert theirs.startswith(base), "CODELY mine side not base+suffix"
suf_a = ours[len(base):]
suf_b = theirs[len(base):]
assert suf_a and suf_b, f"empty suffix face: a={len(suf_a)} b={len(suf_b)}"
merged = base + suf_a + suf_b            # origin (bm-a, first-landed) then mine
with io.open("CODELY.md", "wb") as f:
    f.write(merged)
assert merged.startswith(base) and merged.endswith(suf_b)
print(f"CODELY.md union: base {len(base)} + bm-a suffix {len(suf_a)} + "
      f"bm-b suffix {len(suf_b)} -> {len(merged)}B (zero-loss concat)")

# ---- 2) compute_audit.json: history union by ts + latest take-new
a = json.loads(blob(":2:results/compute_audit.json").decode("utf-8-sig"))
b = json.loads(blob(":3:results/compute_audit.json").decode("utf-8-sig"))
ha = {r.get("ts"): r for r in a.get("history", []) if isinstance(r, dict) and r.get("ts")}
hb = {r.get("ts"): r for r in b.get("history", []) if isinstance(r, dict) and r.get("ts")}
union = dict(ha)
union.update(hb)
hist = sorted(union.values(), key=lambda r: r["ts"])
la, lb = a.get("latest", {}), b.get("latest", {})
latest = lb if str(lb.get("ts", "")) > str(la.get("ts", "")) else la
out = dict(a) if str(la.get("ts", "")) >= str(lb.get("ts", "")) else dict(b)
out["history"] = hist
out["latest"] = latest
raw3 = blob(":3:results/compute_audit.json")
eol = b"\r\n" if b"\r\n" in raw3 else b"\n"
text = json.dumps(out, ensure_ascii=False, indent=1)
if not raw3.endswith(b"\n"):
    text = text.rstrip("\n")
data = text.encode("utf-8")
if eol == b"\r\n":
    data = data.replace(b"\n", b"\r\n")
with io.open("results/compute_audit.json", "wb") as f:
    f.write(data)
json.loads(io.open("results/compute_audit.json", encoding="utf-8-sig").read())
print(f"compute_audit: history union {len(ha)}|{len(hb)} -> {len(hist)} zero-loss, "
      f"latest={latest.get('ts')} (a={la.get('ts')} b={lb.get('ts')})")

# ---- 3) regime_state.json: probe structure -> union or take-new
a = json.loads(blob(":2:results/regime_state.json").decode("utf-8-sig"))
b = json.loads(blob(":3:results/regime_state.json").decode("utf-8-sig"))
led_keys = [k for k in a.keys() if isinstance(a.get(k), list) and k != "history"
            and ("transition" in k.lower() or "log" in k.lower())]
if led_keys or ("history" in a and a.get("history")):
    key = led_keys[0] if led_keys else "history"
    ka = {json.dumps(r, sort_keys=True): r for r in a.get(key, [])}
    kb = {json.dumps(r, sort_keys=True): r for r in b.get(key, [])}
    ka.update(kb)
    merged_state = dict(a)
    merged_state[key] = sorted(ka.values(),
                               key=lambda r: str(r.get("ts") or r.get("date") or ""))
    ta = str(max((v for _, v in flat_ts(a)), default=""))
    tb = str(max((v for _, v in flat_ts(b)), default=""))
    if tb > ta:
        for k in b:
            if k != key:
                merged_state[k] = b[k]
    raw3 = blob(":3:results/regime_state.json")
    eol = b"\r\n" if b"\r\n" in raw3 else b"\n"
    text = json.dumps(merged_state, ensure_ascii=False, indent=1)
    if not raw3.endswith(b"\n"):
        text = text.rstrip("\n")
    data = text.encode("utf-8")
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    with io.open("results/regime_state.json", "wb") as f:
        f.write(data)
    json.loads(io.open("results/regime_state.json", encoding="utf-8-sig").read())
    print(f"regime_state: '{key}' union {len(ka)} zero-loss, state take-new "
          f"(a_top={ta} b_top={tb})")
else:
    side, ma, mb, ra, rb = side_of("results/regime_state.json")
    take("results/regime_state.json", side, ra, rb)
    print(f"  regime_state: pure snapshot, a_top={ma} b_top={mb}")

# ---- 4) token_usage.json: probe per-machine sections
a = json.loads(blob(":2:results/token_usage.json").decode("utf-8-sig"))
b = json.loads(blob(":3:results/token_usage.json").decode("utf-8-sig"))
mach_a = a.get("machines") if isinstance(a.get("machines"), dict) else None
mach_b = b.get("machines") if isinstance(b.get("machines"), dict) else None
if mach_a is not None and mach_b is not None:
    merged_m = dict(mach_a)
    for k, v in mach_b.items():
        if k not in merged_m or str(v) >= str(merged_m[k]):
            merged_m[k] = v
    out = dict(a)
    out["machines"] = merged_m
    ta = str(max((v for _, v in flat_ts(a)), default=""))
    tb = str(max((v for _, v in flat_ts(b)), default=""))
    if tb > ta:
        for k in b:
            if k != "machines":
                out[k] = b[k]
    raw3 = blob(":3:results/token_usage.json")
    eol = b"\r\n" if b"\r\n" in raw3 else b"\n"
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if not raw3.endswith(b"\n"):
        text = text.rstrip("\n")
    data = text.encode("utf-8")
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    with io.open("results/token_usage.json", "wb") as f:
        f.write(data)
    json.loads(io.open("results/token_usage.json", encoding="utf-8-sig").read())
    print(f"token_usage: machines key-union {len(merged_m)} (a={len(mach_a)} "
          f"b={len(mach_b)}), scalar take-new")
else:
    side, ma, mb, ra, rb = side_of("results/token_usage.json")
    take("results/token_usage.json", side, ra, rb)
    print(f"  token_usage: snapshot face, a_top={ma} b_top={mb}")

# ---- 5) snapshot family: per-file take-new (ts probe), pairs same-side
PAIRS = [("docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"),
         ("results/dashboard_status.json", "results/dashboard_status.js")]
singles = ["results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
           "results/heat_update_status.json", "results/lhb_update_status.json",
           "results/update_status.json", "results/scorecard_v1.json",
           "results/strategy_scorecard.json"]
for gov, twin in PAIRS:
    side, ma, mb, ra, rb = side_of(gov)
    take(gov, side, ra, rb)
    print(f"  pair governs by {gov}: a_top={ma} b_top={mb} -> side={side}")
    if twin:
        da = blob(":2:" + twin)
        db = blob(":3:" + twin)
        take(twin, side, da, db)
for p in singles:
    side, ma, mb, ra, rb = side_of(p)
    take(p, side, ra, rb)
    print(f"  {p}: a_top={ma} b_top={mb} -> side={side}")

print("RESOLVE_OK all 14 files written + parse-gated")
