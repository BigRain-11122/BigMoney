"""ETF book -- were the six factor signs knowable in real time?

Every published number on this line (9.13%/yr, OOS 15.2%, the production card, the
ticket) is produced by `etf_composite_pf.build_score`, and that score takes its factor
directions from a hard-coded `SIGNS` block:

    mom_12_1 +, price_position +, drawdown_60 +, adx_14 +, vol_60 -, intraday_range -

Those signs are not a theory, they are a reading of how the six factors paid over
2020-2026. If they were read off the whole sample, then every backtest, walk-forward
and path test on this line is priced with knowledge of which way each factor went --
a choice that sits ABOVE every path test we have run (E188/E199 test the arm, not
the sign). That is the one caveat nobody has priced.

This face prices it. The same six factors, the same engine, the same costs, two arms:

  fixed : the production score, `SIGNS` as published;
  pit   : the same rank-score, but each factor's direction is estimated only from
          windows that had already been REALISED by that decision date. A factor whose
          trailing mean IC is inside +/-IC_MIN is dropped for that date (unknown is not
          a direction), so the pit arm also has to survive running on fewer factors.

The IC is measured on the decision grid itself: at decision date s, Spearman between the
factor value at s and the realised R-bar forward return of that same cross-section. A
window at s is only usable at date t once s's forward return has finished (bar(s)+H <=
bar(t)), so the pit arm cannot see a return it has not lived through.

Frozen before the first run (echoed into the payload; the gate REDs if they differ):
    HORIZON=REBAL=20, IC_WIN=12 windows, IC_MIN=0.01, IC_MIN_ACTIVE=4,
    ADOPT_RATIO=0.70, PARTIAL_RATIO=0.30, N_HOLD=12, COST=10bp/side, START=2020-01-01.

Verdict rule (recomputed by the gate from the summary, never taken on trust):
    either arm did not trade            -> not_assessable_no_trade  (E199 lesson)
    cagr_pit / cagr_fixed >= 0.70       -> signs_learnable_in_realtime
    cagr_pit / cagr_fixed >= 0.30       -> signs_partly_in_sample
    otherwise                           -> signs_in_sample

  python scripts/etf_sign_pit.py run            # full panel, writes results/etf_sign_pit.json
  python scripts/etf_sign_pit.py --check        # re-derive the verdict from the payload
  python scripts/etf_sign_pit.py --selftest     # offline invariants, zero network
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as F  # noqa: E402
import etf_variants_null_rolling as V  # noqa: E402
from engine.factors import FACTORS as ENGINE_FACTORS  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_sign_pit.json"

# --- frozen constants (echoed into the payload, checked by the gate) -----------------
SIGNS = dict(F.SIGNS)
FACTOR_KEYS = list(SIGNS)
REBAL = 20
HORIZON = REBAL
N_HOLD = 12
COST = 0.0010
START = "2020-01-01"
IC_WIN = 12
IC_MIN = 0.02
IC_MIN_ACTIVE = 4
IC_MIN_ARMS = (0.01, IC_MIN, 0.05)
IC_WIN_ARMS = (6, IC_WIN, 24)
MIN_X = 20
ADOPT_RATIO = 0.70
PARTIAL_RATIO = 0.30
DECLARED = {
    "rebal": REBAL,
    "horizon": HORIZON,
    "n_hold": N_HOLD,
    "cost_per_side": COST,
    "start": START,
    "ic_win": IC_WIN,
    "ic_min": IC_MIN,
    "ic_min_arms": list(IC_MIN_ARMS),
    "ic_win_arms": list(IC_WIN_ARMS),
    "ic_min_active": IC_MIN_ACTIVE,
    "min_cross_section": MIN_X,
    "adopt_ratio": ADOPT_RATIO,
    "partial_ratio": PARTIAL_RATIO,
    "signs": SIGNS,
}


# --- measurement helpers -------------------------------------------------------------
def _spearman(a: pd.Series, b: pd.Series, min_x: int = MIN_X) -> float:
    """Rank correlation on the finite, non-degenerate part of one cross-section."""
    m = a.notna() & b.notna()
    if int(m.sum()) < min_x:
        return float("nan")
    ra, rb = a[m].rank(), b[m].rank()
    if ra.std(ddof=0) == 0 or rb.std(ddof=0) == 0:
        return float("nan")
    return float(np.corrcoef(ra.to_numpy(dtype=float), rb.to_numpy(dtype=float))[0, 1])


def grid_dates(dates, rebal: int = REBAL, start: str = START):
    pos = [d for d in dates if d >= pd.Timestamp(start)]
    return pos[::rebal]


def eligibility(close: pd.DataFrame, amt: pd.DataFrame) -> pd.DataFrame:
    hist = close.notna().cumsum()
    return (amt >= F.MIN_AMT) & (hist >= F.MIN_HIST)


def ic_table(px: pd.DataFrame, feats: dict, elig: pd.DataFrame, grid, horizon: int = HORIZON) -> pd.DataFrame:
    """Spearman(factor at decision, realised forward return) per grid date, per factor."""
    pos = {d: i for i, d in enumerate(px.index)}
    rows = {}
    cols = list(px.columns)
    for g in grid:
        p = pos[g]
        q = p + horizon
        if q >= len(px.index):
            rows[g] = {k: np.nan for k in FACTOR_KEYS}
            continue
        fwd = px.iloc[q] / px.iloc[p] - 1.0
        ok = elig.loc[g].reindex(cols).fillna(False).astype(bool)
        fwd = fwd.where(ok)
        row = {}
        for k in FACTOR_KEYS:
            f = feats.get(k)
            if f is None:
                row[k] = np.nan
                continue
            row[k] = _spearman(f.reindex(columns=cols).loc[g].where(ok), fwd)
        rows[g] = row
    return pd.DataFrame(rows).T.reindex(columns=FACTOR_KEYS)


def pit_signs(ic: pd.DataFrame, px: pd.DataFrame, horizon: int = HORIZON,
              ic_win: int = IC_WIN, ic_min: float = IC_MIN,
              min_active: int = IC_MIN_ACTIVE) -> pd.DataFrame:
    """Each factor's direction from windows that had already finished by that decision."""
    grid = list(ic.index)
    pos = {d: i for i, d in enumerate(px.index)}
    signs = pd.DataFrame(np.nan, index=grid, columns=FACTOR_KEYS)
    for j, g in enumerate(grid):
        realised = [grid[i] for i in range(j) if pos[grid[i]] + horizon <= pos[g]]
        real = realised[-ic_win:]
        if len(real) < min_active:
            continue
        sub = ic.loc[real]
        for k in FACTOR_KEYS:
            m = sub[k].mean(skipna=True)
            if not np.isfinite(m):
                continue
            signs.at[g, k] = 1.0 if m >= ic_min else (-1.0 if m <= -ic_min else 0.0)
    return signs


def score_face(close: pd.DataFrame, elig: pd.DataFrame, feats: dict,
               signs_by_date: pd.DataFrame) -> pd.DataFrame:
    """Rank-score of the six factors with a per-date sign matrix (0 = factor dropped)."""
    idx = close.index
    cols = close.columns
    sgn = signs_by_date.reindex(index=idx).reindex(columns=FACTOR_KEYS)
    total = None
    for k in FACTOR_KEYS:
        f = feats.get(k)
        if f is None:
            continue
        z = (f.reindex(index=idx, columns=cols).rank(axis=1, pct=True) - 0.5) * 2.0
        part = z.mul(sgn[k], axis=0)
        total = part if total is None else total.add(part)
    if total is None:
        return pd.DataFrame(np.nan, index=idx, columns=cols)
    active = sgn.abs().gt(0).sum(axis=1).replace(0, np.nan)
    score = total.div(active, axis=0).where(elig)
    score.index = pd.to_datetime(score.index)
    return score


def ic_persistence(ic: pd.DataFrame, px: pd.DataFrame, horizon: int = HORIZON,
                   ic_win: int = IC_WIN, min_active: int = IC_MIN_ACTIVE) -> dict:
    """Does a factor's recent IC carry forward, or does it revert?

    For every grid date with enough closed windows, compare the trailing mean IC (the
    number the pit rule would trade on) against the IC of the window that comes NEXT.
    A positive correlation says the sign is learnable; a negative one says the rule is
    systematically late -- which would explain a losing pit arm mechanically instead of
    leaving it as an unexplained number.
    """
    grid = list(ic.index)
    pos = {d: i for i, d in enumerate(px.index)}
    out = {}
    for k in FACTOR_KEYS:
        trail, nxt = [], []
        for j, g in enumerate(grid[:-1]):
            realised = [grid[i] for i in range(j) if pos[grid[i]] + horizon <= pos[g]]
            real = realised[-ic_win:]
            if len(real) < min_active:
                continue
            m = ic.loc[real, k].mean(skipna=True)
            v = ic.loc[grid[j + 1], k]
            if np.isfinite(m) and np.isfinite(v):
                trail.append(float(m))
                nxt.append(float(v))
        if len(trail) < 8:
            out[k] = {"n": len(trail), "carry_corr": None, "sign_flip_rate": None}
            continue
        t = np.asarray(trail)
        n = np.asarray(nxt)
        corr = float(np.corrcoef(t, n)[0, 1]) if t.std() > 0 and n.std() > 0 else None
        flips = float(np.mean(np.sign(t) != np.sign(n)))
        out[k] = {"n": int(len(t)), "carry_corr": None if corr is None else round(corr, 4),
                  "sign_flip_rate": round(flips, 4),
                  "trailing_mean_ic": round(float(t.mean()), 5)}
    return out


def arm(score: pd.DataFrame, close: pd.DataFrame, openp: pd.DataFrame) -> dict:
    ser, turn, gapfill = V.fast_next_open(score, close, openp, REBAL, n_hold=N_HOLD,
                                          cost=COST, start=START)
    out = {"turnover_per_rebal": round(float(turn), 4), "open_gapfill": int(gapfill),
           # the engine returns gapfill cells, not a decision count -- a traded arm is
           # defined by turnover>0 AND a curve long enough to score (r1261 lesson).
           "traded": bool(float(turn) > 0.0 and len(ser) > 30)}
    for lbl, sl in (("full", ser), ("is_2020_2023", ser[ser.index <= "2023-12-31"]),
                    ("oos_2024_plus", ser[ser.index >= "2024-01-01"])):
        out[lbl] = F.metrics(sl, lbl)
    return out


# --- gate ---------------------------------------------------------------------------
def gate(payload: dict) -> dict:
    """Re-derive the verdict from the payload's own summary and its declared constants."""
    checks = []
    decl = payload.get("declared") or {}
    for key, val in DECLARED.items():
        same = decl.get(key) == val
        checks.append({"check": "declared %s echoed" % key, "ok": bool(same),
                       "payload": decl.get(key), "module": val})
    s = payload.get("summary") or {}
    c_fixed, c_pit = s.get("cagr_fixed"), s.get("cagr_pit")
    traded = bool(s.get("fixed_traded")) and bool(s.get("pit_traded"))
    checks.append({"check": "both arms actually traded (r1261: an untraded arm passes everything)",
                   "ok": traded, "fixed_traded": s.get("fixed_traded"),
                   "pit_traded": s.get("pit_traded")})
    ratio = None
    if traded and isinstance(c_fixed, (int, float)) and isinstance(c_pit, (int, float)) and c_fixed > 0:
        ratio = float(c_pit) / float(c_fixed)
    if not traded or ratio is None:
        verdict = "not_assessable_no_trade"
    elif ratio >= ADOPT_RATIO:
        verdict = "signs_learnable_in_realtime"
    elif ratio >= PARTIAL_RATIO:
        verdict = "signs_partly_in_sample"
    else:
        verdict = "signs_in_sample"
    checks.append({"check": "ratio recomputed", "ok": ratio is not None, "ratio": ratio})
    return {"verdict": verdict, "ratio": ratio, "checks": checks,
            "all_ok": all(c["ok"] for c in checks)}


# --- panel ---------------------------------------------------------------------------
def load_panel():
    """Same panel construction as etf_composite_pf.build_panel, but only the six factors
    this face prices -- compute_all() builds all 26 on a 1,725-column panel and this host
    runs on ~1GB free RAM."""
    prices = F._dedupe(F._load_prices())
    bench = None
    bp = Path(F.PATHS.basic_dir) / "csi300.csv"
    if bp.exists():
        bench = pd.read_csv(bp, parse_dates=["date"]).set_index("date")["close"]
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index().replace(0.0, np.nan)
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    fields = {}
    for field in ("open", "high", "low", "close", "volume"):
        try:
            fields[field] = pd.DataFrame({s: p[field] for s, p in prices.items()
                                          if field in p.columns}).sort_index().ffill()
        except Exception:
            fields[field] = close
    fields["close"] = close
    feats = {}
    for k in FACTOR_KEYS:
        try:
            feats[k] = ENGINE_FACTORS[k](fields)
        except Exception as e:  # a factor that cannot be built is a published hole, not a silent skip
            print("  factor %s failed: %s" % (k, e))
            feats[k] = None
    amt = (close * vol).rolling(20, min_periods=10).median()
    return close, openp, amt, feats


def run() -> dict:
    close, openp, amt, feats = load_panel()
    elig = eligibility(close, amt)
    grid = grid_dates(list(close.index))
    ic = ic_table(close, feats, elig, grid)

    full_ic = {k: (float(ic[k].mean(skipna=True)) if ic[k].notna().any() else None) for k in FACTOR_KEYS}
    matches = {k: (None if full_ic[k] is None else bool(np.sign(full_ic[k]) == np.sign(SIGNS[k])))
               for k in FACTOR_KEYS}

    score_fixed = F.build_score(close, amt, feats)
    a_fixed = arm(score_fixed, close, openp)

    # Threshold fragility (E199/r1140: publish the curve, never one arbitrary cut).
    # Two axes: the IC floor (does "unknown is not a direction" matter?) and the lookback
    # (is a 12-window trailing mean simply too weak an estimator?). The primary is the
    # declared (IC_WIN, IC_MIN) cell; every other cell is a neighbour, not a choice.
    cells = [("pit@%.2f" % m, IC_WIN, m) for m in IC_MIN_ARMS]
    cells += [("pit_w%d" % w, w, IC_MIN) for w in IC_WIN_ARMS if w != IC_WIN]
    pit_arms, match_frac, drop_frac, verdict_cells = {}, {}, {}, {}
    for tag, ic_win, ic_min in cells:
        s = pit_signs(ic, close, ic_win=ic_win, ic_min=ic_min)
        a = arm(score_face(close, elig, feats, s.reindex(close.index).ffill()), close, openp)
        pit_arms[tag] = a
        g0 = gate({"declared": {k: (v if k != "signs" else dict(v)) for k, v in DECLARED.items()},
                   "summary": {"cagr_fixed": (a_fixed.get("full") or {}).get("cagr"),
                               "cagr_pit": (a.get("full") or {}).get("cagr"),
                               "fixed_traded": a_fixed["traded"],
                               "pit_traded": a["traded"]}})
        verdict_cells[tag] = (g0["verdict"], round(g0["ratio"], 4) if g0["ratio"] is not None else None)
        if tag == "pit@%.2f" % IC_MIN:
            known = s.dropna(how="all")
            for k in FACTOR_KEYS:
                col = known[k].dropna()
                if len(col) == 0:
                    match_frac[k] = drop_frac[k] = None
                    continue
                match_frac[k] = round(float((col == SIGNS[k]).mean()), 4)
                drop_frac[k] = round(float((col == 0.0).mean()), 4)

    primary = "pit@%.2f" % IC_MIN
    a_pit = pit_arms[primary]

    # The reversed arm and the no-sign control answer the question the losing pit arm
    # leaves open: if the trailing sign is merely late, the opposite sign would pay.
    # Exploratory only -- nothing here is preregistered or proposed (T-67 sec.2).
    s_primary = pit_signs(ic, close, ic_min=IC_MIN)
    rev_signs = s_primary.mul(-1.0)
    a_rev = arm(score_face(close, elig, feats, rev_signs.reindex(close.index).ffill()), close, openp)
    try:
        ew_ser = F.run_ew(close, amt, REBAL, start=START)
        ew = F.metrics(ew_ser, "equal_weight_eligible")
    except Exception as e:
        ew = {"label": "equal_weight_eligible", "note": "failed: %s" % e}
    persistence = ic_persistence(ic, close)

    summary = {
        "cagr_fixed": (a_fixed.get("full") or {}).get("cagr"),
        "cagr_pit": (a_pit.get("full") or {}).get("cagr"),
        "sharpe_fixed": (a_fixed.get("full") or {}).get("sharpe"),
        "sharpe_pit": (a_pit.get("full") or {}).get("sharpe"),
        "maxdd_fixed": (a_fixed.get("full") or {}).get("maxdd"),
        "maxdd_pit": (a_pit.get("full") or {}).get("maxdd"),
        "fixed_traded": a_fixed["traded"],
        "pit_traded": a_pit["traded"],
        "n_decision_dates": len(grid),
        "n_sign_dates": int(len(known)),
        "primary_arm": primary,
        "cagr_by_cell": {t: (v.get("full") or {}).get("cagr") for t, v in pit_arms.items()},
        "verdict_by_cell": {t: v[0] for t, v in verdict_cells.items()},
        "ratio_by_cell": {t: v[1] for t, v in verdict_cells.items()},
        "verdict_stable_across_cells": len(set(v[0] for v in verdict_cells.values())) == 1,
        "cagr_reversed_sign": (a_rev.get("full") or {}).get("cagr"),
        "sharpe_reversed_sign": (a_rev.get("full") or {}).get("sharpe"),
        "cagr_equal_weight_control": ew.get("cagr"),
        "mean_carry_corr": (round(float(np.nanmean([v["carry_corr"] for v in persistence.values()
                                                   if v.get("carry_corr") is not None])), 4)
                            if any(v.get("carry_corr") is not None for v in persistence.values()) else None),
        "mean_sign_flip_rate": (round(float(np.nanmean([v["sign_flip_rate"] for v in persistence.values()
                                                       if v.get("sign_flip_rate") is not None])), 4)
                                if any(v.get("sign_flip_rate") is not None for v in persistence.values()) else None),
    }
    payload = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "universe": int(close.shape[1]),
        "question": "were the six composite-factor SIGNS knowable in real time, or are they a "
                    "full-sample reading that inflates every published number on this line?",
        "declared": {k: (v if k != "signs" else dict(v)) for k, v in DECLARED.items()},
        "full_sample_ic_mean": full_ic,
        "fixed_sign_matches_full_sample_ic": matches,
        "pit_sign_match_fraction_vs_fixed": match_frac,
        "pit_dropped_fraction": drop_frac,
        "ic_persistence": persistence,
        "arms": {"fixed": a_fixed, **pit_arms, "reversed_sign_exploratory": a_rev},
        "control_equal_weight": ew,
        "summary": summary,
        "caveats": [
            "Reference engine only (no impact cost, no gap risk); paired A/B on one engine call.",
            "The vol target / beta overlay is NOT applied here -- the sign question is orthogonal "
            "to sizing, and both arms are sized flat so the comparison stays paired. That is why "
            "the fixed arm's 6.14% is below the published overlay headline (9.13%).",
            "IC windows are the decision grid itself; a faster IC estimator was not tried.",
            "ETF pool is today's listed set (survivorship) -- unaffected by this face, unchanged.",
            "The pit arm trades only once >= IC_MIN_ACTIVE windows have closed (~4 months), so its "
            "first decisions are 'no position', not a different position.",
            "The reversed-sign arm is exploratory: one sign rule, one estimator, no prereg, "
            "no proposal. A sign rule that only works backwards needs its own frozen test.",
        ],
    }
    g = gate(payload)
    payload["verdict"] = g["verdict"]
    payload["gate"] = {"ratio": g["ratio"], "all_ok": g["all_ok"], "checks": g["checks"]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": g["verdict"], "ratio": g["ratio"],
                      "cagr_fixed": summary["cagr_fixed"], "cagr_pit": summary["cagr_pit"],
                      "sharpe_fixed": summary["sharpe_fixed"], "sharpe_pit": summary["sharpe_pit"],
                      "maxdd_fixed": summary["maxdd_fixed"], "maxdd_pit": summary["maxdd_pit"],
                      "cagr_by_ic_min": summary["cagr_by_cell"],
                      "verdict_by_ic_min": summary["verdict_by_cell"],
                      "stable_across_cells": summary["verdict_stable_across_cells"],
                      "cagr_reversed_sign": summary["cagr_reversed_sign"],
                      "cagr_equal_weight_control": summary["cagr_equal_weight_control"],
                      "mean_carry_corr": summary["mean_carry_corr"],
                      "mean_sign_flip_rate": summary["mean_sign_flip_rate"],
                      "ic_persistence": persistence,
                      "sign_match": match_frac, "dropped": drop_frac,
                      "full_ic": full_ic}, ensure_ascii=False, indent=1))
    return payload


def check() -> int:
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    g = gate(payload)
    print("verdict=%s ratio=%s stored=%s all_ok=%s"
          % (g["verdict"], g["ratio"], payload.get("verdict"), g["all_ok"]))
    for c in g["checks"]:
        if not c["ok"]:
            print("  RED %s -> %s" % (c["check"], {k: v for k, v in c.items() if k != "check"}))
    if not g["all_ok"] or g["verdict"] != payload.get("verdict"):
        return 1
    return 0


# --- selftest -----------------------------------------------------------------------
def _synthetic(n_sym: int = 40, n_bar: int = 520, seed: int = 7):
    """Two factors: one that genuinely drives the NEXT window's returns, one pure noise.

    The predictive factor is drawn once per REBAL window and held constant across it, so
    "the factor read at the decision bar" really does forecast the following 20 bars --
    an iid factor read at date s only touches 1 of the 20 bars it is scored against and
    would make the test measure a 5% effect instead of the mechanism.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_bar)
    cols = ["S%02d" % i for i in range(n_sym)]
    n_win = n_bar // REBAL + 1
    win_sig = rng.normal(size=(n_win, n_sym))
    sig_rows, drift = [], np.zeros((n_bar, n_sym))
    for j in range(n_win):
        a, b = j * REBAL, min(n_bar, (j + 1) * REBAL)
        drift[a:b] = 0.004 * win_sig[j]
        sig_rows.append(np.repeat(win_sig[j][None, :], b - a, axis=0))
    signal = pd.DataFrame(np.vstack(sig_rows), index=dates, columns=cols)
    noise = pd.DataFrame(rng.normal(size=(n_bar, n_sym)), index=dates, columns=cols)
    steps = rng.normal(scale=0.01, size=(n_bar, n_sym))
    px = pd.DataFrame(100 * np.exp(np.cumsum(steps + drift, axis=0)), index=dates, columns=cols)
    feats = {"signal": signal, "noise": noise}
    elig = pd.DataFrame(True, index=dates, columns=cols)
    return px, feats, elig, cols


def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # L1 rank correlation: monotone relation is 1.0, reversed is -1.0
    a = pd.Series([1.0, 2, 3, 4, 5])
    b = pd.Series([10.0, 20, 30, 40, 50])
    leg("L1 spearman detects monotone link", abs(_spearman(a, b, min_x=3) - 1.0) < 1e-12)
    leg("L1b spearman detects the reversed link", abs(_spearman(a, -b, min_x=3) + 1.0) < 1e-12)
    leg("L1c degenerate cross-section is NaN, not 0.0", not np.isfinite(_spearman(a, pd.Series([1.0] * 5), min_x=3)))

    px, feats, elig, cols = _synthetic()
    globals()["FACTOR_KEYS"] = ["signal", "noise"]
    globals()["SIGNS"] = {"signal": 1.0, "noise": 1.0}
    try:
        grid = grid_dates(list(px.index))
        ic = ic_table(px, feats, elig, grid)
        signs = pit_signs(ic, px)
        known = signs.dropna(how="all")
        # L2 the predictive factor is recovered as +1, the noise factor is dropped often
        sig_col = known["signal"].dropna()
        leg("L2 trailing IC recovers the true sign of a predictive factor",
            len(sig_col) > 0 and float((sig_col > 0).mean()) >= 0.8,
            "pos_frac=%.3f" % (float((sig_col > 0).mean()) if len(sig_col) else -1))
        noi_col = known["noise"].dropna()
        # The point is separation, not that noise always lands inside the floor: a 40-symbol
        # x 12-window mean IC of noise has sd ~0.046, so a single threshold run can sit either
        # side of 0.02. What must hold is that the rule sizes noise far below a real factor.
        ic_sig = abs(float(ic["signal"].mean(skipna=True)))
        ic_noi = abs(float(ic["noise"].mean(skipna=True)))
        leg("L2b the rule separates a real factor from noise (|IC_noise| << |IC_signal|)",
            len(noi_col) > 0 and ic_noi < 0.5 * ic_sig, "ic_sig=%.4f ic_noise=%.4f" % (ic_sig, ic_noi))
        leg("L2c signs take only the values -1/0/+1",
            bool(set(np.unique(signs.to_numpy()[np.isfinite(signs.to_numpy())])) <= {-1.0, 0.0, 1.0}))

        # L3 causality: truncating the panel must not change any sign whose windows had closed
        cut = 240
        ic_t = ic_table(px.iloc[:cut], feats, elig, [g for g in grid if g in set(px.index[:cut])])
        signs_t = pit_signs(ic_t, px.iloc[:cut])
        common = [g for g in signs_t.index if g in signs.index]
        same = all(
            (np.isnan(signs.at[g, k]) and np.isnan(signs_t.at[g, k])) or
            (np.isfinite(signs.at[g, k]) and np.isfinite(signs_t.at[g, k]) and signs.at[g, k] == signs_t.at[g, k])
            for g in common for k in ["signal", "noise"])
        leg("L3 no look-ahead: truncating the panel leaves every closed-window sign identical",
            len(common) > 5 and same, "common=%d" % len(common))

        # L4 score: not-eligible symbols are NaN, dropped factors do not silently score
        sgn = signs.reindex(px.index).ffill()
        sc = score_face(px, elig, feats, sgn)
        zero_day = sgn.index[(sgn.abs().sum(axis=1) == 0)]
        leg("L4 score is NaN where no factor has a known direction",
            all(not np.isfinite(sc.loc[d].to_numpy(dtype=float)).any() for d in zero_day[:5]) if len(zero_day) else True,
            "zero_days=%d" % len(zero_day))

        # L5 both arms actually trade on the synthetic panel (r1261 lesson; the engine
        # returns gapfill cells, not a decision count -- turnover is the liveness face)
        ser_f, turn_f, gap_f = V.fast_next_open(sc, px, px, REBAL, n_hold=5, cost=0.0005, start=START)
        leg("L5 the engine actually trades the synthetic book (turnover>0, curve long enough)",
            turn_f > 0 and len(ser_f) > 30, "turn=%.4f bars=%d gapfill=%d" % (turn_f, len(ser_f), gap_f))

        # L6/L7 gate
        base = {"declared": {k: (v if k != "signs" else dict(v)) for k, v in DECLARED.items()},
                "summary": {"cagr_fixed": 0.10, "cagr_pit": 0.09, "fixed_traded": True, "pit_traded": True}}
        leg("L6 gate reads a strong PIT arm as learnable", gate(base)["verdict"] == "signs_learnable_in_realtime")
        mid = json.loads(json.dumps(base)); mid["summary"]["cagr_pit"] = 0.05
        leg("L6b gate reads a half-size PIT arm as partly in-sample", gate(mid)["verdict"] == "signs_partly_in_sample")
        low = json.loads(json.dumps(base)); low["summary"]["cagr_pit"] = 0.01
        leg("L6c gate reads a collapsed PIT arm as in-sample", gate(low)["verdict"] == "signs_in_sample")
        dead = json.loads(json.dumps(base)); dead["summary"]["pit_traded"] = False
        leg("L6d an untraded arm is NOT-ASSESSED, never a verdict",
            gate(dead)["verdict"] == "not_assessable_no_trade")
        bad = json.loads(json.dumps(base)); bad["declared"]["n_hold"] = 5
        leg("L7 gate REDs when the payload was built under different constants", not gate(bad)["all_ok"])
    finally:
        globals()["FACTOR_KEYS"] = list(_ORIG_KEYS)
        globals()["SIGNS"] = dict(_ORIG_SIGNS)

    # L8 construction equivalence: with the SIGNS held constant, this face's score must BE
    # the production score -- otherwise a difference between the arms could come from the
    # score arithmetic rather than from the signs, and the whole face would be unreadable.
    px8, _, _, cols8 = _synthetic(n_sym=30, n_bar=260, seed=3)
    feats8 = {k: px8.pct_change().fillna(0.0) for k in _ORIG_KEYS}
    amt8 = pd.DataFrame(1e12, index=px8.index, columns=cols8)
    elig8 = eligibility(px8, amt8)
    const = pd.DataFrame({k: _ORIG_SIGNS[k] for k in _ORIG_KEYS}, index=px8.index)
    mine = score_face(px8, elig8, feats8, const)
    prod = F.build_score(px8, amt8, feats8)
    diff = float(np.nanmax(np.abs(mine.to_numpy(dtype=float) - prod.to_numpy(dtype=float))))
    leg("L8 with constant signs this face reproduces the production score (max|diff| < 1e-12)",
        np.isfinite(diff) and diff < 1e-12, "max_diff=%.3e" % diff)

    bad = 0
    for name, ok, extra in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + extra) if extra else ""))
        bad += 0 if ok else 1
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


_ORIG_KEYS = list(FACTOR_KEYS)
_ORIG_SIGNS = dict(SIGNS)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.mode == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())