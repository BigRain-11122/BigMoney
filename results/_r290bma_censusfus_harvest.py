# -*- coding: utf-8 -*-
"""R290 bm-a: deterministic harvest of CENSUS-FUS-S2-W1 (r244 landed-marker
law). Fail-closed product verification -> pool entry+shard flip done ->
gate_attrition row append (exploration face, zero judged cells, prereg sec.8
null-annotation law). Idempotent: re-run no-op."""
import io
import json
import os

RES = "results/census_fusion_s2"
POOL = "results/runnable_pool.json"
ATTR = "results/gate_attrition.json"


def _load(path):
    return json.load(io.open(path, encoding="utf-8"))


def _save(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def main():
    # 1) fail-closed landed-product verification
    r = _load(RES + "/w1_results.json")
    assert r["batch"] == "CENSUS_FUS_S2_W1", r["batch"]
    assert r["evidence_cutoff"] == "2026-09-24", r["evidence_cutoff"]
    assert r["face"].startswith("EXPLORATION"), r["face"]
    assert r["audit"]["ledger_trials_added"] == 4518, r["audit"]
    assert r["trials_ledger"]["total"] == 205418, r["trials_ledger"]
    assert r["data_gate"]["ok"] is True, r["data_gate"]
    for prod in r["products"]:
        assert os.path.exists(RES + "/" + prod), prod
    print("verify: products 5/5, N=4518, ledger 205418, gate ok")

    # 2) pool flip done (entry + shard)
    pool = _load(POOL)
    ent = None
    for e in pool["entries"]:
        if e["id"] == "CENSUS-FUS-S2-W1":
            ent = e
            break
    assert ent is not None, "pool entry missing"
    assert ent["runner"] == "scripts/census_fusion_s2.py", ent["runner"]
    flipped = False
    if ent["status"] != "done":
        ent["status"] = "done"
        flipped = True
    for sh in ent["shards"]:
        if sh["key"] != "censusfus-0of1":
            continue
        if sh["status"] != "done":
            sh["status"] = "done"
            sh["checkpoint"] = ("results/census_fusion_s2/w1_results.json audit "
                                "segment = landed marker (R290 bm-a harvest)")
            flipped = True
    ent["harvest_note"] = (
        "R290 bm-a deterministic harvest (r244 law): burn landed 2026-09-27 "
        "03:00:11 via autofill launch-claim 1150732c (checkpoint resume); "
        "N=4518 (4060 cand + 58 rs ctrl + 400 nulls, seed band 20274500..20274899) "
        "ledger 200900+4518=205418; EXPLORATION FACE verdict-free -- zero judged "
        "cells, zero registration effect; prereg s7/s8 single-finalization "
        "(P1 CONFIRMED 74/306=24.2% top-decile 2.4x, P2 CONFIRMED cand p95 "
        "0.4164 > null p95 0.3526, P3 NOT-CONFIRMED rev-x-mom IC median +0.0103, "
        "P4 disclosure face satisfied); attrition row appended; post_review row "
        "T-86-S2-CENSUS-FUS-W1 registered on stable artifacts (R264 law)")
    pool["updated_at"] = "2026-09-27 03:00:11"
    _save(POOL, pool)
    print("pool: entry+shard flipped done" + ("" if flipped else " (already)"))

    # 3) attrition row append (idempotent)
    attr = _load(ATTR)
    if any(e.get("batch") == "CENSUS_FUS_S2_W1" for e in attr["entries"]):
        print("attrition: row already present; no-op")
    else:
        attr["entries"].append({
            "batch": "CENSUS_FUS_S2_W1",
            "ts": "2026-09-27 03:00:11",
            "kind": "measurement",
            "cells_ledger_delta": 4518,
            "ledger_total_after": 205418,
            "gates": {
                "face": "EXPLORATION (prereg sec.4: zero judged cells / zero "
                        "registration effect)",
                "g1_pass": None,
                "g2_eligible": None,
                "d6_reject": None,
                "judgment_lines": None,
            },
            "null_face": {
                "n_nulls": 400,
                "seed_band": "20274500..20274899",
                "x2_median": 0.0388,
                "x2_p95": 0.3526,
            },
            "structure_face": {
                "cand_x2_p95": 0.4164,
                "cand_above_null_p95": 363,
                "cand_above_null_p95_pct": 8.9,
                "base_rate_pct": 5.0,
                "verdict": "structure-exists-moderate (exploratory, no "
                           "registration effect)",
            },
            "note": "R290 bm-a harvest: factor-level fusion census wave-1 "
                    "core48; sole output = sec.4 family aggregation feeding "
                    "T-23 intake funnel; judgment lines null per prereg sec.8 "
                    "exploration-face annotation law",
        })
        _save(ATTR, attr)
        print("attrition: row appended; entries =", len(attr["entries"]))

    print("harvest complete (exit 0)")


if __name__ == "__main__":
    main()
