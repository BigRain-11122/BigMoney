# INNOVATION-QUOTA-SLOT-2 shard-face closure (r211 bm-c)
# MSG-20260929-1038-bmb-ALL-W7-screen-berth item-4 flag: entry status=done (r186 bm-c
# flip, judged landed) but shard main stuck ready (legacy 2026-09-28 22:59:06).
# Three-way verified this round: entry done_note vs product cells vs prereg s7/s8.
import json, os, datetime

POOL = "results/runnable_pool.json"
pool = json.load(open(POOL, encoding="utf-8-sig"))

# three-way verification first (r201 precedent)
prod = json.load(open("results/innovation_quota/REPO-CALENDAR-P2.json", encoding="utf-8"))
c091 = prod["cells"]["CAL-SWITCH-GC091"]
c182 = prod["cells"]["CAL-SWITCH-GC182"]
assert round(c091["sharpe_full"], 2) == 41.89, c091
assert round(c182["sharpe_full"], 2) == 45.29, c182
assert prod["evidence_cutoff"] == "2026-09-22"
prereg_t = open("research/INNOVATION_QUOTA_W2_PREREG.md", encoding="utf-8").read()
assert "GC091" in prereg_t and "GC182" in prereg_t
print("three-way OK: product cells 41.89/45.29 == entry done_note judged numbers; prereg s7/s8 backfill present")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for e in pool["entries"]:
    if e["id"] == "INNOVATION-QUOTA-SLOT-2":
        assert e["status"] == "done", e["status"]
        assert e["done_at"] == "2026-09-28T22:58:00+08:00", e.get("done_at")
        assert "REPO-CALENDAR-P2.json" in e["result_ref"], e.get("result_ref")
        assert len(e["shards"]) == 1
        sh = e["shards"][0]
        assert sh["key"] == "main" and sh["status"] == "ready", sh
        assert sh["owner"] == "bm-c", sh
        sh["status"] = "done"
        sh["closed_at"] = now
        sh["note"] = ("shard face closed r211 bm-c per MSG-1038 item-4 flag: entry-level done flip "
                      "landed r186 2026-09-28T22:58:00 (judged-negative both cells, family slot closed "
                      "law s5, product + prereg s7/s8 backfill same-commit verified three-way this round); "
                      "shard status left ready at r186 = bookkeeping residue, zero science impact "
                      "(entry-level done already had autofill skip; no rerun owed, no reopen)")
        break
else:
    raise SystemExit("SLOT-2 entry not found")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "INNOVATION-QUOTA-SLOT-2"][0]
assert e2["status"] == "done" and e2["shards"][0]["status"] == "done"
print("shard closure OK:", e2["id"], "| entry:", e2["status"], "| shard:", e2["shards"][0]["status"],
      "| closed_at:", e2["shards"][0]["closed_at"])
