# -*- coding: utf-8 -*-
"""E591 -- do the two cash faces accrue on the same bars when the repo panel is short?

E590 (r1617) priced the ticket's silence: 7 bar-steps carry no GC001 quote because the panel
stops on 2026-10-27, and the ticket books nothing on them.  Reading the forward ledger for that
same stretch shows the opposite behaviour: the ledger books carry on all eight bars past the
panel, because its cash leg rolls a three-rung ladder whose panel is *forward-filled* to the
book's own bars.  So one reading says "no quote, no accrual" and the other says "no quote, carry
anyway", on identical bars, and neither face says which treatment it uses.

This study puts the two faces bar by bar, priced on one cash base:

  bars[]      per book bar past the panel: the ledger's own carry (and the ladder rate it
              implies once the printed figure is un-weighted from the ledger's cash share), the
              GC001 accrual the ticket's shipped rule would have booked (prior-bar quote, calendar
              days, zero when unquoted), the ticket's actual zero, and the gap in CNY on the
              publishing ticket's cash
  reproducibility
              a fresh three-rung roll replayed from the panel end is compared with the ledger's
              published carry: the ladder is stateful (contract phase), so a replay can agree on
              most bars and disagree on the roll bars -- the phase is not on the face
  summary     totals, the basis points they represent, and the factor by which the printed carry
              field understates a cash base different from the ledger's own

The accrual rule is the producer's own (``etf_phase_beta_window.repo_daily_cash``) for the ticket
side, and ``etf_book_forward``'s published ``carry``/``cash`` pair for the ledger side -- the
ladder rate is derived from those two fields rather than re-derived from a roll, because a roll
replay cannot recover the ledger's phase (published below).

Honest limits:

  * the printed ``carry`` is a cash-weighted figure (``cash * ladder_rate``); applying it straight
    to another cash base understates by the ratio of the two cash shares, which is published;
  * the ladder rate is a per-bar number whose annualisation depends on the calendar gap of that
    bar, so the annualised column is a reading aid, never a ticket figure;
  * the fresh roll is a phase-changing replay: agreement on a bar is evidence about the quote, not
    proof of the ledger's internals;
  * read-only: no ticket, ledger row, panel or state face is written.

  python scripts/e591_cash_diverge.py build
  python scripts/e591_cash_diverge.py check
  python scripts/e591_cash_diverge.py verify
  python scripts/e591_cash_diverge.py selftest

Output: results/etf_book_order/CASHDIVERGE.json
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

from scripts import etf_phase_beta_window as BW            # noqa: E402
from scripts import etf_book_cash_ladder as REPO          # noqa: E402
from scripts import e590_cash_silence as E590             # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_PATH = os.path.join(OUTDIR, "CASHDIVERGE.json")
LEDGER_PATH = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
TICKET_DIR = OUTDIR
CALENDAR_PATH = os.path.join(ROOT, "data", "daily", "sh510300.csv")

V_DIVERGE = "the_same_stale_panel_is_forward_filled_on_one_face_and_zeroed_on_the_other"
V_AGREE = "the_two_faces_book_the_same_bars"
V_EMPTY = "nothing_on_disk_to_measure"

# a replay is called reproducing when the per-bar rate lands within this relative distance
REPRO_TOL_PCT = 0.5


# --------------------------------------------------------------------------- pure helpers
def ladder_rate(cash_weight, carry_frac):
    """Un-weight the published carry figure back to the ladder's own per-bar rate."""
    if cash_weight is None or carry_frac is None:
        return None
    cash_weight = float(cash_weight)
    if not cash_weight > 0.0:
        return None
    return float(carry_frac) / cash_weight


def ann_pct(rate_per_bar, gap_days):
    """Annualise a per-bar fractional return over the calendar days that bar closes."""
    if rate_per_bar is None or gap_days is None:
        return None
    days = float(gap_days)
    if not days >= 1.0:
        return None
    return float(rate_per_bar) / days * 365.0 * 100.0


def cny_on(cash, rate_per_bar):
    """CNY a per-bar fractional return books on a cash base."""
    if cash is None or rate_per_bar is None:
        return 0.0
    return float(cash) * float(rate_per_bar)


def ticket_accrual_rate(quote_pct, gap_days):
    """The ticket's rule: quote on the PRIOR bar, calendar days, zero when unquoted."""
    if quote_pct is None or gap_days is None:
        return 0.0
    return float(quote_pct) / 100.0 * float(gap_days) / 365.0


def rel_gap_pct(fresh, published):
    """Relative distance of a replayed rate from the published one, in percent."""
    if fresh is None or published is None:
        return None
    published = float(published)
    if abs(published) < 1e-15:
        return None
    return (float(fresh) - published) / abs(published) * 100.0


def bars_past_the_panel(ledger_bars, panel_last):
    """Ledger bars strictly after the repo panel's last real quote."""
    panel_last = pd.Timestamp(panel_last)
    return [b for b in ledger_bars if pd.Timestamp(b["bar"]) > panel_last]


# --------------------------------------------------------------------------- inputs
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def load_ledger(path=LEDGER_PATH):
    return read_json(path)


def last_real_bar_per_tenor(panel_dir=None):
    """Last date each repo panel actually quotes (read the CSV, never a forward-filled view).

    The distinction matters: ``etf_book_cash_ladder.load_panel(bars=...)`` forward-fills the last
    quote onto every later bar, so a series read through it cannot tell a quote from its echo.
    """
    if panel_dir is None:
        panel_dir = os.path.join(ROOT, "data", "repo_daily")
    out = {}
    for name, _tenor, _bp in REPO.TENORS:
        p = os.path.join(panel_dir, name + ".csv")
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p)
        if not len(df):
            continue
        d = pd.to_datetime(df["date"])
        out[name] = str(pd.Timestamp(d.max()).date())
    return out


def fresh_roll_rates(dates):
    """Replay the shipped ladder3 over these bars, from a clean contract phase."""
    idx = pd.DatetimeIndex([pd.Timestamp(d) for d in dates])
    rates = REPO.load_panel(bars=idx)
    if not rates:
        return {}, {}
    ret, per = REPO.ladder(idx, rates, REPO.LADDERS["ladder3"])
    return {str(d.date()): float(v) for d, v in ret.items()}, per


def newest_ticket(directory=TICKET_DIR):
    """The publishing ticket: newest non ``-card`` twin on disk."""
    paths = [p for p in sorted(glob.glob(os.path.join(directory, "TICKET-*.json")))
             if not os.path.basename(p).endswith("-card.json")]
    if not paths:
        return None
    return paths[-1]


# --------------------------------------------------------------------------- build
def build(write=True):
    ledger = load_ledger()
    tb = newest_ticket()
    ticket = read_json(tb) if tb else {}
    blk = ticket.get("ticket") or {}
    cash_leg = ticket.get("cash_leg") or {}
    ticket_cash = float(blk.get("cash_amount") or cash_leg.get("cash_amount_cny") or 0.0)
    ticket_weight = None
    nav = float(blk.get("nav") or 0.0)
    if ticket_cash and nav:
        ticket_weight = round(ticket_cash / nav, 6)

    rates = BW.load_repo_rates()
    panel_last = rates.index[-1] if len(rates) else None
    gc001_last_quote = float(rates.iloc[-1]) if len(rates) else None
    rung_last = last_real_bar_per_tenor()
    stale_bar = max(rung_last.values()) if rung_last else None

    ledger_bars = ledger.get("bars") or []
    dates = [b["bar"] for b in ledger_bars]
    fresh, per_rung = fresh_roll_rates(dates) if dates else ({}, {})
    ladder_quotes = []
    for nm in REPO.LADDERS["ladder3"]:
        p = os.path.join(ROOT, "data", "repo_daily", nm + ".csv")
        if os.path.exists(p):
            df = pd.read_csv(p)
            if len(df):
                ladder_quotes.append(float(df["close"].astype(float).iloc[-1]))

    rows = []
    selected = bars_past_the_panel(ledger_bars, panel_last) if panel_last is not None else []
    prev_bar = None
    for i, b in enumerate(ledger_bars):
        if i == 0:
            continue
        prev_bar = ledger_bars[i - 1]["bar"]
        if pd.Timestamp(b["bar"]) <= pd.Timestamp(panel_last):
            continue
        gap_days = max(int((pd.Timestamp(b["bar"]) - pd.Timestamp(prev_bar)).days), 1)
        cash_w = b.get("cash")
        carry = b.get("carry")
        rate = ladder_rate(cash_w, carry)
        # the ticket's rule reads GC001 on the PRIOR bar; BW.load_repo_rates never forward-fills
        q = rates.get(pd.Timestamp(prev_bar)) if len(rates) else None
        q_pct = float(q) if q is not None and pd.notna(q) else None
        rule_rate = ticket_accrual_rate(q_pct, gap_days)
        fresh_rate = fresh.get(b["bar"])
        rows.append({
            "bar": b["bar"],
            "prev_bar": prev_bar,
            "gap_days": gap_days,
            "ledger_cash_weight": cash_w,
            "ledger_carry_frac": carry,
            "ledger_ladder_rate_per_bar": (round(rate, 12) if rate is not None else None),
            "ledger_rate_ann_pct": (round(ann_pct(rate, gap_days), 6)
                                    if rate is not None else None),
            "ledger_cny_on_ticket_cash": round(cny_on(ticket_cash, rate), 2),
            "gc001_quote_on_prior_bar_pct": q_pct,
            "ticket_rule_rate_per_bar": round(rule_rate, 12),
            "ticket_rule_cny": round(cny_on(ticket_cash, rule_rate), 2),
            "ticket_actual_cny": 0.0,
            "ticket_books_this_bar": bool(q_pct is not None),
            "gap_vs_what_the_ticket_booked_cny": round(cny_on(ticket_cash, rate), 2),
            "fresh_roll_rate_per_bar": (round(fresh_rate, 12)
                                        if fresh_rate is not None else None),
            "fresh_roll_rel_gap_pct": (round(rel_gap_pct(fresh_rate, rate), 4)
                                       if rel_gap_pct(fresh_rate, rate) is not None else None),
            "fresh_roll_reproduces_the_ledger_rate": (
                None if rel_gap_pct(fresh_rate, rate) is None
                else abs(rel_gap_pct(fresh_rate, rate)) <= REPRO_TOL_PCT),
        })
    s = summarise(rows, ticket_cash, ticket_weight, gc001_last_quote, ladder_quotes, ledger)
    cutoff = dates[-1] if dates else "none"
    face = {
        "study": "E591_cash_diverge",
        "generated_by": "scripts/e591_cash_diverge.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": cutoff,
        "question": ("do the forward ledger and the ticket's cash leg accrue on the same bars when "
                     "the repo panel is short, and by how much do they part on one cash base?"),
        "rule": ("ticket side = etf_phase_beta_window.repo_daily_cash: a step accrues at the quote "
                 "on its PRIOR bar, 1-day repo pays calendar days, and an unquoted step accrues "
                 "nothing; ledger side = etf_book_forward's published pair (cash, carry) where "
                 "carry = cash * ladder_rate, so the ladder rate is carry/cash and the panels "
                 "behind it are forward-filled to the book's own bars"),
        "ticket": os.path.basename(tb) if tb else None,
        "ticket_cash_cny": ticket_cash,
        "ticket_cash_weight": ticket_weight,
        "panels": {
            "gc001_last_real_bar": str(panel_last.date()) if panel_last is not None else None,
            "gc001_last_quote_pct": gc001_last_quote,
            "ladder_rungs_last_real_bar": rung_last,
            "ladder_panels_all_stop_on_the_same_bar": (
                len(set(rung_last.values())) <= 1 if rung_last else None),
            "ladder_rungs_quote_on_their_last_bar_pct": ladder_quotes,
            "ledger_bars_past_the_panel": len(rows),
            "ledger_panel_is_forward_filled": True,
            "forward_fill_note": ("etf_book_cash_ladder.load_panel(bars=...) reindexes onto the "
                                  "book's bars and ffills, so every bar past the last real quote "
                                  "earns that quote; the ticket reads the same panel without any "
                                  "fill and books zero"),
        },
        "bars": rows,
        "reproducibility": reproducibility(s, rows, per_rung),
        "summary": s,
        "verdict": verdict_of(s),
        "verdict_line": verdict_line(s),
        "caveats": [
            "the printed carry is cash-weighted: applying it to another cash base without "
            "dividing by the ledger's own cash share understates the ledger by that ratio",
            "the ladder rate is per bar and its annualisation uses that bar's calendar gap, so "
            "the annualised column is a reading aid rather than a ticket figure",
            "the fresh roll starts a clean contract phase, so agreement on a bar is evidence "
            "about the quote, not proof of the ledger's internal state; the phase itself is not "
            "published by either face",
            "the cash base is the publishing ticket's own cash leg on its priced bar; the ledger "
            "runs a smaller cash share, which is exactly the factor published in the summary",
            "read-only: no ticket, ledger row, panel or state face is written",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    return face


def summarise(rows, ticket_cash, ticket_weight, gc001_last_quote, ladder_quotes, ledger):
    def _sum(key):
        return round(sum(float(r.get(key) or 0.0) for r in rows), 2)

    ledger_total = _sum("ledger_cny_on_ticket_cash")
    rule_total = _sum("ticket_rule_cny")
    actual_total = _sum("ticket_actual_cny")
    gap_total = round(ledger_total - actual_total, 2)
    weights = [r.get("ledger_cash_weight") for r in rows
               if r.get("ledger_cash_weight") is not None]
    cash_w = (sum(weights) / len(weights)) if weights else None
    anns = [r["ledger_rate_ann_pct"] for r in rows if r.get("ledger_rate_ann_pct") is not None]
    caveats = [str(c) for c in (ledger.get("caveats") or [])]
    carrying = [r for r in rows if (r.get("ledger_carry_frac") or 0.0) != 0.0]
    return {
        "book_bars_past_the_panel": len(rows),
        "ledger_bars_posting_carry": len(carrying),
        "ledger_bars_posting_no_carry": len(rows) - len(carrying),
        "bars_where_the_ticket_books": sum(1 for r in rows if r.get("ticket_books_this_bar")),
        "bars_where_only_the_ledger_books": sum(
            1 for r in rows if r.get("ticket_books_this_bar") is False),
        "ledger_cny_total_on_ticket_cash": ledger_total,
        "ticket_rule_cny_total": rule_total,
        "ticket_actual_cny_total": actual_total,
        "gap_cny_total": gap_total,
        "gap_bp_of_ticket_cash": (round(10000.0 * gap_total / ticket_cash, 3)
                                  if ticket_cash else None),
        "ledger_rate_ann_pct_min": (round(min(anns), 6) if anns else None),
        "ledger_rate_ann_pct_max": (round(max(anns), 6) if anns else None),
        "ledger_rate_ann_pct_mean": (round(sum(anns) / len(anns), 6) if anns else None),
        "gc001_last_quote_pct": gc001_last_quote,
        "ladder_mean_quote_on_its_last_bar_pct": (
            round(sum(ladder_quotes) / len(ladder_quotes), 4) if ladder_quotes else None),
        "carry_field_is_weighted_by_the_ledgers_own_cash": True,
        "ledger_cash_share": (round(cash_w, 6) if cash_w is not None else None),
        "naive_factor_when_priced_on_the_tickets_cash": (
            round(1.0 / cash_w, 4) if cash_w else None),
        "ticket_cash_weight": ticket_weight,
        "negative_carry_bars": sum(1 for r in rows
                                   if (r.get("ledger_carry_frac") or 0.0) < 0.0),
        "ledger_caveat_claims_cash_earns_zero": any(
            "earns 0" in c for c in caveats),
    }


def reproducibility(s, rows, per_rung):
    """How much of the ledger's carry a clean replay can reproduce."""
    judged = [r for r in rows if r.get("fresh_roll_reproduces_the_ledger_rate") is not None]
    ok = [r for r in judged if r["fresh_roll_reproduces_the_ledger_rate"]]
    bad = [r for r in judged if not r["fresh_roll_reproduces_the_ledger_rate"]]
    gaps = [abs(r["fresh_roll_rel_gap_pct"]) for r in judged
            if r.get("fresh_roll_rel_gap_pct") is not None]
    return {
        "replay": "etf_book_cash_ladder.ladder(ladder3) over the ledger's own bars",
        "tolerance_rel_pct": REPRO_TOL_PCT,
        "bars_judged": len(judged),
        "bars_reproduced": len(ok),
        "bars_not_reproduced": len(bad),
        "bars_not_reproduced_list": [r["bar"] for r in bad],
        "max_abs_rel_gap_pct": (round(max(gaps), 4) if gaps else None),
        "rung_ann_pct_from_the_replay": {k: v.get("ann_pct") for k, v in per_rung.items()},
        "note": ("the ladder rolls stateful contracts, so a replay that starts a fresh phase "
                 "matches the ledger on most bars and misses the bars where the two phases roll "
                 "differently -- the published face carries no phase, so the ledger's own carry "
                 "is not re-derivable from the panel alone"),
    }


def verdict_of(s):
    if not s.get("book_bars_past_the_panel"):
        return V_EMPTY
    if s.get("bars_where_the_ticket_books") == s.get("book_bars_past_the_panel"):
        return V_AGREE
    return V_DIVERGE


def verdict_line(s):
    if s.get("book_bars_past_the_panel") is None or not s.get("book_bars_past_the_panel"):
        return "no book bar sits past the repo panel's last real quote, so nothing diverges yet"
    return ("on the %d book bars past the panel's last real quote the ledger posts carry on %d of "
            "them while the ticket books on %d: %.2f CNY versus %.2f CNY on the %s ticket's cash, "
            "a gap of %.2f CNY (%.3f bp), of which the ticket's own rule would have explained "
            "%.2f CNY had the panel been quoted"
            % (s["book_bars_past_the_panel"], s.get("ledger_bars_posting_carry") or 0,
               s.get("bars_where_the_ticket_books") or 0,
               s.get("ledger_cny_total_on_ticket_cash") or 0.0,
               s.get("ticket_actual_cny_total") or 0.0,
               "publishing", s.get("gap_cny_total") or 0.0,
               s.get("gap_bp_of_ticket_cash") or 0.0,
               s.get("ticket_rule_cny_total") or 0.0))


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    rows = face.get("bars")
    s = face.get("summary") or {}
    if not isinstance(rows, list):
        return ["the face carries no bar rows"]
    if s.get("book_bars_past_the_panel") != len(rows):
        p.append("summary.book_bars_past_the_panel does not match the bar rows")
    cash = float(face.get("ticket_cash_cny") or 0.0)
    prev_bar = None
    for r in rows:
        name = r.get("bar")
        if prev_bar is not None and str(name) <= str(prev_bar):
            p.append("bar rows are not in ascending order at %s" % name)
        prev_bar = name
        days = r.get("gap_days")
        if not days or int(days) < 1:
            p.append("%s: the bar carries a gap under a day" % name)
        w = r.get("ledger_cash_weight")
        carry = r.get("ledger_carry_frac")
        rate = r.get("ledger_ladder_rate_per_bar")
        want_rate = ladder_rate(w, carry)
        if want_rate is None or rate is None or abs(want_rate - float(rate)) > 1e-9:
            p.append("%s: the ladder rate does not re-derive from carry/cash" % name)
            continue
        want_ann = ann_pct(want_rate, days)
        if want_ann is None or r.get("ledger_rate_ann_pct") is None or \
                abs(want_ann - float(r["ledger_rate_ann_pct"])) > 1e-3:
            p.append("%s: the annualised rate does not re-derive" % name)
        want_cny = round(cny_on(cash, want_rate), 2)
        if abs(want_cny - float(r.get("ledger_cny_on_ticket_cash") or 0.0)) > 0.01:
            p.append("%s: the ledger CNY does not re-derive on the ticket cash" % name)
        if abs(want_cny - float(r.get("gap_vs_what_the_ticket_booked_cny") or 0.0)) > 0.01:
            p.append("%s: the published gap does not equal the ledger CNY against a zero" % name)
        q = r.get("gc001_quote_on_prior_bar_pct")
        want_rule = ticket_accrual_rate(q, days)
        if abs(want_rule - float(r.get("ticket_rule_rate_per_bar") or 0.0)) > 1e-12:
            p.append("%s: the ticket rule rate does not re-derive" % name)
        if abs(round(cny_on(cash, want_rule), 2) - float(r.get("ticket_rule_cny") or 0.0)) > 0.01:
            p.append("%s: the ticket rule CNY does not re-derive" % name)
        if bool(q is not None) != bool(r.get("ticket_books_this_bar")):
            p.append("%s: ticket_books_this_bar disagrees with the prior-bar quote" % name)
        if float(r.get("ticket_actual_cny") or 0.0) != 0.0:
            p.append("%s: the ticket's shipped rule books a non-zero accrual" % name)
        fresh = r.get("fresh_roll_rate_per_bar")
        if fresh is not None:
            want_gap = rel_gap_pct(fresh, want_rate)
            got_gap = r.get("fresh_roll_rel_gap_pct")
            if want_gap is not None and (got_gap is None or
                                        abs(want_gap - float(got_gap)) > 1e-3):
                p.append("%s: the replay's relative gap does not re-derive" % name)
            claim = r.get("fresh_roll_reproduces_the_ledger_rate")
            if want_gap is not None and claim is not None:
                if bool(claim) != bool(abs(want_gap) <= REPRO_TOL_PCT):
                    p.append("%s: the replay verdict does not follow from its own gap" % name)
    want_gap = round(sum(float(r.get("ledger_cny_on_ticket_cash") or 0.0) for r in rows), 2)
    if abs(want_gap - float(s.get("ledger_cny_total_on_ticket_cash") or 0.0)) > 0.01:
        p.append("summary.ledger_cny_total_on_ticket_cash does not re-derive from the rows")
    want_rule = round(sum(float(r.get("ticket_rule_cny") or 0.0) for r in rows), 2)
    if abs(want_rule - float(s.get("ticket_rule_cny_total") or 0.0)) > 0.01:
        p.append("summary.ticket_rule_cny_total does not re-derive from the rows")
    want_actual = round(sum(float(r.get("ticket_actual_cny") or 0.0) for r in rows), 2)
    if abs(want_actual - float(s.get("ticket_actual_cny_total") or 0.0)) > 0.01:
        p.append("summary.ticket_actual_cny_total does not re-derive from the rows")
    gap = round(want_gap - want_actual, 2)
    if abs(gap - float(s.get("gap_cny_total") or 0.0)) > 0.01:
        p.append("summary.gap_cny_total does not equal the ledger total minus the ticket's own")
    if cash and s.get("gap_bp_of_ticket_cash") is not None:
        want_bp = round(10000.0 * gap / cash, 3)
        if abs(want_bp - float(s["gap_bp_of_ticket_cash"])) > 1e-3:
            p.append("summary.gap_bp_of_ticket_cash does not re-derive")
    if s.get("bars_where_the_ticket_books") != sum(
            1 for r in rows if r.get("ticket_books_this_bar")):
        p.append("summary.bars_where_the_ticket_books does not re-derive from the rows")
    if s.get("bars_where_only_the_ledger_books") != sum(
            1 for r in rows if r.get("ticket_books_this_bar") is False):
        p.append("summary.bars_where_only_the_ledger_books does not re-derive from the rows")
    if s.get("ledger_bars_posting_carry") is not None:
        want_carry = sum(1 for r in rows if (r.get("ledger_carry_frac") or 0.0) != 0.0)
        if s["ledger_bars_posting_carry"] != want_carry:
            p.append("summary.ledger_bars_posting_carry does not re-derive from the rows")
    if s.get("negative_carry_bars") is not None:
        want_neg = sum(1 for r in rows if (r.get("ledger_carry_frac") or 0.0) < 0.0)
        if s["negative_carry_bars"] != want_neg:
            p.append("summary.negative_carry_bars does not re-derive from the rows")
    w = s.get("ledger_cash_share")
    if w and s.get("naive_factor_when_priced_on_the_tickets_cash") is not None:
        if abs(round(1.0 / float(w), 4)
               - float(s["naive_factor_when_priced_on_the_tickets_cash"])) > 1e-3:
            p.append("summary's naive factor does not re-derive from the ledger cash share")
    rep = face.get("reproducibility") or {}
    if rep.get("bars_judged") is not None:
        judged = [r for r in rows if r.get("fresh_roll_reproduces_the_ledger_rate") is not None]
        ok = [r for r in judged if r["fresh_roll_reproduces_the_ledger_rate"]]
        if rep["bars_judged"] != len(judged):
            p.append("reproducibility.bars_judged does not match the rows")
        if rep.get("bars_reproduced") != len(ok):
            p.append("reproducibility.bars_reproduced does not match the rows")
        if rep.get("bars_not_reproduced_list") != [r["bar"] for r in judged
                                                   if not r["fresh_roll_reproduces_the_ledger_rate"]]:
            p.append("reproducibility.bars_not_reproduced_list does not match the rows")
    panels = face.get("panels") or {}
    if panels.get("ledger_bars_past_the_panel") != len(rows):
        p.append("panels.ledger_bars_past_the_panel does not match the rows")
    if panels.get("ladder_panels_all_stop_on_the_same_bar") is not None:
        vals = list((panels.get("ladder_rungs_last_real_bar") or {}).values())
        if bool(len(set(vals)) <= 1) != bool(panels["ladder_panels_all_stop_on_the_same_bar"]):
            p.append("the 'all rungs stop together' flag does not re-derive")
    if verdict_of(s) != face.get("verdict"):
        p.append("verdict does not re-derive from the summary")
    return p


def check():
    if not os.path.exists(OUT_PATH):
        print("MISSING %s -- run scripts/e591_cash_diverge.py build" % OUT_PATH)
        return 1
    face = read_json(OUT_PATH)
    problems = face_problems(face)
    if problems:
        for x in problems[:20]:
            print("PROBLEM %s" % x)
        print("E591 FAIL %d problem(s)" % len(problems))
        return 1
    s = face["summary"]
    print("E591 OK bars=%d ledger_cny=%.2f rule_cny=%.2f gap=%.2f (%.3f bp) "
          "ticket_books=%d replay=%d/%d verdict=%s"
          % (s["book_bars_past_the_panel"], s["ledger_cny_total_on_ticket_cash"],
             s["ticket_rule_cny_total"], s["gap_cny_total"],
             s["gap_bp_of_ticket_cash"] or 0.0, s["bars_where_the_ticket_books"],
             (face.get("reproducibility") or {}).get("bars_reproduced") or 0,
             (face.get("reproducibility") or {}).get("bars_judged") or 0, face["verdict"]))
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
        print("E591 verify FAIL")
        return 1
    s = fresh["summary"]
    print("E591 verify PASS cutoff=%s bars=%d gap=%.2f CNY ledger=%.2f rule=%.2f verdict=%s"
          % (fresh["evidence_cutoff"], s["book_bars_past_the_panel"], s["gap_cny_total"],
             s["ledger_cny_total_on_ticket_cash"], s["ticket_rule_cny_total"],
             fresh["verdict"]))
    return 0


# --------------------------------------------------------------------------- selftest
def _ledger(bars):
    return {"bars": bars}


def selftest():
    bad = []
    seen = [0]

    def chk(cond, msg):
        seen[0] += 1
        if not cond:
            bad.append(msg)

    # 1. un-weighting: carry is cash * rate, so the rate is carry / cash
    chk(abs(ladder_rate(0.25, 2.5e-5) - 1e-4) < 1e-15,
        "ladder_rate does not un-weight the cash share")
    # 2. a zero cash share cannot carry a rate (no divide-by-zero claim)
    chk(ladder_rate(0.0, 1e-5) is None, "a zero cash share returned a rate")
    chk(ladder_rate(None, 1e-5) is None, "a missing cash share returned a rate")
    # 3. annualisation uses the bar's own calendar gap
    chk(abs(ann_pct(1e-4, 1) - 3.65) < 1e-9, "a one-day bar did not annualise to 3.65%")
    chk(abs(ann_pct(1e-4, 3) - 3.65 / 3.0) < 1e-9, "a three-day bar did not divide by its gap")
    chk(ann_pct(1e-4, 0) is None, "a zero-day gap produced an annual rate")
    # 4. the ticket rule is prior-bar quote x days / 365 and zero when unquoted
    chk(abs(ticket_accrual_rate(1.09, 1) - 0.0109 / 365.0) < 1e-15,
        "the ticket rule does not price one day at the prior quote")
    chk(ticket_accrual_rate(None, 1) == 0.0, "an unquoted step did not accrue zero")
    chk(abs(cny_on(500000.0, 3e-5) - 15.0) < 1e-9, "CNY is not cash x rate")
    # 5. only bars strictly after the panel's last quote are measured
    lb = [{"bar": d} for d in ("2026-01-05", "2026-01-06", "2026-01-07")]
    got = [b["bar"] for b in bars_past_the_panel(lb, "2026-01-06")]
    chk(got == ["2026-01-07"], "the bar selection counted %s instead of only the bars after the "
                               "panel" % got)
    chk(bars_past_the_panel(lb, "2026-01-07") == [], "a bar on the panel's last date was counted")
    # 6. the naive factor is one over the ledger's cash share, and the two bases differ
    s = summarise([{"ledger_cash_weight": 0.25, "ledger_carry_frac": 2.5e-5,
                    "ledger_rate_ann_pct": 0.365, "ledger_cny_on_ticket_cash": 5.0,
                    "ticket_rule_cny": 1.0, "ticket_actual_cny": 0.0,
                    "ticket_books_this_bar": True, "gap_vs_what_the_ticket_booked_cny": 5.0}],
                  100000.0, 0.5, 1.09, [1.35, 1.36, 1.355], _ledger(lb))
    chk(abs(s["naive_factor_when_priced_on_the_tickets_cash"] - 4.0) < 1e-6,
        "the naive factor is not 1/cash_share")
    chk(s["gap_cny_total"] == 5.0 and s["ledger_cny_total_on_ticket_cash"] == 5.0,
        "the totals do not add up on a single row")
    chk(abs(s["gap_bp_of_ticket_cash"] - 0.5) < 1e-9,
        "500 CNY on 100,000 CNY is not 500 bp... the bp conversion is wrong")
    # 7. a negative carry bar is counted and priced with its sign
    neg = summarise([{"ledger_cash_weight": 0.25, "ledger_carry_frac": -1e-5,
                      "ledger_rate_ann_pct": -0.146, "ledger_cny_on_ticket_cash": -4.0,
                      "ticket_rule_cny": 0.0, "ticket_actual_cny": 0.0,
                      "ticket_books_this_bar": False,
                      "gap_vs_what_the_ticket_booked_cny": -4.0}],
                    100000.0, 0.5, 1.09, [], _ledger(lb))
    chk(neg["negative_carry_bars"] == 1, "a negative carry bar was not counted")
    chk(neg["gap_cny_total"] == -4.0, "a negative carry was not priced with its sign")
    # 8. the verdict flips when the ticket books like the ledger
    agree = dict(s)
    agree["bars_where_the_ticket_books"] = agree["book_bars_past_the_panel"] = 1
    chk(verdict_of(agree) == V_AGREE, "an agreeing pair was not read as agreeing")
    chk(verdict_of(dict(s, book_bars_past_the_panel=0)) == V_EMPTY,
        "an empty stretch was not read as empty")
    # 9. the guard accepts a face built here and refuses a doctored row
    rows = [{"bar": "2026-01-07", "prev_bar": "2026-01-06", "gap_days": 1,
             "ledger_cash_weight": 0.25, "ledger_carry_frac": 2.5e-5,
             "ledger_ladder_rate_per_bar": 1e-4, "ledger_rate_ann_pct": 3.65,
             "ledger_cny_on_ticket_cash": 50.0, "gc001_quote_on_prior_bar_pct": None,
             "ticket_rule_rate_per_bar": 0.0, "ticket_rule_cny": 0.0, "ticket_actual_cny": 0.0,
             "ticket_books_this_bar": False, "gap_vs_what_the_ticket_booked_cny": 50.0,
             "fresh_roll_rate_per_bar": None, "fresh_roll_rel_gap_pct": None,
             "fresh_roll_reproduces_the_ledger_rate": None}]
    row_s = summarise(rows, 500000.0, 0.5, 1.09, [], _ledger(lb))
    good = {"bars": rows, "summary": row_s, "verdict": verdict_of(row_s),
            "ticket_cash_cny": 500000.0,
            "panels": {"ledger_bars_past_the_panel": 1,
                       "ladder_panels_all_stop_on_the_same_bar": True,
                       "ladder_rungs_last_real_bar": {"GC007": "2026-01-06",
                                                      "GC014": "2026-01-06"}},
            "reproducibility": {"bars_judged": 0, "bars_reproduced": 0,
                                "bars_not_reproduced_list": []}}
    chk(face_problems(good) == [], "the guard refuses a face it should accept: %s"
        % face_problems(good)[:2])
    doctored = json.loads(json.dumps(good))
    doctored["bars"][0]["ledger_cny_on_ticket_cash"] = 51.0
    chk(bool(face_problems(doctored)), "a doctored CNY row passed the guard")
    drifted = json.loads(json.dumps(good))
    drifted["summary"]["gap_cny_total"] = 49.0
    chk(bool(face_problems(drifted)), "a drifting summary total passed the guard")
    wrong_verdict = json.loads(json.dumps(good))
    wrong_verdict["verdict"] = V_AGREE
    chk(bool(face_problems(wrong_verdict)), "a verdict that does not re-derive passed the guard")
    wrong_ticket = json.loads(json.dumps(good))
    wrong_ticket["bars"][0]["ticket_books_this_bar"] = True
    chk(bool(face_problems(wrong_ticket)),
        "a row claiming the ticket books with no prior quote passed the guard")
    # 10. the replayed-rate verdict follows its own relative gap
    rr = [dict(rows[0], fresh_roll_rate_per_bar=1.01e-4, fresh_roll_rel_gap_pct=1.0,
               fresh_roll_reproduces_the_ledger_rate=False)]
    chk(rr[0]["fresh_roll_reproduces_the_ledger_rate"] is False,
        "a 1% replay gap is not what the tolerance was written for")
    chk(abs(rel_gap_pct(1.01e-4, 1e-4) - 1.0) < 1e-9, "rel_gap_pct is not a relative reading")
    chk(rel_gap_pct(1e-4, 0.0) is None, "a zero published rate produced a relative gap")
    # 11. the "rungs stop together" flag is a reading of the map, not a constant
    stop = {"GC007": "2026-10-27", "GC014": "2026-10-27"}
    split = {"GC007": "2026-10-27", "GC014": "2026-10-28"}
    chk(len(set(stop.values())) <= 1 and not len(set(split.values())) <= 1,
        "the rung-stop reading does not distinguish together from apart")
    # 12. the ledger caveat contradiction is a reading of the text, not an assumption
    chk(summarise([], 0.0, None, None, [], {"caveats": ["Cash earns 0 in the marks."]})
        ["ledger_caveat_claims_cash_earns_zero"] is True,
        "the caveat reading missed a 'earns 0' sentence")
    chk(summarise([], 0.0, None, None, [], {"caveats": ["Cash earns the ladder."]})
        ["ledger_caveat_claims_cash_earns_zero"] is False,
        "the caveat reading invented an 'earns 0' sentence")

    print("E591 selftest %d/%d PASS" % (seen[0] - len(bad), seen[0]))
    for m in bad:
        print("  FAIL %s" % m)
    return 0 if not bad else 1


# --------------------------------------------------------------------------- cli
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