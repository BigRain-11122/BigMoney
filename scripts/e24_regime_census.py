"""E24 regime-conditioning census (descriptive; NO judgment, NO pre-registration).

Question: does the cross-sectional ETF state of the market (dispersion, breadth,
ladder momentum) condition the NEXT 5 trading days of the traded universe?

Everything here is computed from in-repo `data/daily/*.csv` panels only, so the
family is NOT gated on any forward accrual window (the W22 blocker).

Modes
  dispersion : cross-sectional std of trailing 5d returns (causal) -> quintile
               buckets -> forward 5d equal-weight ETF return
  breadth    : share of ETFs above their 20d MA (causal) -> quintile buckets
  ladder     : five-member traded ladder {510300,510050,510500,512100,588000}
               mean 20d momentum sign -> forward 5d ladder return

Honest notes baked into the face:
  * overlapping forward windows (5d step 1d) inflate naive t; a stride-5
    non-overlapping subsample t is reported alongside.
  * expanding (causal) quintile cutoffs with a 250-day burn-in.
  * descriptive only: no gate, no verdict, no trial count consumption.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
OUTDIR = os.path.join(ROOT, "results", "e24_regime_census")
LADDER = ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"]
H = 5
BURN = 250


def load_series(path):
    out = {}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            c = (row.get("close") or "").strip()
            if not d or not c:
                continue
            try:
                out[d] = float(c)
            except ValueError:
                continue
    return out


def load_panel(max_files=None):
    files = sorted(f for f in os.listdir(DAILY) if f.endswith(".csv"))
    if max_files:
        files = files[:max_files]
    series = {}
    for fn in files:
        s = load_series(os.path.join(DAILY, fn))
        if len(s) >= BURN + H + 10:
            series[fn[:-4]] = s
    if "sh510300" in series:
        cal = sorted(series["sh510300"])
    else:
        cal = sorted({d for s in series.values() for d in s})
    symbols = sorted(series)
    rows = []
    for d in cal:
        rows.append([series[s].get(d) for s in symbols])
    return cal, symbols, rows


def build_returns(cal, rows):
    """daily simple returns and close matrix (None for missing)."""
    closes = rows
    rets = []
    for i in range(1, len(closes)):
        r = []
        for a, b in zip(closes[i], closes[i - 1]):
            if a is None or b is None or b <= 0:
                r.append(None)
            else:
                r.append(a / b - 1.0)
        rets.append(r)
    return closes, rets


def trailing(closes, i, n):
    """per-symbol n-day trailing return ending at index i (causal)."""
    out = []
    for j in range(len(closes[i])):
        if i - n < 0:
            continue
        a, b = closes[i][j], closes[i - n][j]
        if a is None or b is None or b <= 0:
            continue
        out.append(a / b - 1.0)
    return out


def forwards(closes, i, h):
    out = []
    if i + h >= len(closes):
        return out
    for j in range(len(closes[i])):
        a, b = closes[i + h][j], closes[i][j]
        if a is None or b is None or b <= 0:
            continue
        out.append(a / b - 1.0)
    return out


def breadth_at(closes, i, n=20):
    hit = tot = 0
    if i - n < 0:
        return None
    for j in range(len(closes[i])):
        acc = 0.0
        ok = True
        for k in range(i - n + 1, i + 1):
            v = closes[k][j]
            if v is None:
                ok = False
                break
            acc += v
        if not ok:
            continue
        tot += 1
        if closes[i][j] > acc / n:
            hit += 1
    if tot == 0:
        return None
    return hit / tot


def ladder_momentum(closes, symbols, i, n=20):
    if i - n < 0:
        return None
    vals = []
    for s in LADDER:
        if s not in symbols:
            continue
        j = symbols.index(s)
        a, b = closes[i][j], closes[i - n][j]
        if a is None or b is None or b <= 0:
            continue
        vals.append(a / b - 1.0)
    if not vals:
        return None
    return sum(vals) / len(vals)


def tstat(xs):
    if len(xs) < 3:
        return None
    m = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return None
    return m / (sd / math.sqrt(len(xs)))


def era_of(d):
    y = int(d[:4])
    if y < 2017:
        return "pre2017"
    if y <= 2020:
        return "2017-2020"
    if y <= 2023:
        return "2021-2023"
    return "2024-now"


def bucketize(samples, q=5):
    """samples: list of (signal, fwd_mean) sorted by time; causal expanding quartiles."""
    hist = []
    buckets = [[] for _ in range(q)]
    for sig, fw in samples:
        if len(hist) >= BURN:
            srt = sorted(hist)
            cuts = [srt[int(len(srt) * k / q)] for k in range(1, q)]
            idx = 0
            while idx < q - 1 and sig > cuts[idx]:
                idx += 1
            buckets[idx].append(fw)
        hist.append(sig)
    return buckets


def summarize(buckets, stride=H):
    out = []
    for i, b in enumerate(buckets):
        if not b:
            out.append({"bucket": i, "n": 0})
            continue
        sub = b[::stride]
        out.append({
            "bucket": i,
            "n": len(b),
            "mean_bp": round(statistics.fmean(b) * 1e4, 2),
            "t_naive_overlap": round(tstat(b), 2) if tstat(b) is not None else None,
            "n_stride": len(sub),
            "mean_bp_stride": round(statistics.fmean(sub) * 1e4, 2) if sub else None,
            "t_stride": round(tstat(sub), 2) if tstat(sub) is not None else None,
        })
    return out


def run_mode(mode, max_files=None):
    cal, symbols, rows = load_panel(max_files)
    closes, _ = build_returns(cal, rows)
    samples = []
    eras = []
    step = 1
    for i in range(BURN, len(closes) - H, step):
        if mode == "dispersion":
            t5 = trailing(closes, i, 5)
            if len(t5) < 20:
                continue
            sig = statistics.pstdev(t5)
        elif mode == "breadth":
            sig = breadth_at(closes, i, 20)
            if sig is None:
                continue
        elif mode == "ladder":
            sig = ladder_momentum(closes, symbols, i, 20)
            if sig is None:
                continue
        else:
            raise SystemExit("unknown mode %s" % mode)
        fw = forwards(closes, i, H)
        if not fw:
            continue
        samples.append((sig, statistics.fmean(fw)))
        eras.append(era_of(cal[i]))
    buckets = bucketize(samples, 5)
    face = {
        "mode": mode,
        "evidence_cutoff": cal[-1] if cal else None,
        "horizon_bars": H,
        "burn_in_days": BURN,
        "universe_files": len(symbols),
        "calendar_days": len(cal),
        "samples": len(samples),
        "buckets": summarize(buckets),
        "era_split_top_bucket": {},
        "honest": [
            "overlapping forward windows (step 1d): naive t inflated, stride-5 t reported",
            "expanding causal quintiles, 250-day burn-in",
            "descriptive census: no gate, no verdict, no trial count consumed",
        ],
    }
    # era split of the top bucket only (cheap, honest)
    top = buckets[-1]
    by_era = {}
    idx = 0
    for (sig, fw), era in zip(samples, eras):
        if len(samples) - len(top) <= idx < len(samples):
            by_era.setdefault(era, []).append(fw)
        idx += 1
    for era, vals in sorted(by_era.items()):
        face["era_split_top_bucket"][era] = {
            "n": len(vals),
            "mean_bp": round(statistics.fmean(vals) * 1e4, 2),
            "t": round(tstat(vals), 2) if tstat(vals) is not None else None,
        }
    return face


def selftest():
    ok = 0
    total = 0
    # 1. trailing returns
    closes = [[10.0, 20.0, 30.0], [11.0, 20.0, 33.0]]
    tr = trailing(closes, 1, 1)
    assert len(tr) == 3 and abs(tr[0] - 0.1) < 1e-9 and abs(tr[1]) < 1e-12 and abs(tr[2] - 0.1) < 1e-9
    ok += 1; total += 1
    # 2. forward returns
    assert abs(forwards(closes, 0, 1)[0] - 0.1) < 1e-12
    ok += 1; total += 1
    # 3. breadth = 2/3 above MA
    c = [[1.0, 1.0, 1.0], [2.0, 0.0, 2.0], [4.0, 0.0, 2.0]]
    assert abs(breadth_at(c, 2, 2) - 1 / 3) < 1e-12
    ok += 1; total += 1
    # 4. bucketize respects burn-in
    s = [(float(i), 0.01) for i in range(BURN + 10)]
    b = bucketize(s, 5)
    assert sum(len(x) for x in b) == 10
    ok += 1; total += 1
    # 5. summarize stride subsampling
    r = summarize([[0.01] * 10], stride=5)[0]
    assert r["n"] == 10 and r["n_stride"] == 2
    ok += 1; total += 1
    # 6. ladder momentum sign
    cl = [[10.0] * 5 for _ in range(21)]
    cl_flat = list(cl)
    for j in range(5):
        cl_flat[20][j] = 12.0
    m = ladder_momentum(cl_flat, LADDER, 20, 20)
    assert abs(m - 0.2) < 1e-9
    ok += 1; total += 1
    # 7. era_of
    assert era_of("2016-05-01") == "pre2017" and era_of("2026-10-20") == "2024-now"
    ok += 1; total += 1
    # 8. tstat None on tiny sample
    assert tstat([0.1, 0.2]) is None
    ok += 1; total += 1
    print("selftest %d/%d PASS" % (ok, total))
    return 0


def main(argv):
    global H
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="dispersion",
                    choices=["dispersion", "breadth", "ladder", "selftest"])
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--horizon", type=int, default=H)
    args = ap.parse_args(argv)
    if args.horizon != H:
        H = args.horizon
    if args.mode == "selftest":
        return selftest()
    face = run_mode(args.mode, args.max_files)
    os.makedirs(OUTDIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    path = os.path.join(OUTDIR, "CENSUS-%s-h%d-%s.json" % (args.mode, H, stamp))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: face[k] for k in ("mode", "evidence_cutoff", "samples", "universe_files")}, ensure_ascii=False))
    for b in face["buckets"]:
        print(b)
    print("face:", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))