# -*- coding: utf-8 -*-
"""r1028 bm-c: W20 absorb closeout pool surgery.
(1) Flip TRIAL-LABOR-W20-GENERATE ready->done (dead-window estate
    machine-verified this window: selftest 20/20 + status gates PASS +
    candidates 31 cells 13/6/12 + grammar sha ff00b0896b088b5a == frozen).
(2) Enroll 4 SCREEN shard entries (W19 8-shard precedent scaled:
    231 cells / 4 = ~58 per shard), lane-pinned bm-c per r429
    machine-local checkpoint law (screen-finalize reads local CKPT_DIR).
Dual-file write (shared runnable_pool.json + lane runnable_pool.bm-c.json),
same indent=1 face as fill_ladder _write_pool_double.
"""
import json
import os
import sys
import datetime

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "results", "runnable_pool.json")
LANE = os.path.join(ROOT, "results", "runnable_pool.bm-c.json")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
MID = "bm-c"

GEN_ID = "TRIAL-LABOR-W20-GENERATE"
RESULT_REF = "results/trial_labor_w20/w20_candidates.json"
ABS_NOTE = (" | r1028 bm-c absorb-window flip: dead-window (14:10-14:20) "
            "generate estate machine-verified BEFORE landing this window "
            "(selftest 20/20 PASS + status gates A9/G-ROSTER/G-SEEDS PASS "
            "+ candidates n_cells=31 fams 13/6/12 + grammar sha "
            "ff00b0896b088b5a == frozen + prep_state G-battery 8/8 PASS "
            "with 1253 starts passive_6m complete); same-grammar rerun "
            "refusal = by-design idempotence face, entry flipped done to "
            "free autofill from a refused re-burn cycle")

SHARD_NOTE = ("stride i%%4 of 231 cells (31 cand + 200 screen nulls); "
              "lane pinned bm-c per r429 machine-local checkpoint law "
              "(screen-finalize reads local CKPT_DIR); RAM gate 4GB "
              "r354 honest-refuse retry (AUTOFILL-PARK; live free RAM "
              "1.2GB at enrollment = park-until-freed honest, autofill "
              "retries; night-window RAM frees per fleet pattern)")


def entry_screen_shard(k, n=4):
    return {
        "id": f"TRIAL-LABOR-W20-SCREEN-SHARD-{k}",
        "ticket_ref": ("T-2026-10-15-187-P1 wave ticket (W20 frozen "
                       "prereg; W19 T-2026-10-14-186 lineage)"),
        "prereg_ref": ("research/TRIAL_LABOR_W20_PREREG.md (FROZEN "
                        "2026-10-15 bm-c r1027 freeze commit 06f323b92)"),
        "runner": "scripts/trial_labor_w20.py",
        "runner_args": ["screen", str(k), str(n)],
        "lane_owner": "bm-c",
        "priority": 1,
        "consumer_plan": (
            "screen shards -> screen-finalize (bm-c local; needs all 31 "
            "cand rows + 200 nulls in CKPT_DIR) -> w20_screen.json + "
            "survivors + family axe -> judge-prep/judge/judge-finalize "
            "(family blocks, dual-nulls B=2000/P=2000) -> intake -> "
            "48h CEO clock + scorecard; negative = entry-GENERATE "
            "supply-line demotion canonical basis (three-axis-pure "
            "single-variable reading per frozen sec.0 banner)"),
        "workers_plan": {
            "workers": "worker_cap() pool BelowNormal",
            "priority": "BelowNormal",
            "note": ("W17/W18/W19 screen machinery precedent "
                     "(run_cells_parallel multiproc; prep_state "
                     "passive_6m shared read)"),
        },
        "data_gates": (
            "in-runner fail-closed: prep+candidates presence + grammar "
            "sha == frozen ff00b0896b088b5a + RAM gate 4GB + checkpoint "
            "resume (screen_shard_kof4.jsonl append-per-cell); "
            "evidence_cutoff=2026-09-22 (P-5C binding)"),
        "status": "ready",
        "shards": [{
            "key": f"w20-screen-{k}of{n}",
            "status": "ready",
            "checkpoint": ("results/trial_labor_w20/checkpoint/"
                           f"screen_shard_{k}of{n}.jsonl (MACHINE-LOCAL "
                           "r429 gitignored; lane pinned bm-c)"),
            "note": SHARD_NOTE,
            "owner": None,
        }],
        "entered_at": NOW,
        "entered_by": "bm-c r1028 (absorb-window enrollment, W19 "
                      "8-shard precedent scaled 231/4)",
    }


def main():
    changed = {"shared": [], "lane": []}
    for label, path in (("shared", SHARED), ("lane", LANE)):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        ents = d["entries"]
        ids = {e.get("id"): i for i, e in enumerate(ents)}
        # (1) flip GENERATE -> done
        if GEN_ID in ids:
            e = ents[ids[GEN_ID]]
            e["status"] = "done"
            e["result_ref"] = RESULT_REF
            e["note"] = (e.get("note", "") + ABS_NOTE).strip()
            sh = e["shards"][0]
            sh["status"] = "done"
            sh["owner"] = MID
            sh["owner_since"] = NOW
            sh["done_at"] = NOW
            sh["harvested_by"] = MID
            sh["result_ref"] = RESULT_REF
            changed[label].append(f"flip:{GEN_ID}->done")
        # (2) enroll 4 screen shards (idempotent: skip if exists)
        for k in range(4):
            sid = f"TRIAL-LABOR-W20-SCREEN-SHARD-{k}"
            if sid in ids:
                continue
            ents.append(entry_screen_shard(k))
            changed[label].append(f"enroll:{sid}")
        if "updated_at" in d:
            d["updated_at"] = NOW
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(json.dumps({"now": NOW, "changed": changed}, ensure_ascii=False))
    # read-back verification
    for label, path in (("shared", SHARED), ("lane", LANE)):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        by = {e.get("id"): e for e in d["entries"]}
        assert by[GEN_ID]["status"] == "done", label
        assert by[GEN_ID]["shards"][0]["status"] == "done", label
        for k in range(4):
            e = by[f"TRIAL-LABOR-W20-SCREEN-SHARD-{k}"]
            assert e["status"] == "ready" and e["shards"][0]["status"] == "ready"
            assert e["lane_owner"] == "bm-c"
            assert e["runner_args"] == ["screen", str(k), "4"]
    print("READBACK-VERIFY PASS (dual-file, generate done + 4 screen shards ready)")


if __name__ == "__main__":
    main()
