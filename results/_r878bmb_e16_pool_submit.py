#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r878 bm-b: append 12 E16-ALPHAGEN-RG-SHARD pool entries (atomic)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

IDS = [f"E16-ALPHAGEN-RG-SHARD-{k}OF12" for k in range(12)]

PREREG_REF = (
    "research/E16_ALPHAGEN_RG_CENSUS_P1.md FROZEN bm-b r878 commit 1f70c9b "
    "(measurement census K=200 = 120 d1 + 80 d2, B=200 same-mask permutation "
    "nulls/formula, window 2018-01-01+, evidence_cutoff 2026-10-09 D2 "
    "lockbox, universe sff._universe 3514 + P4_BATCH2 dynamic clauses, "
    "verdict census_holds=observed_family_max_abs_icir > null_family_p95; "
    "ledger trials=200 roster pin (nulls=calibration); seeds "
    "e16_alphagen_rg_gen=20620000 / e16_alphagen_rg_null=20620100 "
    "registered at freeze one-step R250 law)")

DATA_GATES = (
    "in-runner fail-closed exit 2 (prereg sec.2): t23 gate_face (panel "
    "complete + disk-truth + fresh) + roster sha16==1d06d218b2cbf870 + "
    "seeds registered 20620000/20620100 + cal window 2255 rows (warmup "
    "130, census 2125, first 2017-06-26, last 2026-10-09) + universe band "
    "3400-3600 + panel cutoff >= 2026-10-09 (D2 lockbox: batch face "
    "truncated to 2026-10-09 regardless of later bars); per-formula "
    "checkpoint ckpt/shard_<k>of12.jsonl cross-kill resume; skip >10% "
    "shard-face honest in product")


def entry(k):
    return {
        "consumer_plan": (
            "shard product results/alphagen_rg/shard_"
            f"{k}of12.json -> finalize (observing round after 12/12 "
            "shards complete, refuse-if-exists) -> results/alphagen_rg/"
            "CENSUS-2026-10-09.json verdict face: census_holds=True -> N2 "
            "U3 channel-1 drafting window opens via PREREG_TEMPLATE (RL "
            "build licensed before training spend); False -> RL build "
            "killed (G2 fallback, academic citation only); supply floor "
            "face: pool_ready 0 -> 12 (E16 leg-2 remedy per state verdict "
            "r877)"),
        "data_gates": DATA_GATES,
        "entered_at": "2026-10-11 12:3x",
        "entered_by": "bm-b r878",
        "host_gates": [{"kind": "dir_nonempty",
                        "path": "data/astock_daily/per"}],
        "id": IDS[k],
        "lane_note": (
            "R31 lane law: data/astock_daily/per is a bm-b-lane "
            "gitignored machine-local panel -- all 12 shards burn on bm-b; "
            "host_gates let panel-less machines skip honestly; panel "
            "cache npz (~520MB, gitignored) built once by the first shard "
            "run, deterministic rebuild if absent (cutoff-keyed)"),
        "lane_owner": "bm-b",
        "prereg_ref": PREREG_REF,
        "priority": 1,
        "runner": "scripts/alphagen_rg_census.py",
        "runner_args": ["run", "--shard", str(k), "--shards", "12"],
        "shards": [{
            "checkpoint": (
                "results/alphagen_rg/ckpt/shard_"
                f"{k}of12.jsonl (per-formula append jsonl, done-set "
                "resume cross-kill, truncated-tail tolerated)"),
            "key": f"e16-rg-{k}of12",
            "note": (
                "formulas i%12==" + str(k) + " ("
                + str(sum(1 for i in range(200) if i % 12 == k))
                + " formulas); est 5-15min/shard with workers=8"),
            "owner": None,
            "owner_since": None,
            "status": "ready",
        }],
        "status": "ready",
        "ticket_ref": (
            "state/queue/explore.md E16 (supply-floor chain leg-4, "
            "external catalog #17 / T23 slice-2 POSITIVE-with-riders "
            "continuation; bm-b r877 registration + r878 leg-2; F-04 MSG-"
            "20261011-1215-bmb; prereg freeze commit 1f70c9b precedes "
            "runner build precedes ANY burn, R99 law)"),
        "worker_class": "bm-hosted",
        "workers_plan": {
            "note": (
                "ProcessPool via parallel_runner.run_cells_parallel over "
                "per-formula tasks (top-level picklable fn, npz member "
                "reads per task ~180MB); selftest 31/31 hermetic "
                "(incl injected-signal ICIR leg + permutation determinism "
                "+ OLS/quantile/rank hand-values); autofill multicore law "
                "O-2026-09-30-2355 satisfied (real ProcessPool)"),
            "priority": "BelowNormal",
            "workers": 8,
        },
    }


def main():
    with open(POOL, "r", encoding="utf-8") as f:
        pool = json.load(f)
    existing = {e.get("id") for e in pool["entries"]}
    clash = [i for i in IDS if i in existing]
    if clash:
        print(json.dumps({"refuse": True, "clash": clash}))
        return 1
    pool["entries"].extend(entry(k) for k in range(12))
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, POOL)
    with open(POOL, "r", encoding="utf-8") as f:
        back = json.load(f)
    ids = [e.get("id") for e in back["entries"]]
    ok = all(i in ids for i in IDS) and len(ids) == len(pool["entries"])
    print(json.dumps({"appended": 12, "total_entries": len(ids),
                     "verify": ok, "ids_head": IDS[0], "ids_tail": IDS[-1]}))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
