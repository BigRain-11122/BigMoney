# -*- coding: utf-8 -*-
"""E590 -- what is the ticket's unquoted cash worth?

E589 (r1616) made the ticket's ``cash_leg`` block name the window it averages and disclose that
the repo panel behind it ends before the book's own bar: on the 2026-11-06 ticket the window runs
1,658 bars while GC001 stops on 2026-10-27, so the quote printed beside the window is 8 bars old
and 7 bar-steps of the window carry no quote at all.  The block discloses both numbers; nobody
priced them.

This study prices the silence, per published ticket, and asks whether "8 bars stale" is one fact
or a moving one:

  step_rows        every bar-step whose PRIOR bar carries no GC001 quote, with its calendar gap,
                   the nearest prior quote the writer's rule would fall back to, and what the
                   cash would have earned on that step
  forfeited_*      the sum over those steps, at the nearest prior quote and at the window mean
  book bars past   for every bar the book has processed since the panel's last quote: how old the
  the panel        quote is on that bar, in bars and in calendar days

The accrual rule is the producer's own (``etf_phase_beta_window.repo_daily_cash``): a step accrues
at the quote on its PRIOR bar, 1-day repo pays calendar days, and a step whose prior bar has no
quote accrues nothing and is counted, never replaced.  The repo panel is read through
``BW.load_repo_rates`` so this study cannot drift from the shipped leg.

The book's bar calendar comes from ``data/daily/sh510300.csv`` -- the five-member daily panel the
book itself is built from.  Where a ticket publishes its own ``window_bars``, the calendar count
is compared with it; the comparison is published, not assumed.

Honest limits:

  * the calendar is a proxy: it is the wide-base ETF's trading days, not a stored index of the
    backtester's panel, so ``calendar_matches_published_bars`` is the only claim made about it;
  * the forfeit assumes the cash would have sat at GC001 for the whole step; production rolls the
    three-rung ladder, so this is a reference reading and not the book's own carry;
  * only the 2026-11-06 ticket publishes its window; earlier tickets are read against the writer's
    own constant (2020-01-02 .. the ticket bar) and that reconstruction is disclosed per ticket;
  * read-only: no ticket, ledger row, panel or state face is written.

  python scripts/e590_cash_silence.py build
  python scripts/e590_cash_silence.py check
  python scripts/e590_cash_silence.py verify
  python scripts/e590_cash_silence.py selftest

Output: results/etf_book_order/CASHSILENCE.json
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scripts import etf_phase_beta_window as BW      # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "etf_book_order")
TICKET_DIR = OUTDIR
OUT_PATH = os.path.join(OUTDIR, "CASHSILENCE.json")
CALENDAR_PATH = os.path.join(ROOT, "data", "daily", "sh510300.csv")

# what etf_book_order feeds WB.repo_daily_cash; used only to reconstruct a window the ticket
# itself does not publish (the pre-E589 tickets)
WINDOW_START_FALLBACK = "2020-01-02"

V_PRICED = "the_unquoted_steps_are_priceable"
V_NONE = "no_ticket_carries_an_unquoted_step"
V_EMPTY = "nothing_on_disk_to_measure"


# --------------------------------------------------------------------------- inputs
def load_calendar(path=CALENDAR_PATH):
    """The book's bar calendar: the wide-base daily panel's trading dates."""
    if not os.path.exists(path):
        return pd.DatetimeIndex([])
    df = pd.read_csv(path)
    return pd.DatetimeIndex(pd.to_datetime(df[df.columns[0]])).sort_values()


def ticket_paths(directory=TICKET_DIR):
    """Published tickets only: the ``-card`` twins are the pre-workflow issue."""
    out = []
    for p in sorted(glob.glob(os.path.join(directory, "TICKET-*.json"))):
        if os.path.basename(p).endswith("-card.json"):
            continue
        out.append(p)
    return out


# --------------------------------------------------------------------------- the rule
def unquoted_steps(calendar, quoted, window_start, window_end):
    """Bar-steps of the window whose PRIOR bar carries no quote.

    This mirrors ``etf_phase_beta_window.repo_daily_cash``: a step accrues at the quote on its
    prior bar, so it is the *prior* bar that has to be quoted, and the last bar of the window is
    priced by the bar before it.
    """
    calendar = pd.DatetimeIndex(calendar)
    idx = calendar[(calendar >= window_start) & (calendar <= window_end)]
    steps = []
    for i in range(1, len(idx)):
        prev_bar, bar = idx[i - 1], idx[i]
        if prev_bar in quoted:
            continue
        steps.append({"prev_bar": str(prev_bar.date()), "bar": str(bar.date()),
                      "gap_days": max(int((bar - prev_bar).days), 1)})
    return idx, steps


def nearest_prior_quote(rates, bar):
    """The last quote at or before ``bar``: (bar, rate) or (None, None)."""
    if not len(rates):
        return None, None
    pos = int(rates.index.searchsorted(bar, side="right")) - 1
    if pos < 0:
        return None, None
    return str(rates.index[pos].date()), float(rates.iloc[pos])


def price_steps(steps, cash, mean_pct, rates):
    """Attach the fallback quote and the CNY each step would have earned, two ways."""
    out = []
    for s in steps:
        prev_bar = pd.Timestamp(s["prev_bar"])
        qbar, qrate = nearest_prior_quote(rates, prev_bar)
        days = float(s["gap_days"])
        at_quote = (cash * qrate / 100.0 * days / 365.0) if (qrate is not None and cash) else 0.0
        at_mean = (cash * mean_pct / 100.0 * days / 365.0) if (mean_pct is not None and cash) \
            else 0.0
        out.append({"prev_bar": s["prev_bar"], "bar": s["bar"], "gap_days": s["gap_days"],
                    "nearest_prior_quote_bar": qbar,
                    "nearest_prior_quote_pct": (round(qrate, 4) if qrate is not None else None),
                    "forfeited_at_nearest_quote_cny": round(at_quote, 2),
                    "forfeited_at_window_mean_cny": round(at_mean, 2)})
    return out


def bars_past_the_panel(calendar, rates):
    """For every bar the book has processed since the panel's last quote, how old that quote is."""
    if not len(rates) or not len(calendar):
        return {"available": False, "rows": []}
    panel_last = rates.index[-1]
    rows = []
    for d in calendar[calendar > panel_last]:
        age_bars = int((calendar > panel_last).sum() - (calendar > d).sum())
        qbar, qrate = nearest_prior_quote(rates, d)
        rows.append({"bar": str(d.date()), "quote_age_bars": age_bars,
                     "quote_age_days": int((d - panel_last).days),
                     "nearest_prior_quote_bar": qbar,
                     "nearest_prior_quote_pct": (round(qrate, 4)
                                                 if qrate is not None else None)})
    ages = [r["quote_age_bars"] for r in rows]
    rates_seen = {r["nearest_prior_quote_pct"] for r in rows}
    return {"available": True, "repo_panel_last_bar": str(panel_last.date()),
            "rows": rows, "bars_past_the_panel": len(rows),
            "quote_age_bars_min": (min(ages) if ages else None),
            "quote_age_bars_max": (max(ages) if ages else None),
            "age_is_the_same_on_every_bar": (len(set(ages)) <= 1),
            "the_fallback_rate_is_the_same_on_every_bar": (len(rates_seen) <= 1)}


# --------------------------------------------------------------------------- build
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def ticket_block(path, calendar, quoted, rates):
    doc = read_json(path)
    blk = doc.get("cash_leg") or {}
    tk = doc.get("ticket") or {}
    doc_blk = blk if isinstance(blk, dict) else {}
    ticket_bar = doc.get("pricing_bar") or doc_blk.get("ticket_bar") or doc.get("evidence_cutoff")
    ticket_bar = pd.Timestamp(ticket_bar)
    published_start = doc_blk.get("window_start")
    published_end = doc_blk.get("window_end")
    window_start = pd.Timestamp(published_start or WINDOW_START_FALLBACK)
    window_end = pd.Timestamp(published_end or ticket_bar)
    idx, steps = unquoted_steps(calendar, quoted, window_start, window_end)
    cash = tk.get("cash_amount")
    mean_pct = doc_blk.get("mean_accrual_ann_pct")
    rows = price_steps(steps, cash, mean_pct, rates)
    qbar, qrate = nearest_prior_quote(rates, ticket_bar)
    panel_last = (rates.index[-1] if len(rates) else None)
    quoted_in_window = int(sum(1 for d in idx if d in quoted))
    block = {
        "ticket": os.path.basename(path),
        "ticket_bar": str(ticket_bar.date()),
        "book_nav_cny": tk.get("nav"),
        "cash_amount_cny": (round(float(cash), 2) if cash is not None else None),
        "cash_weight": tk.get("cash_weight"),
        "window": {
            "start": str(window_start.date()), "end": str(window_end.date()),
            "source": ("published_block" if (published_start and published_end)
                       else "reconstructed_from_the_writers_constant"),
            "bars_from_calendar": int(len(idx)),
            "bars_published_by_ticket": doc_blk.get("window_bars"),
            "calendar_matches_published_bars": (
                None if doc_blk.get("window_bars") is None
                else int(len(idx)) == int(doc_blk.get("window_bars")))
        },
        "bars_in_window": int(len(idx)),
        "quoted_bars_in_window": quoted_in_window,
        "unquoted_bars_in_window": int(len(idx)) - quoted_in_window,
        "unquoted_steps": len(rows),
        "steps_published_by_ticket": doc_blk.get("missing_bar_steps"),
        "steps_rederive_the_ticket_block": (
            None if doc_blk.get("missing_bar_steps") is None
            else int(len(rows)) == int(doc_blk.get("missing_bar_steps"))),
        "mean_accrual_ann_pct": (round(float(mean_pct), 4) if mean_pct is not None else None),
        "repo_panel_last_bar": (str(panel_last.date()) if panel_last is not None else None),
        "nearest_prior_quote_bar": qbar,
        "nearest_prior_quote_pct": (round(qrate, 4) if qrate is not None else None),
        "quote_age_bars_at_ticket_bar": (
            int((calendar > panel_last).sum() - (calendar > ticket_bar).sum())
            if panel_last is not None else None),
        "quote_age_days_at_ticket_bar": (
            int((ticket_bar - panel_last).days) if panel_last is not None else None),
        "forfeited_at_nearest_quote_cny": round(
            sum(r["forfeited_at_nearest_quote_cny"] for r in rows), 2),
        "forfeited_at_window_mean_cny": round(
            sum(r["forfeited_at_window_mean_cny"] for r in rows), 2),
        "forfeited_bp_of_cash": (
            round(10000.0 * sum(r["forfeited_at_nearest_quote_cny"] for r in rows) / float(cash), 3)
            if cash else None),
        "step_rows": rows,
    }
    return block


def summarise(blocks, past):
    with_steps = [b for b in blocks if b["unquoted_steps"]]
    total_quote = round(sum(b["forfeited_at_nearest_quote_cny"] for b in blocks), 2)
    total_mean = round(sum(b["forfeited_at_window_mean_cny"] for b in blocks), 2)
    cash_with_steps = sum(float(b["cash_amount_cny"] or 0.0) for b in with_steps)
    checked = [b["steps_rederive_the_ticket_block"] for b in blocks
               if b["steps_rederive_the_ticket_block"] is not None]
    bars_checked = [b["window"]["calendar_matches_published_bars"] for b in blocks
                    if b["window"]["calendar_matches_published_bars"] is not None]
    s = {
        "tickets": len(blocks),
        "tickets_with_unquoted_steps": len(with_steps),
        "tickets_publishing_a_step_count": len(checked),
        "every_published_step_count_rederives": (all(checked) if checked else None),
        "tickets_publishing_a_window_bar_count": len(bars_checked),
        "every_published_window_bar_count_matches_the_calendar": (
            all(bars_checked) if bars_checked else None),
        "unquoted_steps_total": int(sum(b["unquoted_steps"] for b in blocks)),
        "forfeited_at_nearest_quote_cny_total": total_quote,
        "forfeited_at_window_mean_cny_total": total_mean,
        "cash_cny_on_tickets_with_unquoted_steps": round(cash_with_steps, 2),
        "forfeited_bp_of_that_cash": (
            round(10000.0 * total_quote / cash_with_steps, 3) if cash_with_steps else None),
        "repo_panel_last_bar": past.get("repo_panel_last_bar"),
        "book_bars_past_the_panel": past.get("bars_past_the_panel"),
        "quote_age_bars_at_the_newest_book_bar": past.get("quote_age_bars_max"),
        "quote_age_is_the_same_on_every_bar_past_the_panel": past.get(
            "age_is_the_same_on_every_bar"),
    }
    return s


def verdict_of(s):
    if not s.get("tickets"):
        return V_EMPTY
    if not s.get("unquoted_steps_total"):
        return V_NONE
    return V_PRICED


def verdict_line(s):
    if s.get("tickets") == 0:
        return "no published ticket on disk"
    if not s.get("unquoted_steps_total"):
        return ("none of the %d published tickets carries a step with no quote on its prior bar"
                % s["tickets"])
    return ("%d of %d tickets price a cash leg over %d unquoted bar-steps worth %.2f CNY at the "
            "nearest prior quote (%.2f CNY at the window mean, %.2f bp of the %.0f CNY cash they "
            "leave idle); the quote is %s bars old on the newest book bar, and that age is %s on "
            "every bar past the panel (%s)"
            % (s["tickets_with_unquoted_steps"], s["tickets"], s["unquoted_steps_total"],
               s["forfeited_at_nearest_quote_cny_total"],
               s["forfeited_at_window_mean_cny_total"], s["forfeited_bp_of_that_cash"] or 0.0,
               s["cash_cny_on_tickets_with_unquoted_steps"],
               s["quote_age_bars_at_the_newest_book_bar"],
               "the same" if s["quote_age_is_the_same_on_every_bar_past_the_panel"] else "not the same",
               s["repo_panel_last_bar"]))


def build(write=True):
    calendar = load_calendar()
    rates = BW.load_repo_rates()
    quoted = set(rates.index)
    past = bars_past_the_panel(calendar, rates)
    blocks = [ticket_block(p, calendar, quoted, rates) for p in ticket_paths()]
    s = summarise(blocks, past)
    cutoff = max((b["ticket_bar"] for b in blocks), default="none")
    face = {
        "study": "E590_cash_silence",
        "generated_by": "scripts/e590_cash_silence.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": cutoff,
        "question": ("what is an unquoted cash step worth, and is '8 bars stale' one fact or a "
                     "moving one?"),
        "rule": ("a step accrues at the quote on its PRIOR bar, 1-day repo pays calendar days, "
                 "and a step whose prior bar has no quote accrues nothing and is counted "
                 "(etf_phase_beta_window.repo_daily_cash); the forfeit prices those steps at the "
                 "nearest prior quote and, separately, at the window mean"),
        "calendar": {"source": "data/daily/sh510300.csv",
                     "bars": int(len(calendar)),
                     "from": (str(calendar[0].date()) if len(calendar) else None),
                     "to": (str(calendar[-1].date()) if len(calendar) else None)},
        "repo_panel_source": "data/repo_daily/GC001.csv",
        "tickets": blocks,
        "bars_past_the_panel": past,
        "summary": s,
        "verdict": verdict_of(s),
        "verdict_line": verdict_line(s),
        "caveats": [
            "the calendar is the wide-base daily panel's trading days, not a stored index of the "
            "backtester's panel; where a ticket publishes window_bars the count is compared",
            "the forfeit assumes the cash sat at GC001 for the whole step; production rolls the "
            "three-rung ladder, so this is a reference reading, not the book's own carry",
            "only the 2026-11-06 ticket publishes its window; earlier tickets are read against "
            "the writer's own constant and marked reconstructed_from_the_writers_constant",
            "read-only: no ticket, ledger row, panel or state face is written",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    return face


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    blocks = face.get("tickets")
    s = face.get("summary") or {}
    past = face.get("bars_past_the_panel") or {}
    if not isinstance(blocks, list) or not blocks:
        return ["the face carries no tickets"]
    if s.get("tickets") != len(blocks):
        p.append("summary.tickets does not match the ticket list")
    for b in blocks:
        name = b.get("ticket")
        rows = b.get("step_rows") or []
        if b.get("unquoted_steps") != len(rows):
            p.append("%s: unquoted_steps does not match its step rows" % name)
        cash = float(b.get("cash_amount_cny") or 0.0)
        mean_pct = b.get("mean_accrual_ann_pct")
        prev_key = None
        for r in rows:
            if prev_key is not None and r["bar"] <= prev_key:
                p.append("%s: step rows are not in ascending bar order" % name)
            prev_key = r["bar"]
            days = float(r["gap_days"])
            if not days >= 1:
                p.append("%s: step %s carries a gap under a day" % (name, r["bar"]))
            q = r.get("nearest_prior_quote_pct")
            want_q = round(cash * float(q) / 100.0 * days / 365.0, 2) if q is not None else 0.0
            if abs(want_q - float(r.get("forfeited_at_nearest_quote_cny") or 0.0)) > 0.01:
                p.append("%s: step %s forfeit does not re-derive at the nearest quote"
                         % (name, r["bar"]))
            want_m = (round(cash * float(mean_pct) / 100.0 * days / 365.0, 2)
                      if mean_pct is not None else 0.0)
            if abs(want_m - float(r.get("forfeited_at_window_mean_cny") or 0.0)) > 0.01:
                p.append("%s: step %s forfeit does not re-derive at the window mean"
                         % (name, r["bar"]))
        tot_q = round(sum(float(r.get("forfeited_at_nearest_quote_cny") or 0.0) for r in rows), 2)
        tot_m = round(sum(float(r.get("forfeited_at_window_mean_cny") or 0.0) for r in rows), 2)
        if abs(tot_q - float(b.get("forfeited_at_nearest_quote_cny") or 0.0)) > 0.01:
            p.append("%s: ticket forfeit does not re-derive from its steps" % name)
        if abs(tot_m - float(b.get("forfeited_at_window_mean_cny") or 0.0)) > 0.01:
            p.append("%s: ticket mean-based forfeit does not re-derive from its steps" % name)
        w = b.get("window") or {}
        if w.get("bars_from_calendar") != b.get("bars_in_window"):
            p.append("%s: window bar count does not match bars_in_window" % name)
        if w.get("calendar_matches_published_bars") is False:
            p.append("%s: the calendar does not reproduce the ticket's own window_bars" % name)
        if b.get("steps_rederive_the_ticket_block") is False:
            p.append("%s: the step count does not reproduce the ticket's own missing_bar_steps"
                     % name)
        if b.get("unquoted_bars_in_window") is not None and \
                int(b["unquoted_bars_in_window"]) < len(rows):
            p.append("%s: more unquoted steps than unquoted bars" % name)
    want_steps = int(sum(int(b.get("unquoted_steps") or 0) for b in blocks))
    if s.get("unquoted_steps_total") != want_steps:
        p.append("summary.unquoted_steps_total does not re-derive from the tickets")
    want_q = round(sum(float(b.get("forfeited_at_nearest_quote_cny") or 0.0) for b in blocks), 2)
    if abs(want_q - float(s.get("forfeited_at_nearest_quote_cny_total") or 0.0)) > 0.01:
        p.append("summary forfeit total does not re-derive from the tickets")
    cash_steps = sum(float(b.get("cash_amount_cny") or 0.0) for b in blocks
                     if b.get("unquoted_steps"))
    if abs(cash_steps - float(s.get("cash_cny_on_tickets_with_unquoted_steps") or 0.0)) > 0.01:
        p.append("summary cash basis does not re-derive from the tickets")
    if cash_steps and s.get("forfeited_bp_of_that_cash") is not None:
        want_bp = round(10000.0 * want_q / cash_steps, 3)
        if abs(want_bp - float(s["forfeited_bp_of_that_cash"])) > 1e-3:
            p.append("summary basis points do not re-derive")
    rows = past.get("rows") or []
    if past.get("available"):
        if past.get("bars_past_the_panel") != len(rows):
            p.append("bars_past_the_panel does not match its rows")
        ages = [r.get("quote_age_bars") for r in rows]
        if ages != sorted(ages):
            p.append("quote ages are not ascending in bar order")
        if len(set(ages)) > 1:
            step_diff = {ages[i + 1] - ages[i] for i in range(len(ages) - 1)}
            if step_diff != {1}:
                p.append("quote age does not grow by exactly one bar per bar")
        if len(set(ages)) == 1 and past.get("age_is_the_same_on_every_bar") is not True:
            p.append("a flat age table is not published as flat")
        if len(set(ages)) > 1 and past.get("age_is_the_same_on_every_bar") is not False:
            p.append("a moving age table is published as flat")
        rates_seen = {r.get("nearest_prior_quote_pct") for r in rows}
        if (len(rates_seen) <= 1) != bool(
                past.get("the_fallback_rate_is_the_same_on_every_bar")):
            p.append("the fallback-rate flag does not re-derive from the rows")
        if ages and past.get("quote_age_bars_max") != max(ages):
            p.append("quote_age_bars_max does not re-derive")
        # the summary repeats these three readings; a copy that drifts from the table is how a
        # moving age becomes a flat one on the page a reader actually sees
        if s.get("book_bars_past_the_panel") != past.get("bars_past_the_panel"):
            p.append("summary.book_bars_past_the_panel does not match the age table")
        if s.get("quote_age_is_the_same_on_every_bar_past_the_panel") is not past.get(
                "age_is_the_same_on_every_bar"):
            p.append("summary's flat-age claim does not match the age table")
        if s.get("quote_age_bars_at_the_newest_book_bar") != past.get("quote_age_bars_max"):
            p.append("summary's newest quote age does not match the age table")
        if s.get("repo_panel_last_bar") != past.get("repo_panel_last_bar"):
            p.append("summary's repo panel last bar does not match the age table")
    if verdict_of(s) != face.get("verdict"):
        p.append("verdict does not re-derive from the summary")
    return p


def check():
    if not os.path.exists(OUT_PATH):
        print("MISSING %s -- run scripts/e590_cash_silence.py build" % OUT_PATH)
        return 1
    face = read_json(OUT_PATH)
    problems = face_problems(face)
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E590 FAIL %d problem(s)" % len(problems))
        return 1
    s = face["summary"]
    print("E590 OK tickets=%d with_steps=%d steps=%d forfeit=%.2f CNY (mean %.2f, %.3f bp) "
          "age_at_newest=%s flat=%s verdict=%s"
          % (s["tickets"], s["tickets_with_unquoted_steps"], s["unquoted_steps_total"],
             s["forfeited_at_nearest_quote_cny_total"],
             s["forfeited_at_window_mean_cny_total"], s["forfeited_bp_of_that_cash"] or 0.0,
             s["quote_age_bars_at_the_newest_book_bar"],
             s["quote_age_is_the_same_on_every_bar_past_the_panel"], face["verdict"]))
    return 0


def verify():
    fresh = build(write=False)
    problems = face_problems(fresh)
    on_disk = read_json(OUT_PATH).get("evidence_cutoff") if os.path.exists(OUT_PATH) else None
    if on_disk is not None and fresh["evidence_cutoff"] < on_disk:
        problems.append("a rebuild reads an older cutoff (%s < %s)"
                        % (fresh["evidence_cutoff"], on_disk))
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E590 verify FAIL")
        return 1
    s = fresh["summary"]
    print("E590 verify PASS cutoff=%s tickets=%d steps=%d forfeit=%.2f verdict=%s"
          % (fresh["evidence_cutoff"], s["tickets"], s["unquoted_steps_total"],
             s["forfeited_at_nearest_quote_cny_total"], fresh["verdict"]))
    return 0


# --------------------------------------------------------------------------- selftest
def _rates(pairs):
    return pd.Series([float(r) for _, r in pairs],
                     index=pd.DatetimeIndex([pd.Timestamp(d) for d, _ in pairs]))


def selftest():
    bad = []
    seen = [0]

    def chk(cond, msg):
        """Count every assertion, so the printed total is the number actually run."""
        seen[0] += 1
        if not cond:
            bad.append(msg)

    cal = pd.DatetimeIndex(pd.to_datetime(
        ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09"]))
    full = _rates([("2026-01-05", 2.0), ("2026-01-06", 2.0), ("2026-01-07", 2.0),
                   ("2026-01-08", 2.0)])
    # 1. a fully quoted window has no unquoted step
    idx, steps = unquoted_steps(cal, set(full.index), pd.Timestamp("2026-01-05"),
                               pd.Timestamp("2026-01-08"))
    chk(len(idx) == 4 and not steps,
        "a fully quoted window reported %d step(s)" % len(steps))
    # 2. the step that lacks a PRIOR quote is the only one counted past the panel
    short = _rates([("2026-01-05", 2.0), ("2026-01-06", 2.0), ("2026-01-07", 2.0)])
    idx, steps = unquoted_steps(cal, set(short.index), pd.Timestamp("2026-01-05"),
                               pd.Timestamp("2026-01-09"))
    chk([s["bar"] for s in steps] == ["2026-01-09"],
        "the panel-short window counted %s, expected only the row whose prior bar is unquoted"
        % [s["bar"] for s in steps])
    # 3. the forfeit is cash * rate/100 * days/365 on the nearest prior quote
    priced = price_steps(steps, 1_000_000.0, 2.5, short)
    # 2026-01-08 -> 2026-01-09 is a one-day step whose prior bar carries no quote: one day, not
    # the two the window's calendar span suggests
    want = round(1_000_000.0 * 2.0 / 100.0 * 1.0 / 365.0, 2)
    chk(abs(float(priced[0]["forfeited_at_nearest_quote_cny"]) - want) <= 0.01,
        "a one-day unquoted step forfeit is %s, expected %.2f"
        % (priced[0]["forfeited_at_nearest_quote_cny"], want))
    chk(priced[0]["gap_days"] == 1,
        "the step's calendar gap is %s, expected 1" % priced[0]["gap_days"])
    # 4. the nearest prior quote skips back past unquoted bars instead of falling to zero
    chk(priced[0]["nearest_prior_quote_bar"] == "2026-01-07",
        "the fallback quote is %s, expected 2026-01-07"
        % priced[0]["nearest_prior_quote_bar"])
    # 5. the age table grows one bar per bar and is not flat when it has more than one row
    past = bars_past_the_panel(cal, short)
    ages = [r["quote_age_bars"] for r in past["rows"]]
    chk(ages == [1, 2], "the age table is %s, expected [1, 2]" % ages)
    chk(past["age_is_the_same_on_every_bar"] is False,
        "a two-bar age table was published as flat")
    chk(past["the_fallback_rate_is_the_same_on_every_bar"],
        "the fallback rate is the same on every row but was published as varying")
    one = bars_past_the_panel(cal, full)
    chk([r["quote_age_bars"] for r in one["rows"]] == [1],
        "a single bar past the panel did not report age 1")
    chk(one["age_is_the_same_on_every_bar"] is True,
        "a single-row age table was not published as flat")
    # 6. the guard accepts a consistent face and refuses doctored ones
    blk = {"ticket": "TICKET-x.json", "ticket_bar": "2026-01-09", "cash_amount_cny": 1000.0,
           "mean_accrual_ann_pct": 2.5, "unquoted_steps": 1,
           "unquoted_bars_in_window": 2, "bars_in_window": 5,
           "forfeited_at_nearest_quote_cny": round(2000.0 / 100.0 * 2.0 / 365.0, 2),
           "forfeited_at_window_mean_cny": round(2500.0 / 100.0 * 2.0 / 365.0, 2),
           "window": {"bars_from_calendar": 5, "bars_published_by_ticket": 5,
                      "calendar_matches_published_bars": True},
           "steps_rederive_the_ticket_block": True,
           "step_rows": [{"prev_bar": "2026-01-07", "bar": "2026-01-09", "gap_days": 2,
                          "nearest_prior_quote_bar": "2026-01-07",
                          "nearest_prior_quote_pct": 2000.0,
                          "forfeited_at_nearest_quote_cny": round(2000.0 / 100.0 * 2.0 / 365.0, 2),
                          "forfeited_at_window_mean_cny": round(2500.0 / 100.0 * 2.0 / 365.0, 2)}]}
    # 2000.0 is a percent-shaped rate: the fixture keeps the arithmetic honest at 20.0
    for r in blk["step_rows"]:
        r["nearest_prior_quote_pct"] = 2.0
    blk["step_rows"][0]["forfeited_at_nearest_quote_cny"] = round(
        1000.0 * 2.0 / 100.0 * 2.0 / 365.0, 2)
    blk["forfeited_at_nearest_quote_cny"] = blk["step_rows"][0]["forfeited_at_nearest_quote_cny"]
    blk["forfeited_at_window_mean_cny"] = round(1000.0 * 2.5 / 100.0 * 2.0 / 365.0, 2)
    blk["step_rows"][0]["forfeited_at_window_mean_cny"] = blk["forfeited_at_window_mean_cny"]
    s = {"tickets": 1, "unquoted_steps_total": 1,
         "forfeited_at_nearest_quote_cny_total": blk["forfeited_at_nearest_quote_cny"],
         "forfeited_at_window_mean_cny_total": blk["forfeited_at_window_mean_cny"],
         "cash_cny_on_tickets_with_unquoted_steps": 1000.0,
         "forfeited_bp_of_that_cash": round(10000.0 * blk["forfeited_at_nearest_quote_cny"] / 1000.0, 3),
         "repo_panel_last_bar": "2026-01-07", "book_bars_past_the_panel": 2,
         "quote_age_bars_at_the_newest_book_bar": 2,
         "quote_age_is_the_same_on_every_bar_past_the_panel": False}
    face = {"tickets": [blk], "summary": s, "verdict": V_PRICED,
            "bars_past_the_panel": {"available": True, "bars_past_the_panel": 2,
                                    "repo_panel_last_bar": "2026-01-07",
                                    "quote_age_bars_max": 2,
                                    "age_is_the_same_on_every_bar": False,
                                    "the_fallback_rate_is_the_same_on_every_bar": True,
                                    "rows": [{"bar": "2026-01-08", "quote_age_bars": 1,
                                              "nearest_prior_quote_pct": 2.0},
                                             {"bar": "2026-01-09", "quote_age_bars": 2,
                                              "nearest_prior_quote_pct": 2.0}]}}
    chk(not face_problems(face),
        "the guard refused a consistent synthetic face: %s" % face_problems(face)[:2])
    d1 = json.loads(json.dumps(face))
    d1["tickets"][0]["step_rows"][0]["forfeited_at_nearest_quote_cny"] = 9.99
    chk(bool(face_problems(d1)), "a step forfeit that does not re-derive was accepted")
    d2 = json.loads(json.dumps(face))
    d2["tickets"][0]["unquoted_steps"] = 3
    chk(bool(face_problems(d2)), "a step count that does not match its rows was accepted")
    d3 = json.loads(json.dumps(face))
    d3["summary"]["quote_age_is_the_same_on_every_bar_past_the_panel"] = True
    chk(bool(face_problems(d3)), "a flat claim beside a moving age table was accepted")
    d4 = json.loads(json.dumps(face))
    d4["verdict"] = V_NONE
    chk(bool(face_problems(d4)), "a verdict that does not re-derive was accepted")
    d5 = json.loads(json.dumps(face))
    d5["tickets"][0]["window"]["calendar_matches_published_bars"] = False
    chk(bool(face_problems(d5)),
        "a calendar that misses the ticket's own bar count was accepted")
    d6 = json.loads(json.dumps(face))
    d6["bars_past_the_panel"]["rows"][1]["quote_age_bars"] = 3
    chk(bool(face_problems(d6)), "an age table that skips a bar was accepted")
    for x in bad:
        print("SELFTEST FAIL %s" % x)
    print("E590 selftest %d/%d" % (seen[0] - len(bad), seen[0]))
    return 1 if bad else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        print("WROTE %s cutoff=%s verdict=%s" % (OUT_PATH, face["evidence_cutoff"],
                                                 face["verdict"]))
        print(face["verdict_line"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (build|check|verify|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())