"""r882 bm-b: T-184 self-rescue -- reconstruct data/ext_slots/etf_daily/510880.csv
(pinned P5 slot, alloc_paper P5 pin casualty of the 10-10 13:16 deletion incident).

Sender (bm-a) dark ~26h; branch transfer/t184-510880 absent (ls-remote empty
14:0x). Deadline = next new bar Monday 2026-10-12 ~15:30. Same-source
reconstruction replaces the wait:

  original slot (results/allocation/ALLOC_S2_P5_PULL.json, r188 pull evidence):
    slot_rows=4786, earliest=2007-01-18, latest=2026-09-24,
    arm=ak.fund_etf_hist_sina('sh510880') (download_etf.py lineage, 7-col
    face date,open,high,low,close,volume,amount).

  proof chain (fail-closed asserts, no writes unless ALL pass):
    P1 structural: fresh pull sliced date<=2026-09-24 == 4786 rows,
       earliest 2007-01-18, latest 2026-09-24 (== pull-evidence triple).
    P2 vendor-stability: first 4784 rows (2007-01-18..2026-09-22) content ==
       Money0923/data/daily/510880.csv snapshot row-by-row, all 6 value cols
       (frozen pre-revision-era capture of the same vendor+API).
    P3 marks arbitration: NOT here -- alloc_paper run is the decisive leg
       (engine full-forward recompute must come back byte-identical no-op vs
       the pre-incident ALLOC-P5.json; run separately, revert if changed).

exit 0 = reconstructed+written (P1+P2 passed); 2 = assert fail (no write).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SNAP = os.path.join("Money0923", "data", "daily", "510880.csv")
SLOT = os.path.join("data", "ext_slots", "etf_daily", "510880.csv")
EVID = os.path.join("results", "allocation", "ALLOC_S2_P5_PULL.json")
COLS = ["date", "open", "high", "low", "close", "volume", "amount"]
CUT = "2026-09-24"


def main() -> int:
    import akshare as ak
    k = ak.fund_etf_hist_sina(symbol="sh510880")
    k7 = k[COLS].copy()
    k7["date"] = k7["date"].astype(str)
    rec = k7[k7["date"] <= CUT].reset_index(drop=True)

    # P1 structural face vs r188 pull evidence
    ev = pd.read_json(EVID, typ="series")
    p1 = (len(rec) == int(ev["slot_rows"]) == 4786
          and rec["date"].iloc[0] == ev["earliest"] == "2007-01-18"
          and rec["date"].iloc[-1] == ev["latest"] == CUT)
    print(f"P1 structural: rows={len(rec)} earliest={rec['date'].iloc[0]} "
          f"latest={rec['date'].iloc[-1]} -> {'PASS' if p1 else 'FAIL'}")
    if not p1:
        return 2

    # P2 vendor-stability face vs Money0923 frozen snapshot
    old = pd.read_csv(SNAP)
    old["date"] = old["date"].astype(str)
    head = rec.iloc[: len(old)].reset_index(drop=True)
    p2 = (len(old) == 4784
          and list(old["date"]) == list(head["date"])
          and all(((old[c] == head[c]) | (old[c].isna() & head[c].isna())).all()
                  for c in COLS[1:]))
    bad = [c for c in COLS[1:]
           if not ((old[c] == head[c]) | (old[c].isna() & head[c].isna())).all()]
    print(f"P2 vendor-stability: first-{len(old)} rows vs snapshot "
          f"-> {'PASS' if p2 else 'FAIL ' + str(bad)}")
    if not p2:
        return 2

    os.makedirs(os.path.dirname(SLOT), exist_ok=True)
    rec.to_csv(SLOT, index=False)
    print(f"RECONSTRUCTED+WRITTEN: {SLOT} rows={len(rec)} "
          f"(P3 marks arbitration = alloc_paper run, next step)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
