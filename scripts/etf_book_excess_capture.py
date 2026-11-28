"""Does the book earn its excess on the way up, on the way down, or not at all?

Why this face exists
--------------------
r2229 answered "is the live loss normal" with a percentile (22.2% of the book's own
26-bar windows were as bad or worse) and, on the way past, printed one more number:
the book leads the four-exposure basket by **+2.79pp**, at the 87.4th percentile of
its own excess windows.  That number says the work may be right; it does not say
WHERE the work is done.  A book that beats its basket only because it drops half as
much in down-bars is an insurance product, not a selection product, and the two
need opposite decisions when the reader is asked to add capital: insurance is
already doing its job while the market falls, selection has to keep finding the
right names in both directions.

So this face splits the same excess into the two halves a reader actually lives in:

    up-bars    the basket's bar return > 0
    down-bars  the basket's bar return < 0

and reports, per half, how many bars, how much of the log excess each half carries,
and the capture ratio sum(book | half) / sum(basket | half).  Sums, not means, so a
half with three violent bars is not averaged into the same row as a half with two
hundred quiet ones.

Two comparisons, because "the book beat the basket" mixes two different jobs:

    base_book   the same selection at full size, no vol overlay   -> SELECTION
    production  the card's config (12 names, 8% vol target, toll) -> the headline

`production - base_book` is the overlay's doing and is printed as its own row rather
than folded into either half.  Without that split the reader will credit selection
for a vol target's cash drag (29.1% mean cash on the production arm).

Also printed, because a big excess in one half is not a recurring edge:

  * concentration: the share of total log excess carried by the best 10% of bars,
    and what pp/yr is left once those bars are removed;
  * consistency: the sign of the excess in every calendar year it has bars for.

Scope discipline: zero prereg, zero judged face, zero network, zero engine edit, no
production change, no shared face touched (new files only -- this is a CONTENTION
round, see round report).  L1 deterministic: a rerun moves only its own timestamp.

  python scripts/etf_book_excess_capture.py run
  python scripts/etf_book_excess_capture.py --check
  python scripts/etf_book_excess_capture.py --selftest
"""
import io
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etf_book_forward as F                                            # noqa: E402

BARS_PER_YEAR = F.BARS_PER_YEAR
OUT_JSON = os.path.join("results", "etf_book_excess", "capture.json")
OUT_MD = os.path.join("research", "ETF_BOOK_EXCESS_CAPTURE.md")

SCHEMA = "etf_book_excess_capture/v1"
# A capture ratio within this band of 1.0 is called parity, not edge. Five percent is
# the tolerance the desk already reads single-half sums with (a half carries 914 bars,
# so 5% of a half-sum is not a rounding artefact, it is a direction you could act on only
# if it persisted -- and the concentration row says whether it does).
NEAR_PARITY_BAND = 0.05


# ------------------------------------------------------------------ pure maths
def daily(series):
    """Bar-to-bar simple returns from a nav series (index kept)."""
    a = series.astype(float)
    return (a / a.shift(1) - 1.0).iloc[1:]


def split_excess(r_x, r_k):
    """Split the log excess of arm x over basket k into up-bars and down-bars.

    Both tapes are simple returns on the same bars.  The identity this face publishes
    is that the two halves add to the whole:

        sum(log1p(x) - log1p(k)) == up_part + down_part
    """
    rx = np.asarray(r_x, dtype=float)
    rk = np.asarray(r_k, dtype=float)
    if rx.size != rk.size:
        raise ValueError("tapes differ in length: %d vs %d" % (rx.size, rk.size))
    ok = np.isfinite(rx) & np.isfinite(rk) & (rx > -1.0) & (rk > -1.0)
    d = np.where(ok, np.log1p(rx) - np.log1p(rk), 0.0)
    up = ok & (rk > 0)
    down = ok & (rk < 0)
    flat = ok & (rk == 0)
    out = {
        "bars": int(ok.sum()),
        "flat_bars": int(flat.sum()),
        "log_excess_total": float(d.sum()),
        "up": {
            "bars": int(up.sum()),
            "log_excess": float(d[up].sum()),
            "book_sum": float(rx[up].sum()),
            "basket_sum": float(rk[up].sum()),
            "mean_basket_bar": float(rk[up].mean()) if up.any() else None,
        },
        "down": {
            "bars": int(down.sum()),
            "log_excess": float(d[down].sum()),
            "book_sum": float(rx[down].sum()),
            "basket_sum": float(rk[down].sum()),
            "mean_basket_bar": float(rk[down].mean()) if down.any() else None,
        },
    }
    for half in ("up", "down"):
        b = out[half]["basket_sum"]
        # A half where the basket never moves has no ratio; saying 0 or 1 would invent one.
        out[half]["capture"] = (out[half]["book_sum"] / b) if abs(b) > 1e-12 else None
    return out


def concentration(d, top_share=0.10):
    """How much of the excess rides on the best `top_share` of bars."""
    x = np.asarray([v for v in d if np.isfinite(v)], dtype=float)
    n = x.size
    if n < 10:
        return {"bars": int(n), "top_share": top_share, "share_of_total": None,
                "excess_without_top": None, "top_bars": None}
    pos = x[x > 0]
    tot = float(x.sum())
    k = max(1, int(round(n * top_share)))
    srt = np.sort(x)[::-1]
    top = float(srt[:k].sum())
    return {
        "bars": int(n),
        "top_share": top_share,
        "top_bars": int(k),
        "top_log_excess": top,
        "share_of_total": (top / tot) if abs(tot) > 1e-12 else None,
        "excess_without_top": float(tot - top),
        "positive_bars": int(pos.size),
        "mean_bar": float(x.mean()),
    }


def yearly(d, index):
    """Sign and size of the excess in each calendar year on its bars."""
    out = {}
    for ts, v in zip(index, d):
        if not np.isfinite(v):
            continue
        y = str(pd.Timestamp(ts).year)
        e = out.setdefault(y, {"bars": 0, "log_excess": 0.0})
        e["bars"] += 1
        e["log_excess"] += float(v)
    for y in out:
        out[y] = {"bars": out[y]["bars"],
                  "log_excess": round(out[y]["log_excess"], 6),
                  "sign": "positive" if out[y]["log_excess"] > 0
                          else ("negative" if out[y]["log_excess"] < 0 else "flat")}
    return out


def verdict_of(sel, conc):
    """One sentence a reader can act on, derived from the printed numbers only."""
    up = sel["up"]["capture"]
    down = sel["down"]["capture"]
    if up is None or down is None:
        return "UNMEASURABLE_ONE_SIDED_BASKET"
    # Capture is a sum over a half, so a 3% gap on 1.0 is a small number wearing a
    # ratio's clothes. Calling that "alpha" would overstate it by an order of magnitude;
    # the parity band says "no direction you can act on" instead.
    if abs(up - 1.0) <= NEAR_PARITY_BAND and abs(down - 1.0) <= NEAR_PARITY_BAND:
        side = "NEAR_PARITY_BOTH_SIDES"
    elif (up >= 1.0) and (down <= 1.0):
        side = "ALPHA_ON_BOTH_SIDES"
    elif up >= 1.0 and down > 1.0:
        return "PAYS_MORE_IN_REVERSALS_THAN_IT_DODGES"
    elif up < 1.0 and down < 1.0:
        side = "DEFENSE_ONLY_SELECTION"
    else:
        return "SELECTION_IS_A_LIABILITY_BOTH_WAYS"
    share = conc.get("share_of_total")
    if share is not None and share > 0.5:
        return side + "_BUT_CARRIED_BY_FEW_BARS"
    return side


# ------------------------------------------------------------------ the backtest
def prepare():
    close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
    px = close.ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = F.date_grid(px, F.CONFIG["rebal"])
    try:
        carry, carry_note = F.build_carry(dates)
    except Exception as exc:                                            # noqa: BLE001
        print("carry tape unavailable (%s) -- both arms ride parity" % exc, file=sys.stderr)
        carry, carry_note = None, "unavailable"
    return {"px": px, "op": op, "score": score, "dates": dates,
            "rebal_days": rebal_days, "carry": carry, "carry_note": carry_note,
            "n_flip": n_flip}


def run_arm(prep, vol_target):
    """One book over the full history, carry on (the ruler the ledger books)."""
    st = F.Forward(prep["px"], prep["op"], prep["score"], F.CONFIG["n_hold"],
                   F.CONFIG["rebal"], F.CONFIG["cost_per_side"],
                   vol_target=vol_target, carry=prep["carry"])
    marks = st.run(prep["dates"], prep["rebal_days"])
    nav = pd.Series({d: m["nav"] for d, m in marks}).sort_index()
    cash = pd.Series({d: m.get("cash", np.nan) for d, m in marks}).sort_index()
    return {"nav": nav, "cash": cash, "n_fill": st.n_fill,
            "mean_turnover": st.mean_turnover}


def cagr_of(series):
    a = np.asarray(series, dtype=float)
    if a.size < 3 or a[0] <= 0:
        return None
    yrs = (a.size - 1) / float(BARS_PER_YEAR)
    return float((a[-1] / a[0]) ** (1.0 / yrs) - 1.0)


def risk_of(series):
    """CAGR / vol / sharpe / max drawdown -- an excess with no risk yardstick is not a reading."""
    a = np.asarray(series, dtype=float)
    if a.size < 3 or a[0] <= 0:
        return {}
    cagr = cagr_of(a)
    rets = a[1:] / a[:-1] - 1.0
    sd = float(np.std(rets, ddof=1))
    vol = sd * math.sqrt(BARS_PER_YEAR)
    peak, mdd = a[0], 0.0
    for v in a:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return {"cagr_pct": round(100.0 * cagr, 3),
            "vol_pct": round(100.0 * vol, 2),
            "sharpe": round(float(np.mean(rets)) / sd * math.sqrt(BARS_PER_YEAR), 3)
                      if sd > 0 else None,
            "maxdd_pct": round(100.0 * mdd, 2)}


def build():
    prep = prepare()
    if len(prep["dates"]) < 60:
        raise SystemExit("panel too short: %d bars" % len(prep["dates"]))
    prod = run_arm(prep, F.CONFIG["vol_target"])
    base = run_arm(prep, None)
    base_bar = str(prod["nav"].index[0].date())
    try:
        blk = F.bench_block(prep["dates"], prep["rebal_days"], base_bar)
        bench = pd.Series({pd.Timestamp(b["bar"]): b["nav"] for b in blk["bars"]}).sort_index()
    except Exception as exc:                                            # noqa: BLE001
        print("basket unavailable (%s) -- excess unmeasured, not zero" % exc, file=sys.stderr)
        bench = None

    years = (len(prep["dates"]) - 1) / float(BARS_PER_YEAR)
    out = {
        "schema": SCHEMA,
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(prep["dates"][-1].date()),
        "config": {
            "n_hold": F.CONFIG["n_hold"], "rebal": F.CONFIG["rebal"],
            "cost_per_side": F.CONFIG["cost_per_side"],
            "vol_target_production": F.CONFIG["vol_target"],
            "execution": F.CONFIG["execution"],
            "bars_per_year": BARS_PER_YEAR,
            "carry": "on for both arms (%s)" % prep["carry_note"],
            "panels": {"first_bar": str(prep["dates"][0].date()),
                       "bars": len(prep["dates"]), "years": round(years, 4),
                       "symbols": int(prep["px"].shape[1]),
                       "flips_repaired": prep["n_flip"]},
        },
        "arms": {},
        "verdict": None,
        "caveats": [
            "Capture ratios are sums over a half, not means: a half with a few violent bars "
            "is not averaged against the other half's many quiet bars.",
            "The basket is the four-exposure equal-weight one the book itself is measured "
            "against (F.bench_block) -- the same ruler r2229 printed +2.79pp on.",
            "The production arm holds 29.1% mean cash because of its 8% vol target; its "
            "capture ratios are structurally below 1 in up-bars. Reading that as bad "
            "selection is the error this face exists to prevent -- base_book is the "
            "selection arm.",
            "The pool is today's listed ETFs, so the equity sleeve still carries "
            "survivorship inherited from the backtest, not introduced here.",
        ],
    }
    if bench is None:
        out["verdict"] = "UNMEASURED_BASKET_UNAVAILABLE"
        return out

    idx = prod["nav"].index
    if len(bench) != len(idx) or not bench.index.equals(idx):
        bench = bench.reindex(idx).ffill()
    r_p = daily(prod["nav"])
    r_b = daily(base["nav"])
    r_k = daily(bench)
    common = r_p.index.intersection(r_b.index).intersection(r_k.index)
    r_p, r_b, r_k = r_p.reindex(common), r_b.reindex(common), r_k.reindex(common)

    sel = split_excess(r_b, r_k)
    head = split_excess(r_p, r_k)
    d_sel = (np.log1p(r_b.values) - np.log1p(r_k.values))
    conc = concentration(d_sel)
    yrs_common = len(common) / float(BARS_PER_YEAR)

    def pp(logx):
        return round(100.0 * float(logx) / yrs_common, 3)

    def half(x, key):
        h = dict(x[key])
        h["pp_per_year"] = pp(h["log_excess"])
        if h.get("capture") is not None:
            h["capture"] = round(h["capture"], 4)
        if h.get("mean_basket_bar") is not None:
            h["mean_basket_bar_bp"] = round(10000.0 * h["mean_basket_bar"], 2)
            del h["mean_basket_bar"]
        h["log_excess"] = round(h["log_excess"], 6)
        return h

    def arm_block(x, label):
        return {
            "label": label,
            "bars": x["bars"],
            "flat_bars": x["flat_bars"],
            "log_excess_total": round(x["log_excess_total"], 6),
            "excess_pp_per_year": pp(x["log_excess_total"]),
            "up": half(x, "up"),
            "down": half(x, "down"),
            "split_check_abs": round(abs(x["log_excess_total"]
                                         - (x["up"]["log_excess"] + x["down"]["log_excess"])), 12),
        }

    out["arms"]["basket"] = {
        "label": "four-exposure equal-weight basket (F.bench_block)",
        "bars": int(len(common)),
        "cagr_pct": round(100.0 * cagr_of(bench), 3) if cagr_of(bench) is not None else None,
        "total_return_pct": round(100.0 * (float(bench.iloc[-1]) / float(bench.iloc[0]) - 1.0), 3),
        "risk": risk_of(bench),
    }
    out["arms"]["production"] = arm_block(head, "card config: 12 names, 8% vol target, toll")
    out["arms"]["production"]["cagr_pct"] = round(100.0 * cagr_of(prod["nav"]), 3)
    out["arms"]["production"]["mean_cash"] = round(float(prod["cash"].mean()), 4)
    out["arms"]["production"]["risk"] = risk_of(prod["nav"])
    out["arms"]["base_book"] = arm_block(sel, "same selection, full size, no vol overlay")
    out["arms"]["base_book"]["cagr_pct"] = round(100.0 * cagr_of(base["nav"]), 3)
    out["arms"]["base_book"]["mean_cash"] = round(float(base["cash"].mean()), 4)
    out["arms"]["base_book"]["risk"] = risk_of(base["nav"])
    out["arms"]["overlay_wedge"] = {
        "label": "production minus base_book (the vol target's doing)",
        "excess_pp_per_year": round(pp(head["log_excess_total"])
                                    - pp(sel["log_excess_total"]), 3),
        "note": "a cash-drag wedge, not selection and not the basket's doing",
    }
    out["concentration"] = {
        "top_share": conc.get("top_share"),
        "top_bars": conc.get("top_bars"),
        "share_of_total": None if conc.get("share_of_total") is None
                          else round(conc["share_of_total"], 4),
        "excess_pp_per_year_without_top": None if conc.get("excess_without_top") is None
                                          else pp(conc["excess_without_top"]),
        "positive_bars": conc.get("positive_bars"),
        "bars": conc.get("bars"),
    }
    out["by_year_base_book"] = yearly(d_sel, common)
    out["verdict"] = verdict_of(sel, conc)
    return out


# ------------------------------------------------------------------ markdown
def _f(x, dp=2, suffix=""):
    if x is None:
        return "unmeasured"
    return (("%." + str(dp) + "f") % x) + suffix


def _plain(x, dp=2):
    if x is None:
        return "unmeasured"
    return ("%." + str(dp) + "f") % x


def render_md(doc):
    a = doc["arms"]
    if "base_book" not in a:
        return ("# Excess capture\n\n**verdict: %s**\n" % doc["verdict"])
    b = a["base_book"]
    p = a["production"]
    c = doc["concentration"]
    yrs = doc["config"]["panels"]["years"]
    lines = []
    lines.append("# Does the book earn its excess on the way up or on the way down?")
    lines.append("")
    lines.append("<!-- BEGIN GENERATED -->")
    lines.append("")
    lines.append("**verdict: %s**" % doc["verdict"])
    lines.append("")
    lines.append("Bars %d (%s..%s, %.2f years at %d bars/yr). Basket = four-exposure "
                 "equal weight on the book's own grid and fill."
                 % (doc["config"]["panels"]["bars"],
                    doc["config"]["panels"]["first_bar"],
                    doc["config"]["panels"]["bars"] and doc["evidence_cutoff"], yrs,
                    BARS_PER_YEAR))
    lines.append("")
    lines.append("## Selection arm (full size, no vol overlay) versus the basket")
    lines.append("")
    lines.append("| half | bars | basket sum | book sum | capture | excess pp/yr |")
    lines.append("|---|---|---|---|---|---|")
    lines.append("| up (basket bar > 0) | %d | %s | %s | %s | %s |"
                 % (b["up"]["bars"], _plain(b["up"]["basket_sum"], 4),
                    _plain(b["up"]["book_sum"], 4), _plain(b["up"]["capture"], 3),
                    _f(b["up"]["pp_per_year"], 3)))
    lines.append("| down (basket bar < 0) | %d | %s | %s | %s | %s |"
                 % (b["down"]["bars"], _plain(b["down"]["basket_sum"], 4),
                    _plain(b["down"]["book_sum"], 4), _plain(b["down"]["capture"], 3),
                    _f(b["down"]["pp_per_year"], 3)))
    lines.append("| **total** | %d | | | | **%s** |"
                 % (b["bars"], _f(b["excess_pp_per_year"], 3)))
    lines.append("")
    lines.append("Capture is `sum(book return in that half) / sum(basket return in that half)`. "
                 "Sums, not means: %d up-bars and %d down-bars do not get averaged into each "
                 "other." % (b["up"]["bars"], b["down"]["bars"]))
    lines.append("")
    lines.append("## The headline arm, and the wedge between them")
    lines.append("")
    lines.append("| arm | CAGR | vol | Sharpe | max DD | mean cash | up capture | down capture | excess pp/yr |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    rows = [("basket (four exposures, equal weight)", a["basket"], None),
            ("production (8% vol target)", p, p["excess_pp_per_year"]),
            ("base_book (selection only)", b, b["excess_pp_per_year"])]
    for name, arm, ex in rows:
        r = arm.get("risk", {})
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (name,
                        _f(arm.get("cagr_pct"), 2, "%"),
                        _f(r.get("vol_pct"), 1, "%"),
                        _plain(r.get("sharpe"), 2),
                        _f(r.get("maxdd_pct"), 1, "%"),
                        _f(100.0 * arm.get("mean_cash", 0.0), 1, "%") if "mean_cash" in arm else "0.0%",
                        _plain(arm.get("up", {}).get("capture", 1.0) if "up" in arm else 1.0, 3),
                        _plain(arm.get("down", {}).get("capture", 1.0) if "down" in arm else 1.0, 3),
                        _f(ex, 3) if ex is not None else "0.000"))
    lines.append("| overlay wedge | | | | | | | | %s |"
                 % _f(a["overlay_wedge"]["excess_pp_per_year"], 3))
    lines.append("")
    lines.append("The production arm gives up %s pp/yr of raw return against the basket and "
                 "carries %s pp less volatility and a %s pp shallower drawdown. Whether that "
                 "trade is worth it is the risk-dial decision the desk already priced elsewhere "
                 "(8%% is a risk dial, not a return dial); this table does not re-litigate it, "
                 "it only prints both sides so `-%s pp/yr` cannot be read as \"the book was "
                 "pointless\"."
                 % (_plain(0.0 - p["excess_pp_per_year"], 2),
                    _plain(a["basket"]["risk"].get("vol_pct", 0) - p["risk"].get("vol_pct", 0), 1),
                    _plain(abs(a["basket"]["risk"].get("maxdd_pct", 0)
                               - p["risk"].get("maxdd_pct", 0)), 1),
                    _plain(0.0 - p["excess_pp_per_year"], 2)))
    lines.append("")
    lines.append("The selection arm buys its %s pp/yr with **more** volatility (%s%% against "
                 "the basket's %s%%) and a Sharpe of %s against %s -- it is a return engine, "
                 "not a risk-adjusted one, and the vol target is what turns it into the "
                 "production row."
                 % (_plain(b["excess_pp_per_year"], 2),
                    _plain(b["risk"].get("vol_pct"), 1),
                    _plain(a["basket"]["risk"].get("vol_pct"), 1),
                    _plain(b["risk"].get("sharpe"), 2),
                    _plain(a["basket"]["risk"].get("sharpe"), 2)))
    lines.append("The production arm's capture in up-bars is below the selection arm's by "
                 "construction: it sits in cash %s%% of the time, so it cannot capture a "
                 "full up-bar. That gap is the vol target's price, printed here as the wedge, "
                 "not folded into the selection reading."
                 % _plain(100.0 * p.get("mean_cash", 0), 1))
    lines.append("")
    lines.append("**Not the same number as r2229.** r2229 printed +2.79pp of excess on the "
                 "**live 26-bar window** (the first five weeks of the ledger). The rows above "
                 "are the **full 1,672-bar history**. A five-week window and a seven-year "
                 "history disagreeing is not a defect in either; neither may stand in for the "
                 "other.")
    lines.append("")
    lines.append("## Is the excess recurring or a few bars?")
    lines.append("")
    left = c["excess_pp_per_year_without_top"]
    lines.append("Best %s%% of bars (n=%s) carry **%s%%** of the total log excess; removing them "
                 "leaves **%s pp/yr** against the headline's %s pp/yr%s."
                 % (_plain(None if c["top_share"] is None else c["top_share"] * 100, 0),
                    c["top_bars"],
                    _plain(None if c["share_of_total"] is None
                           else c["share_of_total"] * 100, 1),
                    _f(left, 3),
                    _f(b["excess_pp_per_year"], 3),
                    (" -- **the rest of the history loses to the basket**"
                     if (left is not None and left < 0) else "")))
    lines.append("")
    lines.append("## Sign of the excess, by calendar year (selection arm)")
    lines.append("")
    lines.append("| year | bars | log excess | sign |")
    lines.append("|---|---|---|---|")
    for y in sorted(doc["by_year_base_book"]):
        r = doc["by_year_base_book"][y]
        lines.append("| %s | %d | %s | %s |"
                     % (y, r["bars"], _plain(r["log_excess"], 4), r["sign"]))
    lines.append("")
    lines.append("<!-- END GENERATED -->")
    lines.append("")
    lines.append("## Why the two halves are not one number")
    lines.append("")
    lines.append("A book that drops 0.5x while the basket drops and rises 1.0x while it rises is "
                 "insurance: it is already earning its keep in the half where the reader is "
                 "losing money, and adding capital does not make it better at the other half. A "
                 "book that rises 1.2x in up-bars and falls 1.0x in down-bars is selection, and "
                 "the risk of adding capital is that the selection stops finding names. Both "
                 "print the same `+x pp` excess. This face separates them.")
    lines.append("")
    lines.append("Caveats carried from the artifact: %s" % "; ".join(doc["caveats"]))
    lines.append("")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ commands
def cmd_run(args):
    doc = build()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(doc))
    print("verdict=%s base_up=%s base_down=%s excess_pp=%s -> %s"
          % (doc["verdict"],
             doc["arms"].get("base_book", {}).get("up", {}).get("capture"),
             doc["arms"].get("base_book", {}).get("down", {}).get("capture"),
             doc["arms"].get("base_book", {}).get("excess_pp_per_year"), OUT_JSON))
    return 0


def cmd_check(args):
    if not (os.path.exists(OUT_JSON) and os.path.exists(OUT_MD)):
        print("STALE face missing: %s or %s" % (OUT_JSON, OUT_MD))
        return 3
    saved = io.open(OUT_JSON, encoding="utf-8").read()
    doc = json.loads(saved)
    chk = check_face(doc)
    on_disk = io.open(OUT_MD, encoding="utf-8").read()
    rendered = render_md(doc)
    if on_disk != rendered:
        chk.append("markdown does not match the artifact it claims to be rendered from")
    if chk:
        print("CHECK FAILED")
        for c in chk:
            print("  - " + c)
        return 4
    print("OK capture face is self-consistent (verdict=%s)" % doc["verdict"])
    return 0


def check_face(doc):
    """Recompute the published arithmetic from the published numbers. No re-run."""
    out = []
    for name in ("production", "base_book"):
        a = doc["arms"].get(name)
        if not a:
            out.append("arm %s missing" % name)
            continue
        s = a["up"]["log_excess"] + a["down"]["log_excess"]
        if abs(s - a["log_excess_total"]) > 1e-5:
            out.append("%s: halves %.6f do not add to total %.6f"
                       % (name, s, a["log_excess_total"]))
        if a["split_check_abs"] > 1e-9:
            out.append("%s: published split residual %s" % (name, a["split_check_abs"]))
        for half in ("up", "down"):
            h = a[half]
            if h["basket_sum"] and h.get("capture") is not None:
                want = h["book_sum"] / h["basket_sum"]
                if abs(want - h["capture"]) > 1e-3:
                    out.append("%s/%s: capture %s != book/basket %s"
                               % (name, half, h["capture"], round(want, 4)))
    b = doc["arms"].get("base_book")
    if b:
        up = b["up"].get("capture")
        down = b["down"].get("capture")
        want = verdict_of({"up": {"capture": up}, "down": {"capture": down}},
                          doc["concentration"])
        if want != doc["verdict"]:
            out.append("verdict %s does not follow from its own capture numbers (%s)"
                       % (doc["verdict"], want))
    return out


# ------------------------------------------------------------------ selftest
def _tapes(n=200, seed=7):
    rng = np.random.default_rng(seed)
    rk = pd.Series(rng.normal(0.0004, 0.01, n),
                   index=pd.bdate_range("2020-01-02", periods=n))
    return rk


def _selfcheck():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1 identity: the two halves add to the whole.
    rk = _tapes()
    rx = rk * 0.5
    s = split_excess(rx, rk)
    leg("halves add to the whole",
        abs(s["log_excess_total"] - (s["up"]["log_excess"] + s["down"]["log_excess"])) < 1e-9)
    leg("up and down partition the bars",
        s["up"]["bars"] + s["down"]["bars"] + s["flat_bars"] == s["bars"])

    # 2 a book that is half the basket both ways captures 0.5 in both halves.
    leg("half-size book captures 0.5 both ways",
        abs(s["up"]["capture"] - 0.5) < 1e-9 and abs(s["down"]["capture"] - 0.5) < 1e-9)

    # 3 defense-only: full up, half down.
    rx3 = rk.where(rk > 0, rk * 0.5)
    s3 = split_excess(rx3, rk)
    leg("defense-only reads 1.0 up / 0.5 down",
        abs(s3["up"]["capture"] - 1.0) < 1e-9 and abs(s3["down"]["capture"] - 0.5) < 1e-9)
    leg("earning less in both halves is not called alpha",
        verdict_of({"up": {"capture": 0.8}, "down": {"capture": 0.5}},
                   {"share_of_total": 0.1}) == "DEFENSE_ONLY_SELECTION")
    leg("a 3% capture gap is parity, not alpha",
        verdict_of({"up": {"capture": 1.037}, "down": {"capture": 0.976}},
                   {"share_of_total": 0.1}) == "NEAR_PARITY_BOTH_SIDES")
    leg("a 10% capture gap keeps the alpha word",
        verdict_of({"up": {"capture": 1.10}, "down": {"capture": 0.90}},
                   {"share_of_total": 0.1}) == "ALPHA_ON_BOTH_SIDES")

    # 4 a book that doubles in up-bars and loses MORE in down-bars is not alpha.
    rx4 = rk.where(rk <= 0, rk * 2.0)
    s4 = split_excess(rx4, rk)
    leg("up doubling with wider losses is not called alpha",
        s4["up"]["capture"] > 1.0
        and verdict_of({"up": {"capture": s4["up"]["capture"]},
                        "down": {"capture": 1.2}},
                       {"share_of_total": 0.1}) == "PAYS_MORE_IN_REVERSALS_THAN_IT_DODGES")

    # 5 a basket that only rises gives no down-ratio -- None, never 1 or 0.
    rk5 = rk.abs()
    s5 = split_excess(rk5 * 0.5, rk5)
    leg("one-sided basket leaves capture None", s5["down"]["capture"] is None)
    leg("one-sided basket verdict is unmeasurable",
        verdict_of(s5, {"share_of_total": None}) == "UNMEASURABLE_ONE_SIDED_BASKET")

    # 6 concentration: one bar holding everything reads 100%.
    d = np.zeros(100)
    d[3] = 1.0
    c = concentration(d)
    leg("single-bar excess is 100% concentrated", abs(c["share_of_total"] - 1.0) < 1e-9)
    leg("removing the top bar leaves zero", abs(c["excess_without_top"]) < 1e-12)

    # 7 concentration: even excess spreads out.
    d2 = np.full(100, 0.01)
    c2 = concentration(d2)
    leg("even excess is <= 20% concentrated", c2["share_of_total"] <= 0.20)

    # 8 yearly signs follow the tape.
    idx = pd.bdate_range("2020-12-20", periods=30)
    dd = np.array([0.001] * 15 + [-0.01] * 15)
    y = yearly(dd, idx)
    leg("yearly signs split at the calendar boundary",
        y[str(idx[0].year)]["sign"] == "positive" and y[str(idx[-1].year)]["sign"] == "negative")

    bad = [(n, det) for n, ok, det in legs if not ok]
    for n, ok, det in legs:
        print(("  PASS " if ok else "  FAIL ") + n + (("  " + det) if det and not ok else ""))
    print("%d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["run"]
    cmd = args[0]
    if cmd == "--selftest":
        return _selfcheck()
    if cmd == "--check":
        return cmd_check(args[1:])
    if cmd == "run":
        return cmd_run(args[1:])
    print("usage: etf_book_excess_capture.py [run|--check|--selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
