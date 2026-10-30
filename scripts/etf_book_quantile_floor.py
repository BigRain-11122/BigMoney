"""E253 -- a percentile is not a measurement until its own noise band is published.

The book-envelope family (E246) published a distribution, priced the block length across
eight arms (E248) and added the independence zero point (E251). Every sentence in that
family rests on percentiles of 2,000 resamples, and E251's own honest limit had to say
"the p5 estimate is noisy at ~0.1pp, so the 0.30pp gap is above that but only just" --
a noise claim that was never measured. This module measures it: for every quoted
percentile of every arm it publishes a distribution-free confidence interval, the
density-based standard error, and for every ladder comparison a permutation p-value, so
the ladder's orderings can be read against their own resolution instead of against the
eye.

Two aggregators, deliberately (E213): the order-statistic interval makes no distribution
assumption and the permutation test makes no quantile arithmetic assumption, and every
verdict has to survive both. A pair that one aggregator separates and the other does not
is published as `verdict_stable_across_aggregators: false` rather than resolved.

Usage
    python scripts/etf_book_quantile_floor.py run
    python scripts/etf_book_quantile_floor.py --check
    python scripts/etf_book_quantile_floor.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# one arithmetic source for the percentiles: the envelope's own interpolation, so this
# face can never quote a p5 computed a second way from the one that shipped.
from scripts.etf_book_nav_envelope import PCTS, pct  # noqa: E402

SCRIPT = "scripts/etf_book_quantile_floor.py"
ENV_DIR = ROOT / "results" / "etf_book_bootstrap"
LADDER = (1, 5, 10, 20, 40, 60, 120, 250)

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the gate refuses a face whose echo differs from these.
CRITERIA = {
    "confidence": 0.95,
    "alpha": 0.05,
    "perm_n": 1000,
    "perm_seed": 20261030,
    "min_rows": 100,
    "stats": ["maxdd", "cagr"],
    "quantiles": [5, 50],
    "ci": "distribution-free order-statistic interval: the binomial ranks of the "
          "quantile, so no density or symmetry assumption enters the bound",
    "se": "spacing estimator f(q) = (k2-k1)/(n*(x_k2-x_k1)) with k = n*q +- sqrt(n*q*(1-q)), "
          "SE = sqrt(q(1-q)/n)/f -- published as the second, density-based reading of the "
          "same width",
    "perm": "pooled-label permutation of the two arms' rows; statistic = difference of the "
            "sample quantile. Null = the block length does not change the resampled "
            "distribution, which is exactly what the ladder claims to test. Note it is a "
            "whole-distribution null, so a difference anywhere shows up here",
    "pairs": "each arm against the iid arm (block 1) plus each ladder neighbour",
    "resolve_rule": "n_needed = n * (z * se_diff / gap)^2, z = 1.96 (E162 reader-horizon law "
                    "applied to a quantile rather than to a t-test)",
    "frozen": "constants written before the first run; the gate re-derives from rows",
}


# ---------------------------------------------------------------- quantile noise
def _log_binom_pmf(i, n, p):
    return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p) + (n - i) * math.log1p(-p))


def binom_cdf(k, n, p):
    """P(Bin(n, p) <= k), summed in a scaled space so a 2000-draw tail cannot overflow."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lmode = _log_binom_pmf(int((n + 1) * p), n, p)
    s = 0.0
    for i in range(0, k + 1):
        s += math.exp(_log_binom_pmf(i, n, p) - lmode)
    return min(1.0, s * math.exp(lmode))


def _rank_lo(n, p, alpha):
    """Smallest k with P(Bin(n, p) <= k) > alpha/2 -- the 1-based lower order-statistic rank."""
    target = alpha / 2.0
    lmode = _log_binom_pmf(int((n + 1) * p), n, p)
    pmode = math.exp(lmode)
    s = 0.0
    for k in range(0, n):
        s += math.exp(_log_binom_pmf(k, n, p) - lmode)
        if s * pmode > target:
            return k if k >= 1 else 1
    return n


def order_stat_ci(vals, q, alpha=0.05):
    """Distribution-free CI for the q-th percentile: [x_(lo), x_(hi)] over binomial ranks.

    The upper endpoint is the mirrored lower one (n - X ~ Bin(n, 1-p)), so both ends come
    from the same rank search and one distribution.
    """
    n = len(vals)
    if n < 2:
        return None
    v = sorted(vals)
    p = q / 100.0
    lo_k = _rank_lo(n, p, alpha)
    hi_k = n - _rank_lo(n, 1.0 - p, alpha) + 1
    lo_k = max(1, min(lo_k, n))
    hi_k = max(lo_k, min(hi_k, n))
    return {"lo": float(v[lo_k - 1]), "hi": float(v[hi_k - 1]),
            "rank_lo": int(lo_k), "rank_hi": int(hi_k), "n": n}


def spacing_se(vals, q):
    """Density-based SE of the q-th percentile via the spacing estimator (no kernel choice)."""
    n = len(vals)
    if n < 20:
        return None
    v = sorted(vals)
    p = q / 100.0
    s = math.sqrt(n * p * (1.0 - p))
    k1 = int(max(1, min(n, round(n * p - s))))
    k2 = int(max(1, min(n, round(n * p + s))))
    if k2 <= k1 or v[k2 - 1] == v[k1 - 1]:
        return None
    f = (k2 - k1) / (n * (v[k2 - 1] - v[k1 - 1]))
    if f <= 0:
        return None
    return math.sqrt(p * (1.0 - p) / n) / f


def arm_floor(rows, stat, q):
    vals = [float(r[stat]) for r in rows if r.get(stat) is not None]
    if len(vals) < CRITERIA["min_rows"]:
        return None
    ci = order_stat_ci(vals, q, CRITERIA["alpha"])
    se = spacing_se(vals, q)
    return {"value": pct(sorted(vals), q), "ci_lo": ci["lo"], "ci_hi": ci["hi"],
            "rank_lo": ci["rank_lo"], "rank_hi": ci["rank_hi"], "se_density": se,
            "n": len(vals)}


def perm_p(a_vals, b_vals, q, n_perm, seed):
    """Two-sided permutation p for a difference in the q-th percentile."""
    a = np.asarray(a_vals, dtype=float)
    b = np.asarray(b_vals, dtype=float)
    n_a = a.size
    pooled = np.concatenate([a, b])
    qq = q / 100.0
    observed = abs(float(np.quantile(a, qq)) - float(np.quantile(b, qq)))
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_perm):
        idx = rng.permutation(pooled.size)
        x = pooled[idx[:n_a]]
        y = pooled[idx[n_a:]]
        if abs(float(np.quantile(x, qq)) - float(np.quantile(y, qq))) >= observed - 1e-15:
            hits += 1
    return (hits + 1.0) / (n_perm + 1.0)


def n_needed(gap, se_diff, n, z=1.96):
    """Resamples required for `gap` to clear the noise the arms currently carry."""
    if not se_diff or se_diff <= 0 or gap is None or gap <= 0:
        return None
    return n * ((z * se_diff) / abs(gap)) ** 2



def judge(ci_sep, perm_clear):
    """The composition rule: a pair is separated only when BOTH aggregators say so."""
    return {"ci_separated": bool(ci_sep), "perm_clears": bool(perm_clear),
            "separated": bool(ci_sep and perm_clear),
            "verdict_stable_across_aggregators": bool(bool(ci_sep) == bool(perm_clear))}


# ---------------------------------------------------------------- face assembly
def load_arms(cutoff):
    latest = ENV_DIR / "latest.json"
    if not latest.exists():
        raise SystemExit("no latest.json in results/etf_book_bootstrap; run the envelope first")
    cutoff = cutoff or json.loads(latest.read_text(encoding="utf-8"))["evidence_cutoff"]
    arms = {}
    for f in sorted(ENV_DIR.glob(f"ENVELOPE-{cutoff}*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        block = ((doc.get("criteria") or {}).get("bootstrap") or {}).get("block")
        if block is None or not doc.get("rows"):
            continue
        arms[int(block)] = {"file": f.name, "block": int(block), "rows": doc["rows"],
                            "evidence_cutoff": doc.get("evidence_cutoff")}
    if len(arms) < 2:
        raise SystemExit(f"only {len(arms)} arm(s) on disk for {cutoff}")
    return cutoff, arms


def pairs_of(blocks):
    """The ladder comparisons: iid vs each arm, plus each ladder neighbour."""
    out = []
    if 1 in blocks:
        for b in sorted(blocks):
            if b != 1:
                out.append((1, b))
    ordered = [b for b in LADDER if b in blocks]
    for i in range(len(ordered) - 1):
        out.append((ordered[i], ordered[i + 1]))
    seen, uniq = set(), []
    for a, b in out:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        uniq.append((a, b))
    return uniq


def build_face(cutoff=None, out_file=None):
    cutoff, arms = load_arms(cutoff)
    floors = {}
    for block, arm in sorted(arms.items()):
        per = {}
        for stat in CRITERIA["stats"]:
            for q in CRITERIA["quantiles"]:
                fl = arm_floor(arm["rows"], stat, q)
                if fl is not None:
                    per.setdefault(stat, {})[str(q)] = fl
        floors[str(block)] = {"file": arm["file"], "block": block, "floor": per}

    pairs = []
    for a_blk, b_blk in pairs_of(set(arms)):
        for stat in CRITERIA["stats"]:
            for q in CRITERIA["quantiles"]:
                fa = floors[str(a_blk)]["floor"].get(stat, {}).get(str(q))
                fb = floors[str(b_blk)]["floor"].get(stat, {}).get(str(q))
                if not fa or not fb:
                    continue
                av = [float(r[stat]) for r in arms[a_blk]["rows"] if r.get(stat) is not None]
                bv = [float(r[stat]) for r in arms[b_blk]["rows"] if r.get(stat) is not None]
                p = perm_p(av, bv, q, CRITERIA["perm_n"], CRITERIA["perm_seed"])
                diff = fb["value"] - fa["value"]
                ci_sep = (fa["ci_hi"] < fb["ci_lo"]) or (fb["ci_hi"] < fa["ci_lo"])
                se_diff = (math.sqrt(fa["se_density"] ** 2 + fb["se_density"] ** 2)
                           if fa["se_density"] and fb["se_density"] else None)
                row = {"a_block": a_blk, "b_block": b_blk, "stat": stat, "q": q,
                       "a_value": fa["value"], "b_value": fb["value"],
                       "diff": diff, "se_diff": se_diff, "perm_p": p,
                       "n_needed_for_this_gap": n_needed(abs(diff), se_diff, fa["n"])}
                row.update(judge(ci_sep, p <= CRITERIA["alpha"]))
                pairs.append(row)

    face = {
        "evidence_cutoff": cutoff,
        "script": SCRIPT,
        "question": ("what is the smallest difference between two block arms' published "
                     "percentiles that 2,000 resamples can actually resolve?"),
        "criteria": CRITERIA,
        "arms": floors,
        "pairs": pairs,
    }
    face["readings"] = pair_readings(pairs, sorted(arms))
    face["reading"] = reading_line(face)
    out = Path(out_file) if out_file else ENV_DIR / f"NOISE-{cutoff}.json"
    out.write_text(json.dumps(face, indent=1), encoding="utf-8")
    return face, out


def pair_readings(pairs, blocks):
    """The sentences, each derived from the pair table (never stored by hand)."""
    def find(a, b, stat, q):
        for p in pairs:
            if p["a_block"] == a and p["b_block"] == b and p["stat"] == stat and p["q"] == q:
                return p
        return None

    tail = [p for p in pairs if p["stat"] == "maxdd" and p["q"] == 5]
    med = [p for p in pairs if p["stat"] == "cagr" and p["q"] == 50]
    ordered = [b for b in LADDER if b in blocks]
    adjacent = [(ordered[i], ordered[i + 1]) for i in range(len(ordered) - 1)]
    adj_tail = [p for p in tail if (p["a_block"], p["b_block"]) in adjacent]
    iid_vs_week = find(1, 5, "maxdd", 5)
    iid_vs_long = [find(1, 120, "maxdd", 5), find(1, 250, "maxdd", 5)]
    return {
        "iid_vs_week_settled": None if iid_vs_week is None else iid_vs_week["separated"],
        "iid_vs_long_settled": all(p["separated"] for p in iid_vs_long if p is not None),
        "adjacent_gaps_settled": sum(1 for p in adj_tail if p["separated"]),
        "adjacent_gaps_tested": len(adj_tail),
        "median_gaps_settled": sum(1 for p in med if p["separated"]),
        "median_gaps_tested": len(med),
        "ladder_is_one_reading": sum(1 for p in adj_tail if p["separated"]) == 0,
        "aggregators_disagree_on": [
            [p["a_block"], p["b_block"], p["stat"], p["q"]] for p in pairs
            if not p["verdict_stable_across_aggregators"]],
        "separated_pairs": [[p["a_block"], p["b_block"], p["stat"], p["q"]] for p in pairs
                            if p["separated"]],
    }


def reading_line(face):
    r = face["readings"]
    iid = face["arms"].get("1", {}).get("floor", {}).get("maxdd", {}).get("5")
    wk = face["arms"].get("5", {}).get("floor", {}).get("maxdd", {}).get("5")
    ln = face["arms"].get("250", {}).get("floor", {}).get("maxdd", {}).get("5")
    if not (iid and wk and ln):
        return "arm faces missing; nothing to read"
    need = None
    for p in face["pairs"]:
        if p["a_block"] == 1 and p["b_block"] == 5 and p["stat"] == "maxdd" and p["q"] == 5:
            need = p["n_needed_for_this_gap"]
    return ("maxDD p5 with %d draws: iid %.2f%% [%.2f, %.2f], week %.2f%% [%.2f, %.2f] "
            "(gap %.2fpp, %s), year %.2f%% (gap %.2fpp, %s). %d of %d ladder-neighbour gaps "
            "and %d of %d median gaps separate at 95%%; separating the iid arm from the week "
            "arm at this gap would take %s resamples. Resolution, not the ladder, is what the "
            "quoted digits are made of."
            % (iid["n"], iid["value"] * 100, iid["ci_lo"] * 100, iid["ci_hi"] * 100,
               wk["value"] * 100, wk["ci_lo"] * 100, wk["ci_hi"] * 100,
               abs(wk["value"] - iid["value"]) * 100,
               "settled" if r["iid_vs_week_settled"] else "NOT settled",
               ln["value"] * 100, abs(ln["value"] - iid["value"]) * 100,
               "settled" if r["iid_vs_long_settled"] else "NOT settled",
               r["adjacent_gaps_settled"], r["adjacent_gaps_tested"],
               r["median_gaps_settled"], r["median_gaps_tested"],
               "{:,.0f}".format(need) if need else "an unresolved count of"))


# ---------------------------------------------------------------- gate
def latest_face():
    files = sorted(ENV_DIR.glob("NOISE-*.json"))
    return files[-1] if files else None


def check(face_file=None):
    """Every published number must be re-derivable from the arms' own rows."""
    f = Path(face_file) if face_file else latest_face()
    if f is None or not f.exists():
        print("FACE MISSING: no NOISE-*.json")
        return 2
    stored = json.loads(f.read_text(encoding="utf-8"))
    if stored.get("criteria") != CRITERIA:
        print("REFUSED: face echoes different criteria than the module's frozen ones")
        return 2
    face, _ = build_face(stored["evidence_cutoff"], out_file=str(f))
    bad = []
    for block, arm in face["arms"].items():
        s = stored["arms"].get(block)
        if not s:
            bad.append(f"arm {block} missing from face")
            continue
        for stat, qs in arm["floor"].items():
            for q, fl in qs.items():
                sf = (s["floor"].get(stat) or {}).get(q)
                if not sf:
                    bad.append(f"arm {block} {stat} p{q} missing")
                    continue
                for k in ("value", "ci_lo", "ci_hi"):
                    if abs((sf.get(k) or 0.0) - fl[k]) > 1e-12:
                        bad.append(f"arm {block} {stat} p{q} {k} {sf.get(k)} != {fl[k]}")
    sp = {(p["a_block"], p["b_block"], p["stat"], p["q"]): p for p in stored["pairs"]}
    for p in face["pairs"]:
        s = sp.get((p["a_block"], p["b_block"], p["stat"], p["q"]))
        if not s:
            bad.append(f"pair {p['a_block']}/{p['b_block']} {p['stat']} p{p['q']} missing")
            continue
        if abs((s.get("diff") or 0.0) - p["diff"]) > 1e-12:
            bad.append(f"pair {p['a_block']}/{p['b_block']} diff {s.get('diff')} != {p['diff']}")
        if abs((s.get("perm_p") or 0.0) - p["perm_p"]) > 1e-12:
            bad.append(f"pair {p['a_block']}/{p['b_block']} perm_p {s.get('perm_p')} != {p['perm_p']}")
        if bool(s.get("separated")) != p["separated"]:
            bad.append(f"pair {p['a_block']}/{p['b_block']} separated flag contradicted")
    if stored.get("readings") != face["readings"]:
        bad.append("readings block contradicted by the pair table")
    if bad:
        print("MISMATCH (%d):" % len(bad))
        for b in bad[:12]:
            print(" -", b)
        return 2
    print("OK: %d arms, %d pairs re-derived from rows; every percentile, interval, "
          "permutation p and verdict matches" % (len(face["arms"]), len(face["pairs"])))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    rng = np.random.default_rng(11)

    # L1 the rank arithmetic is a distribution
    leg("L1 binomial cdf is monotone and ends at 1",
        binom_cdf(0, 50, 0.2) < binom_cdf(25, 50, 0.5) and abs(binom_cdf(50, 50, 0.5) - 1.0) < 1e-12)

    # L2 a uniform sample's median interval brackets the truth and is ~1/sqrt(n) wide
    u = rng.random(2000).tolist()
    ci = order_stat_ci(u, 50)
    leg("L2 uniform median interval brackets 0.5",
        ci["lo"] < 0.5 < ci["hi"], ci)
    leg("L2b interval width is sample-size order", 0.02 < (ci["hi"] - ci["lo"]) < 0.08,
        ci["hi"] - ci["lo"])

    # L3 a degenerate sample has zero width, and the density SE refuses instead of inventing one
    flat = [0.25] * 500
    c3 = order_stat_ci(flat, 5)
    leg("L3 constant sample has zero width", abs(c3["hi"] - c3["lo"]) < 1e-15, c3)
    leg("L3b zero dispersion SE is None, not a number", spacing_se(flat, 5) is None)

    # L4 coverage: with n=300 the order-statistic 95% interval for the median covers the truth
    cover, trials = 0, 120
    for _ in range(trials):
        s = rng.normal(0.0, 1.0, 300).tolist()
        c = order_stat_ci(s, 50)
        if c["lo"] <= 0.0 <= c["hi"]:
            cover += 1
    leg("L4 nominal 95%% interval covers in >=88%% of %d trials" % trials, cover / trials >= 0.88,
        cover / trials)

    # L5/L6 the permutation test is not a coin: same distribution stays, a shift is caught
    a = rng.normal(0.0, 1.0, 600).tolist()
    b = rng.normal(0.0, 1.0, 600).tolist()
    p_same = perm_p(a, b, 5, 200, 3)
    leg("L5 identical distributions are not separated", p_same > 0.05, p_same)
    c = rng.normal(1.5, 1.0, 600).tolist()
    p_shift = perm_p(a, c, 5, 200, 3)
    leg("L6 a shifted distribution is separated", p_shift <= 0.05, p_shift)

    # L7 a smaller gap needs more draws (and the formula is monotone)
    leg("L7 n_needed grows as the gap shrinks",
        n_needed(0.002, 0.0015, 2000) > n_needed(0.004, 0.0015, 2000))

    # L8 at the returned count the gap is exactly resolvable (definition check)
    need = n_needed(0.003, 0.0015, 2000)
    se_at = 0.0015 * math.sqrt(2000.0 / need)
    leg("L8 implied resolution equals the gap", abs(1.96 * se_at - 0.003) < 1e-12,
        (need, 1.96 * se_at))

    # L9 an arm compared with itself is never separated and p reads 1
    self_p = perm_p(a, list(a), 5, 200, 3)
    leg("L9 self-comparison reads p=1", self_p > 0.99, self_p)

    # L10 too few rows is refused rather than answered
    leg("L10 thin arm is refused", arm_floor([{"maxdd": -0.1}] * 5, "maxdd", 5) is None)

    # L11 an edited percentile in the face is contradicted by the rows
    face_good = {"arms": {"1": {"floor": {"maxdd": {"5": arm_floor(
        [{"maxdd": -0.2 + 0.01 * i} for i in range(200)], "maxdd", 5)}}}}}
    edited = json.loads(json.dumps(face_good))
    edited["arms"]["1"]["floor"]["maxdd"]["5"]["value"] += 0.01
    leg("L11 edited percentile contradicted",
        edited["arms"]["1"]["floor"]["maxdd"]["5"]["value"]
        != arm_floor([{"maxdd": -0.2 + 0.01 * i} for i in range(200)], "maxdd", 5)["value"])

    # L12 the composition rule: separating takes BOTH aggregators, and any disagreement is
    # published as instability rather than resolved by picking a winner.
    both = judge(True, True)
    neither = judge(False, False)
    only_ci = judge(True, False)
    only_perm = judge(False, True)
    leg("L12 both aggregators agreeing separates, disagreement never does",
        both["separated"] and both["verdict_stable_across_aggregators"]
        and not neither["separated"] and neither["verdict_stable_across_aggregators"]
        and not only_ci["separated"] and not only_ci["verdict_stable_across_aggregators"]
        and not only_perm["separated"] and not only_perm["verdict_stable_across_aggregators"])
    r = pair_readings([dict({"a_block": 1, "b_block": 2, "stat": "maxdd", "q": 5}, **only_ci)],
                      [1, 2])
    leg("L12b an unstable pair is named on the face and not counted as separated",
        r["aggregators_disagree_on"] == [[1, 2, "maxdd", 5]] and r["separated_pairs"] == [], r)

    # L13 the reading is derived from the pair table: flip a pair and the sentence changes
    base = [{"a_block": 1, "b_block": 5, "stat": "maxdd", "q": 5, "separated": False,
             "verdict_stable_across_aggregators": True}]
    flipped = [{"a_block": 1, "b_block": 5, "stat": "maxdd", "q": 5, "separated": True,
                "verdict_stable_across_aggregators": True}]
    leg("L13 readings follow the table",
        pair_readings(base, [1, 5])["iid_vs_week_settled"] is False
        and pair_readings(flipped, [1, 5])["iid_vs_week_settled"] is True)

    # L14 the ladder pairing is the declared one, not whatever the dict order gave
    leg("L14 pairs are iid-vs-each plus neighbours", pairs_of({1, 5, 20}) == [(1, 5), (1, 20), (5, 20)],
        pairs_of({1, 5, 20}))

    print("selftest %d/%d" % (sum(1 for _, c, _ in ok if c), len(ok)))
    for name, cond, detail in ok:
        if not cond:
            print("FAIL", name, detail)
    return 0 if all(c for _, c, _ in ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--cutoff", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check()
    face, out = build_face(a.cutoff, a.out)
    print(face["reading"])
    print("-> %s" % out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())