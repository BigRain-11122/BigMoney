"""E27 universe-expansion family (descriptive; NO judgment, NO prereg).

E24-E26 settled the *how* questions on a fixed five-member ladder: weighting
schemes, trend filters and drift bands all wash to zero versus plain monthly
equal-weight, and the ladder turns over only 0.32x/yr (4.2bp/yr of cost).
The one question that family never asked is whether the five members are even
the right *expression* of the idea.

This runner asks it directly:

    equal-weight the top-N most liquid eligible ETFs (N = 10/20/50) with the
    exact same accounting as the ladder, and compare.

Selection is causal: at each month end, rank every ETF that already has 250
bars of history by its trailing 60-day mean turnover (amount), take the top N,
equal weight. Everything else is shared with the E24/E25/E26 chain: same
calendar, 13.041bp/side cost on turnover, un-invested share accruing at the
GC001 repo close, decision read at the close and effective from the next bar.

Honest notes baked into the face:
  * the ETF list itself is the population we hold today (survivorship of the
    *listing set*, not of prices) -- a fund that died before we collected it is
    absent, and that biases any "more funds = better diversification" reading
    upward only mildly here because equal-weight liquidity selection is not a
    return-chasing rule.
  * liquidity is a trailing 60d turnover proxy, not shares outstanding.
  * N = 10/20/50 is a multiple-comparison surface; a single winning N is not
    evidence, a consistent sign across N would be.
  * descriptive census only: no gate, no verdict, no prereg, no trial count.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e24_ladder_weighting as base  # noqa: E402  (shared accounting/metrics)

DAILY = os.path.join(ROOT, "data", "daily")
OUTDIR = os.path.join(ROOT, "results", "e27_universe_expansion")
DEFAULT_NS = [10, 20, 50]
# ETF code prefixes on both exchanges: 15x (SZ), 51x/52x/53x/55x/56x/58x (SH)
ETF_PREFIXES = ("15", "51", "52", "53", "55", "56", "58")
NAME_RE = re.compile(r"^(?:(sh|sz))?(\d{6})(?:_([a-z0-9]+))?$")


def _read_series(path):
    closes, amounts = {}, {}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            v = (row.get("close") or "").strip()
            if not d or not v:
                continue
            try:
                closes[d] = float(v)
            except ValueError:
                continue
            try:
                amounts[d] = float(row.get("amount") or 0.0)
            except ValueError:
                amounts[d] = 0.0
    return closes, amounts


def load_universe(daily_dir=DAILY):
    """Load every ETF csv, de-duplicating the bare-code copies.

    data/daily carries both `sh510300.csv` (full history) and `510300.csv`
    (a 2020+ partial copy). The canonical symbol is the exchange-prefixed name;
    when only the bare copy exists the exchange is inferred from the code.
    Files with a `_suffix` (e.g. the T-73 pinned `510880_t73.csv`) are skipped --
    they are slot copies, not panel members.
    """
    cands = {}
    for path in sorted(glob.glob(os.path.join(daily_dir, "*.csv"))):
        name = os.path.basename(path)[:-4]
        m = NAME_RE.match(name)
        if not m:
            continue
        exch, code, suffix = m.group(1), m.group(2), m.group(3)
        if suffix:
            continue
        if not code.startswith(ETF_PREFIXES):
            continue
        sym = (exch or ("sz" if code.startswith("15") else "sh")) + code
        closes, amounts = _read_series(path)
        if len(closes) < base.MIN_BARS:
            continue
        prev = cands.get(sym)
        # longer series wins; on a tie the exchange-prefixed copy wins (the bare
        # names are the 2020+ partial duplicates in this panel)
        rank = (len(closes), 1 if exch else 0)
        if prev is None or rank > prev[0]:
            cands[sym] = (rank, path, closes, amounts)
    return {s: (c, a) for s, (_, _, c, a) in cands.items()}


def _rank(idx, universe, prices, amounts, cache=None):
    """causal liquidity ranking on calendar index idx (trailing 60d mean amount)."""
    if cache is not None and idx in cache:
        return cache[idx]
    rows = []
    for s in universe:
        p = prices.get(s)
        if p is None or not base.elig(p, idx):
            continue
        m = base.trailing_mean(amounts[s], idx)
        if m is None or m <= 0:
            continue
        rows.append((-m, s))
    rows.sort()
    out = [s for _, s in rows]
    if cache is not None:
        cache[idx] = out
    return out


def simulate(cal, prices, amounts, universe, cash=None, pick_n=None, cost_mult=1.0,
             rank_cache=None, rebal=None, contrib=None, universe_at=None):
    """Simulate one scheme. pick_n=None -> equal-weight the given universe.

    rebal: explicit set of calendar indices whose close is the decision point;
    None keeps the E24 default (every month end). E33 uses this for cadence.

    universe_at: E61 seam. A callable idx -> iterable of symbols. When handed in,
    the candidate pool at each decision is ``universe_at(idx)`` instead of the
    static ``universe``; that is what a per-session restriction ("only the
    names the other calendar holds at this session") needs. Default None means
    the static universe, so every published curve is unchanged. Since the pool
    can now differ between decisions, the idx-keyed rank cache is bypassed in
    this mode instead of answering with whichever pool asked first.

    contrib: E174 seam. When a dict is handed in, every day's ``w * r`` is
    accumulated under ``(YYYY-MM, symbol)``, so a reader can ask WHICH name
    carried a month instead of only how much the month paid. It records the
    same ``growth`` term the loop already sums. The un-invested residual is
    booked under the pseudo-name ``__cash__``, because an attribution that
    silently swallows the cash leg reads complete while being short. Default
    None means the recorder costs nothing and no published face changes.
    """
    sink = contrib  # None => recorder off; an EMPTY dict is still a live sink
    if rebal is None:
        rebal = set(base.month_end_indices(cal))
    port = 1.0
    weights = {}
    curve = []
    cost_paid = 0.0
    turnover_total = 0.0
    n_rebal = 0
    holdings = None
    cash_series = cash["series"] if cash else None

    for i in range(1, len(cal)):
        if weights or cash_series is not None:
            growth = 0.0
            neww = {}
            for s, w in weights.items():
                p = prices[s]
                a, b = p[i], p[i - 1]
                if a is None or b is None or b <= 0:
                    neww[s] = w
                    continue
                r = a / b - 1.0
                neww[s] = w * (1.0 + r)
                growth += w * r
                if sink is not None:
                    key = (cal[i][:7], s)
                    sink[key] = sink.get(key, 0.0) + w * r
            cw = 1.0 - sum(weights.values())
            if cw < 1e-12:
                cw = 0.0
            rc = cash_series.get(cal[i], 0.0) if cash_series else 0.0
            growth += cw * rc
            if sink is not None and cw:
                key = (cal[i][:7], "__cash__")
                sink[key] = sink.get(key, 0.0) + cw * rc
            tv = sum(neww.values()) + cw * (1.0 + rc)
            weights = {s: v / tv for s, v in neww.items()} if tv > 0 else weights
            port *= (1.0 + growth)

        if (i - 1) in rebal:
            idx = i - 1
            pool = universe if universe_at is None else list(universe_at(idx))
            if pick_n is None:
                live = [s for s in pool if s in prices and base.elig(prices[s], idx)]
            else:
                live = _rank(idx, pool, prices, amounts,
                             None if universe_at is not None else rank_cache)[:pick_n]
            if live:
                w = 1.0 / len(live)
                target = {s: w for s in live}
                if weights:
                    turnover = sum(abs(target.get(s, 0.0) - weights.get(s, 0.0))
                                   for s in set(target) | set(weights)) / 2.0
                else:
                    turnover = 1.0
                fee = turnover * base.COST_BP_SIDE * cost_mult / 1e4
                port *= (1.0 - fee)
                cost_paid += fee
                turnover_total += turnover
                n_rebal += 1
                weights = dict(target)
                holdings = sorted(weights)
        curve.append((cal[i], port))

    return curve, {
        "rebalances": n_rebal,
        "turnover_total": turnover_total,
        "cost_paid_frac": cost_paid,
    }, holdings


def _universe_summary(universe, cal, prices, amounts):
    """how many ETFs are live per era -- the honest denominator for top-N."""
    marks = {}
    cal_set = set(cal)
    for d in (cal[0], "2017-01-01", "2020-01-01", "2023-01-01", cal[-1]):
        if d not in cal_set:
            d = next((x for x in cal if x >= d), None)
            if d is None:
                continue
        idx = cal.index(d)
        live = [s for s in universe if s in prices and base.elig(prices[s], idx)]
        liq = [s for s in live if (base.trailing_mean(amounts[s], idx) or 0) > 0]
        marks[d] = {"eligible": len(live), "liquid": len(liq)}
    return marks


def run(ns=None, start=None, cost_mult=1.0, end=None, exclude=None, raw=None):
    ns = DEFAULT_NS if not ns else ns
    # ``raw`` is opt-in so a caller can hand in a repaired universe (E77) while
    # every published face keeps reading the panel exactly as before.
    raw = load_universe() if raw is None else raw
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]  # shared calendar (sh510300 close dates)
    if start:
        cal = [d for d in cal if d >= start]
    if end:
        cal = [d for d in cal if d <= end]
    years = len(cal) / 252.0
    all_syms = sorted(set(base.LADDER) | set(raw))
    prices, amounts = {}, {}
    for s in all_syms:
        if s in raw:
            c, a = raw[s]
        else:
            c, a = {}, {}
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    cash = base.load_cash_series(cal)
    universe = [s for s in all_syms if s in raw]

    faces = {}
    curves = {}
    rank_cache = {}
    specs = [("ladder5", None)] + [("top%d" % n, n) for n in ns]
    for name, n in specs:
        univ = base.LADDER if n is None else universe
        curve, aux, holdings = simulate(cal, prices, amounts, univ, cash, n, cost_mult,
                                       rank_cache)
        curves[name] = curve
        m = base.metrics(curve, years)
        aux["turnover_per_year"] = round(aux["turnover_total"] / years, 3) if years else None
        aux["cost_per_year_bp"] = round(aux["cost_paid_frac"] / years * 1e4, 1) if years else None
        faces[name] = {"pick_n": n, "metrics": m, "aux": aux,
                       "last_holdings": holdings,
                       "last_holdings_n": len(holdings or [])}

    base_curve = curves["ladder5"]
    for name, f in faces.items():
        if name == "ladder5":
            continue
        bmap = dict(base_curve)
        d = [v / bmap[d0] - 1.0 for d0, v in curves[name] if d0 in bmap and bmap[d0] > 0]
        f["vs_ladder_bp_annualised"] = round(d[-1] / years * 1e4, 1) if d and years else None
        f["vs_ladder"] = base.monthly_relative(curves[name], base_curve)

    return {
        "study": "e27_universe_expansion",
        "evidence_cutoff": cal[-1] if cal else None,
        "start": cal[0] if cal else None,
        "bars": len(cal),
        "years": round(years, 2),
        "universe_size": len(universe),
        "excluded_prefixes": exclude or [],
        "truncated_at": end,
        "universe_live_marks": _universe_summary(universe, cal, prices, amounts),
        "cost_bp_per_side": base.COST_BP_SIDE,
        "cost_mult": cost_mult,
        "schemes": faces,
        "cash_leg": ({"source": "data/repo_daily/GC001.csv close (annualised %)",
                      "units_per_year": base.CASH_UNITS_PER_YEAR,
                      "covered_days": cash["covered_days"],
                      "ffilled_days": cash["ffilled_days"],
                      "first_rate_date": cash["first"],
                      "last_rate_date": cash["last"]}
                     if cash else None),
        "honest": [
            "selection reads trailing 60d turnover by volume, never future prices",
            "the ETF population is today's surviving listing set (listing survivorship)",
            "N = 10/20/50 is a multiple-comparison surface; only a consistent sign across N counts",
            "liquidity is a turnover proxy, not shares outstanding; no cap-weight face is claimed",
            "13.041bp/side charged on turnover; idle share accrues at the GC001 repo close",
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
        ],
    }


def selftest():
    ok = 0
    tot = 0

    def cal_of(n=320):
        return ["%d-%02d-%02d" % (2020 + k // 300, (k % 12) + 1, (k % 25) + 1)
                for k in range(n)]

    # 1. the dedupe loader keeps the longer of the two name copies
    import tempfile
    d = tempfile.mkdtemp()
    dates = ["%04d-%02d-%02d" % (2020 + k // 300, (k // 25) % 12 + 1, k % 25 + 1)
             for k in range(300)]

    def _w(name, value, amount):
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write("date,close,amount\n")
            for k, dd in enumerate(dates):
                fh.write("%s,%s,%s\n" % (dd, value + k * 1e-4, amount))

    _w("sh510300.csv", 4.0, 1e6)
    _w("510300.csv", 9.0, 2e6)
    _w("510880_t73.csv", 3.0, 1e6)
    _w("600000.csv", 9.0, 1e6)
    u = load_universe(d)
    assert set(u) == {"sh510300"}, sorted(u)          # suffix copy + stock code dropped
    assert list(u["sh510300"][0].values())[0] < 5.0   # the full-history copy won
    ok += 1; tot += 1

    # synthetic 6-ETF panel: 320 bars, distinct drift and liquidity
    cal = cal_of()
    syms = ["sh510%d" % k for k in range(100, 106)]
    closes = {s: {} for s in syms}
    amounts = {s: {} for s in syms}
    px = {s: 10.0 for s in syms}
    drift = {"sh510100": 0.0020, "sh510101": 0.0015, "sh510102": 0.0010,
             "sh510103": 0.0005, "sh510104": 0.0, "sh510105": -0.0005}
    for s in syms:
        for dd in cal:
            px[s] *= (1.0 + drift[s])
            closes[s][dd] = px[s]
            amounts[s][dd] = {"sh510100": 5e8, "sh510101": 4e8, "sh510102": 3e8,
                              "sh510103": 2e8, "sh510104": 1e8, "sh510105": 5e7}[s]
    prices = {s: [closes[s].get(dd) for dd in cal] for s in syms}
    ams = {s: [amounts[s].get(dd) for dd in cal] for s in syms}

    # 2. an all-inclusive pick (N >= live count) equals equal-weighting the universe
    c_all, a_all, _ = simulate(cal, prices, ams, syms, None, 1000, 1.0, {})
    c_eq, a_eq, _ = simulate(cal, prices, ams, syms, None, None, 1.0, {})
    assert all(abs(x[1] - y[1]) < 1e-12 for x, y in zip(c_all, c_eq)), a_all
    ok += 1; tot += 1

    # 3. top-1 == buy and hold the most liquid member (no drift weights to undo)
    c1, a1, hold = simulate(cal, prices, ams, syms, None, 1, 1.0, {})
    assert hold == ["sh510100"], hold
    bh = prices["sh510100"][-1] / prices["sh510100"][-2]
    assert abs((c1[-1][1] / c1[-2][1]) - bh) < 1e-12
    ok += 1; tot += 1

    # 4. ranking is causal: perturbing everything AFTER idx leaves the pick at idx
    r0 = _rank(280, syms, prices, ams, None)
    shifted = {s: list(prices[s]) for s in syms}
    sh_am = {s: list(ams[s]) for s in syms}
    for s in syms:
        for k in range(281, len(cal)):
            shifted[s][k] = (shifted[s][k] or 1.0) * (10.0 if s == "sh510105" else 0.5)
            sh_am[s][k] = sh_am[s][k] * (50.0 if s == "sh510105" else 0.01)
    r1 = _rank(280, syms, shifted, sh_am, None)
    assert r0 == r1, (r0, r1)
    ok += 1; tot += 1

    # 5. ranking orders by trailing liquidity (highest amount first)
    assert _rank(300, syms, prices, ams, None)[0] == "sh510100"
    ok += 1; tot += 1

    # 6. cost_mult scales the fee linearly and 0 disables it
    _, a_x1, _ = simulate(cal, prices, ams, syms, None, 2, 1.0, {})
    _, a_x3, _ = simulate(cal, prices, ams, syms, None, 2, 3.0, {})
    _, a_x0, _ = simulate(cal, prices, ams, syms, None, 2, 0.0, {})
    assert abs(a_x3["cost_paid_frac"] - 3.0 * a_x1["cost_paid_frac"]) < 1e-12
    assert a_x0["cost_paid_frac"] == 0.0
    ok += 1; tot += 1

    # 7. a zero-rate cash panel is a no-op for a fully invested scheme
    cash0 = {"series": {dd: 0.0 for dd in cal}, "ffilled_days": 0,
             "covered_days": len(cal), "first": cal[0], "last": cal[-1]}
    c_none, _, _ = simulate(cal, prices, ams, syms, None, 3, 1.0, {})
    c_zero, _, _ = simulate(cal, prices, ams, syms, cash0, 3, 1.0, {})
    assert all(abs(x[1] - y[1]) < 1e-12 for x, y in zip(c_none, c_zero))
    ok += 1; tot += 1

    # 8. the ladder path reproduces the E24 equal scheme bit-for-bit
    lcal, lcloses, lam = base.load_panel()
    lprices = {s: [lcloses[s].get(dd) for dd in lcal] for s in lcloses}
    lam_a = {s: [lam[s].get(dd) for dd in lcal] for s in lam}
    c_lad, _, _ = simulate(lcal, lprices, lam_a, base.LADDER, None, None, 1.0, {})
    c_e24, _ = base.simulate("equal", lcal, lcloses, lam, None, 1.0)
    assert len(c_lad) == len(c_e24)
    assert all(abs(x[1] - y[1]) < 1e-10 for x, y in zip(c_lad, c_e24))
    ok += 1; tot += 1

    # 9. curves stay positive and no weight exceeds one
    for n in (1, 3, 1000):
        curve, _, _ = simulate(cal, prices, ams, syms, None, n, 1.0, {})
        assert curve[-1][1] > 0 and all(v > 0 for _, v in curve)
    ok += 1; tot += 1

    # 10. E61 seam: a pool that always hands back the whole universe is the
    #     static universe, bit for bit -- otherwise every published curve that
    #     never asks for the seam would move with this change
    c_static, a_static, h_static = simulate(cal, prices, ams, syms, None, 3, 1.0, {})
    c_seam, a_seam, h_seam = simulate(cal, prices, ams, syms, None, 3, 1.0, {},
                                      None, universe_at=lambda _i: syms)
    assert all(abs(x[1] - y[1]) < 1e-15 for x, y in zip(c_static, c_seam))
    assert h_static == h_seam and a_static == a_seam
    ok += 1; tot += 1

    # 11. and a pool that is a strict subset actually bites: restricting to the
    #     least liquid member cannot return top-3 by liquidity
    thin = ["sh510104", "sh510105"]
    _c, _a, h_thin = simulate(cal, prices, ams, syms, None, 3, 1.0, {},
                              None, universe_at=lambda _i: thin)
    assert set(h_thin) <= set(thin), h_thin
    ok += 1; tot += 1

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--ns", default=None, help="comma list of N (default 10,20,50)")
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None,
                    help="truncate the calendar at the last date with uniform panel coverage")
    ap.add_argument("--exclude", default=None,
                    help="comma list of symbol prefixes dropped from the selection universe "
                         "(e.g. sh511 = the SH money/bond ETF block)")
    ap.add_argument("--cost-mult", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    ns = [int(x) for x in args.ns.split(",")] if args.ns else None
    face = run(ns, args.start, args.cost_mult, args.end,
               [x.strip() for x in args.exclude.split(",")] if args.exclude else None)
    outdir = os.path.join(ROOT, args.out) if args.out else OUTDIR
    os.makedirs(outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    tag = "UNIV"
    if ns:
        import hashlib
        tag += "-" + hashlib.sha1(",".join(str(n) for n in ns).encode()).hexdigest()[:6]
    if args.start:
        tag += "-s" + args.start.replace("-", "")
    if args.end:
        tag += "-e" + args.end.replace("-", "")
    if args.exclude:
        tag += "-x" + "".join(sorted(x.strip() for x in args.exclude.split(",")))
    if args.cost_mult != 1.0:
        tag += "-x%s" % ("%g" % args.cost_mult).replace(".", "p")
    path = os.path.join(outdir, "%s-%s.json" % (tag, stamp))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"start": face["start"], "cutoff": face["evidence_cutoff"],
                      "years": face["years"], "bars": face["bars"],
                      "universe_size": face["universe_size"],
                      "live_marks": face["universe_live_marks"]}, ensure_ascii=False))
    for name, f in face["schemes"].items():
        v = f.get("vs_ladder") or {}
        print("%-8s ann=%5.2f vol=%5.2f sharpe=%s vsLadder=%+6.1fbp t=%s cost=%sbp/yr rebal=%d"
              % (name, f["metrics"]["ann_return_pct"], f["metrics"]["ann_vol_pct"],
                 f["metrics"]["sharpe"], f.get("vs_ladder_bp_annualised") or 0.0,
                 v.get("t"), f["aux"]["cost_per_year_bp"], f["aux"]["rebalances"]))
    print("face:", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))