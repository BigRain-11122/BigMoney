"""ETF book -- the sign question was answered at ONE cadence and ONE width.

E207/E218 priced the six factor directions: they are the full-sample IC signs, and repriced
point-in-time the headline goes from +6.14%/yr to -10.81%/yr. E219 then ran the whole 2^6
space and put the production arm at rank 6/64, the median arm at -1.63%/yr, and the value of
the hindsight at 7.77pp/yr.

Every one of those numbers came from a single cell of the configuration grid:

    REBAL = 20, N_HOLD = 12

But 20 and 12 are not physical constants. The published walk-forward on this line selects
among N3/5/8 x R10/20/40 -- i.e. cadence and width were themselves picked on the sample. If
the sign ORDERING (which factors pay, and by how much) is a property of that cell rather than
of the factors, then the sign disclosure prices the cheapest of several hindsight choices and
the expensive one is still unpriced. That is the question this face asks:

    does the sign ordering survive the cell it was measured at?

Design: three cells, declared before the first run, all 64 arms in each -- the same panel,
the same eligibility, the same engine, the same costs, only (rebal, n_hold) differ.

    CELLS = (R20_N12 primary, R10_N8, R40_N5)

Per cell: production arm rank, median arm, spread, and each factor's main effect (the full
factorial makes that a difference of half-means, see E219). Across cells: for each factor,
does its main-effect SIGN agree everywhere?

Verdict rule (frozen before the first run, recomputed by the gate from the per-cell tables):
    fewer than 2 cells traded all 64 arms / spread < DEGENERATE_SPREAD
                                    -> not_assessable_cells_inactive
    all six factors agree in sign in every active cell
                                    -> sign_order_stable_across_cells
    at least 4 of 6 agree           -> sign_order_partly_stable
    otherwise                       -> sign_order_cell_dependent

  python scripts/etf_sign_cells.py run        # 3 cells x 64 arms -> results/etf_sign_cells.json
  python scripts/etf_sign_cells.py --check    # re-derive the verdict from the payload
  python scripts/etf_sign_cells.py --selftest # offline invariants, zero network
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

import etf_composite_pf as F  # noqa: E402
import etf_sign_enum as E  # noqa: E402
import etf_sign_pit as P  # noqa: E402
import etf_variants_null_rolling as V  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_sign_cells.json"

FACTOR_KEYS = list(E.FACTOR_KEYS)
SIGNS = dict(E.SIGNS)
COST = E.COST
START = E.START
MIN_TRADED_BARS = E.MIN_TRADED_BARS
TOP_DECILE = E.TOP_DECILE
DEGENERATE_SPREAD = E.DEGENERATE_SPREAD
STABLE_MIN_AGREE = 4  # of 6 factors, for the "partly" branch

CELLS = (
    ("R20_N12", 20, 12),
    ("R10_N8", 10, 8),
    ("R40_N5", 40, 5),
)
DECLARED = {
    "cells": [{"tag": t, "rebal": r, "n_hold": n} for t, r, n in CELLS],
    "cost_per_side": COST,
    "start": START,
    "min_traded_bars": MIN_TRADED_BARS,
    "top_decile": TOP_DECILE,
    "degenerate_spread": DEGENERATE_SPREAD,
    "stable_min_agree": STABLE_MIN_AGREE,
    "n_arms_per_cell": 2 ** len(FACTOR_KEYS),
    "signs": SIGNS,
    "primary_cell": CELLS[0][0],
}


# --- cell arithmetic -----------------------------------------------------------------
def arm_key(signs: dict) -> str:
    return "|".join("%s%s" % (k, "+" if signs[k] > 0 else "-") for k in FACTOR_KEYS)


def run_cell(zs: dict, close: pd.DataFrame, openp: pd.DataFrame, elig: pd.DataFrame,
             rebal: int, n_hold: int) -> dict:
    """All 2^6 sign sets at one (rebal, n_hold) cell. Same arithmetic as E.run()."""
    arms = {}
    for v in E.sign_vectors(FACTOR_KEYS):
        sc = E.score_from(zs, v, close, elig)
        ser, turn, _gap = V.fast_next_open(sc, close, openp, rebal, n_hold=n_hold,
                                           cost=COST, start=START)
        a = E.agg(ser)
        a["turnover_per_rebal"] = round(float(turn), 4)
        a["traded"] = bool(float(turn) > 0.0 and len(ser) >= MIN_TRADED_BARS)
        a["signs"] = v
        arms[arm_key(v)] = a
    return arms


def cell_facts(arms: dict, prod_key: str) -> dict:
    """Where the production arm sits at this cell, plus each factor's main effect."""
    cagrs = sorted(a["cagr"] for a in arms.values() if isinstance(a.get("cagr"), (int, float)))
    traded = sum(1 for a in arms.values() if a.get("traded"))
    prod = arms.get(prod_key) or {}
    prod_cagr = prod.get("cagr") if isinstance(prod.get("cagr"), (int, float)) else None
    rank = (1 + sum(1 for c in cagrs if c > prod_cagr)) if prod_cagr is not None else None
    n = len(cagrs)
    spread = (cagrs[-1] - cagrs[0]) if n else 0.0
    effects = E.main_effects(arms)
    active = bool(traded == len(arms) and n == len(arms) and spread >= DEGENERATE_SPREAD)
    return {
        "n_arms": len(arms),
        "n_traded": traded,
        "n_with_cagr": n,
        "production_rank": rank,
        "production_cagr": prod_cagr,
        "production_percentile": (round(1.0 - (rank - 1) / max(1, n - 1), 4) if rank else None),
        "top_decile_cut": int(np.ceil(TOP_DECILE * n)) if n else None,
        "production_in_top_decile": (bool(rank is not None and n and rank <= int(np.ceil(TOP_DECILE * n)))),
        "median_cagr": float(np.median(cagrs)) if cagrs else None,
        "best_cagr": cagrs[-1] if cagrs else None,
        "worst_cagr": cagrs[0] if cagrs else None,
        "spread_cagr": round(float(spread), 6),
        "main_effect_pp": {k: (v.get("pp_per_year") if v.get("pp_per_year") is not None else None)
                           for k, v in effects.items()},
        "active": active,
    }


def cross_cell(cells: dict) -> dict:
    """Per-factor: does the main-effect sign agree in every ACTIVE cell?"""
    active_tags = [t for t, c in cells.items() if c.get("active")]
    per_factor = {}
    for k in FACTOR_KEYS:
        signs = []
        for t in active_tags:
            pp = (cells[t].get("main_effect_pp") or {}).get(k)
            signs.append(0 if pp is None or abs(pp) < 1e-12 else (1 if pp > 0 else -1))
        nonzero = [s for s in signs if s != 0]
        agree = bool(nonzero) and all(s == nonzero[0] for s in nonzero) and len(nonzero) == len(signs)
        per_factor[k] = {
            "pp_by_cell": {t: (cells[t].get("main_effect_pp") or {}).get(k) for t in active_tags},
            "sign_by_cell": dict(zip(active_tags, signs)),
            "sign_stable": agree,
        }
    n_stable = sum(1 for v in per_factor.values() if v["sign_stable"])
    return {"active_cells": active_tags, "per_factor": per_factor,
            "n_factors_stable": n_stable, "n_factors": len(FACTOR_KEYS)}


def gate(payload: dict) -> dict:
    """Re-derive everything from the payload tables; never trust a typed verdict."""
    checks = []
    declared = payload.get("declared") or {}
    for key in ("cells", "cost_per_side", "start", "min_traded_bars", "top_decile",
                "degenerate_spread", "stable_min_agree", "n_arms_per_cell"):
        checks.append({"check": "declared %s echoed" % key,
                       "ok": key in declared, "payload": declared.get(key),
                       "module": DECLARED.get(key)})
    for k, v in DECLARED.items():
        if k == "cells":
            continue
        checks.append({"check": "declared %s matches module" % k,
                       "ok": declared.get(k) == v, "payload": declared.get(k), "module": v})
    cell_decl = {}
    for c in declared.get("cells") or []:
        cell_decl[c.get("tag")] = (c.get("rebal"), c.get("n_hold"))
    checks.append({"check": "declared cells equal the module's frozen cells",
                   "ok": cell_decl == {t: (r, n) for t, r, n in CELLS},
                   "payload": sorted(cell_decl), "module": [t for t, _, _ in CELLS]})

    cells = payload.get("cells") or {}
    n_expected = 2 ** len(FACTOR_KEYS)
    checks.append({"check": "every cell carries all arms",
                   "ok": bool(cells) and all(c.get("n_arms") == n_expected for c in cells.values()),
                   "n_expected": n_expected,
                   "got": {t: c.get("n_arms") for t, c in cells.items()}})

    # rank recomputed from each cell's own arm table
    rank_ok = True
    recomputed = {}
    for tag, c in cells.items():
        arms = c.get("arms") or {}
        cagrs = sorted(a["cagr"] for a in arms.values() if isinstance(a.get("cagr"), (int, float)))
        prod = arms.get(payload.get("production_key") or "")
        pc = prod.get("cagr") if prod and isinstance(prod.get("cagr"), (int, float)) else None
        r = (1 + sum(1 for x in cagrs if x > pc)) if pc is not None else None
        recomputed[tag] = r
        if r != c.get("production_rank"):
            rank_ok = False
    checks.append({"check": "production rank recomputed from each cell's arm table",
                   "ok": rank_ok, "recomputed": recomputed,
                   "payload": {t: c.get("production_rank") for t, c in cells.items()}})

    # active flags are recomputed from each cell's own trade census, not taken on trust
    active_ok = True
    recomputed_active = {}
    for tag, c in cells.items():
        arms = c.get("arms") or {}
        traded = sum(1 for a in arms.values() if a.get("traded"))
        cagrs = [a["cagr"] for a in arms.values() if isinstance(a.get("cagr"), (int, float))]
        spread = (max(cagrs) - min(cagrs)) if len(cagrs) > 1 else 0.0
        act = bool(len(arms) == n_expected and traded == n_expected
                   and len(cagrs) == n_expected and spread >= DEGENERATE_SPREAD)
        recomputed_active[tag] = act
        if act != c.get("active"):
            active_ok = False
    checks.append({"check": "per-cell active flag recomputed from the arm census",
                   "ok": active_ok, "recomputed": recomputed_active,
                   "payload": {t: c.get("active") for t, c in cells.items()}})
    cells = {t: {**c, "active": recomputed_active[t]} for t, c in cells.items()}

    cc = cross_cell(cells)
    checks.append({"check": "stable-factor count recomputed from the per-cell effects",
                   "ok": cc["n_factors_stable"] == (payload.get("cross_cell") or {}).get("n_factors_stable"),
                   "recomputed": cc["n_factors_stable"],
                   "payload": (payload.get("cross_cell") or {}).get("n_factors_stable")})

    active = cc["active_cells"]
    if len(active) < 2:
        verdict = "not_assessable_cells_inactive"
    elif cc["n_factors_stable"] == cc["n_factors"]:
        verdict = "sign_order_stable_across_cells"
    elif cc["n_factors_stable"] >= STABLE_MIN_AGREE:
        verdict = "sign_order_partly_stable"
    else:
        verdict = "sign_order_cell_dependent"
    checks.append({"check": "verdict recomputed from the stable-factor count",
                   "ok": True, "verdict": verdict, "active_cells": active,
                   "n_stable": cc["n_factors_stable"]})
    return {"verdict": verdict, "checks": checks, "all_ok": all(c["ok"] for c in checks),
            "cross_cell": cc, "active_cells": active}


# --- run ------------------------------------------------------------------------------
def run() -> dict:
    t0 = time.time()
    close, openp, amt, feats = P.load_panel()
    elig = P.eligibility(close, amt)
    zs = E.z_mats(close, feats)
    prod_key = arm_key(SIGNS)
    print("panel %d bars x %d symbols in %.1fs" % (len(close.index), close.shape[1],
                                                   time.time() - t0), flush=True)
    cells, rows = {}, []
    for tag, rebal, n_hold in CELLS:
        tc = time.time()
        arms = run_cell(zs, close, openp, elig, rebal, n_hold)
        facts = cell_facts(arms, prod_key)
        facts["rebal"], facts["n_hold"] = rebal, n_hold
        facts["arms"] = arms
        cells[tag] = facts
        rows.append({"tag": tag, "rebal": rebal, "n_hold": n_hold,
                     "production_rank": facts["production_rank"],
                     "production_cagr": facts["production_cagr"],
                     "median_cagr": facts["median_cagr"],
                     "spread_cagr": facts["spread_cagr"]})
        print("  cell %-7s rank=%s/%s prod=%.4f median=%.4f spread=%.4f active=%s (%.1fs)"
              % (tag, facts["production_rank"], facts["n_arms"], facts["production_cagr"] or 0.0,
                 facts["median_cagr"] or 0.0, facts["spread_cagr"], facts["active"],
                 time.time() - tc), flush=True)
    cc = cross_cell(cells)
    payload = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "universe": int(close.shape[1]),
        "question": "the sign ordering behind the published headline was measured at ONE "
                    "(rebal, n_hold) cell that was itself chosen on the sample -- does the "
                    "ordering survive the cells it was chosen among?",
        "declared": {k: (dict(v) if k == "signs" else v) for k, v in DECLARED.items()},
        "production_key": prod_key,
        "cells": cells,
        "cross_cell": cc,
        "summary": {
            "cells": rows,
            "active_cells": cc["active_cells"],
            "n_factors_stable": cc["n_factors_stable"],
            "n_factors": cc["n_factors"],
            "ranks_by_cell": {t: cells[t]["production_rank"] for t in cells},
            "rank_range": (max(r for r in {t: cells[t]["production_rank"] for t in cells}.values()
                               if r is not None)
                           - min(r for r in {t: cells[t]["production_rank"] for t in cells}.values()
                                 if r is not None)
                           if any(cells[t]["production_rank"] for t in cells) else None),
            "production_in_top_decile_by_cell": {t: cells[t]["production_in_top_decile"] for t in cells},
            "elapsed_s": None,
        },
        "caveats": [
            "All arms are in-sample by construction: this compares three in-sample optima, it "
            "does not estimate a live return (E219 caveat applies unchanged).",
            "The three cells are not the full 9-cell walk-forward grid -- they are three declared "
            "corners of the same space, chosen before the run and echoed into the payload, so "
            "'stable' means stable across THESE cells, not across all cells.",
            "ETF pool is today's listed set (survivorship), unchanged caveat.",
            "Engine is the reference one (no impact cost, no gap risk); only the cell changes.",
        ],
    }
    g = gate(payload)
    payload["verdict"] = g["verdict"]
    payload["summary"]["elapsed_s"] = round(time.time() - t0, 1)
    payload["gate"] = {"all_ok": g["all_ok"], "checks": g["checks"],
                       "active_cells": g["active_cells"]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": g["verdict"], **{k: v for k, v in payload["summary"].items()
                                                  if k != "cells"}}, ensure_ascii=False, indent=1))
    return payload


def check() -> int:
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    g = gate(payload)
    print("verdict=%s stored=%s all_ok=%s active=%s stable=%s/%s"
          % (g["verdict"], payload.get("verdict"), g["all_ok"], g["active_cells"],
             g["cross_cell"]["n_factors_stable"], g["cross_cell"]["n_factors"]))
    for c in g["checks"]:
        if not c["ok"]:
            print("  RED %s -> %s" % (c["check"], {k: v for k, v in c.items() if k != "check"}))
    if not g["all_ok"] or g["verdict"] != payload.get("verdict"):
        return 1
    return 0


# --- selftest -------------------------------------------------------------------------
def _fixture(cell_signs: dict, spread: float = 0.20) -> dict:
    """A payload whose arm tables pay exactly the factors in `cell_signs[tag]`.

    Each arm's cagr is the sum of (0.10 * sign_k * cell_sign[k]) over factors plus a small
    deterministic ladder, so the factorial main effect of factor k is 0.20 * cell_sign[k] and
    the sign of that effect is the cell_sign we typed. Rank is set by the ladder: oldest arms
    first, so the production arm's rank is reproducible from the table alone.
    """
    cells = {}
    for tag, rebal, n_hold in CELLS:
        cs = cell_signs[tag]
        arms = {}
        for i, v in enumerate(E.sign_vectors(FACTOR_KEYS)):
            cagr = sum(0.10 * v[k] * cs[k] for k in FACTOR_KEYS) + spread * (1 - i / 63.0) * 1e-3
            arms[arm_key(v)] = {"cagr": cagr, "sharpe": 0.5, "maxdd": -0.2, "bars": 1500,
                                "traded": True, "signs": v}
        facts = cell_facts(arms, arm_key(SIGNS))
        facts["rebal"], facts["n_hold"] = rebal, n_hold
        facts["arms"] = arms
        facts["active"] = True
        cells[tag] = facts
    return {
        "declared": {k: (dict(v) if k == "signs" else v) for k, v in DECLARED.items()},
        "production_key": arm_key(SIGNS),
        "cells": cells,
        "cross_cell": cross_cell(cells),
    }


def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    leg("L1 the three declared cells are distinct and include the primary R20_N12",
        len({(r, n) for _, r, n in CELLS}) == 3 and CELLS[0][0] == "R20_N12",
        str([t for t, _, _ in CELLS]))
    leg("L1b every cell carries all 64 arms", all(2 ** len(FACTOR_KEYS) == 64 for _ in CELLS))

    pos = {k: 1 for k in FACTOR_KEYS}
    neg = {k: -1 for k in FACTOR_KEYS}
    same = {t: dict(pos) for t, _, _ in CELLS}
    strict = _fixture({t: dict(pos) for t, _, _ in CELLS})
    leg("L2 the same paying direction at every cell reads as stable",
        gate(strict)["verdict"] == "sign_order_stable_across_cells",
        gate(strict)["verdict"])

    flip_one = {t: dict(pos) for t, _, _ in CELLS}
    flip_one[CELLS[2][0]] = {**pos, FACTOR_KEYS[0]: -1}
    part = _fixture(flip_one)
    leg("L2b one factor flipping at one cell reads as partly stable (5/6)",
        gate(part)["verdict"] == "sign_order_partly_stable",
        "%s stable=%d" % (gate(part)["verdict"], gate(part)["cross_cell"]["n_factors_stable"]))

    flip_all = {t: (dict(pos) if i % 2 == 0 else dict(neg)) for i, (t, _, _) in enumerate(CELLS)}
    dep = _fixture(flip_all)
    leg("L2c alternating whole-cell direction reads as cell dependent",
        gate(dep)["verdict"] == "sign_order_cell_dependent",
        "%s stable=%d" % (gate(dep)["verdict"], gate(dep)["cross_cell"]["n_factors_stable"]))

    dead = _fixture(same)
    for c in dead["cells"].values():
        for a in c["arms"].values():
            a["traded"] = False
        c["n_traded"] = 0
    dead["cross_cell"] = cross_cell(dead["cells"])
    leg("L3 an entirely untraded fixture is refused (no cell active)",
        gate(dead)["verdict"] == "not_assessable_cells_inactive", gate(dead)["verdict"])

    flat = _fixture(same, spread=0.0)
    for c in flat["cells"].values():
        for a in c["arms"].values():
            a["cagr"] = 0.05
        c["spread_cagr"] = 0.0
        c["active"] = False
    flat["cross_cell"] = cross_cell(flat["cells"])
    leg("L3b a flattened grid is refused rather than called stable",
        gate(flat)["verdict"] == "not_assessable_cells_inactive", gate(flat)["verdict"])

    bad = _fixture(same)
    bad["declared"]["cells"] = [{"tag": "R20_N12", "rebal": 20, "n_hold": 12}]
    leg("L4 the gate REDs when the payload was built under different cells",
        not gate(bad)["all_ok"])

    typed = _fixture(same)
    typed["cross_cell"]["n_factors_stable"] = 0
    leg("L4b the gate recomputes the stable count instead of trusting a typed one",
        not gate(typed)["all_ok"] and gate(typed)["verdict"] == "sign_order_stable_across_cells")

    lost = _fixture(same)
    lost["cells"][CELLS[1][0]]["arms"].pop(arm_key(SIGNS))
    leg("L4c a production arm missing from a cell REDs the arm-count leg",
        not gate(lost)["all_ok"])

    leg("L5 main effects are published per factor per active cell",
        all(len((c.get("main_effect_pp") or {})) == len(FACTOR_KEYS)
            for c in strict["cells"].values()))

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