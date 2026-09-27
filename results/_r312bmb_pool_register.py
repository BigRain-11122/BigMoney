# -*- coding: utf-8 -*-
"""r312 bm-b pool registration: DECISION-CHAIN-E2E-X2 stage-A x2 member
curve re-derivation shards (T-90 CEO ticket O-20260927-0758; prereg v1.1 +
zero-run amendments s9.2/s9.3; runner scripts/decision_chain_e2e.py built+
gated this round: selftest 23/23 hermetic, G-REPRO 12/12 bit-equal real-fire
48.9s, x2 probe 36/36 cells 10.3s, direction gate 36/36 x2<base).

9 shards = 4 legacy (1,255 starts) + 5 deep (1,506 starts); ~1,884-1,812
cells per shard (6 members x startpoints); T54 multi-entry pattern; lane
open (both machines carry the t18 deep panel per T54 precedent + legacy =
local core48 CSVs). Finalize (stage B four-arm overlay) is NOT pooled: it
needs the machine-local t34 base-curve checkpoint -> bm-b harvest round.
"""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

SHARDS = [
    ("LA", "legacy", 0, 314),
    ("LB", "legacy", 314, 628),
    ("LC", "legacy", 628, 942),
    ("LD", "legacy", 942, 1255),
    ("DA", "deep", 0, 301),
    ("DB", "deep", 301, 602),
    ("DC", "deep", 602, 904),
    ("DD", "deep", 904, 1205),
    ("DE", "deep", 1205, 1506),
]
PREREG_REF = ("research/DECISION_CHAIN_E2E_P1.md v1.1 re-frozen r311 (GM "
              "RULING MSG-0814, O-0809 amendment-driven) + r312 zero-run "
              "amendments s9.2 (bootstrap seed 20260929->20261001, taken "
              "by t11_negday_ic, order-law) + s9.3 (G-V3 leg-2 equality "
              "assertion = false premise: v1 live probe vs v3 calibration "
              "layer are different regime versions by law; amended to "
              "freshness+alphabet+disclosure)")
TICKET_REF = ("T-2026-09-27-90 (CEO O-20260927-0758 decision chain "
              "E2E backtest -- THE most important asset; claimed bm-b r310; "
              "F-04 MSG-20260927-0816-bm-b; runner built+gated r312)")
DATA_GATES = ("in-runner fail-closed: SEED_REGISTRY assert "
              "(decision_chain_e2e=20261001, s9.2) + G-ANCHOR 6/6 (exit 3) "
              "+ G-CENSUS vs t22 finalize record live-read (exit 3) + "
              "CostPatch(2.0) multiplier law (t22 Erratum-1, never "
              "COST_X2_RATE) + per-shard row-level checkpoint resume (t22 "
              "law, truncated-tail tolerated). r312 real-data probe: "
              "36/36 cells 10.3s on 11 workers + direction gate 36/36 "
              "(x2 ret_12m < base on every cell, r82 inverted-face trap "
              "absent) + G-REPRO 12/12 bit-equal vs t34 verdict (legacy "
              "0.4296/0.4659 deep 0.3942/0.4304 dd switches all equal)")


def main():
    pool = json.load(open(POOL, encoding="utf-8-sig"))
    entries = pool["entries"]
    have = {e.get("id") for e in entries}
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    for name, axis, lo, hi in SHARDS:
        eid = f"DECISION-CHAIN-E2E-X2-{name}"
        assert eid not in have, f"duplicate pool id {eid}"
        n_cells = 6 * (hi - lo)
        args = ["run", "--face", "x2", "--axis", axis, "--shard", name,
                "--pos-from", str(lo), "--pos-to", str(hi)]
        entry = {
            "id": eid,
            "ticket_ref": TICKET_REF,
            "prereg_ref": PREREG_REF,
            "runner": "scripts/decision_chain_e2e.py",
            "runner_args": args,
            "lane_owner": None,
            "priority": 1,
            "status": "ready",
            "entered_at": now,
            "data_gates": DATA_GATES,
            "workers_plan": {
                "workers": "runner t34 formula min(cores-2, ram_guard) "
                           "ProcessPool BelowNormal",
                "priority": "BelowNormal",
                "note": ("engine cells observed ~3.5/s on 11 workers incl. "
                         "worker warmup (r312 probe); est 5-20min/shard "
                         "(~1.8k cells); O-2130 compliant; autofill C8 "
                         "owns the spawn")},
            "shards": [{
                "key": f"dce2-{axis}-{name.lower()}",
                "status": "ready",
                "owner": None,
                "owner_since": None,
                "checkpoint": (f"results/decision_chain/curves_x2_{axis}_"
                               f"{name.lower()}.jsonl (row-level done-key "
                               "resume, t22 law) + done_x2 marker json"),
                "note": (f"6 members x {hi - lo} starts = {n_cells} cells"
                         + ("; 36 probe cells already checkpointed (r312, "
                            "resume-skipped)" if name == "LA" else "")),
            }],
        }
        entries.append(entry)
        added.append(eid)
    # r301/r305 contract asserts before write
    for e in entries:
        if e.get("id", "").startswith("DECISION-CHAIN-E2E-X2"):
            assert e.get("status") == "ready" and e.get("runner")
            assert e.get("workers_plan"), "r305 law: workers_plan mandatory"
            assert e.get("shards"), "r301 law: shards non-empty"
    pool["updated_at"] = now
    text = json.dumps(pool, ensure_ascii=False, indent=1)
    json.loads(text)                      # parse-validate pre-write (r185)
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    os.replace(tmp, POOL)
    print(f"registered {len(added)} entries: {', '.join(added)}")


if __name__ == "__main__":
    main()
