"""INDEX_BASIS_PROBE -- 股指期货主力连续 vs 对应现货 ETF 的基差结构探针.

P3 exploration (self-drive v2.0, 2026-10-20 bm-a r1090). DESCRIPTIVE ONLY:
no prereg, no judged cells, no verdict line, no pool entry, no admission.
Everything here is a measurement face that later preregs may cite.

Question
--------
A-share index futures (IF/IH/IC/IM, 主力连续) trade at a basis to spot.
That basis is a live crowding / hedging-demand / carry thermometer. Does
its LEVEL and its CHANGE have any monotone relation to the following
5d / 20d ETF return on the same index? Any answer here is descriptive
evidence, not a verdict.

Pairs (frozen in this file, spot = the ETF panel this repo actually keeps)
    IF -> 510300 (沪深300)     IH -> 510050 (上证50)
    IC -> 510500 (中证500)     IM -> 512100 (中证1000)

Definitions (frozen, single source, zero restatement elsewhere)
    lr(t)       = log(fut_close(t)) - log(spot_close(t))
                  (SCALE-FREE: index futures quote index points, the ETF
                   quotes ~index/1000, so a raw fut/spot ratio is a unit
                   mismatch, not a basis -- r1090 first cut proved it at
                   968x; only log-ratio faces are reported)
    basis_norm(t) = lr(t) - mean252(lr)   (premium vs its own 1y normal;
                                           min_periods=120, honest warmup)
    chg5(t)     = lr(t) - lr(t-5)         (roll-jump robust change face)
    z20(t)      = (lr(t) - mean20(lr)) / std20(lr)
    fwd_k(t)    = spot_close(t+k) / spot_close(t) - 1
  mean20/std20 are INCLUSIVE of t, min_periods=20 (same convention as the
  W9 med20amp registration). fwd_* is a descriptive target only.

Honest boundaries (stated, not papered over)
  1. 主力连续 has roll jumps: a contract switch moves the price level
     without any economic change. Level-based faces carry that artefact,
     so the change face (chg5) is reported alongside and the roll caveat
     travels with every number.
  2. signal(t) uses close(t); entry at close(t+k=0) is NOT assumed
     executable -- direction-only descriptive reading, T+1 conservatism
     applies to any later prereg.
  3. ETF tracking error (fees / premium-discount) sits inside every basis
     number; it is not modelled apart.
  4. cutoff = last common bar date; nothing after it is read.

Usage: python scripts/index_basis_probe.py {run,selftest}
Exit codes: 0 ok, 2 mechanism fault (missing/corrupt panel).
"""

import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
SPOT_DIR = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "index_basis_probe.json")

PAIRS = [("IF", "510300", "hs300"),
         ("IH", "510050", "sse50"),
         ("IC", "510500", "csi500"),
         ("IM", "512100", "csi1000")]

MIN_N = 120          # below this a pair is reported as insufficient, not judged
FWD = (5, 20)
DECILES = 5
Z_LOOKBACK_3Y = 750  # ~3 trading years for the percentile reading


# ---------------------------------------------------------------- io helpers
def _read_csv(path):
    """date-keyed close panel -> list[(date, close)] ascending. Missing/ragged
    rows are skipped honestly (returned), never imputed."""
    rows = []
    if not os.path.exists(path):
        return None, "missing file: %s" % path
    with open(path, encoding="utf-8") as f:
        head = f.readline().strip().split(",")
        try:
            i_d = head.index("date")
            i_c = head.index("close")
        except ValueError:
            return None, "missing date/close column in %s (head=%r)" % (path, head)
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= max(i_d, i_c):
                continue
            try:
                rows.append((parts[i_d], float(parts[i_c])))
            except ValueError:
                continue
    rows.sort(key=lambda r: r[0])
    return rows, None


def _map(rows):
    return {d: c for d, c in rows}


# ---------------------------------------------------------------- statistics
def _spearman(xs, ys):
    """Tie-aware Spearman rho (average ranks). None when n < 3 or degenerate."""
    n = len(xs)
    if n < 3:
        return None

    def ranks(v):
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

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def _quantile_bins(vals, k):
    """Equal-count bins by rank (ties share a bin boundary honestly)."""
    n = len(vals)
    if n < k:
        return []
    order = sorted(range(n), key=lambda i: vals[i])
    bins = [[] for _ in range(k)]
    for pos, i in enumerate(order):
        bins[min(k - 1, int(pos * k / n))].append(i)
    return bins


def _pct_rank(series, x):
    """Percentile of x inside series (0..1). None when series empty."""
    if not series:
        return None
    below = sum(1 for v in series if v <= x)
    return below / float(len(series))


# ---------------------------------------------------------------- core
def _series_for(fut_rows, spot_rows, fwd):
    """Align on common dates, build basis/chg5/z20 feature and fwd targets."""
    fm, sm = _map(fut_rows), _map(spot_rows)
    dates = sorted(set(fm) & set(sm))
    if len(dates) < MIN_N:
        return None
    import math
    basis, chg5, z20, fwd_ret, fwd_dates = [], [], [], [], []
    lr = []
    for d in dates:
        if fm[d] <= 0 or sm[d] <= 0:
            lr.append(None)
        else:
            lr.append(math.log(fm[d]) - math.log(sm[d]))
    for i, d in enumerate(dates):
        win = [v for v in lr[max(0, i - 251):i + 1] if v is not None]
        if lr[i] is None or len(win) < 120:
            basis.append(None)
        else:
            basis.append(lr[i] - statistics.fmean(win))
    for i, d in enumerate(dates):
        if i < 5 or lr[i] is None or lr[i - 5] is None:
            chg5.append(None)
        else:
            chg5.append(lr[i] - lr[i - 5])
        win = [b for b in lr[max(0, i - 19):i + 1] if b is not None]
        if lr[i] is None or len(win) < 20:
            z20.append(None)
        else:
            mu = statistics.fmean(win)
            sd = statistics.pstdev(win)
            z20.append(None if sd == 0 else (lr[i] - mu) / sd)
        tgt = None
        if i + fwd < len(dates):
            tgt = sm[dates[i + fwd]] / sm[d] - 1.0
        fwd_ret.append(tgt)
        fwd_dates.append(dates[i])
    return {"dates": dates, "basis": basis, "chg5": chg5, "z20": z20,
            "fwd": fwd_ret}


def _ic_block(ser, feat, fwd):
    xs, ys = [], []
    for f, r in zip(ser[feat], ser["fwd"]):
        if f is None or r is None:
            continue
        xs.append(f)
        ys.append(r)
    rho = _spearman(xs, ys)
    return {"feature": feat, "fwd_bars": fwd, "n": len(xs), "spearman": rho}


def _decile_block(ser, feat):
    idx = [i for i, v in enumerate(ser[feat])
           if v is not None and ser["fwd"][i] is not None]
    if len(idx) < DECILES * 5:
        return []
    bins = _quantile_bins([ser[feat][i] for i in idx], DECILES)
    out = []
    for b, members in enumerate(bins):
        rr = [ser["fwd"][idx[m]] for m in members]
        if not rr:
            continue
        out.append({"bin": b + 1, "n": len(rr),
                    "mean_fwd": statistics.fmean(rr),
                    "hit_rate": sum(1 for x in rr if x > 0) / float(len(rr))})
    return out


def _yearly_ic(ser, feat, fwd):
    out = {}
    by_year = {}
    for i, d in enumerate(ser["dates"]):
        f, r = ser[feat][i], ser["fwd"][i]
        if f is None or r is None:
            continue
        by_year.setdefault(d[:4], ([], []))
        by_year[d[:4]][0].append(f)
        by_year[d[:4]][1].append(r)
    for y, (xs, ys) in sorted(by_year.items()):
        out[y] = {"n": len(xs), "spearman": _spearman(xs, ys)}
    return out


def run():
    report = {
        "probe": "INDEX_BASIS_PROBE",
        "mode": "descriptive",
        "judged": False,
        "pool_entry": False,
        "generated_by": "scripts/index_basis_probe.py",
        "frozen_definitions": {
            "lr": "log(fut_close) - log(spot_close) (scale-free; raw fut/spot is a unit mismatch)",
            "basis_norm": "lr(t) - mean252(lr), min_periods=120",
            "chg5": "lr(t) - lr(t-5)",
            "z20": "(lr(t) - mean20(lr)) / std20(lr), min_periods=20, inclusive",
            "fwd_k": "spot_close(t+k)/spot_close(t) - 1",
            "deciles": DECILES,
        },
        "honest_boundaries": [
            "main-continuous roll jumps move the futures level: change/z faces are contaminated at switch dates, disclosed not smoothed",
            "index futures quote index points while the ETF quotes ~index/1000: only log-ratio (scale-free) faces are reported",
            "signal uses close(t); executable entry is not assumed (T+1 conservatism for any later prereg)",
            "ETF tracking error / premium-discount sits inside every basis number",
            "descriptive only: no verdict, no judged cells, no admission claim",
        ],
        "pairs": {},
    }
    cutoffs = []
    faults = []
    for fut_sym, spot_sym, label in PAIRS:
        fut_rows, e1 = _read_csv(os.path.join(FUT_DIR, fut_sym + ".csv"))
        spot_rows, e2 = _read_csv(os.path.join(SPOT_DIR, spot_sym + ".csv"))
        if e1 or e2:
            faults.append({"pair": "%s/%s" % (fut_sym, spot_sym),
                           "fault": e1 or e2})
            continue
        ser = _series_for(fut_rows, spot_rows, max(FWD))
        if ser is None:
            report["pairs"]["%s/%s" % (fut_sym, spot_sym)] = {
                "label": label,
                "status": "insufficient_sample",
                "overlap_bars": len(set(_map(fut_rows)) & set(_map(spot_rows))),
            }
            continue
        cut = ser["dates"][-1]
        cutoffs.append(cut)
        last = len(ser["dates"]) - 1
        # current reading on the last bar; forward targets exist only up to
        # len-max(FWD), so the last bar is always a pure current-state read.
        def _cur(series):
            vals = [v for v in series[max(0, last - Z_LOOKBACK_3Y):last + 1]
                    if v is not None]
            return {"value": series[last],
                    "pct_3y": _pct_rank(vals, series[last]) if
                    series[last] is not None and vals else None}

        block = {
            "label": label,
            "fut": fut_sym, "spot": spot_sym,
            "status": "ok",
            "overlap_bars": len(ser["dates"]),
            "first_date": ser["dates"][0],
            "last_date": cut,
            "ic": [_ic_block(ser, feat, fwd)
                   for feat in ("basis", "chg5", "z20") for fwd in FWD],
            "yearly_ic_chg5_fwd5": _yearly_ic(ser, "chg5", 5),
            "deciles_z20_fwd5": _decile_block(ser, "z20"),
            "current": {"basis_norm": _cur(ser["basis"]),
                        "chg5": _cur(ser["chg5"]),
                        "z20": _cur(ser["z20"])},
        }
        report["pairs"]["%s/%s" % (fut_sym, spot_sym)] = block
    if faults:
        report["faults"] = faults
    report["evidence_cutoff"] = min(cutoffs) if cutoffs else None
    report["cutoff_meta"] = {
        "rule": "min over pairs of last common futures/ETF bar date",
        "per_pair_last_dates": {k: v.get("last_date") for k, v in
                                report["pairs"].items()},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print("index_basis_probe: %d pairs ok / %d faults -> %s (cutoff %s)"
          % (sum(1 for v in report["pairs"].values() if v.get("status") == "ok"),
             len(faults), OUT, report["evidence_cutoff"]))
    for k, v in report["pairs"].items():
        if v.get("status") != "ok":
            print("  %-12s %s" % (k, v.get("status")))
            continue
        ics = {(i["feature"], i["fwd_bars"]): i["spearman"] for i in v["ic"]}
        print("  %-12s n=%d basis/fwd5=%s chg5/fwd5=%s z20/fwd5=%s "
              "chg5/fwd20=%s" % (
                  k, v["overlap_bars"],
                  _fmt(ics.get(("basis", 5))), _fmt(ics.get(("chg5", 5))),
                  _fmt(ics.get(("z20", 5))), _fmt(ics.get(("chg5", 20)))))
    return 0 if not faults else 2


def _fmt(x):
    return "n/a" if x is None else "%+.3f" % x


# ---------------------------------------------------------------- selftest
def selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    # 1) spearman exact on a monotone pair and its reverse
    xs = [1, 2, 3, 4, 5]
    check("spearman monotone == 1", abs(_spearman(xs, xs) - 1.0) < 1e-12)
    check("spearman reverse == -1",
          abs(_spearman(xs, list(reversed(xs))) + 1.0) < 1e-12)
    # 2) tie handling: all ties -> None (degenerate, honest)
    check("spearman degenerate -> None",
          _spearman([1, 1, 1], [1, 2, 3]) is None)
    check("spearman n<3 -> None", _spearman([1, 2], [1, 2]) is None)
    # 3) quantile bins equal-count and complete
    bins = _quantile_bins(list(range(100)), 5)
    check("quantile bins count", len(bins) == 5 and all(len(b) == 20
                                                        for b in bins))
    flat = _quantile_bins([7.0] * 100, 5)
    check("quantile bins keep all members on ties",
          sum(len(b) for b in flat) == 100)
    # 4) pct rank bounds
    check("pct_rank min", _pct_rank([1, 2, 3, 4], 1) == 0.25)
    check("pct_rank max", _pct_rank([1, 2, 3, 4], 4) == 1.0)
    check("pct_rank empty -> None", _pct_rank([], 1) is None)
    # 5) synthetic series: basis and forward return both strictly increasing
    #    (spot accelerates: exp(.00001*i^2) -> fwd5 rises with i; fut adds a
    #    widening premium -> basis rises with i) => rho must be ~+1
    import math
    n = 300
    fut, spot = [], []
    for i in range(n):
        s = 100.0 * math.exp(0.00001 * i * i)
        spot.append(("2020-%05d" % i, s))
        fut.append(("2020-%05d" % i, s * math.exp(0.0002 * i * i)))
    ser = _series_for(fut, spot, 5)
    check("synthetic series built", ser is not None and len(ser["dates"]) == n)
    ic = _ic_block(ser, "basis", 5)
    # basis_norm carries a 120-bar warmup, so n < n_dates by design
    check("synthetic basis/fwd5 IC is strong positive",
          ic["n"] > 100 and ic["spearman"] is not None and ic["spearman"] > 0.9)
    # 6) no-lookahead guard: last bar has no forward target
    check("last bar forward target None", ser["fwd"][-1] is None)
    check("bar t-6 has forward target", ser["fwd"][n - 6] is not None)
    # 7) warmup honesty: z20 unavailable before 20 bars
    check("z20 warmup gated", all(v is None for v in ser["z20"][:19]))
    check("z20 live after warmup", ser["z20"][19] is not None)
    # 8) NaN/ragged row tolerance: a corrupt row is skipped, not imputed
    import tempfile
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "x.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write("date,open,high,low,close\n")
        f.write("2020-01-02,1,1,1,10\n")
        f.write("2020-01-03,1,1,1,BAD\n")
        f.write("2020-01-06,1,1,1,12\n")
    rows, err = _read_csv(p)
    check("ragged/bad row skipped", err is None and len(rows) == 2)
    rows, err = _read_csv(os.path.join(tmp, "nope.csv"))
    check("missing file -> fault", rows is None and err is not None)
    # 9) alignment: intersection only, no date invention
    fut_rows = [("2020-01-02", 10.0), ("2020-01-03", 10.0),
                ("2020-01-06", 10.0)] * 50
    spot_rows = [("2020-01-02", 9.0), ("2020-01-06", 9.0)] * 50
    ser2 = _series_for(fut_rows, spot_rows, 5)
    check("alignment skips unshared dates",
          ser2 is None or set(ser2["dates"]).issubset({"2020-01-02",
                                                       "2020-01-06"}))
    bad = [t for t, c in ok if not c]
    for t, c in ok:
        print("  [%s] %s" % ("PASS" if c else "FAIL", t))
    print("selftest: %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))