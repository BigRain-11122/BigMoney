# -*- coding: utf-8 -*-
"""E593 -- does the ticket's advertised cash yield survive its own 252-bar convention?

E589 (r1616 bm-b) made ``results/etf_book_order/TICKET-<bar>.json`` publish the window its cash
leg actually averages.  E592 (r1619 bm-b) then found the forward ledger's ladder carry runs at
~1.88%/yr on the same grid while the ticket advertises 2.079%/yr with ``bars_per_year=252``, and
the ladder module's own docstring warns that a 252-bar model of a 365-day market goes wrong.  So
the ticket's headline may be a convention artefact rather than a rate -- that is what this study
measures.

The arithmetic the ticket already ships (``scripts/etf_book_order.py::cash_leg_block``) is

    mean_accrual_ann_pct = mean(repo_daily_cash) * 252 * 100

and ``etf_phase_beta_window.repo_daily_cash`` accrues **calendar days at /365** per bar step
(``rate/100 * gap_days/365``).  So the printed number multiplies a per-bar mean that already
carries the average calendar gap by a bar count, and the bar count is not the window's own
calendar frequency.  This study recomputes the same window three ways:

  (a) printed_method       mean per-bar accrual x 252            -- reproduces the ticket headline
  (b) calendar_days_365    total accrual / (calendar_days / 365)  -- the ladder module's pricing
  (c) per_bar_both_sides   the two implied per-bar accruals, one ratio

and prices (a) - (b) on the ticket's own cash.  Read-only: no ticket, ledger, panel or state face
is written.

Honest limits:

  * the window is whatever the newest ticket prints (2020-01-02..2026-11-06, 1,658 bars); a
    different ticket bar would move both numbers and the study says so by publishing the window;
  * GC001 has 7 bar steps with no quote on this window; those accrue zero and are counted, exactly
    as the ticket's own writer counts them -- this study does not repair the panel;
  * (b) is the ladder module's convention, not a claim that GC001 rolls on calendar days at a
    constant rate; it answers "what annual rate does this accrual stream correspond to".

  python scripts/e593_cash_convention.py build
  python scripts/e593_cash_convention.py check
  python scripts/e593_cash_convention.py verify
  python scripts/e593_cash_convention.py selftest

Output: results/etf_book_order/CASHCONVENTION.json
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scripts import etf_phase_beta_window as BW          # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_PATH = os.path.join(OUTDIR, "CASHCONVENTION.json")
TICKET_GLOB = os.path.join(OUTDIR, "TICKET-*.json")
CAL_PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")
REPO_PANEL = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

TICKET_BARS_PER_YEAR = 252
CALENDAR_DAYS_PER_YEAR = 365.0
# the ticket prints the headline to 3 decimals; reproducing it to half a unit of the last digit
PRINT_TOL_PP = 0.0005

V_SURVIVES = "the_printed_cash_yield_is_its_own_method_recomputed_and_overstates_the_calendar_rate"
V_DOES_NOT_SURVIVE = "the_printed_cash_yield_does_not_reproduce_from_the_window_it_names"
V_EMPTY = "no_ticket_on_disk_to_measure"


# --------------------------------------------------------------------------- pure helpers
def window_index(start, end, path=CAL_PANEL):
    """The trading calendar the ticket's window names, read off the pricing panel."""
    df = pd.read_csv(path, usecols=["date"])
    d = pd.to_datetime(df["date"])
    m = (d >= pd.Timestamp(start)) & (d <= pd.Timestamp(end))
    return pd.DatetimeIndex(sorted(set(d[m])))


def annual_from_printed_method(mean_per_bar, bars_per_year=TICKET_BARS_PER_YEAR):
    """The ticket's own arithmetic: a per-bar mean times a bar count."""
    if mean_per_bar is None:
        return None
    return float(mean_per_bar) * float(bars_per_year) * 100.0


def annual_from_calendar_days(total_accrual, calendar_days,
                              days_per_year=CALENDAR_DAYS_PER_YEAR):
    """The ladder module's convention: total accrual over calendar-years in the window."""
    if total_accrual is None or not calendar_days:
        return None
    return float(total_accrual) / (float(calendar_days) / float(days_per_year)) * 100.0


def implied_bars_per_year(n_bars, calendar_days):
    """How many of the window's own bars a calendar year holds (the honest bar count)."""
    if not n_bars or not calendar_days:
        return None
    return float(n_bars) * CALENDAR_DAYS_PER_YEAR / float(calendar_days)


def convention_ratio(n_bars, calendar_days):
    """printed / calendar -- an identity, so it must re-derive from the two windows."""
    bp = implied_bars_per_year(n_bars, calendar_days)
    if bp is None:
        return None
    return float(TICKET_BARS_PER_YEAR) / bp


def cny_gap(cash, printed_pct, calendar_pct):
    """What the convention difference is worth per year on the ticket's own cash."""
    if cash is None or printed_pct is None or calendar_pct is None:
        return None
    return float(cash) * (float(printed_pct) - float(calendar_pct)) / 100.0


def newest_ticket(paths):
    """The ticket whose ``pricing_bar`` is latest -- never by filename, the bar is the fact."""
    best, best_bar = None, None
    for p in paths:
        try:
            with io.open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception:
            continue
        bar = doc.get("pricing_bar") or doc.get("feed_status", {}).get("ticket_bar")
        cash = (doc.get("cash_leg") or {})
        if bar is None or not cash.get("window_bars"):
            continue
        if best_bar is None or str(bar) > str(best_bar):
            best, best_bar = (p, doc), bar
    return best


# --------------------------------------------------------------------------- build
def build(write=True):
    paths = sorted(glob.glob(TICKET_GLOB))
    picked = newest_ticket(paths)
    if not picked:
        face = {"study": "E593_cash_convention", "generated_by": "scripts/e593_cash_convention.py",
                "verdict": V_EMPTY, "tickets_seen": len(paths)}
        if write:
            write_face(face)
        return face
    path, doc = picked
    cash_blk = doc.get("cash_leg") or {}
    start = cash_blk.get("window_start")
    end = cash_blk.get("window_end")

    idx = window_index(start, end)
    rates = BW.load_repo_rates(REPO_PANEL)
    accrual, missing = BW.repo_daily_cash(idx, rates)
    n_bars = int(len(idx))
    cal_days = int((idx[-1] - idx[0]).days) if n_bars else 0
    mean_bar = float(accrual.mean()) if n_bars else None
    total = float(accrual.sum()) if n_bars else None

    printed = annual_from_printed_method(mean_bar)
    calendar = annual_from_calendar_days(total, cal_days)
    bpy = implied_bars_per_year(n_bars, cal_days)
    ratio = convention_ratio(n_bars, cal_days)
    quoted = cash_blk.get("mean_accrual_ann_pct")

    ticket_cash = (doc.get("ticket") or {}).get("cash_amount")
    issued_cash = (doc.get("ticket_as_issued") or {}).get("cash_amount")
    gap_pp = (printed - calendar) if (printed is not None and calendar is not None) else None

    face = {
        "study": "E593_cash_convention",
        "generated_by": "scripts/e593_cash_convention.py",
        "card": "E593-WHETHER-THE-TICKETS-ADVERTISED-CASH-YIELD-SURVIVES-ITS-OWN-252-CONVENTION",
        "ticket_path": os.path.relpath(path, ROOT).replace("\\", "/"),
        "ticket_bar": doc.get("pricing_bar"),
        "evidence_cutoff": doc.get("pricing_bar"),
        "window": {
            "start": start, "end": end,
            "bars": n_bars, "calendar_days": cal_days,
            "printed_bars": cash_blk.get("window_bars"),
            "printed_calendar_days": cash_blk.get("window_calendar_days"),
            "bars_match_the_printed_window": cash_blk.get("window_bars") == n_bars,
            "calendar_days_match_the_printed_window":
                cash_blk.get("window_calendar_days") == cal_days,
            "missing_bar_steps": int(missing),
            "printed_missing_bar_steps": cash_blk.get("missing_bar_steps"),
            "implied_bars_per_calendar_year": None if bpy is None else round(bpy, 4),
        },
        "printed_method": {
            "label": "mean bar-to-bar accrual x %d" % TICKET_BARS_PER_YEAR,
            "bars_per_year": TICKET_BARS_PER_YEAR,
            "mean_bar_accrual_frac": None if mean_bar is None else mean_bar,
            "annual_pct": None if printed is None else round(printed, 6),
            "quoted_on_ticket_pct": quoted,
            "reproduces_the_quoted_figure": (
                None if (printed is None or quoted is None)
                else abs(printed - float(quoted)) <= PRINT_TOL_PP),
            "gap_vs_quoted_pp": (
                None if (printed is None or quoted is None) else round(printed - float(quoted), 6)),
        },
        "calendar_days_365": {
            "label": "total accrual / (calendar_days / 365)",
            "days_per_year": CALENDAR_DAYS_PER_YEAR,
            "total_accrual_frac": None if total is None else total,
            "annual_pct": None if calendar is None else round(calendar, 6),
            "per_bar_accrual_implied_frac": (
                None if (total is None or not n_bars)
                else total * CALENDAR_DAYS_PER_YEAR / float(cal_days) / float(n_bars)),
        },
        "convention_gap": {
            "printed_minus_calendar_pp": None if gap_pp is None else round(gap_pp, 6),
            "printed_over_calendar_ratio": None if ratio is None else round(ratio, 6),
            "ratio_identity_re_derives": (
                None if (ratio is None or printed is None or calendar is None
                         or abs(calendar) < 1e-12)
                else abs(abs(printed / calendar) - ratio) <= 1e-6),
            "overstatement_as_share_of_printed_pct": (
                None if (gap_pp is None or printed is None or abs(printed) < 1e-12)
                else round(gap_pp / abs(printed) * 100.0, 4)),
        },
        "priced_on_the_tickets_own_cash": {
            "cash_amount_current_ticket": ticket_cash,
            "cash_amount_as_issued": issued_cash,
            "cny_per_year_current_ticket": None if (gap_pp is None) else
                round(cny_gap(ticket_cash, printed, calendar), 2),
            "cny_per_year_as_issued": None if (gap_pp is None) else
                round(cny_gap(issued_cash, printed, calendar), 2),
            "note": "the gap is per year at constant cash; the ticket's cash is a 52.851% weight "
                    "of its NAV",
        },
        "answer": answer_sentence(printed, calendar, quoted, gap_pp, bpy),
        "verdict": (V_SURVIVES
                    if (printed is not None and quoted is not None
                        and abs(printed - float(quoted)) <= PRINT_TOL_PP)
                    else V_DOES_NOT_SURVIVE),
        "read_only": True,
    }
    if write:
        write_face(face)
    return face


def answer_sentence(printed, calendar, quoted, gap_pp, bpy):
    if printed is None or calendar is None:
        return "the window carries no accrual to annualise"
    repro = (quoted is not None and abs(printed - float(quoted)) <= PRINT_TOL_PP)
    head = ("the printed %.3f%%/yr reproduces exactly from its own window as mean accrual x %d "
            % (float(quoted if quoted is not None else printed), TICKET_BARS_PER_YEAR)) if repro \
        else ("the printed figure does NOT reproduce from its own window (recomputed %.3f%%/yr)"
              % printed)
    return ("%s; the same accrual stream annualised on calendar days /365 is %.3f%%/yr "
            "(%s bar steps per calendar year, not %d), so the ticket overstates by %.3f pp "
            "on that convention -- the printed number survives its own arithmetic and is not "
            "a calendar-annual rate."
            % (head, calendar, ("%.2f" % bpy) if bpy is not None else "n/a",
               TICKET_BARS_PER_YEAR, abs(gap_pp) if gap_pp is not None else 0.0))


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "printed_method" not in face:
        return ["the face carries no printed_method block"]
    w = face.get("window") or {}
    pm = face.get("printed_method") or {}
    cd = face.get("calendar_days_365") or {}
    cg = face.get("convention_gap") or {}

    n = w.get("bars")
    days = w.get("calendar_days")
    if not n or not days:
        p.append("the face names no window")
        return p
    if w.get("bars_match_the_printed_window") is not True:
        p.append("the recomputed bar count is not the one the ticket prints")
    if w.get("calendar_days_match_the_printed_window") is not True:
        p.append("the recomputed calendar span is not the one the ticket prints")
    if w.get("missing_bar_steps") != w.get("printed_missing_bar_steps"):
        p.append("the missing-quote count differs from the ticket's own count")

    mean = pm.get("mean_bar_accrual_frac")
    if mean is None:
        p.append("no mean bar accrual is published")
    else:
        want = annual_from_printed_method(mean, pm.get("bars_per_year") or TICKET_BARS_PER_YEAR)
        got = pm.get("annual_pct")
        if got is None or abs(want - float(got)) > 1e-6:
            p.append("the printed-method annual figure does not re-derive from its own mean")
        if pm.get("bars_per_year") != TICKET_BARS_PER_YEAR:
            p.append("bars_per_year is not %d" % TICKET_BARS_PER_YEAR)

    total = cd.get("total_accrual_frac")
    if total is None:
        p.append("no total accrual is published")
    else:
        want = annual_from_calendar_days(total, days, cd.get("days_per_year") or 365.0)
        got = cd.get("annual_pct")
        if got is None or abs(want - float(got)) > 1e-6:
            p.append("the calendar-day annual figure does not re-derive from its own total")
        if abs(float(total) - float(mean) * n) > 1e-12:
            p.append("total accrual is not the mean times the bar count")

    gp = cg.get("printed_minus_calendar_pp")
    if gp is None:
        p.append("no convention gap is published")
    else:
        want = float(pm["annual_pct"]) - float(cd["annual_pct"])
        if abs(want - float(gp)) > 1e-6:
            p.append("the convention gap does not re-derive from the two annual figures")
    if cg.get("ratio_identity_re_derives") is not True:
        p.append("the printed/calendar ratio does not re-derive from the window")
    if pm.get("reproduces_the_quoted_figure") is not True:
        p.append("the recomputed figure does not reproduce the ticket's quote")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # leg1 three consecutive weekdays at a flat 3.65%: one day each
    idx = pd.DatetimeIndex(["2021-01-04", "2021-01-05", "2021-01-06"])
    rates = pd.Series([3.65, 3.65, 3.65], index=idx)
    acc, miss = BW.repo_daily_cash(idx, rates)
    chk("leg1 a flat 3.65%% quote accrues 3.65/365 per one-day step",
        abs(float(acc.iloc[1]) - 3.65 / 100 / 365) < 1e-15, float(acc.iloc[1]))
    chk("leg1b the first bar accrues nothing and no step is counted missing",
        acc.iloc[0] == 0.0 and miss == 0, (float(acc.iloc[0]), miss))

    # leg2 printed method on that window = mean x 252
    mean = float(acc.mean())
    printed = annual_from_printed_method(mean)
    chk("leg2 PrintedMethod = mean x 252", abs(printed - (2 * 3.65 / 365 * 252 / 3)) < 1e-9, printed)

    # leg3 calendar convention = total / (days/365)
    total = float(acc.sum())
    cal = annual_from_calendar_days(total, (idx[-1] - idx[0]).days)
    chk("leg3 CalendarDays365 = total / (days/365)",
        abs(cal - (2 * 3.65 / 100 / 365) / (2 / 365) * 100) < 1e-12, cal)

    # leg4 the ratio identity: printed / calendar == 252 / implied bars-per-year
    bpy = implied_bars_per_year(len(idx), (idx[-1] - idx[0]).days)
    chk("leg4 the ratio is the window's own bar frequency, not a constant",
        abs(bpy - 3 * 365 / 2) < 1e-12 and abs(printed / cal - 252 / bpy) < 1e-12, (bpy, printed / cal))

    # leg5 Friday -> Monday earns three calendar days
    idx2 = pd.DatetimeIndex(["2021-01-08", "2021-01-11"])
    r2 = pd.Series([3.65], index=pd.DatetimeIndex(["2021-01-08"]))
    a2, _ = BW.repo_daily_cash(idx2, r2)
    chk("leg5 a Friday-to-Monday step earns three days",
        abs(float(a2.iloc[1]) - 3.65 / 100 * 3 / 365) < 1e-15, float(a2.iloc[1]))

    # leg6 a missing quote accrues nothing and is counted
    idx3 = pd.DatetimeIndex(["2021-01-08", "2021-01-11", "2021-01-12"])
    r3 = pd.Series([3.65], index=pd.DatetimeIndex(["2021-01-08"]))
    a3, m3 = BW.repo_daily_cash(idx3, r3)
    chk("leg6 a missing quote is zero accrual, counted once",
        float(a3.iloc[2]) == 0.0 and m3 == 1, (float(a3.iloc[2]), m3))

    # leg7 the CNY gap is linear in cash and in the pp gap
    chk("leg7 the CNY gap re-derives from cash x pp",
        abs(cny_gap(1_000_000.0, 2.0, 1.8) - 2000.0) < 1e-9, cny_gap(1_000_000.0, 2.0, 1.8))
    chk("leg7b a zero gap is zero CNY", cny_gap(1_000_000.0, 2.0, 2.0) == 0.0)

    # leg8 a shrinking window lowers the printed figure but not the ratio identity
    idx4 = pd.DatetimeIndex(["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07"])
    a4, _ = BW.repo_daily_cash(idx4, pd.Series([3.65] * 4, index=idx4))
    p4 = annual_from_printed_method(float(a4.mean()))
    c4 = annual_from_calendar_days(float(a4.sum()), (idx4[-1] - idx4[0]).days)
    chk("leg8 the ratio identity holds on a second window too",
        abs(p4 / c4 - 252 / implied_bars_per_year(len(idx4), 3)) < 1e-12, p4 / c4)

    # leg9 the two conventions AGREE exactly when the window holds 252 bars per 365 calendar days
    # -- that is the definition of the printed constant, so the gap is a frequency fact
    mean5, n5, days5 = 2e-5, 252, 365
    p5 = annual_from_printed_method(mean5)
    c5 = annual_from_calendar_days(mean5 * n5, days5)
    chk("leg9 a 252-bars-per-365-days window closes the gap exactly",
        abs(p5 - c5) < 1e-12 and abs(implied_bars_per_year(n5, days5) - 252.0) < 1e-12, (p5, c5))

    # leg10 guard: a face whose gap does not re-derive is refused
    good = {"window": {"bars": 3, "calendar_days": 2, "bars_match_the_printed_window": True,
                       "calendar_days_match_the_printed_window": True,
                       "missing_bar_steps": 0, "printed_missing_bar_steps": 0},
            "printed_method": {"bars_per_year": 252, "mean_bar_accrual_frac": 0.0001,
                               "annual_pct": 0.0001 * 252 * 100,
                               "reproduces_the_quoted_figure": True},
            "calendar_days_365": {"days_per_year": 365.0, "total_accrual_frac": 0.0003,
                                  "annual_pct": 0.0003 / (2 / 365) * 100},
            "convention_gap": {"printed_minus_calendar_pp":
                               0.0001 * 252 * 100 - 0.0003 / (2 / 365) * 100,
                               "ratio_identity_re_derives": True},
            "answer": "x"}
    chk("leg10 the guard accepts a face whose numbers re-derive", face_problems(good) == [],
        face_problems(good))
    bad = json.loads(json.dumps(good))
    bad["convention_gap"]["printed_minus_calendar_pp"] += 0.001
    chk("leg10b the guard refuses a gap that does not re-derive",
        any("gap" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(good))
    bad2["window"]["bars"] = 4
    chk("leg10c the guard refuses a total that is not mean x bars",
        any("mean times the bar count" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(good))
    bad3["printed_method"]["reproduces_the_quoted_figure"] = False
    chk("leg10d the guard refuses a face that does not reproduce the quote",
        any("does not reproduce" in s for s in face_problems(bad3)), face_problems(bad3))

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face = build(write=True)
        pr = face_problems(face)
        print("built %s | verdict=%s" % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        face = build(write=False)
        pr = face_problems(face)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh = build(write=False)
        keys = ("window", "printed_method", "calendar_days_365", "convention_gap",
                "priced_on_the_tickets_own_cash", "verdict", "answer")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))