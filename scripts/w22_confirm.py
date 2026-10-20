"""W22 CONFIRM-P1 -- forward-only confirmation tracker (pre-holiday family).

Why this face exists: the W22 cheap pre-screen (scripts/w22_null_screen.py,
results/trial_labor_w22/w22_cheap_screen.json) returned SCREEN_ZERO_SURVIVOR --
no cell cleared Holm, family p=0.0398 above the K=200 resolution floor.  The
digest's lawful continuation is a NARROWED, FRESH-WINDOW confirmation of
hol_pre1 with h in {3,4} (2 cells => Holm bar 0.025).  The narrowing is
post-hoc by construction, so it may only ever be judged on data the screen
never touched.

Fence: evidence_cutoff = 2026-10-19 (the screen's own cutoff).  Any signal day
with date <= the fence is excluded from confirmation evidence.  Zero forward
windows today => AWAITING_FORWARD_WINDOWS (honest, not a failure).

Frozen spec (mirrored verbatim in research/W22-CONFIRM-P1.md):
  * cells      = [("hol_pre1", 3), ("hol_pre1", 4)]
  * statistic  = mean(fwd[signal days]) - mean(fwd[forward pool]) per cell
  * null       = placebo same-size draw from the forward pool, two-sided,
                 K=1000, seed 20670500 (SEED_REGISTRY: w22_confirm_p1_nulls)
  * multiplicity = Holm step-down over the 2 cells, alpha 0.05
  * stopping   = judge only once every cell has >= 12 forward windows
  * exit axis  = strategy_own: exact-h-bar close, engine default exit stack
                 disabled (TRIAL_LABOR_LAW sec.4 option 2)
  * no cost model here (cost stays with the E23 cost face / runner exit axis)

usage:
    python scripts/w22_confirm.py status     # writes the tracker face
    python scripts/w22_confirm.py judge      # only when the stop rule is met
    python scripts/w22_confirm.py selftest   # hermetic legs
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from seasonal_horizon_stability import daily_face, horizon_matrix  # noqa: E402
from seasonal_calendar_census import PANEL_DIR, annotate_calendar, load_panel  # noqa: E402
import science_gates  # noqa: E402

TZ = timezone(timedelta(hours=8))
OUT_DIR = os.path.join(_ROOT, "results", "trial_labor_w22_confirm")
OUT_JSON = os.path.join(OUT_DIR, "w22_confirm_state.json")

CELLS = [("hol_pre1", 3), ("hol_pre1", 4)]
FENCE = date(2026, 10, 19)
FENCE_TS = "2026-10-19"
NULL_K = 1000
NULL_SEED = 20670500
HOLM_ALPHA = 0.05
MIN_FORWARD_WINDOWS = 12
EXIT_AXIS = "strategy_own: exact-h-bar close; engine default exit stack disabled"
SPEC_SHA_SOURCE = "cells=%s|fence=%s|k=%d|seed=%d|alpha=%.3f|min=%d" % (
    CELLS, FENCE_TS, NULL_K, NULL_SEED, HOLM_ALPHA, MIN_FORWARD_WINDOWS)


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S%z")


def spec_sha16() -> str:
    import hashlib
    return hashlib.sha256(SPEC_SHA_SOURCE.encode("utf-8")).hexdigest()[:16]


def _excess(fwd: np.ndarray, pool: np.ndarray, idx: np.ndarray):
    if idx.size == 0:
        return None
    return float(np.mean(fwd[idx]) - np.mean(fwd[pool]))


def forward_select(dates, d, valid, variants, variant: str, h: int,
                   fence: date = FENCE):
    """Split one (variant, h) cell into forward-pool and forward-signal sets.

    Fence is inclusive-exclusion: only days with date > fence qualify.  Both
    the signal set and the baseline pool are drawn from that forward region so
    the comparison never borrows the screen's data.
    """
    f, ok = horizon_matrix(d, valid, h)
    after = np.array([dt.date() > fence for dt in dates], dtype=bool)
    pool = np.flatnonzero(ok & after)
    flags = np.array([variant in variants.get(dt.date(), ()) for dt in dates],
                     dtype=bool)
    sig = np.flatnonzero(flags & ok & after)
    return f, pool, sig


def null_p(fwd: np.ndarray, pool: np.ndarray, sig: np.ndarray, k: int,
           seed: int):
    """Two-sided placebo p for one cell (forward face only)."""
    o = _excess(fwd, pool, sig)
    if o is None or sig.size == 0 or sig.size > pool.size:
        return None, None, None
    rng = np.random.default_rng(seed)
    draws = np.empty(k, dtype=np.float64)
    for i in range(k):
        pick = rng.choice(pool, size=int(sig.size), replace=False)
        draws[i] = _excess(fwd, pool, pick)
    p = (1.0 + float(np.count_nonzero(np.abs(draws) >= abs(o)))) / (k + 1.0)
    sd = float(np.std(draws, ddof=1)) if k > 1 else float("nan")
    z = (o / sd) if sd and math.isfinite(sd) and sd > 0 else None
    return p, z, float(np.mean(draws))


def holm(pvals: dict, alpha: float = HOLM_ALPHA) -> dict:
    ranked = sorted((v, cid) for cid, v in pvals.items() if v is not None)
    m = len(ranked)
    out = {}
    still = True
    for i, (pv, cid) in enumerate(ranked):
        thr = alpha / (m - i)
        out[cid] = {"p": pv, "threshold": thr, "pass": bool(still and pv <= thr)}
        if not (still and pv <= thr):
            still = False
    return out


def _load(panel_dir: str = PANEL_DIR):
    panel = load_panel(panel_dir)
    face = daily_face(panel)
    variants, _ = annotate_calendar([dt.date() for dt in panel["dates"]])
    return panel["dates"], face["d"], face["valid"], variants


def status(panel_dir: str = PANEL_DIR, write: bool = True) -> dict:
    t0 = time.time()
    dates, d, valid, variants = _load(panel_dir)
    cells = {}
    for variant, h in CELLS:
        f, pool, sig = forward_select(dates, d, valid, variants, variant, h)
        cid = "%s@h%d" % (variant, h)
        cells[cid] = {
            "variant": variant, "h": h,
            "forward_pool_days": int(pool.size),
            "forward_windows": int(sig.size),
            "first_forward_window": (min((dates[i].date() for i in sig),
                                         default=None) and
                                     str(min(dates[i].date() for i in sig))),
            "last_forward_window": (str(max(dates[i].date() for i in sig))
                                    if sig.size else None),
            "excess_to_date": _excess(f, pool, sig),
        }
    ready = all(c["forward_windows"] >= MIN_FORWARD_WINDOWS
                for c in cells.values())
    any_win = any(c["forward_windows"] > 0 for c in cells.values())
    verdict = ("READY_TO_JUDGE" if ready else
               ("ACCRUING" if any_win else "AWAITING_FORWARD_WINDOWS"))
    res = {
        "batch": "W22_CONFIRM_P1",
        "generated": now_iso(),
        "spec_sha16": spec_sha16(),
        "spec_source": SPEC_SHA_SOURCE,
        "fence": FENCE_TS,
        "exit_axis": EXIT_AXIS,
        "panel": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
        "panel_last_day": str(dates[-1].date()),
        "cells": cells,
        "min_forward_windows": MIN_FORWARD_WINDOWS,
        "null": {"k": NULL_K, "seed": NULL_SEED,
                 "method": "placebo same-size draw from the forward pool, "
                           "two-sided"},
        "holm_alpha": HOLM_ALPHA,
        "verdict": verdict,
        "honest": [
            "narrowing (hol_pre1, h in {3,4}) is POST-HOC (screen zero-survivor "
            "at p_family 0.0398); confirmation-only, never a discovery claim",
            "fence is inclusive-exclusion: every evidence day has date > %s"
            % FENCE_TS,
            "screen statistics are NOT carried forward: only forward windows "
            "count towards the stop rule",
            "no cost model in this face; cost is adjudicated by the E23 cost "
            "face and the runner exit axis",
            "a zero-window face is honest awaiting state, not a failure",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
    return res


def judge(panel_dir: str = PANEL_DIR) -> dict:
    res = status(panel_dir, write=True)
    if res["verdict"] != "READY_TO_JUDGE":
        print(json.dumps({"verdict": res["verdict"],
                          "reason": "stop rule not met: every cell needs >= %d "
                                    "forward windows" % MIN_FORWARD_WINDOWS,
                          "cells": {k: v["forward_windows"]
                                    for k, v in res["cells"].items()}}))
        return {"exit": 2, "face": res}
    dates, d, valid, variants = _load(panel_dir)
    pvals, detail = {}, {}
    for variant, h in CELLS:
        cid = "%s@h%d" % (variant, h)
        f, pool, sig = forward_select(dates, d, valid, variants, variant, h)
        p, z, nm = null_p(f, pool, sig, NULL_K, NULL_SEED + 100 * h)
        pvals[cid] = p
        detail[cid] = {"p_two_sided": p, "z_vs_null": z, "null_mean": nm,
                       "forward_windows": int(sig.size),
                       "excess": _excess(f, pool, sig)}
    hh = holm(pvals)
    survivors = [k for k, v in hh.items() if v["pass"]]
    res.update({"judged": now_iso(), "judge_cells": detail, "holm": hh,
                "survivors": survivors,
                "verdict": ("JUDGED_CONFIRMED" if survivors
                            else "JUDGED_NOT_CONFIRMED")})
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
    print(json.dumps({"verdict": res["verdict"], "survivors": survivors}))
    return {"exit": 0, "face": res}


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    ok = 0
    bad = []

    def chk(name, cond, extra=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, extra))

    # 1. fence is inclusive-exclusion on dates
    base = datetime(2026, 10, 15, tzinfo=TZ)
    dates = [base + timedelta(days=i) for i in range(10)]
    keep = np.array([dt.date() > FENCE for dt in dates])
    chk("fence_boundary", not keep[4] and keep[5], dates[4].date())

    # 2. forward_select returns only post-fence signal days
    d = np.arange(10, dtype=float) / 100.0
    valid = np.ones(10, dtype=bool)
    variants = {dt.date(): {"hol_pre1"} for dt in dates}
    f, pool, sig = forward_select(dates, d, valid, variants, "hol_pre1", 1)
    chk("forward_sig_post_fence", all(dates[i].date() > FENCE for i in sig),
        list(sig))
    chk("forward_pool_post_fence", all(dates[i].date() > FENCE for i in pool))
    chk("forward_sig_subset_pool", set(sig.tolist()) <= set(pool.tolist()))

    # 3. excess math identity
    fwd = np.array([0.01, 0.02, -0.01, 0.03])
    e = _excess(fwd, np.arange(4), np.array([1, 3]))
    chk("excess_math", abs(e - (0.025 - 0.0125)) < 1e-12, e)
    chk("excess_empty", _excess(fwd, np.arange(4), np.array([], dtype=int)) is None)

    # 4. planted forward effect -> small p; noise -> larger p (same seed/K)
    rng = np.random.default_rng(3)
    n, k = 400, 200
    pool_i = np.arange(n)
    sig_i = np.arange(60)
    noise = rng.normal(0, 0.01, n)
    planted = noise.copy()
    planted[sig_i] += 0.02
    p_sig, _, _ = null_p(planted, pool_i, sig_i, k, 11)
    p_noise, _, _ = null_p(noise, pool_i, sig_i, k, 11)
    chk("planted_significant", p_sig is not None and p_sig <= 0.05, p_sig)
    chk("noise_not_significant", p_noise is not None and p_noise > 0.05, p_noise)

    # 5. null draws are seed-deterministic
    a = null_p(planted, pool_i, sig_i, 50, 20670500)
    b = null_p(planted, pool_i, sig_i, 50, 20670500)
    chk("null_deterministic", a == b)

    # 6. zero-window cell -> None (never a fabricated p)
    p_none, _, _ = null_p(planted, pool_i, np.array([], dtype=int), k, 11)
    chk("empty_sig_none", p_none is None)

    # 7. Holm over 2 cells: thresholds 0.025 then 0.05
    hh = holm({"a": 0.01, "b": 0.03})
    chk("holm_thresholds", abs(hh["a"]["threshold"] - 0.025) < 1e-12
        and abs(hh["b"]["threshold"] - 0.05) < 1e-12)
    chk("holm_both_pass_at_own_threshold", hh["a"]["pass"] and hh["b"]["pass"])
    hh2 = holm({"a": 0.01, "b": 0.06})
    chk("holm_stopdown", hh2["a"]["pass"] and not hh2["b"]["pass"])

    # 8. seed registry carries this face
    chk("seed_registered",
        science_gates.SEED_REGISTRY.get("w22_confirm_p1_nulls") == NULL_SEED,
        science_gates.SEED_REGISTRY.get("w22_confirm_p1_nulls"))

    # 9. verdict machine: zero windows waits, short accrual accrues, full readies
    def verdict_of(nwin):
        cells = {"x": {"forward_windows": nwin}, "y": {"forward_windows": nwin}}
        ready = all(c["forward_windows"] >= MIN_FORWARD_WINDOWS
                    for c in cells.values())
        any_win = any(c["forward_windows"] > 0 for c in cells.values())
        return ("READY_TO_JUDGE" if ready else
                ("ACCRUING" if any_win else "AWAITING_FORWARD_WINDOWS"))
    chk("verdict_awaiting", verdict_of(0) == "AWAITING_FORWARD_WINDOWS")
    chk("verdict_accruing", verdict_of(5) == "ACCRUING")
    chk("verdict_ready", verdict_of(MIN_FORWARD_WINDOWS) == "READY_TO_JUDGE")

    # 10. frozen spec mirror is stable (sha16 recomputable, 16 hex chars)
    s16 = spec_sha16()
    chk("spec_sha16_shape", len(s16) == 16 and all(c in "0123456789abcdef" for c in s16))

    print("w22_confirm selftest: %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL: %s" % b)
    return 0 if not bad else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "status").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        res = status()
        print(json.dumps({"verdict": res["verdict"],
                          "fence": res["fence"],
                          "cells": {k: v["forward_windows"]
                                    for k, v in res["cells"].items()},
                          "out": os.path.relpath(OUT_JSON, _ROOT)},
                         ensure_ascii=False))
        return 0
    if cmd == "judge":
        return judge()["exit"]
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))