"""Where does the ETF book's uninvested sleeve actually get financed, and what is the tenor
choice worth?

r1255 wired the observed 1-day repo into the beta overlay and reported 2.088%/yr, but it
carried two assumptions a product cannot keep:

  1. the cash sleeve always rolls the 1-DAY tenor -- a real cash desk picks the tenor off
     the curve, and the 28/14-day points usually pay more than overnight;
  2. rolling is cost-free -- exchange repo charges a commission per contract, and rolling
     252 times a year is not free even at 0.001% per roll.

This module prices six cash legs on the same observed panel, all causal, all with the same
commissions schedule:

  gc001        always the 1-day GC contract (the r1255 baseline, reproduced exactly)
  short_pick   best of GC 1/3/4/7 each time a contract matures
  best_gc      best of all eight GC tenors (1..182) each time -- may lock for half a year
  ladder3      three equal rungs on GC007/GC014/GC028, each rolling its own tenor
  ladder4      four equal rungs on GC001/GC007/GC014/GC028
  best_dual    best of GC+R tenors (the Shenzhen leg as an alternate venue)

Mechanics that are not negotiable (each has a selftest):
  * a contract is never exited early -- once bought, cash is locked to its maturity bar,
    even if a much better rate prints the next day;
  * the rate is the quote at the CLOSE of the entry bar, so no same-day lookahead;
  * the maturity interest is rate/100 x calendar days / 365, i.e. Friday's 1-day contract
    earns three days, which is where a 252-day model of a 365-day market goes wrong;
  * a missing quote accrues nothing and is counted, never silently back-filled;
  * commission is charged per contract at entry, per the exchange schedule in FEE_BP.

The panel is `data/repo_daily/*.csv` (11 tenors, refreshed by the bm-a lane). Its last bar
is disclosed in the output: if the panel is behind the equity panel the cash leg is marked
stale rather than quietly ffilled.

Exploratory: no preregistration, no verdict, no ledger booking.

Usage:
  python scripts/etf_book_cash_ladder.py --selftest
  python scripts/etf_book_cash_ladder.py [--fee=0]
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_phase_beta_window as B  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(BASE, "data", "repo_daily")
OUT_PATH = os.path.join(BASE, "results", "etf_book_cash_ladder.json")
TICKET_DIR = os.path.join(BASE, "results", "etf_book_cash_ladder")
BW_PATH = os.path.join(BASE, "results", "etf_phase_beta_window.json")

# (file stem, tenor in calendar days, venue)
TENORS = (
    ("GC001", 1, "SH"), ("GC003", 3, "SH"), ("GC004", 4, "SH"), ("GC007", 7, "SH"),
    ("GC014", 14, "SH"), ("GC028", 28, "SH"), ("GC091", 91, "SH"), ("GC182", 182, "SH"),
    ("R-001", 1, "SZ"), ("R-003", 3, "SZ"), ("R-007", 7, "SZ"),
)

# Shanghai/Shenzhen exchange repo commission, in bp of notional, charged once per contract
# at entry: 1d 0.001%, 2d 0.002%, 3d 0.003%, 4d 0.004%, 7d 0.005%, 14d 0.01%, 28d 0.02%,
# 91d 0.03%, 182d 0.03% of face value. ASSUMPTION, not re-verified against a broker page in
# this window -- every number here can be re-derived with --fee=0.
FEE_BP = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4, 7: 0.5, 14: 1.0, 28: 2.0, 91: 3.0, 182: 3.0}

GC_NAMES = tuple(n for n, _, v in TENORS if v == "SH")
SHORT_NAMES = ("GC001", "GC003", "GC004", "GC007")
CAPPED_NAMES = ("GC001", "GC003", "GC004", "GC007", "GC014", "GC028")
LADDERS = {
    "ladder3": ("GC007", "GC014", "GC028"),
    "ladder4": ("GC001", "GC007", "GC014", "GC028"),
}
WINDOW_START = "2020-07-16"      # the beta-overlay window of r1254/r1255
MEAN_K_BETA020 = 0.541           # r1255 grid, expanding estimator, target 0.20


# ---------------------------------------------------------------------------------------
# panel
# ---------------------------------------------------------------------------------------
def load_panel(panel_dir=PANEL_DIR, bars=None):
    """{name: Series of annualised close (%) indexed by that tenor's own trading date}."""
    out = {}
    for name, _, _ in TENORS:
        p = os.path.join(panel_dir, name + ".csv")
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p)
        d = pd.to_datetime(df["date"])
        s = pd.Series(df["close"].astype(float).to_numpy(), index=d)
        s = s[~s.index.duplicated(keep="last")].sort_index()
        out[name] = s
    if bars is not None and out:
        idx = pd.DatetimeIndex(bars)
        out = {k: v.reindex(v.index.union(idx)).ffill().reindex(idx) for k, v in out.items()}
    return out


def tenor_of(name):
    return next(t for n, t, _ in TENORS if n == name)


def fee_bp(name, fees=None):
    fees = FEE_BP if fees is None else fees
    t = tenor_of(name)
    return float(fees.get(t, 0.0))


# ---------------------------------------------------------------------------------------
# one rung = a rolling repo contract, never exited early
# ---------------------------------------------------------------------------------------
def roll_rung(bars, rates, pick, fees=None, name=None):
    """Simulate one fully-invested repo rung over `bars`.

    `pick(i)` returns the contract name chosen from the quote known at bar i's close;
    with `name` given the rung rolls that single tenor instead.

    Returns (ret, info): `ret` is a per-bar fractional total return (interest credited on
    the step that ENDS at that bar, commission charged on the bar the contract is bought),
    `info` carries the contract list and diagnostics.
    """
    bars = pd.DatetimeIndex(bars)
    n = len(bars)
    ret = np.zeros(n, dtype=float)
    contracts, missing, rolls = [], 0, {k: 0 for k in rates}
    i = 0
    while i < n - 1:
        nm = name if name is not None else pick(i)
        r = np.nan
        if nm in rates:
            v = rates[nm].get(bars[i], np.nan)
            if v is not None and np.isfinite(v):
                r = float(v)
            else:
                missing += 1
        if not np.isfinite(r):
            ret[i] -= fee_bp(nm, fees) / 1e4 if nm else 0.0
            i += 1
            continue
        k = tenor_of(nm)
        target = bars[i] + pd.Timedelta(days=k)
        j = i + 1
        while j < n - 1 and bars[j] < target:
            j += 1
        days = int((bars[j] - bars[i]).days)
        contracts.append({"name": nm, "tenor": k, "entry": str(bars[i].date()),
                          "exit": str(bars[j].date()), "days": days, "rate_pct": r,
                          "open_at_cutoff": bool(bars[j] < target)})
        total = r / 100.0 * days / 365.0
        span = 0
        for s in range(i + 1, j + 1):
            span += int((bars[s] - bars[s - 1]).days)
        span = span or 1
        for s in range(i + 1, j + 1):
            ret[s] += total * (int((bars[s] - bars[s - 1]).days) / float(span))
        ret[i] -= fee_bp(nm, fees) / 1e4
        rolls[nm] = rolls.get(nm, 0) + 1
        i = j
    return pd.Series(ret, index=bars), {"contracts": contracts, "missing": missing,
                                        "rolls": rolls}


def pick_best(rates, universe, fees=None, i=None, bars=None):
    """Highest quoted rate among `universe` at bar `i`; ties -> shortest tenor, then name."""
    def _pick(idx):
        cand = []
        for nm in universe:
            if nm not in rates:
                continue
            v = rates[nm].get(bars[idx], np.nan)
            if v is None or not np.isfinite(v):
                continue
            cand.append((float(v), -tenor_of(nm), nm))
        if not cand:
            return universe[0]
        return max(cand)[2]
    return _pick


def ladder(bars, rates, members, fees=None):
    """Equal-weight rungs, each rolling its own fixed tenor; staggered by construction."""
    w = 1.0 / len(members)
    ret = pd.Series(0.0, index=pd.DatetimeIndex(bars))
    per = {}
    for nm in members:
        r, info = roll_rung(bars, rates, None, fees=fees, name=nm)
        ret = ret.add(r * w, fill_value=0.0)
        per[nm] = {"weight": round(w, 4), "n_contracts": len(info["contracts"]),
                   "ann_pct": round(cagr_pct(r, bars), 4)}
    return ret, per


# ---------------------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------------------
def cagr_pct(ret, bars):
    """Annualised (geometric, actual calendar days) total return in percent."""
    bars = pd.DatetimeIndex(bars)
    nav = float(np.prod(1.0 + ret.to_numpy()))
    days = int((bars[-1] - bars[0]).days) or 1
    return (nav ** (365.0 / days) - 1.0) * 100.0


def liquidity_stats(info, bars, n_rungs=1):
    """How often cash comes back, and how long it can be stuck.

    Repo cash is never "free intraday": once a contract is bought the money is gone until
    its maturity bar. What a treasurer actually needs to know is (a) the longest stretch
    with no maturity at all and (b) the biggest slice that can be raised on one bar.
    """
    bars = pd.DatetimeIndex(bars)
    share = pd.Series(0.0, index=bars)
    per_rung = 1.0 / float(n_rungs)
    for c in info["contracts"]:
        d = pd.Timestamp(c["exit"])
        if d in share.index:
            share.loc[d] += per_rung
    mat = [d for d in bars if share.loc[d] > 0]
    prev, longest = bars[0], 0
    for d in mat:
        longest = max(longest, int((d - prev).days))
        prev = d
    return {
        "share_of_bars_with_a_maturity": round(float((share > 0).mean()), 4),
        "longest_gap_without_any_maturity_days": int(longest),
        "max_slice_raisable_on_one_bar": round(float(share.max()), 4),
        "max_locked_days": max([c["days"] for c in info["contracts"]] or [0]),
    }


def quarter_end_panel(rates, bars):
    """Mean quote on the last three trading days of Mar/Jun/Sep/Dec vs everything else."""
    bars = pd.DatetimeIndex(bars)
    qe = set()
    by_q = {}
    for d in bars:
        by_q.setdefault((d.year, (d.month - 1) // 3), []).append(d)
    for _, ds in by_q.items():
        qe.update(ds[-3:])
    out = {}
    for nm in rates:
        s = rates[nm].dropna()
        s = s[(s.index >= bars[0]) & (s.index <= bars[-1])]
        if not len(s):
            continue
        m_qe = float(s[[d in qe for d in s.index]].mean()) if any(
            d in qe for d in s.index) else None
        m_ot = float(s[[d not in qe for d in s.index]].mean())
        out[nm] = {"tenor": tenor_of(nm),
                   "mean_all_pct": round(float(s.mean()), 3),
                   "mean_quarter_end_pct": round(m_qe, 3) if m_qe is not None else None,
                   "mean_other_pct": round(m_ot, 3),
                   "max_single_day_pct": round(float(s.max()), 2),
                   "max_day": str(s.idxmax().date())}
    return out


# ---------------------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------------------
def _rates_from(bars, value, names=None):
    names = names or [n for n, _, _ in TENORS]
    idx = pd.DatetimeIndex(bars)
    return {n: pd.Series(float(value), index=idx) for n in names}


def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[ok] %s %s" % (name, extra))
        else:
            print("[FAIL] %s %s" % (name, extra))

    # weekday business-day calendar 2021 (no holidays) -- 260 bars
    bars = pd.bdate_range("2021-01-04", "2021-12-31")
    flat = _rates_from(bars, 3.65)

    # leg 1: a 1-day roll on a flat quote compounds to the EFFECTIVE annual rate (a daily
    # quote of 3.65% reinvested every day is worth more than 3.65% a year), less commission
    r1, i1 = roll_rung(bars, flat, None, name="GC001")
    gross = cagr_pct(r1, bars)
    n_rolls = len(i1["contracts"])
    eff = ((1.0 + 3.65 / 100.0 / 365.0) ** 365 - 1.0) * 100.0
    want = eff - n_rolls * 0.1 / 100.0
    chk("leg1 1-day roll nets the effective rate minus commission",
        abs(gross - want) < 0.02, "net=%.3f want=%.3f eff=%.3f rolls=%d"
        % (gross, want, eff, n_rolls))

    # leg 2: Friday's 1-day contract earns three days
    f = pd.DatetimeIndex(["2021-01-08", "2021-01-11", "2021-01-12"])
    rf = _rates_from(f, 3.65)
    r2, i2 = roll_rung(f, rf, None, fees={}, name="GC001")
    want2 = 3.65 / 100.0 * 3 / 365.0
    chk("leg2 weekend gap pays three days",
        abs(float(r2.iloc[1]) - want2) < 1e-15, "mon=%.8f want=%.8f"
        % (float(r2.iloc[1]), want2))

    # leg 3: no early exit -- a spike inside a 28-day contract changes nothing
    spike = {n: s.copy() for n, s in flat.items()}
    spike["GC001"].iloc[5:20] = 60.0
    spike["GC014"].iloc[5:20] = 60.0
    a3, i3 = roll_rung(bars, flat, None, name="GC028")
    b3, _ = roll_rung(bars, spike, None, name="GC028")
    chk("leg3 a live contract is never abandoned", float(np.max(np.abs(
        a3.to_numpy() - b3.to_numpy()))) < 1e-15,
        "maxdiff=%.1e" % float(np.max(np.abs(a3.to_numpy() - b3.to_numpy()))))

    # leg 4: an inverted curve makes the selector take the shortest tenor every time
    inv = {n: pd.Series(4.0 - 0.02 * tenor_of(n), index=bars)
           for n in [x for x, _, _ in TENORS]}
    r4, i4 = roll_rung(bars, inv, pick_best(inv, GC_NAMES, bars=bars))
    chk("leg4 inverted curve picks 1-day", all(c["tenor"] == 1 for c in i4["contracts"]),
        "tenors=%s" % sorted({c["tenor"] for c in i4["contracts"]}))

    # leg 5: causality -- rewriting the future cannot move an earlier contract
    fut = {n: s.copy() for n, s in flat.items()}
    for n in fut:
        fut[n].iloc[100:] = 9.0
    a5 = roll_rung(bars, flat, pick_best(flat, GC_NAMES, bars=bars))[1]["contracts"]
    b5 = roll_rung(bars, fut, pick_best(fut, GC_NAMES, bars=bars))[1]["contracts"]
    same = [c for c in a5 if c["entry"] < str(bars[100].date())] == \
           [c for c in b5 if c["entry"] < str(bars[100].date())]
    chk("leg5 no lookahead before the rewrite", same,
        "n=%d" % len([c for c in a5 if c["entry"] < str(bars[100].date())]))

    # leg 6: on a flat curve every ladder nets about the same as the 1-day roll
    r6, per6 = ladder(bars, flat, ("GC001", "GC007", "GC014", "GC028"))
    chk("leg6 flat curve: ladder == 1-day roll within 3bp",
        abs(cagr_pct(r6, bars) - gross) < 0.03,
        "ladder=%.3f roll=%.3f" % (cagr_pct(r6, bars), gross))

    # leg 7: ladder weights are exactly 1/n and the rung list is complete
    chk("leg7 ladder weights sum to one",
        abs(sum(v["weight"] for v in per6.values()) - 1.0) < 1e-12,
        "w=%s" % [v["weight"] for v in per6.values()])

    # leg 8: commission is charged and scales with the tenor's schedule
    r8, _ = roll_rung(bars, flat, None, fees={}, name="GC001")
    chk("leg8 fees are real", cagr_pct(r1, bars) < cagr_pct(r8, bars) - 0.1,
        "with=%.3f without=%.3f" % (cagr_pct(r1, bars), cagr_pct(r8, bars)))

    # leg 9: a missing quote accrues nothing and is counted
    holed = {n: s.copy() for n, s in flat.items()}
    holed["GC001"].iloc[3] = np.nan
    _, i9 = roll_rung(bars, holed, None, name="GC001")
    chk("leg9 missing quote is counted, not faked", i9["missing"] >= 1,
        "missing=%d" % i9["missing"])

    # leg 10: an over-long tenor at the cutoff is flagged open, not silently closed
    short_bars = pd.bdate_range("2021-01-04", periods=30)
    r10, i10 = roll_rung(short_bars, _rates_from(short_bars, 3.0), None, name="GC182")
    chk("leg10 contract past the cutoff is flagged open",
        i10["contracts"] and all(c["open_at_cutoff"] for c in i10["contracts"]),
        "n=%d" % len(i10["contracts"]))

    # leg 11: the 1-day leg reproduces r1255's repo_daily_cash accrual exactly
    real = B.load_repo_rates()
    real = real[(real.index >= "2021-01-01") & (real.index <= "2021-12-31")]
    rb = real.index
    r11, _ = roll_rung(rb, {"GC001": real}, None, fees={}, name="GC001")
    old, miss_old = B.repo_daily_cash(rb, real)
    d11 = float(np.max(np.abs(r11.to_numpy() - old.to_numpy())))
    chk("leg11 1-day rung reproduces the r1255 cash leg", d11 < 1e-15, "maxdiff=%.1e" % d11)

    # leg 12: the maturity bar is the first bar at or after t+k calendar days
    b12 = pd.DatetimeIndex(["2021-01-04", "2021-01-05", "2021-01-11", "2021-01-12"])
    r12, i12 = roll_rung(b12, _rates_from(b12, 3.0), None, fees={}, name="GC007")
    c0 = i12["contracts"][0]
    chk("leg12 maturity snaps to the first bar past t+k",
        c0["entry"] == "2021-01-04" and c0["exit"] == "2021-01-11" and c0["days"] == 7,
        "%s->%s %dd" % (c0["entry"], c0["exit"], c0["days"]))

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


# ---------------------------------------------------------------------------------------
def main():
    if "--selftest" in sys.argv:
        return selftest()
    fees = FEE_BP
    for a in sys.argv[1:]:
        if a.startswith("--fee="):
            f = float(a.split("=", 1)[1])
            fees = {k: f for k in FEE_BP}
    t_all = time.time()

    close_path = os.path.join(BASE, "results", "etf_composite_pf.json")
    panel_json = {}
    if os.path.exists(close_path):
        with open(close_path, encoding="utf-8") as fh:
            panel_json = json.load(fh)
    book_cutoff = panel_json.get("evidence_cutoff")

    raw = load_panel()
    if not raw:
        print("FATAL: no repo panel under data/repo_daily")
        return 2
    idx = None
    for s in raw.values():
        idx = s.index if idx is None else idx.union(s.index)
    idx = idx[(idx >= WINDOW_START)]
    rates = load_panel(bars=idx)
    stale_days = None
    if book_cutoff:
        stale_days = len(idx[(idx > pd.Timestamp(book_cutoff))])
        if pd.Timestamp(book_cutoff) > idx[-1]:
            stale_days = int(len(pd.bdate_range(idx[-1], pd.Timestamp(book_cutoff)))) - 1
    print("repo panel %s .. %s (%d bars) | book cutoff %s | stale bars=%s"
          % (idx[0].date(), idx[-1].date(), len(idx), book_cutoff, stale_days), flush=True)

    models = {
        "gc001": ("single rung, always 1-day GC", None, ("GC001",)),
        "short_pick": ("single rung, best of GC 1/3/4/7 at each roll",
                       pick_best(rates, SHORT_NAMES, bars=idx), None),
        "best_gc": ("single rung, best of all eight GC tenors at each roll",
                    pick_best(rates, GC_NAMES, bars=idx), None),
        "capped28": ("single rung, best of GC tenors up to 28 days (rebalance-safe)",
                     pick_best(rates, CAPPED_NAMES, bars=idx), None),
        "best_dual": ("single rung, best of GC+R tenors at each roll",
                      pick_best(rates, tuple(n for n, _, _ in TENORS), bars=idx), None),
        "ladder3": ("three equal rungs GC007/GC014/GC028", None, LADDERS["ladder3"]),
        "ladder4": ("four equal rungs GC001/GC007/GC014/GC028", None, LADDERS["ladder4"]),
    }

    out = {
        "evidence_cutoff": str(idx[-1].date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "window": [str(idx[0].date()), str(idx[-1].date())],
        "book_evidence_cutoff": book_cutoff,
        "repo_panel_stale": {"behind_book_bars": stale_days,
                             "owner_lane": "bm-a (update_repo.py, T-88)",
                             "note": "cash leg is read off the panel as of its own last "
                                     "bar; a repo bar missing vs the equity panel is "
                                     "disclosed, never ffilled into a fake quote"},
        "commission_bp_by_tenor": dict(FEE_BP) if fees is FEE_BP else fees,
        "question": "what is the book's uninvested sleeve worth under five tenor "
                    "policies, net of exchange commissions, and what does the ladder "
                    "instruction look like today?",
        "models": {},
        "quarter_end": quarter_end_panel(rates, idx),
        "caveats": [
            "commission schedule is an assumption (see FEE_BP note), rerun with --fee=0 "
            "for the gross read",
            "on-exchange repo settles T+1 and needs face-value lots; lot granularity and "
            "the 0.1% NAV residue of the equity ticket are ignored here",
            "the interest is spread evenly inside a contract, so intra-contract daily "
            "shapes are smooth; contract totals are exact",
            "no intraday execution model: the entry uses the previous/entry bar close",
            "exploratory: no preregistration, no verdict, no ledger booking",
        ],
    }

    zero = {k: 0.0 for k in FEE_BP}
    base_net = None
    for key, (desc, pick, single) in models.items():
        if single and len(single) == 1 and pick is None:
            ret, info = roll_rung(idx, rates, None, fees=fees, name=single[0])
            ret0, _ = roll_rung(idx, rates, None, fees=zero, name=single[0])
            per = {single[0]: {"weight": 1.0, "n_contracts": len(info["contracts"])}}
        elif pick is not None:
            ret, info = roll_rung(idx, rates, pick, fees=fees)
            ret0, _ = roll_rung(idx, rates, pick, fees=zero)
            per = {}
        else:
            ret, per = ladder(idx, rates, single, fees=fees)
            ret0, _ = ladder(idx, rates, single, fees=zero)
            info = {"contracts": [], "missing": 0}
            for nm in single:
                _, ii = roll_rung(idx, rates, None, fees=fees, name=nm)
                info["contracts"] += ii["contracts"]
                info["missing"] += ii["missing"]
        n_rungs = len(single) if (single and pick is None) else 1
        liq = liquidity_stats(info, idx, n_rungs)
        net = cagr_pct(ret, idx)
        grs = cagr_pct(ret0, idx)
        per_year = {}
        for y in sorted({d.year for d in idx}):
            m = pd.DatetimeIndex([d for d in idx if d.year == y])
            if len(m) > 20:
                per_year[str(y)] = round(cagr_pct(ret.reindex(m), m), 3)
        out["models"][key] = {
            "description": desc,
            "net_ann_pct": round(net, 4),
            "gross_ann_pct": round(grs, 4),
            "commission_drag_pp": round(grs - net, 4),
            "n_contracts": len(info["contracts"]),
            "missing_quotes": info["missing"],
            "tenor_mix": {},
            "per_year_net_pct": per_year,
            "liquidity": liq,
            "rungs": per,
        }
        mix = {}
        for c in info["contracts"]:
            mix[str(c["tenor"])] = mix.get(str(c["tenor"]), 0) + 1
        out["models"][key]["tenor_mix"] = mix
        if base_net is None:
            base_net = net
        print("[%s] net %.3f%%/yr gross %.3f%% (drag %.3f) | %d contracts | mix %s | "
              "maturity days %.0f%% maxLock %dd gap %dd"
              % (key, net, grs, grs - net, len(info["contracts"]), mix,
                 liq["share_of_bars_with_a_maturity"] * 100, liq["max_locked_days"],
                 liq["longest_gap_without_any_maturity_days"]), flush=True)

    # what the best cash leg is worth to the whole book at beta 0.20 (r1255 grid mean k)
    cash_share = 1.0 - MEAN_K_BETA020
    out["book_impact_beta020"] = {
        "mean_k": MEAN_K_BETA020,
        "cash_share": round(cash_share, 3),
        "source": "results/etf_phase_beta_window.json grid expanding_t0.20_gc001 k.mean",
        "uplift_pp": {k: round((v["net_ann_pct"] - out["models"]["gc001"]["net_ann_pct"])
                               * cash_share, 3) for k, v in out["models"].items()},
    }

    # the ladder instruction as of the cutoff bar
    ticket = {"as_of": str(idx[-1].date()), "book_evidence_cutoff": book_cutoff,
              "cash_sleeve_pct_of_nav_assumption": round(cash_share * 100, 1),
              "rungs": []}
    for nm in LADDERS["ladder4"]:
        _, ii = roll_rung(idx, rates, None, name=nm)
        live = [c for c in ii["contracts"] if c["entry"] <= str(idx[-1].date())
                and c["exit"] >= str(idx[-1].date())]
        last = live[-1] if live else (ii["contracts"][-1] if ii["contracts"] else None)
        vec = rates[nm].get(idx[-1], np.nan)
        ticket["rungs"].append({
            "contract": nm, "tenor_days": tenor_of(nm),
            "weight_of_cash": round(1.0 / len(LADDERS["ladder4"]), 4),
            "weight_of_nav": round(cash_share / len(LADDERS["ladder4"]), 4),
            "quoted_pct_at_cutoff": round(float(vec), 3) if np.isfinite(vec) else None,
            "holding": last,
            "next_action": "roll %s on the first bar at/after %s"
                           % (nm, last["exit"] if last else str(idx[-1].date())),
        })
    ticket["blended_quoted_pct"] = round(float(np.nanmean(
        [r["quoted_pct_at_cutoff"] for r in ticket["rungs"]] or [np.nan])), 3)
    out["ticket"] = ticket

    # why the tenor choice is small: the curve is nearly flat, and the commission is
    # roughly proportional to holding period, so every policy pays ~the same rent
    curve = {}
    for nm in CAPPED_NAMES:
        s = rates[nm].dropna()
        if not len(s):
            continue
        k = tenor_of(nm)
        curve[nm] = {"tenor": k, "mean_quote_pct": round(float(s.mean()), 3),
                     "rolls_per_year": round(365.0 / k, 1),
                     "commission_bp_per_year": round(365.0 / k * FEE_BP.get(k, 0.0), 1)}
    best_share = {}
    for d in idx:
        vals = [(float(rates[nm].get(d, np.nan)), -tenor_of(nm), nm) for nm in CAPPED_NAMES]
        vals = [v for v in vals if np.isfinite(v[0])]
        if vals:
            nm = max(vals)[2]
            best_share[nm] = best_share.get(nm, 0) + 1
    tot = sum(best_share.values()) or 1
    out["curve"] = {"by_tenor": curve,
                    "share_of_bars_where_this_is_the_best_capped_tenor":
                        {k: round(v / float(tot), 3) for k, v in sorted(best_share.items())},
                    "read": "a flat curve plus a commission that scales with the holding "
                            "period means the ladder buys fee efficiency, not yield"}
    os.makedirs(TICKET_DIR, exist_ok=True)
    with open(os.path.join(TICKET_DIR, "CASH-TICKET-%s.json" % idx[-1].date()), "w",
              encoding="utf-8") as fh:
        json.dump(ticket, fh, ensure_ascii=False, indent=1)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    best = max(out["models"].items(), key=lambda kv: kv[1]["net_ann_pct"])
    print("\nbest cash leg = %s at %.3f%%/yr net (gc001 baseline %.3f%%) | worth %+.3fpp "
          "on the book at beta 0.20"
          % (best[0], best[1]["net_ann_pct"], out["models"]["gc001"]["net_ann_pct"],
             out["book_impact_beta020"]["uplift_pp"][best[0]]), flush=True)
    print("wrote %s (%.0fs)" % (OUT_PATH, time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())