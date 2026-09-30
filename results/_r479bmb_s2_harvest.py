"""r479 bm-b: S2 harvest (verify results, close claim, done-flip shard row)
+ controlled merge probe on the S1 revert mystery."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import merge_lane_views as m  # noqa: E402

TS = "2026-09-30T21:45:10+08:00"


def main():
    # 1) S2 result integrity
    p = os.path.join(ROOT, "results", "p2cal_ext", "shard-2-of-4.json")
    d = json.load(open(p, encoding="utf-8"))
    fam = d["families"]
    na = sum(blk.get("n", 0) for blk in fam.values())
    la = sum(len(blk.get("runs", [])) for blk in fam.values())
    print(f"S2 result: shard={d.get('shard')} nshards={d.get('nshards')} "
          f"ranges={d.get('a_range')}/{d.get('b_range')} "
          f"families={ {k: blk.get('n') for k, blk in fam.items()} } "
          f"declared_n={na} listed_runs={la} cutoff={d.get('evidence_cutoff')}")
    ok = all(blk.get("n") == len(blk.get("runs", [])) for blk in fam.values())
    print("S2 integrity:", "PASS" if ok and na == 550 else "FAIL")

    # 2) close my S2 claim (harvest)
    cp = os.path.join(ROOT, "results", "pool_claims",
                      "P2NULL-KLIFT-K2200-S2", "p2null-klift-s2-0of1.bm-b.json")
    claim = json.load(open(cp, encoding="utf-8"))
    claim["state"] = "closed"
    claim["note"] = ("r479 bm-b: burn complete 370.9s 550 runs "
                     "(A j1000-1499 + B j100-149), single-shot saved "
                     "results/p2cal_ext/shard-2-of-4.json; closed claim "
                     "awaiting harvest flip per O-2210 vocabulary")
    claim["heartbeat"] = TS
    json.dump(claim, open(cp, "w", encoding="utf-8"), indent=1)
    print("S2 claim closed")

    # 3) S2 shard row done-flip (shared + bm-b lane), TRUE timestamp
    for pf in ("runnable_pool.json", "runnable_pool.bm-b.json"):
        fp = os.path.join(ROOT, "results", pf)
        pool = json.load(open(fp, encoding="utf-8"))
        for e in pool.get("entries", []):
            if e.get("id") != "P2NULL-KLIFT-K2200-S2":
                continue
            for sh in e.get("shards", []):
                if sh.get("key") == "p2null-klift-s2-0of1":
                    sh["status"] = "done"
                    sh["result_ref"] = "results/p2cal_ext/shard-2-of-4.json"
                    sh["done_note"] = ("bm-b r479 harvest flip: burn complete "
                                       "370.9s 550 runs, empirical "
                                       "single-shot completion")
                    sh["owner"] = "bm-b"
                    sh["owner_since"] = TS
                    print("flipped", pf, "S2 shard done")
        json.dump(pool, open(fp, "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)

    # 4) settle + verify
    r = m.sync_face("runnable_pool", results_dir=os.path.join(ROOT, "results"))
    print("settle:", r.get("status"))
    v = m.face_view("runnable_pool", results_dir=os.path.join(ROOT, "results"))
    for e in v.get("entries", []):
        if "P2NULL" in str(e.get("id", "")):
            print(e.get("id"), "|",
                  [(s.get("key"), s.get("status"), s.get("owner"))
                   for s in e.get("shards", [])])

    # 5) controlled probe: what does _merge_shard_same_key do with the
    #    S1 pair (my done row vs bm-c lane ready row)?
    my_row = {"key": "x", "status": "done", "owner": None,
              "owner_since": TS}
    other_row = {"key": "x", "status": "ready", "owner": None,
                 "owner_since": None, "checkpoint": "c", "note": "n"}
    merged = m._merge_shard_same_key(dict(my_row), dict(other_row))
    print("probe shared-done vs lane-ready ->", merged.get("status"))
    merged2 = m._merge_shard_same_key(dict(other_row), dict(my_row))
    print("probe lane-ready vs shared-done ->", merged2.get("status"))


if __name__ == "__main__":
    main()
