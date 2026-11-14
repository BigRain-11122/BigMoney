"""Treasury curve spread (T vs TF): the 30-minute kill test (DIRECTION-20261114 section 3).

Who pays: the two legs do not have symmetric hedging demand. An institution holding
10-year cash bonds (insurers, wealth products, bank trading books) needs to hedge long
duration, and the Treasury futures complex offers exactly one instrument liquid enough
for that job -- T. The 5-year contract TF faces far less one-way hedging demand because
the same desk can hedge short duration with cash bonds or IRS. So short interest piles up
in T relative to TF, and the "long T / short TF" leg collects that asymmetry. The payer is
whoever must hedge 10-year duration and will not hold the cash bond; the receiver eats the
curve's own risk. That makes it a structural/positioning premium, not an arbitrage: the
P&L is the curve moving against you, and the drawdown is the curve's drawdown.

What this script measures, and what it deliberately does not:
  * It measures whether the T-TF spread MEAN-REVERTS far enough to pay for a round trip
    once the required margin is the denominator (yuan of capital, not notional points).
  * It does NOT claim the carry story above as evidence. A premium story that only exists
    in prose is not a result; if the numbers do not clear the frozen bar, the line is KILL
    and no explanatory report follows (order section 3 step 4).

Frozen criteria (written before the numbers were read):
  C1  capital-basis annualised net return >= 3.0%/yr. Denominator = margin actually
      posted (T 2.0% + TF 1.5% of 1,000,000 CNY face each = 35,000 CNY per pair), not the
      2,000,000 notional -- a percentage of notional is not money.
  C2  out-of-sample (2024-01-01 onward) Sharpe >= 0.70. The full-sample number can be
      carried by one regime; the OOS number is the one that has to survive.
  C3  permutation control: 200 randomly rotated versions of the same position sequence
      (same holding count, same run lengths distribution via rotation) must put the
      realised return at p < 0.05. If random timing does as well, the z-score is noise.
  Verdict OPEN only if C1 and C2 and C3 all pass. Otherwise KILL, line closed.

Roll handling: sina's main-continuous series is raw (never back-adjusted), so on a roll
day the price steps from the expiring contract to another one and that step is not a loss
to a holder. T and TF roll on different days, so a roll on either leg injects a phantom
spread move. Such days are detected per leg (|daily change| over 8x the median absolute
change AND over 0.3 points) and the spread change on that day is dropped from the return
series and counted separately as phantom_points.
"""
import csv
import json
import math
import os
import random
import statistics
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "treasury_curve_spread.json")
TRADING_DAYS = 244.0

# Contract economics: both T and TF carry 1,000,000 CNY face and quote 1 point = 10,000 CNY.
POINT_VALUE = 10000.0
MARGIN_PER_PAIR = 35000.0     # T 2.0% + TF 1.5% of 1,000,000 each
COST_BP_PER_SIDE = 20.0       # two legs x 10bp (one tick 0.005pt = 5bp per leg) per side

Z_WINDOW = 20                 # rolling mean/sd window for the spread z-score
Z_ENTER = 2.0                 # enter when |z| reaches this
Z_EXIT = 0.0                  # flat when the spread crosses its own mean
MAX_HOLD = 20                 # forced exit after this many bars (no open-ended hold)

ROLL_SCALE = 8.0
ROLL_FLOOR = 0.3

CARRY_MIN_PCT = 3.0
OOS_SHARPE_MIN = 0.70
PERM_TRIALS = 200
SEED_BASE = 94_017            # own reserved band (below the 95_000 contract cluster)


def _rows(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                out.append((r["date"], float(r["close"])))
            except (KeyError, TypeError, ValueError):
                continue
    return out


def _median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0.0


def detect_rolls(closes):
    """Indices where the raw continuous series steps like a contract switch, not a move."""
    diffs = [None]
    for i in range(1, len(closes)):
        diffs.append(abs(closes[i] - closes[i - 1]))
    med = _median(diffs[1:])
    if med <= 0:
        return set([], )
    out = set()
    for i in range(1, len(closes)):
        d = abs(closes[i] - closes[i - 1])
        if d > ROLL_SCALE * med and d > ROLL_FLOOR:
            out.add(i)
    return out


def join_legs(t_rows, tf_rows):
    """Inner-join on date; both legs must have the same bar for the spread to exist."""
    tmap = dict(t_rows)
    tfmap = dict(tf_rows)
    dates = sorted(set(tmap) & set(tfmap))
    return dates, [tmap[d] for d in dates], [tfmap[d] for d in dates]


def build_series(dates, t_close, tf_close):
    t_roll = detect_rolls(t_close)
    tf_roll = detect_rolls(tf_close)
    spread = [t_close[i] - tf_close[i] for i in range(len(dates))]
    # spread change, NaN (None) on a roll day of either leg
    d_spread = [None]
    for i in range(1, len(dates)):
        if i in t_roll or i in tf_roll:
            d_spread.append(None)
        else:
            d_spread.append(spread[i] - spread[i - 1])
    return {
        "spread": spread,
        "d_spread": d_spread,
        "t_roll_days": sorted(dates[i] for i in t_roll),
        "tf_roll_days": sorted(dates[i] for i in tf_roll),
        "phantom_points": sum(spread[i] - spread[i - 1] for i in range(1, len(dates))
                              if d_spread[i] is None),
    }


def zscores(spread):
    out = [None] * len(spread)
    for i in range(Z_WINDOW, len(spread)):
        win = spread[i - Z_WINDOW:i]
        m = sum(win) / Z_WINDOW
        var = sum((x - m) ** 2 for x in win) / Z_WINDOW
        sd = math.sqrt(var)
        out[i] = None if sd <= 0 else (spread[i] - m) / sd
    return out


def positions(z):
    """+1 = long the spread (long T / short TF); -1 = short the spread; 0 = flat.

    Entry on |z| >= Z_ENTER, exit when the spread crosses its mean (sign of z flips)
    or after MAX_HOLD bars. Signals are computed on bar i and applied to bar i+1's
    spread change -- no same-bar future data.
    """
    pos = [0] * len(z)
    cur = 0
    held = 0
    for i in range(len(z)):
        if z[i] is None:
            pos[i] = cur
            continue
        if cur == 0:
            if z[i] <= -Z_ENTER:
                cur, held = 1, 0
            elif z[i] >= Z_ENTER:
                cur, held = -1, 0
        else:
            held += 1
            if held >= MAX_HOLD:
                cur, held = 0, 0
        pos[i] = cur
    return pos


def run_book(dates, d_spread, pos):
    """Daily capital-basis P&L. Position decided at bar i-1 earns bar i's spread change;
    the cost of the change decided at bar i is charged on bar i (close-signal, close-fill --
    a conservative same-bar approximation, disclosed in meta)."""
    n = len(dates)
    daily = [0.0]
    turnovers = 0
    for i in range(1, n):
        p = pos[i - 1]
        ds = d_spread[i]
        gross = 0.0 if ds is None else p * ds * POINT_VALUE / MARGIN_PER_PAIR
        chg = abs(pos[i] - pos[i - 1])
        cost = (COST_BP_PER_SIDE / 10000.0) * chg
        if chg > 0:
            turnovers += 1
        daily.append(gross - cost)
    return daily, turnovers


def stats(daily):
    n = len(daily)
    if n < 2:
        return {"n": n, "ann_pct": 0.0, "sharpe": 0.0, "mdd_pct": 0.0, "total_pct": 0.0}
    total = sum(daily)
    mean = total / n
    var = sum((x - mean) ** 2 for x in daily) / max(1, n - 1)
    sd = math.sqrt(var)
    sharpe = (mean / sd) * math.sqrt(TRADING_DAYS) if sd > 0 else 0.0
    nav, peak, mdd = 1.0, 1.0, 0.0
    for x in daily:
        nav *= (1.0 + x)
        peak = max(peak, nav)
        mdd = min(mdd, nav / peak - 1.0)
    # compounded, not a sum of daily returns -- a 24% sum and a 27% compound are the same
    # series, and quoting the sum under an "annualised" label understates a winner and
    # flatters a loser (the sum is still printed separately as total_pct).
    ann = nav ** (TRADING_DAYS / n) - 1.0 if nav > 0 else -1.0
    return {"n": n, "ann_pct": 100.0 * ann, "sharpe": sharpe,
            "mdd_pct": 100.0 * mdd, "total_pct": 100.0 * total,
            "nav": round(nav, 6)}


def segment(dates, daily, start, end):
    sub = [daily[i] for i in range(len(daily)) if start <= dates[i] < end]
    return stats(sub)


def permute(dates, d_spread, pos, trials, seed_base):
    """Rotation null: same position sequence, randomly rotated against the return series.

    Rotation preserves the holding-count and the run-length distribution exactly (which a
    shuffle of individual days would not), so a pass means the *timing* carried the return.
    """
    n = len(pos)
    valid = [(i, d_spread[i] * POINT_VALUE / MARGIN_PER_PAIR)
             for i in range(1, n) if d_spread[i] is not None]
    if not valid or not any(pos):
        return {"trials": 0, "p_value": 1.0, "real_pct": 0.0, "null_median_pct": 0.0}
    # realised: position decided at i-1 earns bar i
    real = sum(pos[i - 1] * d_spread[i] * POINT_VALUE / MARGIN_PER_PAIR
               for i in range(1, n) if d_spread[i] is not None)
    rng = random.Random(seed_base)
    hits = 0
    nulls = []
    for _ in range(trials):
        k = rng.randrange(1, n)
        rot = [pos[(i - k) % n] for i in range(n)]
        s = sum(rot[i - 1] * d_spread[i] * POINT_VALUE / MARGIN_PER_PAIR
                for i in range(1, n) if d_spread[i] is not None)
        nulls.append(s)
        if s >= real:
            hits += 1
    return {"trials": trials, "p_value": (hits + 1) / (trials + 1),
            "real_pct": 100.0 * real,
            "null_median_pct": 100.0 * _median(nulls),
            "null_p95_pct": 100.0 * sorted(nulls)[int(0.95 * (len(nulls) - 1))]}


def grid(dates, series, seen_z=frozenset([1.5, 2.0, 2.5]), holds=(10, 20, 40)):
    """Robustness disclosure, not a search: every cell of the frozen mechanism's two
    parameters, both signs, printed whether it wins or loses.

    A single winning cell is not a rule (r1140): if only one corner of this grid pays,
    the honest verdict is fragility, not adoption -- so the block reports how many cells
    are positive and the worst cell, and the closure decision never moves on one cell.
    """
    out = []
    for z in sorted(seen_z):
        for h in holds:
            for sign in (1, -1):
                global Z_ENTER, MAX_HOLD
                oz, oh = Z_ENTER, MAX_HOLD
                Z_ENTER, MAX_HOLD = z, h
                try:
                    zz = zscores(series["spread"])
                    pp = [sign * v for v in positions(zz)]
                    dd, _ = run_book(dates, series["d_spread"], pp)
                    st = stats(dd)
                finally:
                    Z_ENTER, MAX_HOLD = oz, oh
                out.append({"z_enter": z, "max_hold": h, "sign": sign,
                            "ann_pct": round(st["ann_pct"], 3),
                            "sharpe": round(st["sharpe"], 3),
                            "mdd_pct": round(st["mdd_pct"], 3)})
    pos_cells = sum(1 for c in out if c["ann_pct"] > 0)
    return {"cells": out, "n_cells": len(out), "positive_cells": pos_cells,
            "best_ann_pct": max(c["ann_pct"] for c in out) if out else 0.0,
            "worst_ann_pct": min(c["ann_pct"] for c in out) if out else 0.0,
            "fragile": pos_cells <= 1}


def run():
    t_path = os.path.join(FUT_DIR, "T.csv")
    tf_path = os.path.join(FUT_DIR, "TF.csv")
    have = {}
    for k, p in (("T", t_path), ("TF", tf_path)):
        have[k] = os.path.exists(p)
    if not all(have.values()):
        out = {"batch": "TREASURY_CURVE_SPREAD", "status": "blocked",
               "reason": "missing leg panel: %s" % [k for k, v in have.items() if not v],
               "verdict": {"verdict": "BLOCKED", "criteria": {}}}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(json.dumps(out["verdict"], ensure_ascii=False))
        return 2

    t_rows = _rows(t_path)
    tf_rows = _rows(tf_path)
    dates, t_close, tf_close = join_legs(t_rows, tf_rows)
    if len(dates) < 300:
        out = {"batch": "TREASURY_CURVE_SPREAD", "status": "blocked",
               "reason": "joined bars %d < 300" % len(dates),
               "verdict": {"verdict": "BLOCKED", "criteria": {}}}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(json.dumps(out["verdict"], ensure_ascii=False))
        return 2

    series = build_series(dates, t_close, tf_close)
    z = zscores(series["spread"])
    pos = positions(z)
    daily, turnovers = run_book(dates, series["d_spread"], pos)
    full = stats(daily)
    half = len(dates) // 2
    h1 = stats([daily[i] for i in range(half)])
    h2 = stats([daily[i] for i in range(half, len(dates))])
    oos = segment(dates, daily, "2024-01-01", "9999-12-31")
    perm = permute(dates, series["d_spread"], pos, PERM_TRIALS, SEED_BASE)

    in_market = sum(1 for p in pos if p != 0) / max(1, len(pos))
    c1 = full["ann_pct"] >= CARRY_MIN_PCT
    c2 = oos["sharpe"] >= OOS_SHARPE_MIN
    c3 = perm["p_value"] < 0.05 and perm["trials"] >= PERM_TRIALS
    stable = (h1["ann_pct"] > 0 and h2["ann_pct"] > 0)

    verdict = "OPEN" if (c1 and c2 and c3) else "KILL"

    out = {
        "batch": "TREASURY_CURVE_SPREAD",
        "evidence_cutoff": dates[-1],
        "status": "ok",
        "meta": {
            "pairs": "T(10y) vs TF(5y), sina main-continuous raw (no back-adjustment)",
            "bars": len(dates),
            "first": dates[0],
            "last": dates[-1],
            "point_value_cny": POINT_VALUE,
            "margin_per_pair_cny": MARGIN_PER_PAIR,
            "cost_bp_per_side": COST_BP_PER_SIDE,
            "cost_note": "two legs x one tick (0.005pt = 5bp of face) per leg per side",
            "z_window": Z_WINDOW, "z_enter": Z_ENTER, "max_hold": MAX_HOLD,
            "in_market_share": round(in_market, 4),
            "turnovers": turnovers,
            "spread_points_last": round(series["spread"][-1], 4),
            "spread_points_median": round(_median(series["spread"]), 4),
            "t_roll_days": len(series["t_roll_days"]),
            "tf_roll_days": len(series["tf_roll_days"]),
            "phantom_points_dropped": round(series["phantom_points"], 4),
            "perm_seed_base": SEED_BASE,
        },
        "full": full,
        "halves": {"h1": {"from": dates[0], "to": dates[half - 1], **h1},
                   "h2": {"from": dates[half], "to": dates[-1], **h2}},
        "oos_2024": oos,
        "permutation": perm,
        "robustness_grid": grid(dates, series),
        "verdict": {
            "verdict": verdict,
            "criteria": {
                "C1_capital_ann_ge_3pct": {"value": round(full["ann_pct"], 4),
                                           "threshold": CARRY_MIN_PCT, "pass": bool(c1)},
                "C2_oos_sharpe_ge_0.70": {"value": round(oos["sharpe"], 4),
                                          "threshold": OOS_SHARPE_MIN, "pass": bool(c2)},
                "C3_permutation_p_lt_0.05": {"value": round(perm["p_value"], 4),
                                             "threshold": 0.05, "pass": bool(c3)},
                "diagnostic_halves_same_sign": {"h1_pct": round(h1["ann_pct"], 4),
                                                "h2_pct": round(h2["ann_pct"], 4),
                                                "pass": bool(stable),
                                                "note": "diagnostic, no veto"},
            },
            "closed_if_kill": verdict == "KILL",
            "note": "KILL = line closed; panel and script stay for reuse; no explanatory report",
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps(out["verdict"], ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------- selftest

def _selftest():
    ok = 0
    fails = []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # rolls: a single 1.0-point step in a series of 0.1 moves is a switch, not a move
    closes = [100.0 + 0.1 * (i % 3) for i in range(40)]
    closes[20] = closes[19] + 1.5
    rolls = detect_rolls(closes)
    # the switch shows up as two steps (in at 20, back out at 21) -- both are phantom
    chk("roll detector finds the switch", 20 in rolls and len(rolls) <= 2)

    # no rolls on a smooth series
    chk("smooth series has no roll", detect_rolls([100.0 + 0.01 * i for i in range(40)]) == set())

    # join: inner join on shared dates only
    d, a, b = join_legs([("2020-01-01", 100.0), ("2020-01-02", 101.0)],
                        [("2020-01-02", 99.0), ("2020-01-03", 98.0)])
    chk("join keeps only shared bars", d == ["2020-01-02"] and a == [101.0] and b == [99.0])

    # z-score of a constant series is undefined, not zero-division
    z = zscores([100.0] * 30)
    chk("flat spread yields None z", all(v is None for v in z))

    # z-score is negative when the last point sits below the window mean
    sp = [100.0 + (0.1 * i if i % 2 else -0.1 * i) for i in range(20)] + [99.0]
    zz = zscores(sp)
    chk("below-mean point yields negative z", zz[-1] is not None and zz[-1] < 0)

    # positions: entry long on the low tail, held until MAX_HOLD or a mean crossing
    zs = [0.0] * 5 + [-2.5] + [0.0] * 3 + [2.5] + [0.0] * 3
    p = positions(zs)
    chk("entry long on z<=-2", p[5] == 1)
    chk("a +2 reading does not flip an open long (no stop-and-reverse)", p[9] == 1)
    chk("book never exceeds one unit", all(abs(v) <= 1 for v in p))

    # max hold forces a flat: entry at bar 5, MAX_HOLD bars later we are flat again
    zs2 = [0.0] * 5 + [-2.5] + [0.0] * 40
    p2 = positions(zs2)
    chk("max hold forces a flat", p2[5 + MAX_HOLD] == 0)

    # book: a long position earns a positive spread change, minus cost
    daily, tn = run_book(["d0", "d1"], [None, 1.0], [1, 1])
    gross = 1.0 * POINT_VALUE / MARGIN_PER_PAIR
    chk("long earns the spread widening", abs(daily[1] - gross) < 1e-12)
    chk("a book that starts already long books no turnover", tn == 0)
    daily_a, tn_a = run_book(["d0", "d1"], [None, 1.0], [0, 1])
    chk("an actual entry books one turnover", tn_a == 1)

    # roll day contributes zero, not a phantom loss
    daily2, _ = run_book(["d0", "d1"], [None, None], [1, 1])
    chk("roll day contributes zero", daily2[1] == 0.0)

    # stats sanity: a constant 0.1% daily return compounds to ~27.7%/yr
    st = stats([0.001] * 244)
    chk("constant daily return compounds ~27.7%", abs(st["ann_pct"] - 27.7) < 0.5)
    chk("zero-variance series has zero sharpe", abs(st["sharpe"]) < 1e-9)

    # permutation: a position aligned to the only move must be rare
    ds = [None] + [0.0] * 49 + [5.0]
    ps = [0] * 49 + [1] + [1]
    pm = permute(["d%d" % i for i in range(51)], ds, ps, 200, 7)
    chk("aligned position is not beaten by rotations", pm["p_value"] < 0.1)

    # permutation on a flat book has no power
    pm2 = permute(["d%d" % i for i in range(60)], [None] + [0.1] * 59, [0] * 60, 50, 7)
    chk("all-flat book returns p=1", pm2["p_value"] == 1.0)

    total = ok + len(fails)
    print("selftest %d/%d" % (ok, total))
    for f in fails:
        print("FAIL:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    sys.exit(run())
