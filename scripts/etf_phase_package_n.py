"""Phase package x holding count, x 8% vol target, and a null for package-minus-median-phase.

Three questions the r1250 phase-cadence round left open, all on the bond_removed book:

  (a) N sweep -- the package was measured at N=5 only. If the excess is a top-5 concentration
      artefact, widening to 8/10 should kill it; if the *dispersion* of the phase outcomes is
      what N buys, the phase spread should shrink as N grows.
  (b) vol target -- r1251-era production candidate carries an 8% realised-vol overlay. Does it
      survive on the phase package (it is applied per sub-book, so the package pays it 20x)?
  (c) null on the package-minus-median-phase gap -- at R=20 the package beat its own median
      phase by only +0.21pp, i.e. it buys the removal of the phase choice rather than alpha.
      Under shuffled factor scores, is that +0.21pp distinguishable from noise at all?

Engine: `fast_next_open_vt` is `etf_variants_null_rolling.fast_next_open` with an optional
per-book vol scaler, and --selftest pins the two at 1e-12 on the real maths path (vol_target
None must reproduce the reference engine exactly, turnover included). The vol overlay's sizing
convention (trailing 60-bar book vol, cap 1.0 = no leverage, scale applied to weights at the
rebalance, turnover charged on the scaled weights) is copied from scripts/etf_robust_pf.py,
which is the published convention in this repo; the remaining difference is that robust sizes
off open-to-open returns while this engine sizes off close-to-close returns, matching the fill
engine's own price face.

Exploratory: no preregistration, no verdict, no ledger booking.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F  # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_phase_ensemble as P  # noqa: E402
from scripts.etf_asset_class import classify  # noqa: E402

ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
REBAL = 20
N_LIST = (3, 5, 8, 10)
TARGET_VOL = 0.08
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "etf_phase_package_n.json")


# --------------------------------------------------------------------------------------------
# engine
# --------------------------------------------------------------------------------------------
def fast_next_open_vt(score, close, openp, rebal, n_hold=None, cost=None, start=ANCHOR,
                      vol_target=None):
    """`V.fast_next_open` with an optional per-book trailing-vol scaler (cap 1.0)."""
    n_hold = F.N_HOLD if n_hold is None else n_hold
    cost = F.COST if cost is None else cost

    def leg_w(a, b, ix, w):
        """Weighted version of V._leg: finite pairs only, weights renormalised onto them."""
        if ix.size == 0:
            return None
        av, bv = a[ix], b[ix]
        v = bv / av - 1.0
        keep = np.isfinite(v) & np.isfinite(av) & (av > 0)
        if not keep.any():
            return None
        ww = w[keep]
        sw = float(ww.sum())
        if sw <= 0:
            return None
        # mean over the names that actually priced (identical to V._leg at scale 1.0),
        # then times the book's exposure so the un-invested remainder sits in cash at 0%
        return float(np.sum(v[keep] * ww) / sw * float(w.sum()))

    idx = pd.to_datetime(close.index)
    cols = close.columns
    Praw = close.reindex(columns=cols).ffill().to_numpy(dtype=float)
    Oraw = openp.reindex(columns=cols).to_numpy(dtype=float)
    O = np.where(np.isfinite(Oraw), Oraw, Praw)
    S = score.reindex(index=idx, columns=cols).to_numpy(dtype=float)
    R = np.full(Praw.shape, np.nan)
    R[1:] = Praw[1:] / Praw[:-1] - 1.0

    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(start)]
    if len(pos) < 3:
        return pd.Series(dtype=float), 0.0, 0
    rebal_pos = set(pos[::rebal])

    def book_vol(book, upto):
        if book.size == 0:
            return np.nan
        win = R[max(0, upto - 59):upto + 1][:, book]
        win = win[np.isfinite(win).all(axis=1)]   # the panel's first bar has no return
        if win.shape[0] < 20:
            return np.nan
        w = np.full(book.size, 1.0 / book.size)
        cov = np.cov(win, rowvar=False, bias=True)
        cov = np.atleast_2d(cov)
        v = float(np.sqrt(max(w @ cov @ w, 0.0)) * np.sqrt(252))
        return v if np.isfinite(v) else np.nan

    equity = 1.0
    curve = [(idx[pos[0]], equity)]
    held = np.empty(0, dtype=int)
    held_w = np.empty(0, dtype=float)
    pending = None
    turn_sum = 0.0
    n_r = 0
    gapfill = 0

    for j, i in enumerate(pos):
        if j > 0:
            prev = pos[j - 1]
            if held.size:
                gapfill += int(np.count_nonzero(~np.isfinite(Oraw[i, held])))
            if pending is not None:
                if held.size:
                    r = leg_w(Praw[prev], O[i], held, held_w)
                    if r is not None:
                        equity *= (1.0 + r)
                new, new_w, turn = pending
                equity *= (1.0 - cost * turn)
                turn_sum += turn
                n_r += 1
                held, held_w = new, new_w
                pending = None
                r = leg_w(O[i], Praw[i], held, held_w)
                if r is not None:
                    equity *= (1.0 + r)
            elif held.size:
                r = leg_w(Praw[prev], Praw[i], held, held_w)
                if r is not None:
                    equity *= (1.0 + r)
            curve.append((idx[i], equity))

        if i in rebal_pos:
            row = S[i]
            m = np.isfinite(row)
            if int(m.sum()) >= n_hold:
                cand = np.flatnonzero(m)
                picks = cand[np.argsort(-row[cand], kind="stable")][:n_hold].astype(int)
                w = np.full(picks.size, 1.0 / n_hold)
                if vol_target:
                    v = book_vol(picks, i)
                    if np.isfinite(v) and v > 0:
                        w = w * float(min(1.0, vol_target / v))
                un = np.union1d(held, picks)
                wh = dict(zip(held.tolist(), held_w.tolist()))
                wn = dict(zip(picks.tolist(), w.tolist()))
                turn = float(sum(abs(wn.get(k, 0.0) - wh.get(k, 0.0)) for k in un.tolist()))
                pending = (picks, w, turn)

    ser = pd.Series(dict(curve))
    return ser, (turn_sum / n_r if n_r else 0.0), gapfill


# --------------------------------------------------------------------------------------------
# package helpers
# --------------------------------------------------------------------------------------------
def phase_grid(idx, anchor=ANCHOR, span=REBAL):
    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(anchor)]
    return [pd.Timestamp(idx[pos[k]]) for k in range(min(span, len(pos)))]


def phase_book(score, close, openp, n_hold, vol_target=None):
    idx = pd.to_datetime(close.index)
    curves, cells = [], []
    for k, start in enumerate(phase_grid(idx)):
        ser, turn, _ = fast_next_open_vt(score, close, openp, REBAL, n_hold=n_hold,
                                         start=str(start.date()), vol_target=vol_target)
        if ser is None or len(ser) < 30:
            continue
        curves.append(ser)
        m = F.metrics(ser, "phase-%02d" % k)
        cells.append({"phase": k, "start": str(start.date()),
                      "cagr_pct": round(m["cagr"] * 100, 2), "sharpe": m["sharpe"],
                      "maxdd_pct": round(m["maxdd"] * 100, 2),
                      "turnover_per_rebal": round(turn, 3)})
    return P.mean_curve(curves), cells


def _disp(vals):
    v = np.asarray(vals, dtype=float)
    if not v.size:
        return None
    return {"min": round(float(v.min()), 2), "median": round(float(np.median(v)), 2),
            "max": round(float(v.max()), 2), "spread": round(float(v.max() - v.min()), 2),
            "n": int(v.size)}


def _block(ser, ew, cells):
    m = F.metrics(ser, "package")
    me = F.metrics(ew, "ew")
    ph = [c["cagr_pct"] for c in cells]
    med = round(float(np.median(ph)), 2) if ph else None
    out = {"package": m, "ew": me,
           "excess_pp": round((m["cagr"] - me["cagr"]) * 100, 2),
           "per_year_pct": P.per_year(ser),
           "phase_cagr": _disp(ph),
           "phase_sharpe": _disp([c["sharpe"] for c in cells]),
           "phase_maxdd": _disp([c["maxdd_pct"] for c in cells]),
           "beats_phases": "%d/%d" % (sum(1 for c in cells if c["cagr_pct"] < m["cagr"] * 100),
                                      len(cells)),
           "package_minus_median_phase_pp": (round(m["cagr"] * 100 - med, 2)
                                             if med is not None else None),
           "mean_turnover_per_rebal": (round(float(np.mean([c["turnover_per_rebal"]
                                                            for c in cells])), 3)
                                       if cells else None),
           "phases": cells}
    oos, ewo = ser[ser.index >= OOS], ew[ew.index >= OOS]
    if len(oos) > 20:
        mo = F.metrics(oos, "package:oos")
        out["oos_2024"] = mo
        out["oos_excess_pp"] = round((mo["cagr"] - F.metrics(ewo, "ew:oos")["cagr"]) * 100, 2)
    return out


def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name, extra)

    rng = np.random.default_rng(5)
    n_bar, n_col = 120, 14
    idx = pd.bdate_range("2021-01-04", periods=n_bar)
    px = np.cumprod(1.0 + rng.normal(0.0006, 0.013, size=(n_bar, n_col)), axis=0) * 10.0
    close = pd.DataFrame(px, index=idx, columns=["c%02d" % k for k in range(n_col)])
    openp = close * (1.0 + rng.normal(0.0, 0.004, size=(n_bar, n_col)))
    openp.iloc[7, 3] = np.nan
    score = pd.DataFrame(rng.normal(size=(n_bar, n_col)), index=idx, columns=close.columns)
    score.iloc[::9, 11] = np.nan

    # leg 1: vol_target=None must reproduce the reference engine bar for bar, turnover included
    ref, ref_turn, ref_gap = V.fast_next_open(score, close, openp, 7, n_hold=4,
                                              start="2021-01-04")
    got, got_turn, got_gap = fast_next_open_vt(score, close, openp, 7, n_hold=4,
                                               start="2021-01-04")
    chk("date grid identical", ref.index.equals(got.index))
    dev = float(np.max(np.abs(ref.to_numpy() / got.to_numpy() - 1.0)))
    chk("levels pinned 1e-12", dev < 1e-12, dev)
    chk("turnover pinned 1e-12", abs(ref_turn - got_turn) < 1e-12, (ref_turn, got_turn))
    chk("gapfill identical", ref_gap == got_gap)

    # leg 2: a huge vol target is a no-op (scale caps at 1.0)
    big, big_turn, _ = fast_next_open_vt(score, close, openp, 7, n_hold=4,
                                         start="2021-01-04", vol_target=99.0)
    dev = float(np.max(np.abs(big.to_numpy() / got.to_numpy() - 1.0)))
    chk("vol_target=99% is a no-op (cap 1.0)", dev < 1e-12, dev)

    # leg 3: a tiny vol target must cut exposure and never lever up
    low, low_turn, _ = fast_next_open_vt(score, close, openp, 7, n_hold=4,
                                         start="2021-01-04", vol_target=0.005)
    lr, br = low.pct_change().dropna(), big.pct_change().dropna()
    chk("vol_target halves or more of the book's vol", lr.std() < 0.9 * br.std(),
        (lr.std(), br.std()))
    chk("scaled book is smaller on a rising panel", low.iloc[-1] < big.iloc[-1],
        (low.iloc[-1], big.iloc[-1]))

    # leg 4: future origin degrades instead of raising
    empty, _, _ = fast_next_open_vt(score, close, openp, 7, n_hold=4, start="2099-01-01")
    chk("future origin returns empty", len(empty) == 0)

    # leg 5: package maths -- unfunded sub-books sit in cash, funded ones average
    a = pd.Series({pd.Timestamp("2020-01-01"): 1.0, pd.Timestamp("2020-01-02"): 1.10})
    b = pd.Series({pd.Timestamp("2020-01-02"): 1.0, pd.Timestamp("2020-01-03"): 1.05})
    ens = P.mean_curve([a, b])
    chk("staggered start sits in cash", abs(ens.iloc[0] - 1.0) < 1e-12)
    chk("package averages funded books", abs(ens.iloc[-1] - (1.10 + 1.05) / 2) < 1e-12)

    # leg 6: phase grid has exactly REBAL phases, one bar apart
    grid = phase_grid(pd.bdate_range("2020-01-01", periods=200))
    chk("phase grid has R phases", len(grid) == REBAL and len(set(grid)) == REBAL)
    chk("phases are consecutive bars", {(grid[i + 1] - grid[i]).days
                                        for i in range(len(grid) - 1)} <= {1, 3})

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    n_iter = 60
    if "--iter" in sys.argv:
        n_iter = int(sys.argv[sys.argv.index("--iter") + 1])

    t_all = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ew = F.run_ew(close[cols], amt[cols], REBAL, start=ANCHOR)
    print("panel %s bars=%d bond_removed=%d | ew full %.2f%%"
          % (close.index[0].date(), close.shape[0], len(cols),
             F.metrics(ew, "ew")["cagr"] * 100), flush=True)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR, "rebal": REBAL,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "basis": "next-open fill per sub-book (decide close t, fill open t+1), 8bp/side on the "
                 "sub-book's own turnover; package = buy-and-hold mean of the R=20 phase NAVs",
        "question": "(a) does the package survive N, (b) does it survive an 8% vol overlay, "
                    "(c) is package-minus-median-phase distinguishable from noise",
        "control_ew": F.metrics(ew, "ew"),
        "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "control = equal-weight on the same subset (close basis, as published)",
            "exploratory: no preregistration, no verdict, no ledger booking",
            "vol overlay sizes off trailing 60-bar close-to-close book vol, cap 1.0, "
            "turnover charged on the scaled weights (robust convention, close face)",
            "null resolution is 1/(n_iter+1); p at the floor means 'small', not 'zero'",
        ],
        "n_sweep": {}, "vol_target": {}, "null_gap": {},
    }

    for n in N_LIST:
        t0 = time.time()
        ens, cells = phase_book(score, close[cols], openp[cols], n)
        row = _block(ens, ew, cells)
        row["secs"] = round(time.time() - t0, 1)
        out["n_sweep"]["N%d" % n] = row
        print("N%-2d package %6.2f%% (ew %5.2f%%, %+.2fpp) | oos %6.2f%% (%+.2fpp) | "
              "sharpe %.3f | mdd %6.2f%% | phase med %6.2f%% spread %5.2f | pkg-med %+.2fpp | "
              "turn %.3f | %.0fs"
              % (n, row["package"]["cagr"] * 100, row["ew"]["cagr"] * 100, row["excess_pp"],
                 row.get("oos_2024", {}).get("cagr", float("nan")) * 100 if "oos_2024" in row
                 else float("nan"), row.get("oos_excess_pp", float("nan")),
                 row["package"]["sharpe"], row["package"]["maxdd"] * 100,
                 row["phase_cagr"]["median"], row["phase_cagr"]["spread"],
                 row["package_minus_median_phase_pp"], row["mean_turnover_per_rebal"],
                 row["secs"]), flush=True)

    # (b) 8% vol target on the base N
    t0 = time.time()
    vt, cells_vt = phase_book(score, close[cols], openp[cols], F.N_HOLD, vol_target=TARGET_VOL)
    row = _block(vt, ew, cells_vt)
    row["target_vol"] = TARGET_VOL
    row["realised_vol_pct"] = round(float(vt.pct_change().dropna().std() * np.sqrt(252)) * 100, 2)
    row["secs"] = round(time.time() - t0, 1)
    out["vol_target"] = row
    print("VT   package %6.2f%% (%+.2fpp) | realised vol %.2f%% | sharpe %.3f | mdd %6.2f%% | "
          "phase spread %5.2f | %.0fs"
          % (row["package"]["cagr"] * 100, row["excess_pp"], row["realised_vol_pct"],
             row["package"]["sharpe"], row["package"]["maxdd"] * 100,
             row["phase_cagr"]["spread"], row["secs"]), flush=True)

    # (c) null on the package-minus-median-phase gap
    idx = pd.to_datetime(close.index)
    hist = close[cols].notna().cumsum()
    elig = ((amt[cols] >= F.MIN_AMT) & (hist >= F.MIN_HIST)).to_numpy()
    base = []
    for c in F.SIGNS:
        f = feats.get(c)
        if f is None:
            continue
        r = f.reindex(index=idx, columns=cols).rank(axis=1, pct=True).to_numpy(dtype=np.float32)
        base.append((F.SIGNS[c], r))
    rng = np.random.default_rng(11)
    real_gap = out["n_sweep"]["N%d" % F.N_HOLD]["package_minus_median_phase_pp"]
    real_gap_oos = None
    g_full, g_oos = [], []
    t0 = time.time()
    for it in range(n_iter):
        parts = []
        for sgn, arr in base:
            a = arr.copy()
            for i in range(a.shape[0]):
                rng.shuffle(a[i])
            parts.append(sgn * a)
        comp = sum(parts) / len(parts)
        sc = pd.DataFrame(np.where(elig, comp, np.nan), index=idx, columns=cols)
        ens, cells = phase_book(sc, close[cols], openp[cols], F.N_HOLD)
        if not cells or ens is None or len(ens) < 50:
            continue
        pkg = F.metrics(ens, "p")["cagr"] * 100
        med = float(np.median([c["cagr_pct"] for c in cells]))
        g_full.append(pkg - med)
        if (it + 1) % 5 == 0:
            print("  null %d/%d  %.0fs  last gap %+.2fpp"
                  % (it + 1, n_iter, time.time() - t0, pkg - med), flush=True)

    gf = np.asarray(g_full, dtype=float)
    out["null_gap"] = {
        "statistic": "package CAGR pct minus median phase CAGR pct (R=20, N=%d)" % F.N_HOLD,
        "n_iter": n_iter, "n_valid": int(gf.size), "seed": 11,
        "real_pp": real_gap,
        "null_mean_pp": round(float(gf.mean()), 3) if gf.size else None,
        "null_p5_pp": round(float(np.percentile(gf, 5)), 3) if gf.size else None,
        "null_p95_pp": round(float(np.percentile(gf, 95)), 3) if gf.size else None,
        "null_min_pp": round(float(gf.min()), 3) if gf.size else None,
        "null_max_pp": round(float(gf.max()), 3) if gf.size else None,
        "p_value_ge": (round(float((1 + int(np.sum(gf >= real_gap))) / (1 + gf.size)), 4)
                       if gf.size else None),
        "secs": round(time.time() - t0, 1),
    }
    print("null gap:", out["null_gap"], flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", OUT_PATH, "(%.0fs total)" % (time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())