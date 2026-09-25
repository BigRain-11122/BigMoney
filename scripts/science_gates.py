"""scripts/science_gates.py — Backtest-science v2 shared gates library (T-2026-09-23-02-P1, deliverable 1).

Authority: research/BACKTEST_SCIENCE.md (O-20260923-2215). Single source for:
  D1  skill_line_v2 = max(passive+0.10, mu_null + sigma_null*sqrt(2*ln N_eff))   (§1)
  D1  DSR >= 0.95 registration gate (Bailey & Lopez de Prado 2014 approximation)  (§1)
  D3  stationary bootstrap 95% CI (block=10d, 1000 resamples, prereg seed family) (§3)

Discipline: gate/judgement numbers MUST come from here — no hand-copied constants in batch scripts.
All data read from results/*.json is data-driven (no frozen numbers); formulas are frozen per
BACKTEST_SCIENCE.md (revision = prereg + 7-day veto window).

Usage:
  python scripts/science_gates.py selftest      # offline synthetic assertions, zero network
  python scripts/science_gates.py report       # live reading -> results/science_gates_v2.json
  import scripts.science_gates as sg           # library use
"""
from __future__ import annotations

import glob
import json
import math
import os

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
PERIODS_PER_YEAR = 252.0
EULER_GAMMA = 0.5772156649015329


# ---------------------------------------------------------------- ledger (D1: N_eff)

def ledger_head(results_dir: str = RESULTS_DIR) -> dict:
    """Chain head of the trials ledger: the results JSON with the largest cumulative total.

    Every batch JSON carries {"trials_ledger": {"prev_total", "batch_trials", "total", ...}}.
    The chain head is data-driven (max total across files), never a hand-copied number.
    """
    head = {"total": 0, "file": None, "note": None}
    # r112: recursive scan -- shortline-family batch files carry trials_ledger
    # blocks invisible to a top-level-only glob, silently diverging this scanner
    # from xlib_synth.chain_head_total's two-face scan (the r110 same-base
    # double-count root cause). Recursive glob unifies the visible face.
    for path in sorted(glob.glob(os.path.join(results_dir, "**", "*.json"),
                                 recursive=True)):
        try:
            with open(path, encoding="utf-8") as fh:
                tl = json.load(fh).get("trials_ledger")
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        if isinstance(tl, dict) and isinstance(tl.get("total"), (int, float)):
            if tl["total"] > head["total"]:
                head = {"total": int(tl["total"]), "file": os.path.basename(path),
                        "note": tl.get("note")}
    return head


def n_eff(batch_cells: int, results_dir: str = RESULTS_DIR) -> int:
    """D1: N_eff = ledger chain head + current batch cell count (line rises with the ledger)."""
    return int(ledger_head(results_dir)["total"]) + int(batch_cells)


# ---------------------------------------------------------------- null pool (D1: mu/sigma)

def null_sharpes(results_dir: str = RESULTS_DIR) -> dict:
    """Collect random-null FULL-PERIOD annualized Sharpe values across batch schemas.

    Extensible schema registry: each entry knows how to mine one batch family's null runs.
    Coverage is reported honestly — unparseable batch files are listed, never silently dropped.
    """
    values: list[float] = []
    parsed: list[str] = []

    def _load(name: str):
        path = os.path.join(results_dir, name)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    # p2_calibration.json: families[random*].runs[].full.sharpe  (n=100 engine-exit null family +
    # n=20 random-exit family = the project's calibration-grade null population)
    d = _load("p2_calibration.json")
    if d:
        for fam_name, fam in (d.get("families") or {}).items():
            if "random" not in fam_name.lower():
                continue
            runs = fam.get("runs") if isinstance(fam, dict) else None
            if isinstance(runs, dict):
                runs = list(runs.values())
            for run in runs or []:
                full = run.get("full") or {} if isinstance(run, dict) else {}
                sr = full.get("sharpe")
                if isinstance(sr, (int, float)) and math.isfinite(sr):
                    values.append(float(sr))
        if values:
            parsed.append("p2_calibration.json:families[random*].runs[].full.sharpe")

    coverage = {
        "n_values": len(values),
        "schemas_parsed": parsed,
        "known_unparsed": [
            "p1_screen.json:random_null (stores oos_sharpes array + p95 summaries only; "
            "full-period null sharpes not persisted -> out of coverage, disclosed)",
        ],
        "mu": (sum(values) / len(values)) if values else None,
        "sigma": (_pstdev(values) if len(values) > 1 else None),
    }
    return {"values": values, "coverage": coverage}


def _pstdev(xs: list[float]) -> float:
    mu = sum(xs) / len(xs)
    return math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1))


# ---------------------------------------------------------------- passive baselines (D1)

def passive_baseline(pool: str = "core48", results_dir: str = RESULTS_DIR) -> float:
    """Per-pool frozen passive baseline: strict (max) of EW-hold vs monthly-rebalance Sharpe.

    core48 values are read live from results/p2_calibration.json (data-driven). New pools must
    register their calibration file here — no silent cross-pool reuse.
    """
    if pool == "stock_b_layer":
        # P4_EXT_TILT additive pool (spec SS4): strict-max of this batch's own
        # monthly-EW + quarterly-EW passive nulls, read from the product file.
        # core48 path below untouched (additive branch, T-02 pattern).
        path = os.path.join(results_dir, "shortline_p4_ext_tilt.json")
        if not os.path.exists(path):
            raise KeyError(f"stock_b_layer passive not on file yet "
                           f"({path}) — run P4_EXT_TILT finalize first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("stock_ew_monthly", "stock_ew_quarterly"):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                          "shortline_p4_ext_tilt.json — schema drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "cta_futures":
        # CTA_P1 additive pool (research/CTA_P1.md SS4): strict-max of this
        # batch's own two passive long baselines (r20 / monthly rebalance),
        # read from the product file — futures domain never borrows core48
        # or stock-domain passives (no silent cross-pool reuse).
        path = os.path.join(results_dir, "shortline_cta_p1.json")
        if not os.path.exists(path):
            raise KeyError(f"cta_futures passive not on file yet "
                          f"({path}) — run CTA_P1 phase-1 write first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("passive_long_r20", "passive_long_monthly"):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                           "shortline_cta_p1.json — schema drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "cta_futures_noau":
        # CTA_P2_NOAU additive pool (research/CTA_P2_NOAU.md SS4): strict-max of
        # THIS batch's own two passive long baselines (r20 / monthly) on the
        # 8-variety no-AU panel — read from the product file; never borrows the
        # 9-variety cta_futures passives (AU must stay out of the line).
        path = os.path.join(results_dir, "shortline_cta_p2_noau.json")
        if not os.path.exists(path):
            raise KeyError(f"cta_futures_noau passive not on file yet "
                           f"({path}) — run CTA_P2_NOAU phase-1 write first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("passive_long_r20", "passive_long_monthly"):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                           "shortline_cta_p2_noau.json — schema drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "im_ic_pair":
        # IM_IC_PAIR additive pool (research/IM_IC_PAIR.md SS4): the only
        # passive on a two-leg mean-zero pair face is FLAT (no position) --
        # constant 0.0, frozen in the prereg; never borrows cta/core48
        # passives (no silent cross-pool reuse).
        return 0.0
    if pool == "t18_deep_axis":
        # T18_DEEP_REVAL additive pool (research/DEEP_AXIS_REVALIDATION.md SS3):
        # strict-max of the deep axis's OWN two passives (EW48 monthly rebal +
        # buy-hold, panel_start..evidence_cutoff window), read from the nulls-
        # stage product file; never borrows core48 passives (no silent
        # cross-pool reuse). R53 acceptance = live dual-pool probe recorded
        # in t18_deep_nulls.json (r53_dual_pool_probe), not selftest alone.
        path = os.path.join(results_dir, "shortline", "t18_deep_nulls.json")
        if not os.path.exists(path):
            raise KeyError(f"t18_deep_axis passive not on file yet ({path}) "
                           "— run scripts/t18_deep_axis.py nulls first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("ew48_monthly_rebal", "ew48_buyhold"):
            sr = ((pas.get(name) or {}).get("full_axis") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in t18_deep_nulls.json "
                           "— schema drift, fix nulls-stage writer")
        return max(cands)  # strict = harder line
    path = os.path.join(results_dir, "p2_calibration.json")
    if pool != "core48" or not os.path.exists(path):
        raise KeyError(f"no frozen passive calibration on file for pool '{pool}' — "
                       "register a calibration batch first (BACKTEST_SCIENCE.md §1)")
    with open(path, encoding="utf-8") as fh:
        fams = (json.load(fh).get("families") or {})
    cands = []
    for fam_name, fam in fams.items():
        if "passive" not in fam_name.lower():
            continue
        runs = fam.get("runs") if isinstance(fam, dict) else None
        if isinstance(runs, dict):
            runs = list(runs.values())
        for run in runs or []:
            sr = (run.get("full") or {}).get("sharpe") if isinstance(run, dict) else None
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
    if not cands:
        raise KeyError("passive family not found in p2_calibration.json — schema drift, fix collector")
    return max(cands)  # strict = harder line


def skill_line_v2(batch_cells: int, pool: str = "core48", results_dir: str = RESULTS_DIR,
                  null_pool: dict | None = None) -> dict:
    """D1: skill_line_v2 = max(passive+0.10, mu_null + sigma_null*sqrt(2*ln N_eff)).

    Returns the line plus every input so batch reports can disclose the whole computation.
    """
    if null_pool is None:
        null_pool = null_sharpes(results_dir)
    cov = null_pool["coverage"]
    if cov["mu"] is None or cov["sigma"] is None or cov["n_values"] < 30:
        raise ValueError(f"null pool too thin ({cov['n_values']} values) — extend collector first")
    n = n_eff(batch_cells, results_dir)
    extreme = cov["sigma"] * math.sqrt(2.0 * math.log(max(n, 2)))
    null_term = cov["mu"] + extreme
    passive = passive_baseline(pool, results_dir)
    passive_term = passive + 0.10
    return {
        "n_eff": n,
        "line": round(max(passive_term, null_term), 4),
        "passive_term": round(passive_term, 4),
        "null_term": round(null_term, 4),
        "mu_null": round(cov["mu"], 4),
        "sigma_null": round(cov["sigma"], 4),
        "pool": pool,
        "ledger_head": ledger_head(results_dir),
    }


# ---------------------------------------------------------------- DSR (D1 registration gate)

def _norm_ppf(p: float) -> float:
    """Acklam's inverse normal CDF approximation (no scipy dependency)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p out of range")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01, 1.0]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549796539399786e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+b[5])


def _norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def deflated_sharpe_ratio(returns, n_trials: int, var_null_sr: float | None = None,
                          periods_per_year: float = PERIODS_PER_YEAR) -> dict:
    """DSR (Bailey & Lopez de Prado 2014 practical approximation).

    DSR = Phi( (SR_hat - SR_star) / sigma_SR ),  sigma_SR = sqrt((1 - g3*SR + (g4-1)/4*SR^2)/(T-1))
    SR_star = expected max SR of N null trials = sqrt(V[SR_null]) *
              ((1-gamma)*Phi^-1(1-1/N) + gamma*Phi^-1(1-1/(N*e)))   (Euler-Mascheroni gamma)
    SR_hat is the NON-annualized per-period Sharpe (daily); annualized value returned for report.
    var_null_sr defaults to the estimated SR variance when the null population is unavailable.
    """
    xs = [float(x) for x in returns]
    t = len(xs)
    if t < 20:
        raise ValueError("DSR needs >= 20 returns")
    mu = sum(xs) / t
    var = sum((x - mu) ** 2 for x in xs) / (t - 1)
    sd = math.sqrt(var)
    if sd == 0:
        raise ValueError("zero-variance returns")
    sr = mu / sd  # per-period Sharpe
    m2 = sum(x ** 2 for x in xs) / t
    m3 = sum(x ** 3 for x in xs) / t
    m4 = sum(x ** 4 for x in xs) / t
    g3 = m3 / sd ** 3            # skewness
    g4 = m4 / sd ** 4            # kurtosis (plain, not excess)
    denom = 1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr * sr
    denom = max(denom, 1e-12)
    sigma_sr = math.sqrt(denom / (t - 1))
    n = max(int(n_trials), 2)
    v_null = var_null_sr if (var_null_sr and var_null_sr > 0) else (sigma_sr * sigma_sr)
    n_e = math.e
    z1 = _norm_ppf(1.0 - 1.0 / n)
    z2 = _norm_ppf(1.0 - 1.0 / (n * n_e)) if n * n_e > 1.0 else 0.0
    sr_star = math.sqrt(v_null) * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)
    dsr = _norm_cdf((sr - sr_star) / sigma_sr)
    return {
        "dsr": round(dsr, 6),
        "sr_annualized": round(sr * math.sqrt(periods_per_year), 4),
        "sr_star": round(sr_star, 6),
        "sigma_sr": round(sigma_sr, 6),
        "n_trials": n,
        "T": t,
        "skew": round(g3, 4),
        "kurtosis": round(g4, 4),
    }


def dsr_from_stats(sr_annualized: float, sigma_sr: float, n_trials: int,
                   periods_per_year: float = PERIODS_PER_YEAR) -> dict:
    """T-02 5/7: DSR recheck path from STORED stats (g25 verdict files) — audit use.

    Same formula/convention as deflated_sharpe_ratio with var_null defaulting to
    sigma_sr^2 (the convention g25_retro runs under): SR_daily = SR_ann/sqrt(ppy);
    SR* = sigma_sr*((1-gamma)*Z(1-1/N)+gamma*Z(1-1/(N*e))). Inputs are the ROUNDED
    stored values, so results carry a +-0.005 DSR rounding tolerance vs the raw-
    returns computation — fine for monthly recheck, NOT a substitute: registration-
    grade DSR always comes from deflated_sharpe_ratio on raw returns.
    """
    sr = float(sr_annualized) / math.sqrt(periods_per_year)
    sigma = float(sigma_sr)
    n = max(int(n_trials), 2)
    z1 = _norm_ppf(1.0 - 1.0 / n)
    z2 = _norm_ppf(1.0 - 1.0 / (n * math.e)) if n * math.e > 1.0 else 0.0
    sr_star = sigma * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)
    return {
        "dsr": round(_norm_cdf((sr - sr_star) / sigma), 6),
        "sr_daily": round(sr, 8),
        "sr_star": round(sr_star, 6),
        "n_trials": n,
    }


# ---------------------------------------------------------------- D3 stationary bootstrap CI

def bootstrap_ci_sharpe(returns, n_resamples: int = 1000, block: float = 10.0,
                        seed: int = 20260923, periods_per_year: float = PERIODS_PER_YEAR) -> dict:
    """Stationary bootstrap (Politis-Romano) 95% CI for annualized Sharpe.

    Mean block length `block` days; geometric block lengths; wraparound resampling;
    1000 resamples; seed = prereg seed family. Deterministic for a fixed seed.
    """
    xs = [float(x) for x in returns]
    t = len(xs)
    if t < 20:
        raise ValueError("bootstrap needs >= 20 returns")
    ann = math.sqrt(periods_per_year)

    def _sharpe(series):
        m = sum(series) / len(series)
        v = sum((x - m) ** 2 for x in series) / (len(series) - 1)
        return (m / math.sqrt(v)) * ann if v > 0 else 0.0

    point = _sharpe(xs)
    rng = _LCG(seed)
    p_block = 1.0 / max(block, 1.0)
    draws = []
    for _ in range(n_resamples):
        out = []
        while len(out) < t:
            start = int(rng.next() * t) % t
            # geometric block length with mean 1/p_block
            length = 1
            while rng.next() > (1.0 - p_block) and length < 4 * t:
                length += 1
            for k in range(length):
                out.append(xs[(start + k) % t])
        draws.append(_sharpe(out[:t]))
    draws.sort()
    lo = draws[int(0.025 * (n_resamples - 1))]
    hi = draws[int(0.975 * (n_resamples - 1))]
    return {
        "ci95_low": round(lo, 4),
        "ci95_high": round(hi, 4),
        "point": round(point, 4),
        "ci_lower_bound_positive": bool(lo > 0.0),
        "n_resamples": n_resamples,
        "block_days": block,
        "seed": seed,
    }


class _LCG:
    """Deterministic 64-bit LCG (portable across machines/Python versions, zero deps)."""

    def __init__(self, seed: int):
        self._s = (int(seed) ^ 0x9E3779B97F4A7C15) & ((1 << 64) - 1)

    def next(self) -> float:
        self._s = (self._s * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return (self._s >> 11) / float(1 << 53)


# ---------------------------------------------------------------- T-03 additions (F3/F6/F9/F10/F11/F12)

def append_ledger(batch_name: str, batch_trials: int, file_name: str | None = None,
                  note: str | None = None, results_dir: str = RESULTS_DIR,
                  evidence_cutoff: str | None = None,
                  prev_total: int | None = None) -> dict:
    """F3 (audit P0-7): unified trials-ledger entry, dict schema for ALL producers.

    prev_total = data-driven chain head at run time (ledger_head()); total =
    prev_total + batch_trials. Historical flat-list writers are retired. Any
    re-run of a historical batch needs fresh prereg (audit note), so the chain
    stays linear under this schema.

    prev_total override (additive, default None = data-driven): for factor-line
    batches whose file lives in results/shortline/ — the r60 one-chain
    convention takes prev = max total across BOTH results/ and
    results/shortline/ (P-1c _chain_head_total precedent); pass that max here.
    """
    prev = int(ledger_head(results_dir)["total"]) if prev_total is None else int(prev_total)
    out = {
        "prev_total": prev,
        "batch_trials": int(batch_trials),
        "total": prev + int(batch_trials),
        "batch": batch_name,
    }
    if file_name:
        out["file"] = file_name
    if note:
        out["note"] = note
    if evidence_cutoff:
        out["evidence_cutoff"] = str(evidence_cutoff)
    return out


def cutoff_meta(cutoff) -> dict:
    """T-02 7/7 (forward lockbox, BACKTEST_SCIENCE s7-M): mandatory top-level
    metadata block for every post-v2 batch results JSON. science_audit C2 scans
    file top level for one of evidence_cutoff/history_end/panel_end/data_cutoff;
    merge this block at the TOP level of the batch payload (ledger-embedded
    copies alone are invisible to C2 by design -- prereg-frozen scan scope)."""
    return {"evidence_cutoff": str(cutoff)}


def ledger_total(entry) -> int:
    """F3 (audit P0-7): tolerant trials-ledger reader -- accepts the unified
    dict schema {total | prev_total+batch_trials} and the historical flat
    list [{batch,n},...] (g25_retro / p3_portfolio / sleeve_p3 precedent)."""
    if isinstance(entry, dict):
        if isinstance(entry.get("total"), (int, float)):
            return int(entry["total"])
        return int(entry.get("prev_total", 0)) + int(entry.get("batch_trials", 0))
    if isinstance(entry, list):
        return sum(int(x.get("n", 0)) for x in entry if isinstance(x, dict))
    return 0


def dual_trade_gate(n_trades: int, n_entries: int, min_trades: int = 30) -> dict:
    """F6 (audit P1-3): dual-basis trade-count gate. num_trades counts TRANCHE
    closes (layered take-profit pads it); num_entries counts distinct position
    opens (engine report_num_entries flag). Batch gate reports disclose BOTH;
    new batches pass on entries_ok, not trades_ok alone."""
    return {
        "n_trades": int(n_trades), "n_entries": int(n_entries), "min": int(min_trades),
        "trades_ok": bool(n_trades >= min_trades),
        "entries_ok": bool(n_entries >= min_trades),
        "dual_ok": bool(n_trades >= min_trades and n_entries >= min_trades),
    }


def passive_strict_max(passive_sharpes) -> float:
    """F10 (audit P1-14): the ONE passive definition -- strict (max) across the
    pool's passive variants (buy-and-hold, monthly-rebalance, ...). Calibration
    PRODUCERS pass their computed Sharpe list here; readers use
    passive_baseline(), which reads the registered calibration file."""
    cands = [float(x) for x in passive_sharpes
             if isinstance(x, (int, float)) and math.isfinite(float(x))]
    if not cands:
        raise ValueError("no finite passive sharpe candidates")
    return max(cands)


def recorded_lines(results_dir: str = RESULTS_DIR) -> dict:
    """F9 (audit P1-13): recorded historical gate constants, read LIVE from the
    authoritative batch JSONs (machine-linkable provenance -- batch scripts
    import from here, no hand-copied numbers). These are REPRODUCTION records
    of the pre-v2 era; the CURRENT registration line is skill_line_v2 (D1)."""
    def _load(name):
        with open(os.path.join(results_dir, name), encoding="utf-8") as fh:
            return json.load(fh)
    gate = _load("p2_calibration.json")["g1_prime_gate"]
    nsp1_ce = float(_load("new_signal_p1.json")["gate"]["random_p95_inbatch_full"]["ce"])
    b1_ce = float(_load("shortline_p4_batch1.json")["gate"]["i_bar_ce_used"])
    return {
        "i_line": float(gate["i_full_sharpe_gt"]),      # 0.3521 recorded (n=100 calibration)
        "vi_bar": float(gate["vi_full_sharpe_gt"]),     # 0.4004 recorded (EW48 bh + 0.10)
        "ce_null_core48": nsp1_ce,                      # 0.4229 recorded (first core48 CE null)
        "ce_null_p4_batch1": b1_ce,                     # 0.4474 recorded (P4-b1 max-rule line)
        "jurisdiction": "historical repro constants; current line = skill_line_v2",
    }


SEED_REGISTRY = {
    # F11 (audit P1-15): prereg seed-family bases, historical frozen; NEW
    # batches register their base here (cross-batch comparability). Verified
    # against the scripts' module constants 2026-09-24.
    "policy": "prereg seed family bases, historical frozen; new batches register here",
    "p2_null_calibration_a": 10_000,    # rng(10_000+k) random+engine family
    "p2_null_calibration_b": 20_000,    # rng_x(20_000+k) random-exit pairing
    "lfc_p1_screen": 30_000,           # default_rng(30_000+k)
    "new_signal_p1": 40_000,           # default regime cells (40_000+k; ce=40_050+k)
    "new_signal_p1_ce": 40_050,
    "p4_batch1": 41_000,               # fresh draw (NSP1 used 40_000)
    "p4_folk": 43_000,                 # fresh draw (40k/41k/42k used before)
    "p4_queue": 44_000,
    "p5_random_entry": 20260923,        # K=50 start-point draw
    "p5b_new_traders": 20260924,        # K=50 fresh independent draw
    "factor_ic_screens": 20260923,     # GTJA191/WQ101 K=50 white-noise panels
    "pc_l2_ic": 45_000,                 # L2 popularity-history K=50 same-mask panels
    "p4_pairs": 48_000,                 # P4_PAIRS random-pair null draws (48_000+k)
    "cta_p1": 50_000,                   # CTA_P1 futures K=50 random signal nulls
    # (50_000+k; registry-checked free 2026-09-24 06:40 before prereg freeze)
    "p1d_gdhs_quarterly": 48_000,        # COLLISION DISCLOSURE (prereg author
    # missed p4_pairs' registration): same base, machinery fully disjoint
    # (pair-index draws vs within-universe value permutations); verdict
    # robustness documented in P1D_GDHS_QUARTERLY.md SS6.
    "p4_ext_tilt_q": 49_000,             # P4_EXT_TILT random quarterly-null base
    "p4_ext_tilt_d20": 49_100,           # P4_EXT_TILT random 20d-null base (r67 prereg)
    "cta_p2_noau": 50_500,               # CTA_P2_NOAU 8-variety K=50 random nulls
    # (50_500+k; registry+rg scanned free 2026-09-24 07:20 before prereg freeze)
    "xlib_synth_null_a": 46_000,          # BACKFILL (compliance fix r83 bm-b): XLIB_SYNTH
    "xlib_synth_null_b": 47_000,          # used these bases (R41 bm-a prereg §4) but never
    # registered -- added 2026-09-24 to prevent future collision; zero code-path change.
    "xstock_synth_null_a": 51_000,        # XSTOCK_SYNTH shelf-band nullA K=4 draws
    "xstock_synth_null_b": 52_000,        # XSTOCK_SYNTH population-band nullB K=4 draws
    # (51_000+i / 52_000+i, i=0..999; registry+rg scanned free 2026-09-24 09:05
    # before prereg freeze; 51_100 rejected: collides with 51_000+i at i=100)
    "j13v2_mill_ic1": 53_000,             # J13V2_MILL_IC1 K=50 white-noise nulls
    # (53_000+i, i<50; per-run ladder 53_000+100*(run-1) per research/J13_V2_MINILOOP.md
    # SS9; registry+rg scanned free 2026-09-24 10:05 before prereg freeze)
    "j13v2_mill_ic2": 53_100,             # J13V2_MILL_IC2 K=50 white-noise nulls (ladder run-2)
    # (53_100+i, i<50; registry+rg scanned free 2026-09-24 12:11 before run; ic1 draws
    # stop at 53_049 so the 100-step ladder leaves a 50-wide collision-free gap)
    "t18_deep_axis": 54_000,              # T18_DEEP_REVAL deep-axis null regeneration
    # (54_000+i, i=0..999; rolling-full-population caliber per research/DEEP_
    # AXIS_REVALIDATION.md SS3; registry+rg scanned free 2026-09-24 13:2x
    # before prereg freeze)
    "pa1_premium_ic": 20260925,           # PA1_PREMIUM_IC K=50 white-noise nulls
    # (20260925+i, i<50; date-style base: 53_x00 band = j13v2_mill per-run ladder,
    # 54_000 = t18_deep_axis, both occupied; registry+rg scanned free 2026-09-24
    # 14:3x before prereg freeze)
    "pa1e_premium_event": 20260926,        # PA1E_PREMIUM_EVENT K=50 circular-shift nulls
    # (20260926+i, i<50; date-style base, rg-repo-scan verified free 2026-09-24
    # 19:0x before PA1E prereg freeze)
    "og1_overnight_ic": 20260927,           # OG1_OVERNIGHT_IC K=50 white-noise nulls
    # (20260927+i, i<50; date-style base, rg-repo-scan verified free 2026-09-24
    # 19:2x before OG1 prereg freeze, T-31 deliverable-5)
    "t34_early_signal": 20260928,          # T34_EARLY_SIGNAL envelope A/B binomial
    # bootstrap CIs on pooled beat rates (single rng base, B=2000, no +i family;
    # date-style base, registry+rg repo-scan verified free 2026-09-24 21:2x --
    # sole repo hit = Money0923/tests fixture date string (non-RNG coincidence,
    # disclosed); registered before T-34 prereg freeze r114)
    "a158_truegap_ic": 55_000,             # A158_TRUEGAP_IC K=50 same-mask stock-pool
    # white-noise nulls (55_000+i, i<50; 55_x00 band verified free: registry scan
    # 2026-09-24 22:4x -- nearest neighbors 54_000=t18_deep_axis (i<=999) and
    # date-style 202609xx bases disjoint; registered before prereg freeze r119)
    "t11_negday_ic": 20260929,              # T11_NEGDAY_IC K=50 event-permutation
    # nulls (20260929+i, i<100; H: i<50, W: 50+i; date-style base, registry+rg
    # repo-scan verified free 2026-09-24 22:4x before T-11 prereg freeze r99;
    # cross-window union with a158_truegap_ic 55_000 -- bases disjoint, both valid)
    "grid_p1": 55_500,                      # GRID_P1 grid-harvest K=100
    "ths_agg_p1": 56_000,                   # THS-AGG-P1 all-size aggregate flow IC null K=50 (T-2026-09-25-43; band 56_000..56_049, rg-scan pre-register 2026-09-25 R120)
    # random-signal nulls (55_500+k default / 55_550+k ce, k<50; band verified
    # free: registry+rg scan 2026-09-25 03:1x -- sole other repo hits =
    # Money02/Money0923 data-file digit coincidences (non-RNG, t34 precedent);
    # registered before GRID_P1 slice-2 pool submission r137, prereg s3 frozen
    # r136 names this base)
    "p4_batch3_dca": 56_500,                # P4-B3-DCA staged vs single K=100
    # random-signal nulls (56_500+k default / 56_550+k ce, k<50; next free
    # band above grid_p1 55_500, registry scan 2026-09-25 04:1x before
    # P4_BATCH3.md prereg freeze r140; prereg s3 names this base;
    # cross-window union with ths_agg_p1 56_000 (band 56_000..56_049, bm-a
    # r120 same-window freeze) -- bases disjoint, both valid, t11/a158
    # precedent)
    "xstock_tilt_h20": 57_000,              # XSTOCK_TILT h20-frequency random
    # top-K nulls (57_000+i, i<20; band 57_000..57_019, next free band above
    # p4_batch3_dca 56_500; registry+rg repo-scan verified free 2026-09-25
    # 06:2x before XSTOCK_TILT prereg freeze r151 bm-b)
    "xstock_tilt_h10": 57_100,              # XSTOCK_TILT h10-frequency random
    "im_ic_pair": 58_000,                   # IM_IC_PAIR pair-direction random nulls (prereg frozen R139 bm-a)
    # top-K nulls (57_100+i, i<20; band 57_100..57_119, same scan; disjoint
    # from h20 band per p4_ext_tilt 49_000/49_100 split precedent)
    "mf_ic_p1": 58_500,                      # MF_IC_P1 K=50 same-mask stock-pool
    # white-noise nulls (58_500+i, i<50; band 58_500..58_549, next free band
    # above im_ic_pair 58_000 (p4_batch3_dca 56_500 spacing precedent);
    # registry+rg full-repo scan verified free 2026-09-25 08:0x before
    # MF_IC_P1 prereg freeze r159 bm-b, T-2026-09-25-46)
    "mf_rot_s1": 59_000,                     # MF_ROT_S1 100 pooled random-Top3 nulls (daily 59000+i i<50, monthly 59050+i; band 59000..59099, next free band above 58550; rg full-repo scan verified free 2026-09-25 13:1x bm-b r179, prereg MF_ROT_S1_PREREG.md §3)
    "div_lowvol_p1": 60_000,                 # DIV_LOWVOL_P1 K=32 random segment-mask
    # nulls (60000+k, k=0..31; band 60000..60031, next free band above mf_rot_s1
    # 59000+99; rg full-repo scan verified free 2026-09-25 17:4x before runner
    # slice; prereg research/DIV_LOWVOL_P1.md §3 names this base, R178 freeze)
}


# ------------------------------------------- T-02 close-out: v2 batch-gate verdicts (D1/D3/D4 columns)

def g1_prime_v2(sharpe_full, returns, batch_cells, pool: str = "core48",
                n_trades: int | None = None, n_entries: int | None = None,
                min_trades: int = 30, ci_seed: int = 20260923,
                results_dir: str = RESULTS_DIR,
                null_pool: dict | None = None) -> dict:
    """T-02 7/7: new-batch G1' verdict under v2 (BACKTEST_SCIENCE D1+D3).

    The two v2 clauses the ticket froze -- full-period Sharpe vs skill_line_v2
    AND stationary-bootstrap CI lower bound > 0 -- plus the F6 dual trade
    gate folded in WHEN counts are supplied (new batches pass on entries_ok).
    Historical descriptive clauses (annualized>0, OOS dual-positive,
    dd>=-35%) stay batch-level requirements disclosed in the batch report,
    not re-implemented here. Line is data-driven (live chain head), so the
    verdict NEVER hand-copies a number (O-2250 single-source rule).
    null_pool (additive, P4_EXT_TILT): batch-own null family overrides the
    default collector — stock-domain batches calibrate their own line.
    """
    line = skill_line_v2(batch_cells=batch_cells, pool=pool,
                         results_dir=results_dir, null_pool=null_pool)
    ci = bootstrap_ci_sharpe(returns, seed=ci_seed)
    line_ok = bool(float(sharpe_full) > line["line"])
    ci_ok = bool(ci["ci_lower_bound_positive"])
    out = {
        "gate": "g1_prime_v2",
        "sharpe_full": round(float(sharpe_full), 4),
        "skill_line": line,
        "line_ok": line_ok,
        "bootstrap_ci": ci,
        "ci_lower_bound_positive": ci_ok,
        "pass_v2": bool(line_ok and ci_ok),
    }
    if n_trades is not None or n_entries is not None:
        dtg = dual_trade_gate(int(n_trades or 0), int(n_entries or 0), min_trades)
        out["trade_gate"] = dtg
        out["pass_v2"] = bool(out["pass_v2"] and dtg["entries_ok"])
    return out


def g2_registration_v2(g1_pass, dsr, pbo, dsr_gate: float = 0.95,
                       pbo_gate: float = 0.25) -> dict:
    """T-02 7/7: G2 registration eligibility v2 columns (BACKTEST_SCIENCE D1/D4).

    eligible_v2 = g1_prime_v2 pass AND DSR>=0.95 (raw-returns
    deflated_sharpe_ratio -- dsr_from_stats is an audit path, NOT this) AND
    family PBO<=0.25 (screening/pbo.py CSCV, same-family grid per g25_retro).
    Missing inputs are refused honestly (missing_inputs list, never silently
    skipped); hr.py promotion reads the same rule via g25 verdict files.
    """
    dsr_val = float(dsr["dsr"]) if isinstance(dsr, dict) else float(dsr)
    pbo_val = None if pbo is None else float(pbo)
    missing = []
    if not g1_pass:
        missing.append("g1_prime_v2")
    if pbo_val is None:
        missing.append("family_pbo")
    dsr_ok = bool(dsr_val >= dsr_gate)
    pbo_ok = bool(pbo_val is not None and pbo_val <= pbo_gate)
    return {
        "gate": "g2_registration_v2",
        "g1_pass": bool(g1_pass),
        "dsr": round(dsr_val, 6),
        "dsr_gate": dsr_gate,
        "dsr_ok": dsr_ok,
        "family_pbo": (round(pbo_val, 4) if pbo_val is not None else None),
        "pbo_gate": pbo_gate,
        "pbo_ok": pbo_ok,
        "missing_inputs": missing,
        "eligible_v2": bool(bool(g1_pass) and dsr_ok and pbo_ok),
    }


# ---------------------------------------------------------------- F12 CostPatch (single source)

COST_X2_RATE = 0.0026082  # G2-recorded stressed single-side cost (2x fee schedule)


class CostPatch:
    """FeeSchedule name-factory stress patch (G2-proven pattern; single source
    since T-03-F12 -- was duplicated in paper/ce_transfer/combined_exit/
    lowchurn/p2_deepening).

    Replaces the FeeSchedule NAME inside engine.backtester with a factory
    returning a stressed instance. (Class-attribute patching does NOT work:
    dataclass __init__ bakes field defaults into the function signature at
    class creation, so FeeSchedule() ignores later class-attr edits --
    verified empirically 2026-09-23, J14.) Engine/knowledge files untouched,
    name always restored. Stress only ever makes costs STRICTER.
    """

    def __init__(self, mult: float):
        self.mult = mult
        self.orig = None
        self._eb = None

    def __enter__(self):
        import engine.backtester as _eb
        self._eb = _eb
        self.orig = _eb.FeeSchedule
        Orig, m = self.orig, self.mult
        _eb.FeeSchedule = lambda: Orig(
            commission_rate=Orig.commission_rate * m,
            handling_fee=Orig.handling_fee * m,
            supervision_fee=Orig.supervision_fee * m,
            slippage_a=Orig.slippage_a * m)
        return self

    def __exit__(self, *exc):
        self._eb.FeeSchedule = self.orig
        return False


# ---------------------------------------------------------------- selftest / report

def _synth_returns(n: int, sr_annual: float, seed: int) -> list[float]:
    """Deterministic synthetic daily returns with an approximate target annualized Sharpe."""
    rng = _LCG(seed)
    daily_sr = sr_annual / math.sqrt(PERIODS_PER_YEAR)
    xs = [rng.next() * 2.0 - 1.0 for _ in range(n)]  # uniform(-1,1), zero mean
    m = sum(xs) / n
    xs = [x - m for x in xs]
    sd = math.sqrt(sum(x * x for x in xs) / (n - 1))
    unit = [x / sd for x in xs]  # zero-mean, unit sd
    return [x + daily_sr for x in unit]  # daily Sharpe ~= daily_sr


def selftest() -> int:
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # skill line: monotone in N_eff, both terms present, data-driven
    line50 = skill_line_v2(batch_cells=50)
    line500 = skill_line_v2(batch_cells=500)
    ok("skill_line_v2 n_eff = live chain head + cells (data-driven, no frozen count)",
       line50["n_eff"] == ledger_head()["total"] + 50)
    ok("skill_line_v2 monotone in N_eff", line500["null_term"] > line50["null_term"])
    ok("skill_line_v2 line = max(passive_term, null_term)",
       abs(line50["line"] - max(line50["passive_term"], line50["null_term"])) < 1e-9)
    ok("skill_line_v2 passive core48 strict(>=0.379)+0.10", line50["passive_term"] >= 0.479)

    # DSR: honest multiple-testing calibration. At N=2727 the 0.95 gate demands full-period
    # Sharpe ~2.1+ (6y) — a 1.6 edge must NOT clear it; a 2.5 edge must. Noise fails hard.
    good16 = _synth_returns(1512, 1.6, seed=11)
    good25 = _synth_returns(1512, 2.5, seed=13)
    noise = _synth_returns(1512, 0.0, seed=12)
    dsr_good16 = deflated_sharpe_ratio(good16, n_trials=2727)
    dsr_good25 = deflated_sharpe_ratio(good25, n_trials=2727)
    dsr_noise = deflated_sharpe_ratio(noise, n_trials=2727)
    dsr_noise_bigN = deflated_sharpe_ratio(noise, n_trials=20000)
    ok("DSR honest: SR~1.6 at N=2727 does NOT clear 0.95 (calibration bite)", 0.45 < dsr_good16["dsr"] < 0.95)
    ok("DSR strong edge (SR~2.5 ann) > 0.95 at N=2727", dsr_good25["dsr"] > 0.95)
    ok("DSR pure noise < 0.60", dsr_noise["dsr"] < 0.60)
    ok("DSR penalizes more trials (2727 -> 20000 lowers noise DSR)",
       dsr_noise_bigN["dsr"] < dsr_noise["dsr"])

    # T-02 5/7: recheck path from stored stats reproduces raw-returns DSR (rounding tolerance)
    re_16 = dsr_from_stats(dsr_good16["sr_annualized"], dsr_good16["sigma_sr"], 2727)
    re_25 = dsr_from_stats(dsr_good25["sr_annualized"], dsr_good25["sigma_sr"], 2727)
    ok("dsr_from_stats reproduces raw-returns DSR within +-0.005 rounding tolerance",
       abs(re_16["dsr"] - dsr_good16["dsr"]) <= 0.005
       and abs(re_25["dsr"] - dsr_good25["dsr"]) <= 0.005)
    ok("dsr_from_stats monotone in N (growing ledger never raises DSR)",
       dsr_from_stats(dsr_good25["sr_annualized"], dsr_good25["sigma_sr"], 20000)["dsr"]
       <= re_25["dsr"])

    # bootstrap CI: covers point, deterministic, low-power honesty
    ci_a = bootstrap_ci_sharpe(good25, seed=4242)
    ci_b = bootstrap_ci_sharpe(good25, seed=4242)
    ok("bootstrap CI deterministic under fixed seed", ci_a == ci_b)
    ok("bootstrap CI brackets point estimate", ci_a["ci95_low"] <= ci_a["point"] <= ci_a["ci95_high"])
    ok("bootstrap CI lower bound > 0 for genuine edge", ci_a["ci_lower_bound_positive"])
    ci_noise = bootstrap_ci_sharpe(noise, seed=4242)
    ok("bootstrap CI noise lower bound < 0 (low-power disclosure)",
       not ci_noise["ci_lower_bound_positive"])

    # passive baseline: only calibrated pools
    try:
        passive_baseline("lfc_gold5")
        ok("passive_baseline rejects uncalibrated pool", False)
    except KeyError:
        ok("passive_baseline rejects uncalibrated pool", True)

    # T-03 F3: unified ledger schema + tolerant reader
    head_total = ledger_head()["total"]
    led = append_ledger("t03-selftest-batch", 7, "selftest.json", note="synthetic")
    ok("append_ledger dict schema + chain-head prev",
       led["prev_total"] == head_total and led["total"] == head_total + 7
       and {"prev_total", "batch_trials", "total", "batch", "file", "note"} <= set(led))
    ok("ledger_total tolerant: dict / flat list / dict-without-total / junk",
       ledger_total(led) == led["total"]
       and ledger_total([{"n": 432}, {"n": 59}]) == 491
       and ledger_total({"prev_total": 100, "batch_trials": 27}) == 127
       and ledger_total(None) == 0)
    led_cut = append_ledger("t02-7of7-selftest", 1, "selftest.json", evidence_cutoff="2026-09-22")
    led_nocut = append_ledger("t02-7of7-selftest", 1, "selftest.json")
    ok("T-02 7/7 evidence_cutoff: append_ledger embeds when given, omits when not",
       led_cut["evidence_cutoff"] == "2026-09-22" and "evidence_cutoff" not in led_nocut
       and cutoff_meta("2026-09-22") == {"evidence_cutoff": "2026-09-22"}
       and led_nocut["total"] == led_cut["total"])
    led_ovr = append_ledger("prev-override-selftest", 63, prev_total=5476)
    ok("append_ledger prev_total override honored (r60 one-chain max, factor-line)",
       led_ovr["prev_total"] == 5476 and led_ovr["total"] == 5539
       and ledger_total(led_ovr) == 5539)

    # r112: ledger_head must see subdirectory batch files (shortline family)
    sub = os.path.join(RESULTS_DIR, "_selftest_sub")
    os.makedirs(sub, exist_ok=True)
    sub_path = os.path.join(sub, "sub_ledger.json")
    try:
        with open(sub_path, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 1, "batch_trials": 1,
                                         "total": head_total + 11}}, fh)
        ok("ledger_head recursive: subdir batch file visible (r112 fix)",
           ledger_head()["total"] == head_total + 11
           and ledger_head()["file"] == "sub_ledger.json")
    finally:
        os.unlink(sub_path)
        os.rmdir(sub)

    # T-03 F6: dual-basis trade gate
    ok("dual_trade_gate: tranches pad, entries honest",
       dual_trade_gate(35, 12)["trades_ok"] and not dual_trade_gate(35, 12)["entries_ok"]
       and dual_trade_gate(35, 12)["dual_ok"] is False
       and dual_trade_gate(35, 32)["dual_ok"] is True)

    # T-03 F10: passive strict-max
    ok("passive_strict_max = max across variants (0.3004 vs 0.379)",
       passive_strict_max([0.3004, 0.379]) == 0.379)

    # T-03 F9: recorded lines live-read from source JSONs
    rl = recorded_lines()
    ok("recorded_lines: p2 gate + CE nulls live-read",
       rl["i_line"] == 0.3521 and rl["vi_bar"] == 0.4004
       and rl["ce_null_core48"] == 0.4229 and rl["ce_null_p4_batch1"] == 0.4474)

    # T-03 F12: CostPatch stresses and restores
    import sys
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    import engine.backtester as _eb
    orig_cls = _eb.FeeSchedule
    with CostPatch(2.0):
        stressed = _eb.FeeSchedule()
        rate2 = (stressed.commission_rate + stressed.handling_fee
                 + stressed.supervision_fee + stressed.slippage_a)
        ok("CostPatch x2: stressed single-side == recorded COST_X2_RATE",
           abs(rate2 - COST_X2_RATE) < 1e-12)
    ok("CostPatch restores FeeSchedule name on exit", _eb.FeeSchedule is orig_cls)

    # T-03 F11: seed registry sanity
    ok("SEED_REGISTRY: verified bases present, all ints positive",
       SEED_REGISTRY["p4_folk"] == 43_000 and SEED_REGISTRY["p5b_new_traders"] == 20260924
       and all(v > 0 for v in SEED_REGISTRY.values() if isinstance(v, int)))
    ok("SEED_REGISTRY: t18_deep_axis base 54_000 registered (T-18 nulls lineage)",
       SEED_REGISTRY["t18_deep_axis"] == 54_000)
    ok("SEED_REGISTRY: div_lowvol_p1 base 60_000 registered (band 60000..60031,"
       " disjoint from mf_rot_s1 59000..59099)",
       SEED_REGISTRY["div_lowvol_p1"] == 60_000)

    # T-18 deep-axis additive pool branch (additive; core48 path untouched)
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _tmp:
        try:
            passive_baseline(pool="t18_deep_axis", results_dir=_tmp)
            _pre_ok = False
        except KeyError:
            _pre_ok = True
        _np_file = os.path.join(_tmp, "shortline", "t18_deep_nulls.json")
        os.makedirs(os.path.dirname(_np_file), exist_ok=True)
        json.dump({"passive": {
            "ew48_monthly_rebal": {"full_axis": {"sharpe": 0.31}},
            "ew48_buyhold": {"full_axis": {"sharpe": 0.42}}}},
            open(_np_file, "w", encoding="utf-8"))
        _val = passive_baseline(pool="t18_deep_axis", results_dir=_tmp)
        ok("t18_deep_axis pool: KeyError before nulls file; strict-max after",
           _pre_ok and abs(_val - 0.42) < 1e-12)

    # T-02 close-out: v2 batch-gate verdicts
    g1_edge = g1_prime_v2(sharpe_full=1.8, returns=good25, batch_cells=60,
                          n_trades=80, n_entries=45, ci_seed=4242)
    g1_noise = g1_prime_v2(sharpe_full=0.30, returns=noise, batch_cells=60,
                           n_trades=80, n_entries=45, ci_seed=4242)
    ok("g1_prime_v2: line data-driven (= skill_line_v2 live, CI seed passthrough)",
       g1_edge["skill_line"]["line"] == skill_line_v2(batch_cells=60)["line"]
       and g1_edge["skill_line"]["n_eff"] == ledger_head()["total"] + 60
       and g1_edge["bootstrap_ci"]["seed"] == 4242)
    ok("g1_prime_v2: genuine edge passes; noise fails line clause (edge vs ~0.93 line)",
       g1_edge["pass_v2"] and not g1_noise["line_ok"] and not g1_noise["pass_v2"])
    ok("g1_prime_v2: F6 entries gate folded when counts supplied",
       not g1_prime_v2(1.8, good25, 60, n_trades=80, n_entries=12)["pass_v2"])
    ok("g2_registration_v2: eligible only all-three; missing/weak inputs refused",
       g2_registration_v2(True, 0.97, 0.20)["eligible_v2"]
       and not g2_registration_v2(True, 0.97, None)["eligible_v2"]
       and "family_pbo" in g2_registration_v2(True, 0.97, None)["missing_inputs"]
       and not g2_registration_v2(False, 0.97, 0.20)["eligible_v2"]
       and not g2_registration_v2(True, 0.90, 0.30)["eligible_v2"])
    ok("g2_registration_v2: consumes deflated_sharpe_ratio dict directly",
       g2_registration_v2(True, dsr_good25, 0.1143)["dsr"] == dsr_good25["dsr"]
       and g2_registration_v2(True, dsr_good25, 0.1143)["eligible_v2"])

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\nscience_gates selftest: {len(checks)-n_fail}/{len(checks)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


def report() -> int:
    out_path = os.path.join(RESULTS_DIR, "science_gates_v2.json")
    head = ledger_head()
    nulls = null_sharpes()
    line = skill_line_v2(batch_cells=0)  # current standing line (no batch in flight)
    payload = {
        "module": "scripts/science_gates.py",
        "authority": "research/BACKTEST_SCIENCE.md (O-20260923-2215) D1/D3",
        "ledger_head": head,
        "null_pool_coverage": nulls["coverage"],
        "skill_line_v2_current": line,
        "formulas_frozen": {
            "skill_line_v2": "max(passive+0.10, mu_null + sigma_null*sqrt(2*ln N_eff))",
            "dsr": "Phi((SR-SR*)/sigma_SR), SR*=sqrt(V[SR_null])*((1-g)*Z(1-1/N)+g*Z(1-1/(N*e)))",
            "bootstrap": "stationary bootstrap, block=10d mean, 1000 resamples, seed=prereg family",
        },
        "gate_bindings": {"registration": "DSR>=0.95 AND PBO<=0.25 AND CI lower>0 (D1/D3/D4 composite)"},
        "honesty": "null collector v0.1 covers p2_calibration random family only; "
                   "p1_screen and later batches' null arrays persist OOS-side only -> disclosed "
                   "in coverage, extension queued (T-02 follow-up)",
        "generated": _now(),
    }
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print(f"report -> {out_path}")
    print(json.dumps({"ledger_head": head, "skill_line_v2_current": line,
                      "null_n": nulls["coverage"]["n_values"]}, ensure_ascii=False))
    return 0


def _now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    raise SystemExit(selftest() if cmd == "selftest" else report() if cmd == "report" else 0)
