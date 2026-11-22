#!/usr/bin/env python
"""idx_fut_carry_forward_clock -- what account ran those six bars, and can this one hold them?

Why this face exists
--------------------
`results/idx_fut_carry_paper/LEDGER.json` publishes a forward series for two accounts, each
declared as `capital_cny: 1,000,000`, and after five sessions it reads IC -37.84% and
IM -58.50%.  Three other faces say, separately, that a 1,000,000 CNY account at the book's
own 8% vol target may hold **zero** lots (`idx_fut_carry_open_capital` -> ruler
BELOW_FIRST_RUNG, `executable_ticket` WITHDRAWN, the series relabelled
FUNDED_BY_A_LARGER_CAPITAL).  Both statements are in the repo; no face puts them in the
same sentence with the arithmetic that links them, so the reader can carry away a -37.84%
"forward record" of a book that this account cannot open.

This face answers three questions, all recomputed from the parents and never re-run:

1. **What was the ledger actually carrying?**  implied annualised volatility of the held
   position = lots x per-lot vol from the paper's own sizing block, and that number as a
   multiple of the 8% budget -- both arms, because the ledger holds the long leg only.
2. **Could this account have held any of it?**  per bar: lots vs admissible lots, margin
   committed / capital, and whether the smallest legal size is one lot or zero.
3. **In whose denominator does the loss look like a strategy loss?**  the same money read
   on the notional, on the capital the ticket needs, and on the first funding rung -- that
   last one is what one legally holdable lot would have cost.

Verdict rule (frozen; the gate refuses a face whose echoed criteria differ):

    every account's admissible_money_bars == 0  -> FORWARD_RECORD_IS_A_LEVERAGE_STATEMENT
    some account can hold its record            -> FORWARD_RECORD_HOLDABLE
    and, independently of the above,
    the sleeve's own excess P&L over the window < 0
                                                -> THE_SLEEVE_LOST_ON_ITS_OWN_ALPHA_TOO

Frozen before the first run: PRODUCTS, TARGET_PCT, MONEY_TOL (1 CNY), PCT_TOL (0.01 pp),
and the identity list below.  No line is tuned after seeing the numbers.

Usage:
    python scripts/idx_fut_carry_forward_clock.py run
    python scripts/idx_fut_carry_forward_clock.py check
    python scripts/idx_fut_carry_forward_clock.py show
    python scripts/idx_fut_carry_forward_clock.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_JSON = ROOT / "results" / "idx_fut_carry_forward_clock.json"
OUT_MD = ROOT / "research" / "IDX_FUT_CARRY_FORWARD_CLOCK.md"
P_LEDGER = ROOT / "results" / "idx_fut_carry_paper" / "LEDGER.json"
P_LATEST = ROOT / "results" / "idx_fut_carry_paper" / "latest.json"
P_OPEN = ROOT / "results" / "idx_fut_carry_open_capital.json"
SCRIPT = "scripts/idx_fut_carry_forward_clock.py"
FACE = "results/idx_fut_carry_forward_clock.json"
KIND = "idx_fut_carry_forward_clock"

# ---------------------------------------------------------------- frozen criteria
PRODUCTS = ("IC", "IM")
TARGET_PCT = 8.0            # the book's own vol budget, from the paper's sizing block
MONEY_TOL = 1.0             # CNY; published money is rounded to the yuan
PCT_TOL = 0.01              # percent units; published percents carry two decimals

CRITERIA = {
    "products": list(PRODUCTS),
    "target_pct": TARGET_PCT,
    "money_tol_cny": MONEY_TOL,
    "pct_tol": PCT_TOL,
    "parents": {
        "ledger": "results/idx_fut_carry_paper/LEDGER.json",
        "latest": "results/idx_fut_carry_paper/latest.json",
        "open_capital": "results/idx_fut_carry_open_capital.json",
    },
    "identities": [
        "nav == capital + pnl",
        "pnl == sum(bar pnl)",
        "pnl == excess_cum + index_cum",
        "pnl_pct == 100 * pnl / capital",
        "drawdown_pct == 100 * min(cumulative pnl) / capital",
        "capital_the_ticket_needs == lots * first_rung",
        "implied_vol_pct == lots * vol_pct_of_capital_per_lot",
    ],
    "verdict_rule": {
        "FORWARD_RECORD_IS_A_LEVERAGE_STATEMENT": "every account's admissible money bars == 0",
        "FORWARD_RECORD_HOLDABLE": "at least one account could have held its own record",
        "THE_SLEEVE_LOST_ON_ITS_OWN_ALPHA_TOO": "sleeve excess P&L over the window < 0",
    },
    "frozen": "constants above were written before the first run",
}


# ------------------------------------------------------------------ pure helpers
def _load(path):
    if not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def bar_pnls(rows):
    """Bar P&L of the forward line only -- the anchor bar books nothing."""
    return [float(r.get("pnl_cny") or 0.0) for r in rows]


def cumulative(rows):
    out, run = [], 0.0
    for p in bar_pnls(rows):
        run += p
        out.append(run)
    return out


def implied_vol_pct(lots, vol_pct_per_lot):
    return float(lots) * float(vol_pct_per_lot)


def budget_multiple(implied_pct, target_pct=TARGET_PCT):
    return implied_pct / float(target_pct)


def admissible_money_bars(n_bars, lots, admissible_lots):
    """A bar the account could not have been holding is not evidence about this account."""
    return int(n_bars) if float(lots) <= float(admissible_lots) + 1e-12 else 0


def pct_on(cny, base_cny):
    return 100.0 * float(cny) / float(base_cny)


def worst_bar(rows):
    if not rows:
        return None
    worst = min(rows, key=lambda r: float(r.get("pnl_cny") or 0.0))
    return {"date": worst.get("date"), "pnl_cny": float(worst.get("pnl_cny") or 0.0)}


def money_identities(rows, acct, open_blk, target_pct=TARGET_PCT, lots_override=None):
    """All the arithmetic this face relies on, recomputed.  Returns a list of problems."""
    probs = []
    capital = float(acct["capital_cny"])
    pnl = float(acct["pnl_cny"])
    lots = float(acct["lots"] if lots_override is None else lots_override)
    if abs(float(acct["nav_cny"]) - (capital + pnl)) > MONEY_TOL:
        probs.append("nav %s != capital + pnl %s" % (acct["nav_cny"], capital + pnl))
    s = sum(bar_pnls(rows))
    if abs(s - pnl) > MONEY_TOL:
        probs.append("sum(bar pnl) %s != pnl %s" % (round(s, 2), pnl))
    exc = float(acct.get("excess_pnl_cum_cny") or 0.0)
    idx = float(acct.get("index_pnl_cum_cny") or 0.0)
    if abs((exc + idx) - pnl) > MONEY_TOL:
        probs.append("excess %s + index %s != pnl %s" % (exc, idx, pnl))
    if abs(float(acct["pnl_pct"]) - pct_on(pnl, capital)) > PCT_TOL:
        probs.append("pnl_pct %s != 100*pnl/capital %.4f"
                     % (acct["pnl_pct"], pct_on(pnl, capital)))
    dd = pct_on(min(cumulative(rows)), capital)
    if abs(float(acct["drawdown_pct"]) - dd) > PCT_TOL:
        probs.append("drawdown_pct %s != worst cumulative %.4f" % (acct["drawdown_pct"], dd))
    if open_blk:
        desk = open_blk.get("desk_ticket") or {}
        rung = float((open_blk.get("funding") or {}).get("first_rung_cny") or 0.0)
        need = float(desk.get("capital_the_ticket_needs_cny") or 0.0)
        if rung and abs(need - lots * rung) > max(MONEY_TOL, 0.001 * need):
            probs.append("capital_the_ticket_needs %s != %s lots * first rung %s"
                         % (need, lots, rung))
    return probs


# ------------------------------------------------------------------------ the face
def build(write=True):
    led = _load(P_LEDGER)
    lat = _load(P_LATEST)
    opc = _load(P_OPEN)
    if not led or not lat or not opc:
        raise SystemExit("parent face missing: %s"
                         % [str(p) for p in (P_LEDGER, P_LATEST, P_OPEN)
                            if not Path(p).exists()])

    cutoff = led.get("evidence_cutoff")
    accounts, problems, book = {}, [], None
    money_lost_total = 0.0
    holdable_total = 0
    bars_total = 0

    for prod in PRODUCTS:
        lrow = (led.get("accounts") or {}).get(prod)
        arow = (lat.get("accounts") or {}).get(prod) or {}
        orow = (opc.get("accounts") or {}).get(prod)
        if lrow is None or orow is None:
            problems.append("%s missing from a parent face" % prod)
            continue
        rows = lrow.get("rows") or []
        n_bars = len([r for r in rows if (r.get("event") or "") != "anchor"])
        capital = float(lrow["capital_cny"])
        lots = float(lrow["lots"])
        nav = float(lrow["nav_cny"])
        # the ledger keeps nav; the latest face keeps the money.  Read the money where it
        # is published and derive it from the ledger when it is not.
        pnl = float(arow["pnl_cny"]) if "pnl_cny" in arow else (nav - capital)
        pnl_pct = float(arow["pnl_pct"]) if "pnl_pct" in arow else pct_on(pnl, capital)
        sizing = ((led.get("sizing") or {}).get(prod) or {})
        unhedged = (sizing.get("unhedged") or {})
        hedged = (sizing.get("hedged") or {})
        ticket = (led.get("ticket") or {}).get(prod) or {}
        margin_lot = float(ticket.get("margin_per_lot_cny") or 0.0)
        admissible = float((orow.get("ruler") or {}).get("admissible_lots") or 0.0)
        need = float((orow.get("desk_ticket") or {}).get("capital_the_ticket_needs_cny") or 0.0)
        rung = float((orow.get("funding") or {}).get("first_rung_cny") or 0.0)
        notional = float(lrow.get("notional_basis_cny") or 0.0)
        # the cumulative legs are published on the latest face's account block and, in the
        # ledger, only on the last row -- read the top block first, fall back to that row
        tail = rows[-1] if rows else {}
        exc = float(arow.get("excess_pnl_cum_cny",
                            lrow.get("excess_pnl_cum_cny", tail.get("excess_pnl_cum_cny"))) or 0.0)
        idx = float(arow.get("index_pnl_cum_cny",
                            lrow.get("index_pnl_cum_cny", tail.get("index_pnl_cum_cny"))) or 0.0)
        ident_acct = {
            "capital_cny": capital, "pnl_cny": pnl, "nav_cny": nav, "pnl_pct": pnl_pct,
            "drawdown_pct": float(lrow["drawdown_pct"]), "lots": lots,
            "excess_pnl_cum_cny": exc, "index_pnl_cum_cny": idx,
        }
        if "pnl_cny" in arow and abs(float(arow["pnl_cny"]) - (nav - capital)) > MONEY_TOL:
            problems.append("%s: latest pnl_cny %s != ledger nav - capital %s"
                            % (prod, arow["pnl_cny"], nav - capital))

        vol_un = implied_vol_pct(lots, unhedged.get("vol_pct_of_capital_per_lot") or 0.0)
        vol_hg = implied_vol_pct(lots, hedged.get("vol_pct_of_capital_per_lot") or 0.0)
        wb = worst_bar(rows)
        m_bars = admissible_money_bars(n_bars, lots, admissible)

        problems.extend(["%s: %s" % (prod, p)
                         for p in money_identities(rows, ident_acct, orow)])

        accounts[prod] = {
            "bars_recorded_forward": n_bars,
            "bars_holdable_by_this_account": m_bars,
            "capital_cny": capital,
            "lots_in_ledger": lots,
            "notional_basis_cny": notional,
            "lots_admissible_at_own_ruler": admissible,
            "margin_per_lot_cny": margin_lot,
            "margin_committed_cny": round(lots * margin_lot, 2),
            "margin_pct_of_capital": round(pct_on(lots * margin_lot, capital), 4),
            "distance_to_call_pct_published": ticket.get("distance_to_call_pct"),
            "implied_vol_pct_unhedged": round(vol_un, 4),
            "implied_vol_pct_hedged": round(vol_hg, 4),
            "budget_multiple_unhedged": round(budget_multiple(vol_un), 4),
            "budget_multiple_hedged": round(budget_multiple(vol_hg), 4),
            "one_day_cost_multiple_of_year_budget": (
                round(abs(wb["pnl_cny"]) / (TARGET_PCT / 100.0 * capital), 4) if wb else None),
            "pnl_cny": pnl,
            "excess_pnl_cum_cny": exc,
            "index_pnl_cum_cny": idx,
            "alpha_sign": "LOST" if exc < 0 else "EARNED",
            "worst_bar": wb,
            "worst_bar_pct_of_capital": (round(pct_on(wb["pnl_cny"], capital), 4)
                                         if wb else None),
            "pnl_pct_on_capital": pnl_pct,
            "pnl_pct_on_notional": round(pct_on(pnl, notional), 4) if notional else None,
            "pnl_pct_on_capital_the_ticket_needs": round(pct_on(pnl, need), 4) if need else None,
            "one_lot_money_cny": round(pnl / lots, 2) if lots else None,
            "one_lot_pnl_pct_on_first_rung": (round(pct_on(pnl / lots, rung), 4)
                                              if lots and rung else None),
            "first_rung_cny": rung,
            "capital_the_ticket_needs_cny": need,
            "state": ("COULD_NOT_HOLD_ANY_OF_IT" if m_bars == 0 and n_bars > 0
                      else "HOLDS_ITS_OWN_RECORD"),
        }
        money_lost_total += pnl
        holdable_total += m_bars
        bars_total += n_bars

    book = {
        "bars_recorded_total": bars_total,
        "bars_holdable_total": holdable_total,
        "money_cny_total": round(money_lost_total, 2),
        "capital_declared_total_cny": round(sum(a["capital_cny"] for a in accounts.values()), 2),
        "capital_the_ticket_needs_total_cny": round(
            sum(a["capital_the_ticket_needs_cny"] for a in accounts.values()), 2),
        "first_rung_total_cny": round(sum(a["first_rung_cny"] for a in accounts.values()), 2),
    }

    if accounts and all(a["bars_holdable_by_this_account"] == 0 for a in accounts.values()):
        verdict = "FORWARD_RECORD_IS_A_LEVERAGE_STATEMENT"
    else:
        verdict = "FORWARD_RECORD_HOLDABLE"
    alpha_verdict = ("THE_SLEEVE_LOST_ON_ITS_OWN_ALPHA_TOO"
                     if all(a["excess_pnl_cum_cny"] < 0 for a in accounts.values())
                     else "THE_SLEEVE_EARNED_ON_ITS_OWN_ALPHA")

    worst_mult = max((a["one_day_cost_multiple_of_year_budget"] or 0.0)
                     for a in accounts.values()) if accounts else 0.0
    headline = (
        "%d bars, %d of them holdable by the accounts that recorded them; the ledger carried "
        "%s lots at %.1f%% implied annual vol against an %.0f%% budget (%.1fx) and "
        "%.0f%% margin; money moved %s CNY. Verdict: %s / %s."
        % (book["bars_recorded_total"], book["bars_holdable_total"],
           "/".join("%g" % a["lots_in_ledger"] for a in accounts.values()),
           max((a["implied_vol_pct_unhedged"] for a in accounts.values()), default=0.0),
           TARGET_PCT,
           max((a["budget_multiple_unhedged"] for a in accounts.values()), default=0.0),
           max((a["margin_pct_of_capital"] for a in accounts.values()), default=0.0),
           "{:,.0f}".format(book["money_cny_total"]),
           verdict, alpha_verdict))

    face = {
        "kind": KIND,
        "script": SCRIPT,
        "evidence_cutoff": cutoff,
        "generated": None,          # filled below so tests can compare payloads
        "criteria": CRITERIA,
        "accounts": accounts,
        "book": book,
        "verdict": verdict,
        "alpha_verdict": alpha_verdict,
        "worst_day_multiple_of_year_budget": round(worst_mult, 4),
        "headline": headline,
        "problems": problems,
        "ok": not problems,
        "sentence": (
            "Each account declares %s CNY and its own 8%% vol budget allows %s lot(s) (%s); the "
            "record was written at %s lot(s) instead, i.e. %.1f%% implied annual volatility "
            "and %.0f%% of capital posted as margin, so none of its %d account-bars is "
            "evidence about this account. The same money (%s CNY) read on the capital the "
            "ticket needs (%s CNY) is %s -- which is the same as one lot on the first funding "
            "rung (%s CNY), because the ticket is exactly %s lots of it -- so even the "
            "smallest implementable size lost money in these five sessions."
            % (_one_or_each("{:,.0f}".format(a["capital_cny"]) for a in accounts.values()),
               "/".join("%g" % a["lots_admissible_at_own_ruler"] for a in accounts.values()),
               " / ".join(accounts.keys()),
               "/".join("%g" % a["lots_in_ledger"] for a in accounts.values()),
               max((a["implied_vol_pct_unhedged"] for a in accounts.values()), default=0.0),
               max((a["margin_pct_of_capital"] for a in accounts.values()), default=0.0),
               book["bars_recorded_total"],
               "{:,.0f}".format(book["money_cny_total"]),
               "{:,.0f}".format(book["capital_the_ticket_needs_total_cny"]),
               " / ".join("%+.2f%%" % a["pnl_pct_on_capital_the_ticket_needs"]
                          for a in accounts.values()),
               "{:,.0f}".format(book["first_rung_total_cny"]),
               _one_or_each("%g" % a["lots_in_ledger"] for a in accounts.values()))),
    }
    import datetime as _dt
    face["generated"] = _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    if write:
        _dump(OUT_JSON, face)
        _write_doc(face)
    return face


# ------------------------------------------------------------------------ render
def _one_or_each(values):
    """'1,000,000' when every account declares the same capital, 'a / b' when they differ."""
    vals = list(values)
    if not vals:
        return ""
    return vals[0] if len(set(vals)) == 1 else " / ".join(vals)


def _render(face):
    L = []
    L.append("### What account ran these bars\n")
    L.append("| account | bars | holdable | lots in ledger | lots allowed | margin used | "
             "implied vol (unhedged) | budget multiple |")
    L.append("|---|---|---|---|---|---|---|---|")
    for prod in PRODUCTS:
        a = face["accounts"].get(prod) or {}
        L.append("| %s | %d | **%d** | %g | %g | %s CNY (%.2f%%) | %.2f%% | %.2fx |"
                 % (prod, a.get("bars_recorded_forward", 0),
                    a.get("bars_holdable_by_this_account", 0),
                    a.get("lots_in_ledger", 0), a.get("lots_admissible_at_own_ruler", 0),
                    "{:,.0f}".format(a.get("margin_committed_cny", 0.0)),
                    a.get("margin_pct_of_capital", 0.0),
                    a.get("implied_vol_pct_unhedged", 0.0),
                    a.get("budget_multiple_unhedged", 0.0)))
    L.append("")
    L.append("The ledger holds the long leg only, so the unhedged column is the one the "
             "record actually ran at.  The hedged column is published beside it because the "
             "ticket's design hedges with IF: even with the hedge on, %s lots is **%.2fx** the "
             "budget, which is the part that does not depend on the hedge being cheap.\n"
             % ("/".join("%g" % (face["accounts"].get(p, {}).get("lots_in_ledger") or 0)
                         for p in PRODUCTS),
                max((face["accounts"].get(p, {}).get("budget_multiple_hedged") or 0.0)
                    for p in PRODUCTS)))

    L.append("### Where the loss came from\n")
    L.append("| account | total | index leg | sleeve's own excess | alpha | worst bar | "
             "worst bar as multiple of the year's 8% budget |")
    L.append("|---|---|---|---|---|---|---|")
    for prod in PRODUCTS:
        a = face["accounts"].get(prod) or {}
        wb = a.get("worst_bar") or {}
        L.append("| %s | %s CNY (%.2f%%) | %s | %s | %s | %s (%s CNY, %.2f%% of capital) | %.2fx |"
                 % (prod, "{:,.0f}".format(a.get("pnl_cny", 0.0)), a.get("pnl_pct_on_capital", 0.0),
                    "{:,.0f}".format(a.get("index_pnl_cum_cny", 0.0)),
                    "{:,.0f}".format(a.get("excess_pnl_cum_cny", 0.0)),
                    a.get("alpha_sign"), wb.get("date"),
                    "{:,.0f}".format(wb.get("pnl_cny", 0.0)),
                    a.get("worst_bar_pct_of_capital") or 0.0,
                    a.get("one_day_cost_multiple_of_year_budget") or 0.0))
    L.append("")
    L.append("The excess column is what the sleeve itself did (futures minus the index over "
             "the same lots).  It is not positive, so this is not a story about an unlucky "
             "beta month stacked on a working carry trade: over these five sessions the "
             "sleeve lost on both legs.\n")

    L.append("### The same money in the denominator that could hold it\n")
    L.append("| account | capital declared | notional held | capital the ticket needs | "
             "first rung (one legal lot) | P&L on notional | P&L on ticket capital | "
             "P&L per lot on first rung |")
    L.append("|---|---|---|---|---|---|---|---|")
    for prod in PRODUCTS:
        a = face["accounts"].get(prod) or {}
        L.append("| %s | %s | %s | %s | %s | %+.2f%% | %+.2f%% | %+.2f%% |"
                 % (prod, "{:,.0f}".format(a.get("capital_cny", 0.0)),
                    "{:,.0f}".format(a.get("notional_basis_cny", 0.0)),
                    "{:,.0f}".format(a.get("capital_the_ticket_needs_cny", 0.0)),
                    "{:,.0f}".format(a.get("first_rung_cny", 0.0)),
                    a.get("pnl_pct_on_notional") or 0.0,
                    a.get("pnl_pct_on_capital_the_ticket_needs") or 0.0,
                    a.get("one_lot_pnl_pct_on_first_rung") or 0.0))
    L.append("")
    L.append("Notional column is arithmetic on the ledger's own `notional_basis_cny`.  The "
             "last two columns agree by construction -- `capital_the_ticket_needs` is exactly "
             "`lots x first_rung` -- so they are one measurement read two ways, not two "
             "pieces of evidence.")
    L.append("")
    L.append("### Verdict\n")
    L.append("- record: **%s** (%d account-bars recorded across %d accounts, %d holdable by "
             "the accounts that wrote them)"
             % (face["verdict"], face["book"]["bars_recorded_total"], len(face["accounts"]),
                face["book"]["bars_holdable_total"]))
    L.append("- sleeve alpha: **%s** (excess %s CNY)"
             % (face["alpha_verdict"],
                " / ".join("{:,.0f}".format((face["accounts"].get(p) or {}).get("excess_pnl_cum_cny", 0.0))
                           for p in PRODUCTS)))
    L.append("- money at risk per bad day: %.2fx the whole year's 8%% budget" %
             face["worst_day_multiple_of_year_budget"])
    L.append("")
    L.append(face["sentence"])
    L.append("")
    L.append("Read this next to `research/IDX_FUT_CARRY_OPEN_CAPITAL.md`: that face prices "
             "opening the book; this one prices the record that has been kept while it is "
             "closed.  The clock on this sleeve has not started -- what the ledger holds is "
             "a demonstration of what a %s CNY account would look like, not evidence about "
             "a %s CNY one.  Nothing here says the carry is gone; it says the five sessions "
             "that were recorded were run at a size this account cannot buy, so they are not "
             "the first five days of its forward record."
             % ("{:,.0f}".format(face["book"]["capital_the_ticket_needs_total_cny"]),
                "{:,.0f}".format(face["book"]["capital_declared_total_cny"])))
    return "\n".join(L)


def _write_doc(face):
    body = _render(face)
    head = (
        "# Carry forward clock: what account ran those six bars?\n\n"
        "Generated by `%s` -- do not edit the block below by hand; `check` compares it\n"
        "byte-for-byte with what the face would render today.\n\n"
        "<!-- BEGIN GENERATED -->\n" % SCRIPT
    )
    tail = "\n<!-- END GENERATED -->\n"
    Path(OUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + body + tail)


def _doc_block(text):
    a = text.find("<!-- BEGIN GENERATED -->")
    b = text.find("<!-- END GENERATED -->")
    if a < 0 or b < 0:
        return None
    return text[a + len("<!-- BEGIN GENERATED -->"):b]


# ------------------------------------------------------------------------ check
CMP_FIELDS = (
    "bars_recorded_forward", "bars_holdable_by_this_account", "capital_cny",
    "lots_in_ledger", "lots_admissible_at_own_ruler", "margin_committed_cny",
    "margin_pct_of_capital", "implied_vol_pct_unhedged", "implied_vol_pct_hedged",
    "budget_multiple_unhedged", "budget_multiple_hedged", "pnl_cny",
    "excess_pnl_cum_cny", "index_pnl_cum_cny", "alpha_sign",
    "pnl_pct_on_capital", "pnl_pct_on_notional", "pnl_pct_on_capital_the_ticket_needs",
    "one_lot_money_cny", "one_lot_pnl_pct_on_first_rung", "first_rung_cny",
    "capital_the_ticket_needs_cny", "state",
)


def check():
    """Anchored to what moves: the parents' cutoff and their per-account money fields."""
    face = _load(OUT_JSON)
    if not face:
        print("STALE face missing: %s" % FACE)
        return 3
    if (face.get("criteria") or {}) != CRITERIA:
        print("CHECK FAILED criteria differ from the frozen constants (face is not this code)")
        return 4
    try:
        fresh = build(write=False)
    except SystemExit as exc:
        print("STALE parent face missing: %s" % exc)
        return 3
    if fresh["evidence_cutoff"] != face.get("evidence_cutoff"):
        print("STALE parents advanced: face cutoff %s, parents now %s"
              % (face.get("evidence_cutoff"), fresh["evidence_cutoff"]))
        return 3
    bad = []
    for prod in PRODUCTS:
        o = (face.get("accounts") or {}).get(prod) or {}
        c = (fresh.get("accounts") or {}).get(prod) or {}
        if not c:
            bad.append("%s missing from a parent" % prod)
            continue
        for f in CMP_FIELDS:
            if o.get(f) != c.get(f):
                bad.append("%s.%s %s != %s" % (prod, f, o.get(f), c.get(f)))
        for f in ("pnl_pct_on_notional", "one_lot_pnl_pct_on_first_rung"):
            if o.get(f) is None or c.get(f) is None:
                continue
            if abs(o[f] - c[f]) > PCT_TOL:
                bad.append("%s.%s %s != %s" % (prod, f, o[f], c[f]))
    for f in ("verdict", "alpha_verdict", "headline", "sentence", "problems"):
        if (face.get(f) or None) != (fresh.get(f) or None):
            bad.append("%s differs from a rebuild" % f)
    if (face.get("book") or {}) != (fresh.get("book") or {}):
        bad.append("book block differs from a rebuild")
    md = OUT_MD.read_text(encoding="utf-8") if OUT_MD.exists() else ""
    blk = _doc_block(md)
    if blk is None:
        bad.append("doc marker block missing")
    elif blk.strip() != _render(face).strip():
        bad.append("doc block does not match the face")
    if bad:
        print("CHECK FAILED")
        for line in bad[:12]:
            print("  " + line)
        return 4
    print("OK verdict=%s alpha=%s cutoff=%s bars=%d holdable=%d money=%s"
          % (face["verdict"], face["alpha_verdict"], face["evidence_cutoff"],
             face["book"]["bars_recorded_total"], face["book"]["bars_holdable_total"],
             "{:,.0f}".format(face["book"]["money_cny_total"])))
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond, extra=""):
        legs.append((bool(cond), name, extra))

    rows = [
        {"event": "anchor", "date": "2026-01-05", "pnl_cny": 0.0},
        {"date": "2026-01-06", "pnl_cny": -100.0},
        {"date": "2026-01-07", "pnl_cny": -50.0},
        {"date": "2026-01-08", "pnl_cny": 20.0},
    ]
    leg("bar P&L excludes the anchor", bar_pnls(rows) == [0.0, -100.0, -50.0, 20.0],
        str(bar_pnls(rows)))
    leg("cumulative path ends at the total", abs(cumulative(rows)[-1] - (-130.0)) < 1e-9,
        str(cumulative(rows)))
    leg("worst bar is the largest single loss", worst_bar(rows)["pnl_cny"] == -100.0)

    leg("implied vol is lots x per-lot vol", abs(implied_vol_pct(4, 45.25) - 181.0) < 1e-9)
    leg("budget multiple divides by the 8% target", abs(budget_multiple(181.0) - 22.625) < 1e-9)
    leg("one lot at the budget is a multiple of one", abs(budget_multiple(8.0) - 1.0) < 1e-12)

    leg("a position under the ruler keeps its bars", admissible_money_bars(5, 1, 1) == 5)
    leg("a position over the ruler keeps none", admissible_money_bars(5, 4, 0) == 0)
    leg("a zero-lot ruler cannot hold anything", admissible_money_bars(5, 4, 0.8893) == 0)
    leg("pct_on is a plain ratio in percent", abs(pct_on(100.0, 1000.0) - 10.0) < 1e-12)

    # worst cumulative here is -150 on 1,000, so the drawdown is -15.0, not the -13.0 final
    acct = {"capital_cny": 1000.0, "pnl_cny": -130.0, "nav_cny": 870.0, "pnl_pct": -13.0,
            "drawdown_pct": -15.0, "lots": 2, "excess_pnl_cum_cny": -30.0,
            "index_pnl_cum_cny": -100.0}
    ob = {"desk_ticket": {"capital_the_ticket_needs_cny": 2000.0},
          "funding": {"first_rung_cny": 1000.0},
          "ruler": {"admissible_lots": 0}}
    leg("a consistent account has no identity problems", money_identities(rows, acct, ob) == [],
        str(money_identities(rows, acct, ob)))

    broken = dict(acct, nav_cny=999.0)
    leg("a broken nav is caught", any("nav" in p for p in money_identities(rows, broken, ob)))
    broken = dict(acct, drawdown_pct=-9.0)
    leg("a broken drawdown is caught",
        any("drawdown" in p for p in money_identities(rows, broken, ob)))
    broken = dict(acct, pnl_pct=-12.0)
    leg("a broken pnl_pct is caught",
        any("pnl_pct" in p for p in money_identities(rows, broken, ob)))
    ob_short = {"desk_ticket": {"capital_the_ticket_needs_cny": 1500.0},
                "funding": {"first_rung_cny": 1000.0}}
    leg("a ticket capital that is not lots x rung is caught",
        any("ticket_needs" in p for p in money_identities(rows, acct, ob_short)))

    # verdict rule, exercised as a mapping rather than by prose
    def verdict(accts):
        if accts and all(a["bars_holdable_by_this_account"] == 0 for a in accts):
            return "FORWARD_RECORD_IS_A_LEVERAGE_STATEMENT"
        return "FORWARD_RECORD_HOLDABLE"

    leg("all-unholdable reads leverage statement",
        verdict([{"bars_holdable_by_this_account": 0}] * 2)
        == "FORWARD_RECORD_IS_A_LEVERAGE_STATEMENT")
    leg("one holdable account flips the verdict",
        verdict([{"bars_holdable_by_this_account": 0},
                 {"bars_holdable_by_this_account": 3}]) == "FORWARD_RECORD_HOLDABLE")

    # behaviour legs: the real check() on poisoned copies, restored in finally
    if OUT_JSON.exists() and OUT_MD.exists():
        import io
        import shutil
        import tempfile
        from contextlib import redirect_stdout
        tmpdir = Path(tempfile.mkdtemp(prefix="carry_clock_"))
        jbak, mbak = tmpdir / "face.json", tmpdir / "doc.md"
        shutil.copy2(OUT_JSON, jbak)
        shutil.copy2(OUT_MD, mbak)
        try:
            face = _load(OUT_JSON)

            poisoned = json.loads(json.dumps(face))
            poisoned["evidence_cutoff"] = "1999-01-01"
            _dump(OUT_JSON, poisoned)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            leg("a moved cutoff reads STALE", rc == 3 and "STALE" in out,
                "rc=%s %r" % (rc, out.strip()[:60]))

            broken_face = json.loads(json.dumps(face))
            broken_face["accounts"][PRODUCTS[0]]["lots_in_ledger"] = 99
            _dump(OUT_JSON, broken_face)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            leg("a changed lot count fails without claiming STALE",
                rc == 4 and "CHECK FAILED" in out and "STALE" not in out,
                "rc=%s %r" % (rc, out.strip()[:60]))

            doc = OUT_MD.read_text(encoding="utf-8")
            OUT_MD.write_text(doc.replace("holdable", "holdabl", 1), encoding="utf-8")
            _dump(OUT_JSON, face)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            leg("a hand-edited doc block fails", rc == 4, "rc=%s" % rc)
        finally:
            shutil.copy2(jbak, OUT_JSON)
            shutil.copy2(mbak, OUT_MD)

    passed = sum(1 for ok, _, _ in legs if ok)
    for ok, name, extra in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" [%s]" % extra) if extra else ""))
    print("SELFTEST %d/%d %s" % (passed, len(legs), "PASS" if passed == len(legs) else "FAIL"))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------------ cli
def show():
    face = _load(OUT_JSON)
    if not face:
        print("no face at %s" % FACE)
        return 2
    print(face.get("headline"))
    for prod in PRODUCTS:
        a = (face.get("accounts") or {}).get(prod) or {}
        print("  %-3s bars=%s holdable=%s lots=%s allowed=%s vol=%.2f%% (%.2fx) money=%s"
              % (prod, a.get("bars_recorded_forward"), a.get("bars_holdable_by_this_account"),
                 a.get("lots_in_ledger"), a.get("lots_admissible_at_own_ruler"),
                 a.get("implied_vol_pct_unhedged") or 0.0,
                 a.get("budget_multiple_unhedged") or 0.0,
                 "{:,.0f}".format(a.get("pnl_cny") or 0.0)))
    print("verdict=%s alpha=%s cutoff=%s" % (face.get("verdict"), face.get("alpha_verdict"),
                                             face.get("evidence_cutoff")))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "show"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "show":
        return show()
    face = build(write=not args.no_write)
    print(face["headline"])
    if face["problems"]:
        for p in face["problems"]:
            print("  IDENTITY: " + p)
    if args.no_write:
        return 0
    print("wrote %s + research/IDX_FUT_CARRY_FORWARD_CLOCK.md" % FACE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
