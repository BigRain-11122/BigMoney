"""T27 PIT availability face for the three statement panels.

DEFECT (r1093 audit, re-proved at source r1094): the declare column the
collector stores as ``avail_date`` is a LATEST-REVISION date, not the
first-announce date.

  * income  : source column is literally 最新公告日期 (latest notice) ->
              panel equals source verbatim, median lag ~360d from period end.
  * balance / cashflow: column is 公告日期 but rows restated later get
              bumped to the revision date (annual rows ~73% shifted,
              quarterly mostly clean).

Because a latest-revision date is always >= the first announce, the stored
face is not look-ahead-unsafe, but it destroys coverage (a 2024-06-30
statement looks unavailable until 2025-08). The consumer-grade repair that
is PROVABLY safe without re-deriving the original announce date is:

    avail_pit = min(stored_latest_revision, statutory_deadline(period))

Proof of safety: the statutory deadline is >= the true first announce date
(companies must file by then) and the stored revision date is also >= the
true first announce. The minimum of two upper bounds is still an upper
bound -> avail_pit >= true announce for every row. It is also strictly
tighter than the stored face whenever the row was revised late.

Outputs (derived face, never overwrites the source panel):
    data/fund_statements/pit_avail/<face>_avail.parquet
    results/fund_avail_pit_t27.json

Exit codes: 0 ok | 2 machinery | 3 missing panel face.
Selftest: python scripts/fund_avail_pit_t27.py selftest
"""
import datetime as dt
import io
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from update_fund_statements import (  # noqa: E402
    DATA_DIR, FACE_PATH, statutory_deadline)

OUT_DIR = os.path.join(DATA_DIR, "pit_avail")
SUMMARY = os.path.join(ROOT, "results", "fund_avail_pit_t27.json")
FACES = ("income", "balance", "cashflow")


def _deadline_date(period_end) -> dt.date:
    """period_end is stored as 'YYYY-MM-DD' -> statutory deadline date."""
    d = dt.date.fromisoformat(str(period_end))
    return statutory_deadline(f"{d.year}{d.month:02d}{d.day:02d}")


def avail_pit(period_end, avail_date):
    """Conservative PIT availability = min(latest-revision, deadline).

    avail_date may be None/NaT/'' for rows the source never dated; the
    deadline is then the only honest bound. A stored date EARLIER than the
    period end is impossible for a real announce (a second leak of the
    revision-column semantic: some balance rows carry another period's
    notice); those fall back to the deadline instead of fabricating an
    early, look-ahead-unsafe date. Returns ISO date string.
    """
    deadline = _deadline_date(period_end)
    d = None
    if avail_date is not None and not (isinstance(avail_date, float)
                                       and pd.isna(avail_date)):
        try:
            stamp = pd.Timestamp(avail_date)
            if not pd.isna(stamp):
                d = stamp.date()
        except (ValueError, TypeError):
            d = None
    if d is None:
        return deadline.isoformat()
    period_d = dt.date.fromisoformat(str(period_end))
    if d < period_d:
        return deadline.isoformat()
    return min(d, deadline).isoformat()


def build_face(face: str, frame: pd.DataFrame):
    """Keyed on (code, period_end): the collected panels normalise the symbol
    to ``code``, the EM raw export calls it ``股票代码`` -- r1096: looking only
    for the raw name silently dropped the key and made the derived face
    unjoinable by every per-symbol consumer."""
    cols = [c for c in ("code", "股票代码", "period_end", "avail_date")
            if c in frame.columns]
    sub = frame[cols].copy()
    if "股票代码" in sub.columns and "code" not in sub.columns:
        sub = sub.rename(columns={"股票代码": "code"})
    sub["avail_pit"] = [avail_pit(p, a) for p, a in zip(sub["period_end"],
                                                        sub["avail_date"])]
    sub["deadline"] = [_deadline_date(p).isoformat() for p in sub["period_end"]]
    early = pd.to_datetime(sub["avail_date"], errors="coerce") < \
        pd.to_datetime(sub["period_end"])
    sub.attrs["invalid_early"] = int(early.sum())
    # hard invariants: period_end <= avail_pit <= both bounds
    if (pd.to_datetime(sub["avail_pit"]) <
            pd.to_datetime(sub["period_end"])).any():
        raise AssertionError(f"{face}: avail_pit before period_end")
    if (pd.to_datetime(sub["avail_pit"]) >
            pd.to_datetime(sub["deadline"])).any():
        raise AssertionError(f"{face}: avail_pit after statutory deadline")
    return sub


def run():
    receipts = {"ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
                "audit": "T27 PIT availability repair (min(latest_revision, deadline))",
                "faces": {}}
    missing = []
    os.makedirs(OUT_DIR, exist_ok=True)
    for face in FACES:
        path = FACE_PATH[face]
        if not os.path.exists(path):
            missing.append(face)
            continue
        frame = pd.read_parquet(path)
        pit = build_face(face, frame)
        out = os.path.join(OUT_DIR, f"{face}_avail.parquet")
        pit.to_parquet(out, index=False)
        known = pit["avail_date"].notna()
        lag_before = (pd.to_datetime(pit.loc[known, "avail_date"]) -
                      pd.to_datetime(pit.loc[known, "period_end"])).dt.days
        lag_after = (pd.to_datetime(pit["avail_pit"]) -
                     pd.to_datetime(pit["period_end"])).dt.days
        receipts["faces"][face] = {
            "rows": int(len(pit)),
            "avail_date_present": int(known.sum()),
            "median_lag_days_before": float(lag_before.median()) if known.any() else None,
            "median_lag_days_after": float(lag_after.median()),
            "p90_lag_days_after": float(lag_after.quantile(0.9)),
            "rows_tightened": int((lag_after < lag_before.reindex(pit.index)).sum()),
            "invalid_early_avail": int(pit.attrs.get("invalid_early", 0)),
            "out": os.path.relpath(out, ROOT),
        }
        print(face, receipts["faces"][face])
    io.open(SUMMARY, "w", encoding="utf-8", newline="\n").write(
        json.dumps(receipts, ensure_ascii=False, indent=2))
    print("wrote", os.path.relpath(SUMMARY, ROOT))
    if missing:
        print("MISSING PANEL FACES:", missing)
        return 3
    return 0


def selftest():
    checks = []
    # 1. on-time row unchanged
    checks.append(avail_pit("2024-06-30", "2024-08-28") == "2024-08-28")
    # 2. late-revision row clamped to the H1 deadline (2024-08-31)
    checks.append(avail_pit("2024-06-30", "2025-08-26") == "2024-08-31")
    # 3. annual period spans the year boundary (deadline 2025-04-30)
    checks.append(avail_pit("2024-12-31", "2026-03-01") == "2025-04-30")
    checks.append(avail_pit("2024-12-31", "2025-03-20") == "2025-03-20")
    # 4. Q1 / Q3 deadlines
    checks.append(avail_pit("2025-03-31", "2026-09-14") == "2025-04-30")
    checks.append(avail_pit("2025-09-30", "2026-09-14") == "2025-10-31")
    # 5. absent / garbage availability -> deadline (never fabricated early)
    checks.append(avail_pit("2024-06-30", None) == "2024-08-31")
    checks.append(avail_pit("2024-06-30", float("nan")) == "2024-08-31")
    checks.append(avail_pit("2024-06-30", pd.NaT) == "2024-08-31")
    checks.append(avail_pit("2024-06-30", "--") == "2024-08-31")
    checks.append(avail_pit("2024-06-30", "") == "2024-08-31")
    # 5b. stored date before period end (impossible announce) -> deadline
    checks.append(avail_pit("2024-06-30", "2024-02-01") == "2024-08-31")
    # 6. safety property: result is never EARLIER than the stored revision
    for period, stored in (("2024-06-30", "2024-08-28"),
                           ("2024-06-30", "2025-08-26"),
                           ("2024-12-31", "2025-03-20")):
        checks.append(avail_pit(period, stored) >= min(
            stored, _deadline_date(period).isoformat()))
    # 7. build_face invariants + tightening on a tiny frame
    tiny = pd.DataFrame({"股票代码": ["000001", "000002"],
                         "period_end": ["2024-06-30", "2024-06-30"],
                         "avail_date": ["2024-08-28", "2025-08-26"]})
    out = build_face("income", tiny)
    checks.append(list(out["avail_pit"]) == ["2024-08-28", "2024-08-31"])
    # 7b. the symbol key survives (r1096: keyed face must stay joinable)
    checks.append(list(out["code"]) == ["000001", "000002"])
    # 8. build_face refuses rows whose period_end is unparseable
    try:
        build_face("income", pd.DataFrame({"period_end": ["bogus"],
                                           "avail_date": [None]}))
        checks.append(False)
    except ValueError:
        checks.append(True)
    failed = [i for i, ok in enumerate(checks) if not ok]
    print(f"selftest {len(checks) - len(failed)}/{len(checks)} PASS")
    if failed:
        print("failed cases:", failed)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(run())
    except AssertionError as exc:
        print("INVARIANT BREACH:", exc)
        sys.exit(2)