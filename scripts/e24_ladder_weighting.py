"""E24 ladder weighting-scheme census (descriptive; NO judgment, NO prereg).

The r1091/r1092 timing overlays were honest negatives: the five-member ladder
edge is a hold effect, not a timing effect. That leaves the open question --
given we always hold, HOW should the five members be weighted?

Schemes compared (all causal, monthly rebalance at the last trading day of the
month, weights from data through that day only):

  equal    : 1/k among members that already have >=250 bars of history
  invvol   : inverse of trailing 60d realised vol, normalised
  liq      : trailing 60d mean turnover (amount) share, normalised
  momtilt  : max(120d return, 0) + 0.10 floor, normalised (momentum tilt)

Cash-leg treatment (E25 r1097): `trendN` parks the filtered-out share in cash.
That cash now accrues at the daily GC001 repo close (annualised percent, 252-day
convention, ffilled over non-repo days) for EVERY scheme, including the idle
capital before a member clears the 250-bar eligibility gate -- so the comparison
is against a real account, not against cash that earns nothing.

Honest notes baked into the face:
  * universe grows over time (510300 from 2012, 512100 from 2016-11,
    588000 from 2020-11) -- the same membership rule applies to every scheme,
    so the comparison is within-universe, not against a fixed basket.
  * 13.041bp per side cost applied to turnover at each rebalance.
  * synthetic cap-weight is NOT reported: the panel has no shares outstanding;
    `liq` is a turnover-share proxy and is labelled as such.
  * descriptive only: no gate, no verdict, no trial count consumed.
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
OUTDIR = os.path.join(ROOT, "results", "e24_ladder_weighting")
LADDER = ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"]
COST_BP_SIDE = 13.041
MIN_BARS = 250
VOL_WIN = 60
MOM_WIN = 120
CASH_FILE = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
CASH_UNITS_PER_YEAR = 252.0


def load_panel(symbols=LADDER):
    """returns (calendar, closes, amounts) aligned on the primary symbol calendar."""
    closes = {}
    amounts = {}
    for s in symbols:
        p = os.path.join(DAILY, s + ".csv")
        if not os.path.exists(p):
            continue
        c = {}
        a = {}
        with open(p, "r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                d = (row.get("date") or "").strip()
                v = (row.get("close") or "").strip()
                if not d or not v:
                    continue
                try:
                    c[d] = float(v)
                except ValueError:
                    continue
                try:
                    a[d] = float(row.get("amount") or 0.0)
                except ValueError:
                    a[d] = 0.0
        closes[s] = c
        amounts[s] = a
    primary = LADDER[0]
    cal = sorted(closes.get(primary) or sorted({d for c in closes.values() for d in c}))
    return cal, closes, amounts


def rate_daily(ann_pct):
    """annualised repo percent -> per-trading-day decimal return."""
    return float(ann_pct) / 100.0 / CASH_UNITS_PER_YEAR


def load_cash_series(cal):
    """GC001 close (annualised %) aligned to cal, ffilled; missing tail = None.

    Returns {date: daily decimal return} plus coverage counters, or None when the
    panel is absent (callers then fall back to the 0% cash convention).
    """
    if not os.path.exists(CASH_FILE):
        return None
    raw = {}
    with open(CASH_FILE, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            v = (row.get("close") or "").strip()
            if not d or not v:
                continue
            try:
                raw[d] = float(v)
            except ValueError:
                continue
    if not raw:
        return None
    out = {}
    last = None
    filled = 0
    for d in cal:
        if d in raw:
            last = raw[d]
        elif last is not None:
            filled += 1
        if last is not None:
            out[d] = rate_daily(last)
    return {"series": out, "ffilled_days": filled, "covered_days": len(out),
            "first": next(iter(sorted(raw))), "last": max(raw)}


def trailing_vol(prices, i, win=VOL_WIN):
    if i - win < 0:
        return None
    rs = []
    for k in range(i - win + 1, i + 1):
        a, b = prices[k], prices[k - 1]
        if a is None or b is None or b <= 0 or a <= 0:
            return None
        rs.append(a / b - 1.0)
    if len(rs) < 3:
        return None
    sd = statistics.pstdev(rs)
    return sd if sd > 0 else None


def trailing_mean(values, i, win=VOL_WIN):
    if i - win + 1 < 0:
        return None
    seg = values[i - win + 1:i + 1]
    if any(v is None for v in seg):
        return None
    return statistics.fmean(seg)


def trailing_ret(prices, i, win=MOM_WIN):
    if i - win < 0:
        return None
    a, b = prices[i], prices[i - win]
    if a is None or b is None or b <= 0:
        return None
    return a / b - 1.0


def elig(prices, i):
    """member is investable when it has MIN_BARS of non-missing closes."""
    if i < MIN_BARS:
        return False
    return all(prices[k] is not None for k in range(i - MIN_BARS + 1, i + 1))


def scheme_weights(scheme, idx, prices, amounts):
    """idx: calendar index of the rebalance day. Returns {symbol: weight} or {}."""
    live = [s for s in LADDER if s in prices and elig(prices[s], idx)]
    if not live:
        return {}
    if scheme == "equal":
        w = 1.0 / len(live)
        return {s: w for s in live}
    if scheme.startswith("trend"):
        # per-member trend filter: hold a member only while its close sits above
        # its own win-day moving average (causal, read at the rebalance day).
        # "trendNr" renormalises the survivors to full investment; "trendN"
        # leaves the filtered-out share in cash (0%).
        body = scheme[5:]
        while body and body[-1] in ("r", "h", "c"):
            body = body[:-1]
        renorm = scheme.endswith("r")
        half = "h" in scheme[5:].replace(body, "")
        win_s = body
        try:
            win = int(win_s)
        except ValueError:
            raise SystemExit("unknown scheme %s" % scheme)
        keep, drop = [], []
        for s in live:
            m = trailing_mean(prices[s], idx, win)
            a = prices[s][idx]
            if m is None or a is None or m <= 0:
                continue
            (keep if a > m else drop).append(s)
        if not keep and not drop:
            return {}
        if half:
            # soft filter: a member below its MA keeps a half share (partial cash)
            w0 = 1.0 / len(live)
            out = {s: w0 for s in keep}
            out.update({s: 0.5 * w0 for s in drop})
            return out
        if not keep:
            return {}
        if renorm:
            w = 1.0 / len(keep)
            return {s: w for s in keep}
        w = 1.0 / len(live)
        return {s: w for s in keep}
    raw = {}
    for s in live:
        if scheme == "invvol":
            v = trailing_vol(prices[s], idx)
            if v is None or v <= 0:
                continue
            raw[s] = 1.0 / v
        elif scheme == "liq":
            m = trailing_mean(amounts[s], idx)
            if m is None or m <= 0:
                continue
            raw[s] = m
        elif scheme == "momtilt":
            r = trailing_ret(prices[s], idx)
            if r is None:
                continue
            raw[s] = max(r, 0.0) + 0.10
        else:
            raise SystemExit("unknown scheme %s" % scheme)
    tot = sum(raw.values())
    if not raw or tot <= 0:
        w = 1.0 / len(live)
        return {s: w for s in live}
    return {s: v / tot for s, v in raw.items()}


def month_end_indices(cal):
    """indices of the last trading day of each calendar month."""
    out = []
    for i in range(len(cal)):
        if i == len(cal) - 1 or cal[i + 1][:7] != cal[i][:7]:
            out.append(i)
    return out


def simulate(scheme, cal, closes, amounts, cash=None, cost_mult=1.0):
    prices = {s: [closes[s].get(d) for d in cal] for s in closes}
    vol_proxy = {s: [amounts[s].get(d) for d in cal] for s in closes}
    rebal = set(month_end_indices(cal))
    port = 1.0
    weights = {}
    curve = []
    cost_paid = 0.0
    turnover_total = 0.0
    n_rebal = 0
    cash_series = cash["series"] if cash else None
    for i in range(1, len(cal)):
        # drift existing weights with today's returns
        if weights or cash_series is not None:
            growth = 0.0
            neww = {}
            for s, w in weights.items():
                a, b = prices[s][i], prices[s][i - 1]
                if a is None or b is None or b <= 0:
                    neww[s] = w
                    continue
                r = a / b - 1.0
                neww[s] = w * (1.0 + r)
                growth += w * r
            if cash_series is None:
                tot = sum(neww.values())
                weights = {s: v / tot for s, v in neww.items()} if tot > 0 else weights
                port *= (1.0 + growth)
            else:
                # the filtered share is real cash: it accrues at the repo rate
                # instead of sitting at 0%, and stock weights are normalised by
                # the WHOLE portfolio value so the cash share survives drift.
                cw = 1.0 - sum(weights.values())
                if cw < 1e-12:
                    cw = 0.0
                rc = cash_series.get(cal[i], 0.0)
                growth += cw * rc
                tv = sum(neww.values()) + cw * (1.0 + rc)
                weights = {s: v / tv for s, v in neww.items()} if tv > 0 else weights
                port *= (1.0 + growth)
        # rebalance on the LAST trading day of the month: weights are set from
        # data through that day and take effect from the next bar (causal).
        if (i - 1) in rebal:
            target = scheme_weights(scheme, i - 1, prices, vol_proxy)
            if target:
                if weights:
                    turnover = sum(abs(target.get(s, 0.0) - weights.get(s, 0.0))
                                   for s in set(target) | set(weights)) / 2.0
                else:
                    turnover = 1.0
                fee = turnover * COST_BP_SIDE * cost_mult / 1e4
                port *= (1.0 - fee)
                cost_paid += fee
                turnover_total += turnover
                n_rebal += 1
                weights = dict(target)
        curve.append((cal[i], port))
    return curve, {
        "rebalances": n_rebal,
        "turnover_total": turnover_total,
        "turnover_per_year": None,
        "cost_paid_frac": cost_paid,
    }


def metrics(curve, years):
    if len(curve) < 30:
        return {}
    vals = [v for _, v in curve]
    rets = [vals[k] / vals[k - 1] - 1.0 for k in range(1, len(vals))]
    total = vals[-1] / vals[0] - 1.0
    ann = (vals[-1] / vals[0]) ** (1.0 / years) - 1.0 if years > 0 else None
    vol = statistics.pstdev(rets) * math.sqrt(252)
    shp = (statistics.fmean(rets) / statistics.pstdev(rets) * math.sqrt(252)
           if statistics.pstdev(rets) > 0 else None)
    return {
        "total_return_pct": round(total * 100, 2),
        "ann_return_pct": round(ann * 100, 2) if ann is not None else None,
        "ann_vol_pct": round(vol * 100, 2),
        "sharpe": round(shp, 3) if shp is not None else None,
        "bars": len(rets),
    }


def era_of(d):
    y = int(d[:4])
    if y < 2017:
        return "pre2017"
    if y <= 2020:
        return "2017-2020"
    if y <= 2023:
        return "2021-2023"
    return "2024-now"


def monthly_relative(curve, base_curve):
    """monthly return differences vs the base curve -> (mean_bp, t, n_months)."""
    b = dict(base_curve)
    months = {}
    prev = None
    for d, v in curve:
        if d not in b or b[d] <= 0 or v <= 0:
            continue
        ratio = v / b[d]
        if prev is not None:
            months.setdefault(d[:7], []).append(ratio / prev - 1.0)
        prev = ratio
    ends = []
    for key in sorted(months):
        acc = 1.0
        for r in months[key]:
            acc *= (1.0 + r)
        if months[key]:
            ends.append(acc - 1.0)
    if len(ends) < 12:
        return {"months": len(ends), "mean_bp": None, "t": None}
    mean = statistics.fmean(ends)
    sd = statistics.pstdev(ends)
    t = mean / (sd / math.sqrt(len(ends))) if sd > 0 else None
    by_era = {}
    for key in sorted(months):
        vals = months[key]
        if not vals:
            continue
        acc = 1.0
        for r in vals:
            acc *= (1.0 + r)
        by_era.setdefault(era_of(key + "-01"), []).append(acc - 1.0)
    eras = {}
    for era, vals in sorted(by_era.items()):
        eras[era] = {"months": len(vals),
                     "mean_bp": round(statistics.fmean(vals) * 1e4, 2)}
    return {"months": len(ends), "mean_bp": round(mean * 1e4, 2),
            "t": round(t, 2) if t is not None else None, "by_era": eras}


def run(schemes, start=None, cost_mult=1.0):
    cal, closes, amounts = load_panel()
    if start:
        cal = [d for d in cal if d >= start]
        closes = {s: {d: v for d, v in c.items() if d >= start} for s, c in closes.items()}
        amounts = {s: {d: v for d, v in a.items() if d >= start} for s, a in amounts.items()}
    years = len(cal) / 252.0
    faces = {}
    base_curve = None
    cash = load_cash_series(cal)  # idle cash earns the repo rate for EVERY scheme
    for sch in schemes:
        curve, aux = simulate(sch, cal, closes, amounts, cash, cost_mult)
        m = metrics(curve, years)
        aux["turnover_per_year"] = round(aux["turnover_total"] / years, 3) if years else None
        aux["cost_per_year_bp"] = round(aux["cost_paid_frac"] / years * 1e4, 1) if years else None
        if sch == "equal":
            base_curve = curve
        faces[sch] = {"metrics": m, "aux": aux}
    # delta vs equal, on the shared calendar
    if base_curve:
        bmap = dict(base_curve)
        for sch, f in faces.items():
            if sch == "equal":
                continue
            curve, _ = simulate(sch, cal, closes, amounts, cash, cost_mult)
            d = []
            for d0, v in curve:
                if d0 in bmap and bmap[d0] > 0:
                    d.append(v / bmap[d0] - 1.0)
            f["vs_equal_bp_annualised"] = round(d[-1] / years * 1e4, 1) if d and years else None
            f["vs_equal_monthly"] = monthly_relative(curve, base_curve)
    face = {
        "study": "e24_ladder_weighting",
        "evidence_cutoff": cal[-1] if cal else None,
        "start": cal[0] if cal else None,
        "bars": len(cal),
        "years": round(years, 2),
        "members": LADDER,
        "cost_bp_per_side": COST_BP_SIDE,
        "cost_mult": cost_mult,
        "schemes": faces,
        "cash_leg": ({"source": "data/repo_daily/GC001.csv close (annualised %)",
                      "units_per_year": CASH_UNITS_PER_YEAR,
                      "covered_days": cash["covered_days"],
                      "ffilled_days": cash["ffilled_days"],
                      "first_rate_date": cash["first"],
                      "last_rate_date": cash["last"]}
                     if cash else None),
        "honest": [
            "universe grows over time (510300 2012-05 / 510500 2013-03 / 512100 2016-11 / 588000 2020-11); "
            "membership rule is identical across schemes so the comparison is within-universe",
            "liq is a turnover(amount)-share proxy, NOT cap-weight: the panel carries no shares outstanding",
            "weights drift with returns inside the month; 13.041bp/side charged on turnover at each monthly rebalance",
            "`c` schemes accrue the cash share at the daily GC001 close (annualised %, /252, ffilled over non-repo days); "
            "the repo rate is the SAME series a live account would earn, but it is not a traded return and carries no cost",
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
        ],
    }
    return face


def selftest():
    ok = 0
    tot = 0
    # 1. trailing_vol on a constant series -> 0 -> None
    p = [10.0] * 70
    assert trailing_vol(p, 69) is None
    ok += 1; tot += 1
    # 2. trailing_vol positive on a rising series
    p = [10.0 * (1.001 ** k) for k in range(70)]
    v = trailing_vol(p, 69)
    assert v is not None and v > 0
    ok += 1; tot += 1
    # 3. trailing_mean
    a = [float(k) for k in range(70)]
    assert abs(trailing_mean(a, 69) - statistics.fmean(range(10, 70))) < 1e-9
    ok += 1; tot += 1
    # 4. trailing_ret
    p = [10.0] * 121
    p[120] = 12.0
    assert abs(trailing_ret(p, 120) - 0.2) < 1e-9
    ok += 1; tot += 1
    # 5. elig needs MIN_BARS history
    prices = {"sh510300": [10.0] * 300}
    assert elig(prices["sh510300"], 249) is False and elig(prices["sh510300"], 250) is True
    ok += 1; tot += 1
    # 6. equal weights sum to 1
    cal = ["2020-01-%02d" % d for d in range(1, 32)]
    prices = {s: [10.0] * 300 for s in LADDER}
    amounts = {s: [1.0] * 300 for s in LADDER}
    w = scheme_weights("equal", 260, prices, amounts)
    assert abs(sum(w.values()) - 1.0) < 1e-12 and len(w) == len(LADDER)
    ok += 1; tot += 1
    # 7. invvol tilts toward the calmer member (alternating returns so stdev > 0)
    def walk(amp):
        out = [10.0]
        for k in range(1, 300):
            out.append(out[-1] * (1.0 + (amp if k % 2 else -amp)))
        return out
    prices = {s: walk(0.005) for s in LADDER}
    prices["sh510300"] = walk(0.0005)
    w = scheme_weights("invvol", 260, prices, amounts)
    assert w["sh510300"] > 0.5
    ok += 1; tot += 1
    # 8. momtilt floors a negative-momentum member at the 0.10 floor
    prices = {s: [10.0] * 300 for s in LADDER}
    for s in LADDER:
        prices[s] = [10.0 * (0.999 ** k) for k in range(300)]
    prices["sh510050"] = [10.0 * (1.01 ** k) for k in range(300)]
    w = scheme_weights("momtilt", 260, prices, amounts)
    assert w["sh510050"] > 0.5 and abs(sum(w.values()) - 1.0) < 1e-12
    ok += 1; tot += 1
    # 9. month_end_indices picks last day of each month
    cal = ["2020-01-30", "2020-01-31", "2020-02-03", "2020-02-28"]
    assert month_end_indices(cal) == [1, 3]
    ok += 1; tot += 1
    # 10. metrics recover a known constant curve
    curve = [("d%d" % k, 1.01 ** k) for k in range(253)]
    m = metrics(curve, 1.0)
    assert abs(m["total_return_pct"] - (1.01 ** 252 - 1) * 100) < 0.1
    assert abs(m["ann_return_pct"] - (1.01 ** 252 - 1) * 100) < 0.1
    ok += 1; tot += 1
    # 11. simulate pays a cost on the first rebalance and never divides by zero
    cal = ["%d-%02d-%02d" % (2020 + k // 300, (k % 12) + 1, (k % 25) + 1) for k in range(320)]
    closes = {s: {d: 10.0 + 0.01 * k for k, d in enumerate(cal)} for s in LADDER}
    amounts = {s: {d: 1e6 for d in cal} for s in LADDER}
    curve, aux = simulate("equal", cal, closes, amounts)
    assert aux["rebalances"] >= 1 and 0 < aux["cost_paid_frac"] < 1
    assert curve[-1][1] > 0
    ok += 1; tot += 1
    # 12. trend filter drops members trading below their own MA
    up = [10.0 * (1.002 ** k) for k in range(300)]
    down = [10.0 * (0.998 ** k) for k in range(300)]
    prices = {s: up for s in LADDER}
    prices["sh510050"] = down
    w = scheme_weights("trend200r", 260, prices, amounts)
    assert "sh510050" not in w and abs(sum(w.values()) - 1.0) < 1e-12
    ok += 1; tot += 1
    # 13. cash variant keeps the nominal share (exposure < 1) instead of renormalising
    w = scheme_weights("trend200", 260, prices, amounts)
    assert "sh510050" not in w and sum(w.values()) < 1.0
    ok += 1; tot += 1
    # 14. all members below their MA -> fully in cash
    prices = {s: down for s in LADDER}
    assert scheme_weights("trend200r", 260, prices, amounts) == {}
    ok += 1; tot += 1
    # 15. soft filter halves a filtered-out member instead of zeroing it
    prices = {s: up for s in LADDER}
    prices["sh510050"] = down
    wh = scheme_weights("trend200h", 260, prices, amounts)
    assert abs(wh["sh510050"] - 0.5 / len(LADDER)) < 1e-12
    assert abs(sum(wh.values()) - (len(LADDER) - 0.5) / len(LADDER)) < 1e-12
    ok += 1; tot += 1
    # 16. annualised percent -> per-day decimal (252-unit convention)
    assert abs(rate_daily(2.52) - 0.0001) < 1e-15
    ok += 1; tot += 1
    # 17. cash-only window accrues at the repo rate (all members below MA)
    down = [10.0 * (0.998 ** k) for k in range(300)]
    prices = {s: down for s in LADDER}
    cal = ["%d-%02d-%02d" % (2020 + k // 300, (k % 12) + 1, (k % 25) + 1) for k in range(300)]
    closes = {s: {d: down[k] for k, d in enumerate(cal)} for s in LADDER}
    amounts = {s: {d: 1e6 for d in cal} for s in LADDER}
    cash = {"series": {d: rate_daily(2.52) for d in cal}, "ffilled_days": 0,
            "covered_days": len(cal), "first": cal[0], "last": cal[-1]}
    curve, _ = simulate("trend200c", cal, closes, amounts, cash)
    assert curve[-1][1] > 1.0 + 0.0001 * (len(cal) - 5)
    ok += 1; tot += 1
    # 18. a zero-rate cash panel leaves every scheme's numbers bit-identical
    flat = {s: {d: 10.0 + 0.001 * k for k, d in enumerate(cal)} for s in LADDER}
    zero = dict(cash)
    zero["series"] = {d: 0.0 for d in cal}
    c0, _ = simulate("equal", cal, flat, amounts)
    c1, _ = simulate("equal", cal, flat, amounts, zero)
    assert all(abs(a[1] - b[1]) < 1e-12 for a, b in zip(c0, c1))
    ok += 1; tot += 1
    # 19. cost_mult scales the paid fee linearly (x3 costs 3x)
    _, a1 = simulate("equal", cal, flat, amounts, None, 1.0)
    _, a3 = simulate("equal", cal, flat, amounts, None, 3.0)
    assert abs(a3["cost_paid_frac"] - 3.0 * a1["cost_paid_frac"]) < 1e-12
    ok += 1; tot += 1
    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--start", default=None)
    ap.add_argument("--schemes", default="equal,invvol,liq,momtilt")
    ap.add_argument("--out", default=None,
                    help="optional output dir (e.g. results/e25_trend_tilt) for a named sub-face")
    ap.add_argument("--cost-mult", type=float, default=1.0,
                    help="scale the per-side cost (3.0 = the standard cost x3 robustness read)")
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    schemes = [s.strip() for s in args.schemes.split(",") if s.strip()]
    face = run(schemes, args.start, args.cost_mult)
    outdir = os.path.join(ROOT, args.out) if args.out else OUTDIR
    os.makedirs(outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    tag = "TREND" if any(s.startswith("trend") for s in schemes) else "WEIGHTING"
    if args.out:
        # a named sub-face may be run several times with different scheme sets;
        # keep one file per set instead of overwriting the same day's face
        import hashlib
        tag += "-" + hashlib.sha1(",".join(schemes).encode()).hexdigest()[:6]
    if args.cost_mult != 1.0:
        tag += "-x%s" % ("%g" % args.cost_mult).replace(".", "p")
    path = os.path.join(outdir, "%s-%s.json" % (tag, stamp))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"start": face["start"], "cutoff": face["evidence_cutoff"],
                      "years": face["years"], "bars": face["bars"]}, ensure_ascii=False))
    for sch, f in face["schemes"].items():
        print(sch, json.dumps(f, ensure_ascii=False))
    print("face:", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))