"""ETF book -- is the 64-arm sign ordering a property of the panel, or of one period?

E219 priced the sign choice: the six production directions rank 6 of 64, the median arm
(what "pick one direction per factor" is worth without looking) earns -1.63%/yr, and one
sign block moves the headline by 20.8pp/yr. Every number there is one window: 2020-01-01 to
the panel cutoff. If the arm *ordering* does not survive a split of that window, then
"production sits in the top decile" describes the window and nothing else -- there is no
sign rule to learn, and the honest quote is a distribution, not a rank. If it does survive,
the in-sample-best arm is a chooser a live operator could actually have run, and its
out-of-sample number is the money figure E219 left open.

Frozen before the first run (echoed into the payload, gate REDs on any drift):
    REBAL=20, N_HOLD=12, COST=10bp/side, START=2020-01-01, MIN_TRADED_BARS=30,
    TOP_DECILE=0.10, SPEARMAN_TRANSFER=0.50, MIN_BARS_PER_PERIOD=200,
    IS=(2020-01-01..2023-12-31), OOS=(2024-01-01..cutoff).

Verdict rule (recomputed by the gate from the per-period arm table, never taken on trust):
    any half traded fewer than 2^6 arms, or any half < MIN_BARS_PER_PERIOD
                                                 -> not_assessable_short_period
    spearman(IS arm cagrs, OOS arm cagrs) < SPEARMAN_TRANSFER
                                                 -> sign_ordering_does_not_transfer
    production arm in the top decile of BOTH halves
                                                 -> sign_ordering_transfers
    otherwise                                    -> ordering_transfers_but_not_this_arm

Measurement choice, disclosed rather than hidden: a period's numbers are read off the SAME
return series as the full-window arm (the path trades across the split; there is no re-entry
cost or fresh flat start at 2024-01-01). So they say "what this path did during these bars",
which is exactly the question a rank-transfer test asks, and NOT "what starting this book on
2024-01-01 would have earned".

  python scripts/etf_sign_stability.py run         # 64 arms x 2 halves, writes results/etf_sign_stability.json
  python scripts/etf_sign_stability.py --check     # re-derive the verdict from the payload
  python scripts/etf_sign_stability.py --selftest  # offline invariants, zero network
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_sign_enum as SE  # noqa: E402
import etf_sign_pit as P  # noqa: E402
import etf_variants_null_rolling as V  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_sign_stability.json"

SIGNS = dict(SE.SIGNS)
FACTOR_KEYS = list(SE.FACTOR_KEYS)
REBAL = SE.REBAL
N_HOLD = SE.N_HOLD
COST = SE.COST
START = SE.START
MIN_TRADED_BARS = SE.MIN_TRADED_BARS
TOP_DECILE = SE.TOP_DECILE
SPEARMAN_TRANSFER = 0.50
MIN_BARS_PER_PERIOD = 200
IS_START = "2020-01-01"
IS_END = "2023-12-31"
OOS_START = "2024-01-01"
BARS_PER_YEAR = 252

DECLARED = {
    "rebal": REBAL,
    "n_hold": N_HOLD,
    "cost_per_side": COST,
    "start": START,
    "min_traded_bars": MIN_TRADED_BARS,
    "top_decile": TOP_DECILE,
    "spearman_transfer": SPEARMAN_TRANSFER,
    "min_bars_per_period": MIN_BARS_PER_PERIOD,
    "is_window": [IS_START, IS_END],
    "oos_window": [OOS_START, "cutoff"],
    "n_arms": 2 ** len(SIGNS),
    "bars_per_year": BARS_PER_YEAR,
    "signs": SIGNS,
}


# --- measurement ---------------------------------------------------------------------
def period_stats(nav: pd.Series) -> dict:
    """CAGR/Sharpe/maxDD of a NAV slice, computed from that slice alone.

    The engine hands back an equity curve (it starts at 1.0), not per-bar returns -- reading
    it as returns multiplies the curve by itself and prints inf (this module's first run did
    exactly that, which is why L3 now pins the convention on a growing NAV rather than on a
    flat return series).
    """
    s = pd.Series(nav).dropna()
    n = int(len(s))
    if n < 2:
        return {"cagr": None, "sharpe": None, "maxdd": None, "bars": max(0, n - 1),
                "growth": None}
    v = s.pct_change().dropna().to_numpy(dtype=float)
    first, last = float(s.iloc[0]), float(s.iloc[-1])
    growth = last / first if first > 0 else None
    cagr = (growth ** (BARS_PER_YEAR / len(v)) - 1.0) if growth and growth > 0 else -1.0
    sd = float(np.std(v, ddof=1)) if len(v) > 1 else 0.0
    sharpe = float(np.mean(v) / sd * np.sqrt(BARS_PER_YEAR)) if sd > 0 else 0.0
    arr = s.to_numpy(dtype=float)
    peak = np.maximum.accumulate(arr)
    mdd = float(np.min(arr / peak - 1.0))
    return {"cagr": round(cagr, 6), "sharpe": round(sharpe, 4), "maxdd": round(mdd, 6),
            "bars": int(len(v)), "growth": round(growth, 8) if growth else None}


def slice_window(ser: pd.Series, lo: str, hi: str | None) -> pd.Series:
    idx = pd.to_datetime(pd.Series(ser.index))
    mask = idx >= pd.Timestamp(lo)
    if hi is not None:
        mask &= idx <= pd.Timestamp(hi)
    return ser[np.asarray(mask)]


def ranks_from(cagrs: dict) -> dict:
    """1 = best. Ties broken by key order so the output is deterministic."""
    keys = [k for k in cagrs if isinstance(cagrs[k], (int, float))]
    vals = np.array([float(cagrs[k]) for k in keys])
    order = np.argsort(-vals, kind="stable")
    out = {}
    for pos, i in enumerate(order, 1):
        out[keys[i]] = pos
    return out


def spearman(a: dict, b: dict) -> float | None:
    keys = [k for k in a if k in b and isinstance(a[k], (int, float))
            and isinstance(b[k], (int, float))]
    if len(keys) < 3:
        return None
    sa = pd.Series([float(a[k]) for k in keys])
    sb = pd.Series([float(b[k]) for k in keys])
    if sa.nunique() < 2 or sb.nunique() < 2:
        return None
    return round(float(sa.corr(sb, method="spearman")), 6)


def overlap_tail(n: int, k: int, observed: int) -> float | None:
    """P(shared >= observed) for two independent k-subsets of an n-element set.

    The E199 discipline applied to this face: "the top deciles do not line up" is only a
    measurement if the number it is being compared to is on the page. Chance overlap is
    k^2/n; this returns the exact upper tail so the reading is not a shrug.
    """
    from math import comb
    if n <= 0 or k <= 0 or k > n:
        return None
    tot = comb(n, k)
    p = 0.0
    for j in range(max(0, observed), min(k, n - k if n - k < k else k) + 1):
        if k - j > n - k:
            continue
        p += comb(k, j) * comb(n - k, k - j) / tot
    return round(min(1.0, p), 6)


# --- gate ----------------------------------------------------------------------------
def gate(payload: dict) -> dict:
    """Recompute ranks, rank transfer and the verdict from the per-period table alone."""
    decl = payload.get("declared") or {}
    checks = []
    for key, val in DECLARED.items():
        got = decl.get(key)
        same = got == (dict(val) if key == "signs" else val)
        checks.append({"check": "declared %s echoed" % key, "ok": bool(same),
                       "payload": got, "module": val})
    arms = payload.get("arms") or {}
    n_expected = 2 ** len(SIGNS)
    have = {p: {k: (a.get(p) or {}).get("cagr") for k, a in arms.items()
                if isinstance((a.get(p) or {}).get("cagr"), (int, float))}
            for p in ("is", "oos")}
    checks.append({"check": "every arm carries both halves (r1261: an empty half passes everything)",
                   "ok": len(arms) == n_expected and len(have["is"]) == n_expected
                         and len(have["oos"]) == n_expected,
                   "arms": len(arms), "is": len(have["is"]), "oos": len(have["oos"]),
                   "expected": n_expected})
    bars = {p: {k: int((a.get(p) or {}).get("bars") or 0) for k, a in arms.items()}
            for p in ("is", "oos")}
    min_bars = min([b for p in bars for b in bars[p].values()] or [0])
    checks.append({"check": "both halves long enough to rank (min_bars_per_period)",
                   "ok": min_bars >= MIN_BARS_PER_PERIOD, "min_bars": min_bars,
                   "required": MIN_BARS_PER_PERIOD})
    rho = spearman(have["is"], have["oos"])
    checks.append({"check": "spearman rank transfer recomputed from the arm table",
                   "ok": rho is not None, "spearman": rho,
                   "line": SPEARMAN_TRANSFER})
    r_is = ranks_from(have["is"])
    r_oos = ranks_from(have["oos"])
    prod_key = payload.get("production_key") or ""
    n = len(r_is)
    top_k = int(np.ceil(TOP_DECILE * n)) if n else 0
    prod_is = r_is.get(prod_key)
    prod_oos = r_oos.get(prod_key)
    in_both = bool(prod_is and prod_oos and prod_is <= top_k and prod_oos <= top_k)
    traded_ok = len(have["is"]) == n_expected == len(have["oos"]) == len(arms)
    if not traded_ok or prod_is is None or prod_oos is None:
        verdict = "not_assessable_short_period"
    elif min_bars < MIN_BARS_PER_PERIOD:
        verdict = "not_assessable_short_period"
    elif rho is None or rho < SPEARMAN_TRANSFER:
        verdict = "sign_ordering_does_not_transfer"
    elif in_both:
        verdict = "sign_ordering_transfers"
    else:
        verdict = "ordering_transfers_but_not_this_arm"
    # the practical chooser: take the IS winner, quote what it did in OOS
    best_is = min(r_is, key=lambda k: r_is[k]) if r_is else None
    best_is_oos_rank = r_oos.get(best_is) if best_is else None
    checks.append({"check": "ranks and both-half membership recomputed",
                   "ok": prod_is is not None and prod_oos is not None,
                   "production_is_rank": prod_is, "production_oos_rank": prod_oos,
                   "top_k": top_k, "n": n})
    # how much transfer the test could have seen, and whether what it saw beats chance
    ov = _overlap(r_is, r_oos, top_k) if r_is and r_oos else {"n_shared": None}
    ov_tail = overlap_tail(n, top_k, ov["n_shared"]) if ov.get("n_shared") is not None else None
    null_sd = round(1.0 / float(np.sqrt(n - 1)), 6) if n > 1 else None
    med = {p: (round(float(np.median(list(have[p].values()))), 6) if have[p] else None)
           for p in ("is", "oos")}
    return {"verdict": verdict, "spearman": rho, "n": n, "top_k": top_k,
            "production_is_rank": prod_is, "production_oos_rank": prod_oos,
            "production_in_top_decile_both": in_both,
            "best_is_key": best_is, "best_is_oos_rank": best_is_oos_rank,
            "median_cagr": med,
            "spearman_null_sd": null_sd,
            "spearman_z": (round(rho / null_sd, 4) if rho is not None and null_sd else None),
            "top_decile_shared": ov.get("n_shared"),
            "top_decile_chance_expected": (round(top_k * top_k / n, 4) if n else None),
            "top_decile_shared_p": ov_tail,
            "is_cagrs": have["is"], "oos_cagrs": have["oos"],
            "is_ranks": r_is, "oos_ranks": r_oos,
            "checks": checks, "all_ok": all(c["ok"] for c in checks)}


# --- run -----------------------------------------------------------------------------
def run() -> dict:
    t0 = time.time()
    close, openp, amt, feats = P.load_panel()
    elig = P.eligibility(close, amt)
    zs = SE.z_mats(close, feats)
    cutoff = str(pd.Timestamp(close.index[-1]).date())
    print("panel %d bars x %d symbols, cutoff %s (%.1fs)"
          % (len(close.index), close.shape[1], cutoff, time.time() - t0), flush=True)
    vecs = SE.sign_vectors(FACTOR_KEYS)
    prod_key = "|".join("%s%s" % (k, "+" if SIGNS[k] > 0 else "-") for k in FACTOR_KEYS)
    arms = {}
    for i, v in enumerate(vecs, 1):
        key = "|".join("%s%s" % (k, "+" if v[k] > 0 else "-") for k in FACTOR_KEYS)
        sc = SE.score_from(zs, v, close, elig)
        ser, turn, _gap = V.fast_next_open(sc, close, openp, REBAL, n_hold=N_HOLD,
                                           cost=COST, start=START)
        is_ser = slice_window(ser, IS_START, IS_END)
        oos_ser = slice_window(ser, OOS_START, None)
        full = period_stats(ser)
        traded = bool(float(turn) > 0.0 and full["bars"] >= MIN_TRADED_BARS)
        years = {}
        for y in sorted({int(pd.Timestamp(t).year) for t in ser.index}):
            ys = ser[[int(pd.Timestamp(t).year) == y for t in ser.index]]
            years[str(y)] = period_stats(ys)
        arms[key] = {"signs": v, "turnover_per_rebal": round(float(turn), 4),
                     "traded": traded, "full": full,
                     "is": period_stats(is_ser), "oos": period_stats(oos_ser),
                     "years": years}
        if i % 8 == 0 or i == len(vecs):
            print("  arm %2d/%d cagr_full=%s is=%s oos=%s (%.0fs)"
                  % (i, len(vecs), full["cagr"], arms[key]["is"]["cagr"],
                     arms[key]["oos"]["cagr"], time.time() - t0), flush=True)
    payload = {
        "evidence_cutoff": cutoff,
        "universe": int(close.shape[1]),
        "question": "E219's 64-arm table is one window: does the arm ordering survive a split "
                    "of it, and what does the in-sample-best sign set earn out of sample?",
        "declared": {k: (dict(v) if k == "signs" else v) for k, v in DECLARED.items()},
        "production_key": prod_key,
        "arms": arms,
        "caveats": [
            "Sub-period numbers come from the SAME trading path as the full-window arm (no "
            "fresh flat start and no re-entry cost at the split), so they describe what this "
            "path did during those bars, not what launching the book on 2024-01-01 earns.",
            "Reference engine only (no impact cost, no gap risk), flat sizing: the vol "
            "target/beta overlay is deliberately out, so this is not the card's headline.",
            "Signs are the six production factors: a dropped factor is a different question, "
            "and E219 already priced the IC floor for that.",
            "ETF pool is today's listed set (survivorship), unchanged caveat on this line.",
            "The rank-transfer question is about ORDER, not level: a panel where every arm "
            "falls together can still show a stable ordering.",
        ],
    }
    g = gate(payload)
    payload["verdict"] = g["verdict"]
    payload["gate"] = {"spearman": g["spearman"], "n": g["n"], "top_k": g["top_k"],
                       "production_is_rank": g["production_is_rank"],
                       "production_oos_rank": g["production_oos_rank"],
                       "production_in_top_decile_both": g["production_in_top_decile_both"],
                       "spearman_null_sd": g["spearman_null_sd"],
                       "spearman_z": g["spearman_z"],
                       "top_decile_shared": g["top_decile_shared"],
                       "top_decile_chance_expected": g["top_decile_chance_expected"],
                       "top_decile_shared_p": g["top_decile_shared_p"],
                       "all_ok": g["all_ok"], "checks": g["checks"]}
    prod = arms[prod_key]
    oos_c = {k: a["oos"]["cagr"] for k, a in arms.items()}
    is_c = {k: a["is"]["cagr"] for k, a in arms.items()}
    best_is = g["best_is_key"]
    payload["summary"] = {
        "verdict": g["verdict"],
        "spearman_rank_transfer": g["spearman"],
        "spearman_null_sd": g["spearman_null_sd"],
        "spearman_z": g["spearman_z"],
        "top_decile_shared": g["top_decile_shared"],
        "top_decile_chance_expected": g["top_decile_chance_expected"],
        "top_decile_shared_p": g["top_decile_shared_p"],
        "production_is_rank": g["production_is_rank"],
        "production_oos_rank": g["production_oos_rank"],
        "top_k": g["top_k"],
        "n_arms": g["n"],
        "production_cagr_full": prod["full"]["cagr"],
        "production_cagr_is": prod["is"]["cagr"],
        "production_cagr_oos": prod["oos"]["cagr"],
        "median_cagr_is": g["median_cagr"]["is"],
        "median_cagr_oos": g["median_cagr"]["oos"],
        "best_is_key": best_is,
        "best_is_cagr_is": is_c.get(best_is),
        "best_is_cagr_oos": oos_c.get(best_is),
        "best_is_oos_rank": g["best_is_oos_rank"],
        "best_oos_key": min(g["oos_ranks"], key=lambda k: g["oos_ranks"][k]),
        "delta_learnable_pp": (round((oos_c.get(best_is) - g["median_cagr"]["oos"]) * 100.0, 3)
                               if oos_c.get(best_is) is not None
                               and g["median_cagr"]["oos"] is not None else None),
        "delta_production_vs_median_oos_pp": (
            round((prod["oos"]["cagr"] - g["median_cagr"]["oos"]) * 100.0, 3)
            if prod["oos"]["cagr"] is not None and g["median_cagr"]["oos"] is not None else None),
        "top_decile_overlap_is_oos": _overlap(g["is_ranks"], g["oos_ranks"], g["top_k"]),
        "elapsed_s": round(time.time() - t0, 1),
    }
    # production's rank over the FULL window, for the E219 cross-check
    full_ranks = ranks_from({k: a["full"]["cagr"] for k, a in arms.items()})
    payload["summary"]["production_full_rank"] = full_ranks.get(prod_key)
    payload["summary"]["full_rank_matches_e219"] = (
        payload["summary"]["production_full_rank"] ==
        ((json.loads(SE.OUT_JSON.read_text(encoding="utf-8")).get("summary") or {})
         .get("production_rank") if SE.OUT_JSON.exists() else None))
    payload["gate"]["checks"].append(
        {"check": "full-window rank reproduces the stored E219 rank",
         "ok": bool(payload["summary"]["full_rank_matches_e219"]),
         "this_round": payload["summary"]["production_full_rank"],
         "e219": (json.loads(SE.OUT_JSON.read_text(encoding="utf-8")).get("summary") or {})
         .get("production_rank") if SE.OUT_JSON.exists() else None})
    payload["gate"]["all_ok"] = all(c["ok"] for c in payload["gate"]["checks"])
    # per-period factor attribution (cheap arithmetic on the same table)
    payload["marginal_by_factor"] = {
        p: SE.main_effects({k: {"cagr": a[p]["cagr"], "signs": a["signs"]}
                            for k, a in arms.items() if a[p]["cagr"] is not None})
        for p in ("is", "oos")}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=1), flush=True)
    return payload


def _overlap(a: dict, b: dict, k: int) -> dict:
    topa = {key for key, r in a.items() if r <= k}
    topb = {key for key, r in b.items() if r <= k}
    return {"is": sorted(topa), "oos": sorted(topb),
            "shared": sorted(topa & topb), "n_shared": len(topa & topb)}


def check() -> int:
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    g = gate(payload)
    print("verdict=%s spearman=%s prod_is_rank=%s prod_oos_rank=%s stored=%s all_ok=%s"
          % (g["verdict"], g["spearman"], g["production_is_rank"], g["production_oos_rank"],
             payload.get("verdict"), g["all_ok"]))
    for c in g["checks"]:
        if not c["ok"]:
            print("  RED %s -> %s" % (c["check"], {k: v for k, v in c.items() if k != "check"}))
    if not g["all_ok"] or g["verdict"] != payload.get("verdict"):
        return 1
    return 0


# --- selftest ------------------------------------------------------------------------
def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # L1 rank transfer: an identical ordering must read 1.0, a reversed one -1.0
    same = {("k%02d" % i): float(64 - i) for i in range(64)}
    rev = {k: -v for k, v in same.items()}
    leg("L1 identical orderings give spearman 1.0", spearman(same, same) == 1.0,
        "rho=%s" % spearman(same, same))
    leg("L1b a reversed ordering gives spearman -1.0", spearman(same, rev) == -1.0,
        "rho=%s" % spearman(same, rev))

    # L2 rank helper: best cagr is rank 1 and ranks are a permutation of 1..n
    c = {"a": 0.10, "b": 0.30, "c": -0.05, "d": 0.30}
    r = ranks_from(c)
    leg("L2 ranks are 1..n with the largest cagr at 1",
        sorted(r.values()) == [1, 2, 3, 4] and r["b"] == 1 and r["c"] == 4, "ranks=%s" % r)

    # L3 period stats are exact on a constant-growth NAV, and must not read NAV as returns
    nav = pd.Series(1.001 ** np.arange(501))
    st = period_stats(nav)
    exact = 1.001 ** BARS_PER_YEAR - 1
    leg("L3 cagr of a constant-growth NAV matches 1.001^252 - 1 (NAV is not a return series)",
        abs(st["cagr"] - exact) < 1e-6 and st["bars"] == 500 and st["maxdd"] == 0.0,
        "cagr=%s exact=%.6f mdd=%s bars=%s" % (st["cagr"], exact, st["maxdd"], st["bars"]))
    leg("L3a the same series read as returns would be absurd (guard against the inf bug)",
        abs(st["cagr"]) < 1.0, "cagr=%s" % st["cagr"])
    leg("L3b a slice shorter than two points is None-and-zero-bars, not an exception",
        period_stats(pd.Series([], dtype=float))["cagr"] is None)

    def fixture(rho_case: str, prod_rank_is=6, n=64, bars=800):
        """A synthetic 64-arm table where the OOS ordering is a chosen permutation of IS."""
        is_c = {("a%02d" % i): (0.20 - 0.005 * i) for i in range(n)}
        if rho_case == "same":
            oos_c = dict(is_c)
        elif rho_case == "reverse":
            oos_c = {k: -v for k, v in is_c.items()}
        else:  # shuffle deterministically
            keys = sorted(is_c)
            vals = [is_c[k] for k in keys]
            oos_c = {k: vals[(i * 17 + 5) % n] for i, k in enumerate(keys)}
        prod = "a%02d" % (prod_rank_is - 1)
        arms = {k: {"signs": {}, "traded": True,
                    "is": {"cagr": is_c[k], "bars": bars},
                    "oos": {"cagr": oos_c[k], "bars": bars}} for k in is_c}
        return {"declared": {k: (dict(v) if k == "signs" else v) for k, v in DECLARED.items()},
                "production_key": prod, "arms": arms}

    leg("L4 a stable ordering puts a top-decile arm in the top decile of both halves",
        gate(fixture("same"))["verdict"] == "sign_ordering_transfers")
    leg("L4b a reversed ordering is 'does not transfer' even though the arm is top-decile in IS",
        gate(fixture("reverse"))["verdict"] == "sign_ordering_does_not_transfer")
    g_sh = gate(fixture("shuffle"))
    leg("L4c a shuffled ordering is 'does not transfer' and reports a near-zero rho",
        g_sh["verdict"] == "sign_ordering_does_not_transfer" and abs(g_sh["spearman"] or 1) < 0.5,
        "rho=%s" % g_sh["spearman"])
    leg("L4d a stable ordering with an ordinary production arm is neither transfer nor optimum",
        gate(fixture("same", prod_rank_is=40))["verdict"]
        == "ordering_transfers_but_not_this_arm")
    leg("L4e a half shorter than the declared floor is not assessable, not a yes",
        gate(fixture("same", bars=MIN_BARS_PER_PERIOD - 1))["verdict"]
        == "not_assessable_short_period")

    bad = fixture("same")
    bad["declared"]["spearman_transfer"] = 0.1
    leg("L5 gate REDs when the payload was built under different constants",
        not gate(bad)["all_ok"])
    missing = fixture("same")
    missing["arms"].pop(missing["production_key"])
    leg("L5b a production arm missing from the table is not assessable",
        gate(missing)["verdict"] == "not_assessable_short_period")
    half = fixture("same")
    for k in list(half["arms"])[:10]:
        half["arms"][k]["oos"]["cagr"] = None
    leg("L5c an arm with an empty half makes the table not assessable",
        gate(half)["verdict"] == "not_assessable_short_period")

    # L6 the practical chooser: best-of-IS must be the arm with the highest IS cagr
    g6 = gate(fixture("same"))
    leg("L6 best-of-IS names the IS winner, not the production arm",
        g6["best_is_key"] == "a00" and g6["best_is_oos_rank"] == 1,
        "best=%s oos_rank=%s" % (g6["best_is_key"], g6["best_is_oos_rank"]))
    leg("L6b top-decile overlap counts the shared arms", _overlap(g6["is_ranks"], g6["oos_ranks"],
                                                                g6["top_k"])["n_shared"] == 7)

    # L7 window slicing honours both bounds
    idx = pd.date_range("2020-01-01", periods=1500, freq="B")
    ser = pd.Series(1.0, index=idx)
    is_s = slice_window(ser, IS_START, IS_END)
    oos_s = slice_window(ser, OOS_START, None)
    leg("L7 the two windows partition the series and respect the bounds",
        len(is_s) + len(oos_s) == len(ser) and len(is_s) > 0 and len(oos_s) > 0
        and pd.Timestamp(is_s.index[-1]).year == 2023
        and pd.Timestamp(oos_s.index[0]).year == 2024,
        "is=%d oos=%d" % (len(is_s), len(oos_s)))

    # L8 the overlap floor: chance expectation, an exactly-known tail, and monotonicity
    leg("L8 two k-subsets of n share k^2/n arms on average",
        abs(7 * 7 / 64 - 0.765625) < 1e-9,
        "expected=%.4f" % (7 * 7 / 64))
    leg("L8b hand-checkable tail: with n=4, k=2, P(share 2) = 1/6",
        abs((overlap_tail(4, 2, 2) or 0) - 1 / 6) < 1e-6, "p=%s" % overlap_tail(4, 2, 2))
    t1, t2 = overlap_tail(64, 7, 1), overlap_tail(64, 7, 3)
    leg("L8c the tail is monotone decreasing in the observed overlap and inside [0,1]",
        t1 is not None and t2 is not None and 0.0 <= t2 < t1 <= 1.0, "p1=%s p3=%s" % (t1, t2))
    leg("L8d observing zero shared arms is certain", overlap_tail(64, 7, 0) == 1.0)

    bad_n = 0
    for name, ok, extra in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + extra) if extra else ""))
        bad_n += 0 if ok else 1
    print("%d/%d PASS" % (len(legs) - bad_n, len(legs)))
    return 0 if bad_n == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.mode == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())