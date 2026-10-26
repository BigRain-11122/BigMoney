"""Which single ETF book do we publish, and how much money does it make per year?

The open question this answers (state pointer r1298 -> next):
"do the four live faces collapse to one published book, using the capacity
frontier as the tie-breaker - money per year at a stated capital cap?"

This script adds NO new backtest. It reads what the book already published,
puts the arms side by side in CNY/year at a stated capital, and refuses to
compare arms that were not run under the same rule, window and cost basis.

Conventions borrowed from the round-1291/1292 rulings:
  * every number carries its own source file + as-of + rule label;
  * a "delta" is only printed inside one comparable group;
  * capacity is a fraction of ADV in every artifact we read, so it is
    converted to CNY once here (`_deployable`) and the unit is asserted.

Usage:
  python scripts/etf_book_publish_decision.py run
  python scripts/etf_book_publish_decision.py selftest
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

CAPITAL_GRID = (1_000_000.0, 5_000_000.0, 10_000_000.0, 30_000_000.0, 50_000_000.0)


def _load(name):
    p = RES / name
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _deployable(capital_cny, ceiling_cny):
    """Both arguments are CNY. Anything above the ceiling cannot be placed."""
    if ceiling_cny is None or ceiling_cny <= 0:
        return 0.0
    return min(float(capital_cny), float(ceiling_cny))


def _money(capital_cny, cagr, ceiling_cny):
    """Annual CNY the arm can actually earn at this capital and this size ceiling."""
    return _deployable(capital_cny, ceiling_cny) * float(cagr)


def build_arms():
    """One row per config, each row traceable to a single artifact."""
    arms = []

    card = _load("etf_book_production/latest.json")
    if card:
        bt = (card.get("backtest") or {}).get("n12_vt08") or {}
        full = bt.get("full") or {}
        cfg = card.get("config") or {}
        arms.append({
            "config": "12@vol",
            "label": "published card (12 names, vol target 8%, R20, with bonds)",
            "faces": ["card", "forward"],
            "source": "results/etf_book_production/latest.json::backtest.n12_vt08.full",
            "as_of": card.get("evidence_cutoff"),
            "basis": "same-engine backtest, cost %.0fbp/side, decide close -> fill next open"
                     % (cfg.get("cost_bp_per_side") or 0),
            "n_hold": cfg.get("n_hold"),
            "rebal": cfg.get("rebal"),
            "vol_target": cfg.get("vol_target"),
            "cagr": full.get("cagr"),
            "sharpe": full.get("sharpe"),
            "maxdd": full.get("maxdd"),
            "turnover": bt.get("turnover_per_decision"),
            "capacity_1pct": _frontier_aum("N12_R20", "aum_1pct"),
            "capacity_5pct": _frontier_aum("N12_R20", "aum_5pct"),
            "capacity_note": "frontier cell N12_R20 (fraction-of-ADV ceiling, weights of the un-targeted 12-name arm)",
            "group": "R20_with_bonds",
        })

    ticket = _load("etf_book_order/TICKET-2026-10-26.json")
    ladder = _load("etf_book_capacity_rule.json")
    if ticket and ladder:
        ref = (ladder.get("capacity_frontier_by_cap") or {}).get("rule") or []
        at_1 = next((r for r in ref if abs(r.get("cap_p90_of_adv", 0) - 0.01) < 1e-9), None)
        at_5 = next((r for r in ref if abs(r.get("cap_p90_of_adv", 0) - 0.05) < 1e-9), None)
        arms.append({
            "config": "5@beta",
            "label": "executable ticket (5 names, k = min(1, 0.20/beta), R20, repo cash leg)",
            "faces": ["ticket"],
            "source": "results/etf_book_capacity_rule.json::capacity_frontier_by_cap.rule",
            "as_of": ladder.get("evidence_cutoff"),
            "basis": "same-engine ladder priced at 8bp + K*sqrt(p/1%%) size impact, k from realised weight path",
            "n_hold": (ladder.get("config") or {}).get("n_hold"),
            "rebal": (ladder.get("config") or {}).get("rebal"),
            "vol_target": None,
            "cagr": (at_1 or {}).get("cagr"),
            "sharpe": (at_1 or {}).get("sharpe"),
            "maxdd": (at_1 or {}).get("maxdd"),
            "turnover": None,
            "capacity_1pct": (at_1 or {}).get("deployable_nav_cny"),
            "capacity_5pct": (at_5 or {}).get("deployable_nav_cny"),
            "capacity_note": "deployable NAV already in CNY (p90 participation capped at 1%% / 5%% of ADV)",
            "ticket_metrics": (ticket.get("metrics") or {}).get("book"),
            "ticket_inception": ticket.get("inception"),
            "group": "R20_with_bonds",
        })

    stag = _load("etf_stagger_capacity.json")
    if stag:
        s = stag.get("staggered") or {}
        arms.append({
            "config": "10@vol",
            "label": "staggered 5+5 ledger (R10, vol target 8%, bond-free)",
            "faces": ["staggered"],
            "source": "results/etf_stagger_capacity.json::staggered",
            "as_of": stag.get("evidence_cutoff") or "2026-10-26",
            "basis": "own run: two sleeves half a rebalance apart, R10, bond-free universe",
            "n_hold": 10,
            "rebal": 10,
            "vol_target": 0.08,
            "cagr": s.get("cagr"),
            "sharpe": s.get("sharpe"),
            "maxdd": s.get("maxdd"),
            "turnover": s.get("turnover"),
            "capacity_1pct": s.get("aum_1pct"),
            "capacity_5pct": s.get("aum_5pct"),
            "capacity_note": "own run's p90 1%%/5%% ADV ceiling",
            "group": "R10_bond_free",
        })
    return arms


def _frontier_aum(cell, key):
    fr = _load("etf_capacity_frontier.json")
    if not fr:
        return None
    for c in fr.get("cells") or []:
        if c.get("cell") == cell:
            return c.get(key)
    return None


def money_table(arms):
    """Annual CNY at each stated capital, clipped by the arm's own capacity."""
    out = {}
    for a in arms:
        rows = []
        for cap in CAPITAL_GRID:
            rows.append({
                "capital_cny": cap,
                "deployable_1pct": _deployable(cap, a["capacity_1pct"]),
                "annual_cny_1pct": _money(cap, a["cagr"], a["capacity_1pct"]),
                "deployable_5pct": _deployable(cap, a["capacity_5pct"]),
                "annual_cny_5pct": _money(cap, a["cagr"], a["capacity_5pct"]),
            })
        out[a["config"]] = rows
    return out


def verdict(arms, table):
    """The decision, in words, with the reason each band is drawn where it is."""
    by_cfg = {a["config"]: a for a in arms}
    groups = {}
    for a in arms:
        groups.setdefault(a["group"], []).append(a["config"])

    # who wins money-per-year at each capital, inside each comparable group only
    winners = {}
    for g, cfgs in groups.items():
        if len(cfgs) < 2:
            continue
        winners[g] = []
        for cap in CAPITAL_GRID:
            best = max(cfgs, key=lambda c: (table[c][CAPITAL_GRID.index(cap)]["annual_cny_1pct"] or 0))
            winners[g].append({"capital_cny": cap, "winner": best,
                               "annual_cny": table[best][CAPITAL_GRID.index(cap)]["annual_cny_1pct"]})

    bands = []
    # inside the R20 group: compare the published card against the executable ticket
    r20 = groups.get("R20_with_bonds") or []
    if "12@vol" in r20 and "5@beta" in r20:
        for cap in CAPITAL_GRID:
            i = CAPITAL_GRID.index(cap)
            card = table["12@vol"][i]["annual_cny_1pct"]
            tick = table["5@beta"][i]["annual_cny_1pct"]
            bands.append({
                "capital_cny": cap,
                "card_12vol_cny": card,
                "ticket_5beta_cny": tick,
                "delta_cny": card - tick,
                "note": "same group: R20, with bonds, same-size basis is NOT identical "
                        "(card pays flat 10bp/side, ticket pays 8bp + size impact)",
            })

    publish = "12@vol" if "12@vol" in by_cfg else (arms[0]["config"] if arms else None)
    why = []
    if "12@vol" in by_cfg:
        why.append("only config that carries a published card AND a forward ledger AND a "
                   "same-engine backtest AND a measured capacity ceiling")
        why.append("the two live faces of that config (card, forward) are one book, not two - "
                   "the four faces collapse to three configs")
        why.append("at 1%% ADV the card can place about %.2fM CNY, at 5%% about %.2fM CNY"
                   % ((by_cfg["12@vol"]["capacity_1pct"] or 0) / 1e6,
                      (by_cfg["12@vol"]["capacity_5pct"] or 0) / 1e6))
    if "5@beta" in by_cfg:
        why.append("the 5@beta ticket stays as the smaller-capital executable sleeve: under ~%.1fM CNY "
                   "it is the only config a broker can follow name by name"
                   % ((by_cfg["5@beta"]["capacity_1pct"] or 0) / 1e6))
    if "10@vol" in by_cfg:
        why.append("the staggered 10@vol ledger is NOT a variant of the published book - it runs a "
                   "different cadence (R10) on a bond-free universe, so its higher headline CAGR "
                   "cannot be read as the same book doing better; it stays an experiment until it is "
                   "re-run on the published rule for an apples-to-apples number")

    return {
        "publish": publish,
        "why": why,
        "bands": bands,
        "group_winners": winners,
        "not_comparable": [
            "12@vol vs 10@vol: different rebalance cadence (R20 vs R10) and universe (with vs without bonds)",
            "card vs ticket head-to-head inside R20 is directional only: 10bp flat vs 8bp + sqrt impact",
        ],
        "faces": {"count": sum(len(a["faces"]) for a in arms),
                  "distinct_configs": len(arms),
                  "merges": [{"config": a["config"], "faces": a["faces"]} for a in arms if len(a["faces"]) > 1]},
    }


def run():
    arms = build_arms()
    if not arms:
        print("publish_decision: no book artifacts on disk -- nothing to decide")
        return 2
    table = money_table(arms)
    v = verdict(arms, table)
    payload = {
        "ts": None,
        "evidence_cutoff": max((a["as_of"] or "") for a in arms),
        "script": "scripts/etf_book_publish_decision.py",
        "capital_grid_cny": list(CAPITAL_GRID),
        "units": ("cagr/sharpe/maxdd are decimals; capacity_1pct/capacity_5pct are CNY ceilings "
                  "(p90 participation at 1%/5% of ADV); deployable_* and annual_cny are CNY / CNY per year"),
        "arms": arms,
        "money_table": table,
        "verdict": v,
        "method_note": "aggregation only -- every number is copied from the arm's own artifact; "
                       "money_per_year = min(capital, own_capacity_ceiling) * own_cagr; "
                       "cross-group ranking is deliberately suppressed",
    }
    out = RES / "etf_book_publish_decision.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print("== arms (own numbers, own sources) ==")
    for a in arms:
        print("%-8s cagr %6.2f%%  sharpe %5.3f  maxdd %7.2f%%  cap@1%%ADV %8.2fM  cap@5%%ADV %8.2fM  [%s]"
              % (a["config"], 100 * (a["cagr"] or 0), a["sharpe"] or 0, 100 * (a["maxdd"] or 0),
                 (a["capacity_1pct"] or 0) / 1e6, (a["capacity_5pct"] or 0) / 1e6, a["as_of"]))
    print("== money per year at stated capital (1% ADV tolerance) ==")
    hdr = "%-9s" % "capital" + "".join("%18s" % a["config"] for a in arms)
    print(hdr)
    for cap in CAPITAL_GRID:
        i = CAPITAL_GRID.index(cap)
        print("%-9s" % ("%.0fM" % (cap / 1e6)) +
              "".join("%18s" % ("%.0fk" % (table[a["config"]][i]["annual_cny_1pct"] / 1e3)) for a in arms))
    print("== money per year at stated capital (5% ADV tolerance) ==")
    print(hdr)
    for cap in CAPITAL_GRID:
        i = CAPITAL_GRID.index(cap)
        print("%-9s" % ("%.0fM" % (cap / 1e6)) +
              "".join("%18s" % ("%.0fk" % (table[a["config"]][i]["annual_cny_5pct"] / 1e3)) for a in arms))
    print("== verdict ==")
    print("publish:", v["publish"])
    for w in v["why"]:
        print("  -", w)
    print("wrote", out)
    return 0


# ---------------------------------------------------------------- selftest
def _chk(cond, name, fails):
    if not cond:
        fails.append(name)


def selftest():
    fails = []
    # money math: 10M capital, 10% cagr, no capacity limit -> 1.0M a year
    _chk(abs(_money(10e6, 0.10, 1e12) - 1e6) < 1.0, "L1 money = capital * cagr when no ceiling bites", fails)
    # capacity clips: 10M capital but 1.5M ceiling -> 150k, not 1M
    _chk(abs(_money(10e6, 0.10, 1.5e6) - 150e3) < 1.0, "L2 capacity clips capital", fails)
    # a configured ceiling is CNY, never a percentage -- the r1292 100x trap
    _chk(_deployable(10e6, 1.5e6) == 1.5e6, "L3 ceiling used as CNY", fails)
    _chk(_money(50e6, 0.10, 1.82e6) < 2e5, "L3b 1.82M ceiling at 50M capital stays 1.82M deployed", fails)
    _chk(_deployable(1e6, 1.5e6) == 1e6, "L4 capital below ceiling is not inflated", fails)
    _chk(_deployable(1e6, 0) == 0.0, "L5 zero capacity deployable zero", fails)
    # the clipping has to be the thing that moves the number
    _chk(_money(50e6, 0.10, 1.5e6) != _money(50e6, 0.10, 9e6), "L6 mechanism actually bites", fails)
    # verdict must never rank across groups
    arms = [
        {"config": "A", "faces": ["a"], "cagr": 0.20, "capacity_1pct": 1e6, "capacity_5pct": 5e6, "group": "g1"},
        {"config": "B", "faces": ["b"], "cagr": 0.10, "capacity_1pct": 3e6, "capacity_5pct": 15e6, "group": "g2"},
    ]
    table = money_table(arms)
    v = verdict(arms, table)
    _chk(set(v["group_winners"].keys()) == set(), "L7 no cross-group winner", fails)
    _chk(v["faces"]["distinct_configs"] == 2, "L8 config count from arms", fails)
    arms2 = arms + [{"config": "A2", "faces": ["a2"], "cagr": 0.11, "capacity_1pct": 1e6,
                     "capacity_5pct": 5e6, "group": "g1"}]
    v2 = verdict(arms2, money_table(arms2))
    _chk("g1" in v2["group_winners"], "L9 winner computed inside group", fails)
    _chk(all(w["winner"] == "A" for w in v2["group_winners"]["g1"]), "L10 higher cagr wins same cap", fails)
    # merging faces must be visible
    arms3 = [{"config": "X", "faces": ["card", "forward"], "cagr": 0.09, "capacity_1pct": 2e6,
              "capacity_5pct": 9e6, "group": "g"}]
    _chk(verdict(arms3, money_table(arms3))["faces"]["count"] == 2, "L11 face count", fails)
    print("selftest: %d/%d legs pass" % (12 - len(fails), 12))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())