# -*- coding: utf-8 -*-
"""R290 bm-a: register T-86 s2 (CENSUS-FUS-S2-W1) post-review row per
O-2115/R246 law -- claim + claim_source (pre-frozen faces only) + machine
checks anchored to stable artifacts (R264 law: commit-stable product files
or json_field faces, zero post-hoc criteria)."""
import io
import json

P = "results/post_review_criteria.json"
d = json.load(io.open(P, encoding="utf-8"))
items = d["items"]

if any(it.get("id") == "T-86-S2-CENSUS-FUS-W1" for it in items):
    print("row already present; no-op")
    raise SystemExit(0)

items.append({
    "id": "T-86-S2-CENSUS-FUS-W1",
    "claim": "T-86 s2 factor-level fusion census wave-1 full arc: prereg "
             "research/CENSUS_FUSION_S2_PREREG.md FROZEN e51e55e0 precedes "
             "runner build 8a00f514 precedes ANY run (R99) -> runner "
             "scripts/census_fusion_s2.py (selftest 14/14, hermetic) -> pool "
             "CENSUS-FUS-S2-W1 burn landed 2026-09-27 03:00:11 via autofill "
             "launch-claim 1150732c (checkpoint resume, N=4518 = 4060 cand + "
             "58 rs ctrl + 400 nulls seed band 20274500..20274899, ledger "
             "200900+4518=205418, evidence_cutoff 2026-09-24, data gate 48/48 "
             "ok) -> deterministic harvest R290 (r244 law): pool entry+shard "
             "flipped done + prereg s7/s8 single-finalization + attrition row "
             "52 (kind=measurement, judgment lines null per exploration-face "
             "annotation law) -> EXPLORATION FACE verdict-free closure: zero "
             "judged cells, zero registration effect, sole output = sec.4 "
             "family aggregation feeding T-23 intake funnel; s5 reconciliation "
             "P1 CONFIRMED (74/306=24.2% top-decile = 2.4x enrichment, all 74 "
             "beat EW48 ann), P2 CONFIRMED (cand p95 0.4164 > null p95 0.3526, "
             "363/4060=8.9% above null p95 vs 5% base), P3 NOT-CONFIRMED "
             "(rev-x-mom 208 pairs IC median +0.0103, neg frac 30%), P4 "
             "disclosure face satisfied",
    "claim_source": "research/CENSUS_FUSION_S2_PREREG.md (frozen R286/R287 "
                    "pre-run; R99 law: post-run s7/s8 backfill only) + commit "
                    "46a156ba runner contract (frozen) + "
                    "results/_r290bma_censusfus_harvest.py (deterministic "
                    "harvest gate, exit 0) + w1_results.json audit segment + "
                    "w1_summary.json/w1_nulls.json/w1_cells.csv products",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["research/CENSUS_FUSION_S2_PREREG.md"]},
        {"kind": "file_contains",
         "args": ["research/CENSUS_FUSION_S2_PREREG.md", "R290 bm-a 一次定稿"]},
        {"kind": "file_exists", "args": ["scripts/census_fusion_s2.py"]},
        {"kind": "file_exists",
         "args": ["results/census_fusion_s2/w1_results.json"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json",
                  "evidence_cutoff", "2026-09-24"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json", "face",
                  "EXPLORATION (zero judgment claims / zero paper eligibility)"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json",
                  "audit.ledger_trials_added", "4518"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json",
                  "trials_ledger.total", "205418"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json",
                  "trials_ledger.prev_total", "200900"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_results.json",
                  "data_gate.ok", "True"]},
        {"kind": "file_exists",
         "args": ["results/census_fusion_s2/w1_summary.json"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_summary.json", "batch",
                  "CENSUS_FUS_S2_W1"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_nulls.json", "n", "400"]},
        {"kind": "file_exists",
         "args": ["results/_r290bma_censusfus_harvest.py"]},
        {"kind": "file_contains",
         "args": ["results/runnable_pool.json",
                  "R290 bm-a deterministic harvest"]},
        {"kind": "file_contains",
         "args": ["results/gate_attrition.json", "CENSUS_FUS_S2_W1"]},
    ],
})

with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("row T-86-S2-CENSUS-FUS-W1 appended; items =", len(items))
