# -*- coding: utf-8 -*-
"""R290 bm-a: register T-86 s3 (CENSUS_FUS_S2_W1-UNC) post-review row per
O-2115/R246 law -- claim + claim_source (pre-frozen faces only) + machine
checks anchored to stable artifacts (R264 law)."""
import io
import json

P = "results/post_review_criteria.json"
d = json.load(io.open(P, encoding="utf-8"))
items = d["items"]

if any(it.get("id") == "T-86-S3-CENSUS-FUS-UNC" for it in items):
    print("row already present; no-op")
    raise SystemExit(0)

items.append({
    "id": "T-86-S3-CENSUS-FUS-UNC",
    "claim": "T-86 s3 uncertainty face full arc: prereg sec.3 s3 rules frozen "
             "at e51e55e0 + sec.9.1 seed freeze census_fusion_s2_unc=20275000 "
             "committed BEFORE unc runner build (R99 chain) -> runner extended "
             "scripts/census_fusion_s2.py unc subcommand (selftest 22 legs ALL "
             "PASS incl. determinism/ordinal-sensitivity/bootstrap/permutation/"
             "native-type/return-series-parity/worker-glue legs) -> full run "
             "landed 2026-09-27 03:3x in-round 62.6s (below O-2100 5-min pool "
             "threshold; pre-declared pool second entry discharged by "
             "completion, honestly disclosed) -> 4,060 candidate combos "
             "derivation face ledger +0 (B=200 block-20td circular bootstrap "
             "x2 Sharpe CI + P=200 sign-flip two-sided IC permutation p, per-"
             "combo rng [20275000, i]) -> cross-anchor vs w1_cells.csv "
             "4,060 checked 0 mismatches -> honest readings: ci_pos 1/4060 "
             "(T:amt_20|price_position|lowamp20 CI [0.0317, 1.4564]), top x2 "
             "combo CI [-0.05, 1.4686] = NOT ci_pos, ic_p<=0.05 2203/4060 "
             "(54.3%, IC face far more permissive than blend face), both=1; "
             "zero registration effect, per-row annotations serialized for "
             "T-23 intake funnel",
    "claim_source": "research/CENSUS_FUSION_S2_PREREG.md sec.3 s3 (frozen at "
                    "e51e55e0) + sec.9.1 seed freeze (R290 commit precedes "
                    "build) + sec.9.2 one-time finalization + "
                    "results/census_fusion_s2/w1_unc.json product + "
                    "results/census_fusion_s2/unc_checkpoint.jsonl (4,060 "
                    "rows, 200-combo cadence)",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["research/CENSUS_FUSION_S2_PREREG.md"]},
        {"kind": "file_contains",
         "args": ["research/CENSUS_FUSION_S2_PREREG.md", "§9.2 s3 不确定面（UNC）跑后定稿"]},
        {"kind": "file_exists", "args": ["scripts/census_fusion_s2.py"]},
        {"kind": "file_exists",
         "args": ["results/census_fusion_s2/w1_unc.json"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "batch",
                  "CENSUS_FUS_S2_W1-UNC"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "evidence_cutoff",
                  "2026-09-24"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "n_combos", "4060"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "unc.B", "200"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "unc.block_days",
                  "20"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "unc.P", "200"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json", "unc.seed_base",
                  "20275000"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "cross_anchor.mismatches", "0"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "cross_anchor.checked", "4060"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "audit.ledger_trials_added", "0"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "trials_ledger.added", "0"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "uncert_summary.n_ci_pos", "1"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "uncert_summary.n_ic_p_le_0.05", "2203"]},
        {"kind": "json_field",
         "args": ["results/census_fusion_s2/w1_unc.json",
                  "uncert_summary.n_ci_pos_and_p", "1"]},
    ],
})

with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("row T-86-S3-CENSUS-FUS-UNC appended; items =", len(items))
