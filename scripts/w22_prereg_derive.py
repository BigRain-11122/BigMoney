"""W22 prereg cell-derive -- pre-holiday multi-bar hold (TRIAL_LABOR_W22).

Deterministic, hermetic (zero panel, zero network). Consumes the E23 seasonal
horizon/stability census and freezes the W22 cell grid, the explicit exit-axis
declaration (O-20261001-1108 three-way gate) and the D6 same-family
correlation admission. Emits results/trial_labor_w22/w22_grammar.json.

Law anchors:
  * E23 handoff (research/digests/DIGEST-20261020-seasonal-horizon-stability.md):
    monthly-switch family is dead after cost; the ONLY era-stable cost-positive
    cell is the pre-holiday multi-bar hold.
  * O-20261001-1108 exit axis must be declared explicitly at freeze time.
  * D6 same-family max|corr| >= 0.7 -> reject (declared here, measured at screen).

Usage:
  python scripts/w22_prereg_derive.py derive [--out <path>]
  python scripts/w22_prereg_derive.py selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS_PATH = os.path.join(ROOT, "results", "seasonal_horizon_stability",
                           "CENSUS-2026-10-19.json")
OUT_DIR = os.path.join(ROOT, "results", "trial_labor_w22")
OUT_PATH = os.path.join(OUT_DIR, "w22_grammar.json")

BATCH = "TRIAL_LABOR_W22"
VARIANTS = ["hol_pre1", "hol_pre2"]
HORIZONS = [1, 2, 3, 4, 5]
NULL_K = 200
NULL_SEED = 20670000          # fresh band; verify FREE via seed_admit_gate at burn
D6_PEERS = ["fund_divlowvol_p2", "rev_osc_std"]
D6_THRESHOLD = 0.70

# Exit axis (O-20261001-1108): strategy-own time exit, engine default stack OFF.
EXIT_AXIS = {
    "mode": "strategy_own",
    "rule": "hold exactly h bars from entry, exit at close of bar h",
    "engine_default_stack": "disabled",
    "template_default_allowed": False,
}

PREREG = "research/TRIAL_LABOR_W22_PREREG.md"


def load_census(path: str = CENSUS_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _anchor(census: dict, variant: str, h: int) -> dict:
    row = census.get("horizon_table", {}).get(f"{variant}@h{h}")
    if row is None:
        raise KeyError(f"census has no horizon cell {variant}@h{h}")
    return {
        "excess": row["excess"],
        "excess_per_year": row["excess_per_year"],
        "variant_mean": row["variant_mean"],
        "variant_win": row["variant_win"],
        "t_naive": row["t_naive"],
        "n": row["n"],
    }


def derive(census_path: str = CENSUS_PATH) -> dict:
    census = load_census(census_path)
    cells = []
    for variant in VARIANTS:
        for h in HORIZONS:
            cells.append({
                "cell_id": f"{variant}@h{h}",
                "family": "hol_pre_hold",
                "variant": variant,
                "params": {"h": h, "entry": "t+1 open after signal day",
                           "exit": f"close of bar h={h}"},
                "census_anchor": _anchor(census, variant, h),
            })
    body = {
        "batch": BATCH,
        "status": "DRAFT_DERIVED (freeze at runner pin + seed registration)",
        "prereg": PREREG,
        "evidence_cutoff": census["evidence_cutoff"],
        "upstream": {
            "census": "results/seasonal_horizon_stability/CENSUS-2026-10-19.json",
            "series": census.get("series"),
            "cells": census.get("cells"),
            "face_symbols": census.get("face", {}).get("symbols"),
            "face_days_usable": census.get("face", {}).get("days_usable"),
            "years_span": census.get("years_span"),
            "cost_per_side": census.get("face", {}).get("cost_per_side"),
        },
        "grid": {
            "variants": VARIANTS,
            "horizons": HORIZONS,
            "cells_n": len(cells),
            "null_k": NULL_K,
            "null_seed": NULL_SEED,
            "screen_trials_n": len(cells) + NULL_K,
        },
        "cells": cells,
        "exit_axis": EXIT_AXIS,
        "d6": {
            "peers": D6_PEERS,
            "threshold": D6_THRESHOLD,
            "rule": "max|corr| >= 0.70 vs peer daily returns -> reject family",
            "measured": None,
            "note": "measured at screen-finalize on the frozen leg-L face",
        },
        "gates": ["banned_direction_gate", "queue_seed_gate", "seed_admit_gate",
                  "G-PANEL", "G-ROSTER", "G-EXITCFG", "G-LINEAGE"],
        "honest": [
            "upstream census cells are uncorrected (45 cells) and h>1 windows overlap",
            "h=4 best cell was selected post-hoc from 45 cells; this batch re-tests it",
            "entry at t+1 open is an engine convention, not a modelled auction",
        ],
    }
    blob = json.dumps(body, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    body["grammar_sha16"] = hashlib.sha256(blob).hexdigest()[:16]
    return body


def write(grammar: dict, out_path: str = OUT_PATH) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(grammar, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return out_path


def selftest() -> int:
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    g = derive()
    g2 = derive()
    leg("cells_n==10", g["grid"]["cells_n"] == 10, g["grid"]["cells_n"])
    leg("screen_trials_n==210", g["grid"]["screen_trials_n"] == 210)
    leg("determinism", g == g2, "" if g == g2 else "derive is not reproducible")
    leg("exit_axis strategy_own", g["exit_axis"]["mode"] == "strategy_own")
    leg("engine default stack disabled",
        g["exit_axis"]["engine_default_stack"] == "disabled")
    leg("template_default disallowed",
        g["exit_axis"]["template_default_allowed"] is False)
    ids = [c["cell_id"] for c in g["cells"]]
    leg("cell ids unique", len(ids) == len(set(ids)))
    leg("all horizons covered",
        {c["params"]["h"] for c in g["cells"]} == set(HORIZONS))
    leg("all anchors present",
        all(c["census_anchor"]["n"] > 0 for c in g["cells"]))
    leg("d6 threshold 0.70", g["d6"]["threshold"] == 0.70 and
        g["d6"]["peers"] == D6_PEERS)
    leg("evidence_cutoff==census", g["evidence_cutoff"] == "2026-10-19")
    leg("sha16 len 16", len(g["grammar_sha16"]) == 16)
    import inspect
    import re
    src = inspect.getsource(sys.modules[__name__])
    net_import = re.search(
        r"^\s*(?:import|from)\s+(?:requests|urllib|urllib3|http|socket)\b",
        src, re.MULTILINE)
    leg("hermetic (no net imports)", net_import is None,
        "" if net_import is None else net_import.group(0).strip())
    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("PASS" if ok else "FAIL"), name, detail)
    print(f"selftest {passed}/{len(legs)}")
    return 0 if passed == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["derive", "selftest"])
    ap.add_argument("--out", default=OUT_PATH)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    g = derive()
    path = write(g, args.out)
    print(json.dumps({"out": os.path.relpath(path, ROOT).replace("\\", "/"),
                      "sha16": g["grammar_sha16"],
                      "cells_n": g["grid"]["cells_n"],
                      "screen_trials_n": g["grid"]["screen_trials_n"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())