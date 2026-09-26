# -*- coding: utf-8 -*-
"""R263 bm-a: CN-CORE-DDCTL-P1 harvest gate + pool flip (deterministic, zero network).

Landed marker per pool entry shard.checkpoint:
  results/cn_core_ddctl/p1_results.json with trials_ledger block (R252 canonical key).
Gate (fail-closed exit 2 on any miss):
  1. product parses, evidence_cutoff == 2026-09-22 (D2 lockbox);
  2. trials_ledger arithmetic: prev_total(187741) + batch_trials(104) == total(187845);
  3. canonical scanner (science_gates.ledger_head) re-derives max-total head == 187845
     (append is visible to the consumer face, not just present in the file);
  4. four cells exactly {CORE_DD10, CORE_DD20, SAT40_DD10, SAT40_DD20} x2 face;
  5. dead-condition differentiation guard (R263 crash-2 lesson encoded): CORE cells
     g1 sharpe differ from their SAT40 twins (bug made CORE faces run as SAT40);
  6. g1/g2 verdict face present (all-False honest negative is a legitimate landed
     outcome -- harvest carries the science evidence, pass/fail is the judgment).
Flip: entry.status/shard.status ready->done + harvest_note (R244 shape).
Write-back mirrors producer exactly: text-mode json.dump(ensure_ascii=False,
indent=1) => CRLF, no trailing newline, raw UTF-8 (byte probe _r263bma_pool_byteprobe).
"""
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import science_gates as sg  # noqa: E402

PROD = os.path.join(ROOT, "results", "cn_core_ddctl", "p1_results.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EXPECT_CELLS = {"CORE_DD10", "CORE_DD20", "SAT40_DD10", "SAT40_DD20"}


def main() -> int:
    fails = []
    if not os.path.exists(PROD):
        print("FAIL: product absent")
        return 2
    d = json.load(io.open(PROD, encoding="utf-8"))

    if d.get("evidence_cutoff") != "2026-09-22":
        fails.append(f"evidence_cutoff {d.get('evidence_cutoff')!r} != 2026-09-22")

    tl = d.get("trials_ledger")
    if not isinstance(tl, dict):
        fails.append("trials_ledger block missing (R252 canonical key)")
    else:
        if tl.get("prev_total") + tl.get("batch_trials", 0) != tl.get("total"):
            fails.append(f"ledger arithmetic {tl.get('prev_total')}+{tl.get('batch_trials')} != {tl.get('total')}")
        if tl.get("batch_trials") != 104:
            fails.append(f"batch_trials {tl.get('batch_trials')} != 104 (4 judged + 100 nulls)")

    head = sg.ledger_head()
    if head.get("total") != 187845:
        fails.append(f"canonical scanner head {head.get('total')} != 187845 (append not visible to consumer face)")

    g1 = d.get("g1_prime_v2", {})
    cells = set(g1.keys())
    if cells != EXPECT_CELLS:
        fails.append(f"cells {sorted(cells)} != expected 2x2 grid")
    else:
        for a, b in (("CORE_DD10", "SAT40_DD10"), ("CORE_DD20", "SAT40_DD20")):
            if abs(g1[a].get("sharpe_full", -99) - g1[b].get("sharpe_full", -99)) < 1e-12:
                fails.append(f"dead-condition face: {a} == {b} sharpe (R263 crash-2 lesson)")
    g2 = d.get("g2_registration_v2", {})
    if not isinstance(g2, dict) or not g2:
        fails.append("g2_registration_v2 verdict face missing")

    verdict = {
        "harvest_gate": "PASS" if not fails else "FAIL",
        "ledger_head_total": head.get("total"),
        "cells": {k: g1[k].get("sharpe_full") for k in sorted(cells)},
        "g2_all_false_honest_negative": all(not v for v in g2.values()) if g2 else None,
        "fails": fails,
    }
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    if fails:
        return 2

    pool = json.load(io.open(POOL, encoding="utf-8"))
    entry = next((e for e in pool.get("entries", []) if e.get("id") == "CN-CORE-DDCTL-P1"), None)
    if entry is None or entry.get("status") != "ready":
        print(f"FAIL: entry missing or not pre-flip ready (status={entry and entry.get('status')})")
        return 2
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    entry["status"] = "done"
    entry["updated_at"] = now
    for sh in entry.get("shards", []):
        if sh.get("key") == "coreddctl-0of1":
            sh["status"] = "done"
    entry["harvest_note"] = (
        "harvested bm-a R263 2026-09-26 18:5x: p1_results.json landed 18:43:56 "
        "(trials_ledger prev 187741 + 104 = 187845, canonical head re-derived 187845; "
        "evidence_cutoff 2026-09-22 D2; 2x2 cells differentiated CORE_DD10 0.1048 / "
        "CORE_DD20 0.3086 / SAT40_DD10 0.3796 / SAT40_DD20 0.4477; g1/g2 all-False "
        "honest negative); launch arc = 5 launches, first 4 died pre-finalize "
        "zero-ledger-pollution (naming bug x2, dead-condition bug, h4 prev-audit "
        "n-1 crash), 5th (pid 37364, runner c4161eec) landed 22.3s; harvest gate = "
        "results/_r263bma_coreddctl_harvest.py exit 0 (self-verifiable)"
    )
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, POOL)
    print("pool flipped: CN-CORE-DDCTL-P1 entry+shard done, harvest_note landed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
