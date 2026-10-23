"""Cross-statement FILING-EVENT availability face (r1104 bm-a).

WHY (measured, results/fund_avail_filing_event.json):
    The per-face ``NOTICE_DATE`` pull of r1099/r1102 is not equally reliable
    across the three statements. Per-period medians of ``first_notice`` lag
    from period end:

        face      pre-2010 era        2010+ era
        income    ~1 year late (r1099)  ~27d   (correct)
        cashflow  ~26d  (correct)       ~39x d  (WRONG: the following year's
                                                 same-quarter filing notice)
        balance   ~48d  (correct)       ~50d   (correct)

    So cashflow's own notice field is unusable for every period except the
    last few (median-of-medians 394d; only 9.1% of its rows land inside the
    disclosure window). That is why r1102/r1103 had to disclose cashflow's
    first-announce face as "90% deadline fallback and thin".

INSIGHT: the three statements are published in ONE filing event. A quarterly
report announces income, cashflow and balance sheet on the same day. So the
first-announce date of a cashflow row is the same event's date, and a face
that carries a wrong (late) stamp can be repaired by the sibling faces of the
same (code, period) -- without inventing anything.

RULE (never early, never fabricated):
    filing_event(code, period) = min over the three faces' cached
    first_notice dates that fall inside the plausible disclosure window
    (period_end, statutory_deadline + 90d]; if no candidate is in the window
    the row falls back to the statutory deadline (the pre-existing honest
    upper bound), exactly like fund_avail_notice.build_face.
    Caches are joined INSIDE the period they were fetched for (r1102 law):
    a notice date is only meaningful for its own (code, period).

Outputs:
    data/fund_statement_export/pit_avail/<face>_avail_event.parquet
    results/fund_avail_filing_event.json   (face/era comparison + anchors)
Subcommands: run | selftest
Exit codes: 0 ok, 2 machinery, 3 coverage/panel missing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from fund_avail_notice import (  # noqa: E402
    CACHE_DIR, FACES, NOTICE_GRACE_DAYS, OUT_DIR, atomic_write_json,
    cache_path, iso_period, staged_periods)
from update_fund_statements import FACE_PATH, statutory_deadline  # noqa: E402

SUMMARY = os.path.join(ROOT, "results", "fund_avail_filing_event.json")
ANCHOR_PERIODS = ("20050331", "20100331", "20200331", "20250331", "20250930")


# ------------------------------------------------------------------- core
def _load_candidate(face, period):
    """Cached first_notice for one (face, period); empty frame if absent."""
    path = cache_path(face, period)
    if not os.path.exists(path):
        return pd.DataFrame(columns=["code", "first_notice"])
    frame = pd.read_parquet(path)
    frame["code"] = frame["code"].astype(str).str.zfill(6)
    return frame


def filing_event_frame(codes, period_end, deadline, candidates, grace_days=None):
    """Build the filing-event face for ONE period.

    ``candidates`` maps face -> Series(code -> Timestamp) already restricted to
    this period. Accepts a date only if period_end <= d <= deadline + grace.
    Returns (event_series, source_series) both indexed like ``codes``.
    """
    grace = NOTICE_GRACE_DAYS if grace_days is None else int(grace_days)
    pe = pd.Timestamp(period_end)
    dl = pd.Timestamp(deadline)
    window_end = dl + pd.Timedelta(days=grace)
    idx = pd.Index([str(c).zfill(6) for c in codes])
    cleaned = {}
    for face, series in candidates.items():
        if series is None or len(series) == 0:
            continue
        s = series.copy()
        s.index = [str(i).zfill(6) for i in s.index]
        s = pd.to_datetime(s, errors="coerce").reindex(idx)
        cleaned[face] = s.where((s >= pe) & (s <= window_end))
    if not cleaned:
        event = pd.Series([dl] * len(idx), index=idx, dtype="datetime64[ns]")
        return event, pd.Series([None] * len(idx), index=idx, dtype="object")
    grid = pd.DataFrame(cleaned)
    # no in-window candidate -> statutory deadline (honest upper bound)
    event = grid.min(axis=1, skipna=True)
    # source = first face (in FACES order) that supplies the winning date
    source = pd.Series([None] * len(idx), index=idx, dtype="object")
    for face in FACES:
        if face not in grid.columns:
            continue
        hit = source.isna() & grid[face].notna() & (grid[face] == event)
        source = source.mask(hit, face)
    event = event.fillna(dl)
    return event, source


def build_face(face, frame, grace_days=None):
    """Full face rebuild; asserts row count and (code, period) uniqueness."""
    frame = frame.copy()
    frame["period_end"] = (pd.to_datetime(frame["period_end"])
                           .dt.strftime("%Y-%m-%d"))
    cache_by_period = {}
    for period in sorted(frame["period_end"].unique()):
        key = period.replace("-", "")
        cache_by_period[period] = {
            f: _load_candidate(f, key).set_index("code")["first_notice"]
            for f in FACES}
    parts = []
    for period in sorted(frame["period_end"].unique()):
        part = frame[frame["period_end"] == period]
        deadline = statutory_deadline(period.replace("-", ""))
        event, source = filing_event_frame(
            part["code"], period, deadline, cache_by_period[period],
            grace_days=grace_days)
        out = part[["code", "period_end"]].copy()
        out["code"] = out["code"].astype(str).str.zfill(6)
        out["avail_event"] = event.values
        out["source_face"] = source.values
        out["deadline"] = deadline
        fallback = pd.Timestamp(deadline)
        out["avail_event"] = pd.to_datetime(out["avail_event"]).fillna(fallback)
        out["fallback"] = out["source_face"].isna()
        parts.append(out)
    res = pd.concat(parts, ignore_index=True) if parts else frame.iloc[0:0]
    if len(res) != len(frame):
        raise AssertionError(f"{face}: event rows {len(res)} != panel {len(frame)}")
    dup = int(res.duplicated(["code", "period_end"]).sum())
    if dup:
        raise AssertionError(f"{face}: {dup} duplicated (code, period_end)")
    early = (pd.to_datetime(res["avail_event"])
             < pd.to_datetime(res["period_end"]))
    if bool(early.any()):
        raise AssertionError(f"{face}: {int(early.sum())} rows before period_end")
    return res


# ------------------------------------------------------------------ stats
def _era(period_end):
    return "pre_2010" if pd.Timestamp(period_end).year < 2010 else "2010_plus"


def _agg(sub, label):
    pe = pd.to_datetime(sub["period_end"])
    ev = pd.to_datetime(sub["avail_event"])
    lag = (ev - pe).dt.days
    by_period = pd.DataFrame({"period_end": sub["period_end"], "ev": ev})
    distinct = (by_period.groupby("period_end")["ev"].nunique()
                .astype(float))
    return {
        "rows": int(len(sub)),
        "periods": int(sub["period_end"].nunique()),
        "fallback_rows": int(sub["fallback"].sum()),
        "fallback_share": round(float(sub["fallback"].mean()), 4),
        "median_lag_days": float(lag.median()),
        "distinct_first_median": float(distinct.median()),
        "distinct_first_mean": round(float(distinct.mean()), 2),
        "source_share": {f: round(float((sub["source_face"] == f).mean()), 4)
                         for f in FACES},
        "label": label,
    }


def _compare_with_avail_first(face, event):
    """How far does the event face move from the published avail_first face?"""
    path = os.path.join(OUT_DIR, f"{face}_avail_first.parquet")
    if not os.path.exists(path):
        return None
    first = pd.read_parquet(path)
    first["code"] = first["code"].astype(str).str.zfill(6)
    first["period_end"] = (pd.to_datetime(first["period_end"])
                           .dt.strftime("%Y-%m-%d"))
    m = event.merge(first[["code", "period_end", "avail_first",
                           "notice_status"]],
                    on=["code", "period_end"], how="left")
    if len(m) != len(event):
        raise AssertionError(f"{face}: avail_first join changed row count")
    a = pd.to_datetime(m["avail_first"], errors="coerce")
    b = pd.to_datetime(m["avail_event"])
    delta = (b - a).dt.days
    return {
        "rows": int(len(m)),
        "identical_share": round(float((delta == 0).mean()), 4),
        "earlier_share": round(float((delta < 0).mean()), 4),
        "later_share": round(float((delta > 0).mean()), 4),
        "median_delta_days": float(delta.median()),
        "avail_first_fallback_share": round(
            float((m["notice_status"] != "ok").mean()), 4),
        "event_fallback_share": round(float(m["fallback"].mean()), 4),
        "note": "negative delta = the event face makes a row available EARLIER "
                "than the published face (a wrong-late stamp repaired); "
                "positive delta would mean the event face is MORE conservative",
    }


def cross_face_agreement(log=print):
    """How often do the three statements' own notice stamps agree?

    This is the diagnostic that identified the defect: on 2010+ periods income
    and balance agree, cashflow is ~1 year late; pre-2010 it inverts.
    """
    out = {"note": "per-period median absolute day-difference between the "
                   "faces' own first_notice stamps, over codes present in "
                   "both faces of the same period (in-window rows only)"}
    eras = {"pre_2010": [], "2010_plus": []}
    pairs = (("income", "balance"), ("income", "cashflow"),
             ("cashflow", "balance"))
    buckets = {f"{a}-{b}": {"pre_2010": [], "2010_plus": []} for a, b in pairs}
    usable = {f: {"pre_2010": [], "2010_plus": []} for f in FACES}
    for period in staged_periods("income"):
        pe = pd.Timestamp(iso_period(period))
        dl = pd.Timestamp(statutory_deadline(period))
        win_end = dl + pd.Timedelta(days=NOTICE_GRACE_DAYS)
        era = _era(iso_period(period))
        cache = {}
        for face in FACES:
            frame = _load_candidate(face, period)
            if len(frame) == 0:
                cache[face] = None
                continue
            raw = pd.to_datetime(frame.set_index("code")["first_notice"],
                                 errors="coerce")
            good = raw.where((raw >= pe) & (raw <= win_end))
            cache[face] = good
            if len(raw):
                usable[face][era].append(float(good.notna().mean()))
        for a, b in pairs:
            if cache.get(a) is None or cache.get(b) is None:
                continue
            j = pd.concat([cache[a].rename("a"), cache[b].rename("b")],
                          axis=1, join="inner").dropna()
            if len(j) < 50:
                continue
            buckets[f"{a}-{b}"][era].append(
                float((j["a"] - j["b"]).abs().dt.days.median()))
    for key, per_era in buckets.items():
        out[key] = {}
        for era, vals in per_era.items():
            out[key][era] = {
                "periods": len(vals),
                "median_abs_diff_days": (float(pd.Series(vals).median())
                                         if vals else None),
                "share_within_3d": (round(float((pd.Series(vals) <= 3).mean()), 4)
                                    if vals else None),
            }
    out["own_stamp_usable_share"] = {
        f: {era: {"periods": len(vals),
                  "median_usable_share": (round(float(pd.Series(vals).median()), 4)
                                          if vals else None)}
            for era, vals in per_era.items()}
        for f, per_era in usable.items()}
    log("cross-face agreement: " + json.dumps(
        {k: v for k, v in out.items() if k != "note"}, sort_keys=True))
    return out


def run(log=print):
    receipts = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "cross-statement filing-event availability face "
                 "(min in-window first_notice over income|cashflow|balance "
                 "per code/period, aggregated period by period)",
        "grace_days": NOTICE_GRACE_DAYS,
        "faces": {},
        "anchors": {},
        "cross_face_agreement": cross_face_agreement(log=log),
    }
    missing, incomplete = [], []
    os.makedirs(OUT_DIR, exist_ok=True)
    for face in FACES:
        if not os.path.exists(FACE_PATH[face]):
            missing.append(face)
            continue
        periods = staged_periods(face)
        frame = pd.read_parquet(FACE_PATH[face])
        event = build_face(face, frame)
        target = os.path.join(OUT_DIR, f"{face}_avail_event.parquet")
        event.to_parquet(target, index=False)
        entry = _agg(event, face)
        entry["out"] = os.path.relpath(target, ROOT)
        entry["eras"] = {
            era: _agg(event[event["period_end"].map(_era) == era], era)
            for era in ("pre_2010", "2010_plus")}
        cmp = _compare_with_avail_first(face, event)
        if cmp:
            entry["vs_avail_first"] = cmp
        # anchors: per-period lag for the documented sample periods
        anchors = {}
        for p in ANCHOR_PERIODS:
            iso = iso_period(p)
            sub = event[event["period_end"] == iso]
            if len(sub) == 0:
                continue
            ev = pd.to_datetime(sub["avail_event"])
            anchors[iso] = {
                "rows": int(len(sub)),
                "fallback_share": round(float(sub["fallback"].mean()), 4),
                "median_lag_days": float((ev - pd.Timestamp(iso)).dt.days.median()),
                "distinct_first": int(ev.nunique()),
            }
        if anchors:
            receipts["anchors"][face] = anchors
        entry["periods_staged"] = len(periods)
        receipts["faces"][face] = entry
        log(f"{face}: rows={entry['rows']} fallback={entry['fallback_share']} "
            f"median_lag={entry['median_lag_days']} "
            f"distinct_median={entry['distinct_first_median']}")
        if cmp:
            log(f"  vs avail_first: identical={cmp['identical_share']} "
                f"earlier={cmp['earlier_share']} "
                f"fallback {cmp['avail_first_fallback_share']} -> "
                f"{cmp['event_fallback_share']}")
    atomic_write_json(SUMMARY, receipts)
    log("wrote " + os.path.relpath(SUMMARY, ROOT))
    if missing:
        log(f"MISSING PANEL FACES: {missing}")
        return 3
    if incomplete:
        log(f"coverage incomplete: {incomplete}")
        return 3
    return 0


# ---------------------------------------------------------------- selftest
def selftest(log=print):
    checks = []

    def leg(name, fn):
        try:
            fn()
            checks.append((name, True, ""))
        except Exception as exc:                               # noqa: BLE001
            checks.append((name, False, f"{type(exc).__name__}: {exc}"))

    pe = "2025-03-31"
    dl = "2025-04-30"

    def leg_min_across_faces():
        # cashflow wrong-late (2026-04-25), income right (2025-04-19)
        cands = {"income": pd.Series({"000001": "2025-04-19"}),
                 "cashflow": pd.Series({"000001": "2026-04-25"}),
                 "balance": pd.Series({"000001": "2025-04-25"})}
        ev, src = filing_event_frame(["000001"], pe, dl, cands)
        assert ev.iloc[0] == pd.Timestamp("2025-04-19"), ev.iloc[0]
        assert src.iloc[0] == "income", src.iloc[0]

    def leg_out_of_window_rejected():
        # the +1y stamp must never be consumed
        cands = {"cashflow": pd.Series({"000001": "2026-04-25"})}
        ev, src = filing_event_frame(["000001"], pe, dl, cands)
        assert ev.iloc[0] == pd.Timestamp(dl), ev.iloc[0]
        assert src.iloc[0] is None

    def leg_pre_2010_other_way():
        # pre-2010 income is the late one, cashflow is right
        cands = {"income": pd.Series({"000002": "2006-04-26"}),
                 "cashflow": pd.Series({"000002": "2005-04-26"})}
        ev, src = filing_event_frame(["000002"], "2005-03-31", "2005-04-30",
                                     cands)
        assert ev.iloc[0] == pd.Timestamp("2005-04-26"), ev.iloc[0]
        assert src.iloc[0] == "cashflow"

    def leg_before_period_end_rejected():
        cands = {"income": pd.Series({"000003": "2025-03-01"})}
        ev, src = filing_event_frame(["000003"], pe, dl, cands)
        assert ev.iloc[0] == pd.Timestamp(dl), ev.iloc[0]

    def leg_gate_is_inclusive_of_deadline():
        cands = {"income": pd.Series({"000004": dl})}
        ev, src = filing_event_frame(["000004"], pe, dl, cands)
        assert ev.iloc[0] == pd.Timestamp(dl), ev.iloc[0]

    def leg_grace_day_boundary():
        # deadline + grace + 1 -> rejected; deadline + grace -> accepted
        cands = {"income": pd.Series({"000005": "2025-04-30"})}
        ev, _ = filing_event_frame(["000005"], pe, dl, cands, grace_days=0)
        assert ev.iloc[0] == pd.Timestamp(dl)
        cands2 = {"income": pd.Series({"000005": "2025-07-29"})}
        ev2, _ = filing_event_frame(["000005"], pe, dl, cands2, grace_days=90)
        assert ev2.iloc[0] == pd.Timestamp("2025-07-29"), ev2.iloc[0]

    def leg_unknown_code_falls_back():
        cands = {"income": pd.Series({"000001": "2025-04-19"})}
        ev, src = filing_event_frame(["999999"], pe, dl, cands)
        assert ev.iloc[0] == pd.Timestamp(dl)
        assert src.iloc[0] is None

    def leg_series_index_alignment():
        # a candidate for a DIFFERENT code must not leak onto this row
        cands = {"income": pd.Series({"600000": "2025-04-19"})}
        ev, src = filing_event_frame(["000001", "600000"], pe, dl, cands)
        assert ev.loc["000001"] == pd.Timestamp(dl)
        assert ev.loc["600000"] == pd.Timestamp("2025-04-19")

    def leg_never_earlier_than_period_end():
        cands = {"income": pd.Series({"000001": "2025-04-19"})}
        ev, _ = filing_event_frame(["000001"], pe, dl, cands)
        assert ev.iloc[0] >= pd.Timestamp(pe)

    for name, fn in [
        ("min across faces picks the in-window earliest", leg_min_across_faces),
        ("out-of-window (next-year) stamp rejected -> deadline", leg_out_of_window_rejected),
        ("pre-2010 era: cashflow supplies the good date", leg_pre_2010_other_way),
        ("date before period end rejected", leg_before_period_end_rejected),
        ("deadline boundary accepted", leg_gate_is_inclusive_of_deadline),
        ("grace boundary honoured both sides", leg_grace_day_boundary),
        ("unknown code falls back to deadline", leg_unknown_code_falls_back),
        ("candidate series align strictly by code", leg_series_index_alignment),
        ("event never precedes period end", leg_never_earlier_than_period_end),
    ]:
        leg(name, fn)

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    for name, ok, err in checks:
        log(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {err}" if err else ""))
    log(f"selftest {passed}/{total}")
    return 0 if passed == total else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print("usage: fund_avail_filing_event.py [run|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())