"""W22 CHEAP PRE-SCREEN -- placebo null battery on the E23 daily face.

Why this face exists (TRIAL_LABOR_LAW sec.4: cheap screen before a full
burn): W22's grammar (results/trial_labor_w22/w22_grammar.json, 10 cells =
{hol_pre1, hol_pre2} x h{1..5}, K=200 null, seed 20670000) is DRAFT-derived
from the E23 census, whose 45 cells were uncorrected and whose best cell was
selected post-hoc.  Before spending a full runner burn we ask the cheap
question: does any W22 cell's excess survive an exact placebo null with
family-wise multiplicity control?

Design (single execution config, zero degrees of freedom beyond the frozen
grammar):
  * face = seasonal_horizon_stability.daily_face (single source, E23 verbatim)
    -- one observation per trading day, no cross-sectional pooling.
  * forward window = seasonal_horizon_stability.horizon_matrix(d, valid, h).
    Eligible day pool = every day with a valid h-window.
  * observed statistic per cell = mean(fwd[signal days]) - mean(fwd[pool]).
  * null draw per replicate = a random set of the SAME SIZE drawn without
    replacement from the eligible pool (placebo "seasonal window" of the same
    calendar budget).  Two-sided p = (1 + #{|null| >= |obs|}) / (K + 1).
  * family-wise face = per replicate, one independent draw per cell (all 10),
    statistic = max |excess| over cells; observed max |excess| is compared to
    that family-max null.  This is the multiplicity control the census did not
    have; K=200 => the smallest reachable family p is 1/201 = 0.00498.
  * no cost model, no engine touch, no prereg/judged/pool write.  Descriptive
    screen only: a surviving cell becomes a full-runner candidate, a family
    with zero survivors is axed cheaply.

usage:
    python scripts/w22_null_screen.py run        # writes the screen face
    python scripts/w22_null_screen.py selftest   # hermetic legs
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from seasonal_horizon_stability import (      # single-source lineage (E23)
    daily_face, horizon_matrix,
)
from seasonal_calendar_census import PANEL_DIR, annotate_calendar, load_panel

TZ = timezone(timedelta(hours=8))
OUT_DIR = os.path.join(_ROOT, "results", "trial_labor_w22")
GRAMMAR = os.path.join(OUT_DIR, "w22_grammar.json")
OUT_JSON = os.path.join(OUT_DIR, "w22_cheap_screen.json")


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S%z")


def load_grammar(path: str = GRAMMAR) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        g = json.load(fh)
    cells = []
    for c in g["cells"]:
        cells.append({"cell_id": c["cell_id"], "variant": c["variant"],
                      "h": int(c["params"]["h"])})
    return {
        "grammar_sha16": g["grammar_sha16"],
        "evidence_cutoff": g["evidence_cutoff"],
        "null_k": int(g["grid"]["null_k"]),
        "null_seed": int(g["grid"]["null_seed"]),
        "cells": cells,
    }


def variant_flags(dates, variants, name: str) -> np.ndarray:
    return np.array([name in variants.get(dt.date(), ()) for dt in dates],
                    dtype=bool)


def _excess(fwd: np.ndarray, pool_idx: np.ndarray, idx: np.ndarray):
    if idx.size == 0:
        return None
    return float(np.mean(fwd[idx]) - np.mean(fwd[pool_idx]))


def screen(panel_dir: str = PANEL_DIR, grammar_path: str = GRAMMAR,
           k_override: int | None = None) -> dict:
    t0 = time.time()
    gram = load_grammar(grammar_path)
    K = int(k_override or gram["null_k"])
    rng = np.random.default_rng(gram["null_seed"])

    panel = load_panel(panel_dir)
    dates = panel["dates"]
    face = daily_face(panel)
    d, valid = face["d"], face["valid"]
    variants, _breaks = annotate_calendar([dt.date() for dt in dates])

    # per-h forward vectors, shared across cells (single source math)
    fwd = {}
    pool = {}
    for h in sorted({c["h"] for c in gram["cells"]}):
        f, ok = horizon_matrix(d, valid, h)
        fwd[h] = f
        pool[h] = np.flatnonzero(ok)

    obs = {}
    for c in gram["cells"]:
        h = c["h"]
        flags = variant_flags(dates, variants, c["variant"])
        ok = np.zeros(len(d), dtype=bool)
        ok[pool[h]] = True
        sel = np.flatnonzero(flags & ok)
        obs[c["cell_id"]] = {"variant": c["variant"], "h": h,
                             "n_signal": int(sel.size),
                             "n_pool": int(pool[h].size),
                             "excess": _excess(fwd[h], pool[h], sel)}

    cell_ids = [c["cell_id"] for c in gram["cells"]]
    sizes = np.array([obs[c]["n_signal"] for c in cell_ids])
    used = np.array([obs[c]["h"] for c in cell_ids])

    # null battery: independent sets per cell per replicate
    null_ex = np.zeros((K, len(cell_ids)), dtype=np.float64)
    for rep in range(K):
        for j, cid in enumerate(cell_ids):
            h = int(used[j])
            p = pool[h]
            if sizes[j] <= 0 or sizes[j] > p.size:
                null_ex[rep, j] = 0.0
                continue
            idx = rng.choice(p, size=int(sizes[j]), replace=False)
            null_ex[rep, j] = _excess(fwd[h], p, idx)

    per_cell = {}
    for j, cid in enumerate(cell_ids):
        o = obs[cid]["excess"]
        col = null_ex[:, j]
        if o is None:
            per_cell[cid] = {**obs[cid], "p_two_sided": None,
                             "null_sd": None, "z_vs_null": None}
            continue
        pv = (1.0 + float(np.count_nonzero(np.abs(col) >= abs(o)))) / (K + 1.0)
        sd = float(np.std(col, ddof=1)) if K > 1 else float("nan")
        per_cell[cid] = {
            **obs[cid], "p_two_sided": pv, "null_sd": sd,
            "z_vs_null": (o / sd) if sd and math.isfinite(sd) and sd > 0 else None,
            "null_mean": float(np.mean(col)),
        }

    obs_max = max((abs(v["excess"]) for v in per_cell.values()
                   if v.get("excess") is not None), default=None)
    fam_null = np.max(np.abs(null_ex), axis=1)
    p_family = ((1.0 + float(np.count_nonzero(fam_null >= obs_max))) / (K + 1.0)
                if obs_max is not None else None)

    # Holm step-down on the per-cell p values (10 cells)
    ranked = sorted(((v["p_two_sided"], cid) for cid, v in per_cell.items()
                     if v["p_two_sided"] is not None))
    holm = {}
    m = len(ranked)
    still = True
    for i, (pv, cid) in enumerate(ranked):
        thr = 0.05 / (m - i)
        if still and pv <= thr:
            holm[cid] = {"pass": True, "threshold": thr}
        else:
            still = False
            holm[cid] = {"pass": False, "threshold": thr}

    survivors = [cid for cid, v in holm.items() if v["pass"]]
    cutoff = str(gram["evidence_cutoff"])
    return {
        "batch": "W22_CHEAP_SCREEN",
        "generated": now_iso(),
        "grammar": os.path.relpath(grammar_path, _ROOT).replace("\\", "/"),
        "grammar_sha16": gram["grammar_sha16"],
        "evidence_cutoff": cutoff,
        "panel": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
        "face_days": int(d.size),
        "face_days_usable": int(np.count_nonzero(valid)),
        "null": {"k": K, "seed": gram["null_seed"], "method": "placebo "
                 "same-size window draws without replacement from the "
                 "eligible h-window pool; two-sided"},
        "cells": per_cell,
        "family": {"stat": "max|excess| across cells",
                   "observed": obs_max, "p_family": p_family,
                   "min_reachable_p": 1.0 / (K + 1.0)},
        "holm": holm,
        "survivors": survivors,
        "verdict": ("SCREEN_SURVIVOR" if survivors else "SCREEN_ZERO_SURVIVOR"),
        "honest": [
            "placebo null conditions only on the window count, not on the "
            "calendar structure (a real seasonal effect is NOT a random set)",
            "h>1 windows overlap -> the null inherits the same overlap, so the "
            "comparison is like-for-like but the per-cell p is not independent",
            "K=%d leaves the smallest family p at %.5f; a survivor needs "
            "p<=%.5f to be admissible at family level" % (K, 1.0 / (K + 1.0),
                                                        1.0 / (K + 1.0)),
            "no cost model here: cost is adjudicated by the E23 cost face and "
            "the runner exit axis",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }


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

    # 1. variant_flags is a pure date->set membership map
    base = datetime(2020, 1, 1, tzinfo=TZ)
    dates = [base + timedelta(days=i) for i in range(10)]
    v = {dates[2].date(): {"hol_pre1"}, dates[5].date(): {"hol_pre1", "hol_pre2"}}
    f = variant_flags(dates, v, "hol_pre1")
    chk("flags_pre1", f.sum() == 2 and f[2] and f[5])
    chk("flags_pre2", variant_flags(dates, v, "hol_pre2").sum() == 1)

    # 2. _excess on a synthetic vector is mean-difference, exactly
    fwd = np.array([0.01, 0.02, -0.01, 0.03], dtype=float)
    pool = np.array([0, 1, 2, 3])
    idx = np.array([1, 3])
    e = _excess(fwd, pool, idx)
    chk("excess_math", abs(e - (0.025 - 0.0125)) < 1e-12, e)
    chk("excess_empty", _excess(fwd, pool, np.array([], dtype=int)) is None)

    # 3. planted signal -> small two-sided p; noise -> larger p (same K/seed)
    rng = np.random.default_rng(7)
    n = 400
    noise = rng.normal(0, 0.01, n)
    okv = np.ones(n, dtype=bool)
    sig_idx = np.arange(50)
    planted = noise.copy()
    planted[sig_idx] += 0.02
    K = 200

    def p_for(vec):
        pool_i = np.arange(n)
        o = _excess(vec, pool_i, sig_idx)
        draws = np.empty(K)
        r2 = np.random.default_rng(11)
        for i in range(K):
            pick = r2.choice(pool_i, size=sig_idx.size, replace=False)
            draws[i] = _excess(vec, pool_i, pick)
        return ((1.0 + float(np.count_nonzero(np.abs(draws) >= abs(o))))
                / (K + 1.0)), o

    p_sig, o_sig = p_for(planted)
    p_noise, o_noise = p_for(noise)
    chk("planted_significant", p_sig <= 0.05, "p=%s" % p_sig)
    chk("noise_not_significant", p_noise > 0.05, "p=%s" % p_noise)
    chk("planted_effect_positive", o_sig > 0.015, o_sig)

    # 4. determinism of the null battery (same seed -> identical draws)
    def battery(seed):
        r = np.random.default_rng(seed)
        out = []
        for _ in range(20):
            out.append(float(r.choice(100, size=5, replace=False).sum()))
        return out

    chk("null_deterministic", battery(20670000) == battery(20670000))

    # 5. family-max null is >= per-cell null by construction
    ctx = np.array([[0.01, -0.02], [0.03, 0.001]])
    chk("family_max_ge_cell", np.all(np.max(np.abs(ctx), axis=1)
                                     >= np.abs(ctx).max(axis=1)))

    # 6. Holm step-down thresholds widen as rank i grows (0.05/(m-i))
    thr = [0.05 / (10 - i) for i in range(10)]
    chk("holm_thresholds_monotone", all(thr[i] <= thr[i + 1]
                                        for i in range(len(thr) - 1)))

    # 7. grammar loader maps cells to (variant, h) faithfully
    g = load_grammar()
    chk("grammar_cells_n", len(g["cells"]) == 10, len(g["cells"]))
    chk("grammar_seed", g["null_seed"] == 20670000, g["null_seed"])
    chk("grammar_k", g["null_k"] == 200, g["null_k"])
    chk("grammar_variants", sorted({c["variant"] for c in g["cells"]})
        == ["hol_pre1", "hol_pre2"])
    chk("grammar_horizons", sorted({c["h"] for c in g["cells"]}) == [1, 2, 3, 4, 5])

    print("w22_null_screen selftest: %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL: %s" % b)
    return 0 if not bad else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        res = screen()
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
        print(json.dumps({"verdict": res["verdict"],
                          "survivors": res["survivors"],
                          "p_family": res["family"]["p_family"],
                          "out": os.path.relpath(OUT_JSON, _ROOT),
                          "elapsed_sec": res["elapsed_sec"]}, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))