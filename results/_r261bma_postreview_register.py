# -*- coding: utf-8 -*-
"""R261 bm-a: post_review registration row for CN-CORE-SATELLITE-P1
(r246 law: any delivery claiming post_review must land its registry row
the SAME round; checks anchor stable product files + pre-frozen faces
only -- zero post-hoc criteria)."""
import collections
import json

P = "results/post_review_criteria.json"
d = json.load(open(P, encoding="utf-8"),
              object_pairs_hook=collections.OrderedDict)
assert not any(r["id"] == "T-73-CN-CORE-SATELLITE-P1"
               for r in d["items"])
row = collections.OrderedDict([
    ("id", "T-73-CN-CORE-SATELLITE-P1"),
    ("claim",
     "T-73 s3 slice-5 (FINAL CN-native model) CN-CORE-SATELLITE full arc "
     "one round: anti-repeat scan (satellite=style-momentum rotation per "
     "slice-E alive law; T-57 wild-route negative disclosed as spec "
     "evolution) -> probe frozen results/core_sat_probe.json (T=3333, "
     "first_active 2013-07-17, zero post-activation cash, event set 3, "
     "510880 zero events) -> prereg research/CN_CORE_SATELLITE_PREREG.md "
     "FREEZE commit cd708338 BEFORE any run (seed cn_core_sat_p1=20261080 "
     "registered same commit, band scan clean) -> runner "
     "scripts/cn_core_sat_p1.py commit d6c7975c selftest 12/12 (family "
     "machinery reuse: DRV engine injected + SRP slice-E guards + "
     "science_gates shared criteria) -> pool entry 8fd4427c 17:48:11 -> "
     "autofill launch 17:50:04 -> landed 21.8s 64 units -> verdict "
     "NEGATIVE: G1'v2 0/4 (best SAT40_bare 0.4586 < line 0.5664, CI95 "
     "low -0.0843 negative; DSR 0.0 x4; PBO 0.5571; G2 ineligible x4) -> "
     "ledger 187687+54=187741 -> ten-face harvest gate "
     "_r261bma_coresat_harvest.py PASS -> pool flipped done -> s7/s8 "
     "backfilled one-pass -> s3 five-model family ALL-NEGATIVE chain "
     "closed (no reopen; new evidence = new prereg)"),
    ("claim_source",
     "research/CN_CORE_SATELLITE_PREREG.md (frozen cd708338; s7/s8 "
     "backfill only sanctioned edit) + results/core_sat_probe.json + "
     "scripts/cn_core_sat_p1.py (frozen header contract) + "
     "results/cn_core_satellite/p1_results.json + "
     "results/_r261bma_coresat_harvest.py + pool entry "
     "results/runnable_pool.json CN-CORE-SATELLITE-P1 harvest_note"),
    ("status", "pending"),
    ("checks", [
        {"kind": "file_exists",
         "args": ["research/CN_CORE_SATELLITE_PREREG.md"]},
        {"kind": "file_exists",
         "args": ["results/core_sat_probe.json"]},
        {"kind": "file_exists",
         "args": ["scripts/cn_core_sat_p1.py"]},
        {"kind": "file_exists",
         "args": ["results/cn_core_satellite/p1_results.json"]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "trials_ledger.total", 187741]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "trials_ledger.prev_total", 187687]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "cells.SAT20_bare.x2.sharpe", 0.4234]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "cells.SAT40_bare.x2.sharpe", 0.4586]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "g1_prime_v2.SAT40_bare.pass_v2", False]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "g2_registration_v2.SAT40_bare.eligible_v2", False]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "skill_line.line", 0.5664]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "nulls.config.base", 20261080]},
        {"kind": "json_field",
         "args": ["results/cn_core_satellite/p1_results.json",
                  "baselines.core_only_buy_hold_510880.sharpe", 0.3605]},
        {"kind": "file_contains",
         "args": ["scripts/science_gates.py", "cn_core_sat_p1"]},
        {"kind": "file_contains",
         "args": ["results/runnable_pool.json",
                  "harvested bm-a R261 same-round 2026-09-26 17:5x"]},
    ]),
])
d["items"].append(row)
tmp = P + ".tmp"
open(tmp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1) + "\n")
import os
os.replace(tmp, P)
print("post_review row registered:", row["id"],
      "checks:", len(row["checks"]))
