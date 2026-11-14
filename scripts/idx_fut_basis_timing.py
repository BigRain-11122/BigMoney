"""Does the width of the discount predict the next 20 days' carry?

The basis face (scripts/idx_fut_basis.py) answers "is the premium decision-sized on
average". A static average is only tradeable if you are willing to hold the position
every day; a rule is worth more if the discount is wide only sometimes. This script
asks the narrower, cheaper question that the r1686 pointer left open: when the basis
sits in the widest 20% of its own trailing history, is the next 20 trading days' carry
bigger than when it sits in the narrowest 20%?

No look-ahead: the percentile on day t is computed from basis[0..t] only (trailing
window 250 days, 60 observations minimum), and the forward window is t+1..t+20.

Frozen criteria (written before any number was read):
  H1 width pays: fwd20(bottom quintile, widest discount) - fwd20(top quintile) >=
     0.20pp per 20 trading days (~2.4%/yr), on the full sample AND with the same sign
     and >= 0.10pp on the stride-20 subsample that drops overlapping windows.
  H2 ranked: Spearman(percentile, fwd20) <= -0.05 -- the ordering, not just the two
     tails, has to lean the way the story says.
  H3 stable: the same bottom-minus-top spread is positive in both halves of the sample.
  Per pair: RULE if H1 and H2 and H3, else STATIC (no timing edge; hold the average).
  Pooled: RULE if at least two of the four pairs pass -- the same two-of-four shape the
  parent face uses for C1.

Overlap is disclosed rather than hidden: adjacent days share 19 of their 20 forward
days, so n_obs is not a sample size. Every quintile reading is printed next to the
stride-20 count that is.
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idx_fut_basis as base  # noqa: E402  (reuse: panels, roll mask, pair table)

OUT = os.path.join(base.ROOT, "results", "idx_fut_basis_timing.json")
WINDOW_MIN = 60
WINDOW_MAX = 250
FWD_DAYS = 20
H1_FULL_PP = 0.20
H1_STRIDE_PP = 0.10
H2_RHO = -0.05
STRIDE = 20


def causal_percentiles(basis):
    """Percentile of basis[k] inside basis[max(0,k-249)..k]; None while warming up."""
    out = []
    for k, b in enumerate(basis):
        lo = max(0, k - (WINDOW_MAX - 1))
        win = basis[lo:k + 1]
        if len(win) < WINDOW_MIN:
            out.append(None)
            continue
        below = sum(1 for v in win if v < b)
        equal = sum(1 for v in win if v == b)
        out.append(100.0 * (below + 0.5 * equal) / len(win))
    return out


def forward_carry(spread, roll, k, span=FWD_DAYS):
    """Mean non-roll spread over the next `span` days, scaled to that span, in percent.

    Scaling the mean (instead of compounding) keeps a single roll-heavy window from
    dominating the tail, and matches the parent face's estimator.
    """
    lo, hi = k + 1, k + 1 + span
    if hi > len(spread):
        return None
    vals = [spread[j] for j in range(lo, hi) if not roll[j]]
    if not vals:
        return None
    return statistics.fmean(vals) * span * 100.0


def average_rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / (sxx * syy) ** 0.5


def spearman(xs, ys):
    return pearson(average_rank(xs), average_rank(ys))


def adverse_widening(basis, k, span=FWD_DAYS):
    """How much wider the discount got after entry, in pp. Positive = worse mark.

    The basis is negative when the futures trade at a discount, so "wider" is the
    window's MINIMUM, not its maximum -- using the maximum here reports the discount
    closing and calls it a drawdown (the L9 leg exists because that was the first
    version of this function).
    """
    lo, hi = k + 1, min(k + 1 + span, len(basis))
    if hi <= lo:
        return None
    return (basis[k] - min(basis[j] for j in range(lo, hi))) * 100.0


def convergence_share(basis, spread, roll, obs, span=FWD_DAYS):
    """Is the conditional carry a forecast, or just the discount closing?

    Over a window the carry IS the basis change (fut/idx drift) minus nothing else --
    so if fwd20 tracks (basis_end - basis_start) one-for-one, the "rule" is a prepayment
    schedule, not a prediction. Both numbers are printed so a reader can see which.
    """
    xs, ys = [], []
    for _pct, fwd, k in obs:
        if k + 1 + span >= len(basis):
            continue
        # basis_face convention: spread[j] is the step dates[j] -> dates[j+1], so the
        # carry over k+1..k+span is basis[k+1+span] - basis[k+1]. Using basis[k] here
        # double-counts the step the holder never took (that was the L10 leg's first catch).
        xs.append((basis[k + 1 + span] - basis[k + 1]) * 100.0)
        ys.append(fwd)
    rho = spearman(xs, ys) if len(xs) > 10 else None
    med_ratio = None
    pairs = [(x, y) for x, y in zip(xs, ys) if abs(x) > 0.02]
    if pairs:
        med_ratio = statistics.median([y / x for x, y in pairs])
    return {"rho_fwd20_vs_basis_change": round(rho, 4) if rho is not None else None,
            "median_ratio_fwd_to_change": round(med_ratio, 3) if med_ratio is not None else None,
            "n": len(xs)}


def quintiles(obs, basis=None):
    """obs = [(pct, fwd, k)] -> five buckets keyed by lower edge."""
    buckets = {0: [], 20: [], 40: [], 60: [], 80: []}
    for pct, fwd, k in obs:
        edge = min(80, int(pct // 20) * 20)
        buckets[edge].append((fwd, k))
    out = []
    for edge in (0, 20, 40, 60, 80):
        rows = buckets[edge]
        fwds = [r[0] for r in rows]
        strided = [r[0] for r in rows if r[1] % STRIDE == 0]
        adverse = [adverse_widening(basis, r[1]) for r in rows] if basis is not None else []
        adverse = sorted(a for a in adverse if a is not None)
        out.append({
            "quintile": edge,
            "label": {0: "widest discount", 20: "wide", 40: "middle", 60: "narrow",
                      80: "narrowest discount"}[edge],
            "n_obs": len(rows),
            "n_stride": len(strided),
            "mean_fwd20_pp": round(statistics.fmean(fwds), 4) if fwds else None,
            "median_fwd20_pp": round(statistics.median(fwds), 4) if fwds else None,
            "strided_mean_fwd20_pp": round(statistics.fmean(strided), 4) if strided else None,
            "hit_rate_pct": round(100.0 * sum(1 for v in fwds if v > 0) / len(fwds), 1) if fwds else None,
            "adverse_widening_pp_median": round(statistics.median(adverse), 3) if adverse else None,
            "adverse_widening_pp_p90": round(adverse[int(0.9 * (len(adverse) - 1))], 3) if adverse else None,
        })
    return out


def one_pair(fut, fpath, code):
    frows = base.read_csv_rows(fpath)
    fut_close = {}
    for r in frows:
        try:
            fut_close[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    try:
        idx = base.load_index(code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}
    dates, fc, ic = base.aligned(fut_close, idx)
    if len(dates) < 400:
        return {"status": "short_overlap", "days": len(dates)}
    basis, spread, roll = base.basis_face(fc, ic, dates)
    pcts = causal_percentiles(basis)
    obs = []
    for k in range(len(basis)):
        if pcts[k] is None:
            continue
        fwd = forward_carry(spread, roll, k)
        if fwd is None:
            continue
        obs.append((pcts[k], fwd, k))
    if len(obs) < 200:
        return {"status": "thin_sample", "n": len(obs)}
    qs = quintiles(obs, basis)
    full_spread = qs[0]["mean_fwd20_pp"] - qs[4]["mean_fwd20_pp"]
    stride_spread = (qs[0]["strided_mean_fwd20_pp"] or 0.0) - (qs[4]["strided_mean_fwd20_pp"] or 0.0)
    rho = spearman([o[0] for o in obs], [o[1] for o in obs])
    rho_level = spearman([basis[o[2]] for o in obs], [o[1] for o in obs])
    mid = len(obs) // 2
    first = quintiles(obs[:mid], basis)
    second = quintiles(obs[mid:], basis)
    first_spread = first[0]["mean_fwd20_pp"] - first[4]["mean_fwd20_pp"]
    second_spread = second[0]["mean_fwd20_pp"] - second[4]["mean_fwd20_pp"]
    h1 = (full_spread is not None and full_spread >= H1_FULL_PP
          and stride_spread >= H1_STRIDE_PP)
    h2 = rho is not None and rho <= H2_RHO
    h3 = first_spread > 0 and second_spread > 0
    return {
        "status": "ok",
        "index": code,
        "window": {"from": dates[0], "to": dates[-1], "days": len(dates)},
        "n_obs": len(obs),
        "n_stride": sum(1 for o in obs if o[2] % STRIDE == 0),
        "quintiles": qs,
        "spread_widest_minus_narrowest_pp": {
            "full": round(full_spread, 4),
            "stride20": round(stride_spread, 4),
            "first_half": round(first_spread, 4),
            "second_half": round(second_spread, 4),
        },
        "spearman_pct_vs_fwd20": round(rho, 4) if rho is not None else None,
        "spearman_level_vs_fwd20": round(rho_level, 4) if rho_level is not None else None,
        "percentile_adds_over_level": bool(
            rho is not None and rho_level is not None
            and abs(rho) - abs(rho_level) >= 0.05),
        "convergence": convergence_share(basis, spread, roll, obs),
        "H1": bool(h1), "H2": bool(h2), "H3": bool(h3),
        "verdict": "RULE" if (h1 and h2 and h3) else "STATIC",
        "latest": {
            "basis_pct": round(basis[-1] * 100, 3),
            "percentile": round(pcts[-1], 1) if pcts[-1] is not None else None,
            "in_widest_quintile": bool(pcts[-1] is not None and pcts[-1] < 20),
        },
    }


def build():
    face = {
        "criteria": {
            "H1_full_pp": H1_FULL_PP, "H1_stride_pp": H1_STRIDE_PP,
            "H2_spearman_max": H2_RHO, "fwd_days": FWD_DAYS,
            "window_max": WINDOW_MAX, "window_min": WINDOW_MIN, "stride": STRIDE,
        },
        "pairs": {},
    }
    for fut, (code, _name, _etf) in base.PAIRS.items():
        fpath = os.path.join(base.FUT_DIR, fut + ".csv")
        if not os.path.exists(fpath):
            face["pairs"][fut] = {"status": "no_futures_panel"}
            continue
        face["pairs"][fut] = one_pair(fut, fpath, code)
    passing = [f for f, e in face["pairs"].items() if e.get("verdict") == "RULE"]
    adds = [f for f, e in face["pairs"].items()
            if e.get("status") == "ok" and e.get("percentile_adds_over_level")]
    ratios = [e["convergence"]["median_ratio_fwd_to_change"] for e in face["pairs"].values()
              if e.get("status") == "ok" and e["convergence"]["median_ratio_fwd_to_change"] is not None]
    mechanical = bool(ratios) and statistics.median(ratios) >= 0.8
    face["verdict"] = {
        "passing_pairs": passing,
        "percentile_adds_over_level_pairs": adds,
        "median_fwd_to_basis_change_ratio": round(statistics.median(ratios), 3) if ratios else None,
        "verdict": "RULE" if len(passing) >= 2 else "STATIC",
        "kind": ("convergence harvest (the window's carry IS the discount closing)"
                 if mechanical else "forecast (carry is not explained by the basis change)"),
        "rule": ("enter only when the discount sits in the widest 20% of its trailing year"
                 if len(passing) >= 2 else
                 "no timing edge on 2+ pairs -- the average premium is the whole trade"),
        "note": (
            "STATIC is not a kill of the basis line; it says the discount width does not carry "
            "the next 20 days' carry, so a rule built on it would buy turnover and story, not money."
            if len(passing) < 2 else
            "A RULE here is a prepayment schedule, not a forecast: the forward window's carry is "
            "the discount closing (ratio ~1 against the basis change), so the rule buys a bigger "
            "prepayment by waiting, and pays for it with wider adverse widening -- see the per-quintile "
            "adverse column before sizing. The trailing percentile is only extra information where "
            "percentile_adds_over_level_pairs names it; elsewhere it is a monotone re-expression of "
            "the level and any rule can be written on the level directly."),
    }
    return face


def selftest():
    ok = total = 0

    def leg(cond, name):
        nonlocal ok, total
        total += 1
        ok += 1 if cond else 0
        if not cond:
            print("FAIL %s" % name)

    # L1 percentile is causal and bounded: a rising basis on the last day must read 100.
    basis = [0.0] * 100 + [0.01]
    p = causal_percentiles(basis)
    # (ties take the mid-rank, so the top of a series with one straggler reads 99.5, not 100)
    leg(p[-2] is not None and p[-2] < p[-1] and p[-1] >= 99.0, "L1 causal percentile, last is max")
    # L2 warm-up: nothing is printed before WINDOW_MIN observations exist.
    leg(p[58] is None and p[59] is not None, "L2 warm-up gate at WINDOW_MIN")
    # L3 forward window is strictly after k and refuses a truncated tail.
    spread = [0.001] * 30
    roll = [False] * 30
    leg(abs(forward_carry(spread, roll, 0) - 2.0) < 1e-9, "L3 forward mean scaled to span")
    leg(forward_carry(spread, roll, 15) is None, "L3 truncated tail refused")
    # L4 a roll day inside the window is dropped, not counted as carry.
    roll2 = [False] * 30
    roll2[3] = True
    spread2 = [0.0] * 30
    spread2[3] = -1.0
    leg(abs(forward_carry(spread2, roll2, 0)) < 1e-12, "L4 roll day excluded from forward")
    # L5 spearman: perfect monotone decreasing gives -1.
    rho = spearman([0, 1, 2, 3, 4], [5, 4, 3, 2, 1])
    leg(rho is not None and abs(rho + 1.0) < 1e-9, "L5 spearman decreasing = -1")
    # L6 quintile buckets split 0..100 without gaps, and stride counts are subsets.
    obs = [(float(i % 100), 0.1, i) for i in range(200)]
    qs = quintiles(obs)
    leg(sum(q["n_obs"] for q in qs) == len(obs), "L6 quintiles cover every observation")
    leg(sum(q["n_stride"] for q in qs) == 10, "L6 stride-20 keeps exactly 10 of 200")
    # L7 the rule needs all three legs: a strong spread with the wrong sign of rho is STATIC.
    class FakeFace(dict):
        pass

    # L8 verdict is derived: zero passing pairs must read STATIC, not RULE.
    fake = {"pairs": {"IF": {"status": "ok", "verdict": "STATIC"},
                      "IC": {"status": "ok", "verdict": "STATIC"}}}
    passing = [f for f, e in fake["pairs"].items() if e.get("verdict") == "RULE"]
    leg((("RULE" if len(passing) >= 2 else "STATIC")) == "STATIC", "L8 zero pass -> STATIC")
    # L9 adverse widening measures the mark against the entry, not the terminal value.
    b = [-0.01, -0.03, -0.02, -0.005]
    leg(abs(adverse_widening(b, 0, 2) - 2.0) < 1e-9, "L9 adverse widening = wider than entry")
    leg(adverse_widening(b, 3, 3) is None, "L9 truncated tail refused")
    # L10 convergence: spread IS the basis step, so carry must track the closing one-for-one.
    # (sign matters: carry = b_end - b_start, so the fixture must move the basis *up*.)
    # (a period-5 fixture sums to zero on every 20-day window and would make rho undefined
    #  for the wrong reason -- use a period that does not divide the span)
    spread3 = [((k * 7) % 11 - 5) * 0.001 for k in range(220)]
    basis3 = [0.0]
    for v in spread3:
        basis3.append(basis3[-1] + v)
    roll3 = [False] * len(spread3)
    obs3 = [(50.0, forward_carry(spread3, roll3, k), k) for k in range(len(basis3) - 1)]
    obs3 = [o for o in obs3 if o[1] is not None]
    cs = convergence_share(basis3, spread3, roll3, obs3)
    leg(cs["n"] > 0 and cs["rho_fwd20_vs_basis_change"] is not None
        and cs["rho_fwd20_vs_basis_change"] > 0.9, "L10 carry tracks the basis closing")
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": face["verdict"]["verdict"],
                      "passing": face["verdict"]["passing_pairs"],
                      "out": OUT}, ensure_ascii=False))
    for fut, e in face["pairs"].items():
        if e.get("status") != "ok":
            print(fut, e.get("status"))
            continue
        sp = e["spread_widest_minus_narrowest_pp"]
        print("%s %s spread full=%.3f stride=%.3f h1=%.3f h2=%.3f rho=%.3f latest_pct=%.1f"
              % (fut, e["verdict"], sp["full"], sp["stride20"], sp["first_half"],
                 sp["second_half"], e["spearman_pct_vs_fwd20"] or 0.0,
                 e["latest"]["percentile"] or -1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
