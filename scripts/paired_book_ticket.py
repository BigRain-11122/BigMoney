#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One wallet, two books -- the order list that actually puts them together.

Why this face exists
--------------------
r2173 priced the question "is splitting the wallet better than picking the better
book" and answered it with a blend of the two published books (30% convertible /
70% ETF, Sharpe 1.066 vs 0.969 and 0.532).  That number tells a reader the split
is worth having.  It does not tell them what to buy: each book has its own ticket
(`results/etf_book_nobond_ticket.json`, `results/cb_book_ticket_floor.json`), and
nobody has ever printed the two side by side for one wallet.

Two facts make that omission expensive:

  * the ETF sleeve of the blend is the 8% vol-target book, which deliberately
    holds ~25% cash -- so a "70% ETF" sleeve is only ~52% equity exposure, and a
    reader who budgets 70% will think they bought 70%;
  * the convertible sleeve is twenty names at one board lot each, so a 30% sleeve
    below 25,850 CNY holds *fewer names* -- i.e. it is not the book that was
    backtested, it is a thinner one.

This face is a ticket, not a new strategy.  It imports both parents' published
picks (their screens and their weights, not a re-implementation), splits the
wallet at the weight `results/book_pair_blend.json` calls best, and prints whole
lots, fees, and cash -- separated into the cash the book *meant* to hold (the vol
target) and the cash the lot grid *left behind* (an artifact).

Frozen rules
------------
    split          w_cb taken from book_pair_blend.best.w_cb, never chosen here
    ETF sleeve     budget_i = weight_i * (1-w_cb) * W, whole 100-share lots,
                   fee = max(5 CNY, 3bp) per name
    CB sleeve      the same `ticket_math` the CB ladder uses (10 bonds a lot),
                   imported from scripts/cb_book_ticket_floor.py
    refuse         the two parents priced on different bars -- one wallet cannot
                   be assembled from two different days, so nothing is published

Verdict (frozen before the first run):

    HOLDS_THE_BLEND      both sleeves hold every name and the lot grid strands
                         <= STRAND_CAP of the wallet
    HOLDS_WITH_STRAND    every name holds, but the grid strands more than that
    CB_SLEEVE_TOO_SMALL  the 30% sleeve is below one lot of each of the twenty
                         names -- prints how much more money closes the gap
    ETF_SLEEVE_TOO_SMALL the 70% sleeve cannot buy one lot of all five names
    PARTIAL              a sleeve holds some names and not others

Freshness: `check` compares the three input stamps (bytes+mtime) recorded when
this ticket priced (~0.05s, no panel load) and says STALE when any moved; a face
that is missing says `face missing`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

ETF_TICKET = os.path.join(ROOT, "results", "etf_book_nobond_ticket.json")
CB_TICKET = os.path.join(ROOT, "results", "cb_book_ticket_floor.json")
BLEND = os.path.join(ROOT, "results", "book_pair_blend.json")
OUT_JSON = os.path.join(ROOT, "results", "paired_book_ticket.json")
OUT_MD = os.path.join(ROOT, "results", "paired_book_ticket.md")

LOT_SHARES = 100          # A-share ETF board lot
FEE_FLOOR = 5.0           # CNY per ticket, the brokers' usual minimum
BROKER_BP = 3.0           # per side, the assumption the ETF parent's ticket uses
STRAND_CAP = 0.02         # lot-grid cash above 2% of the wallet is a printed cost
REFERENCE_WALLETS = (50_000, 100_000, 200_000, 500_000, 1_000_000)


# ------------------------------------------------------------------ pure parts
def etf_sleeve(budget: float, picks: list[dict]) -> dict:
    """Whole 100-share lots of every name at the published weights inside `budget`."""
    legs, invested, fees = [], 0.0, 0.0
    for p in picks:
        b = round(float(budget) * p["weight"], 2)
        one = float(p["one_lot_cny"])
        lots = int(math.floor(b / one)) if one > 0 else 0
        amount = round(lots * one, 2)
        fee = round(max(FEE_FLOOR, amount * BROKER_BP / 10_000.0), 2) if amount > 0 else 0.0
        invested += amount
        fees += fee
        legs.append({
            "symbol": p["symbol"],
            "weight": p["weight"],
            "price_close": p["price_close"],
            "one_lot_cny": round(one, 2),
            "budget_cny": b,
            "lots": lots,
            "shares": lots * LOT_SHARES,
            "amount_cny": amount,
            "fee_cny": fee,
            "residual_cny": round(b - amount, 2),
            "fits": bool(lots > 0),
        })
    tot_w = sum(p["weight"] for p in picks)
    return {
        "budget_cny": round(float(budget), 2),
        "design_cash_cny": round(float(budget) * max(0.0, 1.0 - tot_w), 2),
        "invested_cny": round(invested, 2),
        "fees_cny": round(fees, 2),
        "lot_residual_cny": round(float(budget) - invested - float(budget) * max(0.0, 1.0 - tot_w), 2),
        "names": len(picks),
        "names_held": int(sum(1 for l in legs if l["lots"] > 0)),
        "legs": legs,
    }


def cb_sleeve(budget: float, one_lots: list[float]) -> dict:
    """The CB ladder's own whole-lot arithmetic, imported so the numbers reconcile."""
    import cb_book_ticket_floor as cb
    m = cb.ticket_math(one_lots, float(budget))
    m["fees_cny"] = 0.0   # the CB parent never prices a broker bill; print it as absent
    return m


def paired(wallet: float, etf_picks, cb_one_lots, w_cb: float) -> dict:
    etf_budget = round(float(wallet) * (1.0 - w_cb), 2)
    cb_budget = round(float(wallet) * w_cb, 2)
    e = etf_sleeve(etf_budget, etf_picks)
    c = cb_sleeve(cb_budget, cb_one_lots)
    invested = round(e["invested_cny"] + c["invested"], 2)
    fees = round(e["fees_cny"] + c["fees_cny"], 2)
    cash = round(float(wallet) - invested - fees, 2)
    grid_cash = round(e["lot_residual_cny"] + c["stranded"], 2)
    return {
        "wallet_cny": round(float(wallet), 2),
        "w_cb": w_cb,
        "etf_sleeve_cny": etf_budget,
        "cb_sleeve_cny": cb_budget,
        "etf": e,
        "cb": c,
        "invested_cny": invested,
        "fees_cny": fees,
        "cash_cny": cash,
        "cash_pct": round(cash / float(wallet), 6) if wallet else None,
        "design_cash_cny": e["design_cash_cny"],
        "lot_grid_cash_cny": grid_cash,
        "lot_grid_pct": round(grid_cash / float(wallet), 6) if wallet else None,
        "names_held": int(e["names_held"] + c["names_held"]),
        "names_total": int(e["names"] + c["n"]),
    }


def verdict_of(m: dict) -> str:
    e, c = m["etf"], m["cb"]
    if c["n"] and c["names_held"] == 0:
        return "CB_SLEEVE_TOO_SMALL"
    if e["names"] and e["names_held"] == 0:
        return "ETF_SLEEVE_TOO_SMALL"
    if e["names_held"] < e["names"] or c["names_held"] < c["n"]:
        return "PARTIAL"
    if m["lot_grid_pct"] is not None and m["lot_grid_pct"] > STRAND_CAP:
        return "HOLDS_WITH_STRAND"
    return "HOLDS_THE_BLEND"


def bars_align(etf_bar, cb_bar) -> bool:
    """One wallet cannot be assembled from two different days (r2174 guard)."""
    return bool(etf_bar) and bool(cb_bar) and etf_bar == cb_bar


def min_wallet_cny(cb_rung: float, w_cb: float) -> float:
    """The wallet whose 30% sleeve is exactly the CB book's one-lot floor."""
    return round(float(cb_rung) / float(w_cb), 2)


def rung_wallet_ceil(cb_rung: float, w_cb: float) -> int:
    """The floor above, rounded UP to whole yuan -- the lot grid needs the budget to reach."""
    return int(math.ceil(float(cb_rung) / float(w_cb)))


# ------------------------------------------------------------------ io helpers
def stamp(path: str):
    try:
        st = os.stat(path)
    except OSError:
        return None
    return {"bytes": int(st.st_size), "mtime": int(st.st_mtime)}


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ build
def build() -> dict:
    missing = [os.path.relpath(p, ROOT) for p in (ETF_TICKET, CB_TICKET, BLEND) if not os.path.exists(p)]
    if missing:
        return {"face": "paired_book_ticket", "status": "face missing",
                "why": "missing inputs: " + ", ".join(missing)}

    etf = load(ETF_TICKET)
    cb = load(CB_TICKET)
    blend = load(BLEND)
    w_cb = float((blend.get("best") or {}).get("w_cb") or 0.0)
    etf_picks = etf.get("picks") or []
    cb_picks = cb.get("picks") or []
    if not w_cb or not etf_picks or not cb_picks:
        return {"face": "paired_book_ticket", "status": "no input",
                "why": "blend best.w_cb=%r, etf picks=%d, cb picks=%d"
                       % (w_cb, len(etf_picks), len(cb_picks))}

    # one wallet cannot be assembled from two different days
    etf_bar, cb_bar = etf.get("asof_bar"), cb.get("evidence_cutoff")
    if not bars_align(etf_bar, cb_bar):
        return {"face": "paired_book_ticket", "status": "SLEEVES_OFF_BY_DAYS",
                "why": ("the ETF sleeve was priced on %r and the CB sleeve on %r -- "
                        "a single wallet cannot mix two days; re-price the older ticket"
                        % (etf_bar, cb_bar)),
                "etf_asof_bar": etf_bar, "cb_asof_bar": cb_bar}

    cb_one_lots = [float(p["one_lot_cny"]) for p in cb_picks]
    cb_rung = float((cb.get("one_lot_floor") or {}).get("rung_cny") or 0.0)
    min_wallet = min_wallet_cny(cb_rung, w_cb)
    floor_wallet = rung_wallet_ceil(cb_rung, w_cb)

    # r2174: `book_pair_blend` publishes a minimum wallet of 86,167 CNY -- 25,850.20 / 0.30
    # rounded DOWN to the yuan.  The lot grid does not round: at exactly 86,167 the CB
    # sleeve budgets 25,850.10 against a 25,850.20 rung, so one name is silently dropped
    # and the wallet is not the book that was backtested.  Print both sides of that yuan.
    blend_pub = (blend.get("executable_floor") or {}).get("min_wallet_cny")
    probe_wallet = float(blend_pub) if blend_pub else min_wallet
    at_published = paired(probe_wallet, etf_picks, cb_one_lots, w_cb)
    at_ceil = paired(floor_wallet, etf_picks, cb_one_lots, w_cb)
    floor_check = {
        "published_min_wallet_cny": round(probe_wallet, 2),
        "published_by": "results/book_pair_blend.json executable_floor.min_wallet_cny",
        "cb_budget_at_published_cny": at_published["cb_sleeve_cny"],
        "cb_one_lot_rung_cny": round(cb_rung, 2),
        "holds_at_published_floor": at_published["cb"]["names_held"] == at_published["cb"]["n"],
        "names_held_at_published": at_published["cb"]["names_held"],
        "exact_threshold_cny": min_wallet,
        "true_min_wallet_cny": floor_wallet,
        "names_held_at_ceil": at_ceil["cb"]["names_held"],
        "gap_cny": round(floor_wallet - probe_wallet, 2),
        "why": ("the published floor divides the one-lot rung by the sleeve weight and "
                "rounds to the yuan; the grid needs the budget to reach the rung, so the "
                "wallet must round UP -- one yuan below, one name is silently dropped"),
    }

    wallets = sorted(set(list(REFERENCE_WALLETS) + [round(probe_wallet), floor_wallet]))
    ladder = []
    for w in wallets:
        m = paired(w, etf_picks, cb_one_lots, w_cb)
        m["verdict"] = verdict_of(m)
        ladder.append(harvest(m))

    # reconciliation: the ETF sleeve at a parent capital must BE the parent's ticket,
    # and the CB floor must reproduce the blend face's own executable minimum.
    recon = {"etf_tickets": [], "cb_rung_cny": round(cb_rung, 2),
             "min_wallet_cny": min_wallet}
    for t in etf.get("tickets") or []:
        mine = etf_sleeve(t["capital_cny"], etf_picks)
        diffs = []
        for a, b in zip(mine["legs"], t["legs"]):
            for k in ("symbol", "lots", "shares", "amount_cny", "fee_cny"):
                if a[k] != b[k]:
                    diffs.append("%s@%s %s %r != %r" % (t["capital_cny"], a["symbol"], k, a[k], b[k]))
        recon["etf_tickets"].append({"capital_cny": t["capital_cny"],
                                     "legs": len(mine["legs"]), "diffs": diffs,
                                     "matches": not diffs})
    blend_floor = (blend.get("executable_floor") or {}).get("min_wallet_cny")
    recon["blend_min_wallet_cny"] = blend_floor
    recon["min_wallet_matches_blend"] = (
        blend_floor is not None and abs(float(blend_floor) - min_wallet) <= 0.51)
    recon["why"] = ("the ETF sleeve must reproduce the parent ticket lot for lot, and the "
                    "minimum wallet must be the same number the blend face published -- "
                    "if either fails this is not the blend's ticket")

    by_v = {str(key): next((x["verdict"] for x in ladder if x["wallet_cny"] == key), None)
            for key in [w for w in wallets]}
    first_holds = next((x for x in ladder if x["verdict"] in ("HOLDS_THE_BLEND", "HOLDS_WITH_STRAND")), None)
    short = None
    if first_holds is None or first_holds["wallet_cny"] > floor_wallet:
        short = {"needed_cny": floor_wallet,
                 "why": "below this the 30%% sleeve cannot hold one lot of all %d names" % len(cb_picks)}

    out = {
        "face": "paired_book_ticket",
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": etf_bar,
        "question": ("with one wallet and the 30/70 split the blend face calls best, "
                     "what exactly do I buy -- lots, fees, and the cash that is left?"),
        "split": {"w_cb": w_cb, "w_etf": round(1.0 - w_cb, 6),
                  "source": "results/book_pair_blend.json best.w_cb (imported, not chosen here)"},
        "inputs": {
            "etf": {"face": "results/etf_book_nobond_ticket.json", "asof_bar": etf_bar,
                    "stamp": stamp(ETF_TICKET),
                    "scale": (etf.get("sizing") or {}).get("scale"),
                    "cash_weight": (etf.get("sizing") or {}).get("cash_weight"),
                    "picks": [p["symbol"] for p in etf_picks]},
            "cb": {"face": "results/cb_book_ticket_floor.json", "asof_bar": cb_bar,
                   "stamp": stamp(CB_TICKET), "picks": [p["code"] for p in cb_picks],
                   "one_lot_floor_cny": round(cb_rung, 2)},
            "blend": {"face": "results/book_pair_blend.json", "stamp": stamp(BLEND),
                      "verdict": (blend.get("verdict") or {}).get("word")},
        },
        "cash_caliber": {
            "design_cash": "inside the ETF sleeve: the 8% vol target deliberately holds "
                           "this much out of equities (not an artifact)",
            "lot_grid_cash": "left behind by whole lots (100 shares of an ETF, 10 bonds of "
                             "a CB) -- this is the artifact, and it is what STRAND_CAP judges",
        },
        "ladder": ladder,
        "verdict_by_wallet": by_v,
        "floor_check": floor_check,
        "first_wallet_that_holds": (first_holds or {}).get("wallet_cny"),
        "short": short,
        "reconciliation": recon,
        "honest_limits": [
            "prices are each parent's as-of close; a real order pays the next open plus impact",
            "the CB parent prices no broker bill, so this ticket's fee line is the ETF sleeve only",
            "the 30/70 split is sample-in optimal on the overlap (2020-01..2026-11) -- it is "
            "the blend face's best, not a law",
            "cash between the two sleeves is not rebalanced here; the blend face's own note "
            "says it models no transfer cost",
            "the CB sleeve's twenty names are chosen on one bar; names that leave the pool "
            "before the next rebalance are the book's problem, not the ticket's",
        ],
    }
    return out


def harvest(m: dict) -> dict:
    """The ladder row: enough to read, not the whole leg table."""
    return {
        "wallet_cny": m["wallet_cny"],
        "verdict": m["verdict"],
        "etf_sleeve_cny": m["etf_sleeve_cny"],
        "cb_sleeve_cny": m["cb_sleeve_cny"],
        "etf_names_held": m["etf"]["names_held"],
        "etf_names": m["etf"]["names"],
        "cb_names_held": m["cb"]["names_held"],
        "cb_names": m["cb"]["n"],
        "cb_top_weight": m["cb"]["top_weight"],
        "cb_max_weight_dev_pp": m["cb"]["max_weight_dev_pp"],
        "invested_cny": m["invested_cny"],
        "fees_cny": m["fees_cny"],
        "cash_cny": m["cash_cny"],
        "cash_pct": m["cash_pct"],
        "design_cash_cny": m["design_cash_cny"],
        "lot_grid_cash_cny": m["lot_grid_cash_cny"],
        "lot_grid_pct": m["lot_grid_pct"],
    }


# ------------------------------------------------------------------ page
def render_md(face: dict) -> str:
    L = []
    A = L.append
    A("# One wallet, two books -- the order list")
    A("")
    A("generated %s | priced on bar %s | split %.0f%% CB / %.0f%% ETF (from the blend face)"
      % (face["generated"], face["evidence_cutoff"],
         100 * face["split"]["w_cb"], 100 * face["split"]["w_etf"]))
    A("")
    A("> " + face["question"])
    A("")
    A("## What the two sleeves are on this bar")
    A("")
    ei, ci = face["inputs"]["etf"], face["inputs"]["cb"]
    A("* ETF sleeve -- %d names %s, vol-target scale %.4f, so %.1f%% of *its own* budget sits in cash by design"
      % (len(ei["picks"]), ", ".join(ei["picks"]), ei["scale"] or 0, 100 * (ei["cash_weight"] or 0)))
    A("* CB sleeve -- %d names, one board lot each costs %.0f CNY of wallet before the sleeve fits at all"
      % (len(ci["picks"]), ci["one_lot_floor_cny"] / max(face["split"]["w_cb"], 1e-9)))
    A("")
    A("## Wallet ladder")
    A("")
    A("| wallet CNY | verdict | ETF names | CB names | invested | cash | of which design cash | of which lot-grid cash |")
    A("|---|---|---|---|---|---|---|---|")
    for m in face["ladder"]:
        A("| %s | %s | %d/%d | %d/%d | %s | %.1f%% | %.0f | %.1f%% |"
          % (f"{m['wallet_cny']:,.0f}", m["verdict"], m["etf_names_held"], m["etf_names"],
             m["cb_names_held"], m["cb_names"], f"{m['invested_cny']:,.0f}",
             100 * (m["cash_pct"] or 0), m["design_cash_cny"], 100 * (m["lot_grid_pct"] or 0)))
    A("")
    if face.get("short"):
        A("The 30%% sleeve holds all twenty convertible names only from **%s CNY** upward "
          "(one lot of each = %.0f)." % (f"{face['short']['needed_cny']:,.0f}",
                                          face["inputs"]["cb"]["one_lot_floor_cny"]))
        A("")
    fc = face.get("floor_check") or {}
    if fc:
        A("### The published minimum is one yuan short")
        A("")
        A("`book_pair_blend` prints a minimum wallet of **%s CNY** (%.2f / %.2f, rounded to the yuan). "
          "At that wallet the CB sleeve budgets %s CNY against a %s CNY lot rung, so **%d of %d names "
          "are held** -- the book is not the backtested book. At **%s CNY** all %d hold. "
          "The difference is %s CNY, and it is the whole point of printing a ticket instead of a ratio."
          % (f"{fc['published_min_wallet_cny']:,.2f}", fc["cb_one_lot_rung_cny"], face["split"]["w_cb"],
             f"{fc['cb_budget_at_published_cny']:,.2f}", f"{fc['cb_one_lot_rung_cny']:,.2f}",
             fc["names_held_at_published"], face["inputs"]["cb"]["picks"].__len__(),
             f"{fc['true_min_wallet_cny']:,.0f}", fc["names_held_at_ceil"],
             f"{fc['gap_cny']:,.0f}"))
        A("")
    A("## How this page can be wrong")
    A("")
    for x in face["honest_limits"]:
        A("* " + x)
    A("")
    return "\n".join(L)


# ------------------------------------------------------------------ check
def check() -> int:
    """The parents moving is STALE (worth a re-run); this face contradicting them is not."""
    if not os.path.exists(OUT_JSON):
        print("CHECK face missing: %s does not exist" % os.path.relpath(OUT_JSON, ROOT))
        return 3
    try:
        face = load(OUT_JSON)
    except Exception as e:  # noqa: BLE001
        print("CHECK unreadable: %s" % e)
        return 2
    if face.get("status"):
        print("STALE: the published face carries status %r (%s)"
              % (face.get("status"), face.get("why")))
        return 3

    stale, probs = [], []
    for key, path in (("etf", ETF_TICKET), ("cb", CB_TICKET), ("blend", BLEND)):
        cur = stamp(path)
        old = (face.get("inputs", {}).get(key) or {}).get("stamp") or {}
        if cur is None:
            stale.append("STALE: %s is gone since this ticket priced it" % os.path.relpath(path, ROOT))
            continue
        if cur.get("bytes") != old.get("bytes") or cur.get("mtime") != old.get("mtime"):
            stale.append("STALE: %s changed since this ticket was written (%s -> %s bytes)"
                         % (os.path.relpath(path, ROOT), old.get("bytes"), cur.get("bytes")))
    if not os.path.exists(OUT_MD):
        probs.append("page missing")
    else:
        with open(OUT_MD, encoding="utf-8") as f:
            if f.read() != render_md(face):
                probs.append("page does not match this face's own render (hand-edited or stale)")

    if probs:
        print("CHECK FAILED:")   # no STALE word: this is a self-contradiction, not drift
        for x in probs:
            print("  -", x)
        return 1
    if stale:
        print("CHECK STALE:")
        for x in stale:
            print("  -", x)
        return 3
    print("CHECK OK: %d wallets on bar %s, first full hold at %s CNY"
          % (len(face.get("ladder") or []), face.get("evidence_cutoff"),
             f"{face.get('first_wallet_that_holds') or 0:,.0f}"))
    return 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    ok = fail = 0

    def want(cond, msg):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("  FAIL:", msg)

    # leg 1-2: whole 100-share lots, and the money identity (budget = lots + residual)
    picks = [{"symbol": "A", "weight": 0.25, "price_close": 2.0, "one_lot_cny": 200.0},
             {"symbol": "B", "weight": 0.25, "price_close": 4.0, "one_lot_cny": 400.0}]
    s = etf_sleeve(10_000.0, picks)
    want([l["lots"] for l in s["legs"]] == [12, 6], "lots %r != [12, 6]" % ([l["lots"] for l in s["legs"]],))
    want(abs(s["lot_residual_cny"] - (10_000 * 0.5 - s["invested_cny"])) < 0.011,
         "lot residual %.2f is not budget-minus-invested" % s["lot_residual_cny"])
    # weights sum to 0.5 -> half the sleeve is design cash, and it is NOT called strand
    want(abs(s["design_cash_cny"] - 5000.0) < 0.011, "design cash %.2f != 5000" % s["design_cash_cny"])

    # leg 3: the fee floor wins over 3bp of a small ticket
    s2 = etf_sleeve(100.0, [{"symbol": "A", "weight": 1.0, "price_close": 1.0, "one_lot_cny": 100.0}])
    want(abs(s2["legs"][0]["fee_cny"] - FEE_FLOOR) < 1e-9,
         "3bp of 100 is 0.03, the 5 CNY floor must win (%r)" % (s2["legs"][0]["fee_cny"],))

    # leg 4: a slice below one lot buys nothing and is flagged, not silently rounded up
    s3 = etf_sleeve(100.0, [{"symbol": "A", "weight": 0.5, "price_close": 10.0, "one_lot_cny": 1000.0}])
    want(s3["legs"][0]["lots"] == 0 and s3["legs"][0]["fits"] is False,
         "a 50 CNY slice of a 1000 CNY lot must buy 0 and be flagged unfit")

    # leg 5-7: verdict ladder
    base = {"wallet_cny": 1e6, "cash_pct": 0.2, "lot_grid_pct": 0.005,
            "etf": {"names": 5, "names_held": 5}, "cb": {"n": 20, "names_held": 20}}
    want(verdict_of(base) == "HOLDS_THE_BLEND", "full hold with small strand must be HOLDS_THE_BLEND")
    want(verdict_of({**base, "lot_grid_pct": 0.05}) == "HOLDS_WITH_STRAND",
         "5% grid cash must be HOLDS_WITH_STRAND")
    want(verdict_of({**base, "cb": {"n": 20, "names_held": 0}}) == "CB_SLEEVE_TOO_SMALL",
         "an empty CB sleeve has its own word")
    want(verdict_of({**base, "cb": {"n": 20, "names_held": 12}}) == "PARTIAL",
         "a thin CB sleeve is PARTIAL, not HOLDS")
    want(verdict_of({**base, "etf": {"names": 5, "names_held": 0}}) == "ETF_SLEEVE_TOO_SMALL",
         "an empty ETF sleeve has its own word")

    # leg 8: the minimum wallet is the CB rung divided by the sleeve weight (r1780 pattern)
    want(abs(min_wallet_cny(25_850.2, 0.30) - 86_167.33) < 0.02,
         "min wallet %.2f != 86,167.33" % min_wallet_cny(25_850.2, 0.30))

    # leg 9: the CB sleeve is the CB face's own arithmetic, not a copy
    import cb_book_ticket_floor as cb
    want(abs(cb_sleeve(30_000.0, [1000.0, 1500.0])["invested"]
             - cb.ticket_math([1000.0, 1500.0], 30_000.0)["invested"]) < 1e-9,
         "cb_sleeve drifted from cb_book_ticket_floor.ticket_math")

    # leg 10: two days cannot be one wallet -- the refusal guard itself
    want(bars_align("2026-11-26", "2026-11-26") is True, "same bar must align")
    want(bars_align("2026-11-20", "2026-11-26") is False,
         "an ETF sleeve six days older than the CB sleeve must be refused")
    want(bars_align(None, "2026-11-26") is False, "a missing bar must be refused, not aligned")

    # leg 11-13: the published floor rounds DOWN and silently drops one name; the ceiling holds.
    # Fixture mirrors production arithmetic (rung 25,850.20 / 0.30 = 86,167.33).
    four = [6462.55, 1000.0, 1000.0, 1000.0]          # rung = 6462.55 * 4 = 25,850.20
    pub, ceil_ = min_wallet_cny(25_850.20, 0.30), rung_wallet_ceil(25_850.20, 0.30)
    want(abs(pub - 86_167.33) < 0.01, "exact threshold %.2f != 86,167.33" % pub)
    want(ceil_ == 86_168, "ceiling %r != 86,168" % (ceil_,))
    want(cb_sleeve(86_167.0 * 0.30, four)["names_held"] == 3,
         "the blend's printed 86,167 must drop the dearest of four (%r held)"
         % (cb_sleeve(86_167.0 * 0.30, four)["names_held"],))
    want(cb_sleeve(ceil_ * 0.30, four)["names_held"] == 4,
         "86,168 must hold all four (%r held)" % (cb_sleeve(ceil_ * 0.30, four)["names_held"],))

    print(f"paired_book_ticket selftest {ok}/{ok + fail}", flush=True)
    return 0 if fail == 0 else 1


# ------------------------------------------------------------------ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()

    out = build()
    if out.get("status"):
        print("%s: %s" % (out["status"], out.get("why", "")))
        if out["status"] in ("SLEEVES_OFF_BY_DAYS", "no input"):
            # do not publish a wallet out of two different days; leave the old face alone
            return 3
        return 3
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT_JSON)
    tmp = OUT_MD + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(render_md(out))
    os.replace(tmp, OUT_MD)

    first = out.get("first_wallet_that_holds")
    print("bar %s | split %.0f/%.0f | ETF %s | CB %s"
          % (out["evidence_cutoff"], 100 * out["split"]["w_cb"], 100 * out["split"]["w_etf"],
             ",".join(out["inputs"]["etf"]["picks"]), ",".join(out["inputs"]["cb"]["picks"])))
    print("first wallet that holds both books: %s CNY"
          % (f"{first:,.0f}" if first else "none on this ladder"))
    for m in out["ladder"]:
        print("  %10s -> %-20s ETF %d/%d CB %d/%d invested %10s cash %5.1f%% (grid %4.1f%%)"
              % (f"{m['wallet_cny']:,.0f}", m["verdict"], m["etf_names_held"], m["etf_names"],
                 m["cb_names_held"], m["cb_names"], f"{m['invested_cny']:,.0f}",
                 100 * (m["cash_pct"] or 0), 100 * (m["lot_grid_pct"] or 0)))
    bad = [t for t in out["reconciliation"]["etf_tickets"] if not t["matches"]]
    print("reconciliation: ETF legs %s | min wallet matches blend: %s"
          % ("match" if not bad else "MISMATCH " + str(bad),
             out["reconciliation"]["min_wallet_matches_blend"]))
    fc = out.get("floor_check") or {}
    if fc and not fc.get("holds_at_published_floor"):
        print("FLOOR: the blend's %s CNY minimum holds only %d/%d CB names; %s CNY holds all %d "
              "(gap %.0f CNY)"
              % (f"{fc['published_min_wallet_cny']:,.0f}", fc["names_held_at_published"],
                 len(out["inputs"]["cb"]["picks"]), f"{fc['true_min_wallet_cny']:,.0f}",
                 fc["names_held_at_ceil"], fc["gap_cny"]))
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT))
    print("wrote %s" % os.path.relpath(OUT_MD, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
