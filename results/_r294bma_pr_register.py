"""R294 bm-a: register post_review criteria for CN_KLINE_PATTERN_P1 (R293-closure
NEXT P0). Anchors = stable product artifacts only (r291/D-20260927-04 no-hot-file
law): single-commit product JSON json_field pairs + one-time-finalized prereg
s7/s8 phrases + append-only attrition ledger contains. Values dry-run verified
23/23 exactly as reviewer sees them (utf-8 load, str() compare) BEFORE write."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = os.path.join(ROOT, "results", "post_review_criteria.json")

P = "results/cn_kline_pattern/p1_results.json"
checks = [
    {"kind": "file_exists", "args": ["scripts/cn_kline_pattern_p1.py"]},
    {"kind": "file_exists", "args": [P]},
    {"kind": "file_exists", "args": ["results/cn_kline_pattern/cells_summary.csv"]},
    {"kind": "file_exists", "args": ["research/CN_KLINE_PATTERN_PREREG.md"]},
    {"kind": "json_field", "args": [P, "evidence_cutoff", "2026-09-22"]},
    {"kind": "json_field", "args": [P, "batch", "CN_KLINE_PATTERN_P1"]},
    {"kind": "json_field", "args": [P, "trials_ledger.total", "200396"]},
    {"kind": "json_field", "args": [P, "trials_ledger.batch_trials", "2007"]},
    {"kind": "json_field", "args": [P, "panel.universe_n", "3106"]},
    {"kind": "json_field", "args": [P, "gates.MS-FIX10.g1_prime_v2.sharpe_full", "-0.7145"]},
    {"kind": "json_field", "args": [P, "gates.TWS-BEAR.g1_prime_v2.sharpe_full", "0.4"]},
    {"kind": "json_field", "args": [P, "gates.COMBO.g1_prime_v2.sharpe_full", "0.2768"]},
    {"kind": "json_field", "args": [P, "gates.MS-FIX10.g1_prime_v2.pass_v2", "False"]},
    {"kind": "json_field", "args": [P, "gates.COMBO.g2.eligible_v2", "False"]},
    {"kind": "json_field", "args": [P, "gates.TWS-BEAR.dsr.dsr", "0.015014"]},
    {"kind": "json_field", "args": [P, "family_pbo.pbo", "0.4429"]},
    {"kind": "json_field", "args": [P, "tbc_advisory.n_tbc", "14"]},
    {"kind": "json_field", "args": [P, "tbc_advisory.insufficient_sample", "True"]},
    {"kind": "json_field", "args": [P, "nulls.MS-FIX10.coverage.n_values", "2000"]},
    {"kind": "json_field", "args": [P, "virtual_starts.n_starts", "8466"]},
    {"kind": "file_contains", "args": ["research/CN_KLINE_PATTERN_PREREG.md",
                                       "7/7 cells 判负照报"]},
    {"kind": "file_contains", "args": ["research/CN_KLINE_PATTERN_PREREG.md",
                                       "判负关槽"]},
    {"kind": "file_contains", "args": ["results/gate_attrition.json",
                                       "CN_KLINE_PATTERN_P1"]},
]

item = {
    "id": "T-87-CN-KLINE-PATTERN-P1",
    "claim": ("T-87 s2 queue #3 CN_KLINE_PATTERN_P1 (THS-formula K-line pattern "
              "families per SCHOOL_SUPPLY_S1 sec.4 queue ledger, folklore gate "
              "PASS R289) full arc: prereg frozen commit cbf6c93c BEFORE runner "
              "build BEFORE any run (R99 law; probe facts results/"
              "cn_kline_probe.json frozen same commit: universe 3106, census "
              "MS 1342 / TWS 21518 / DCC 35270 / TBC 14) + runner selftest "
              "23/23 hermetic + real-data gate PASS census zero-drift vs frozen "
              "probe -> pool entry #55 -> autofill claim fill latency 5.4min "
              "(<= 10min O-2100 target) -> burn pid 56364 elapsed 353s -> "
              "7/7 judged cells NEGATIVE per frozen s4: x2 Sharpe MS-FIX "
              "-0.7145 / MS-STOP -0.6385 / TWS-FIX -0.3811 / TWS-STOP -0.4363 "
              "/ MS-BEAR +0.1218 / TWS-BEAR +0.4000 / COMBO +0.2768; own-null "
              "skill lines 1.9486 / 2.6603 / 3.5701-4.0655 ALL line_ok=False "
              "with bootstrap CI lower <= 0; DSR <= 0.015 all; family PBO "
              "0.4429 > 0.25; batch cells_ok 7/7 False (maxDD -97 to -100pct "
              "triple-fail honest); D6 max|corr| 0.1295 vs ew6 canon zero "
              "reject; TBC 14 events insufficient-sample flag honest; ledger "
              "200,396 = 198,389 + 2,007 single-count PASS; s7/s8 "
              "single-finalization with 5-prediction reconciliation (p1 "
              "CONFIRMED claim!=verify, p3 half-hit honest) -> K-line pattern "
              "face judged-negative slot closed, reopen = new-evidence "
              "new-prereg only"),
    "claim_source": ("research/CN_KLINE_PATTERN_PREREG.md (frozen cbf6c93c, "
                     "s7/s8 backfilled R293 single-finalization) + results/"
                     "cn_kline_pattern/p1_results.json product + results/"
                     "gate_attrition.json entries row CN_KLINE_PATTERN_P1 + "
                     "pool done-flip R293 (autofill CN-KLINE finalize trail)"),
    "status": "closed",
    "checks": checks,
}

with open(CRITERIA, encoding="utf-8") as fh:
    d = json.load(fh)
ids = [it["id"] for it in d["items"]]
assert item["id"] not in ids, "duplicate id"
d["items"].append(item)
tmp = CRITERIA + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
# byte-level sanity: reparse both, zero-loss check
old_n = len(ids)
new = json.load(open(tmp, encoding="utf-8"))
assert len(new["items"]) == old_n + 1
assert [it["id"] for it in new["items"]][:old_n] == ids
assert new["items"][-1]["id"] == item["id"]
os.replace(tmp, CRITERIA)
print(f"registered {item['id']}: items {old_n} -> {old_n + 1}, "
      f"checks={len(checks)}")
