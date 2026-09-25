"""P-1e zoo behavior-factor constructors (#85/#92/#93) + offline selftest.

Parameterization frozen r219 (bm-b) from the STR notebook + vendored
scr/core.py deep-read (no-license repo -> code structurally not copied;
formulas re-implemented from the frozen parameterization record in
research/shortline/ASTYLE_ZOO.md rows #85/#92/#93 and
research/digests/DIGEST-20260926-zoo-paramfreeze-92-94.md).

Conventions (P-1c harness, no rewrite):
  - panels are float64 DataFrames on the union calendar; OHLC ffilled
  - returns are close-based (close/close.shift(1)-1), consistent with the
    fwd_ret convention of the IC layer
  - rolling windows use pandas defaults (min_periods=window)

Selftest fixtures mirror production input shapes (r157/r180 pairing
discipline): the #93 ARC path is gated against a brute-force direct
reference on a synthetic panel; #85/#92 get semantic invariants.
"""
import time

import numpy as np
import pandas as pd

N_ARC = 60          # #93 frozen window (validity-masked trading-day analogue)
DELTA_STV = 0.7     # calc_weight default (scr/core.py, extracted)
THETA_SAL = 0.1     # sigma denominator theta (Cosemans-Frehen normalization)
STV_X = 0.1         # |r| threshold (notebook cell 22)
W_ROLL = 20         # #85 legs and #92 rolling windows (frozen)
TR_CLIP = 0.99      # decay-math guard for turnover spikes (disclosed)


def _xs_spearman_series(fa: pd.DataFrame, fb: pd.DataFrame) -> pd.Series:
    """Per-date cross-sectional spearman between two factor frames.

    Mirrors _ic_series_fast rank-after-pairing math (pair first, then rank
    within the per-date intersection).
    """
    mask = fa.notna() & fb.notna()
    n = mask.sum(axis=1)
    F = fa.where(mask).rank(axis=1)
    G = fb.where(mask).rank(axis=1)
    fm = F.mean(axis=1)
    gm = G.mean(axis=1)
    df_ = F.sub(fm, axis=0)
    dg_ = G.sub(gm, axis=0)
    cov = (df_ * dg_).sum(axis=1)
    sf = np.sqrt((df_ ** 2).sum(axis=1))
    sg = np.sqrt((dg_ ** 2).sum(axis=1))
    ic = cov / (sf * sg)
    ic = ic.where(sf > 0).where(sg > 0).where(n >= 5)
    return ic.dropna()


def build_zoo85_terrified(rets):
    """#85 main (frozen r219): salience-weighted return, roll20 mean+std.

    sigma = |r - r_cs_mean| / (|r| + |r_cs_mean| + 0.1); bench = equal-weight
    cross-sectional mean of panel returns (= scr/core.calc_sigma default
    when bench=None; the report text names CSI-All-Share and the notebook's
    方正-section comment names HS300 -- both external-index benches are
    unavailable on the in-repo stock cache, so the panel-native
    cross-sectional mean is frozen with the deviation disclosed).
    terrified = 0.5 * (roll20_mean(sigma*r) + roll20_std(sigma*r)).
    Direction: reversal (high terrified -> expect negative forward IC).
    """
    bench = rets.mean(axis=1)                     # skipna default
    rv = rets.values
    bv = bench.values[:, None]
    sigma = np.abs(rv - bv) / (np.abs(rv) + np.abs(bv) + THETA_SAL)
    weighted = pd.DataFrame(sigma * rv, index=rets.index, columns=rets.columns)
    avg = weighted.rolling(W_ROLL).mean()
    std = weighted.rolling(W_ROLL).std()
    return (avg + std) * 0.5


def build_zoo85_stv(rets, tr_frac):
    """#85 STV variant (frozen r219): salience fn per notebook cell 22.

    sigma_stv = |r|*100 if |r|>=0.1 else turnover(fraction); weights =
    delta^(desc rank)/row-mean(delta^rank), delta=0.7 (calc_weight);
    STV = roll20 cov(w, r). r NaN -> NaN; turnover branch NaN when TR NaN.
    """
    absr = rets.abs()
    cond_hi = absr.values >= STV_X
    vals = np.where(cond_hi, absr.values * 100.0, tr_frac.values)
    vals[~np.isfinite(absr.values)] = np.nan
    sigma_stv = pd.DataFrame(vals, index=rets.index, columns=rets.columns)
    rank = sigma_stv.rank(axis=1, ascending=False)   # NaN stays NaN
    a = DELTA_STV ** rank
    b = a.mean(axis=1)
    w = a.div(b, axis=0)
    return w.rolling(W_ROLL).cov(rets)


def _flip_roll_mean(leg, cond):
    """corr2 leg: flip today's return where cond, then roll20 mean."""
    flip = np.where(cond, -leg.values, leg.values)
    flip[~np.isfinite(leg.values)] = np.nan
    flip[~np.isfinite(cond)] = np.nan
    return pd.DataFrame(flip, index=leg.index,
                        columns=leg.columns).rolling(W_ROLL).mean()


def build_zoo92_coin_team(close, open_, tr_frac):
    """#92 main (frozen r218): three-leg conditional-flip reversal, rolling20.

    legs: inter=close/close{t-1}-1, intra=close/open-1, on=open/close{t-1}-1.
    per leg: corr1 = -roll20_mean if roll20_std < its date cross-sectional
    mean else +roll20_mean; corr2 = roll20_mean of the leg return flipped
    where dTR < its date cross-sectional mean; leg = 0.5*(corr1+corr2);
    factor = sum of the three legs (equal weight, frozen; the revise
    synthetic path dTR convention t/t-1 per freeze card).
    Direction: reversal (low value long -> expect negative forward IC on
    the raw factor; community backtests take -f top-k).
    """
    legs = {
        "inter": close / close.shift(1) - 1.0,
        "intra": close / open_ - 1.0,
        "on": open_ / close.shift(1) - 1.0,
    }
    dtr = tr_frac - tr_frac.shift(1)
    dtr_xs = dtr.mean(axis=1)
    cond_tr = dtr.values < dtr_xs.values[:, None]
    out = None
    for leg in legs.values():
        mu = leg.rolling(W_ROLL).mean()
        sg = leg.rolling(W_ROLL).std()
        sg_xs = sg.mean(axis=1)
        cond_vol = sg.values < sg_xs.values[:, None]
        c1v = np.where(cond_vol, -mu.values, mu.values)
        c1v[~np.isfinite(sg.values) | ~np.isfinite(mu.values)] = np.nan
        c1 = pd.DataFrame(c1v, index=leg.index, columns=leg.columns)
        c2 = _flip_roll_mean(leg, cond_tr)
        legf = 0.5 * (c1 + c2)
        out = legf if out is None else out + legf
    return out


def build_zoo93_arc_family(tr_frac, vwap, close):
    """#93 ARC/CGO + moment variants (frozen r218, measured re-check clause).

    Survival weight ATR(t,k) = TR(t-k) * prod(1-TR) over (t-k, t]; via
    C_t = cumsum(log(1-TR)) the window sums factor exp(C_t) out of every
    ratio: RP(t) = RS1/RS0 with RSj(t) = sum over window rows [t-60, t-1] of
    [TR*exp(-C)*P^j](i). P = vwap (freeze card: 成交均价口径; close 口径 =
    classic Grinblatt-Han variant, disclosed, not in batch v1).
    Window semantics: 60 panel rows with validity count == 60
    (trading-day analogue; long-suspension stocks lose coverage rather
    than silently mixing calendar gaps -- disclosed).
    exp(-C) reaches exp(~200) over the full panel: fine in float64;
    non-finite RS0 masks the cell (counter returned).
    Direction: disposition premium -- low CGO/ARC outperforms -> raw-factor
    forward IC expected NEGATIVE (r219 prereg erratum: draft docstring said
    "positive"; freeze-card truth source = zoo row #93 low-value-long;
    comment-only fix, zero computation change).
    """
    valid = close.notna() & tr_frac.notna() & vwap.notna()
    V = valid.values.astype(np.float64)
    TRc = np.clip(tr_frac.values, 0.0, TR_CLIP)
    dC = np.where(V > 0, np.log1p(-TRc), 0.0)
    C = np.cumsum(dC, axis=0)
    P = vwap.values
    TRv = np.where(V > 0, TRc, 0.0)
    X0 = TRv * np.exp(-C)
    X0[~np.isfinite(X0)] = 0.0
    RS = {}
    for j in range(5):
        Xj = X0 * (P ** j)
        Xj[~np.isfinite(Xj)] = 0.0
        cs = np.cumsum(Xj, axis=0)
        rs = np.full_like(cs, np.nan)
        # window rows [t-60, t-1] for t in [61, T-1]:
        # RS[t] = cs[t-1] - cs[t-61]
        rs[N_ARC + 1:] = cs[N_ARC:-1] - cs[:-(N_ARC + 1)]
        RS[j] = rs
        del Xj, cs
    cs_v = np.cumsum(V, axis=0)
    vc = np.full_like(cs_v, np.nan)
    vc[N_ARC + 1:] = cs_v[N_ARC:-1] - cs_v[:-(N_ARC + 1)]
    ok = (vc == float(N_ARC)) & np.isfinite(RS[0]) & (RS[0] > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        m = {j: np.where(ok, RS[j] / np.where(ok, RS[0], np.nan), np.nan)
             for j in range(5)}
    rp = m[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        arc = np.where(ok, (P - rp) / P, np.nan)
        arc[~np.isfinite(P)] = np.nan
        vrc = m[2] - rp ** 2
        src = (m[3] - 3 * rp * m[2] + 2 * rp ** 3) / vrc ** 1.5
        krc = (m[4] - 4 * rp * m[3] + 6 * rp ** 2 * m[2] - 3 * rp ** 4) \
            / vrc ** 2
    idx, cols = tr_frac.index, tr_frac.columns
    fam = {
        "zoo93_arc": pd.DataFrame(arc, index=idx, columns=cols),
        "zoo93_vrc": pd.DataFrame(vrc, index=idx, columns=cols),
        "zoo93_src": pd.DataFrame(src, index=idx, columns=cols),
        "zoo93_krc": pd.DataFrame(krc, index=idx, columns=cols),
    }
    n_bad = int((~np.isfinite(arc)).sum())
    return fam, n_bad


# ---------------------------------------------------------------- selftest

def _arc_bruteforce(tr_frac, vwap, close, t_max):
    """Direct-loop reference for ARC on a small panel (equivalence gate)."""
    T, N = close.shape
    out = np.full((T, N), np.nan)
    TRc = np.clip(tr_frac.values, 0.0, TR_CLIP)
    Pv = vwap.values
    Cv = close.values
    for col in range(N):
        for t in range(T):
            if t < N_ARC + 1 or not np.isfinite(Pv[t, col]):
                continue
            rows = []
            for i in range(t - N_ARC, t):
                if (np.isfinite(Cv[i, col]) and np.isfinite(TRc[i, col])
                        and np.isfinite(Pv[i, col])):
                    rows.append(i)
            if len(rows) != N_ARC:
                continue
            wsum = num = 0.0
            for i in rows:
                w = TRc[i, col]
                for j in range(i + 1, t + 1):
                    w *= (1.0 - TRc[j, col])
                wsum += w
                num += w * Pv[i, col]
            if wsum > 0:
                out[t, col] = (Pv[t, col] - num / wsum) / Pv[t, col]
    return out


def selftest():
    t0 = time.time()
    rng = np.random.default_rng(20260926)
    T, N = 200, 8
    idx = pd.date_range("2020-01-01", periods=T, freq="B")
    cols = [f"S{i}" for i in range(N)]
    close = pd.DataFrame(10.0 + np.cumsum(rng.normal(0, 0.2, (T, N)), axis=0),
                         index=idx, columns=cols)
    # stock 0: flat price, constant turnover -> ARC == 0 after warmup
    close["S0"] = 10.0
    open_ = close.shift(1).fillna(10.0) * 1.001
    tr = pd.DataFrame(0.01 + 0.05 * rng.random((T, N)), index=idx,
                      columns=cols)
    tr["S0"] = 0.1
    vwap = close * (1.0 + 0.001 * rng.random((T, N)))
    vwap["S0"] = 10.0          # flat-price stock: constant vwap too

    # --- [ARC vs brute force] production-input-shaped synthetic panel
    fam, n_bad = build_zoo93_arc_family(tr, vwap, close)
    ref = _arc_bruteforce(tr, vwap, close, T)
    got = fam["zoo93_arc"].values
    both = np.isfinite(ref) & np.isfinite(got)
    n_both = int(both.sum())
    worst = float(np.abs(ref - got)[both].max()) if n_both else 9.9
    finite_ref = int(np.isfinite(ref).sum())
    ok_arc = n_both > 0 and worst < 1e-9 and n_both == finite_ref
    # flat-price stock: ARC == 0 where finite
    s0 = fam["zoo93_arc"]["S0"].dropna()
    ok_flat = len(s0) > 0 and float(s0.abs().max()) < 1e-12
    # warmup: rows before N_ARC+1 must be NaN
    ok_warm = bool(fam["zoo93_arc"].iloc[:N_ARC + 1].isna().all().all())
    # variant moments: VRC finite on the ARC mask; SRC/KRC finite where
    # VRC materially positive -- near-flat cells carry +-1e-14 float-
    # cancellation noise (undefined skew/kurt -> NaN, naturally masked
    # downstream); 1e-12 sits ~10 orders below real dispersion (O(0.01+))
    vrc_v = fam["zoo93_vrc"].values
    src_v = fam["zoo93_src"].values
    krc_v = fam["zoo93_krc"].values
    n_degen = int((np.isfinite(vrc_v[both])
                   & (np.abs(vrc_v[both]) <= 1e-12)).sum())
    ok_vrc = bool(np.isfinite(vrc_v[both]).all())
    pos = both & np.isfinite(vrc_v) & (vrc_v > 1e-12)
    ok_mom = ok_vrc and bool(np.isfinite(src_v[pos]).all()
                             and np.isfinite(krc_v[pos]).all())
    print(f"  [1/3] ARC vs brute-force: n_both={n_both} "
          f"finite_ref={finite_ref} worst={worst:.2e} "
          f"flat_ok={ok_flat} warmup_ok={ok_warm} mom_ok={ok_mom} "
          f"(degenerate VRC==0 cells masked: {n_degen})",
          flush=True)

    # --- [#85 semantic] constant returns -> zero salience -> terrified==0
    rets = close / close.shift(1) - 1.0
    flat_close = pd.DataFrame(np.tile(np.linspace(10, 12, T)[:, None],
                                      (1, N)), index=idx, columns=cols)
    flat_rets = flat_close / flat_close.shift(1) - 1.0
    terr_flat = build_zoo85_terrified(flat_rets)
    fin = terr_flat.dropna()
    ok_terr = len(fin) > 0 and float(fin.abs().max().max()) < 1e-12
    terr = build_zoo85_terrified(rets)
    ok_terr_shape = bool(terr.notna().sum().sum() > 0
                         and terr.shape == close.shape)
    print(f"  [2/3] zoo85 semantic: flat_zero={ok_terr} "
          f"shape_ok={ok_terr_shape}", flush=True)

    # --- [#92/#85_stv shape+finite on production-shaped input]
    coin = build_zoo92_coin_team(close, open_, tr)
    stv = build_zoo85_stv(rets, tr)
    ok_coin = bool(coin.notna().sum().sum() > 0
                   and coin.iloc[:W_ROLL].isna().all().all())
    ok_stv = bool(stv.notna().sum().sum() > 0)
    # negative fixture: coin_team with constant cross-section (all rows
    # identical, open==close) -> intra leg == 0, inter/on legs identical;
    # cond_vol False everywhere (sigma == xs mean) -> corr1 = +mu; dTR
    # identical -> cond_tr False -> corr2 = mu; each leg = 0.5*(mu+mu) = mu;
    # total = inter_mu + 0 + on_mu = 2 * inter_mu
    cs_close = pd.DataFrame(np.tile(np.linspace(10, 11, T)[:, None],
                                    (1, 4)), index=idx,
                            columns=["A", "B", "C", "D"])
    cs_tr = pd.DataFrame(0.05, index=idx, columns=cs_close.columns)
    coin_cs = build_zoo92_coin_team(cs_close, cs_close, cs_tr)
    mu_inter = (cs_close / cs_close.shift(1) - 1.0).rolling(W_ROLL).mean()
    expect = 2.0 * mu_inter
    got_cs = coin_cs
    common = expect.dropna().index
    worst_cs = float((expect.loc[common] - got_cs.loc[common])
                     .abs().max().max()) if len(common) else 9.9
    ok_coin_neg = len(common) > 0 and worst_cs < 1e-12
    print(f"  [3/3] zoo92/stv: coin_ok={ok_coin} stv_ok={ok_stv} "
          f"const_cs_math={ok_coin_neg} (worst {worst_cs:.1e})", flush=True)

    ok = (ok_arc and ok_flat and ok_warm and ok_mom and ok_terr
          and ok_terr_shape and ok_coin and ok_stv and ok_coin_neg)
    print(f"SELFTEST {'PASS' if ok else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(selftest())
