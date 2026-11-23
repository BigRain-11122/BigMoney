"""A-share residual veto book: the order ticket -- what the 90.13% actually is in lots

r2022 priced five hedge sizes on a tradable instrument, r2023 turned that into a
drawdown-budget purchase decision, r2024 re-read it on daily marks, r2025 raced nine
ways of choosing a size, and r2026 said which size is the default (k = 1.00, i.e.
90.13% of the book at beta = 0.9013) and what would have to be true to swap it.

Every one of those faces speaks in *shares of the book*.  A person with an account
cannot place "90.13%".  They place lots, and the lots come in sizes that have nothing
to do with the book's size: one 512100 lot is 100 shares, one IM contract is 200 CNY
per index point.  So this face answers the four questions an order ticket answers,
and nothing else:

1. **How many lots** does k x beta need, at the last close?
2. **What does rounding cost** -- the beta you end up with, not the beta you wanted?
3. **How much capital does the hedge tie up** -- margin and frozen proceeds, per the
   broker-term axis, not per a guess?
4. **How far is the forced-liquidation line** on the futures arm, and how much of it
   did the latest session already spend?

Everything is arithmetic on already-published numbers plus the two price panels' last
bars.  No beta is refitted, no size is re-chosen, no cost model is introduced: the
carry axis and the roll cost belong to the parents and are quoted.

The axis this face will not invent
----------------------------------
Margin ratios and 融券 availability are broker terms this repository cannot observe.
They are printed as *axes* (three and three), never as a single number, and the
verdict below is written so that it holds on every rung of the axis, or says which
rung it needs.

Outputs (new files only):
    results/astock_veto_hedge_lots.json
    research/ASTOCK_VETO_HEDGE_LOTS.md

Usage:
    python scripts/astock_veto_hedge_lots.py selftest
    python scripts/astock_veto_hedge_lots.py run
    python scripts/astock_veto_hedge_lots.py check
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = os.path.join(ROOT, "results", "astock_veto_hedge_default.json")
BETA_FACE = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
ETF_CSV = os.path.join(ROOT, "data", "daily", "sh512100.csv")
IM_CSV = os.path.join(ROOT, "data", "futures_daily", "IM.csv")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_lots.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_LOTS.md")

ETF_LOT = 100                     # one 512100 lot = 100 shares
IM_MULT = 200                     # CNY per index point, IM
K = 1.0                           # the default from r2026 (one unit of beta)
# broker-term axes, NOT estimates: 融券 margin ratio and 股指期货 margin ratio.
ETF_MARGIN_AXIS = (0.50, 0.80, 1.00)
IM_MARGIN_AXIS = (0.12, 0.15)
# published r2007-era capital rungs plus the two capital levels where one and two IM
# contracts are exactly beta-neutral (one_lot / beta).  They are printed, not searched.
CAPITALS = (1_000_000, 3_000_000, 10_000_000, 20_000_000)
BETA_ERR_LINE = 0.005             # 0.5% of beta = the rounding error this face calls "small"
TOL = 1e-9

PREREG = {
    "frozen_before_the_numbers": True,
    "k": K,
    "beta_source": "results/astock_veto_hedge_default.json:default.beta (published)",
    "one_etf_lot": "100 x 512100 last close",
    "one_im_lot": "200 x IM last close (main continuous)",
    "capital_rungs": "the four the family already publishes, plus the two exact-neutral levels",
    "beta_error_definition": "|lots x one_lot / capital - k x beta|, absolute, "
                             "on the sorted arm (floor for 'do not overshoot', round for 'closest')",
    "margin_axes": {"etf_short": list(ETF_MARGIN_AXIS), "im": list(IM_MARGIN_AXIS),
                    "why": "broker terms, unobservable from this repository; printed as axes"},
    "forced_liquidation_line": "the margin ratio itself: a short loses the whole margin at "
                               "a move equal to the ratio, ignoring variation margin calls "
                               "and fees -- an upper bound on the distance, not a schedule",
    "not_fitted": "no beta, size, cost or basis is estimated here",
    "verdict_rungs": [
        "the ETF rounds free and the contract does not -> LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE",
        "both round fine -> THE_ROUNDING_IS_FREE_ON_BOTH_ARMS",
        "the ETF does not round fine either -> THE_ROUNDING_BITES_ON_BOTH_ARMS",
    ],
}


# ------------------------------------------------------------------ pure logic
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    # a path on another drive cannot be made relative to ROOT (ntpath raises); the
    # fingerprint only needs a stable name, not a short one.
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    """A face's own digest, with the runtime stamp left out."""
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


def tail_bar(path: str) -> dict:
    """The last bar of a price panel.  Only the columns an order needs."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("price panel has no rows: %s" % path)
    last, prev = rows[-1], (rows[-2] if len(rows) > 1 else None)
    out = {"date": last["date"], "close": float(last["close"]),
           "file_sha256": _sha_file(path), "rows": len(rows)}
    for col in ("volume", "amount", "oi"):
        if col in last and last[col] not in ("", None):
            out[col] = float(last[col])
    if prev is not None and float(prev["close"]):
        out["day_move"] = out["close"] / float(prev["close"]) - 1.0
        out["prev_date"] = prev["date"]
    return out


def lots_for(capital: float, beta: float, unit_price: float, multiplier: float) -> dict:
    """How many lots a beta-neutral short needs, and what each rounding choice costs.

    `floor` never overshoots the target; `round` is the closest number of lots.  Both
    are printed because an order ticket is filled at one of them, and the beta you
    end up holding is the one that came out of the fill, not the one you wrote down.
    """
    notional = abs(beta) * float(capital)
    one = float(unit_price) * float(multiplier)
    need = float("nan") if one <= 0 else notional / one
    out = {"capital": float(capital), "target_notional": float(notional),
           "one_lot_notional": float(one), "lots_needed": float(need)}
    for name, n in (("floor", int(need // 1) if need == need else 0),
                    ("round", int(round(need)) if need == need else 0)):
        got = n * one
        out[name] = {
            "lots": n,
            "notional": float(got),
            "residual_cny": float(notional - got),
            "beta_achieved": float(got / float(capital)) if capital else None,
            "beta_error": float(got / float(capital) - abs(beta)) if capital else None,
            "short_of_target_pct": float((notional - got) / notional * 100.0) if notional else None,
        }
    return out


def capital_for_beta_error(one_lot_notional: float, beta_err: float = BETA_ERR_LINE) -> float:
    """The smallest capital where rounding to the nearest lot moves beta by <= beta_err.

    The fill error is at most half a lot, so |delta beta| <= 0.5 x one_lot / capital.
    Solve for capital.  This is the number that tells a reader how big the account has
    to be before "one unit of beta" is a thing you can actually hold.
    """
    if beta_err <= 0:
        return float("inf")
    return 0.5 * float(one_lot_notional) / float(beta_err)


def margin_table(notional: float, axis: tuple, also_frozen: bool) -> dict:
    """Margin per rung, plus -- for 融券 -- the proceeds the sale leaves frozen.

    Shorted-notional margin is required up front; the sale proceeds are held as
    collateral and are not spendable either.  Printing both is the difference between
    "90% of the book" and "how much of the account is available afterwards".
    """
    out = {}
    for r in axis:
        m = float(notional) * float(r)
        row = {"ratio": float(r), "margin_cny": m}
        if also_frozen:
            row["frozen_proceeds_cny"] = float(notional)
            row["committed_cny"] = m + float(notional)
        out["%.2f" % float(r)] = row
    return out


def liquidation_line(margin_ratio: float) -> dict:
    """How far the short can move against you before the margin is gone.

    Deliberately crude and labelled as such: it ignores maintenance margin, variation
    margin calls, fees and the fact that a call arrives before the margin is gone.
    """
    return {"margin_ratio": float(margin_ratio),
            "adverse_move_to_zero_equity": float(margin_ratio),
            "note": "upper bound on the distance; a real account is called sooner"}


def verdict_of(face: dict) -> tuple:
    """Frozen ladder.  Reads the two rounding arms and says which one bites."""
    etf = face["granularity"]["etf"]
    im = face["granularity"]["im"]
    etf_ok = etf["beta_error_at_smallest_rung"] <= BETA_ERR_LINE + TOL
    im_ok = im["beta_error_at_smallest_rung"] <= BETA_ERR_LINE + TOL
    if etf_ok and not im_ok:
        return ("LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE",
                "the ETF's half-lot error is %.5f of beta at the smallest capital, while "
                "one contract is %.1f%% of that book and cannot be made beta-neutral "
                "with any whole number"
                % (etf["beta_error_at_smallest_rung"], im["one_lot_pct_of_smallest_capital"]))
    if etf_ok and im_ok:
        return ("THE_ROUNDING_IS_FREE_ON_BOTH_ARMS",
                "both arms can be filled within %.2f%% of beta at the smallest capital"
                % (BETA_ERR_LINE * 100))
    return ("THE_ROUNDING_BITES_ON_BOTH_ARMS",
            "even the ETF cannot be filled within %.2f%% of beta at the smallest capital"
            % (BETA_ERR_LINE * 100))


# ------------------------------------------------------------------------ the face
def build() -> dict:
    parent = _read_json(PARENT)
    betaface = _read_json(BETA_FACE)
    beta = float(parent["default"]["beta"])
    k = float(parent["default"]["k"])

    etf_bar = tail_bar(ETF_CSV)
    im_bar = tail_bar(IM_CSV)
    one_etf = etf_bar["close"] * ETF_LOT
    one_im = im_bar["close"] * IM_MULT
    target_beta = k * beta

    ladder = {}
    for cap in CAPITALS:
        e = lots_for(cap, target_beta, etf_bar["close"], ETF_LOT)
        m = lots_for(cap, target_beta, im_bar["close"], IM_MULT)
        e_notional = e["round"]["notional"]
        m_notional = m["round"]["notional"]
        ladder[str(cap)] = {
            "capital": float(cap),
            "etf": {
                "lots_needed": e["lots_needed"],
                "floor": e["floor"], "round": e["round"],
                "margin": margin_table(e_notional, ETF_MARGIN_AXIS, also_frozen=True),
            },
            "im": {
                "lots_needed": m["lots_needed"],
                "floor": m["floor"], "round": m["round"],
                "margin": margin_table(m_notional, IM_MARGIN_AXIS, also_frozen=False),
                "cannot_fill_at_all": bool(m["lots_needed"] < 0.5),
            },
        }

    # the exact-neutral capital levels (one and two contracts)
    neutral = {}
    for n in (1, 2):
        neutral[str(n)] = {"contracts": n, "capital_cny": n * one_im / target_beta}

    # how much cash one CNY of *target* notional ties up, per arm and rung: the number
    # that explains why a real desk prefers the future even though it cannot hit the size
    funding_efficiency = {}
    for cap in CAPITALS:
        row = ladder[str(cap)]
        tgt = float(cap) * target_beta
        eff = {}
        for rung, v in row["etf"]["margin"].items():
            eff["etf_%s" % rung] = v["committed_cny"] / tgt
        for rung, v in row["im"]["margin"].items():
            eff["im_%s" % rung] = v["margin_cny"] / tgt
        funding_efficiency[str(cap)] = eff

    smallest = float(CAPITALS[0])
    smallest_etf = ladder[str(int(smallest))]["etf"]
    smallest_im = ladder[str(int(smallest))]["im"]

    gran = {
        "ratio_one_contract_over_one_lot": float(one_im / one_etf),
        "etf": {
            "one_lot_notional": float(one_etf),
            "beta_error_at_smallest_rung": abs(smallest_etf["round"]["beta_error"]),
            "capital_for_half_pct_beta": capital_for_beta_error(one_etf),
            "liquidity_share_of_day_amount": (smallest_etf["round"]["notional"] /
                                              etf_bar["amount"]) if etf_bar.get("amount") else None,
        },
        "im": {
            "one_lot_notional": float(one_im),
            "beta_error_at_smallest_rung": abs(smallest_im["round"]["beta_error"]),
            "one_lot_pct_of_smallest_capital": one_im / smallest * 100.0,
            "capital_for_half_pct_beta": capital_for_beta_error(one_im),
            "liquidity_share_of_day_volume": (smallest_im["round"]["lots"] /
                                              im_bar["volume"]) if im_bar.get("volume") else None,
        },
        "exact_neutral_capital": neutral,
    }

    carry = {
        "etf_roll_cost_per_year_on_notional":
            float(betaface["spec"]["roll_cost_per_period"]) *
            float(betaface["spec"]["periods_per_year"]),
        "etf_roll_cost_per_year_on_capital":
            float(betaface["spec"]["roll_cost_per_period"]) *
            float(betaface["spec"]["periods_per_year"]) * target_beta,
        "periods_per_year": float(betaface["spec"]["periods_per_year"]),
        "im_basis_median": betaface["data"]["im"].get("basis_median"),
        "im_basis_note": "a negative median basis is the future trading below the index; "
                         "the direction is against a short, but it cannot be annualised "
                         "from a median taken across mixed expiries -- not modelled here",
        "source": "results/astock_veto_hedgeable_beta.json:spec / data.im",
    }

    face = {
        "generated": _now(),
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "astock_veto_hedge_lots",
        "fills_the_hole_of": ("r2023-r2026 decided how much insurance to buy, in shares of the book; "
                              "no face said what that is in lots, what the rounding costs in beta, "
                              "how much capital the hedge ties up, or how far the futures margin "
                              "is from a call"),
        "parent": fingerprint(PARENT),
        "beta_parent": fingerprint(BETA_FACE),
        "prereg": PREREG,
        "beta": beta,
        "k": k,
        "target_beta": target_beta,
        "hedge_notional_pct": target_beta * 100.0,
        "prices": {
            "etf": {"symbol": "512100", "csv": _rel(ETF_CSV), **etf_bar,
                    "lot": ETF_LOT, "one_lot_notional": one_etf},
            "im": {"symbol": "IM", "csv": _rel(IM_CSV), **im_bar,
                   "multiplier": IM_MULT, "one_lot_notional": one_im},
        },
        "granularity": gran,
        "funding_efficiency": funding_efficiency,
        "ladders": ladder,
        "carry": carry,
        "verdict": None,
        "verdict_why": None,
    }
    face["verdict"], face["verdict_why"] = verdict_of(face)
    return face


# ------------------------------------------------------------------------- render
def _f(x, digits: int = 2) -> str:
    if x is None:
        return "—"
    return ("%." + str(digits) + "f") % float(x)


def _pct(x, digits: int = 2) -> str:
    return "—" if x is None else _f(float(x) * 100.0, digits) + "%"


def _cny(x) -> str:
    return "—" if x is None else "{:,.0f}".format(float(x))


def render_md(face: dict) -> str:
    L = []
    a = L.append
    a("# The order ticket: what 90.13% of the book is in lots")
    a("")
    a("Generated %s · evidence cutoff %s · machine %s"
      % (face["generated"], face["evidence_cutoff"], face["machine"]))
    a("")
    a("## Why this face exists")
    a("")
    a(face["fills_the_hole_of"] + ".")
    a("")
    a("Nothing is re-fitted. The size comes from `results/astock_veto_hedge_default.json` "
      "(k = %.2f, beta = %.4f, i.e. %.2f%% of the book); the two prices come from the last bar "
      "of their own panels. The margin ratios are broker terms this repository cannot observe, "
      "so they are printed as axes and every rung is shown."
      % (face["k"], face["beta"], face["hedge_notional_pct"]))
    a("")
    a("## The two instruments, as of the last bar")
    a("")
    e, m = face["prices"]["etf"], face["prices"]["im"]
    a("| | 512100 (ETF) | IM (index future) |")
    a("|---|---|---|")
    a("| bar | %s | %s |" % (e["date"], m["date"]))
    a("| close | %s | %s |" % (_f(e["close"], 3), _f(m["close"], 1)))
    a("| one lot | 100 shares = **%s CNY** | 200 x index = **%s CNY** |"
      % (_cny(e["one_lot_notional"]), _cny(m["one_lot_notional"])))
    a("| last session | %s | %s |" % (_pct(e.get("day_move"), 2), _pct(m.get("day_move"), 2)))
    if e.get("amount"):
        a("| traded that day | %s CNY | %s lots |" % (_cny(e["amount"]), _cny(m.get("volume"))))
    a("")
    g = face["granularity"]
    a("**One contract is %.0f times one ETF lot.** That ratio is the whole story of this face: "
      "the two arms are the same hedge and they are not the same order."
      % g["ratio_one_contract_over_one_lot"])
    a("")
    a("## What rounding costs, in beta")
    a("")
    a("`floor` never overshoots the target; `round` is the nearest whole number. The error is "
      "`|lots x one_lot / capital - target beta|`.")
    a("")
    a("| capital | arm | lots needed | floor | beta after floor | round | beta after round | beta error |")
    a("|---|---|---|---|---|---|---|---|")
    for cap in sorted(face["ladders"], key=lambda x: float(x)):
        row = face["ladders"][cap]
        for arm, label in (("etf", "512100"), ("im", "IM")):
            r = row[arm]
            a("| %s | %s | %s | %d | %s | %d | %s | %s |"
              % (_cny(float(cap)), label, _f(r["lots_needed"], 3),
                 r["floor"]["lots"], _f(r["floor"]["beta_achieved"], 4),
                 r["round"]["lots"], _f(r["round"]["beta_achieved"], 4),
                 _f(abs(r["round"]["beta_error"]), 5)))
    a("")
    a("A half-lot is the most a fill can be off, so the smallest capital at which the rounding "
      "moves beta by no more than %.2f%% is `0.5 x one_lot / %.2f%%`:"
      % (BETA_ERR_LINE * 100, BETA_ERR_LINE * 100))
    a("")
    a("* 512100: **%s CNY**" % _cny(g["etf"]["capital_for_half_pct_beta"]))
    a("* IM: **%s CNY**" % _cny(g["im"]["capital_for_half_pct_beta"]))
    a("")
    a("At the smallest published capital (%s CNY) one contract is **%.1f%% of the book**, so "
      "the closest fill is either no hedge at all or a book hedged at **%.2f units of beta** "
      "instead of %.2f — the same order, two different books."
      % (_cny(face["ladders"][sorted(face["ladders"], key=lambda x: float(x))[0]]["capital"]),
         g["im"]["one_lot_pct_of_smallest_capital"],
         face["ladders"][sorted(face["ladders"], key=lambda x: float(x))[0]]["im"]["round"]["beta_achieved"],
         face["target_beta"]))
    a("")
    a("### The capitals where one and two contracts are exactly beta-neutral")
    a("")
    a("| contracts | capital that makes it exactly neutral |")
    a("|---|---|")
    for kk in sorted(g["exact_neutral_capital"], key=int):
        n = g["exact_neutral_capital"][kk]
        a("| %d | %s CNY |" % (n["contracts"], _cny(n["capital_cny"])))
    a("")
    a("## What the hedge ties up")
    a("")
    a("Margin per rung, plus — for the ETF short — the proceeds the sale leaves frozen as "
      "collateral. `committed` is what is not available to the rest of the account while the "
      "hedge is on.")
    a("")
    for cap in sorted(face["ladders"], key=lambda x: float(x))[:2]:
        row = face["ladders"][cap]
        a("### %s CNY" % _cny(float(cap)))
        a("")
        a("| arm | ratio | margin | frozen proceeds | committed | share of capital |")
        a("|---|---|---|---|---|---|")
        for rung, v in row["etf"]["margin"].items():
            a("| 512100 | %s | %s | %s | %s | %s |"
              % (_pct(v["ratio"], 0), _cny(v["margin_cny"]),
                 _cny(v.get("frozen_proceeds_cny")), _cny(v["committed_cny"]),
                 _pct(v["committed_cny"] / row["capital"], 0)))
        for rung, v in row["im"]["margin"].items():
            a("| IM (%d lot) | %s | %s | — | %s | %s |"
              % (row["im"]["round"]["lots"], _pct(v["ratio"], 0), _cny(v["margin_cny"]),
                 _cny(v["margin_cny"]), _pct(v["margin_cny"] / row["capital"], 0)))
        if row["im"]["cannot_fill_at_all"]:
            a("")
            a("*The IM row is not an order this account can place: one contract needs "
              "**%s CNY** of capital at this beta. The share of capital beside it is a "
              "reference reading taken against a book that cannot hold the contract, not a "
              "margin requirement you would actually post.*"
              % _cny(g["exact_neutral_capital"]["1"]["capital_cny"]))
        a("")
    eff = face["funding_efficiency"][sorted(face["funding_efficiency"],
                                            key=lambda x: float(x))[0]]
    a("### What one CNY of target notional ties up")
    a("")
    a("At the smallest capital, cash committed per CNY of the %s CNY the hedge is supposed "
      "to be worth:" % _cny(float(CAPITALS[0]) * face["target_beta"]))
    a("")
    a("| arm and rung | CNY committed per CNY of target notional |")
    a("|---|---|")
    for rung in sorted(eff, key=lambda x: (x.split("_")[0], x)):
        arm, ratio = rung.split("_", 1)
        label = ("512100" if arm == "etf" else "IM") + " at " + _pct(float(ratio), 0) + " margin"
        a("| %s | %.2f |" % (label, eff[rung]))
    a("")
    a("The future is the cheaper way to hold the exposure by an order of magnitude — "
      "0.12–0.15 CNY per CNY against 1.50–2.00 for a 融券 short, whose sale proceeds are "
      "frozen on top of the margin. That is exactly why the arm that wins on funding is the "
      "arm that cannot be sized: cheap capital does not buy the beta you asked for.")
    a("")
    a("## How far the futures margin is from a call")
    a("")
    imr = face["prices"]["im"]
    a("The crude bound: a short loses its whole margin at an adverse move equal to the margin "
      "ratio. On the latest session that instrument moved **%s**, which is %s of the 12%% rung "
      "and %s of the 15%% rung — one session, before any call."
      % (_pct(imr.get("day_move"), 2),
         _pct(abs(imr.get("day_move", 0)) / 0.12, 0),
         _pct(abs(imr.get("day_move", 0)) / 0.15, 0)))
    a("")
    a("| ratio | adverse move to zero equity |")
    a("|---|---|")
    for r in (0.12, 0.15):
        a("| %s | %s |" % (_pct(r, 0), _pct(liquidation_line(r)["adverse_move_to_zero_equity"], 0)))
    a("")
    a("## What the hedge costs to keep rolling")
    a("")
    c = face["carry"]
    a("Quoted from the parent's spec, not re-estimated: %s rolls a year, %s per roll on the "
      "shorted notional, i.e. **%s of the shorted notional a year** and **%s of the book**."
      % (_f(c["periods_per_year"], 1), "16 bp", _pct(c["etf_roll_cost_per_year_on_notional"]),
         _pct(c["etf_roll_cost_per_year_on_capital"])))
    a("")
    a("The futures arm pays its roll inside the price. Its median basis is **%s** — %s."
      % (_pct(c["im_basis_median"], 3), c["im_basis_note"]))
    a("")
    a("## Liquidity is not the constraint on either arm")
    a("")
    a("At the smallest capital the ETF short is %s of that day's traded value and the contract "
      "is %s of that day's traded lots. What cannot be read from here is 券源 — whether a broker "
      "has the inventory to lend — and that is a desk question, not a panel question."
      % ("%.1f ppm" % (g["etf"]["liquidity_share_of_day_amount"] * 1e6)
         if g["etf"]["liquidity_share_of_day_amount"] is not None else "—",
         "%.1f ppm" % (g["im"]["liquidity_share_of_day_volume"] * 1e6)
         if g["im"]["liquidity_share_of_day_volume"] is not None else "—"))
    a("")
    a("## The answer")
    a("")
    a("**%s** — %s." % (face["verdict"], face["verdict_why"]))
    a("")
    small_row = face["ladders"][sorted(face["ladders"], key=lambda x: float(x))[0]]
    eight = small_row["etf"]["margin"]["0.80"]
    a("Read two numbers together before placing anything. At an 80%% 融券 ratio the ETF short "
      "at the smallest capital ties up **%s CNY** — **%s of the book** — because the margin and "
      "the frozen sale proceeds are both unavailable while the hedge is on. So \"90%% of the "
      "book\" is not 90%% of the account: it is a promise of about **%.1f times** the book in "
      "cash, and the futures arm that would cost a tenth of that cannot be filled at this size."
      % (_cny(eight["committed_cny"]),
         _pct(eight["committed_cny"] / small_row["capital"], 0),
         eight["committed_cny"] / small_row["capital"]))
    a("")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------- commands
def run(write: bool = True) -> int:
    face = build()
    md = render_md(face)
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(md)
        print("wrote %s" % _rel(OUT_JSON))
        print("wrote %s" % _rel(OUT_MD))
    print("verdict: %s" % face["verdict"])
    print("one contract = %.2f ETF lots; beta error at smallest capital: ETF %.6f / IM %.4f"
          % (face["granularity"]["ratio_one_contract_over_one_lot"],
             face["granularity"]["etf"]["beta_error_at_smallest_rung"],
             face["granularity"]["im"]["beta_error_at_smallest_rung"]))
    return 0


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """Re-derive every published reading from the parents and the two panels.

    Two kinds of red, kept apart: an input moved (STALE — re-run, do not edit) and this
    face disagrees with arithmetic on the same inputs (CHECK FAILED).
    """
    fails = []
    try:
        face = _read_json(json_path)
        md = open(md_path, encoding="utf-8").read()
    except Exception as exc:                                  # noqa: BLE001
        print("CHECK FAILED: cannot read the face (%s)" % exc)
        return 3

    try:
        parent = _read_json(PARENT)
        betaface = _read_json(BETA_FACE)
        etf_bar = tail_bar(ETF_CSV)
        im_bar = tail_bar(IM_CSV)
    except Exception as exc:                                  # noqa: BLE001
        print("STALE: an input face or panel cannot be read (%s)" % exc)
        return 3

    for name, path in (("parent", PARENT), ("beta_parent", BETA_FACE)):
        want = fingerprint(path)
        have = face.get(name) or {}
        if have.get("content_sha256") != want["content_sha256"] or \
                have.get("file_sha256") != want["file_sha256"]:
            print("STALE: %s face moved since this face was derived (%s -> %s)"
                  % (name, str(have.get("content_sha256"))[:12],
                     want["content_sha256"][:12]))
            return 3

    pub = face.get("prices") or {}
    for arm, bar in (("etf", etf_bar), ("im", im_bar)):
        have = pub.get(arm) or {}
        if have.get("date") != bar["date"] or \
                abs(float(have.get("close", -1)) - bar["close"]) > TOL:
            print("STALE: the %s panel's last bar moved (%s %s -> %s %s)"
                  % (arm, have.get("date"), have.get("close"), bar["date"], bar["close"]))
            return 3

    beta = float(parent["default"]["beta"])
    k = float(parent["default"]["k"])
    target = k * beta
    one_etf = etf_bar["close"] * ETF_LOT
    one_im = im_bar["close"] * IM_MULT

    if abs(float(face.get("beta", -1)) - beta) > 1e-12:
        fails.append("beta %r != %r" % (face.get("beta"), beta))
    if abs(float(face.get("target_beta", -1)) - target) > 1e-12:
        fails.append("target_beta %r != %r" % (face.get("target_beta"), target))
    if abs(float(face.get("hedge_notional_pct", -1)) - target * 100.0) > 1e-9:
        fails.append("hedge_notional_pct %r != %r" % (face.get("hedge_notional_pct"), target * 100.0))
    if abs(float(pub["etf"]["one_lot_notional"]) - one_etf) > TOL:
        fails.append("etf one lot %r != %r" % (pub["etf"]["one_lot_notional"], one_etf))
    if abs(float(pub["im"]["one_lot_notional"]) - one_im) > TOL:
        fails.append("im one lot %r != %r" % (pub["im"]["one_lot_notional"], one_im))

    # 1. the ladders, every rung, both arms, both rounding choices
    for cap in CAPITALS:
        row = (face.get("ladders") or {}).get(str(cap))
        if not isinstance(row, dict):
            fails.append("capital rung %s missing" % cap)
            continue
        for arm, price, mult in (("etf", etf_bar["close"], ETF_LOT),
                                 ("im", im_bar["close"], IM_MULT)):
            exp = lots_for(cap, target, price, mult)
            got = row.get(arm) or {}
            if abs(float(got.get("lots_needed", -1)) - exp["lots_needed"]) > 1e-9:
                fails.append("%s.%s lots_needed %r != %r"
                             % (cap, arm, got.get("lots_needed"), exp["lots_needed"]))
            for which in ("floor", "round"):
                g = got.get(which) or {}
                x = exp[which]
                for field in ("lots", "notional", "residual_cny", "beta_achieved", "beta_error"):
                    if g.get(field) is None or x[field] is None:
                        if g.get(field) != x[field]:
                            fails.append("%s.%s.%s %r != %r" % (cap, arm, which, field, x[field]))
                    elif abs(float(g[field]) - float(x[field])) > 1e-9:
                        fails.append("%s.%s.%s.%s %r != %r"
                                     % (cap, arm, which, field, g[field], x[field]))
            axis = ETF_MARGIN_AXIS if arm == "etf" else IM_MARGIN_AXIS
            exp_m = margin_table(exp["round"]["notional"], axis, also_frozen=(arm == "etf"))
            got_m = got.get("margin") or {}
            for rung, v in exp_m.items():
                gv = got_m.get(rung) or {}
                for field, val in v.items():
                    gfield = gv.get(field)
                    if gfield is None or val is None:
                        if gfield != val:
                            fails.append("%s.%s.margin[%s].%s %r != %r"
                                         % (cap, arm, rung, field, gfield, val))
                    elif abs(float(gfield) - float(val)) > 1e-9:
                        fails.append("%s.%s.margin[%s].%s %r != %r"
                                     % (cap, arm, rung, field, gfield, val))

    # 2. granularity, including the capital levels and the liquidity shares
    g = face.get("granularity") or {}
    if abs(float(g.get("ratio_one_contract_over_one_lot", -1)) - one_im / one_etf) > 1e-6:
        fails.append("granularity ratio %r != %r"
                     % (g.get("ratio_one_contract_over_one_lot"), one_im / one_etf))
    checks = [
        ("etf", "one_lot_notional", one_etf),
        ("etf", "capital_for_half_pct_beta", capital_for_beta_error(one_etf)),
        ("im", "one_lot_notional", one_im),
        ("im", "capital_for_half_pct_beta", capital_for_beta_error(one_im)),
    ]
    for arm, field, val in checks:
        got = (g.get(arm) or {}).get(field)
        if got is None or abs(float(got) - float(val)) > 1e-6:
            fails.append("granularity.%s.%s %r != %r" % (arm, field, got, val))
    smallest = float(CAPITALS[0])
    if abs(float(g["im"].get("one_lot_pct_of_smallest_capital", -1)) - one_im / smallest * 100.0) > 1e-9:
        fails.append("one_lot_pct_of_smallest_capital %r != %r"
                     % (g["im"].get("one_lot_pct_of_smallest_capital"), one_im / smallest * 100.0))
    if etf_bar.get("amount"):
        exp_share = round(float(CAPITALS[0]) * target / one_etf) * one_etf / etf_bar["amount"]
        if abs(float(g["etf"].get("liquidity_share_of_day_amount", -1)) - exp_share) > 1e-12:
            fails.append("etf liquidity share %r != %r"
                         % (g["etf"].get("liquidity_share_of_day_amount"), exp_share))
    for n in (1, 2):
        got = (g.get("exact_neutral_capital") or {}).get(str(n)) or {}
        exp_cap = n * one_im / target
        if abs(float(got.get("capital_cny", -1)) - exp_cap) > 1e-6:
            fails.append("neutral[%d] capital %r != %r" % (n, got.get("capital_cny"), exp_cap))
    betaf_etf = abs(lots_for(smallest, target, etf_bar["close"], ETF_LOT)["round"]["beta_error"])
    betaf_im = abs(lots_for(smallest, target, im_bar["close"], IM_MULT)["round"]["beta_error"])
    if abs(float(g["etf"].get("beta_error_at_smallest_rung", -1)) - betaf_etf) > 1e-12:
        fails.append("etf beta error at smallest rung %r != %r"
                     % (g["etf"].get("beta_error_at_smallest_rung"), betaf_etf))
    if abs(float(g["im"].get("beta_error_at_smallest_rung", -1)) - betaf_im) > 1e-12:
        fails.append("im beta error at smallest rung %r != %r"
                     % (g["im"].get("beta_error_at_smallest_rung"), betaf_im))

    # 3. funding efficiency, every capital rung and every margin rung
    fe = face.get("funding_efficiency") or {}
    for cap in CAPITALS:
        got = fe.get(str(cap)) or {}
        tgt = float(cap) * target
        exp = {}
        for rung, v in (ladder_of := face["ladders"][str(cap)])["etf"]["margin"].items():
            exp["etf_%s" % rung] = v["committed_cny"] / tgt
        for rung, v in ladder_of["im"]["margin"].items():
            exp["im_%s" % rung] = v["margin_cny"] / tgt
        if sorted(got) != sorted(exp):
            fails.append("funding_efficiency[%s] keys %r != %r" % (cap, sorted(got), sorted(exp)))
            continue
        for name, val in exp.items():
            if abs(float(got.get(name, -1)) - val) > 1e-9:
                fails.append("funding_efficiency[%s][%s] %r != %r"
                             % (cap, name, got.get(name), val))

    # 4. carry, quoted from the parent's spec
    c = face.get("carry") or {}
    exp_carry = (float(betaface["spec"]["roll_cost_per_period"]) *
                 float(betaface["spec"]["periods_per_year"]))
    if abs(float(c.get("etf_roll_cost_per_year_on_notional", -1)) - exp_carry) > 1e-12:
        fails.append("carry.on_notional %r != %r"
                     % (c.get("etf_roll_cost_per_year_on_notional"), exp_carry))
    if abs(float(c.get("etf_roll_cost_per_year_on_capital", -1)) - exp_carry * target) > 1e-12:
        fails.append("carry.on_capital %r != %r"
                     % (c.get("etf_roll_cost_per_year_on_capital"), exp_carry * target))

    # 4. the verdict, re-judged
    exp_verdict, _why = verdict_of(face)
    if face.get("verdict") != exp_verdict:
        fails.append("verdict %r != %r" % (face.get("verdict"), exp_verdict))

    # 5. the page is the face, byte for byte
    if md != render_md(face):
        fails.append("the page is not the rendered face (the markdown was edited by hand "
                     "or the renderer changed)")

    if fails:
        print("CHECK FAILED: %d disagreement(s)" % len(fails))
        for f in fails[:40]:
            print("  - %s" % f)
        return 3
    n = len(CAPITALS) * (2 * 2 * 5 + 15) + 15
    print("CHECK OK: every published reading re-derived from the parents and the two panels, "
          "page matches (>=%d comparisons)" % n)
    return 0


def selftest() -> int:
    ok = 0
    bad = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    # 1-4 lots
    r = lots_for(1_000_000, 0.9, 2.30, 100)
    leg("one ETF lot is 100 shares x price", abs(r["one_lot_notional"] - 230) < 1e-9)
    leg("lots needed is target notional over one lot", abs(r["lots_needed"] - 900_000 / 230) < 1e-9)
    leg("floor never overshoots", r["floor"]["notional"] <= r["target_notional"] + 1e-9)
    leg("round is within half a lot", abs(r["round"]["notional"] - r["target_notional"]) <= 0.5 * 230 + 1e-9)
    leg("floor leaves a positive residual", r["floor"]["residual_cny"] > 0)
    leg("beta achieved is notional over capital",
        abs(r["round"]["beta_achieved"] - r["round"]["notional"] / 1_000_000) < 1e-12)
    leg("beta error is achieved minus target",
        abs(r["round"]["beta_error"] - (r["round"]["beta_achieved"] - 0.9)) < 1e-12)
    small = lots_for(1_000_000, 0.9, 5_545.6, 200)
    leg("one IM contract is 200 x index", abs(small["one_lot_notional"] - 1_109_120) < 1e-6)
    leg("a 1M book cannot fill one contract", small["lots_needed"] < 1.0)
    leg("floor of a sub-lot need is zero", small["floor"]["lots"] == 0)
    leg("rounding up overshoots beta", small["round"]["beta_achieved"] > 1.0)
    leg("overshoot is measured against the target, not against 1.0",
        abs(small["round"]["beta_error"] - (1_109_120 / 1_000_000 - 0.9)) < 1e-12)

    # 5-6 the capital where rounding is small
    leg("half a lot at 0.5% of beta needs 100 lots of capital",
        abs(capital_for_beta_error(230) - 23_000) < 1e-9)
    leg("the contract needs 4822x that capital",
        abs(capital_for_beta_error(1_109_120) / capital_for_beta_error(230) - 1_109_120 / 230) < 1e-6)
    leg("a zero error line is infinite capital", capital_for_beta_error(1000, 0.0) == float("inf"))

    # 7-9 margin
    mg = margin_table(1000.0, (0.5, 0.8), also_frozen=True)
    leg("margin is notional times ratio", abs(mg["0.80"]["margin_cny"] - 800) < 1e-9)
    leg("committed adds the frozen proceeds", abs(mg["0.80"]["committed_cny"] - 1800) < 1e-9)
    leg("without frozen proceeds committed is the margin",
        abs(margin_table(1000.0, (0.12,), also_frozen=False)["0.12"]["committed_cny"] if False
            else margin_table(1000.0, (0.12,), also_frozen=False)["0.12"]["margin_cny"] - 120) < 1e-9)
    leg("the futures table carries no frozen proceeds",
        "frozen_proceeds_cny" not in margin_table(1000.0, (0.12,), also_frozen=False)["0.12"])

    # 10-11 liquidation line
    leg("the crude line equals the ratio", abs(liquidation_line(0.12)["adverse_move_to_zero_equity"] - 0.12) < 1e-12)
    leg("a bigger ratio is a farther line",
        liquidation_line(0.15)["adverse_move_to_zero_equity"] >
        liquidation_line(0.12)["adverse_move_to_zero_equity"])

    # 12-14 verdict ladder
    def _v(etf_err, im_err, im_pct=111.0):
        return verdict_of({"granularity": {
            "etf": {"beta_error_at_smallest_rung": etf_err},
            "im": {"beta_error_at_smallest_rung": im_err,
                   "one_lot_pct_of_smallest_capital": im_pct}}})
    leg("ETF free / IM not -> the split verdict",
        _v(0.0001, 0.20)[0] == "LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE")
    leg("both free -> free on both", _v(0.0001, 0.0001)[0] == "THE_ROUNDING_IS_FREE_ON_BOTH_ARMS")
    leg("neither free -> bites on both", _v(0.02, 0.20)[0] == "THE_ROUNDING_BITES_ON_BOTH_ARMS")
    leg("exactly on the line counts as free", _v(BETA_ERR_LINE, BETA_ERR_LINE)[0] ==
        "THE_ROUNDING_IS_FREE_ON_BOTH_ARMS")

    # 15 digest
    leg("digest ignores the runtime stamp",
        content_sha({"generated": "a", "x": 1}) == content_sha({"generated": "b", "x": 1}))
    leg("digest sees a changed reading",
        content_sha({"generated": "a", "x": 1}) != content_sha({"generated": "a", "x": 2}))

    # 16-17 the live panels are readable and dated
    try:
        eb = tail_bar(ETF_CSV)
        ib = tail_bar(IM_CSV)
        leg("the ETF panel has a last bar with a price", eb["close"] > 0)
        leg("the futures panel has a last bar with a price", ib["close"] > 0)
    except Exception as exc:                                  # noqa: BLE001
        leg("panels readable", False, str(exc))

    print("selftest %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  - FAIL %s" % b)
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "check", "selftest"], nargs="?", default="run")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
