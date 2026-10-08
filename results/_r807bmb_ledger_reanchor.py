"""r807 bm-b trio fork re-anchor (append-ledger repair, single-count law).

Facts (data-driven, no hand-copied prev):
- FUND-DIVLOWVOL/QUALITY/VALUE-P1 trio finalize landed 2026-10-08 23:30-23:39
  on bm-b's network-blocked STALE tree: prev consumed 790905 (10-03 freeze-era
  head), internal chain 790905->792907->794909->796913 EXACT (verified r807).
- Live fleet head at repair time = ledger_head() (W190 chain, excludes trio).
- The three blocks are already on origin (r806 push landed 00:33) -> the only
  lawful repair = ADDITIVE re-anchor row via science_gates.append_ledger
  (prev derived from live head at call time, voids stamped, fresh batch name
  per finalize_already_landed channel law).

Counting: trio batch_trials 2002+2002+2004 = 6008 counted ONCE here; the
superseded branch totals (792907/794909/796913) stay as sub-head records and
must never be re-added (note below says so explicitly).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from science_gates import (  # noqa: E402
    append_ledger, ledger_head, cutoff_meta, finalize_already_landed)
OUT = os.path.join(ROOT, "results", "fund_trio_p1_ledger_reanchor.json")
RECEIPT = os.path.join(ROOT, "results", "_r807bmb_ledger_reanchor_receipt.json")

TRIO = [
    ("FUND-DIVLOWVOL-P1", 2002, "results/fund_divlowvol_p1/fund_divlowvol_p1_results.json"),
    ("FUND-QUALITY-P1", 2002, "results/fund_quality_p1/fund_quality_p1_results.json"),
    ("FUND-VALUE-P1", 2004, "results/fund_value_p1/fund_value_p1_results.json"),
]
BATCH = "FUND-TRIO-REANCHOR-R807"


def main():
    # integrity precondition: trio internal chain EXACT + blocks present
    prevs = []
    for name, trials, path in TRIO:
        with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
            tl = json.load(fh)["trials_ledger"]
        assert tl["batch"] == name and tl["batch_trials"] == trials, name
        prevs.append((tl["prev_total"], tl["total"]))
    assert prevs[0][1] == prevs[1][0] == 792907 + 0 or True  # chain identity below
    assert prevs[0][0] == 790905
    assert prevs[0][1] == 792907 and prevs[1][0] == 792907
    assert prevs[1][1] == 794909 and prevs[2][0] == 794909
    assert prevs[2][1] == 796913
    batch_trials = sum(t for _, t, _ in TRIO)
    assert batch_trials == 6008
    # double-append guard: fresh batch name must be genuinely new
    landed = finalize_already_landed(BATCH, os.path.relpath(OUT, ROOT))
    assert landed is None, "re-anchor batch already landed: %r" % landed
    head_before = ledger_head()
    # canonical append (prev = live head at call time, voids stamped)
    block = append_ledger(
        batch_name=BATCH, batch_trials=batch_trials,
        file_name="results/fund_trio_p1_ledger_reanchor.json",
        note="fork re-anchor (single-count): FUND-DIVLOWVOL/QUALITY/VALUE-P1 "
             "finalize landed on bm-b network-blocked stale tree consuming "
             "prev=790905 (freeze-era head); live head here excludes the trio; "
             "their 6008 trials are counted exactly ONCE in this row and the "
             "superseded branch totals 792907/794909/796913 are sub-head "
             "records that must never be re-added (E34 landing-head anchor + "
             "MSG-20261001-1432 fork family; verdicts untouched: "
             "insufficient-sample x3 single-read r638 law)",
        evidence_cutoff=cutoff_meta("2026-09-22")["evidence_cutoff"])
    doc = {
        **cutoff_meta("2026-09-22"),
        "batch": BATCH,
        "machine": "bm-b",
        "kind": "trials-ledger fork re-anchor (additive repair row)",
        "trio_batches": [
            {"batch": n, "batch_trials": t, "file": p,
             "stale_prev": a, "stale_total": b,
             "verdict": "insufficient-sample"}
            for (n, t, p), (a, b) in zip(TRIO, prevs)],
        "trials_ledger": block,
        "guard_note": "finalize_already_landed(BATCH)=None pre-append; "
                      "append_ledger prev is data-driven (no hand-copied prev)",
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    head_after = ledger_head()
    receipt = {
        "ts_": __import__("time").strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "head_before": head_before,
        "head_after": head_after,
        "block": block,
        "file": os.path.relpath(OUT, ROOT),
        "law": "append-only additive repair; verdicts untouched (r638 "
               "single-read); zero double-count (superseded branch totals "
               "sub-head); zero loss (6008 re-anchored)",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("REANCHOR_OK prev=%d total=%d head_after=%d file=%s"
          % (block["prev_total"], block["total"],
             head_after["total"], receipt["file"]))
    assert head_after["total"] == block["total"], "head must adopt re-anchor"
    assert head_after["file"] == os.path.basename(OUT)


if __name__ == "__main__":
    main()
