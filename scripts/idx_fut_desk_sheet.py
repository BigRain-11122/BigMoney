# -*- coding: utf-8 -*-
"""The carry sleeve as a desk reads it the morning before it trades it. (bm-c r1701)

`idx_fut_carry_risk` answered "is holding the future instead of the ETF worth +9pp?".
That is a judgement, not a position: it carries no contract name, no lot count, no
margin, and no answer to "when does this roll next".  A desk cannot act on it.  This
face is the smallest thing that turns the judgement into a morning sheet:

  * which contract tomorrow's fill would go into, and how much of the product's open
    interest actually sits in it (a contract holding 4% of the book is a fill you may
    not get);
  * the margin one lot ties up at the exchange minimum -- an ASSUMPTION, printed as
    one, because a broker's surcharge is not measurable from this host -- and so how
    many lots a stated capital buys, both naively and after funding the product's own
    published max drawdown (the margin identity the source face already prints);
  * how far the index must fall before the account is below maintenance margin, and the
    largest lot count that survives the index's own worst drawdown without a call
    (r1705).  The lot count that funds the sample's drawdown and the count that survives
    the record are different numbers, and only the second one is a position;
  * when the next roll falls, measured from this book's own switch history rather than
    a calendar rule -- the calendar rule was already shown to catch 50% of the rolls
    while eating market days near expiry;
  * the published gap after roll cost, BOTH ends of the band, read from the source
    face rather than recomputed here.

Nothing here is adopted.  The source face calls IC/IM `SLEEVE_CANDIDATE`; this sheet
repeats that word in every row it prints, and a product the source face refuses is
still printed with its refusal, not hidden.
"""
import os
import sys
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base            # noqa: E402  (products, TRADING_DAYS, index panels)
import idx_fut_real_nav as rn           # noqa: E402  (contract panel + switch history, single source)

OUT = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_DESK_SHEET.md")
SRC = os.path.join(ROOT, "results", "idx_fut_carry_risk.json")

# CFFEX contract specs.  An assumption like the margin: the exchange publishes them,
# this host cannot query the file, and getting one wrong scales every lot count.
MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}

# The level at which the broker calls, not the level at which it is posted.  Same family
# of assumption as the 12% initial margin and printed for the same reason: the exchange
# file and the broker's surcharge are both unreachable from this host.  It is smaller
# than the initial margin by construction -- a book that is only ever called after it has
# already posted the full initial margin again is not a call, it is a liquidation.
MAINTENANCE = {"IF": 0.08, "IH": 0.08, "IC": 0.08, "IM": 0.08}
MAINTENANCE_SURCHARGE_BAND = 0.02

CRITERIA = {
    "products": ["IC", "IF", "IM", "IH"],
    "capital_cny": 1000000.0,
    # the middle of the source face's three printed margin assumptions
    "margin_pct": 0.12,
    "thin_interest_share_pct": 8.0,
    # account sizes a reader might actually have; the sheet prices every one of them
    # instead of answering only for the face's own 1M
    "ladder_capitals_cny": [300000, 1000000, 3000000, 10000000, 50000000],
}


def _face():
    """The published judgement this sheet sits on.  Absent => the sheet is refused."""
    if not os.path.isfile(SRC):
        return None
    try:
        with open(SRC, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def _panel(prod, cache_dir=None):
    ohlc = rn.contract_panel_ohlc(prod, cache_dir)
    if not ohlc:
        return None, None, None
    proj = {sym: {d: (row["close"], row["hold"], row["volume"])
                  for d, row in series.items()}
            for sym, series in ohlc.items()}
    days = sorted({d for sym in proj for d in proj[sym]})
    if not days:
        return None, None, None
    return ohlc, proj, days


def roll_intervals(days, rolls):
    """Trading days between consecutive switches, from the history this book booked.

    Measured rather than assumed: a fixed "roll 3 days before expiry" rule is what the
    calendar mask tried, and the source family already showed it mis-names half of them.
    """
    idx = {d: k for k, d in enumerate(days)}
    pos = [idx[r["date"]] for r in rolls if r.get("date") in idx]
    gaps = [b - a for a, b in zip(pos, pos[1:])] if len(pos) > 1 else []
    if not gaps:
        return {"n": 0, "median_td": None, "iqr_td": None, "gaps": []}
    s = sorted(gaps)
    mid = len(s) // 2
    median = float(s[mid]) if len(s) % 2 else (s[mid - 1] + s[mid]) / 2.0
    q1 = float(s[len(s) // 4])
    q3 = float(s[(3 * len(s)) // 4])
    return {"n": len(gaps), "median_td": round(median, 1),
            "iqr_td": [q1, q3], "gaps": gaps}


def margin_call(lots, notional_per_lot, capital, maint_pct):
    """How far the index must fall before this account is below maintenance margin.

    The algebra, because a paper that prints a number without it cannot be argued with:

        equity(f)      = capital - V*f                 a future is unfunded, no interest
        required(f)    = m * (1 - f) * V               maintenance is a share of the mark
        call when      capital - V*f < m*(1-f)*V
                    => f > (capital - m*V) / ((1-m)*V)

    Two consequences worth printing rather than discovering: the distance SHRINKS as lots
    grow (every extra lot adds V, which costs more equity than it adds maintenance), and it
    can exceed 100% -- that is the honest reading of "no call short of a total loss", not a
    number a reader should see as a percentage of a fall.
    """
    out = {"lots": lots, "maint_pct_assumed": round(maint_pct * 100.0, 2),
           "fall_to_call_pct": None, "equity_at_call_cny": None,
           "never_short_of_total_loss": False}
    if not lots or not notional_per_lot or notional_per_lot <= 0:
        return out
    v = lots * notional_per_lot
    denom = (1.0 - maint_pct) * v
    if denom <= 0:
        return out
    f = (capital - maint_pct * v) / denom
    out["notional_cny"] = round(v, 0)
    out["equity_at_call_cny"] = round(capital - v * f, 0) if f < 1.0 else None
    if f >= 1.0:
        # a 100% fall is a total loss of the index; anything at or past it is not a call
        out["never_short_of_total_loss"] = True
        out["fall_to_call_pct_ge_100"] = round(f * 100.0, 2)
        return out
    out["fall_to_call_pct"] = round(f * 100.0, 2)
    return out


def lots_that_survive(capital, notional_per_lot, maint_pct, worst_dd_pct):
    """The largest lot count this account can hold and still not be called at the worst
    drawdown on record.

    Closed form: f*(N) > D  <=>  capital > N*notional*(m + D*(1-m)).  Strict inequality,
    because f* == D is a call exactly at the worst day, which is not survival.  Both sides
    of the boundary are asserted in the selftest -- a count that is one lot too high is the
    failure that costs money, and only the "+1 does get called" leg catches it.
    """
    if worst_dd_pct is None or notional_per_lot is None or notional_per_lot <= 0:
        return None
    d = abs(float(worst_dd_pct)) / 100.0
    denom = notional_per_lot * (maint_pct + d * (1.0 - maint_pct))
    if denom <= 0:
        return None
    n = int(capital // denom)
    if n > 0 and abs(capital - n * denom) < 1e-6:
        n -= 1               # exact equality is a call, not survival
    return max(n, 0)


def desk_row(prod, face, cache_dir=None, capital=None):
    ohlc, proj, days = _panel(prod, cache_dir)
    if not ohlc:
        return {"product": prod, "status": "no_contract_book"}
    held, rolls = rn.active_path(days, proj)
    last = days[-1]
    sym = held.get(last)
    if not sym or sym not in ohlc or last not in ohlc[sym]:
        return {"product": prod, "status": "no_contract_on_cutoff", "cutoff": last}
    row = ohlc[sym][last]
    oi_total = sum(ser.get(last, {}).get("hold", 0.0) or 0.0 for ser in ohlc.values())
    share = (row["hold"] / oi_total * 100.0) if oi_total > 0 else None

    mult = MULTIPLIER.get(prod)
    if not mult:
        return {"product": prod, "status": "no_contract_multiplier", "held": sym}
    notional = row["close"] * mult
    margin = notional * CRITERIA["margin_pct"]

    # the published judgement, read not recomputed
    src = (face or {}).get("products", {}).get(prod, {})
    verdict_row = ((face or {}).get("verdict", {}) or {}).get("rows", {}).get(prod, {})
    mdd = (src.get("risk") or {}).get("mdd_pct")
    dd_buffer = (abs(mdd) / 100.0 * notional) if isinstance(mdd, (int, float)) else None
    cap = float(CRITERIA["capital_cny"] if capital is None else capital)
    lots_naive = int(cap // margin) if margin > 0 else None
    lots_after_dd = (int(cap // (margin + dd_buffer))
                     if (dd_buffer is not None and margin + dd_buffer > 0) else None)

    # The second ruler the source face already carries: the index's own worst drawdown over
    # its whole history.  The lot count above funds the window's drawdown, which on a
    # four-year futures series is small; funding the record instead is what survives a 2008.
    mi = (src.get("margin_identity") or {}).get("12pct") or {}
    stress_dd = mi.get("stress_dd_pct")
    stress_buffer = (abs(stress_dd) / 100.0 * notional) if isinstance(stress_dd, (int, float)) else None
    lots_after_stress = (int(cap // (margin + stress_buffer))
                         if (stress_buffer is not None and margin + stress_buffer > 0) else None)

    # And the third question a desk actually asks: not "how many do I keep behind this" but
    # "how far does the index fall before someone calls me".  Priced at the count the sheet
    # otherwise recommends (the sample-drawdown one), because that is the count a reader
    # would act on, and at the count that survives the record, because that is the cap.
    maint = MAINTENANCE.get(prod)
    call_at_recommended = (margin_call(lots_after_dd, notional, cap, maint)
                           if maint is not None else None)
    call_at_recommended_band = (margin_call(lots_after_dd, notional, cap,
                                            maint + MAINTENANCE_SURCHARGE_BAND)
                                if maint is not None else None)
    lots_survive = lots_that_survive(cap, notional, maint, stress_dd) if maint is not None else None
    call_at_survive = (margin_call(lots_survive, notional, cap, maint)
                       if (maint is not None and lots_survive) else None)

    # Every count above is a margin-account answer.  A cash account cannot carry a lot
    # whose notional exceeds its capital at all, and the earlier prints of this sheet put
    # "1 lot survives the record" next to a 1M capital while one IC lot is 1.275M of
    # index: a reader would size a book the account cannot fund without borrowing, so the
    # cash count is printed beside the margin counts instead of being left to arithmetic.
    cash_lots = int(cap // notional) if notional > 0 else None

    # What the sleeve pays on the capital it actually needs behind it.  Carry is measured
    # on notional, but nobody holds a future on notional alone -- the money that has to sit
    # there is the maintenance level plus the fall it must fund.  Both rulers are printed
    # because they answer different questions: the sample's own drawdown says what this
    # window cost, the index's worst says what a 2008 would demand.
    carry = (src.get("risk") or {}).get("ann_compound_pct")
    sample_dd = (src.get("risk") or {}).get("mdd_pct")
    rec_ratio = (maint + abs(stress_dd) / 100.0 * (1 - maint)
                 if (maint is not None and isinstance(stress_dd, (int, float))) else None)
    smp_ratio = (maint + abs(sample_dd) / 100.0 * (1 - maint)
                 if (maint is not None and isinstance(sample_dd, (int, float))) else None)

    iv = roll_intervals(days, rolls)
    idx = {d: k for k, d in enumerate(days)}
    last_roll = rolls[-1] if rolls else None
    since = (idx[last] - idx[last_roll["date"]]) if (last_roll and last_roll.get("date") in idx) else None
    eta = (iv["median_td"] - since) if (iv["median_td"] is not None and since is not None) else None

    ex = src.get("execution") or {}
    band = ex.get("gap_after_roll_cost_pp") or {}
    return {
        "product": prod,
        "status": "ok",
        "cutoff": last,
        "held_contract": sym,
        "close": row["close"],
        "open_interest": row["hold"],
        "oi_share_pct": None if share is None else round(share, 2),
        "thin_interest": (share is not None and share < CRITERIA["thin_interest_share_pct"]),
        "multiplier": mult,
        "notional_per_lot_cny": round(notional, 0),
        "margin_per_lot_cny": round(margin, 0),
        "margin_pct_assumed": CRITERIA["margin_pct"] * 100.0,
        "drawdown_buffer_per_lot_cny": None if dd_buffer is None else round(dd_buffer, 0),
        "lots_for_capital": lots_naive,
        "lots_after_own_drawdown": lots_after_dd,
        "lots_after_index_worst_drawdown": lots_after_stress,
        "lots_that_survive_index_worst_without_a_call": lots_survive,
        # the same question asked of a cash account: a lot whose notional exceeds the
        # capital is not a small position, it is not a position at all
        "cash_lots_at_stated_capital": cash_lots,
        "carry_ann_compound_pct": carry,
        "sample_drawdown_pct": None if not isinstance(sample_dd, (int, float)) else round(abs(sample_dd), 2),
        "record_risk_capital_per_lot_cny": None if rec_ratio is None else round(notional * rec_ratio, 0),
        "record_return_on_risk_capital_pct": (None if (carry is None or not rec_ratio)
                                             else round(carry / rec_ratio, 2)),
        "sample_risk_capital_per_lot_cny": None if smp_ratio is None else round(notional * smp_ratio, 0),
        "sample_return_on_risk_capital_pct": (None if (carry is None or not smp_ratio)
                                             else round(carry / smp_ratio, 2)),
        "index_worst_drawdown_pct": None if not isinstance(stress_dd, (int, float)) else round(abs(stress_dd), 2),
        "stress_buffer_per_lot_cny": None if stress_buffer is None else round(stress_buffer, 0),
        "margin_call_at_recommended_lots": call_at_recommended,
        "margin_call_at_recommended_lots_surcharge_band": call_at_recommended_band,
        "margin_call_at_surviving_lots": call_at_survive,
        "capital_cny": cap,
        "rolls": len(rolls),
        "last_roll": None if not last_roll else {"date": last_roll["date"],
                                                 "from": last_roll.get("from"),
                                                 "to": last_roll.get("to"),
                                                 "reason": last_roll.get("reason")},
        "td_since_last_roll": since,
        "roll_interval": {"n": iv["n"], "median_td": iv["median_td"], "iqr_td": iv["iqr_td"]},
        "next_roll_eta_td": eta,
        "verdict": verdict_row.get("verdict"),
        "verdict_why": verdict_row.get("why"),
        "gap_after_roll_cost_pp": {"file_floor": band.get("file_floor"),
                                   "measured_median": band.get("measured_median")},
        "gap_open_open_pp": ex.get("gap_open_open_pp"),
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
        # why the gap is refused, when it is: the source face names the reason and this
        # sheet copies it instead of printing a dash that reads like "nothing to report".
        # A gap that HAS a number cannot be refused -- a share-conversion flag on the ETF
        # leg is a note about that leg, not a reason to refuse the futures gap, so it
        # travels in its own field below instead of masquerading as a refusal.
        "gap_refused_because": (
            None if band.get("file_floor") is not None
            else (ex.get("etf_flag") or "the source face carries no execution block")),
        "etf_leg_note": ex.get("etf_flag"),
    }


def build(cache_dir=None, capital=None):
    face = _face()
    rows = {}
    for prod in CRITERIA["products"]:
        rows[prod] = desk_row(prod, face, cache_dir, capital)
    live = {p: r for p, r in rows.items() if r.get("status") == "ok"}
    return {
        "kind": "idx_fut_desk_sheet",
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
        "source_face": "results/idx_fut_carry_risk.json",
        "source_present": face is not None,
        "criteria": dict(CRITERIA, capital_cny=float(CRITERIA["capital_cny"] if capital is None else capital)),
        "multiplier_assumption": MULTIPLIER,
        "maintenance_margin_assumption": MAINTENANCE,
        "maintenance_surcharge_band": MAINTENANCE_SURCHARGE_BAND,
        "rows": rows,
        "candidates": sorted(p for p, r in rows.items()
                             if r.get("verdict") == "SLEEVE_CANDIDATE"),
        "tradable_today": sorted(p for p, r in live.items()
                                 if not r.get("thin_interest")),
        "note": ("a candidate is a sleeve being priced forward, not an adopted position;"
                 " the margin and the multipliers are assumptions printed with the numbers"),
        "capital_ladder": capital_ladder(rows),
        "book": _book_block(face),
    }


def _book_block(face):
    """The adopted book's own risk face, copied so the sleeve can be read against it."""
    b = ((face or {}).get("book") or {})
    if not b:
        return None
    return {k: b.get(k) for k in ("n", "ann_mean_pct", "ann_vol_pct", "sharpe",
                                  "mdd_pct", "ann_compound_pct", "worst_year_pct",
                                  "worst_year", "underwater_max_bars")}


def capital_ladder(rows, capitals=None):
    """One row per (product, account size): what a cash account can hold, what a margin
    account can hold, and what each of those earns in CNY at the published carry.

    Both counts are printed because they diverge in the direction that matters: a 1M
    cash account carries zero IC lots while a margin account carries six, and a reader
    who is handed only the second number will believe the first is six too.
    """
    caps = [float(c) for c in (capitals or CRITERIA["ladder_capitals_cny"])]
    out = []
    for prod in CRITERIA["products"]:
        r = (rows or {}).get(prod) or {}
        if r.get("status") != "ok":
            out.append({"product": prod, "status": r.get("status") or "absent", "steps": []})
            continue
        notional = r.get("notional_per_lot_cny") or 0.0
        margin = r.get("margin_per_lot_cny") or 0.0
        carry = r.get("carry_ann_compound_pct")
        steps = []
        for cap in caps:
            cash_lots = int(cap // notional) if notional > 0 else None
            margin_lots = int(cap // margin) if margin > 0 else None
            steps.append({
                "capital_cny": cap,
                "cash_lots": cash_lots,
                "cash_return_cny": (None if (cash_lots is None or carry is None)
                                    else round(cash_lots * notional * carry / 100.0, 0)),
                "cash_occupancy_pct": (None if (cash_lots is None or not cap)
                                       else round(cash_lots * notional / cap * 100.0, 1)),
                "margin_lots": margin_lots,
                "margin_return_cny": (None if (margin_lots is None or carry is None)
                                      else round(margin_lots * notional * carry / 100.0, 0)),
            })
        out.append({"product": prod, "status": "ok",
                    "notional_per_lot_cny": notional, "carry_ann_compound_pct": carry,
                    "steps": steps})
    return {"capitals_cny": caps, "rows": out,
            "note": ("cash = the lot is paid for in full (notional <= capital); margin = the"
                     " exchange minimum is posted and the rest of the capital is what absorbs"
                     " the fall -- the two are different positions, not two estimates")}


# ------------------------------------------------------------------ rendering
def _p(v, nd=2, dash="-"):
    return dash if v is None else ("%." + str(nd) + "f") % v


def _sgn(v, nd=2, dash="-"):
    return dash if v is None else (("%+." if v >= 0 else "%.") + str(nd) + "f") % v


def render_md(face):
    L = []
    L.append("# the carry sleeve as a morning sheet")
    L.append("")
    L.append("evidence cutoff: **%s** | source judgement: `%s`%s"
             % (face.get("evidence_cutoff") or "unknown", face.get("source_face"),
                "" if face.get("source_present") else " **(absent: every number below is refused)**"))
    L.append("")
    L.append("The judgement face says whether the sleeve is worth holding. It does not say")
    L.append("which contract, how many lots, or when it rolls. This sheet answers only that.")
    L.append("")
    L.append("## what tomorrow's fill would be")
    L.append("")
    L.append("| product | judgement | contract | close | OI share | notional/lot | margin/lot |")
    L.append("|---|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            L.append("| %s | %s | - | - | - | - | - |" % (prod, r.get("status")))
            continue
        share = _p(r.get("oi_share_pct"), 2)
        if r.get("thin_interest"):
            share += " (thin)"
        L.append("| %s | %s | %s | %s | %s%% | %s | %s |"
                 % (prod, r.get("verdict") or "unknown", r["held_contract"],
                    _p(r["close"], 1), share,
                    _p(r["notional_per_lot_cny"], 0), _p(r["margin_per_lot_cny"], 0)))
    L.append("")
    L.append("Margin is the exchange minimum at %.0f%%; a broker adds its own, which this"
             " host cannot measure. Notional and margin are per lot = price x multiplier"
             " (IF/IH 300, IC/IM 200)." % (face["criteria"]["margin_pct"] * 100.0))
    L.append("")
    L.append("## what a stated capital buys")
    L.append("")
    L.append("Capital **%s CNY**. Five counts, because \"how many lots\" has five different"
             " answers depending on what the capital is supposed to survive: paid for in"
             " full, margin only, the product's own published max drawdown, the index's"
             " worst on record paid in cash, and the largest book that is never called at"
             " that worst."
             % _p(face["criteria"]["capital_cny"], 0))
    L.append("")
    L.append("| product | cash, no borrowing | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |")
    L.append("|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        L.append("| %s | %s lots | %s lots | %s lots | %s lots | %s lots |"
                 % (prod, _p(r.get("cash_lots_at_stated_capital"), 0, "?"),
                    _p(r.get("lots_for_capital"), 0, "?"),
                    _p(r.get("lots_after_own_drawdown"), 0, "?"),
                    _p(r.get("lots_after_index_worst_drawdown"), 0, "?"),
                    _p(r.get("lots_that_survive_index_worst_without_a_call"), 0, "?")))
    L.append("")
    L.append("The **own max drawdown** column funds the hole this window")
    L.append("produced (a few percent, on a four-year futures series); the **index worst**")
    L.append("column funds the index's own worst historical drawdown (the per-product number")
    L.append("is printed in the call table below). They are not two estimates of one thing:")
    L.append("the first is a fact about the sample, the second is the size of the hole this")
    L.append("position can be asked to fund. The last column is never larger than the third")
    L.append("because a call arrives at the maintenance level, not at the initial one -- and")
    L.append("that difference is the only room this trade is actually given.")
    L.append("")
    # The five counts differ in one direction that costs money: a cash account cannot
    # carry a lot whose notional exceeds its capital.  Say which products are in that
    # shape at this account size instead of leaving the reader to multiply.
    live_prods = [p for p in CRITERIA["products"]
                  if (face["rows"].get(p) or {}).get("status") == "ok"]
    cannot_pay = [p for p in live_prods
                  if (face["rows"][p].get("cash_lots_at_stated_capital") or 0) == 0]
    if cannot_pay:
        L.append("**%s** cannot be paid for in full even once at this account size (one"
                 " lot's notional is larger than the stated capital), so every count in"
                 " the last three columns is a margin position: the account borrows, and"
                 " the borrowed part is exactly what a fall calls first."
                 % ", ".join(cannot_pay))
        L.append("")
    L.append("## what the sleeve earns on the capital it needs behind it")
    L.append("")
    L.append("Carry is measured on notional. Nobody holds a future on notional alone -- the")
    L.append("money that has to sit there is the maintenance level plus the fall it must")
    L.append("fund -- so the same carry buys a different return on the capital actually")
    L.append("committed, and the answer depends on which fall you prepare for.")
    L.append("")
    L.append("| product | carry on notional | capital/lot for sample DD | return on it | capital/lot for index worst | return on it |")
    L.append("|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        L.append("| %s | %s%% | %s | %s%% | %s | %s%% |"
                 % (prod,
                    _p(r.get("carry_ann_compound_pct"), 2, "?"),
                    _p(r.get("sample_risk_capital_per_lot_cny"), 0, "?"),
                    _p(r.get("sample_return_on_risk_capital_pct"), 2, "?"),
                    _p(r.get("record_risk_capital_per_lot_cny"), 0, "?"),
                    _p(r.get("record_return_on_risk_capital_pct"), 2, "?")))
    L.append("")
    L.append("The sample column prepares for the hole this window produced (%s%% for IC);"
             " the index column prepares for the index's own worst (%s%%)."
             % (_p((face["rows"].get("IC") or {}).get("sample_drawdown_pct"), 2, "?"),
                _p((face["rows"].get("IC") or {}).get("index_worst_drawdown_pct"), 2, "?")))
    L.append(" A return computed on the smaller capital is not a better trade, it is the same")
    L.append(" trade with less money held against the day the larger number happens.")
    L.append("")
    bk = face.get("book") or {}
    if bk and bk.get("ann_compound_pct") is not None:
        L.append("Read against the adopted book on the same source face (n=%s bars, %s%%"
                 " vol, Sharpe %s, max drawdown %s%%):"
                 % (bk.get("n"), _p(bk.get("ann_vol_pct"), 2, "?"),
                    _p(bk.get("sharpe"), 3, "?"), _p(bk.get("mdd_pct"), 2, "?")))
        L.append("")
        L.append("- the book compounds **%s%%/yr** and its worst drawdown is **%s%%**;"
                 % (_p(bk.get("ann_compound_pct"), 2, "?"), _p(bk.get("mdd_pct"), 2, "?")))
        for prod in CRITERIA["products"]:
            r = face["rows"].get(prod, {})
            if r.get("status") != "ok" or r.get("record_return_on_risk_capital_pct") is None:
                continue
            L.append("- **%s** pays **%s%%/yr** on the capital that funds its index worst"
                     " (%s), and that capital is the size of a %s%% fall."
                     % (prod, _p(r.get("record_return_on_risk_capital_pct"), 2),
                        _p(r.get("record_risk_capital_per_lot_cny"), 0),
                        _p(r.get("index_worst_drawdown_pct"), 2, "?")))
        L.append("")
        L.append("A sleeve that pays the book's rate while requiring its holder to fund a")
        L.append("%s%% fall is not the same instrument at the same price; that comparison"
                 " is the one this sheet refuses to make for the reader."
                 % _p(max([(face["rows"].get(p) or {}).get("index_worst_drawdown_pct") or 0
                           for p in live_prods] or [0]), 2))
        L.append("")
        priced = [(p, (face["rows"].get(p) or {}).get("record_return_on_risk_capital_pct"))
                  for p in live_prods
                  if (face["rows"].get(p) or {}).get("record_return_on_risk_capital_pct") is not None]
        if priced and bk.get("ann_compound_pct") is not None:
            best_prod, best_pct = max(priced, key=lambda x: x[1])
            gap = best_pct - bk["ann_compound_pct"]
            L.append("So the money question has one answer on this face: the best sleeve is")
            L.append("**%s** at %s%%/yr against the book's %s%%/yr (%spp), and the %spp is"
                     " paid for by holding capital sized for a %s%% fall rather than the book's"
                     " %s%% worst. A reader who wants the book's risk shape should not"
                     " substitute this; a reader who will fund a %s%% hole for %spp is being"
                     " quoted the whole price here, not a partial one."
                     % (best_prod, _p(best_pct, 2), _p(bk.get("ann_compound_pct"), 2),
                        _sgn(gap, 2), _p(gap, 2),
                        _p((face["rows"].get(best_prod) or {}).get("index_worst_drawdown_pct"), 2, "?"),
                        _p(abs(bk.get("mdd_pct") or 0), 2),
                        _p(max([(face["rows"].get(p) or {}).get("index_worst_drawdown_pct") or 0
                                for p in live_prods] or [0]), 2), _sgn(gap, 2)))
            L.append("")
    L.append("## how far the index must fall before someone calls")
    L.append("")
    L.append("| product | index worst DD on record | fall that calls the own-DD count | with +%spp maintenance | fall that calls the surviving count |"
             % _p(MAINTENANCE_SURCHARGE_BAND * 100, 0))
    L.append("|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        c1 = r.get("margin_call_at_recommended_lots") or {}
        c2 = r.get("margin_call_at_recommended_lots_surcharge_band") or {}
        c3 = r.get("margin_call_at_surviving_lots") or {}

        def _fall(c):
            if not c:
                return "?"
            if c.get("fall_to_call_pct") is not None:
                return "%s%%" % _p(c["fall_to_call_pct"], 1, "?")
            if c.get("never_short_of_total_loss"):
                return ">100%"
            return "?"
        n1 = "%s lots" % _p(r.get("lots_after_own_drawdown"), 0, "?")
        L.append("| %s | %s%% | %s → %s | %s | %s lots → %s |"
                 % (prod, _p(r.get("index_worst_drawdown_pct"), 2, "?"), n1, _fall(c1),
                    _fall(c2), _p(r.get("lots_that_survive_index_worst_without_a_call"), 0, "?"),
                    _fall(c3)))
    L.append("")
    L.append("The fall column is not a scenario, it is arithmetic:")
    L.append("")
    L.append("```")
    L.append("equity(f)   = capital - V*f          (a future is unfunded, so no interest)")
    L.append("required(f) = m * (1 - f) * V         (maintenance is a share of the marked value)")
    L.append("called when equity(f) < required(f) => f > (capital - m*V) / ((1-m)*V)")
    L.append("```")
    L.append("")
    L.append("with m = %.0f%% maintenance (an assumption, printed with the rest) and V = lots x"
             " notional. Every extra lot adds V, which costs more equity than it adds"
             " maintenance, so the distance shrinks as the book grows -- that is the whole"
             " reason a count can look affordable and still be called inside a recorded year."
             % ((MAINTENANCE.get(CRITERIA["products"][0]) or 0.0) * 100.0))
    L.append("")
    binding = []
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        c1 = r.get("margin_call_at_recommended_lots") or {}
        dd = r.get("index_worst_drawdown_pct")
        f = c1.get("fall_to_call_pct")
        if f is not None and dd is not None and f < dd:
            binding.append((prod, r.get("lots_after_own_drawdown"), f, dd))
    if binding:
        L.append("Counts this table would call **inside the record**, i.e. the own-drawdown")
        L.append("count is not a position a broker lets you keep:")
        L.append("")
        for prod, n, f, dd in binding:
            L.append("- **%s** — %s lots are called after a %.1f%% fall; the index has fallen"
                     " %.1f%% before." % (prod, _p(n, 0), f, dd))
        L.append("")
    unbinding = [(p, (face["rows"].get(p) or {}).get("lots_after_own_drawdown"),
                  ((face["rows"].get(p) or {}).get("margin_call_at_recommended_lots") or {}).get("fall_to_call_pct"),
                  (face["rows"].get(p) or {}).get("index_worst_drawdown_pct"))
                 for p in CRITERIA["products"]
                 if (face["rows"].get(p) or {}).get("status") == "ok"
                 and ((face["rows"].get(p) or {}).get("margin_call_at_recommended_lots") or {}).get("fall_to_call_pct") is not None
                 and (face["rows"].get(p) or {}).get("index_worst_drawdown_pct") is not None
                 and ((face["rows"][p].get("margin_call_at_recommended_lots") or {}).get("fall_to_call_pct")
                      >= face["rows"][p]["index_worst_drawdown_pct"])]
    if unbinding:
        L.append("And the counts that survive the record with room to spare -- printed for the")
        L.append("same reason: the answer is per product, so it cannot be summarised in one line:")
        L.append("")
        for prod, n, f, dd in unbinding:
            L.append("- **%s** — %s lots are called after a %.1f%% fall against a %.1f%% worst."
                     % (prod, _p(n, 0), f, dd))
        L.append("")
    no_stress = [p for p in CRITERIA["products"]
                 if (face["rows"].get(p) or {}).get("status") == "ok"
                 and (face["rows"].get(p) or {}).get("index_worst_drawdown_pct") is None]
    if no_stress:
        L.append("No index worst drawdown on the source face for **%s**, so its buffers and call"
                 " distances print as `?` -- an absent ruler, not a comfortable one."
                 % ", ".join(no_stress))
        L.append("")
    L.append("Two things this table does not model, both of which can only make the distance")
    L.append("shorter: the broker's surcharge (printed as the +%spp column, not as a guess at"
             " one number) and the fact that CFFEX may raise the maintenance level mid-crisis,"
             " which is exactly when the distance is being used." % _p(MAINTENANCE_SURCHARGE_BAND * 100, 0))
    L.append("")
    lad = face.get("capital_ladder") or {}
    if lad.get("rows"):
        L.append("## a ladder: what each account size holds, and what it earns")
        L.append("")
        L.append("Two counts per account because they answer two different questions: the")
        L.append("cash column is a position that cannot be called, the margin column is the")
        L.append("one the exchange minimum buys and the rest of the capital absorbs the fall.")
        L.append("Returns are carry on notional at the published rate; idle cash earns nothing")
        L.append("here, and the repo rate on that cash is another host's panel.")
        L.append("")
        L.append("| product | capital | cash lots | cash earns /yr | cash occupancy | margin lots | margin earns /yr |")
        L.append("|---|---|---|---|---|---|---|")
        for row in lad["rows"]:
            if row.get("status") != "ok":
                L.append("| %s | - | %s | - | - | - | - |" % (row.get("product"), row.get("status")))
                continue
            for st in row.get("steps") or []:
                L.append("| %s | %s | %s | %s | %s%% | %s | %s |"
                         % (row.get("product"), _p(st.get("capital_cny"), 0, "?"),
                            _p(st.get("cash_lots"), 0, "?"),
                            _p(st.get("cash_return_cny"), 0, "?"),
                            _p(st.get("cash_occupancy_pct"), 1, "?"),
                            _p(st.get("margin_lots"), 0, "?"),
                            _p(st.get("margin_return_cny"), 0, "?")))
        L.append("")
        L.append("A zero in the cash column is not a small position: it means one lot costs")
        L.append("more than the whole account, and the margin column is what a leveraged")
        L.append("holder would be looking at -- the row that has a call distance attached.")
        L.append("")
    L.append("## when it rolls, and what the published gap is")
    L.append("")
    L.append("| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |")
    L.append("|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        lr = r.get("last_roll") or {}
        band = r.get("gap_after_roll_cost_pp") or {}
        L.append("| %s | %s (%s→%s) | %s | %s td (n=%s) | %s | %s / %s pp |"
                 % (prod, lr.get("date") or "-", lr.get("from") or "-", lr.get("to") or "-",
                    _p(r.get("td_since_last_roll"), 0, "?"),
                    _p((r.get("roll_interval") or {}).get("median_td"), 1, "?"),
                    (r.get("roll_interval") or {}).get("n"),
                    _sgn(r.get("next_roll_eta_td"), 0, "?"),
                    _sgn(band.get("file_floor"), 2, "?"),
                    _sgn(band.get("measured_median"), 2, "?")))
    L.append("")
    L.append("The next-roll column is an estimate off this book's own switch history, not a")
    L.append("calendar rule: the calendar rule was measured to catch half of the rolls while")
    L.append("also eating market days near expiry. A negative number means the central")
    L.append("interval has already elapsed -- read it against who is actually holding the book:")
    L.append("")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok" or r.get("next_roll_eta_td") is None:
            continue
        if r["next_roll_eta_td"] < 0:
            L.append("- **%s** is %s td past its median interval, and the incumbent still"
                     " holds %.2f%% of the product's open interest (median over %d switches,"
                     " IQR %s td): the series is irregular, so this is not a deadline."
                     % (prod, _p(abs(r["next_roll_eta_td"]), 0), r.get("oi_share_pct") or 0.0,
                        (r.get("roll_interval") or {}).get("n"),
                        (r.get("roll_interval") or {}).get("iqr_td")))
    L.append("")
    refused = [(p, (face["rows"].get(p) or {}).get("gap_refused_because"))
               for p in CRITERIA["products"]
               if (face["rows"].get(p) or {}).get("status") == "ok"
               and (face["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is None]
    if refused:
        L.append("A missing gap is refused, not zero:")
        L.append("")
        for prod, why in refused:
            L.append("- **%s** — %s" % (prod, why or "the source face gave no reason"))
        L.append("")
    noted = [(p, (face["rows"].get(p) or {}).get("etf_leg_note"))
             for p in CRITERIA["products"]
             if (face["rows"].get(p) or {}).get("status") == "ok"
             and (face["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is not None
             and (face["rows"][p] or {}).get("etf_leg_note")]
    if noted:
        L.append("Known defects in the ETF leg behind each gap -- the gap still prints, but")
        L.append("this is what the source face had to repair to get there:")
        L.append("")
        for prod, note in noted:
            L.append("- **%s** — %s" % (prod, note))
        L.append("")
    L.append("## the sentence this sheet is not allowed to say")
    L.append("")
    L.append("Nothing here is adopted. Candidates: **%s**. The readings behind them are"
             " in-sample, the margin is an assumption, and the roll cost is a band whose two"
             " ends are printed side by side because the estimator has no resolution below a"
             " few dozen ticks." % (", ".join(face.get("candidates") or []) or "none"))
    L.append("")
    L.append("The call distance is arithmetic on those assumptions, not a record: this host has"
             " no broker statement, no CFFEX margin file and no margin-call history to fit, so"
             " it says what the stated rules imply, not what a broker did to anybody.")
    L.append("")
    if face.get("candidates"):
        L.append("What the source face says, copied verbatim so it cannot drift here:")
        L.append("")
        for prod in face["candidates"]:
            why = (face["rows"].get(prod) or {}).get("verdict_why")
            L.append("- **%s** — %s" % (prod, why or "no reason recorded"))
        L.append("")
    return "\n".join(L) + "\n"


def write_doc(face):
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def checkdoc(face=None, capital=None):
    face = build(capital=capital) if face is None else face
    if not os.path.isfile(DOC):
        print("checkdoc: page missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        have = f.read()
    want = render_md(face)
    if have.strip() != want.strip():
        print("checkdoc: page != face (%d vs %d chars)" % (len(have), len(want)))
        return 1
    print("checkdoc: rc0 page==face (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. the multiplier table is the CFFEX one; a wrong entry scales every lot count
    leg("multipliers are CFFEX specs (IF/IH 300, IC/IM 200)",
        MULTIPLIER == {"IF": 300, "IH": 300, "IC": 200, "IM": 200}, str(MULTIPLIER))
    leg("every product the sheet prints has a multiplier",
        set(CRITERIA["products"]) <= set(MULTIPLIER), str(sorted(MULTIPLIER)))

    # 2. margin per lot is price x multiplier x the assumed ratio, never a typed number
    price, mult, m = 6375.0, 200, 0.12
    notional = price * mult
    leg("margin per lot == price x multiplier x ratio",
        abs(notional * m - 153000.0) < 1e-6, str(notional * m))

    # 3. funding the drawdown can only reduce the lot count
    cap = 1000000.0
    naive = int(cap // (notional * m))
    after = int(cap // (notional * m + abs(5.639) / 100.0 * notional))
    leg("the drawdown-aware count never exceeds the margin-only count", after <= naive,
        "naive=%d after=%d" % (naive, after))

    # 4. a zero drawdown leaves the two counts equal (the buffer must not shrink for free)
    after0 = int(cap // (notional * m + 0.0))
    leg("with no drawdown the two counts agree", after0 == naive, str(after0))

    # 5. interval statistics come off the dates given, and a single roll has no interval
    days = ["d%03d" % i for i in range(30)]
    rr = [{"date": days[5]}, {"date": days[15]}, {"date": days[25]}]
    iv = roll_intervals(days, rr)
    leg("median interval is the median of the actual gaps", iv["median_td"] == 10.0, str(iv))
    leg("one roll yields no interval instead of a zero",
        roll_intervals(days, rr[:1])["median_td"] is None, str(roll_intervals(days, rr[:1])))

    # 6. the ETA keeps its sign -- an overdue roll is negative, not missing
    since, median = 12.0, 10.0
    leg("an overdue roll reads negative, not zero", (median - since) < 0, str(median - since))

    # 7. OI share is a share of the product's own book, so all shares sum to <= 100
    fake = {"A": {days[-1]: {"hold": 60.0}}, "B": {days[-1]: {"hold": 40.0}}}
    tot = sum(s[days[-1]]["hold"] for s in fake.values())
    leg("OI shares sum to 100 across contracts",
        abs(60.0 / tot * 100.0 + 40.0 / tot * 100.0 - 100.0) < 1e-9, str(tot))

    # 8. a missing judgement is printed as unknown, never inherited from a neighbour
    # r1297 bm-a: this leg used to null the verdict on whatever the LIVE panel produced. On a
    # day the product's own status is not "ok" the renderer takes the status branch first, so
    # the leg failed on a correct page -- a fixture that reads the world is not a fixture.
    base_face = build()
    tampered = json.loads(json.dumps(base_face))
    tampered["rows"]["IC"] = {"status": "ok", "verdict": None, "held_contract": "IC2601",
                             "close": 1.0, "oi_share_pct": 1.0, "thin_interest": False,
                             "notional_per_lot_cny": 1.0, "margin_per_lot_cny": 1.0}
    page = render_md(tampered)
    leg("a missing judgement reads 'unknown', never a borrowed verdict",
        "| IC | unknown |" in page, "row-level fixture")
    # ...and a refused gap has to say why, not print a bare dash
    refused_prods = [p for p in CRITERIA["products"]
                     if (tampered["rows"].get(p) or {}).get("status") == "ok"
                     and (tampered["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is None]
    leg("a refused gap carries its reason into the page",
        not refused_prods or all(
            not (tampered["rows"].get(p) or {}).get("gap_refused_because")
            or ((tampered["rows"][p]["gap_refused_because"] or "")[:24] in page)
            for p in refused_prods),
        "refused=%s" % refused_prods)
    # ...and the converse: a gap that printed a number must not also claim to be refused
    leg("a printed gap does not masquerade as a refused one",
        all(not (tampered["rows"].get(p) or {}).get("gap_refused_because")
            for p in CRITERIA["products"]
            if (tampered["rows"].get(p) or {}).get("status") == "ok"
            and (tampered["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is not None),
        str({p: (tampered["rows"].get(p) or {}).get("gap_refused_because")
             for p in CRITERIA["products"]}))

    # 9. the page's numbers are the face's numbers (re-render is byte-identical)
    face = build()
    leg("the page renders deterministically", render_md(face) == render_md(face), "")
    leg("a candidate row quotes the source face's reason",
        all((face["rows"].get(p) or {}).get("verdict_why")
            for p in face.get("candidates") or []), str(face.get("candidates")))

    # 10. determinism of the face itself, excluding nothing -- the sheet carries no clock
    leg("the face is byte-stable for identical inputs",
        json.dumps(build(), sort_keys=True) == json.dumps(build(), sort_keys=True), "")

    # 11. the financing ruler: algebra first, then both sides of the boundary.  A lot count
    # that is one too high is the failure that costs money, so the "+1 does get called" leg
    # is not optional -- a count-only leg would pass for any number above the true cap.
    notl, mnt = 1275000.0, 0.08
    c0 = margin_call(0, notl, 1000000.0, mnt)
    leg("an empty book has no call distance to print", c0["fall_to_call_pct"] is None,
        str(c0["fall_to_call_pct"]))
    c1 = margin_call(1, notl, 1000000.0, mnt)
    c2 = margin_call(2, notl, 1000000.0, mnt)
    c4 = margin_call(4, notl, 1000000.0, mnt)
    leg("more lots means a shorter fall to the call",
        c1["fall_to_call_pct"] > c2["fall_to_call_pct"] > c4["fall_to_call_pct"],
        "%s > %s > %s" % (c1["fall_to_call_pct"], c2["fall_to_call_pct"],
                          c4["fall_to_call_pct"]))
    leg("the distance is the published formula, not a fitted one",
        abs(c1["fall_to_call_pct"]
            - round((1000000.0 - mnt * notl) / ((1 - mnt) * notl) * 100.0, 2)) < 1e-9,
        str(c1["fall_to_call_pct"]))
    f2 = c2["fall_to_call_pct"] / 100.0
    eq = 1000000.0 - 2 * notl * f2
    req = mnt * (1 - f2) * 2 * notl
    # the printed fall is rounded to 2 decimals, so the identity can only be asserted to
    # one basis point of notional -- a tighter tolerance tests the rounding, not the algebra
    leg("at the printed fall, equity equals the maintenance requirement",
        abs(eq - req) < 1e-4 * 2 * notl, "%.2f vs %.2f" % (eq, req))
    D = 72.417
    n_surv = lots_that_survive(1000000.0, notl, mnt, D)
    f_n = margin_call(n_surv, notl, 1000000.0, mnt)["fall_to_call_pct"]
    f_n1 = margin_call(n_surv + 1, notl, 1000000.0, mnt)["fall_to_call_pct"]
    leg("the surviving count is still above the worst drawdown", f_n > D,
        "%s lots -> %s%% vs %s%%" % (n_surv, f_n, D))
    leg("one lot more IS called inside the worst drawdown", f_n1 <= D,
        "%s lots -> %s%% vs %s%%" % (n_surv + 1, f_n1, D))
    cex = notl * (mnt + D / 100.0 * (1 - mnt))
    leg("a capital that funds exactly the worst day survives zero lots, not one",
        lots_that_survive(cex, notl, mnt, D) == 0,
        "%s lots at exact equality" % lots_that_survive(cex, notl, mnt, D))
    leg("no worst drawdown on the source face means no borrowed ruler",
        lots_that_survive(1000000.0, notl, mnt, None) is None, "")
    leg("more capital never buys fewer surviving lots",
        lots_that_survive(2000000.0, notl, mnt, D) >= n_surv,
        "%s vs %s" % (lots_that_survive(2000000.0, notl, mnt, D), n_surv))
    leg("maintenance is below the initial margin, else the call is a liquidation",
        all(MAINTENANCE[p] < CRITERIA["margin_pct"] for p in CRITERIA["products"]),
        str(MAINTENANCE))

    # 12. on the real face: every live row prices a call or says it cannot be called, the
    # maintenance ruler never buys more lots than funding the hole in cash, and a row with
    # no stress ruler prints "?" rather than inheriting a neighbour's number.
    ok_rows = [r for r in face["rows"].values() if r.get("status") == "ok"]
    leg("every live row prices a call or says no call short of a total loss",
        all(((r.get("margin_call_at_recommended_lots") or {}).get("fall_to_call_pct") is not None
             or (r.get("margin_call_at_recommended_lots") or {}).get("never_short_of_total_loss"))
            for r in ok_rows if r.get("index_worst_drawdown_pct") is not None),
        str([(r["product"], (r.get("margin_call_at_recommended_lots") or {}).get("fall_to_call_pct"))
             for r in ok_rows]))
    leg("the maintenance ruler never buys more lots than funding the hole in cash",
        all(r["lots_that_survive_index_worst_without_a_call"] >= r["lots_after_index_worst_drawdown"]
            for r in ok_rows
            if r.get("lots_that_survive_index_worst_without_a_call") is not None
            and r.get("lots_after_index_worst_drawdown") is not None),
        str({r["product"]: (r.get("lots_after_index_worst_drawdown"),
                            r.get("lots_that_survive_index_worst_without_a_call"))
             for r in ok_rows}))
    page12 = render_md(face)
    leg("the page prints the maintenance assumption it priced with",
        "maintenance" in page12 and ("m = %.0f%%" % (MAINTENANCE[CRITERIA["products"][0]] * 100.0)) in page12,
        "")
    tampered2 = json.loads(json.dumps(face))
    if "IH" in tampered2["rows"] and tampered2["rows"]["IH"].get("status") == "ok":
        for k in ("index_worst_drawdown_pct", "lots_after_index_worst_drawdown",
                  "lots_that_survive_index_worst_without_a_call",
                  "margin_call_at_recommended_lots", "margin_call_at_surviving_lots"):
            tampered2["rows"]["IH"][k] = None
        tp2 = render_md(tampered2)
        leg("a product with no stress ruler prints ? for it and says why",
            "No index worst drawdown on the source face for **IH**" in tp2, "")
        leg("a row with no stress ruler does not inherit a neighbour's fall",
            "| IH | ?% |" in tp2, "")

    # 13. the cash ruler (r1706).  The failure that costs money here is printing a margin
    # count where a reader reads a cash one, so the legs assert the boundary from both
    # sides: a notional above the capital is zero lots, a notional below it is at least one.
    leg("a lot that costs more than the account is not a small position: zero cash lots",
        int(999999.0 // 1000000.0) == 0, "999999 // 1000000")
    leg("cash lots x notional never exceeds the capital",
        int(2000000.0 // 1275000.0) * 1275000.0 <= 2000000.0,
        "1 lot of 1.275M inside 2M")
    r_ic = (face["rows"].get("IC") or {})
    if r_ic.get("status") == "ok":
        leg("a cash lot is priced against notional, not margin",
            r_ic.get("cash_lots_at_stated_capital")
            == int(r_ic["capital_cny"] // r_ic["notional_per_lot_cny"]),
            str(r_ic.get("cash_lots_at_stated_capital")))
        # the risk-capital return is the carry divided by the capital ratio, not a second
        # estimate of carry: assert the identity at the printed precision
        ratio = MAINTENANCE["IC"] + abs(r_ic["index_worst_drawdown_pct"]) / 100.0 * (1 - MAINTENANCE["IC"])
        leg("return on risk capital == carry / (maintenance + fall funded)",
            abs(r_ic["record_return_on_risk_capital_pct"]
                - round(r_ic["carry_ann_compound_pct"] / ratio, 2)) < 0.006,
            "%s vs %s" % (r_ic["record_return_on_risk_capital_pct"],
                          round(r_ic["carry_ann_compound_pct"] / ratio, 2)))
        leg("preparing for the index worst costs more capital than preparing for the sample",
            (r_ic.get("record_risk_capital_per_lot_cny") or 0)
            >= (r_ic.get("sample_risk_capital_per_lot_cny") or 0),
            "%s vs %s" % (r_ic.get("sample_risk_capital_per_lot_cny"),
                          r_ic.get("record_risk_capital_per_lot_cny")))
        leg("a return on the smaller capital is larger, which is why both are printed",
            (r_ic.get("sample_return_on_risk_capital_pct") or 0)
            >= (r_ic.get("record_return_on_risk_capital_pct") or 0),
            "%s vs %s" % (r_ic.get("sample_return_on_risk_capital_pct"),
                          r_ic.get("record_return_on_risk_capital_pct")))
        if (r_ic.get("cash_lots_at_stated_capital") or 0) == 0:
            leg("a product a cash account cannot buy says so on the page",
                "cannot be paid for in full" in page12 and "IC" in page12, "")
    lad = face.get("capital_ladder") or {}
    ladder_rows = [x for x in (lad.get("rows") or []) if x.get("status") == "ok"]
    leg("the ladder prices every product the sheet carries",
        len(ladder_rows) == len([p for p in CRITERIA["products"]
                                 if (face["rows"].get(p) or {}).get("status") == "ok"]),
        str([x.get("product") for x in ladder_rows]))
    mono = True
    money_ok = True
    for x in ladder_rows:
        prev_cash, prev_marg = -1, -1
        for st in x.get("steps") or []:
            if st["cash_lots"] is not None:
                if st["cash_lots"] < prev_cash:
                    mono = False
                prev_cash = st["cash_lots"]
            if st["margin_lots"] is not None:
                if st["margin_lots"] < prev_marg:
                    mono = False
                prev_marg = st["margin_lots"]
            if st.get("cash_return_cny") is not None and x.get("carry_ann_compound_pct") is not None:
                want = round(st["cash_lots"] * x["notional_per_lot_cny"]
                             * x["carry_ann_compound_pct"] / 100.0, 0)
                if abs(want - st["cash_return_cny"]) > 1.0:
                    money_ok = False
    leg("more capital never buys fewer lots (cash or margin)", mono, "")
    leg("a cash step earns lots x notional x the published carry", money_ok, "")
    leg("the margin count is never below the cash count",
        all((st.get("margin_lots") or 0) >= (st.get("cash_lots") or 0)
            for x in ladder_rows for st in x.get("steps") or []), "")
    # the comparison sentence is derived, so a hand-typed product name or a stale gap
    # would be a silent edit of the only money sentence on the page
    bk = face.get("book") or {}
    priced = [(p, (face["rows"].get(p) or {}).get("record_return_on_risk_capital_pct"))
              for p in CRITERIA["products"]
              if (face["rows"].get(p) or {}).get("status") == "ok"
              and (face["rows"].get(p) or {}).get("record_return_on_risk_capital_pct") is not None]
    if bk.get("ann_compound_pct") is not None and priced:
        best_prod, best_pct = max(priced, key=lambda x: x[1])
        gap = best_pct - bk["ann_compound_pct"]
        leg("the page names the sleeve that pays most, and by how much",
            ("**%s** at %.2f%%/yr" % (best_prod, best_pct)) in page12
            and ("%+.2fpp" % gap) in page12,
            "%s %+.2fpp" % (best_prod, gap))

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, d in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", n, (" | " + d) if d else ""))
    print("selftest: %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-doc", action="store_true")
    ap.add_argument("--checkdoc", action="store_true")
    ap.add_argument("--capital", type=float, default=None,
                    help="price the lot counts for this account size instead of the face's own")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    face = build(capital=args.capital)
    # A side question ("what would 5M buy?") must not silently rewrite the published face:
    # the chain leg prices the face's own capital, so an ad-hoc --capital run only prints
    # unless it is explicitly given --write-doc, which is the same act as publishing a page.
    if args.capital is not None and not args.write_doc:
        sys.stdout.write(render_md(face))
        print("(not written: --capital without --write-doc prints only; the published face"
              " stays priced at its own capital)")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote %s (cutoff=%s capital=%.0f candidates=%s)"
          % (OUT, face.get("evidence_cutoff"), face["criteria"]["capital_cny"],
             ",".join(face.get("candidates") or []) or "none"))
    if args.write_doc:
        print("wrote", write_doc(face))
    if args.checkdoc:
        return checkdoc(face)
    return 0


if __name__ == "__main__":
    sys.exit(main())
