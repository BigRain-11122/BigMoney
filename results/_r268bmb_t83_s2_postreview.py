"""r268 bm-b: register post_review row T-83-S2-DETECTION (O-2115 / r246 law --
any delivery annotated post_review must land its registry row the SAME round,
checks pre-frozen against stable artifact files only, per r256 reanchor law).

Byte-face mirror probe (R254/R255/R257 five-face law, probed this round from
HEAD blob): no BOM, LF-only, no trailing newline, ensure_ascii=False,
indent=1, insertion key order preserved (items first, _law second).
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "results", "post_review_criteria.json")

ROW = {
    "id": "T-83-S2-DETECTION",
    "claim": "T-83 s2 conflict/duplication/dead-face detection delivered (O-20260926-1355 CEO governance audit slice 2, detection-only zero canon edits): deterministic detector scripts/governance_audit_s2.py (selftest 9/9, rerun byte-identical) -> snapshot results/governance_s2_20260926.json (as_of 2026-09-26; D1 161 carriers/1 prereg zero-face, D2 971 refs -> 5 template+17 inbox-moved+19 relocated+24 true-missing, D9 1 explicit supersession edge O-20260924-1136->O-20260923-1738 + 6 mechanism-amendment candidates, D10 zero stale round-report hits + BACKTEST_PLAN.md cites partially-superseded O-1738) -> findings report research/AUDIT-20260926-S2.md; all findings = candidates for GM s3 adjudication, s3 seven GM deliverables untouched per ticket lane note",
    "claim_source": "fleet/tasks/T-2026-09-26-83-P1.json spec s2 (frozen at b25f78fa pre-claim) + research/AUDIT-20260926-FULL.md s2 input table (ten observations, r267)",
    "status": "claimed",
    "checks": [
        {"kind": "file_exists", "args": ["research/AUDIT-20260926-S2.md"]},
        {"kind": "file_contains",
         "args": ["research/AUDIT-20260926-S2.md",
                  "## 真死链 24（D2·按引用源聚簇·全候选禁自动修）"]},
        {"kind": "file_contains",
         "args": ["research/AUDIT-20260926-S2.md",
                  "—— s2 完 · bm-b r268"]},
        {"kind": "file_exists", "args": ["results/governance_s2_20260926.json"]},
        {"kind": "json_field",
         "args": ["results/governance_s2_20260926.json", "as_of", "2026-09-26"]},
        {"kind": "json_field",
         "args": ["results/governance_s2_20260926.json",
                  "summary_counts.D2_true_missing", "24"]},
        {"kind": "json_field",
         "args": ["results/governance_s2_20260926.json",
                  "summary_counts.D9_edges", "1"]},
        {"kind": "json_field",
         "args": ["results/governance_s2_20260926.json",
                  "summary_counts.D8_parked", "15"]},
        {"kind": "file_contains",
         "args": ["scripts/governance_audit_s2.py",
                  "Governance audit s2 -- conflict/duplication/dead-face detector"]},
    ],
}


def main():
    with io.open(PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    ids = [r["id"] for r in d["items"]]
    assert "T-83-S2-DETECTION" not in ids, "row already registered"
    d["items"].append(ROW)
    # byte-face mirror: no BOM, LF, ensure_ascii=False, indent=1, no trailing \n
    with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    print("registered T-83-S2-DETECTION; items=%d" % len(d["items"]))


if __name__ == "__main__":
    main()
