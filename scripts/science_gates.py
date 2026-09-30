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
                d = json.load(fh)
            # r239: results/ is a shared surface carrying non-dict top-level JSONs
            # by design (e.g. local_coding_pilot C-arm metrics.json = list of
            # per-round dicts). A non-dict file simply is not a ledger file ->
            # skip, same as unparseable. .get on a list raised AttributeError
            # and crashed every ledger_head consumer (aggressive_lab S6 leg).
            tl = d.get("trials_ledger") if isinstance(d, dict) else None
            # r459: nested face -- etf_ops family products carry the ledger
            # block under science_gates.ledger (BP1/BP2 precedent); a
            # top-level-only read sinks those +N into an invisible branch and
            # every later batch under-counts N_eff (r253 redo-echo family,
            # live instance: BP1 +30 sunk 09-28, BP2 +15 caught 09-30).
            if tl is None and isinstance(d, dict):
                _sg = d.get("science_gates")
                if isinstance(_sg, dict) and isinstance(_sg.get("ledger"), dict):
                    tl = _sg["ledger"]
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

    # RW-6 (T-127, r477): prefer the v2 engine-effect recompute pool when
    # present -- the fixed-engine null population (same frozen design, same
    # window 2026-09-22, same seeds; mu/sigma shift = pure engine effect).
    # Fallback = frozen v1 canon (pre-fix engine) if v2 is absent.
    for _fname in ("p2_calibration_v2.json", "p2_calibration.json"):
        d = _load(_fname)
        if not d:
            continue
        _vals: list[float] = []
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
                    _vals.append(float(sr))
        if _vals:
            values = _vals
            parsed.append(f"{_fname}:families[random*].runs[].full.sharpe"
                          + (" (RW-6 engine-effect recompute, preferred)"
                             if _fname.endswith("_v2.json") else " (v1 canon fallback)"))
            break

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
    return {"values": values, "coverage": coverage,
            "source": (parsed[-1] if parsed else None)}


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
    if pool == "repo_cash":
        # REPO_CALENDAR_P1 additive pool (research/INNOVATION_QUOTA_W1_PREREG
        # .md SS4): THIS batch's own PASSIVE-GC001-ROLL Sharpe (daily
        # overnight roll on the repo panel) read from the phase-1 product --
        # the cash-leg domain never borrows equity/cta passives (no silent
        # cross-pool reuse; CTA_P1 phase-1-write-first precedent).
        path = os.path.join(results_dir, "innovation_quota",
                            "REPO-CALENDAR-P1.json")
        if not os.path.exists(path):
            raise KeyError(f"repo_cash passive not on file yet ({path}) — "
                           f"run REPO_CALENDAR_P1 phase-1 write first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("passive_gc001_roll",):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                           "innovation_quota/REPO-CALENDAR-P1.json — schema "
                           "drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "cta_wave1":
        # CTA_WAVE1 additive pool (research/CTA_WAVE1_PREREG.md SS4): strict-max
        # of THIS batch's own two passive long baselines (r20 / monthly) on the
        # 10-variety deep panel (TS leg included, 2008-01-09 union start) --
        # read from the product file; never borrows cta_futures (2017 panel) or
        # cta_futures_noau (8-variety) passives: deep-panel passives are a
        # different universe and must calibrate their own line.
        path = os.path.join(results_dir, "shortline_cta_wave1.json")
        if not os.path.exists(path):
            raise KeyError(f"cta_wave1 passive not on file yet "
                          f"({path}) — run CTA_WAVE1 phase-1 write first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("passive_long_r20", "passive_long_monthly"):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                          "shortline_cta_wave1.json — schema drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "options_wave2":
        # OPTIONS_WAVE2 additive pool (research/OPTIONS_WAVE2_PREREG.md §3):
        # strict-max of THIS batch's own two buy-hold passives (510050 /
        # 510300), read from the product file — options domain never borrows
        # core48 / futures / stock passives (no silent cross-pool reuse).
        path = os.path.join(results_dir, "options_wave2.json")
        if not os.path.exists(path):
            raise KeyError(f"options_wave2 passive not on file yet "
                           f"({path}) — run the options_wave2 batch first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        cands = []
        for name in ("passive_buy_hold_510050", "passive_buy_hold_510300"):
            sr = ((pas.get(name) or {}).get("full") or {}).get("sharpe")
            if isinstance(sr, (int, float)) and math.isfinite(sr):
                cands.append(float(sr))
        if not cands:
            raise KeyError("passive block missing/empty in "
                          "options_wave2.json — schema drift, fix batch writer")
        return max(cands)  # strict = harder line
    if pool == "bond_w3a":
        # BOND_CARRY_WAVE3A additive pool (research/BOND_CARRY_WAVE3A_PREREG.md
        # §4 工程腿): the in-domain passive (all ADV20>=500k members, cap-
        # bounded EW, monthly rebalance) is the skill-line anchor the prereg
        # names ("债券域 skill line 锚"); the 510300 buy-hold is the cross-
        # asset disclosure anchor and deliberately NOT a line candidate. Read
        # from this batch's own product file, honest KeyError until it exists
        # (cta_futures run-first-then-read precedent; never borrows core48).
        path = os.path.join(results_dir, "bond_carry_w3a.json")
        if not os.path.exists(path):
            raise KeyError(f"bond_w3a passive not on file yet ({path}) "
                           "— run scripts/bond_carry_w3a.py first")
        with open(path, encoding="utf-8") as fh:
            pas = (json.load(fh).get("passive") or {})
        sr = ((pas.get("passive_domain_ew") or {}).get("full") or {}).get("sharpe")
        if isinstance(sr, (int, float)) and math.isfinite(sr):
            return float(sr)
        raise KeyError("passive_domain_ew.full.sharpe missing/empty in "
                       "bond_carry_w3a.json — schema drift, fix batch writer")
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
                  null_pool: dict | None = None,
                  n_eff_override: int | None = None,
                  passive_override: float | None = None) -> dict:
    """D1: skill_line_v2 = max(passive+0.10, mu_null + sigma_null*sqrt(2*ln N_eff)).

    Returns the line plus every input so batch reports can disclose the whole computation.
    n_eff_override (additive, r259 prev-echo guard face): a deterministic
    re-execution of an ALREADY-APPENDED batch passes its own chain position
    (stored prev_total + batch_cells) -- the live data-driven head would
    otherwise include the batch's own echo and drift the line on redo
    (r253 single-count law: redo faces must be byte-stable).
    passive_override (additive, REPO_CALENDAR_P2): per-cell batch-own
    passive Sharpe -- batches whose judged cells each live on their own
    window of the panel calendar (cell-window passives differ per cell)
    pass each cell's own passive here; the named-pool reader stays the
    default for every other caller (no silent cross-pool reuse).
    """
    if null_pool is None:
        null_pool = null_sharpes(results_dir)
    cov = null_pool["coverage"]
    if cov["mu"] is None or cov["sigma"] is None or cov["n_values"] < 30:
        raise ValueError(f"null pool too thin ({cov['n_values']} values) — extend collector first")
    n = int(n_eff_override) if n_eff_override is not None \
        else n_eff(batch_cells, results_dir)
    extreme = cov["sigma"] * math.sqrt(2.0 * math.log(max(n, 2)))
    null_term = cov["mu"] + extreme
    if passive_override is not None:
        passive = float(passive_override)
        passive_source = "batch_own_per_cell"
    else:
        passive = passive_baseline(pool, results_dir)
        passive_source = "pool:" + pool
    passive_term = passive + 0.10
    return {
        "n_eff": n,
        "line": round(max(passive_term, null_term), 4),
        "passive_term": round(passive_term, 4),
        "null_term": round(null_term, 4),
        "mu_null": round(cov["mu"], 4),
        "sigma_null": round(cov["sigma"], 4),
        "pool": pool,
        "null_pool_source": null_pool.get("source"),
        "passive_source": passive_source,
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


def finalize_already_landed(batch_name: str, file_name: str | None = None,
                            results_dir: str = RESULTS_DIR) -> dict | None:
    """pit-95 guard (orphan-finalize double-append): read-only tripwire that
    reports whether the target product file already carries this batch's
    trials_ledger block.

    Producers land a batch exactly once; the only lawful re-run channel is a
    fresh prereg under a fresh batch name. A finalize re-running on an
    already-landed product must REFUSE instead of re-appending (r206
    incident: orphan W6 judge finalize re-ran on the landed chain and
    inflated the head 333,432 -> 333,725). Returns the landed ledger block
    (callers dump it for disclosure and refuse), or None when the batch is
    genuinely new / the file is absent, corrupt, or carries no matching
    block (crash-recovery re-finalize stays lawful).

    file_name resolution mirrors append_ledger metadata conventions:
    'results/<sub>/<file>.json' (repo-relative), '<sub>/<file>.json'
    (results-relative), and absolute paths are all accepted.
    """
    if not file_name:
        return None
    root = os.path.dirname(results_dir)
    for cand in (os.path.join(results_dir, file_name),
                 os.path.join(root, file_name)):
        if not os.path.exists(cand):
            continue
        try:
            with open(cand, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        tl = d.get("trials_ledger") if isinstance(d, dict) else None
        # r459: nested face (same fix as ledger_head -- etf_ops family
        # products nest the block under science_gates.ledger; the guard must
        # see landed blocks it would otherwise miss -> double-append risk).
        if tl is None and isinstance(d, dict):
            _sg = d.get("science_gates")
            if isinstance(_sg, dict) and isinstance(_sg.get("ledger"), dict):
                tl = _sg["ledger"]
        if isinstance(tl, dict) and tl.get("batch") == batch_name:
            out = dict(tl)
            out["file"] = os.path.basename(cand)
            return out
    return None


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
    "decision_chain_e2e": 20261001,        # DECISION_CHAIN_E2E_P1 four-arm envelope
    # binomial bootstrap CIs (single rng base, B=2000, no +i family; date-style
    # base, rg repo-scan verified free 2026-09-27 r312 -- prereg v1.1 s3 named
    # 20260929 but that base was already taken by t11_negday_ic (registered
    # 2026-09-24 22:4x, pre-freeze); zero-run amendment s9.2 to next clean
    # date-style one-step 20261001 (20260930=cn_rev_tilt_p1 occupied), order
    # law (rg-zero-hit-then-register) honored at runner-build time, zero cells
    # burned at amendment time)
    # decision_chain_v2 seed: single entry 20284110 registered by bm-a R365
    # (band-avoidance verified); bm-c r118 owner ruling amendment a3 deduped
    # the duplicate 20261002 entry this commit originally added -- duplicate
    # dict keys silently last-win in python, deduped pre-rebase-continue
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
    "sina_construct_p1": 58_550,             # SINA_CONSTRUCT_P1 K=100 same-mask
    # within-day factor-rank permutation nulls (58_550+k, k<100; band
    # 58_550..58_649, next free band above mf_ic_p1 58_500..58_549 with the
    # mf_rot_s1 59_000 spacing precedent intact); rg full-repo scan (--type
    # py, Money02/Money0923 excluded per t34/wild_route precedent) 2026-09-27
    # r333 zero RNG hits in band (sole hits = worldquant101 formula constant
    # 7.58555 + mf_rot_s1's own 'next free band above 58550' comment);
    # registered at prereg freeze BEFORE any burn, one-step R250 law; lane =
    # T-2026-09-25-46 sibling SINA_CONSTRUCT_P1 (claim MSG-20260927-1556 +
    # lane pick MSG-20260927-1615 (a)), prereg research/SINA_CONSTRUCT_P1.md §3
    "mf_rot_s1": 59_000,                     # MF_ROT_S1 100 pooled random-Top3 nulls (daily 59000+i i<50, monthly 59050+i; band 59000..59099, next free band above 58550; rg full-repo scan verified free 2026-09-25 13:1x bm-b r179, prereg MF_ROT_S1_PREREG.md §3)
    "div_lowvol_p1": 60_000,                 # DIV_LOWVOL_P1 K=32 random segment-mask
    # nulls (60000+k, k=0..31; band 60000..60031, next free band above mf_rot_s1
    # 59000+99; rg full-repo scan verified free 2026-09-25 17:4x before runner
    # slice; prereg research/DIV_LOWVOL_P1.md §3 names this base, R178 freeze)
    "wild_route_s1": 61_000,                 # WILD_ROUTE_S1 K=50 same-mask random
    # event-day nulls (61000+k, k<50; band 61000..61049, next free band above
    # div_lowvol_p1 60031; rg full-repo scan 2026-09-25 18:5x: sole hits =
    # Money02 fold/data-file digit coincidences (non-RNG, t34 precedent);
    # registered before WILD_ROUTE_S1 prereg freeze, T-2026-09-25-57 s2)
    "cta_wave1": 62_000,                     # CTA_WAVE1 K=50 random-signal nulls
    # (62000+k, k<50; band 62000..62049, next free band above wild_route_s1
    # 61049; registry+rg full-repo scan 2026-09-25 19:5x before CTA_WAVE1
    # prereg freeze -- sole rg hits = data-file digit coincidences
    # (AU.csv oi 262000 / IH.csv volume 62000 / eligibility tails, non-RNG,
    # t34/wild_route precedent); T-2026-09-25-65-P1 s2 wave-1 futures revival)
    "options_wave2": 63_000,                  # OPTIONS_WAVE2 K=50 weekly tri-state
    # random nulls (63000+k, k<50; band 63000..63049, next free band above
    # cta_wave1 62049; registry+rg full-repo scan 2026-09-25 22:0x before
    # OPTIONS_WAVE2 prereg freeze -- sole rg hits = data-file digit
    # coincidences (league.json float / transfer sha256 / state id, non-RNG,
    # t34/wild_route precedent); T-2026-09-25-67-P1 wave-2 options pilot)
    "bond_carry_w3a": 66_000,                 # BOND_CARRY_WAVE3A K=32 random-member
    # nulls (66000+k, k<32; band 66000..66031, next free band above
    # options_wave2 63049 -- 64k/65k left clear for in-flight families;
    # registered 2026-09-25 22:2x bm-b r207 before BOND_CARRY_WAVE3A prereg
    # freeze; T-2026-09-25-68-P1 wave-3a exchange-bonds lane)
    "p1e_zoo_behavior": 67_000,               # P-1e zoo behavior IC batch K=50
    # nulls x3 mask classes (67000+k, k<150; band 67000..67149, next free
    # band above bond_carry_w3a 66031; rg scripts/+research/ scan clean
    # 2026-09-26 03:0x before P1E prereg freeze -- sole full-repo hits =
    # Money* data-file digit coincidences (csv volumes / fold indices,
    # non-RNG, t34/wild_route precedent); registered bm-b r219; lane =
    # ASTYLE_ZOO #85/#92/#93 consumption face, P-1c harness family
    "p1e_synth_null_b": 67_200,              # P1E_SYNTH K=2 white-noise pair
    # nulls (draw i: seeds 67200+2i / 67200+2i+1, i<50; band 67200..67299,
    # next free band above p1e_zoo_behavior 67149; rg scripts/+research/
    # scan 2026-09-26 06:4x before P1E_SYNTH prereg freeze -- sole full-repo
    # hits = results/*.json backtest digit coincidences (867200.91 etc,
    # non-RNG, t34/wild_route precedent); registered bm-b r229; lane =
    # P-1e survivors joint synth, PS2 K=2 precedent)
    "cny_window_p1": 68_000,                 # CNY_WINDOW_P1 K=20 same-mask
    # nulls (draw k: seed 68000+k, k<20; band 68000..68019, next free
    # band above p1e_synth_null_b 67299; rg scripts/+research/ scan 2026-09-26
    # 09:1x before CNY_WINDOW_P1 prereg freeze -- zero full-repo hits
    # (t34/wild_route precedent); registered bm-b r235; lane = zoo sec.8
    # #38 evidence-upgrade, spring-festival concrete-window batch)
    "t19_phantom_p1": 68_500,                # T19-PHANTOM-P1 stage-2c K=50
    # placebo tranche-family nulls (draw k: seed 68500+k, k<50, band
    # 68500..68549; rg full-repo scan zero operational hits 2026-09-27
    # 10:2x bm-c r74 prereg research/T19_PHANTOM_P1.md sec.3 -- Money02
    # legacy numeric coincidences excluded; lane = T-19 GM decision pack)
    "grid_sleeve_p1": 62_500,                # GRID-SLEEVE-P1 K=50 layout-
    # sensitivity nulls (null i: seed 62500+i, i<50, draw = band-phase
    # offset uniform(-1,+1) grids on the 5 live instruments, 10 each;
    # band 62500..62549, next free band above cta_wave1 62049 -- sole
    # full-repo rg hit = cta_wave1_probe.py's own upper-bound constant
    # (non-RNG, t34 precedent); registered bm-b r244 before runner burn;
    # lane = T-2026-09-26-78 s5b, prereg research/GRID_SLEEVE_P1.md sec.3
    "cn_rev_tilt_p1": 20260930,               # CN-REV-TILT-P1 K=50 same-mask
    # random-signal 20-name sleeves (20260930+k, k<50; band 20260930..20260979,
    # next free DATE-STYLE base above t11_negday_ic 20260929 -- prereg R245
    # s3.4 wrote 20260926 = COLLISION with pa1e_premium_event (20260926+i,
    # i<50) caught at the pre-run registration scan (xstock_synth 51_100-
    # rejection precedent; ZERO runs before this amendment, prereg s3.4
    # carries the in-place disclosure); rg full-repo scan 2026-09-26 12:2x:
    # sole hit = update_fundamental.py report-period string constant
    # (non-RNG, t34/wild_route precedent); registered before runner burn,
    # lane = T-2026-09-26-73 s3, prereg research/CN_REV_TILT_PREREG.md s3.4
    "cn_div_lowvol_rot_p1": 20260980,        # CN-DIV-LOWVOL-ROT-P1 K=50
    # random-leg rotation sleeves (20260980+k, k<50; band 20260980..20261029,
    # next free DATE-STYLE base above cn_rev_tilt_p1 20260979; registered at
    # prereg freeze BEFORE any runner burn; rg full-repo scan 2026-09-26 14:1x:
    # hits in band = Money0923 legacy CSV amount column (601919.csv
    # 20260980.0 = data face), MIDTERM_DOSSIER-20261009 filename (doc face),
    # sh511900.csv / sh516270.csv amount columns (data face) -- ZERO RNG-usage
    # hits in any script (t34/wild_route non-RNG precedent);
    # lane = T-2026-09-26-73 s3 slice-2, prereg
    # research/CN_DIV_LOWVOL_ROT_PREREG.md s3.4
    "t73_style_rot_s1": 20261030,           # T73-STYLE-ROT-S1 K=50
    # within-month leg-permutation nulls (20261030+k, k<50; band
    # 20261030..20261079, next free DATE-STYLE base above
    # cn_div_lowvol_rot_p1 20261029; registered at prereg freeze BEFORE any
    # runner burn, one-step R250 law; rg full-repo scan 2026-09-26 17:1x:
    # hits in band = data-face digit coincidences only (Money0923 600160.csv
    # amount 20261035.0, sh513700/sh516220/sh563900.csv volume columns,
    # T-2026-09-23-01 transfer sha256 substring 20261059, Money02 fold json
    # digit) -- ZERO RNG-usage hits in any script (t34/wild_route non-RNG
    # precedent); lane = T-2026-09-26-73 s2 slice-E (style rotation),
    # prereg = scripts/t73_s2_style_rotation.py frozen header (s2 slice
    # family convention, slice-A/C/D precedent)
    "cn_core_sat_p1": 20261080,             # CN-CORE-SATELLITE-P1 K=50
    # random-satellite sleeves (20261080+k, k<50; band 20261080..20261129,
    # next free DATE-STYLE base above t73_style_rot_s1 20261079; registered
    # at prereg freeze BEFORE any runner burn, one-step R250 law;
    # rg full-repo scan 2026-09-26 17:4x: hits in band = data-face digit
    # coincidences only (eligibility.csv share counts 202611012.5, Money0923
    # 600000/600519/600160 amount+volume columns, sz159547.csv amount
    # 20261092) -- ZERO RNG-usage hits in any script (t34/wild_route
    # non-RNG precedent); lane = T-2026-09-26-73 s3 slice-5 (final CN-native
    # model), prereg research/CN_CORE_SATELLITE_PREREG.md s3.4
    "cn_core_ddctl_p1": 20261130,           # CN-CORE-DDCTL-P1 K=100 nulls
    # (2 arms x 50: DD10 arm = 20261130+k k<50, DD20 arm = 20261180+k k<50;
    # band 20261130..20261229 sits exactly above cn_core_sat_p1 band top
    # 20261129 = collision-free by construction; registered at prereg freeze
    # BEFORE any runner burn, one-step R250 law; rg full-repo scan 2026-09-26
    # 18:1x: hits in band = data-face digit coincidence only (stock_mood csv
    # row 2010-11-12) -- ZERO RNG-usage hits in any script; lane =
    # T-2026-09-26-73 s3 slice-6 (doctrine residual prereg), prereg
    # research/CN_CORE_DDCTL_PREREG.md s3.4
    "rev_osc_stock_p1": 20261230,           # REV_OSC_STOCK_P1 K=2000 nulls
    # (rev_osc nulls = 20261230+k k<2000); band 20261230..20261429 sits
    # exactly above cn_core_ddctl_p1 band top 20261229 = collision-free by
    # construction; registered at prereg freeze BEFORE any runner burn,
    # one-step R250 law; rg full-repo scan 2026-09-26 23:4x clean; lane =
    # T-2026-09-26-87 s2 first-priority slot (CEO O-2026-09-26-2330
    # 超跌反弹呈件特选 + O-2026-09-26-2335 淬炼令), prereg
    # research/REV_OSC_STOCK_PREREG.md
    "cn_trend_etf_p1": 20270201,            # CN_TREND_ETF_P1 K=2000 nulls
    # (cn_trend_etf nulls = 20270201+k k<2000); band 20270201..20272200 sits
    # above max registered 20261230 = collision-free; full-repo scan
    # 2026-09-27 00:3x zero hits; lane = T-2026-09-26-87 s2 queue #1
    # (SCHOOL_SUPPLY_S1.md §二 趋势跟踪), prereg research/CN_TREND_ETF_PREREG.md
    "cn_soe_etf_p1": 20272301,              # CN_SOE_ETF_P1 K=2000 nulls
    # (cn_soe_etf nulls = 20272301+k, k<2000); band 20272301..20274300 sits
    # exactly above cn_trend_etf_p1 band top 20272200 = collision-free by
    # construction; registered at prereg freeze BEFORE any runner burn, one-step
    # R250 law; rg full-repo scan 2026-09-27 01:2x: zero hits in band (t34/
    # wild_route precedent); lane = T-2026-09-26-87 s2 queue #2
    # (SCHOOL_SUPPLY_S1.md §二 中特估/国家队), prereg research/CN_SOE_ETF_PREREG.md
    "census_fusion_s2": 20274500,        # CENSUS_FUS_S2_W1 K=400 combo nulls
    # (200 random pairs + 200 random triples = 20274500+k, k<400); band
    # 20274500..20274900 sits above cn_soe_etf_p1 band top 20274300 =
    # collision-free; registered at prereg freeze BEFORE any runner burn,
    # one-step R250 law; rg full-repo scan 2026-09-27 02:2x zero hits in
    # band; lane = T-2026-09-26-86 s2 combinatorial census (O-20260926-2320),
    # prereg research/CENSUS_FUSION_S2_PREREG.md
    "census_fusion_s2_unc": 20275000,    # CENSUS_FUS_S2_W1-UNC s3 uncertainty
    # face (prereg sec.3 s3 frozen rules + sec.9.1 seed freeze R290 bm-a):
    # per-combo deterministic streams np.random.default_rng([20275000, i])
    # for block bootstrap B=200 (block=20td circular, x2 blend Sharpe CI
    # p2.5/p97.5) + sign-flip permutation P=200 (two-sided IC p-value);
    # derivation face ledger +0; no band occupation (seed-sequence derive);
    # registered at sec.9.1 freeze commit BEFORE unc runner build, one-step
    # R250 law; collision scan R290 03:2x zero hits; lane = T-2026-09-26-86
    # s3, prereg research/CENSUS_FUSION_S2_PREREG.md sec.9.1
    "cn_kline_pattern_p1": 20275100,     # CN_KLINE_PATTERN_P1 K=2000 same-mask
    # random event-day nulls (20275100+k, k<2000; band 20275100..20277100
    # sits above census_fusion_s2 band top 20274900 AND above
    # census_fusion_s2_unc seed-sequence base 20275000 = collision-free by
    # construction; registered at prereg freeze BEFORE any runner burn,
    # one-step R250 law; rg full-repo scan 2026-09-27 03:5x: in-band hits =
    # own claim files only (MSG-20260927-0355-bm-a + prereg itself), all
    # other 20275x hits = census_fusion_s2_unc base refs below band (t34/
    # wild_route non-RNG precedent); lane = T-2026-09-26-87 s2 queue #3
    # (SCHOOL_SUPPLY_S1.md sec.2 K-line pattern face, folklore gate PASS
    # R289), prereg research/CN_KLINE_PATTERN_PREREG.md sec.3
    "fusion_grid_p1": 20275200,        # FUSION_GRID_P1 K=2000 random-portfolio
    # nulls (T-85 s2/s3 fusion grid): per-null-per-rebalance deterministic
    # streams np.random.default_rng([20275200, k, j]) — null k, rebalance j;
    # subset size mirror + members + Dirichlet(1) simplex weights all drawn
    # from that stream (prereg sec.3 frozen); band 20275200..20275900 in-band
    # below cn_kline_pattern_p1 band top 20277100 = collision-free by
    # construction; registered at prereg freeze commit BEFORE runner build,
    # one-step R250 law; rg scan 2026-09-27 05:1x: code/canon faces zero
    # hits (data/*.csv digit coincidences excluded per kline precedent);
    # lane = T-2026-09-26-85 s2/s3, prereg research/FUSION_GRID_P1_PREREG.md
    "cn_sector_leader_p1": 20277200,   # CN_SECTOR_LEADER_P1 K=2000 same-mask
    # random (leader,day) nulls (20277200+k, k<2000; band 20277200..20279200
    # sits exactly above cn_kline_pattern_p1 band top 20277100 =
    # collision-free by construction; Sobol sensitivity leg scrambles via
    # seed-sequence np.random.default_rng([20277200, 2000]) — no band
    # occupation, census_fusion_s2_unc derive precedent; registered at prereg
    # freeze BEFORE any runner build, one-step R250 law; rg full-repo scan
    # 2026-09-27 06:3x zero hits in band (Money02/Money0923 data-file digit
    # coincidences excluded per t34/wild_route precedent); lane =
    # T-2026-09-26-87 s2 queue #4 (SCHOOL_SUPPLY_S1.md sec.2 sector-leader
    # non-limit-up face), prereg research/CN_SECTOR_LEADER_PREREG.md sec.3
    "cn_mkneutral_p1": 20279300,      # CN_MKTNEUTRAL_P1 K=2000 same-mask
    # random-quintile-basket nulls (20279300+k, k<2000; band 20279300..20281300
    # sits exactly above cn_sector_leader_p1 band top 20279200 =
    # collision-free by construction; Sobol sensitivity leg scrambles via
    # seed-sequence np.random.default_rng([20279300, 2000]) — no band
    # occupation, SECTOR derive precedent; registered at prereg freeze BEFORE
    # any runner build, one-step R250 law; rg full-repo scan (--type py,
    # Money02/Money0923 excluded per t34/wild_route precedent) 2026-09-27
    # 07:5x zero hits in band; lane = T-2026-09-26-87 s2 queue #5
    # (SCHOOL_SUPPLY_S1.md sec.2 market-neutral face), prereg
    # research/CN_MKTNEUTRAL_PREREG.md sec.3
    "census_fusion_s2_w2": 20281500,  # CENSUS_FUS_S2_W2-A nulls K=400 (200
    # pairs + 200 triples; band 20281500..20281899 sits exactly above
    # cn_mkneutral_p1 band top 20281300 = collision-free by construction; rg
    # full-repo scan (--type py, Money02/Money0923 excluded per t34/wild_route
    # precedent) 2026-09-27 r325 zero hits in band; registered at wave-2 roster
    # freeze BEFORE any wave-2 runner build, one-step R250 law; lane =
    # T-2026-09-26-86 s2 wave-2 W2-A wide-universe fusion census, freeze =
    # CENSUS_FUSION_S2_PREREG.md sec.9.3 + results/census_fusion_s2/
    # w2_roster.json (scripts/census_w2_roster.py deterministic derivation)
    "census_fusion_s2_w2_unc": 20282000,  # CENSUS_FUS_S2_W2-UNC wave-2
    # uncertainty face: np.random.default_rng([20282000, i]) seed-sequence
    # double-int derivation = no band occupation, wave-1 census_fusion_s2_unc
    # (20275000) same-protocol precedent; registered same commit as the
    # wave-2 freeze (one-step R250 law); lane = T-2026-09-26-86 s3 wave-2
    "census_fusion_s2_w2b": 20282500,  # CENSUS_FUS_S2_W2B nulls K=400 (200
    # pairs + 200 triples, each forced >=1 D face -- same-structure
    # same-coverage-window baseline, divergence from W2-A's unconditional
    # draw disclosed in prereg sec.9.4; band 20282500..20282899 sits exactly
    # above census_fusion_s2_w2_unc base 20282000 = collision-free by
    # construction; rg full-repo scan (--type py, Money02/Money0923 excluded
    # per t34/wild_route precedent) 2026-09-27 R344 zero hits in band;
    # registered at the W2-B sec.9.4 append-confirm freeze BEFORE any W2-B
    # runner build, one-step R250 law; lane = T-2026-09-26-86 s2 wave-2
    # W2-B D8-only sub-wave (E-heat deferred, structural data-availability
    # downscope, zero cells burned), freeze = CENSUS_FUSION_S2_PREREG.md
    # sec.9.4 + results/census_fusion_s2/w2b_roster.json
    # (scripts/census_w2b_roster.py deterministic derivation)

    "trial_labor_w1_gen": 20283500,  # TRIAL_LABOR_W1 mass-candidate-trial
    # wave-1 generation draws N=500/family (A registered-six 500 + B school
    # factory 500 = raw 1000, ceiling-not-quota per O-20260927-2245);
    # derivation = np.random.default_rng([20283500, family_idx, draw_idx])
    # seed-sequence multi-int = no band occupation, census_fusion_s2_unc
    # (20275000) same-protocol precedent; band head sits exactly above
    # census_fusion_s2_w2b band top 20282899 = collision-free by
    # construction; rg full-repo scan (--type py, Money02/Money0923 excluded
    # per t34/wild_route precedent) 2026-09-27 r347 zero hits in band;
    # registered same commit as the wave-1 prereg freeze (one-step R250 law);
    # lane = T-2026-09-27-94 s1, freeze = research/TRIAL_LABOR_W1_PREREG.md
    "trial_labor_w1_scrnull": 20284000,  # TRIAL_LABOR_W1_SCREEN null family
    # K=200 same-structure random-signal candidates (template leg randomized,
    # axis legs drawn from same grids/spaces, same engine/cost/panel --
    # BACKTEST_PLAN iron law "every backtest batch runs random-signal
    # baseline alongside"; screen floor = null p95 of beat6m, procedure-frozen
    # zero hand-tuning); derivation = default_rng([20284000, i]); rg scan
    # clean r347; registered same commit as wave-1 prereg freeze (R250 law)
    "trial_labor_w1_unc": 20284500,  # TRIAL_LABOR_W1_JUDGE dual-nulls
    # resampling face per survivor cell: block bootstrap B=2000 (block=20td
    # circular) + sign-flip permutation P=2000 (daily independent, two-sided)
    # per RANDOM_LARGE_SAMPLE_LAW sec.3 nulls>=2000 double-method; derivation
    # = default_rng([20284500, cell_idx]) with rng stream pinned to the two
    # resampling faces only (census sec.9.1 purpose-pinning precedent); rg
    # scan clean r347; registered same commit as wave-1 prereg freeze (R250 law)
    "mass_trial_w1": 20283000,  # T-2026-09-27-94 mass candidate trial wave-1
    # (CEO O-2026-09-27-2245). ALREADY-BURNED face (975-cell stage-1 screen,
    # side-branch yielded to bm-b TRIAL_LABOR_W1 lane per sec.4 commit-time
    # 22:49 < 22:57; trials stay counted). Same-window blind double-reg
    # disclosure: originally declared band 20283000..20283899 covered
    # bm-b r347 trial_labor_w1_gen 20283500 (invisible locally at reg
    # time); actual used = Sobol seeds 20283000..20283074 (75 families)
    # + null rngs 20283100..20283119 -- disjoint from bm-b seeds by
    # both range and derivation protocol (scalar Sobol seed vs multi-int
    # seed-sequence), zero stream collision; kept for reproducibility of
    # the counted cells
    "decision_chain_v2": 20284110,  # T-2026-09-27-95 decision-chain v2 simplification
    # batch (CEO O-2026-09-27-2255). Binomial bootstrap B=2000 CI seed only
    # (v1 decision_chain_e2e protocol). Band avoidance disclosure: 20283000..20283899
    # = mass_trial_w1 declared band; 20284000 = trial_labor_w1_scrnull (bm-b
    # TRIAL_LABOR_W1 s2); 20261002..20261030 = t11_negday_ic nulls data pollution;
    # rg --no-ignore whole-repo zero-hit verified 2026-09-28 00:1x; registered
    # same commit as prereg freeze (R250 law)
    "mass_trial_w1_judge": 20285000,  # MASS_TRIAL_W1_JUDGE dual-nulls
    # resampling face per survivor cell (T-2026-09-27-94 s3 wave-1a judgment
    # freeze = research/MASS_TRIAL_W1_PREREG.md sec.9.1, owner bm-b r350):
    # block bootstrap B=2000 (block=20td circular) + sign-flip permutation
    # P=2000 (two-sided) per RANDOM_LARGE_SAMPLE_LAW sec.3; derivation =
    # default_rng([20285000, cell_idx]) with rng stream pinned to the two
    # resampling faces only (trial_labor_w1_unc 20284500 purpose-pinning
    # precedent); declared band 20285000..20285199 sits with clean gap above
    # trial_labor_w1_unc (20284500+i, i<~170 tops below 20284700) and above
    # decision_chain_v2 20284110; rg --type py repo scan + registry band scan
    # 2026-09-28 00:4x zero hits; registered same commit as sec.9.1 freeze
    # (one-step R250 law)
    "trial_labor_w2_gen": 20285500,  # TRIAL_LABOR_W2 candidate generation
    # (T-20260928-96 wave-2 prereg freeze = research/TRIAL_LABOR_W2_PREREG.md,
    # owner bm-b r357). Sobol low-discrepancy sampling (wave-2 declared
    # upgrade face (b); scipy.stats.qmc.Sobol scramble=True per-family frames,
    # mass_trial_w1 sample_draws protocol imported not rewritten): Sobol seed
    # = 20285500 + family_idx (A-family idx 0-5, B-family idx 6-81 -> band
    # 20285500..20285581); axis-combo RNG stream (R/X/S/T/STOP quintuple) =
    # default_rng([20285500 + family_idx, 7919]) -- scalar-seed Sobol and
    # two-int seed-sequence derivation protocols are disjoint from all
    # neighboring bands; band 20285500..20285599 rg --type py full-repo scan
    # 2026-09-28 r357 zero hits (Money02/Money0923 excluded per precedent);
    # registered same commit as the wave-2 prereg freeze (one-step R250 law)
    "trial_labor_w2_scrnull": 20286000,  # TRIAL_LAB_W2_SCREEN null family
    # K=200 same-structure random-signal candidates (template leg randomized,
    # axis legs + initial-stop leg drawn from same grids/spaces, same
    # engine/cost/panel -- BACKTEST_PLAN iron law "every backtest batch runs
    # random-signal baseline alongside"); screen floor = null p95 of beat6m,
    # procedure-frozen zero hand-tuning; derivation = default_rng([20286000,
    # i]); band 20286000..20286019 rg --type py scan r357 zero hits;
    # registered same commit as wave-2 prereg freeze (R250 law)
    "trial_labor_w2_unc": 20286500,  # TRIAL_LAB_W2_JUDGE dual-nulls
    # resampling face per survivor cell: block bootstrap B=2000 (block=20td
    # circular) + sign-flip permutation P=2000 (two-sided) per
    # RANDOM_LARGE_SAMPLE_LAW sec.3 nulls>=2000 double-method; derivation =
    # default_rng([20286500, cell_idx]) with rng stream pinned to the two
    # resampling faces only (trial_labor_w1_unc 20284500 purpose-pinning
    # precedent); band 20286500..20286519 rg --type py scan r357 zero hits;
    # clean gap above mass_trial_w1_judge (20285000..20285199) and
    # trial_labor_w2_scrnull (20286000); registered same commit as wave-2
    # prereg freeze (R250 law)
    "trial_labor_w3_gen": 20287500,  # TRIAL_LABOR_W3 candidate generation
    # (wave-3 regime-gate deepening wave; Sobol scalar seed = 20287500 +
    # family_idx, A-family idx 0-5 / B-family idx 6-81 -> band
    # 20287500..20287581); six-tuple axis-combo RNG stream (R/X/S/T/STOP/GATE)
    # = default_rng([20287500 + family_idx, 7919]); clean gap above
    # trial_labor_w2_unc (20286500..20286519); band 20287500..20287599
    # rg --type py full-repo scan r391 zero hits; registered same commit as
    # wave-3 prereg freeze (R250 law)
    "trial_labor_w3_scrnull": 20288000,  # TRIAL_LAB_W3_SCREEN null family
    # K=200 same-structure random-signal candidates (template leg -> random
    # signal-day generator; axis legs + initial-stop leg + gate leg drawn
    # from same grids/param spaces, same engine/cost/panel); derivation =
    # default_rng([20288000, i]); band 20288000..20288019 rg --type py scan
    # r391 zero hits; registered same commit as wave-3 prereg freeze (R250
    # law)
    "trial_labor_w3_unc": 20288500,  # TRIAL_LAB_W3_JUDGE dual-nulls
    # resampling face per survivor cell: block bootstrap B=2000 (block=20td
    # circular) + sign-flip permutation P=2000 (two-sided) per
    # RANDOM_LARGE_SAMPLE_LAW sec.3; derivation = default_rng([20288500,
    # cell_idx]) rng stream pinned to the two resampling faces only
    # (purpose-pinning precedent); band 20288500..20288519 rg --type py scan
    # r391 zero hits; clean gap above trial_labor_w3_scrnull (20288000);
    # registered same commit as wave-3 prereg freeze (R250 law)
    "trial_labor_w4_gen": 20289500,  # TRIAL_LABOR_W4 candidate generation
    # (wave-4 vol-gate deepening wave; Sobol scalar seed = 20289500 +
    # family_idx, A-family idx 0-5 / B-family idx 6-81 -> band
    # 20289500..20289581); seven-tuple axis-combo RNG stream
    # (R/X/S/T/STOP/GATE/VOL) = default_rng([20289500 + family_idx, 7919]);
    # clean gap above trial_labor_w3_unc (20288500..20288519); band
    # 20289500..20289599 rg --type py full-repo scan r396 zero hits;
    # registered same commit as wave-4 prereg freeze (R250 law)
    "trial_labor_w4_scrnull": 20290000,  # TRIAL_LAB_W4_SCREEN null family
    # K=200 same-structure random-signal candidates (template leg -> random
    # signal-day generator; axis legs + initial-stop leg + gate leg + vol leg
    # drawn from same grids/param spaces, same engine/cost/panel); derivation
    # = default_rng([20290000, i]); band 20290000..20290019 rg --type py scan
    # r396 zero hits; registered same commit as wave-4 prereg freeze (R250
    # law)
    "trial_labor_w4_unc": 20290500,  # TRIAL_LAB_W4_JUDGE dual-nulls
    # resampling face per survivor cell: block bootstrap B=2000 (block=20td
    # circular) + sign-flip permutation P=2000 (two-sided) per
    # RANDOM_LARGE_SAMPLE_LAW sec.3; derivation = default_rng([20290500,
    # cell_idx]) rng stream pinned to the two resampling faces only
    # (purpose-pinning precedent); band 20290500..20290519 rg --type py scan
    # r396 zero hits; clean gap above trial_labor_w4_scrnull (20290000);
    # registered same commit as wave-4 prereg freeze (R250 law)
    "decision_chain_v3_tournament": 20291000,
    # T-20260928-101 chain v3 tournament 3-arm batch (H1 style-tilt /
    # H2 theme-satellite / H3 minimal-chain control); bootstrap beat-rate CI
    # seed family; band 20291000..20291019 free (rg --type py zero hits
    # 2026-09-28 15:2x; occupied band ends 20290500 = trial_labor_w4_unc);
    # registered same commit as prereg freeze (R250 law; prereg =
    # research/DECISION_CHAIN_V3_TOURNAMENT_PREREG.md)
    "national_team_s3_perm": 20291500,
    # NATIONAL-TEAM-S3-EVENT-REVIEW K=2000 same-regime random-day
    # permutation nulls (T-20260928-106 s3 event-window review;
    # derivation = default_rng([20291500, i]), i<2000; band
    # 20291500..20293499 clean gap above decision_chain_v3_tournament
    # (20291000..20291019), far below trial_wave1 20920000; rg --type py
    # full-repo scan zero hits 2026-09-28 18:2x before prereg freeze;
    # registered same commit as prereg freeze (R250 law; prereg =
    # research/NATIONAL_TEAM_S3_REVIEW_PREREG.md; F-04 MSG-20260928-1825)
    "etf_ops_bp1": 20294000,
    # ETF-OPS-BP1 broad-index pullback-buy chain K=200/cell same-mask
    # random-entry nulls (T-2026-09-28-103 s2; 30 member-cell streams
    # default_rng([20294000, cell_idx]), cell_idx<30, K=200 sequential
    # draws per stream; band 20294000..20294029 clean gap above
    # national_team_s3_perm band (20291500..20293499); NOTE: parked W5
    # prereg doc claims 20291500/20292000/20292500 unregistered (parked;
    # must re-pick on unfreeze -- national_team collision); rg --type py
    # full-repo scan zero hits 2026-09-28 19:5x before prereg freeze;
        # registered same commit as prereg freeze (R250 law; prereg =
        # research/etf_ops/ETF_OPS_BP1_PREREG.md; F-04 MSG-20260928-2000)
    "etf_ops_bp2": 20294100,
    # ETF-OPS-BP2 calendar-DCA discipline chain (T-2026-09-28-103 s2 chain
    # #2, BP1 family-lesson exit-discipline transplant): 15 member-cell
    # streams default_rng([20294100, cell_idx]), cell_idx<15, K=200
    # sequential draws per stream (uniform-random-trading-day entry nulls);
    # bootstrap-CI streams default_rng([20294100, 1000+cell_idx]); band
    # 20294100..20294114 clean gap inside etf_ops_bp1 band tail (bp1 uses
    # 20294000..20294029; member_reinforce starts 20294500); rg full-repo
    # scan zero hits 2026-09-30 11:4x before prereg freeze; registered same
    # commit as prereg freeze (R250 law; prereg =
    # research/etf_ops/ETF_OPS_BP2_PREREG.md; F-04 MSG-20260930-1150)
        "member_reinforce_p1_null": 20294500,
        # MEMBER_REINFORCE_P1 seed-stability face, seed #1 base: K=200
        # same-mask random nulls per member (default_rng([20294500, k]),
        # k<200); bands 20294500/600/700 are three independent null
        # re-derivations for the 3-seed G1' verdict-stability check (T-107
        # sec.4(b)); band 20294500..20294700+199 clean gap above
        # etf_ops_bp1 (20294000..20294029); rg --type py full-repo scan
        # zero hits 2026-09-28 20:3x before prereg freeze; registered same
        # commit as prereg freeze (R250 law; prereg =
        # research/MEMBER_REINFORCE_P1_PREREG.md; F-04 MSG-20260928-2035)
        "member_reinforce_p1_seedstab2": 20294600,
        "member_reinforce_p1_seedstab3": 20294700,
        "innovation_quota_w1_repo": 20295000,
        # INNOVATION_QUOTA_W1 / REPO_CALENDAR_P1 calendar term-switch family:
        # K=2000 random-calendar-placement nulls (rng([20295000,k]), k<2000)
        # + K=1000 virtual startpoints (k in [2000,3000)) + 100 random
        # split windows (k in [3000,3100)) per RANDOM_LARGE_SAMPLE_LAW
        # (T-107 sec.4(d)); usage band 20295000..20298099 clean gap above
        # member_reinforce_p1 block; rg --type py full-repo scan zero hits
        # 2026-09-28 20:3x before prereg freeze; registered same commit as
        # prereg freeze (R250 law; prereg =
        # research/INNOVATION_QUOTA_W1_PREREG.md; F-04 MSG-20260928-2035)
        "grid_dualface_p1": 20295500,  # GRID_DUALFACE_P1 K=200 same-mask
        # random-trigger-day nulls (T-104 s2 broad-base oscillation grid
        # dual-face batch): per-member-cell deterministic streams
        # np.random.default_rng([20295500, cell_idx]), cell_idx<30
        # (member_idx x 6 + grid_idx), K=200 sequential draws per stream
        # (prereg sec.3.7 frozen); pair-derivation first element 20295500
        # is distinct from innovation_quota_w1_repo's constant 20295000
        # first element (its k<3100 rides the SECOND element only) = zero
        # actual RNG collision by construction (census_fusion_s2_unc
        # pair-derivation precedent); the 20295000..20298099 nominal band
        # claim above is a k-range description, not single-int occupation;
        # rg --type py full-repo scan zero 202955xx hits at freeze;
        # registered at prereg freeze commit BEFORE any runner build,
        # one-step R250 law; lane = T-2026-09-28-104 s2, prereg
        # research/etf_ops/GRID_DUALFACE_P1_PREREG.md, F-04
        # MSG-20260928-2110-bmb (dead r399 session salvage: seed declared
        # in MSG+prereg, registered here at salvage freeze commit r399)
        "innovation_quota_w2_repo": 20298500,
        # INNOVATION_QUOTA_W2 / REPO_CALENDAR_P2 long-term extension family:
        # K=2000 random-calendar masks (rng([20298500,k]), k<2000) each
        # evaluated on both cell structures (per-cell 2000-draw null pools)
        # + K=1000 virtual startpoints (k in [2000,3000)) + 100 random
        # split windows (k in [3000,3100)) per RANDOM_LARGE_SAMPLE_LAW
        # (T-107 sec.4(d) slot-2); base 20298500 first element distinct from
        # every other registry base = pair-derivation zero-collision
        # semantics (grid_dualface_p1 same-window precedent; the W1
        # 20295000..20298099 note above is a k-range description, not
        # single-int occupation); full-repo rg scan zero
        # seed-face hits 2026-09-28 21:4x before prereg freeze (CSV
        # volume-column digit coincidences are not seed faces); registered
        # same commit as prereg freeze (R250 law; prereg =
        # research/INNOVATION_QUOTA_W2_PREREG.md; F-04 MSG-20260928-2140)
        "trial_labor_w5_gen": 20302000,
        # TRIAL_LABOR_W5 (T-114 wave-5 single-K-line yang-gate trial):
        # Sobol(., scramble=True, seed=20302000+family_idx) param-box draws
        # (idx 0-5 family A templates / 6-81 family B factory functions)
        # + axis-stream rng([20302000+family_idx, 7919]) (W5 prereg sec.3).
        # RE-PICK disclosure: draft parked at 20291500 collided with
        # national_team_s3_perm=20291500 registered band (T-103 progress
        # note "W5 unfreeze must re-pick"); three-step take-number law
        # (r183 69th): 92-key registry inventory + first-element-distinct
        # + rg full-repo scan zero seed-face hits 2026-09-29 00:1x (CSV
        # volume-column coincidences excluded per 69th batch); 20299000/
        # 20299500 left free for NT-CHAIN-P1 (MSG-2305 declared pair).
        # Registered same commit as prereg freeze (R250 law; prereg =
        # research/TRIAL_LABOR_W5_PREREG.md; F-04 MSG-20260929-0010)
        "trial_labor_w5_scrnull": 20302500,
        # W5 screen K=200 same-grammar random-signal nulls
        # (rng([20302500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        "trial_labor_w5_unc": 20303000,
        # W5 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20303000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w6_gen": 20303500,
        # TRIAL_LABOR_W6 (T-117 wave-6 volume-confirmation VCONF-gate trial):
        # Sobol(., scramble=True, seed=20303500+family_idx) param-box draws
        # + axis-stream rng([20303500+family_idx, 7919]) (W6 prereg sec.3).
        # Draft berths 20303500/20304000/20304500 (bm-a r410 parked bases)
        # re-verified at freeze per three-step take-number law (r183 69th):
        # 95-key int inventory zero exact/key collision + first8 distinct
        # vs all existing bases + rg full-repo zero seed-face hits
        # 2026-09-29 04:2x (HANDOVER/round-report berth-declaration doc
        # mentions are not seed faces; W5 20291500 re-pick precedent NOT
        # triggered -- berths held). Freeze takeover receipt: draft author
        # bm-a heartbeat stalled since 03:19:43 (>20min), healthy-machine
        # takeover per O-20260924-1730; trigger MET = W5-JUDGE ledger head
        # 328,987 (w5_judge.json) + zero in-flight judge faces (pool
        # non-done = V3-TOURNAMENT waiting only). Registered same commit
        # as prereg freeze (R250 law; prereg =
        # research/TRIAL_LABOR_W6_PREREG.md; F-04 MSG-20260929-0425)
        "trial_labor_w6_scrnull": 20304000,
        # W6 screen K=200 same-grammar random-signal nulls
        # (rng([20304000, i]), i<200) per BACKTEST_PLAN three-iron-laws
        "trial_labor_w6_unc": 20304500,
        # W6 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20304500, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w7_gen": 20305000,
        # TRIAL_LABOR_W7 (T-118 wave-7 streak-confirmation gate trial):
        # Sobol(., scramble=True, seed=20305000+family_idx) param-box draws
        # + axis-stream rng([20305000+family_idx, 7919]) (W7 prereg sec.3).
        # Draft berths 20305000/20305500/20306000 (bm-c r206 parked bases)
        # re-verified at freeze per three-step take-number law (r183 69th):
        # 98-key int inventory zero exact/key collision + first-element
        # distinct vs all existing bases + rg full-repo zero seed-face
        # hits 2026-09-29 09:2x (prereg/W8-candidate/digest/round-report
        # berth-declaration doc mentions are not seed faces; the 2 CSV hits
        # are data volume-column digit coincidences per 69th batch; W5
        # 20291500 re-pick precedent NOT triggered -- berths held; draft
        # collision YIELD receipt: bm-b AMP draft yielded per fleet README
        # sec.4 commit-time law, parked as W8 candidate berth). Registered
        # same commit as prereg freeze (R250 law; prereg =
        # research/TRIAL_LABOR_W7_PREREG.md; F-04 MSG-20260929-0930)
        "trial_labor_w7_scrnull": 20305500,
        # W7 screen K=200 same-grammar random-signal nulls
        # (rng([20305500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        "trial_labor_w7_unc": 20306000,
        # W7 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20306000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w8_gen": 20306500,
        # TRIAL_LABOR_W8 (T-120 wave-8 temporal-state gate trial):
        # Sobol(., scramble=True, seed=20306500+family_idx) param-box draws
        # + eleven-tuple axis-stream rng([20306500+family_idx, 7919])
        # (W8 prereg sec.3). Draft berths 20306500/20307000/20307500
        # (bm-b r423 parked bases) re-verified at freeze per three-step
        # take-number law (r183 69th): 101-key int inventory zero
        # exact/key collision (band 20306xxx-20308xxx occupied only by
        # w7_unc 20306000) + first-element distinct vs all existing bases
        # and mutually distinct + rg full-repo hits all doc-berth
        # declarations or CSV volume-column digit coincidences, zero
        # seed faces (2026-09-29 12:3x freeze live-read; W6/W7 same-family
        # precedent; berths held, no re-pick). Registered same commit as
        # prereg freeze (R250 law; prereg =
        # research/TRIAL_LABOR_W8_PREREG.md; F-04 MSG-20260929-1235)
        "trial_labor_w8_scrnull": 20307000,
        # W8 screen K=200 same-grammar random-signal nulls
        # (rng([20307000, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (tstate gate leg merged into same-grid same-param-space draw)
        "trial_labor_w8_unc": 20307500,
        # T-101-V4-A2-PRESCREEN (r433 bm-a; take-number law: 101-key
        # inventory zero-conflict checked 2026-09-29 15:0x before freeze):
        "t101_v4_a2_scrnull": 20308000,  # same-mask circular-shift nulls K=200/cell
        "t101_v4_a2_corrnull": 20308500,  # T-101-V4-A2-CORRSOURCE same-mask
        # circular-shift nulls K=200 (r434 bm-a D6-exit child batch; band
        # 20308500..20308699 = clean 300-gap above t101_v4_a2_scrnull
        # 20308000..20308199; rg seed-face scan zero hits 2026-09-29 15:3x
        # before freeze; prereg research/T-101-V4-A2-CORRSOURCE_PREREG.md)
        # T-101-V4-A7-PRESCREEN (r435 bm-a; take-number law: 108-key
        # inventory zero-conflict checked 2026-09-29 15:2x before freeze):
        "t101_v4_a7_scrnull": 20309000,  # same-mask circular-shift nulls K=200/cell
        # (band 20309000..20309199 = clean 300-gap above a2_corrnull band)
        # W8 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20307500, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w9_gen": 20309500,
        # TRIAL_LABOR_W9 (T-121 wave-9 amplitude-confirmation AMP-gate
        # trial): Sobol(., scramble=True, seed=20309500+family_idx)
        # param-box draws + twelve-tuple axis-stream
        # rng([20309500+family_idx, 7919]) (W9 prereg sec.3). Draft
        # berths 20309500/20310000/20310500 (bm-b r431 parked bases,
        # in-draft-window DOUBLE collision re-pick: +500 natural
        # positions 20308000/20308500/20309000 hit t101_v4_a2 batch
        # {20308000, 20308500} -> first take 20309000/20309500/20310000
        # hit t101_v4_a7_scrnull=20309000 (bm-a r435 same-window freeze,
        # 108-key tree live-read) -> final take 20309500/20310000/
        # 20310500) re-verified at freeze per three-step take-number law
        # (r183 69th): 108-key live inventory (107 int seed values + 1
        # policy annotation) zero exact/key collision (band 20309xxx-
        # 20310xxx occupied only by t101_v4_a7_scrnull=20309000, its
        # null band 20309000..20309199 zero-overlap vs gen Sobol band
        # head 20309500) + first-element distinct vs all existing bases
        # and mutually distinct (1097877923/930621365/1010720707 zero
        # clash) + rg full-repo zero seed-face hits 2026-09-29 16:0x
        # freeze live-read (hits = data\daily + Money0923 CSV volume-
        # column digit coincidences + berth-declaration docs; 69th batch
        # exclusion face; W5/W6/W7 same-family precedent; berths held,
        # no re-pick at freeze). Registered same commit as prereg
        # freeze (R250 law; prereg =
        # research/TRIAL_LABOR_W9_PREREG.md; F-04 MSG-20260929-1615)
        "trial_labor_w9_scrnull": 20310000,
        # W9 screen K=200 same-grammar random-signal nulls
        # (rng([20310000, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (amp gate leg merged into same-grid same-param-space draw)
        "trial_labor_w9_unc": 20310500,
        # W9 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20310500, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        # GATE-TIMING-PRESCREEN-A158 (bm-c r231; take-number law: 111-key
        # inventory live-read 2026-09-29 18:0x -- 20311000/20311500/
        # 20312000 = W10 catalog-reserved berths (Tools/fill_ladder_catalog
        # .json W10-GENERATE pre-arm, r229) left untouched; band
        # 20312500..20312699 = clean 300-gap above W10 reserved block):
        "gate_timing_prescreen_a158_scrnull": 20312500,
        # 17 library gates x 5 members = 85 cells, same-mask circular-shift
        # nulls K=200/cell (rng base re-init per cell = r433 t101_v4_a2
        # template verbatim semantics; prereg =
        # research/GATE_TIMING_PRESCREEN_A158_PREREG.md; F-04
        # MSG-20260929-1800)
        # TRIAL_LABOR_W10 (bm-b r437 freeze; berths held from bm-c r228
        # candidate draft, zero re-pick -- three-step take-number law
        # re-verified at freeze ALL GREEN: 112-key registry live-read zero
        # exact value/key collision; first elements 1282508069/905546082/
        # 1631370965 distinct vs all 111 existing int bases and mutually
        # distinct; rg whole-repo hits all = berth-declaration documents
        # (prereg/MSG/catalog/HANDOVER/comments) != seed face; null-derive
        # band 20311500..20311699 and unc-derive band 20312000..20312200
        # overlap zero registered values; prereg =
        # research/TRIAL_LABOR_W10_PREREG.md; F-04 MSG-20260929-1820)
        "trial_labor_w10_gen": 20311000,
        # 5000-draw Sobol generation axis draws
        # (rng([20311000+family_idx, 7919]) integer-axis draw per
        # W1-W9 lineage)
        "trial_labor_w10_scrnull": 20311500,
        # s2 screen K=200 same-structure random-signal nulls
        # (rng([20311500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (mom gate leg merged into same-grid same-param-space draw)
        "trial_labor_w10_unc": 20312000,
        # W10 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20312000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "t101_v4_a158_fv_scrnull": 20313000,
        # T-101-V4-A158-FULLVERDICT same-mask circular-shift nulls K=200/cell
        # (rng re-init per cell, template semantics) -- r441 bm-a
        "t101_v4_a158_fv_unc": 20313500,
        # T-101-V4-A158-FULLVERDICT dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20313500, cell_idx])) W1 semantics -- r441 bm-a
        "t101_v4_a10_combo_scrnull": 20314000,
        # T-101-V4-A10-REGIMECOMBO random-gate-combo nulls K=200/cell
        # (rng([20314000, cell_idx]) per cell) -- r442 bm-a; three-step law
        # verified pre-freeze (118 int bases zero-collision, band 20314xxx
        # empty, Sobol first-els 0.7516/0.2982 distinct, rg hits = data
        # volume-column numeric coincidence = batch-69 precedent face)
        "t101_v4_a10_combo_unc": 20314500,
        # T-101-V4-A10-REGIMECOMBO dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20314500, cell_idx])) W1 semantics -- r442 bm-a
        "t101_v4_a11_xsel_scrnull": 20315000,
        # T-101-V4-A11-XSELECT random-topk-selection nulls K=200/cell
        # (rng([20315000, cell_idx]) per cell) -- r443 bm-a; three-step law
        # verified pre-freeze (119 int bases zero-collision, band 20315xxx
        # rg-empty, first-el distinctness check, rg hits = Money0923 volume
        # column numeric coincidence = t34/batch-69 precedent face)
        "t101_v4_a11_xsel_unc": 20315500,
        # T-101-V4-A11-XSELECT dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20315500, cell_idx])) W1 semantics -- r443 bm-a
        "t101_v4_a12_predcond_scrnull": 20316000,
        # T-101-V4-A12-PREDCOND random-conditioning nulls K=200/cell
        # (rng([20316000, cell_idx]) per cell) -- r445 bm-a; three-step law
        # verified pre-freeze (122 numeric bases, both new bases zero-collision
        # vs all existing values; band 20316xxx rg-empty in code; the only
        # in-registry dups are two pre-registry-law legacy pairs 20260923
        # [p5_random_entry/factor_ic_screens] and 48000 [p4_pairs/
        # p1d_gdhs_quarterly], historical frozen, untouched; first-el
        # distinctness check passed; repo rg hits for the bare numbers =
        # data volume-column numeric coincidence = t34/batch-69 precedent face)
        "t101_v4_a12_predcond_unc": 20316500,
        # T-101-V4-A12-PREDCOND dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20316500, cell_idx])) W1 semantics -- r445 bm-a
        "trial_labor_w11_gen": 20317000,
        # W11 STD-gate (std20_hi/std10_hi high-dispersion confirm) wave:
        # 5,000-draw Sobol generation axis draws (rng([20317000+family_idx,
        # 7919]) integer-axis draw per W1-W10 lineage); draft berth
        # 20316000/20316500 collided with A12 keys -> +500 re-take per draft
        # clause-5 (W9 double-collision precedent) -- r441 bm-b; three-step law
        # verified at freeze (123 int bases zero-collision, first-els
        # 673516273/1869008098/1084768275 mutually distinct vs all bases,
        # null band 20317500..20317699 and unc band 20318000..20318200 clean,
        # rg hits = berth-declaration docs x2 + data volume-column numeric
        # coincidence x3 = t34/batch-69 precedent face; facts =
        # results/_r441bmb_w11_seed_law_facts.json)
        "trial_labor_w11_scrnull": 20317500,
        # s2 screen K=200 same-structure random-signal nulls
        # (rng([20317500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (std gate leg merged into same-grid same-param-space draw)
        "trial_labor_w11_unc": 20318000,
        # W11 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20318000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "t101_v4_a13_predface_scrnull": 20318500,
        # T-101-V4-A13-PREDFACE circular-shift nulls K=200/cell
        # (rng([20318500, cell_idx]) offsets in [1, n-1]) -- r446 bm-a;
        # three-step law verified pre-freeze (126 registry keys, both new
        # bases zero-collision vs all existing values; canon first-els
        # int(default_rng(s).integers(0,2**31)) = 295045756 / 989029903
        # mutually distinct and vs all existing bases; derive bands
        # 20318500..20318539 and 20319000..20319039 clean with 500-gap;
        # rg repo code face 20318xxx/20319xxx zero hits)
        "t101_v4_a13_predface_unc": 20320000,
        # T-101-V4-A13-PREDFACE circular block bootstrap B=2000 block=10
        # (rng([20320000, cell_idx])) percentile CI face -- r446 bm-a;
        # declared base = actual base by construction (A12 rebind law:
        # this batch does not route through fv.dual_nulls, no inherited-base
        # mismatch face)
        # RE-TAKE 20319000 -> 20320000 (zero-run correction, r446 bm-a):
        # bm-c r239 addendum d6909bf32 froze innovation_quota_w3_mom=20319000
        # on origin while the A13 freeze commit was unpushed in-rebase
        # (lawful race, later-yields law; push-reject = zero-leak window;
        # runner never burned = zero cells affected; W9/W11/SLOT-3 re-take
        # precedent family). 20319500 probed and discarded (canon first-el
        # 883288081 collides an existing base's canon first-el). Three-step
        # law re-verified post-re-take vs merged registry (129 keys incl.
        # bm-c 20319000: zero exact collision for 20320000; canon first-el
        # 1700875381 distinct vs all bases; bands 20320000..20320039 clean;
        # rg code face AND data/daily volume face both zero hits)

        # INNOVATION-QUOTA-SLOT-3 / HIGHERMOM-TIMING-P1 (r239 bm-c; take-number
        # TWO: draft base 20317500 collided mid-flight with bm-b r441 W11
        # scrnull re-take landed on origin 21:08 while r239 was unpushed
        # in-rebase -- later-yields law, SLOT-3 re-takes; runner not yet built
        # = zero cells burned on 20317500, zero verdict impact; re-take 20319000
        # band rg zero repo hits (20318500 discarded: data-volume column
        # coincidence x4); single base key, k-indexed sub-streams like
        # innovation_quota_w1_repo W1 semantics
        "innovation_quota_w3_mom": 20319000,  # random-episode nulls K=2000 + virtual starts K=1000 + splits 100
        # INNOVATION-QUOTA-SLOT-4 VOLREGIME_TIMING_P1 (zoo #96
        # volume_regime_bimodal; berth bm-c r243, freeze r244 bm-c):
        # random-day-placement nulls K=2000 + virtual starts K=1000 +
        # splits 100, k-indexed sub-streams rng([20322000, k]) like W3;
        # three-step law r244 ALL GREEN (129-key zero-collision, canon
        # first-el 615887398 distinct, band 20322000 clean; rg hits =
        # sse.csv/sh513990.csv volume-column numeric coincidences
        # t34/batch-69 precedent family + prereg own text); +500 ladder
        # above W12 declared berths 20320500/20321000/20321500
        # (unregistered at freeze, bm-a r447 MSG-2225)
        "innovation_quota_w4_volregime": 20322000,
        # INNOVATION-QUOTA-SLOT-5 ICU_MA_TIMING_P1 (zoo #86 icu_ma_timing
        # Siegel repeated-median regression endpoint timing; berth bm-c
        # r247, freeze r248 bm-c): random-day-placement nulls K=2000 +
        # virtual starts K=1000 + splits 100, k-indexed sub-streams
        # rng([20322500, k]) like W3/W4; three-step law r248 live
        # re-verified ALL GREEN (134-key full import view, 130 existing
        # distinct bases zero-collision, canon first-el 989747964
        # distinct, band 20322500 clean; rg hits = sh513070.csv volume-column numeric coincidence t34/69
        # precedent family + own berth/prereg/catalog text); +500 ladder
        # above W4 20322000 (W12 trio 20320500/20321000/20321500
        # registered bm-b r444 before this window)
        "innovation_quota_w5_icu_ma": 20322500,
        # TRIAL_LABOR_W12 RSQR-gate (rsqr20_hi/rsqr10_hi trend-fit-quality
        # confirm, three-value axis per W4 VOL / W11 STD precedent) wave:
        # 5,000-draw Sobol generation axis draws (rng([20320500+family_idx,
        # 7919]) integer-axis draw per W1-W11 lineage); berths drafted bm-a
        # r447 (berth declaration MSG-20260929-2225), adopted+frozen bm-b
        # r444 (four-straight adoption AMP->W9/MOM->W10/STD->W11/RSQR->W12);
        # three-step law verified at freeze (143-key registry zero-collision
        # on all three berths; canon first-els 1294340368/1873818339/
        # 561143918 mutually distinct vs all bases; null band
        # 20321000..20321199 and unc band 20321500..20321700 clean; rg hits
        # = berth-declaration docs + data volume-column numeric coincidences
        # t34/batch-69 precedent face; facts = results/_r444bmb_w12_seed_
        # law_facts.json)
        "trial_labor_w12_gen": 20320500,
        # s2 screen K=200 same-structure random-signal nulls
        # (rng([20321000, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (rsqr gate leg merged into same-grid same-param-space draw)
        "trial_labor_w12_scrnull": 20321000,
        # W12 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20321500, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w12_unc": 20321500,

        # [r453 bm-a yield-note: duplicate bm-a freeze block removed per
        # fleet README sec.4 commit-time order (bm-b r444 02:25:52 earlier
        # vs bm-a r453 02:30:49 later -> later yields); independent bm-a
        # three-step re-verification all-green on the same berths kept as
        # cross-check at results/_r453bma_w12_seed_law_facts.json]

        # INNOVATION-QUOTA-SLOT-6 RRG-ROTATION-P1 (zoo #91
        # rrg_quadrant_rotation, core48 month-end quadrant rotation):
        # virtual starts K=1000 + splits 100 k-indexed sub-streams
        # rng([20324500, k]) per W1-W5 lineage; +500 ladder above W5
        # 20322500 and above the W13 berthed-but-unregistered draft seeds
        # 20323000/20323500/20324000 (r456 berth declaration; W13 freeze
        # will register those -- 20324500 clear of both faces); registered
        # r459 bm-a freeze window, three-step law verified same window
        # (results/_r459bma_w6_seed_law_facts.json)
        "innovation_quota_w6_rrg_rotation": 20324500,

        # INNOVATION-QUOTA-SLOT-7 NNL-BREADTH-P1 (zoo #87
        # nh_nl_breadth, core48 net-new-high breadth two-sided
        # extreme-turn gate): virtual starts K=1000 + splits 100
        # k-indexed sub-streams rng([20325000, k]) per W1-W6 lineage;
        # +500 ladder above W6 20324500; berthed bm-c r254 (MSG-
        # 20260930-0547, commit 57636c713), registered r255 bm-c
        # freeze window, three-step law FULL import view verified
        # same window (facts = results/_r255bmc_w7_seed_law_facts.json);
        # W13 berthed-but-unregistered trio 20323000/20323500/20324000
        # (bm-a r456) stays clear of this base by construction
        "innovation_quota_w7_nlnl": 20325000,

        # TRIAL_LABOR_W13 SUMN up-purity gate (sumn20_lo/sumn10_lo
        # down-share-of-absolute-amplitude low-quantile window,
        # three-value axis per W4 VOL / W11 STD / W12 RSQR precedent)
        # wave: 5,000-draw Sobol generation axis draws
        # (rng([20323000+family_idx, 7919]) integer-axis draw per
        # W1-W12 lineage); berthed bm-a r456 (draft + probe MSG-
        # 20260930-0356-bma-ALL; bm-c r251/r252 independent cross-
        # validation yielded per fleet README sec.4 commit-time
        # order, digest DIGEST-20260930-w13-sumn-yield-crossvalidation
        # .md); adopted+frozen bm-a r461 (drafting machine's next
        # round self-freeze, W5 r247->r248 / W6 r458->r459 / W7
        # r254->r255 timeline mirror); three-step law verified at
        # freeze (135-key pre-registration import view zero-collision
        # on all three berths; canon first-els mutually distinct vs
        # all bases; null band 20323500..20323699 and unc band
        # 20324000..20324200 clean; rg hits = berth/freeze docs +
        # registry placeholder comments, all self-classifiable per
        # W7 r255 precedent; facts = results/_r461bma_w13_seed_law_
        # facts.json)
        "trial_labor_w13_gen": 20323000,
        # s2 screen K=200 same-structure random-signal nulls
        # (rng([20323500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (sumn gate leg merged into same-grid same-param-space draw)
        "trial_labor_w13_scrnull": 20323500,
        # W13 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20324000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
        "trial_labor_w13_unc": 20324000,
        # INNOVATION-QUOTA-SLOT-8 COV-SHRINK-AB-P1 (zoo #89
        # cov_shrinkage_lw adoption route: A/B variant batch sample-cov
        # vs LW-shrunk-cov fed to the same frozen T-27 MaxDiv pipeline,
        # rolling 252d@21td anchors over the 28-member x1 sleeve matrix):
        # virtual starts K=1000 + splits 100 k-indexed sub-streams
        # rng([20325500, k]) per W1-W7 lineage; +500 ladder above W7
        # 20325000 (W13 berthed-but-unregistered trio 20323000/
        # 20323500/20324000 stays clear by construction); berthed bm-b
        # r448 (draft sec.B berth band), registered r450 bm-b freeze
        # window, three-step law FULL import view verified same window
        # (facts = results/_r450bmb_w8_seed_law_facts.json)
        "innovation_quota_w8_covshrink": 20325500,

        # INNOVATION-QUOTA-W9 CROWD-VOTE-P1 four-vote crowding state
        # gate (zoo #84 crowding_vote, bm-c r259 berth / r260 freeze
        # window); +500 ladder above W8 20325500 (last registered quota
        # base); three-step law FULL import view verified same window
        # (facts = results/_r260bmc_w9_seed_law_facts.json); W13 trio
        # (registered bm-a r461) stays clear of this base by construction
        "innovation_quota_w9_crowd": 20326000,

        # INNOVATION-QUOTA-W10 PREMIUM-SENT-P1 cross-mean premium_adj
        # IC routing-input state gate (zoo #97 etf_premium_sentiment
        # CORRECTED face, bm-c r264 berth / r265 freeze window); +500
        # ladder above W9 20326000 (last registered quota base);
        # k-sub-stream semantics same law (nulls k<2000, splits
        # k in [3000,3100), starts band reserved-unused); three-step
        # law FULL import view verified same window
        # (facts = results/_r265bmc_w10_seed_law_facts.json)
        "innovation_quota_w10_premium": 20326500,

        # INNOVATION-QUOTA-W11 MOM-TIMING-P1 index higher-moment
        # timing gate (zoo #95 index_higher_mom_timing, bm-c r267
        # berth / r268 freeze window); +500 ladder above W10 20326500
        # (last registered quota base); k-sub-stream semantics same law
        # (nulls k<2000, splits k in [3000,3100), starts band
        # k in [2000,3000)); three-step law FULL import view verified
        # same window (facts = results/_r268bmc_w11_seed_law_facts.json)
        "innovation_quota_w11_momtiming": 20327000,

    }

# ------------------------------------------- T-02 close-out: v2 batch-gate verdicts (D1/D3/D4 columns)

def g1_prime_v2(sharpe_full, returns, batch_cells, pool: str = "core48",
                n_trades: int | None = None, n_entries: int | None = None,
                min_trades: int = 30, ci_seed: int = 20260923,
                results_dir: str = RESULTS_DIR,
                null_pool: dict | None = None,
                n_eff_override: int | None = None,
                passive_override: float | None = None) -> dict:
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
    passive_override (additive, REPO_CALENDAR_P2): per-cell batch-own
    passive (each judged cell on its own window of the panel calendar);
    named-pool reader stays the default otherwise.
    """
    line = skill_line_v2(batch_cells=batch_cells, pool=pool,
                         results_dir=results_dir, null_pool=null_pool,
                         n_eff_override=n_eff_override,
                         passive_override=passive_override)
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


# --------------------------------------- O-20260930-1058 registration reform (L3)
# Reform law (O-20260930-1058 §二2): L3 registration gate = batch-internal BH FDR
# (q<=10% -- REPLACING the global-ledger DSR>=0.95 execution whose structural
# unreachability as the ledger inflates was the "always zero results" root
# cause) + four-dimension composite score. Effective from the W14 verdict face
# (O-1058 §三2); W13 and earlier waves keep g2_registration_v2 per their frozen
# preregs -- this section is ADDITIVE ONLY, zero behavior change for existing
# consumers. This library carries the MECHANISM; weight VALUES freeze at the
# REGISTRATION_REFORM_FDR4D freeze window (prereg §9-②, pre-registered, loop
# side). Scope division per MSG-20260930-1332: bm-c = W14+ standing standards
# canon; bm-a T-126 = REEVAL-18 drill product line consuming the same refs.

REFORM_Q_LEVEL = 0.10  # BH batch-internal FDR q (O-1058 §二2 verbatim: q<=10%)

REFORM_DIMENSIONS = ("ret", "robust", "anti_overfit", "anti_luck")

# Sub-metric direction map (+1 higher-better, -1 lower-better). Mechanism face;
# a key present here is not forced into scoring -- frozen sub-weights decide.
#   ret        Sharpe / annualized / return-ceiling O-1126 / beat rates
#   robust     cost-x2 Sharpe / worst-regime-segment Sharpe / bootstrap CI low
#   anti_overfit  family PBO (CSCV) / D6 cross-family |corr|
#   anti_luck  batch-internal deflated DSR (n_trials = batch size, NOT the
#              global ledger; one of four dimensions, never the sole gate)
REFORM_SUB_DIRECTIONS = {
    "ret": {"sharpe_full_L": +1, "annualized_ret_L": +1, "return_ceiling_O1126": +1,
            "beat6m_rate_L": +1, "beat12m_rate_L": +1},
    "robust": {"cost_x2_sharpe_L": +1, "regime_min_sharpe_L": +1,
               "bootstrap_ci_low_L": +1},
    "anti_overfit": {"family_pbo": -1, "d6_max_abs_corr": -1},
    "anti_luck": {"batch_dsr": +1},
}

# --- Freeze-window step-2 ratification (2026-09-30 bm-c r271, prereg §9-②
# DRAFT -> FROZEN). Ratified BEFORE any W14+ reeval burn; engine-reads
# independent, so lawful inside RW-5 (MSG-1330 §2 "既有件内容修订合法");
# append-only ratification record lives in the prereg §9. Values below are
# the SINGLE canonical source -- W14 scoring runners consume these
# constants directly (禁手抄判线), never hand-copied numbers. ---
# No single dimension >= 0.50: CEO "多维度考量" (O-1058) mechanical
# expression -- single-dim dictatorship is impossible by construction.
REFORM_DIM_WEIGHTS = {
    "ret": 0.30, "robust": 0.30, "anti_overfit": 0.20, "anti_luck": 0.20,
}
# Within-dimension sub-weights (each dim sums to 1). Keys are a subset of
# REFORM_SUB_DIRECTIONS[dim]; positive-weight keys only are consumed.
REFORM_SUB_WEIGHTS = {
    "ret": {"sharpe_full_L": 0.40, "annualized_ret_L": 0.20,
            "return_ceiling_O1126": 0.10, "beat6m_rate_L": 0.15,
            "beat12m_rate_L": 0.15},
    "robust": {"cost_x2_sharpe_L": 0.40, "regime_min_sharpe_L": 0.35,
               "bootstrap_ci_low_L": 0.25},
    "anti_overfit": {"family_pbo": 0.60, "d6_max_abs_corr": 0.40},
    "anti_luck": {"batch_dsr": 1.00},
}
# L4 wide-in cap: top-N per wave promoted to TRIAL-* paper probation
# (宽进不滥进; forward monthly exam stays the true final gate).
REFORM_TOPN_PER_WAVE = 3
# O-1126 return-ceiling comparison baseline. Candidates per O-20260929-1116:
# EW-48 / five-member-EW / B_MAXDIV. Ratified = five-member equal weight of
# the O-1555 frozen universe {510300,510050,510500,512100,588000}: the only
# candidate that is simultaneously (a) deterministic and batch-independent
# (cross-wave comparability of a standing standard), and (b) the investable
# ETF face (落地性). EW-48 imports non-investable members for the ETF line;
# B_MAXDIV is a moving target (promotion-dependent composition), not a
# passive baseline. Metric = candidate annualized minus baseline annualized
# over the same evaluation window, higher=better (direction already frozen).
REFORM_CEILING_BASELINE = "five_member_ew_O1555"


def reform_weight_freeze_integrity() -> dict:
    """Deterministic audit of the frozen step-2 values (no I/O, no engine).

    Consumed by selftest and by the W14 scoring runner pre-flight: dim
    weights cover all four dims, sum to 1, and no single dim >= 0.5; every
    sub-weight key is a known direction; each dim's sub-weights sum to 1;
    top-N is a positive int.
    """
    errs = []
    if set(REFORM_DIM_WEIGHTS) != set(REFORM_DIMENSIONS):
        errs.append("dim_weights keys != REFORM_DIMENSIONS")
    total = sum(REFORM_DIM_WEIGHTS.values())
    if abs(total - 1.0) > 1e-9:
        errs.append(f"dim_weights sum={total} != 1")
    for d, w in REFORM_DIM_WEIGHTS.items():
        if float(w) >= 0.5:
            errs.append(f"single-dim dictatorship {d}={w} (>=0.5)")
    for d, subs in REFORM_SUB_WEIGHTS.items():
        if d not in REFORM_SUB_DIRECTIONS:
            errs.append(f"unknown dim {d} in sub_weights")
            continue
        unknown = [s for s in subs if s not in REFORM_SUB_DIRECTIONS[d]]
        if unknown:
            errs.append(f"unknown sub keys {unknown} in {d}")
        st = sum(subs.values())
        if abs(st - 1.0) > 1e-9:
            errs.append(f"sub_weights[{d}] sum={st} != 1")
    if not isinstance(REFORM_TOPN_PER_WAVE, int) or REFORM_TOPN_PER_WAVE < 1:
        errs.append("REFORM_TOPN_PER_WAVE must be int >= 1")
    return {"gate": "reform_weight_freeze_integrity", "errors": errs,
            "pass": not errs, "dim_weights": REFORM_DIM_WEIGHTS,
            "sub_weights": REFORM_SUB_WEIGHTS,
            "top_n_per_wave": REFORM_TOPN_PER_WAVE,
            "ceiling_baseline": REFORM_CEILING_BASELINE}


def _pct_ranks(values: dict) -> dict:
    """Within-batch percentile ranks in (0,1) -- midrank ties, None dropped.

    Mechanism-frozen normalization for the reform composite score: scale-free,
    robust to outliers, and inherently batch-internal (O-1058 replaces the
    global-ledger execution with batch-internal faces). n=1 -> 0.5 honest.
    """
    items = [(cid, v) for cid, v in values.items() if v is not None]
    if not items:
        return {}
    n = len(items)
    if n == 1:
        return {items[0][0]: 0.5}
    order = sorted(items, key=lambda t: t[1])
    ranks = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and order[j + 1][1] == order[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # 1-based midrank of the tie block
        for k in range(i, j + 1):
            ranks[order[k][0]] = (avg_rank - 0.5) / n
        i = j + 1
    return ranks


def bh_batch_fdr(p_values: dict, q: float = REFORM_Q_LEVEL) -> dict:
    """Benjamini-Hochberg batch-internal FDR (O-20260930-1058 §二2 L3).

    Step-up over ONE batch's p-values: BH adjusted q_(i) = min_{j>=i}
    min(m/j * p_(j), 1) computed top-down (monotone); a candidate passes iff
    adjusted q <= q. Equivalent to the classical k* rule (largest k with
    p_(k) <= (k/m)*q; all i<=k pass). Ties resolve deterministically by id
    order. m=1 degenerates honestly to p<=q. None p-values are refused
    honestly (excluded from m, reported missing, never zero-filled).
    """
    out_items = {cid: {"p": p, "bh_q": None, "fdr_pass": False}
                 for cid, p in p_values.items()}
    items = sorted(((cid, p) for cid, p in p_values.items() if p is not None),
                   key=lambda t: (t[1], t[0]))
    m = len(items)
    if m == 0:
        return {"gate": "bh_batch_fdr", "q_level": q, "m": 0, "items": out_items}
    adjusted = [None] * m
    running = float("inf")
    for idx in range(m - 1, -1, -1):
        cid, p = items[idx]
        rank = idx + 1
        running = min(running, (m / rank) * p, 1.0)
        adjusted[idx] = running
    for idx, (cid, p) in enumerate(items):
        out_items[cid]["bh_q"] = adjusted[idx]
        out_items[cid]["fdr_pass"] = bool(adjusted[idx] <= q)
    return {"gate": "bh_batch_fdr", "q_level": q, "m": m, "items": out_items}


def reform_composite_scores(member_metrics: dict, dim_weights: dict,
                            sub_weights: dict) -> dict:
    """Four-dimension composite scores within one batch (O-1058 §二2).

    Per-dimension sub-score = weighted mean of within-batch midrank percentiles
    of the dimension's PRESENT sub-metrics (direction-corrected via
    REFORM_SUB_DIRECTIONS so every percentile reads "higher=better");
    composite = sum(dim_weight * dim_sub_score). Weights MUST be pre-frozen at
    the reform freeze window (values live in the prereg, not here). Missing
    dimensions (no present weighted sub-metric) are refused honestly: the
    member gets missing_dims and composite None -- never silently zero-filled.
    """
    errs = []
    dims = {}
    for d in REFORM_DIMENSIONS:
        if d not in dim_weights:
            errs.append(f"dim_weights missing {d}")
        else:
            w = float(dim_weights[d])
            if w < 0.0:
                errs.append(f"negative dim weight {d}")
            dims[d] = w
    if not errs and abs(sum(dims.values()) - 1.0) > 1e-9:
        errs.append("dim_weights must sum to 1")
    if errs:
        return {"error": errs, "scores": {}}
    cids = list(member_metrics)
    # per (dim, sub) -> within-batch quality percentiles
    per_dim_ranked = {}
    for d in REFORM_DIMENSIONS:
        subs_w = sub_weights.get(d, {}) or {}
        ranked = {}
        for sub, sw in subs_w.items():
            if float(sw) <= 0:
                continue
            if sub not in REFORM_SUB_DIRECTIONS[d]:
                return {"error": [f"unknown sub-metric {d}.{sub}"], "scores": {}}
            sign = REFORM_SUB_DIRECTIONS[d][sub]
            raw = {cid: (member_metrics[cid].get(d, {}) or {}).get(sub)
                   for cid in cids}
            corrected = {cid: (sign * v if v is not None else None)
                        for cid, v in raw.items()}
            ranked[sub] = _pct_ranks(corrected)
        per_dim_ranked[d] = ranked
    scores = {}
    for cid in cids:
        dim_scores = {}
        missing = []
        composite = 0.0
        for d in REFORM_DIMENSIONS:
            w = dims[d]
            if w == 0.0:
                dim_scores[d] = None
                continue
            num = 0.0
            den = 0.0
            for sub, r in per_dim_ranked[d].items():
                rv = r.get(cid)
                if rv is None:
                    continue
                sw = float(sub_weights[d][sub])
                num += sw * rv
                den += sw
            if den <= 0.0:
                missing.append(d)
                dim_scores[d] = None
                continue
            dim_scores[d] = num / den
            composite += w * (num / den)
        scores[cid] = {
            "composite": (None if missing else composite),
            "dim_scores": dim_scores,
            "missing_dims": missing,
        }
    return {"error": None, "scores": scores}


def g2_reform_fdr4d(member_metrics: dict, dim_weights: dict, sub_weights: dict,
                    batch_p_values: dict, q: float = REFORM_Q_LEVEL) -> dict:
    """Reformed L3 registration gate (O-20260930-1058 §二2): batch-internal BH
    FDR + four-dimension composite score.

    eligible_reform = fdr_pass AND complete composite (no missing dims).
    The global-ledger DSR>=0.95 execution is GONE here; the deflated Sharpe
    ratio enters as the anti_luck DIMENSION computed with n_trials = batch
    size (one of four, never the sole gate). L4 (top-N -> TRIAL-*) ranks by
    composite among eligible_reform members -- selection stays with the
    caller's prereg (N and paper risk caps frozen there).
    """
    fdr = bh_batch_fdr(batch_p_values, q)
    comp = reform_composite_scores(member_metrics, dim_weights, sub_weights)
    if comp.get("error"):
        return {"gate": "g2_reform_fdr4d", "q_level": q, "m": fdr["m"],
                "error": comp["error"], "members": {}}
    members = {}
    for cid, sc in comp["scores"].items():
        f = fdr["items"][cid]
        members[cid] = {
            "p": f["p"],
            "bh_q": f["bh_q"],
            "fdr_pass": f["fdr_pass"],
            "composite": sc["composite"],
            "dim_scores": sc["dim_scores"],
            "missing_dims": sc["missing_dims"],
            "eligible_reform": bool(f["fdr_pass"] and sc["composite"] is not None),
        }
    return {"gate": "g2_reform_fdr4d", "q_level": q, "m": fdr["m"],
            "error": None, "members": members}


# ---------------------------------------------------------------- F12 CostPatch (single source)

from knowledge import cost_spec as _cost_spec  # RW-3 single-source (T-127)

COST_X2_RATE = _cost_spec.X2_RATE  # = 2x FeeSchedule-derived x1 (was G2 literal)


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
    line500 = skill_line_v2(batch_cells=50_000)
    ok("skill_line_v2 n_eff = live chain head + cells (data-driven, no frozen count)",
       line50["n_eff"] == ledger_head()["total"] + 50)
    # r347 bm-b: probe gap widened 500 -> 50_000. At chain-head scale (~287k)
    # the raw null_term gap for +50 vs +500 cells (~7.6e-5) falls below the
    # 4-decimal rounding resolution of the returned dict, so the rounded
    # values compared equal and the check false-failed while the underlying
    # function stays strictly monotone. Wider gap keeps the check's intent
    # (data-driven monotonicity in N_eff) robust at any ledger scale.
    ok("skill_line_v2 monotone in N_eff", line500["null_term"] > line50["null_term"])
    ok("skill_line_v2 line = max(passive_term, null_term)",
       abs(line50["line"] - max(line50["passive_term"], line50["null_term"])) < 1e-9)
    ok("skill_line_v2 passive core48 strict(>=0.379)+0.10", line50["passive_term"] >= 0.479)
    # r259 prev-echo guard face: n_eff_override pins the chain position so a
    # deterministic re-execution of an already-appended batch does not feed
    # its own echo into the line (r253 single-count redo law).
    line_ov = skill_line_v2(batch_cells=50, n_eff_override=1000)
    ok("skill_line_v2 n_eff_override pins chain position",
       line_ov["n_eff"] == 1000
       and abs(line_ov["null_term"] - (line50["mu_null"] + line50["sigma_null"]
                                       * math.sqrt(2.0 * math.log(1000)))) < 5e-4)

    # DSR: honest multiple-testing calibration. At N=2727 the 0.95 gate demands full-period
    # Sharpe ~2.1+ (6y) — a 1.6 edge must NOT clear it; a 2.5 edge must. Noise fails hard.
    good16 = _synth_returns(1512, 1.6, seed=11)
    good25 = _synth_returns(1512, 2.5, seed=13)
    noise = _synth_returns(1512, 0.0, seed=12)
    g1_ov = g1_prime_v2(1.2, good25, batch_cells=10, n_eff_override=1234)
    ok("g1_prime_v2 passes n_eff_override through (redo echo guard)",
       g1_ov["skill_line"]["n_eff"] == 1234)
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

    # r239: non-dict top-level JSONs (C-arm metrics.json list form) must be
    # skipped without crashing the recursive scan (real-form mirror fixture)
    os.makedirs(sub, exist_ok=True)
    list_path = os.path.join(sub, "c_arm_metrics.json")
    try:
        with open(list_path, "w", encoding="utf-8") as fh:
            json.dump([{"round": 1, "ok": True}], fh)
        ok("ledger_head tolerates non-dict JSONs (r239 C-arm list form)",
           isinstance(ledger_head()["total"], int))
    finally:
        os.unlink(list_path)
        os.rmdir(sub)

    # pit-95 guard: finalize_already_landed read-only tripwire
    os.makedirs(sub, exist_ok=True)
    guard_path = os.path.join(sub, "guard_ledger.json")
    guard_rel = os.path.join(sub, "guard_rel.json")
    guard_repo_rel = os.path.join(sub, "guard_repo_rel.json")
    try:
        with open(guard_path, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 100,
                                         "batch_trials": 7, "total": 107,
                                         "batch": "guard-selftest-batch"}}, fh)
        with open(guard_rel, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 10,
                                         "batch_trials": 5, "total": 15,
                                         "batch": "guard-rel-batch"}}, fh)
        with open(guard_repo_rel, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 20,
                                         "batch_trials": 6, "total": 26,
                                         "batch": "guard-repo-rel-batch"}}, fh)
        landed = finalize_already_landed("guard-selftest-batch", guard_path)
        ok("finalize_already_landed trips on landed batch (pit-95 guard)",
           isinstance(landed, dict) and landed["total"] == 107
           and landed["batch"] == "guard-selftest-batch")
        ok("finalize_already_landed: absolute / results-relative / "
           "repo-relative file_name forms all resolve",
           finalize_already_landed("guard-rel-batch",
                                   "_selftest_sub/guard_rel.json")[
               "total"] == 15
           and finalize_already_landed(
               "guard-repo-rel-batch",
               "results/_selftest_sub/guard_repo_rel.json")[
               "total"] == 26)
        ok("finalize_already_landed None on different batch name",
           finalize_already_landed("other-batch", guard_path) is None)
        ok("finalize_already_landed None on missing file",
           finalize_already_landed("guard-selftest-batch",
                                   os.path.join(sub, "nope.json")) is None)
        ok("finalize_already_landed None when file_name is None",
           finalize_already_landed("guard-selftest-batch", None) is None)
        with open(guard_path, "w", encoding="utf-8") as fh:
            fh.write("{corrupt json")
        ok("finalize_already_landed None on corrupt file "
           "(crash-recovery re-finalize lawful)",
           finalize_already_landed("guard-selftest-batch", guard_path) is None)
    finally:
        for p in (guard_path, guard_rel, guard_repo_rel):
            if os.path.exists(p):
                os.unlink(p)
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

    # O-20260930-1058 registration reform (L3): BH batch-internal FDR + 4-dim
    # composite mechanism. Known-answer checks first (BH step-up by hand).
    bh_all = bh_batch_fdr({"A": 0.01, "B": 0.02, "C": 0.03, "D": 0.04})
    ok("bh_batch_fdr: hand-checked all-pass batch (m=4, all adj q=0.04<=0.10)",
       bh_all["m"] == 4 and all(v["fdr_pass"] for v in bh_all["items"].values())
       and all(abs(v["bh_q"] - 0.04) < 1e-12 for v in bh_all["items"].values()))
    bh_sel = bh_batch_fdr({"A": 0.001, "B": 0.02, "C": 0.5})
    ok("bh_batch_fdr: hand-checked selective batch (A,B pass @0.003/0.03; C fail @0.5)",
       bh_sel["items"]["A"]["fdr_pass"] and bh_sel["items"]["B"]["fdr_pass"]
       and not bh_sel["items"]["C"]["fdr_pass"]
       and abs(bh_sel["items"]["A"]["bh_q"] - 0.003) < 1e-12
       and abs(bh_sel["items"]["B"]["bh_q"] - 0.03) < 1e-12)
    ok("bh_batch_fdr: m=1 degenerates honestly to p<=q",
       bh_batch_fdr({"X": 0.10})["items"]["X"]["fdr_pass"]
       and not bh_batch_fdr({"X": 0.11})["items"]["X"]["fdr_pass"])
    ok("bh_batch_fdr: None p refused honestly (excluded from m, not zero-filled)",
       bh_batch_fdr({"X": None, "Y": 0.01})["m"] == 1
       and bh_batch_fdr({"X": None, "Y": 0.01})["items"]["X"]["bh_q"] is None)
    pr = _pct_ranks({"a": 1.0, "b": 2.0, "c": 3.0})
    pr_tie = _pct_ranks({"a": 1.0, "b": 1.0, "c": 2.0})
    ok("_pct_ranks: midrank percentiles + tie block averaging (n=3)",
       abs(pr["a"] - 1 / 6) < 1e-12 and abs(pr["b"] - 0.5) < 1e-12
       and abs(pr["c"] - 5 / 6) < 1e-12
       and abs(pr_tie["a"] - 1 / 3) < 1e-12 and abs(pr_tie["b"] - 1 / 3) < 1e-12
       and abs(pr_tie["c"] - 5 / 6) < 1e-12)
    mm = {
        "X": {"ret": {"sharpe_full_L": 2.0, "beat6m_rate_L": 0.60},
              "anti_overfit": {"family_pbo": 0.10}, "anti_luck": {"batch_dsr": 0.40}},
        "Y": {"ret": {"sharpe_full_L": 1.0, "beat6m_rate_L": 0.50},
              "anti_overfit": {"family_pbo": 0.50}, "anti_luck": {"batch_dsr": 0.20}},
    }
    w_ok = {"ret": 0.4, "robust": 0.0, "anti_overfit": 0.3, "anti_luck": 0.3}
    sw = {"ret": {"sharpe_full_L": 0.7, "beat6m_rate_L": 0.3},
          "anti_overfit": {"family_pbo": 1.0}, "anti_luck": {"batch_dsr": 1.0}}
    cs = reform_composite_scores(mm, w_ok, sw)
    ok("reform_composite_scores: direction-corrected percentiles (low PBO ranks high)",
       abs(cs["scores"]["X"]["dim_scores"]["ret"]
           - (0.7 * 0.75 + 0.3 * 0.75)) < 1e-12
       and abs(cs["scores"]["X"]["dim_scores"]["anti_overfit"] - 0.75) < 1e-12
       and abs(cs["scores"]["Y"]["dim_scores"]["anti_overfit"] - 0.25) < 1e-12
       and cs["scores"]["X"]["composite"] > cs["scores"]["Y"]["composite"])
    ok("reform_composite_scores: dim weights must sum to 1 (refused honestly)",
       reform_composite_scores(mm, {"ret": 0.9, "robust": 0.0,
                                    "anti_overfit": 0.05, "anti_luck": 0.04},
                               sw)["error"] is not None)
    mm_missing = dict(mm)
    mm_missing["Y"] = {"ret": {"sharpe_full_L": 1.0},
                       "anti_overfit": {"family_pbo": 0.50}, "anti_luck": {}}
    cs2 = reform_composite_scores(mm_missing, w_ok, sw)
    ok("reform_composite_scores: missing dim refused (composite None, no zero-fill)",
       cs2["scores"]["Y"]["composite"] is None
       and "anti_luck" in cs2["scores"]["Y"]["missing_dims"])
    g2r = g2_reform_fdr4d(mm, w_ok, sw, {"X": 0.01, "Y": 0.5})
    ok("g2_reform_fdr4d: FDR + composite joint verdict (X eligible, Y not)",
       g2r["members"]["X"]["eligible_reform"] and not g2r["members"]["Y"]["eligible_reform"]
       and g2r["members"]["X"]["fdr_pass"] and not g2r["members"]["Y"]["fdr_pass"])
    ok("g2_reform_fdr4d: anti-luck DSR is a DIMENSION not the sole gate (O-1058)",
       g2r["members"]["X"]["dim_scores"]["anti_luck"] is not None
       and g2r["members"]["Y"]["dim_scores"]["anti_luck"] is not None)
    ok("reform: unknown sub-metric refused; existing g2_registration_v2 untouched",
       reform_composite_scores(mm, w_ok, {"ret": {"nope": 1.0},
                                          "anti_overfit": {}, "anti_luck": {}})["error"] is not None
       and g2_registration_v2(True, 0.97, 0.20)["eligible_v2"])
    wf = reform_weight_freeze_integrity()
    ok("reform step-2 FROZEN integrity: 4 dims, sum=1, no dim>=0.5, "
       "sub keys known, per-dim sums=1, top-N int>=1",
       wf["pass"] and set(wf["dim_weights"]) == set(REFORM_DIMENSIONS)
       and abs(sum(wf["dim_weights"].values()) - 1.0) < 1e-9
       and all(v < 0.5 for v in wf["dim_weights"].values())
       and wf["top_n_per_wave"] == REFORM_TOPN_PER_WAVE
       and wf["ceiling_baseline"] == REFORM_CEILING_BASELINE)
    ok("reform step-2 FROZEN weights pass the composite gate unmodified "
       "(end-to-end consumption, zero hand-copied lines)",
       reform_composite_scores(mm, REFORM_DIM_WEIGHTS,
                              REFORM_SUB_WEIGHTS)["error"] is None)
    mm_full = {
        "X": {"ret": {"sharpe_full_L": 2.0, "annualized_ret_L": 0.15,
                      "return_ceiling_O1126": 0.05, "beat6m_rate_L": 0.6,
                      "beat12m_rate_L": 0.55},
              "robust": {"cost_x2_sharpe_L": 1.4, "regime_min_sharpe_L": 0.5,
                         "bootstrap_ci_low_L": 0.3},
              "anti_overfit": {"family_pbo": 0.1, "d6_max_abs_corr": 0.2},
              "anti_luck": {"batch_dsr": 0.4}},
        "Y": {"ret": {"sharpe_full_L": 1.0, "annualized_ret_L": 0.08,
                      "return_ceiling_O1126": -0.02, "beat6m_rate_L": 0.5,
                      "beat12m_rate_L": 0.45},
              "robust": {"cost_x2_sharpe_L": 0.6, "regime_min_sharpe_L": -0.1,
                         "bootstrap_ci_low_L": 0.1},
              "anti_overfit": {"family_pbo": 0.5, "d6_max_abs_corr": 0.6},
              "anti_luck": {"batch_dsr": 0.2}},
    }
    g2f = g2_reform_fdr4d(mm_full, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                          {"X": 0.01, "Y": 0.5})
    ok("g2_reform_fdr4d: frozen-weights end-to-end (X dominates every dim, "
       "eligible; Y fails FDR)",
       g2f["members"]["X"]["eligible_reform"] is True
       and g2f["members"]["X"]["composite"] > g2f["members"]["Y"]["composite"]
       and not g2f["members"]["Y"]["eligible_reform"])

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
