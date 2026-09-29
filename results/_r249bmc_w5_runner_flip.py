# -*- coding: utf-8 -*-
"""_r249bmc_w5_runner_flip.py -- surgical SLOT-5 runner_exists gate
flip + runnable_pool enqueue for INNOVATION-QUOTA-SLOT-5 (r246
row-level surgery law: load -> surgical edit -> dump, no reorder;
atomic tmp+os.replace; round-trip re-verify).

Idempotent: refuses if SLOT-5 pool id already present (rc=2) or
catalog runner already flipped (rc=3, idempotent no-op face)."""
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "Tools", "fill_ladder_catalog.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
NOW = time.strftime("%Y-%m-%d %H:%M:%S")

RUNNER_BUILT = (
    "scripts/innovation_quota_w5.py (BUILT r249 bm-c, selftest 31/31: "
    "scipy siegelslopes hierarchical rolling RM endpoint engine + "
    "tie-maintain entangled state machine ffill(side!=0) + G-ANCHOR "
    "fail-closed vs r247 probe facts (verified live on real panel "
    "pre-enqueue, all faces bit-exact) + r450 landed-state guard rc=2 "
    "+ GBK reconfigure entry law; both enqueue gates now pass -> "
    "pool-enqueued same window)")
PREREG_FROZEN = (
    "research/INNOVATION_QUOTA_W5_PREREG.md FROZEN (r248 bm-c; seed "
    "innovation_quota_w5_icu_ma=20322500 registered + full-registry "
    "three-step reverify ALL GREEN via import view 134 keys / "
    "r244 pit law; sec.5 predictions locked verbatim at freeze)")


def main() -> int:
    # ---- catalog flip (runner_exists gate face)
    with open(CATALOG, encoding="utf-8") as fh:
        cat = json.load(fh)
    slot = None
    for e in cat["entries"]:
        if e.get("id") == "INNOVATION-QUOTA-SLOT-5":
            slot = e
            break
    if slot is None:
        print("catalog SLOT-5 entry absent")
        return 1
    already = str(slot.get("runner", "")).startswith("scripts/")
    if already and any(
            t.get("id") == "INNOVATION-QUOTA-SLOT-5"
            for t in json.load(open(POOL, encoding="utf-8"))
            .get("entries", [])):
        print("SLOT-5 already flipped + enqueued -- idempotent no-op "
              "(rc=3)")
        return 3
    slot["runner"] = RUNNER_BUILT
    slot["prereg_ref"] = PREREG_FROZEN
    cat["version"] = (cat.get("version") or "") + (
        " + SLOT-5 runner_exists flip (bm-c r249: "
        "scripts/innovation_quota_w5.py built selftest 31/31, "
        "G-ANCHOR real-panel pre-verified, both gates pass)")
    with open(CATALOG + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=1)
    os.replace(CATALOG + ".tmp", CATALOG)
    with open(CATALOG, encoding="utf-8") as fh:
        cat2 = json.load(fh)
    slot2 = [e for e in cat2["entries"]
             if e.get("id") == "INNOVATION-QUOTA-SLOT-5"][0]
    assert slot2["runner"] == RUNNER_BUILT
    assert len(cat2["entries"]) == len(cat["entries"])
    print("catalog SLOT-5 flipped: runner_exists gate TRUE")

    # ---- pool enqueue (execution-face separation: burn = autofill)
    with open(POOL, encoding="utf-8") as fh:
        pool = json.load(fh)
    if any(t.get("id") == "INNOVATION-QUOTA-SLOT-5"
           for t in pool.get("entries", [])):
        print("SLOT-5 pool id already present -- refuse (rc=2)")
        return 2
    entry = {
        "id": "INNOVATION-QUOTA-SLOT-5",
        "ticket_ref": "T-2026-09-28-107 sec.4(d) innovation quota "
                      "slot-5 (catalog tranche-5; prereg FROZEN r248 "
                      "bm-c + full-registry seed three-step reverify "
                      "ALL GREEN via import view; runner built r249 "
                      "bm-c selftest 31/31 + G-ANCHOR real-panel "
                      "pre-verification bit-exact)",
        "prereg_ref": "research/INNOVATION_QUOTA_W5_PREREG.md FROZEN "
                      "(ICU-MA-TIMING-P1 judged batch, 3 frozen cells "
                      "ICU-N5 / ICU-N120 / ICU-N15 all-three-channels "
                      "snooping-discount carrier; scipy siegelslopes "
                      "hierarchical rolling RM endpoint trend face "
                      "r222 clean-room; tie-maintain entangled state "
                      "machine; NO stop line; nulls K2000 uniform day "
                      "placement + starts K1000 + splits 100, seed "
                      "20322500; evidence_cutoff 2026-09-22 P-5C "
                      "binding; batch_cells 2003 s0 counting law)",
        "consumer_plan": "ICU_MA_TIMING_P1 judged verdict "
                         "(results/innovation_quota/"
                         "ICU-MA-TIMING-P1.json) -> G2 pass = T-34 "
                         "fastline candidate pool eligibility; fail = "
                         "judged-negative family closure + attrition "
                         "row + 48h CEO report (per prereg s0)",
        "runner": "scripts/innovation_quota_w5.py",
        "runner_args": ["run"],
        "lane_owner": None,
        "priority": 3,
        "status": "ready",
        "entered_at": NOW,
        "entered_by": "bm-c fill_ladder T-107 slot-5 r249",
        "data_gates": "runner fail-closed if panel/anchor faces drift "
                      "(G-PANEL rows 3483 / first 2012-05-28 / last "
                      "2026-09-22; G-ANCHOR N5 3479/4/1171/1224/1084/"
                      "0.336591 + N120 3364/119/1733/1631/0/0.515161 + "
                      "N15 3469/14/1570/1612/287/0.45258 + extreme-day "
                      "per-state records incl. rounded ICU/close values "
                      "+ intra-family containment a_in_b 0.5098/0.5884/"
                      "0.5484; exit 2 honest face-mismatch = config "
                      "VOID not data corruption); r450 landed-state "
                      "guard: judged product (trials_ledger read from "
                      "content) refuses re-run rc=2, "
                      "INNOVATION_QUOTA_W5_REFINALIZE=1 = only redo",
        "note": "ladder (d) slot-5 burn face: judged-negative = family "
                "closure + attrition row + 48h CEO report (s5.2 "
                "prediction = judged-negative main channel, W1-W4 "
                "quota lineage 0-registered); G2 pass = T-34 fastline "
                "candidate pool eligibility; N5 tie-maintain 31.1% "
                "structural face + N15 dual-window negative descriptive "
                "carried per prereg s2 honest disclosures",
        "shards": [{"key": "main", "status": "ready",
                    "checkpoint": "",
                    "note": "single-face judged batch (3 cells + 6000 "
                            "null draws), default shard",
                    "owner": None}],
        "workers_plan": {"workers": "worker_cap() pool BelowNormal",
                         "priority": "BelowNormal",
                         "note": "3-cell judged burn + 6000 null draws "
                                 "(uniform day placement, cheap numpy "
                                 "per draw); minute-scale single-"
                                 "machine; ICU rolling siegelslopes "
                                 "faces computed once (N120 heaviest, "
                                 "~2s measured)"},
    }
    pool.setdefault("entries", []).append(entry)
    pool["updated_at"] = NOW
    with open(POOL + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(pool, fh, indent=1)
    os.replace(POOL + ".tmp", POOL)
    with open(POOL, encoding="utf-8") as fh:
        pool2 = json.load(fh)
    got = [t for t in pool2["entries"]
           if t.get("id") == "INNOVATION-QUOTA-SLOT-5"][0]
    assert got["status"] == "ready" and got["runner"] == \
        "scripts/innovation_quota_w5.py"
    assert len(pool2["entries"]) == len(pool["entries"])
    print("pool enqueued: INNOVATION-QUOTA-SLOT-5 ready (entries=%d)"
          % len(pool2["entries"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
