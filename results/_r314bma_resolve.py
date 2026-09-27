"""R314 bm-a rebase-conflict resolver (canon recipes per classify_conflicts.py).

Sides during rebase: :2 = ours = origin/HEAD (bm-c r76 chain), :3 = theirs =
replayed round-314 commit (bm-a). Recipes:
  memory-union        CODELY.md (keep both entries, HEAD side first)
  mixed-dict+ledger   autofill_state.json (launches union cap50, last_tick
                      whole-dict ts compare, CRLF mirror)
  rolling-ledger      compute_audit.json / regime_state.json (history union
                      zero-loss, state take-new)
  snapshot take-new   dashboard_status/futures/heat/lhb/update_status/
                      fundamental_b_layer_filter/token_usage (by embedded ts)
  derive face (manual  scorecard_v1 + strategy_scorecard + daily_report pair
  classification)      (verify metadata-only diff scope, take-newer by ts)
"""
import json
import subprocess
import io
import sys

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


# ---- 1. CODELY.md: memory-union (manual, single hunk: HEAD entry + ours entry)
h = open("CODELY.md", "r", encoding="utf-8").read()
lines = h.split("\n")
out_lines, block, mode = [], [], None
for ln in lines:
    if ln.startswith("<<<<<<<"):
        mode = "head"
        continue
    if ln.startswith("=======") and mode == "head":
        mode = "theirs"
        continue
    if ln.startswith(">>>>>>>") and mode == "theirs":
        out_lines.extend(block)  # HEAD-side lines first
        block = []
        mode = None
        continue
    if mode in ("head", "theirs"):
        block.append(ln)
    else:
        out_lines.append(ln)
assert mode is None, "conflict markers not fully consumed"
out = "\n".join(out_lines)
# dedupe identical lines safety (byte-identical entries only)
seen, lines = set(), []
for ln in out.split("\n"):
    if ln.strip().startswith("- [2026-09-27") and ln in seen:
        continue
    if ln.strip().startswith("- [2026-09-27"):
        seen.add(ln)
    lines.append(ln)
out = "\n".join(lines)
w("CODELY.md", out.encode("utf-8"))
notes.append("CODELY.md memory-union: both entries kept (bm-c r76 + bm-a R314)")

# ---- 2. autofill_state.json: mixed-dict+ledger
b2, b3 = side("results/autofill_state.json", 2), side("results/autofill_state.json", 3)
crlf = b2.count(b"\r\n") > 0
a, b = jload(b2), jload(b3)
la = a.get("launches", [])
lb = b.get("launches", [])
un = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in la + lb}
merged = sorted(un.values(), key=lambda x: str(x.get("ts", "")), reverse=True)[:50]
merged = sorted(merged, key=lambda x: str(x.get("ts", "")))  # asc write-back
outd = dict(a)
outd["launches"] = merged
ta = (a.get("last_tick") or {}).get("ts")
tb = (b.get("last_tick") or {}).get("ts")
outd["last_tick"] = a.get("last_tick") if (str(tb or "") <= str(ta or "")) else b.get("last_tick")
assert isinstance(outd["last_tick"], dict), "last_tick must stay dict"
txt = json.dumps(outd, ensure_ascii=False, indent=1)
txt = txt.replace("\r\n", "\n")
data = txt.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
w("results/autofill_state.json", data)
notes.append(f"autofill launches union {len(la)}+{len(lb)}->{len(merged)} cap50, "
             f"last_tick ts {ta} vs {tb}, crlf={crlf}")

# ---- 3. rolling-ledger: compute_audit.json / regime_state.json
for path in ("results/compute_audit.json", "results/regime_state.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    outd = dict(b)  # take-new state fields from theirs (my newer run) base
    for key in ("history", "transitions", "launches"):
        if key in a or key in b:
            ua = a.get(key) or []
            ub = b.get(key) or []
            un = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in ua + ub}
            merged = sorted(un.values(), key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
            outd[key] = merged
            notes.append(f"{path} {key} union {len(ua)}+{len(ub)}->{len(merged)} "
                         f"(expect {len(un)})")
    # state fields: take-new by embedded ts
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    if ka and kb and str(va) >= str(vb):
        for k, v in a.items():
            if k not in ("history", "transitions", "launches"):
                outd[k] = v
    w(path, json.dumps(outd, ensure_ascii=False, indent=1).encode("utf-8"))
    json.loads(io.open(path, encoding="utf-8-sig").read())  # verify

# ---- 4. snapshot take-new by ts
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

# ---- 5. derive faces (manual classification): scorecard pair + daily_report pair
for path in ("results/scorecard_v1.json", "results/strategy_scorecard.json"):
    b2, b3 = side(path, 2), side(path, 3)
    a, b = jload(b2), jload(b3)
    meta = {"generated", "elapsed_sec", "ts", "generated_at", "asof"}

    def strip(d):
        return {k: v for k, v in d.items() if k not in meta} if isinstance(d, dict) else d
    scope_ok = json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)
    ka, va = pick_ts(a)
    kb, vb = pick_ts(b)
    win = "origin" if (ka and (not kb or str(va) >= str(vb))) else "replay"
    w(path, b2 if win == "origin" else b3)
    notes.append(f"{path} derive-face take-new={win} metadata-only-diff={scope_ok} "
                 f"({ka}={va} vs {kb}={vb})")
    json.loads(io.open(path, encoding="utf-8-sig").read())

# daily report pair: json twin decides the side, md follows
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

print(json.dumps({"resolved": resolved, "notes": notes}, ensure_ascii=False, indent=1))
print("ALL PARSE-VERIFIED")
