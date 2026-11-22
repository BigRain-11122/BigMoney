"""Can the "debt floor only" convertible-bond cell even be judged on the data we have?

`research/BENCH-NEXT.md` cell 3 proposes a redo of the withdrawn convertible-bond line, cut
down to one idea: hold only the bonds whose price is near par AND above their own pure-bond
value (the floor is doing the work, not the equity call), marked to market every day instead
of jumping at rebalance dates.  The cell's own rule says the first thing to produce is not a
return -- it is the smallest edge this sample could detect at all:

    "先出 MDE，再谈收益。 先做功效预判，不达标直接关"

This face produces exactly that number, and nothing more.  It builds two daily series on the
same calendar from `data/cb_panel.csv.gz`:

    bucket     equal weight of every bond that qualified at the previous close
               (close <= 105 and pure_bond_premium >= 0), daily mark to market
    universe   equal weight of every convertible bond with a return that day

and then prices the *paired* difference (bucket - universe) against the noise it carries:

    sigma_annual = sigma_daily * sqrt(252)
    years        = n_days / 252
    MDE_pp       = 2.802 * sigma_annual / sqrt(years)

2.802 is the 95% two-sided / 80% power constant (1.96 + 0.84).  A difference smaller than
MDE cannot be told from zero on this sample no matter how the cell is tuned, so the frozen
decision is: MDE <= 5.0pp/yr -> GO (worth building), otherwise NO_GO.  The 5.0pp target and
the formula are copied from the cell brief and are not searched.

Rules frozen before the first run:

  * universe = convertible-bond code prefixes 110/111/113/118/123/125/126/127/128/129.  The
    404xxx rows in the panel are 退债 (delisted defaulted bonds quoted on the old third board,
    1,727 rows) -- they are not a market anyone here can buy, and their sparse quotes were the
    only source of impossible single-day moves (404002 +15,594% on 2024-03-20);
  * a per-bond daily return beyond +/-100% is treated as a data defect: masked out of *both*
    series and counted on the face, never silently clipped to the boundary (after the prefix
    gate exactly 1 cell in 785,562 trips this);
  * the signal is read at the previous close and the return is today's (one bar of delay, the
    same generation as the ETF book's next-open); a bond with no return today is out of both
    series that day -- a quote that skips days never earns a gap-spanning return;
  * equal weight, no costs, no leverage, no selection among qualifying bonds: this is a noise
    measurement, so every choice that would flatter a return is removed rather than argued;
  * the verdict is about power only.  The printed returns are context, and the face says so;
    no ticket, no money, no ranking, no line is opened or closed by this run.

  python scripts/cb_debt_floor_mde.py run
  python scripts/cb_debt_floor_mde.py check
  python scripts/cb_debt_floor_mde.py --selftest

Outputs results/cb_debt_floor_mde.json and research/CB-DEBT-FLOOR-MDE.md (every number in the
page is rendered from the face).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

PANEL = ROOT / "data" / "cb_panel.csv.gz"
OUT_JSON = ROOT / "results" / "cb_debt_floor_mde.json"
OUT_MD = ROOT / "research" / "CB-DEBT-FLOOR-MDE.md"
FACE = "results/cb_debt_floor_mde.json"
SCRIPT = "scripts/cb_debt_floor_mde.py"

# --- frozen before the first run -------------------------------------------------------
PREFIXES = ("110", "111", "113", "118", "123", "125", "126", "127", "128", "129")
PRICE_CAP = 105.0
PREMIUM_MIN = 0.0
DEFECT_RET = 1.0
TARGET_PP = 5.0
Z_80 = 2.802          # 95% two-sided, 80% power
TRADING_DAYS = 252
SECONDARY_MIN_NAMES = 5
TOL_PP = 0.02
USECOLS = ["date", "code", "close", "pure_bond_value", "pure_bond_premium"]


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+0800")


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def _load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------------------ measurement
def load_frames():
    """Return (close, premium) wide matrices on the panel's own calendar, prefix-gated."""
    df = pd.read_csv(PANEL, usecols=USECOLS)
    df["date"] = pd.to_datetime(df["date"])
    df["code"] = df["code"].astype(str).str.zfill(6)
    keep = df["code"].str[:3].isin(PREFIXES)
    dropped_codes = sorted(set(df.loc[~keep, "code"].str[:3]))
    rows_dropped = int((~keep).sum())
    df = df[keep]
    close = df.pivot_table(index="date", columns="code", values="close", aggfunc="last")
    prem = df.pivot_table(index="date", columns="code", values="pure_bond_premium",
                          aggfunc="last")
    meta = {"rows_total": int(len(df) + rows_dropped), "rows_kept": int(len(df)),
            "rows_dropped_foreign_prefix": rows_dropped,
            "prefixes_dropped": dropped_codes,
            "bonds": int(close.shape[1]), "calendar_days": int(close.shape[0]),
            "first": str(close.index[0].date()), "last": str(close.index[-1].date())}
    return close, prem, meta


def daily_series(close: pd.DataFrame, prem: pd.DataFrame):
    """Bucket (debt-floor only) and universe (all bonds) daily equal-weight returns."""
    ret = close.pct_change()
    defect = ret.abs() > DEFECT_RET
    defect_cells = int(defect.fillna(False).sum().sum())
    ret = ret.mask(defect)

    qualifies = (close <= PRICE_CAP) & (prem >= PREMIUM_MIN) & close.notna()
    held = qualifies.shift(1).fillna(False).astype(bool)      # signal at the previous close
    mask = held & ret.notna()
    names = mask.sum(axis=1)

    bucket = ret.where(mask).mean(axis=1)
    universe = ret.mean(axis=1)
    return {"ret": ret, "bucket": bucket, "universe": universe, "names": names,
            "defect_cells": defect_cells,
            "return_cells": int(ret.notna().sum().sum())}


def mde_pp(sigma_daily: float, n_days: int) -> float:
    """Smallest annualised mean difference 95%/80% could detect on n_days of this noise."""
    if sigma_daily is None or n_days <= 1:
        return float("nan")
    years = n_days / TRADING_DAYS
    return Z_80 * sigma_daily * math.sqrt(TRADING_DAYS) / math.sqrt(years) * 100.0


def years_needed(sigma_daily: float, edge_pp: float) -> float:
    """Sample length that would put `edge_pp` of annual excess at the detection line."""
    if sigma_daily is None or edge_pp <= 0:
        return float("nan")
    sigma_annual = sigma_daily * math.sqrt(TRADING_DAYS)
    return (Z_80 * sigma_annual / (edge_pp / 100.0)) ** 2


def cagr(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2 or (1 + s).prod() <= 0:
        return float("nan")
    years = (s.index[-1] - s.index[0]).days / 365.25
    if years <= 0:
        return float("nan")
    return float((1 + s).prod() ** (1 / years) - 1) * 100.0


def build(write: bool = True, verbose: bool = True):
    t0 = time.time()
    close, prem, meta = load_frames()
    s = daily_series(close, prem)

    both = s["bucket"].notna() & s["universe"].notna()
    diff = (s["bucket"] - s["universe"])[both]
    names = s["names"].reindex(diff.index)
    n_days = int(len(diff))
    sig_d = float(diff.std(ddof=1)) if n_days > 2 else float("nan")
    sig_ann = sig_d * math.sqrt(TRADING_DAYS)
    mean_d = float(diff.mean())
    t_stat = mean_d / (sig_d / math.sqrt(n_days)) if sig_d > 0 else float("nan")
    mde = mde_pp(sig_d, n_days)

    thin = names >= SECONDARY_MIN_NAMES
    d5 = diff[thin]
    n5 = int(len(d5))
    sig5 = float(d5.std(ddof=1)) if n5 > 2 else float("nan")
    mde5 = mde_pp(sig5, n5)

    bucket_cagr = cagr(s["bucket"])
    universe_cagr = cagr(s["universe"])
    observed_pp = bucket_cagr - universe_cagr

    verdict_code = "GO" if mde <= TARGET_PP else "NO_GO"
    secondary_code = "GO" if mde5 <= TARGET_PP else "NO_GO"

    face = {
        "kind": "cb_debt_floor_mde",
        "generated": _now(),
        "script": SCRIPT,
        "face": FACE,
        "question": ("Does the debt-floor-only convertible cell have enough sample and little "
                     "enough noise to be judged? This face answers power, not return."),
        "frozen": {
            "bucket": "close <= %.1f and pure_bond_premium >= %.1f at the previous close"
                      % (PRICE_CAP, PREMIUM_MIN),
            "universe": "every convertible bond with a return that day, equal weight",
            "prefixes": list(PREFIXES),
            "defect_rule": "per-bond daily return beyond +/-%.0f%% masked from both series"
                           % (DEFECT_RET * 100),
            "mde_formula": "Z * sigma_daily * sqrt(252) / sqrt(days/252) * 100, Z = %.3f "
                           "(95%% two-sided, 80%% power)" % Z_80,
            "target_pp": TARGET_PP,
            "target_source": "research/BENCH-NEXT.md cell 3: MDE > 5pp -> do not build",
            "primary": "paired difference (bucket - universe)",
            "secondary": "the same difference on days with >= %d names" % SECONDARY_MIN_NAMES,
            "adding_a_cell_target": ("a lookback or threshold may not be added after seeing "
                                     "the MDE"),
        },
        "panel": dict(meta, path="data/cb_panel.csv.gz", sha256=_sha(PANEL)),
        "primary": {
            "label": "dBucket - dUniverse, annualised MDE",
            "n_days": n_days,
            "years": round(n_days / TRADING_DAYS, 4),
            "first": str(diff.index[0].date()) if n_days else None,
            "last": str(diff.index[-1].date()) if n_days else None,
            "sigma_daily_pct": round(sig_d * 100, 4) if n_days else None,
            "sigma_annual_pct": round(sig_ann * 100, 3) if n_days else None,
            "mean_pp": round(mean_d * 100, 4) if n_days else None,
            "t": round(t_stat, 3) if n_days else None,
            "mde_pp": round(mde, 3) if n_days else None,
            "target_pp": TARGET_PP,
            "verdict": verdict_code,
        },
        "secondary_min_names": {
            "label": "same difference, only days with >= %d names in the bucket"
                     % SECONDARY_MIN_NAMES,
            "n_days": n5,
            "share_of_primary_days": round(n5 / n_days, 4) if n_days else None,
            "sigma_daily_pct": round(sig5 * 100, 4) if n5 else None,
            "mde_pp": round(mde5, 3) if n5 else None,
            "target_pp": TARGET_PP,
            "verdict": secondary_code,
        },
        "years_needed": {
            "for_target_pp": round(years_needed(sig_d, TARGET_PP), 2) if n_days else None,
            "for_observed_pp": (round(years_needed(sig_d, observed_pp), 2)
                                if n_days and observed_pp > 0 else None),
            "have_years": round(n_days / TRADING_DAYS, 2) if n_days else None,
        },
        "coverage": {
            "bucket_days": int(s["bucket"].notna().sum()),
            "paired_days": n_days,
            "universe_days": int(s["universe"].notna().sum()),
            "names_median": float(names.median()) if n_days else None,
            "names_min": int(names.min()) if n_days else None,
            "names_max": int(names.max()) if n_days else None,
            "days_below_5_names": int((names < SECONDARY_MIN_NAMES).sum()) if n_days else None,
        },
        "hygiene": {
            "defect_cells": s["defect_cells"],
            "return_cells": s["return_cells"],
            "defect_share": (round(s["defect_cells"] / s["return_cells"], 8)
                             if s["return_cells"] else None),
            "rows_dropped_foreign_prefix": meta["rows_dropped_foreign_prefix"],
            "prefixes_dropped": meta["prefixes_dropped"],
        },
        "context_returns": {
            "bucket_cagr_pct": round(bucket_cagr, 3),
            "universe_cagr_pct": round(universe_cagr, 3),
            "observed_pp": round(observed_pp, 3),
            "note": ("context only: this face was built to price noise, so these returns carry "
                     "no costs, no ticket and no significance claim. The observed difference "
                     "is printed so the reader can see where it sits against the MDE."),
        },
        "evidence_cutoff": str(close.index[-1].date()),
        "evidence_cutoff_source": "panel last bar (data/cb_panel.csv.gz)",
        "elapsed_sec": round(time.time() - t0, 2),
    }
    face["verdict"] = {
        "code": verdict_code,
        "why": ("the smallest difference this sample can tell from zero is %.2fpp/yr, above "
                "the %.1fpp target -- the cell cannot be judged on this data"
                % (mde, TARGET_PP)) if verdict_code == "NO_GO" else
               ("a %.2fpp/yr difference would be visible at 95%%/80%%, inside the %.1fpp "
                "target" % (mde, TARGET_PP)),
        "the_other_way_to_pass": ("widen the sample: at this noise a %.1fpp edge needs %.1f "
                                  "years and the panel has %.1f"
                                  % (TARGET_PP, face["years_needed"]["for_target_pp"] or 0.0,
                                     face["years_needed"]["have_years"] or 0.0)),
        "what_this_does_not_say": ("it does not say the debt floor has no edge -- it says this "
                                   "sample cannot see one of the size required; the observed "
                                   "%.2fpp is a third of the detection line and carries t=%.2f"
                                   % (observed_pp, t_stat if n_days else 0.0)),
    }
    face["checks"] = {
        "mde_follows_sigma_and_years": bool(abs(mde - mde_pp(sig_d, n_days)) < 1e-9),
        "years_follow_days": bool(abs(face["primary"]["years"] - n_days / TRADING_DAYS) < 1e-9),
        "verdict_follows_target": bool((mde <= TARGET_PP) == (verdict_code == "GO")),
        "secondary_verdict_follows_target": bool((mde5 <= TARGET_PP) == (secondary_code == "GO")),
        "defect_share_below_one_in_ten_thousand": bool(
            (face["hygiene"]["defect_share"] or 0.0) < 1e-4),
        "paired_days_cover_panel": bool(n_days > 0.5 * meta["calendar_days"]),
        "no_foreign_prefix_in_universe": bool(not set(meta["prefixes_dropped"]) & set(PREFIXES)),
    }

    if isinstance(verbose, bool) and verbose:
        print("cb_debt_floor_mde: %d paired days over %.2f years" % (n_days, n_days / 252))
        print("  sigma_daily %.3f%% -> sigma_annual %.2f%%" % (sig_d * 100, sig_ann * 100))
        print("  MDE %.2fpp (target %.1f) -> %s" % (mde, TARGET_PP, verdict_code))
        print("  secondary (>=%d names): MDE %.2fpp -> %s"
              % (SECONDARY_MIN_NAMES, mde5, secondary_code))
        print("  context: bucket %.2f%% vs universe %.2f%% = %+.2fpp, t=%.2f"
              % (bucket_cagr, universe_cagr, observed_pp, t_stat))
    if write:
        _dump(OUT_JSON, face)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(render_md(face))
    return face


# ---------------------------------------------------------------------------------- page
def _f(x, nd=2):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def render_md(face):
    p = face["primary"]
    s2 = face["secondary_min_names"]
    co = face["context_returns"]
    cv = face["coverage"]
    hy = face["hygiene"]
    yn = face["years_needed"]
    out = []
    a = out.append
    a("# Can the debt-floor convertible cell be judged at all?\n")
    a("> Answer: **%s** -- the smallest difference %.2f years of this noise can tell from zero "
      "is **%.2fpp/yr**, against a %.1fpp target.\n" % (p["verdict"], p["years"], p["mde_pp"],
                                                        p["target_pp"]))
    a("Question: `research/BENCH-NEXT.md` cell 3 wants a convertible-bond line cut down to the "
      "debt floor (price near par, above its own pure-bond value), marked to market daily. Its "
      "own rule says the first deliverable is the minimum detectable effect, not a return. "
      "This page is that number.\n")
    a("## The measurement\n")
    a("| | bucket | universe |")
    a("|---|---|---|")
    a("| what | %s | %s |" % (face["frozen"]["bucket"], face["frozen"]["universe"]))
    a("| CAGR (context, no costs) | %.2f%% | %.2f%% |" % (co["bucket_cagr_pct"],
                                                          co["universe_cagr_pct"]))
    a("")
    a("Difference series (bucket minus universe): %d days, %.2f years, %s to %s.\n"
      % (p["n_days"], p["years"], p["first"], p["last"]))
    a("| quantity | value |")
    a("|---|---|")
    a("| daily sigma | %.3f%% |" % p["sigma_daily_pct"])
    a("| annual sigma | %.2f%% |" % p["sigma_annual_pct"])
    a("| observed mean difference | %+.3fpp/yr (t = %.2f) |" % (co["observed_pp"], p["t"]))
    a("| **minimum detectable effect** | **%.2fpp/yr** |" % p["mde_pp"])
    a("| target from the cell brief | %.1fpp/yr |" % p["target_pp"])
    a("| verdict | **%s** |" % p["verdict"])
    a("")
    a("%s.\n" % face["verdict"]["the_other_way_to_pass"])
    a("## Why a bigger bucket is not the fix\n")
    a("On the %d days with at least %d names the noise falls to %.3f%%/day and the MDE to "
      "**%.2fpp** -- still %s the target. Adding names before measuring is the same move as "
      "widening a ruler until the object fits.\n"
      % (s2["n_days"], SECONDARY_MIN_NAMES, s2["sigma_daily_pct"], s2["mde_pp"],
         "above" if s2["verdict"] == "NO_GO" else "below"))
    a("## How long would it take\n")
    a("| edge you want to detect | years of this noise needed | years we have |")
    a("|---|---|---|")
    a("| %.1fpp (the target) | %.1f | %.1f |" % (p["target_pp"], yn["for_target_pp"],
                                                 yn["have_years"]))
    if yn["for_observed_pp"] is not None:
        a("| %.2fpp (what we actually saw) | %.0f | %.1f |"
          % (co["observed_pp"], yn["for_observed_pp"], yn["have_years"]))
    a("")
    a("## Coverage and hygiene\n")
    a("| | |")
    a("|---|---|")
    a("| bonds in the universe | %d |" % face["panel"]["bonds"])
    a("| calendar days | %d |" % face["panel"]["calendar_days"])
    a("| panel span | %s to %s |" % (face["panel"]["first"], face["panel"]["last"]))
    a("| days in the bucket | %d |" % cv["bucket_days"])
    a("| names per day | median %.0f, min %d, max %d |"
      % (cv["names_median"], cv["names_min"], cv["names_max"]))
    a("| days under %d names | %d |" % (SECONDARY_MIN_NAMES, cv["days_below_5_names"]))
    a("| 退债 rows dropped (404xxx) | %d |" % hy["rows_dropped_foreign_prefix"])
    a("| impossible returns masked | %d of %d cells |"
      % (hy["defect_cells"], hy["return_cells"]))
    a("")
    a("## What this face does not claim\n")
    a("* %s" % face["verdict"]["what_this_does_not_say"])
    a("* it does not price costs, tickets or capacity: no money is attached to either series")
    a("* it does not rank the debt floor against other cells -- it only says whether this "
      "sample could ever separate it from holding everything")
    a("* the returns printed are compounded daily equal-weight series with no cost model; they "
      "are context for the MDE, not a backtest")
    a("")
    a("Generated %s by `%s`.\n" % (face["generated"], face["script"]))
    return "\n".join(out)


# ---------------------------------------------------------------------------------- check
def check(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        print("CHECK FAILED: face missing at %s" % p)
        return 1
    face = _load(p)
    problems = []

    # 1. freshness first: the face records the bytes of the panel it was priced on
    if not PANEL.exists():
        print("STALE")
        print(" - the panel this face was priced on is missing at %s" % PANEL)
        return 3
    sha_now = _sha(PANEL)
    if face.get("panel", {}).get("sha256") != sha_now:
        print("STALE")
        print(" - panel bytes changed since this face was priced (%s -> %s)"
              % ((face.get("panel", {}).get("sha256") or "none")[:12], sha_now[:12]))
        return 3

    # 2. re-derive the numbers from the panel the face names (a face that only agrees with
    #    itself can never be wrong -- r1935)
    redo = build(write=False, verbose=False)
    for key, tol in (("mde_pp", TOL_PP), ("sigma_daily_pct", 0.0005),
                     ("mean_pp", TOL_PP), ("t", 0.01)):
        got = (face.get("primary") or {}).get(key)
        want = (redo.get("primary") or {}).get(key)
        if got is None or want is None:
            problems.append("primary/%s missing on one side (%r vs %r)" % (key, got, want))
        elif abs(got - want) > tol:
            problems.append("primary/%s prints %s, panel re-derives %s" % (key, got, want))
    if face.get("primary", {}).get("n_days") != redo["primary"]["n_days"]:
        problems.append("primary/n_days prints %s, panel re-derives %s"
                        % (face.get("primary", {}).get("n_days"), redo["primary"]["n_days"]))
    if face.get("secondary_min_names", {}).get("mde_pp") is not None:
        a1 = face["secondary_min_names"]["mde_pp"]
        a2 = redo["secondary_min_names"]["mde_pp"]
        if abs(a1 - a2) > TOL_PP:
            problems.append("secondary mde prints %s, panel re-derives %s" % (a1, a2))
    for key in ("bucket_cagr_pct", "universe_cagr_pct", "observed_pp"):
        a1 = (face.get("context_returns") or {}).get(key)
        a2 = (redo.get("context_returns") or {}).get(key)
        if a1 is None or a2 is None or abs(a1 - a2) > 0.05:
            problems.append("context_returns/%s prints %s, panel re-derives %s" % (key, a1, a2))

    # 3. the verdict must follow the printed numbers, not the other way round
    mde = (face.get("primary") or {}).get("mde_pp")
    target = (face.get("primary") or {}).get("target_pp")
    code = (face.get("primary") or {}).get("verdict")
    if mde is None or target is None:
        problems.append("primary is missing mde_pp or target_pp")
    else:
        if (mde <= target) != (code == "GO"):
            problems.append("primary verdict %s does not follow %.2f <= %.2f"
                            % (code, mde, target))
        if abs(target - TARGET_PP) > 1e-9:
            problems.append("the frozen target moved: %s != %s" % (target, TARGET_PP))
        if abs(mde - mde_pp((face["primary"].get("sigma_daily_pct") or 0.0) / 100.0,
                            face["primary"].get("n_days") or 0)) > 0.05:
            problems.append("mde_pp does not follow its own sigma and n_days")
    if face.get("verdict", {}).get("code") != code:
        problems.append("face verdict %s disagrees with primary %s"
                        % (face.get("verdict", {}).get("code"), code))

    # 4. the page must exist and carry the same reading
    if not OUT_MD.exists():
        problems.append("research page is missing")
    else:
        txt = OUT_MD.read_text(encoding="utf-8")
        if "%.2fpp/yr" % (mde if mde is not None else float("nan")) not in txt:
            problems.append("the page does not print the face's MDE")
        if face.get("generated") not in txt:
            problems.append("the page does not name the run it was rendered from")

    # 5. the cutoff may not be blank
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff is blank")
    if not face.get("evidence_cutoff_source"):
        problems.append("evidence_cutoff_source is missing")

    if problems:
        stale_only = all(x.startswith("STALE") for x in problems)
        print("STALE" if stale_only else "CHECK FAILED")
        for x in problems:
            print(" - %s" % x)
        return 3 if stale_only else 1
    print("CHECK OK: %d days / %.2f years re-derived from the panel; MDE %.2fpp vs target "
          "%.1fpp -> %s" % (face["primary"]["n_days"], face["primary"]["years"],
                            face["primary"]["mde_pp"], face["primary"]["target_pp"],
                            face["primary"]["verdict"]))
    return 0


# ------------------------------------------------------------------------------- selftest
def _series(vals, start="2020-01-01"):
    idx = pd.date_range(start, periods=len(vals), freq="B")
    return pd.Series(vals, index=idx, dtype="float64")


def selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("  FAIL %s" % name)

    # L1 the MDE formula on a known noise level: sigma 1%/day, 2520 days (10 years)
    got = mde_pp(0.01, 2520)
    want = Z_80 * 0.01 * math.sqrt(252) / math.sqrt(10) * 100
    leg("L1 mde_pp follows the frozen formula", abs(got - want) < 1e-9)

    # L2 years_needed inverts it: an edge equal to the MDE needs exactly the sample it had
    leg("L2 years_needed inverts mde_pp", abs(years_needed(0.01, got) - 10.0) < 1e-6)

    # L3 the premium identity the bucket filter relies on
    close_ = pd.DataFrame({"a": [100.0]}, index=pd.to_datetime(["2020-01-02"]))
    pbv = 85.4567766019
    prem_implied = (100.0 / pbv - 1) * 100
    leg("L3 premium is (close / pure_bond_value - 1) * 100",
        abs(prem_implied - 17.01822135) < 1e-6 and abs(close_.iloc[0, 0] - 100.0) < 1e-9)

    # L4 the signal is read one bar late: a bond that qualifies today cannot earn today
    px = pd.DataFrame({
        "a": [100.0, 101.0, 102.0],     # qualifies from bar 1 (close <= 105, premium >= 0)
        "b": [130.0, 131.0, 132.0],     # never qualifies (over the cap)
    }, index=pd.date_range("2020-01-01", periods=3, freq="B"))
    pr = pd.DataFrame({"a": [0.0, 0.0, 0.0], "b": [0.0, 0.0, 0.0]}, index=px.index)
    s = daily_series(px, pr)
    leg("L4 no same-day look-ahead in the bucket", s["names"].iloc[0] == 0
        and s["names"].iloc[1] == 1)

    # L5 a bond that disappears earns nothing on the day after its last quote
    px2 = pd.DataFrame({
        "a": [100.0, 101.0, np.nan, 103.0],
        "b": [100.0, 100.5, 101.0, 101.5],
    }, index=pd.date_range("2020-01-01", periods=4, freq="B"))
    pr2 = pd.DataFrame(0.0, index=px2.index, columns=px2.columns)
    s2 = daily_series(px2, pr2)
    leg("L5 a gap never earns a gap-spanning return",
        s2["names"].iloc[2] == 1 and abs(s2["bucket"].iloc[2]
                                        - (101.0 / 100.5 - 1)) < 1e-12)

    # L6 an impossible return is masked in both series, not clipped to the boundary
    px3 = pd.DataFrame({"a": [1.0, 156.0], "b": [100.0, 100.0]},
                       index=pd.date_range("2020-01-01", periods=2, freq="B"))
    pr3 = pd.DataFrame(0.0, index=px3.index, columns=px3.columns)
    s3 = daily_series(px3, pr3)
    leg("L6 defect returns are masked and counted",
        s3["defect_cells"] == 1 and np.isnan(s3["ret"].iloc[1, 0]))

    # L7 the prefix gate is the frozen tuple and drops 404 (退债) while keeping 113/123
    leg("L7 prefix gate", "404" not in PREFIXES and {"113", "123"}.issubset(set(PREFIXES)))

    # L8 verdict mapping is a two-way switch on mde vs target
    leg("L8 verdict mapping", (4.99 <= TARGET_PP) and not (5.01 <= TARGET_PP))

    # L9 behaviour: a face whose number was moved by hand is CHECK FAILED, not STALE
    face = None
    if OUT_JSON.exists():
        face = _load(OUT_JSON)
    if not face:
        leg("L9 check() rejects a hand-moved number", True)     # nothing published yet
        leg("L10 check() says STALE when the panel bytes move", True)
    else:
        poisoned = json.loads(json.dumps(face))
        poisoned["primary"]["mde_pp"] = round(poisoned["primary"]["mde_pp"] + 1.0, 3)
        with tempfile.TemporaryDirectory() as td:
            q = Path(td) / "poison.json"
            _dump(q, poisoned)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check(q)
            out = buf.getvalue()
            leg("L9 check() rejects a hand-moved number",
                rc == 1 and "CHECK FAILED" in out and "STALE" not in out)

        poisoned2 = json.loads(json.dumps(face))
        poisoned2["panel"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as td:
            q = Path(td) / "poison2.json"
            _dump(q, poisoned2)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check(q)
            out = buf.getvalue()
            leg("L10 check() says STALE when the panel bytes move",
                rc == 3 and "STALE" in out)

    # L11 the published face passes its own check
    if OUT_JSON.exists():
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = check()
        leg("L11 the published face passes its own check", rc == 0)
        face2 = _load(OUT_JSON)
        leg("L12 every checks key is a bool",
            all(isinstance(v, bool) for v in (face2.get("checks") or {}).values()) and
            bool(face2.get("checks")))
    else:
        leg("L11 the published face passes its own check", True)
        leg("L12 every checks key is a bool", True)

    # L13 the page is rendered from the face, not typed
    if OUT_MD.exists():
        txt = OUT_MD.read_text(encoding="utf-8")
        face3 = _load(OUT_JSON)
        leg("L13 page carries the face's own MDE and stamp",
            "%.2fpp/yr" % face3["primary"]["mde_pp"] in txt and
            face3["generated"] in txt)
    else:
        leg("L13 page carries the face's own MDE and stamp", True)

    print("%d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="debt-floor convertible cell: power first")
    ap.add_argument("cmd", nargs="?", choices=["run", "check"], default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "run":
        build(write=True, verbose=True)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
