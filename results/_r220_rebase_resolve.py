"""r220 conflict resolver: autofill_state.json rolling-ledger union (r161/r185/r188/r203 recipe).

Both sides extracted via git show (authoritative blobs), union merge:
- launches: full-blob identity union, ts-sorted, cap 50 rolling window
- last_tick: dict type -- compare inner 'ts' field, assign WHOLE dict (r203 type law)
- scalar counters: side-by-side disclosure, take newer-side context
Verify-parse BEFORE write-back + git add (r185 order law).
"""
import json, subprocess, sys

def blob(rev):
    out = subprocess.run(["git", "show", f"{rev}:results/autofill_state.json"],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        sys.exit(f"git show {rev} failed: {out.stderr}")
    return json.loads(out.stdout)

ours = blob("HEAD")        # origin/main side (bm-a latest, incl. its own tick runs)
mine = blob("REBASE_HEAD") # bm-b replayed commit (my pre-pull tick sync)

ol, ml = ours.get("launches", []), mine.get("launches", [])
def lid(x):
    # launch record identity: prefer unique id-ish fields, else full record
    return x.get("id") or x.get("ts") or json.dumps(x, sort_keys=True)

seen, union = set(), []
for rec in ol + ml:  # origin first (older history), then mine
    k = lid(rec)
    if k in seen:
        continue
    seen.add(k)
    union.append(rec)
# sort by ts if present, newest last (append-only ledger convention)
def ts_of(x):
    t = x.get("ts") or x.get("launched_at") or ""
    return str(t)
union.sort(key=ts_of)
cap = 50
dropped = max(0, len(union) - cap)
union = union[-cap:] if cap and len(union) > cap else union

ot, mt = ours.get("last_tick", {}), mine.get("last_tick", {})
# last_tick: dict, take newer by inner ts; same-second tie -> HEAD/ours (bm-a R208 convention)
def tick_ts(d):
    return str(d.get("ts", ""))
last_tick = ot if tick_ts(ot) >= tick_ts(mt) else mt
assert isinstance(last_tick, dict), "r203 type law: last_tick must stay dict"

merged = dict(ours)  # base = ours (has any new bm-a-side keys)
merged["launches"] = union
merged["last_tick"] = last_tick
# counters that exist on both: keep ours (origin-newer context) but disclose
merged["_r220_union_note"] = {
    "ours_launches": len(ol), "mine_launches": len(ml),
    "union_before_cap": len(union) + dropped, "dropped_over_cap": dropped,
    "last_tick_from": "HEAD(ours)" if last_tick is ot else "REBASE_HEAD(mine)",
    "ours_last_tick_ts": tick_ts(ot), "mine_last_tick_ts": tick_ts(mt),
}

json.loads(json.dumps(merged))  # verify-parse before write (r185 order law)
with open("results/autofill_state.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
reloaded = json.load(open("results/autofill_state.json", encoding="utf-8"))
assert isinstance(reloaded.get("last_tick"), dict)
assert len(reloaded["launches"]) == len(union)
print("UNION OK: launches", len(ol), "+", len(ml), "->", len(union),
      f"(cap-drop {dropped})", "| last_tick", tick_ts(last_tick), "| from",
      merged["_r220_union_note"]["last_tick_from"])
