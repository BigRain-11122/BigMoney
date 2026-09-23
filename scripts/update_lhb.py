"""LHB event history incremental refresh (P-A family pointer 4, claim
MSG-20260923-2045). Pure data engineering: zero IC, zero engine runs,
ledger N untouched.

Source-consistent with the original archive: ak.stock_lhb_detail_em
(EastMoney), same schema by construction. The original pipeline
(Money02/lhb_download.py) is quarterly-chunked and idempotent; this
refresh keeps that mechanism intact: re-fetch ONLY the quarter that
contains the current cutoff (superset overwrite of that one chunk),
then rebuild lhb_detail.parquet exactly the way the original script does
(concat all chunks). Appending to the parquet without the chunk would
desynchronize the two and a future re-run of the original downloader
would silently drop the appended rows.

Safety (update_daily paradigm):
  - overlap check: re-fetched rows with date <= cutoff must match the
    stored rows for the cutoff date (row count + net-buy sum, tol 1e-6);
    mismatch = source restated history -> write NOTHING, flag, exit 3
  - idempotent: no events beyond cutoff -> honest no-op exit 0
  - fetch failure -> no write, exit 2 (retry next run)
Write-domain (claim-scoped): the current-quarter chunk file,
lhb_detail.parquet, results/lhb_update_status.json. Nothing else.
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_DIR = os.path.join(ROOT, "Money02", "data", "lhb")
PARQUET = os.path.join(LHB_DIR, "lhb_detail.parquet")
CHUNKS = os.path.join(LHB_DIR, "chunks")
STATUS = os.path.join(ROOT, "results", "lhb_update_status.json")
TOL = 1e-6


def save_status(payload):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)


def rebuild_from_chunks():
    frames = []
    for name in sorted(os.listdir(CHUNKS)):
        if not name.endswith(".parquet"):
            continue
        p = os.path.join(CHUNKS, name)
        if os.path.getsize(p) == 0:
            continue
        frames.append(pd.read_parquet(p))
    full = pd.concat([f for f in frames if len(f)], ignore_index=True)
    full.to_parquet(PARQUET, index=False)
    return len(full)


def main():
    t0 = time.time()
    lhb = pd.read_parquet(PARQUET)
    dates = pd.to_datetime(lhb["上榜日"])
    cutoff = dates.max()
    today = pd.Timestamp.today().normalize()
    q = pd.Period(cutoff, freq="Q")
    qs = q.start_time.strftime("%Y%m%d")
    qe = q.end_time.strftime("%Y%m%d")
    print(f"cutoff={cutoff.date()} quarter={q} today={today.date()}",
          flush=True)
    if today <= cutoff:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "no-op (today <= cutoff)"})
        print("no-op: nothing beyond cutoff", flush=True)
        return 0

    # ---- re-fetch the cutoff quarter (superset by construction)
    try:
        import akshare as ak
        df = ak.stock_lhb_detail_em(start_date=qs, end_date=qe)
    except Exception as ex:
        save_status({"cutoff": str(cutoff.date()), "verdict":
                     f"fetch_fail: {type(ex).__name__}: {str(ex)[:120]}"})
        print(f"FETCH FAIL {type(ex).__name__}: {str(ex)[:120]}", flush=True)
        return 2
    if df is None or df.empty:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "fetch returned empty (kept local)"})
        print("fetch empty - kept local", flush=True)
        return 0
    fd = pd.to_datetime(df["上榜日"])
    new = df[fd > cutoff]
    print(f"refetched quarter rows={len(df)} new_beyond_cutoff={len(new)}",
          flush=True)

    # ---- overlap check at the cutoff date
    old_day = lhb[pd.to_datetime(lhb["上榜日"]) == cutoff]
    new_day = df[fd == cutoff]
    ok_overlap = True
    detail = {"old_rows": int(len(old_day)), "new_rows": int(len(new_day))}
    if len(old_day) and len(new_day):
        old_sum = float(pd.to_numeric(old_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        new_sum = float(pd.to_numeric(new_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        detail["netbuy_sum_old"] = round(old_sum, 2)
        detail["netbuy_sum_new"] = round(new_sum, 2)
        ok_overlap = (len(old_day) == len(new_day)
                      and abs(old_sum - new_sum) <= max(TOL, abs(old_sum) * 1e-9))
    elif len(old_day) != len(new_day):
        ok_overlap = False
    if not ok_overlap:
        save_status({"cutoff": str(cutoff.date()),
                     "verdict": "overlap_mismatch: source restated history, "
                                "local kept untouched",
                     "overlap": detail})
        print(f"OVERLAP MISMATCH {detail} - kept local, no write", flush=True)
        return 3

    # ---- overwrite the cutoff quarter chunk, rebuild parquet
    if len(new) == 0:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "no-op (no events beyond cutoff yet)",
                     "overlap": detail})
        print("no events beyond cutoff yet - no-op", flush=True)
        return 0
    chunk_path = os.path.join(CHUNKS, f"{q}.parquet")
    df.to_parquet(chunk_path, index=False)
    total = rebuild_from_chunks()
    new_cutoff = str(pd.to_datetime(
        pd.read_parquet(PARQUET, columns=["上榜日"])["上榜日"]).max().date())
    save_status({"cutoff_before": str(cutoff.date()),
                 "cutoff_after": new_cutoff, "new_rows": int(len(new)),
                 "quarter_refetched": str(q), "total_rows": int(total),
                 "overlap": detail, "verdict": "updated"})
    print(f"updated: +{len(new)} rows, cutoff {cutoff.date()} -> "
          f"{new_cutoff}, total {total} ({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
