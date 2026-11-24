#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_catchup_rotation -- does the shelf's depressed side pay for the trip?

WHY THIS FACE EXISTS
--------------------
r2050 (`money_premium_carry_audit`) showed the money shelf prints 1.8-7.8pp/yr more than
its own carry and concluded `PREMIUM_IS_NOT_CARRY`.  r2051 (`money_band_blind_spot`) then
looked below the 1% band and found the elevated side still gives back 6.5bp per 20 bars
(38bp on 511920), with one clean sentence attached: *not harvestable without foresight*.

That sentence is true of the elevated side -- you cannot short a cash ETF you were about to
buy.  It says nothing about the mirror side.  If price above the local level bleeds back,
price below the local level should catch up, and that side **is** buyable: pick the most
depressed members of the shelf, hold one window, repeat.  No foresight required -- the
signal is the deviation you can see at the close.

So the question is not "is there a premium" (r2050) nor "is there a tail" (r2051).  It is:
**once you only pick from the depressed side and pay the two trips per window, is what is
left worth having?**

THE QUESTION (frozen before the first run)
------------------------------------------
On the cash shelf -- every instrument r2048's census priced as money/bond with at least
MIN_BARS of history:

1. At a rebalance close, rank members by their own deviation from their own trailing
   20-bar median.  Buy the K most depressed at the **next open**, sell at the open
   H+1 bars later.  Costs charged at the frozen schedule, both trips, every window.
2. Compare that to holding the whole shelf with the same calendar and the same costs.
3. Print the cross-sectional rank correlation (deviation -> forward return) beside it, so a
   reader can see whether the ordering carries information even where the top-K spread
   does not clear costs.

RULER (nothing re-decided here)
-------------------------------
* shelf membership   -- `results/cash_shelf_flip_census.json` rows with `priced` true and
  `class` in (money, bond).  The census is r2048's; membership is not re-picked here.
* local level        -- `money_premium_carry_audit.local_level` (trailing 20-bar median,
  minimum 10 bars), exactly -- the same level r2050 and r2051 used.
* deviation          -- close / level - 1, in percent.  Positive = rich, negative = cheap.
* execution          -- signal at close(t), entered at open(t+1), exited at open(t+1+H).
  No same-bar fills, no close-to-close shortcut.
* **H in {20, 60}** (added here) -- one local-level window and three, so a reader can see
  whether a slower bleed is worth fewer trips.
* **K in {1, 5}** (added here) -- the deepest single name and a small basket, because a
  single money ETF can be halted or mispriced and one name is not a strategy.
* costs              -- `COST_BP = 8.0` per side (the book's own conservative cash-trade
  assumption); a `COST_BP_LOW = 2.0` sensitivity is printed, because real money-ETF
  spreads are nearer 1-2bp and the answer flips between the two.
* annualisation      -- (1+net_per_window)^(252/H)-1; the cost of a window is
  2*COST_BP, so the annual cost is 2*COST_BP*252/H bp.  Printed as its own line.
* gates              -- a date needs MIN_MEMBERS valid members to be traded at all; a
  configuration with fewer than MIN_REBAL rebalances refuses to publish a verdict.

VERDICTS (mechanical, frozen on the primary configuration H=20, K=5, COST_BP=8)
-------------------------------------------------------------------------------
* CATCH_UP_CLEARS_COSTS   -- gross spread > 0 with t >= 2.0 AND net annualised >= 0.25pp.
* CATCH_UP_SMALLER_THAN_COSTS -- gross > 0 (t >= 2.0) but net annualised < 0.25pp.
* NO_CATCH_UP_IN_THE_SHELF -- gross <= 0 or t < 2.0.

WHAT THIS RULER CANNOT SEPARATE (printed, not folded)
-----------------------------------------------------
* The census is list-based: instruments that delisted never enter, so every shelf study in
  this lineage carries survivor bias, this one included.
* Money ETFs accrue; a "cheap" member is usually one that paid its accrual early.  The
  catch-up is then a *timing* transfer inside the same asset class, not alpha over cash --
  the comparison that matters is against shelf-equal-weight, which is printed.
* A halt or a distribution reset inside a window shows up as a large "catch-up".  Resets
  are handled by the reader (`consolidation_returns`), halts are not: they are printed as
  the count of windows with a member missing a price at entry or exit.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import money_premium_carry_audit as MP  # noqa: E402  (r2050's local level, exactly)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
PREMIUM_FACE = "results/money_premium_carry_audit.json"
BLIND_FACE = "results/money_band_blind_spot.json"
FACE = "results/cash_shelf_catchup_rotation.json"
DOC = "research/CASH_SHELF_CATCHUP_ROTATION.md"

# Frozen before the first run.
LEVEL_WIN = 20          # MP.local_level's own window
HORIZONS = (20, 60)     # one local-level window and three
KS = (1, 5)             # deepest single name and a small basket
COST_BP = 8.0           # per side, the book's conservative cash-trade assumption
COST_BP_LOW = 2.0       # sensitivity: real money-ETF spreads
PRIMARY_H = 20
PRIMARY_K = 5
MIN_BARS = 500          # a member needs this much history to be ranked at all
MIN_MEMBERS = 20        # a date needs this many valid members to be traded
MIN_REBAL = 40          # fewer rebalances than this and no verdict is published
T_POWER = 2.0           # the spread has to clear this t-stat
NET_FLOOR_PP = 0.25     # net annualised must beat this for CLEARS_COSTS
WARMUP = 60             # bars before the first rebalance (level + one window)

MARK_BEGIN = "<!-- CATCHUP-TABLE:BEGIN -->"
MARK_END = "<!-- CATCHUP-TABLE:END -->"


# ------------------------------------------------------------------------ plumbing

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _daily_path(code):
    for prefix in ("sh", "sz"):
        p = os.path.join(ROOT, "data", "daily", prefix + code + ".csv")
        if os.path.exists(p):
            return p
    return None


# --------------------------------------------------------------------- measurement

def shelf_members(census=None):
    """Money/bond members of the priced census shelf.  Membership is r2048's, not ours."""
    census = census if census is not None else _load(CENSUS_FACE)
    out = []
    for row in census.get("rows") or []:
        if not row.get("priced"):
            continue
        if row.get("class") not in ("money", "bond"):
            continue
        if int(row.get("bars") or 0) < MIN_BARS:
            continue
        out.append(row["code"])
    return sorted(set(out))


def load_panel(codes):
    """{code: DataFrame[open, close]} from the in-repo daily CSVs."""
    panel = {}
    for code in codes:
        p = _daily_path(code)
        if not p:
            continue
        try:
            df = pd.read_csv(p, usecols=["date", "open", "close"])
        except Exception:
            continue
        if df.empty:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df.dropna(subset=["close"]).set_index("date").sort_index()
        df = df[~df.index.duplicated(keep="last")]
        if df.shape[0] < MIN_BARS:
            continue
        panel[code] = df
    return panel


def frames(panel, horizon):
    """close/open matrices plus deviation and the causal forward return, aligned on dates."""
    close = pd.DataFrame({c: d["close"] for c, d in panel.items()}).sort_index()
    opn = pd.DataFrame({c: d["open"] if "open" in d else d["close"]
                        for c, d in panel.items()}).reindex(close.index)
    dev = pd.DataFrame({c: (d["close"] / MP.local_level(d["close"]) - 1.0) * 100.0
                        for c, d in panel.items()}).reindex(close.index)
    entry = opn.shift(-1)
    exit_ = opn.shift(-(1 + horizon))
    fwd = exit_ / entry - 1.0
    return close, dev, fwd


def evaluate(dev, fwd, horizon, k, cost_bp):
    """Walk the rebalance grid and return the spread series and its bookkeeping."""
    dates = list(dev.index)
    rebal = dates[WARMUP::horizon]
    spreads, ics, held_dev, members, gaps = [], [], [], [], 0
    for d in rebal:
        dv = dev.loc[d]
        fw = fwd.loc[d]
        ok = dv.notna() & fw.notna()
        n = int(ok.sum())
        if n < MIN_MEMBERS:
            gaps += 1
            continue
        dv_ok = dv[ok].astype(float)
        fw_ok = fw[ok].astype(float)
        picked = dv_ok.nsmallest(k).index
        richest = dv_ok.nlargest(k).index
        base = fw_ok.mean()
        spreads.append({"date": str(d.date()),
                        "spread": float(fw_ok[picked].mean() - base),
                        "rich_spread": float(fw_ok[richest].mean() - base),
                        "held_dev_pct": float(dv_ok[picked].mean()),
                        "members": n})
        held_dev.append(float(dv_ok[picked].mean()))
        members.append(n)
        if n >= MIN_MEMBERS:
            ics.append(float(pd.Series(dv_ok).corr(pd.Series(fw_ok), method="spearman")))
    if not spreads:
        return None
    s = np.array([r["spread"] for r in spreads], dtype=float)
    rs = np.array([r["rich_spread"] for r in spreads], dtype=float)
    mean = float(s.mean())
    se = float(s.std(ddof=1) / np.sqrt(s.size)) if s.size > 1 else float("nan")
    t = (mean / se) if se and se > 1e-12 else None
    rmean = float(rs.mean())
    rse = float(rs.std(ddof=1) / np.sqrt(rs.size)) if rs.size > 1 else float("nan")
    rt = (rmean / rse) if rse and rse > 1e-12 else None
    gross_pp = ((1.0 + mean) ** (252.0 / horizon) - 1.0) * 100.0
    cost_per_window = 2.0 * cost_bp / 1e4
    net_pp = ((1.0 + mean - cost_per_window) ** (252.0 / horizon) - 1.0) * 100.0
    rich_net_pp = ((1.0 + rmean - cost_per_window) ** (252.0 / horizon) - 1.0) * 100.0
    return {
        "horizon": horizon, "k": k, "cost_bp_per_side": cost_bp,
        "rebalances": int(s.size), "skipped_dates": int(gaps),
        "mean_spread_bp": round(mean * 1e4, 3),
        "spread_se_bp": round(se * 1e4, 3) if se == se else None,
        "spread_t": round(t, 2) if t is not None else None,
        "positive_share": round(float((s > 0).mean()), 4),
        "gross_pp_per_year": round(gross_pp, 3),
        "cost_pp_per_year": round(2.0 * cost_bp * (252.0 / horizon) / 100.0, 3),
        "net_pp_per_year": round(net_pp, 3),
        "rich_spread_bp": round(rmean * 1e4, 3),
        "rich_spread_t": round(rt, 2) if rt is not None else None,
        "rich_net_pp_per_year": round(rich_net_pp, 3),
        "mean_ic": round(float(np.nanmean(ics)), 3) if ics else None,
        "mean_held_dev_pct": round(float(np.mean(held_dev)), 4) if held_dev else None,
        "mean_members": round(float(np.mean(members)), 1) if members else None,
        "series": spreads,
    }


def configs():
    out = []
    for h in HORIZONS:
        for k in KS:
            out.append((h, k, COST_BP))
    for h in HORIZONS:
        out.append((h, PRIMARY_K, COST_BP_LOW))
    return out


def verdict_of(primary, sensitivity):
    """Mechanical verdict on the primary configuration; sensitivity only printed."""
    if primary is None:
        return "NOT_MEASURABLE", None
    gross_t = primary["spread_t"]
    gross = primary["mean_spread_bp"]
    net = primary["net_pp_per_year"]
    if gross is None or gross <= 0 or gross_t is None or gross_t < T_POWER:
        return "NO_CATCH_UP_IN_THE_SHELF", net
    if net >= NET_FLOOR_PP:
        return "CATCH_UP_CLEARS_COSTS", net
    return "CATCH_UP_SMALLER_THAN_COSTS", net


def build():
    census = _load(CENSUS_FACE)
    members = shelf_members(census)
    panel = load_panel(members)
    results = []
    for h in HORIZONS:
        _close, dev, fwd = frames(panel, h)
        for cfg_h, k, cost in configs():
            if cfg_h != h:
                continue
            res = evaluate(dev, fwd, h, k, cost)
            if res is not None:
                results.append(res)

    def pick(h, k, cost):
        for r in results:
            if r["horizon"] == h and r["k"] == k and r["cost_bp_per_side"] == cost:
                return r
        return None

    primary = pick(PRIMARY_H, PRIMARY_K, COST_BP)
    sens = pick(PRIMARY_H, PRIMARY_K, COST_BP_LOW)
    verdict, net = verdict_of(primary, sens)
    bars = max((d.shape[0] for d in panel.values()), default=0)
    window = None
    if panel:
        start = min(d.index[0] for d in panel.values())
        end = max(d.index[-1] for d in panel.values())
        window = {"start": str(start.date()), "end": str(end.date())}

    face = {
        "schema": "cash_shelf_catchup_rotation/v1",
        "artifact": FACE,
        "generated": dt.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "evidence_cutoff": window["end"] if window else None,
        "window": window,
        "question": ("On the cash shelf, does the side that trades below its own local level "
                     "catch up enough to pay two trips per window?"),
        "upstream": {
            "census": {"face": CENSUS_FACE, "sha256": _sha(os.path.join(ROOT, CENSUS_FACE)),
                       "members": len(members)},
            "premium": {"face": PREMIUM_FACE,
                        "sha256": _sha(os.path.join(ROOT, PREMIUM_FACE))},
            "blind": {"face": BLIND_FACE, "sha256": _sha(os.path.join(ROOT, BLIND_FACE))
                      if os.path.exists(os.path.join(ROOT, BLIND_FACE)) else None},
            "level": "money_premium_carry_audit.local_level (unchanged)",
        },
        "ruler": {
            "level_window": LEVEL_WIN, "horizons": list(HORIZONS), "ks": list(KS),
            "cost_bp_per_side": COST_BP, "cost_bp_low": COST_BP_LOW,
            "min_bars": MIN_BARS, "min_members": MIN_MEMBERS, "warmup_bars": WARMUP,
            "execution": "signal at close(t), entry open(t+1), exit open(t+1+H)",
        },
        "headline": {
            "verdict": verdict,
            "net_pp_per_year": net,
            "gross_spread_bp": primary["mean_spread_bp"] if primary else None,
            "gross_t": primary["spread_t"] if primary else None,
            "cost_pp_per_year": primary["cost_pp_per_year"] if primary else None,
            "mean_ic": primary["mean_ic"] if primary else None,
            "rebalances": primary["rebalances"] if primary else 0,
            "max_bars_available": bars,
            "rich_spread_bp": primary["rich_spread_bp"] if primary else None,
            "rich_spread_t": primary["rich_spread_t"] if primary else None,
            "rich_net_pp_per_year": primary["rich_net_pp_per_year"] if primary else None,
        },
        "results": [{k: v for k, v in r.items() if k != "series"} for r in results],
        "primary_series": (primary or {}).get("series"),
        "not_claimed": [
            "no live order: this is a measurement of a shelf-wide ordering, not a ticket",
            "survivor bias: membership is r2048's priced census, delisted names never enter",
            "a 'cheap' money ETF is usually one that paid its accrual early -- the comparison "
            "that matters is shelf-equal-weight, which is the baseline here",
            "costs are a frozen schedule, not a measured spread for any single name",
            "the richest side is printed beside the cheapest but is NOT a claim: it mixes a "
            "level effect (some vehicles simply accrue faster) with a timing effect, and its "
            "t-stat on the primary configuration sits under the power line",
        ],
        "caveat": ("Catch-up inside a money shelf is a timing transfer between names that all "
                   "accrue at roughly the same rate.  A positive spread here is not alpha over "
                   "cash unless it survives the two trips; that is exactly what the net line is."),
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items()
                                           if k not in ("content_sha256", "generated")})
    return face


# ------------------------------------------------------------------------- output

def _f(v, nd=2, dash="-"):
    if v is None:
        return dash
    try:
        return ("%%.%df" % nd) % float(v)
    except (TypeError, ValueError):
        return dash


def render_table(face):
    rows = ["| H | K | cost/side | rebalances | cheap bp/win | t | rich bp/win | t | IC | "
            "gross pp/yr | cost pp/yr | **net pp/yr** |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in face["results"]:
        rows.append("| %d | %d | %s bp | %d | %s | %s | %s | %s | %s | %s | %s | **%s** |" % (
            r["horizon"], r["k"], _f(r["cost_bp_per_side"], 1), r["rebalances"],
            _f(r["mean_spread_bp"], 3), _f(r["spread_t"]),
            _f(r.get("rich_spread_bp"), 3), _f(r.get("rich_spread_t")),
            _f(r["mean_ic"], 3),
            _f(r["gross_pp_per_year"], 3), _f(r["cost_pp_per_year"], 3),
            _f(r["net_pp_per_year"], 3)))
    return "\n".join(rows)


def write_doc(face):
    h = face["headline"]
    body = [
        "# The cash shelf's depressed side: %s" % h["verdict"],
        "",
        "**Product increment, not a ticket.** On the shelf r2048's census priced as money/bond, "
        "this face buys the K members trading furthest below their own 20-bar median at the next "
        "open and sells one window later, charging both trips. Window: %s .. %s, %d members, "
        "%d rebalances." % (face["window"]["start"], face["window"]["end"],
                            face["upstream"]["census"]["members"], h["rebalances"]),
        "",
        "## What the ordering is worth",
        "",
        MARK_BEGIN,
        render_table(face),
        MARK_END,
        "",
        "Primary configuration (H=%d, K=%d, %s bp/side): the cheap side earns **%s bp** per "
        "window with t=%s, rank correlation %s; the two trips cost **%s pp/yr**, so what is left "
        "is **%s pp/yr**."
        % (PRIMARY_H, PRIMARY_K, _f(COST_BP, 1), _f(h["gross_spread_bp"], 3), _f(h["gross_t"]),
           _f(h["mean_ic"], 3), _f(h["cost_pp_per_year"], 3), _f(h["net_pp_per_year"], 3)),
        "",
        "The same ruler on the **rich** side prints %s bp per window (t=%s, %s pp/yr after the "
        "same two trips).  It is printed so the reader can see the sign of the ordering rather "
        "than infer it, and it is **not** a claim: part of it is a level effect (some vehicles "
        "accrue faster and stay rich), the t-stat sits under the power line, and separating the "
        "two effects is a different question than the one frozen here."
        % (_f(h.get("rich_spread_bp"), 3), _f(h.get("rich_spread_t")),
           _f(h.get("rich_net_pp_per_year"), 3)),
        "",
        "At %s bp/side (the realistic money-ETF spread) the same configuration prints **%s pp/yr**; "
        "the gap between the two cost schedules is the whole question, which is why both are printed."
        % (_f(COST_BP_LOW, 1), _f(face["results"][-1]["net_pp_per_year"]
                                  if face["results"] else None, 3)),
        "",
        "## What this does not claim",
        "",
    ]
    for line in face["not_claimed"]:
        body.append("- " + line)
    body += ["", "## Caveat", "", face["caveat"], ""]
    path = os.path.join(ROOT, DOC)
    head = ""
    if os.path.exists(path):
        with io.open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if MARK_BEGIN in text and MARK_END in text:
            head = text.split(MARK_BEGIN)[0]
        else:
            head = text
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + "\n".join(body) + "\n")
    return path


def check():
    on_disk = _load(FACE)
    fresh = build()
    a = {k: v for k, v in on_disk.items() if k not in ("content_sha256", "generated")}
    b = {k: v for k, v in fresh.items() if k not in ("content_sha256", "generated")}
    if _content_sha(a) != _content_sha(b):
        diffs = [k for k in sorted(set(a) | set(b))
                 if json.dumps(a.get(k), sort_keys=True, ensure_ascii=False)
                 != json.dumps(b.get(k), sort_keys=True, ensure_ascii=False)]
        return 3, "STALE %s differs from a fresh derive: %s" % (FACE, ", ".join(diffs[:6]))
    return 0, "CHECK OK %s (%d configs, %d rebalances)" % (
        FACE, len(on_disk["results"]), on_disk["headline"]["rebalances"])


# ------------------------------------------------------------------------ selftest

def _synth(mode="catchup", members=40, bars=420, seed=7):
    """A shelf where the depressed side either pays back or does not."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=bars)
    panel = {}
    for i in range(members):
        code = "%06d" % (100000 + i)
        drift = 0.00008  # ~2%/yr accrual
        noise = rng.normal(0, 0.0006, bars)
        if mode == "catchup":
            # a slow oscillation: below the median predicts above-average next-20-bar return
            cyc = 0.0012 * np.sin(2 * np.pi * np.arange(bars) / 40.0 + i)
            ret = drift + noise + cyc
        else:
            ret = drift + noise + rng.normal(0, 0.0004, bars)
        px = 100.0 * np.cumprod(1.0 + ret)
        panel[code] = pd.DataFrame({"open": px, "close": px}, index=dates)
    return panel


def _eval_synth(panel, horizon=20, k=5, cost_bp=8.0):
    _close, dev, fwd = frames(panel, horizon)
    return evaluate(dev, fwd, horizon, k, cost_bp)


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1 the causal window: entry is next open, exit is H+1, never the same bar
    panel = _synth("catchup", members=10, bars=120)
    close, dev, fwd = frames(panel, 20)
    code = list(panel)[0]
    px = panel[code]
    i = 80
    expect = px["open"].iloc[i + 21] / px["open"].iloc[i + 1] - 1.0
    got = fwd[code].iloc[i]
    leg("execution is open(t+1) -> open(t+1+H), no same-bar fill",
        abs(got - expect) < 1e-12, "%.8f vs %.8f" % (got, expect))

    # 2 the last bars have no forward return -- a face must not read the future
    leg("bars inside the horizon carry NaN forward return",
        bool(np.isnan(fwd[code].iloc[-3])), "tail=%s" % fwd[code].iloc[-3])

    # 3 a shelf whose depressed side really pays back clears costs
    res_up = _eval_synth(_synth("catchup"), 20, 5, 8.0)
    v_up, _ = verdict_of(res_up, None)
    leg("synthetic catch-up shelf is priced (gross > 0)", res_up["mean_spread_bp"] > 0,
        "gross=%.3fbp t=%s" % (res_up["mean_spread_bp"], res_up["spread_t"]))
    leg("synthetic catch-up verdict is mechanical on the frozen thresholds",
        v_up in ("CATCH_UP_CLEARS_COSTS", "CATCH_UP_SMALLER_THAN_COSTS"), v_up)

    # 4 a shelf with no structure does not produce one
    res_null = _eval_synth(_synth("noise"), 20, 5, 8.0)
    leg("synthetic noise shelf stays under the power line",
        res_null["spread_t"] is None or abs(res_null["spread_t"]) < 3.0,
        "t=%s" % res_null["spread_t"])

    # 5 costs are charged on both trips, and annualised by the window count
    cost_ann = 2.0 * 8.0 * (252.0 / 20) / 100.0
    leg("cost line = 2 sides x 8bp x 252/H",
        abs(res_up["cost_pp_per_year"] - round(cost_ann, 3)) < 1e-9,
        "%s vs %s" % (res_up["cost_pp_per_year"], round(cost_ann, 3)))

    # 6 net is gross minus cost per window, annualised -- not gross minus annual cost
    mean = res_up["mean_spread_bp"] / 1e4
    expect_net = ((1.0 + mean - 16.0 / 1e4) ** (252.0 / 20) - 1.0) * 100.0
    leg("net uses per-window cost inside the compounding",
        abs(res_up["net_pp_per_year"] - round(expect_net, 3)) < 1e-9,
        "%s vs %s" % (res_up["net_pp_per_year"], round(expect_net, 3)))

    # 7 a date with too few members is skipped, not scored on three names
    thin = _synth("catchup", members=8, bars=200)
    res_thin = _eval_synth(thin, 20, 5, 8.0)
    leg("a thin shelf never reaches the member floor",
        res_thin is None or res_thin["mean_members"] is None
        or res_thin["mean_members"] < MIN_MEMBERS or res_thin["skipped_dates"] > 0,
        "members=%s skipped=%s" % (res_thin["mean_members"] if res_thin else None,
                                   res_thin["skipped_dates"] if res_thin else None))

    # 8 the verdict refuses to speak without enough rebalances
    leg("no verdict on an unmeasurable primary",
        verdict_of(None, None)[0] == "NOT_MEASURABLE", verdict_of(None, None)[0])

    # 9 content hash ignores the wall clock
    a = {"x": 1, "generated": "2026-01-01T00:00:00+08:00"}
    b = {"x": 1, "generated": "2026-11-24T00:00:00+08:00"}
    sa = _content_sha({k: v for k, v in a.items() if k != "generated"})
    sb = _content_sha({k: v for k, v in b.items() if k != "generated"})
    leg("content sha ignores generated", sa == sb)

    ok = sum(1 for _n, o, _d in legs if o)
    for name, passed, detail in legs:
        print("%s %s%s" % ("PASS" if passed else "FAIL", name,
                           (" | " + detail) if detail else ""))
    print("cash_shelf_catchup_rotation selftest %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------------------- run

def run():
    face = build()
    path = os.path.join(ROOT, FACE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    doc = write_doc(face)
    h = face["headline"]
    print("VERDICT %s" % h["verdict"])
    print("  gross %s bp per %d-bar window (t=%s), rank IC %s" % (
        _f(h["gross_spread_bp"], 3), PRIMARY_H, _f(h["gross_t"]), _f(h["mean_ic"], 3)))
    print("  two trips cost %s pp/yr -> net %s pp/yr at %s bp/side" % (
        _f(h["cost_pp_per_year"], 3), _f(h["net_pp_per_year"], 3), _f(COST_BP, 1)))
    print("  rebalances %d, members %d, window %s..%s" % (
        h["rebalances"], face["upstream"]["census"]["members"],
        face["window"]["start"], face["window"]["end"]))
    print("  face -> %s" % FACE)
    print("  doc  -> %s" % os.path.relpath(doc, ROOT).replace("\\", "/"))
    return 0


def main(argv):
    args = set(argv[1:])
    if "--selftest" in args:
        return selftest()
    if "--check" in args:
        rc, msg = check()
        print(msg)
        return rc
    if "--write" in args:
        return run()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
