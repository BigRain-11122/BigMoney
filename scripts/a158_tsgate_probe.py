# -*- coding: utf-8 -*-
"""A158-TSGATE-P1 -- Alpha158 factor library as per-instrument time-series
quantile gates: discriminative-power census + triage (standby supply B2,
GM feed STANDBY_POOL_SUPPLY_B2_B4.md sec.B2; prereg frozen
research/A158_TSGATE_P1_PREREG.md BEFORE this burn).

Hypothesis (falsifiable): the Alpha158 census killed the CROSS-SECTIONAL
use (157/158 |ICIR|<0.09 on the ETF/fund panel); the SAME factor library
in PER-INSTRUMENT time-series quantile-gate use (f < own rolling q10 /
f > own rolling q90) may still discriminate 20d forward returns.

Verdict discipline = gate_verify.py verbatim mirror (IS<=2016-12-31 /
OOS>=2017-01-01 | cost 0.10% RT | stride-20 thinning | PASS/PARTIAL/FAIL/
N/A line), with the pit-95/r431 STRICTER bucket law: both in/out buckets
AND the decidable mask (out = closed AND decidable; gate_verify's original
out-bucket was raw ~mask incl. warmup days -- disclosed deviation).

Triage, NOT a strategy verdict: PASS only earns gate_verify-style
independent-recheck candidacy for T-101 v4 regime-gate arms; PARTIAL is
demoted to a C1 input-feature candidate; FAIL = line closed (lawful
output, O-1820 negative handling).

Consumer plan (O-1820(3)): T-101 v4 regime-gate candidate library +
C1 input-feature list + T-74 L5 ladder. Lane-free (lane_owner=null).

Alpha158 port provenance: qlib/contrib/data/loader.py get_feature_config()
formula strings ported verbatim to pandas (kbar 9 + price 3 -- VWAP0
excluded, panel has no $vwap, census err=1 lineage -- + rolling 29 ops x
windows {5,10,20,30,60} = 157 factors). Rolling semantics min_periods=1
(qlib); Slope/Rsquare/Resi via closed-form OLS (cumsum, O(n)); IdxMax/
IdxMin via sliding_window_view argmax + exact expanding warmup; Rank via
pandas rolling.rank(pct=True) (qlib percentileofscore semantics).

Anchor gate (G-ANCHOR-ROC20, fail-closed every invocation): 510300
ROC20_q10 must reproduce r228 probe facts exactly -- decidable==3344,
open==374, first-decidable bar-idx==139 at evidence_cutoff 2026-09-22.
Affine invariance (ROC with/without -1 -> identical gate mask) is live-
verified; the anchor is the MASK counts, not factor scale.

Deterministic: rerun byte-identical on the stable segment (runtime
metadata segregated in a "runtime" block). Checkpoint = per-shard jsonl,
append-per-instrument with done-set resume (cross-kill law, r340).
Refuse-if-exists on the final artifacts (same-grammar rerun ban adapted).
__main__ guarded (Windows mp trap, alpha158_census lineage). Zero network,
zero token, local CPU only.

Exit codes: 0 = normal/no-op; 2 = fail-closed gate breach / mechanism
fault (VOID, nothing written)."""
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

try:  # repo science_gates: cutoff_meta for the C2-mandatory top-level block
    import science_gates
except Exception:  # pragma: no cover - selftest hermetic fallback
    science_gates = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "daily"
OUT_DIR = ROOT / "results" / "a158_tsgate_p1"
RESULTS_JSON = ROOT / "results" / "a158_tsgate_p1.json"
MD_PATH = ROOT / "research" / "A158_TSGATE_P1.md"

CUTOFF = "2026-09-22"          # P-5C frozen binding (prereg sec.2)
SPLIT = "2017-01-01"           # IS<=2016-12-31 / OOS>=2017-01-01
H = 20                          # forward horizon (days)
COST = 0.001                    # 0.10% round trip
MIN_BARS = 500                  # gate_verify verbatim
MIN_EV = 15                      # per inst per split gate events
STRIDE = 20                      # non-overlap thinning
GATE_WIN, GATE_MINP = 252, 120   # rolling quantile reference window
QLOW, QHIGH = 0.10, 0.90
WINDOWS = [5, 10, 20, 30, 60]
FIVE = ["510300", "510050", "510500", "512100", "588000"]
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
ANCHOR_INST = "510300"
ANCHOR_ROWS = 3483              # truncated 2012-05-28 -> 2026-09-22
ANCHOR_DECIDABLE = 3344         # r228 probe facts, verbatim
ANCHOR_OPEN = 374
ANCHOR_FIRST_IDX = 139
N_FACTORS = 157                 # 9 kbar + 3 price + 145 rolling
N_GATES = N_FACTORS * 2         # 314 (q10 low / q90 high)

PREREG = {
    "batch": "A158-TSGATE-P1",
    "type": "gate-discrimination census+triage (B2 standby supply)",
    "evidence_cutoff": CUTOFF,
    "universe": "full local ETF/fund panel data/daily/*.csv, >=500 bars at cutoff",
    "five_member_secondary": FIVE,
    "factors": "Alpha158 static library qlib-verbatim pandas port (157; VWAP0 excluded, no $vwap)",
    "gates": "per factor two sides: f<own rolling(252,min120).q10 / f>own rolling(252,min120).q90 = 314",
    "forward": "h=20, fwd=close.shift(-21)/close.shift(-1)-1 (T+1 next-close buy)",
    "split": SPLIT, "cost_rt": COST, "min_bars": MIN_BARS, "min_ev_per_split": MIN_EV,
    "thin_stride": STRIDE,
    "bucket_law": "in=open&decidable&fwd_ok; out=(~open)&decidable&fwd_ok (pit-95/r431 strict; gate_verify out-bucket was raw ~mask -- disclosed)",
    "verdict": ("PASS=OOS med diff_net>0 & pos_share>=0.55 & IS med diff_net>0; "
                "PARTIAL=OOS med diff_net>0 only; FAIL=else; N/A=OOS n_inst<30"),
    "multiple_testing": "N_gates=314, E[FP]=0.05*314=15.7 expected spurious PASS-level reads; PASS earns independent-recheck candidacy only",
    "consumer": "T-101 v4 regime-gate candidate library / C1 input-feature list / T-74 L5",
    "negative_handling": "FAIL=line closed (lawful); PARTIAL=demote to C1 input feature",
    "nature": "supply census + triage, NOT a strategy verdict, NOT registration",
    "anchor_gate": {"gate": "ROC20_q10", "inst": ANCHOR_INST, "rows": ANCHOR_ROWS,
                    "decidable": ANCHOR_DECIDABLE, "open": ANCHOR_OPEN,
                    "first_decidable_idx": ANCHOR_FIRST_IDX,
                    "provenance": "r228 bm-c MOM probe facts, same cutoff, affine-invariant mask"},
}


# ---------------------------------------------------------------- factor lib
def _ols_cumsums(y):
    """Closed-form expanding+rolling OLS ingredients for a fixed window d
    against t=1..d (qlib rolling_slope/rsquare/resi semantics).
    Returns callables cheap per d; y must be NaN-free (asserted upstream)."""
    n = y.shape[0]
    j = np.arange(1, n + 1, dtype=float)          # absolute position 1..n
    S = np.cumsum(y)                              # prefix sum of y
    P = np.cumsum(j * y)                          # prefix sum of t_abs * y
    Q = np.cumsum(y * y)                          # prefix sum of y^2
    S0 = np.concatenate(([0.0], S))
    P0 = np.concatenate(([0.0], P))
    Q0 = np.concatenate(([0.0], Q))
    return S0, P0, Q0, j


def _slope_full(y, d):
    """qlib Slope(y, d): rolling OLS slope vs t=1..d, min_periods=1."""
    n = y.shape[0]
    out = np.full(n, np.nan)
    S0, P0, Q0, j = _ols_cumsums(y)
    # warmup i<d-1: expanding window 1..i+1 (k=1 window -> undefined slope = NaN)
    with np.errstate(invalid="ignore", divide="ignore"):
        for i in range(min(d - 1, n)):
            k = i + 1
            tbar = (k + 1) / 2.0
            St = k * (k + 1) * (2 * k + 1) / 6.0
            sy, sty = S0[k], P0[k]
            out[i] = (sty - tbar * sy) / (St - tbar * (k * (k + 1) / 2.0))
    if n >= d:
        kall = np.arange(d, n + 1)                # window ends (1-based)
        Sy = S0[kall] - S0[kall - d]
        Sty = P0[kall] - P0[kall - d] - (kall - d) * Sy
        tbar = (d + 1) / 2.0
        St = d * (d + 1) * (2 * d + 1) / 6.0
        Stt = St - tbar * (d * (d + 1) / 2.0)
        out[d - 1:] = (Sty - tbar * Sy) / Stt
    return out


def _rsquare_resi_full(y, d):
    """qlib Rsquare(y,d)/Resi(y,d): rolling r^2 and last-point residual."""
    n = y.shape[0]
    rq = np.full(n, np.nan)
    rs = np.full(n, np.nan)
    S0, P0, Q0, j = _ols_cumsums(y)
    for i in range(min(d - 1, n)):
        k = i + 1
        sy, sty, qy = S0[k], P0[k], Q0[k]
        tbar = (k + 1) / 2.0
        St = k * (k + 1) / 2.0
        Stt = k * (k + 1) * (2 * k + 1) / 6.0 - tbar * St
        ybar = sy / k
        sxy = sty - tbar * sy
        syy = qy - k * ybar * ybar
        if Stt <= 0 or syy <= 0:
            continue
        b = sxy / Stt
        a = ybar - b * tbar
        rq[i] = (sxy * sxy) / (Stt * syy)
        rs[i] = y[i] - (a + b * k)
    if n >= d:
        kall = np.arange(d, n + 1)
        Sy = S0[kall] - S0[kall - d]
        Sty = P0[kall] - P0[kall - d] - (kall - d) * Sy
        Qy = Q0[kall] - Q0[kall - d]
        tbar = (d + 1) / 2.0
        St = d * (d + 1) / 2.0
        Stt = d * (d + 1) * (2 * d + 1) / 6.0 - tbar * St
        ybar = Sy / d
        sxy = Sty - tbar * Sy
        syy = Qy - d * ybar * ybar
        b = np.where(Stt > 0, sxy / np.where(Stt > 0, Stt, 1.0), np.nan)
        a = ybar - b * tbar
        with np.errstate(invalid="ignore", divide="ignore"):
            rq[d - 1:] = np.where((Stt > 0) & (syy > 0),
                                  (sxy * sxy) / (Stt * np.where(syy > 0, syy, 1.0)),
                                  np.nan)
            rs[d - 1:] = y[d - 1:] - (a + b * d)
    return rq, rs


def _idx_extreme_full(v, d, is_max):
    """qlib IdxMax/IdxMin: position (1-based) of window max/min, min_periods=1."""
    n = v.shape[0]
    out = np.full(n, np.nan)
    fn = np.argmax if is_max else np.argmin
    for i in range(min(d - 1, n)):                # expanding warmup, exact
        out[i] = fn(v[: i + 1]) + 1
    if n >= d:
        from numpy.lib.stride_tricks import sliding_window_view
        sw = sliding_window_view(v, d)
        out[d - 1:] = (np.argmax(sw, axis=1) + 1) if is_max else (np.argmin(sw, axis=1) + 1)
    return out


def alpha158_factors(df):
    """df: date-indexed frame with open/high/low/close/volume.
    Returns OrderedDict name -> pd.Series, 157 factors, qlib-verbatim."""
    o, h, l, c, v = (df[k] for k in ("open", "high", "low", "close", "volume"))
    F = {}
    hl = h - l
    hls = hl + 1e-12
    co = c - o
    up = np.maximum(o, c)
    dn = np.minimum(o, c)
    F["KMID"] = co / o
    F["KLEN"] = hl / o
    F["KMID2"] = co / hls
    F["KUP"] = (h - up) / o
    F["KUP2"] = (h - up) / hls
    F["KLOW"] = (dn - l) / o
    F["KLOW2"] = (dn - l) / hls
    F["KSFT"] = (2 * c - h - l) / o
    F["KSFT2"] = (2 * c - h - l) / hls
    F["OPEN0"] = o / c
    F["HIGH0"] = h / c
    F["LOW0"] = l / c
    cv = c.to_numpy(dtype=float)
    for d in WINDOWS:
        r = c.rolling(d, min_periods=1)
        F["ROC%d" % d] = c.shift(d) / c
        F["MA%d" % d] = r.mean() / c
        F["STD%d" % d] = r.std() / c
        sl = pd.Series(_slope_full(cv, d), index=df.index)
        rq, rs = _rsquare_resi_full(cv, d)
        F["BETA%d" % d] = sl / c
        rqs = pd.Series(rq, index=df.index)
        # qlib rsquare guard: rolling std of feature isclose(0, atol=2e-05) -> NaN
        rqs = rqs.mask(np.isclose(c.rolling(d, min_periods=1).std().to_numpy(), 0.0, atol=2e-05))
        F["RSQR%d" % d] = rqs
        F["RESI%d" % d] = pd.Series(rs, index=df.index) / c
        F["MAX%d" % d] = h.rolling(d, min_periods=1).max() / c
        F["MIN%d" % d] = l.rolling(d, min_periods=1).min() / c
        F["QTLU%d" % d] = r.quantile(0.8) / c
        F["QTLD%d" % d] = r.quantile(0.2) / c
        F["RANK%d" % d] = r.rank(pct=True)
        hh = h.rolling(d, min_periods=1).max()
        ll = l.rolling(d, min_periods=1).min()
        F["RSV%d" % d] = (c - ll) / (hh - ll + 1e-12)
        F["IMAX%d" % d] = pd.Series(_idx_extreme_full(h.to_numpy(dtype=float), d, True), index=df.index) / d
        F["IMIN%d" % d] = pd.Series(_idx_extreme_full(l.to_numpy(dtype=float), d, False), index=df.index) / d
        F["IMXD%d" % d] = (F["IMAX%d" % d] * d - F["IMIN%d" % d] * d) / d
        F["CORR%d" % d] = c.rolling(d, min_periods=1).corr(np.log(v + 1))
        F["CORD%d" % d] = (c / c.shift(1)).rolling(d, min_periods=1).corr(np.log(v / v.shift(1) + 1))
        upd = (c > c.shift(1)).astype(float)
        dnd = (c < c.shift(1)).astype(float)
        F["CNTP%d" % d] = upd.rolling(d, min_periods=1).mean()
        F["CNTN%d" % d] = dnd.rolling(d, min_periods=1).mean()
        F["CNTD%d" % d] = F["CNTP%d" % d] - F["CNTN%d" % d]
        dfc = c - c.shift(1)
        gain = dfc.clip(lower=0)
        ab = dfc.abs()
        sg = gain.rolling(d, min_periods=1).sum()
        sa = ab.rolling(d, min_periods=1).sum()
        loss = (-dfc).clip(lower=0)
        F["SUMP%d" % d] = sg / (sa + 1e-12)
        F["SUMN%d" % d] = loss.rolling(d, min_periods=1).sum() / (sa + 1e-12)
        F["SUMD%d" % d] = (sg - loss.rolling(d, min_periods=1).sum()) / (sa + 1e-12)
        F["VMA%d" % d] = v.rolling(d, min_periods=1).mean() / (v + 1e-12)
        F["VSTD%d" % d] = v.rolling(d, min_periods=1).std() / (v + 1e-12)
        wv = (c / c.shift(1) - 1).abs() * v
        F["WVMA%d" % d] = wv.rolling(d, min_periods=1).std() / (wv.rolling(d, min_periods=1).mean() + 1e-12)
        vd = v - v.shift(1)
        vg = vd.clip(lower=0)
        va = vd.abs()
        vsg = vg.rolling(d, min_periods=1).sum()
        vsa = va.rolling(d, min_periods=1).sum()
        vloss = (-vd).clip(lower=0)
        F["VSUMP%d" % d] = vsg / (vsa + 1e-12)
        F["VSUMN%d" % d] = vloss.rolling(d, min_periods=1).sum() / (vsa + 1e-12)
        F["VSUMD%d" % d] = (vsg - vloss.rolling(d, min_periods=1).sum()) / (vsa + 1e-12)
    assert len(F) == N_FACTORS, "factor table broken: %d != %d" % (len(F), N_FACTORS)
    return F


GATE_NAMES = None  # built lazily, order = factor name x (q10, q90)


def gate_universe(F):
    """[(gate_name, open_bool_series, decidable_series)] for 314 gates."""
    out = []
    for name, f in F.items():
        qlow = f.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
        dec = f.notna() & qlow.notna()
        out.append((name + "_q10", (f < qlow) & dec, dec))
        qhi = f.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QHIGH)
        dech = f.notna() & qhi.notna()
        out.append((name + "_q90", (f > qhi) & dech, dech))
    return out


# ------------------------------------------------------------------- stats
def thin(pos, stride=STRIDE):
    kept, last = [], -10 ** 9
    for p in pos:
        if p - last >= stride:
            kept.append(p)
            last = p
    return np.array(kept, dtype=int)


def inst_gate_stats(mask, dec, fwd, oos_sel):
    """Per-instrument IS/OOS stats for one gate (B2 frozen bucket law)."""
    f = fwd.to_numpy(dtype=float)
    m = mask.to_numpy()
    d = dec.to_numpy()
    ok = ~np.isnan(f)
    res = {}
    for tag, sel in (("IS", ~oos_sel), ("OOS", oos_sel)):
        base = d & ok & sel
        pin = np.flatnonzero(base & m)
        pout = np.flatnonzero(base & ~m)
        if len(pin) < MIN_EV or len(pout) < MIN_EV:
            res[tag] = None
            continue
        a, b = f[pin], f[pout]
        diff = float(a.mean() - b.mean())
        se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        tin, tout = thin(pin), thin(pout)
        dt = float(f[tin].mean() - f[tout].mean() - COST) if (len(tin) >= 5 and len(tout) >= 5) else None
        res[tag] = {"n_in": int(len(pin)), "n_out": int(len(pout)),
                    "diff": round(diff, 6), "net": round(diff - COST, 6),
                    "t": round(float(diff / se), 3) if se > 0 else 0.0,
                    "thin": round(dt, 6) if dt is not None else None}
    return res


# ------------------------------------------------------------- fail helper
def _fail(msg, code=2):
    """Fail-closed exit: print + exit code (pool contract: 2=VOID)."""
    print("[a158tsg] %s" % msg, flush=True)
    raise SystemExit(code)


# ------------------------------------------------------------- worker face
def load_truncated(path):
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return df[df.index <= pd.Timestamp(CUTOFF)]


def preflight_gates():
    """Fail-closed G-PANEL / G-CUTOFF / G-ANCHOR-ROC20 / G-FACTORS."""
    csvs = sorted(SRC.glob("*.csv"))
    if len(csvs) < 1500:
        _fail("G-PANEL FAIL: only %d csvs (<1500)" % len(csvs))
    stems = [p.stem for p in csvs]
    missing = [k for k in FIVE if not any(k in s for s in stems)]
    if missing:
        _fail("G-PANEL FAIL: five-member missing %s" % missing)
    ap = SRC / ("sh%s.csv" % ANCHOR_INST)
    adf = load_truncated(ap)
    if len(adf) != ANCHOR_ROWS:
        _fail("G-CUTOFF FAIL: 510300 truncated rows %d != %d" % (len(adf), ANCHOR_ROWS))
    for k in FIVE:
        d5 = load_truncated(SRC / ("sh%s.csv" % k))
        if str(d5.index[-1].date()) > CUTOFF:
            _fail("G-CUTOFF FAIL: %s tail beyond cutoff" % k)
    c = adf["close"]
    for form in (c / c.shift(20) - 1.0, c / c.shift(20)):   # affine invariance
        q = form.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
        dec = q.notna() & form.notna()
        op = (form < q) & dec
        fi = int(np.flatnonzero(dec.to_numpy())[0])
        if int(dec.sum()) != ANCHOR_DECIDABLE or int(op.sum()) != ANCHOR_OPEN or fi != ANCHOR_FIRST_IDX:
            _fail("G-ANCHOR-ROC20 FAIL: dec=%d open=%d first=%d"
                  % (int(dec.sum()), int(op.sum()), fi))
    F = alpha158_factors(adf)
    bad = [k for k, s in F.items() if int(s.notna().sum()) < 500]
    if bad:
        _fail("G-FACTORS FAIL: <500 valid values on anchor: %s" % bad[:8])
    # gate-order identity pin: worker gate indices == finalize name table
    flat = [nm for k in F.keys() for nm in (k + "_q10", k + "_q90")]
    if flat != gate_name_list():
        _fail("G-FACTORS FAIL: gate order drift vs name table")
    return len(csvs), len(adf)


def process_instrument(path):
    """Top-level picklable worker: full per-instrument stats row."""
    stem = pathlib.Path(path).stem
    try:
        df = load_truncated(path)
    except Exception:
        return {"inst": stem, "skip": "unreadable", "stats": []}
    if len(df) < MIN_BARS:
        return {"inst": stem, "skip": "min_bars", "stats": []}
    try:
        F = alpha158_factors(df)
        gates = gate_universe(F)
    except Exception as ex:
        return {"inst": stem, "skip": "factor_error:%s" % type(ex).__name__, "stats": []}
    c = df["close"]
    fwd = c.shift(-H - 1) / c.shift(-1) - 1
    oos_sel = np.asarray(df.index >= pd.Timestamp(SPLIT))
    five = any(k in stem for k in FIVE)
    rows = []
    for gi, (gname, mask, dec) in enumerate(gates):
        st = inst_gate_stats(mask, dec, fwd, oos_sel)
        for si, tag in ((0, "IS"), (1, "OOS")):
            r = st[tag]
            if r is None:
                continue
            rows.append([gi, si, r["n_in"], r["n_out"], r["diff"], r["t"], r["net"], r["thin"]])
    out = {"inst": stem, "five": five, "stats": rows}
    if stem.endswith(ANCHOR_INST):
        xd = {}
        idx = {str(ts.date()): i for i, ts in enumerate(df.index)}
        for day in EXTREME_DAYS:
            i = idx.get(day)
            if i is None:
                xd[day] = None
                continue
            opens = []
            for gi, (gname, mask, dec) in enumerate(gates):
                m = mask.to_numpy()
                dd = dec.to_numpy()
                opens.append(gi) if (dd[i] and m[i]) else None
            xd[day] = opens
        out["xdays"] = xd
    return out


# ---------------------------------------------------------------- run/ckpt
def shard_stems(k, n):
    csvs = sorted(SRC.glob("*.csv"))
    return [p for i, p in enumerate(csvs) if i % n == k]


def ckpt_path(k, n):
    return OUT_DIR / ("shard_%dof%d.jsonl" % (k, n))


def done_set(k, n):
    done = set()
    fp = ckpt_path(k, n)
    if fp.exists():
        for line in fp.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["inst"])
            except Exception:
                continue
    return done


def cmd_run(shard, shards, workers):
    t0 = time.time()
    ncsv, _ = preflight_gates()          # fail-closed every invocation
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fp = ckpt_path(shard, shards)
    todo = [p for p in shard_stems(shard, shards) if p.stem not in done_set(shard, shards)]
    print("[a158tsg] shard %d/%d instruments=%d todo=%d (panel=%d)"
          % (shard, shards, len(shard_stems(shard, shards)), len(todo), ncsv), flush=True)
    if todo:
        from parallel_runner import run_cells_parallel, worker_cap
        jobs = [(p.stem, process_instrument, (str(p),)) for p in todo]
        with open(fp, "a", encoding="utf-8") as fh:
            def keep(key, payload):
                fh.write(json.dumps(payload, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
                fh.flush()
            run_cells_parallel(jobs, workers=workers or worker_cap(),
                               desc="insts", on_result=keep)
    print("[a158tsg] shard done in %.0fs -> %s" % (time.time() - t0, fp), flush=True)
    return 0


def read_all_rows():
    rows = []
    xdays = None
    skipped = {}
    for fp in sorted(OUT_DIR.glob("shard_*.jsonl")):
        for line in fp.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("skip"):
                skipped[r["inst"]] = r["skip"]
                continue
            if "xdays" in r:
                xdays = r["xdays"]
            rows.append(r)
    return rows, xdays, skipped


def gate_name_list():
    """Deterministic gate ordering = factor order x sides (must match workers)."""
    names = []
    for w in WINDOWS:
        pass
    # factor order is fixed by alpha158_factors construction; rebuild cheaply
    # from the anchor file without computing rolling stats twice: names only.
    seq = (["KMID", "KLEN", "KMID2", "KUP", "KUP2", "KLOW", "KLOW2", "KSFT", "KSFT2",
            "OPEN0", "HIGH0", "LOW0"]
           + ["%s%d" % (op, d) for d in WINDOWS for op in
              ("ROC", "MA", "STD", "BETA", "RSQR", "RESI", "MAX", "MIN", "QTLU", "QTLD",
               "RANK", "RSV", "IMAX", "IMIN", "IMXD", "CORR", "CORD", "CNTP", "CNTN",
               "CNTD", "SUMP", "SUMN", "SUMD", "VMA", "VSTD", "WVMA", "VSUMP", "VSUMN",
               "VSUMD")])
    assert len(seq) == N_FACTORS
    for nm in seq:
        names.append(nm + "_q10")
        names.append(nm + "_q90")
    assert len(names) == N_GATES
    return names


def aggregate(rows, xdays, skipped, n_workers):
    names = gate_name_list()
    per = {g: {"IS": [], "OOS": []} for g in names}
    five_rows = {}
    for r in rows:
        five = bool(r.get("five"))
        for gi, si, n_in, n_out, diff, t, net, thin in r["stats"]:
            g = names[gi]
            tag = "IS" if si == 0 else "OOS"
            per[g][tag].append((net, t, thin))
            if five and tag == "OOS":
                five_rows.setdefault(g, {})[r["inst"]] = {"net": net, "n_in": n_in, "thin": thin}
    agg = {}
    for g in names:
        d = {}
        for tag in ("IS", "OOS"):
            arr = per[g][tag]
            if not arr:
                d[tag] = {"n_inst": 0, "med_net": None, "pos_share": None,
                          "med_t": None, "med_thin": None, "pct_abs_t_gt2": None}
                continue
            nets = np.array([x[0] for x in arr], dtype=float)
            ts = np.array([x[1] for x in arr], dtype=float)
            th = [x[2] for x in arr if x[2] is not None]
            d[tag] = {"n_inst": int(len(arr)),
                      "med_net": round(float(np.median(nets)), 5),
                      "pos_share": round(float((nets > 0).mean()), 4),
                      "med_t": round(float(np.median(ts)), 3),
                      "med_thin": round(float(np.median(th)), 5) if th else None,
                      "pct_abs_t_gt2": round(float((np.abs(ts) > 2).mean()), 4)}
        i_, o_ = d["IS"], d["OOS"]
        if o_["n_inst"] < 30:
            v = "N/A"
        elif o_["med_net"] > 0 and o_["pos_share"] >= 0.55 and i_["med_net"] > 0:
            v = "PASS"
        elif o_["med_net"] > 0:
            v = "PARTIAL"
        else:
            v = "FAIL"
        agg[g] = {"IS": i_, "OOS": o_, "verdict": v}
    return agg, five_rows


def write_artifacts(payload, md_lines):
    if RESULTS_JSON.exists():
        _fail("refuse-if-exists: %s already landed (rerun ban; harvest via existing artifact)" % RESULTS_JSON)
    RESULTS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    MD_PATH.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def cmd_finalize(workers_used=None):
    t0 = time.time()
    preflight_gates()                     # anchor + gates recomputed at finalize (honest claim)
    rows, xdays, skipped = read_all_rows()
    if not rows:
        _fail("finalize FAIL: no checkpoint rows")
    n_workers = workers_used or int(os.cpu_count() * 0.8)
    agg, five_rows = aggregate(rows, xdays, skipped, n_workers)
    verdicts = {g: a["verdict"] for g, a in agg.items()}
    cnt = {v: sum(1 for x in verdicts.values() if x == v) for v in ("PASS", "PARTIAL", "FAIL", "N/A")}
    names = gate_name_list()
    xd_out = {}
    if xdays:
        for day, opens in xdays.items():
            xd_out[day] = {"n_open": len(opens) if opens is not None else None,
                           "open_gates": [names[i] for i in (opens or [])][:60]}
    if science_gates is not None:
        cutoff_block = science_gates.cutoff_meta(CUTOFF)
    else:
        cutoff_block = {"evidence_cutoff": CUTOFF}
    payload = {
        **cutoff_block,
        "batch": "A158-TSGATE-P1",
        "prereg": PREREG,
        "gate_names": names,
        "results": agg,
        "verdict_counts": cnt,
        "five_member_oos": {g: five_rows[g] for g in sorted(five_rows)
                            if agg[g]["verdict"] in ("PASS", "PARTIAL", "N/A")},
        "extreme_day_open_gates_510300": xd_out,
        "audit": {"insts_with_stats": len(rows), "skipped": skipped,
                  "n_gates": N_GATES, "e_fp_expected": round(0.05 * N_GATES, 1),
                  "workers": n_workers,
                  "anchor_gate_reproduced": True},
        "runtime": {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "elapsed_sec": round(time.time() - t0, 1)},
    }
    md = build_md(payload)
    write_artifacts(payload, md)
    print("[a158tsg] finalize: PASS=%d PARTIAL=%d FAIL=%d N/A=%d -> %s"
          % (cnt["PASS"], cnt["PARTIAL"], cnt["FAIL"], cnt["N/A"], RESULTS_JSON), flush=True)
    return 0


def build_md(p):
    cnt = p["verdict_counts"]
    lines = [
        "# A158 时序分位门普查+分诊（Alpha158 157 因子×双侧=314 门·B2 备货落地）", "",
        "> 生成: %(gen)s ｜ evidence_cutoff=2026-09-22（P-5C binding·面板一律截断）｜ IS≤2016-12-31 / OOS≥2017-01-01 ｜ 成本 0.10%% 往返 ｜ 不重叠=stride-20 双组抽稀 ｜ 判线=gate_verify 逐字镜像（PASS=OOS 净差中位>0 ∧ 正份额≥0.55 ∧ IS 同号；PARTIAL=仅 OOS>0；FAIL=其余；N/A=OOS 工具<30）" % {"gen": p["runtime"]["generated"]},
        "> **桶定义（B2 冻结·严口径）**: in=open∧decidable∧fwd 有效；out=（¬open）∧decidable∧fwd 有效——pit-95/r431 decidable 掩码双桶 AND 律（严于 gate_verify 原 out 桶·如实披露）；锚门掩码计数不受桶定义影响", "",
        "## 判定汇总", "",
        "| 判定 | 门数 | 说明 |", "|---|---|---|",
        "| PASS | %d | 独立复核资格（gate_verify 式下一关）→ T-101 v4 政体门候选库 |" % cnt["PASS"],
        "| PARTIAL | %d | 降格 C1 输入特征候选清单 |" % cnt["PARTIAL"],
        "| FAIL | %d | 该因子时序门用法关线（合法产出·与截面判负互为独立假设） |" % cnt["FAIL"],
        "| N/A | %d | OOS 工具数<30（样本不足不判） |" % cnt["N/A"],
        "", "**多重检验税**: N=314 门·E[FP]=%.1f（5%% 假阳量级）——PASS 门升格 v4 候选前必过独立复核面（D6 邻接审计+独立 OOS 复核），普查面零注册效力。" % p["audit"]["e_fp_expected"],
        "",
        "## 锚门复现（G-ANCHOR-ROC20·r228 探针逐位）", "",
        "- 510300 ROC20_q10 @cutoff 2026-09-22：decidable=%d·open=%d·首可判 bar-idx=%d（预注册 §5.1 逐位复现）" % (ANCHOR_DECIDABLE, ANCHOR_OPEN, ANCHOR_FIRST_IDX),
        "",
        "## PASS 门表", "", "| 门 | IS净差中位 | OOS净差中位 | OOS正份额 | OOS不重叠 | 中位t IS→OOS | OOS工具数 |", "|---|---|---|---|---|---|---|",
    ]
    for order, tag in ((0, "PASS"), (1, "PARTIAL")):
        if tag == "PARTIAL":
            lines += ["", "## PARTIAL 门表（C1 输入特征候选）", "",
                      "| 门 | IS净差中位 | OOS净差中位 | OOS正份额 | OOS不重叠 | 中位t IS→OOS | OOS工具数 |", "|---|---|---|---|---|---|---|"]
        for g, a in sorted(p["results"].items()):
            if a["verdict"] != tag:
                continue
            i_, o_ = a["IS"], a["OOS"]
            lines.append("| %s | %+.5f | %+.5f | %.2f | %s | %s→%s | %d |" % (
                g, i_["med_net"] or 0, o_["med_net"] or 0, o_["pos_share"] or 0,
                ("%+.5f" % o_["med_thin"]) if o_["med_thin"] is not None else "N/A",
                i_["med_t"], o_["med_t"], o_["n_inst"]))
    fm = p["five_member_oos"]
    if fm:
        lines += ["", "## 五员落地性次级面（O-1531④·OOS 净差·仅判定面门）", ""]
        for g in sorted(fm):
            row = ["- %s:" % g]
            for inst, r in sorted(fm[g].items()):
                row.append(" %s %+.5f (n_in=%d)" % (inst, r["net"], r["n_in"]))
            lines.append("".join(row))
    xd = p["extreme_day_open_gates_510300"]
    if xd:
        lines += ["", "## 极端日门态披露（510300·七日开窗门数）", ""]
        for day, r in xd.items():
            lines.append("- %s: n_open=%s" % (day, r["n_open"]))
    lines += ["", "## 诚实注记", "",
              "- 本批=供应普查+分诊闸：PASS 仅获独立复核资格，非策略宣称、非注册；判负处置=FAIL 关线照报（O-1820②）",
              "- Alpha158 公式=qlib get_feature_config 逐字移植（VWAP0 剔除=面板无 $vwap·census err=1 血统）；A158 VSTD*=成交量口径≠census 价格波动门（命名撞车如实）",
              "- 工具间横截面相关未做市场中性化（同日冲击共享）→聚合读数偏乐观如实；314 门多重比较未校正（E[FP]=15.7 量级）",
              "- 前瞻收益=信号日收盘信息集·T+1 次日收盘买入·持有 20 日；成本 0.10% 往返",
              "- 消费面: T-101 v4 政体门候选库 / C1 输入特征清单 / T-74 L5（prereg §0 consumer_plan）",
              "- r433 同门换用法律随附: 择时用法面 9/10 判负在册——本批门=政体门输入特征用法，升格臂前必过择时用法廉价初筛"]
    return lines


def cmd_status():
    rows, xdays, skipped = read_all_rows()
    total = len(sorted(SRC.glob("*.csv")))
    print("[a158tsg] checkpoint insts=%d/%d skipped=%d artifacts=%s"
          % (len(rows), total, len(skipped),
             "landed" if RESULTS_JSON.exists() else "pending"))
    return 0


# ----------------------------------------------------------------- selftest
def _synth_frame(n=3000, seed=7):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.01, n)
    px = 4.0 * np.exp(np.cumsum(r))
    df = pd.DataFrame({
        "open": px * (1 + rng.normal(0, 0.002, n)),
        "high": px * (1 + np.abs(rng.normal(0, 0.004, n))),
        "low": px * (1 - np.abs(rng.normal(0, 0.004, n))),
        "close": px,
        "volume": rng.integers(1e6, 5e6, n).astype(float),
    }, index=pd.bdate_range("2012-01-02", periods=n))
    return df


def cmd_selftest():
    total = [0]
    fails = [0]

    def check(name, cond):
        total[0] += 1
        if not cond:
            fails[0] += 1
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            print("[a158tsg] selftest FAIL at %s" % name)
            sys.exit(2)

    print("[a158tsg] selftest: hermetic legs")
    # [1] factor formula anchors on hand-computable cases
    df = _synth_frame(120, seed=11)
    F = alpha158_factors(df)
    check("factor count 157", len(F) == 157)
    c, o, h, l, v = df["close"], df["open"], df["high"], df["low"], df["volume"]
    check("KMID formula", np.allclose(F["KMID"].to_numpy(), ((c - o) / o).to_numpy(), equal_nan=True))
    check("KLEN formula", np.allclose(F["KLEN"].to_numpy(), ((h - l) / o).to_numpy(), equal_nan=True))
    check("ROC20 formula", np.allclose(F["ROC20"].to_numpy(), (c.shift(20) / c).to_numpy(), equal_nan=True))
    check("MA5 formula", np.allclose(F["MA5"].to_numpy(), (c.rolling(5, min_periods=1).mean() / c).to_numpy(), equal_nan=True))
    check("STD5 ddof=1", np.allclose(F["STD5"].to_numpy(), (c.rolling(5, min_periods=1).std() / c).to_numpy(), equal_nan=True))
    check("RSV5 formula", np.allclose(
        F["RSV5"].to_numpy(),
        ((c - l.rolling(5, min_periods=1).min()) / (h.rolling(5, min_periods=1).max() - l.rolling(5, min_periods=1).min() + 1e-12)).to_numpy(),
        equal_nan=True))
    check("QTLU5 formula", np.allclose(F["QTLU5"].to_numpy(), (c.rolling(5, min_periods=1).quantile(0.8) / c).to_numpy(), equal_nan=True))
    # BETA/RSQR/RESI vs direct per-window OLS on a small slice
    y = c.to_numpy()[:60]
    d = 10
    t = np.arange(1, d + 1, dtype=float)
    b_ref = np.polyfit(t, y[-d:], 1)[0]
    check("BETA10 vs polyfit(last window)", abs(F["BETA10"].to_numpy()[59] - b_ref / y[59]) < 1e-9)
    a_ref = np.polyfit(t, y[-d:], 1)[1]
    check("RESI10 vs fit", abs(F["RESI10"].to_numpy()[59] * y[59] - (y[59] - (a_ref + b_ref * d))) < 1e-9)
    r_ref = np.corrcoef(y[-d:], t)[0, 1] ** 2
    check("RSQR10 vs corr^2", abs(F["RSQR10"].to_numpy()[59] - r_ref) < 1e-9)
    im = y[-d:].argmax() + 1
    check("IMAX10 position", abs(F["IMAX10"].to_numpy()[59] * d - im) < 1e-9)
    imx = _idx_extreme_full(h.to_numpy()[:60].astype(float), d, True)
    imn = _idx_extreme_full(l.to_numpy()[:60].astype(float), d, False)
    check("IMXD10 = (idxmax-idxmin)/d", np.allclose(
        F["IMXD10"].to_numpy()[:60] * d, (imx - imn), equal_nan=True))
    check("CNTP5 first valid", abs(float(F["CNTP5"].iloc[4]) - float(((c > c.shift(1)).astype(float)).iloc[:5].mean())) < 1e-12)
    check("RANK5 pct in [0,1]", float(F["RANK5"].dropna().min()) > 0 and float(F["RANK5"].dropna().max()) <= 1.0)
    # warmup exactness: expanding slope at i=3 vs direct OLS on prefix
    tt = np.arange(1, 4, dtype=float)
    b3 = np.polyfit(tt, y[:3], 1)[0]
    check("Slope warmup expanding (i=2)", abs(_slope_full(y, 5)[2] - b3) < 1e-9)
    check("IdxMax warmup (i=1)", _idx_extreme_full(y, 5, True)[1] == (np.argmax(y[:2]) + 1))

    # [2] gate construction: affine invariance + NaN decidable discipline
    f1 = c / c.shift(20) - 1.0
    f2 = c / c.shift(20)
    q1 = f1.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
    q2 = f2.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
    d1 = q1.notna() & f1.notna()
    d2 = q2.notna() & f2.notna()
    check("affine-invariant masks", bool(((f1 < q1) & d1).equals((f2 < q2) & d2)) and bool(d1.equals(d2)))
    g = gate_universe({"X": f1})
    check("gate universe shape 2", len(g) == 2 and g[0][0] == "X_q10" and g[1][0] == "X_q90")
    check("decidable excludes warmup", not bool(g[0][2].iloc[:GATE_MINP - 1].any()))

    # [3] stats + verdict four states on synthetic rows
    n = 400
    idx = pd.bdate_range("2010-01-01", periods=n)
    fwd = pd.Series(np.random.default_rng(3).normal(0.001, 0.02, n), index=idx)
    oos_sel = np.asarray(idx >= pd.Timestamp(SPLIT))
    mk = pd.Series(np.zeros(n, dtype=bool), index=idx)
    mk.iloc[100:180] = True  # IS-side open events
    dec = pd.Series(np.ones(n, dtype=bool), index=idx)
    dec.iloc[:GATE_MINP] = False
    st = inst_gate_stats(mk, dec, fwd, oos_sel)
    check("split buckets present", st["IS"] is not None)
    base = inst_gate_stats(mk, dec, fwd, oos_sel)["IS"]
    check("cost subtracted", abs(base["net"] - (base["diff"] - COST)) < 1e-9)
    a = np.array([0.01] * 5)
    pos = np.arange(5) * 25
    check("thin stride", list(thin(np.array([0, 5, 19, 20, 40, 60]))) == [0, 20, 40, 60])
    # verdict line via aggregate(): PASS/PARTIAL/FAIL/NA
    rows = []
    rng2 = np.random.default_rng(5)
    for i in range(35):
        rows.append({"inst": "s%02d" % i, "five": i < 5,
                     "stats": [[0, 0, 30, 30, 0.01, 2.0, 0.009, 0.008],
                               [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]]})
    agg, five = aggregate(rows, None, {}, 4)
    check("verdict PASS synthetic", agg[list(agg)[0]]["verdict"] == "PASS")
    rows2 = [dict(r, stats=[[0, 0, 30, 30, 0.01, 2.0, 0.009, 0.008],
                            [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]])
             for r in rows[:29]]  # OOS n_inst<30 -> N/A
    agg2, _ = aggregate(rows2, None, {}, 4)
    check("verdict N/A synthetic", agg2[list(agg2)[0]]["verdict"] == "N/A")
    rows3 = [dict(r, stats=[[0, 0, 30, 30, -0.01, -2.0, -0.011, -0.01],
                            [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]]) for r in rows]
    agg3, _ = aggregate(rows3, None, {}, 4)
    check("verdict PARTIAL synthetic", agg3[list(agg3)[0]]["verdict"] == "PARTIAL")
    rows4 = [dict(r, stats=[[0, 0, 30, 30, -0.01, -2.0, -0.011, -0.01],
                            [0, 1, 30, 30, -0.02, -2.5, -0.021, -0.02]]) for r in rows]
    agg4, _ = aggregate(rows4, None, {}, 4)
    check("verdict FAIL synthetic", agg4[list(agg4)[0]]["verdict"] == "FAIL")

    # [4] determinism: aggregate twice -> identical payload stable segment
    aggA, fA = aggregate(rows, None, {}, 4)
    aggB, fB = aggregate(rows, None, {}, 4)
    check("aggregate determinism", json.dumps(aggA, sort_keys=True) == json.dumps(aggB, sort_keys=True))

    # [5] real-data anchor leg (G-ANCHOR-ROC20)
    ncsv, adf_rows = preflight_gates()
    check("G-PANEL csvs>=1500", ncsv >= 1500)
    check("G-CUTOFF 510300 rows==3483", adf_rows == ANCHOR_ROWS)

    # [6] shard split covers all, no dup
    allstems = [p.stem for p in sorted(SRC.glob("*.csv"))]
    parts = [[p for i, p in enumerate(sorted(SRC.glob("*.csv"))) if i % 3 == k] for k in range(3)]
    check("shard split partition", sorted(x for part in parts for x in part) == sorted(SRC.glob("*.csv")))

    print("[a158tsg] selftest: %d/%d PASS" % (total[0] - fails[0], total[0]))
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] == "selftest":
        if args and args[0] == "selftest":
            return cmd_selftest()
        print(__doc__)
        return 0
    cmd = args[0]
    if cmd == "run":
        shard, shards, workers = 0, 1, None
        it = iter(args[1:])
        for a in it:
            if a == "--shard":
                shard = int(next(it))
            elif a == "--shards":
                shards = int(next(it))
            elif a == "--workers":
                workers = int(next(it))
        return cmd_run(shard, shards, workers)
    if cmd == "finalize":
        return cmd_finalize()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
