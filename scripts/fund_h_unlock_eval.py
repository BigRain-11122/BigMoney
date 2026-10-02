# -*- coding: utf-8 -*-
"""T-145 leg (b): census H-row unlock evaluation (8 DATA_GATE-locked fundamental faces).

Inputs (evidence-only, no raw fund_history needed -- dataset is bm-c machine-local per R31):
  - results/fund_pit_audit/audit_results.json   (bm-c leg (a) PIT audit, 2026-10-02 21:21, structure PASS)
  - results/fund_history_status.json             (T-131 dataset completeness: complete=true 2026-10-02 15:40)

Output: results/fund_h_unlock_eval.json (per-face verdict table + mandatory prereg gate).

Verdict kinds:
  direct      = derivable 1:1 from a collected face (no new data needed)
  proxy       = derivable via a DECLARED proxy (face substitution / derived series); not the canonical
                academic construction -- proxy disclosure is part of the unlock contract
  STAY-LOCKED = required face absent from dataset -> DATA_GAP remains -> next data slice
All UNLOCK faces inherit the MANDATORY statutory-anchoring prereg gate from the PIT audit
(financial_face_rule: period-end anchoring = prereg rejection).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "results", "fund_pit_audit", "audit_results.json")
STATUS = os.path.join(ROOT, "results", "fund_history_status.json")
OUT = os.path.join(ROOT, "results", "fund_h_unlock_eval.json")

# frozen derivability mapping (H-row faces -> T-131 collected faces)
# collected faces: pe_ttm, pe_static, pb, total_mv, roe_q, div_events (audit face keys)
FACE_EVAL = {
    "academic_hml": dict(
        needs="FF5 value B/M", formula="bm = 1.0 / pb", source_faces=["pb"], kind="direct"),
    "fund_earnings_yield": dict(
        needs="E/P", formula="ep = 1.0 / pe_ttm", source_faces=["pe_ttm"], kind="direct"),
    "fund_roe": dict(
        needs="ROE", formula="roe_q (quarterly; anchor at statutory availability date)", source_faces=["roe_q"], kind="direct"),
    "academic_smb": dict(
        needs="size", formula="size = ln(total_mv)", source_faces=["total_mv"], kind="direct"),
    "academic_rmw": dict(
        needs="FF5 operating profitability",
        formula="PROXY: roe_q substitutes op-profitability (A-share adaptation; NOT canonical FF5 RMW)",
        source_faces=["roe_q"], kind="proxy"),
    "academic_cma": dict(
        needs="FF5 investment (asset growth)",
        formula="PROXY: book-equity growth = (total_mv/pb)_t / (total_mv/pb)_{t-12m} - 1",
        source_faces=["total_mv", "pb"], kind="proxy"),
    "fund_asset_growth": dict(
        needs="asset growth",
        formula="PROXY: book-equity growth (equity-growth proxy for asset growth)",
        source_faces=["total_mv", "pb"], kind="proxy"),
    "fund_gross_profitability": dict(
        needs="gross profit / assets (Novy-Marx GP/A)",
        formula="NOT derivable: gross-profit (income-statement) face absent from T-131 dataset",
        source_faces=[], kind="gap"),
}


def main():
    audit = json.load(open(AUDIT, encoding="utf-8"))
    status = json.load(open(STATUS, encoding="utf-8"))
    collected = set(audit.get("faces", {}).keys())
    stat_rule = audit.get("pit", {}).get("financial_face_rule", "")
    rows, n_unlock = [], 0
    for name, ev in FACE_EVAL.items():
        have = [f for f in ev["source_faces"] if f in collected]
        if ev["kind"] == "gap":
            verdict = "STAY-LOCKED"
        elif len(have) == len(ev["source_faces"]):
            verdict = "UNLOCK"
        else:
            verdict = "STAY-LOCKED"  # would mean an audited face went missing -- fail-closed
        rows.append(dict(face=name, needs=ev["needs"], formula=ev["formula"],
                         source_faces=ev["source_faces"], kind=ev["kind"], verdict=verdict))
        if verdict == "UNLOCK":
            n_unlock += 1
    out = dict(
        generated="2026-10-02", ticket_ref="T-2026-10-02-145-P1", leg="b (census H-row unlock evaluation)",
        evidence=dict(
            pit_audit="results/fund_pit_audit/audit_results.json (bm-c 2026-10-02 21:21, structure PASS, machine=bm-c leg per audit_results)",
            dataset_status="results/fund_history_status.json (T-131 complete=true 2026-10-02 15:40, universe 5229, done 5224, quarantined 5)",
            data_locality="data/fund_history/ = bm-c machine-local (R31/R65 lane); bm-a holds no raw copy -- burns/preregs must plan lane or TRANSFER per fleet/TRANSFER.md",
        ),
        statutory_gate=stat_rule,
        gate_inheritance="ALL UNLOCK faces: preregs MUST inherit the statutory-anchoring gate (period-end anchoring = prereg rejection)",
        faces=rows, n_unlock=n_unlock, n_stay_locked=len(rows) - n_unlock,
        conclusion=("4 direct + 3 proxy-declared UNLOCK (7/8); 1 STAY-LOCKED (fund_gross_profitability: "
                    "income-statement gap -> next data slice candidate); all unlocks gated on statutory anchoring."),
    )
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("unlock:", n_unlock, "stay-locked:", len(rows) - n_unlock)
    for r in rows:
        print(" ", r["face"], r["verdict"], "(" + r["kind"] + ")")


if __name__ == "__main__":
    main()
