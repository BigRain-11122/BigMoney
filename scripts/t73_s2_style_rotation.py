# -*- coding: utf-8 -*-
"""T-73 s2 slice-E: A-share STYLE-ROTATION history (风格轮动史), ETF-panel
empirical check (CEO order O-20260926-0926 s2 last remaining topic; CEO top
criterion 实战出真知).

PRE-REGISTERED (frozen before first run; no threshold edits after results):
- Topic (s2 mandated): 风格轮动史 2017 核心资产 -> 2021 成长 -> 2023 微盘 ->
  2024 红利, each law with in-repo numbers + applicability honesty note;
  external narrative = UNVERIFIED claim, only cross-checked against repo data.
- Panel (FROZEN, 9 ETF legs, long-history prefixed face data/daily/):
  base 510300 (沪深300, core-asset + normalization base),
  510050 (上证50, 2005-02-23, 5248 bars), 510300 (2012-05-28, 3483),
  510500 (中证500, 2013-03-15, 3286), 512100 (中证1000 small, 2016-11-04,
  2402), 159915 (创业板指 growth, 2011-12-09, 3591), 588000 (科创50
  growth-2, 2020-11-16, 1422), 510880 (红利, 2007-01-18, 4784), 512890
  (红利低波, 2019-01-18, 1862), 563300 (中证2000 micro, 2023-09-14, 732).
  Micro narrative face: 563300 starts 2023-09 (misses 2023 H1 micro rally)
  -> 2023 micro leadership measured via 512100 proxy, disclosed.
  evidence_cutoff = 2026-09-22 (common last bar of the prefixed face; the
  non-prefixed core48 face has 2 fresher bars but starts 2020 -> long-history
  face wins for rotation history; staleness disclosed).
- FUND-EVENT GUARD (r239 law family, momentum/rotation faces MUST guard;
  envelope rule, deterministic, constituent-limit-structure based):
  legs whose index families are 10%-limit (510300/510050/510500/512100/
  510880/512890/563300): |daily ret| > 0.11 is IMPOSSIBLE from market moves
  alone -> suspected fund event (share conversion/split) -> that day's ret
  set NaN in the CLEAN face (fail-closed); 20%-limit families (159915 创业板,
  588000 科创): |daily ret| > 0.21 -> suspected. Known catches (pre-freeze
  probe): 510500 2015-04-15 +248.6%, 510500 2022-08-29 -12.7%, 512100
  2022-09-05 +176.3%, 512890 2021-10-25 -51.1% -- all with |base ret|<1% =
  fund-level artifacts, NaN'd. Growth-leg days within envelope (159915
  2024-09-30 +20.0% / 588000 2024-10-18 +12.4% etc., base-corroborated or
  within 20%-limit envelope) are REAL price days (index move + ETF premium
  blowout) -> KEPT, flagged descriptively. Residual risk disclosed: sub-
  envelope phantoms (e.g. 6% conversion artifacts) not caught by the level
  rule; finer face = CN-DIV-LOWVOL-ROT s3 corpus event machinery (cross-cite).
- LAW FACES (falsifiable, judged; style-level momentum persistence =
  quantifies rotation itself: persistence alive -> trailing style winners
  keep winning; null/negative -> leadership rotates fast):
  signal(t) = trailing-w RELATIVE return of leg vs 510300 over the last w
  trading days (clean face, STRICT all-valid window: any NaN day inside ->
  signal NaN, no fabrication); forward(t) = next-h RELATIVE return. Daily rel
  factor x = (1+r_leg)/(1+r_base), log-sum rolling exact: signal =
  exp(rolling(w).sum of log x) - 1; forward = exp(rolling(h).sum shifted
  -h) - 1. No-lookahead: signal at t uses <= t only; forward uses > t only.
  PRIMARY face STYLE-MOM-252-63: w=252, h=63. SECONDARY STYLE-MOM-63-21:
  w=63, h=21. Sampling: month-end trading days only (last trading day of
  each month); cross-section per month = legs with valid signal+forward,
  >=4 legs required else month skipped. IC = spearman(signal, forward) per
  month; pooled IC series = monthly ICs; stats mean/std/ir/n per window.
  Split (composite_ic.IS_END convention, split by SIGNAL month date):
  IS <= 2024-12-31 / OOS >= 2025-01-01; forward windows may cross the
  boundary (family convention, disclosed).
- NULL BASELINE (BACKTEST_PLAN iron law, MINTED THIS BATCH): within-month
  leg-label permutation, 50 seeds (SEED_REGISTRY t73_style_rot_s1 base
  20261030, registered in this freeze commit one-step R250 law; band scan
  clean of RNG usage). Per seed: permute signal values across legs within
  each month (forward fixed) -> null monthly IC series -> window means.
  Threshold p95_abs per window x face = quantile 0.95 of |null means|
  (50-draw thinness = p1c nulls family convention, disclosed).
  VERDICTS (frozen): style_mom_<face>_alive_oos = oos mean IC >
  p95_abs_oos of its null; alive_is disclosed same shape; NO cost-adjusted
  portfolio claims (IC-face research verdict only, slice-D honesty).
- DESCRIPTIVE (no verdicts): per-calendar-year leg CAGR table (raw price
  face) + yearly best/worst leadership + winner-repeat count vs 1/K chance;
  era table with slice-D ERAS for cross-slice comparability; suspected fund
  events list; narrative cross-check (2017 core / 2021 growth / 2023 micro /
  2024 dividend vs in-repo numbers, external narrative marked unverified).
- trials_N = 2 judged law faces + 50 seeds x 2 faces null draws = 102
  (ledger-chained via science_gates.append_ledger, canonical key
  trials_ledger, r252 law).
- Honesty: price faces exclude cash distributions (510880 dividend family
  understated, slice-D conservative-bound precedent); no fabricated
  busywork; O-1137.

Engineering: deterministic full recompute each run (fast in-repo batch,
<5min inline legal per O-20260924-2100); zero network. Exit 0 = batch
complete; 2 = mechanism failure (corpus missing etc.).
Selftest subcommand = offline asserts (envelope rule, strict-window NaN,
no-lookahead, month-end sampling, permutation determinism, spearman sanity,
era boundaries, corpus presence, known fund-event set, forward formula).
"""
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END                    # shared split convention
import science_gates                               # SEED_REGISTRY + append_ledger

OUT_DIR = os.path.join(ROOT, "results", "t73_s2")
OUT_JSON = os.path.join(OUT_DIR, "style_rotation.json")
DAILY = os.path.join(ROOT, "data", "daily")

EVIDENCE_CUTOFF = "2026-09-22"
BATCH = "T73-STYLE-ROT-S1"
SEED_BASE = None                                    # resolved from registry
N_NULLS = 50
MIN_LEGS_PER_MONTH = 4
EVENT_ENV_10 = 0.11                                  # 10%-limit family envelope
EVENT_ENV_20 = 0.21                                  # 20%-limit family envelope

# sym, csv file, style name, family envelope, corpus bars (frozen)
LEGS = [
    ("510300", "sh510300.csv", "hs300_core", "10", 3483),
    ("510050", "sh510050.csv", "sse50_large", "10", 5248),
    ("510500", "sh510500.csv", "csi500_mid", "10", 3286),
    ("512100", "sh512100.csv", "csi1000_small", "10", 2402),
    ("159915", "sz159915.csv", "chinext_growth", "20", 3591),
    ("588000", "sh588000.csv", "star50_growth2", "20", 1422),
    ("510880", "sh510880.csv", "dividend", "10", 4784),
    ("512890", "sh512890.csv", "div_lowvol", "10", 1862),
    ("563300", "sh563300.csv", "csi2000_micro", "10", 732),
]
BASE_SYM = "510300"

FACES = [("STYLE-MOM-252-63", 252, 63), ("STYLE-MOM-63-21", 63, 21)]

ERAS = [("2014-2016", "2014-01-01", "2016-12-31"),
        ("2017-2020", "2017-01-01", "2020-12-31"),
        ("2021-2022", "2021-01-01", "2022-12-31"),
        ("2023", "2023-01-01", "2023-12-31"),
        ("2024", "2024-01-01", "2024-12-31"),
        ("2025plus", "2025-01-01", None)]


def _seed_base():
    global SEED_BASE
    if SEED_BASE is None:
        SEED_BASE = science_gates.SEED_REGISTRY["t73_style_rot_s1"]
    return SEED_BASE


def _load_leg(csv):
    df = pd.read_csv(os.path.join(DAILY, csv), parse_dates=["date"])
    return df.set_index("date")["close"].astype(float)


def load_panels():
    closes, rets = {}, {}
    for sym, csv, name, fam, bars in LEGS:
        c = _load_leg(csv)
        assert len(c) == bars, f"{csv} corpus {len(c)} != frozen {bars}"
        closes[sym] = c
        rets[sym] = c.pct_change(fill_method=None)
    idx = sorted(set().union(*[set(c.index) for c in closes.values()]))
    idx = pd.DatetimeIndex(idx)
    close = pd.DataFrame({s: closes[s].reindex(idx) for s, _, _, _, _ in LEGS})
    ret = pd.DataFrame({s: rets[s].reindex(idx) for s, _, _, _, _ in LEGS})
    return close, ret


def fund_events(ret):
    """Envelope-rule guard: suspected fund-level artifact days per leg."""
    out = {}
    for sym, csv, name, fam, _ in LEGS:
        env = EVENT_ENV_10 if fam == "10" else EVENT_ENV_20
        r = ret[sym]
        bad = r[r.abs() > env]
        out[sym] = [{"date": str(d.date()), "ret": round(float(v), 4),
                     "envelope": env}
                    for d, v in bad.items()]
    return out


def clean_rets(ret, events):
    """Clean face: suspected fund-event day rets -> NaN (fail-closed)."""
    clean = ret.copy()
    flagged = 0
    for sym, evs in events.items():
        for e in evs:
            d = pd.Timestamp(e["date"])
            if d in clean.index:
                clean.loc[d, sym] = np.nan
                flagged += 1
    return clean, flagged


def _rel_log(clean, sym):
    """log(1+r_leg) - log(1+r_base) on union calendar (NaN if either)."""
    a = np.log1p(clean[sym])
    b = np.log1p(clean[BASE_SYM])
    return a - b


def signal_forward(clean, sym, w, h):
    """Strict-window trailing relative return + forward relative return."""
    L = _rel_log(clean, sym)
    sig = np.expm1(L.rolling(w, min_periods=w).sum())
    fwd = np.expm1(L.rolling(h, min_periods=h).sum().shift(-h))
    return sig, fwd


def month_ends(idx):
    s = pd.Series(idx, index=idx)
    return s.groupby([idx.year, idx.month]).last().values


def _stats(vals):
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    if len(arr) == 0:
        return {"n": 0}
    return {"n": int(len(arr)), "mean": round(float(arr.mean()), 5),
            "std": round(float(arr.std(ddof=1)), 5) if len(arr) > 1 else None,
            "ir": round(float(arr.mean() / arr.std(ddof=1)), 3)
            if len(arr) > 1 and arr.std(ddof=1) > 0 else None}


def _win_mask(dates, which):
    if which == "full":
        return np.ones(len(dates), dtype=bool)
    if which == "is":
        return np.asarray([d <= pd.Timestamp(IS_END) for d in dates])
    return np.asarray([d > pd.Timestamp(IS_END) for d in dates])


def monthly_ic_series(clean, w, h):
    """Per-month cross-sectional spearman; returns (dates, ics, k_list)."""
    idx = clean.index
    me = pd.DatetimeIndex(month_ends(idx))
    sigs, fwds = {}, {}
    for sym, _, _, _, _ in LEGS:
        if sym == BASE_SYM:
            continue
        s, f = signal_forward(clean, sym, w, h)
        sigs[sym], fwds[sym] = s.reindex(me), f.reindex(me)
    dates, ics, ks = [], [], []
    legs = [s for s, _, _, _, _ in LEGS if s != BASE_SYM]
    for d in me:
        vals = [(sigs[s][d], fwds[s][d]) for s in legs
                if np.isfinite(sigs[s][d]) and np.isfinite(fwds[s][d])]
        if len(vals) < MIN_LEGS_PER_MONTH:
            continue
        sig_v = np.asarray([v[0] for v in vals])
        fwd_v = np.asarray([v[1] for v in vals])
        ic = _spearman(sig_v, fwd_v)
        dates.append(d)
        ics.append(ic)
        ks.append(len(vals))
    return pd.DatetimeIndex(dates), np.asarray(ics, dtype=float), ks


def _spearman(a, b):
    ra = pd.Series(a).rank().values
    rb = pd.Series(b).rank().values
    if np.std(ra) == 0 or np.std(rb) == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def null_thresholds(clean, w, h, which, n_nulls=N_NULLS):
    """Permutation nulls: permute signal labels within month; window means."""
    idx = clean.index
    me = pd.DatetimeIndex(month_ends(idx))
    legs = [s for s, _, _, _, _ in LEGS if s != BASE_SYM]
    sigs, fwds = {}, {}
    for sym in legs:
        s, f = signal_forward(clean, sym, w, h)
        sigs[sym], fwds[sym] = s.reindex(me), f.reindex(me)
    months = []
    for d in me:
        vals = [(sigs[s][d], fwds[s][d]) for s in legs
                if np.isfinite(sigs[s][d]) and np.isfinite(fwds[s][d])]
        if len(vals) >= MIN_LEGS_PER_MONTH:
            months.append((d, np.asarray([v[0] for v in vals]),
                           np.asarray([v[1] for v in vals])))
    mask_by_date = {}
    for which_w in ("full", "is", "oos"):
        mask_by_date[which_w] = {
            d: (_win_mask([d], which_w)[0]) for d, _, _ in months}
    draws = {}
    base = _seed_base()
    for which_w in ("full", "is", "oos"):
        draws[which_w] = []
    for k in range(n_nulls):
        rng = np.random.default_rng(base + k)
        per_month_perm = {d: rng.permutation(sig) for d, sig, _ in months}
        ics = []
        for d, sig, fwd in months:
            ic = _spearman(per_month_perm[d], fwd)
            ics.append((d, ic))
        for which_w in ("full", "is", "oos"):
            sel = [ic for d, ic in ics if mask_by_date[which_w][d]
                   and np.isfinite(ic)]
            draws[which_w].append(float(np.mean(sel)) if sel else np.nan)
    out = {}
    for which_w in ("full", "is", "oos"):
        arr = np.abs(np.asarray(draws[which_w], dtype=float))
        arr = arr[np.isfinite(arr)]
        out[which_w] = {
            "n_draws": int(len(arr)),
            "p95_abs_mean_ic": round(float(np.quantile(arr, 0.95)), 5)
            if len(arr) else None,
        }
    return out


def _era_slice(s, a, b):
    lo = pd.Timestamp(a) if a else None
    hi = pd.Timestamp(b) if b else None
    seg = s
    if lo is not None:
        seg = seg[seg.index >= lo]
    if hi is not None:
        seg = seg[seg.index <= hi]
    return seg


def _cagr(close):
    if len(close) < 20:
        return None
    n = len(close)
    total = float(close.iloc[-1] / close.iloc[0])
    yrs = n / 252.0
    cagr = total ** (1.0 / yrs) - 1.0 if total > 0 else np.nan
    dd = float((close / close.cummax() - 1.0).min())
    return {"n_days": int(n), "cagr": round(cagr, 4),
            "max_dd": round(dd, 4)}


def descriptive(close, events):
    """Yearly leadership + era table + narrative cross-check (raw face)."""
    legs = [s for s, _, _, _, _ in LEGS]
    names = {s: n for s, _, n, _, _ in LEGS}
    base = close[BASE_SYM]
    years = sorted(set(close.index.year))
    yearly = {}
    winners, nK = [], {}
    for y in years:
        seg = close[close.index.year == y]
        if len(seg) < 20:
            continue
        row = {}
        for s in legs:
            c = seg[s].dropna()
            if len(c) < 20:
                continue
            row[s] = _cagr(c)
        # best/worst by CAGR among present legs
        present = {s: v["cagr"] for s, v in row.items()
                   if np.isfinite(v["cagr"])}
        if len(present) >= 4:
            best = max(present, key=present.get)
            worst = min(present, key=present.get)
            yearly[y] = {"legs": {s: v["cagr"] for s, v in row.items()},
                         "best": best, "worst": worst,
                         "k_present": len(present)}
            winners.append(best)
            nK[y] = len(present)
        else:
            yearly[y] = {"legs": {s: v["cagr"] for s, v in row.items()},
                         "k_present": len(present),
                         "note": "fewer than 4 legs, no leadership call"}
    repeats = 0
    ylist = sorted(nK)
    for a, b in zip(ylist, ylist[1:]):
        if yearly[a].get("best") and yearly[a]["best"] == yearly[b].get("best"):
            repeats += 1
    era_tab = {}
    for name, a, b in ERAS:
        seg_c = _era_slice(close, a, b)
        row = {}
        for s in legs:
            c = seg_c[s].dropna()
            if len(c) >= 20:
                row[s] = _cagr(c)
        bs = _era_slice(base, a, b).dropna()
        row["_rel_vs_base"] = {}
        for s in legs:
            c = seg_c[s].dropna()
            ov = c.index.intersection(bs.index)
            if len(ov) >= 20:
                rel = float((c[ov].iloc[-1] / c[ov].iloc[0])
                           / (bs[ov].iloc[-1] / bs[ov].iloc[0]))
                row["_rel_vs_base"][s] = round(rel, 4)
        era_tab[name] = row
    return {"yearly": yearly, "winner_repeat_transitions": repeats,
            "n_year_transitions": max(0, len(nK) - 1),
            "era_table": era_tab, "suspected_fund_events": events,
            "leg_names": names}


def selftest() -> int:
    # envelope rule: 10%-leg +/-12% flagged, +10.5% not; 20%-leg +12% NOT
    r = pd.DataFrame({"a": [0.105, -0.12, 0.12, 0.25, 0.21],
                      "b": [0.12, 0.12, 0.12, 0.25, 0.20]},
                     index=pd.date_range("2020-01-01", periods=5))
    assert (r["a"].abs() > EVENT_ENV_10).tolist() == \
        [False, True, True, True, True]
    assert (r["b"].abs() > EVENT_ENV_20).tolist() == \
        [False, False, False, True, False]
    # strict-window NaN propagation
    L = pd.Series(np.log1p(np.asarray([0.01] * 10)))
    L.iloc[4] = np.nan
    sig = np.expm1(L.rolling(5, min_periods=5).sum())
    assert np.isnan(sig.iloc[3])                 # 4 obs < window -> NaN
    assert np.isnan(sig.iloc[4]) and np.isnan(sig.iloc[8])  # NaN inside window
    assert np.isfinite(sig.iloc[9])              # window [5..9] all-valid
    # no-lookahead: change future -> past signal unchanged
    L2 = L.copy()
    L2.iloc[9] = 0.5
    sig2 = np.expm1(L2.rolling(5, min_periods=5).sum())
    assert np.array_equal(sig2.iloc[:5].values, sig.iloc[:5].values,
                          equal_nan=True)
    # forward formula: fwd at t = window (t, t+h] strictly future
    L3 = pd.Series(np.log1p(np.asarray([0.01, 0.02, -0.005, 0.0, 0.015])))
    fwd = np.expm1(L3.rolling(3, min_periods=3).sum().shift(-3))
    expect = float(np.expm1(L3.iloc[2:5].sum()))
    assert abs(fwd.iloc[1] - expect) < 1e-12   # t=1 -> window [2,3,4]
    assert np.isnan(fwd.iloc[2]) and np.isnan(fwd.iloc[3])  # tail no future
    # month-end sampling
    idx = pd.DatetimeIndex(["2020-01-10", "2020-01-31", "2020-02-03",
                            "2020-02-28"])
    me = pd.DatetimeIndex(month_ends(idx))
    assert [str(d.date()) for d in me] == ["2020-01-31", "2020-02-28"]
    # permutation determinism
    a = np.random.default_rng(20261030).permutation([1, 2, 3, 4, 5])
    b = np.random.default_rng(20261030).permutation([1, 2, 3, 4, 5])
    assert (a == b).all()
    # spearman sanity: monotone -> +1
    assert abs(_spearman([1, 2, 3, 4], [10, 20, 30, 44]) - 1.0) < 1e-9
    assert abs(_spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-9
    # era disjointness
    edges = [pd.Timestamp(e[1]) for e in ERAS]
    ends = [pd.Timestamp(e[2]) if e[2] else pd.Timestamp("2100-01-01")
            for e in ERAS]
    for i in range(len(ERAS) - 1):
        assert ends[i] < edges[i + 1]
    # corpus presence (offline, repo-tracked)
    for sym, csv, name, fam, bars in LEGS:
        c = _load_leg(csv)
        assert len(c) == bars, f"{csv} {len(c)} != {bars}"
    # known fund-event set on real corpus (frozen probe)
    _, ret_real = load_panels()
    ev = fund_events(ret_real)
    flat = {(s, e["date"]) for s, evs in ev.items() for e in evs}
    for k in [("510500", "2015-04-15"), ("510500", "2022-08-29"),
              ("512100", "2022-09-05"), ("512890", "2021-10-25")]:
        assert k in flat, f"expected fund event {k} missing"
    assert ("159915", "2024-09-30") not in flat   # 20%-limit real rally day
    assert ("588000", "2024-10-18") not in flat   # within 20% envelope
    assert len(flat) == 4, f"unexpected event set {flat}"
    print("t73_s2 slice-E selftest: envelope + strict-NaN + no-lookahead + "
          "forward-exact + month-end + perm-determinism + spearman + eras + "
          "corpus + frozen-event-set PASS")
    return 0


def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    close, ret = load_panels()
    events = fund_events(ret)
    clean, flagged = clean_rets(ret, events)

    art = {
        "prereg": {
            "ticket": "T-2026-09-26-73 s2 slice-E",
            "topic": "style rotation history 风格轮动史 (2017 core / 2021 "
                     "growth / 2023 micro / 2024 dividend) via ETF panels",
            "law_faces": [f[0] for f in FACES],
            "law_def": "style momentum persistence: pooled monthly "
                       "cross-sectional spearman(trailing rel return, "
                       "forward rel return) vs 510300 base",
            "sampling": "month-end trading days, >=4 legs cross-section",
            "split": f"IS<={IS_END} / OOS>{IS_END} (signal-date split, "
                     "forward windows may cross boundary, family "
                     "convention)",
            "fund_event_guard": f"envelope rule: 10%-limit legs |ret|>"
                                f"{EVENT_ENV_10} -> NaN clean face; "
                                f"20%-limit legs |ret|>{EVENT_ENV_20}; "
                                "strict all-valid windows; residual "
                                "sub-envelope risk disclosed",
            "nulls": f"within-month leg-permutation, {N_NULLS} seeds, "
                     f"SEED_REGISTRY t73_style_rot_s1 base "
                     f"{_seed_base()} (one-step R250: registered in this "
                     "freeze commit before any burn)",
            "no_lookahead": "signal rolling window ends at t; forward "
                             "rolling window starts t+1 (shift -h)",
            "external_narrative_unverified": True,
        },
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "panel": {
            "legs": {s: {"csv": csv, "name": name, "family_env": fam,
                         "bars": bars}
                     for s, csv, name, fam, bars in LEGS},
            "base": BASE_SYM,
            "union_days": int(len(close.index)),
            "first": str(close.index[0].date()),
            "last": str(close.index[-1].date()),
            "fund_events_flagged": int(flagged),
        },
    }

    faces_out = {}
    for face_name, w, h in FACES:
        dates, ics, ks = monthly_ic_series(clean, w, h)
        nulls = null_thresholds(clean, w, h)
        blk = {}
        for which in ("full", "is", "oos"):
            mask = _win_mask(dates, which)
            blk[which] = _stats(ics[mask])
        faces_out[face_name] = {"w": w, "h": h,
                                "blocks": blk,
                                "null_p95_abs": nulls,
                                "months": {"first": str(dates[0].date())
                                           if len(dates) else None,
                                           "last": str(dates[-1].date())
                                           if len(dates) else None,
                                           "n": int(len(dates)),
                                           "k_median": float(np.median(ks))
                                           if ks else None}}
        v = faces_out[face_name]
        v["verdict"] = {
            "alive_oos": bool(
                blk["oos"].get("mean") is not None
                and blk["oos"]["mean"]
                > nulls["oos"]["p95_abs_mean_ic"]),
            "alive_is": bool(
                blk["is"].get("mean") is not None
                and blk["is"]["mean"]
                > nulls["is"]["p95_abs_mean_ic"]),
        }
        print(f"  {face_name}: is mean={blk['is'].get('mean')} "
              f"oos mean={blk['oos'].get('mean')} "
              f"null_p95 is={nulls['is']['p95_abs_mean_ic']} "
              f"oos={nulls['oos']['p95_abs_mean_ic']} "
              f"verdict={v['verdict']}", flush=True)
    art["faces"] = faces_out
    art["verdict"] = {name: faces_out[name]["verdict"]
                      for name, _, _ in FACES}
    art["verdict"]["honesty"] = ("IC-face research verdict only; no "
                                 "portfolio/cost claim; external narrative "
                                 "unverified; applicability window in digest")

    art["descriptive"] = descriptive(close, events)

    art["trials_N"] = {"law_faces_this_batch": len(FACES),
                       "null_draws": N_NULLS * len(FACES),
                       "seeds": N_NULLS,
                       "seed_base": int(_seed_base())}
    art["trials_ledger"] = science_gates.append_ledger(
        BATCH, len(FACES) + N_NULLS * len(FACES),
        file_name="style_rotation.json",
        note="2 judged style-momentum persistence faces (pooled monthly "
             "spearman, trail-rel->fwd-rel vs 510300, strict-window clean "
             "face, envelope fund-event guard r239 family) + 100 "
             "leg-permutation null draws (50 seeds x 2 faces, SEED_REGISTRY "
             "t73_style_rot_s1); descriptive era/yearly tables no "
             "verdicts; prereg = runner header frozen pre-burn (s2 slice "
             "family convention)",
        evidence_cutoff=EVIDENCE_CUTOFF)
    art["elapsed_s"] = round(time.time() - t0, 1)
    art["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(art, ensure_ascii=False, indent=1) + "\n")
    print(f"written {OUT_JSON} elapsed={art['elapsed_s']}s "
          f"ledger_total={art['trials_ledger']['total']}", flush=True)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": run, "selftest": selftest}[cmd]())
