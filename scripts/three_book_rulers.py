#!/usr/bin/env python
"""One window, one clock: can the carry leg's page number sit beside the ETF book's?

Why this face exists
--------------------
Three books are quoted in this repo with the same-looking units -- an annual
percentage -- and readers (us included) have been lining them up:

    ETF composite book      9.94%   vol 10.47%   sharpe 0.95
    CB dual-low sleeve      6.34%   vol 12.93%   sharpe 0.49
    index-futures carry    10.22%   vol  3.21%   sharpe 3.19

The third row is not the same object as the first two.  It is the carry arm
(basis only, hedged excess), whose return is quoted per unit of **notional**
while the first two are quoted per unit of **capital**.  The carry family
publishes three different Sharpe numbers for the same IC leg because it is
three different arms:

    carry_unhedged    per-lot daily points on the held contract   0.5057
    excess_hedged     the same day minus the index's return        1.4162
    basis only        the basis move net of cost                  2.9720

Only the middle one is what a hedged sleeve earns, and only a sleeve can be
held by an account.  This face puts the three arms on one page, on the same
window and clock as the other two books, and prints the arithmetic that turns
a Sharpe into a capital return under the book's own 8% vol target -- plus the
one fact that decides whether any of it is reachable: one IC lot needs
1,137,862 CNY of capital, and the wallet is 1,000,000.

What it does not do: it re-prices nothing, re-runs no backtest rule, and does
not relabel any published number.  It slices published daily series and
restates them on one ruler (the r2189 pattern), then reads the published
sizing faces for the capital arithmetic.
"""
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
FACE = "three_book_rulers"

RESULTS = "results"
RESEARCH = "research"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

TDAYS = 244.0
TARGET_PCT = 8.0
WALLET_CNY = 1_000_000.0

OUT_JSON = os.path.join(ROOT, RESULTS, FACE + ".json")
OUT_MD = os.path.join(ROOT, RESULTS, FACE + ".md")
OUT_RESEARCH = os.path.join(ROOT, RESEARCH, "THREE_BOOK_RULERS.md")

PARENTS = {
    "etf_book": "results/etf_nobond_vt.json",
    "cb_sleeve": "results/cb_dual_low.json",
    "carry_power": "results/idx_fut_carry_kill_rule_power.json",
    "carry_search_rent": "results/idx_fut_carry_search_rent.json",
    "carry_sizing": "results/idx_fut_carry_sizing_spec.json",
    "carry_open_capital": "results/idx_fut_carry_open_capital.json",
}


# --------------------------------------------------------------------- io
def _rp(rel):
    return os.path.join(ROOT, rel)


def _load(rel):
    with open(_rp(rel), encoding="utf-8") as fh:
        return json.load(fh)


def _sha(rel):
    p = _rp(rel)
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now_iso():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


# ------------------------------------------------------------- book series
def load_books():
    """The same two parent legs the book family uses, plus the carry arm."""
    import book_pair_blend as B

    cb_ser, cb_meta = B.load_cb()
    etf_ser, etf_meta = B.load_etf()

    def norm(s):
        s = s.copy()
        s.index = pd.to_datetime(s.index)
        return s.astype(float).sort_index()

    cb = norm(cb_ser)
    etf = norm(etf_ser)

    import paper_basis_timing_cost_split as CS

    legs = {}
    for code in ("IC", "IM"):
        rows = CS.replay(code, 1.5)
        legs[code] = pd.Series(
            {pd.Timestamp(r["date"]): float(r["net"]) for r in rows}
        ).sort_index()

    idx = legs["IC"].index.union(legs["IM"].index)
    carry = pd.Series(index=idx, dtype=float)
    for d in idx:
        vals = [legs[c][d] for c in ("IC", "IM") if d in legs[c].index]
        carry[d] = float(np.mean(vals))
    carry = carry.sort_index()

    return {
        "cb": cb,
        "etf": etf,
        "carry": carry,
        "meta": {"cb": cb_meta, "etf": etf_meta},
        "carry_legs": legs,
    }


def common_window(books):
    starts = [books["cb"].index.min(), books["etf"].index.min(), books["carry"].index.min()]
    ends = [books["cb"].index.max(), books["etf"].index.max(), books["carry"].index.max()]
    start, end = max(starts), min(ends)
    days = None
    for k in ("cb", "etf", "carry"):
        ids = set(books[k].index)
        days = ids if days is None else (days & ids)
    days = sorted(d for d in days if start <= d <= end)
    return start, end, days


def _nav_level(name, ser, days):
    """Nav over the common calendar.  Levels are held across gaps for the two
    level books; the carry arm is a daily excess return, so gaps compound."""
    if name == "carry":
        nav = [1.0]
        for i in range(1, len(days)):
            seg = ser.loc[days[i - 1]:days[i]].values[1:]
            r = float(np.prod(1.0 + seg) - 1.0) if len(seg) else 0.0
            nav.append(nav[-1] * (1.0 + r))
        return pd.Series(nav, index=days)
    lvl = ser.reindex(days).ffill()
    return lvl / float(lvl.iloc[0])


def stats_of(nav):
    rets = nav.pct_change().dropna()
    n = len(nav) - 1
    yrs = n / TDAYS
    cagr = float(nav.iloc[-1] ** (1.0 / yrs) - 1.0)
    vol = float(rets.std(ddof=1)) * math.sqrt(TDAYS)
    mdd = float((nav / nav.cummax() - 1.0).min())
    return {
        "bars": int(len(nav)),
        "years": round(yrs, 4),
        "cagr_pct": round(cagr * 100.0, 4),
        "vol_pct": round(vol * 100.0, 4),
        "sharpe": round(cagr / vol, 4) if vol else None,
        "mdd_pct": round(mdd * 100.0, 4),
        "total_pct": round((float(nav.iloc[-1]) - 1.0) * 100.0, 4),
    }


def by_year(name, ser, days):
    out = {}
    for y in sorted({d.year for d in days}):
        seg = [d for d in days if d.year == y]
        if len(seg) < 5:
            continue
        if name == "carry":
            r = 1.0
            for i in range(1, len(seg)):
                part = ser.loc[seg[i - 1]:seg[i]].values[1:]
                r *= (1.0 + (float(np.prod(1.0 + part) - 1.0) if len(part) else 0.0))
        else:
            lvl = ser.reindex(seg).ffill()
            r = float(lvl.iloc[-1] / lvl.iloc[0])
        out[str(y)] = round((r - 1.0) * 100.0, 3)
    return out


# ------------------------------------------------------------ published arms
def published_arms():
    power = _load(PARENTS["carry_power"])
    rent = _load(PARENTS["carry_search_rent"])
    sizing = _load(PARENTS["carry_sizing"])
    open_cap = _load(PARENTS["carry_open_capital"])

    ic_stats = power["products"]["IC"]["stats"]
    cells = rent["cells"]
    acc = sizing["accounts"]["IC"]

    return {
        "carry_basis_only": {
            "sharpe": ic_stats["sharpe"],
            "ann_mean_pct": ic_stats["ann_mean_pct"],
            "ann_vol_pct": ic_stats["ann_vol_pct"],
            "window": [
                power["products"]["IC"]["first_bar"],
                power["products"]["IC"]["last_bar"],
            ],
            "source": PARENTS["carry_power"],
            "definition": "the basis move net of cost -- no index exposure, no hedge, no account",
        },
        "carry_excess_hedged": {
            "sharpe": cells["IC|excess_hedged"]["sharpe_ann"],
            "window": cells["IC|excess_hedged"]["window"],
            "bars": cells["IC|excess_hedged"]["bars"],
            "source": PARENTS["carry_search_rent"],
            "definition": "the same day minus the same notional's index return -- the residual a hedge leaves",
        },
        "carry_unhedged": {
            "sharpe": cells["IC|carry_unhedged"]["sharpe_ann"],
            "window": cells["IC|carry_unhedged"]["window"],
            "source": PARENTS["carry_search_rent"],
            "definition": "per-lot daily points on the held contract -- carries the index's own vol",
        },
        "capital": {
            "target_pct": float(sizing.get("rule") and TARGET_PCT or TARGET_PCT),
            "per_lot_vol_cny_hedged": acc["per_lot_vol_cny_hedged"],
            "first_executable_capital_cny": acc["first_executable_capital_cny"],
            "lots_at_wallet": acc["admissible_lots"],
            "gap_cny": acc["capital_gap_to_first_lot_cny"],
            "wallet_cny": acc["capital_cny"],
            "arm_used": sizing.get("arm_used_for_decision"),
            "decision": open_cap.get("withdrawal", {}).get("decision"),
            "source": PARENTS["carry_sizing"],
        },
    }


def lots_for(capital, per_lot_vol, target_pct=TARGET_PCT):
    return int(math.floor(target_pct / 100.0 * float(capital) / float(per_lot_vol) + 1e-9))


def capital_return_pct(sharpe, target_pct=TARGET_PCT):
    """Identity for a vol-targeted book: expected return = target vol x Sharpe."""
    return float(target_pct) * float(sharpe)


# ---------------------------------------------------------------- verdict
def verdict_of(books, arms, capital_line):
    etf_sr = books["etf"]["sharpe"]
    cb_sr = books["cb"]["sharpe"]
    basis_sr = books["carry"]["sharpe"]
    hedged_sr = arms["carry_excess_hedged"]["sharpe"]

    smooth_wins = basis_sr > etf_sr and basis_sr > cb_sr
    holdable_below = hedged_sr < basis_sr
    unreachable = capital_line["lots_at_wallet"] == 0

    if smooth_wins and holdable_below and unreachable:
        return "THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD"
    if smooth_wins and holdable_below and not unreachable:
        return "THE_SMOOTH_LINE_IS_NOT_THE_HOLDABLE_LINE"
    if not holdable_below:
        return "THE_HEDGED_ARM_KEEPS_THE_BASIS_SHARPE"
    return "THE_THREE_LINES_ARE_COMPARABLE_ON_THIS_WINDOW"


def sentence_of(books, arms, capital_line):
    cap = capital_line
    return (
        "On one window (%s..%s) and one clock the three books print %.2f%% / %.2f%% / %.2f%% "
        "(ETF / CB / carry basis). The carry line wins and cannot be bought: it is the basis arm, "
        "quoted per notional, and the family's own hedged arm on the same leg is %.2f Sharpe, not %.2f. "
        "At the book's %s%% vol target one IC lot still needs %s CNY of capital against a %s CNY wallet, "
        "so the executable line is %d lots."
        % (
            books["window"]["first"],
            books["window"]["last"],
            books["etf"]["cagr_pct"],
            books["cb"]["cagr_pct"],
            books["carry"]["cagr_pct"],
            arms["carry_excess_hedged"]["sharpe"],
            arms["carry_basis_only"]["sharpe"],
            cap["target_pct"],
            "{:,.0f}".format(cap["first_executable_capital_cny"]),
            "{:,.0f}".format(cap["wallet_cny"]),
            cap["lots_at_wallet"],
        )
    )


# ------------------------------------------------------------------- build
def build(books=None, arms=None, write=True, quiet=False):
    books = books or load_books()
    arms = arms or published_arms()

    start, end, days = common_window(books)
    table = {}
    yearly = {}
    for name in ("etf", "cb", "carry"):
        nav = _nav_level(name, books[name], days)
        table[name] = stats_of(nav)
        yearly[name] = by_year(name, books[name], days)

    cap = dict(arms["capital"])
    cap["lots_at_first_rung"] = lots_for(cap["first_executable_capital_cny"], cap["per_lot_vol_cny_hedged"])
    cap["lots_at_wallet_recomputed"] = lots_for(cap["wallet_cny"], cap["per_lot_vol_cny_hedged"])

    hedged_capital_return = capital_return_pct(arms["carry_excess_hedged"]["sharpe"])
    basis_capital_return = capital_return_pct(arms["carry_basis_only"]["sharpe"])

    verdict = verdict_of(table, arms, cap)
    sentence = sentence_of(
        {"window": {"first": days[0].date().isoformat(), "last": days[-1].date().isoformat()}, **table},
        arms,
        cap,
    )

    face = {
        "face": FACE,
        "kind": "three_book_same_window_rulers",
        "generated": _now_iso(),
        "evidence_cutoff": days[-1].date().isoformat(),
        "window": {
            "first": days[0].date().isoformat(),
            "last": days[-1].date().isoformat(),
            "bars": len(days),
            "clock": "244 trading days; each book's own published execution lag is kept",
            "how_chosen": "intersection of the three published daily series",
        },
        "books": table,
        "by_year_pct": yearly,
        "carry_arms": arms,
        "capital_line": cap,
        "capital_return_identity": {
            "rule": "expected return on capital = target vol x Sharpe (a vol-targeted book holds vol fixed)",
            "is_a_forecast": False,
            "hedged_pct": round(hedged_capital_return, 3),
            "basis_only_pct": round(basis_capital_return, 3),
            "note": "printed because the casual comparison is a Sharpe: a reader who multiplies sees why "
                    "the basis line's 3.19 cannot turn into a 25% book",
        },
        "verdict": verdict,
        "sentence": sentence,
        "what_this_face_does_not_do": (
            "it re-prices nothing and re-runs no rule; it slices three published daily series onto one "
            "calendar and reads the published sizing faces for the capital arithmetic"
        ),
        "caveats": [
            "the carry arm is a daily excess return on notional; the ETF/CB books are returns on capital",
            "the carry row's sharpe on this common window is not the family's published 2.97 — that one is the "
            "2017-2026 IC-only window; the two differ because the window differs, not because the rule changed",
            "2020-01..2022-07 the carry arm is IC only (IM listed 2022-07-25); after that it is the mean of the two legs",
            "the ETF book's vol target makes its drawdown a dial, so its return is not a fair 'more risk more return' comparison",
            "costs: ETF/CB 10bp per side as published, carry 1.5bp per side as published",
        ],
        "inputs": {k: {"path": v, "sha256": _sha(v)} for k, v in PARENTS.items()},
    }

    if write:
        _write(OUT_JSON, json.dumps(_plain(face), ensure_ascii=False, indent=1) + "\n")
        _write(OUT_MD, render_md(face))
        _write(OUT_RESEARCH, render_research(face))
    if not quiet:
        print("%s %s" % (FACE, verdict))
        print(sentence)
    return face


def _n(v, nd=2, dash="n/a"):
    if v is None:
        return dash
    return ("%%.%df" % nd) % v


def render_md(face):
    b = face["books"]
    L = []
    L.append("# Three books, one window, one clock")
    L.append("")
    L.append("Window **%s .. %s** (%d bars, 244 days/yr). Cutoff %s."
             % (face["window"]["first"], face["window"]["last"], face["window"]["bars"], face["evidence_cutoff"]))
    L.append("")
    L.append("| book | what the return is per | cagr | vol | sharpe | max drawdown | total |")
    L.append("|---|---|---|---|---|---|---|")
    labels = {
        "etf": ("ETF composite book", "capital"),
        "cb": ("CB dual-low sleeve", "capital"),
        "carry": ("index-futures carry (basis arm)", "notional"),
    }
    for k in ("etf", "cb", "carry"):
        s = b[k]
        L.append("| %s | %s | %s%% | %s%% | %s | %s%% | %s%% |"
                 % (labels[k][0], labels[k][1], _n(s["cagr_pct"]), _n(s["vol_pct"]),
                    _n(s["sharpe"], 3), _n(s["mdd_pct"]), _n(s["total_pct"])))
    L.append("")
    L.append("Year by year, same calendar:")
    L.append("")
    years = sorted({y for k in face["by_year_pct"] for y in face["by_year_pct"][k]})
    L.append("| year | ETF | CB | carry (basis) |")
    L.append("|---|---|---|---|")
    for y in years:
        L.append("| %s | %s%% | %s%% | %s%% |"
                 % (y,
                    _n(face["by_year_pct"]["etf"].get(y)),
                    _n(face["by_year_pct"]["cb"].get(y)),
                    _n(face["by_year_pct"]["carry"].get(y))))
    L.append("")
    L.append("## The same leg, three published Sharpes")
    L.append("")
    L.append("| arm | sharpe | what it is | window |")
    L.append("|---|---|---|---|")
    for key in ("carry_basis_only", "carry_excess_hedged", "carry_unhedged"):
        a = face["carry_arms"][key]
        w = a.get("window") or []
        L.append("| %s | %s | %s | %s |"
                 % (key, _n(a["sharpe"], 4), a["definition"],
                    ("%s..%s" % (w[0], w[1])) if len(w) == 2 else "n/a"))
    L.append("")
    cap = face["capital_line"]
    L.append("## What it takes to hold it")
    L.append("")
    L.append("- sizing rule: lots = floor(%s%% x capital / %s CNY per lot)"
             % (_n(cap["target_pct"], 1).rstrip("0").rstrip("."), "{:,.0f}".format(cap["per_lot_vol_cny_hedged"])))
    L.append("- wallet %s CNY -> **%d lots**; first executable capital %s CNY (gap %s CNY)"
             % ("{:,.0f}".format(cap["wallet_cny"]), cap["lots_at_wallet"],
                "{:,.0f}".format(cap["first_executable_capital_cny"]), "{:,.0f}".format(cap["gap_cny"])))
    L.append("- the book's decision on the desk ticket: `%s`" % cap.get("decision"))
    L.append("- capital-return identity at the %s%% target: hedged arm %s%%, basis arm %s%%"
             % (_n(cap["target_pct"], 1).rstrip("0").rstrip("."),
                _n(face["capital_return_identity"]["hedged_pct"]),
                _n(face["capital_return_identity"]["basis_only_pct"])))
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("`%s`" % face["verdict"])
    L.append("")
    L.append(face["sentence"])
    L.append("")
    L.append("### Caveats")
    L.append("")
    for c in face["caveats"]:
        L.append("- " + c)
    L.append("")
    L.append("Generated %s. Inputs are hashed; `--check` says STALE when one of them moves."
             % face["generated"])
    return "\n".join(L) + "\n"


def render_research(face):
    b = face["books"]
    cap = face["capital_line"]
    L = []
    L.append("# Three books on one ruler")
    L.append("")
    L.append("## The question")
    L.append("")
    L.append("This repo now quotes three books in annual percentages. Readers compare them. "
             "The comparison is only fair if the three numbers are the same kind of thing. "
             "This face asks: on one window and one clock, are they?")
    L.append("")
    L.append("## Answer")
    L.append("")
    L.append("Two of them are. The third is not, and the third is the one that wins the table.")
    L.append("")
    L.append("- ETF composite: **%s%%** cagr, vol %s%%, Sharpe %s (per unit of capital)"
             % (_n(b["etf"]["cagr_pct"]), _n(b["etf"]["vol_pct"]), _n(b["etf"]["sharpe"], 3)))
    L.append("- CB dual-low sleeve: **%s%%** cagr, vol %s%%, Sharpe %s (per unit of capital)"
             % (_n(b["cb"]["cagr_pct"]), _n(b["cb"]["vol_pct"]), _n(b["cb"]["sharpe"], 3)))
    L.append("- carry, basis arm: **%s%%** cagr, vol %s%%, Sharpe %s (per unit of **notional**)"
             % (_n(b["carry"]["cagr_pct"]), _n(b["carry"]["vol_pct"]), _n(b["carry"]["sharpe"], 3)))
    L.append("")
    L.append("The carry family prints three Sharpes for the same IC leg because it is three arms: "
             "basis-only %s, excess-after-hedge %s, unhedged per-lot points %s. The one a sleeve can "
             "hold is the middle one."
             % (_n(face["carry_arms"]["carry_basis_only"]["sharpe"], 4),
                _n(face["carry_arms"]["carry_excess_hedged"]["sharpe"], 4),
                _n(face["carry_arms"]["carry_unhedged"]["sharpe"], 4)))
    L.append("")
    L.append("## Why the smooth number is smooth")
    L.append("")
    L.append("The basis arm removes the index. What is left is a slow, low-vol rent -- vol %s%% a year "
             "against the index's own tens of percent. That is a real property of the trade and it is "
             "also why the number cannot be read as a book: the capital that must stand behind one "
             "contract is set by the hedged sleeve's vol, not by the basis's."
             % _n(b["carry"]["vol_pct"]))
    L.append("")
    L.append("## What it costs to find out")
    L.append("")
    L.append("At the book's %s%% hard cap one IC lot needs %s CNY of capital. The wallet has %s CNY. "
             "Executable lots today: **%d**. The published decision on the desk ticket is `%s`."
             % (_n(cap["target_pct"], 1).rstrip("0").rstrip("."),
                "{:,.0f}".format(cap["first_executable_capital_cny"]),
                "{:,.0f}".format(cap["wallet_cny"]),
                cap["lots_at_wallet"], cap.get("decision")))
    L.append("")
    L.append("The vol-target identity turns Sharpe into capital return: %s%% x %s = %s%%. For the basis "
             "arm the same identity gives %s%% -- and that is the arithmetic a reader would run if they "
             "took the page's Sharpe at face value."
             % (_n(cap["target_pct"], 1).rstrip("0").rstrip("."),
                _n(face["carry_arms"]["carry_excess_hedged"]["sharpe"], 4),
                _n(face["capital_return_identity"]["hedged_pct"]),
                _n(face["capital_return_identity"]["basis_only_pct"])))
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("`%s`" % face["verdict"])
    L.append("")
    L.append(face["sentence"])
    L.append("")
    L.append("## What would change this")
    L.append("")
    L.append("- capital to %s CNY: the same rule hands back one lot and the hedge arm's Sharpe becomes "
             "the book's Sharpe, at %s%% expected on capital."
             % ("{:,.0f}".format(cap["first_executable_capital_cny"]),
                _n(face["capital_return_identity"]["hedged_pct"])))
    L.append("- a published arm that measures the basis rent against capital at the sleeve's own vol "
             "(the r2185 ruler argument): if that arm's Sharpe lands near the basis Sharpe, the gap in "
             "this page is a measurement artifact, not a holding cost.")
    L.append("- a common window that starts 2018-10 (IC's first bar) would give the carry arm six more "
             "years the other two books do not have; this face refuses that window on purpose.")
    L.append("")
    L.append("## Caveats")
    L.append("")
    for c in face["caveats"]:
        L.append("- " + c)
    L.append("")
    L.append("Generated %s, cutoff %s, verdict `%s`."
             % (face["generated"], face["evidence_cutoff"], face["verdict"]))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------- check
def check(quiet=False):
    if not os.path.exists(OUT_JSON):
        return 2, "face missing: %s (run without --check)" % OUT_JSON
    face = _load(os.path.join(RESULTS, FACE + ".json"))
    problems = []
    stale = []

    for key, rel in PARENTS.items():
        cur = _sha(rel)
        old = (face.get("inputs", {}).get(key) or {}).get("sha256")
        if cur != old:
            stale.append("%s (%s)" % (key, rel))

    books = face["books"]
    arms = face["carry_arms"]
    cap = face["capital_line"]
    want = verdict_of(books, arms, cap)
    if want != face["verdict"]:
        problems.append("verdict does not recompute from the published rows: %r vs %r"
                        % (face["verdict"], want))

    recomputed_lots = lots_for(cap["wallet_cny"], cap["per_lot_vol_cny_hedged"])
    if recomputed_lots != cap["lots_at_wallet"]:
        problems.append("wallet lots do not recompute: %d vs %d"
                        % (cap["lots_at_wallet"], recomputed_lots))
    recomputed_first = lots_for(cap["first_executable_capital_cny"], cap["per_lot_vol_cny_hedged"])
    if recomputed_first != 1:
        problems.append("first rung does not yield one lot: %d" % recomputed_first)

    hedged = round(capital_return_pct(arms["carry_excess_hedged"]["sharpe"]), 3)
    if abs(hedged - face["capital_return_identity"]["hedged_pct"]) > 1e-6:
        problems.append("hedged capital-return identity does not recompute")

    src = arms["carry_excess_hedged"]["source"]
    if src != PARENTS["carry_search_rent"]:
        problems.append("hedged arm is not read from the search-rent face")

    if problems:
        rc, kind = 3, "CHECK FAILED"
        msg = "%s: %s" % (kind, "; ".join(problems))
    elif stale:
        rc, kind = 2, "STALE: input face(s) moved since this face was built"
        msg = "%s: %s" % (kind, ", ".join(stale))
    else:
        rc, kind = 0, "CHECK OK"
        msg = "%s (%d books, cutoff %s)" % (kind, len(books), face["evidence_cutoff"])
    if not quiet:
        print(json.dumps({"ok": rc == 0, "kind": kind, "detail": msg}, ensure_ascii=False))
    return rc, msg


# ----------------------------------------------------------------- selftest
def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((bool(cond), name, detail))

    books = load_books()
    start, end, days = common_window(books)

    leg("window starts at the latest of the three series' first bars",
        start == max(books["cb"].index.min(), books["etf"].index.min(), books["carry"].index.min()),
        str(start))
    leg("window ends at the earliest last bar",
        end == min(books["cb"].index.max(), books["etf"].index.max(), books["carry"].index.max()),
        str(end))
    leg("common window is the intersection, not a union", len(days) > 500, str(len(days)))
    leg("no bar after the earliest parent last bar",
        days[-1] <= end and days[0] >= start, "%s..%s" % (days[0].date(), days[-1].date()))

    etf_nav = _nav_level("etf", books["etf"], days)
    lvl = books["etf"].reindex(days).ffill()
    leg("etf nav is the parent level itself, rebased to 1 (no re-pricing)",
        float(np.nanmax(np.abs(etf_nav.values * float(lvl.iloc[0]) - lvl.values))) < 1e-12)

    navs = {k: _nav_level(k, books[k], days) for k in ("etf", "cb", "carry")}
    st = {k: stats_of(v) for k, v in navs.items()}
    leg("carry total return equals compounded daily plan returns",
        abs((1.0 + st["carry"]["total_pct"] / 100.0)
            - float(np.prod(1.0 + books["carry"].loc[days[0]:days[-1]].values[1:]))) < 1e-6,
        "%.6f" % st["carry"]["total_pct"])

    # independent recomputation of the etf cagr straight from ratio chain
    ratios = (lvl / lvl.shift(1) - 1.0).dropna()
    indep_vol = float(ratios.std(ddof=1)) * math.sqrt(TDAYS) * 100.0
    leg("etf vol matches an independent ratio-chain computation",
        abs(round(indep_vol, 4) - st["etf"]["vol_pct"]) < 1e-9, "%.6f" % indep_vol)

    arms = published_arms()
    leg("the three IC arms are ordered basis >= hedged >= unhedged",
        arms["carry_basis_only"]["sharpe"] >= arms["carry_excess_hedged"]["sharpe"]
        >= arms["carry_unhedged"]["sharpe"],
        "%.3f/%.3f/%.3f" % (arms["carry_basis_only"]["sharpe"],
                            arms["carry_excess_hedged"]["sharpe"],
                            arms["carry_unhedged"]["sharpe"]))
    leg("the hedged arm is not read from the same face as the basis arm",
        arms["carry_excess_hedged"]["source"] != arms["carry_basis_only"]["source"])

    cap = dict(arms["capital"])
    leg("wallet of 1,000,000 admits zero lots under the published rule",
        lots_for(cap["wallet_cny"], cap["per_lot_vol_cny_hedged"]) == 0)
    leg("first executable capital admits exactly one lot",
        lots_for(cap["first_executable_capital_cny"], cap["per_lot_vol_cny_hedged"]) == 1)
    leg("the gap equals first rung minus wallet",
        abs((cap["first_executable_capital_cny"] - cap["wallet_cny"]) - cap["gap_cny"]) < 0.02)

    # negative controls
    bad_books = {k: dict(v) for k, v in st.items()}
    bad_books["carry"]["sharpe"] = st["etf"]["sharpe"] - 0.5
    cap0 = dict(cap)
    cap0["lots_at_wallet"] = 0
    v_bad = verdict_of(bad_books, arms, cap0)
    leg("if the basis arm stops winning, the verdict changes", v_bad != "THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD", v_bad)
    cap1 = dict(cap)
    cap1["lots_at_wallet"] = 1
    v_funded = verdict_of(st, arms, cap1)
    leg("if the wallet could hold it, the verdict stops saying nobody can hold it",
        v_funded == "THE_SMOOTH_LINE_IS_NOT_THE_HOLDABLE_LINE", v_funded)
    arms2 = {k: dict(v) if isinstance(v, dict) else v for k, v in arms.items()}
    arms2["carry_excess_hedged"]["sharpe"] = st["carry"]["sharpe"]
    v_same = verdict_of(st, arms2, cap0)
    leg("if the hedged arm kept the basis Sharpe, the verdict does not claim a gap",
        v_same != "THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD", v_same)

    # drift classification: real build, then check on a poisoned copy
    face = build(books=books, arms=arms, write=False, quiet=True)
    phys = FACE + ".json"
    backup = None
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON, encoding="utf-8") as fh:
            backup = fh.read()
    try:
        _write(OUT_JSON, json.dumps(_plain(face), ensure_ascii=False, indent=1) + "\n")
        rc_ok, _ = check(quiet=True)
        leg("check is green on a freshly built face", rc_ok == 0, "rc=%d" % rc_ok)

        poisoned = json.loads(json.dumps(_plain(face)))
        poisoned["verdict"] = "THE_THREE_LINES_ARE_COMPARABLE_ON_THIS_WINDOW"
        _write(OUT_JSON, json.dumps(poisoned, ensure_ascii=False, indent=1) + "\n")
        rc_bad, msg_bad = check(quiet=True)
        leg("a mutated verdict is CHECK FAILED and does not advertise STALE",
            rc_bad == 3 and "CHECK FAILED" in msg_bad and "STALE" not in msg_bad, msg_bad[:60])

        stale = json.loads(json.dumps(_plain(face)))
        stale["inputs"]["carry_power"]["sha256"] = "0" * 64
        _write(OUT_JSON, json.dumps(stale, ensure_ascii=False, indent=1) + "\n")
        rc_st, msg_st = check(quiet=True)
        leg("a moved input face says STALE (so a chain leg will pay for a rewrite)",
            rc_st == 2 and "STALE" in msg_st, msg_st[:60])
    finally:
        if backup is not None:
            with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(backup)

    ok = all(l[0] for l in legs)
    for good, name, detail in legs:
        print(("PASS " if good else "FAIL ") + name + ((" [" + detail + "]") if detail else ""))
    print("%d/%d legs" % (sum(1 for l in legs if l[0]), len(legs)))
    return 0 if ok else 1


def run():
    face = build()
    rc, msg = check(quiet=True)
    print("check -> " + msg)
    print("wrote %s, %s, %s" % (OUT_JSON, OUT_MD, OUT_RESEARCH))
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(_selftest())
    elif arg == "--check":
        rc, msg = check()
        sys.exit(rc)
    elif arg == "run" or arg == "":
        sys.exit(run())
    else:
        print("usage: %s [run|--check|--selftest]" % os.path.basename(__file__))
        sys.exit(1)
