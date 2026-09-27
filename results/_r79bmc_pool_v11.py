# r79 bm-c control-plane: T19-PHANTOM-P1 pool entry v1.1 amendment note
# (prereg_ref + data_gates G-SET v2 semantics; zero-run discipline: no
#  completed run exists on disk at write time -- crash #4 left no results)
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
POOL = "results/runnable_pool.json"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entry = None
for e in pool["entries"]:
    if e["id"] == "T19-PHANTOM-P1":
        entry = e
        break
assert entry is not None, "T19-PHANTOM-P1 entry missing"

assert "v1.0 FROZEN r74a" in entry["prereg_ref"], "unexpected prereg_ref head"
entry["prereg_ref"] = (
    "research/T19_PHANTOM_P1.md v1.1 (v1.0 FROZEN r74a commit 79e8b1a7; "
    "s7 empty pre-run; seed base 68_500 SEED_REGISTRY-registered same commit; "
    "selftest 12/12 PASS r75 pre-registration) + v1.1 zero-run amendment "
    "r79 bm-c 2026-09-27 12:0x (G-SET v2: s4 list-multiset identity law "
    "falsified by real-fire crash #4 12:00:12 -- equity_fraction "
    "path-dependence drifts every downstream trade's entry date/hold_days/qty "
    "once a family is suppressed; hard faces = family-window entry "
    "suppression exactness + mask-surface purity; downstream identity drift "
    "-> disclosed face; amendment precedes any completed run: zero results "
    "on disk; selftest 17/17 incl crash#4-mode permanent legs)"
)

old_gate = "G-SET closure exact (actual 3 + placebo 150)"
assert old_gate in entry["data_gates"], "unexpected data_gates head"
entry["data_gates"] = entry["data_gates"].replace(
    old_gate,
    "G-SET v2 = family-window entry suppression exact (actual 3 + placebo "
    "150) + mask buy-surface purity; downstream identity drift disclosed "
    "per trader (downstream_drift field), never a gate input (v1.1 r79 "
    "amendment; v1 list-multiset law structurally unsatisfiable under "
    "re-simulation, crash #4 evidence)",
)

pool["updated_at"] = "2026-09-27 12:05:00"

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

with open(POOL, encoding="utf-8") as fh:
    back = json.load(fh)
e2 = [x for x in back["entries"] if x["id"] == "T19-PHANTOM-P1"][0]
assert "v1.1 zero-run amendment r79" in e2["prereg_ref"]
assert "G-SET v2" in e2["data_gates"] and old_gate not in e2["data_gates"]
assert back["updated_at"] == "2026-09-27 12:05:00"
print("pool entry updated + json.loads round-trip verified")
print("shard status:", e2["shards"][0]["status"], "owner:",
      e2["shards"][0]["owner"])
