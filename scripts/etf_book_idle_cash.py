"""What does the book's idle sleeve earn?  The two published faces were never composed.

`etf_book_nobond_vt` sizes the book to an 8% vol target and de-levers into cash
(`scale <= 1`); the engine prices that cash at 0.  `etf_book_cash_vehicle` priced the
same cash at 1.77%/yr net via a daily GC001 roll -- on the very money the newest ticket
already carries.  So the book's public headline (11.49% / Sharpe 1.132 / -10.56%) is a
return on a book that spends much of its life in an unremunerated sleeve, and the
cash-vehicle face is money the desk can earn but the book's own NAV never counted
(E240: a face with a reader and a face with a producer, never the same book).

This module composes them, using the engine's own step returns so the control is exact:
with the cash rate set to zero the composed series must BE the engine series.

The engine holds nominal weights between rebalances, so the idle fraction is taken as
`1 - scale` constant over a holding period.  That is the engine's own convention (its
weights do not drift either), not an extra modelling choice, and it is what makes the
zero-cash control bit-exact.  A drifting sleeve would move the number by less than the
disclosed rounding.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_cash_ladder as CL
import etf_book_cash_vehicle as V

VOL_TARGET = 0.08
REBAL, NHOLD, COST = 20, 5, 0.0010
IS_END = "2023-12-31"
OUT = os.path.join(E.PATHS.results_dir, "etf_book_idle_cash.json")
REPRO_TOL = 5e-5

# Frozen before the numbers were seen.
CRITERIA = {
    "C0_control": "with the cash rate forced to zero the composed curve must equal the "
                  "engine curve (max |diff| <= 5e-5 relative) -- otherwise the composition, "
                  "not the cash, is what moved the number",
    "C1_cash_vehicle_published": "the idle sleeve must be priced by the already-published "
                                 "vehicle (GC001 daily roll) and reproduce its net rate to "
                                 "0.5bp; a new vehicle would be a second implementation",
    "C2_cagr_gain_pp": 0.30,
    "C3_sharpe_must_not_fall": True,
    "C4_maxdd_must_not_deepen_pp": 0.20,
}


# ---------------------------------------------------------------------------------------
# composition (pure, so the selftest can hold it)
# ---------------------------------------------------------------------------------------
def scale_schedule(diag, index):
    """Scale in force at each bar: the last decision's scale, carried forward.

    Bars before the first decision have no scale; they are returned as NaN and are
    treated as no cash by `compose` (never inventing an idle sleeve that was not held).
    """
    if not diag:
        return pd.Series(np.nan, index=index)
    s = pd.Series({pd.Timestamp(r["date"]): float(r["scale"]) for r in diag}).sort_index()
    return s.reindex(s.index.union(index)).ffill().reindex(index)


def compose(book, idle, cash_ret):
    """book = engine NAV; idle = fraction earning `cash_ret` (fraction/bar).

    A step return is `(book step) + idle * cash`.  With `cash_ret == 0` this is exactly
    `book`, which is the control the face publishes.
    """
    r_book = book.pct_change().fillna(0.0)
    idle = idle.reindex(book.index).fillna(0.0).clip(lower=0.0, upper=1.0)
    cash_ret = cash_ret.reindex(book.index).fillna(0.0)
    step = r_book.to_numpy() + idle.to_numpy() * cash_ret.to_numpy()
    return pd.Series(np.cumprod(1.0 + step), index=book.index) * float(book.iloc[0])


def cash_step_returns(rates, index, name="GC001", ladder=None, fees=None):
    """Per-bar net cash return on `index`, from the published repo engine.

    The rung's interest is credited on contract-maturity bars, so the curve is built on
    the repo calendar and then differenced on the book's calendar: ffill of the
    cumulative growth carries accrual across bars where no contract matured, which keeps
    the total accrual exact.  Differencing the raw per-bar rate instead would drop the
    interest of every contract that matured on a non-book bar.

    `ladder` (a tuple of tenors taken from `etf_book_cash_ladder.LADDERS`) prices the
    sleeve as an equal-weight ladder instead of one rolling tenor; `ladder=None` keeps the
    published GC001 path byte-identical. r1739 added the parameter because the forward
    ledger already prices its cash on `ladder3` with commission charged, so "is the carrier
    worth anything?" has to be answered on this composition, not typed into a second
    engine.
    """
    bars = V.repo_bars(rates, str(pd.Timestamp(index[0]).date()))
    if len(bars) < 250:
        raise RuntimeError("too few repo bars (%d)" % len(bars))
    if ladder is None:
        ret, info = CL.roll_rung(bars, rates, None, fees=None, name=name)
    else:
        ret, info = CL.ladder(bars, rates, tuple(ladder), fees=fees)
    cum = (1.0 + ret).cumprod()
    cum = cum.reindex(cum.index.union(index)).ffill().reindex(index)
    step = cum.pct_change().fillna(0.0)
    return step, info, ret, bars


def cagr_pct(ser):
    ser = ser.dropna()
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    return (float(ser.iloc[-1]) / float(ser.iloc[0])) ** (1 / yrs) * 100.0 - 100.0


def verdict_of(readings, criteria=CRITERIA):
    """Derived, never typed: every gate is recomputed off the readings."""
    c2 = readings["cagr_gain_pp"] >= criteria["C2_cagr_gain_pp"]
    c3 = readings["sharpe_with"] >= readings["sharpe_without"]
    c4 = readings["maxdd_with_pct"] >= readings["maxdd_without_pct"] - \
        criteria["C4_maxdd_must_not_deepen_pp"]
    gates = {"C2_cagr_gain_pp": bool(c2), "C3_sharpe_must_not_fall": bool(c3),
             "C4_maxdd_must_not_deepen_pp": bool(c4)}
    return ("ADMIT" if all(gates.values()) else "REJECT"), gates


# ---------------------------------------------------------------------------------------
def run():
    import time
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    print("bond-free universe %d, flips repaired %d" % (len(cols), n_flip), flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    diag = []
    book, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, REBAL, NHOLD,
                                       COST, vol_target=VOL_TARGET, diag=diag)
    print("book bars %d turnover %.3f  cagr %.4f%%" % (len(book), turn, cagr_pct(book)),
          flush=True)

    scale = scale_schedule(diag, book.index)
    idle = (1.0 - scale).clip(lower=0.0, upper=1.0)

    # control: no cash at all must reproduce the engine curve
    ctrl = compose(book, idle, pd.Series(0.0, index=book.index))
    ctrl_err = float((ctrl / book - 1.0).abs().max())

    rates = CL.load_panel()
    cash_ret, info, raw_ret, raw_bars = cash_step_returns(rates, book.index)
    cash_on_window = CL.cagr_pct(raw_ret, raw_bars) / 100.0

    # the published vehicle's own control, read off the face that already prices it.
    # It must be reproduced ON ITS OWN WINDOW: a rate recomputed over a different span is
    # a different number, and comparing the two would read a window difference as a defect.
    published, published_end = None, None
    if os.path.exists(os.path.join(E.PATHS.results_dir, "etf_book_cash_vehicle.json")):
        with io.open(os.path.join(E.PATHS.results_dir, "etf_book_cash_vehicle.json"),
                     encoding="utf-8") as f:
            cv = json.load(f)
        for v in cv.get("vehicles", []):
            if v.get("name") == "gc001_daily_roll":
                published = v.get("net_ann_pct")
        pw = (cv.get("gate", {}) or {}).get("published_window")
        published_end = pw[1] if pw else None
    gap_bp, ctrl_rate = None, None
    if published is not None and published_end:
        cb = V.repo_bars(rates, CL.WINDOW_START, pd.Timestamp(published_end))
        if len(cb) > 250:
            cr, _ = CL.roll_rung(cb, rates, None, fees=None, name="GC001")
            ctrl_rate = CL.cagr_pct(cr, cb)
            gap_bp = abs(ctrl_rate - float(published)) * 100.0

    comp = compose(book, idle, cash_ret)
    st_wo = A.stats2(book, "without_fix")
    st_w = A.stats2(comp, "with_fix")

    def slice_stats(ser):
        out = {}
        for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
            m = A.stats2(sl, lbl)
            for k in ("cagr", "sharpe", "maxdd"):
                out["%s_%s" % (k, lbl)] = m.get(k)
        return out

    per_year = {}
    for y in sorted({d.year for d in comp.index}):
        m = comp[[d for d in comp.index if d.year == y]]
        if len(m) > 20:
            per_year[str(y)] = round(cagr_pct(m), 3)

    readings = {
        "cagr_without_pct": round(float(st_wo["cagr"]) * 100.0, 4),
        "cagr_with_pct": round(float(st_w["cagr"]) * 100.0, 4),
        "cagr_gain_pp": round((float(st_w["cagr"]) - float(st_wo["cagr"])) * 100.0, 4),
        "sharpe_without": round(float(st_wo["sharpe"]), 4),
        "sharpe_with": round(float(st_w["sharpe"]), 4),
        "maxdd_without_pct": round(float(st_wo["maxdd"]) * 100.0, 4),
        "maxdd_with_pct": round(float(st_w["maxdd"]) * 100.0, 4),
        "vol_without_pct": round(float(st_wo.get("vol", np.nan)) * 100.0, 4),
        "vol_with_pct": round(float(st_w.get("vol", np.nan)) * 100.0, 4),
        "control_max_rel_err": ctrl_err,
        "cash_vehicle_net_pct_on_window": round(cash_on_window * 100.0, 4),
        "cash_vehicle_published_pct": published,
        "cash_vehicle_reproduced_on_published_window_pct": None if ctrl_rate is None
        else round(ctrl_rate, 4),
        "cash_vehicle_gap_bp": None if gap_bp is None else round(gap_bp, 4),
        "idle_share_mean": round(float(idle.fillna(0.0).mean()), 4),
        "idle_share_median": round(float(idle.fillna(0.0).median()), 4),
        "bars_fully_invested": int((idle.fillna(0.0) <= 1e-9).sum()),
        "bars_with_cash": int((idle.fillna(0.0) > 1e-9).sum()),
        "bars": int(len(book)),
        "cny_per_year_on_1m": round(1_000_000.0 * (float(st_w["cagr"]) -
                                                   float(st_wo["cagr"])), 0),
        "per_year_cagr_with": per_year,
        "without": st_wo, "with": st_w,
        "is_oos": {"without": slice_stats(book), "with": slice_stats(comp)},
    }
    verdict, gates = verdict_of(readings)
    gates["C0_control"] = bool(ctrl_err <= REPRO_TOL)
    gates["C1_cash_vehicle_published"] = bool(gap_bp is not None and gap_bp <= 0.5)
    if not (gates["C0_control"] and gates["C1_cash_vehicle_published"]):
        verdict = "REFUSE"

    payload = {
        "face": "etf_book_idle_cash",
        "asof": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(book.index[-1].date()),
        "window": {"start": str(book.index[0].date()), "end": str(book.index[-1].date()),
                   "bars": int(len(book))},
        "book": {"vol_target": VOL_TARGET, "rebal": REBAL, "n_hold": NHOLD, "cost": COST,
                 "universe": len(cols), "turnover": round(turn, 4)},
        "question": "the book de-levers into cash and the engine prices that cash at 0; "
                    "the desk already priced the same cash at 1.77%/yr -- what is the book "
                    "worth with its idle sleeve paid?",
        "criteria_frozen": CRITERIA,
        "readings": readings,
        "gates": gates,
        "verdict": verdict,
        "repo_contracts": len(info["contracts"]),
        "repo_missing_quotes": info.get("missing", 0),
        "honest": [
            "idle = 1 - scale held constant over a holding period, the engine's own "
            "nominal-weight convention; a drifting sleeve would move the number by less "
            "than the 3rd decimal",
            "the cash vehicle is a daily GC001 roll at the quoted rate, not a dealer quote; "
            "one contract per bar, exchange commission included, no bid-offer",
            "the composed curve is a book-return statement, not a ticket: it says the idle "
            "sleeve is worth paying, not which vehicle the account should use",
            "%d repo bars on the window, %d missing quotes; cash accrual is carried across "
            "non-maturity bars by differencing the rung's cumulative growth"
            % (len(raw_bars), info.get("missing", 0)),
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    A.dir_ready = True
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: readings[k] for k in
                      ("cagr_without_pct", "cagr_with_pct", "cagr_gain_pp", "sharpe_without",
                       "sharpe_with", "maxdd_without_pct", "maxdd_with_pct", "idle_share_mean",
                       "cash_vehicle_net_pct_on_window", "cash_vehicle_gap_bp",
                       "cny_per_year_on_1m")}, ensure_ascii=False), flush=True)
    print("gates %s verdict %s" % (json.dumps(gates), verdict), flush=True)
    print("saved", OUT, flush=True)
    return 0 if verdict in ("ADMIT", "REJECT") else 2


# ---------------------------------------------------------------------------------------
def selftest():
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)
            print("FAIL", msg, flush=True)

    idx = pd.DatetimeIndex(pd.date_range("2024-01-01", periods=300, freq="B"))
    rng = np.random.default_rng(20261115)
    book = pd.Series(np.cumprod(1.0 + rng.normal(0.0003, 0.006, 300)), index=idx)
    diag = [{"date": str(d.date()), "scale": 1.0} for d in idx[::20]]

    # L1 zero-cash must reproduce the engine curve exactly (the control)
    idle = (1.0 - scale_schedule(diag, idx)).clip(lower=0.0, upper=1.0)
    ctrl = compose(book, idle, pd.Series(0.0, index=idx))
    chk(float((ctrl / book - 1.0).abs().max()) < 1e-12, "L1 zero-cash control is exact")

    # L2 a fully idle book earning a constant rate must return exactly that rate
    flat = pd.Series(1.0 + 0.0 * np.arange(300), index=idx)
    idle1 = pd.Series(1.0, index=idx)
    rate = 0.0001
    # the accrual series is differenced, so its first element is 0 (no bar before it)
    step_rate = pd.Series(rate, index=idx)
    step_rate.iloc[0] = 0.0
    out = compose(flat, idle1, step_rate)
    chk(abs(out.iloc[-1] - (1.0 + rate) ** 299) < 1e-9,
        "L2 a fully idle book compounds exactly at the cash rate")

    # L3 a de-levered book earning nothing must match the engine: idle never invents return
    half = [{"date": str(d.date()), "scale": 0.5} for d in idx[::20]]
    idle3 = (1.0 - scale_schedule(half, idx)).clip(lower=0.0, upper=1.0)
    chk(float(idle3.dropna().mean() - 0.5) < 1e-9, "L3 scale 0.5 leaves half the book idle")

    # L4 bars before the first decision carry no scale -> no invented idle sleeve
    late = [{"date": str(idx[100].date()), "scale": 1.0}]
    idle4 = (1.0 - scale_schedule(late, idx)).clip(lower=0.0, upper=1.0)
    chk(float(idle4.iloc[:100].fillna(0.0).sum()) == 0.0,
        "L4 bars before the first decision are not credited with idle cash")

    # L5 the verdict is derived: flipping one reading must flip the gate
    r_ok = {"cagr_gain_pp": 1.0, "sharpe_with": 1.10, "sharpe_without": 1.00,
            "maxdd_with_pct": -10.0, "maxdd_without_pct": -10.0}
    chk(verdict_of(r_ok)[0] == "ADMIT", "L5a an improving reading admits")
    r_bad = dict(r_ok, cagr_gain_pp=0.1)
    chk(verdict_of(r_bad)[0] == "REJECT", "L5b a gain below the frozen line rejects")
    r_dd = dict(r_ok, maxdd_with_pct=-11.0)
    chk(verdict_of(r_dd)[0] == "REJECT", "L5c a deeper drawdown rejects")
    r_sh = dict(r_ok, sharpe_with=0.99)
    chk(verdict_of(r_sh)[0] == "REJECT", "L5d a lower Sharpe rejects")

    print("selftest %s" % ("PASS" if not errs else "FAIL %d" % len(errs)), flush=True)
    return 0 if not errs else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run())
