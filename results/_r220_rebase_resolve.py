"""r220 conflict resolver v2: autofill_state.json rolling-ledger union.

R209 law (bm-a, just landed on origin): reproduce the PRODUCER canonical
format per file (Tools/autofill.py _save_state: json.dump ensure_ascii=False
indent=1, key order preserved, NO foreign keys) -- v1 of this resolver
injected a _r220_union_note key and reordered launches = whole-file rewrite
diff (572/563 lines), never pushed (push rejected, caught here).

Recipe (r161/r185/r188/r203 + R208 snapshot-vs-ledger + R209 format):
- launches: full-blob identity union (json-dump identity, both sides),
  ts-sorted, rolling cap 50 -- records from both machines are distinct
  real events (entry/shard/pid differ)
- last_tick: dict, take newer by inner ts, WHOLE-dict assign (r203 type law)
- key order: HEAD(origin) side's key order verbatim, no added keys
- write: producer-canonical json.dump(ensure_ascii=False, indent=1)
- verify-parse BEFORE write-back + git add (r185 order law)
"""
import json
import subprocess
import sys


def blob(rev):
    out = subprocess.run(["git", "show", f"{rev}:results/autofill_state.json"],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        sys.exit(f"git show {rev} failed: {out.stderr}")
    return json.loads(out.stdout)


ours = blob("HEAD")          # origin/main side (producer-canonical form)
mine = blob("REBASE_HEAD")   # local replayed commit (v1 resolver output)

ol, ml = ours.get("launches", []), mine.get("launches", [])
seen, union = set(), []
for rec in ol + ml:                       # origin first, then mine
    k = json.dumps(rec, sort_keys=True)   # full-record identity
    if k in seen:
        continue
    seen.add(k)
    union.append(rec)
union.sort(key=lambda x: str(x.get("ts", "")))
CAP = 50
union = union[-CAP:] if len(union) > CAP else union

ot, mt = ours.get("last_tick", {}), mine.get("last_tick", {})
last_tick = ot if str(ot.get("ts", "")) >= str(mt.get("ts", "")) else mt
assert isinstance(last_tick, dict), "r203 type law: last_tick stays dict"

merged = dict(ours)                        # origin key order verbatim
merged["launches"] = union
merged["last_tick"] = last_tick            # no foreign keys added (R209)

json.loads(json.dumps(merged))             # verify-parse before write
with open("results/autofill_state.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
re = json.load(open("results/autofill_state.json", encoding="utf-8"))
assert isinstance(re.get("last_tick"), dict)
assert len(re["launches"]) == len(union)
assert "_r220_union_note" not in re
print(f"UNION v2 OK: launches {len(ol)}+{len(ml)} -> {len(union)} (cap {CAP}) "
      f"| last_tick ts={last_tick.get('ts')} | origin keys order kept: "
      f"{list(re.keys())}")
