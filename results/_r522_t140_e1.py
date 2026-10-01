"""T-140 LOWAMP-P2 E1 known-answer three-leg reconciliation (r492/r301 law).

MUST run BEFORE any P2 verdict number is consumed downstream (watchlist exit,
family meta-conclusions). P2 burned WITH the engine default exit stack
neutralized key-by-key (prereg sec.0.6 HOLD-THROUGH), so the as-burned face
IS the intended ALWAYS-ON face -- legs:

  Leg A  as-burned replay of the headline cell (LA-REP legacy base) through
         the P2 runner's OWN machinery (build_signal + run_cell_portfolio,
         zero reimplementation) reconciled to the recorded cont artifact
         summary + full returns series to the bp.
  Leg A2 exit-reason census per symbol with the frozen neutralized params --
         asserts ZERO default-stack exits fired (neutralization held).
  Leg C  fully independent P1-only arithmetic simulator (no engine on the
         path; T+1 open fills, COST_X1_RATE both ways, 1-day re-entry gap,
         weights set at entry never resized) cross-validating Leg A
         (r301 tolerance: B/C legs <= 5bp/day).

  Verdict-face reconciliation: lowamp_p2_results.json headline block must
  equal the cont_LA-REP_legacy_base artifact summary (the numbers any
  consumer would cite).

Zero network, deterministic, evidence_cutoff 2026-09-22 (runner's own lock).
Evidence: results/lowamp_p2/e1_three_leg.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

import lowamp_p2 as L
from live.paper import build_panels, COST_X1_RATE, ExitPatch

ART = json.load(open(os.path.join(L.OUT_DIR, "cont_LA-REP_legacy_base.json"),
                     encoding="utf-8"))
RESULTS = json.load(open(os.path.join(L.OUT_DIR, "lowamp_p2_results.json"),
                         encoding="utf-8"))

CELL = "LA-REP"
AXIS = "legacy"
FACE = "base"


def leg_a2_reasons(prices, close, entry, weights, active):
    """Per-symbol engine run with the FROZEN neutralized params (verbatim
    from run_cell_portfolio) capturing per-trade exit reasons."""
    from engine import run_backtest
    from contextlib import nullcontext
    params = {"position_size_pct": 1.0, "max_positions": 1,
              "sizing_mode": "fixed_initial", "report_num_entries": True,
              "take_profit_levels": (), "trailing_stop_activate": 1e12,
              "initial_stop": -1.0, "time_decay_period": 10 ** 9,
              "loss_time_days": 10 ** 9, "global_hard_limit": 10 ** 9}
    per_sym, per_trade = {}, []
    for sym in active:
        win = {sym: prices[sym]}
        ent = entry[[sym]]
        sc = L.exec_day_scale(weights, sym)
        with (L.CostPatch(2.0) if FACE == "x2" else nullcontext()):
            res = run_backtest(win, params, entry_signal=ent,
                               exit_signal=ent <= 0, entry_size_scale=sc)
        reasons = {}
        for tr in res["trades"]:
            reasons[tr["reason"]] = reasons.get(tr["reason"], 0) + 1
            per_trade.append({"sym": sym, "reason": tr["reason"],
                              "hold_days": tr["hold_days"]})
        per_sym[sym] = {"n_trades": len(res["trades"]), "reasons": reasons}
    return per_sym, per_trade


def leg_c_independent(prices, close, entry, weights, active):
    """Independent arithmetic simulator -- no engine on the path.
    Semantics mirrored from the frozen engine contract (read-only audit):
    entry signal at close T -> buy at open T+1, budget = 1M x w_s(T);
    not-selected at close T -> sell all at open T+1; T+1 sell guard;
    buy rate = sell rate = COST_X1_RATE; NAV marked at close; after an
    exit fill at open E, a fresh entry at close E fills at open E+1."""
    idx = close.index
    r = COST_X1_RATE
    pnl = pd.Series(0.0, index=idx)
    per_sym = {}
    for sym in active:
        df = prices[sym]
        opens = df["open"].reindex(idx)
        closes = df["close"].reindex(idx)
        w = weights[sym]
        sig = entry[sym].to_numpy(dtype=bool)
        cash = L.CAPITAL
        qty = 0.0
        nav = pd.Series(L.CAPITAL, index=idx)
        pending = None
        bought_today = -1
        n_buys = n_sells = 0
        for i in range(len(idx)):
            op = opens.iloc[i]
            if pending is not None and not pd.isna(op):
                kind, pw = pending
                if kind == "sell" and qty > 0 and i > bought_today:
                    cash += qty * op * (1 - r)
                    qty = 0.0
                    n_sells += 1
                    pending = None
                elif kind == "buy" and qty == 0:
                    budget = L.CAPITAL * pw
                    qty = budget / op
                    cash -= budget * (1 + r)
                    n_buys += 1
                    bought_today = i
                    pending = None
            if qty > 0:
                if not sig[i] and i > bought_today:
                    pending = ("sell", None)
            else:
                if sig[i]:
                    pending = ("buy", float(w.iloc[i]))
            nav.iloc[i] = cash + qty * closes.iloc[i]
        per_sym[sym] = {"n_buys": n_buys, "n_sells": n_sells,
                        "nav_last": round(float(nav.iloc[-1]), 2)}
        pnl = pnl + (nav - L.CAPITAL)
    nav = pnl + L.CAPITAL
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    return {"sharpe_full": round(float(sharpe(nav)), 6),
            "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "nav_last": round(float(nav.iloc[-1]), 2),
            "returns": [round(float(v), 8) for v in rets.to_numpy()],
            "per_sym": per_sym}


def main():
    print("[E1-P2] loading legacy axis ...")
    prices = L.load_axis(AXIS)
    P = build_panels(prices)
    close = P["close"]
    facts = L.axis_face_facts(prices, AXIS)
    print("[E1-P2] panel:", facts)

    spec = L.CELLS[CELL]
    entry, weights, _ = L.build_signal(close, P["volume"], P["amount"],
                                       spec["W"], spec["N"])
    active = [c for c in entry.columns if entry[c].any()]
    print("[E1-P2] active members:", len(active))

    out = {"batch": "LOWAMP-P2", "cell": CELL, "axis": AXIS, "face": FACE,
           "panel_facts": facts, "active_n": len(active),
           "cost_x1_rate": COST_X1_RATE, "evidence_cutoff": "2026-09-22"}

    # ---- Leg A: as-burned replay via P2's own machinery ----
    print("[E1-P2] Leg A: as-burned replay (runner machinery) ...")
    run = L.run_cell_portfolio(prices, close, entry, weights, FACE, active)
    nav = run["pnl"] + L.CAPITAL
    nav = nav.reindex(close.index).ffill().fillna(L.CAPITAL)
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    yrs = len(nav) / 252.0
    A = {"sharpe_full": round(float(sharpe(nav)), 6),
         "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
         "max_dd": round(float(max_drawdown(nav)), 6),
         "n_trades": run["n_trades"], "n_entries": run["n_entries"],
         "trades_per_year": round(run["n_trades"] / yrs, 2) if yrs else None,
         "n_days": int(len(nav)),
         "nav_first": round(float(nav.iloc[0]), 2),
         "nav_last": round(float(nav.iloc[-1]), 2),
         "returns": [round(float(v), 8) for v in rets.to_numpy()]}
    art_rets = ART["returns"]
    a_rets = A["returns"]
    max_diff = (max(abs(a - b) for a, b in zip(a_rets, art_rets))
                if len(a_rets) == len(art_rets) else None)
    summary_match = all(A[k] == ART[k] for k in
                        ("sharpe_full", "ret_full", "max_dd", "n_trades",
                         "n_entries", "trades_per_year", "n_days",
                         "nav_first", "nav_last"))
    out["legA_as_burned"] = {
        "replay": {k: A[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "n_trades", "n_entries",
                                     "trades_per_year", "n_days",
                                     "nav_first", "nav_last")},
        "artifact": {k: ART[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                         "n_trades", "n_entries",
                                         "trades_per_year", "n_days",
                                         "nav_first", "nav_last")},
        "returns_len_replay": len(a_rets),
        "returns_len_artifact": len(art_rets),
        "returns_max_abs_diff": max_diff,
        "returns_bp_match": (max_diff is not None and max_diff < 5e-7),
        "summary_fields_match": summary_match,
    }
    print("[E1-P2] Leg A sharpe:", A["sharpe_full"], "vs art:",
          ART["sharpe_full"], "| bp match:",
          out["legA_as_burned"]["returns_bp_match"],
          "| summary match:", summary_match)

    # ---- Leg A2: exit-reason census (neutralization held) ----
    print("[E1-P2] Leg A2: exit-reason census ...")
    per_sym, per_trade = leg_a2_reasons(prices, close, entry, weights, active)
    reason_totals = {}
    for t in per_trade:
        reason_totals[t["reason"]] = reason_totals.get(t["reason"], 0) + 1
    default_stack_reasons = {"take_profit", "trailing_stop", "initial_stop",
                             "time_decay", "loss_time", "global_hard_limit"}
    out["legA2_exit_census"] = {
        "reason_totals": reason_totals,
        "per_sym_reasons": {s: v["reasons"] for s, v in per_sym.items()},
        "default_stack_fires": {k: v for k, v in reason_totals.items()
                                if k in default_stack_reasons},
        "neutralization_held": not any(k in default_stack_reasons
                                       for k in reason_totals),
    }
    print("[E1-P2] Leg A2 reasons:", reason_totals, "| neutralization held:",
          out["legA2_exit_census"]["neutralization_held"])

    # ---- Leg C: independent arithmetic ----
    print("[E1-P2] Leg C: independent arithmetic (no engine) ...")
    C = leg_c_independent(prices, close, entry, weights, active)
    c_rets = C["returns"]
    ac_max = (max(abs(a - b) for a, b in zip(a_rets, c_rets))
              if len(a_rets) == len(c_rets) else None)
    # r301 tolerance: <=5bp/day
    tol = 5e-4
    out["legC_independent"] = {
        "result": {k: C[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "nav_last")},
        "per_sym": C["per_sym"],
        "A_vs_C_returns_max_abs_diff": ac_max,
        "A_vs_C_within_5bp_per_day": (ac_max is not None and ac_max <= tol),
    }
    print("[E1-P2] Leg C ret_full:", C["ret_full"], "sharpe:",
          C["sharpe_full"], "| A-vs-C max diff:", ac_max,
          "| within 5bp/day:",
          out["legC_independent"]["A_vs_C_within_5bp_per_day"])

    # ---- Leg B': engine + ExitPatch corrected face (the declared §0.6 face)
    # ExitPatch injects the two NON-bridged fields the params channel cannot
    # reach (engine/backtester.py ExitConfig bridge reads only 6 kwargs);
    # T-136 Leg B precedent verbatim.
    print("[E1-P2] Leg B': engine + ExitPatch corrected face ...")
    from engine import run_backtest
    from contextlib import nullcontext
    from engine.metrics import max_drawdown as _mdd, sharpe as _shp
    params_b = {"position_size_pct": 1.0, "max_positions": 1,
                  "sizing_mode": "fixed_initial", "report_num_entries": True,
                  "take_profit_levels": (), "trailing_stop_activate": 1e12,
                  "initial_stop": -1.0, "time_decay_period": 10 ** 9}
    pnl_b = None
    n_trades_b = 0
    b_reasons = {}
    win_idx = close.index
    with ExitPatch({"loss_time_days": 10 ** 9, "global_hard_limit": 10 ** 9}):
        for sym in active:
            win = {sym: prices[sym]}
            ent = entry[[sym]]
            sc = L.exec_day_scale(weights, sym)
            with (L.CostPatch(2.0) if FACE == "x2" else nullcontext()):
                res = run_backtest(win, params_b, entry_signal=ent,
                                   exit_signal=ent <= 0, entry_size_scale=sc)
            eq = pd.Series(res["equity_curve"],
                           index=win[sym].index[:len(res["equity_curve"])])
            p = (eq - L.CAPITAL).reindex(win_idx).ffill().fillna(0.0)
            pnl_b = p if pnl_b is None else pnl_b + p
            n_trades_b += len(res["trades"])
            for tr in res["trades"]:
                b_reasons[tr["reason"]] = b_reasons.get(tr["reason"], 0) + 1
    nav_b = (pnl_b + L.CAPITAL).reindex(close.index).ffill().fillna(L.CAPITAL)
    rets_b = nav_b.pct_change().dropna()
    B = {"sharpe_full": round(float(_shp(nav_b)), 6),
         "ret_full": round(float(nav_b.iloc[-1] / nav_b.iloc[0] - 1), 6),
         "max_dd": round(float(_mdd(nav_b)), 6),
         "n_trades": n_trades_b,
         "nav_last": round(float(nav_b.iloc[-1]), 2),
         "returns": [round(float(v), 8) for v in rets_b.to_numpy()]}
    bc_max = (max(abs(a - b) for a, b in zip(B["returns"], C["returns"]))
              if len(B["returns"]) == len(C["returns"]) else None)
    out["legB_engine_exitpatch"] = {
        "result": {k: B[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "n_trades", "nav_last")},
        "reason_totals": b_reasons,
        "B_vs_C_returns_max_abs_diff": bc_max,
        "B_vs_C_within_5bp_per_day": (bc_max is not None and bc_max <= 5e-4),
    }
    print("[E1-P2] Leg B' ret_full:", B["ret_full"], "sharpe:", B["sharpe_full"],
          "| reasons:", b_reasons, "| B-vs-C max diff:", bc_max)

    # ---- verdict-face reconciliation ----
    hl = RESULTS["headline"]
    verdict_keys = ("sharpe_full", "ret_full", "max_dd", "n_trades",
                    "n_entries", "trades_per_year")
    out["verdict_face_reconciliation"] = {
        "headline": {k: hl.get(k) for k in verdict_keys},
        "artifact": {k: ART.get(k) for k in verdict_keys},
        "match": all(hl.get(k) == ART.get(k) for k in verdict_keys),
        "verdict_recorded": RESULTS.get("verdict"),
    }
    print("[E1-P2] verdict-face match:",
          out["verdict_face_reconciliation"]["match"],
          "| recorded verdict:", RESULTS.get("verdict"))

    out["e1_verdict"] = "PASS" if (
        out["legA_as_burned"]["returns_bp_match"]
        and out["legA_as_burned"]["summary_fields_match"]
        and out["legA2_exit_census"]["neutralization_held"]
        and out["legC_independent"]["A_vs_C_within_5bp_per_day"]
        and out["verdict_face_reconciliation"]["match"]) else "FAIL"

    path = os.path.join(L.OUT_DIR, "e1_three_leg.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("[E1-P2] E1 VERDICT:", out["e1_verdict"], "| evidence:", path)
    return 0 if out["e1_verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
