# -*- coding: utf-8 -*-
"""E587 -- do the forward ledger's carry and the ticket's printed cash leg use the same window?

E585 (r1613) measured what the ticket's ``cash_leg`` block actually prints: the mean of GC001
over ``2020-01-01..cutoff`` scaled by 252, not the rate on the bar the ticket names.  The other
cash face of this book is the forward ledger (``results/etf_book_forward/LEDGER.json``), which
accrues a per-bar return produced by the three-rung repo ladder (GC007/GC014/GC028, commission
charged) and scales it by 244.  So the book publishes two annualised cash numbers, over two
different windows, from two different instruments, and neither face says which window it used.

This study rebuilds both from the repo panel and puts them side by side:

  ledger_ladder3_ann_pct          mean ladder3 per-bar return over the ledger's own bars, 244
  ledger_ladder3_ann_pct_gross    the same with commission waived (a ruler, not the shipped leg)
  gc001_mean_over_ledger_bars     GC001 mean over exactly those bars
  gc001_mean_over_ticket_window   GC001 mean over 2020-01-01..cutoff (what the ticket prints)
  ticket_published_mean_min/max   what the tickets on disk actually print

and splits the printed-minus-accrued gap arithmetically into a window term and an instrument
term, publishing the residual rather than calling the split an attribution:

  window_effect_pp = gc001(ticket window) - gc001(ledger bars)
  instrument_effect_pp = gc001(ledger bars) - ladder3(ledger bars)
  residual_pp = printed - ledger_ladder3 - window_effect - instrument_effect

It also asks whether the ledger's own ``carry`` column reproduces from the panel at all, under
five candidate rules (ladder at this row's cash, ladder at the previous row's cash, GC001 prior
quote for one day, GC001 prior quote for the calendar gap, GC001 same-bar quote for one day).
The published carry is stored at 10 dp and the cash basis at 6 dp, so both a 1e-9 absolute count
and a 1e-4 relative count are published: the first says "exact reproduction", the second says
"reproduction up to the record's own rounding".

Per row it publishes:

  bar / prev_bar / gap_days       the calendar gap the row closes
  cash / published_carry          what the record holds
  published_frac_ann_pct          published_carry / cash, annualised at 244
  ladder_frac / ladder_implied_carry
  ladder_abs_diff / ladder_rel_diff
  gc001_on_bar_pct                GC001 close quoted on that bar (None past the panel)
  class                           see CLASSES

Honest limits:

  * the ladder's per-bar return apportions a maturing contract across the bars it spans; it is
    rebuilt with the engine's own module (``etf_book_cash_ladder``), not re-implemented here;
  * 244 is the repo convention this repo uses everywhere for CAGR, 252 is the ticket's; the
    day-count difference is published as its own field and is not folded into either effect;
  * GC001 is the short rung, not the ladder the ledger actually holds, so
    ``gc001_mean_over_ledger_bars`` is a reference reading, not the shipped leg;
  * this study is read-only: it writes no ledger row, rewrites no ticket, and prices no return.

  python scripts/e587_cash_window.py build
  python scripts/e587_cash_window.py check
  python scripts/e587_cash_window.py verify
  python scripts/e587_cash_window.py selftest

Output: results/etf_book_order/CASHWINDOW.json + CASHWINDOW-latest.json
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

OUTDIR = os.path.join(ROOT, "results", "etf_book_order")
LEDGER_PATH = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
REPO_PATH = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

WINDOW_START = "2020-01-01"       # what etf_book_order feeds to BW.repo_daily_cash
BARS_PER_YEAR_LEDGER = 244.0      # repo convention, what the ledger's CAGR uses
BARS_PER_YEAR_TICKET = 252.0      # what the ticket's cash_leg block uses
TOL_PP = 0.02                     # published ticket values are rounded to 3 dp
TOL_ABS = 1e-9                    # "exact" reproduction of the stored carry
TOL_REL = 1e-4                    # reproduction up to the record's own dp rounding
TOL_REL_NEAR = 0.01               # a 1% band: an alignment/rounding story, not a free pass
GAP_TOL_DAYS = 0.25               # a one-day rule never implies 1.5 days on a 3-day gap

C_LADDER = "carry_reproduces_the_ladder"
C_LADDER_NEAR = "carry_reproduces_the_ladder_within_one_percent"
C_LADDER_GROSS = "carry_reproduces_the_ladder_only_with_commission_waived"
C_LADDER_SWAPPED = "carry_reproduces_the_neighbouring_bars_ladder"
C_PANEL_SHORT = "zero_carry_on_a_bar_past_the_repo_panel"
C_GC001_PREV = "carry_reproduces_from_the_prior_bar_quote"
C_NO_RULE = "carry_reproduces_no_published_rule"
CLASSES = (C_LADDER, C_LADDER_NEAR, C_LADDER_GROSS, C_LADDER_SWAPPED, C_PANEL_SHORT,
           C_GC001_PREV, C_NO_RULE)

V_DIFFERENT = "the_two_cash_faces_do_not_share_a_window"
V_SAME = "the_two_cash_faces_share_a_window_and_an_instrument"
V_EMPTY = "nothing_on_disk_to_compare"

RULES = (
    "ladder3_at_this_rows_cash",
    "ladder3_at_the_previous_rows_cash",
    "ladder3_at_the_next_bars_quote",
    "ladder3_gross_of_commission_at_this_rows_cash",
    "gc001_prior_bar_quote_for_one_day",
    "gc001_prior_bar_quote_for_the_calendar_gap",
    "gc001_same_bar_quote_for_one_day",
)


# --------------------------------------------------------------------------- #
# inputs
# --------------------------------------------------------------------------- #

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


def ledger_bars(led):
    bars = led.get("bars") or []
    return sorted(bars, key=lambda b: b.get("bar") or "")


def ledger_dates(bars):
    import pandas as pd
    return [pd.Timestamp(b["bar"]) for b in bars]


def build_ladder(dates, fee_free=False):
    """Per-bar ladder return aligned to ``dates`` (engine module, never re-implemented)."""
    try:
        from scripts import etf_book_forward as F
        ret, note = F.build_carry(dates, fee_free=fee_free)
    except Exception as exc:                                  # pragma: no cover - env dependent
        return None, "unreadable: %s" % exc
    return ret, note


def ticket_cash_legs():
    rows = []
    for path in sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json"))):
        d = _read_json(path)
        block = d.get("cash_leg") if isinstance(d.get("cash_leg"), dict) else None
        rows.append({
            "file": os.path.basename(path),
            "evidence_cutoff": d.get("evidence_cutoff"),
            "published_mean_accrual_ann_pct": (block or {}).get("mean_accrual_ann_pct"),
            "block_fields": sorted(block.keys()) if block else [],
            "names_a_window": bool(
                block and any(k for k in block if "window" in str(k).lower()
                              or "start" in str(k).lower())),
            "source": (block or {}).get("source"),
        })
    return rows


# --------------------------------------------------------------------------- #
# per row
# --------------------------------------------------------------------------- #

def _diff(published, implied):
    if published is None or implied is None:
        return None, None
    a = abs(float(published) - float(implied))
    d = float(implied)
    rel = (a / abs(d)) if abs(d) > 1e-15 else (0.0 if a == 0.0 else float("inf"))
    return round(a, 12), (round(rel, 8) if rel != float("inf") else None)


def classify(row, ladder_reproduces_gross):
    if row["ladder_rel_diff"] is not None and row["ladder_rel_diff"] <= TOL_REL:
        return C_LADDER
    if row["ladder_rel_diff"] is not None and row["ladder_rel_diff"] <= TOL_REL_NEAR:
        return C_LADDER_NEAR
    if (row["published_carry"] is not None and abs(float(row["published_carry"])) == 0.0
            and row["gc001_on_bar_pct"] is None and row["gc001_on_prev_bar_pct"] is None):
        return C_PANEL_SHORT
    if row.get("ladder_swapped_rel_diff") is not None and \
            row["ladder_swapped_rel_diff"] <= TOL_REL_NEAR:
        return C_LADDER_SWAPPED
    if ladder_reproduces_gross:
        return C_LADDER_GROSS
    if row["gc001_prev_rule_rel_diff"] is not None and \
            row["gc001_prev_rule_rel_diff"] <= TOL_REL_NEAR:
        return C_GC001_PREV
    return C_NO_RULE


def analyse(bars, rates, ladder, ladder_gross):
    import pandas as pd
    rows, prev = [], None
    prev_cash = None
    dates = [pd.Timestamp(b["bar"]) for b in bars]
    for i, b in enumerate(bars):
        bar = b.get("bar")
        cash = b.get("cash")
        carry = b.get("carry")
        gap = None if prev is None else int((pd.Timestamp(bar) - pd.Timestamp(prev)).days)
        frac = None if ladder is None else ladder.get(pd.Timestamp(bar))
        frac = None if frac is None else float(frac)
        next_frac = None
        if ladder is not None and i + 1 < len(dates):
            nxt = ladder.get(dates[i + 1])
            next_frac = None if nxt is None else float(nxt)
        frac_g = None if ladder_gross is None else ladder_gross.get(pd.Timestamp(bar))
        frac_g = None if frac_g is None else float(frac_g)
        basis = cash if cash else prev_cash
        prev_basis = prev_cash if prev_cash else cash
        implied = None if (frac is None or basis is None) else float(basis) * frac
        implied_g = None if (frac_g is None or basis is None) else float(basis) * frac_g
        implied_prev_basis = (None if (frac is None or prev_basis is None)
                              else float(prev_basis) * frac)
        implied_next = (None if (next_frac is None or basis is None)
                        else float(basis) * next_frac)
        abs_d, rel_d = _diff(carry, implied)
        _, rel_g = _diff(carry, implied_g)
        _, rel_prev_basis = _diff(carry, implied_prev_basis)
        _, rel_next = _diff(carry, implied_next)
        gc_now = rate_on(rates, bar)
        gc_prev = rate_on(rates, prev) if prev is not None else None
        # candidate "one day at the prior quote" and "the calendar gap at the prior quote"
        gc_prev_one = (None if (gc_prev is None or basis is None)
                       else float(basis) * float(gc_prev) / 100.0 / 365.0)
        gc_prev_gap = (None if (gc_prev_one is None or gap is None)
                       else gc_prev_one * max(1, gap))
        gc_now_one = (None if (gc_now is None or basis is None)
                      else float(basis) * float(gc_now) / 100.0 / 365.0)
        _, gc_prev_rel = _diff(carry, gc_prev_one)
        _, gc_prev_gap_rel = _diff(carry, gc_prev_gap)
        _, gc_now_rel = _diff(carry, gc_now_one)
        published_frac_ann = (None if (carry is None or not basis)
                              else round(float(carry) / float(basis)
                                         * BARS_PER_YEAR_LEDGER * 100.0, 6))
        row = {
            "index": i,
            "bar": bar,
            "prev_bar": prev,
            "gap_days": gap,
            "cash": cash,
            "cash_used_as_basis": basis,
            "published_carry": carry,
            "published_frac_ann_pct": published_frac_ann,
            "ladder_frac": None if frac is None else round(frac, 10),
            "ladder_implied_carry": None if implied is None else round(implied, 12),
            "ladder_abs_diff": abs_d,
            "ladder_rel_diff": rel_d,
            "ladder_gross_rel_diff": rel_g,
            "ladder_prev_basis_rel_diff": rel_prev_basis,
            "ladder_swapped_rel_diff": rel_next,
            "gc001_on_bar_pct": gc_now,
            "gc001_on_prev_bar_pct": gc_prev,
            "gc001_prev_one_day_implied": (None if gc_prev_one is None
                                           else round(gc_prev_one, 12)),
            "gc001_prev_rule_rel_diff": gc_prev_rel,
            "gc001_prev_gap_rule_rel_diff": gc_prev_gap_rel,
            "gc001_same_bar_rule_rel_diff": gc_now_rel,
        }
        row["class"] = classify(row, rel_g is not None and rel_g <= TOL_REL_NEAR)
        rows.append(row)
        prev, prev_cash = bar, cash
    return rows


def rule_counts(rows):
    """How many rows each candidate rule reproduces, at three tolerances."""
    keys = {
        "ladder3_at_this_rows_cash": "ladder_rel_diff",
        "ladder3_at_the_previous_rows_cash": "ladder_prev_basis_rel_diff",
        "ladder3_at_the_next_bars_quote": "ladder_swapped_rel_diff",
        "ladder3_gross_of_commission_at_this_rows_cash": "ladder_gross_rel_diff",
        "gc001_prior_bar_quote_for_one_day": "gc001_prev_rule_rel_diff",
        "gc001_prior_bar_quote_for_the_calendar_gap": "gc001_prev_gap_rule_rel_diff",
        "gc001_same_bar_quote_for_one_day": "gc001_same_bar_rule_rel_diff",
    }
    out = {}
    for rule in RULES:
        key = keys[rule]
        vals = [r.get(key) for r in rows if r.get(key) is not None]
        out[rule] = {
            "rows": len(rows),
            "rows_with_a_reading": len(vals),
            "exact": sum(1 for v in vals if v <= 0.0),
            "within_1e_4_relative": sum(1 for v in vals if v <= TOL_REL),
            "within_1_percent_relative": sum(1 for v in vals if v <= TOL_REL_NEAR),
            "worst_rel_diff": (round(max(vals), 8) if vals else None),
        }
    return out


# --------------------------------------------------------------------------- #
# summary / verdict
# --------------------------------------------------------------------------- #

def summarise(rows, ticket_rows, led, ladder, ladder_gross, rates, bars):
    import pandas as pd
    dates = ledger_dates(bars)
    cutoff = max([b.get("bar") for b in bars]) if bars else None
    fr = [float(ladder.get(d)) for d in dates
          if ladder is not None and ladder.get(d) is not None]
    frg = [float(ladder_gross.get(d)) for d in dates
           if ladder_gross is not None and ladder_gross.get(d) is not None]
    ledger_ann = round(sum(fr) / len(fr) * BARS_PER_YEAR_LEDGER * 100.0, 4) if fr else None
    ledger_ann_gross = (round(sum(frg) / len(frg) * BARS_PER_YEAR_LEDGER * 100.0, 4)
                        if frg else None)
    gc_ledger = [float(v) for v in rates.reindex(dates).tolist() if v == v]
    gc_ledger_mean = round(sum(gc_ledger) / len(gc_ledger), 4) if gc_ledger else None
    ticket_window = rates[rates.index >= pd.Timestamp(WINDOW_START)]
    if cutoff is not None:
        ticket_window = ticket_window[ticket_window.index <= pd.Timestamp(cutoff)]
    gc_ticket_mean = (round(float(ticket_window.mean()), 4)
                      if len(ticket_window) else None)
    printed = [t["published_mean_accrual_ann_pct"] for t in ticket_rows
               if t.get("published_mean_accrual_ann_pct") is not None]
    printed_mean = round(sum(printed) / len(printed), 4) if printed else None

    window_effect = (None if (gc_ticket_mean is None or gc_ledger_mean is None)
                     else round(gc_ticket_mean - gc_ledger_mean, 4))
    instrument_effect = (None if (gc_ledger_mean is None or ledger_ann is None)
                         else round(gc_ledger_mean - ledger_ann, 4))
    printed_minus_ledger = (None if (printed_mean is None or ledger_ann is None)
                            else round(printed_mean - ledger_ann, 4))
    residual = None
    if None not in (printed_minus_ledger, window_effect, instrument_effect):
        residual = round(printed_minus_ledger - window_effect - instrument_effect, 4)

    by_class = {c: 0 for c in CLASSES}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1

    first_bar = bars[0]["bar"] if bars else None
    s = {
        "ledger_bars": len(rows),
        "ledger_first_bar": first_bar,
        "ledger_last_bar": cutoff,
        "ledger_ladder3_ann_pct": ledger_ann,
        "ledger_ladder3_ann_pct_gross": ledger_ann_gross,
        "ledger_published_frac_ann_pct_mean": (
            round(sum(r["published_frac_ann_pct"] for r in rows
                      if r["published_frac_ann_pct"] is not None)
                  / max(1, sum(1 for r in rows if r["published_frac_ann_pct"] is not None)), 4)
            if any(r["published_frac_ann_pct"] is not None for r in rows) else None),
        "gc001_mean_over_ledger_bars_pct": gc_ledger_mean,
        "gc001_mean_over_ticket_window_pct": gc_ticket_mean,
        "ticket_window_start": WINDOW_START,
        "ticket_window_end": cutoff,
        "ticket_window_bars": int(len(ticket_window)),
        "tickets_total": len(ticket_rows),
        "tickets_printing_a_cash_leg": len(printed),
        "ticket_published_mean_min_pct": min(printed) if printed else None,
        "ticket_published_mean_max_pct": max(printed) if printed else None,
        "printed_minus_accrued_pp": printed_minus_ledger,
        "window_effect_pp": window_effect,
        "instrument_effect_pp": instrument_effect,
        "residual_pp": residual,
        "decomposition_is_arithmetic_not_attribution": True,
        "day_count_ledger": BARS_PER_YEAR_LEDGER,
        "day_count_ticket": BARS_PER_YEAR_TICKET,
        "same_window": False,
        "window_note": ("the ledger accrues bar by bar over its own %d bars from %s; the ticket "
                        "prints a mean over %d bars from %s" %
                        (len(rows), first_bar, int(len(ticket_window)), WINDOW_START)),
        "faces_that_name_their_window": sum(
            1 for t in ticket_rows if t.get("names_a_window")),
        "ledger_names_its_instrument": None,
        "by_class": by_class,
        "rule_reproduction": rule_counts(rows),
        "repo_panel_last_bar": (str(rates.index[-1].date()) if len(rates) else None),
    }
    carry_note = (led.get("carry_note")
                  or ((led.get("engine") or {}).get("cash_leg"))
                  or ((led.get("engine") or {}).get("carry_note")))
    s["ledger_names_its_instrument"] = bool(carry_note)
    s["ledger_carry_note"] = carry_note
    s["ledger_names_its_window"] = bool(
        carry_note and "window" in str(carry_note).lower())
    s["same_window"] = bool(gc_ticket_mean is not None and gc_ledger_mean is not None
                            and abs(gc_ticket_mean - gc_ledger_mean) <= TOL_PP)
    return s


def verdict_of(s):
    if not s.get("ledger_bars") or not s.get("tickets_printing_a_cash_leg"):
        return V_EMPTY
    if s.get("same_window"):
        return V_SAME
    return V_DIFFERENT


def _verdict_line(s):
    if not s.get("ledger_bars"):
        return "no accrued ledger row on disk"
    if not s.get("tickets_printing_a_cash_leg"):
        return ("the ledger accrues over %d bars (%s..%s) but no ticket on disk prints a "
                "cash leg, so there is nothing to compare" %
                (s["ledger_bars"], s["ledger_first_bar"], s["ledger_last_bar"]))
    return ("the ledger accrues %.3f%%/yr from the ladder over its own %d bars (%s..%s), which "
            "is the GC001 mean of that stretch (%.3f%%) less %.3fpp of ladder/commission shape; "
            "the %d tickets print %.3f%%..%.3f%%/yr because they feed a %d-bar window from %s "
            "(GC001 mean there %.3f%%) -- the printed number exceeds the accrued leg by %.3fpp, "
            "of which %.3fpp is window and %.3fpp is instrument, leaving %.3fpp unexplained; "
            "%d of %d faces name the window they used (%s)" %
            (s["ledger_ladder3_ann_pct"] or 0.0, s["ledger_bars"], s["ledger_first_bar"],
             s["ledger_last_bar"], s["gc001_mean_over_ledger_bars_pct"] or 0.0,
             s["instrument_effect_pp"] or 0.0,
             s["tickets_printing_a_cash_leg"], s["ticket_published_mean_min_pct"] or 0.0,
             s["ticket_published_mean_max_pct"] or 0.0, s["ticket_window_bars"],
             WINDOW_START, s["gc001_mean_over_ticket_window_pct"] or 0.0,
             s["printed_minus_accrued_pp"] or 0.0, s["window_effect_pp"] or 0.0,
             s["instrument_effect_pp"] or 0.0, s["residual_pp"] or 0.0,
             (s["faces_that_name_their_window"] or 0)
             + (1 if s["ledger_names_its_window"] else 0),
             s["tickets_total"] + 1,
             "the ledger names its leg (%s) but not its window" %
             (s.get("ledger_carry_note") or "no carry note")))


# --------------------------------------------------------------------------- #
# build / check / verify
# --------------------------------------------------------------------------- #

def build(write=True):
    led = _read_json(LEDGER_PATH)
    bars = ledger_bars(led)
    dates = ledger_dates(bars)
    rates = load_rates()
    ladder, ladder_note = build_ladder(dates)
    ladder_gross, ladder_gross_note = build_ladder(dates, fee_free=True)
    rows = analyse(bars, rates, ladder, ladder_gross)
    tickets = ticket_cash_legs()
    s = summarise(rows, tickets, led, ladder, ladder_gross, rates, bars)
    s["ladder_note"] = ladder_note
    s["ladder_gross_note"] = ladder_gross_note
    cutoff = s["ledger_last_bar"] or "none"
    face = {
        "study": "E587_cash_window",
        "generated_by": "scripts/e587_cash_window.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": cutoff,
        "question": ("do the carry the forward ledger accrues and the mean the ticket's cash_leg "
                     "block prints come from the same repo window?"),
        "rule": ("the ledger's window is its own bar list and its leg is the three-rung ladder "
                 "annualised at 244; the ticket's window is 2020-01-01..cutoff on GC001 "
                 "annualised at 252; a carry 'reproduces' only within the record's own dp "
                 "rounding"),
        "caveats": [
            "GC001 is the short rung, not the ladder the ledger holds: "
            "gc001_mean_over_ledger_bars is a reference reading",
            "the ladder apportions a maturing contract across the bars it spans; it is rebuilt "
            "with scripts/etf_book_cash_ladder.py, not re-implemented here",
            "the window/instrument split is arithmetic, not attribution",
            "244 vs 252 day counts are published as their own fields and folded into no effect",
        ],
        "tickets": tickets,
        "rows": rows,
        "summary": s,
        "verdict": verdict_of(s),
        "verdict_line": _verdict_line(s),
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        for name in ("CASHWINDOW.json", "CASHWINDOW-latest.json"):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
    return face


def face_problems(face):
    p = []
    rows = face.get("rows")
    s = face.get("summary") or {}
    if not isinstance(rows, list) or not rows:
        return ["the face carries no ledger rows"]
    if s.get("ledger_bars") != len(rows):
        p.append("summary.ledger_bars does not match the rows")
    for r in rows:
        if r.get("class") not in CLASSES:
            p.append("row %s carries an undefined class" % r.get("index"))
        abs_d, rel_d = _diff(r.get("published_carry"), r.get("ladder_implied_carry"))
        if abs_d is not None and (
                r.get("ladder_abs_diff") is None or
                abs(float(abs_d) - float(r.get("ladder_abs_diff"))) > 1e-9 or
                (rel_d is not None and r.get("ladder_rel_diff") is not None
                 and abs(float(rel_d) - float(r.get("ladder_rel_diff"))) > 1e-6)):
            p.append("row %s ladder diff does not re-derive from its own two numbers"
                     % r.get("index"))
        if abs_d is None and r.get("ladder_abs_diff") is not None:
            p.append("row %s publishes a ladder diff with nothing to difference"
                     % r.get("index"))
        rel_d = r.get("ladder_rel_diff")
        gross = r.get("ladder_gross_rel_diff")
        want = classify(r, gross is not None and gross <= TOL_REL_NEAR)
        if want != r.get("class"):
            p.append("row %s class does not re-derive" % r.get("index"))
        if r.get("class") == C_LADDER and (rel_d is None or rel_d > TOL_REL):
            p.append("row %s is called the ladder while its carry disagrees with it"
                     % r.get("index"))
        if r.get("class") == C_LADDER_NEAR and (rel_d is None or rel_d > TOL_REL_NEAR):
            p.append("row %s is called the ladder-within-1pct while it disagrees by more"
                     % r.get("index"))
        pf = r.get("published_frac_ann_pct")
        if pf is not None and r.get("published_carry") is not None and r.get("cash_used_as_basis"):
            want_pf = round(float(r["published_carry"]) / float(r["cash_used_as_basis"])
                            * BARS_PER_YEAR_LEDGER * 100.0, 6)
            if abs(want_pf - float(pf)) > 1e-6:
                p.append("row %s annualised carry does not re-derive" % r.get("index"))
    counts = {c: 0 for c in CLASSES}
    for r in rows:
        if r.get("class") in counts:
            counts[r["class"]] += 1
    if counts != (s.get("by_class") or {}):
        p.append("summary.by_class does not re-derive from the rows")
    # the decomposition must add up from the published arms
    pm = s.get("printed_minus_accrued_pp")
    we, ie, res = s.get("window_effect_pp"), s.get("instrument_effect_pp"), s.get("residual_pp")
    if None not in (pm, we, ie, res):
        if abs(float(pm) - float(we) - float(ie) - float(res)) > 1e-6:
            p.append("the window/instrument split does not re-derive to the printed gap")
    pmin, pmax = s.get("ticket_published_mean_min_pct"), s.get("ticket_published_mean_max_pct")
    if pmin is not None and pmax is not None and pmin > pmax:
        p.append("ticket published min exceeds max")
    printed = [t.get("published_mean_accrual_ann_pct") for t in (face.get("tickets") or [])
               if t.get("published_mean_accrual_ann_pct") is not None]
    if printed and s.get("tickets_printing_a_cash_leg") != len(printed):
        p.append("summary ticket count does not re-derive from the ticket block")
    if verdict_of(s) != face.get("verdict"):
        p.append("verdict does not re-derive from the summary")
    rules = (s.get("rule_reproduction") or {})
    if set(rules.keys()) != set(RULES):
        p.append("rule_reproduction does not enumerate every rule")
    else:
        for name, blk in rules.items():
            if blk.get("rows") != len(rows):
                p.append("rule %s does not report the row count" % name)
            if blk.get("rows_with_a_reading") is not None and \
                    (blk.get("within_1_percent_relative") or 0) > blk["rows_with_a_reading"]:
                p.append("rule %s reports more reproductions than readings" % name)
    return p


def _cutoff_on_disk():
    path = os.path.join(OUTDIR, "CASHWINDOW-latest.json")
    if not os.path.exists(path):
        return None
    return _read_json(path).get("evidence_cutoff")


def check():
    path = os.path.join(OUTDIR, "CASHWINDOW-latest.json")
    if not os.path.exists(path):
        print("MISSING %s -- run scripts/e587_cash_window.py build" % path)
        return 1
    face = _read_json(path)
    problems = face_problems(face)
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E587 FAIL %d problem(s)" % len(problems))
        return 1
    s = face["summary"]
    print("E587 OK rows=%d ledger=%.4f%%/yr gc001_ledger_bars=%.4f%% ticket=%s..%s%% "
          "gap=%.4fpp window=%.4fpp instrument=%.4fpp residual=%.4fpp verdict=%s" %
          (s["ledger_bars"], s["ledger_ladder3_ann_pct"] or 0.0,
           s["gc001_mean_over_ledger_bars_pct"] or 0.0,
           s["ticket_published_mean_min_pct"], s["ticket_published_mean_max_pct"],
           s["printed_minus_accrued_pp"] or 0.0, s["window_effect_pp"] or 0.0,
           s["instrument_effect_pp"] or 0.0, s["residual_pp"] or 0.0, face["verdict"]))
    return 0


def verify():
    fresh = build(write=False)
    published_cutoff = _cutoff_on_disk()
    problems = face_problems(fresh)
    if published_cutoff is not None and published_cutoff != fresh["evidence_cutoff"]:
        problems = [] if fresh["evidence_cutoff"] > published_cutoff else problems
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E587 verify FAIL")
        return 1
    s = fresh["summary"]
    print("E587 verify PASS cutoff=%s rows=%d verdict=%s" %
          (fresh["evidence_cutoff"], s["ledger_bars"], fresh["verdict"]))
    return 0


def _row(published_carry, frac, cash=1.0, gc_now=None, gc_prev=None, gross=None,
         next_frac=None):
    implied = None if frac is None else round(cash * frac, 12)
    abs_d, rel_d = _diff(published_carry, implied)
    _, g = _diff(published_carry, None if gross is None else round(cash * gross, 12))
    _, nxt = _diff(published_carry, None if next_frac is None else round(cash * next_frac, 12))
    return {
        "index": 0, "bar": "2026-01-02", "prev_bar": "2026-01-01", "gap_days": 1,
        "cash": cash, "cash_used_as_basis": cash, "published_carry": published_carry,
        "published_frac_ann_pct": (None if not cash else
                                   round(float(published_carry) / cash
                                         * BARS_PER_YEAR_LEDGER * 100.0, 6)),
        "ladder_frac": frac, "ladder_implied_carry": implied,
        "ladder_abs_diff": abs_d, "ladder_rel_diff": rel_d, "ladder_gross_rel_diff": g,
        "ladder_prev_basis_rel_diff": None, "ladder_swapped_rel_diff": nxt,
        "gc001_on_bar_pct": gc_now, "gc001_on_prev_bar_pct": gc_prev,
        "gc001_prev_one_day_implied": None, "gc001_prev_rule_rel_diff": None,
        "gc001_prev_gap_rule_rel_diff": None, "gc001_same_bar_rule_rel_diff": None,
        "class": classify({"ladder_rel_diff": rel_d, "published_carry": published_carry,
                           "gc001_on_bar_pct": gc_now, "gc001_on_prev_bar_pct": gc_prev,
                           "gc001_prev_rule_rel_diff": None,
                           "ladder_swapped_rel_diff": nxt},
                          g is not None and g <= TOL_REL_NEAR),
    }


def selftest():
    """Synthetic checks: the classes, the decomposition and the guard's refusals."""
    bad = []
    # 1. exact ladder reproduction
    r = _row(1e-5, 1e-5)
    if r["class"] != C_LADDER:
        bad.append("an exact ladder row is not classed as the ladder")
    # 2. reproduction up to dp rounding
    r2 = _row(1e-5, 1e-5 * (1.0 + 1e-5))
    if r2["class"] != C_LADDER:
        bad.append("a carry within 1e-4 relative is not classed as the ladder")
    # 3. within the 1% band but not the rounding band
    r2b = _row(1e-5, 1e-5 * 1.006)
    if r2b["class"] != C_LADDER_NEAR:
        bad.append("a carry 0.6%% away from the ladder is not classed as the 1%% band")
    # 4. zero carry past the panel
    r3 = _row(0.0, None, gc_now=None, gc_prev=None)
    if r3["class"] != C_PANEL_SHORT:
        bad.append("a zero carry with no quote on the bar is not classed as panel-short")
    # 5. a carry that reproduces the next bar's ladder (the swap shape seen live)
    r3b = _row(1e-5, 5e-6, next_frac=1e-5)
    if r3b["class"] != C_LADDER_SWAPPED:
        bad.append("a carry equal to the next bar's ladder is not classed as swapped")
    # 6. a carry that reproduces nothing
    r4 = _row(9.9e-5, 1e-5)
    if r4["class"] != C_NO_RULE:
        bad.append("an unexplained carry is not classed as no-rule")
    # 7. gross-of-commission only
    r5 = _row(1e-5, 2e-5, gross=1e-5)
    if r5["class"] != C_LADDER_GROSS:
        bad.append("a carry that is the ladder only with fees waived is not classed as such")
    # 8. the guard accepts a consistent face and refuses doctored ones
    rows = [_row(1e-5, 1e-5), _row(0.0, None)]
    s = {"ledger_bars": 2, "by_class": {c: 0 for c in CLASSES},
         "printed_minus_accrued_pp": 1.0, "window_effect_pp": 0.6,
         "instrument_effect_pp": 0.4, "residual_pp": 0.0,
         "tickets_printing_a_cash_leg": 0, "ticket_published_mean_min_pct": None,
         "ticket_published_mean_max_pct": None,
         "rule_reproduction": {n: {"rows": 2, "rows_with_a_reading": 2, "exact": 0,
                                   "within_1e_4_relative": 0,
                                   "within_1_percent_relative": 0}
                               for n in RULES}}
    for x in rows:
        s["by_class"][x["class"]] += 1
    face = {"study": "E587_cash_window", "rows": rows, "tickets": [], "summary": s,
            "verdict": V_EMPTY}
    if face_problems(face):
        bad.append("the guard refused a consistent synthetic face: %s" % face_problems(face)[:2])
    d1 = json.loads(json.dumps(face))
    d1["rows"][0]["class"] = C_NO_RULE
    if not face_problems(d1):
        bad.append("a class that does not re-derive was accepted")
    d2 = json.loads(json.dumps(face))
    d2["rows"][0]["ladder_abs_diff"] = 0.5
    if not face_problems(d2):
        bad.append("a ladder diff that does not re-derive was accepted")
    d3 = json.loads(json.dumps(face))
    d3["summary"]["residual_pp"] = 0.9
    if not face_problems(d3):
        bad.append("a decomposition that does not add up was accepted")
    d4 = json.loads(json.dumps(face))
    d4["summary"]["by_class"] = {c: 5 for c in CLASSES}
    if not face_problems(d4):
        bad.append("a by_class block that does not re-derive was accepted")
    d5 = json.loads(json.dumps(face))
    d5["verdict"] = V_DIFFERENT
    if not face_problems(d5):
        bad.append("a verdict that does not re-derive was accepted")
    for x in bad:
        print("SELFTEST FAIL %s" % x)
    print("E587 selftest %d/%d" % (13 - len(bad), 13))
    return 1 if bad else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        s = face["summary"]
        print("WROTE %s cutoff=%s rows=%d verdict=%s" %
              (os.path.join(OUTDIR, "CASHWINDOW.json"), face["evidence_cutoff"],
               s["ledger_bars"], face["verdict"]))
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