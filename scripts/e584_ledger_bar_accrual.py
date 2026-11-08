# -*- coding: utf-8 -*-
"""E584 -- does the forward ledger accrue on the bar each of its rows names?

The forward ledger (``results/etf_book_forward/LEDGER.json``) is the artefact of this book that
accrues money in public: every row carries a ``bar``, a ``nav`` and a ``carry``.  E583/E585 priced
the *tickets* against the bar their file names; this study asks the same of the ledger's rows:

  1. is every row a distinct bar, or is a bar published more than once?
  2. does the carry on a row pay the calendar gap that row closes -- Friday's 1-day contract
     earning three days over the weekend -- or one day's interest on every row?

Per row it publishes:

  bar / prev_distinct_bar / gap_days      the calendar gap the row closes
  cash_at_start                          the cash the carry is charged on
  published_carry                        what the row books
  reference_rate_pct                     GC001 close on the previous distinct bar (the ladder's
                                         short rung; a reference, not the ladder's own blend)
  implied_accrual_days                   published_carry / (cash * rate/100/365) at that reference
  class                                  the row's shape (see CLASSES)

and the record-level block:

  rows_published / distinct_bars / duplicated_bars / duplicated_dates
  carry_sum_over_rows / carry_sum_over_distinct_bars / duplicating_extra_carry
  capital_cny / duplicating_extra_cny     the duplicate's carry priced in CNY on the seed capital
  significance_bar_count_published        what the ledger's significance block was fed
  significance_bar_count_distinct         how many bars the record actually holds
  bar_count_inflation_pct

Honest limits, published with the face rather than hidden:

  * ``implied_accrual_days`` is measured at the GC001 reference rate.  The engine's cash leg is
    ``etf_book_cash_ladder``'s three-rung ladder (GC007/GC014/GC028, commission charged), which
    apportions a maturing contract's interest across the bars it spans; that split cannot be
    rebuilt from the short rung alone, so ``rows_reproducing_the_ladder`` is published as its own
    reading and drives no verdict.
  * a negative carry is classed as such, not as a defect: GC001 can quote either side of zero.

Read-only over the ledger and the repo panel.  This study writes no ledger row; the write-side
dedupe is a guarded fix in ``etf_book_forward.py`` and a repair of the published file is done by
re-running that tool, never by hand-editing the JSON.

  python scripts/e584_ledger_bar_accrual.py build
  python scripts/e584_ledger_bar_accrual.py check
  python scripts/e584_ledger_bar_accrual.py verify
  python scripts/e584_ledger_bar_accrual.py selftest

Output: results/state_tilt/LEDGERBARS-<ledger cutoff>.json + ledgerbars_latest.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
LEDGER_PATH = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
REPO_PATH = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

ONE_DAY_TOL = 0.25     # a one-day charge implies ~1 day at the reference rate, never 1.5

C_FIRST = "first_row_no_accrual"
C_GAP = "pays_the_calendar_gap"
C_UNDER = "pays_one_day_on_a_multi_day_gap"
C_NEG = "negative_carry"
C_NO_RATE = "prev_bar_has_no_repo_quote"
C_DUP = "duplicate_row"
CLASSES = (C_FIRST, C_GAP, C_UNDER, C_NEG, C_NO_RATE, C_DUP)

V_DUP = "the_rows_accrue_on_the_bar_they_name_but_the_record_publishes_bars_twice"
V_UNDER = "the_record_charges_one_day_on_gaps_that_span_more"
V_NEG = "the_rows_pay_the_gap_and_one_row_carries_a_negative_rate"
V_CLEAN = "every_row_accrues_the_gap_it_closes_and_no_bar_is_published_twice"
V_EMPTY = "no_accrued_rows_to_measure"


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_rates(path=REPO_PATH):
    import pandas as pd
    df = pd.read_csv(path)
    d = pd.to_datetime(df["date"])
    s = pd.Series(df["close"].astype(float).to_numpy(), index=d)
    return s[~s.index.duplicated(keep="last")].sort_index()


def rate_on(rates, bar):
    import pandas as pd
    if bar is None:
        return None
    try:
        ts = pd.Timestamp(bar)
    except Exception:
        return None
    if ts not in rates.index:
        return None
    v = rates.get(ts)
    try:
        if v != v:
            return None
    except Exception:
        return None
    return round(float(v), 4)


def classify(row):
    """The one class a row carries; every number the class names is on the row."""
    if row["is_duplicate"]:
        return C_DUP
    if row["prev_distinct_bar"] is None:
        return C_FIRST
    if (row["published_carry"] or 0.0) < 0.0:
        return C_NEG
    if row["reference_rate_pct"] is None:
        return C_NO_RATE
    if row["implied_accrual_days"] is None:
        return C_NO_RATE
    if row["gap_days"] > 1 and row["implied_accrual_days"] <= 1.0 + ONE_DAY_TOL:
        return C_UNDER
    return C_GAP


def analyse(bars, rates):
    import pandas as pd
    rows, seen = [], {}
    for i, b in enumerate(bars):
        bar = b.get("bar")
        prev = rows[-1]["bar"] if rows else None
        gap = None
        if prev is not None:
            gap = int((pd.Timestamp(bar) - pd.Timestamp(prev)).days)
        cash_start = rows[-1]["cash"] if rows and rows[-1]["cash"] is not None else b.get("cash")
        carry = b.get("carry")
        rate = rate_on(rates, prev) if prev is not None else None
        implied = None
        if (carry is not None and cash_start and rate is not None and rate > 0.0
                and abs(float(carry)) > 1e-15):
            implied = float(carry) / (float(cash_start) * float(rate) / 100.0 / 365.0)
        row = {
            "index": i,
            "bar": bar,
            "prev_distinct_bar": prev,
            "gap_days": gap,
            "cash": b.get("cash"),
            "cash_at_start": cash_start,
            "published_carry": carry,
            "nav": b.get("nav"),
            "reference_rate_pct": rate,
            "implied_accrual_days": None if implied is None else round(implied, 4),
            "is_duplicate": bar in seen,
            "first_seen_index": seen.get(bar),
        }
        row["class"] = classify(row)
        if bar not in seen:
            seen[bar] = i
        rows.append(row)
    return rows


def ladder_check(bars):
    """Compare each row's carry with the engine's own ladder, as a separate published reading."""
    import pandas as pd
    try:
        from scripts import etf_book_forward as F
        dates = [pd.Timestamp(b["bar"]) for b in bars]
        ret, note = F.build_carry(dates)
    except Exception as exc:                                    # pragma: no cover - env dependent
        return {"rows_reproducing_the_ladder": None, "ladder_note": "unreadable: %s" % exc}
    if ret is None or len(ret) == 0:
        return {"rows_reproducing_the_ladder": None, "ladder_note": note}
    n, prev_cash = 0, None
    for b, ts in zip(bars, dates):
        frac = ret.get(ts)
        cash = prev_cash if prev_cash is not None else b.get("cash")
        prev_cash = b.get("cash")
        if frac is None or cash is None or b.get("carry") is None:
            continue
        if abs(float(b["carry"]) - float(cash) * float(frac)) <= 1e-9:
            n += 1
    return {"rows_reproducing_the_ladder": n, "ladder_note": note,
            "ladder_rows_compared": len(bars)}


def summarise(rows, led, ladder=None):
    dup = [r for r in rows if r["is_duplicate"]]
    distinct = [r for r in rows if not r["is_duplicate"]]
    by_class = {c: 0 for c in CLASSES}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    capital = (led.get("seed") or {}).get("capital_cny")
    sum_rows = sum(float(r["published_carry"] or 0.0) for r in rows)
    sum_distinct = sum(float(r["published_carry"] or 0.0) for r in distinct)
    extra = sum_rows - sum_distinct
    sig = ((led.get("benchmark") or {}).get("significance") or {})
    published_n = sig.get("n_bars") or sig.get("bars") or len(rows)
    distinct_n = len({r["bar"] for r in rows})
    out = {
        "rows_published": len(rows),
        "distinct_bars": distinct_n,
        "duplicated_bars": len(dup),
        "duplicated_dates": sorted({r["bar"] for r in dup}),
        "published_row_carry_sum": round(sum_rows, 12),
        "distinct_row_carry_sum": round(sum_distinct, 12),
        "duplicating_extra_carry": round(extra, 12),
        "capital_cny": capital,
        "duplicating_extra_cny": None if capital is None else round(extra * float(capital), 2),
        "significance_bar_count_published": published_n,
        "significance_bar_count_distinct": distinct_n,
        "bar_count_inflation_pct": None if not distinct_n else
        round((float(published_n) / distinct_n - 1.0) * 100.0, 2),
        "multi_day_gaps": sum(1 for r in distinct if (r["gap_days"] or 0) > 1),
        "rows_that_pay_the_calendar_gap": by_class.get(C_GAP, 0),
        "rows_that_pay_one_day_on_a_multi_day_gap": by_class.get(C_UNDER, 0),
        "rows_with_negative_carry": by_class.get(C_NEG, 0),
        "rows_without_a_reference_rate": by_class.get(C_NO_RATE, 0),
        "by_class": by_class,
    }
    if ladder:
        out.update(ladder)
    return out


def verdict_of(s):
    if not s["rows_published"]:
        return V_EMPTY
    if s["duplicated_bars"]:
        return V_DUP
    if s["rows_that_pay_one_day_on_a_multi_day_gap"]:
        return V_UNDER
    if s["rows_with_negative_carry"]:
        return V_NEG
    return V_CLEAN


def _verdict_line(s):
    if not s["rows_published"]:
        return "no accrued rows on disk"
    return ("%d rows / %d distinct bars -- %d duplicated (%s); %d rows classed as the calendar gap "
            "(%d of them multi-day); %d rows have no repo reference; carry sums %.3e over rows vs "
            "%.3e over distinct bars; significance was fed %s bars where %d exist (%+.2f%%)" % (
                s["rows_published"], s["distinct_bars"], s["duplicated_bars"],
                ",".join(s["duplicated_dates"]) or "none",
                s["rows_that_pay_the_calendar_gap"], s["multi_day_gaps"],
                s["rows_without_a_reference_rate"],
                s["published_row_carry_sum"], s["distinct_row_carry_sum"],
                s["significance_bar_count_published"], s["significance_bar_count_distinct"],
                s["bar_count_inflation_pct"] or 0.0))


def face_problems(face):
    problems = []
    rows, s = face.get("rows") or [], face.get("summary") or {}
    if len(rows) != s.get("rows_published"):
        problems.append("summary.rows_published does not match the rows")
    if len({r.get("bar") for r in rows}) != s.get("distinct_bars"):
        problems.append("summary.distinct_bars does not re-derive")
    if sum(1 for r in rows if r.get("is_duplicate")) != s.get("duplicated_bars"):
        problems.append("summary.duplicated_bars does not re-derive")
    counts = {c: 0 for c in CLASSES}
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("row %s carries an undefined class" % r.get("index"))
            continue
        counts[r["class"]] += 1
        if classify(r) != r.get("class"):
            problems.append("row %s class does not re-derive from its own numbers"
                            % r.get("index"))
    if counts[C_GAP] != s.get("rows_that_pay_the_calendar_gap"):
        problems.append("summary.rows_that_pay_the_calendar_gap does not re-derive")
    if counts[C_UNDER] != s.get("rows_that_pay_one_day_on_a_multi_day_gap"):
        problems.append("summary under-accrual count does not re-derive")
    if counts[C_NEG] != s.get("rows_with_negative_carry"):
        problems.append("summary negative-carry count does not re-derive")
    carry_rows = sum(float(r.get("published_carry") or 0.0) for r in rows)
    if abs(carry_rows - float(s.get("published_row_carry_sum") or 0.0)) > 1e-9:
        problems.append("summary.published_row_carry_sum does not re-derive")
    distinct = [r for r in rows if not r.get("is_duplicate")]
    carry_d = sum(float(r.get("published_carry") or 0.0) for r in distinct)
    if abs(carry_d - float(s.get("distinct_row_carry_sum") or 0.0)) > 1e-9:
        problems.append("summary.distinct_row_carry_sum does not re-derive")
    if s.get("capital_cny") is not None:
        want = (carry_rows - carry_d) * float(s["capital_cny"])
        if abs(want - float(s.get("duplicating_extra_cny") or 0.0)) > 0.02:
            problems.append("summary.duplicating_extra_cny does not re-derive")
    if verdict_of(s) != face.get("verdict"):
        problems.append("verdict does not re-derive from the summary")
    return problems


def build(write=True):
    led = _read_json(LEDGER_PATH)
    rates = load_rates()
    bars = led.get("bars") or []
    rows = analyse(bars, rates)
    stairs = ladder_check(bars)
    s = summarise(rows, led, stairs)
    cutoff = (bars[-1].get("bar") if bars else None) or "unknown"
    face = {
        "study": "E584",
        "question": "does the forward ledger accrue on the bar each row names, and is every "
                    "published row a distinct bar",
        "ledger": os.path.relpath(LEDGER_PATH, ROOT).replace("\\", "/"),
        "evidence_cutoff": cutoff,
        "verdict": verdict_of(s),
        "verdict_line": _verdict_line(s),
        "summary": s,
        "rows": rows,
        "source_note": "rows re-derived live from the ledger file; reference rate = GC001 close "
                       "on the previous distinct bar; implied_accrual_days is measured at that "
                       "reference and does not reconstruct the ladder's own split",
    }
    probs = face_problems(face)
    if probs:
        raise SystemExit("FACE GUARD FAILED: %s" % probs)
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, indent=1, ensure_ascii=False)
        for name in ("LEDGERBARS-%s.json" % cutoff, "ledgerbars_latest.json"):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
    return face


def _cutoff_on_disk():
    led = _read_json(LEDGER_PATH)
    bars = led.get("bars") or [{}]
    return bars[-1].get("bar") or "unknown"


def check():
    for name in ("LEDGERBARS-%s.json" % _cutoff_on_disk(), "ledgerbars_latest.json"):
        p = os.path.join(OUTDIR, name)
        if not os.path.exists(p):
            print("MISSING %s" % name)
            return 1
        probs = face_problems(_read_json(p))
        print(("OK %s" % name) if not probs else ("PROBLEMS %s: %s" % (name, probs)))
        if probs:
            return 1
    return 0


def verify():
    """Re-derive the published face from the ledger without writing anything."""
    face = build(write=False)
    on_disk = _read_json(os.path.join(OUTDIR, "ledgerbars_latest.json"))
    a = [(r["bar"], r["class"], r["implied_accrual_days"], r["published_carry"])
         for r in face["rows"]]
    b = [(r["bar"], r["class"], r["implied_accrual_days"], r["published_carry"])
         for r in on_disk["rows"]]
    if a != b:
        print("VERIFY FAILED: rows do not re-derive")
        return 1
    if face["verdict"] != on_disk["verdict"]:
        print("VERIFY FAILED: verdict drifted")
        return 1
    print("VERIFIED %d rows re-derived, verdict=%s" % (len(a), face["verdict"]))
    return 0


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #

def selftest():
    import pandas as pd
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "got %r want %r" % (got, want)))

    def near(name, got, want, tol=1e-9):
        good = got is not None and want is not None and abs(float(got) - float(want)) <= tol
        ok.append((name, good, "got %r want %r" % (got, want)))

    rates = pd.Series([2.0, 2.0, 1.0],
                      index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"]))
    cash = 0.5
    fri, mon = "2020-01-03", "2020-01-06"
    three_days = cash * 2.0 / 100.0 * 3 / 365.0
    one_day = cash * 2.0 / 100.0 * 1 / 365.0
    bars = [{"bar": fri, "nav": 1.0, "cash": cash, "carry": 0.0},
            {"bar": mon, "nav": 1.001, "cash": cash, "carry": three_days}]

    rows = analyse(bars, rates)
    eq("the first row accrues nothing", rows[0]["class"], C_FIRST)
    eq("the three-day gap is measured in calendar days", rows[1]["gap_days"], 3)
    eq("a Friday contract paying three days is classed as the calendar gap",
       rows[1]["class"], C_GAP)
    near("the implied accrual days equal the gap", rows[1]["implied_accrual_days"], 3.0, 1e-4)
    near("the cash at the start of a row is the previous row's cash",
         rows[1]["cash_at_start"], cash)

    rows2 = analyse([bars[0], dict(bars[1], carry=one_day)], rates)
    eq("a one-day charge on a weekend gap is named as such", rows2[1]["class"], C_UNDER)
    near("the one-day charge implies one day", rows2[1]["implied_accrual_days"], 1.0, 1e-4)
    eq("the under-accrual population drives its own verdict",
       verdict_of(summarise(rows2, {"seed": {"capital_cny": 1.0}, "bars": []})), V_UNDER)

    bars3 = [bars[0], bars[1], dict(bars[1])]
    rows3 = analyse(bars3, rates)
    eq("a bar published twice is marked duplicate", rows3[2]["is_duplicate"], True)
    eq("the duplicate names where it was first seen", rows3[2]["first_seen_index"], 1)
    eq("the duplicate's class is duplicate_row", rows3[2]["class"], C_DUP)

    eq("a negative carry is classed rather than treated as an arithmetic failure",
       analyse([bars[0], dict(bars[1], carry=-1e-9)], rates)[1]["class"], C_NEG)
    eq("a gap with no repo quote on its start bar is named",
       analyse(bars, pd.Series([2.0], index=pd.to_datetime(["2020-01-06"])))[1]["class"],
       C_NO_RATE)
    two_day = [bars[0], dict(bars[1], bar="2020-01-06",
                             carry=cash * 2.0 / 100.0 * 2 / 365.0)]
    eq("a two-day gap paying two days is classed as the gap",
       analyse(two_day, rates)[1]["class"], C_GAP)

    led = {"seed": {"capital_cny": 1000000.0}, "bars": bars3,
           "benchmark": {"significance": {"n_bars": 3}}}
    s = summarise(rows3, led)
    eq("summary counts the published rows", s["rows_published"], 3)
    eq("summary counts the distinct bars", s["distinct_bars"], 2)
    eq("summary counts the duplicated rows", s["duplicated_bars"], 1)
    eq("the duplicated dates are published", s["duplicated_dates"], [mon])
    near("the extra carry is the duplicated row's carry", s["duplicating_extra_carry"],
         three_days)
    near("the extra carry priced on capital", s["duplicating_extra_cny"],
         round(three_days * 1000000.0, 2), 0.02)
    eq("the bar count inflation is measured against the distinct count",
       s["bar_count_inflation_pct"], 50.0)
    eq("the verdict names the double publication", verdict_of(s), V_DUP)
    eq("a clean population takes the clean verdict",
       verdict_of(summarise(rows, led)), V_CLEAN)

    face = {"study": "E584", "verdict": verdict_of(s), "summary": s, "rows": rows3}
    eq("the guard passes a face it built itself", face_problems(face), [])

    doctored = json.loads(json.dumps(face))
    doctored["rows"][2]["class"] = C_GAP
    ok.append(("the guard refuses a duplicate relabelled as an accruing row",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][1]["implied_accrual_days"] = 1.0
    ok.append(("the guard refuses a gap row whose implied days were rewritten",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["distinct_bars"] = 3
    ok.append(("the guard refuses a distinct count that does not re-derive",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["duplicating_extra_cny"] = 999.0
    ok.append(("the guard refuses an extra-cny that does not re-derive",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["verdict"] = V_CLEAN
    ok.append(("the guard refuses a verdict the summary does not support",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][0]["class"] = "a_class_this_study_does_not_define"
    ok.append(("the guard refuses a class the study does not define",
               bool(face_problems(doctored)), "no problem reported"))

    bad = [n for n, good, msg in ok if not good]
    print("%s selftest %d/%d" % ("PASS" if not bad else "FAIL", len(ok) - len(bad), len(ok)))
    for n, good, msg in ok:
        if not good:
            print("  FAIL %s: %s" % (n, msg))
    return 0 if not bad else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd in ("build", "run"):
        face = build(write=True)
        print("BUILT %s | %s" % (face["verdict"], face["verdict_line"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())