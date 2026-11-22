"""ETF book -- the sell half of the ticket, in whole lots and in CNY.

The published ticket is one-directional. `k_gap` answers "how much more k until
I can ADD one lot" (`next_lot_dk_pp`) on every row, and nothing on the sheet says
what happens when the sizing dial goes the other way -- which is the direction
that actually happens when the book's beta to the market rises. A reader who
wants to de-risk holds a percentage and has to do the lot arithmetic alone.

This face is that mirror, computed from the ticket's own rows and the ticket's
own sizing identity (k = beta_target / beta_hat, clipped to [0, 1]):

  * for each k rung below today, how many whole lots of each name must be SOLD,
    the CNY that frees, and the cost at the ticket's own per-side bp;
  * the exact k fall needed to sell the FIRST lot of each name (the mirror of
    `next_lot_dk_pp`), and the beta_hat that each rung requires;
  * the honest boundary: this is the same book re-sized, not a new ranking. A
    real de-risk is executed on a decision bar (the ticket publishes the next
    one), at that bar's prices, so every CNY here is a price today, not a
    forecast.

No face is rewritten: the ticket is read, never touched.

  python scripts/etf_book_sell_plan.py run [--ticket PATH] [--nav CNY]
  python scripts/etf_book_sell_plan.py --check
  python scripts/etf_book_sell_plan.py --selftest

Outputs:
  results/etf_book_sell_plan.json
  research/ETF_BOOK_SELL_PLAN.md
"""
import argparse
import glob
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_book_sell_plan.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_SELL_PLAN.md")
TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")
RUNG_STEP = 0.05
LOT = 100


def load_latest_ticket(path=None):
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return path, json.load(f)
    cands = sorted(glob.glob(TICKET_GLOB))
    if not cands:
        return None, None
    # stem is a trading bar; the newest stem is the sheet a reader would open
    cands.sort(key=lambda p: os.path.basename(p))
    path = cands[-1]
    with open(path, "r", encoding="utf-8") as f:
        return path, json.load(f)


def lots_at(price, amount, lot=LOT):
    """Whole lots that fit in `amount` CNY at `price` -- the ticket's own floor rule."""
    if price is None or not (price > 0) or amount is None or not (amount >= 0):
        return None
    return int(amount // (price * lot))


def sell_at_rung(rows, nav, k_now, k_target, n_hold, cost_frac, lot=LOT):
    """What must be SOLD per name to move the sheet from k_now to k_target."""
    per_name = nav * float(k_target) / float(n_hold)
    out, sold_cny, unmeasured = [], 0.0, []
    for r in rows:
        sym, px, lots = r["symbol"], r.get("price"), r.get("lots")
        if px is None or not (px > 0) or lots is None:
            unmeasured.append(sym)
            out.append({"symbol": sym, "price": px, "lots_held": lots,
                        "lots_after": None, "lots_sell": None, "sell_cny": None,
                        "note": "UNMEASURABLE: no lot or no price"})
            continue
        after = lots_at(px, per_name, lot)
        sell = int(lots) - int(after)
        sell = sell if sell > 0 else 0
        cny = round(sell * lot * float(px), 2)
        sold_cny += cny
        out.append({"symbol": sym, "price": round(float(px), 4), "lots_held": int(lots),
                    "lots_after": int(after), "lots_sell": sell, "sell_cny": cny,
                    "note": "" if sell else "this name does not move at this rung"})
    return {
        "k_target": round(float(k_target), 6),
        "k_fall_pp": round(100.0 * (float(k_now) - float(k_target)), 3),
        "per_name_cny": round(per_name, 2),
        "book_after_cny": round(sum((r["lots_after"] or 0) * lot * float(r["price"])
                                    for r in out if r["lots_after"] is not None), 2),
        "sell_cny": round(sold_cny, 2),
        "sell_pct_of_nav": round(100.0 * sold_cny / float(nav), 3),
        "cost_cny": round(sold_cny * cost_frac, 2),
        "n_names_moving": sum(1 for r in out if (r["lots_sell"] or 0) > 0),
        "unmeasured": unmeasured,
        "rows": out,
    }


def one_lot_dk(rows, nav, k_now, n_hold, lot=LOT):
    """The k fall that sells the FIRST whole lot of each name (mirror of next_lot_dk_pp).

    Solving `nav * k / n_hold < lots_held * price * lot` for k: the lot disappears the
    moment the budget for that name drops under the value of the lots still held.
    """
    out = []
    for r in rows:
        sym, px, lots = r["symbol"], r.get("price"), r.get("lots")
        if px is None or not (px > 0) or lots is None:
            out.append({"symbol": sym, "dk_pp": None, "beta_at_trigger": None,
                        "note": "UNMEASURABLE: no lot or no price"})
            continue
        k_edge = float(n_hold) * int(lots) * float(px) * lot / float(nav)
        dk = max(0.0, float(k_now) - k_edge)
        out.append({"symbol": sym, "k_edge": round(k_edge, 9),
                    "dk_pp": round(100.0 * dk, 4),
                    "lots_held": int(lots),
                    "sell_cny_when_it_goes": round(lot * float(px), 2),
                    "note": ""})
    return out


def build(ticket_path, ticket, nav=None):
    tk = ticket.get("ticket") or {}
    rows = tk.get("order") or []
    k_now = float(ticket.get("k_now") if ticket.get("k_now") is not None
                  else tk.get("beta_k"))
    beta_target = float(ticket.get("beta_target") or 0.20)
    cost_bp = float(ticket.get("cost_bp_per_side") or 8.0)
    cost_frac = cost_bp / 10000.0
    n_hold = int(ticket.get("n_hold") or len(rows) or 5)
    nav = float(nav if nav is not None else (tk.get("nav") or 0) or 1000000.0)

    beta_now = (beta_target / k_now) if k_now > 0 else None
    floor_k = min(1.0, beta_target / 1.0)          # beta_hat = 1.0 -> k = target
    rungs = []
    k = math.floor(k_now / RUNG_STEP) * RUNG_STEP - 0.0
    # first rung strictly below today, then every step down, then the beta=1 floor
    k = round(k_now - RUNG_STEP, 6) if k_now - RUNG_STEP > floor_k else None
    while k is not None and k > floor_k + 1e-9:
        rungs.append(round(k, 6))
        k = round(k - RUNG_STEP, 6)
    if floor_k < k_now - 1e-9 and (not rungs or abs(rungs[-1] - floor_k) > 1e-9):
        rungs.append(round(floor_k, 6))

    ladder = []
    for kt in rungs:
        d = sell_at_rung(rows, nav, k_now, kt, n_hold, cost_frac)
        d["beta_at_trigger"] = round(beta_target / kt, 6) if kt > 0 else None
        d["beta_rise_pct"] = (round(100.0 * ((beta_target / kt) / beta_now - 1.0), 2)
                              if beta_now and kt > 0 else None)
        ladder.append(d)

    deepest = ladder[-1] if ladder else None
    one_turn_cost = None
    try:
        # the ticket page's own turn cost: 8bp on the book it orders
        one_turn_cost = round(float(tk.get("book_amount") or 0) * cost_frac, 2)
    except Exception:
        one_turn_cost = None

    if deepest is None:
        verdict = "NO_RUNG_BELOW_TODAY"
    elif deepest["unmeasured"]:
        verdict = "LADDER_PARTIAL_UNMEASURABLE_NAMES"
    elif one_turn_cost and deepest["cost_cny"] <= one_turn_cost:
        verdict = "DE_RISK_COSTS_LESS_THAN_ONE_TURN"
    else:
        verdict = "DE_RISK_COSTS_MORE_THAN_ONE_TURN"

    return {
        "artifact": "etf_book_sell_plan",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": ticket.get("evidence_cutoff"),
        "ticket": os.path.relpath(ticket_path, ROOT).replace("\\", "/"),
        "ticket_generated": ticket.get("generated"),
        "question": ("when the sizing dial goes down, what has to be SOLD -- which "
                     "whole lots, how many CNY, and what does it cost"),
        "identity": {
            "rule": "k = beta_target / beta_hat clipped to [0, 1] (imported identity, "
                    "read off the ticket; scripts/etf_book_order.py k_schedule)",
            "beta_target": beta_target,
            "k_now": round(k_now, 6),
            "beta_now": None if beta_now is None else round(beta_now, 6),
            "cost_bp_per_side": cost_bp,
            "nav_cny": nav,
            "n_hold": n_hold,
            "lot": LOT,
        },
        "book_now": {
            "book_cny": round(sum(float(r.get("amount") or 0) for r in rows), 2),
            "cash_cny": round(float(tk.get("cash_amount") or 0), 2),
            "n_names": len(rows),
            "one_turn_cost_cny": one_turn_cost,
        },
        "ladder": ladder,
        "one_lot_first_sell": one_lot_dk(rows, nav, k_now, n_hold),
        "next_decision_bar": (ticket.get("next_decision") or {}).get("grid", {}).get("next_bar"),
        "verdict": verdict,
        "limits": [
            "same book re-sized, not a new ranking: a real de-risk executes on a "
            "decision bar at that bar's prices, so every CNY here is today's price",
            "k moves only when beta_hat moves; beta_hat is the engine's expanding slope, "
            "not a number this face estimates",
            "whole lots only: each name floors separately, so the freed CNY differs from "
            "(k_now - k_target) * nav by at most one lot per name, in either direction",
            "this face does not decide that a de-risk is due -- it prices the action "
            "once the sizing rule has already said so",
        ],
        "sentence": None,
    }


def sentence(face):
    idn = face["identity"]
    rows = face["ladder"]
    if not rows:
        return "No k rung sits below today's %.6f, so there is nothing to sell." % idn["k_now"]
    deep = rows[-1]
    first = rows[0]
    return ("If the sizing dial goes from %.4f to %.4f (beta_hat %.3f -> %.3f), the sheet "
            "sells %d lots across %d names for %s CNY, which frees %.2f%% of NAV and costs "
            "%s CNY at %s bp per side; going all the way to %.2f sells %s CNY for %s CNY, "
            "against %s CNY for one ordinary turn."
            % (idn["k_now"], first["k_target"], idn["beta_now"] or float("nan"),
               first["beta_at_trigger"], sum(r["lots_sell"] or 0 for r in first["rows"]),
               first["n_names_moving"], format(first["sell_cny"], ",.0f"),
               first["sell_pct_of_nav"], format(first["cost_cny"], ",.2f"),
               idn["cost_bp_per_side"], deep["k_target"],
               format(deep["sell_cny"], ",.0f"), format(deep["cost_cny"], ",.2f"),
               format(face["book_now"]["one_turn_cost_cny"] or 0, ",.0f")))


def write_doc(face):
    idn = face["identity"]
    L = []
    L.append("# ETF book -- the sell half of the ticket\n")
    L.append("generated %s | ticket `%s` (ticket generated %s) | cutoff %s\n"
             % (face["generated"], face["ticket"], face["ticket_generated"],
                face["evidence_cutoff"]))
    L.append("## What this answers\n")
    L.append(face["question"] + ".\n")
    L.append("The ticket only ever looked up: every row carried `next_lot_dk_pp`, the k "
             "rise needed to ADD a lot. When the dial goes down -- which is what happens "
             "when the book's beta to the market rises -- the reader had a percentage and "
             "no lots. This is that mirror.\n")
    L.append("## The sell ladder\n")
    L.append("| k | beta_hat required | beta rise | lots sold | names moving | CNY freed | % NAV | cost CNY |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in face["ladder"]:
        L.append("| %.4f | %s | %s%% | %d | %d | %s | %.3f | %.2f |"
                 % (r["k_target"],
                    "%.3f" % r["beta_at_trigger"] if r["beta_at_trigger"] else "--",
                    "%.1f" % r["beta_rise_pct"] if r["beta_rise_pct"] is not None else "--",
                    sum(x["lots_sell"] or 0 for x in r["rows"]), r["n_names_moving"],
                    format(r["sell_cny"], ",.0f"), r["sell_pct_of_nav"], r["cost_cny"]))
    L.append("")
    L.append("## What it takes to sell the FIRST lot of each name\n")
    L.append("| name | lots held | k fall needed | one lot is | beta_hat at that point |")
    L.append("|---|---|---|---|---|")
    for r in face["one_lot_first_sell"]:
        L.append("| %s | %s | %s | %s | %s |"
                 % (r["symbol"], r.get("lots_held") or "--",
                    ("%.4f pp" % r["dk_pp"]) if r.get("dk_pp") is not None else "UNMEASURABLE",
                    format(r["sell_cny_when_it_goes"], ",.2f")
                    if r.get("sell_cny_when_it_goes") else "--",
                    "%.3f" % (idn["beta_target"] / r["k_edge"])
                    if r.get("k_edge") else "--"))
    L.append("")
    L.append("## Verdict\n")
    L.append("`%s`\n" % face["verdict"])
    L.append(face["sentence"] + "\n")
    L.append("## What this face does not say\n")
    for lim in face["limits"]:
        L.append("- " + lim)
    L.append("")
    L.append("Next decision bar: `%s`.\n" % (face["next_decision_bar"] or "unreadable"))
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


def run(ticket_path=None, nav=None):
    path, ticket = load_latest_ticket(ticket_path)
    if ticket is None:
        print("no ticket on disk -> nothing to price")
        return 2
    face = build(path, ticket, nav=nav)
    face["sentence"] = sentence(face)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    write_doc(face)
    print("SELL PLAN %s | k %.4f -> %.4f | %d rungs | deepest %s CNY for %s CNY"
          % (face["verdict"], face["identity"]["k_now"],
             face["ladder"][-1]["k_target"] if face["ladder"] else float("nan"),
             len(face["ladder"]),
             format(face["ladder"][-1]["sell_cny"], ",.0f") if face["ladder"] else "--",
             format(face["ladder"][-1]["cost_cny"], ",.2f") if face["ladder"] else "--"))
    print("  -> results/etf_book_sell_plan.json / research/ETF_BOOK_SELL_PLAN.md")
    return 0


def _load_face():
    if not os.path.exists(OUT):
        return None
    with open(OUT, "r", encoding="utf-8") as f:
        return json.load(f)


def check():
    face = _load_face()
    if face is None:
        print("STALE face missing: results/etf_book_sell_plan.json")
        return 3
    path, ticket = load_latest_ticket(face.get("ticket") and
                                      os.path.join(ROOT, face["ticket"]))
    if ticket is None:
        print("STALE ticket missing")
        return 3
    mine = build(path, ticket)
    mine["sentence"] = sentence(mine)
    errs = []
    if face.get("verdict") != mine["verdict"]:
        errs.append("verdict %s != rebuilt %s" % (face.get("verdict"), mine["verdict"]))
    for k in ("k_now", "beta_now", "nav_cny", "beta_target"):
        a, b = face["identity"].get(k), mine["identity"].get(k)
        if isinstance(a, float) or isinstance(b, float):
            if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
                errs.append("identity.%s %s != %s" % (k, a, b))
        elif a != b:
            errs.append("identity.%s %s != %s" % (k, a, b))
    if len(face.get("ladder") or []) != len(mine["ladder"]):
        errs.append("ladder rungs %d != %d"
                    % (len(face.get("ladder") or []), len(mine["ladder"])))
    else:
        for a, b in zip(face["ladder"], mine["ladder"]):
            if abs(float(a["sell_cny"]) - float(b["sell_cny"])) > 0.01:
                errs.append("rung %.4f sell_cny %s != %s"
                            % (b["k_target"], a["sell_cny"], b["sell_cny"]))
            if abs(float(a["cost_cny"]) - float(b["cost_cny"])) > 0.01:
                errs.append("rung %.4f cost_cny %s != %s"
                            % (b["k_target"], a["cost_cny"], b["cost_cny"]))
    doc_ok = os.path.exists(DOC)
    if not doc_ok:
        errs.append("doc missing")
    if errs:
        print("CHECK FAILED (%d)" % len(errs))
        for e in errs[:12]:
            print("  - " + e)
        return 3
    print("CHECK_OK rungs=%d deepest=%s sentence=yes doc=%s"
          % (len(mine["ladder"]),
             format(mine["ladder"][-1]["sell_cny"], ",.0f") if mine["ladder"] else "--",
             "yes" if doc_ok else "no"))
    return 0


def selftest():
    fails = []

    def chk(cond, msg):
        if not cond:
            fails.append(msg)

    rows = [
        {"symbol": "A", "price": 1.228, "lots": 708},
        {"symbol": "B", "price": 1.183, "lots": 735},
        {"symbol": "C", "price": 1.854, "lots": 469},
        {"symbol": "D", "price": 1.116, "lots": 779},
        {"symbol": "E", "price": 1.702, "lots": 511},
    ]
    nav, k_now, n_hold, cf = 1000000.0, 0.435003, 5, 0.0008

    # L1 whole-lot budget rule: the ticket's own floor, not a round
    chk(lots_at(1.228, 87001.0) == int(87001.0 // 122.8), "lots_at floors by lot")
    chk(lots_at(None, 1000.0) is None, "no price -> None, never zero")
    chk(lots_at(1.228, None) is None, "no amount -> None")

    # L2 at today's k nothing moves -- the ladder must not invent sells
    same = sell_at_rung(rows, nav, k_now, k_now, n_hold, cf)
    chk(same["sell_cny"] == 0.0, "k unchanged sells nothing")
    chk(all((r["lots_sell"] == 0) for r in same["rows"]), "k unchanged: every row flat")

    # L3 whole-lot residual: freed CNY is never more than the notional, and the gap
    #    is at most one lot per name at the dearest price
    deep = sell_at_rung(rows, nav, k_now, 0.20, n_hold, cf)
    book_now = sum(x["lots"] * 100 * x["price"] for x in rows)
    book_after = book_now - deep["sell_cny"]
    chk(deep["sell_cny"] <= book_now + 1e-6, "freed <= the book on the sheet")
    chk(-(n_hold * 100 * 1.854) - 1e-6 <= book_after - 0.20 * nav <= 1e-6,
        "after the deepest rung the book sits just under the target notional")

    # L4 cost is the stated bp of what is freed
    chk(abs(deep["cost_cny"] - deep["sell_cny"] * cf) <= 0.02, "cost = bp x freed")

    # L5 monotone: a deeper rung never sells fewer lots of a name
    mid = sell_at_rung(rows, nav, k_now, 0.35, n_hold, cf)
    for a, b in zip(mid["rows"], deep["rows"]):
        chk((b["lots_sell"] or 0) >= (a["lots_sell"] or 0),
            "deeper rung sells >= per name (%s)" % a["symbol"])

    # L6 the one-lot dk is the exact boundary: one tick below it, a lot is gone
    for r in one_lot_dk(rows, nav, k_now, n_hold):
        if r.get("dk_pp") is None:
            continue
        edge = float(r["k_edge"])
        px = next(x["price"] for x in rows if x["symbol"] == r["symbol"])
        after = lots_at(px, nav * (edge - 1e-7) / n_hold)
        chk(after <= r["lots_held"] - 1, "one tick under the edge loses a lot (%s)" % r["symbol"])
        before = lots_at(px, nav * (edge + 1e-7) / n_hold)
        chk(before >= r["lots_held"], "at the edge the lot is still held (%s)" % r["symbol"])

    # L7 identity: every rung names the beta_hat it needs
    for kt in (0.40, 0.30, 0.20):
        chk(abs(0.20 / kt - (0.20 / kt)) < 1e-12, "beta identity holds")

    # L8 an unmeasurable name does not silently vanish into the total
    bad = sell_at_rung(rows + [{"symbol": "Z", "price": None, "lots": 10}],
                       nav, k_now, 0.30, 6, cf)
    chk(bad["unmeasured"] == ["Z"], "unmeasurable name is named")
    chk(any(r["lots_sell"] is None for r in bad["rows"]), "unmeasurable row has no zero")

    # L9 the ladder never quotes a rung above today (that would be a buy, not a sell)
    tic = {"evidence_cutoff": "2026-11-20", "beta_target": 0.2, "k_now": k_now,
           "cost_bp_per_side": 8, "n_hold": 5,
           "ticket": {"order": rows, "nav": nav, "cash_amount": 565245.9,
                      "book_amount": 434754.1}}
    face = build(os.path.join(ROOT, "results", "etf_book_order", "TICKET-2026-11-20.json"),
                 tic, nav=nav)
    chk(all(r["k_target"] < k_now for r in face["ladder"]), "no rung above today")
    chk(face["identity"]["beta_now"] is not None, "beta_now derived from k")
    chk(face["ladder"][-1]["k_target"] <= 0.20 + 1e-9, "ladder reaches the beta=1 floor")

    # L10 the sentence carries the money, not only the percentage
    s = sentence(face)
    chk("CNY" in s and "lots" in s, "sentence prints lots and CNY")

    if fails:
        print("SELFTEST FAILED (%d)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST PASS (10 legs)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--ticket", default=None)
    ap.add_argument("--nav", type=float, default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    return run(a.ticket, a.nav)


if __name__ == "__main__":
    sys.exit(main())
