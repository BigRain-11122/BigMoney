# -*- coding: utf-8 -*-
"""E583 -- re-issue every ticket this book has already published, priced on the bar it names.

r1611 (bm-b) fixed the producer: ``etf_book_order.build_ticket`` now takes ``close_price`` /
``price_bar`` / ``decision_bar``, so a ticket dated B can be priced at B.  That fix answers the
question for new tickets and says nothing about the ones already on disk.  Each published ticket
file is named after a bar; this study asks, for every one of them, whether the money on the sheet
was priced on that bar.

Per ticket file it publishes:

  named_bar           the bar the file name carries (TICKET-YYYY-MM-DD.json)
  decision_bar        the bar the ranking was taken on (``book_decided_at``)
  declares_its_bar    whether the file states a pricing bar at all (only r1611's ticket does)
  class               priced_on_the_bar_it_names / priced_on_an_earlier_bar /
                      priced_on_a_later_bar / no_order_sheet / named_bar_not_on_panel
  legs[]              per leg: the price on the sheet, the close on the named bar, whether those
                      agree, whether it agrees with the decision bar's close instead, and how
                      many bars in the whole panel round to that same 4dp price

and two money arms, because they answer different questions:

  keep_shares_at_named_bar   the sheet's own share counts executed on the named bar -- what a
                             follower would actually have paid versus what the sheet printed
  reissued_at_named_bar      the same weights rebuilt into whole lots on the named bar -- what
                             ``build_ticket`` would emit today for that bar

The gap between the two arms is the point: the weights were never wrong, so re-issuing barely
moves the total; the whole-lot counts were computed on a nine-day-old close, and that is where the
money is.

A price is a weak witness.  ``159263`` printed 1.148 on the 2026-10-23 sheet and that same 4dp
price also appears on 2026-01-27, 2026-08-11 and 2026-11-04, so "the newest bar whose close equals
this price" would date the leg to a bar five days *after* the ticket.  Legs are therefore decided
by the file's own fields, and the coincidence count is published as its own column.

  python scripts/e583_ticket_repricing.py build
  python scripts/e583_ticket_repricing.py check
  python scripts/e583_ticket_repricing.py verify
  python scripts/e583_ticket_repricing.py selftest

Output: results/state_tilt/REPRICEDTICKETS-<panel cutoff>.json + repricedtickets_latest.json
Read-only over the ticket files and the panel.  No ticket is rewritten; no ledger row is booked;
no verdict about the returns of this book is made here.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")

LOT = 100
NDP = 4

C_OWN = "priced_on_the_bar_it_names"
C_EARLIER = "priced_on_an_earlier_bar"
C_LATER = "priced_on_a_later_bar"
C_NO_SHEET = "no_order_sheet"
C_NO_PANEL = "named_bar_not_on_panel"
CLASSES = (C_OWN, C_EARLIER, C_LATER, C_NO_SHEET, C_NO_PANEL)

L_ON = "priced_on_the_named_bar"
L_DECISION = "priced_on_the_decision_bar"
L_COINCIDES = "the_named_bar_and_the_decision_bar_share_this_price"
L_NEITHER = "priced_on_neither_bar_named_in_the_file"
L_NO_CLOSE = "no_close_on_the_named_bar"
LEG_CLASSES = (L_ON, L_DECISION, L_COINCIDES, L_NEITHER, L_NO_CLOSE)

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def panel():
    from scripts import etf_composite_pf as F
    close, openp, amt, feats = F.build_panel()
    return close


# --------------------------------------------------------------------------- #
# per leg
# --------------------------------------------------------------------------- #

def price_witness(series, px):
    """Bars in the whole panel whose close rounds to ``px`` at 4dp (oldest first)."""
    if px is None:
        return []
    hit = series.dropna()
    hit = hit[hit.round(NDP) == round(float(px), NDP)]
    return [str(d.date()) if hasattr(d, "date") else str(d) for d in hit.index]


def leg_row(leg, close, named_bar, decision_bar):
    sym = leg.get("symbol")
    px = leg.get("price")
    row = {
        "symbol": sym,
        "weight": leg.get("weight"),
        "price": px,
        "shares": leg.get("shares"),
        "amount": leg.get("amount"),
        "price_on_named_bar": None,
        "price_on_decision_bar": None,
        "price_bars_sharing_this_price": 0,
        "class": L_NO_CLOSE,
    }
    if sym is None or sym not in close.columns:
        row["class"] = L_NO_CLOSE
        return row
    ser = close[sym]
    on_named = ser.get(named_bar) if named_bar in ser.index else None
    on_dec = ser.get(decision_bar) if decision_bar in ser.index else None
    row["price_on_named_bar"] = None if on_named is None or _isnan(on_named) else round(
        float(on_named), NDP)
    row["price_on_decision_bar"] = None if on_dec is None or _isnan(on_dec) else round(
        float(on_dec), NDP)
    row["price_bars_sharing_this_price"] = len(price_witness(ser, px))
    if px is None:
        row["class"] = L_NO_CLOSE
        return row
    same_named = row["price_on_named_bar"] is not None and abs(
        row["price_on_named_bar"] - round(float(px), NDP)) < 1e-9
    same_dec = row["price_on_decision_bar"] is not None and abs(
        row["price_on_decision_bar"] - round(float(px), NDP)) < 1e-9
    if row["price_on_named_bar"] is None:
        row["class"] = L_NO_CLOSE
    elif same_named and same_dec:
        row["class"] = L_COINCIDES
    elif same_named:
        row["class"] = L_ON
    elif same_dec:
        row["class"] = L_DECISION
    else:
        row["class"] = L_NEITHER
    return row


def _isnan(v):
    try:
        return v != v
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# per ticket
# --------------------------------------------------------------------------- #

def named_bar_of(path):
    m = DATE_RE.search(os.path.basename(path))
    return m.group(1) if m else None


def analyse_ticket(path, close):
    d = _read_json(path)
    tk = d.get("ticket") or {}
    order = tk.get("order") or []
    named = named_bar_of(path)
    decision = d.get("book_decided_at")
    declared = tk.get("pricing_bar") or d.get("pricing_bar")
    row = {
        "file": os.path.basename(path),
        "named_bar": named,
        "decision_bar": decision,
        "declares_its_pricing_bar": declared is not None,
        "declared_pricing_bar": declared,
        "nav": tk.get("nav"),
        "legs_total": len(order),
        "legs": [],
        "money": None,
        "class": None,
    }
    if named is None or named not in close.index:
        row["class"] = C_NO_PANEL
        return row
    if not order:
        row["class"] = C_NO_SHEET
        return row
    legs = [leg_row(leg, close, named, decision) for leg in order]
    row["legs"] = legs

    by_class = {c: 0 for c in LEG_CLASSES}
    for lg in legs:
        by_class[lg["class"]] += 1
    row["leg_classes"] = by_class

    nav = tk.get("nav")
    issued = sum(float(l["amount"]) for l in order if l.get("amount") is not None)
    keep = 0.0
    reissued = 0.0
    shares_delta = 0
    for l in order:
        sym = l.get("symbol")
        if sym not in close.columns or named not in close.index:
            continue
        px = close[sym].get(named)
        if px is None or _isnan(px) or float(px) <= 0:
            continue
        px = float(px)
        shares = int(l.get("shares") or 0)
        keep += shares * px
        want = float(nav) * float(l.get("weight") or 0.0)
        lots = int(want // (px * LOT))
        reissued += lots * LOT * px
        shares_delta += lots * LOT - shares

    money = {
        "issued_book_amount": round(issued, 2),
        "keep_shares_at_named_bar": round(keep, 2),
        "keep_shares_delta_cny": round(keep - issued, 2),
        "reissued_at_named_bar": round(reissued, 2),
        "reissued_delta_cny": round(reissued - issued, 2),
        "shares_delta_if_reissued": shares_delta,
    }
    if nav:
        money["keep_shares_delta_pct_nav"] = round(100.0 * (keep - issued) / float(nav), 4)
        money["reissued_delta_pct_nav"] = round(100.0 * (reissued - issued) / float(nav), 4)
    else:
        money["keep_shares_delta_pct_nav"] = None
        money["reissued_delta_pct_nav"] = None
    row["money"] = money

    n_on = by_class[L_ON] + by_class[L_COINCIDES]
    if n_on == len(legs):
        row["class"] = C_OWN
    elif by_class[L_DECISION] and (decision or "") < named:
        row["class"] = C_EARLIER
    elif by_class[L_DECISION] and (decision or "") > named:
        row["class"] = C_LATER
    else:
        row["class"] = C_EARLIER if (decision or "") < named else C_LATER
    return row


# --------------------------------------------------------------------------- #
# summary / verdict
# --------------------------------------------------------------------------- #

def summarise(rows):
    sheets = [r for r in rows if r["class"] != C_NO_SHEET]
    legs = [lg for r in rows for lg in (r.get("legs") or [])]
    leg_by_class = {c: 0 for c in LEG_CLASSES}
    for lg in legs:
        leg_by_class[lg["class"]] += 1
    keep_pcts = [r["money"]["keep_shares_delta_pct_nav"] for r in sheets
                 if r.get("money") and r["money"].get("keep_shares_delta_pct_nav") is not None]
    reiss_pcts = [r["money"]["reissued_delta_pct_nav"] for r in sheets
                  if r.get("money") and r["money"].get("reissued_delta_pct_nav") is not None]
    stray = [r for r in sheets if r["class"] != C_OWN]
    return {
        "tickets_total": len(rows),
        "order_sheets": len(sheets),
        "tickets_without_an_order_sheet": len(rows) - len(sheets),
        "sheets_that_declare_a_pricing_bar": sum(
            1 for r in rows if r["declares_its_pricing_bar"]),
        "sheets_priced_on_the_bar_they_name": sum(1 for r in rows if r["class"] == C_OWN),
        "sheets_priced_on_an_earlier_bar": sum(1 for r in rows if r["class"] == C_EARLIER),
        "sheets_priced_on_a_later_bar": sum(1 for r in rows if r["class"] == C_LATER),
        "legs_total": len(legs),
        "leg_adjudication": leg_by_class,
        "legs_whose_price_is_not_a_unique_witness": sum(
            1 for lg in legs if lg.get("price_bars_sharing_this_price", 0) > 1),
        "keep_shares_delta_pct_nav_worst": min(keep_pcts) if keep_pcts else None,
        "keep_shares_delta_pct_nav_best": max(keep_pcts) if keep_pcts else None,
        "keep_shares_delta_cny_total": round(sum(
            r["money"]["keep_shares_delta_cny"] for r in sheets if r.get("money")), 2),
        "reissued_delta_pct_nav_worst": min(reiss_pcts) if reiss_pcts else None,
        "reissued_delta_pct_nav_best": max(reiss_pcts) if reiss_pcts else None,
        "sheets_whose_money_moves_with_the_bar": sum(
            1 for r in sheets
            if r.get("money") and abs(r["money"]["keep_shares_delta_cny"]) > 1.0),
    }


def _verdict(s):
    if not s["order_sheets"]:
        return "no_published_order_sheet_to_measure"
    if s["sheets_priced_on_the_bar_they_name"] == s["order_sheets"]:
        return "every_published_order_sheet_prices_on_the_bar_it_names"
    return "the_share_counts_are_what_the_stale_bar_corrupted"


def _verdict_line(s):
    if not s["order_sheets"]:
        return "no published order sheet on disk, so this study has no population"
    n = s["order_sheets"] - s["sheets_priced_on_the_bar_they_name"]
    if not n:
        return ("all %d order sheets price on the bar their file name carries, and %d of them "
                "declare that bar in the payload" % (s["order_sheets"],
                                                     s["sheets_that_declare_a_pricing_bar"]))
    lo = abs(s["keep_shares_delta_pct_nav_best"] or 0.0)
    hi = abs(s["keep_shares_delta_pct_nav_worst"] or 0.0)
    rlo = abs(s["reissued_delta_pct_nav_best"] or 0.0)
    rhi = abs(s["reissued_delta_pct_nav_worst"] or 0.0)
    if lo > hi:
        lo, hi = hi, lo
    if rlo > rhi:
        rlo, rhi = rhi, rlo
    side = "less" if (s["keep_shares_delta_pct_nav_worst"] or 0) < 0 else "more"
    return ("%d of %d published order sheets price on a bar earlier than the one they are named "
            "after, and %d of them declares a pricing bar at all: a follower executing those "
            "sheets on their own bar would have spent %.2f%%..%.2f%% of NAV %s for the same "
            "shares, while re-issuing the same weights into whole lots on that bar moves the "
            "total by only %.2f%%..%.2f%% -- the weights were never stale, the whole-lot counts "
            "were"
            % (n, s["order_sheets"], s["sheets_that_declare_a_pricing_bar"],
               lo, hi, side, rlo, rhi))


# --------------------------------------------------------------------------- #
# build / check / verify
# --------------------------------------------------------------------------- #

def build(write=True):
    close = panel()
    cutoff = str(close.index[-1].date())
    paths = sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json")))
    rows = [analyse_ticket(p, close) for p in paths]
    s = summarise(rows)
    face = {
        "study": "E583_ticket_repricing",
        "generated_by": "scripts/e583_ticket_repricing.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": cutoff,
        "rule": ("the named bar is the date in the ticket file name; the decision bar is the "
                 "file's own book_decided_at; a leg is adjudicated by those two fields and never "
                 "by 'the newest bar whose close happens to equal this price'"),
        "rows": rows,
        "summary": s,
        "verdict": _verdict(s),
        "verdict_line": _verdict_line(s),
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        name = "REPRICEDTICKETS-%s.json" % cutoff
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        with io.open(os.path.join(OUTDIR, "repricedtickets_latest.json"), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return face


def face_problems(face):
    p = []
    rows = face.get("rows")
    if not isinstance(rows, list) or not rows:
        return ["the face carries no ticket rows"]
    s = face.get("summary") or {}
    for r in rows:
        if r.get("class") not in CLASSES:
            p.append("%s: unknown class %r" % (r.get("file"), r.get("class")))
        legs = r.get("legs") or []
        if r.get("legs_total") != len(legs):
            p.append("%s: legs_total does not match the leg list" % r.get("file"))
        if r.get("class") == C_NO_SHEET and legs:
            p.append("%s: classified as no order sheet but carries legs" % r.get("file"))
        if r.get("class") == C_NO_SHEET and r.get("money") is not None:
            p.append("%s: a ticket with no order sheet publishes money" % r.get("file"))
        if r.get("money"):
            m = r["money"]
            need = ("issued_book_amount", "keep_shares_at_named_bar", "keep_shares_delta_cny",
                    "reissued_at_named_bar", "reissued_delta_cny")
            missing = [k for k in need if m.get(k) is None]
            if missing:
                p.append("%s: the money block is missing %s"
                         % (r.get("file"), ",".join(missing)))
                continue
            if abs((m["keep_shares_at_named_bar"] - m["keep_shares_delta_cny"])
                   - m["issued_book_amount"]) > 0.02:
                p.append("%s: the keep-shares delta does not re-derive from its two totals"
                         % r.get("file"))
            if abs((m["reissued_at_named_bar"] - m["reissued_delta_cny"])
                   - m["issued_book_amount"]) > 0.02:
                p.append("%s: the re-issue delta does not re-derive from its two totals"
                         % r.get("file"))
            nav = r.get("nav")
            if nav and m.get("keep_shares_delta_pct_nav") is not None:
                want = round(100.0 * m["keep_shares_delta_cny"] / float(nav), 4)
                if abs(want - m["keep_shares_delta_pct_nav"]) > 2e-3:
                    p.append("%s: the keep-shares pct-of-NAV does not re-derive" % r.get("file"))
        by_class = r.get("leg_classes") or {}
        if by_class and sum(by_class.values()) != len(legs):
            p.append("%s: the leg classes do not cover every leg" % r.get("file"))
        if r.get("class") == C_OWN and by_class:
            if (by_class.get(L_ON, 0) + by_class.get(L_COINCIDES, 0)) != len(legs):
                p.append("%s: called priced-on-its-own-bar while a leg prices elsewhere"
                         % r.get("file"))
    if s.get("tickets_total") != len(rows):
        p.append("the summary ticket count does not match the published rows")
    if (s.get("sheets_priced_on_the_bar_they_name", 0)
            + s.get("sheets_priced_on_an_earlier_bar", 0)
            + s.get("sheets_priced_on_a_later_bar", 0)) != s.get("order_sheets"):
        p.append("the sheet classes do not cover every order sheet")
    if s.get("legs_total") != sum((s.get("leg_adjudication") or {}).values()):
        p.append("the summary leg count does not re-derive from the leg classes")
    return p


def check():
    face = _read_json(os.path.join(OUTDIR, "repricedtickets_latest.json"))
    problems = face_problems(face)
    for x in problems:
        print("CHECK FAIL %s" % x)
    if not problems:
        print("CHECK PASS %s" % face.get("verdict_line"))
    return 0 if not problems else 1


def verify():
    published = _read_json(os.path.join(OUTDIR, "repricedtickets_latest.json"))
    fresh = build(write=False)
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "evidence_cutoff"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if (fresh.get("summary") or {}) != (published.get("summary") or {}):
        problems.append("the summary drifted between the published face and a live rebuild")
    for a, b in zip(fresh.get("rows") or [], published.get("rows") or []):
        if (a.get("file"), a.get("class"), a.get("legs_total")) != (
                b.get("file"), b.get("class"), b.get("legs_total")):
            problems.append("%s: the class or leg count changed on a live rebuild" % a.get("file"))
    for x in problems:
        print("VERIFY FAIL %s" % x)
    if not problems:
        print("VERIFY PASS %d tickets re-derived against the panel" % len(published.get("rows") or []))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- #
# selftest -- closed form, no panel, no disk
# --------------------------------------------------------------------------- #
def selftest():
    import pandas as pd

    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want)))

    def near(name, got, want, tol=1e-6):
        ok.append((name, abs(got - want) <= tol, "%r != %r" % (got, want)))

    bars = ["2026-10-14", "2026-10-23", "2026-10-26"]
    idx = pd.to_datetime(bars)
    close = pd.DataFrame({
        "AAA": [10.00, 9.50, 9.60],
        "BBB": [20.00, 19.00, 19.20],
        "CCC": [5.000, 5.000, 5.000],
    }, index=idx)

    # ---- leg adjudication -------------------------------------------------
    leg_on_dec = {"symbol": "AAA", "weight": 0.5, "price": 10.00, "shares": 50000,
                  "amount": 500000.0}
    r = leg_row(leg_on_dec, close, "2026-10-23", "2026-10-14")
    eq("a leg priced at the decision bar is classed as such", r["class"], L_DECISION)
    eq("its named-bar close is the named bar's close", r["price_on_named_bar"], 9.5)

    leg_on_named = {"symbol": "AAA", "weight": 0.5, "price": 9.50, "shares": 52600,
                    "amount": 499700.0}
    r = leg_row(leg_on_named, close, "2026-10-23", "2026-10-14")
    eq("a leg priced at its own bar is classed as such", r["class"], L_ON)

    leg_coincide = {"symbol": "CCC", "weight": 0.5, "price": 5.00, "shares": 1000,
                    "amount": 5000.0}
    r = leg_row(leg_coincide, close, "2026-10-23", "2026-10-14")
    eq("a price both bars share is published as a coincidence, not a witness",
       r["class"], L_COINCIDES)

    r = leg_row({"symbol": "ZZZ", "weight": 0.5, "price": 1.0, "shares": 1, "amount": 1.0},
                close, "2026-10-23", "2026-10-14")
    eq("a symbol the panel does not carry is classed as no close", r["class"], L_NO_CLOSE)

    r = leg_row({"symbol": "AAA", "weight": 0.5, "price": None, "shares": 1, "amount": None},
                close, "2026-10-23", "2026-10-14")
    eq("a leg with no price is classed as no close, never priced at zero", r["class"], L_NO_CLOSE)

    eq("a price that appears on two bars reports two bars sharing it",
       leg_row({"symbol": "CCC", "weight": 0.1, "price": 5.0, "shares": 1, "amount": 5.0},
               close, "2026-10-23", "2026-10-14")["price_bars_sharing_this_price"], 3)
    eq("a price that appears on one bar reports one",
       leg_row(leg_on_dec, close, "2026-10-23", "2026-10-14")["price_bars_sharing_this_price"], 1)

    # ---- money arms -------------------------------------------------------
    tk = {
        "file": "TICKET-2026-10-23.json",
        "named_bar": "2026-10-23",
        "decision_bar": "2026-10-14",
        "declares_its_pricing_bar": False,
        "declared_pricing_bar": None,
        "nav": 1000000.0,
        "legs_total": 2,
        "legs": [leg_on_dec, {"symbol": "BBB", "weight": 0.5, "price": 20.00, "shares": 25000,
                              "amount": 500000.0}],
        "money": None,
        "class": None,
    }
    # emulate analyse_ticket's money block on the fixture
    nav = tk["nav"]
    issued = 1000000.0
    keep = 50000 * 9.5 + 25000 * 19.0
    reiss = int(500000 // (9.5 * LOT)) * LOT * 9.5 + int(500000 // (19.0 * LOT)) * LOT * 19.0
    near("keep-shares arm is shares times the named-bar close", keep, 950000.0)
    near("re-issue arm floors whole lots on the named-bar close", reiss, 999400.0)
    ok.append(("the keep-shares arm loses money when the named bar is lower",
               keep - issued < 0, "%r !< 0" % (keep - issued),))
    ok.append(("the re-issue arm moves far less than the keep-shares arm",
               abs(reiss - issued) < abs(keep - issued),
               "|%r| !< |%r|" % (reiss - issued, keep - issued)))
    near("keep-shares pct of NAV uses the ticket's own NAV", 100.0 * (keep - issued) / nav,
           -5.0)
    eq("a re-issued share delta can be positive or negative",
       int(500000 // (9.5 * LOT)) * LOT - 50000, 2600)

    # ---- summary and verdict ---------------------------------------------
    # adjudicated copies -- the face carries leg_row() output, never the raw order row
    lg_dec = leg_row(leg_on_dec, close, "2026-10-23", "2026-10-14")
    lg_named = leg_row(leg_on_named, close, "2026-10-23", "2026-10-14")
    lg_dec_b = leg_row({"symbol": "BBB", "weight": 0.5, "price": 20.00, "shares": 25000,
                        "amount": 500000.0}, close, "2026-10-23", "2026-10-14")
    ok.append(("the second fixture leg also prices at the decision bar",
               lg_dec_b["class"] == L_DECISION, "%r" % lg_dec_b["class"]))

    row_own = dict(tk, **{
        "file": "TICKET-2026-11-06.json",
        "named_bar": "2026-10-23",
        "class": C_OWN,
        "declares_its_pricing_bar": True,
        "leg_classes": {L_ON: 2, L_DECISION: 0, L_COINCIDES: 0, L_NEITHER: 0, L_NO_CLOSE: 0},
        "legs": [lg_named, lg_named],
        "money": {"issued_book_amount": 1000000.0,
                  "keep_shares_at_named_bar": 1000000.0,
                  "keep_shares_delta_cny": 0.0,
                  "reissued_at_named_bar": 1000000.0,
                  "reissued_delta_cny": 0.0,
                  "shares_delta_if_reissued": 0,
                  "keep_shares_delta_pct_nav": 0.0,
                  "reissued_delta_pct_nav": 0.0},
    })
    row_stale = dict(tk, **{
        "class": C_EARLIER,
        "legs": [lg_dec, lg_dec_b],
        "leg_classes": {L_ON: 0, L_DECISION: 2, L_COINCIDES: 0, L_NEITHER: 0, L_NO_CLOSE: 0},
        "money": {"issued_book_amount": 1000000.0,
                  "keep_shares_at_named_bar": 950000.0,
                  "keep_shares_delta_cny": -50000.0,
                  "reissued_at_named_bar": 999400.0,
                  "reissued_delta_cny": -600.0,
                  "shares_delta_if_reissued": 3900,
                  "keep_shares_delta_pct_nav": -5.0,
                  "reissued_delta_pct_nav": -0.06},
    })
    row_none = dict(tk, **{
        "file": "TICKET-2026-10-28-card.json",
        "class": C_NO_SHEET,
        "legs": [],
        "legs_total": 0,
        "money": None,
        "leg_classes": {},
    })
    s = summarise([row_stale, row_own, row_none])
    eq("order sheets exclude the ticket with no order sheet", s["order_sheets"], 2)
    eq("one sheet is counted as priced on its own bar",
       s["sheets_priced_on_the_bar_they_name"], 1)
    eq("one sheet is counted as priced earlier", s["sheets_priced_on_an_earlier_bar"], 1)
    eq("the money-moves count is one, not two", s["sheets_whose_money_moves_with_the_bar"], 1)
    eq("the leg count sums the leg classes", s["legs_total"], 4)
    eq("the verdict for a mixed population is the share-count one",
       _verdict(s), "the_share_counts_are_what_the_stale_bar_corrupted")
    eq("an all-clean population flips the verdict",
       _verdict(summarise([row_own])), "every_published_order_sheet_prices_on_the_bar_it_names")

    face = {"rows": [row_stale, row_own, row_none], "summary": s}
    eq("the guard passes a face it built itself", face_problems(face), [])

    doctored = json.loads(json.dumps(face))
    doctored["rows"][0]["money"]["keep_shares_delta_cny"] = -1.0
    ok.append(("the guard refuses a keep-shares delta that does not re-derive from its totals",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][1]["leg_classes"] = {L_ON: 1, L_DECISION: 0, L_COINCIDES: 0,
                                          L_NEITHER: 0, L_NO_CLOSE: 0}
    ok.append(("the guard refuses leg classes that do not cover every leg",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["legs_total"] = 99
    ok.append(("the guard refuses a summary leg count that does not re-derive",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][2]["money"] = {"issued_book_amount": 1.0}
    ok.append(("the guard refuses money on a ticket with no order sheet",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][1]["class"] = C_OWN
    doctored["rows"][1]["leg_classes"] = {L_ON: 1, L_DECISION: 1, L_COINCIDES: 0,
                                          L_NEITHER: 0, L_NO_CLOSE: 0}
    ok.append(("the guard refuses a sheet called priced-on-its-own-bar with a stray leg",
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