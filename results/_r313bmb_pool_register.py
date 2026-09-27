# -*- coding: utf-8 -*-
"""r313 bm-b pool registration: PROS_REGIME_SEGMENTS_P1 shards (T-89
slice-1b; runner scripts/prospect_regime_segments.py built+gated this
round: selftest 9/9 hermetic, real-fire probe 22/22 cells 6.3s on 12
workers with G-ANCHOR 22/22 byte-reconcile + G-PANEL cutoff-frozen +
G-CENSUS 1256/1506 all PASS).

9 shards = 4 legacy (1,256 starts, s9 amended) + 5 deep (1,506 starts);
~6.6-6.9k cells per shard (22 members x startpoints), base face only
(prereg s3). Lane open (both machines carry the t18 deep panel per T54
precedent + legacy = local core48 CSVs + PROSPECT roster/anchor faces in
git). Finalize is NOT pooled: harvest round after all 9 done markers
(results/prospect_regime_segments.json + research/shortline CSV + prereg
s7 backfill + MARKET_STAGE_TABLE row refresh).
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
    ("LD", "legacy", 942, 1256),
    ("DA", "deep", 0, 301),
    ("DB", "deep", 301, 602),
    ("DC", "deep", 602, 904),
    ("DD", "deep", 904, 1205),
    ("DE", "deep", 1205, 1506),
]
PREREG_REF = ("research/PROS_REGIME_SEGMENTS_P1.md frozen e33984e4 r309 "
              "+ s9 zero-run amendment r313 (legacy census gate "
              "1255->1256 probe-adjudicated: 09-23->09-24 panel +1 "
              "start, results/_r313bmb_prospect_probe.json; cells "
              "legacy 27,632 + deep 33,132 + passive 2,762 "
              "= ~63,525)")
TICKET_REF = ("T-2026-09-26-89 (CEO O-20260927-0752 market-stage "
              "statistics; claimed bm-b r309 07:55:54, bm-a yielded "
              "sec.4; slice-1 prereg frozen r309; slice-1b runner "
              "built+gated r313; F-04 MSG-20260927-0757)")
DATA_GATES = ("in-runner fail-closed: G-ANCHOR 22/22 anchor_ok + "
              "constructive byte-reconcile vs member registration + "
              "uniform cutoff 2026-09-22 (exit 3) + G-PANEL cutoff-"
              "frozen truncation (legacy 2026-09-24, deep manifest "
              "2026-09-22, Monday-bar-proof, exit 3) + G-CENSUS "
              "1256/1506 == t22 record +{1,0} cross-check (exit 3) + "
              "row-contract first-row validation + per-cell checkpoint "
              "resume (t22 law, truncated-tail tolerated). r313 "
              "real-fire probe: 22/22 cells 6.3s on 12 workers, all "
              "gates PASS, ~3.5 cells/s")


def main():
    pool = json.load(open(POOL, encoding="utf-8-sig"))
    entries = pool["entries"]
    have = {e.get("id") for e in entries}
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    for name, axis, lo, hi in SHARDS:
        eid = f"PROSPECT-REGIME-SEGMENTS-{name}"
        assert eid not in have, f"duplicate pool id {eid}"
        n_cells = 22 * (hi - lo)
        args = ["run", "--axis", axis, "--shard", name,
                "--pos-from", str(lo), "--pos-to", str(hi)]
        entry = {
            "id": eid,
            "ticket_ref": TICKET_REF,
            "prereg_ref": PREREG_REF,
            "runner": "scripts/prospect_regime_segments.py",
            "runner_args": args,
            "lane_owner": None,
            "priority": 1,
            "status": "ready",
            "entered_at": now,
            "data_gates": DATA_GATES,
            "workers_plan": {
                "workers": "runner worker_cap() ProcessPool BelowNormal",
                "priority": "BelowNormal",
                "note": ("~6.6-6.9k cells/shard @ ~3.5 cells/s on 12 "
                         "workers -> est ~30min/shard; O-1136 "
                         "compliant; autofill C8 owns the spawn")},
            "shards": [{
                "key": f"prs-{axis}-{name.lower()}",
                "status": "ready",
                "owner": None,
                "owner_since": None,
                "checkpoint": (f"results/pros_segs/cells_{axis}_{name}"
                               f".jsonl (row-level done-key resume, t22 "
                               "law) + done marker json (gitignored "
                               "lane, prereg s6)"),
                "note": (f"22 members x {hi - lo} starts = {n_cells} "
                         "cells" + ("; 22 probe cells already "
                                    "checkpointed (r313 real-fire, "
                                    "resume-skipped)" if name == "LA"
                                    else "")),
            }],
        }
        entries.append(entry)
        added.append(eid)
    # r301/r305 contract asserts before write
    for e in entries:
        if e.get("id", "").startswith("PROSPECT-REGIME-SEGMENTS"):
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
