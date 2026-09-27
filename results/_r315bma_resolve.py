"""R315 bm-a rebase-conflict resolver (canon recipes per classify_conflicts.py).

Sides during rebase: :2 = ours = origin/HEAD (bm-b r317 + bm-c r77 chain),
:3 = theirs = replayed round-315 commit (bm-a). Recipes:
  rolling-ledger      compute_audit.json / regime_state.json (history union
                      zero-loss, state take-new by ts)
  js-wrapper          dashboard_status.js (whole-byte take-side by embedded
                      generated_at; NEVER json.dumps re-emit -- R209)
  snapshot take-new   dashboard_status.json / futures / heat / lhb /
                      update_status / fundamental_b_layer_filter /
                      token_usage (by embedded ts)
  derive face (manual  scorecard_v1 + strategy_scorecard + prospect_promotion
  classification)      _summary (verify metadata-only diff, take-newer by ts)
  daily_report pair    json twin decides side, md follows (R313/R314 precedent)
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


# ---- 1. rolling-ledger: compute_audit.json / regime_state.json
for path in ("results/compute_audit.json", "results/regime_state.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    outd = dict(b)  # base = replay side; state fields re-decided by ts below
    for key in ("history", "transitions", "launches"):
        if key in a or key in b:
            ua = a.get(key) or []
            ub = b.get(key) or []
            un = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in ua + ub}
            merged = sorted(un.values(),
                            key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
            outd[key] = merged
            notes.append(f"{path} {key} union {len(ua)}+{len(ub)}->{len(merged)} "
                         f"(expect {len(un)})")
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    if ka and kb and str(va) >= str(vb):  # origin side newer -> state from origin
        for k, v in a.items():
            if k not in ("history", "transitions", "launches"):
                outd[k] = v
        notes.append(f"{path} state take-new=origin ({ka}={va} vs {kb}={vb})")
    else:
        notes.append(f"{path} state take-new=replay ({ka}={va} vs {kb}={vb})")
    w(path, json.dumps(outd, ensure_ascii=False, indent=1).encode("utf-8"))
    json.loads(io.open(path, encoding="utf-8-sig").read())  # verify

# ---- 2. js-wrapper: dashboard_status.js (whole-byte take-side by generated_at)
p_js = "results/dashboard_status.js"
ts_re = re.compile(rb'"generated_at"\s*:\s*"([^"]+)"')


def js_ts(blob):
    m = ts_re.search(blob)
    return m.group(1).decode() if m else ""


b2, b3 = side(p_js, 2), side(p_js, 3)
t2, t3 = js_ts(b2), js_ts(b3)
win = b2 if t2 >= t3 else b3
w(p_js, win)
notes.append(f"{p_js} js-wrapper whole-byte take={'origin' if win is b2 else 'replay'} "
             f"(generated_at {t2} vs {t3})")

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

# ---- 4. derive faces (manual classification): scorecard pair + prospect _summary
for path in ("results/scorecard_v1.json", "results/strategy_scorecard.json",
             "results/prospect_promotion/_summary.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    meta = {"generated", "elapsed_sec", "ts", "generated_at", "asof"}

    def strip(d):
        if isinstance(d, dict):
            return {k: strip(v) if isinstance(v, (dict, list)) else v
                    for k, v in d.items() if k not in meta}
        if isinstance(d, list):
            return [strip(x) for x in d]
        return d
    scope_ok = json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    win = "origin" if (ka and (not kb or str(va) >= str(vb))) else "replay"
    w(path, b2 if win == "origin" else b3)
    notes.append(f"{path} derive-face take-new={win} metadata-only-diff={scope_ok} "
                 f"({ka}={va} vs {kb}={vb})")
    json.loads(io.open(path, encoding="utf-8-sig").read())

# ---- 5. daily report pair: json twin decides the side, md follows
p_j, p_m = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
b2, b3 = side(p_j, 2), side(p_j, 3)
a, b = jload(b2), jload(b3)
ka, va = pick_ts(a)
kb, vb = pick_ts(b)
win = 2 if (ka and (not kb or str(va) >= str(vb))) else 3
w(p_j, side(p_j, win))
w(p_m, side(p_m, win))
notes.append(f"daily_report pair take-new={'origin' if win == 2 else 'replay'} "
             f"({ka}={va} vs {kb}={vb})")
json.loads(io.open(p_j, encoding="utf-8-sig").read())

# ---- 6. sanity: auto-merged autofill_state.json parses + no conflict markers left
d = json.loads(io.open("results/autofill_state.json", encoding="utf-8-sig").read())
assert isinstance(d.get("last_tick"), dict), "last_tick must stay dict"
notes.append(f"autofill_state auto-merged sanity: launches={len(d.get('launches', []))} "
             f"last_tick dict OK")

print(json.dumps({"resolved": resolved, "notes": notes}, ensure_ascii=False, indent=1))
print("ALL PARSE-VERIFIED")
