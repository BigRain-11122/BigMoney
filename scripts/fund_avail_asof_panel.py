"""Strict PIT as-of read path for the fundamental availability face (r1108 bm-a).

WHY: r1104-r1107 built and audited ``<face>_avail_event.parquet`` (per code /
period filing-event availability date + a ``fallback`` boolean), yet nothing in
the repo consumed it -- a data face with no read path. Any factor builder that
joins the statements on ``period_end`` instead of the availability date reads
reports before they were public (lookahead), and the r1105-r1107 audits measured
that this is not hypothetical: the deadline bound still covers 15%/11%/8% of the
income/cashflow/balance rows in aggregate and ~12.5% of the 2010+ income panel,
and that residual is concentrated in the high-roe tail (r1107).

WHAT THIS DELIVERS (product, not prose):
    * ``asof_slice(...)`` -- the join primitive: at date ``d``, per code, take
      the newest REPORT PERIOD whose availability date is already ``<= d``, and
      carry the availability date plus a confidence tier so consumers can weight
      the deadline-bound block instead of silently mixing it in (r1107 verdict:
      keep it, do not exclude).
    * a bounded as-of panel artifact (last ``PANEL_WINDOW`` month-ends) written
      to the gitignored data lane, so it is usable today;
    * ``results/fund_avail_asof_panel.json`` -- coverage / staleness / tier
      evidence over the full month-end grid, plus the NAIVE-vs-PIT row delta that
      quantifies how many rows a period_end join would have read too early.

DEFINITION (disclosed, one reading only):
    candidate set = rows with ``avail_event <= asof``; choice = max
    ``period_end`` in that set (a late stamp on an OLD period never rolls the
    panel back), ties broken by the earliest availability that revealed it. This
    is strictly lookahead-free by construction: the chosen row's own
    ``avail_event`` is <= asof, asserted on the emitted panel.

Outputs:
    data/fund_statement_export/pit_avail/asof_income_monthly.parquet (local)
    results/fund_avail_asof_panel.json
Subcommands: run | selftest
Exit codes: 0 ok, 2 machinery, 3 availability face missing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AVAIL_DIR = os.path.join(ROOT, "data", "fund_statement_export", "pit_avail")
INCOME = os.path.join(ROOT, "data", "fund_statement_export", "income_faces.parquet")
SUMMARY = os.path.join(ROOT, "results", "fund_avail_asof_panel.json")

ROE = "\u51c0\u8d44\u4ea7\u6536\u76ca\u7387"
NP = "\u51c0\u5229\u6da6-\u51c0\u5229\u6da6"
REV = "\u8425\u4e1a\u603b\u6536\u5165-\u8425\u4e1a\u603b\u6536\u5165"

GRID_START = "2010-01-31"
PANEL_WINDOW = 24
_TIER_EVENT = "filing_event"
_TIER_DEADLINE = "deadline_bound"

_DAY = np.int64(86400000000000)          # ns per day
_MULT = np.int64(10 ** 6)                # avail-day offset stride
_BIG = np.int64(10 ** 7)                 # period-day offset stride


# ------------------------------------------------------------------ helpers
def month_ends(start, end):
    """Ascending calendar month-ends in [start, end] (as-of dates)."""
    try:
        idx = pd.date_range(start, end, freq="ME")
    except ValueError:                                # pandas < 2.2
        idx = pd.date_range(start, end, freq="M")
    return [pd.Timestamp(d) for d in idx]


def _days(values):
    return np.asarray(values).astype("datetime64[D]").astype(np.int64)


def _prep(avail, values=None, value_cols=()):
    """Sort by (code, avail_event) and precompute the as-of pick index.

    The pick is two monotone lookups, no per-code python loop:
      * ``key``  = code_index * _MULT + avail_day  -> the last AVAILABLE row,
      * ``acc``  = running per-code maximum of code_index * _BIG + period_day
        (code_index dominates, so the accumulate resets at every block) and
        ``markers`` = positions where that maximum changed, i.e. the row that
        currently holds the newest known period for its code.
    """
    frame = avail.copy()
    frame["code"] = frame["code"].astype(str).str.zfill(6)
    frame["period_end"] = pd.to_datetime(frame["period_end"])
    frame["avail_event"] = pd.to_datetime(frame["avail_event"])
    if values is not None and len(value_cols):
        vals = values.copy()
        vals["code"] = vals["code"].astype(str).str.zfill(6)
        vals["period_end"] = pd.to_datetime(vals["period_end"])
        dup = int(vals.duplicated(["code", "period_end"]).sum())
        if dup:
            raise AssertionError(f"values: {dup} duplicated (code, period_end)")
        frame = frame.merge(vals[["code", "period_end", *value_cols]],
                            on=["code", "period_end"], how="left")
        if len(frame) != len(avail):
            raise AssertionError("values join changed the availability row count")
    frame = frame.sort_values(["code", "avail_event", "period_end"],
                              kind="stable").reset_index(drop=True)
    codes = frame["code"].to_numpy()
    uniq, starts = np.unique(codes, return_index=True)
    ends = np.append(starts[1:], len(codes))
    code_idx = np.repeat(np.arange(len(uniq), dtype=np.int64),
                         (ends - starts).astype(np.int64))
    avail_days = _days(frame["avail_event"].to_numpy())
    pe_days = _days(frame["period_end"].to_numpy())
    key = code_idx * _MULT + avail_days
    key2 = code_idx * _BIG + pe_days
    acc = np.maximum.accumulate(key2)
    change = np.empty(len(acc), dtype=bool)
    change[0] = True
    change[1:] = acc[1:] != acc[:-1]
    out = {
        "frame": frame,
        "codes": uniq,
        "starts": starts.astype(np.int64),
        "ends": ends.astype(np.int64),
        "avail_days": avail_days,
        "pe_days": pe_days,
        "key": key,
        "acc": acc,
        "markers": np.flatnonzero(change).astype(np.int64),
        "period_end": frame["period_end"].to_numpy(),
        "avail_event": frame["avail_event"].to_numpy(),
        "fallback": (frame["fallback"].to_numpy() if "fallback" in frame
                     else np.zeros(len(frame), dtype=bool)),
        "vals": {c: frame[c].to_numpy() for c in value_cols},
    }
    if not np.all(np.diff(out["key"]) >= 0):
        raise AssertionError("as-of keys are not monotone")
    # second index for the naive (period_end) join: same rows, sorted so that a
    # global searchsorted finds the newest period <= as-of per code.
    order_pe = np.argsort(key2, kind="stable")
    out["key_pe"] = key2[order_pe]
    out["avail_days_pe"] = avail_days[order_pe]
    code_pe = out["key_pe"] // _BIG
    out["starts_pe"] = np.flatnonzero(
        np.r_[True, code_pe[1:] != code_pe[:-1]]).astype(np.int64)
    if not np.all(np.diff(out["key_pe"]) >= 0):
        raise AssertionError("period keys are not monotone")
    return out


def asof_positions(prep, asof):
    """(available_last_pos, chosen_row_pos) per code at ``asof``; -1 = no data.

    ``available_last_pos`` is the last row inside each code block whose
    availability date is <= asof (basis for the naive-vs-PIT measurement);
    ``chosen_row_pos`` is the row holding the newest known period.
    """
    days = np.int64(int((pd.Timestamp(asof).to_datetime64()
                         .astype("datetime64[D]").astype(np.int64))))
    targets = np.arange(len(prep["codes"]), dtype=np.int64) * _MULT + days
    avail_pos = np.searchsorted(prep["key"], targets, side="right") - 1
    avail_pos = np.where(avail_pos >= prep["starts"], avail_pos, -1)
    safe = np.where(avail_pos < 0, 0, avail_pos)
    m = np.searchsorted(prep["markers"], safe, side="right") - 1
    chosen = np.where(avail_pos >= 0, prep["markers"][m], -1)
    return avail_pos, chosen.astype(np.int64)


def asof_slice(prep, asof, value_cols=()):
    """Newest-known-period row per code at ``asof`` as a DataFrame."""
    asof = pd.Timestamp(asof)
    _, chosen = asof_positions(prep, asof)
    hit = chosen[chosen >= 0]
    out = pd.DataFrame({"asof": asof, "code": prep["codes"][chosen >= 0],
                        "period_end": prep["period_end"][hit],
                        "avail_event": prep["avail_event"][hit],
                        "avail_tier": np.where(prep["fallback"][hit],
                                               _TIER_DEADLINE, _TIER_EVENT)})
    for col in value_cols:
        out[col] = prep["vals"][col][hit]
    return out.reset_index(drop=True)


def naive_rows(prep, asof):
    """Codes a period_end join would pick whose report was NOT yet public.

    The naive consumer takes max period_end <= asof per code; the count returned
    is how many of those picks carry ``avail_event > asof`` (i.e. lookahead).
    """
    days = np.int64(int((pd.Timestamp(asof).to_datetime64()
                         .astype("datetime64[D]").astype(np.int64))))
    targets = np.arange(len(prep["codes"]), dtype=np.int64) * _BIG + days
    pos = np.searchsorted(prep["key_pe"], targets, side="right") - 1
    valid = pos >= prep["starts_pe"]
    safe = np.where(valid, pos, 0)
    ahead = valid & (prep["avail_days_pe"][safe] > days)
    return int(np.count_nonzero(ahead))


def grid_evidence(prep, asofs):
    """Coverage / staleness / tier evidence over the full as-of grid."""
    rows = []
    for asof in asofs:
        _, chosen = asof_positions(prep, asof)
        ahead = naive_rows(prep, asof)
        hit = chosen[chosen >= 0]
        if len(hit) == 0:
            rows.append({"asof": asof.strftime("%Y-%m-%d"), "codes": 0,
                         "naive_codes_ahead": ahead})
            continue
        a_days = np.int64(int((asof.to_datetime64()
                              .astype("datetime64[D]").astype(np.int64))))
        staleness = a_days - prep["pe_days"][hit]
        rows.append({
            "asof": asof.strftime("%Y-%m-%d"),
            "codes": int(len(hit)),
            "deadline_bound_share": round(float(prep["fallback"][hit].mean()), 4),
            "median_staleness_days": float(np.median(staleness)),
            "naive_codes_ahead": ahead,
        })
    return rows


# --------------------------------------------------------------------- run
def run(log=print):
    avail_path = os.path.join(AVAIL_DIR, "income_avail_event.parquet")
    missing = [p for p in (avail_path, INCOME) if not os.path.exists(p)]
    if missing:
        log(f"MISSING INPUTS: {missing}")
        return 3
    avail = pd.read_parquet(avail_path)
    values = pd.read_parquet(INCOME)[["code", "period_end", ROE, NP, REV]]
    prep = _prep(avail, values, (ROE, NP, REV))

    last_avail = pd.Timestamp(prep["avail_event"].max())
    asofs = month_ends(GRID_START, last_avail)
    evidence = grid_evidence(prep, asofs)

    window = asofs[-PANEL_WINDOW:]
    parts = [asof_slice(prep, d, (ROE, NP, REV)) for d in window]
    panel = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    target = os.path.join(AVAIL_DIR, "asof_income_monthly.parquet")
    if len(panel):
        lookahead = (pd.to_datetime(panel["avail_event"])
                     > pd.to_datetime(panel["asof"]))
        if bool(lookahead.any()):
            raise AssertionError(f"{int(lookahead.sum())} panel rows read a "
                                 "report before it was available")
        os.makedirs(AVAIL_DIR, exist_ok=True)
        panel.to_parquet(target, index=False)

    latest = evidence[-1] if evidence else {}
    receipts = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "strict PIT as-of read path over the income filing-event "
                 "availability face (newest known report period per code)",
        "face": "income",
        "avail_rows": int(len(prep["frame"])),
        "avail_max_date": last_avail.strftime("%Y-%m-%d"),
        "grid": {"start": asofs[0].strftime("%Y-%m-%d"),
                 "end": asofs[-1].strftime("%Y-%m-%d"),
                 "points": len(asofs)},
        "definition": "candidates avail_event<=asof; choice max period_end; "
                      "tie -> earliest availability",
        "tier_meaning": {_TIER_EVENT: "a disclosure stamp landed inside the "
                                      "plausible window (cross-statement event "
                                      "or own notice)",
                         _TIER_DEADLINE: "statutory deadline bound (no usable "
                                         "stamp) -- usable but LOW confidence"},
        "latest": latest,
        "panel_artifact": {
            "path": "data/fund_statement_export/pit_avail/"
                    "asof_income_monthly.parquet",
            "rows": int(len(panel)),
            "asofs": len(window),
            "window_start": window[0].strftime("%Y-%m-%d") if window else None,
            "note": "gitignored data lane; regenerate with this script",
        },
        "grid_rows": evidence,
    }
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    tmp = SUMMARY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(receipts, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, SUMMARY)
    log(f"grid {len(asofs)} month-ends; latest asof {latest.get('asof')}: "
        f"codes={latest.get('codes')} "
        f"deadline_bound={latest.get('deadline_bound_share')} "
        f"median_staleness={latest.get('median_staleness_days')}d "
        f"naive_codes_ahead={latest.get('naive_codes_ahead')}")
    log(f"panel rows={len(panel)} asofs={len(window)} -> "
        f"{os.path.relpath(target, ROOT)}")
    log("wrote " + os.path.relpath(SUMMARY, ROOT))
    return 0


# ---------------------------------------------------------------- selftest
def selftest(log=print):
    checks = []

    def leg(name, fn):
        try:
            fn()
            checks.append((name, True, ""))
        except Exception as exc:                              # noqa: BLE001
            checks.append((name, False, f"{type(exc).__name__}: {exc}"))

    def _synthetic():
        # 000001: Q1 stamped 04-25, Q2 stamped 08-20
        # 000002: Q2 stamped EARLY (08-01), Q1 stamped LATE (08-15)
        # 600000: Q2 only, deadline bound
        avail = pd.DataFrame({
            "code": ["000001", "000001", "000002", "000002", "600000"],
            "period_end": ["2024-03-31", "2024-06-30", "2024-06-30",
                           "2024-03-31", "2024-06-30"],
            "avail_event": ["2024-04-25", "2024-08-20", "2024-08-01",
                            "2024-08-15", "2024-08-20"],
            "fallback": [False, False, False, False, True],
        })
        values = pd.DataFrame({
            "code": ["000001", "000001", "000002", "000002", "600000"],
            "period_end": ["2024-03-31", "2024-06-30", "2024-06-30",
                           "2024-03-31", "2024-06-30"],
            "roe": [10.0, 11.0, 22.0, 21.0, 5.0],
        })
        return _prep(avail, values, ("roe",))

    def leg_picks_newest_period():
        s = asof_slice(_synthetic(), "2024-09-30", ("roe",))
        row = s[s["code"] == "000001"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2024-06-30"), row["period_end"]
        assert row["roe"] == 11.0, row["roe"]

    def leg_availability_decides():
        s = asof_slice(_synthetic(), "2024-06-01", ("roe",))
        row = s[s["code"] == "000001"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2024-03-31"), row["period_end"]
        assert row["avail_event"] == pd.Timestamp("2024-04-25")

    def leg_flips_exactly_on_availability():
        prep = _synthetic()
        before = asof_slice(prep, "2024-08-19", ("roe",))
        on = asof_slice(prep, "2024-08-20", ("roe",))
        assert before[before["code"] == "000001"].iloc[0]["period_end"] == \
            pd.Timestamp("2024-03-31")
        assert on[on["code"] == "000001"].iloc[0]["period_end"] == \
            pd.Timestamp("2024-06-30")

    def leg_nothing_available_yet():
        s = asof_slice(_synthetic(), "2024-04-01", ("roe",))
        assert len(s) == 0, len(s)

    def leg_late_old_stamp_never_rolls_back():
        # 000002 Q1 stamp arrives 08-15, AFTER Q2 (08-01): the panel must stay
        # on Q2 rather than regress to the older period.
        s = asof_slice(_synthetic(), "2024-08-16", ("roe",))
        row = s[s["code"] == "000002"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2024-06-30"), row["period_end"]
        assert row["roe"] == 22.0, row["roe"]

    def leg_tier_column_marks_deadline():
        s = asof_slice(_synthetic(), "2024-09-30", ("roe",))
        assert s[s["code"] == "600000"].iloc[0]["avail_tier"] == _TIER_DEADLINE
        assert s[s["code"] == "000001"].iloc[0]["avail_tier"] == _TIER_EVENT

    def leg_naive_join_reads_ahead():
        prep = _synthetic()
        # at 2024-08-19 the naive join takes Q2 for 000001 and 600000
        # (period_end <= asof) although their stamp is 08-20 -> two codes read
        # before publication; on the stamp date the count drops to zero.
        assert naive_rows(prep, "2024-08-19") == 2, naive_rows(prep, "2024-08-19")
        assert naive_rows(prep, "2024-08-20") == 0, naive_rows(prep, "2024-08-20")
        # before any Q2 period exists the naive join still reads 000002's Q1
        # ahead of its 08-15 stamp -> exactly one code, not the whole panel.
        assert naive_rows(prep, "2024-06-01") == 1, naive_rows(prep, "2024-06-01")

    def leg_values_do_not_leak_across_periods():
        s = asof_slice(_synthetic(), "2024-09-30", ("roe",))
        q1 = s[(s["code"] == "000001") & (s["period_end"] == "2024-03-31")]
        assert len(q1) == 0
        assert s[s["code"] == "000001"].iloc[0]["roe"] == 11.0

    def leg_month_ends_ascending_unique():
        idx = month_ends("2024-01-31", "2024-06-30")
        assert idx == [pd.Timestamp(d) for d in
                       ("2024-01-31", "2024-02-29", "2024-03-31",
                        "2024-04-30", "2024-05-31", "2024-06-30")], idx

    def leg_duplicate_value_rows_rejected():
        avail = pd.DataFrame({"code": ["000001"], "period_end": ["2024-03-31"],
                              "avail_event": ["2024-04-25"], "fallback": [False]})
        dup = pd.DataFrame({"code": ["000001", "000001"],
                            "period_end": ["2024-03-31", "2024-03-31"],
                            "roe": [1.0, 2.0]})
        try:
            _prep(avail, dup, ("roe",))
        except AssertionError:
            return
        raise AssertionError("duplicate value rows were accepted")

    for name, fn in [
        ("newest known period wins", leg_picks_newest_period),
        ("availability, not period_end, decides", leg_availability_decides),
        ("panel flips exactly on the availability date", leg_flips_exactly_on_availability),
        ("codes with nothing available yield no row", leg_nothing_available_yet),
        ("a late stamp on an old period never rolls the panel back",
         leg_late_old_stamp_never_rolls_back),
        ("tier column separates event from deadline bound", leg_tier_column_marks_deadline),
        ("naive period_end join reads ahead of availability", leg_naive_join_reads_ahead),
        ("values never attach across periods", leg_values_do_not_leak_across_periods),
        ("month-end grid is ascending and unique", leg_month_ends_ascending_unique),
        ("duplicate value rows are rejected", leg_duplicate_value_rows_rejected),
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
    print("usage: fund_avail_asof_panel.py [run|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())