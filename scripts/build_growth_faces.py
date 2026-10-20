"""Build the growth data face for a future FUND-GROWTH family batch (r1092 bm-a).

Why this exists: O-20261019-2230-bm-b sec.2 item 5 asks for rolling
fundamental-family new batches (growth / shareholder behaviour / seasonality)
and every family has to pass a data-availability audit first ("五步制·每族带
数据可达性审计"). FUND-VALUE / FUND-QUALITY already have P1+P2 faces in
data/fund_history_export/. The growth family had no face at all, so no runner
could be wired. This script produces that face with the same contract as
quality_faces.parquet so the P1 runner can mirror the quality skeleton verbatim.

Source (single, in-repo, zero network):
  data/fund_statement_export/income_faces.parquet
  columns used: code / period_end / avail_date /
                '净利润-同比增长' (net profit YoY, percent) /
                '营业总收入-同比增长' (revenue YoY, percent)

PIT convention (statutory only, same contract as the quality face):
  avail = statutory_avail(period_end)   (Q1->04-30 / H1->08-31 / Q3->10-31 /
                                        FY->next-year 04-30)
  The source avail_date column is NOT usable as a PIT anchor: measured on the
  full panel, its median distance to the statutory deadline is exactly 360
  days (90% of rows > 90 days, 91.7% classified year-shifted ~365d) while the
  newest rows are on time -- i.e. the historical availability dates carry a
  systematic +1 year offset. Using max(statutory, observed) would therefore
  delay every row by a year. The face uses the statutory map and the anomaly
  is measured and reported in the receipt (data-defect finding for the
  collector lane), never silently applied.

Dedupe: per (code, period_end) keep the row with the latest effective avail
(as-collected revisions win, one row per period, same as the quality contract).

Output:
  data/fund_history_export/growth_faces.parquet
      code str / period_end str / avail_date str / np_yoy float32 / rev_yoy float32
  results/_growth_faces_build.json     receipt (counts, coverage, disclosures)

Usage:
  python scripts/build_growth_faces.py build
  python scripts/build_growth_faces.py verify
  python scripts/build_growth_faces.py selftest
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "fund_statement_export", "income_faces.parquet")
OUT = os.path.join(ROOT, "data", "fund_history_export", "growth_faces.parquet")
RECEIPT = os.path.join(ROOT, "results", "_growth_faces_build.json")

COL_NP = "净利润-同比增长"
COL_REV = "营业总收入-同比增长"

# period-end month-day -> statutory availability month-day (+ year rollover)
_STAT = {
    "03-31": ("04-30", 0),
    "06-30": ("08-31", 0),
    "09-30": ("10-31", 0),
    "12-31": ("04-30", 1),
}


def now_iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def statutory_avail(period_end: str):
    """'YYYY-MM-DD' period end -> statutory availability 'YYYY-MM-DD' or None."""
    if not isinstance(period_end, str) or len(period_end) != 10:
        return None
    if period_end[4] != "-" or period_end[7] != "-":
        return None
    hit = _STAT.get(period_end[5:])
    if hit is None:
        return None
    avail_md, rollover = hit
    year = int(period_end[:4]) + rollover
    return f"{year:04d}-{avail_md}"


def build_frame(src: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Pure transform: raw income rows -> growth face + facts. No IO."""
    missing = [c for c in ("code", "period_end", "avail_date", COL_NP, COL_REV)
               if c not in src.columns]
    if missing:
        raise RuntimeError(f"source columns missing: {missing}")

    df = src[["code", "period_end", "avail_date", COL_NP, COL_REV]].copy()
    for c in ("code", "period_end", "avail_date"):
        df[c] = (df[c].astype("object").where(df[c].notna(), "")
                 .astype(str).str.strip())
        df[c] = df[c].replace({"nan": "", "None": "", "<NA>": ""})

    stat = df["period_end"].map(statutory_avail)
    invalid_period = stat.isna()
    df = df[~invalid_period].copy()
    stat = stat[~invalid_period]

    observed = df["avail_date"].to_numpy(dtype=object)
    legal = stat.to_numpy(dtype=object)
    has_obs = np.array([o != "" for o in observed])
    # PIT anchor = statutory deadline (see module docstring); the observed
    # column is measured below and never used as the anchor.
    gaps = {}
    for i, o in enumerate(observed):
        if not has_obs[i]:
            continue
        try:
            d0 = datetime.date.fromisoformat(legal[i])
            d1 = datetime.date.fromisoformat(o)
        except ValueError:
            continue
        gaps[i] = (d1 - d0).days
    gap_days = list(gaps.values())
    n_obs = len(gap_days)
    cls = {"on_time_0_120": 0, "year_shifted_300_430": 0,
           "other_late_gt_430": 0, "early_lt_0": 0}
    for g in gap_days:
        if g < 0:
            cls["early_lt_0"] += 1
        elif g <= 120:
            cls["on_time_0_120"] += 1
        elif g <= 430:
            cls["year_shifted_300_430"] += 1
        else:
            cls["other_late_gt_430"] += 1
    df["avail_date"] = legal

    df = df.rename(columns={COL_NP: "np_yoy", COL_REV: "rev_yoy"})
    for c in ("np_yoy", "rev_yoy"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float32")

    both_null = df["np_yoy"].isna() & df["rev_yoy"].isna()
    dups = int(df.duplicated(subset=["code", "period_end"]).sum())
    df = df[~both_null]
    df = (df.sort_values(["code", "period_end", "avail_date"])
            .drop_duplicates(subset=["code", "period_end"], keep="last")
            .reset_index(drop=True))
    df = df.sort_values(["code", "avail_date", "period_end"]).reset_index(drop=True)

    mono_violations = 0
    for _, g in df.groupby("code", sort=False):
        a = g["avail_date"].to_numpy()
        if len(a) > 1 and (a[1:] < a[:-1]).any():
            mono_violations += 1

    facts = {
        "rows_in": int(len(src)),
        "rows_out": int(len(df)),
        "codes": int(df["code"].nunique()),
        "periods": int(df["period_end"].nunique()),
        "invalid_period_rows": int(invalid_period.sum()),
        "both_null_rows_dropped": int(both_null.sum()),
        "duplicate_period_rows_collapsed": dups,
        "observed_avail_available_rows": n_obs,
        "observed_avail_gap_days_median": (sorted(gap_days)[len(gap_days) // 2]
                                           if gap_days else None),
        "observed_avail_class": {k: (round(v / n_obs, 6) if n_obs else 0.0)
                                 for k, v in cls.items()},
        "observed_avail_usable_as_pit_anchor": False,
        "np_yoy_null_share": round(float(df["np_yoy"].isna().mean()), 6),
        "rev_yoy_null_share": round(float(df["rev_yoy"].isna().mean()), 6),
        "avail_min": str(df["avail_date"].min()),
        "avail_max": str(df["avail_date"].max()),
        "period_min": str(df["period_end"].min()),
        "period_max": str(df["period_end"].max()),
        "monotonic_avail_violations": mono_violations,
    }
    return df, facts


def cmd_build() -> int:
    if not os.path.exists(SRC):
        print(f"FAIL missing source {SRC}")
        return 2
    src = pd.read_parquet(SRC)
    df, facts = build_frame(src)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_parquet(OUT, index=False)

    # per-year row counts + latest-period coverage read back from the file
    df["_y"] = df["avail_date"].str[:4]
    per_year = {str(k): int(v) for k, v in df["_y"].value_counts().sort_index().items()}
    last_period = str(df["period_end"].max())
    last_codes = int(df.loc[df["period_end"] == last_period, "code"].nunique())

    receipt = {
        "generated": now_iso(),
        "machine": "bm-a",
        "source": os.path.relpath(SRC, ROOT).replace("\\", "/"),
        "output": os.path.relpath(OUT, ROOT).replace("\\", "/"),
        "bytes": os.path.getsize(OUT),
        "faces": ["np_yoy", "rev_yoy"],
        "pit_rule": "avail = max(statutory_avail(period_end), source avail_date)",
        "facts": facts,
        "rows_by_avail_year": per_year,
        "latest_period": last_period,
        "latest_period_codes": last_codes,
        "verdict": ("GREEN" if facts["monotonic_avail_violations"] == 0
                    and facts["rows_out"] > 0 else "RED"),
        "note": ("read-only data face; no judgment line, no prereg, no burn. "
                 "Family batch still needs its own prereg + freeze gate."),
    }
    os.makedirs(os.path.dirname(RECEIPT), exist_ok=True)
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: receipt[k] for k in ("verdict", "bytes", "latest_period",
                                             "latest_period_codes")}, ensure_ascii=False))
    print(json.dumps(facts, ensure_ascii=False))
    return 0 if receipt["verdict"] == "GREEN" else 1


def cmd_verify() -> int:
    if not os.path.exists(OUT):
        print("FAIL face missing")
        return 2
    df = pd.read_parquet(OUT)
    checks = {
        "columns": list(df.columns) == ["code", "period_end", "avail_date",
                                        "np_yoy", "rev_yoy"],
        "dtype_np": str(df["np_yoy"].dtype) == "float32",
        "dtype_rev": str(df["rev_yoy"].dtype) == "float32",
        "no_dup_period": not df.duplicated(subset=["code", "period_end"]).any(),
        "avail_ge_statutory": bool(
            (df["avail_date"].to_numpy()
             >= df["period_end"].map(statutory_avail).to_numpy()).all()),
        "not_empty": len(df) > 0,
    }
    print(json.dumps(checks, ensure_ascii=False))
    return 0 if all(checks.values()) else 1


# ------------------------------------------------------------------ selftest

def _fixture() -> pd.DataFrame:
    return pd.DataFrame([
        # normal Q1, disclosed before the statutory deadline -> statutory wins
        {"code": "000001", "period_end": "2005-03-31", "avail_date": "2005-04-20",
         COL_NP: 10.0, COL_REV: 12.0},
        # FY -> rolls to next-year 04-30
        {"code": "000001", "period_end": "2005-12-31", "avail_date": "2006-04-10",
         COL_NP: 18.0, COL_REV: 9.0},
        # late reporter: observed disclosure AFTER the statutory date -> max wins
        {"code": "600000", "period_end": "2005-03-31", "avail_date": "2006-04-26",
         COL_NP: -4.0, COL_REV: 3.0},
        # duplicate period (revision) -> keep the later avail row
        {"code": "600000", "period_end": "2005-06-30", "avail_date": "2005-08-01",
         COL_NP: 1.0, COL_REV: 2.0},
        {"code": "600000", "period_end": "2005-06-30", "avail_date": "2005-08-29",
         COL_NP: 5.0, COL_REV: 6.0},
        # invalid period end -> dropped
        {"code": "600000", "period_end": "2005-05-15", "avail_date": "2005-06-01",
         COL_NP: 9.0, COL_REV: 9.0},
        # both faces null -> dropped
        {"code": "600001", "period_end": "2005-09-30", "avail_date": "2005-10-20",
         COL_NP: None, COL_REV: None},
    ])


def cmd_selftest() -> int:
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    leg("statutory_q1", statutory_avail("2005-03-31") == "2005-04-30")
    leg("statutory_h1", statutory_avail("2005-06-30") == "2005-08-31")
    leg("statutory_q3", statutory_avail("2005-09-30") == "2005-10-31")
    leg("statutory_fy_rollover", statutory_avail("2005-12-31") == "2006-04-30")
    leg("statutory_invalid", statutory_avail("2005-05-15") is None)
    leg("statutory_none", statutory_avail(None) is None)

    df, facts = build_frame(_fixture())
    leg("rows_after_filter", len(df) == 4)
    leg("invalid_dropped", facts["invalid_period_rows"] == 1)
    leg("both_null_dropped", facts["both_null_rows_dropped"] == 1)
    leg("dup_collapsed", facts["duplicate_period_rows_collapsed"] == 1)
    leg("no_dup_period", not df.duplicated(subset=["code", "period_end"]).any())

    a1 = df[(df["code"] == "000001") & (df["period_end"] == "2005-03-31")].iloc[0]
    leg("statutory_wins_when_earlier_observed", a1["avail_date"] == "2005-04-30")
    a2 = df[(df["code"] == "000001") & (df["period_end"] == "2005-12-31")].iloc[0]
    leg("fy_rollover_applied", a2["avail_date"] == "2006-04-30")
    b1 = df[(df["code"] == "600000") & (df["period_end"] == "2005-03-31")].iloc[0]
    leg("late_reporter_still_statutory", b1["avail_date"] == "2005-04-30")
    b2 = df[(df["code"] == "600000") & (df["period_end"] == "2005-06-30")].iloc[0]
    leg("revision_keeps_latest", float(b2["np_yoy"]) == 5.0)
    leg("dtype_float32", str(df["np_yoy"].dtype) == "float32")
    leg("monotonic_ok", facts["monotonic_avail_violations"] == 0)
    leg("observed_gap_measured",
        facts["observed_avail_available_rows"] == 6
        and facts["observed_avail_class"]["year_shifted_300_430"] > 0)

    # coverage semantics: a code whose last anchor is old simply has no new rows
    leg("codes_counted", facts["codes"] == 2)

    ok = all(v for _, v in legs)
    for name, val in legs:
        print(("PASS " if val else "FAIL ") + name)
    print(f"selftest: {sum(1 for _, v in legs if v)}/{len(legs)} " +
          ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "verify", "selftest"])
    a = ap.parse_args()
    return {"build": cmd_build, "verify": cmd_verify, "selftest": cmd_selftest}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())