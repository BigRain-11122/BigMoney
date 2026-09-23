"""screening/pbo.py — CSCV PBO, backtest-science v2 D4 (T-2026-09-23-02-P1, deliverable 2/7).

Authority: research/BACKTEST_SCIENCE.md §4 (O-20260923-2215).
Combinatorially Symmetric Cross-Validation (Lopez de Prado & Lewis 2015):

  - full history split into S=8 contiguous time blocks (frozen split rule below)
  - all C(8,4)=70 combinations: 4 blocks = IS, complement 4 blocks = OOS
  - per combination: rank trials by IS Sharpe, take the IS-best trial, read its
    OOS relative rank  omega = (oos_rank - 1) / (N - 1)   (1 = best OOS)
  - PBO = fraction of combinations with omega > 0.5
    (probability that the IS-best trial lands BELOW the OOS median)

Bands (frozen per §4): PBO <= 0.25 register-eligible; 0.25 < PBO <= 0.5
observe (no registration); PBO > 0.5 fail.

FROZEN CSCV PARAMETERS (batch preregs must reference these defaults; any deviation
= new prereg + 7-day veto window per BACKTEST_SCIENCE.md):
  S = 8 blocks, contiguous, bounds[i] = i*T//8 (sizes differ by at most 1)
  IS = exactly 4 blocks (C(8,4)=70 combinations, exhaustive, zero RNG)
  metric = annualized Sharpe (252) on concatenated block rows, time-ordered
  IS-best tie-break = first column (numpy argmax order), deterministic
  OOS ties = average rank; degenerate all-tied trials give omega=0.5
  min history = 8 x MIN_ROWS_PER_BLOCK (Sharpe on a 20-row block is already thin)

Discipline: pure numpy/pandas, zero new dependencies; deterministic for a fixed
input (exhaustive enumeration, no resampling noise). Judgement numbers come from
pbo_verdict() — no hand-copied bands in batch scripts.

O-20260923-2250 amendment-9 review (audit C family): CSCV core stays frozen on the
complete-matrix semantic (staggered-start handling = explicit caller decision,
guarded in align_returns — dead trials refused, >50% silent truncation refused,
per-column coverage disclosed via attrs); no masked-mode extension until a real
consumer needs it (YAGNI; any core-math change = new prereg per BACKTEST_SCIENCE).

Usage:
  python screening/pbo.py selftest   # offline synthetic assertions, zero network
  python screening/pbo.py report    # live-fire: registered-book CSCV demo
  from screening.pbo import cscv_pbo, pbo_verdict
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
TRADERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "firm", "traders")

PERIODS_PER_YEAR = 252.0
N_BLOCKS = 8                 # frozen per BACKTEST_SCIENCE.md §4
MIN_ROWS_PER_BLOCK = 20      # frozen: T >= 160 for CSCV


# ---------------------------------------------------------------- frozen block split

def block_bounds(t: int, n_blocks: int = N_BLOCKS) -> list[int]:
    """Contiguous floor-division split; block i = rows [b[i], b[i+1]). Sizes differ by <= 1."""
    t = int(t)
    if t < n_blocks * MIN_ROWS_PER_BLOCK:
        raise ValueError(f"CSCV needs T >= {n_blocks * MIN_ROWS_PER_BLOCK} rows "
                         f"(8 blocks x {MIN_ROWS_PER_BLOCK}); got T={t}")
    return [i * t // n_blocks for i in range(n_blocks + 1)]


def _combos(n_blocks: int = N_BLOCKS) -> list[tuple[int, ...]]:
    """All C(S, S/2) IS-block combinations, exhaustive (70 for S=8). Zero RNG."""
    if n_blocks % 2:
        raise ValueError("CSCV needs an even block count")
    return list(itertools.combinations(range(n_blocks), n_blocks // 2))


# ---------------------------------------------------------------- core CSCV

def _block_sharpe(mat: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Annualized Sharpe per trial on the given row positions (positional, no alignment traps)."""
    x = mat[rows, :]
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = np.where(sd > 0, mu / sd, 0.0)  # zero-variance block -> 0 (screening/overfit convention)
    return sh * math.sqrt(PERIODS_PER_YEAR)


def cscv_pbo(returns: pd.DataFrame, n_blocks: int = N_BLOCKS) -> dict:
    """CSCV PBO over a T x N daily-returns matrix (columns = trials, index = dates).

    Returns the full computation record (pbo, verdict, per-combination omegas) so
    batch reports can disclose everything; no hand-copied numbers downstream.
    """
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame (rows=dates, cols=trials)")
    if returns.isna().any().any():
        raise ValueError("NaN in returns matrix — align/complete the panel first "
                         "(align_returns helper); CSCV needs a complete matrix")
    t, n = returns.shape
    if n < 2:
        raise ValueError("PBO needs >= 2 trials (cross-trial ranking is the object)")
    bounds = block_bounds(t, n_blocks)
    mat = returns.to_numpy(dtype=float)
    combos = _combos(n_blocks)
    all_rows = np.arange(t)
    omegas = []
    records = []
    for j in combos:
        jc = tuple(b for b in range(n_blocks) if b not in j)
        is_rows = np.concatenate([np.arange(bounds[b], bounds[b + 1]) for b in j])
        oos_rows = np.concatenate([np.arange(bounds[b], bounds[b + 1]) for b in jc])
        is_sh = _block_sharpe(mat, is_rows)
        oos_sh = _block_sharpe(mat, oos_rows)
        best = int(np.argmax(is_sh))                      # first-occurrence tie-break, frozen
        # average-method rank: 1 = best OOS; ties share the mean rank
        better = (oos_sh > oos_sh[best]).sum()
        tied = (oos_sh == oos_sh[best]).sum()
        rank = 1.0 + float(better) + (float(tied) - 1.0) / 2.0
        omega = (rank - 1.0) / (n - 1.0)
        omegas.append(omega)
        records.append({"is_blocks": list(j), "is_best_trial": returns.columns[best],
                        "oos_rank": round(rank, 2), "omega": round(omega, 4)})
    omegas_arr = np.asarray(omegas)
    pbo = float((omegas_arr > 0.5).mean())
    return {
        "pbo": round(pbo, 4),
        "verdict": pbo_verdict(pbo),
        "n_trials": int(n),
        "n_rows": int(t),
        "n_combinations": len(combos),
        "n_blocks": n_blocks,
        "block_bounds": bounds,
        "omega_mean": round(float(omegas_arr.mean()), 4),
        "omega_median": round(float(np.median(omegas_arr)), 4),
        "omega_p05": round(float(np.percentile(omegas_arr, 5)), 4),
        "omega_p95": round(float(np.percentile(omegas_arr, 95)), 4),
        "per_combination": records,
        "bands_frozen": {"register_eligible": "pbo <= 0.25", "observe": "0.25 < pbo <= 0.5",
                         "fail": "pbo > 0.5"},
    }


def pbo_verdict(pbo: float) -> str:
    """D4 band mapping (frozen): <=0.25 eligible, >0.5 fail, middle observe."""
    if pbo <= 0.25:
        return "register_eligible"
    if pbo > 0.5:
        return "fail"
    return "observe"


# ---------------------------------------------------------------- helpers

def align_returns(series_by_trial: dict, max_truncation: float = 0.5) -> pd.DataFrame:
    """Date-intersect per-trial return series -> complete matrix.

    O-2250 amendment-9 review (audit C family, silent-truncation sin): intersection is
    the only CSCV-legal alignment here (the core requires a complete matrix, frozen),
    so instead of letting one late-start trial silently shrink the WHOLE book we
    (a) never silently skip a trial column (None/empty = caller error, refused), and
    (b) refuse when the intersection keeps < max_truncation of any column's own rows —
    staggered-start panels must drop late trials EXPLICITLY in the caller (disclosed),
    never via silent whole-matrix truncation. Per-column coverage is disclosed via
    DataFrame.attrs["coverage"] for batch reports.
    """
    if not isinstance(series_by_trial, dict) or len(series_by_trial) < 2:
        raise ValueError("need >= 2 series (dict of trial -> return Series)")
    dead = sorted(k for k, v in series_by_trial.items() if v is None or len(v) == 0)
    if dead:  # never symbol-dropping: dead trials are a caller decision, not a silent skip
        raise ValueError(f"empty/None trial series refused: {dead} — exclude them "
                         "explicitly in the caller if intended (disclosed)")
    df = pd.DataFrame(series_by_trial)
    own_rows = df.notna().sum()                       # per-column coverage pre-intersection
    df = df.dropna(how="any")
    kept_frac = df.shape[0] / own_rows.astype(float)
    worst_trial = str(kept_frac.idxmin())
    worst = float(kept_frac.min())
    if worst < float(max_truncation):
        raise ValueError(f"intersection keeps only {worst:.0%} of trial '{worst_trial}' "
                         f"rows (T={df.shape[0]} common vs max own rows "
                         f"{int(own_rows.max())}) — staggered-start panel; drop late "
                         f"trials explicitly or pass max_truncation with disclosure "
                         f"(silent whole-matrix truncation refused, audit C family)")
    if df.shape[0] < N_BLOCKS * MIN_ROWS_PER_BLOCK:
        raise ValueError(f"aligned matrix too thin (T={df.shape[0]}) — insufficient overlap")
    df.attrs["coverage"] = {
        "t_common": int(df.shape[0]),
        "per_trial_own_rows": {k: int(v) for k, v in own_rows.items()},
        "per_trial_kept_fraction": {k: round(float(v), 4) for k, v in kept_frac.items()},
        "max_truncation": float(max_truncation),
    }
    return df


def equity_to_daily_returns(equity: pd.Series) -> pd.Series:
    """Mark-to-market equity curve -> daily returns (drops the seed row)."""
    return equity.pct_change().dropna()


# ---------------------------------------------------------------- selftest

class _LCG:
    """Deterministic 64-bit LCG (same family as scripts/science_gates.py)."""

    def __init__(self, seed: int):
        self._s = (int(seed) ^ 0x9E3779B97F4A7C15) & ((1 << 64) - 1)

    def next(self) -> float:
        self._s = (self._s * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return (self._s >> 11) / float(1 << 53)


def _noise_matrix(t: int, n: int, seed: int, signal_col: int | None = None,
                  daily_sr: float = 0.0, front_loaded: int | None = None,
                  front_sr: float = 0.0, back_sr: float = 0.0) -> pd.DataFrame:
    """Deterministic synthetic trials: unit-variance noise, optional embedded edge.

    PITFALL (found by the selftest itself): do NOT mean-center columns — a full-column
    centering forces sum=0, making any two disjoint block means EXACT negatives, so the
    IS-best trial is mechanically the OOS-worst (PBO=1.0 on pure noise). Real equity
    returns are uncentered; synthetic panels must be too. Scale only.
    """
    rng = _LCG(seed)
    cols = {}
    for c in range(n):
        xs = [rng.next() * 2.0 - 1.0 for _ in range(t)]
        sd = math.sqrt(sum(x * x for x in xs) / (t - 1))
        unit = [x / sd for x in xs]
        if c == signal_col and signal_col is not None:
            unit = [x + daily_sr for x in unit]
        cols[f"trial_{c}"] = unit
    if front_loaded is not None:
        xs = cols[f"trial_{front_loaded}"]
        half = t // 2
        for i in range(t):
            xs[i] += front_sr if i < half else back_sr
        cols[f"trial_{front_loaded}"] = xs
    return pd.DataFrame(cols)


def selftest() -> int:
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # frozen block split: contiguous, exhaustive coverage, sizes within 1
    for t in (160, 1600, 1631):
        b = block_bounds(t)
        ok(f"block_bounds T={t}: contiguous & exhaustive",
           b[0] == 0 and b[-1] == t and all(b[i + 1] > b[i] for i in range(len(b) - 1)))
        ok(f"block_bounds T={t}: sizes differ by <= 1",
           max(b[i + 1] - b[i] for i in range(len(b) - 1)) -
           min(b[i + 1] - b[i] for i in range(len(b) - 1)) <= 1)

    # combinations: C(8,4)=70, closed under complement, each block in exactly C(7,3)=35
    combos = _combos()
    ok("combos = 70 for S=8", len(combos) == 70)
    cset = set(combos)
    ok("combos closed under complement",
       all(tuple(sorted(set(range(8)) - set(j))) in cset for j in combos))
    ok("each block appears in exactly 35 combos",
       all(sum(1 for j in combos if b in j) == 35 for b in range(8)))

    # genuine persistent edge among noise -> low PBO
    edge = _noise_matrix(1600, 12, seed=7, signal_col=0, daily_sr=2.0 / math.sqrt(252))
    res_edge = cscv_pbo(edge)
    ok(f"genuine edge trial -> PBO low ({res_edge['pbo']}, eligible)", res_edge["pbo"] <= 0.25)
    ok("genuine edge verdict = register_eligible",
       res_edge["verdict"] == "register_eligible")

    # pure noise -> PBO must not read as skill (structural band, single disclosed seed)
    noise = _noise_matrix(1600, 12, seed=12)
    res_noise = cscv_pbo(noise)
    ok(f"pure noise PBO in structural band 0.15-0.85 ({res_noise['pbo']})",
       0.15 <= res_noise["pbo"] <= 0.85)

    # front-loaded lucky trial (IS hero, OOS zero) -> PBO > 0.5 fail
    hero = _noise_matrix(1600, 12, seed=21, front_loaded=0,
                         front_sr=0.12, back_sr=-0.12)
    res_hero = cscv_pbo(hero)
    ok(f"front-loaded IS-hero -> PBO > 0.5 ({res_hero['pbo']})", res_hero["pbo"] > 0.5)
    ok("IS-hero verdict = fail", res_hero["verdict"] == "fail")

    # determinism: exhaustive enumeration, identical on repeat
    ok("CSCV deterministic on repeat", cscv_pbo(edge) == res_edge)

    # degenerate ties: identical trials carry no ranking information -> omega=0.5, PBO=0
    flat = pd.DataFrame({"a": [0.01] * 1600, "b": [0.01] * 1600})
    res_flat = cscv_pbo(flat)
    ok("identical trials -> PBO 0.0 (no differentiation, structural)", res_flat["pbo"] == 0.0)

    # verdict band boundaries (frozen §4)
    ok("verdict 0.25 = register_eligible", pbo_verdict(0.25) == "register_eligible")
    ok("verdict 0.26 = observe", pbo_verdict(0.26) == "observe")
    ok("verdict 0.50 = observe (fail strictly above)", pbo_verdict(0.50) == "observe")
    ok("verdict 0.51 = fail", pbo_verdict(0.51) == "fail")

    # input guards
    for bad, name in ((pd.DataFrame({"a": [np.nan] * 200, "b": [0.0] * 200}), "NaN matrix rejected"),
                      (pd.DataFrame({"a": [0.0] * 200}, index=range(200)), "N=1 rejected"),
                      (pd.DataFrame({"a": [0.0] * 100, "b": [0.0] * 100}), "short history rejected")):
        try:
            cscv_pbo(bad)
            ok(name, False)
        except ValueError:
            ok(name, True)

    # align helper: date intersection only
    idx = pd.bdate_range("2020-01-01", periods=300)
    s_a = pd.Series(0.01, index=idx[:250])
    s_b = pd.Series(0.02, index=idx[50:])
    aligned = align_returns({"a": s_a, "b": s_b})
    ok("align_returns intersects dates (200 = 250-50 overlap)", aligned.shape == (200, 2))
    cov = aligned.attrs.get("coverage", {})
    ok("align_returns discloses per-column coverage",
       cov.get("t_common") == 200 and cov.get("per_trial_own_rows") == {"a": 250, "b": 250}
       and cov.get("per_trial_kept_fraction") == {"a": 0.8, "b": 0.8})

    # amendment-9 guards (audit C family): dead trials refused, silent truncation refused
    try:
        align_returns({"a": s_a, "b": s_b, "dead": None})
        ok("align_returns refuses None trial (never silently skipped)", False)
    except ValueError:
        ok("align_returns refuses None trial (never silently skipped)", True)
    idx2 = pd.bdate_range("2020-01-01", periods=2000)
    s_late = pd.Series(0.01, index=idx2[800:])   # starts at row 800: 200/1000 = 20% kept
    try:
        align_returns({"a": pd.Series(0.01, index=idx2[:1000]), "c": s_late})
        ok("align_returns refuses >50% silent truncation by late trial", False)
    except ValueError as e:
        ok("align_returns refuses >50% silent truncation by late trial",
           "truncation refused" in str(e))
    ok("align_returns accepts explicit low-truncation call (disclosed caller choice)",
       align_returns({"a": pd.Series(0.01, index=idx2[:1000]), "c": s_late},
                     max_truncation=0.1).shape[0] == 200)

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\npbo selftest: {len(checks) - n_fail}/{len(checks)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


# ---------------------------------------------------------------- live-fire report

def _registered_returns() -> tuple[pd.DataFrame, dict]:
    """Reproduce each registered trader's full-history equity via the paper-anchor
    machinery (SIGNAL_BUILDERS + ExitPatch + evidence_cutoff truncation) and verify
    the IS/OOS segment metrics match the registered backtest evidence — the matrix
    IS the registered evidence, not a new trial. Mirrors live.paper.anchor_gate.
    """
    from engine import run_backtest
    from live.paper import (OOS_START, SIGNAL_BUILDERS, ExitPatch, _evidence_matches,
                            build_panels, evidence_cutoff, load_core, seg_metrics)

    prices_full = load_core()
    traders = sorted(f for f in os.listdir(TRADERS_DIR)
                     if f.endswith(".json") and not f.startswith("_"))
    if len(traders) < 2:
        raise RuntimeError("need >= 2 registered traders for book-level CSCV")
    rets: dict[str, pd.Series] = {}
    validity: dict[str, dict] = {}
    for fname in traders:
        with open(os.path.join(TRADERS_DIR, fname), encoding="utf-8") as fh:
            t = json.load(fh)
        tid = t["id"]
        # canonical book filter (same as the anchor gate): registered = params.entry
        # contract in SIGNAL_BUILDERS; scaffolding seeds (e.g. TREND-001, no entry
        # contract, zero evidence) are not registered traders
        if t.get("params", {}).get("entry") not in SIGNAL_BUILDERS:
            continue
        cutoff = evidence_cutoff(t, prices_full)
        ps = pd.Timestamp(cutoff)
        prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
        P = build_panels(prices)
        entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params = {k: v for k, v in t["params"].items() if k != "entry"}
        with ExitPatch(t.get("exit_overrides")):
            res = run_backtest(prices, params, entry_signal=entry, exit_signal=(entry <= 0))
        idx = P["close"].index
        eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
        n_trades = res["metrics"]["num_trades"]
        oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
        got = {"in_sample": {**seg_metrics(eq[eq.index < OOS_START]),
                             "trades": n_trades - oos_trades},
               "out_sample": {**seg_metrics(eq, OOS_START), "trades": oos_trades}}
        want = t["backtest"]
        checks = {"in_sample": _evidence_matches(got["in_sample"], want["in_sample"]),
                  "out_sample": _evidence_matches(got["out_sample"], want["out_sample"])}
        if not all(checks.values()):
            raise RuntimeError(f"{tid}: reproduced curve does NOT match registered evidence "
                               f"({checks}) — anchor drift, abort (do not fake the matrix)")
        rets[tid] = equity_to_daily_returns(eq)
        validity[tid] = {"cutoff": cutoff, "is_match": bool(checks["in_sample"]),
                         "oos_match": bool(checks["out_sample"]),
                         "full_sharpe": seg_metrics(eq)["sharpe"]}
    matrix = align_returns(rets)
    return matrix, validity


def report() -> int:
    matrix, validity = _registered_returns()
    res = cscv_pbo(matrix)
    out_path = os.path.join(RESULTS_DIR, "pbo_cscv_v1.json")
    payload = {
        "module": "screening/pbo.py",
        "authority": "research/BACKTEST_SCIENCE.md §4 D4 (O-20260923-2215), T-02 deliverable 2/7",
        "frozen_params": {
            "n_blocks": N_BLOCKS, "is_blocks": 4, "combinations": "C(8,4)=70 exhaustive",
            "split_rule": "bounds[i]=i*T//8 contiguous", "metric": "annualized Sharpe 252",
            "is_best_tiebreak": "first argmax column", "oos_ties": "average rank",
            "min_rows_per_block": MIN_ROWS_PER_BLOCK,
            "bands": {"register_eligible": "<=0.25", "observe": "(0.25,0.5]", "fail": ">0.5"},
        },
        "live_fire": {
            "scope": "book-level CSCV across registered traders — PIPELINE VALIDATION DEMO",
            "NOT": ("this is NOT the G2.5 per-family retro (T-02 deliverable 4, due before the "
                    "2026-10-31 promotion gate) — G2.5 runs PBO per candidate family against "
                    "its own prereg trial grid"),
            "validity_gate": ("per trader: reproduced full-history curve seg-metrics match the "
                              "registered backtest evidence at anchor tolerances -> the matrix "
                              "IS the registered evidence (6 engine runs = anchor-gate "
                              "reproductions, same as smoke/paper run each round; NOT new "
                              "trials, trials ledger N unchanged)"),
            "traders": validity,
            "matrix": {"T": int(matrix.shape[0]), "N": int(matrix.shape[1]),
                       "span": [str(matrix.index[0].date()), str(matrix.index[-1].date())],
                       "alignment": (matrix.attrs.get("coverage") or
                                      "attrs unavailable (pandas version)")},
            "cscv": res,
            "interpretation": ("book-level PBO reads the time-stability of the members' relative "
                              "ranking under CSCV block rotations; P-5B already established "
                              "regime dependence book-wide, so a high book PBO would be "
                              "consistent evidence, not a surprise"),
        },
        "generated": _now(),
    }
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print(f"report -> {out_path}")
    print(json.dumps({"pbo": res["pbo"], "verdict": res["verdict"],
                      "n": res["n_trials"], "T": res["n_rows"],
                      "omega_mean": res["omega_mean"]}, ensure_ascii=False))
    return 0


def _now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    raise SystemExit(selftest() if cmd == "selftest" else report() if cmd == "report" else 0)
