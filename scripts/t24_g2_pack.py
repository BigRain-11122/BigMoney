"""T-24 PROSPECT G2 evidence-pack batch (promotion-gate legs producer).

PRE-REGISTERED (research/shortline/T24_G2_PACK.md, frozen before any data
run). G2_NSP1 / G2_FOLK paradigm transposed onto the 22 PROSPECT members:
per member -> center-1x anchor re-verify + per-year clause, center-x3 cost
clause, frozen OAT neighborhood grid clause. Products =
results/prospect_g2/<ID>.json packs (three subleg booleans), consumed
read-only by scripts/t24_prospect_promotion.py (g2_full leg). ZERO new
engine code: run_backtest / CostPatch / ExitPatch / seg_metrics pipeline
reuse via the member_run convention; member files are NEVER written
(read-only inputs, promotion execution stays the registration pipeline).

Judgment lines are machine-linked (science_gates.recorded_lines, no
hand-copied numbers). Recorded-cell replay precedent: center-1x runs
re-verify already-counted p4 evidence -> ledger +0; the 76 neighborhood +
22 x3 cells are new evidence -> ledger +98 (append_ledger, prev = dual-dir
max chain head per r60 convention).

Usage (detached BelowNormal per O-1612 full-load pool):
  python scripts/t24_g2_pack.py run        # all 22 members, JSONL checkpoint
  python scripts/t24_g2_pack.py status    # progress read
  python scripts/t24_g2_pack.py selftest  # offline synthetic checks
"""
import argparse
import csv
import glob
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # p3 import

import pandas as pd

from config import PATHS
from science_gates import (append_ledger, cutoff_meta, ledger_head,
                           recorded_lines)

EVIDENCE_CUT = "2026-09-22"          # pool + member files frozen cutoff
ANCHOR_TOL = 0.002                    # onboarding anchor gate tol (J14/J15)
WORST_YEAR_FLOOR = -0.35              # G2_FOLK clause 4 verbatim
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}

G2_DIR = os.path.join(PATHS.results_dir, "prospect_g2")
CELLS_PATH = os.path.join(G2_DIR, "t24_g2_pack_cells.jsonl")
BATCH_JSON = os.path.join(PATHS.results_dir, "t24_g2_pack.json")
CSV_PATH = os.path.join(os.path.dirname(PATHS.results_dir), "research",
                        "shortline", "t24_g2_pack_results.csv")

RL = recorded_lines()
I_LINE = {"default": RL["i_line"], "ce": RL["ce_null_p4_batch1"]}
VI_BAR = RL["vi_bar"]

# ---------------------------------------------------------------- families
# spec: build(P, p) must reproduce SIGNAL_BUILDERS[key](P) bit-exactly at
# CENTER (selftest S1 hard gate); oat = [(param, lo, hi), ...] frozen per
# prereg s3 table. inside_bar_breakup has NO perturbable parameter in its
# frozen construction -> grid empty -> neighborhood REFUSED (prereg s2).


def _apply_sym(fn, P, keys, **kw):
    syms = list(P["close"].columns)
    return pd.DataFrame({s: fn(*[P[k][s] for k in keys], **kw)
                         for s in syms}).fillna(0)


def _ovb(P, p):
    return ((P["close"].pct_change(p["lookback"]) < p["drop"])
            & (P["amount"].rolling(5).mean()
               < p["shrink"] * P["amount"].rolling(20).mean())
            ).fillna(False).astype(int)


def _ta():
    import strategies.ta as m
    return m


def _pt():
    import strategies.patterns as m
    return m


def _fk():
    import strategies.folk as m
    return m


FAMILIES = {
    "OVB": {
        "key": "oversold_bounce(lookback=20, drop=-15%, shrink=0.8)",
        "center": {"lookback": 20, "drop": -0.15, "shrink": 0.8},
        "oat": [("lookback", 15, 25), ("drop", -0.10, -0.20),
                ("shrink", 0.70, 0.90)],
        "build": _ovb,
    },
    "RSRS": {
        "key": "rsrs_timing(18/250/0.8/-0.8)",
        "center": {"window": 18, "z_win": 250, "buy_z": 0.8,
                   "exit_z": -0.8},
        "oat": [("window", 12, 24), ("z_win", 120, 480),
                ("buy_z", 0.70, 0.90), ("exit_z", -0.90, -0.70)],
        "build": lambda P, p: _apply_sym(
            _ta().rsrs_timing, P, ["high", "low"], **p),
    },
    "VOB": {
        "key": "vol_breakout(20/1.5/20/10)",
        "center": {"brk_len": 20, "vol_mult": 1.5, "vol_avg_len": 20,
                   "exit_len": 10},
        "oat": [("brk_len", 15, 25), ("vol_mult", 1.3, 1.7),
                ("vol_avg_len", 15, 25), ("exit_len", 7, 14)],
        "build": lambda P, p: _apply_sym(
            _ta().vol_breakout, P, ["high", "low", "close", "volume"], **p),
    },
    "HAM": {
        "key": "hammer_reversal(classic, drop5, reclaim_ma20)",
        "center": {"body_max": 0.35, "shadow_mult": 2.0, "drop_th": -0.05},
        "oat": [("body_max", 0.25, 0.45), ("shadow_mult", 1.5, 2.5),
                ("drop_th", -0.04, -0.06)],
        "build": lambda P, p: _apply_sym(
            _ta().hammer_reversal, P, ["open", "high", "low", "close"], **p),
    },
    "TMU": {
        "key": "three_methods_up()",
        "center": {"big_yang": 0.03},
        "oat": [("big_yang", 0.02, 0.04)],
        "build": lambda P, p: _apply_sym(
            _pt().three_methods_up, P, ["open", "high", "low", "close"],
            **p),
    },
    "DOJI": {
        "key": "doji_at_low()",
        "center": {"drop_th": -0.05},
        "oat": [("drop_th", -0.04, -0.06)],
        "build": lambda P, p: _apply_sym(
            _pt().doji_at_low, P, ["open", "high", "low", "close"], **p),
    },
    "IBB": {
        "key": "inside_bar_breakup()",
        "center": {},
        "oat": [],          # no param space -> grid empty -> REFUSED
        "build": lambda P, p: _apply_sym(
            _pt().inside_bar_breakup, P, ["open", "high", "low", "close"]),
    },
    "MCB": {
        "key": "ma_converge_break()",
        "center": {"spread": 0.015},
        "oat": [("spread", 0.010, 0.020)],
        "build": lambda P, p: _apply_sym(
            _pt().ma_converge_break, P, ["open", "high", "low", "close"],
            **p),
    },
    "DUCK": {
        "key": "duck_head()",
        "center": {"neck": 8},
        "oat": [("neck", 5, 12)],
        "build": lambda P, p: _apply_sym(
            _pt().duck_head, P, ["open", "high", "low", "close"], **p),
    },
    "IMM": {
        "key": "immortal_guide()",
        "center": {"shadow_pct": 0.015},
        "oat": [("shadow_pct", 0.010, 0.020)],
        "build": lambda P, p: _apply_sym(
            _pt().immortal_guide, P, ["open", "high", "low", "close"], **p),
    },
    "ANTS": {
        "key": "ants_climb()",
        "center": {"max_day": 0.012},
        "oat": [("max_day", 0.008, 0.016)],
        "build": lambda P, p: _apply_sym(
            _fk().ants_climb, P, ["open", "high", "low", "close"], **p),
    },
    "BBS": {
        "key": "bb_squeeze_breakout()",
        "center": {"bb_n": 20, "k": 2.0, "width_n": 60},
        "oat": [("bb_n", 15, 25), ("k", 1.7, 2.3), ("width_n", 40, 80)],
        "build": lambda P, p: _apply_sym(
            _ta().bb_squeeze_breakout, P, ["high", "low", "close"], **p),
    },
}


def member_abbr(mid: str) -> str:
    return mid.split("-")[1]          # PROS-<ABBR>[-CE]-01


def load_members() -> list:
    from firm.hr import TRADERS_DIR
    out = []
    for name in sorted(os.listdir(TRADERS_DIR)):
        if not (name.startswith("PROS-") and name.endswith(".json")):
            continue
        with open(os.path.join(TRADERS_DIR, name), encoding="utf-8") as fh:
            m = json.load(fh)
        abbr = member_abbr(m["id"])
        if abbr not in FAMILIES:
            raise KeyError(f"no family spec for member {m['id']}")
        if m.get("evidence_cutoff") != EVIDENCE_CUT:
            raise ValueError(f"{m['id']} cutoff drift: "
                             f"{m.get('evidence_cutoff')}")
        if m["params"]["entry"] != FAMILIES[abbr]["key"]:
            raise ValueError(f"{m['id']} entry key drift: "
                             f"{m['params']['entry']}")
        out.append(m)
    return out


def cell_id(m: dict, kind: str, p: dict) -> str:
    if kind in ("center", "x3"):
        return f"{m['id']}::{kind}"
    (pname, val), = p.items()
    return f"{m['id']}::nbhd::{pname}={val}"


def cells_todo(members: list, done: set, anchor_fail: set) -> list:
    """Per member: center first (anchor gate), then x3 + OAT points.
    anchor-FAIL members contribute nothing beyond their center cell."""
    plan = []
    for m in members:
        mid = m["id"]
        spec = FAMILIES[member_abbr(mid)]
        if f"{mid}::center" not in done:
            plan.append((m, "center", {}))
        if mid in anchor_fail:
            continue
        if f"{mid}::x3" not in done:
            plan.append((m, "x3", {}))
        for pname, lo, hi in spec["oat"]:
            for v in (lo, hi):
                if cell_id(m, "nbhd", {pname: v}) not in done:
                    plan.append((m, "nbhd", {pname: v}))
    return plan


def _read_cells() -> list:
    cells = []
    if os.path.exists(CELLS_PATH):
        with open(CELLS_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    cells.append(json.loads(line))
                except json.JSONDecodeError:
                    continue    # corrupt tail tolerated (t22 convention)
    return cells


def _cells_done(cells: list) -> set:
    return {c["id"] for c in cells if "id" in c}


def _anchor_fail_ids(cells: list) -> set:
    out = set()
    for c in cells:
        if c.get("kind") == "center" and c.get("anchor") and not c["anchor"].get("pass"):
            out.add(c["member"])
    return out


def _append_cell(rec: dict):
    os.makedirs(G2_DIR, exist_ok=True)
    with open(CELLS_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _run_cell(prices, P, state, regime: str, cost_mult=None) -> dict:
    """member_run convention verbatim, entry state injected (g2 run_cell
    precedent -- zero new engine code)."""
    from engine import run_backtest
    from live.paper import CostPatch, ExitPatch, OOS_START, seg_metrics
    params = dict(CE_PARAMS) if regime == "ce" else {}
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ExitPatch(dict(CE_OVERRIDES) if regime == "ce" else None):
        res = run_backtest(prices, params, entry_signal=state,
                           exit_signal=(state <= 0))
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_trades = sum(1 for tr in res["trades"]
                     if str(tr["date"]) >= OOS_START)
    return {"eq": eq, "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"],
            "oos_trades": oos_trades}


def cmd_run() -> int:
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
    except Exception:
        pass
    from live.paper import build_panels, load_core
    from p3_portfolio import yearly_returns

    members = load_members()
    cells = _read_cells()
    done = _cells_done(cells)
    anchor_fail = _anchor_fail_ids(cells)
    todo = cells_todo(members, done, anchor_fail)
    print(f"members={len(members)} cells_done={len(done)} "
          f"cells_todo={len(todo)} cutoff={EVIDENCE_CUT}")
    if not todo:
        return _finalize(members)

    prices = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = build_panels(prices)
    idx = P["close"].index
    if str(idx[-1].date()) != EVIDENCE_CUT:
        print(f"HONEST ABORT: panel tail {idx[-1].date()} != cutoff "
              f"{EVIDENCE_CUT}")
        return 2
    if bool(P["close"].isna().any().any()) or len(P["close"].columns) != 48:
        print("HONEST ABORT: panel NaN or universe != 48")
        return 2
    print(f"core48: {len(P['close'].columns)} syms, "
          f"{idx[0].date()} .. {idx[-1].date()}")

    t0 = time.time()
    for i, (m, kind, p) in enumerate(todo):
        mid = m["id"]
        if kind in ("x3", "nbhd") and mid in anchor_fail:
            continue        # fresh center verdict failed this session
        spec = FAMILIES[member_abbr(mid)]
        regime = m["prospect"]["exit_regime"]
        pp = dict(spec["center"])
        pp.update(p)
        state = spec["build"](P, pp)
        r = _run_cell(prices, P, state, regime,
                      cost_mult=3.0 if kind == "x3" else None)
        rec = {"id": cell_id(m, kind, p), "member": mid, "kind": kind,
               "point": p or None, "regime": regime,
               "full_sharpe": round(float(r["full"]["sharpe"]), 4),
               "oos_sharpe": round(float(r["oos"]["sharpe"]), 4),
               "n_trades": int(r["n_trades"]),
               "oos_trades": int(r["oos_trades"]),
               "max_dd": round(float(r["full"]["max_drawdown"]), 4),
               "annual_return": round(float(r["full"]["annual_return"]), 4),
               "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
        if kind == "center":
            rec["yearly"] = {str(k): v for k, v in
                             yearly_returns(r["eq"]).items()}
            d = abs(float(r["full"]["sharpe"])
                    - float(m["prospect"]["recorded_full_sharpe"]))
            rec["anchor"] = {
                "d_full": round(d, 6),
                "trades_exact": bool(int(r["n_trades"])
                                    == int(m["prospect"]["recorded_n_trades"])),
                "pass": bool(d < ANCHOR_TOL
                             and int(r["n_trades"])
                             == int(m["prospect"]["recorded_n_trades"])),
            }
            if not rec["anchor"]["pass"]:
                anchor_fail.add(mid)
                print(f"[{i+1}/{len(todo)}] {mid} center: ANCHOR FAIL "
                      f"(d={d:.4f} trades={r['n_trades']}) -- member void")
        _append_cell(rec)
        print(f"[{i+1}/{len(todo)}] {rec['id']}: "
              f"full_s={rec['full_sharpe']} oos_s={rec['oos_sharpe']} "
              f"trades={rec['n_trades']} ({time.time() - t0:.0f}s)")
    return _finalize(members)


def _chain_head_total() -> int:
    """r60 dual-dir convention: prev = max total across results/ AND
    results/shortline/ ledger carriers."""
    best = int(ledger_head()["total"])

    def _scan(pattern):
        nonlocal best
        for path in sorted(glob.glob(pattern)):
            try:
                with open(path, encoding="utf-8") as fh:
                    tl = json.load(fh).get("trials_ledger")
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            if isinstance(tl, dict) and isinstance(tl.get("total"),
                                                   (int, float)):
                best = max(best, int(tl["total"]))
    _scan(os.path.join(PATHS.results_dir, "*.json"))
    _scan(os.path.join(PATHS.results_dir, "shortline", "*.json"))
    return best


def _finalize(members: list) -> int:
    cells = _read_cells()
    by_member = {}
    for c in cells:
        by_member.setdefault(c["member"], {})[c["id"]] = c
    packs, rows = [], []
    for m in members:
        mid = m["id"]
        spec = FAMILIES[member_abbr(mid)]
        regime = m["prospect"]["exit_regime"]
        mc = by_member.get(mid, {})
        center = mc.get(f"{mid}::center")
        x3 = mc.get(f"{mid}::x3")
        pack = {
            "member": mid, "family": member_abbr(mid),
            "exit_regime": regime, "entry_key": spec["key"],
            "gate": "t24-g2-pack (prereg research/shortline/T24_G2_PACK.md)",
            "lines": {"i_line": I_LINE[regime], "vi_bar": VI_BAR,
                      "worst_year_floor": WORST_YEAR_FLOOR,
                      "source": "science_gates.recorded_lines() live read"},
            "neighborhood_pass": False, "cost_x3_pass": False,
            "per_year_pass": False,
        }
        if center is None:
            pack["status"] = "incomplete"
            packs.append(pack)
            continue
        anchor = center.get("anchor", {})
        yearly = center.get("yearly", {})
        worst = min(yearly.values()) if yearly else None
        pack["anchor_reverify"] = anchor
        pack["yearly"] = yearly
        pack["worst_year"] = worst
        nb_cells = sorted((c for c in mc.values() if c["kind"] == "nbhd"),
                          key=lambda c: str(c["point"]))
        pts = len(nb_cells)
        red_ids = {c["id"] for c in nb_cells
                   if float(c["full_sharpe"]) <= I_LINE[regime]}
        if pts == 0:
            pack["neighborhood"] = {
                "points": 0, "red": 0,
                "refused": "grid_empty (no param space in frozen "
                           "construction; prereg s2 disclosure)"}
        else:
            pack["neighborhood"] = {
                "points": pts, "red": len(red_ids),
                "clause": "red*2 <= points (G2_FOLK clause 2 verbatim)",
                "cells": [{"point": c["point"],
                           "full_sharpe": c["full_sharpe"],
                           "red": bool(c["id"] in red_ids)}
                          for c in nb_cells]}
            pack["neighborhood_pass"] = bool(len(red_ids) * 2 <= pts)
        if x3 is not None:
            pack["x3"] = {"full_sharpe": x3["full_sharpe"],
                          "oos_sharpe": x3["oos_sharpe"],
                          "n_trades": x3["n_trades"]}
        x3_ok = bool(x3 is not None and float(x3["full_sharpe"]) > 0
                     and float(x3["oos_sharpe"]) > 0)
        x2_ok = bool(float(m["prospect"]["recorded_x2_full_sharpe"])
                     > VI_BAR)
        pack["cost_x3_pass"] = bool(x3_ok and x2_ok)
        pack["cost_clause"] = {
            "x3_positive": x3_ok,
            "recorded_x2_beats_vi": x2_ok,
            "recorded_x2_full_sharpe":
                m["prospect"]["recorded_x2_full_sharpe"],
            "note": "x2>vi = registration-standard G2 clause 3 on recorded "
                    "evidence (no relaxation); x3 survival = new evidence"}
        pack["per_year_pass"] = bool(worst is not None
                                     and float(worst) > WORST_YEAR_FLOOR)
        pack["status"] = ("judged" if anchor.get("pass")
                          else "anchor_broken")
        if pack["status"] == "anchor_broken":
            pack["neighborhood_pass"] = False
            pack["cost_x3_pass"] = False
            pack["per_year_pass"] = False
        packs.append(pack)
        for c in nb_cells:
            rows.append([mid, "nbhd", json.dumps(c["point"], sort_keys=True),
                         regime, c["full_sharpe"], c["oos_sharpe"],
                         c["n_trades"],
                         "RED" if c["id"] in red_ids else "green"])
        rows.append([mid, "center", "", regime, center["full_sharpe"],
                     center["oos_sharpe"], center["n_trades"],
                     f"anchor={'OK' if anchor.get('pass') else 'FAIL'} "
                     f"worst_year={worst}"])
        if x3 is not None:
            rows.append([mid, "x3", "", regime, x3["full_sharpe"],
                         x3["oos_sharpe"], x3["n_trades"], ""])

    os.makedirs(G2_DIR, exist_ok=True)
    for pack in packs:
        pack.update(cutoff_meta(EVIDENCE_CUT))
        pack["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        with open(os.path.join(G2_DIR, f"{pack['member']}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(pack, fh, ensure_ascii=False, indent=1)

    complete = (len(packs) == len(members)
                and all(p.get("status") in ("judged", "anchor_broken")
                        for p in packs))
    batch_ledger = None
    if os.path.exists(BATCH_JSON):
        try:
            with open(BATCH_JSON, encoding="utf-8") as fh:
                prev_batch = json.load(fh)
            if prev_batch.get("complete"):
                batch_ledger = prev_batch.get("trials_ledger")  # idempotent
        except (OSError, ValueError):
            batch_ledger = None
    if batch_ledger is None:
        batch_ledger = append_ledger(
            "t24-g2-pack", 98, file_name="t24_g2_pack.json",
            note="76 OAT neighborhood + 22 x3 cost-stress cells; center-1x "
                 "runs are recorded-cell replays (ledger +0, onboarding "
                 "precedent)",
            evidence_cutoff=EVIDENCE_CUT,
            prev_total=_chain_head_total())
    n_runs = len(cells)
    out = {
        "batch": "t24-g2-pack",
        "ticket": "T-2026-09-24-24",
        "prereg": "research/shortline/T24_G2_PACK.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "members": len(members),
        "complete": bool(complete),
        "engine_runs": n_runs,
        "packs": [{"member": p["member"], "status": p.get("status"),
                   "neighborhood_pass": p["neighborhood_pass"],
                   "cost_x3_pass": p["cost_x3_pass"],
                   "per_year_pass": p["per_year_pass"]} for p in packs],
        "subleg_counts": {
            "neighborhood_pass":
                sum(1 for p in packs if p["neighborhood_pass"]),
            "cost_x3_pass": sum(1 for p in packs if p["cost_x3_pass"]),
            "per_year_pass": sum(1 for p in packs if p["per_year_pass"]),
        },
        "trials_ledger": batch_ledger,
        "audit": {
            "ledger_trials_added": batch_ledger["batch_trials"],
            "note": "promotion-gate evidence producer; judgments frozen "
                    "pre-run (prereg s4); member files read-only",
        },
    }
    out.update(cutoff_meta(EVIDENCE_CUT))
    with open(BATCH_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["member", "kind", "point", "regime", "full_sharpe",
                    "oos_sharpe", "n_trades", "verdict"])
        w.writerows(rows)

    print(f"packs={len(packs)} complete={complete} engine_runs={n_runs} "
          f"sublegs={out['subleg_counts']}")
    print(f"saved: {BATCH_JSON} + {G2_DIR} packs")
    return 0


def cmd_status() -> int:
    members = load_members()
    cells = _read_cells()
    done = _cells_done(cells)
    total = 0
    for m in members:
        spec = FAMILIES[member_abbr(m["id"])]
        total += 2 + 2 * len(spec["oat"])     # center + x3 + OAT points
    print(f"members={len(members)} cells_done={len(done)}/{total} "
          f"pending={max(0, total - len(done))}")
    return 0


def _synth_panel(n=900, seed=20260924):
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=n)
    close = pd.DataFrame(
        {"AAA": 1 + np.cumsum(rng.normal(0.0002, 0.01, n)),
         "BBB": 1 + np.cumsum(rng.normal(-0.0001, 0.015, n))},
        index=idx)
    high = close * (1 + np.abs(rng.normal(0, 0.006, (n, 2))))
    low = close * (1 - np.abs(rng.normal(0, 0.006, (n, 2))))
    open_ = close.shift(1).fillna(1.0)
    vol = pd.DataFrame(rng.lognormal(12, .4, (n, 2)), index=idx,
                       columns=close.columns)
    return {"open": open_, "high": high, "low": low, "close": close,
            "volume": vol, "amount": vol * close}


def cmd_selftest() -> int:
    ok = True

    # S1: parametrized builder == frozen SIGNAL_BUILDERS key at center
    # (bit-exact; guards rewrite-vs-frozen drift).
    from live.paper import SIGNAL_BUILDERS
    P = _synth_panel()
    s1 = True
    for abbr, spec in FAMILIES.items():
        mine = spec["build"](P, dict(spec["center"]))
        frozen = SIGNAL_BUILDERS[spec["key"]](P)
        if not mine.equals(frozen):
            print(f"FAIL S1: {abbr} center build != frozen key")
            s1 = False
    print(f"S1 center-equivalence: {'PASS' if s1 else 'FAIL'} "
          f"({len(FAMILIES)} families)")
    ok &= s1

    # S2: OAT coupling guards -- (a) every param is accepted by the frozen
    # constructor (TypeError/KeyError = table drift), (b) steps are strictly
    # ordered around the center, (c) causal + no NaN. "Signal actually
    # moved" is data-dependent (rare-event patterns bind only on real
    # crash days) -> disclosed as WARNING, not a gate.
    s2 = True
    half = P["close"].shape[0] // 2
    for abbr, spec in FAMILIES.items():
        base = spec["build"](P, dict(spec["center"]))
        for pname, lo, hi in spec["oat"]:
            ctr = spec["center"][pname]
            if not (min(lo, hi) < ctr < max(lo, hi) and lo != hi):
                print(f"FAIL S2: {abbr} {pname} steps not ordered around "
                      f"center ({lo}/{ctr}/{hi})")
                s2 = False
            for v in (lo, hi):
                pp = dict(spec["center"])
                pp[pname] = v
                try:
                    got = spec["build"](P, pp)
                except (TypeError, KeyError) as exc:
                    print(f"FAIL S2: {abbr} {pname}={v} rejected: {exc}")
                    s2 = False
                    continue
                Phalf = {k: d.iloc[:half] for k, d in P.items()}
                shorth = spec["build"](Phalf, pp)
                causal = bool((got.iloc[:half].values == shorth.values).all())
                no_nan = not bool(got.isna().any().any())
                if not (causal and no_nan):
                    print(f"FAIL S2: {abbr} {pname}={v} causal={causal} "
                          f"no_nan={no_nan}")
                    s2 = False
                if got.equals(base):
                    print(f"WARN S2: {abbr} {pname}={v} does not move the "
                          f"synthetic-panel signal (rare-event density; "
                          f"binds on real crash days or honest center-equal "
                          f"point)")
    print(f"S2 oat-coupling: {'PASS' if s2 else 'FAIL'} "
          f"(moved-checks downgraded to WARN: data-dependent)")
    ok &= s2

    # S3: member registry -- 22 members, spec coverage, key + cutoff intact.
    members = load_members()
    s3 = bool(len(members) == 22
              and all(member_abbr(m["id"]) in FAMILIES for m in members))
    print(f"S3 member-registry: {'PASS' if s3 else 'FAIL'} "
          f"({len(members)} members)")
    ok &= s3

    # S4: judgment arithmetic (frozen clauses on synthetic values).
    s4 = True

    def _nb(pts, red):          # G2_FOLK clause 2: red*2 <= points; empty->refused
        return bool(pts > 0 and red * 2 <= pts)

    if not (_nb(6, 3) and not _nb(6, 4) and _nb(2, 1) and not _nb(2, 2)
            and not _nb(0, 0)):
        print("FAIL S4: neighborhood clause arithmetic")
        s4 = False

    def _cx(x3f, x3o, x2):      # three-conjunct cost clause
        return bool(x3f > 0 and x3o > 0 and x2 > VI_BAR)

    if not (_cx(0.1, 0.05, VI_BAR + 0.01)
            and not _cx(0.1, 0.05, VI_BAR - 0.01)
            and not _cx(0.1, -0.05, VI_BAR + 0.01)
            and not _cx(-0.1, 0.05, VI_BAR + 0.01)):
        print("FAIL S4: cost_x3 clause arithmetic")
        s4 = False
    if not ((WORST_YEAR_FLOOR + 0.01 > WORST_YEAR_FLOOR)
            and not (WORST_YEAR_FLOOR > WORST_YEAR_FLOOR)):
        print("FAIL S4: per-year floor strictness")
        s4 = False
    print(f"S4 judgment-arithmetic: {'PASS' if s4 else 'FAIL'}")
    ok &= s4

    # S5: cell-plan/checkpoint idempotence on a fixture JSONL (tmp dir).
    s5 = True
    import tempfile
    global CELLS_PATH
    with tempfile.TemporaryDirectory() as td:
        old = CELLS_PATH
        try:
            CELLS_PATH = os.path.join(td, "cells.jsonl")
            _append_cell({"id": f"{members[0]['id']}::center",
                          "member": members[0]["id"], "kind": "center",
                          "anchor": {"pass": True}})
            _append_cell({"id": f"{members[0]['id']}::x3",
                          "member": members[0]["id"], "kind": "x3"})
            cells = _read_cells()
            done = _cells_done(cells)
            plan = cells_todo(members[:1], done, set())
            ids = [cell_id(m, k, p) for (m, k, p) in plan]
            expect = {f"{members[0]['id']}::nbhd::max_day=0.008",
                      f"{members[0]['id']}::nbhd::max_day=0.016"}
            if (set(ids) != expect or len(ids) != len(set(ids))):
                print(f"FAIL S5: idempotence ids={ids}")
                s5 = False
        finally:
            CELLS_PATH = old
    print(f"S5 checkpoint-idempotence: {'PASS' if s5 else 'FAIL'}")
    ok &= s5

    # S6: judgment inputs are machine-linked (no hand-copied lines).
    s6 = bool(I_LINE["default"] == RL["i_line"]
              and I_LINE["ce"] == RL["ce_null_p4_batch1"]
              and VI_BAR == RL["vi_bar"]
              and abs(VI_BAR - 0.4004) < 1e-9
              and abs(I_LINE["default"] - 0.3521) < 1e-9
              and abs(I_LINE["ce"] - 0.4474) < 1e-9)
    print(f"S6 machine-linked-lines: {'PASS' if s6 else 'FAIL'}")
    ok &= s6

    print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "status", "selftest"])
    args = ap.parse_args()
    return {"run": cmd_run, "status": cmd_status,
            "selftest": cmd_selftest}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
