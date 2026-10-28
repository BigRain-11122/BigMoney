"""Capital placement: what each vehicle actually pays at a given account size.

The book, the four-ETF basket and the futures sleeve have been measured separately,
each in its own window and its own cost model. Nobody had put them on one axis --
account size -- which is the only axis a capital allocator actually holds. This face
reads the three published result files and answers, per capital tier, "what does this
vehicle pay in CNY per year", with the capacity ceiling applied where one exists and
the cash remainder priced at the repo leg.

It deliberately does NOT re-measure anything. Every number below is read from a
published face and carries that face's file name; if a face is missing the vehicle is
reported `unavailable` instead of being silently zeroed.

Reading rules baked into the output (all selftested):
  * returns are fractions. 0.1009 means 10.09%/yr, never 100.9%.
  * the book cannot deploy more than its 1%-of-ADV ceiling; the excess sits in repo
    at the NET cash rate (gross quote minus the roll commission measured in r1258).
  * the basket's turnover is 1.0 for the whole window -- it is bought once and held,
    so its binding constraint is the entry print, not daily liquidity. That difference
    is disclosed rather than modelled.
  * the futures sleeve below its capital floor is `below_floor`, not a 0.15% sleeve.

Usage:
    python scripts/capital_placement.py run          # write results/capital_placement.json + md
    python scripts/capital_placement.py --selftest   # offline checks, no writes
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SPANNING = "results/etf_book_spanning.json"
RECONCILE = "results/etf_book_cagr_reconcile.json"
CAPACITY = "results/etf_book_capacity_rule.json"
FUTURES = "results/futures_sleeve_economics.json"

# Disciplined participation rule for the book (p90 participation of a decision's trade
# against ADV). 1% is the production rule; 2% and 5% are printed as stretch columns by
# the capacity face itself and are not used to size anything here.
BOOK_PARTICIPATION = 0.01

# GROSS repo quote (r1255) minus the roll commission (r1258 cash ladder, GC001): the
# cash remainder is not free to hold.
CASH_NET_ANNUAL = 0.01777

TIERS = [300_000, 1_000_000, 1_500_000, 3_000_000, 8_000_000, 50_000_000]

OUT_JSON = RESULTS / "capital_placement.json"
OUT_MD = ROOT / "research" / "CAPITAL_PLACEMENT.md"


def _load(rel):
    p = ROOT / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def gather():
    """Read every input once. Missing faces stay None so the caller can say so."""
    sp, cap, fut = _load(SPANNING), _load(CAPACITY), _load(FUTURES)

    book = {"source": SPANNING, "available": False}
    basket = {"source": SPANNING, "available": False}
    if sp:
        b = sp.get("book") or {}
        if _num(b.get("cagr")):
            book.update(available=True, cagr=float(b["cagr"]), sharpe=b.get("sharpe"),
                        maxdd=b.get("maxdd"), vol=b.get("vol"),
                        turnover_per_decision=b.get("turnover_per_decision"))
        pf = (sp.get("span_portfolios") or {}).get("equal_weight_basket") or {}
        if _num(pf.get("cagr")):
            basket.update(available=True, cagr=float(pf["cagr"]), sharpe=pf.get("sharpe"),
                          maxdd=pf.get("maxdd"), vol=pf.get("vol"),
                          codes=pf.get("codes"), turnover_total=pf.get("turnover_total"))

    ceiling = {"source": CAPACITY, "available": False}
    if cap:
        ceil_block = cap.get("participation_ceiling_1pct_adv") or {}
        frontier = ((cap.get("capacity_frontier_by_cap") or {}).get("rule") or [])
        cell = None
        for c in frontier:
            if _num(c.get("cap_p90_of_adv")) and abs(float(c["cap_p90_of_adv"]) - BOOK_PARTICIPATION) < 1e-9:
                cell = c
                break
        if cell is None and frontier:
            cell = frontier[0]
        if cell is not None and _num(cell.get("deployable_nav_cny")):
            ceiling.update(
                available=True,
                participation=float(cell.get("cap_p90_of_adv")),
                deployable_nav_cny=float(cell["deployable_nav_cny"]),
                cagr_at_ceiling=cell.get("cagr"),
                annual_profit_ceiling_cny=cell.get("annual_profit_cny"),
                worst_participation=cell.get("participation_worst"),
                rule_label=(cap.get("rule_at_8bp_no_size") or {}).get("label"),
                gross_cash_pct=(cap.get("cash_leg") or {}).get("rf_mean_ann_pct"),
            )
            lad = ((cap.get("ladder") or {}).get("rule") or [])
            ceiling["ladder"] = sorted(
                (float(c["nav"]), float(c["cagr"])) for c in lad
                if _num(c.get("nav")) and _num(c.get("cagr")))
            ns = (cap.get("rule_at_8bp_no_size") or {}).get("cagr")
            ceiling["nosize_cagr"] = float(ns) if _num(ns) else None

    # The level the book is actually traded at. Published separately (r1320) because the
    # card headline and the capacity ladder are priced on two different universes, and
    # neither of them is the rule the order sheet executes.
    recon = {"source": RECONCILE, "available": False}
    rc = _load(RECONCILE)
    if rc:
        br = rc.get("bridge") or {}
        to, frm = br.get("to") or {}, br.get("from") or {}
        if _num(to.get("cagr_pp")):
            se = (((rc.get("stack_effect") or {}).get("cells") or {})
                  .get("n5|beta020|8bp") or {})
            tc = (((rc.get("stacks") or {}).get("production") or {}).get("cells") or {})
            tcell = tc.get("(5, 'beta020', 8.0)") or {}
            inter = br.get("interaction") or {}
            recon.update(available=True,
                         ticket_cagr=float(to["cagr_pp"]) / 100.0,
                         ticket_cfg=to.get("cfg"),
                         card_cagr=float(frm["cagr_pp"]) / 100.0 if _num(frm.get("cagr_pp")) else None,
                         knob_delta_pp=br.get("total_pp"),
                         interaction_pp=inter.get("interaction_pp"),
                         stack_delta_pp=se.get("delta_pp"),
                         ticket_vol=tcell.get("vol"),
                         ticket_maxdd=tcell.get("maxdd"),
                         ticket_sharpe=tcell.get("sharpe"),
                         evidence_cutoff=rc.get("evidence_cutoff"))
    ceiling["recon"] = recon

    sleeve = {"source": FUTURES, "available": False}
    if fut and fut.get("capital_sweep"):
        sleeve.update(
            available=True,
            capital_floor_cny=(fut.get("capital_floor") or {}).get("cny"),
            cells={float(c["capital"]): float(c["lot_cagr"]) for c in fut["capital_sweep"]
                   if _num(c.get("capital")) and _num(c.get("lot_cagr"))},
            continuous_cagr=((fut.get("model") or {}).get("continuous_cagr")
                             if isinstance(fut.get("model"), dict) else None),
        )
        sleeve["continuous_cagr"] = _num(sleeve.get("continuous_cagr")) and sleeve["continuous_cagr"] or 0.0137

    return book, basket, ceiling, sleeve


def _nearest_cell(cells, capital):
    """Return the closest measured capital key (not its CAGR)."""
    if not cells:
        return None
    return min(cells, key=lambda k: abs(k - capital))


def _ladder_cagr(ladder, nosize, capital):
    """CAGR at a given NAV from the capacity ladder, log-interpolated between rungs.

    Below the first rung the size-free number IS the answer (the first rung already
    carries that rung's own impact); above the last rung the last rung is returned, and
    the deployable amount is capped separately, so extrapolation never happens here.
    """
    if not ladder:
        return float(nosize) if _num(nosize) else None
    pts = sorted(ladder)
    if float(capital) <= pts[0][0]:
        return float(nosize) if _num(nosize) else pts[0][1]
    if float(capital) >= pts[-1][0]:
        return pts[-1][1]
    for (nav0, c0), (nav1, c1) in zip(pts, pts[1:]):
        if nav0 <= float(capital) <= nav1:
            t = (math.log(float(capital)) - math.log(nav0)) / (math.log(nav1) - math.log(nav0))
            return c0 + t * (c1 - c0)
    return pts[-1][1]


def place(capital, book, basket, ceiling, sleeve, cash_net=CASH_NET_ANNUAL):
    """One row per vehicle for a given account size. Pure function."""
    row = {"capital_cny": float(capital), "vehicles": {}}

    if book.get("available") and ceiling.get("available"):
        deployable = min(float(capital), ceiling["deployable_nav_cny"])
        idle = float(capital) - deployable
        recon = ceiling.get("recon") or {}
        ladder = ceiling.get("ladder") or []
        nosize = ceiling.get("nosize_cagr")
        ticket = recon.get("ticket_cagr")
        if _num(ticket):
            level, level_src = float(ticket), "reconcile ticket (%s)" % recon.get("ticket_cfg")
        elif _num(nosize):
            level, level_src = float(nosize), "capacity face, no-size arm"
        else:
            level, level_src = float(book["cagr"]), "spanning card headline"
        # impact is a statement about the money actually at work, so it is priced at the
        # DEPLOYED size, not at the account size: an account far above the ceiling does not
        # pay the ladder's 50M impact, it pays the ceiling's.
        at_size = _ladder_cagr(ladder, nosize, deployable)
        impact = max(0.0, float(nosize) - float(at_size)) if _num(nosize) and _num(at_size) else 0.0
        cagr = level - impact
        profit = deployable * cagr + idle * cash_net
        row["vehicles"]["etf_book"] = {
            "status": "ok",
            "deployed_cny": round(deployable, 2),
            "idle_in_repo_cny": round(idle, 2),
            "cagr_on_deployed": cagr,
            "cagr_level_used": level,
            "level_source": level_src,
            "cagr_card_uncapped": float(book["cagr"]),
            "cagr_capacity_ladder_nosize": nosize,
            "impact_pp_per_year": round(100.0 * impact, 4),
            "impact_priced_at_cny": round(deployable, 2),
            "annual_profit_cny": round(profit, 2),
            "annual_profit_rule_uncapped_cny": round(float(capital) * float(book["cagr"]), 2),
            "cash_net_annual_on_idle": cash_net,
            "capacity_bound": bool(idle > 1.0),
            "source": CAPACITY,
            "note": "level = the executable ticket on the production stack (reconcile face); the size "
                    "effect is the capacity ladder's impact DELTA (a cost difference) -- the ladder's "
                    "absolute levels are priced on a different universe and are not used here. ceiling = "
                    "%.2f%% of ADV (p90); excess priced at repo net." % (100 * BOOK_PARTICIPATION),
        }
    else:
        row["vehicles"]["etf_book"] = {"status": "unavailable", "source": CAPACITY}

    if basket.get("available"):
        row["vehicles"]["four_etf_basket"] = {
            "status": "ok",
            "deployed_cny": float(capital),
            "cagr": float(basket["cagr"]),
            "annual_profit_cny": round(float(capital) * float(basket["cagr"]), 2),
            "source": SPANNING,
            "note": "bought once and held (turnover 1.0 over the window); capacity is an entry-print question, not a daily one, and is not modelled here",
        }
    else:
        row["vehicles"]["four_etf_basket"] = {"status": "unavailable", "source": SPANNING}

    if sleeve.get("available"):
        floor = sleeve.get("capital_floor_cny")
        if not _num(floor):
            row["vehicles"]["futures_sleeve"] = {"status": "unavailable", "source": FUTURES}
        elif float(capital) < float(floor):
            row["vehicles"]["futures_sleeve"] = {
                "status": "below_floor",
                "capital_floor_cny": float(floor),
                "annual_profit_cny": round(float(capital) * cash_net, 2),
                "source": FUTURES,
                "note": "below the one-lot floor the sleeve can only hold repo; profit shown is the cash leg",
            }
        else:
            cell_cap = _nearest_cell(sleeve["cells"], float(capital))
            cagr = sleeve["cells"][cell_cap]
            row["vehicles"]["futures_sleeve"] = {
                "status": "ok",
                "deployed_cny": float(capital),
                "cagr": cagr,
                "lot_cagr_cell_capital_cny": cell_cap,
                "annual_profit_cny": round(float(capital) * cagr, 2),
                "source": FUTURES,
                "note": "lot-sized arm at the nearest measured capital cell; the continuous-weight 1.37%/yr is not reachable at these sizes",
                "disclosure_cell_distance_cny": round(abs(cell_cap - float(capital)), 2),
            }
    else:
        row["vehicles"]["futures_sleeve"] = {"status": "unavailable", "source": FUTURES}

    ranked = [(k, v.get("annual_profit_cny")) for k, v in row["vehicles"].items()
              if v.get("status") in ("ok", "below_floor") and _num(v.get("annual_profit_cny"))]
    if ranked:
        ranked.sort(key=lambda kv: -kv[1])
        row["best_vehicle"] = ranked[0][0]
        row["best_annual_profit_cny"] = round(ranked[0][1], 2)
        ok_only = [(k, v) for k, v in ranked if row["vehicles"][k]["status"] == "ok"]
        if len(ok_only) >= 2:
            row["spread_best_vs_second_cny"] = round(ok_only[0][1] - ok_only[1][1], 2)
            row["spread_best_vs_second_pct_of_capital"] = (
                round(100.0 * (ok_only[0][1] - ok_only[1][1]) / float(capital), 3)
                if float(capital) > 0 else 0.0)

    # Same-experiment split (r1262), now with every term measured (r1320). The four terms
    # are defined so they ADD UP exactly to the basket-vs-book gap:
    #   basket_vs_card   = basket CAGR     - card headline      (the book loses this one)
    #   card_vs_ticket   = card headline   - ticket level       (knobs: width/rule/cost)
    #   ticket_vs_size   = ticket level    - ticket at size     (impact only)
    #   size_vs_effective= ticket at size  - effective on ALL   (undeployable part at repo)
    # r1319 charged the middle of these to "run diff, unattributed"; it is the knob bridge
    # plus the panel/engine difference, both measured in results/etf_book_cagr_reconcile.json.
    bk, ba = row["vehicles"].get("etf_book", {}), row["vehicles"].get("four_etf_basket", {})
    if bk.get("status") == "ok" and ba.get("status") == "ok" and float(capital) > 0:
        effective = bk["annual_profit_cny"] / float(capital)
        card = float(book["cagr"])
        level = float(bk["cagr_level_used"])
        on_size = float(bk["cagr_on_deployed"])
        rec = ceiling.get("recon") or {}
        row["book_vs_basket"] = {
            "basket_vs_card_pp_per_year": round(100.0 * (ba["cagr"] - card), 3),
            "card_vs_ticket_pp_per_year": round(100.0 * (card - level), 3),
            "ticket_vs_size_pp_per_year": round(100.0 * (level - on_size), 3),
            "size_vs_effective_pp_per_year": round(100.0 * (on_size - effective), 3),
            "effective_cagr_on_all_capital": round(effective, 6),
            "total_gap_cny": round(ba["annual_profit_cny"] - bk["annual_profit_cny"], 2),
            "ticket_cfg": rec.get("ticket_cfg"),
            "ticket_vol": rec.get("ticket_vol"),
            "ticket_maxdd": rec.get("ticket_maxdd"),
            "ticket_sharpe": rec.get("ticket_sharpe"),
            "panel_stack_delta_pp": rec.get("stack_delta_pp"),
            "knob_interaction_pp": rec.get("interaction_pp"),
            "note": "basket_vs_card: the basket beats the card's own config, size-free. "
                    "card_vs_ticket: the published card is NOT the rule the order sheet trades; "
                    "this is that distance (knobs + their interaction). ticket_vs_size: impact "
                    "from the capacity ladder's own delta. panel_stack_delta_pp is the part of "
                    "the two published faces' disagreement that belongs to the universe, not to "
                    "a rule, and it is NOT charged to capacity.",
        }
    return row


def build():
    book, basket, ceiling, sleeve = gather()
    rows = [place(c, book, basket, ceiling, sleeve) for c in TIERS]

    caveats = [
        "Every number is read from a published face, not re-measured: book card headline %.2f%%/yr (%s), "
        "book level as traded %.2f%%/yr (the executable ticket, %s), basket %.2f%%/yr (%s), sleeve lot arm (%s)."
        % (100 * book.get("cagr", 0), SPANNING,
           100 * ((ceiling.get("recon") or {}).get("ticket_cagr") or book.get("cagr", 0)), RECONCILE,
           100 * basket.get("cagr", 0), SPANNING, FUTURES)
        if book.get("available") and basket.get("available") else "one or more source faces unavailable -- see per-vehicle status",
        "Risk is not free: the ticket carries ~13.5% vol and a ~-16% max drawdown against the card's "
        "10.2% / -11.8% -- it earns more because it takes more, Sharpe 1.04 vs 0.99.",
        "The card headline and the executable ticket are DIFFERENT books: the card prints a 12-name "
        "8%-vol-target run, the order sheet trades 5 names with a 0.20 beta cover at 8bp. The distance "
        "between them (+3.7pp/yr on the same stack) is decomposed knob by knob in "
        "research/ETF_BOOK_CAGR_RECONCILE.md, including the -1.25pp width x rule interaction.",
        "The capacity face's absolute levels (7.2-7.4%/yr) are priced on a different universe "
        "(un-repaired panel, no class filter) and run ~5.5pp/yr below the production stack at identical "
        "settings; only its impact DELTA is used here, never its levels.",
        "Impact is priced at the DEPLOYED size, so an account above the ceiling pays the ceiling's impact, "
        "not the ladder's 50M rung; below the first rung (1M) impact is zero and the size-free ticket is used.",
        "The book's ceiling is a p90-of-ADV statement: half of its decisions trade less than that, so the ceiling is a tail constraint, not an average.",
        "The basket has no modelled capacity ceiling. It is bought once and held, so liquidity binds only on the entry print; that print is not measured here.",
        "The futures sleeve pays nothing usable below its one-lot floor and stays under 2%/yr until roughly the 10M tier -- the continuous-weight series is not a tradable claim.",
        "Cash remainder is priced at the NET repo rate %.3f%%/yr (gross quote minus roll commission), not at zero and not at the gross quote." % (100 * CASH_NET_ANNUAL),
        "All three vehicles were measured on 2020-2026 panels; the book's own pre-2020 test says the rotation premium there is a fraction of the boom-window figure.",
        "The basket is not a neutral benchmark either: over this window it is carried by Nasdaq-100 QDII (20.7%/yr) and gold (13.3%/yr) with CSI300 at 0.2%. Its 10.09% is a window statement about a mix chosen in that window -- the point of the column is that the BOOK does not beat it, not that the basket keeps paying.",
    ]

    payload = {
        "schema": "capital_placement/v1",
        "ts": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": (json.loads((ROOT / SPANNING).read_text(encoding="utf-8")).get("evidence_cutoff")
                            if (ROOT / SPANNING).exists() else None),
        "config": {"book_participation_cap": BOOK_PARTICIPATION,
                   "cash_net_annual": CASH_NET_ANNUAL,
                   "tiers_cny": TIERS},
        "inputs": {"book": book, "basket": basket, "ceiling": ceiling, "futures_sleeve": sleeve},
        "rows": rows,
        "caveats": caveats,
    }
    return payload


def _fmt_cny(x):
    """ASCII-only currency text: the doc is read on GBK consoles and in git diffs."""
    if not _num(x):
        return "-"
    return "CNY {:,.0f}".format(x)


def render_md(payload):
    lines = ["# What each vehicle pays at a given account size", ""]
    lines.append("`scripts/capital_placement.py` -> `results/capital_placement.json` "
                 "(read-only consumer of three published faces; it measures nothing itself)")
    lines.append("")
    lines.append("The book, the four-ETF basket and the futures sleeve were each measured in their own "
                 "window and cost model. This face puts them on the only axis an allocator holds: how much "
                 "money you are trying to place. Profit is CNY **per year**, capacity ceiling applied where "
                 "one exists, and the undeployable remainder priced at the net repo rate "
                 "({:.3f}%/yr).".format(100 * payload["config"]["cash_net_annual"]))
    lines.append("")
    lines.append("| capital | ETF book (card config, size-free) | ETF book (ticket, size applied) | 4-ETF basket | futures sleeve | best | basket vs card | card vs ticket | ticket vs size | size vs effective |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in payload["rows"]:
        cells = []
        for key in ("etf_book", "four_etf_basket", "futures_sleeve"):
            v = r["vehicles"][key]
            if v["status"] == "ok":
                extra = ""
                if key == "etf_book" and v.get("capacity_bound"):
                    extra = " (capped at %s)" % _fmt_cny(v["deployed_cny"])
                cells.append("%s%s" % (_fmt_cny(v["annual_profit_cny"]), extra))
            elif v["status"] == "below_floor":
                cells.append("floor not met (repo only %s)" % _fmt_cny(v["annual_profit_cny"]))
            else:
                cells.append("unavailable")
        bk = r["vehicles"]["etf_book"]
        rule_side = ("%s" % _fmt_cny(bk.get("annual_profit_rule_uncapped_cny"))
                     if _num(bk.get("annual_profit_rule_uncapped_cny")) else "-")
        split = r.get("book_vs_basket") or {}
        def _pp(key):
            return ("%+.2fpp/yr" % split[key]) if _num(split.get(key)) else "-"
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            _fmt_cny(r["capital_cny"]), rule_side, cells[0], cells[1], cells[2],
            r.get("best_vehicle", "-"),
            _pp("basket_vs_card_pp_per_year"), _pp("card_vs_ticket_pp_per_year"),
            _pp("ticket_vs_size_pp_per_year"), _pp("size_vs_effective_pp_per_year")))
    lines.append("")
    lines.append("Four columns, four different statements, and they add up exactly to the gap in the "
                 "table above (a selftest leg enforces the sum). **basket vs card**: the basket beats the "
                 "card's own configuration, size-free -- the book loses that one on its own terms. "
                 "**card vs ticket**: the card headline is not the rule the order sheet executes; this is "
                 "that distance, measured knob by knob in `research/ETF_BOOK_CAGR_RECONCILE.md`. "
                 "**ticket vs size**: impact only, taken from the capacity ladder's own delta rather than "
                 "from its absolute levels (which are priced on a different universe). "
                 "**size vs effective**: the part of the account that cannot be deployed and earns repo.")
    lines.append("")
    lines.append("## How to read it")
    lines.append("")
    for c in payload["caveats"]:
        lines.append("* " + c)
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- selftest

def _eq(name, got, want, tol=1e-6):
    ok = False
    if _num(got) and _num(want):
        ok = abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))
    else:
        ok = got == want
    return (name, ok, "got=%r want=%r" % (got, want))


def selftest():
    book, basket, ceiling, sleeve = gather()
    legs = []

    legs.append(_eq("inputs: all four source faces readable", 
                    all([book.get("available"), basket.get("available"),
                         ceiling.get("available"), sleeve.get("available")]), True))

    # L2 no phantom at zero capital: no vehicle invents profit out of nothing
    zero = place(0, book, basket, ceiling, sleeve)
    legs.append(_eq("zero capital -> every vehicle prints 0 profit",
                    all((v.get("annual_profit_cny") or 0) == 0 for v in zero["vehicles"].values()), True))

    # L3 basket is linear in capital (it is a fraction, not a fee schedule)
    a, b = place(1_000_000, book, basket, ceiling, sleeve), place(2_000_000, book, basket, ceiling, sleeve)
    pa = a["vehicles"]["four_etf_basket"]["annual_profit_cny"]
    pb = b["vehicles"]["four_etf_basket"]["annual_profit_cny"]
    legs.append(_eq("basket profit is linear in capital (2x -> 2x)", pb, 2 * pa, 1e-9))

    # L4 units: the basket CAGR is a fraction. 1M at ~10.09% is ~100,900, never 10,090,000.
    legs.append(("unit leg: basket CAGR is a fraction not a percent (100x guard)",
                 _num(pa) and 50_000 < pa < 200_000, "profit@1M=%r" % pa))

    # L5 the book ceiling actually binds: above it, extra capital only earns repo
    hi = place(50_000_000, book, basket, ceiling, sleeve)["vehicles"]["etf_book"]
    lo = place(8_000_000, book, basket, ceiling, sleeve)["vehicles"]["etf_book"]
    legs.append(("book capacity binds above the ceiling (extra capital earns repo only)",
                 hi["capacity_bound"] and lo["capacity_bound"] and
                 (hi["annual_profit_cny"] - lo["annual_profit_cny"]) <=
                 (50_000_000 - 8_000_000) * CASH_NET_ANNUAL + 1e-6, True))
    legs.append(_eq("book deployable never exceeds its ceiling",
                    hi["deployed_cny"], ceiling["deployable_nav_cny"], 1e-9))

    # L6 monotone: more capital never pays less, for any vehicle that is ok
    rows = [place(c, book, basket, ceiling, sleeve) for c in TIERS]
    mono = True
    for key in ("etf_book", "four_etf_basket", "futures_sleeve"):
        prev = None
        for r in rows:
            v = r["vehicles"][key]
            if v.get("status") not in ("ok", "below_floor"):
                continue
            val = v.get("annual_profit_cny")
            if prev is not None and val + 1e-6 < prev:
                mono = False
            prev = val
    legs.append(("every vehicle's profit is non-decreasing in capital", mono, "see tiers"))

    # L7 futures below floor is flagged, not silently a tiny positive sleeve
    below = place(1_000_000, book, basket, ceiling, sleeve)["vehicles"]["futures_sleeve"]
    legs.append(("futures below the one-lot floor is reported as below_floor",
                 below["status"] == "below_floor" and _num(below.get("capital_floor_cny")), below["status"]))

    # L8 a missing face must be unavailable, never zero
    blank = {"source": "x", "available": False}
    row = place(1_000_000, blank, blank, blank, blank)
    legs.append(("missing sources -> unavailable, never a silent 0",
                 all(v["status"] == "unavailable" for v in row["vehicles"].values()), True))

    # L9 ranking is consistent with the printed numbers
    consistent = True
    for r in rows:
        vals = {k: v["annual_profit_cny"] for k, v in r["vehicles"].items()
                if v.get("status") == "ok" and _num(v.get("annual_profit_cny"))}
        if vals:
            if r["best_vehicle"] not in vals or abs(vals[r["best_vehicle"]] - max(vals.values())) > 1e-6:
                consistent = False
    legs.append(("best_vehicle per row is the maximum of the ok vehicles", consistent, "see rows"))

    # L10 provenance: every ok cell names a source file that exists
    prov = True
    for r in rows:
        for v in r["vehicles"].values():
            if v.get("status") == "ok" and not (ROOT / v["source"]).exists():
                prov = False
    legs.append(("every ok cell carries an existing source file", prov, "see sources"))

    # L11 payload is deterministic apart from ts
    one, two = build(), build()
    one.pop("ts", None); two.pop("ts", None)
    legs.append(("payload deterministic apart from the ts envelope", one == two, "dict compare"))

    # L12 basket-vs-card and card-vs-ticket are size-free constants; only the impact and
    # the repo drag move with capital
    g1 = [r["book_vs_basket"]["basket_vs_card_pp_per_year"] for r in rows if r.get("book_vs_basket")]
    g2 = [r["book_vs_basket"]["card_vs_ticket_pp_per_year"] for r in rows if r.get("book_vs_basket")]
    legs.append(("basket-vs-card and card-vs-ticket are constant across account sizes",
                 len(g1) == len(rows) and max(g1) - min(g1) <= 1e-6
                 and max(g2) - min(g2) <= 1e-6, "g1=%r g2=%r" % (g1[:2], g2[:2])))

    # L13 the four terms add up to the total gap (no unexplained residual term)
    decomp = True
    for r in rows:
        d = r.get("book_vs_basket")
        if not d:
            continue
        cny = sum(r["capital_cny"] * d[k] / 100.0 for k in
                  ("basket_vs_card_pp_per_year", "card_vs_ticket_pp_per_year",
                   "ticket_vs_size_pp_per_year", "size_vs_effective_pp_per_year"))
        if abs(cny - d["total_gap_cny"]) > 2.0 + 1e-5 * r["capital_cny"]:
            decomp = False
    legs.append(("basket-vs-card + card-vs-ticket + ticket-vs-size + size-vs-effective "
                 "== total gap in CNY", decomp, "per row"))

    # L14 capacity cost is 0 under the ceiling and >0 well above it, and the run diff
    # (which is NOT a capacity statement) does not move with capital
    under = place(300_000, book, basket, ceiling, sleeve)["book_vs_basket"]
    over = place(50_000_000, book, basket, ceiling, sleeve)["book_vs_basket"]
    legs.append(("impact is 0 under the first ladder rung and binds at the ceiling",
                 abs(under["ticket_vs_size_pp_per_year"]) <= 1e-9
                 and over["ticket_vs_size_pp_per_year"] > 0.2,
                 "under=%r over=%r" % (under["ticket_vs_size_pp_per_year"],
                                       over["ticket_vs_size_pp_per_year"])))
    legs.append(("impact is priced at the deployed size, so an over-ceiling account does "
                 "not pay the ladder's own 50M rung",
                 over["ticket_vs_size_pp_per_year"] < 2.0,
                 "over=%r" % over["ticket_vs_size_pp_per_year"]))

    # the level actually used must be the reconcile ticket, and it must be disclosed
    bk_lvl = place(1_000_000, book, basket, ceiling, sleeve)["vehicles"]["etf_book"]
    rec = (ceiling.get("recon") or {})
    legs.append(("the book level comes from the reconcile ticket, not from the capacity "
                 "ladder's absolute cell or the card alone",
                 bool(rec.get("available")) and _num(bk_lvl.get("cagr_level_used"))
                 and abs(bk_lvl["cagr_level_used"] - rec["ticket_cagr"]) <= 1e-12,
                 "level=%r src=%r" % (bk_lvl.get("cagr_level_used"), bk_lvl.get("level_source"))))

    # L18 reader text is final text: no doubled percent and no unexpanded placeholder.
    # The caveat list mixes %-formatted items with plain literals, and a literal that was
    # written as if it were formatted kept its "%%" -- the published face then said
    # "13.5%% vol" to every reader. Only a gate on the OUTPUT catches that, because the
    # code looks correct at the line where the string is defined.
    def _strings(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str):
                    yield k
                yield from _strings(v)
        elif isinstance(o, list):
            for v in o:
                yield from _strings(v)

    bad = [s for s in _strings(one)
           if "%%" in s or re.search(r"%[-+ 0-9.]*[sdfr]", s)]
    legs.append(("reader-facing text carries no doubled percent or unexpanded placeholder",
                 not bad, "offenders=%r" % (bad[:3],)))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + (" | " + detail if not ok else ""))
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    if "--selftest" in argv or "selftest" in argv:
        return selftest()
    payload = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    for r in payload["rows"]:
        print("cap=%-12s best=%-16s spread=%s" % (
            "{:,.0f}".format(r["capital_cny"]), r.get("best_vehicle"),
            _fmt_cny(r.get("spread_best_vs_second_cny"))))
    print("wrote %s + %s" % (OUT_JSON.relative_to(ROOT), OUT_MD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))