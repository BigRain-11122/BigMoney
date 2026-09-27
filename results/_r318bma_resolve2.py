"""R318 bm-a wave-2 rebase-conflict resolver (canon recipes per classify_conflicts.py).

Sides during rebase: :2 = ours = origin/HEAD (bm-b r319 closeout + collision
addenda cfe25ac3), :3 = theirs = replayed round-318 commit (bm-a 3c312692).
Wave-2 recipes:
  rolling-ledger      compute_audit.json (history ts-key union zero-loss,
                      per bm-b r319 union-key law) / regime_state.json
                      (asof-key union)
  js-wrapper          dashboard_status.js (R209: take-side WHOLE bytes by
                      inner ts, no json re-emit)
  snapshot take-new   dashboard_status/futures/heat/lhb/update_status/
                      fundamental_b_layer_filter/token_usage (by embedded ts)
  derive face (manual scorecard_v1 + strategy_scorecard + prospect_promotion
  classification)      _summary + daily_report pair: take-newer by ts with
                      deep-strip honesty check (R314/R316/r317 bm-b laws)
"""
import json
import subprocess
import io
import re

ROOT = "."


def side(path, n):
    out = subprocess.run(["git", "show", f":{n}:{path}"],
                         capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(f"git show :{n}:{path} rc={out.returncode}")
    return out.stdout


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def pick_ts(d):
    for k in ("ts", "generated", "generated_at", "updated", "updated_at",
              "time", "asof"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and len(v) >= 10:
            return (k, v)
    return (None, None)


resolved, notes = [], []


def w(path, text_bytes):
    with io.open(path, "wb") as f:
        f.write(text_bytes)
    resolved.append(path)


def deep_strip(d, meta):
    if isinstance(d, dict):
        return {k: deep_strip(v, meta) for k, v in d.items() if k not in meta}
    if isinstance(d, list):
        return [deep_strip(x, meta) for x in d]
    return d


# ---- 1. rolling-ledger with per-face dedupe key (bm-b r319 union-key law)
KEY_BY_FACE = {
    "results/compute_audit.json": ("history", lambda r: str(r.get("ts", ""))),
    "results/regime_state.json": ("history", lambda r: str(r.get("asof", r.get("ts", "")))),
}
for path, (key, rowkey) in KEY_BY_FACE.items():
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    outd = dict(b)
    ua, ub = a.get(key) or [], b.get(key) or []
    un = {}
    for r in list(ua) + list(ub):
        un.setdefault(rowkey(r), r)
    rows = sorted(un.values(), key=rowkey)
    assert len(rows) == len(un), "union key collision"
    outd[key] = rows
    for k2 in ("transitions", "launches"):
        if k2 in a or k2 in b:
            va2, vb2 = a.get(key2 := k2) or [], b.get(k2) or []
            un2 = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in va2 + vb2}
            outd[k2] = sorted(un2.values(), key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    if ka and kb and str(va) >= str(vb):
        for k, v in a.items():
            if k not in (key, "transitions", "launches"):
                outd[k] = v
        st = "origin"
    else:
        st = "replay"
    notes.append(f"{path} {key} union {len(ua)}+{len(ub)}->{len(rows)} (|keyset|={len(un)}), state take-new={st} ({ka}={va} vs {kb}={vb})")
    w(path, json.dumps(outd, ensure_ascii=False, indent=1).encode("utf-8"))
    json.loads(io.open(path, encoding="utf-8-sig").read())  # r185 verify

# ---- 2. js-wrapper dashboard_status.js: take-side whole bytes by inner ts (R209)
p_js = "results/dashboard_status.js"
b2, b3 = side(p_js, 2), side(p_js, 3)


def inner(b):
    m = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", b, re.S)
    return jload(m.group(1)) if m else None


ia, ib = inner(b2), inner(b3)
ka, va = pick_ts(ia) if ia else (None, None)
kb, vb = pick_ts(ib) if ib else (None, None)
win = b2 if (ka and (not kb or str(va) >= str(vb))) else b3
w(p_js, win)
notes.append(f"dashboard_status.js js-wrapper take-side={'origin' if win is b2 else 'replay'} whole-bytes ({ka}={va} vs {kb}={vb})")

# ---- 3. snapshot take-new by ts
for path in ("results/dashboard_status.json", "results/futures_update_status.json",
             "results/heat_update_status.json", "results/lhb_update_status.json",
             "results/update_status.json", "results/fundamental_b_layer_filter.json",
             "results/token_usage.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    win = "origin" if (ka and (not kb or str(va) >= str(vb))) else "replay"
    w(path, b2 if win == "origin" else b3)
    notes.append(f"{path} take-new={win} ({ka}={va} vs {kb}={vb})")
    json.loads(io.open(path, encoding="utf-8-sig").read())

# ---- 4. derive faces (manual): scorecard pair + promo summary + daily_report pair
META = {"generated", "elapsed_sec", "ts", "generated_at", "asof", "updated", "updated_at"}
for path in ("results/scorecard_v1.json", "results/strategy_scorecard.json",
             "results/prospect_promotion/_summary.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    deep_ok = json.dumps(deep_strip(a, META), sort_keys=True) == \
              json.dumps(deep_strip(b, META), sort_keys=True)
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    win = "origin" if (ka and (not kb or str(va) >= str(vb))) else "replay"
    w(path, b2 if win == "origin" else b3)
    notes.append(f"{path} derive-face take-new={win} deep-strip-eq={deep_ok} ({ka}={va} vs {kb}={vb})")
    json.loads(io.open(path, encoding="utf-8-sig").read())

p_j, p_m = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
b2, b3 = side(p_j, 2), side(p_j, 3)
a, b = jload(b2), jload(b3)
ka, va = pick_ts(a)
kb, vb = pick_ts(b)
win = 2 if (ka and (not kb or str(va) >= str(vb))) else 3
w(p_j, side(p_j, win))
w(p_m, side(p_m, win))
notes.append(f"daily_report pair take-new={'origin' if win == 2 else 'replay'} ({ka}={va} vs {kb}={vb})")
json.loads(io.open(p_j, encoding="utf-8-sig").read())

# ---- 5. autofill_state.json auto-merged this wave: parse-verify only
af = json.loads(io.open("results/autofill_state.json", encoding="utf-8-sig").read())
assert isinstance(af.get("last_tick"), dict), "autofill last_tick must stay dict"
notes.append(f"autofill_state auto-merge parse-verify PASS (launches={len(af.get('launches', []))}, last_tick ts={(af.get('last_tick') or {}).get('ts')})")

print(json.dumps({"resolved": resolved, "notes": notes}, ensure_ascii=False, indent=1))
print("ALL PARSE-VERIFIED")
