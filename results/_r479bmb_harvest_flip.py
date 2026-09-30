"""r479 bm-b: harvest done-flip P2NULL-KLIFT-K2200 shards S0/S1 (empirical
single-shot completion: A n=500 + B n=50 runs verified in results files).

r180 wedge law: done shards never re-fire. The S1 shard row carries
owner=None -> fleet pickers relaunch it as duplicate burn (白跑 per CEO
O-20260930-2054 CPU-efficiency order). Cross-lane transparent bookkeeping:
original owner preserved, owner_since bumped to flip time so the merger
base-row resolution (newer owner_since wins) carries the done state
fleet-wide at next settle. Entry-level status stays bm-c's (batch finalize
owner); only shard compute-scheduling rows flip."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = "2026-09-30T21:39:30+08:00"
POOL_FILES = [
    os.path.join(ROOT, "results", "runnable_pool.json"),
    os.path.join(ROOT, "results", "runnable_pool.bm-b.json"),
]
FLIPS = {
    "P2NULL-KLIFT-K2200-S0": ("p2null-klift-s0-0of1",
                               "results/p2cal_ext/shard-0-of-4.json"),
    "P2NULL-KLIFT-K2200-S1": ("p2null-klift-s1-0of1",
                               "results/p2cal_ext/shard-1-of-4.json"),
}
DONE_NOTE = (
    "bm-b r479 harvest flip: empirical single-shot completion verified "
    "(A family n=500 runs + B family n=50 runs present in result file, "
    "evidence_cutoff 2026-09-22); r180 done-shard wedge law + CEO "
    "O-20260930-2054 anti-blind-burn; original owner preserved"
)


def main():
    for pf in POOL_FILES:
        with open(pf, encoding="utf-8") as fh:
            pool = json.load(fh)
        changed = False
        for e in pool.get("entries", []):
            if e.get("id") not in FLIPS:
                continue
            key, ref = FLIPS[e["id"]]
            for sh in e.get("shards", []):
                if sh.get("key") == key and sh.get("status") != "done":
                    sh["status"] = "done"
                    sh["result_ref"] = ref
                    sh["done_note"] = DONE_NOTE
                    sh["owner_since"] = TS
                    changed = True
                    print("FLIPPED", os.path.basename(pf), e["id"], key)
        if changed:
            with open(pf, "w", encoding="utf-8") as fh:
                json.dump(pool, fh, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
