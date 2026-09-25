"""r221 rebase-conflict union for results/autofill_state.json (bm-b).

Usage: python results/_r221_af_union.py <base_blob_spec> <incoming_blob_spec>
e.g. :2:results/autofill_state.json :3:results/autofill_state.json  (rebase
stages: 2=ours=surviving base=bm-a side, 3=theirs=replayed commit=my side)

r185/r188/r208/r220 authoritative recipe:
- full-blob sources (never marker-block sides -- r220 stash lesson)
- launches: identity-dedupe union, keep last 50 (rolling cap design)
- last_tick: newer ts wins, same-second tie -> base (r140); stays dict (r203)
- base key order preserved (r209 producer-canonical: indent=1,
  ensure_ascii=False, no foreign keys); scalar diffs disclosed
- parse-validated BEFORE any git add (r185)
"""
import json, subprocess, io, sys

def blob(spec):
    raw = subprocess.run(["git", "show", spec],
                         capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))

base_spec, inc_spec = sys.argv[1], sys.argv[2]
base = blob(base_spec)
inc = blob(inc_spec)

out = {}                      # base key order first (r209 origin key order)
for k in base:
    out[k] = base[k]

# launches union (dedupe by exact identity), rolling cap 50
seen, merged = set(), []
for e in base.get("launches", []) + inc.get("launches", []):
    key = json.dumps(e, ensure_ascii=False, sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    merged.append(e)
out["launches"] = merged[-50:]

lt_b = base.get("last_tick", {}) or {}
lt_i = inc.get("last_tick", {}) or {}
ts_b = lt_b.get("ts") or ""
ts_i = lt_i.get("ts") or ""
out["last_tick"] = lt_i if (ts_i and ts_i > ts_b) else lt_b  # tie -> base

# disclose other-key scalar diffs; base value kept (shared ledger face)
diffs = []
for k in out:
    if k in ("launches", "last_tick", "rebase_union_note"):
        continue
    if k in inc and isinstance(out[k], (str, int, float, bool)) \
            and out[k] != inc[k]:
        diffs.append((k, out[k], inc[k]))

out["rebase_union_note"] = (
    f"r221 rebase union (bm-b): base {base_spec} + incoming {inc_spec}; "
    f"launches union {len(base.get('launches', []))}+"
    f"{len(inc.get('launches', []))} -> {len(out['launches'])} cap50; "
    f"last_tick take-newer (base {ts_b} vs inc {ts_i} -> "
    f"{out['last_tick'].get('ts')}); base key order preserved")

payload = json.dumps(out, ensure_ascii=False, indent=1)
parsed = json.loads(payload)                       # parse-validate (r185)
assert isinstance(parsed["last_tick"], dict), "last_tick must stay dict (r203)"
with io.open("results/autofill_state.json", "w", encoding="utf-8",
             newline="") as f:
    f.write(payload)
print("union: launches", len(base.get("launches", [])), "+",
      len(inc.get("launches", [])), "->", len(out["launches"]),
      "| last_tick winner:", out["last_tick"].get("ts"),
      "| scalar diffs disclosed:", diffs)
