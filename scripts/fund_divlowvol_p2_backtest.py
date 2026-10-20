"""FUND-DIVLOWVOL-P2 runner -- dividend low-vol REVIVAL batch.

Prereg: research/FUND-DIVLOWVOL-P2.md (freeze window r1038-r1068, bm-b).
Authorization: O-20261019-2230-bm-b sec.2.1 (CEO negative-line revival,
three-piece law: authorization + new prereg + new evidence).

This file only IMPLEMENTS prereg numbers; it never re-states a threshold.
Derive kernels (ttm_cash_sum / sidecar_f_at / quality PIT) are imported from
the probe modules -- single source, zero re-implementation. The universe /
signal skeleton is P1's own code, reused by binding the P1 module globals to
this run's panel (F1._G), so the family skeleton cannot drift.

Judged cell table (prereg sec.3, N_eff 2,018 = 18 strategy cells + 2,000 nulls):
  main  ........ TN20 x face x1,x2              (quality ON, vol_frac 0.5)
  neighbourhood  TN{10,15,25,30} x face x1,x2   (8)
  ablation  .... VOL100-N20 x face x1,x2        (vol_frac 1.0, quality ON)
  exit axis .... HARD15 / HARD20 / TRAIL12 x face x1,x2  (6)
Quality filter (leg 1) is ON for every strategy cell except the declared
ablation face (which ablates the LOW-VOL screen, not quality).

Exit axis (leg 3, prereg sec.3): (1) strategy-owned = monthly rotation
signal_reversal PLUS a stop parameter family; the engine default stack is
disabled through BOTH channels (params + ExitPatch) exactly as P1 r522.
Hold-through is the P1 registered face (0.89) and is NOT re-burned here.

Usage (CWD = repo root):
  python scripts/fund_divlowvol_p2_backtest.py probe
  python scripts/fund_divlowvol_p2_backtest.py cells
  python scripts/fund_divlowvol_p2_backtest.py run --cell TN20 --face x1 --dry-run
  python scripts/fund_divlowvol_p2_backtest.py run --cell TN20 --face x1
  python scripts/fund_divlowvol_p2_backtest.py status
  python scripts/fund_divlowvol_p2_backtest.py finalize
  python scripts/fund_divlowvol_p2_backtest.py selftest
"""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "fund_divlowvol_p2")
CELL_DIR = os.path.join(OUT_DIR, "cells")
PREREG = os.path.join(ROOT, "research", "FUND-DIVLOWVOL-P2.md")
PROBE_RECEIPT = os.path.join(ROOT, "results",
                             "_fund_divlowvol_p2_freeze_probe_local.json")
CUTOFF = pd.Timestamp("2026-09-22")     # prereg sec.2 D2 lockbox (P1 same anchor)
BATCH_NAME = "FUND-DIVLOWVOL-P2"
FAMILY_KEY = "fund_divlowvol_stock_xs"
BATCH_CELLS = 2018                      # prereg sec.0 (18 + 2000)
K_NULLS = 2000
SEED_NULLS = 20_523_000                 # prereg sec.3 rng([20523000, k])
K_SENS = 500
SEED_SENS = 20_523_500
TOPN_MAIN = 20
VOL_FRAC = 0.5
NEIGH_N = (10, 15, 25, 30)
FACES = ("x1", "x2")

# exit axis (leg 3) -- every variant disables the engine default stack
# through BOTH channels; only the declared parameter differs.
BASE_PARAMS = {
    "position_size_pct": 1.0, "max_positions": 1,
    "sizing_mode": "fixed_initial", "report_num_entries": True,
    "take_profit_levels": (),
    "trailing_stop_activate": 1e12,
    "initial_stop": -1.0,
    "time_decay_period": 10 ** 9,
}
EXIT_PATCH_OVERRIDES = {"loss_time_days": 10 ** 9, "global_hard_limit": 10 ** 9}
EXIT_SPECS = {
    "HARD15": {"initial_stop": -0.15},
    "HARD20": {"initial_stop": -0.20},
    "TRAIL12": {"trailing_stop_activate": 0.12, "trailing_lock": 0.08},
}
EXIT_KINDS = ("HARD15", "HARD20", "TRAIL12")


def _cells():
    """The frozen 18 strategy cells -> spec dict."""
    out = {}
    out[f"TN{TOPN_MAIN}"] = {"kind": "main", "N": TOPN_MAIN,
                             "vol_frac": VOL_FRAC, "exit": None}
    for n in NEIGH_N:
        out[f"TN{n}"] = {"kind": "neighbour", "N": n,
                         "vol_frac": VOL_FRAC, "exit": None}
    out[f"VOL100-N{TOPN_MAIN}"] = {"kind": "ablation", "N": TOPN_MAIN,
                                   "vol_frac": 1.0, "exit": None}
    for k in EXIT_KINDS:
        out[f"EXIT-{k}"] = {"kind": "exit", "N": TOPN_MAIN,
                            "vol_frac": VOL_FRAC, "exit": k}
    return out


CELLS = _cells()

_G = {}


def _now_iso():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def _log(msg):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "runner.log"), "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


# ------------------------------------------------------------------ data faces

def _init(basis="auto"):
    """Load the panel + rebind the P1 family skeleton to it (single source)."""
    if _G.get("ready"):
        return _G
    import fund_divlowvol_p2_probe as P2
    import fund_divlowvol_p1 as F1

    panel = P2._load_panel(basis)
    if isinstance(panel, Exception):
        raise RuntimeError(f"panel unavailable: {panel!r}")
    idx, syms, meta, close_q, pct, amt, volm = panel
    if isinstance(idx, np.ndarray):
        idx = pd.to_datetime(idx)

    def _mm(name):
        for cand in (os.path.join(P2.LOCAL_CACHE, name + ".npy"),):
            if os.path.exists(cand):
                return np.load(cand, mmap_mode="r")
        import p1c_stock_ic_batch as P1C
        return np.load(os.path.join(P1C.CACHE_DIR, name + ".npy"),
                       mmap_mode="r")

    open_np, high_np, low_np = _mm("open"), _mm("high"), _mm("low")
    close_np = close_q
    first_valid = np.argmax(np.isfinite(np.asarray(close_np[:])), axis=0)
    codes_arr = np.array([str(s) for s in syms])
    static_thr = np.where(np.array([s.startswith("68") for s in syms]),
                          0.20, 0.10).astype(np.float32)
    is_cx = np.array([s.startswith("30") for s in syms])
    by_sym = P2._load_div_by_sym()
    sidecars = P2._load_sidecars(by_sym.keys())
    _, qmap = P2._load_quality()

    G = F1._G
    G.clear()
    G.update(idx=idx, syms=syms, codes_arr=codes_arr, first_valid=first_valid,
             static_thr=static_thr, is_cx=is_cx,
             close_np=close_np, open_np=open_np, high_np=high_np,
             low_np=low_np, volume_np=volm, amount_np=amt, pct_np=pct,
             by_sym=by_sym, sidecars=sidecars,
             month_pos=F1.enumerate_starts_monthly(idx, close_np),
             regime=None)
    _G.update(ready=True, basis=P2.PANEL_BASIS.get("basis"),
              idx=idx, syms=syms, codes_arr=codes_arr, qmap=qmap,
              close_np=close_np,
              cut_pos=int(np.max(np.where(idx <= CUTOFF)[0])))
    _log(f"init basis={_G['basis']} bars={len(idx)} syms={len(syms)} "
         f"cut_pos={_G['cut_pos']} months={len(G['month_pos'])}")
    return _G


def _quality_mask(t_int, j_arr):
    """PIT quality filter (leg 1): latest period_end with avail_date<=t and
    roe_q>0. No available period = honest exclusion."""
    import fund_divlowvol_p2_probe as P2
    qmap = _G["qmap"]
    codes = _G["codes_arr"]
    out = np.zeros(len(j_arr), dtype=bool)
    for i, j in enumerate(j_arr):
        pack = qmap.get(str(codes[j]))
        if pack is None:
            continue
        out[i] = P2.quality_pass(pack[0], pack[1], t_int)
    return out


def cell_picks(name):
    """Monthly (pos, end, picks, weight) for one frozen cell."""
    import fund_divlowvol_p1 as F1
    cache = _G.setdefault("_picks", {})
    if name in cache:
        return cache[name]
    spec = CELLS[name]
    codes = _G["codes_arr"]
    picks = []
    for (m, end) in F1._firing_months():
        u = F1._month_universe(m)
        pj, vals = F1._pick_j(u, spec["vol_frac"])
        if len(pj):
            keep = _quality_mask(u["t_int"], pj)
            pj, vals = pj[keep], vals[keep]
        if len(pj):
            order = np.lexsort((codes[pj], -vals))
            top = pj[order[:min(spec["N"], len(pj))]]
        else:
            top = pj
        picks.append((m, end, top, 1.0 / max(1, len(top))))
    cache[name] = picks
    return picks


def cell_spans(name):
    import fund_divlowvol_p1 as F1
    return F1._spans_from_picks(cell_picks(name))


# ------------------------------------------------------------- engine face

def run_cell(spans, face, lo, hi, exit_kind=None):
    """Engine-canonical burn over [lo..hi]; P1's per-symbol span-sliced
    sub-account decomposition verbatim, only the exit parameter face differs."""
    import fund_divlowvol_p1 as F1
    from engine import run_backtest
    from contextlib import nullcontext
    from live.paper import ExitPatch
    from science_gates import CostPatch

    params = dict(BASE_PARAMS)
    if exit_kind:
        params.update(EXIT_SPECS[exit_kind])
    idx = _G["idx"]
    syms = _G["syms"]
    win_idx = idx[lo:hi + 1]
    pnl = None
    n_trades = n_entries = 0
    reasons = Counter()
    for j in sorted(spans):
        sp = spans[j]
        e_lo = max(sp[0][0] - 2, lo)
        e_hi = min(sp[-1][1] + 2, hi)
        if e_hi < e_lo:
            continue
        sym = syms[j]
        ent, scale = F1._sym_arrays(j, sp)
        ent_df = pd.DataFrame({sym: pd.Series(ent, index=idx)})
        frame = F1._sym_frame(j, e_lo, e_hi)
        with ExitPatch(EXIT_PATCH_OVERRIDES), \
             (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest({sym: frame}, dict(params),
                               entry_signal=ent_df,
                               exit_signal=ent_df <= 0,
                               entry_size_scale=scale)
        eq = pd.Series(res["equity_curve"],
                       index=frame.index[:len(res["equity_curve"])])
        p = (eq - F1.CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        for tr in res["trades"]:
            reasons[str(tr.get("reason", tr.get("exit_reason", "na")))] += 1
    if pnl is None:
        return None
    nav = (pnl + F1.CAPITAL).reindex(win_idx).ffill().fillna(F1.CAPITAL)
    return {"nav": nav, "n_trades": n_trades, "n_entries": n_entries,
            "exit_reasons": dict(reasons)}


def _metrics(nav):
    rets = nav.pct_change().dropna()
    if len(rets) < 30 or float(rets.std(ddof=1)) == 0:
        return {"n_days": int(len(rets)), "sharpe_ann": None,
                "ann_ret": None, "max_dd": None, "total_ret": None}
    mu, sd = float(rets.mean()), float(rets.std(ddof=1))
    sharpe = mu / sd * np.sqrt(252.0)
    ann = (1.0 + mu) ** 252 - 1.0
    peak = nav.cummax()
    mdd = float((nav / peak - 1.0).min())
    return {"n_days": int(len(rets)), "sharpe_ann": round(sharpe, 6),
            "ann_ret": round(ann, 6), "max_dd": round(mdd, 6),
            "total_ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1.0), 6)}


# ------------------------------------------------------------------ commands

def cmd_probe(_):
    import fund_divlowvol_p2_probe as P2
    gates = {}
    ok = True
    if not os.path.exists(PREREG):
        gates["prereg"] = "MISSING"
        ok = False
    else:
        gate_txt = open(PREREG, encoding="utf-8").read()
        frozen = "DRAFT-NOT-FROZEN" not in gate_txt.split("\n")[0]
        gates["prereg"] = "FROZEN" if frozen else "DRAFT-NOT-FROZEN"
        ok = ok and frozen
    rc = P2.main("auto")
    gates["probe_legs"] = {0: "GREEN", 4: "AWAITING_PANEL"}.get(rc, f"rc{rc}")
    ok = ok and rc == 0
    q = os.path.join(OUT_DIR, "quality_faces.parquet")
    gates["quality_faces"] = "LOCAL" if os.path.exists(
        os.path.join(ROOT, "data", "fund_history_export",
                     "quality_faces.parquet")) else "MISSING"
    payload = {"batch": BATCH_NAME, "ok": bool(ok), "gates": gates,
               "ts": _now_iso(), "receipt": PROBE_RECEIPT}
    _dump(payload, os.path.join(OUT_DIR, "probe.json"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if ok else 4


def cmd_cells(_):
    rows = [{"cell": k, **v} for k, v in sorted(CELLS.items())]
    for r in rows:
        r["cell_faces"] = list(FACES)
    print(json.dumps({"n_cells": len(rows), "cell_faces": len(rows) * 2,
                      "nulls": K_NULLS, "n_eff": BATCH_CELLS,
                      "rows": rows}, ensure_ascii=False, indent=2))
    return 0


def cmd_run(args):
    _init(args.basis)
    if args.cell not in CELLS:
        print(f"unknown cell {args.cell}; known={sorted(CELLS)}", file=sys.stderr)
        return 2
    spec = CELLS[args.cell]
    t0 = _G["idx"][_G["cut_pos"]]
    lo = None
    import fund_divlowvol_p1 as F1
    F1._firing_months()
    lo = int(F1._G["_t0_pos"])
    hi = int(_G["cut_pos"])
    spans = cell_spans(args.cell)
    path = os.path.join(CELL_DIR, f"{args.cell}__{args.face}.json")

    if args.dry_run:
        per_month = [len(top) for (_, _, top, _) in cell_picks(args.cell)]
        p1 = F1._cell_picks("yieldvol", spec["N"], spec["vol_frac"])
        own = cell_picks(args.cell)
        ovl = [len(set(map(int, o[2])) & set(map(int, q[2])))
               / max(1, len(o[2])) for o, q in zip(own, p1)]
        last_p1 = p1[-1][2] if p1 else np.array([], dtype=int)
        last_own = own[-1][2]
        overlap = (len(set(map(int, last_own)) & set(map(int, last_p1)))
                   / max(1, len(last_own)))
        payload = {
            "batch": BATCH_NAME, "cell": args.cell, "face": args.face,
            "mode": "dry-run", "basis": _G["basis"],
            "t0": str(_G["idx"][lo].date()), "window_end": str(t0.date()),
            "n_firing_months": len(own),
            "pick_size_min": min(per_month) if per_month else 0,
            "pick_size_max": max(per_month) if per_month else 0,
            "n_symbols_touched": len(spans),
            "overlap_vs_p1_mean": round(float(np.mean(ovl)), 4) if ovl else None,
            "overlap_vs_p1_last": round(float(overlap), 4),
            "exit_face": spec["exit"] or "signal_reversal_only",
            "evidence_cutoff": str(CUTOFF.date()), "ts": _now_iso(),
        }
        _dump(payload, path)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0

    run = run_cell(spans, args.face, lo, hi, spec["exit"])
    if run is None:
        print("no spans -- nothing burned", file=sys.stderr)
        return 2
    m = _metrics(run["nav"])
    payload = {
        "batch": BATCH_NAME, "cell": args.cell, "face": args.face,
        "basis": _G["basis"], "spec": spec,
        "window": [str(_G["idx"][lo].date()), str(t0.date())],
        "metrics": m, "n_trades": run["n_trades"],
        "n_entries": run["n_entries"],
        "exit_reasons": run["exit_reasons"],
        "default_stack_share": round(
            sum(v for k, v in run["exit_reasons"].items()
                if k != "signal_reversal") / max(1, run["n_trades"]), 6),
        "evidence_cutoff": str(CUTOFF.date()), "ts": _now_iso(),
    }
    _dump(payload, path)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_status(_):
    done = {}
    if os.path.isdir(CELL_DIR):
        for fn in sorted(os.listdir(CELL_DIR)):
            if not fn.endswith(".json"):
                continue
            try:
                d = json.load(open(os.path.join(CELL_DIR, fn), encoding="utf-8"))
            except Exception:
                continue
            done[fn[:-5]] = d.get("metrics") or {"mode": d.get("mode")}
    want = [f"{c}__{f}" for c in CELLS for f in FACES]
    print(json.dumps({"want": len(want), "done": len(done),
                      "missing": [w for w in want if w not in done],
                      "cells": done}, ensure_ascii=False, indent=2))
    return 0


def cmd_finalize(_):
    from science_gates import cutoff_meta, g1_prime_v2
    rows = {}
    if os.path.isdir(CELL_DIR):
        for fn in sorted(os.listdir(CELL_DIR)):
            if fn.endswith(".json"):
                d = json.load(open(os.path.join(CELL_DIR, fn), encoding="utf-8"))
                rows[fn[:-5]] = d
    burns = {k: v for k, v in rows.items() if v.get("mode") != "dry-run"}
    head = burns.get(f"TN{TOPN_MAIN}__x1")
    g1 = None
    if head and head.get("metrics", {}).get("sharpe_ann") is not None:
        g1 = g1_prime_v2(head["metrics"]["sharpe_ann"], [],
                         BATCH_CELLS, n_trades=head.get("n_trades"),
                         n_entries=head.get("n_entries"))
    payload = {
        "batch": BATCH_NAME, "family_key": FAMILY_KEY,
        "n_eff": BATCH_CELLS, "nulls": K_NULLS, "sens": K_SENS,
        "cells_burned": len(burns), "cells_expected": len(CELLS) * len(FACES),
        "headline_cell": f"TN{TOPN_MAIN}__x1",
        "g1_prime_v2": g1,
        "verdict_note": ("judged face incomplete" if not g1 else
                         "g1 computed on headline cell; registration columns "
                         "require the batch null family"),
        "rows": {k: {"metrics": v.get("metrics"),
                     "n_trades": v.get("n_trades"),
                     "default_stack_share": v.get("default_stack_share")}
                 for k, v in sorted(burns.items())},
        **cutoff_meta(CUTOFF.date()), "ts": _now_iso(),
    }
    out = os.path.join(OUT_DIR, "fund_divlowvol_p2_results.json")
    _dump(payload, out)
    print(json.dumps({k: payload[k] for k in
                      ("cells_burned", "cells_expected", "g1_prime_v2",
                       "evidence_cutoff")}, ensure_ascii=False, sort_keys=True))
    return 0


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "pass": bool(cond), "detail": detail})

    cells = _cells()
    # 9 distinct cells x 2 cost faces = the 18 judged strategy cell-faces
    leg("L1_cell_faces_18", len(cells) == 9 and len(cells) * 2 == 18,
        f"cells={len(cells)} faces={len(cells) * 2}")
    leg("L2_n_eff_2018", len(cells) * 2 + K_NULLS == BATCH_CELLS, BATCH_CELLS)
    leg("L3_faces_2", tuple(FACES) == ("x1", "x2"))
    kinds = Counter(v["kind"] for v in cells.values())
    leg("L4_kind_mix", kinds == {"main": 1, "neighbour": 4,
                                 "ablation": 1, "exit": 3}, dict(kinds))
    leg("L5_neigh_set", tuple(NEIGH_N) == (10, 15, 25, 30))
    leg("L6_ablation_vol1", cells[f"VOL100-N{TOPN_MAIN}"]["vol_frac"] == 1.0)
    leg("L7_exit_cells_share_topn",
        all(cells[f"EXIT-{k}"]["N"] == TOPN_MAIN for k in EXIT_KINDS))
    # every exit variant keeps the default stack dead through BOTH channels
    ok_exit = True
    for k in EXIT_KINDS:
        p = dict(BASE_PARAMS, **EXIT_SPECS[k])
        ok_exit &= p["take_profit_levels"] == () and p["time_decay_period"] >= 10 ** 9
        ok_exit &= EXIT_PATCH_OVERRIDES["loss_time_days"] >= 10 ** 9
        ok_exit &= EXIT_PATCH_OVERRIDES["global_hard_limit"] >= 10 ** 9
    leg("L8_default_stack_disabled", ok_exit)
    leg("L9_hard_stops_declared",
        EXIT_SPECS["HARD15"]["initial_stop"] == -0.15
        and EXIT_SPECS["HARD20"]["initial_stop"] == -0.20)
    leg("L10_trail_12_8",
        EXIT_SPECS["TRAIL12"]["trailing_stop_activate"] == 0.12
        and EXIT_SPECS["TRAIL12"]["trailing_lock"] == 0.08)
    leg("L11_seeds_distinct", SEED_NULLS != SEED_SENS, f"{SEED_NULLS}/{SEED_SENS}")
    # quality PIT kernel (probe single source)
    import fund_divlowvol_p2_probe as P2
    av = np.array([20200101, 20200401, 20200701], dtype=np.int64)
    roe = np.array([0.05, -0.02, 0.03])
    leg("L12_quality_pass_pos", P2.quality_pass(av, roe, 20200201) is True)
    leg("L13_quality_pass_neg", P2.quality_pass(av, roe, 20200501) is False)
    leg("L14_quality_no_period", P2.quality_pass(av, roe, 20190101) is False)
    leg("L15_quality_latest_wins", P2.quality_pass(av, roe, 20200801) is True)
    # metrics kernel (synthetic constant NAV -> degenerate guarded)
    nav = pd.Series(np.linspace(1e6, 1.1e6, 60))
    m = _metrics(nav)
    leg("L16_metrics_ann_ret_positive", (m["ann_ret"] or 0) > 0, m["ann_ret"])
    leg("L17_metrics_max_dd_nonpos", (m["max_dd"] or 0) <= 0, m["max_dd"])
    flat = _metrics(pd.Series([1e6] * 60))
    leg("L18_metrics_flat_degenerate", flat["sharpe_ann"] is None)
    # cell naming bijection
    names = set(cells)
    leg("L19_names_unique", len(names) == 9)
    leg("L20_main_cell_name", f"TN{TOPN_MAIN}" in cells and "TN20" in cells)
    ok = all(x["pass"] for x in legs)
    print(json.dumps({"selftest": "PASS" if ok else "FAIL",
                      "legs": legs, "n": len(legs)},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe").set_defaults(fn=cmd_probe)
    sub.add_parser("cells").set_defaults(fn=cmd_cells)
    p = sub.add_parser("run")
    p.add_argument("--cell", required=True)
    p.add_argument("--face", default="x1", choices=list(FACES))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--basis", default="auto", choices=["auto", "local", "p1c"])
    p.set_defaults(fn=cmd_run)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("finalize").set_defaults(fn=cmd_finalize)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    a = ap.parse_args(argv)
    return a.fn(a)


def cmd_selftest(_):
    return _selftest()


if __name__ == "__main__":
    sys.exit(main())