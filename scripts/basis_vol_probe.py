"""BASIS_VOL_PROBE -- does the index-futures basis carry volatility
information the index's own volatility history does not?

P3 exploration (self-drive v2.0, 2026-10-20 bm-a r1091). DESCRIPTIVE ONLY:
no prereg, no judged cells, no verdict line, no pool entry, no admission.

Why this question (and why it is not r1090 repeated)
----------------------------------------------------
r1090 (index_basis_probe.py) asked whether basis predicts the following
5d/20d RETURN; the answer was no (|IC| <= 0.13 everywhere, yearly sign
flips, non-monotone deciles). A null on direction does not settle the
volatility channel: hedging demand shows up as basis pressure, and the
practical consumer here is the regime gate (REGIME-5 / market_clock),
which is a volatility-state classifier, not a return forecaster.

The decisive control is VOL PERSISTENCE. Realized vol is strongly
autocorrelated, so "basis correlates with future vol" is only interesting
if it survives after the index's own trailing vol is in the regression.
Every number below is therefore reported as an INCREMENT over a
trailing-vol baseline (rank-OLS), never as a raw correlation alone.

Definitions (frozen here, single source)
    r(t)        = log(spot(t)) - log(spot(t-1))
    pv20(t)     = stdev of r over [t-19 .. t]        (baseline, uses t)
    rv20(t)     = stdev of r over [t+1 .. t+20]      (target, strictly
                  forward -- nothing after t is used by any feature)
    basis_norm  = lr - mean252(lr), min_periods=120
    chg5        = lr(t) - lr(t-5)
    z20         = (lr - mean20(lr)) / std20(lr), min_periods=20
    lr          = log(fut_close) - log(spot_close)   (scale-free)

Tests
    1. spearman(feature, rv20) over the full sample.
    2. rank-OLS: rank(rv20) ~ rank(pv20) + rank(feature).
       Reported: R2 of the baseline alone, R2 with the feature, the
       delta, and the feature coefficient t-statistic.
    3. the same delta-R2 re-estimated inside each trailing-vol quintile
       (a monotone confound would show as delta ~ 0 everywhere).
    4. per-year delta-R2, so a single-era artefact is visible.

Honest boundaries
    - main-continuous roll jumps contaminate the basis level; change and
      z faces are reported alongside the level face.
    - ETF tracking error and premium/discount sit inside every basis.
    - rv20 needs 20 future bars, so the tail is excluded (honest, not
      imputed); evidence_cutoff is the last bar with a target.
    - descriptive only: no verdict, no judged cells, no pool entry.

Usage: python scripts/basis_vol_probe.py {run,selftest}
Exit codes: 0 ok, 2 mechanism fault (missing/corrupt panel).
"""

import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "basis_vol_probe.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index_basis_probe import (  # single source, zero restatement
    PAIRS, FUT_DIR, SPOT_DIR, _pct_rank, _quantile_bins, _read_csv, _spearman,
)

MIN_N = 120          # aligned bars below this -> insufficient, not judged
RV_WIN = 20          # forward realized-vol window
PV_WIN = 20          # trailing baseline window
FEATURES = ("basis", "chg5", "z20")
QUINTILES = 5


# ---------------------------------------------------------------- statistics
def _ranks(v):
    n = len(v)
    order = sorted(range(n), key=lambda i: v[i])
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def _rank_ols(y, x_cols):
    """OLS of rank(y) on rank(x_cols) + intercept. Returns dict with coefs,
    R2, and t-stats. None when n < len(x_cols)+3 or a column is degenerate."""
    n = len(y)
    k = len(x_cols)
    if n < k + 3:
        return None
    Y = _ranks(y)
    X = [_ranks(c) for c in x_cols]
    for c in X:
        if max(c) == min(c):
            return None
    # design matrix with intercept
    rows = [[1.0] + [X[j][i] for j in range(k)] for i in range(n)]
    # normal equations solved by Gauss-Jordan on [X'X | I | X'y]
    m = k + 1
    A = [[sum(rows[i][a] * rows[i][b] for i in range(n)) for b in range(m)]
         + [1.0 if a == b else 0.0 for b in range(m)]
         + [sum(rows[i][a] * Y[i] for i in range(n))] for a in range(m)]
    for col in range(m):
        piv = max(range(col, m), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            return None
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        for b in range(col, 2 * m + 1):
            A[col][b] /= pv
        for r in range(m):
            if r == col:
                continue
            f = A[r][col]
            if f == 0.0:
                continue
            for b in range(col, 2 * m + 1):
                A[r][b] -= f * A[col][b]
    beta = [A[i][2 * m] for i in range(m)]
    inv_diag = [A[j][m + j] for j in range(m)]
    fitted = [sum(rows[i][j] * beta[j] for j in range(m)) for i in range(n)]
    my = sum(Y) / n
    sst = sum((v - my) ** 2 for v in Y)
    sse = sum((Y[i] - fitted[i]) ** 2 for i in range(n))
    r2 = None if sst == 0 else 1.0 - sse / sst
    dof = n - m
    if dof <= 0:
        return {"beta": beta, "r2": r2, "t": [None] * m}
    sigma2 = sse / dof
    tstats = []
    for j in range(m):
        var = sigma2 * inv_diag[j]
        tstats.append(None if var <= 0 else beta[j] / math.sqrt(var))
    return {"beta": beta, "r2": r2, "t": tstats}


# ---------------------------------------------------------------- series
def _build(fut_rows, spot_rows):
    """Aligned series with features, forward realized vol and baseline."""
    fm = {d: c for d, c in fut_rows}
    sm = {d: c for d, c in spot_rows}
    dates = sorted(set(fm) & set(sm))
    if len(dates) < MIN_N:
        return None
    lr, r = [], []
    for i, d in enumerate(dates):
        if fm[d] <= 0 or sm[d] <= 0:
            lr.append(None)
        else:
            lr.append(math.log(fm[d]) - math.log(sm[d]))
        if i == 0 or sm[d] <= 0 or sm[dates[i - 1]] <= 0:
            r.append(None)
        else:
            r.append(math.log(sm[d]) - math.log(sm[dates[i - 1]]))
    basis, chg5, z20 = [], [], []
    for i in range(len(dates)):
        win = [v for v in lr[max(0, i - 251):i + 1] if v is not None]
        basis.append(None if lr[i] is None or len(win) < 120
                     else lr[i] - statistics.fmean(win))
        if i < 5 or lr[i] is None or lr[i - 5] is None:
            chg5.append(None)
        else:
            chg5.append(lr[i] - lr[i - 5])
        w20 = [v for v in lr[max(0, i - 19):i + 1] if v is not None]
        if lr[i] is None or len(w20) < 20:
            z20.append(None)
        else:
            mu = statistics.fmean(w20)
            sd = statistics.pstdev(w20)
            z20.append(None if sd == 0 else (lr[i] - mu) / sd)
    pv, rv = [], []
    for i in range(len(dates)):
        past = [v for v in r[max(0, i - PV_WIN + 1):i + 1] if v is not None]
        pv.append(statistics.pstdev(past) if len(past) >= PV_WIN else None)
        # strictly forward: bars t+1 .. t+RV_WIN
        nxt = [v for v in r[i + 1:i + RV_WIN + 1] if v is not None]
        rv.append(statistics.pstdev(nxt)
                  if len(nxt) == RV_WIN and i + RV_WIN < len(dates) else None)
    return {"dates": dates, "basis": basis, "chg5": chg5, "z20": z20,
            "pv20": pv, "rv20": rv}


def _pairs_ok(ser, feat, extra_filter=None):
    xs, ys, base = [], [], []
    for i, f in enumerate(ser[feat]):
        v, rv, pv = f, ser["rv20"][i], ser["pv20"][i]
        if v is None or rv is None or pv is None:
            continue
        if extra_filter is not None and not extra_filter(i):
            continue
        xs.append(v)
        ys.append(rv)
        base.append(pv)
    return xs, ys, base


def _test(ser, feat):
    xs, ys, base = _pairs_ok(ser, feat)
    n = len(xs)
    if n < MIN_N:
        return {"feature": feat, "status": "insufficient", "n": n}
    rho = _spearman(xs, ys)
    ols_base = _rank_ols(ys, [base])
    ols_full = _rank_ols(ys, [base, xs])
    delta = None
    if ols_base and ols_full and ols_base["r2"] is not None \
            and ols_full["r2"] is not None:
        delta = ols_full["r2"] - ols_base["r2"]
    return {"feature": feat, "status": "ok", "n": n,
            "spearman": rho,
            "r2_base": None if not ols_base else ols_base["r2"],
            "r2_full": None if not ols_full else ols_full["r2"],
            "delta_r2": delta,
            "feature_t": None if not ols_full else ols_full["t"][-1]}


def _quintile_delta(ser, feat):
    """Re-estimate delta-R2 inside trailing-vol quintiles: a pure confound
    through vol level collapses here."""
    xs, ys, base = _pairs_ok(ser, feat)
    if len(xs) < QUINTILES * 40:
        return []
    bins = _quantile_bins(base, QUINTILES)
    out = []
    for q, members in enumerate(bins):
        yy = [ys[m] for m in members]
        bb = [base[m] for m in members]
        xx = [xs[m] for m in members]
        b0 = _rank_ols(yy, [bb])
        b1 = _rank_ols(yy, [bb, xx])
        delta = None
        if b0 and b1 and b0["r2"] is not None and b1["r2"] is not None:
            delta = b1["r2"] - b0["r2"]
        out.append({"quintile": q + 1, "n": len(members),
                    "delta_r2": delta,
                    "feature_t": None if not b1 else b1["t"][-1]})
    return out


def _yearly_delta(ser, feat):
    by_year = {}
    for i, d in enumerate(ser["dates"]):
        f, rv, pv = ser[feat][i], ser["rv20"][i], ser["pv20"][i]
        if f is None or rv is None or pv is None:
            continue
        y = d[:4]
        e = by_year.setdefault(y, ([], [], []))
        e[0].append(f)
        e[1].append(rv)
        e[2].append(pv)
    out = {}
    for y, (xx, yy, bb) in sorted(by_year.items()):
        if len(xx) < 40:
            out[y] = {"n": len(xx), "delta_r2": None}
            continue
        b0 = _rank_ols(yy, [bb])
        b1 = _rank_ols(yy, [bb, xx])
        delta = None
        if b0 and b1 and b0["r2"] is not None and b1["r2"] is not None:
            delta = b1["r2"] - b0["r2"]
        out[y] = {"n": len(xx), "delta_r2": delta}
    return out


def run():
    report = {
        "probe": "BASIS_VOL_PROBE",
        "mode": "descriptive",
        "judged": False,
        "pool_entry": False,
        "generated_by": "scripts/basis_vol_probe.py",
        "question": ("does the futures basis add volatility information "
                     "beyond the index's own trailing realized vol?"),
        "frozen_definitions": {
            "lr": "log(fut_close)-log(spot_close) (scale-free)",
            "basis": "lr - mean252(lr), min_periods=120",
            "chg5": "lr(t)-lr(t-5)",
            "z20": "(lr-mean20)/std20(lr), min_periods=20, inclusive",
            "pv20": "stdev of spot log-return over [t-19..t]",
            "rv20": "stdev of spot log-return over strictly [t+1..t+20]",
            "ols": "rank-OLS: rank(rv20) ~ rank(pv20) + rank(feature)",
        },
        "honest_boundaries": [
            "main-continuous roll jumps move the futures level; change/z faces reported alongside",
            "ETF tracking error / premium-discount sits inside every basis number",
            "rv20 needs 20 future bars: the tail is excluded, never imputed",
            "rank-OLS delta-R2 is an in-sample descriptive increment, not an OOS claim",
            "descriptive only: no verdict, no judged cells, no pool entry",
        ],
        "pairs": {},
    }
    cutoffs, faults = [], []
    for fut_sym, spot_sym, label in PAIRS:
        fut_rows, e1 = _read_csv(os.path.join(FUT_DIR, fut_sym + ".csv"))
        spot_rows, e2 = _read_csv(os.path.join(SPOT_DIR, spot_sym + ".csv"))
        if e1 or e2:
            faults.append({"pair": "%s/%s" % (fut_sym, spot_sym),
                           "fault": e1 or e2})
            continue
        ser = _build(fut_rows, spot_rows)
        key = "%s/%s" % (fut_sym, spot_sym)
        if ser is None:
            report["pairs"][key] = {"label": label,
                                    "status": "insufficient_sample"}
            continue
        valid = [i for i, v in enumerate(ser["rv20"]) if v is not None]
        if not valid:
            report["pairs"][key] = {"label": label, "status": "no_target"}
            continue
        last = valid[-1]
        cutoffs.append(ser["dates"][last])
        report["pairs"][key] = {
            "label": label, "fut": fut_sym, "spot": spot_sym,
            "status": "ok",
            "overlap_bars": len(ser["dates"]),
            "first_date": ser["dates"][0],
            "last_target_date": ser["dates"][last],
            "n_targets": len(valid),
            "tests": [_test(ser, f) for f in FEATURES],
            "quintile_delta_basis": _quintile_delta(ser, "basis"),
            "yearly_delta_basis": _yearly_delta(ser, "basis"),
            "current": {
                "basis": ser["basis"][-1],
                "basis_pct_3y": _pct_rank(
                    [v for v in ser["basis"][-750:] if v is not None],
                    ser["basis"][-1]) if ser["basis"][-1] is not None else None,
                "pv20": ser["pv20"][-1],
            },
        }
    if faults:
        report["faults"] = faults
    report["evidence_cutoff"] = max(cutoffs) if cutoffs else None
    report["cutoff_meta"] = {
        "rule": "max over pairs of last bar with a complete 20-bar forward target",
        "per_pair_last_dates": {k: v.get("last_target_date") for k, v in
                                report["pairs"].items()},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    ok_n = sum(1 for v in report["pairs"].values() if v.get("status") == "ok")
    print("basis_vol_probe: %d pairs ok / %d faults -> %s (cutoff %s)"
          % (ok_n, len(faults), OUT, report["evidence_cutoff"]))
    for k, v in report["pairs"].items():
        if v.get("status") != "ok":
            print("  %-12s %s" % (k, v.get("status")))
            continue
        bits = []
        for t in v["tests"]:
            if t.get("status") != "ok":
                bits.append("%s=n/a" % t["feature"])
                continue
            bits.append("%s dR2=%s t=%s" % (
                t["feature"], _fmt(t["delta_r2"]), _fmt(t["feature_t"], 2)))
        print("  %-12s n=%d %s" % (k, v["n_targets"], "  ".join(bits)))
    return 0 if not faults else 2


def _fmt(x, nd=4):
    return "n/a" if x is None else ("%+." + str(nd) + "f") % x


# ---------------------------------------------------------------- selftest
def selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    # 1) ranks: ties averaged, order preserved
    check("ranks ties averaged", _ranks([5, 5, 1]) == [2.5, 2.5, 1.0])
    check("ranks strictly increasing", _ranks([1, 2, 3]) == [1.0, 2.0, 3.0])
    # 2) OLS recovers a known linear relation and R2=1
    y = [1.0 + 2.0 * i for i in range(20)]
    x = [float(i) for i in range(20)]
    r = _rank_ols(y, [x])
    check("ols R2 == 1 on exact linear", abs(r["r2"] - 1.0) < 1e-9)
    check("ols slope sign positive", r["beta"][-1] > 0)
    check("ols exact fit t is degenerate (None) or enormous",
          r["t"][-1] is None or abs(r["t"][-1]) > 1e3)
    # 2b) t-stat sanity: strong signal -> |t| large, pure noise -> |t| small
    import random as _rnd
    _rnd.seed(11)
    n = 200
    xs_sig = [float(i) for i in range(n)]
    ys_sig = [2.0 * xs_sig[i] + _rnd.gauss(0, 1.0) for i in range(n)]
    rs = _rank_ols(ys_sig, [xs_sig])
    check("ols strong signal |t| > 5", rs["t"][-1] is not None
          and abs(rs["t"][-1]) > 5)
    ys_noise = [_rnd.gauss(0, 1.0) for _ in range(n)]
    rn = _rank_ols(ys_noise, [xs_sig])
    check("ols pure noise |t| < 3", rn["t"][-1] is not None
          and abs(rn["t"][-1]) < 3)
    # 3) mean-only regressor adds nothing (degenerate column -> None)
    check("ols degenerate column -> None",
          _rank_ols(y, [[3.0] * 20]) is None)
    # 4) short sample guard
    check("ols short sample -> None", _rank_ols([1.0, 2.0], [[1.0, 2.0]]) is None)
    # 5) forward vol must not read the future beyond t+RV_WIN and must be
    #    strictly forward: craft returns where bar t+1..t+20 are constant 1%
    dates = ["2020-01-%03d" % (i + 1) for i in range(200)]
    fut = [(d, 100.0) for d in dates]
    spot = []
    px = 100.0
    for i, d in enumerate(dates):
        if i == 0:
            spot.append((d, px))
            continue
        px *= math.exp(0.01 if 140 <= i < 160 else 0.0)
        spot.append((d, px))
    ser = _build(fut, spot)
    check("series builds", ser is not None)
    check("rv20 zero before the burst", ser["rv20"][5] == 0.0)
    check("rv20 at bar 130 sees bars 131..150 (includes burst)",
          ser["rv20"][130] is not None and ser["rv20"][130] > 0)
    check("rv20 at bar 100 sees only quiet bars 101..120",
          ser["rv20"][100] == 0.0)
    check("rv20 tail is None (no imputation)",
          ser["rv20"][-1] is None)
    check("pv20 at bar 25 has a full quiet window (==0.0)",
          ser["pv20"][25] == 0.0)
    check("pv20 before a full window is None (no imputation)",
          ser["pv20"][5] is None)
    # 6) quintile delta runs and returns the right number of buckets
    fake = {"dates": ["2021-%02d-01" % (m % 12 + 1) for m in range(400)],
            "basis": [((i * 37) % 101) / 100.0 - 0.5 for i in range(400)],
            "chg5": [0.0] * 400, "z20": [0.0] * 400,
            "pv20": [abs(math.sin(i / 7.0)) + 0.01 for i in range(400)],
            "rv20": [0.01 + 0.0001 * (i % 30) for i in range(400)]}
    q = _quintile_delta(fake, "basis")
    check("quintiles cover all bars", sum(b["n"] for b in q) == 400)
    check("quintile count", len(q) == QUINTILES)
    # 7) yearly delta keys by calendar year
    yd = _yearly_delta({"dates": ["2021-01-01"] * 60 + ["2022-01-01"] * 60,
                        "basis": [i * 0.001 for i in range(120)],
                        "chg5": [0.0] * 120, "z20": [0.0] * 120,
                        "pv20": [0.01] * 120,
                        "rv20": [0.01 + i * 0.0001 for i in range(120)]},
                       "basis")
    check("yearly keys", set(yd) == {"2021", "2022"})
    npass = sum(1 for _, c in ok if c)
    for name, c in ok:
        print(("  PASS " if c else "  FAIL ") + name)
    print("selftest: %d/%d PASS" % (npass, len(ok)))
    return 0 if npass == len(ok) else 1


def main(argv):
    if len(argv) < 2 or argv[1] not in ("run", "selftest"):
        print("usage: basis_vol_probe.py {run,selftest}")
        return 2
    return run() if argv[1] == "run" else selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv))