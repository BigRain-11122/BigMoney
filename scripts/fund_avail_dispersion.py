"""T27 measurement: does the first-announce face restore cross-sectional
disclosure ordering that the deadline fallback destroys?

Context (r1097-r1098 bm-a):
  * the collector column ``avail_date`` is a LATEST-REVISION stamp
    (== UPDATE_DATE for 99.83% of rows, == NOTICE_DATE for 4.67%), so
    ``avail_pit = min(revision, statutory_deadline)`` collapses almost every
    (code, period) row of a period onto the same statutory date;
  * ``scripts/fund_avail_notice.py`` rebuilds ``avail_first = min(NOTICE_DATE,
    stored)`` from the EM datacenter NOTICE_DATE field, cached per period.

This module answers one question with numbers: on the periods whose
NOTICE_DATE cache already exists, how much ordering does the repair restore,
and what does each row move by?

Per (face, period) it records, on the same row set:
    rows, distinct_pit, distinct_first      (ordering capacity)
    med_lag / iqr_lag  for the pit vs the first face  (days from period end)
    tighten_n (first < pit), delay_n (first > pit), median / p90 |shift| days
    spearman between the two date vectors when both sides have variance
plus a rows-weighted aggregate per face and an honest coverage block.

Read-only on every input face; writes only results/fund_avail_dispersion.json.

Usage: python scripts/fund_avail_dispersion.py [run] [--face income]
       python scripts/fund_avail_dispersion.py selftest
Exit: 0 ok, 2 machinery failure.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from fund_avail_notice import (  # noqa: E402
    CACHE_DIR, FACES, build_face, cache_path, iso_period)
from update_fund_statements import DATA_DIR, FACE_PATH  # noqa: E402

OUT = os.path.join(ROOT, "results", "fund_avail_dispersion.json")
PIT_DIR = os.path.join(DATA_DIR, "pit_avail")


def _lag_days(dates, period):
    return (pd.to_datetime(dates) - pd.Timestamp(period)).dt.days.astype(float)


def _stats(series):
    s = series.dropna()
    if len(s) == 0:
        return {"n": 0, "med": None, "iqr": None}
    return {"n": int(len(s)), "med": float(s.median()),
            "iqr": float(s.quantile(0.75) - s.quantile(0.25))}


def _spearman(a, b):
    """Rank agreement without scipy: Pearson on average ranks."""
    a = pd.Series(a).astype(float)
    b = pd.Series(b).astype(float)
    if a.nunique() < 2 or b.nunique() < 2:
        return None
    ra, rb = a.rank(), b.rank()
    ra, rb = ra - ra.mean(), rb - rb.mean()
    den = (ra.pow(2).sum() ** 0.5) * (rb.pow(2).sum() ** 0.5)
    if den == 0:
        return None
    return float((ra * rb).sum() / den)


def measure_period(face, period, frame, cache):
    """frame = rows of one period from the published pit face (code,
    period_end, avail_pit); cache = this period's notice frame."""
    built = build_face(face, frame, cache)
    ref = frame[["code", "avail_pit"]].copy()
    ref["code"] = ref["code"].astype(str).str.zfill(6)
    built["code"] = built["code"].astype(str).str.zfill(6)
    m = built.merge(ref, on="code", how="left")
    period_iso = iso_period(period)
    pit_lag = _lag_days(m["avail_pit"], period_iso)
    first_lag = _lag_days(m["avail_first"], period_iso)
    shift = (pd.to_datetime(m["avail_first"])
             - pd.to_datetime(m["avail_pit"])).dt.days
    covered = m["source_notice"].notna()
    return {
        "rows": int(len(m)),
        "notice_covered": int(covered.sum()),
        "distinct_pit": int(m["avail_pit"].nunique()),
        "distinct_first": int(m["avail_first"].nunique()),
        "lag_pit": _stats(pit_lag),
        "lag_first": _stats(first_lag),
        "tighten_n": int((shift < 0).sum()),
        "delay_n": int((shift > 0).sum()),
        "same_n": int((shift == 0).sum()),
        "abs_shift_med": float(shift.abs().median()) if len(shift) else None,
        "abs_shift_p90": float(shift.abs().quantile(0.90)) if len(shift) else None,
        "late_first_n": int(m["late_filer"].sum()),
        "spearman": _spearman(pit_lag, first_lag),
    }


def run(only_face=None, log=print):
    faces = [only_face] if only_face else list(FACES)
    out = {"ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
           "audit": "T27 dispersion: avail_pit (deadline fallback) vs "
                    "avail_first (min NOTICE_DATE, stored)",
           "faces": {}}
    for face in faces:
        pit_path = os.path.join(PIT_DIR, f"{face}_avail.parquet")
        src_path = FACE_PATH[face]
        if not os.path.exists(pit_path) or not os.path.exists(src_path):
            out["faces"][face] = {"status": "missing_input",
                                  "pit_face": os.path.exists(pit_path),
                                  "panel": os.path.exists(src_path)}
            continue
        frame = pd.read_parquet(pit_path)
        frame["code"] = frame["code"].astype(str).str.zfill(6)
        staged = sorted(frame["period_end"].dropna().unique())
        cached = [p for p in staged
                  if os.path.exists(cache_path(face, p.replace("-", "")))]
        rows = []
        for p in cached:
            period = p.replace("-", "")
            sub = frame[frame["period_end"] == p]
            cache = pd.read_parquet(cache_path(face, period))
            try:
                rows.append(dict(period=period,
                                 **measure_period(face, period, sub, cache)))
            except Exception as exc:  # noqa: BLE001 - report, never abort
                rows.append({"period": period, "error": f"{type(exc).__name__}: {exc}"})
        ok = [r for r in rows if "error" not in r]
        agg = {}
        if ok:
            n = sum(r["rows"] for r in ok)
            agg = {
                "periods_measured": len(ok),
                "periods_staged": len(staged),
                "coverage_share": round(len(ok) / len(staged), 4) if staged else 0.0,
                "rows": n,
                "notice_covered": sum(r["notice_covered"] for r in ok),
                "distinct_pit_median": float(pd.Series(
                    [r["distinct_pit"] for r in ok]).median()),
                "distinct_first_median": float(pd.Series(
                    [r["distinct_first"] for r in ok]).median()),
                "tighten_share": round(sum(r["tighten_n"] for r in ok) / n, 4),
                "delay_share": round(sum(r["delay_n"] for r in ok) / n, 4),
                "same_share": round(sum(r["same_n"] for r in ok) / n, 4),
                "late_first_share": round(
                    sum(r["late_first_n"] for r in ok) / n, 4),
            }
            sp = [r["spearman"] for r in ok if r["spearman"] is not None]
            agg["spearman_median"] = float(pd.Series(sp).median()) if sp else None
            # era split: the NOTICE_DATE channel only becomes a real
            # first-announce stamp from ~2010 (pre-2010 emits restatement
            # stamps, which the build gate sends back to the deadline bound).
            eras = {}
            for label, sel in (("pre_2010", lambda p: p < "20100101"),
                               ("2010_plus", lambda p: p >= "20100101")):
                sub = [r for r in ok if sel(r["period"])]
                if not sub:
                    continue
                n2 = sum(r["rows"] for r in sub)
                eras[label] = {
                    "periods": len(sub), "rows": n2,
                    "distinct_pit_mean": round(sum(
                        r["distinct_pit"] for r in sub) / len(sub), 1),
                    "distinct_first_mean": round(sum(
                        r["distinct_first"] for r in sub) / len(sub), 1),
                    "tighten_share": round(sum(
                        r["tighten_n"] for r in sub) / n2, 4),
                    "delay_share": round(sum(
                        r["delay_n"] for r in sub) / n2, 4),
                    "same_share": round(sum(r["same_n"] for r in sub) / n2, 4),
                    "late_first_share": round(sum(
                        r["late_first_n"] for r in sub) / n2, 4),
                }
            agg["eras"] = eras
        out["faces"][face] = {"status": "measured" if ok else "no_cached_periods",
                              "aggregate": agg, "periods": rows}
        log(f"[dispersion] {face}: measured {len(ok)}/{len(staged)} periods"
            + (f", tighten_share={agg.get('tighten_share')}"
               f", distinct_pit={agg.get('distinct_pit_median')}"
               f" -> distinct_first={agg.get('distinct_first_median')}"
               if ok else ""))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    log(f"[dispersion] wrote {os.path.relpath(OUT, ROOT)}")
    return 0


def selftest():
    """Synthetic legs: collapse, tighten, delay, deadline fallback, ordering."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="availdisp_")
    frame = pd.DataFrame({
        "code": ["000001", "000002", "000003"],
        "period_end": ["2020-03-31"] * 3,
        # the stored revision stamp is a year late on every row ...
        "avail_date": ["2021-04-30"] * 3,
        # ... so the deadline fallback puts every row on the statutory date
        "avail_pit": ["2020-04-30"] * 3,
    })
    cache = pd.DataFrame({
        "code": ["000001", "000002"],          # 000003 uncached -> deadline
        "first_notice": [pd.Timestamp("2020-04-10"), pd.Timestamp("2020-05-20")],
    })
    r = measure_period("income", "20200331", frame, cache)
    assert r["rows"] == 3, r
    assert r["notice_covered"] == 2, r
    assert r["distinct_pit"] == 1 and r["distinct_first"] == 3, r
    assert r["tighten_n"] == 1, r          # 000001 moves 20d earlier
    assert r["delay_n"] == 1, r            # 000002 moves 20d later (late filer)
    assert r["same_n"] == 1, r             # 000003 keeps the deadline bound
    assert r["abs_shift_med"] == 20.0, r
    assert r["late_first_n"] == 1, r
    assert r["lag_pit"]["med"] == 30.0, r  # 2020-03-31 -> 2020-04-30
    assert r["lag_first"]["med"] == 30.0, r
    assert r["spearman"] is None or abs(r["spearman"]) <= 1.0, r
    # sync check: an all-cached period with reversed ordering must be -1
    frame2 = pd.DataFrame({"code": ["000001", "000002"],
                           "period_end": ["2020-03-31"] * 2,
                           "avail_date": ["2021-04-30"] * 2,
                           "avail_pit": ["2020-04-10", "2020-04-20"]})
    cache2 = pd.DataFrame({"code": ["000001", "000002"],
                           "first_notice": [pd.Timestamp("2020-04-20"),
                                            pd.Timestamp("2020-04-10")]})
    r2 = measure_period("income", "20200331", frame2, cache2)
    assert r2["distinct_pit"] == 2 and r2["distinct_first"] == 2, r2
    assert (r2["spearman"] is not None
            and abs(r2["spearman"] + 1.0) < 1e-9), r2
    # identical faces -> spearman undefined (zero variance on one side only)
    cache3 = pd.DataFrame({"code": ["000001", "000002"],
                           "first_notice": [pd.Timestamp("2020-04-10"),
                                            pd.Timestamp("2020-04-10")]})
    r3 = measure_period("income", "20200331", frame2, cache3)
    assert r3["distinct_first"] == 1 and r3["spearman"] is None, r3
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("fund_avail_dispersion selftest: 3/3 PASS")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = None
        if "--face" in argv:
            face = argv[argv.index("--face") + 1]
            if face not in FACES:
                print(f"unknown face {face}", file=sys.stderr)
                return 2
        return run(face)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"machinery failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)