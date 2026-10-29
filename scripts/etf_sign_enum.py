"""ETF book -- is the production sign set special, or just the winning draw of 64?

E207 showed the six factor directions in `etf_composite_pf.SIGNS` are exactly the
full-sample IC signs, so every published number on this line is priced with knowledge of
which way each factor paid. It could not say how much that knowledge is worth, because it
only ever ran three arms (fixed / trailing-IC / reversed).

Six factors, two directions each, is 64 arms. That is small enough to run all of them, and
the answer is then not an argument:

  * where the production signs rank among the 64 possible sign sets,
  * what an operator with NO hindsight earns -- the median arm, which is what "pick a
    direction per factor" is worth when the direction is not read off the answer,
  * and the best-of-64, i.e. the ceiling that any in-sample sign chooser can reach.

Everything but the signs is held fixed: same panel, same eligibility, same engine
(`etf_variants_null_rolling.fast_next_open`), same costs, same width, same cadence.

Frozen before the first run (echoed into the payload; the gate REDs if they differ):
    REBAL=20, N_HOLD=12, COST=10bp/side, START=2020-01-01, MIN_TRADED_BARS=30,
    TOP_DECILE=0.10, DEGENERATE_SPREAD=0.01.

Verdict rule (recomputed by the gate from the arm table, never taken on trust):
    fewer than 2^6 arms traded            -> not_assessable_no_trade
    (max - min) CAGR < DEGENERATE_SPREAD -> not_assessable_degenerate
    production rank <= ceil(TOP_DECILE*n) -> signs_sit_at_the_sample_optimum
    otherwise                             -> signs_are_ordinary_choices

  python scripts/etf_sign_enum.py run         # 64 arms, writes results/etf_sign_enum.json
  python scripts/etf_sign_enum.py --check     # re-derive the verdict from the payload
  python scripts/etf_sign_enum.py --selftest  # offline invariants, zero network
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as F  # noqa: E402
import etf_sign_pit as P  # noqa: E402
import etf_variants_null_rolling as V  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_sign_enum.json"

SIGNS = dict(F.SIGNS)
FACTOR_KEYS = list(SIGNS)
REBAL = 20
N_HOLD = 12
COST = 0.0010
START = "2020-01-01"
MIN_TRADED_BARS = 30
TOP_DECILE = 0.10
DEGENERATE_SPREAD = 0.01
DECLARED = {
    "rebal": REBAL,
    "n_hold": N_HOLD,
    "cost_per_side": COST,
    "start": START,
    "min_traded_bars": MIN_TRADED_BARS,
    "top_decile": TOP_DECILE,
    "degenerate_spread": DEGENERATE_SPREAD,
    "n_arms": 2 ** len(SIGNS),
    "signs": SIGNS,
}


# --- construction --------------------------------------------------------------------
def z_mats(close: pd.DataFrame, feats: dict) -> dict:
    """The six signed-rank matrices, built once (64 arms then cost one add each)."""
    cols = close.columns
    idx = close.index
    out = {}
    for k in FACTOR_KEYS:
        f = feats.get(k)
        if f is None:
            out[k] = None
            continue
        out[k] = (f.reindex(index=idx, columns=cols).rank(axis=1, pct=True) - 0.5) * 2.0
    return out


def score_from(zs: dict, signs: dict, close: pd.DataFrame, elig: pd.DataFrame) -> pd.DataFrame:
    """Same arithmetic as etf_sign_pit.score_face, from pre-built rank matrices."""
    total = None
    active = None
    for k in FACTOR_KEYS:
        z = zs.get(k)
        if z is None:
            continue
        s = float(signs.get(k, 0.0))
        if s == 0.0:
            continue
        part = z * s
        total = part if total is None else total.add(part)
        active = 1 if active is None else active + 1
    if total is None or not active:
        return pd.DataFrame(np.nan, index=close.index, columns=close.columns)
    score = (total / active).where(elig)
    score.index = pd.to_datetime(score.index)
    return score


def sign_vectors(keys) -> list:
    return [dict(zip(keys, combo)) for combo in itertools.product((1.0, -1.0), repeat=len(keys))]


def main_effects(arms: dict) -> dict:
    """Factorial main effect of each factor's direction, from the arm table alone.

    The design is a full 2^6, so the other five signs are perfectly balanced between the
    '+' and '-' halves of any one factor: the difference of the two half-means is that
    factor's own contribution and nothing else. This is what says whether the whole
    no-hindsight gap above is one factor wearing six hats.
    """
    out = {}
    cagrs = {k: float(a["cagr"]) for k, a in arms.items()
             if isinstance(a.get("cagr"), (int, float)) and a.get("signs")}
    if not cagrs:
        return out
    for k in FACTOR_KEYS:
        hi = [c for key, c in cagrs.items() if arms[key]["signs"].get(k) == 1.0]
        lo = [c for key, c in cagrs.items() if arms[key]["signs"].get(k) == -1.0]
        if not hi or not lo:
            out[k] = {"pp_per_year": None, "n_plus": len(hi), "n_minus": len(lo)}
            continue
        eff = float(np.mean(hi) - np.mean(lo))
        out[k] = {"pp_per_year": round(eff * 100.0, 3),
                  "production_sign": "+" if SIGNS[k] > 0 else "-",
                  "n_plus": len(hi), "n_minus": len(lo)}
    return out


# --- gate ---------------------------------------------------------------------------
def gate(payload: dict) -> dict:
    decl = payload.get("declared") or {}
    checks = []
    for key, val in DECLARED.items():
        same = decl.get(key) == val
        checks.append({"check": "declared %s echoed" % key, "ok": bool(same),
                       "payload": decl.get(key), "module": val})
    arms = payload.get("arms") or {}
    n_expected = 2 ** len(SIGNS)
    traded = sum(1 for a in arms.values() if a.get("traded"))
    checks.append({"check": "every enumerated arm traded (r1261: an untraded arm passes everything)",
                   "ok": traded == n_expected == len(arms), "traded": traded,
                   "arms": len(arms), "expected": n_expected})
    cagrs = sorted(float(a["cagr"]) for a in arms.values()
                   if isinstance(a.get("cagr"), (int, float)))
    spread = float(cagrs[-1] - cagrs[0]) if len(cagrs) >= 2 else 0.0
    prod = arms.get(payload.get("production_key") or "")
    prod_cagr = float(prod["cagr"]) if prod and isinstance(prod.get("cagr"), (int, float)) else None
    if prod_cagr is None or len(cagrs) != len(arms):
        rank = None
    else:
        rank = 1 + sum(1 for c in cagrs if c > prod_cagr)
    n = len(cagrs)
    median = float(np.median(cagrs)) if cagrs else None
    if traded != n_expected or rank is None:
        verdict = "not_assessable_no_trade"
    elif spread < DEGENERATE_SPREAD:
        verdict = "not_assessable_degenerate"
    elif rank <= int(np.ceil(TOP_DECILE * n)):
        verdict = "signs_sit_at_the_sample_optimum"
    else:
        verdict = "signs_are_ordinary_choices"
    checks.append({"check": "rank recomputed from the arm table", "ok": rank is not None,
                   "rank": rank, "n": n, "spread": round(spread, 6)})
    return {"verdict": verdict, "rank": rank, "n": n, "median_cagr": median,
            "best_cagr": cagrs[-1] if cagrs else None, "worst_cagr": cagrs[0] if cagrs else None,
            "production_cagr": prod_cagr, "checks": checks,
            "all_ok": all(c["ok"] for c in checks)}


def agg(ser: pd.Series) -> dict:
    """One arm's headline numbers, from the engine's own return series."""
    m = F.metrics(ser, "arm")
    return {"cagr": m.get("cagr"), "sharpe": m.get("sharpe"), "maxdd": m.get("maxdd"),
            "bars": int(len(ser))}


# --- run ----------------------------------------------------------------------------
def run(limit: int | None = None) -> dict:
    t0 = time.time()
    close, openp, amt, feats = P.load_panel()
    elig = P.eligibility(close, amt)
    zs = z_mats(close, feats)
    print("panel %d bars x %d symbols loaded in %.1fs" % (len(close.index), close.shape[1],
                                                          time.time() - t0), flush=True)
    vecs = sign_vectors(FACTOR_KEYS)
    prod_key = "|".join("%s%s" % (k, "+" if SIGNS[k] > 0 else "-") for k in FACTOR_KEYS)
    if limit:
        vecs = vecs[:limit]
    arms, rows = {}, []
    for i, v in enumerate(vecs, 1):
        ta = time.time()
        key = "|".join("%s%s" % (k, "+" if v[k] > 0 else "-") for k in FACTOR_KEYS)
        sc = score_from(zs, v, close, elig)
        ser, turn, gap = V.fast_next_open(sc, close, openp, REBAL, n_hold=N_HOLD,
                                          cost=COST, start=START)
        a = agg(ser)
        a["turnover_per_rebal"] = round(float(turn), 4)
        a["traded"] = bool(float(turn) > 0.0 and len(ser) >= MIN_TRADED_BARS)
        a["signs"] = v
        arms[key] = a
        rows.append((key, a["cagr"]))
        print("  arm %2d/%d %s cagr=%s sharpe=%s (%.1fs)"
              % (i, len(vecs), key, a["cagr"], a["sharpe"], time.time() - ta), flush=True)
    effects = main_effects(arms)
    payload = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "universe": int(close.shape[1]),
        "question": "the six production signs are the full-sample IC signs (E207); how much of the "
                    "published headline is that choice, measured by running all 64 sign sets?",
        "declared": {k: (v if k != "signs" else dict(v)) for k, v in DECLARED.items()},
        "production_key": prod_key,
        "arms": arms,
        "marginal_by_factor": effects,
        "caveats": [
            "Reference engine only (no impact cost, no gap risk), flat sizing: the vol target/beta "
            "overlay is deliberately out so the only thing differing across arms is the signs.",
            "All 64 arms are in-sample by construction -- the distribution bounds what a sign "
            "chooser can reach, it is not an estimate of live return.",
            "ETF pool is today's listed set (survivorship), unchanged caveat.",
            "Zero-sign arms are excluded by construction: the enumeration is over directions, and "
            "a dropped factor is a different question (E207's IC floor already prices it).",
        ],
    }
    g = gate(payload)
    payload["summary"] = {
        "production_cagr": g["production_cagr"],
        "production_rank": g["rank"],
        "n_arms": g["n"],
        "production_percentile": (round(1.0 - (g["rank"] - 1) / max(1, g["n"] - 1), 4)
                                  if g["rank"] else None),
        "median_cagr": g["median_cagr"],
        "best_cagr": g["best_cagr"],
        "worst_cagr": g["worst_cagr"],
        "spread_cagr": (round(g["best_cagr"] - g["worst_cagr"], 6)
                        if g["best_cagr"] is not None else None),
        "share_positive": round(float(np.mean([1.0 if (a.get("cagr") or 0) > 0 else 0.0
                                               for a in arms.values()])), 4),
        "no_hindsight_gap_pp": (round((g["production_cagr"] - g["median_cagr"]) * 100.0, 3)
                                if g["production_cagr"] is not None and g["median_cagr"] is not None
                                else None),
        "elapsed_s": round(time.time() - t0, 1),
    }
    eff = [(k, v["pp_per_year"]) for k, v in effects.items() if v.get("pp_per_year") is not None]
    eff.sort(key=lambda kv: -abs(kv[1]))
    payload["summary"]["largest_effect_factor"] = eff[0][0] if eff else None
    payload["summary"]["largest_effect_pp"] = eff[0][1] if eff else None
    payload["summary"]["largest_share_of_gap"] = (
        round(abs(eff[0][1]) / abs(payload["summary"]["no_hindsight_gap_pp"]), 4)
        if eff and payload["summary"]["no_hindsight_gap_pp"] else None)
    payload["verdict"] = g["verdict"]
    payload["gate"] = {"rank": g["rank"], "all_ok": g["all_ok"], "checks": g["checks"]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": g["verdict"], **payload["summary"]}, ensure_ascii=False, indent=1),
          flush=True)
    return payload


def check() -> int:
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    g = gate(payload)
    print("verdict=%s rank=%s/%s stored=%s all_ok=%s"
          % (g["verdict"], g["rank"], g["n"], payload.get("verdict"), g["all_ok"]))
    for c in g["checks"]:
        if not c["ok"]:
            print("  RED %s -> %s" % (c["check"], {k: v for k, v in c.items() if k != "check"}))
    if not g["all_ok"] or g["verdict"] != payload.get("verdict"):
        return 1
    return 0


# --- selftest -----------------------------------------------------------------------
def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    vecs = sign_vectors(FACTOR_KEYS)
    leg("L1 the enumeration is 2^6 = 64 vectors, every entry +1/-1 (no dropped factor)",
        len(vecs) == 64 and len({tuple(sorted(v.items())) for v in vecs}) == 64
        and all(set(v.values()) <= {1.0, -1.0} for v in vecs))
    prod = dict(SIGNS)
    leg("L1b the production sign set is inside the enumeration", prod in vecs)

    # L2 construction equivalence: with one fixed sign vector the fast path must BE the
    # production score, else a difference between arms could be arithmetic, not signs.
    px, feats, elig, cols = P._synthetic(n_sym=30, n_bar=260, seed=5)
    feats6 = {k: px.pct_change().fillna(0.0) for k in FACTOR_KEYS}
    amt6 = pd.DataFrame(1e12, index=px.index, columns=cols)
    elig6 = P.eligibility(px, amt6)
    zs = z_mats(px, feats6)
    mine = score_from(zs, dict(SIGNS), px, elig6)
    their = P.score_face(px, elig6, feats6, pd.DataFrame({k: SIGNS[k] for k in FACTOR_KEYS},
                                                        index=px.index))
    d1 = float(np.nanmax(np.abs(mine.to_numpy(dtype=float) - their.to_numpy(dtype=float))))
    leg("L2 with production signs the fast path equals score_face (max|diff| < 1e-12)",
        np.isfinite(d1) and d1 < 1e-12, "max_diff=%.3e" % d1)
    prodsc = F.build_score(px, amt6, feats6)
    d2 = float(np.nanmax(np.abs(mine.to_numpy(dtype=float) - prodsc.to_numpy(dtype=float))))
    leg("L2b and equals the production build_score (max|diff| < 1e-12)",
        np.isfinite(d2) and d2 < 1e-12, "max_diff=%.3e" % d2)

    # L3 sign asymmetry: flipping every sign must give the mirrored score, not the same one
    mirrored = score_from(zs, {k: -SIGNS[k] for k in FACTOR_KEYS}, px, elig6)
    dm = float(np.nanmax(np.abs(mine.to_numpy(dtype=float) + mirrored.to_numpy(dtype=float))))
    leg("L3 flipping all six signs mirrors the score exactly", np.isfinite(dm) and dm < 1e-9,
        "max|a+b|=%.3e" % dm)

    # L4/L5 gate. The fixture places the production arm at an EXACT rank: arm "prod"
    # takes the cagr that sits at position `rank` of a strictly descending ladder, so the
    # gate's own "1 + count(strictly greater)" must return rank+1 from the table alone.
    def fake(rank_idx, n=64, spread=0.20):
        ladder = [0.20 - spread * i / (n - 1) for i in range(n)]
        arms = {}
        for i in range(n):
            if i == rank_idx:
                continue  # that rung belongs to the production arm, keeping the table at n arms
            arms["a%02d" % i] = {"cagr": ladder[i], "sharpe": 0.5, "maxdd": -0.2, "bars": 1500,
                                 "traded": True, "signs": {}}
        arms["prod"] = {"cagr": ladder[rank_idx], "sharpe": 0.5, "maxdd": -0.2, "bars": 1500,
                        "traded": True, "signs": {}}
        return {"declared": {k: (v if k != "signs" else dict(v)) for k, v in DECLARED.items()},
                "production_key": "prod", "arms": arms}

    leg("L4 gate names a top-of-table production arm as sitting at the sample optimum",
        gate(fake(0))["verdict"] == "signs_sit_at_the_sample_optimum")
    leg("L4b gate calls a mid-table production arm ordinary", gate(fake(31))["verdict"] == "signs_are_ordinary_choices")
    leg("L4c gate refuses to rule on a flattened table (all arms alike = nothing was measured)",
        gate(fake(0, spread=0.0))["verdict"] == "not_assessable_degenerate")
    dead = fake(0)
    for a in dead["arms"].values():
        a["traded"] = False
    leg("L4d gate refuses an untraded table", gate(dead)["verdict"] == "not_assessable_no_trade")
    bad = fake(0)
    bad["declared"]["n_hold"] = 5
    leg("L5 gate REDs when the payload was built under different constants", not gate(bad)["all_ok"])
    leg("L5b gate recomputes the rank instead of trusting a typed one", gate(fake(10))["rank"] == 11)
    missing = fake(0)
    missing["arms"].pop(missing["production_key"])
    leg("L5c a production arm missing from the table is not assessable",
        gate(missing)["verdict"] == "not_assessable_no_trade")

    # L6 main effect: a table where exactly one factor's direction pays must give that
    # factor the whole effect and every other factor ~0 (the other five signs are balanced).
    table = {}
    for v in vecs:
        table["k" + "".join("+" if v[k] > 0 else "-" for k in FACTOR_KEYS)] = {
            "cagr": 0.10 * v[FACTOR_KEYS[0]], "traded": True, "signs": dict(v)}
    eff6 = main_effects(table)
    leg("L6 only the factor that actually pays shows a main effect",
        abs(eff6[FACTOR_KEYS[0]]["pp_per_year"] - 20.0) < 1e-9
        and all(abs(eff6[k]["pp_per_year"]) < 1e-9 for k in FACTOR_KEYS[1:]),
        "mom=%.3f others=%s" % (eff6[FACTOR_KEYS[0]]["pp_per_year"],
                                [eff6[k]["pp_per_year"] for k in FACTOR_KEYS[1:]]))

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
    ap.add_argument("--limit", type=int, default=None,
                    help="run only the first N arms (timing probe; never a published face)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.mode == "check":
        return check()
    run(limit=a.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())