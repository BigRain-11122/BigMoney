"""FUND-QUALITY-P2 runner -- quality-family revival batch (definition x neighbourhood x exit).

Prereg: research/FUND-QUALITY-P2.md (freeze window r1087, bm-a).
Authorization: O-20261019-2230-bm-b sec.2 (CEO negative-line revival, three-piece
law: authorization + new prereg + new evidence).
Plan: results/fund_quality_p2/PLAN.json (r1088, scripts/fund_vq_p2_plan.py,
20 judged cells / N_eff 2,020 / seeds 20517500+20518000).

This file only IMPLEMENTS the frozen plan; it never restates a threshold. The
universe / liquidity / ST skeleton, the statutory PIT join and the engine
decomposition are P1's own code (scripts/fund_quality_p1.py), reused by binding
the P1 module globals to this run's panel, so the family skeleton cannot drift.

Definition neighbourhood (prereg sec.3 leg1, frozen):
  roe_level                    P1 verbatim: descending latest available roe_q
  roe_stability_only           descending 1/std of the last 8 available roe_q
                               quarters; fewer than 8 quarters = honest exclusion
  roe_level_x_stability_rank   composite: rank(level) + rank(stability), the
                               lowest rank sum wins
Stability is computed on the STATUTORY avail-anchor series only (no period_end
join, no forward-fill of period_end), matching P1's disclosed PIT convention.

Usage (CWD = repo root):
  python scripts/fund_quality_p2_backtest.py probe
  python scripts/fund_quality_p2_backtest.py cells
  python scripts/fund_quality_p2_backtest.py run --cell MAIN-x1 --dry-run
  python scripts/fund_quality_p2_backtest.py run --cell MAIN-x1
  python scripts/fund_quality_p2_backtest.py status
  python scripts/fund_quality_p2_backtest.py finalize
  python scripts/fund_quality_p2_backtest.py selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import fund_vq_p2_common as C

ROOT = C.ROOT
OUT_DIR = os.path.join(ROOT, "results", "fund_quality_p2")
CELL_DIR = os.path.join(OUT_DIR, "cells")
PREREG = os.path.join(ROOT, "research", "FUND-QUALITY-P2.md")
PROBE_RECEIPT = os.path.join(ROOT, "results", "_fund_quality_p2_freeze_probe.json")
BATCH_NAME = "FUND-QUALITY-P2"
FAMILY_KEY = "fund_quality_stock_xs"
DEFINITIONS = ("roe_level", "roe_stability_only", "roe_level_x_stability_rank")
FACES = ("x1", "x2")
K_NULLS = 2000
BATCH_CELLS = 2020
SEED_NULLS = 20_517_500
SEED_SENS = 20_518_000
STAB_WINDOW = 8          # prereg sec.3 leg1: last 8 available quarters
CUTOFF = C.CUTOFF

_G = {}


def _plan():
    return C.load_plan("quality")


def _cells():
    return C.cells_of(_plan())


# ------------------------------------------------------------------ data face

def _init(basis="auto"):
    """Load the price panel and rebind P1's skeleton globals to it."""
    if _G.get("ready"):
        return _G
    import fund_divlowvol_p2_probe as DP
    import fund_quality_p1 as F1

    panel = DP._load_panel(basis)
    if isinstance(panel, Exception):
        raise RuntimeError(f"panel unavailable: {panel!r}")
    idx, syms, meta, close_q, pct, amt, volm = panel
    if isinstance(idx, np.ndarray):
        idx = pd.to_datetime(idx)

    def _mm(name):
        cand = os.path.join(DP.LOCAL_CACHE, name + ".npy")
        if os.path.exists(cand):
            return np.load(cand, mmap_mode="r")
        import p1c_stock_ic_batch as P1C
        return np.load(os.path.join(P1C.CACHE_DIR, name + ".npy"), mmap_mode="r")

    open_np, high_np, low_np = _mm("open"), _mm("high"), _mm("low")
    close_np = close_q
    first_valid = np.argmax(np.isfinite(np.asarray(close_np[:])), axis=0)
    codes_arr = np.array([str(s) for s in syms])
    static_thr = np.where(np.array([s.startswith("68") for s in syms]),
                          0.20, 0.10).astype(np.float32)
    is_cx = np.array([s.startswith("30") for s in syms])

    G = F1._G
    G.clear()
    G.update(idx=idx, syms=syms, codes_arr=codes_arr, first_valid=first_valid,
             static_thr=static_thr, is_cx=is_cx,
             close_np=close_np, open_np=open_np, high_np=high_np,
             low_np=low_np, volume_np=volm, amount_np=amt, pct_np=pct,
             by_sym=F1._load_quality_faces(),
             month_pos=F1.enumerate_starts_monthly(idx, close_np),
             regime=None)
    F1._firing_months()
    _G.update(ready=True, basis=DP.PANEL_BASIS.get("basis"), G=G, idx=idx,
              syms=syms, codes_arr=codes_arr,
              cut_pos=int(np.max(np.where(idx <= CUTOFF)[0])),
              t0_pos=int(G["_t0_pos"]))
    C.log(OUT_DIR, f"init basis={_G['basis']} bars={len(idx)} syms={len(syms)} "
                   f"cut_pos={_G['cut_pos']} t0={_G['t0_pos']} "
                   f"months={len(G['month_pos'])}")
    return _G


def _stability(pack, t_int):
    """1/std of the last STAB_WINDOW statutory avail anchors <= t.
    Fewer than STAB_WINDOW quarters = insufficient history (honest NaN)."""
    if pack is None:
        return np.nan
    ad, roe = pack
    k = int(np.searchsorted(ad, t_int, side="right"))
    if k < STAB_WINDOW:
        return np.nan
    v = np.asarray(roe[k - STAB_WINDOW:k], dtype=np.float64)
    if not np.all(np.isfinite(v)):
        return np.nan
    sd = float(np.std(v, ddof=1))
    return float("inf") if sd == 0.0 else 1.0 / sd


def _month_choice(definition, n):
    """(m, end, picks, weight) for one definition at one month, P1 skeleton."""
    import fund_quality_p1 as F1
    G = _G["G"]
    codes = G["codes_arr"]
    syms = G["syms"]
    by_sym = G["by_sym"]
    idx = G["idx"]
    out = []
    for (m, end) in F1._firing_months():
        u = F1._month_universe(m)
        pj, roe = F1._pick_j(u)
        t_int = int(idx[m].strftime("%Y%m%d"))
        if definition == "roe_level":
            top = C.top_desc(pj, roe, n, codes)
        elif definition == "roe_stability_only":
            stab = np.array([_stability(by_sym.get(syms[j]), t_int) for j in pj],
                            dtype=np.float64)
            keep = np.isfinite(stab)
            pj2, stab2 = pj[keep], stab[keep]
            top = C.top_desc(pj2, stab2, n, codes)
        elif definition == "roe_level_x_stability_rank":
            stab = np.array([_stability(by_sym.get(syms[j]), t_int) for j in pj],
                            dtype=np.float64)
            keep = np.isfinite(stab)
            pj2, roe2, stab2 = pj[keep], roe[keep], stab[keep]
            if len(pj2):
                score = C.avg_rank(roe2) + C.avg_rank(stab2)
                top = C.top_composite_asc(pj2, score, n, codes)
            else:
                top = pj2
        else:
            raise RuntimeError(f"undeclared definition: {definition}")
        out.append((m, end, top, 1.0 / max(1, len(top))))
    return out


def _cell_spans(cell_id):
    import fund_quality_p1 as F1
    cell = _cells()[cell_id]
    cache = _G.setdefault("_spans", {})
    key = (cell["definition"], int(cell["top_n"]))
    if key not in cache:
        cache[key] = F1._spans_from_picks(_month_choice(*key))
    return cache[key]


def cmd_probe(_):
    gates = {}
    ok = True
    if not os.path.exists(PREREG):
        gates["prereg"] = "MISSING"
        ok = False
    else:
        with open(PREREG, encoding="utf-8") as fh:
            head = fh.readline()
        frozen = "DRAFT-NOT-FROZEN" not in head
        gates["prereg"] = "FROZEN" if frozen else "DRAFT-NOT-FROZEN"
        ok = ok and frozen
    if not os.path.exists(PROBE_RECEIPT):
        gates["freeze_probe"] = "MISSING"
        ok = False
    else:
        with open(PROBE_RECEIPT, encoding="utf-8") as fh:
            gates["freeze_probe"] = json.load(fh).get("verdict")
        ok = ok and gates["freeze_probe"] == "GREEN"
    try:
        plan = _plan()
        gates["plan"] = f"{len(plan['judged_cells'])} cells / n_eff {plan['n_eff']}"
        ok = ok and len(plan["judged_cells"]) == 20
    except Exception as exc:                     # fail closed
        gates["plan"] = f"ERROR {exc}"
        ok = False
    payload = {"batch": BATCH_NAME, "ok": bool(ok), "gates": gates,
               "ts": C.now_iso(), "receipt": PROBE_RECEIPT}
    C.dump(payload, os.path.join(OUT_DIR, "probe.json"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if ok else 4


def cmd_cells(_):
    plan = _plan()
    rows = [{"cell_id": c["cell_id"], "leg": c["leg"],
             "definition": c["definition"], "top_n": c["top_n"],
             "cost_face": c["cost_face"], "exit": c["exit_axis"]["kind"]}
            for c in plan["judged_cells"]]
    print(json.dumps({"n_cells": len(rows), "nulls": K_NULLS,
                      "n_eff": plan["n_eff"], "rows": rows},
                     ensure_ascii=False, indent=2))
    return 0


def cmd_run(args):
    cells = _cells()
    if args.cell not in cells:
        print(f"unknown cell {args.cell}; known={sorted(cells)}", file=sys.stderr)
        return 2
    cell = cells[args.cell]
    _init(args.basis)
    lo = int(_G["t0_pos"])
    hi = int(_G["cut_pos"])
    spans = _cell_spans(args.cell)
    path = os.path.join(CELL_DIR, f"{args.cell}.json")

    if args.dry_run:
        picks = _month_choice(cell["definition"], int(cell["top_n"]))
        sizes = [len(top) for (_, _, top, _) in picks]
        payload = {
            "batch": BATCH_NAME, "cell": args.cell, "mode": "dry-run",
            "definition": cell["definition"], "top_n": cell["top_n"],
            "cost_face": cell["cost_face"],
            "exit": cell["exit_axis"], "basis": _G["basis"],
            "window": [str(_G["idx"][lo].date()), str(CUTOFF.date())],
            "n_firing_months": len(picks),
            "pick_size_min": min(sizes) if sizes else 0,
            "pick_size_max": max(sizes) if sizes else 0,
            "empty_months": sum(1 for s in sizes if s == 0),
            "n_symbols_touched": len(spans),
            "evidence_cutoff": str(CUTOFF.date()), "ts": C.now_iso(),
        }
        C.dump(payload, path)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0

    import fund_quality_p1 as F1
    run = C.run_cell(F1, _G["G"], spans, cell["cost_face"], lo, hi,
                     cell["exit_axis"])
    if run is None:
        print("no spans -- nothing burned", file=sys.stderr)
        return 2
    payload = {
        "batch": BATCH_NAME, "cell": args.cell,
        "definition": cell["definition"], "top_n": cell["top_n"],
        "cost_face": cell["cost_face"], "exit": cell["exit_axis"],
        "basis": _G["basis"],
        "window": [str(_G["idx"][lo].date()), str(CUTOFF.date())],
        "metrics": C.metrics(run["nav"]), "n_trades": run["n_trades"],
        "n_entries": run["n_entries"], "exit_reasons": run["exit_reasons"],
        "default_stack_share": C.default_stack_share(run["exit_reasons"],
                                                     run["n_trades"]),
        "evidence_cutoff": str(CUTOFF.date()), "ts": C.now_iso(),
    }
    C.dump(payload, path)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_run_cells(args):
    """Burn every not-yet-burned cell (resume = per-cell JSON checkpoint).
    One pool unit = one process; a killed run resumes where it stopped."""
    cells = _cells()
    _init(args.basis)
    lo = int(_G["t0_pos"])
    hi = int(_G["cut_pos"])
    import fund_quality_p1 as F1
    done = skipped = failed = 0
    for cid in sorted(cells):
        path = os.path.join(CELL_DIR, f"{cid}.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    if json.load(fh).get("mode") != "dry-run":
                        skipped += 1
                        continue
            except Exception:
                pass
        cell = cells[cid]
        spans = _cell_spans(cid)
        run = C.run_cell(F1, _G["G"], spans, cell["cost_face"], lo, hi,
                         cell["exit_axis"])
        if run is None:
            failed += 1
            continue
        payload = {
            "batch": BATCH_NAME, "cell": cid,
            "definition": cell["definition"], "top_n": cell["top_n"],
            "cost_face": cell["cost_face"], "exit": cell["exit_axis"],
            "basis": _G["basis"],
            "window": [str(_G["idx"][lo].date()), str(CUTOFF.date())],
            "metrics": C.metrics(run["nav"]), "n_trades": run["n_trades"],
            "n_entries": run["n_entries"], "exit_reasons": run["exit_reasons"],
            "default_stack_share": C.default_stack_share(run["exit_reasons"],
                                                         run["n_trades"]),
            "evidence_cutoff": str(CUTOFF.date()), "ts": C.now_iso(),
        }
        C.dump(payload, path)
        done += 1
        C.log(OUT_DIR, f"cell {cid} burned trades={run['n_trades']} "
                       f"sharpe={payload['metrics']['sharpe_ann']}")
    print(json.dumps({"batch": BATCH_NAME, "mode": "run-cells",
                      "burned": done, "resumed_skip": skipped,
                      "failed": failed, "cells": len(cells)},
                     ensure_ascii=False, sort_keys=True))
    return 0 if failed == 0 else 2


def cmd_status(_):
    payload = C.status_payload(CELL_DIR, _cells())
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_finalize(_):
    plan = _plan()
    payload, _ = C.finalize_payload(plan, CELL_DIR, BATCH_NAME, FAMILY_KEY,
                                    "fund_quality_p2_results.json")
    C.dump(payload, os.path.join(OUT_DIR, "fund_quality_p2_results.json"))
    print(json.dumps({k: payload[k] for k in
                      ("cells_burned", "cells_expected", "g1_prime_v2",
                       "evidence_cutoff")}, ensure_ascii=False, sort_keys=True))
    return 0


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "pass": bool(cond), "detail": str(detail)})

    plan = _plan()
    cells = _cells()
    leg("L1_plan_20_cells", len(cells) == 20 and plan["judged_strategy_cells"] == 20,
        len(cells))
    leg("L2_n_eff_2020", int(plan["n_eff"]) == BATCH_CELLS == 20 + K_NULLS,
        plan["n_eff"])
    leg("L3_faces_2", all(c["cost_face"] in FACES for c in cells.values()))
    leg("L4_definitions", set(c["definition"] for c in cells.values()) == set(DEFINITIONS),
        sorted(set(c["definition"] for c in cells.values())))
    leg("L5_seed_band", plan["nulls"]["seed_base"] == SEED_NULLS
        and plan["sensitivity"]["seed_base"] == SEED_SENS,
        f"{plan['nulls']['seed_base']}/{plan['sensitivity']['seed_base']}")
    leg("L6_leg_counts", plan["leg_counts"] == {
        "leg1_main": 2, "leg2_n_neighborhood": 8, "leg3_definition_ablation": 2,
        "leg3b_composite": 2, "leg4_exit_axis": 6}, plan["leg_counts"])
    leg("L7_exit_cells", sum(1 for c in cells.values()
                             if c["exit_axis"]["kind"] != "hold_through") == 6)
    ok = True
    for c in cells.values():
        p, patch = C.exit_params(c["exit_axis"])
        ok &= p["take_profit_levels"] == () and p["time_decay_period"] >= 10 ** 9
        ok &= p["trailing_stop_activate"] >= 1e12 or c["exit_axis"]["kind"] == "trailing"
        ok &= patch["loss_time_days"] >= 10 ** 9
        ok &= patch["global_hard_limit"] >= 10 ** 9
    leg("L8_default_stack_disabled", ok)
    hard = {c["cell_id"]: c["exit_axis"] for c in cells.values()
            if c["exit_axis"]["kind"] == "hard_stop"}
    leg("L9_hard_stops", hard["EX-hard_stop_-15pct-x1"]["level"] == -0.15
        and hard["EX-hard_stop_-20pct-x1"]["level"] == -0.20)
    trail = [c["exit_axis"] for c in cells.values() if c["exit_axis"]["kind"] == "trailing"][0]
    leg("L10_trail_12_8", trail["activate"] == 0.12 and trail["drawdown"] == 0.08)
    # stability kernel: 8-period window, PIT as-of, honest exclusion
    ad = np.array([20200101, 20200401, 20200701, 20201001, 20210101,
                   20210401, 20210701, 20211001], dtype=np.int64)
    roe = np.array([0.05, 0.06, 0.04, 0.07, 0.05, 0.06, 0.05, 0.05])
    pack = (ad, roe)
    leg("L11_stab_full_window", np.isfinite(_stability(pack, 20211231)))
    leg("L12_stab_insufficient", np.isnan(_stability(pack, 20210701)))
    leg("L13_stab_zero_std_inf",
        _stability((ad, np.array([0.05] * 8)), 20211231) == float("inf"))
    leg("L14_stab_asof_cut",
        np.isnan(_stability(pack, 20201001)))  # only 4 anchors <= t
    leg("L15_stab_missing_pack", np.isnan(_stability(None, 20211231)))
    # rank kernels reused from the shared core
    r = C.avg_rank([3.0, 1.0, 1.0, 2.0])
    leg("L16_avg_rank_ties", list(r) == [4.0, 1.5, 1.5, 3.0], list(r))
    codes = np.array(["b", "a", "c"])
    leg("L17_top_desc",
        list(C.top_desc(np.array([0, 1, 2]), np.array([0.1, 0.3, 0.2]), 2, codes)) == [1, 2])
    leg("L18_top_desc_tie_code",
        list(C.top_desc(np.array([0, 1]), np.array([0.2, 0.2]), 1, codes)) == [1])
    nav = pd.Series(np.linspace(1e6, 1.1e6, 60))
    leg("L19_metrics_ann_positive", (C.metrics(nav)["ann_ret"] or 0) > 0)
    leg("L20_metrics_flat_degenerate",
        C.metrics(pd.Series([1e6] * 60))["sharpe_ann"] is None)
    ok_all = all(x["pass"] for x in legs)
    print(json.dumps({"selftest": "PASS" if ok_all else "FAIL", "legs": legs,
                      "n": len(legs)}, ensure_ascii=False, indent=2))
    return 0 if ok_all else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe").set_defaults(fn=cmd_probe)
    sub.add_parser("cells").set_defaults(fn=cmd_cells)
    p = sub.add_parser("run")
    p.add_argument("--cell", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--basis", default="auto", choices=["auto", "local", "p1c"])
    p.set_defaults(fn=cmd_run)
    q = sub.add_parser("run-cells")
    q.add_argument("--basis", default="auto", choices=["auto", "local", "p1c"])
    q.set_defaults(fn=cmd_run_cells)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("finalize").set_defaults(fn=cmd_finalize)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    a = ap.parse_args(argv)
    return a.fn(a)


def cmd_selftest(_):
    return _selftest()


if __name__ == "__main__":
    sys.exit(main())