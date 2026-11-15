"""IDX_FUT_LEVERAGE_WASHOUT — what happens to a margin account that holds the carry.

Why this face exists: results/idx_fut_desk_sheet.json already prints the ladder
(1,000,000 CNY posts margin and can hold N lots, so the *notional* carry becomes a
large percent of capital).  It prints the return.  It does not print what the same
position did on the way there: a long-futures carry book is levered index beta with a
small positive drift, and the account is force-liquidated when equity falls under the
maintenance requirement -- before the index has to go to zero.  "6 lots, 67% a year"
and "6 lots, wiped in 2018" are the same position read at two different moments, and
only the second one decides how much capital may be committed.

Who pays (unchanged from the parent face): the discount is paid by whoever needs the
short leg (alpha hedgers, snowball issuers, ETF-arb desks).  The receiver holds long to
expiry and eats the index's own risk.  This face measures that risk in money.

Frozen reading rules (written before the numbers were read):
  W1  the position is LONG futures (that is the side that receives the discount).
      A short-futures book earns when the discount widens, which is the opposite trade
      and must never be blended into these numbers.
  W2  roll days carry no price P&L for a holder: the parent face excludes the splice
      jump from its return series, so the same exclusion applies here.  A simulator
      that books the splice as a loss invents a drawdown that no holder experiences.
  W3  a wipeout is mechanical, not a mood: equity <= maintenance_rate * notional closes
      the book at that day's close.  Days after that are not simulated (a wiped account
      does not keep its lots) -- reporting a later recovery would be a fantasy.
  W4  lots are set by the margin box, matching the desk sheet's ladder, so the two faces
      are the same position.  If the two faces disagreed on size, neither could be read.

Subcommands:
  run      -- deterministic, local only; writes results/idx_fut_leverage_washout.json
  selftest -- hermetic synthetic checks of W1/W2/W3/W4
"""
import json
import math
import os
import statistics
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base  # noqa: E402  (panels, roll detector, drawdown: one source)

OUT = os.path.join(ROOT, "results", "idx_fut_leverage_washout.json")
CARRY_FACE = os.path.join(ROOT, "results", "idx_fut_carry_capital.json")
DESK_FACE = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")

# Contract multipliers (CNY per index point).  Printed with every number: a reader who
# disagrees changes one constant and re-runs, rather than arguing with a conclusion.
MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
TIERS = [1000000, 3000000, 5000000, 10000000]
MAINTENANCE_RATE = 0.12   # exchange maintenance margin (below initial 15%): the call line
MARGIN_RATE = 0.15        # initial margin, same constant the capital face declares
MARGIN_USE = 0.60         # share of capital allowed into margin, same as capital face


def load_futures(product):
    path = os.path.join(base.FUT_DIR, product + ".csv")
    if not os.path.exists(path):
        return None
    out = {}
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            out[str(r["date"])[:10]] = v
    return out or None


def effective_returns(fut_close, idx_close, dates):
    """Index return plus the non-roll spread (W2).

    A holder's daily P&L is the index move plus the carry the basis delivers; on a roll
    day the splice is excluded, so the day reads as plain index exposure.
    """
    basis, spread, roll = base.basis_face(fut_close, idx_close, dates)
    r_idx, r_eff = [], []
    for k in range(1, len(dates)):
        ri = idx_close[k] / idx_close[k - 1] - 1.0
        r_idx.append(ri)
        # spread/roll are indexed from the first *daily return*, i.e. k-1 for the step
        # dates[k-1] -> dates[k]
        r_eff.append(ri + (0.0 if roll[k - 1] else spread[k - 1]))
    return r_idx, r_eff, roll[1:]


def lots_by_margin(capital, notional_per_lot):
    if notional_per_lot <= 0:
        return 0
    return int(math.floor(capital * MARGIN_USE / (notional_per_lot * MARGIN_RATE)))


def simulate(capital, lots, mult, prices, r_eff, maintenance_rate=MAINTENANCE_RATE, dates=None):
    """Mark the margin account daily; stop at the first forced liquidation (W3).

    `prices` is the full path (len == len(r_eff) + 1); the P&L of step k is booked on the
    price it started from, while the margin call is tested against the notional the
    account would carry after the move -- both halves of that sentence matter, and using
    one price for both is how a simulator quietly understates the call.
    """
    if lots <= 0:
        return {"status": "no_lot", "lots": 0,
                "capital_needed_cny": round(capital / max(MARGIN_USE, 1e-9), 0)}
    equity = float(capital)
    peak, worst_dd = equity, 0.0
    worst_day_pct = 0.0
    path = [equity]
    for k, r in enumerate(r_eff):
        equity += lots * mult * prices[k] * r
        day_pct = (equity / path[-1] - 1.0) * 100.0 if path[-1] else 0.0
        worst_day_pct = min(worst_day_pct, day_pct)
        path.append(equity)
        peak = max(peak, equity)
        worst_dd = min(worst_dd, equity / peak - 1.0)
        notional_now = lots * mult * prices[min(k + 1, len(prices) - 1)]
        if equity <= maintenance_rate * notional_now:
            return {"status": "wiped", "lots": lots, "days_held": k + 1,
                    "call_date": dates[k + 1] if dates else None,
                    "equity_at_call_cny": round(equity, 0),
                    "loss_pct_of_capital": round((equity / capital - 1.0) * 100.0, 2),
                    "max_drawdown_pct": round(worst_dd * 100.0, 2),
                    "worst_day_pct": round(worst_day_pct, 2),
                    "survived": False}
    return {"status": "survived", "lots": lots, "days_held": len(r_eff),
            "final_equity_cny": round(equity, 0),
            "total_return_pct": round((equity / capital - 1.0) * 100.0, 2),
            "annualised_pct": round(((equity / capital) ** (base.TRADING_DAYS / max(len(r_eff), 1)) - 1.0) * 100.0, 2)
            if equity > 0 else None,
            "max_drawdown_pct": round(worst_dd * 100.0, 2),
            "worst_day_pct": round(worst_day_pct, 2),
            "survived": True}


def build():
    face = {"generated": datetime.now().isoformat(timespec="seconds"),
            "kind": "idx_fut_leverage_washout",
            "assumptions": {
                "multiplier_per_point": MULTIPLIER,
                "initial_margin_rate": MARGIN_RATE,
                "maintenance_margin_rate": MAINTENANCE_RATE,
                "margin_use_share_of_capital": MARGIN_USE,
                "side": "LONG futures (receives the discount, W1)",
                "sizing": "margin box = floor(capital*margin_use / (entry notional*initial_margin)); same rule as the desk sheet (W4)",
                "lifetime": "book opens on the panel's first day and is held to the last day: no de-levering, no adding, no re-entry after a call",
                "note": "assumptions are printed, not sourced: change a constant and re-run instead of arguing with a verdict",
            },
            "rules": {"W1": "long futures only", "W2": "roll splice excluded from P&L",
                      "W3": "wipeout is mechanical at equity <= maintenance*notional; nothing simulated after",
                      "W4": "lots match the desk sheet's ladder"},
            "products": {}}
    for product, (code, name, _etf) in base.PAIRS.items():
        fut_close = load_futures(product)
        if not fut_close:
            face["products"][product] = {"status": "no_futures_panel"}
            continue
        try:
            idx = base.load_index(code)
        except RuntimeError as exc:
            face["products"][product] = {"status": "no_index", "detail": str(exc)[:200]}
            continue
        dates, fc, ic = base.aligned(fut_close, idx)
        if len(dates) < 500:
            face["products"][product] = {"status": "short_overlap", "days": len(dates)}
            continue
        r_idx, r_eff, _roll = effective_returns(fc, ic, dates)
        mult = MULTIPLIER[product]
        rows = []
        entry_notional = mult * ic[0]
        for cap in TIERS:
            lots = lots_by_margin(cap, entry_notional)
            sim = simulate(cap, lots, mult, ic, r_eff, dates=dates)
            sim.update({"capital_cny": cap,
                        "entry_notional_per_lot_cny": round(entry_notional, 0),
                        "latest_notional_per_lot_cny": round(mult * ic[-1], 0)})
            rows.append(sim)
        index_dd = base.max_drawdown_pct(ic)
        face["products"][product] = {
            "status": "ok", "index": code, "index_name": name,
            "window": {"from": dates[0], "to": dates[-1], "days": len(dates)},
            "index_max_drawdown_pct": round(index_dd, 3),
            "ladder": rows,
            "verdict": _verdict(rows),
        }
    face["headline"] = _headline(face)
    return face


def _verdict(rows):
    """One sentence per product: did the margin-sized book survive its own history?"""
    survived = [r for r in rows if r.get("status") == "survived"]
    wiped = [r for r in rows if r.get("status") == "wiped"]
    if not survived and not wiped:
        return "NO_LOT_AT_ANY_TIER"
    if wiped and not survived:
        return "WIPED_AT_EVERY_TIER"
    if wiped:
        return "WIPED_AT_SMALL_TIERS_ONLY"
    return "SURVIVED_EVERY_TIER"


def _headline(face):
    """The money sentence: at each tier, how many products a margin book survives."""
    out = []
    for idx, cap in enumerate(TIERS):
        ok, wiped, nolot = [], [], []
        for product, block in face["products"].items():
            if block.get("status") != "ok":
                continue
            row = block["ladder"][idx]
            st = row.get("status")
            if st == "wiped":
                wiped.append(product)
            elif st == "no_lot":
                nolot.append(product)
            else:
                ok.append(product)
        out.append({"capital_cny": cap, "survived": ok, "wiped": wiped,
                    "cannot_afford_one_lot": nolot})
    return out


def selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, (" | " + detail) if detail else ""))

    # W4: sizing follows the margin box, and a capital below one lot's margin is zero lots.
    check("W4 lots = floor(capital*margin_use/(notional*initial_margin))",
          lots_by_margin(1000000, 1255360) == int(math.floor(1000000 * 0.6 / (1255360 * 0.15))),
          "got %d" % lots_by_margin(1000000, 1255360))
    check("W4 below one lot's margin is not a fractional position",
          lots_by_margin(100000, 1255360) == 0, "got %d" % lots_by_margin(100000, 1255360))

    # W1: a long book earns when futures outrun the index (the discount paying out).
    idx = [100.0] * 51
    r_eff = [0.001] * 50            # +10bp/day of carry, no index move
    sim = simulate(1000000, 1, 200, idx, r_eff)
    check("W1 long futures converts carry into equity gain",
          sim["status"] == "survived" and sim["total_return_pct"] > 0,
          json.dumps({k: sim[k] for k in ("status", "total_return_pct")}, ensure_ascii=False))
    # W1 negative control: the same carry read as a short book must lose.
    sim_short = simulate(1000000, 1, 200, idx, [-x for x in r_eff])
    check("W1 short-futures control loses on the same series",
          sim_short["status"] == "survived" and sim_short["total_return_pct"] < 0,
          json.dumps({k: sim_short[k] for k in ("status", "total_return_pct")}, ensure_ascii=False))

    # W2: a roll day must not book the splice as P&L. Build a panel whose day 10 jumps -5%
    # in the futures tape; the effective series (spread excluded on that day) must not move.
    fut = {}
    idxs = {}
    v = 100.0
    dates = ["2020-01-%02d" % d for d in range(1, 32)]
    for i, d in enumerate(dates):
        idxs[d] = 100.0
        fut[d] = 95.0 if i < 10 else 90.25   # a -5% splice at i==10
    fc = [fut[d] for d in dates]
    ic = [idxs[d] for d in dates]
    _ri, reff, roll = effective_returns(fc, ic, dates)
    jumped = [k for k, x in enumerate(reff) if abs(x) > 0.01]
    check("W2 roll splice does not appear as a holder's return",
          not jumped, "days above 1%%: %s" % jumped[:5])
    check("W2 splice is reported by the detector instead of swallowed",
          any(roll), "roll flags=%d" % sum(1 for x in roll if x))

    # W3: wipeout triggers at the maintenance line and nothing is simulated afterwards.
    # 60 lots x 200 x 100 = 1.2M notional against 200k of equity: the margin box is full,
    # which is the only way this rule can ever bite.
    idx_fall = [100.0 - i * 2.0 for i in range(30)]        # straight 2pt/day fall
    r_fall = [idx_fall[k + 1] / idx_fall[k] - 1.0 for k in range(29)]
    sim_w = simulate(200000, 60, 200, idx_fall, r_fall, maintenance_rate=0.12)
    check("W3 a fall through maintenance returns wiped, not a recovery", sim_w["status"] == "wiped",
          json.dumps({k: sim_w[k] for k in ("status", "days_held", "loss_pct_of_capital")}, ensure_ascii=False))
    check("W3 wipeout reports the loss and the call day", sim_w.get("days_held", 0) > 0
          and sim_w.get("loss_pct_of_capital", 0) <= -10.0, json.dumps(sim_w, ensure_ascii=False)[:160])
    # W3 negative control: a book that never breaches maintenance must be 'survived'.
    flat = simulate(1000000, 1, 200, [100.0] * 30, [0.0] * 29, maintenance_rate=0.12)
    check("W3 flat book survives and reports its drawdown as zero",
          flat["status"] == "survived" and flat["max_drawdown_pct"] == 0.0, json.dumps(flat, ensure_ascii=False)[:160])

    # W3 tail: the verdict vocabulary has to distinguish "wiped at every tier" from
    # "wiped where the margin box allows size" -- those are different decisions.
    rows_all_wiped = [{"status": "wiped"} for _ in TIERS]
    rows_mixed = [{"status": "wiped"}, {"status": "survived"}]
    rows_none = [{"status": "no_lot"} for _ in TIERS]
    check("verdict separates every-tier wipeout from mixed",
          _verdict(rows_all_wiped) == "WIPED_AT_EVERY_TIER" and _verdict(rows_mixed) == "WIPED_AT_SMALL_TIERS_ONLY",
          _verdict(rows_all_wiped) + "/" + _verdict(rows_mixed))
    check("verdict says NO_LOT when no tier can buy a contract", _verdict(rows_none) == "NO_LOT_AT_ANY_TIER",
          _verdict(rows_none))

    # Headline must place each product in exactly one bucket per tier.
    fake = {"products": {"X": {"status": "ok", "ladder": [{"status": "wiped"}] + [{"status": "survived"}] * 3}}}
    head = _headline(fake)[0]
    check("headline buckets are exclusive", head["wiped"] == ["X"] and "X" not in head["survived"],
          json.dumps(head, ensure_ascii=False))

    print("SELFTEST %s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    for product, block in face["products"].items():
        if block.get("status") != "ok":
            print("  %s: %s" % (product, block.get("status")))
            continue
        print("  %s [%s] index_mdd=%.1f%% verdict=%s" % (
            product, block["index_name"], block["index_max_drawdown_pct"], block["verdict"]))
        for row in block["ladder"]:
            if row["status"] == "no_lot":
                print("    %.0f: 0 lots" % row["capital_cny"])
            elif row["status"] == "wiped":
                print("    %.0f: %d lots -> WIPED %s (day %d, equity %.0f, %.1f%% of capital, mdd %.1f%%)" % (
                    row["capital_cny"], row["lots"], row.get("call_date") or "?", row["days_held"],
                    row["equity_at_call_cny"], row["loss_pct_of_capital"], row["max_drawdown_pct"]))
            else:
                print("    %.0f: %d lots -> survived, %.1f%% total, mdd %.1f%%, worst day %.1f%%" % (
                    row["capital_cny"], row["lots"], row["total_return_pct"],
                    row["max_drawdown_pct"], row["worst_day_pct"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
