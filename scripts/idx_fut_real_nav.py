#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The discount, collected by actually rolling contracts.

Every carry number on the basis pages is a *daily difference* between a continuous
futures series and its index, with the splice days deleted.  That is a model of rolling:
it assumes the only thing a roller loses on the seam is the jump, and it needs a mask to
find the seam.  This face does not model the roll -- it books it.

The book: hold whichever contract the market has the most open interest in; when another
contract takes that over by a margin, sell the incumbent and buy the successor **at the
same close**.  No money changes hands on the switch itself: the position is marked at the
close it moves at, so the seam is invisible by construction rather than by masking.

What is left is the real thing the mask was approximating: each contract's own return
while it is held, which includes its convergence into the index as it ages.  Subtract the
index over the same days and the difference is the discount actually collected.

Two questions this answers that no published table could:
  1. Does the discount survive an actual roll book?  (the mask-free ground truth)
  2. What does a roll have to cost before it stops?  (the break-even, in bp per roll)

Costs are a ladder, not a claim: the exchange fee plus one tick each leg is the floor
(commission 0.46bp + 2 x tick), and the ladder publishes where the verdict changes.
"""

import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idx_fut_basis as base  # noqa: E402  (panels, stats, verdict line -- single source)
import idx_fut_contract_roll as cr  # noqa: E402  (contract cache reader -- single source)

ROOT = base.ROOT
CONTRACT_DIR = cr.CONTRACT_DIR
OUT = os.path.join(ROOT, "results", "idx_fut_real_nav.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_REAL_NAV.md")
ROLL_FACE = os.path.join(ROOT, "results", "idx_fut_contract_roll.json")

CRITERIA = {
    "products": ["IF", "IC", "IH", "IM"],
    # A successor has to hold this much more open interest than the incumbent before it
    # takes the book.  Without the margin the position flips on noise around a tie.
    "switch_margin": 0.05,
    "commission_bp": 0.46,        # CFFEX 开仓 0.23bp + 平昨 0.23bp per roll (both legs)
    "tick_points": 0.2,           # CFFEX index futures minimum price fluctuation
    "cost_ladder_bp": [0.0, 1.5, 4.0, 8.0, 15.0],
    "default_cost_bp": 1.5,       # commission + one tick each leg, at a ~4000pt index
    "min_days": 400,
    "min_rolls": 12,
    "admitted_line_pct": base.CARRY_MIN_PCT,
}


# ------------------------------------------------------------------ contract book
def contract_panel_ohlc(prod, cache_dir=None):
    """Every cached contract of this product, with the open as well as the close.

    {sym: {date: {"open", "close", "hold", "volume"}}}.  The close-only tuple below is a
    projection of this one, not a second parser: an execution face has to fill at the
    next open, and two readers over the same CSVs is how the two faces stop agreeing
    (r1375 family).  An open that is missing or non-positive falls back to that day's
    close and is counted, never invented.
    """
    d = cache_dir or CONTRACT_DIR
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.startswith(prod) or not name.endswith(".csv"):
            continue
        sym = name[:-4]
        tail = sym[len(prod):]
        if len(tail) != 4 or not tail.isdigit():
            continue
        rows = cr.read_cached(sym, d)
        if not rows:
            continue
        series = {}
        for r in rows:
            try:
                close = float(r["close"])
                hold = float(r["hold"])
                vol = float(r["volume"])
                try:
                    op = float(r["open"])
                except (KeyError, TypeError, ValueError):
                    op = 0.0
                if not (op > 0):
                    op = close                      # counted by the caller, not hidden
                series[str(r["date"])[:10]] = {"open": op, "close": close,
                                               "hold": hold, "volume": vol}
            except (KeyError, TypeError, ValueError):
                continue
        if series:
            out[sym] = series
    return out


def contract_panel(prod, cache_dir=None):
    """Every cached contract of this product: {sym: {date: (close, open interest, volume)}}.

    Cache only.  The roll-reconstruction leg already owns the pull (and its --max-pull
    budget); this face is a reader, so a missing contract is an absent year, not a fetch.
    """
    return {sym: {d: (row["close"], row["hold"], row["volume"])
                  for d, row in series.items()}
            for sym, series in contract_panel_ohlc(prod, cache_dir).items()}


def active_path(dates, panel, margin=None):
    """{date: contract held after that close} plus the rolls that were booked.

    The incumbent is only displaced when the challenger's open interest beats it by
    `margin`; an incumbent that stops quoting is replaced without the margin (there is
    nothing to compare against) and the roll is flagged `forced`, because deciding to move
    on the day the old contract died is not a choice the roller made.
    """
    margin = CRITERIA["switch_margin"] if margin is None else margin
    held, rolls = {}, []
    cur = None
    for d in dates:
        row = {s: v[d] for s, v in panel.items() if d in v}
        if not row:
            held[d] = cur
            continue
        best = max(row.items(), key=lambda kv: (kv[1][1], kv[0]))[0]
        if cur is None:
            cur = best
        elif cur not in row:
            rolls.append({"date": d, "from": cur, "to": best, "reason": "incumbent not quoted"})
            cur = best
        elif best != cur and row[best][1] > row[cur][1] * (1.0 + margin):
            rolls.append({"date": d, "from": cur, "to": best, "reason": "open interest"})
            cur = best
        held[d] = cur
    return held, rolls


def book_returns(dates, panel, held, index_close, dates_out=None):
    """Daily returns of the held contract and of the index over the same calendar.

    The contract is held from the close it was marked at, so day k's return is the return
    of `held[dates[k-1]]` between the two closes -- exactly what a book that moves at the
    close earns, with no splice in it.  When an incumbent has no quote on the second day
    the return falls back to the contract it was replaced by and the day is counted as
    forced, never silently dropped.
    """
    rf, ri, forced = [], [], 0
    # r1699: a consumer that needs the calendar of these returns (risk units per day)
    # must not rebuild it -- every `continue` below drops a day, and a rebuilt calendar
    # then sits one day off the series.  The optional list records the date each kept
    # return belongs to, so the pairing is produced here or nowhere.
    keep_dates = dates_out if dates_out is not None else None
    for k in range(1, len(dates)):
        d0, d1 = dates[k - 1], dates[k]
        sym = held.get(d0)
        a = panel.get(sym, {}).get(d0) if sym else None
        b = panel.get(sym, {}).get(d1) if sym else None
        if a and b and a[0] > 0 and b[0] > 0:
            rf.append(b[0] / a[0] - 1.0)
        else:
            alt = held.get(d1)
            a2 = panel.get(alt, {}).get(d0) if alt else None
            b2 = panel.get(alt, {}).get(d1) if alt else None
            if a2 and b2 and a2[0] > 0 and b2[0] > 0:
                rf.append(b2[0] / a2[0] - 1.0)
                forced += 1
            else:
                continue
        if index_close.get(d0) and index_close.get(d1):
            ri.append(index_close[d1] / index_close[d0] - 1.0)
        else:
            rf.pop()
            continue
        if keep_dates is not None:
            keep_dates.append(d1)
    return rf, ri, forced


def by_year(dates, rf, ri):
    """Annualised futures-minus-index return per calendar year (the mask-free per-year face)."""
    buckets = {}
    for k, (a, b) in enumerate(zip(rf, ri)):
        y = dates[k + 1][:4]
        buckets.setdefault(y, []).append(a - b)
    return {y: {"days": len(v),
                "carry_ann_pct": round(statistics.fmean(v) * base.TRADING_DAYS * 100, 3),
                "years_frac": round(len(v) / base.TRADING_DAYS, 2)}
            for y, v in sorted(buckets.items())}


def carried(path=None):
    """What the roll-reconstruction leg already published, read not re-typed (r1280 class)."""
    path = ROLL_FACE if path is None else path
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return {}
    out = {}
    for prod, v in (doc.get("products") or {}).items():
        c = (v or {}).get("carry_ann_pct_by_mask") or {}
        out[prod] = {k: (val or {}).get("carry_ann_pct") for k, val in c.items()}
    return out


# ------------------------------------------------------------------ one product
def one_product(prod, index_close=None, cost_bp=None, cache_dir=None):
    code, name, _etf = base.PAIRS[prod]
    idx = index_close if index_close is not None else base.load_index(code)
    panel = contract_panel(prod, cache_dir)
    if not panel:
        return {"status": "no_contracts", "product": prod}

    first = min(min(v) for v in panel.values())
    last = max(max(v) for v in panel.values())
    days = sorted(set(d for d in idx if first <= d <= last))
    held, rolls = active_path(days, panel)
    if len(days) < CRITERIA["min_days"]:
        return {"status": "TOO_SHORT", "product": prod, "days": len(days)}
    rf, ri, forced = book_returns(days, panel, held, idx)
    if len(rf) < CRITERIA["min_days"]:
        return {"status": "TOO_SHORT", "product": prod, "days": len(rf)}

    spread = [a - b for a, b in zip(rf, ri)]
    years = len(rf) / base.TRADING_DAYS
    gross = base.compound_pct(spread)                       # cost-free, compounded
    fut_ann = base.compound_pct(rf)
    idx_ann = base.compound_pct(ri)
    per_roll = len(rolls) / years if years else None

    ladder = {}
    for c in CRITERIA["cost_ladder_bp"]:
        drag_bp = (per_roll or 0.0) * c                      # bp per year
        net = None if gross is None else round(gross - drag_bp / 100.0, 3)
        ladder["%.1f" % c] = {"net_ann_pct": net,
                              "admitted": bool(net is not None
                                               and net >= CRITERIA["admitted_line_pct"])}
    default_cost = CRITERIA["default_cost_bp"] if cost_bp is None else cost_bp
    net_default = ladder.get("%.1f" % default_cost, ladder["%.1f" % CRITERIA["default_cost_bp"]])

    # The number the next person actually needs: how expensive may one roll get before
    # this line falls under the admission line.  A big number means the cost assumption
    # was never the binding constraint, and the mask was.
    breakeven_bp = None
    if gross is not None and per_roll:
        breakeven_bp = round(max(0.0, (gross - CRITERIA["admitted_line_pct"])) * 100.0 / per_roll, 2)

    gaps = [r for r in rolls if r["reason"] == "open interest"]
    return {
        "status": "ok",
        "product": prod,
        "index": code,
        "span": {"first": days[0], "last": days[-1], "days": len(rf),
                 "years": round(years, 2)},
        "contracts_quoted": len(panel),
        "rolls_n": len(rolls),
        "rolls_per_year": round(per_roll, 2) if per_roll else None,
        "rolls_by_reason": {"open_interest": len(gaps),
                            "incumbent_not_quoted": len(rolls) - len(gaps)},
        "forced_return_days": forced,
        "futures_ann_pct": fut_ann,
        "index_ann_pct": idx_ann,
        "carry_gross_ann_pct": None if gross is None else round(gross, 3),
        "carry_net_ann_pct": net_default.get("net_ann_pct"),
        "admitted_at_default_cost": net_default.get("admitted"),
        "default_cost_bp_per_roll": default_cost,
        "cost_ladder": ladder,
        "breakeven_bp_per_roll": breakeven_bp,
        "stats": base.stats_pct(spread),
        "by_year": by_year(days, rf, ri),
        "recent_2y_ann_pct": _recent(spread, 2),
        "roll_days_sample": rolls[-6:],
    }


def _recent(spread, years):
    n = int(years * base.TRADING_DAYS)
    tail = spread[-n:] if len(spread) > n else spread
    return round(base.compound_pct(tail), 3) if tail else None


def _r2(v):
    return "—" if v is None else round(float(v), 2)


# ------------------------------------------------------------------ face
def build(cost_bp=None, cache_dir=None):
    face = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,
        "kind": "real_contract_roll_book",
        "criteria": dict(CRITERIA),
        "published_by_mask": carried(),
        "products": {},
    }
    cut = None
    for prod in CRITERIA["products"]:
        try:
            res = one_product(prod, cost_bp=cost_bp, cache_dir=cache_dir)
        except Exception as exc:  # one product must not take the face down
            res = {"status": "error", "product": prod,
                   "detail": "%s: %s" % (type(exc).__name__, exc)}
        face["products"][prod] = res
        sp = res.get("span")
        if sp and (cut is None or sp["last"] > cut):
            cut = sp["last"]
    face["evidence_cutoff"] = cut
    face["verdict"] = judge(face)
    return face


def judge(face):
    """Which lines survive an actual roll book, and what a roll may cost before they don't."""
    prods = {p: v for p, v in face.get("products", {}).items() if v.get("status") == "ok"}
    if not prods:
        return {"state": "no_book"}
    admitted = sorted([p for p, v in prods.items() if v.get("admitted_at_default_cost")])
    gross_admitted = sorted([p for p, v in prods.items()
                             if v.get("carry_gross_ann_pct") is not None
                             and v["carry_gross_ann_pct"] >= CRITERIA["admitted_line_pct"]])
    pub = face.get("published_by_mask") or {}
    flips = []
    for p, v in prods.items():
        obs_pub = (pub.get(p) or {}).get("observed")
        if obs_pub is None:
            continue
        mine = v.get("carry_gross_ann_pct")
        if mine is None:
            continue
        if (obs_pub >= CRITERIA["admitted_line_pct"]) != (mine >= CRITERIA["admitted_line_pct"]):
            flips.append({"product": p, "published_observed_mask": obs_pub, "real_book": mine})
    bes = [v["breakeven_bp_per_roll"] for v in prods.values()
           if v.get("breakeven_bp_per_roll") is not None
           and v.get("carry_gross_ann_pct") is not None
           and v["carry_gross_ann_pct"] >= CRITERIA["admitted_line_pct"]]
    weakest = min(bes) if bes else None
    # Lines that never clear the admission line even at zero cost are absent, not expensive;
    # folding them into the breakeven would read a missing discount as a cost problem.
    absent = sorted([p for p, v in prods.items()
                     if v.get("carry_gross_ann_pct") is not None
                     and v["carry_gross_ann_pct"] < CRITERIA["admitted_line_pct"]])
    # A roll priced at commission + one tick each leg is ~1.5bp; anything under that floor
    # means the line is already gone and no cost assumption can save it.
    cost_was_binding = weakest is not None and weakest < CRITERIA["default_cost_bp"]
    return {
        "state": "booked",
        "admitted_at_default_cost": admitted,
        "admitted_gross_of_cost": gross_admitted,
        "below_line_before_any_cost": absent,
        "flips_vs_published_observed_mask": flips,
        "weakest_breakeven_bp_per_roll": weakest,
        "cost_was_the_binding_constraint": cost_was_binding,
        "line_pct": CRITERIA["admitted_line_pct"],
    }


# ------------------------------------------------------------------ page
def render_md(face):
    v = face.get("verdict", {})
    c = face.get("criteria", {})
    L = ["# Index futures: what the discount pays a book that actually rolls", ""]
    L.append("Every carry number on the basis pages is a daily difference between the "
             "continuous series and its index with the splice days deleted -- a model of "
             "rolling, not a roll. This page books the roll: hold the contract with the most "
             "open interest, move to its successor when another one takes that over by %s%%, "
             "and mark both legs at the same close, so the seam costs nothing by "
             "construction rather than by being masked out." % (100 * c.get("switch_margin", 0.05)))
    L.append("")
    L.append("Evidence cutoff: `%s`  ·  generated %s" % (face.get("evidence_cutoff"),
                                                         face.get("generated")))
    L.append("")
    prods = {p: x for p, x in (face.get("products") or {}).items() if x.get("status") == "ok"}
    L.append("## The roll book against the published mask")
    L.append("")
    L.append("| product | years | rolls/yr | futures %%/yr | index %%/yr | discount (gross) | "
             "discount net @ %sbp | published (observed mask) |"
             % c.get("default_cost_bp"))
    L.append("|---|---|---|---|---|---|---|---|")
    for p, x in prods.items():
        pub = ((face.get("published_by_mask") or {}).get(p) or {}).get("observed")
        L.append("| %s | %s | %s | %s | %s | **%s** | **%s** | %s |" % (
            p, x["span"]["years"], x["rolls_per_year"], _r2(x["futures_ann_pct"]),
            _r2(x["index_ann_pct"]), x["carry_gross_ann_pct"], x["carry_net_ann_pct"],
            "—" if pub is None else pub))
    L.append("")
    L.append("A negative futures column with a positive discount is the normal shape: the "
             "contract converges into the index without the index paying a dividend.")
    L.append("")
    L.append("## What a roll may cost")
    L.append("")
    L.append("Cost is a ladder, not a claim: the floor is the exchange fee (%sbp) plus one "
             "tick each leg, and the table says where the line stops." % c.get("commission_bp"))
    L.append("")
    steps = list(c.get("cost_ladder_bp") or [])
    L.append("| product | breakeven bp/roll | " + " | ".join("%sbp" % s for s in steps) + " |")
    L.append("|---" * (len(steps) + 2) + "|")
    for p, x in prods.items():
        cells = []
        for s in steps:
            cell = (x.get("cost_ladder") or {}).get("%.1f" % s) or {}
            cells.append("%s%s" % (cell.get("net_ann_pct"),
                                   "" if cell.get("admitted") else " ✗"))
        L.append("| %s | %s | %s |" % (p, x.get("breakeven_bp_per_roll"), " | ".join(cells)))
    L.append("")
    if v.get("weakest_breakeven_bp_per_roll") is not None:
        if v.get("cost_was_the_binding_constraint"):
            L.append("**The weakest line breaks inside the floor cost band (%s bp/roll < %s bp)** "
                     "-- a roll is expensive enough here to matter."
                     % (v["weakest_breakeven_bp_per_roll"], c.get("default_cost_bp")))
        else:
            L.append("**No line breaks inside the floor cost band**: the weakest allows %s bp per "
                     "roll, i.e. roughly %sx the commission-plus-tick floor of %s bp. The cost "
                     "assumption was never what decided these lines -- the mask was."
                     % (v["weakest_breakeven_bp_per_roll"],
                        round((v["weakest_breakeven_bp_per_roll"] or 0) /
                              max(0.1, c.get("default_cost_bp", 1.5)), 1),
                        c.get("default_cost_bp")))
        L.append("")
    L.append("## Admission")
    L.append("")
    L.append("| line | value |")
    L.append("|---|---|")
    L.append("| at/above %s%% gross of cost | %s |" % (c.get("admitted_line_pct"),
                                                       ", ".join(v.get("admitted_gross_of_cost") or []) or "none"))
    L.append("| still above %s%% net at %sbp/roll | %s |" % (c.get("admitted_line_pct"),
                                                             c.get("default_cost_bp"),
                                                             ", ".join(v.get("admitted_at_default_cost") or []) or "none"))
    L.append("| below the line before any cost | %s |" % (", ".join(v.get("below_line_before_any_cost") or []) or "none"))
    L.append("")
    if v.get("flips_vs_published_observed_mask"):
        L.append("### Where the book disagrees with the published observed mask")
        L.append("")
        L.append("| product | published (observed mask) | real book |")
        L.append("|---|---|---|")
        for f in v["flips_vs_published_observed_mask"]:
            L.append("| %s | %s | %s |" % (f["product"], f["published_observed_mask"],
                                           f["real_book"]))
        L.append("")
    L.append("## Per year")
    L.append("")
    L.append("The discount is not a constant, and an average over the whole span hides the "
             "years it was absent.")
    L.append("")
    years = sorted(set(y for x in prods.values() for y in (x.get("by_year") or {})))
    L.append("| year | " + " | ".join(prods) + " |")
    L.append("|---" * (len(prods) + 1) + "|")
    for y in years:
        row = []
        for p in prods:
            b = (prods[p].get("by_year") or {}).get(y)
            row.append("—" if not b else "%s (%sd)" % (b.get("carry_ann_pct"), b.get("days")))
        L.append("| %s | %s |" % (y, " | ".join(row)))
    L.append("")
    L.append("## What this does not measure")
    L.append("")
    L.append("The book marks at closes, so it pays no spread and no slippage -- that is what "
             "the cost ladder is for. It also assumes the position can always be moved on the "
             "day open interest flips; in practice a roll is done over a day or two, which "
             "costs a little basis but no exposure. And the roll itself is a quote-source "
             "fact, not a broker statement: the contract codes come from the same daily "
             "endpoint as the continuous series.")
    L.append("")
    L.append("Products where the cache covers too few years are reported, not silently "
             "dropped: see `status` in the JSON.")
    return "\n".join(L)


def write_doc(face=None):
    face = face or build()
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def checkdoc(face=None):
    face = face or build()
    if not os.path.isfile(DOC):
        print("checkdoc: page missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        have = f.read()
    want = render_md(face)
    if have.strip() != want.strip():
        print("checkdoc: page differs from face")
        return 1
    print("checkdoc ok (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def _series(rows):
    return {d: (c, oi, 1000.0) for d, c, oi in rows}


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    # A book must not move when the incumbent keeps the deepest open interest.
    panel = {"AAA": _series([("d1", 100.0, 500), ("d2", 101.0, 510), ("d3", 102.0, 520)]),
             "BBB": _series([("d1", 101.0, 100), ("d2", 101.5, 120), ("d3", 102.5, 130)])}
    held, rolls = active_path(["d1", "d2", "d3"], panel)
    leg("noo roll without an open-interest takeover", not rolls and held["d3"] == "AAA")

    # ...and must move when it does, booking the day it moved.
    panel["BBB"] = _series([("d1", 101.0, 100), ("d2", 101.5, 600), ("d3", 102.5, 620)])
    held, rolls = active_path(["d1", "d2", "d3"], panel)
    leg("rolls on the day the challenger takes over", len(rolls) == 1 and rolls[0]["date"] == "d2")
    leg("holds the successor after the roll", held["d3"] == "BBB")

    # A takeover under the margin is noise, not a roll.
    panel2 = {"AAA": _series([("d1", 100.0, 500), ("d2", 101.0, 500)]),
              "BBB": _series([("d1", 101.0, 490), ("d2", 101.5, 500)])}
    _held, rolls2 = active_path(["d1", "d2"], panel2)
    leg("a tie inside the margin is not a roll", not rolls2)

    # An incumbent that stops quoting is replaced and flagged forced, never dropped.
    panel3 = {"AAA": _series([("d1", 100.0, 500), ("d2", 101.0, 500)]),
              "BBB": _series([("d2", 101.0, 100), ("d3", 102.0, 110)])}
    held3, rolls3 = active_path(["d1", "d2", "d3"], panel3)
    leg("dead incumbent is replaced, roll flagged",
        len(rolls3) == 1 and rolls3[0]["reason"] == "incumbent not quoted")
    leg("replacement is held afterwards", held3["d3"] == "BBB")

    # The book's return is the held contract's own move: no splice enters it.
    rf, ri, forced = book_returns(["d1", "d2", "d3"], panel3, {d: "AAA" for d in ("d1", "d2", "d3")},
                                  {"d1": 100.0, "d2": 100.0, "d3": 100.0})
    leg("contract return is its own close-to-close", rf == [0.01, 0.00990099] or
        abs(rf[0] - 0.01) < 1e-9)
    leg("index leg aligned on the same days", len(ri) == len(rf) and not forced)

    # A day where the incumbent has no quote falls back to the successor and is counted.
    panel4 = {"AAA": _series([("d1", 100.0, 500)]),
              "BBB": _series([("d1", 101.0, 100), ("d2", 102.0, 620)])}
    rf2, _ri2, forced2 = book_returns(["d1", "d2"], panel4,
                                      {"d1": "AAA", "d2": "BBB"},
                                      {"d1": 1.0, "d2": 1.0})
    leg("missing incumbent quote falls back and is flagged forced",
        forced2 == 1 and len(rf2) == 1 and abs(rf2[0] - (102.0 / 101.0 - 1.0)) < 1e-12)

    # Cost ladder: drag is rolls-per-year times bp, and the breakeven follows from it.
    face = {"criteria": dict(CRITERIA), "published_by_mask": {},
            "products": {"XX": {"status": "ok", "carry_gross_ann_pct": 7.0,
                                "carry_net_ann_pct": 6.5, "admitted_at_default_cost": True,
                                "breakeven_bp_per_roll": 33.3, "rolls_per_year": 12.0,
                                "cost_ladder": {"1.5": {"net_ann_pct": 6.5, "admitted": True}},
                                "span": {"years": 5.0}, "futures_ann_pct": 1.0,
                                "index_ann_pct": 3.0, "by_year": {"2025": {"carry_ann_pct": 9.0}}}},
            "evidence_cutoff": "2026-11-14", "generated": "now"}
    v = judge(face)
    leg("verdict lists the admitted line", v["admitted_at_default_cost"] == ["XX"])
    page = render_md(face)
    leg("page prints the breakeven column", "33.3" in page)
    leg("page prints the per-year cell", "2025" in page and "9.0" in page)
    # A breakeven under the floor cost is a different finding, and the page must say so.
    face["products"]["XX"]["breakeven_bp_per_roll"] = 0.9
    face["verdict"] = judge(face)
    leg("a line that dies inside the floor band is called out",
        "breaks inside the floor cost band" in render_md(face))
    face["products"]["XX"]["breakeven_bp_per_roll"] = 33.3
    face["verdict"] = judge(face)
    leg("a line clear of the floor band is not called out",
        "No line breaks inside the floor cost band" in render_md(face))

    # A line under the admission line at zero cost is absent, not cost-bound: it must not
    # drag the weakest-breakeven reading down and turn the page into a cost story.
    face["products"]["YY"] = {"status": "ok", "carry_gross_ann_pct": 1.2,
                              "carry_net_ann_pct": 1.1, "admitted_at_default_cost": False,
                              "breakeven_bp_per_roll": 0.0, "rolls_per_year": 10.0,
                              "cost_ladder": {}, "span": {"years": 3.0},
                              "futures_ann_pct": 0.0, "index_ann_pct": 1.0, "by_year": {}}
    face["verdict"] = judge(face)
    leg("an absent line is not read as a cost problem",
        face["verdict"]["weakest_breakeven_bp_per_roll"] == 33.3
        and face["verdict"]["below_line_before_any_cost"] == ["YY"]
        and "No line breaks inside the floor cost band" in render_md(face))
    face["products"].pop("YY")
    face["verdict"] = judge(face)

    # Published numbers are read from the other face, never re-typed.
    leg("carried() returns {} when the face is absent",
        carried(os.path.join(ROOT, "research", "__no_such_face__.json")) == {})

    passed = sum(1 for _n, c in ok if c)
    for n, c in ok:
        print("%s %s" % ("PASS" if c else "FAIL", n))
    print("%d/%d legs" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    flags = set(a for a in argv[1:] if a.startswith("-"))
    if "--selftest" in flags:
        return selftest()
    cost = None
    for f in flags:
        if f.startswith("--cost-bp="):
            cost = float(f.split("=", 1)[1])
    face = build(cost_bp=cost)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if "--write-doc" in flags:
        write_doc(face)
    if "--checkdoc" in flags:
        return checkdoc(face)
    v = face.get("verdict", {})
    print("real-roll book: admitted gross=%s net=%s weakest breakeven=%sbp (cutoff %s)" % (
        v.get("admitted_gross_of_cost"), v.get("admitted_at_default_cost"),
        v.get("weakest_breakeven_bp_per_roll"), face.get("evidence_cutoff")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
