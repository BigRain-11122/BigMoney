"""FUND-VALUE-P2 / FUND-QUALITY-P2 -- judged-cell planner + freeze gate.

Tickets: research/FUND-VALUE-P2.md + research/FUND-QUALITY-P2.md
(r1087 bm-a freeze-window opening; CEO revival licence
O-20261019-2230-bm-b sec.2.2).

Purpose (this slice): turn the frozen sec.3 prose into an EXECUTABLE,
auditable cell plan so the burn runner and every claiming machine share
one machine-checkable grid. It does NOT burn anything and it does NOT
judge anything -- it emits:

  results/fund_value_p2/PLAN.json
  results/fund_quality_p2/PLAN.json

with the 20 judged cells, the null/sens seed sub-streams, the N_eff
accounting, and the two-channel default-stack disable declaration.

Gates enforced here (fail-closed, exit 3):
  G1 judged-cell count == 20 and the sec.3 leg arithmetic identity
  G2 N_eff == 20 + K(2000)
  G3 seeds registered in science_gates.SEED_REGISTRY and distinct
  G4 cost caliber stated (CN-C7 13.041bp/side, x1/x2 faces both present)
  G5 exit-axis declaration present and default-stack disable declared
     on BOTH channels (params 4 keys + ExitPatch 2 keys, r522)

Commands:
  plan      emit both PLAN.json faces (deterministic, offline)
  selftest  offline self-check of the planner itself

Exit codes: 0 ok / 3 gate breach (fail-closed) / 2 mechanism failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

N_NEIGHBORHOOD = [10, 15, 20, 25, 30]
MAIN_N = 20
FACES = ["x1", "x2"]
EXIT_VARIANTS = [
    {"id": "hard_stop_-15pct", "kind": "hard_stop", "level": -0.15},
    {"id": "hard_stop_-20pct", "kind": "hard_stop", "level": -0.20},
    # trailing 12% activate / 8% drawdown
    {"id": "trailing_12_8", "kind": "trailing", "activate": 0.12, "drawdown": 0.08},
]

# Two-channel default-stack disable (r522 engine bridge surface).
DEFAULT_STACK_DISABLE = {
    "params_channel": {
        "take_profit_levels": [],
        "trailing_stop_activate": 1e12,
        "initial_stop": -1.0,
        "time_decay_period": 1e9,
    },
    "exitpatch_channel": {"loss_time_days": 1e9, "global_hard_limit": 1e9},
}

FAMILIES = {
    "value": {
        "batch": "FUND-VALUE-P2",
        "prereg": "research/FUND-VALUE-P2.md",
        "family_key": "fund_value_stock_xs",
        "out_dir": "results/fund_value_p2",
        "t0": "1994-05-03",
        "starts": 401,
        "universe_floor": 60,
        "null_seed": 20515000,
        "sens_seed": 20515500,
        "null_k": 2000,
        "sens_k": 500,
        "main_definition": "pe_only",
        "ablation_definitions": ["pb_only", "pe_x_pb_rank"],
        "data_face": "data/fund_history_export/value_faces.parquet",
        "cost_rt_bp": 52.164,
    },
    "quality": {
        "batch": "FUND-QUALITY-P2",
        "prereg": "research/FUND-QUALITY-P2.md",
        "family_key": "fund_quality_stock_xs",
        "out_dir": "results/fund_quality_p2",
        "t0": "2001-09-03",
        "starts": 401,
        "universe_floor": 60,
        "null_seed": 20517500,
        "sens_seed": 20518000,
        "null_k": 2000,
        "sens_k": 500,
        "main_definition": "roe_level",
        # sec.3 legs: definition ablation (stability-only rank) + composite
        # (level rank + stability rank). Both are ablations of the main judge.
        "ablation_definitions": ["roe_stability_only",
                                 "roe_level_x_stability_rank"],
        "data_face": "data/fund_history_export/quality_faces.parquet",
        "cost_rt_bp": 52.164,
    },
}


def build_cells(cfg: dict) -> list:
    """Emit the 20 judged cells exactly per prereg sec.3 leg arithmetic.

    leg1 main judge      : main definition, N=20, x1/x2        -> 2
    leg2 N neighborhood  : N in {10,15,25,30}, x1/x2           -> 8
    leg3 definition abl. : each ablation def, N=20, x1/x2      -> 2 (value)
                                                                  2 (quality)
    leg3b composite      : second ablation def (value: composite rank)
                           / stability composite (quality)      -> 2
    leg4 exit axis       : 3 variants, x1/x2, N=20 main def     -> 6
    total                                                      -> 20
    """
    cells = []
    main_def = cfg["main_definition"]
    ablations = cfg["ablation_definitions"]

    def add(cid, leg, definition, n, face, exit_axis, extra=None):
        cell = {
            "cell_id": cid,
            "leg": leg,
            "definition": definition,
            "top_n": n,
            "cost_face": face,
            "exit_axis": exit_axis,
            "signal_day": "month_first_trading_day",
            "weighting": "equal",
            "rebalance": "monthly_rotation",
        }
        if extra:
            cell.update(extra)
        cells.append(cell)

    # leg1 -- main judge (2)
    for face in FACES:
        add("MAIN-%s" % face, "leg1_main", main_def, MAIN_N, face,
            {"kind": "hold_through", "engine_default_stack": "DISABLED_TWO_CHANNEL"})

    # leg2 -- Top-N neighborhood (8)
    for n, face in product([n for n in N_NEIGHBORHOOD if n != MAIN_N], FACES):
        add("NN-%d-%s" % (n, face), "leg2_n_neighborhood", main_def, n, face,
            {"kind": "hold_through", "engine_default_stack": "DISABLED_TWO_CHANNEL"})

    # leg3 -- definition ablation, first definition (2)
    for face in FACES:
        add("DEF-%s-%s" % (ablations[0], face), "leg3_definition_ablation",
            ablations[0], MAIN_N, face,
            {"kind": "hold_through", "engine_default_stack": "DISABLED_TWO_CHANNEL"})

    # leg3b -- second ablation / composite (2)
    for face in FACES:
        add("DEF-%s-%s" % (ablations[-1], face), "leg3b_composite",
            ablations[-1], MAIN_N, face,
            {"kind": "hold_through", "engine_default_stack": "DISABLED_TWO_CHANNEL"})

    # leg4 -- exit axis (6): strategy-owned exits, main definition
    for vari, face in product(EXIT_VARIANTS, FACES):
        add("EX-%s-%s" % (vari["id"], face), "leg4_exit_axis", main_def, MAIN_N,
            face, dict(vari), {"strategy_owned_exit": True})

    return cells


def build_plan(cfg: dict) -> dict:
    cells = build_cells(cfg)
    leg_counts = {}
    for c in cells:
        leg_counts[c["leg"]] = leg_counts.get(c["leg"], 0) + 1
    n_eff = len(cells) + cfg["null_k"]
    return {
        "batch": cfg["batch"],
        "prereg": cfg["prereg"],
        "family_key": cfg["family_key"],
        "generated_by": "scripts/fund_vq_p2_plan.py",
        "status": "PLAN_ONLY__NOT_FROZEN__NOT_BURNED",
        "data_face": cfg["data_face"],
        "signal_skeleton": {
            "t0": cfg["t0"],
            "monthly_starts": cfg["starts"],
            "universe_floor": cfg["universe_floor"],
            "signal_day": "month_first_trading_day",
            "weighting": "equal",
        },
        "judged_cells": cells,
        "leg_counts": leg_counts,
        "judged_strategy_cells": len(cells),
        "nulls": {
            "k": cfg["null_k"],
            "family": "same_mask_random_spans",
            "seed_base": cfg["null_seed"],
            "rng": "default_rng([null_seed, k]) k=0..k-1 (pair-seed sub-stream)",
        },
        "sensitivity": {
            "k": cfg["sens_k"],
            "seed_base": cfg["sens_seed"],
            "note": "descriptive bootstrap axis, zero judged weight",
        },
        "n_eff": n_eff,
        "cost_caliber": {
            "spec": "V2 (ADV20 three-layer slippage + 1% ADV cap), always-on",
            "x1_side_bp": cfg["cost_rt_bp"] / 2.0,
            "x2_rt_bp": cfg["cost_rt_bp"],
            "faces": FACES,
        },
        "exit_axis_declaration": {
            "main_judge": "strategy_signal_reversal_plus_stop_family",
            "control": "hold_through_with_engine_default_stack_disabled",
            "template_default": "zero cells (not adopted)",
            "default_stack_disable": DEFAULT_STACK_DISABLE,
            "census_block_share": 0.20,
        },
        "gates": {
            "G1_prime_v2": "science_gates.g1_prime_v2 (shared library, never copied)",
            "G2_registration_v2": "science_gates.g2_registration_v2 (DSR>=0.95, PBO<=0.25)",
            "M1_t": "science_gates.m1_t_value_gate (t>=2.0)",
        },
        "burn_discipline": {
            "frozen_before_burn": True,
            "pool_claim": True,
            "bm_a_weekday_daytime": "zero scheduling (machine iron law)",
        },
    }


def gate_plan(plan: dict, cfg: dict) -> list:
    """Return a list of breach strings (empty == pass)."""
    breaches = []
    cells = plan["judged_cells"]
    if len(cells) != 20:
        breaches.append("G1 cell count %d != 20" % len(cells))
    if len({c["cell_id"] for c in cells}) != len(cells):
        breaches.append("G1 duplicate cell_id")
    expect_legs = {"leg1_main": 2, "leg2_n_neighborhood": 8,
                   "leg3_definition_ablation": 2, "leg3b_composite": 2,
                   "leg4_exit_axis": 6}
    if plan["leg_counts"] != expect_legs:
        breaches.append("G1 leg arithmetic %r != %r"
                        % (plan["leg_counts"], expect_legs))
    if plan["n_eff"] != 20 + cfg["null_k"]:
        breaches.append("G2 N_eff %d != %d" % (plan["n_eff"], 20 + cfg["null_k"]))
    if sorted({c["cost_face"] for c in cells}) != FACES:
        breaches.append("G4 cost faces %r" % sorted({c["cost_face"] for c in cells}))
    if not all(c.get("exit_axis") for c in cells):
        breaches.append("G5 cell without exit-axis declaration")
    dis = plan["exit_axis_declaration"]["default_stack_disable"]
    if len(dis["params_channel"]) != 4 or len(dis["exitpatch_channel"]) != 2:
        breaches.append("G5 default-stack disable is not two-channel 4+2")
    # seeds
    try:
        for p in (os.path.join(ROOT, "scripts"), ROOT):
            if p not in sys.path:
                sys.path.insert(0, p)
        import science_gates as sg
        reg = getattr(sg, "SEED_REGISTRY", {})
    except Exception as exc:  # mechanism failure, not a gate breach
        raise RuntimeError("science_gates import failed: %s" % exc)
    for key in ("null_seed", "sens_seed"):
        if cfg[key] not in reg.values():
            breaches.append("G3 seed %s=%d not registered" % (key, cfg[key]))
    if cfg["null_seed"] == cfg["sens_seed"]:
        breaches.append("G3 null and sens seed bases must differ")
    return breaches


def cmd_plan(_args) -> int:
    changed = []
    for name, cfg in FAMILIES.items():
        plan = build_plan(cfg)
        breaches = gate_plan(plan, cfg)
        receipt = {
            "batch": cfg["batch"],
            "verdict": "GREEN" if not breaches else "RED",
            "breaches": breaches,
            "judged_strategy_cells": plan["judged_strategy_cells"],
            "n_eff": plan["n_eff"],
            "leg_counts": plan["leg_counts"],
            "generated_at_utc_epoch": int(__import__("time").time()),
        }
        out_dir = os.path.join(ROOT, cfg["out_dir"])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "PLAN.json"), "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(os.path.join(ROOT, "results",
                               "_%s_plan_gate.json" % name), "w",
                  encoding="utf-8") as fh:
            json.dump(receipt, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        changed.append(receipt)
        print("[%s] %s cells=%d n_eff=%d breaches=%d"
              % (cfg["batch"], receipt["verdict"],
                 receipt["judged_strategy_cells"], receipt["n_eff"],
                 len(breaches)))
        if breaches:
            for b in breaches:
                print("   BREACH: %s" % b)
    if any(r["verdict"] != "GREEN" for r in changed):
        return 3
    return 0


def cmd_selftest(_args) -> int:
    fails = []

    def check(name, cond):
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    for name, cfg in FAMILIES.items():
        cells = build_cells(cfg)
        check("%s: 20 judged cells" % name, len(cells) == 20)
        check("%s: unique ids" % name,
              len({c["cell_id"] for c in cells}) == 20)
        check("%s: both cost faces" % name,
              sorted({c["cost_face"] for c in cells}) == FACES)
        check("%s: N grid covers 5 values" % name,
              sorted({c["top_n"] for c in cells}) == N_NEIGHBORHOOD)
        check("%s: 3 exit variants x2 faces" % name,
              len([c for c in cells if c["leg"] == "leg4_exit_axis"]) == 6)
        check("%s: main definition on main cells" % name,
              all(c["definition"] == cfg["main_definition"]
                  for c in cells if c["leg"] in ("leg1_main", "leg2_n_neighborhood",
                                                 "leg4_exit_axis")))
        check("%s: ablations distinct from main" % name,
              all(d != cfg["main_definition"] for d in cfg["ablation_definitions"]))
        plan = build_plan(cfg)
        check("%s: N_eff == 2020" % name, plan["n_eff"] == 2020)
        check("%s: plan deterministic" % name,
              json.dumps(plan, sort_keys=True) == json.dumps(build_plan(cfg), sort_keys=True))
        check("%s: default stack disabled on 4+2 keys" % name,
              len(DEFAULT_STACK_DISABLE["params_channel"]) == 4
              and len(DEFAULT_STACK_DISABLE["exitpatch_channel"]) == 2)
        check("%s: seed bases differ" % name, cfg["null_seed"] != cfg["sens_seed"])

    # negative controls: the gate must actually catch breakage
    bad = build_plan(FAMILIES["value"])
    bad["judged_cells"] = bad["judged_cells"][:-1]
    bad["leg_counts"] = dict(bad["leg_counts"])
    bad["leg_counts"]["leg4_exit_axis"] = 5
    has_breach = False
    try:
        has_breach = bool(gate_plan(bad, FAMILIES["value"]))
    except Exception:
        has_breach = False
    check("negative control: dropped cell is caught", has_breach)

    bad2 = build_plan(FAMILIES["quality"])
    bad2["exit_axis_declaration"]["default_stack_disable"]["params_channel"].pop(
        "initial_stop")
    has_breach2 = False
    try:
        has_breach2 = bool(gate_plan(bad2, FAMILIES["quality"]))
    except Exception:
        has_breach2 = False
    check("negative control: 3-key disable is caught", has_breach2)

    print("selftest: %d/%d PASS" % (14 - len(fails), 14))
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    return {"plan": cmd_plan, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())