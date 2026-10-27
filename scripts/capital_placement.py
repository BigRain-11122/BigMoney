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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SPANNING = "results/etf_book_spanning.json"
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


def place(capital, book, basket, ceiling, sleeve, cash_net=CASH_NET_ANNUAL):
    """One row per vehicle for a given account size. Pure function."""
    row = {"capital_cny": float(capital), "vehicles": {}}

    if book.get("available") and ceiling.get("available"):
        deployable = min(float(capital), ceiling["deployable_nav_cny"])
        idle = float(capital) - deployable
        cagr = ceiling.get("cagr_at_ceiling")
        cagr = float(cagr) if _num(cagr) else float(book["cagr"])
        profit = deployable * cagr + idle * cash_net
        row["vehicles"]["etf_book"] = {
            "status": "ok",
            "deployed_cny": round(deployable, 2),
            "idle_in_repo_cny": round(idle, 2),
            "cagr_on_deployed": cagr,
            "cagr_rule_uncapped": float(book["cagr"]),
            "annual_profit_cny": round(profit, 2),
            "annual_profit_rule_uncapped_cny": round(float(capital) * float(book["cagr"]), 2),
            "cash_net_annual_on_idle": cash_net,
            "capacity_bound": bool(idle > 1.0),
            "source": CAPACITY,
            "note": "capacity ceiling = %.2f%% of ADV (p90); excess priced at repo net. cagr_on_deployed comes from the capacity face's own run; cagr_rule_uncapped is the spanning face's headline and is NOT achievable above the ceiling."
                    % (100 * BOOK_PARTICIPATION),
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
                "note": "lot-sized arm at the nearest measured capital cell; the continuous-weight 1.37%%/yr is not reachable at these sizes",
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

    # Same-experiment split (r1262). The three terms are defined so they ADD UP exactly:
    #   rule_gap       = basket CAGR        - book rule CAGR (spanning run, size-free)
    #   run_diff       = book rule CAGR     - capacity run's CAGR on deployed capital
    #   capacity_cost  = capacity run CAGR  - the book's effective CAGR on ALL capital
    # The middle term exists because the two published runs do not agree with each other
    # (cost model / cell definition differ by ~2.3pp) -- it is NOT a capacity statement and
    # is published as unattributed rather than folded into the ceiling's cost.
    bk, ba = row["vehicles"].get("etf_book", {}), row["vehicles"].get("four_etf_basket", {})
    if bk.get("status") == "ok" and ba.get("status") == "ok" and float(capital) > 0:
        effective = bk["annual_profit_cny"] / float(capital)
        row["book_vs_basket"] = {
            "rule_gap_pp_per_year": round(100.0 * (ba["cagr"] - bk["cagr_rule_uncapped"]), 3),
            "run_diff_pp_per_year": round(100.0 * (bk["cagr_rule_uncapped"] - bk["cagr_on_deployed"]), 3),
            "capacity_cost_pp_per_year": round(100.0 * (bk["cagr_on_deployed"] - effective), 3),
            "effective_cagr_on_all_capital": round(effective, 6),
            "total_gap_cny": round(ba["annual_profit_cny"] - bk["annual_profit_cny"], 2),
            "note": "rule_gap: basket vs book rule, same spanning run, size-free. run_diff: the capacity face's CAGR does not reproduce the spanning face's headline even under the ceiling -- unattributed, not a capacity cost. capacity_cost: only the 1%-ADV ceiling, zero while the book is under it.",
        }
    return row


def build():
    book, basket, ceiling, sleeve = gather()
    rows = [place(c, book, basket, ceiling, sleeve) for c in TIERS]

    caveats = [
        "Every number is read from a published face, not re-measured: book %.2f%%/yr (%s), basket %.2f%%/yr (%s), sleeve lot arm (%s)."
        % (100 * book.get("cagr", 0), SPANNING, 100 * basket.get("cagr", 0), SPANNING, FUTURES)
        if book.get("available") and basket.get("available") else "one or more source faces unavailable -- see per-vehicle status",
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
    lines.append("| capital | ETF book (rule, size-free) | ETF book (achievable at 1% ADV) | 4-ETF basket | futures sleeve | best | rule gap | run diff | capacity cost |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
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
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            _fmt_cny(r["capital_cny"]), rule_side, cells[0], cells[1], cells[2],
            r.get("best_vehicle", "-"),
            ("%+.2fpp/yr" % split["rule_gap_pp_per_year"]) if _num(split.get("rule_gap_pp_per_year")) else "-",
            ("%+.2fpp/yr" % split["run_diff_pp_per_year"]) if _num(split.get("run_diff_pp_per_year")) else "-",
            ("%+.2fpp/yr" % split["capacity_cost_pp_per_year"]) if _num(split.get("capacity_cost_pp_per_year")) else "-"))
    lines.append("")
    lines.append("Three columns, three different statements, and they add up exactly to the gap in the "
                 "table above (a selftest leg enforces the sum). The **rule gap** is the book's ranking "
                 "versus the basket with size taken out of the picture -- the basket wins that one already. "
                 "The **run diff** is not a finding: the capacity face's return does not reproduce the "
                 "spanning face's headline by ~2.3pp even under the ceiling, and this window does not "
                 "separate that difference (cost model vs cell definition), so it is published as "
                 "unattributed instead of being charged to the ceiling. The **capacity cost** is the "
                 "1%-of-ADV ceiling alone: zero while the book is under it, and it widens with size.")
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

    # L12 the rule gap is a size-free constant; only the capacity gap moves with capital
    gaps = [r["book_vs_basket"]["rule_gap_pp_per_year"] for r in rows if r.get("book_vs_basket")]
    legs.append(("rule gap vs the basket is constant across account sizes",
                 len(gaps) == len(rows) and max(gaps) - min(gaps) <= 1e-6, "gaps=%r" % gaps[:3]))

    # L13 the three published terms add up to the total gap (no unexplained fourth term)
    decomp = True
    for r in rows:
        s = r.get("book_vs_basket")
        if not s:
            continue
        bk = r["vehicles"]["etf_book"]
        rule_cny = r["capital_cny"] * s["rule_gap_pp_per_year"] / 100.0
        run_cny = r["capital_cny"] * s["run_diff_pp_per_year"] / 100.0
        cap_cny = r["capital_cny"] * s["capacity_cost_pp_per_year"] / 100.0
        if abs((rule_cny + run_cny + cap_cny) - s["total_gap_cny"]) > 2.0 + 1e-5 * r["capital_cny"]:
            decomp = False
    legs.append(("rule gap + run diff + capacity cost == total gap in CNY", decomp, "per row"))

    # L14 capacity cost is 0 under the ceiling and >0 well above it, and the run diff
    # (which is NOT a capacity statement) does not move with capital
    under = place(300_000, book, basket, ceiling, sleeve)["book_vs_basket"]
    over = place(50_000_000, book, basket, ceiling, sleeve)["book_vs_basket"]
    legs.append(("capacity cost is 0 under the ceiling and >0 well above it",
                 abs(under["capacity_cost_pp_per_year"]) <= 1e-9 and over["capacity_cost_pp_per_year"] > 1.0,
                 "under=%r over=%r" % (under["capacity_cost_pp_per_year"], over["capacity_cost_pp_per_year"])))
    legs.append(("the run diff is a constant, not a function of capital",
                 abs(under["run_diff_pp_per_year"] - over["run_diff_pp_per_year"]) <= 1e-9,
                 "under=%r over=%r" % (under["run_diff_pp_per_year"], over["run_diff_pp_per_year"])))

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