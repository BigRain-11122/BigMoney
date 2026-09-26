"""R302 bm-a: register post_review criteria for CN_SECTOR_LEADER_P1 (T-87
queue #4 judged closure). Anchors = stable product artifacts only (r291 /
D-20260927-04 no-hot-file law): single-commit product JSON json_field pairs +
one-time-finalized prereg s7/s8 phrases + append-only attrition ledger row.
Values dry-run verified exactly as reviewer sees them (utf-8 load, str()
compare) BEFORE any write; float anchors frozen from the same json.load the
evaluator uses so round-trip is exact.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = os.path.join(ROOT, "results", "post_review_criteria.json")
sys.path.insert(0, os.path.join(ROOT, "Tools"))
from post_review import _check  # noqa: E402

P = "results/cn_sector_leader/p1_results.json"
prod = json.load(open(os.path.join(ROOT, P), encoding="utf-8"))


def _v(dotted):
    d = prod
    for k in dotted.split("."):
        d = d[k]
    return d


F = lambda dotted: str(_v(dotted))  # freeze exact str() as evaluator sees

checks = [
    {"kind": "file_exists", "args": ["scripts/cn_sector_leader_p1.py"]},
    {"kind": "file_exists", "args": [P]},
    {"kind": "file_exists", "args": ["results/cn_sector_leader/cells_summary.csv"]},
    {"kind": "file_exists", "args": ["research/CN_SECTOR_LEADER_PREREG.md"]},
    {"kind": "json_field", "args": [P, "evidence_cutoff", "2026-09-22"]},
    {"kind": "json_field", "args": [P, "batch", "CN_SECTOR_LEADER_P1"]},
    {"kind": "json_field", "args": [P, "trials_ledger.total", "204445"]},
    {"kind": "json_field", "args": [P, "trials_ledger.batch_trials", "2004"]},
    {"kind": "json_field", "args": [P, "panel.universe_n", "3106"]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX10.g1_prime_v2.sharpe_full",
              F("gates.LDR-FIX10.g1_prime_v2.sharpe_full")]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX20.g1_prime_v2.sharpe_full",
              F("gates.LDR-FIX20.g1_prime_v2.sharpe_full")]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-SECT10.g1_prime_v2.sharpe_full",
              F("gates.LDR-SECT10.g1_prime_v2.sharpe_full")]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-STOP10.g1_prime_v2.sharpe_full",
              F("gates.LDR-STOP10.g1_prime_v2.sharpe_full")]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX10.g1_prime_v2.pass_v2", "False"]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX20.g2.eligible_v2", "False"]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX20.dsr.dsr", F("gates.LDR-FIX20.dsr.dsr")]},
    {"kind": "json_field",
     "args": [P, "gates.LDR-FIX10.g1_prime_v2.skill_line.line",
              F("gates.LDR-FIX10.g1_prime_v2.skill_line.line")]},
    {"kind": "json_field", "args": [P, "family_pbo.pbo", "0.0"]},
    {"kind": "json_field", "args": [P, "virtual_starts.n_starts", "8466"]},
    {"kind": "json_field",
     "args": [P, "d6.cells.LDR-STOP10.max_abs_corr",
              F("d6.cells.LDR-STOP10.max_abs_corr")]},
    {"kind": "file_contains",
     "args": ["research/CN_SECTOR_LEADER_PREREG.md", "4/4 cells 判负照报"]},
    {"kind": "file_contains",
     "args": ["research/CN_SECTOR_LEADER_PREREG.md", "判负关槽"]},
    {"kind": "file_contains",
     "args": ["results/gate_attrition.json", "CN_SECTOR_LEADER_P1"]},
]

# dry-run gate: every check green exactly as the reviewer will see it
bad = [(c["kind"], c["args"], d) for c in checks
       for ok_, d in [_check(c["kind"], c["args"])] if not ok_]
assert not bad, f"dry-run red: {bad}"

item = {
    "id": "T-87-CN-SECTOR-LEADER-P1",
    "claim": ("T-87 s2 queue #4 CN_SECTOR_LEADER_P1 (sector-leader "
              "non-limit face per SCHOOL_SUPPLY_S1 sec.4 queue ledger, "
              "post-WILD-S1 new-face candidate) full arc: prereg frozen "
              "commit b3d72924 BEFORE runner build BEFORE any run (R99 "
              "law; probe facts results/cn_sector_leader_probe.json "
              "frozen same commit: universe 3106, SW2021 L2 boards 131, "
              "census 17,823 trigger events, limit-face excluded 2,562) "
              "+ runner selftest 15/15 hermetic + real-data gate PASS "
              "census zero-drift -> pool entry (shards contract defect "
              "fixed R301) -> autofill claim 07:20:16 latency 18.8min "
              "honest (starvation window reported R301) -> burn pid "
              "64840 elapsed ~503s -> 4/4 judged cells NEGATIVE per "
              "frozen s4 on x2 faces: Sharpe LDR-FIX10 -0.5378 / "
              "LDR-FIX20 +0.2288 / LDR-SECT10 -1.3880 / LDR-STOP10 "
              "-1.0618 vs own-null skill lines 2.041 (H10, mu 0.8413) / "
              "3.5375 (H20, mu 2.0495) ALL line_ok=False with bootstrap "
              "CI lower <= 0 all; DSR <= 0.0007; family PBO 0.0 but G1 "
              "fail -> G2 eligible_v2=False 4/4; batch cells_ok 4/4 "
              "False (ann -0.71..-0.83 < 0 and maxDD -1.0 < -35% "
              "double-fail honest; OOS 2025+ oos_sharpe 1.45-4.01 "
              "positive disclosed, single-window sign does not rescue "
              "the batch AND rule); entries 17,771/cell trade gate "
              "pass; D6 max|corr| vs ew6 canon <= 0.0375 zero reject, "
              "within-batch pairwise 0.508-0.873 as predicted; census "
              "8,466 virtual starts beat_rate_6m 0.20-0.39 all < 0.5, "
              "four segments sufficient; robust sign-flip p 0.002/0.171/"
              "0.0/0.0; ledger 204,445 = 202,441 + 2,004 single-count "
              "PASS; s7/s8 single-finalization with 6-prediction "
              "reconciliation (p2 SECT10 whipsaw MISS honest, p5/p6 "
              "full hit) -> sector-leader monopoly-premium face "
              "judged-negative slot closed, SCHOOL row-3 leader-lore "
              "stream fully judged-closed with WILD-S1, reopen = "
              "new-evidence new-prereg only"),
    "claim_source": ("research/CN_SECTOR_LEADER_PREREG.md (frozen "
                     "b3d72924, s7/s8 backfilled R302 "
                     "single-finalization) + results/cn_sector_leader/"
                     "p1_results.json product + results/"
                     "gate_attrition.json entries row ts 2026-09-27 "
                     "07:28:39 + pool done-flip R302 with result_ref"),
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
old_n = len(ids)
new = json.load(open(tmp, encoding="utf-8"))
assert len(new["items"]) == old_n + 1
assert [it["id"] for it in new["items"]][:old_n] == ids
assert new["items"][-1]["id"] == item["id"]
os.replace(tmp, CRITERIA)
print(f"registered {item['id']}: items {old_n} -> {old_n + 1}, "
      f"checks={len(checks)} (dry-run all green)")
