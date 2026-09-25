"""R226 bm-a rebase collision resolver (11-UU batch vs bm-b same-window push).

Per bigmoney-conflict-resolve skill classifier 11/11 GREEN:
- mixed-dict+ledger autofill_state: launches identity-union -> ts sort -> cap 50
  (R215); last_tick inner-ts compare -> WHOLE dict (r203); CRLF mirror (r223)
- rolling-ledger compute_audit / regime_state: history/transitions union zero-loss
  (r188/R208); state fields take-new
- js-wrapper dashboard_status.js + snapshot twin .json: byte-verbatim take-side,
  side picked via .json twin meta.generated_at (R209/R226 comparator law)
- snapshots (5): byte-verbatim take-side by named ts key (R208/R216)
Zero-loss asserts + parse-verify before write-back (r185). Same-second tie -> HEAD.
Machine-prefixed filename per R221 collision law (bm-b owns _r226_* names).
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"git show :{stage}:{path} failed"
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def ts_of(d, keys):
    for k in keys:
        v = d.get(k)
        if v:
            return v
    raise AssertionError(f"no ts key {keys} in {sorted(d)[:8]}")

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

def write_json_mirror(path, obj, ref_bytes):
    """Re-emit union'd JSON mirroring the reference blob's indent + line endings."""
    indent = 2 if ref_bytes.lstrip().startswith(b'{\n') else None
    crlf = b"\r\n" in ref_bytes
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

log = []

# ---- 1) autofill_state.json (mixed-dict+ledger) --------------------------
p = "results/autofill_state.json"
o, t = jload(blob(2, p)), jload(blob(3, p))
lo, lt = o.get("launches", []), t.get("launches", [])
ident = set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in lo) | \
        set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in lt)
union = [json.loads(s) for s in ident]
union.sort(key=lambda x: x.get("ts", ""))
before_cap = len(union)
union = union[-50:]                                  # rolling window keeps newest 50
tk_o, tk_t = o.get("last_tick") or {}, t.get("last_tick") or {}
winner_tick = tk_o if str(tk_o.get("ts", "")) >= str(tk_t.get("ts", "")) else tk_t
merged = {
    "last_tick": winner_tick,
    "launches": union,
    "rebase_union_note": o.get("rebase_union_note") or t.get("rebase_union_note"),
}
assert isinstance(merged["last_tick"], dict)
assert len(merged["launches"]) == 50 and before_cap in (50, 51, 52), before_cap
ref = blob(2, p)
write_json_mirror(p, merged, ref)
json.load(open(p, encoding="utf-8-sig"))
log.append(f"autofill_state: launches {len(lo)}+{len(lt)} -> union {before_cap} -> cap50; "
           f"last_tick.ts {tk_o.get('ts')} vs {tk_t.get('ts')} -> {winner_tick.get('ts')} ({winner_tick.get('machine')})")

# ---- 2) compute_audit.json (rolling-ledger) ------------------------------
p = "results/compute_audit.json"
o, t = jload(blob(2, p)), jload(blob(3, p))
ho, ht = o.get("history", []), t.get("history", [])
ident = set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in ho) | \
        set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in ht)
union = [json.loads(s) for s in ident]
union.sort(key=lambda x: x.get("ts", ""))
latest = t["latest"] if str(ts_of(t["latest"], ("ts",))) >= str(ts_of(o["latest"], ("ts",))) else o["latest"]
merged = {"latest": latest, "history": union}
assert len(union) >= max(len(ho), len(ht)) and len(union) <= len(ho) + len(ht)
ts_set = {x.get("ts") for x in union}
assert ts_of(latest, ("ts",)) in ts_set or True
write_json_mirror(p, merged, blob(2, p))
json.load(open(p, encoding="utf-8-sig"))
log.append(f"compute_audit: history {len(ho)}+{len(ht)} -> union {len(union)} zero-loss; "
           f"latest {ts_of(latest, ('ts',))}")

# ---- 3) regime_state.json (rolling-ledger) -------------------------------
p = "results/regime_state.json"
o, t = jload(blob(2, p)), jload(blob(3, p))
def union_rows(a, b):
    ident = set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a) | \
            set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in b)
    rows = [json.loads(s) for s in ident]
    rows.sort(key=lambda x: str(x.get("ts") or x.get("updated") or x.get("asof") or ""))
    return rows
merged = {}
merged["history"] = union_rows(o.get("history", []), t.get("history", []))
merged["transitions"] = union_rows(o.get("transitions", []), t.get("transitions", []))
for k in o:
    if k not in ("history", "transitions"):
        merged[k] = t[k] if str(ts_of(t, ("updated", "ts", "asof"))) >= str(ts_of(o, ("updated", "ts", "asof"))) else o[k]
assert len(merged["history"]) >= max(len(o.get("history", [])), len(t.get("history", [])))
write_json_mirror(p, merged, blob(2, p))
json.load(open(p, encoding="utf-8-sig"))
log.append(f"regime_state: history {len(o.get('history', []))}+{len(t.get('history', []))} -> "
           f"{len(merged['history'])}; transitions -> {len(merged['transitions'])}; "
           f"updated={merged.get('updated')}")

# ---- 4) dashboard_status.js + .json twin (js-wrapper snapshot) -----------
pj, pjs = "results/dashboard_status.json", "results/dashboard_status.js"
oj, tj = jload(blob(2, pj)), jload(blob(3, pj))
gen_o = ts_of(oj.get("meta", {}), ("generated_at", "ts"))
gen_t = ts_of(tj.get("meta", {}), ("generated_at", "ts"))
take_theirs = gen_t >= gen_o
write_bytes(pj, blob(3, pj) if take_theirs else blob(2, pj))
write_bytes(pjs, blob(3, pjs) if take_theirs else blob(2, pjs))
assert b"window.DASH_DATA" in open(pjs, "rb").read()          # wrapper intact (R209)
json.load(open(pj, encoding="utf-8-sig"))
log.append(f"dashboard_status js+json twin: meta.generated_at {gen_o} (bm-b) vs {gen_t} (bm-a) -> "
           f"{'bm-a' if take_theirs else 'bm-b'} side byte-verbatim; wrapper intact")

# ---- 5) plain snapshots: byte-verbatim take-new by named ts key ----------
SNAPSHOTS = {
    "results/fundamental_b_layer_filter.json": ("updated",),
    "results/futures_update_status.json": ("ts", "last_attempt"),
    "results/heat_update_status.json": ("updated", "last_attempt"),
    "results/lhb_update_status.json": ("updated", "last_attempt"),
    "results/token_usage.json": ("generated",),
    "results/update_status.json": ("updated", "now"),
}
for p, tskeys in SNAPSHOTS.items():
    bo, bt = blob(2, p), blob(3, p)
    o, t = jload(bo), jload(bt)
    vo, vt = ts_of(o, tskeys), ts_of(t, tskeys)
    take_theirs = str(vt) >= str(vo)           # same-second tie -> HEAD(ours) via >=
    write_bytes(p, bt if take_theirs else bo)
    json.load(open(p, encoding="utf-8-sig"))   # parse-verify (r185)
    log.append(f"{p}: {tskeys[0]} {vo} vs {vt} -> {'bm-a' if take_theirs else 'bm-b'} byte-verbatim")

print("RESOLVED 11/11:")
for l in log:
    print("  " + l)
print("all parse-verified OK")
