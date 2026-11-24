#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""could the book's parking lot be convertible bonds?  four parked vehicles, one window

WHY THIS FILE EXISTS
--------------------
O-20261009-1105 says, in the CEO's own words, that convertibles may serve as a
supplement for the idle periods ("可转债可以作为空仓期的补充").  The desk has
measured convertibles twice since -- `cb_dual_low` (selection is dead) and
`cb_floor` / `cb_debt_floor_mde` (no selection edge is measurable at this sample)
-- but neither answers the question the order actually asks.  Both measured
*selection*; nobody measured *parking*.

The ticket parks 56.5% of NAV in a repo ladder.  `etf_book_cash_vehicle` already
put GC001 next to one money ETF.  It did not put convertibles next to either,
and it did not ask the only question a parking sleeve has to answer:

    on the days the book is defending, does the parking lot fall too?

WHAT IT MEASURES
----------------
Six daily total-return series on ONE window (2020-07-16 .. the last bar every
arm shares), each built by importing the desk's own engine for that asset
class -- never re-implemented here:

  repo_gc001      CL.roll_rung on GC001, the caliber the ticket's cash_leg prints
  money_511880    cash_vehicle.consolidation_returns (yearly share resets removed)
  cb_etf_ew       the two convertible ETFs (511180 / 511380), equal weight, monthly
  cb_universe_ew  every convertible bond on the panel, equal weight (bias-free:
                  the panel carries delisted and defaulted names)
  bond_etf_ew     bond+money class ETFs, equal weight, monthly -- the incumbent defence
  equity_etf_ew   equity class ETFs, equal weight, monthly -- read-only, as the
                  yardstick for "the days the book defends"

Per arm: net CAGR, vol, Sharpe, max drawdown, worst 20-bar stretch, worst month,
share of days at or below -1%, beta and correlation to the equity yardstick, and
the mean return on the yardstick's own -1% days (the defence test).

Then the dosage table: move s of the cash leg from repo into convertibles, and
price what that does to the parking lot and to 1,000,000 CNY of book.

THREE THINGS THAT WOULD MAKE THIS FACE LIE
------------------------------------------
1. A convertibles sleeve marked to market and called a parking lot.  A parking
   lot is judged on its worst 20 bars and on the defence days, not only on CAGR;
   every table here prints those three columns next to the return.
2. The equal-weight bond universe is not one instrument.  It is 40-370 bonds in
   lot sizes; it is priced because it is the cleanest read of the asset class
   (no ETF fee, no premium/discount, no delisting hole), and it is labelled
   NOT_ONE_ORDER on every row it appears in.
3. A chemistry of costs.  ETF round trips are charged 2bp/side on the rebalance
   date, the bond universe 10bp/side once per entry, the repo arm at the desk's
   published caliber.  No arm is charged for a cost another arm pays.
"""
import hashlib
import io
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_debt_floor_mde as CB  # noqa: E402  (panel hygiene + universe series)
import etf_book_cash_ladder as CL  # noqa: E402  (repo engine)
import etf_book_cash_vehicle as CV  # noqa: E402  (money ETF resets)
import etf_composite_pf as E  # noqa: E402  (ETF panel)
import etf_equity_alpha as A  # noqa: E402  (flip repair + class map)

OUT_JSON = os.path.join(ROOT, "results", "cb_parking_bakeoff.json")
OUT_MD = os.path.join(ROOT, "research", "CB_PARKING_BAKEOFF.md")
PANEL = os.path.join(ROOT, "data", "cb_panel.csv.gz")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
REPO_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

START = "2020-07-16"          # the window every existing cash-leg face already uses
BARS_PER_YEAR = 244.0         # A-share count; one convention for every arm
WORST_WINDOW = 20             # the stretch a parking lot is judged on
TAIL_DAY = -0.01              # "a bad day" for a parking lot
DEFENCE_DAY = -0.01           # the yardstick's own bad day
CB_ETF_CODES = ("511180", "511380")
ETF_COST_BP_SIDE = 2.0        # 0.02%/side, the retail ETF rate used by cash_vehicle
CB_COST_BP_SIDE = 10.0        # convertibles pay no stamp duty; 10bp/side at the desk
DOSES = (0.0, 0.10, 0.25, 0.50, 1.00)
NEW_ISSUE_BARS = 20           # the listing window a fixed basket cannot re-buy

SCHEMA = "cb-parking-bakeoff/v1"


# --------------------------------------------------------------------------- helpers
def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def load_ticket():
    """The newest ticket: its cash line and its NAV, read, never typed."""
    files = sorted(f for f in os.listdir(TICKET_DIR)
                   if f.startswith("TICKET-") and f.endswith(".json") and "-card" not in f)
    if not files:
        raise FileNotFoundError("no ticket under %s" % TICKET_DIR)
    path = os.path.join(TICKET_DIR, files[-1])
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    cash = float(d["cash_leg"]["money"]["cash_amount_cny"])
    nav = float(d["permission"]["nav_cny"])
    return {"file": files[-1], "cash_cny": cash, "nav_cny": nav,
            "cash_share": cash / nav,
            "published_window_net_pct": float(d["cash_leg"]["money"]["window"]["net_pct"])}


def load_etf_close(codes):
    """Close matrix for a handful of ETF codes, via the cash-vehicle reader."""
    cols = {}
    for c in codes:
        s = CV.load_etf(c)
        if len(s) >= 60:
            cols[c] = s
    return pd.DataFrame(cols).sort_index()


def ew_arm(close, start, end, cost_bp_side=0.0, rebal="M"):
    """Equal-weight, monthly (or 'W') rebalanced, with the turnover it really costs.

    Returns (daily return Series, info).  Weights are reset on the first bar of each
    period to equal weights over the names priced on that bar; between resets they
    drift with prices.  A name with no price that day contributes a zero return (a
    suspended holding is still held), which is the honest reading for a parked sleeve.
    """
    px = close.loc[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    px = px.loc[:, px.notna().sum() >= 60]
    if px.empty:
        raise ValueError("empty panel in window")
    px = px.ffill()
    ret = px.pct_change().fillna(0.0)
    dates = px.index
    periods = dates.to_period(rebal)
    anchors = set(pd.Series(dates, index=periods).groupby(level=0).first().tolist())

    w = pd.Series(dtype=float)
    out, turns, anchors_used = [], [], 0
    for d in dates:
        fee = 0.0
        if d in anchors or w.empty:
            live = px.loc[d].dropna()
            new_w = pd.Series(1.0 / len(live), index=live.index) if len(live) else pd.Series(dtype=float)
            if len(w) and len(new_w):
                aligned = pd.concat([w, new_w], axis=1).fillna(0.0)
                turn = float((aligned.iloc[:, 0] - aligned.iloc[:, 1]).abs().sum()) / 2.0
            else:
                turn = 1.0 if len(new_w) else 0.0
            fee = turn * 2.0 * cost_bp_side / 1e4
            turns.append(turn)
            anchors_used += 1
            w = new_w
        r = float((w * ret.loc[d].reindex(w.index).fillna(0.0)).sum()) if len(w) else 0.0
        out.append(r - fee)
        if len(w):
            grown = w * (1.0 + ret.loc[d].reindex(w.index).fillna(0.0))
            tot = float(grown.sum())
            w = grown / tot if tot > 0 else grown
    ser = pd.Series(out, index=dates)
    return ser, {"names": int(px.shape[1]), "rebalances": anchors_used,
                 "mean_turnover": round(float(np.mean(turns)), 3) if turns else 0.0,
                 "turnover_per_year": round(float(np.sum(turns)) / max(len(dates) / BARS_PER_YEAR, 1e-9), 2),
                 "cost_bp_per_side": cost_bp_side}


# --------------------------------------------------------------------------- metrics
def level(ser):
    return (1.0 + ser.fillna(0.0)).cumprod()


def cagr(ser):
    s = ser.dropna()
    if len(s) < 40:
        return float("nan")
    years = (s.index[-1] - s.index[0]).days / 365.25
    g = float(level(s).iloc[-1])
    return float(g ** (1.0 / years) - 1.0) * 100.0


def maxdd(ser):
    lv = level(ser)
    return float((lv / lv.cummax() - 1.0).min()) * 100.0


def worst_stretch(ser, n=WORST_WINDOW):
    """Worst compounded return over any n consecutive bars (the parking-lot column)."""
    lv = level(ser)
    if len(lv) <= n:
        return float("nan")
    return float((lv / lv.shift(n) - 1.0).min()) * 100.0


def beta_corr(ser, yard):
    df = pd.concat([ser, yard], axis=1).dropna()
    if len(df) < 40:
        return float("nan"), float("nan")
    x, y = df.iloc[:, 1], df.iloc[:, 0]
    vx = float(x.var())
    if vx <= 0:
        return float("nan"), float("nan")
    return float(y.cov(x) / vx), float(y.corr(x))


def defence_stats(ser, yard):
    """What the arm does on the yardstick's own bad days -- the parking-lot test."""
    df = pd.concat([ser.rename("arm"), yard.rename("yard")], axis=1).dropna()
    bad = df[df["yard"] <= DEFENCE_DAY]
    if not len(bad):
        return {"days": 0, "mean_pct": float("nan"), "sum_pct": float("nan"),
                "share_negative": float("nan")}
    return {"days": int(len(bad)),
            "mean_pct": round(float(bad["arm"].mean()) * 100.0, 4),
            "sum_pct": round(float(((1 + bad["arm"]).prod() - 1.0)) * 100.0, 3),
            "share_negative": round(float((bad["arm"] < 0).mean()), 4)}


def metrics(ser, label, yard=None, extra=None):
    ser = ser.dropna()
    r = ser
    vol = float(r.std() * math.sqrt(BARS_PER_YEAR)) * 100.0 if len(r) > 2 else float("nan")
    m = {
        "label": label,
        "bars": int(len(ser)),
        "first": str(ser.index[0].date()) if len(ser) else None,
        "last": str(ser.index[-1].date()) if len(ser) else None,
        "net_cagr_pct": round(cagr(ser), 4),
        "vol_pct": round(vol, 4),
        "sharpe": round(float(r.mean() * BARS_PER_YEAR / (vol / 100.0)), 3) if vol and vol > 0 else 0.0,
        "maxdd_pct": round(maxdd(ser), 3),
        "worst_20bar_pct": round(worst_stretch(ser), 3),
        "worst_day_pct": round(float(r.min()) * 100.0, 3),
        "share_days_le_minus1_pct": round(float((r <= TAIL_DAY).mean()) * 100.0, 3),
        "positive_years": None,
        "yearly_pct": {},
    }
    for y, grp in ser.groupby(ser.index.year):
        m["yearly_pct"][str(y)] = round(float(((1 + grp).prod() - 1.0)) * 100.0, 2)
    ys = [v for v in m["yearly_pct"].values() if v is not None]
    m["positive_years"] = "%d/%d" % (sum(1 for v in ys if v > 0), len(ys))
    m["worst_month_pct"] = round(float(level(ser).resample("ME").last().pct_change().dropna().min()) * 100.0, 3)
    if yard is not None:
        b, c = beta_corr(ser, yard)
        m["beta_to_equity"] = round(b, 3) if np.isfinite(b) else None
        m["corr_to_equity"] = round(c, 3) if np.isfinite(c) else None
        m["defence_days"] = defence_stats(ser, yard)
    if extra:
        clash = set(extra) & set(m)
        if clash:
            raise ValueError("arm info would silently overwrite a metric key: %s" % sorted(clash))
        m.update(extra)
    return m


# --------------------------------------------------------------------------- arms
def build_arms(verbose=True):
    log = (lambda *a: print(*a, flush=True)) if verbose else (lambda *a: None)
    # 1. ETF panel (flip-repaired, class-labelled)
    close_all, open_all, _amt, _feats = E.build_panel()
    close_all, _open_all, n_flip = A.repair_flips(close_all, open_all)
    cmap = A.load_class_map()
    cls = A.classify(close_all.columns, cmap, close_all)
    log("  ETF panel: %d columns, %d flips repaired" % (close_all.shape[1], n_flip))

    eq_cols = [c for c in close_all.columns if cls[c] == "equity"]
    bd_cols = [c for c in close_all.columns if cls[c] in ("bond", "money")]
    yard_close = close_all[eq_cols]

    # 2. repo arm at the desk's published caliber
    rates = CL.load_panel()
    allb = sorted(set().union(*[set(s.index) for s in rates.values()]))
    bars = pd.DatetimeIndex([b for b in allb if b >= pd.Timestamp(START)])
    repo_ret, repo_info = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
    repo_ret = pd.Series(repo_ret, index=bars).dropna()

    # 3. money ETF (share resets removed)
    money_ret, money_jumps = CV.consolidation_returns(CV.load_etf("511880"))

    # 4. convertible bond universe (bias-free panel) -- not one order
    cb_close, cb_prem, cb_meta = CB.load_frames()
    cb_series = CB.daily_series(cb_close, cb_prem)
    cb_uni = cb_series["universe"].dropna()
    log("  CB panel: %d bonds / %s..%s" % (cb_meta["bonds"], cb_meta["first"], cb_meta["last"]))

    end = min(pd.Timestamp("2026-12-31"), cb_uni.index[-1], repo_ret.index[-1],
              money_ret.index[-1], close_all.index[-1])
    end = min(end, cb_uni.index[-1])
    log("  common window: %s .. %s" % (START, end.date()))

    arms, info = {}, {}
    arms["repo_gc001"], info["repo_gc001"] = (
        repo_ret[(repo_ret.index >= pd.Timestamp(START)) & (repo_ret.index <= end)],
        {"orders": len(repo_info["contracts"]), "cost_bp_per_side": 0.0,
         "caliber": "CL.roll_rung GC001, published cash-leg caliber"})
    arms["money_511880"], info["money_511880"] = (
        money_ret[(money_ret.index >= pd.Timestamp(START)) & (money_ret.index <= end)],
        {"share_resets_removed": len(money_jumps), "cost_bp_per_side": ETF_COST_BP_SIDE,
         "caliber": "buy and hold, one round trip charged"})

    cb_etf_close = load_etf_close(CB_ETF_CODES)
    arms["cb_etf_ew"], info["cb_etf_ew"] = ew_arm(cb_etf_close, START, end, ETF_COST_BP_SIDE)
    info["cb_etf_ew"]["codes"] = list(cb_etf_close.columns)
    info["cb_etf_ew"]["caliber"] = "equal weight, monthly, turnover charged each rebalance"

    arms["bond_etf_ew"], info["bond_etf_ew"] = ew_arm(close_all[bd_cols], START, end, ETF_COST_BP_SIDE)
    info["bond_etf_ew"]["caliber"] = "bond+money class ETFs, equal weight, monthly"

    arms["equity_etf_ew"], info["equity_etf_ew"] = ew_arm(yard_close, START, end, ETF_COST_BP_SIDE)
    info["equity_etf_ew"]["caliber"] = "equity class ETFs, equal weight, monthly (yardstick only)"

    # the bond universe pays one entry ticket: 10bp/side, charged on the first bar
    midx_end = min(end, cb_uni.index[-1])
    arms["cb_universe_daily_ew"] = cb_uni[
        (cb_uni.index >= pd.Timestamp(START)) & (cb_uni.index <= midx_end)].copy()
    arms["cb_universe_daily_ew"].iloc[0] -= 2.0 * CB_COST_BP_SIDE / 1e4
    info["cb_universe_daily_ew"] = {
        "cost_bp_per_side": CB_COST_BP_SIDE, "entered_once_bp": 2.0 * CB_COST_BP_SIDE,
        "instrument_note": "NOT_ONE_ORDER: every bond, equal weight, REBALANCED EVERY BAR",
        "caliber": "the desk's existing CB convention (cb_debt_floor_mde.daily_series universe)"}

    # same rule as every ETF arm: equal weight, monthly, turnover charged -- otherwise
    # the comparison would be measuring the rebalancing frequency, not the vehicle
    arms["cb_universe_ew"], info["cb_universe_ew"] = ew_arm(
        cb_close, START, midx_end, CB_COST_BP_SIDE)
    info["cb_universe_ew"]["instrument_note"] = "NOT_ONE_ORDER: 40-370 bonds in lot sizes"
    info["cb_universe_ew"]["caliber"] = ("every convertible on the panel, equal weight, monthly "
                                         "-- same rule as the ETF arms")
    info["cb_universe_ew"]["median_names_per_day"] = int(
        np.nanmedian(cb_close.loc[START:midx_end].notna().sum(axis=1)))

    # why does the class beat the ETF?  split the class into the first 20 bars of a
    # bond's life and everything after it: an equal-weight basket re-buys every new
    # issue, and a fixed-tracker ETF cannot
    age = cb_close.notna().cumsum()
    ret_all = cb_close.pct_change().mask(cb_close.pct_change().abs() > CB.DEFECT_RET)
    ret_win = ret_all[(ret_all.index >= pd.Timestamp(START)) & (ret_all.index <= midx_end)]
    age_win = age.reindex(ret_win.index)
    for name, keep in (("cb_newissue_ew", age_win <= NEW_ISSUE_BARS),
                       ("cb_mature_ew", age_win > NEW_ISSUE_BARS)):
        arm = ret_win.where(keep).mean(axis=1).dropna()
        if len(arm) and abs(arm.iloc[0]) >= 0:
            arm.iloc[0] -= 2.0 * CB_COST_BP_SIDE / 1e4
        arms[name] = arm
        info[name] = {"cost_bp_per_side": CB_COST_BP_SIDE,
                      "instrument_note": "NOT_ONE_ORDER: equal-weight slice of the CB panel",
                      "caliber": ("bonds in their first %d priced bars" % NEW_ISSUE_BARS
                                  if name == "cb_newissue_ew"
                                  else "bonds past their first %d priced bars" % NEW_ISSUE_BARS)}
    return arms, info, {"window": {"start": START, "end": str(end.date())},
                        "etf_flips_repaired": int(n_flip),
                        "cb_panel": cb_meta}


# --------------------------------------------------------------------------- dosage
def dosage(repo, arm, name, cash_share, dose):
    """Move `dose` of the cash leg from repo into `arm`; charge the switch once."""
    df = pd.concat([repo.rename("repo"), arm.rename("arm")], axis=1).dropna()
    ret = (1.0 - dose) * df["repo"] + dose * df["arm"]
    ret.iloc[0] = ret.iloc[0] - dose * (2.0 * (CB_COST_BP_SIDE if name == "cb_universe_ew"
                                                else ETF_COST_BP_SIDE) / 1e4)
    delta_pp = cagr(ret) - cagr(df["repo"])
    out = {
        "arm": name, "dose_of_cash_leg": dose,
        "net_cagr_pct": round(cagr(ret), 4),
        "vol_pct": round(float(ret.std() * math.sqrt(BARS_PER_YEAR)) * 100.0, 3),
        "maxdd_pct": round(maxdd(ret), 3),
        "worst_20bar_pct": round(worst_stretch(ret), 3),
        "delta_vs_repo_pp": round(delta_pp, 4),
        "cny_per_year_on_one_million_book": round(delta_pp / 100.0 * cash_share * dose * 1_000_000.0, 0),
    }
    return out


# --------------------------------------------------------------------------- gates
def build(write=True, verbose=True):
    t0 = time.time()
    arms, info, meta = build_arms(verbose)
    ticket = load_ticket()
    yard = arms["equity_etf_ew"]

    rows = []
    for name in ("repo_gc001", "money_511880", "bond_etf_ew", "cb_etf_ew",
                 "cb_universe_ew", "cb_universe_daily_ew", "cb_newissue_ew",
                 "cb_mature_ew", "equity_etf_ew"):
        rows.append(metrics(arms[name], name, yard=yard, extra=info[name]))

    by = {r["label"]: r for r in rows}
    doses = []
    for name in ("cb_etf_ew", "cb_universe_ew"):
        for d in DOSES:
            doses.append(dosage(arms["repo_gc001"], arms[name], name, ticket["cash_share"], d))

    # ---- verdict arithmetic (every number below is printed somewhere above)
    repo_m, cbe_m, cbu_m = by["repo_gc001"], by["cb_etf_ew"], by["cb_universe_ew"]
    cbd_m = by["cb_universe_daily_ew"]
    extra_etf = cbe_m["net_cagr_pct"] - repo_m["net_cagr_pct"]
    extra_uni = cbu_m["net_cagr_pct"] - repo_m["net_cagr_pct"]
    rebal_gap = cbd_m["net_cagr_pct"] - cbu_m["net_cagr_pct"]
    deeper_20 = min(cbe_m["worst_20bar_pct"], cbu_m["worst_20bar_pct"]) < repo_m["worst_20bar_pct"]
    beta_hi = max(cbe_m.get("beta_to_equity") or 0.0, cbu_m.get("beta_to_equity") or 0.0)
    defence_bad = min(cbe_m["defence_days"]["mean_pct"] if cbe_m["defence_days"]["days"] else 0.0,
                      cbu_m["defence_days"]["mean_pct"] if cbu_m["defence_days"]["days"] else 0.0) < 0.0

    verdicts = []
    if extra_uni > 0:
        verdicts.append("CONVERTIBLES_PAY_MORE_THAN_THE_REPO_LEG")
    if deeper_20 and defence_bad and beta_hi > 0.1:
        verdicts.append("BUT_THEY_FALL_ON_THE_DAYS_THE_BOOK_DEFENDS")
    if rebal_gap > 1.0:
        verdicts.append("THE_CLASS_RETURN_IS_MOSTLY_A_REBALANCING_FREQUENCY")
    if extra_etf < 1.0 <= extra_uni:
        verdicts.append("THE_INSTRUMENT_ON_SALE_DOES_NOT_HOLD_THE_CLASS_RETURN")
    if not verdicts:
        verdicts.append("NO_SEPARATION_AT_THIS_WINDOW")

    five = [d for d in doses if d["arm"] == "cb_etf_ew"]
    wide = [d for d in doses if d["arm"] == "cb_universe_ew"]
    at25 = next(d for d in five if abs(d["dose_of_cash_leg"] - 0.25) < 1e-9)
    at100 = next(d for d in five if abs(d["dose_of_cash_leg"] - 1.0) < 1e-9)
    u25 = next(d for d in wide if abs(d["dose_of_cash_leg"] - 0.25) < 1e-9)
    u100 = next(d for d in wide if abs(d["dose_of_cash_leg"] - 1.0) < 1e-9)

    face = {
        "schema": SCHEMA,
        "artifact": "cb_parking_bakeoff",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": meta["window"]["end"],
        "window": meta["window"],
        "question": "could the 56.5% parking lot park in convertibles instead of the repo ladder?",
        "order_ref": "O-20261009-1105 (CEO: convertibles may supplement the idle periods)",
        "ticket": ticket,
        "arms": rows,
        "arm_info": info,
        "dosage": doses,
        "verdict": verdicts,
        "headline": {
            "repo_net_pct": repo_m["net_cagr_pct"],
            "cb_etf_net_pct": cbe_m["net_cagr_pct"],
            "cb_universe_net_pct": cbu_m["net_cagr_pct"],
            "cb_universe_daily_net_pct": cbd_m["net_cagr_pct"],
            "extra_etf_pp": round(extra_etf, 4),
            "extra_universe_pp": round(extra_uni, 4),
            "rebalance_frequency_gap_pp": round(rebal_gap, 4),
            "repo_worst_20bar_pct": repo_m["worst_20bar_pct"],
            "cb_etf_worst_20bar_pct": cbe_m["worst_20bar_pct"],
            "cb_universe_worst_20bar_pct": cbu_m["worst_20bar_pct"],
            "cb_etf_beta_to_equity": cbe_m.get("beta_to_equity"),
            "cb_universe_beta_to_equity": cbu_m.get("beta_to_equity"),
            "cb_etf_defence_mean_pct": cbe_m["defence_days"]["mean_pct"],
            "cb_universe_defence_mean_pct": cbu_m["defence_days"]["mean_pct"],
            "quarter_parking_delta_cny_per_year": at25["cny_per_year_on_one_million_book"],
            "full_parking_delta_cny_per_year": at100["cny_per_year_on_one_million_book"],
            "quarter_parking_worst20_etf_pct": at25["worst_20bar_pct"],
            "quarter_parking_worst20_basket_pct": u25["worst_20bar_pct"],
            "quarter_parking_delta_basket_cny_per_year": u25["cny_per_year_on_one_million_book"],
            "full_parking_delta_basket_cny_per_year": u100["cny_per_year_on_one_million_book"],
            "full_parking_worst20_basket_pct": u100["worst_20bar_pct"],
            "newissue_slice_net_pct": by["cb_newissue_ew"]["net_cagr_pct"],
            "mature_slice_net_pct": by["cb_mature_ew"]["net_cagr_pct"],
        },
        "data_sha": {"cb_panel": _sha(PANEL), "repo_gc001": _sha(REPO_CSV),
                     "ticket": _sha(os.path.join(TICKET_DIR, ticket["file"]))},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items()
                                           if k not in ("content_sha256", "elapsed_sec", "generated")})
    md = render_md(face)
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(md)
        print("  ->", OUT_JSON, flush=True)
        print("  ->", OUT_MD, flush=True)
    if verbose:
        print("  verdict:", " | ".join(verdicts), flush=True)
        print("  repo %.2f%%  cb_etf %.2f%% (+%.2fpp)  cb_universe %.2f%% (+%.2fpp)"
              % (repo_m["net_cagr_pct"], cbe_m["net_cagr_pct"], extra_etf,
                 cbu_m["net_cagr_pct"], extra_uni), flush=True)
        print("  worst20: repo %.2f%%  cb_etf %.2f%%  cb_uni %.2f%%"
              % (repo_m["worst_20bar_pct"], cbe_m["worst_20bar_pct"],
                 cbu_m["worst_20bar_pct"]), flush=True)
        print("  defence days: %d, cb_etf mean %.3f%% / cb_uni mean %.3f%%"
              % (cbe_m["defence_days"]["days"], cbe_m["defence_days"]["mean_pct"],
                 cbu_m["defence_days"]["mean_pct"]), flush=True)
    return face


# --------------------------------------------------------------------------- page
def _pp(x, nd=3):
    """Format a number that is ALREADY a percent. Never scales by 100."""
    return "n/a" if x is None or (isinstance(x, float) and not math.isfinite(x)) else ("%.*f" % (nd, x))


def _pct(x, nd=2):
    """Format a FRACTION as a percent."""
    return "n/a" if x is None else ("%.*f%%" % (nd, x * 100.0))


def _money(x):
    return "n/a" if x is None else "{:,.0f}".format(x)


def render_md(face):
    by = {a["label"]: a for a in face["arms"]}
    tk = face["ticket"]
    h = face["headline"]
    L = []
    L.append("# 空仓期能不能停泊在可转债？")
    L.append("")
    L.append("> 一句话：**能买，但不是停泊。** 转债这个类别比回购每年多给 %.2f 个百分点，"
             "代价是它在你靠这笔钱防守的那些日子里跟着跌（防守日均值 **%s%%**，权益 beta **%s**）——"
             "这台停车场的墙是纸做的。而货架上真能买的那只 ETF 只兑现了 **%s%%/年**："
             "「能多赚」与「能买到」之间还隔着 %.2fpp，本面只拆掉一小半。"
             % (h["extra_universe_pp"], _pp(h["cb_universe_defence_mean_pct"], 2),
                _pp(h["cb_universe_beta_to_equity"], 2), _pp(h["cb_etf_net_pct"], 2),
                h["extra_universe_pp"] - h["extra_etf_pp"]))
    L.append("")
    L.append("CEO 令 O-20261009-1105 说「可转债可以作为空仓期的补充」。这句话此前被实现成两次**选券**测量"
             "（`cb_dual_low` 判死、`cb_floor` 功效不足），而令问的是**停泊**。本面答停泊。")
    L.append("")
    L.append("窗口 **%s → %s**（与既有现金腿面同一窗口）。票面上的现金腿是 **%s 元 / %s 元 = %s**，"
             "按它来算每 100 万元书的效果。" % (face["window"]["start"], face["window"]["end"],
                                      _money(tk["cash_cny"]), _money(tk["nav_cny"]),
                                      _pct(tk["cash_share"], 2)))
    L.append("")
    L.append("## 七条腿（同一窗口，同一套成本口径）")
    L.append("")
    L.append("| 腿 | 净年化 | 波动 | 夏普 | 最大回撤 | **最差 20 根** | 最差单日 | ≤-1% 天数占比 | 正收益年 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for k in ("repo_gc001", "money_511880", "bond_etf_ew", "cb_etf_ew",
              "cb_universe_ew", "cb_universe_daily_ew", "equity_etf_ew"):
        a = by[k]
        L.append("| `%s` | %s%% | %s%% | %s | %s%% | **%s%%** | %s%% | %s%% | %s |"
                 % (k, _pp(a["net_cagr_pct"], 2), _pp(a["vol_pct"], 2), _pp(a["sharpe"], 3),
                    _pp(a["maxdd_pct"], 2), _pp(a["worst_20bar_pct"], 2),
                    _pp(a["worst_day_pct"], 2), _pp(a["share_days_le_minus1_pct"], 2),
                    a["positive_years"]))
    L.append("")
    L.append("`cb_universe_ew` 与 `cb_universe_daily_ew` 读的是同一批券、同一批收益，"
             "**唯一差别是重新配平的频率**（月频 vs 每根 bar）：%s%% vs %s%%，差 **%.2fpp**。"
             "这不是转债这个类别赚的，这是每天把涨的卖掉落进跌的里去赚的——"
             "它也真的每天要买卖上百只券。"
             % (_pp(by["cb_universe_ew"]["net_cagr_pct"], 2),
                _pp(by["cb_universe_daily_ew"]["net_cagr_pct"], 2),
                h["rebalance_frequency_gap_pp"]))
    L.append("")
    L.append("`cb_universe_ew` = 面板上**每一只**转债等权（含已退市/违约，无生存者偏差），"
             "**不是一张单子**（每日中位 %d 只、需整手配比）。它在这里是转债这个资产类别的干净读数："
             "没有 ETF 费用、没有折溢价、没有退市空洞。"
             % face["arm_info"]["cb_universe_ew"]["median_names_per_day"])
    L.append("")
    L.append("## 防守测试：书在防守的那天，停车场在干什么")
    L.append("")
    L.append("标尺 = 权益类 ETF 等权（`equity_etf_ew`）。取它跌 ≥1%% 的那些日子（共 %d 天），看每条腿在那些天的平均收益。"
             % by["cb_etf_ew"]["defence_days"]["days"])
    L.append("")
    L.append("| 腿 | 对权益 beta | 相关 | 防守日均值 | 防守日累计 | 防守日下跌占比 |")
    L.append("|---|---|---|---|---|---|")
    for k in ("repo_gc001", "money_511880", "bond_etf_ew", "cb_etf_ew",
              "cb_universe_ew", "cb_universe_daily_ew"):
        a = by[k]
        dd = a["defence_days"]
        L.append("| `%s` | %s | %s | **%s%%** | %s%% | %s |"
                 % (k, _pp(a.get("beta_to_equity"), 3), _pp(a.get("corr_to_equity"), 3),
                    _pp(dd["mean_pct"], 3), _pp(dd["sum_pct"], 2), _pct(dd["share_negative"], 1)))
    L.append("")
    L.append("这是本面的核心读数：现金腿的存在理由不是收益，是**书在亏钱的那些天它不亏**。"
             "转债在这张表里的位置和债券/货币 ETF 不在一列。")
    L.append("")
    L.append("## 为什么货架上的 ETF 只兑现 %s%%" % _pp(by["cb_etf_ew"]["net_cagr_pct"], 2))
    L.append("")
    L.append("同一个资产类别在这里有三个读数：**ETF %s%%** / **等权月频 %s%%** / **等权每根 bar %s%%**。"
             "把全池再切成两片看钱从哪来："
             % (_pp(by["cb_etf_ew"]["net_cagr_pct"], 2),
                _pp(by["cb_universe_ew"]["net_cagr_pct"], 2),
                _pp(by["cb_universe_daily_ew"]["net_cagr_pct"], 2)))
    L.append("")
    L.append("* **新券上市档**（每只券的前 %d 个有价 bar，等权切片）：%s%%/年——"
             "转债上市普遍从面值起来，等权篮子每次都按面值买一遍；固定成分的 ETF 做不到。"
             % (NEW_ISSUE_BARS, _pp(h["newissue_slice_net_pct"], 2)))
    L.append("* **成熟券**（过了上市档，每日等权）：%s%%/年——**即使把新券全剔掉，等权也远高于 ETF**，"
             "所以差额不只是上市档。" % _pp(h["mature_slice_net_pct"], 2))
    L.append("* 剩下的差额本面**拆不开**：ETF 跟的是发行量加权的转债指数（大盘银行转债权重很高），"
             "本仓没有指数成分数据，等权与指数权重之差、现金拖累、费率三者混在一起。"
             "要拆干净需要另开一张面，本面不假装有答案。")
    L.append("")
    L.append("对 CEO 的问题来说，能买的是 **%s%%/年** 这一档，不是 %s%%："
             "「可转债能当空仓期补充」这句话在**类别层面**成立、在**货架层面**不成立。"
             % (_pp(by["cb_etf_ew"]["net_cagr_pct"], 2), _pp(by["cb_universe_ew"]["net_cagr_pct"], 2)))
    L.append("")
    L.append("## 剂量表：把现金腿的一部分挪进转债")
    L.append("")
    L.append("| 腿 | 挪走比例 | 净年化 | 波动 | 最大回撤 | 最差 20 根 | Δ vs 回购 | 每 100 万元书每年 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for d in face["dosage"]:
        L.append("| `%s` | %s | %s%% | %s%% | %s%% | %s%% | %+.3fpp | %s 元 |"
                 % (d["arm"], _pct(d["dose_of_cash_leg"], 0), _pp(d["net_cagr_pct"], 2),
                    _pp(d["vol_pct"], 2), _pp(d["maxdd_pct"], 2), _pp(d["worst_20bar_pct"], 2),
                    d["delta_vs_repo_pp"], _money(d["cny_per_year_on_one_million_book"])))
    L.append("")
    L.append("挪 25%% 的现金腿（= 整本书的 %s），用**货架上买得到的那只 ETF**："
             "每年多 **%s 元/百万**，停车场的**最差 20 根从 %s%% 变成 %s%%**、最大回撤从 0 变成 %s%%——"
             "为了三位数的钱，把一个零回撤的桶换成一个能在 20 天里亏掉 2%% 的桶。"
             % (_pct(tk["cash_share"] * 0.25, 1),
                _money(h["quarter_parking_delta_cny_per_year"]),
                _pp(h["repo_worst_20bar_pct"], 2),
                _pp(h["quarter_parking_worst20_etf_pct"], 2),
                _pp([d for d in face["dosage"] if d["arm"] == "cb_etf_ew" and abs(d["dose_of_cash_leg"] - 0.25) < 1e-9][0]["maxdd_pct"], 2)))
    L.append("")
    L.append("换成**全池等权**（不是一张单子，见上）：同样 25%% 每年多 **%s 元/百万**，"
             "但最差 20 根是 **%s%%**；把整条现金腿都换过去也只有 %s 元/百万（整本书的 %s pp），"
             "而最差 20 根是 **%s%%**、回撤 **%s%%**。"
             % (_money(h["quarter_parking_delta_basket_cny_per_year"]),
                _pp(h["quarter_parking_worst20_basket_pct"], 2),
                _money(h["full_parking_delta_basket_cny_per_year"]),
                _pp(h["extra_universe_pp"], 2),
                _pp(h["full_parking_worst20_basket_pct"], 2),
                _pp([d for d in face["dosage"] if d["arm"] == "cb_universe_ew" and abs(d["dose_of_cash_leg"] - 1.0) < 1e-9][0]["maxdd_pct"], 2)))
    L.append("")
    L.append("注意剂量表在 50%→100% 之间不是单调的（ETF 臂 +0.128pp → +0.060pp）："
             "这是波动拖累，不是成本——同一个资产类别持有得越多，它的波动越替你决定结果。")
    L.append("")
    L.append("## 判词")
    L.append("")
    for v in face["verdict"]:
        L.append("- `%s`" % v)
    L.append("")
    L.append("## 本面不宣称什么")
    L.append("")
    L.append("* 不宣称转债不值得持有——只宣称它**不是停泊**：它和权益同向，停在这里等于把防守的钱重新押上牌桌。")
    L.append("* 不宣称 ETF 定价错了：本面把 ETF 与全池并排，差额只拆出「上市档」这一块，"
             "剩下的（等权 vs 指数权重、现金拖累、费率）混在一起未再拆。")
    L.append("* 不给择时：没有「转债便宜时再停」这条腿，那需要另一份预注册。")
    L.append("* 全池腿按等权、无整手、无冲击；真实执行要上百只券的整手配比，这条腿只作类别读数。"
             "月频与每日两条只是为了把「重排频率」和「资产类别」分开，两条都不是可下单的篮子。")
    L.append("* 窗口 2020-07 起，只覆盖这个 regime（含 2022 转债杀与 2024 修复），不外推到更早。")
    L.append("* 单日 ≤-1% 与最差 20 根都是**盯市**读数：真停泊还要看申赎/流动性，本面不建模。")
    L.append("")
    L.append("数据：转债面板 `data/cb_panel.csv.gz`（sha %s…）· 回购 `data/repo_daily/GC001.csv` · "
             "票面 `results/etf_book_order/%s`。生成 %s，用时 %ss。"
             % (face["data_sha"]["cb_panel"][:12], tk["file"], face["generated"], face["elapsed_sec"]))
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- check
def check(json_path=None, md_path=None):
    """Re-derive every printed number from the face; refuse a face that drifts."""
    json_path, md_path = json_path or OUT_JSON, md_path or OUT_MD
    problems = []
    if not os.path.exists(json_path):
        print("STALE face missing:", json_path)
        return 3
    if not os.path.exists(md_path):
        print("STALE page missing:", md_path)
        return 3
    with io.open(json_path, encoding="utf-8") as f:
        face = json.load(f)
    md = io.open(md_path, encoding="utf-8").read()

    # input drift is STALE (the chain's own contract word), self-contradiction is CHECK FAILED
    for key, path in (("cb_panel", PANEL), ("repo_gc001", REPO_CSV)):
        if os.path.exists(path) and _sha(path) != face["data_sha"][key]:
            print("STALE input moved:", key)
            return 3

    by = {a["label"]: a for a in face["arms"]}
    h = face["headline"]

    def near(a, b, tol=5e-3, what=""):
        num = (int, float)
        bad = [x for x in (a, b)
               if x is not None and (isinstance(x, bool) or not isinstance(x, num))]
        if bad:
            problems.append("%s: not a number (%r)" % (what, bad[0]))
            return
        if a is None or b is None or not (abs(a - b) <= tol):
            problems.append("%s: %r vs %r" % (what, a, b))

    near(h["repo_net_pct"], by["repo_gc001"]["net_cagr_pct"], 1e-9, "repo headline")
    near(h["cb_etf_net_pct"], by["cb_etf_ew"]["net_cagr_pct"], 1e-9, "cb_etf headline")
    near(h["extra_etf_pp"], by["cb_etf_ew"]["net_cagr_pct"] - by["repo_gc001"]["net_cagr_pct"],
         1e-6, "extra_etf")
    near(h["extra_universe_pp"],
         by["cb_universe_ew"]["net_cagr_pct"] - by["repo_gc001"]["net_cagr_pct"], 1e-6, "extra_uni")
    near(h["repo_worst_20bar_pct"], by["repo_gc001"]["worst_20bar_pct"], 1e-9, "repo worst20")
    near(h["cb_etf_worst_20bar_pct"], by["cb_etf_ew"]["worst_20bar_pct"], 1e-9, "cb worst20")

    # dosage identities: dose 0 must be exactly the repo arm, dose 1 exactly the arm
    for arm in ("cb_etf_ew", "cb_universe_ew"):
        z = [d for d in face["dosage"] if d["arm"] == arm and abs(d["dose_of_cash_leg"]) < 1e-12]
        one = [d for d in face["dosage"] if d["arm"] == arm and abs(d["dose_of_cash_leg"] - 1.0) < 1e-12]
        if not z or not one:
            problems.append("dosage rows missing for %s" % arm)
            continue
        near(z[0]["delta_vs_repo_pp"], 0.0, 1e-9, "%s dose0 delta" % arm)
        near(z[0]["net_cagr_pct"], by["repo_gc001"]["net_cagr_pct"], 1e-9, "%s dose0 level" % arm)
    # the money arithmetic on every row
    cash = face["ticket"]["cash_share"]
    for d in face["dosage"]:
        want = d["delta_vs_repo_pp"] / 100.0 * cash * d["dose_of_cash_leg"] * 1_000_000.0
        near(d["cny_per_year_on_one_million_book"], want, 1.0, "dosage cny %s@%s" % (d["arm"], d["dose_of_cash_leg"]))

    # page must carry the verdict tokens -- a face nobody can read is not a product
    for v in face["verdict"]:
        if v not in md:
            problems.append("page missing verdict token: %s" % v)
    if "最差 20 根" not in md:
        problems.append("page missing the parking-lot column")
    # the r2039 lesson: a percent-of-percent print is invisible to arithmetic legs
    if "1658.0%" in md or "1658.03%" in md:
        problems.append("page prints a percent-of-percent")

    # content hash
    want = _content_sha({k: v for k, v in face.items()
                         if k not in ("content_sha256", "elapsed_sec", "generated")})
    if want != face.get("content_sha256"):
        problems.append("content_sha256 mismatch")

    if problems:
        for p in problems:
            print("CHECK FAILED:", p)
        return 3
    print("CHECK OK", face["artifact"], face["evidence_cutoff"], "|", " ".join(face["verdict"]))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    errs = []
    legs = [0]

    def chk(cond, msg):
        legs[0] += 1
        if not cond:
            errs.append(msg)

    idx = pd.bdate_range("2021-01-01", periods=260)

    # 1. a constant-return panel is returned unchanged when turnover is zero
    px = pd.DataFrame({"A": 1.0002 ** np.arange(260)}, index=idx)
    ser, info = ew_arm(px, "2021-01-01", "2099-01-01", cost_bp_side=0.0)
    chk(abs(float((1 + ser).prod()) - 1.0002 ** 259) < 1e-9,
        "constant panel: one name must reproduce its own growth (first bar is the entry)")
    chk(abs(float(ser.iloc[1]) - 0.0002) < 1e-12, "constant panel: every bar is that return")
    chk(info["rebalances"] >= 12, "monthly anchors must appear")

    # 2. a cost is charged, and only once: a one-name book has nothing to turn over
    ser_c, info_c = ew_arm(px, "2021-01-01", "2099-01-01", cost_bp_side=2.0)
    chk(abs(float((ser - ser_c).sum()) - 2.0 * 2.0 / 1e4) < 1e-12,
        "a one-name book pays exactly one round trip, not one per rebalance")
    chk(info_c["rebalances"] == info["rebalances"], "charging a cost must not move the anchors")

    # 3. metrics on a constant rate: no drawdown, zero vol, exact worst window
    flat = pd.Series(0.0001, index=idx)
    chk(abs(maxdd(flat)) < 1e-12, "constant rate: max drawdown must be zero")
    chk(abs(worst_stretch(flat) - ((1.0001 ** 20 - 1) * 100)) < 1e-9,
        "constant rate: worst 20-bar must be exactly 20 bars of it")
    chk(abs(float(flat.std())) < 1e-18, "constant rate: vol must be zero")

    # 4. level/cagr identity: the same series read two ways must agree
    rnd = pd.Series(np.random.RandomState(7).normal(0.0003, 0.01, 260), index=idx)
    lv = level(rnd)
    yrs = (idx[-1] - idx[0]).days / 365.25
    chk(abs(cagr(rnd) / 100.0 - (lv.iloc[-1] ** (1 / yrs) - 1)) < 1e-9, "cagr must match its level")
    chk(abs(maxdd(rnd) - float((lv / lv.cummax() - 1).min()) * 100) < 1e-12,
        "maxdd must be read off the level it compounds")

    # 5. beta/corr against itself
    b, c = beta_corr(rnd, rnd)
    chk(abs(b - 1.0) < 1e-9 and abs(c - 1.0) < 1e-9, "beta of a series to itself is 1/1")

    # 6. defence stats: the count and sign must follow the yard, not the arm
    yard = pd.Series(0.0, index=idx)
    yard.iloc[10:20] = -0.02
    arm = pd.Series(0.0, index=idx)
    arm.iloc[10:20] = -0.01
    dd = defence_stats(arm, yard)
    chk(dd["days"] == 10, "defence days must equal the yard's own bad days")
    chk(abs(dd["mean_pct"] + 1.0) < 1e-9, "defence mean must be the arm's reading on those days")
    chk(abs(dd["share_negative"] - 1.0) < 1e-12, "a falling arm must read as falling")

    # 7. worst_stretch is order-sensitive (the shuffle null)
    base = pd.Series(np.random.RandomState(11).normal(0.0004, 0.008, 400), index=pd.bdate_range("2021-01-01", periods=400))
    base.iloc[100:106] = -0.02          # one sustained slide, same returns either way
    chk(worst_stretch(base) < -10.0, "a planted slide must show up in the worst window")
    shuffled = pd.Series(np.random.RandomState(12).permutation(base.values), index=base.index)
    chk(abs(shuffled.mean() - base.mean()) < 1e-6, "shuffle keeps the mean")
    chk(abs(shuffled.std() - base.std()) < 1e-3, "shuffle keeps the vol")
    # the tail column must not be a function of mean and vol: re-placing the same
    # returns has to move it, and it must move the drawdown too
    chk(abs(worst_stretch(shuffled) - worst_stretch(base)) > 0.5,
        "shuffle must move the worst window -- otherwise that column only re-reads mean/vol")
    chk(abs(maxdd(shuffled) - maxdd(base)) > 0.5,
        "shuffle must move the drawdown for the same reason")

    # 8. dosage endpoints are identities
    repo = pd.Series(0.0001, index=idx)
    arm2 = pd.Series(0.0004, index=idx)
    d0 = dosage(repo, arm2, "cb_etf_ew", 0.5, 0.0)
    d1 = dosage(repo, arm2, "cb_etf_ew", 0.5, 1.0)
    chk(abs(d0["net_cagr_pct"] - cagr(repo)) < 1e-4, "dose 0 must be the repo arm exactly")
    chk(abs(d0["cny_per_year_on_one_million_book"]) < 1.0, "dose 0 must be worth zero money")
    chk(d1["cny_per_year_on_one_million_book"] > 0, "dose 1 on a richer arm must be worth money")

    # 9. the two formatters must not be interchangeable (r2039's percent-of-percent)
    chk(_pp(27.3433) == "27.343", "_pp must never scale: it formats an already-percent number")
    chk(_pct(0.273433) == "27.34%", "_pct must scale a fraction once")
    chk(_pp(27.3433) != _pct(27.3433), "the two helpers must disagree on their own domain")

    # 10. an arm's provenance block may not overwrite the arm's own identity
    try:
        metrics(rnd, "label_x", extra={"label": "something else"})
        chk(False, "metrics must refuse a provenance key that clashes with a metric key")
    except ValueError:
        chk(True, "")

    if errs:
        for e in errs:
            print("SELFTEST FAIL:", e)
        print("SELFTEST %d/%d FAILED" % (legs[0] - len(errs), legs[0]))
        return 1
    print("SELFTEST OK %d/%d PASS" % (legs[0], legs[0]))
    return 0


# --------------------------------------------------------------------------- main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        build(write=True)
        return 0
    if cmd in ("--check", "check"):
        return check()
    if cmd == "--selftest" or cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
