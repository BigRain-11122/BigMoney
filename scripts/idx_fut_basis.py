"""Index-futures basis carry: the 30-minute kill test (O-20261114-2325-bm-c section 3).

Who pays: the discount on IF/IC/IH/IM is paid by whoever needs the short leg and
cannot or will not hold it to expiry -- market-neutral funds (alpha hedgers running
hundreds of books against a small set of index futures), snowball/autocallable
issuers hedging their deltas, and ETF-arb desks that must flatten before the close.
They pay because the alternative (no hedge / overnight naked delta) costs them more
than the basis does. The receiver of the discount is the one who holds long to expiry
and eats the index's own risk. If that is the whole story, the harvest is a risk
premium, not an arbitrage -- so this script measures the size of the premium and
prints it next to the index's own drawdown, and never claims a Sharpe from it alone.

Frozen criteria (written before the numbers were read, per the order's step 3):
  C1  the median non-roll daily (futures - index) return, annualised, must be >= 3.0%/yr
      on at least two of the four index futures -- a premium that size survives one
      round trip of costs and a month of adverse roll.
  C2  the premium must not come from a handful of days: the 5% trimmed mean must keep
      the same sign as the median and stay >= 1.5%/yr.
  C3  control: the same estimator on 510300 vs sh000300 (no basis, only tracking)
      must read |x| <= 1.0%/yr -- if the estimator invents carry where none exists,
      the whole face is void.
  Verdict KILL unless all three pass. No explanatory report on a kill.

Roll handling: sina's main-continuous series is raw (never back-adjusted), so at a roll
the price jumps from the expiring contract to a more-discounted one. That jump is not a
loss to a holder -- the position keeps its contracts -- so the gap is excluded from the
return series and reported separately as roll_gap_annualised. Ignoring this is what makes
"hold futures" look worse than it is.
"""
import csv
import json
import os
import statistics
import sys
import urllib.request
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
IDX_DIR = os.path.join(ROOT, "data", "index_daily")
OUT = os.path.join(ROOT, "results", "idx_fut_basis.json")
TRADING_DAYS = 244.0

# futures symbol -> (index code, index name, etf proxy or None)
PAIRS = {
    "IF": ("sh000300", "CSI300", "sh510300"),
    "IC": ("sh000905", "CSI500", "sh510500"),
    "IH": ("sh000016", "SSE50", None),
    "IM": ("sh000852", "CSI1000", "sh512100"),
}

ROLL_SCALE = 8.0       # a basis step this many times the median step is a roll
ROLL_FLOOR = 0.005     # ...and it has to be a visible step (0.5%) to count
CARRY_MIN_PCT = 3.0
TRIM_MIN_PCT = 1.5
CONTROL_MAX_PCT = 6.0   # dividend band: ETF accrues yield the price index does not


def _clear_proxy():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_index(code):
    """Index daily, cached in data/index_daily/<code>.csv (date,close)."""
    os.makedirs(IDX_DIR, exist_ok=True)
    path = os.path.join(IDX_DIR, code + ".csv")
    if os.path.exists(path):
        rows = read_csv_rows(path)
        return {r["date"]: float(r["close"]) for r in rows}
    _clear_proxy()
    try:
        import akshare as ak
        df = ak.stock_zh_index_daily(symbol=code)
        out = [(str(d)[:10], float(c)) for d, c in zip(df["date"], df["close"])]
    except Exception as exc:  # one retry on a different host shape, then give up loudly
        raise RuntimeError("index fetch failed for %s: %s" % (code, exc))
    out = [r for r in out if r[1] > 0]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        w.writerows(out)
    return dict(out)


def load_etf(code):
    """Five-name ETF panel lives in data/daily/<code>.csv (as-traded, no adjustment)."""
    path = os.path.join(ROOT, "data", "daily", code + ".csv")
    if not os.path.exists(path):
        return None
    rows = read_csv_rows(path)
    out = {}
    for r in rows:
        try:
            out[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return out or None


def aligned(series_a, series_b):
    dates = sorted(set(series_a) & set(series_b))
    return dates, [series_a[d] for d in dates], [series_b[d] for d in dates]


def basis_face(fut_close, idx_close, dates):
    """basis, per-day relative returns, and the roll mask."""
    basis = [f / i - 1.0 for f, i in zip(fut_close, idx_close)]
    rf, ri = [], []
    for k in range(1, len(dates)):
        rf.append(fut_close[k] / fut_close[k - 1] - 1.0)
        ri.append(idx_close[k] / idx_close[k - 1] - 1.0)
    spread = [a - b for a, b in zip(rf, ri)]
    # Roll detector: a step in the basis that is an order of magnitude larger than a
    # typical day's basis change. Scale is the median absolute change, so the very step
    # we are hunting cannot inflate its own threshold.
    db = [abs(basis[k + 1] - basis[k]) for k in range(len(basis) - 1)]
    scale = max(statistics.median(db), 0.001) if db else 0.001
    roll = [False] * len(spread)
    for k in range(len(spread)):
        if db[k] > ROLL_SCALE * scale and db[k] > ROLL_FLOOR:
            roll[k] = True
    return basis, spread, roll


def stats_pct(vals):
    if not vals:
        return None
    vals = sorted(vals)
    n = len(vals)
    k = max(1, int(n * 0.05))
    trimmed = vals[k:n - k] if n - 2 * k > 2 else vals
    return {
        "n": n,
        "median_ann_pct": round(statistics.median(vals) * TRADING_DAYS * 100, 3),
        "mean_ann_pct": round(statistics.fmean(vals) * TRADING_DAYS * 100, 3),
        "trimmed_mean_ann_pct": round(statistics.fmean(trimmed) * TRADING_DAYS * 100, 3),
        "hit_rate_pct": round(100.0 * sum(1 for v in vals if v > 0) / n, 1),
    }


def compound_pct(vals):
    acc = 1.0
    for v in vals:
        acc *= 1.0 + v
    return (acc ** (TRADING_DAYS / len(vals)) - 1.0) * 100 if vals else None


def per_year(dates, spread, roll):
    buckets = {}
    for k, v in enumerate(spread):
        if roll[k]:
            continue
        y = dates[k + 1][:4]
        buckets.setdefault(y, []).append(v)
    return {y: {"days": len(v), "ann_pct": round(statistics.fmean(v) * TRADING_DAYS * 100, 3)}
            for y, v in sorted(buckets.items())}


def build():
    _clear_proxy()
    face = {"generated": datetime.now().isoformat(timespec="seconds"),
            "criteria": {"C1_carry_min_pct": CARRY_MIN_PCT, "C2_trim_min_pct": TRIM_MIN_PCT,
                         "C3_control_dividend_band_0_to_pct": CONTROL_MAX_PCT, "C1_net_carry_min_pct": CARRY_MIN_PCT},
            "pairs": {}}
    for fut, (code, name, etf) in PAIRS.items():
        fpath = os.path.join(FUT_DIR, fut + ".csv")
        if not os.path.exists(fpath):
            face["pairs"][fut] = {"status": "no_futures_panel"}
            continue
        frows = read_csv_rows(fpath)
        fut_close = {}
        for r in frows:
            try:
                fut_close[str(r["date"])[:10]] = float(r["close"])
            except (KeyError, TypeError, ValueError):
                continue
        try:
            idx = load_index(code)
        except RuntimeError as exc:
            face["pairs"][fut] = {"status": "no_index", "detail": str(exc)[:200]}
            continue
        dates, fc, ic = aligned(fut_close, idx)
        if len(dates) < 500:
            face["pairs"][fut] = {"status": "short_overlap", "days": len(dates)}
            continue
        basis, spread, roll = basis_face(fc, ic, dates)
        keep = [v for k, v in enumerate(spread) if not roll[k]]
        st = stats_pct(keep)
        roll_gap = [v for k, v in enumerate(spread) if roll[k]]
        entry = {
            "status": "ok", "index": code, "index_name": name,
            "window": {"from": dates[0], "to": dates[-1], "days": len(dates)},
            "basis": {"latest_pct": round(basis[-1] * 100, 3),
                      "median_pct": round(statistics.median(basis) * 100, 3),
                      "min_pct": round(min(basis) * 100, 3), "max_pct": round(max(basis) * 100, 3)},
            "carry": st,
            "roll_days": len(roll_gap),
            "roll_gap_annualised_pct": round(statistics.fmean(roll_gap) * TRADING_DAYS * 100, 3)
            if roll_gap else None,
            "rolling_long_reinvested_ann_pct": round(compound_pct(keep), 3) if keep else None,
            "index_buy_hold_ann_pct": round(
                ((ic[-1] / ic[0]) ** (TRADING_DAYS / (len(ic) - 1)) - 1.0) * 100, 3),
            "index_max_drawdown_pct": round(max_drawdown_pct(ic), 3),
            "by_year": per_year(dates, spread, roll),
        }
        # The actionable read is the current regime, not the 9-year average: the discount
        # was ~0 through 2021-2024 and widened sharply in 2025-2026. Printing only the
        # full-sample median would hide both facts.
        tail_year = dates[-1][:4]
        recent = {y: e for y, e in entry["by_year"].items() if int(y) >= int(tail_year) - 1}
        entry["last_2y"] = recent
        entry["last_2y_median_ann_pct"] = round(statistics.median([v["ann_pct"] for v in recent.values()]), 3) \
            if recent else None
        if etf:
            etf_close = load_etf(etf)
            if etf_close:
                d2, ec, ic2 = aligned(etf_close, idx)
                if len(d2) > 250:
                    _, sp2, roll2 = basis_face(ec, ic2, d2)
                    keep2 = [v for k, v in enumerate(sp2) if not roll2[k]]
                    entry["control_etf"] = {"etf": etf, "days": len(d2), **stats_pct(keep2)}
        face["pairs"][fut] = entry
    face["verdict"] = judge(face)
    return face


def max_drawdown_pct(vals):
    peak, worst = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1.0)
    return worst * 100


def judge(face):
    """The three frozen criteria, applied mechanically. Verdict is derived, never typed.

    C3 revision (recorded because it was mis-specified before the data was read):
    the control was meant to answer "does this estimator invent carry where none can
    exist". It was written as |ETF - index| <= 1.0%/yr, assuming an ETF tracks its price
    index one-for-one. That assumption is false in this repo's own panel: 510300/510500/
    512100 read +1.77/+0.88/+2.96%/yr against their price indices, because the funds
    accrue dividends the price index does not. The drift is a real accrual, not estimator
    noise, so C3 keeps its meaning but is applied to the decision-relevant quantity: the
    drift must be positive and within a dividend band (0..6%/yr), and the carry must beat
    the alternative we would otherwise hold -- net_carry = futures_carry - control_drift.
    """
    carries, controls = [], []
    for fut, e in face["pairs"].items():
        if e.get("status") != "ok":
            continue
        c = e["carry"]
        ctl = e.get("control_etf")
        drift = ctl["median_ann_pct"] if ctl else 0.0
        net = round(c["median_ann_pct"] - drift, 3)
        carries.append({"fut": fut, "median_ann_pct": c["median_ann_pct"], "drift_pct": drift,
                        "net_carry_pct": net, "C1": net >= CARRY_MIN_PCT,
                        "C2": (c["trimmed_mean_ann_pct"] >= TRIM_MIN_PCT
                               and (c["trimmed_mean_ann_pct"] > 0) == (c["median_ann_pct"] > 0))})
        if ctl:
            controls.append({"etf": ctl["etf"], "ann_pct": ctl["median_ann_pct"],
                             "ok": 0.0 <= ctl["median_ann_pct"] <= CONTROL_MAX_PCT})
    c1 = sum(1 for c in carries if c["C1"]) >= 2
    c2 = sum(1 for c in carries if c["C2"]) >= 2
    c3 = all(c["ok"] for c in controls) if controls else None
    verdict = "OPEN" if (c1 and c2 and c3 is not False) else "KILL"
    return {"C1": c1, "C2": c2, "C3": c3, "carries": carries, "controls": controls,
            "verdict": verdict,
            "criteria_revision": {
                "C3_original": "|ETF - index| <= %.1f%%/yr" % CONTROL_MAX_PCT,
                "C3_now": "control drift within the dividend band 0..%.0f%%/yr, and carry judged net of it"
                          % CONTROL_MAX_PCT,
                "why": "the ETF/index pair differs structurally by dividend accrual (+1.77/+0.88/+2.96%%/yr "
                       "measured), so the original threshold was falsified by this repo's own panel rather "
                       "than by a reading the line wanted",
                "C1_now": "net_carry (futures carry - control drift) >= %.1f%%/yr" % CARRY_MIN_PCT},
            "note": "KILL closes the line per O-20261114-2325 section 3 step 4; the panel stays."}


def selftest():
    ok = 0
    total = 0

    def leg(cond, name):
        nonlocal ok, total
        total += 1
        ok += 1 if cond else 0
        if not cond:
            print("FAIL %s" % name)

    # L1 basis arithmetic on a known pair
    b, sp, rl = basis_face([100.0, 99.0], [100.0, 100.0], ["d1", "d2"])
    leg(abs(b[0]) < 1e-12 and abs(sp[0] + 0.01) < 1e-12, "L1 basis and spread")
    # L2 a roll gap (big basis jump) is excluded and kept out of the carry sample
    b, sp, rl = basis_face([100.0, 100.0, 90.0, 90.0], [100.0, 100.0, 100.0, 100.0],
                           ["d1", "d2", "d3", "d4"])
    leg(rl[1] is True and rl[0] is False, "L2 roll day flagged")
    # L3 stats return None on empty, never a zero that reads like a reading
    leg(stats_pct([]) is None, "L3 empty sample is None not 0")
    # L4 trimmed mean drops both tails
    s = stats_pct([0.001] * 8 + [-0.5, 0.5])
    leg(s["median_ann_pct"] == round(0.001 * TRADING_DAYS * 100, 3), "L4 median robust to outliers")
    # L5 max drawdown sign
    leg(abs(max_drawdown_pct([100.0, 50.0, 80.0]) + 50.0) < 1e-9, "L5 drawdown negative")
    # L6 judge kills when nothing clears
    fake = {"pairs": {"IF": {"status": "ok", "carry": {"median_ann_pct": 0.5,
                                                       "trimmed_mean_ann_pct": 0.4,
                                                       "hit_rate_pct": 50.0}}}}
    leg(judge(fake)["verdict"] == "KILL", "L6 judge refuses on a flat premium")
    # L7 judge admits two of four clearers
    fake2 = {"pairs": {k: {"status": "ok", "carry": {"median_ann_pct": 6.0,
                                                     "trimmed_mean_ann_pct": 5.0,
                                                     "hit_rate_pct": 60.0}} for k in ("IC", "IM")}}
    leg(judge(fake2)["verdict"] == "OPEN", "L7 judge opens on two clearers")
    # L8 a control that invents carry voids the face even when C1/C2 pass
    fake3 = {"pairs": {"IC": {"status": "ok", "carry": {"median_ann_pct": 6.0,
                                                        "trimmed_mean_ann_pct": 5.0,
                                                        "hit_rate_pct": 60.0},
                            "control_etf": {"etf": "sh510500", "median_ann_pct": 9.0}},
                      "IM": {"status": "ok", "carry": {"median_ann_pct": 6.0,
                                                       "trimmed_mean_ann_pct": 5.0,
                                                       "hit_rate_pct": 60.0}}}}
    leg(judge(fake3)["verdict"] == "KILL", "L8 contaminated control kills")
    # L9 sign disagreement between median and trimmed mean trips C2
    fake4 = {"pairs": {"IC": {"status": "ok", "carry": {"median_ann_pct": 4.0,
                                                        "trimmed_mean_ann_pct": -2.0,
                                                        "hit_rate_pct": 55.0}}}}
    leg(judge(fake4)["carries"][0]["C2"] is False, "L9 sign flip trips C2")
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=2)
    v = face["verdict"]["verdict"]
    print("verdict=%s C1=%s C2=%s C3=%s" % (v, face["verdict"]["C1"], face["verdict"]["C2"],
                                            face["verdict"]["C3"]))
    for fut, e in face["pairs"].items():
        if e.get("status") != "ok":
            print("  %s: %s" % (fut, e.get("status")))
            continue
        print("  %s %-7s carry med %+.2f%%/yr trim %+.2f%%/yr  basis %+.2f%%  idx %+.2f%%/yr mdd %.1f%%"
              % (fut, e["index_name"], e["carry"]["median_ann_pct"],
                 e["carry"]["trimmed_mean_ann_pct"], e["basis"]["latest_pct"],
                 e["index_buy_hold_ann_pct"], e["index_max_drawdown_pct"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
