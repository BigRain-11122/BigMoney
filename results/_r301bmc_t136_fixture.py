"""T-136 LOWAMP-P1 verdict integrity audit -- known-answer fixture legs A/B/C.

Leg A  as-burned replay of the judged continuous face (engine, exact runner
       machinery, zero reimplementation drift) reconciled to the recorded
       cont artifact to the bp, incl. full returns-series match.
Leg A2 exit-reason census per symbol (which frozen exit rules fired).
Leg B  same window/signal/weights/costs with the engine default exit stack
       NEUTRALIZED (P1 signal exit only) = the family's intended ALWAYS-ON
       face.
Leg C  independent P1-only arithmetic simulator (no engine on the path) --
       cross-validates Leg B.

Zero network, deterministic, evidence_cutoff 2026-09-22 (runner's own lock).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

import lowamp_p1 as L
from live.paper import build_panels, ExitPatch, COST_X1_RATE

OUT_DIR = os.path.join(L.ROOT, "results", "t136_verdict_audit")
os.makedirs(OUT_DIR, exist_ok=True)

ART = json.load(open(os.path.join(L.OUT_DIR, "cont_LA-REP_legacy_base.json"),
                     encoding="utf-8"))


def load_legacy_face():
    prices = L.load_axis("legacy")
    P = build_panels(prices)
    close = P["close"]
    return prices, P, close


def engine_run_per_symbol(prices, close, entry, weights, face, active,
                           params_override=None, exit_patch=None):
    """run_cell_portfolio internals, keeping per-symbol trades (reasons)."""
    from engine import run_backtest
    from contextlib import nullcontext
    params = {"position_size_pct": 1.0, "max_positions": 1,
              "sizing_mode": "fixed_initial", "report_num_entries": True}
    if params_override:
        params.update(params_override)
    win_idx = close.index
    pnl = None
    per_sym = {}
    n_trades = n_entries = 0
    for sym in active:
        win = {sym: prices[sym]}
        ent = entry[[sym]]
        sc = L.exec_day_scale(weights, sym)
        patch = ExitPatch(exit_patch) if exit_patch else nullcontext()
        with patch:
            with (L.CostPatch(2.0) if face == "x2" else nullcontext()):
                res = run_backtest(win, params, entry_signal=ent,
                                   exit_signal=ent <= 0,
                                   entry_size_scale=sc)
        eq = pd.Series(res["equity_curve"],
                       index=win[sym].index[:len(res["equity_curve"])])
        p = (eq - L.CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        reasons = {}
        for tr in res["trades"]:
            reasons[tr["reason"]] = reasons.get(tr["reason"], 0) + 1
        per_sym[sym] = {
            "n_trades": len(res["trades"]),
            "num_entries": int(res["metrics"].get("num_entries", 0)),
            "reasons": reasons,
            "avg_hold_days": (round(sum(t["hold_days"] for t in res["trades"])
                                    / max(1, len(res["trades"])), 2)),
            "avg_pnl_rate": (round(sum(t["pnl_rate"] for t in res["trades"])
                                   / max(1, len(res["trades"])), 6)),
            "nav_last": round(float(eq.iloc[-1]), 2),
        }
    nav = pnl + L.CAPITAL
    nav = nav.reindex(close.index).ffill().fillna(L.CAPITAL)
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    return {
        "sharpe_full": round(float(sharpe(nav)), 6),
        "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
        "max_dd": round(float(max_drawdown(nav)), 6),
        "n_trades": n_trades, "n_entries": n_entries,
        "nav_last": round(float(nav.iloc[-1]), 2),
        "returns": [round(float(v), 8) for v in rets.to_numpy()],
        "per_sym": per_sym,
    }


def leg_c_independent(prices, close, entry, weights, active):
    """P1-only arithmetic simulator -- no engine on the path.

    Semantics mirrored from the frozen engine contract (read-only audit):
    entry signal at close T -> buy at open T+1, budget = 1M x w_s(T);
    not-selected at close T -> sell all at open T+1; T+1 sell guard
    (cannot exit on entry day); buy rate = sell rate = COST_X1_RATE;
    NAV marked at close.  After an exit fill at open E, a fresh entry
    signal at close E queues a fill at open E+1 (engine re-entry gap).
    """
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
        pending = None            # (kind, w) queued at prior close
        bought_today = -1
        n_fills_buy = n_fills_sell = 0
        for i in range(len(idx)):
            op = opens.iloc[i]
            if pending is not None and not pd.isna(op):
                kind, pw = pending
                if kind == "sell" and qty > 0 and i > bought_today:
                    cash += qty * op * (1 - r)
                    qty = 0.0
                    n_fills_sell += 1
                    pending = None
                elif kind == "buy" and qty == 0:
                    budget = L.CAPITAL * pw
                    qty = budget / op
                    cash -= budget * (1 + r)
                    n_fills_buy += 1
                    bought_today = i
                    pending = None
                elif pd.isna(op):
                    pass
            # queue at today's close
            if qty > 0:
                if not sig[i] and i > bought_today:
                    pending = ("sell", None)
            else:
                if sig[i]:
                    pending = ("buy", float(w.iloc[i]))
            nav.iloc[i] = cash + qty * closes.iloc[i]
        per_sym[sym] = {
            "n_buys": n_fills_buy, "n_sells": n_fills_sell,
            "nav_last": round(float(nav.iloc[-1]), 2),
            "pnl_last": round(float(nav.iloc[-1] - L.CAPITAL), 2),
        }
        pnl = pnl + (nav - L.CAPITAL)
    nav = pnl + L.CAPITAL
    rets = nav.pct_change().dropna()
    from engine.metrics import max_drawdown, sharpe
    return {
        "sharpe_full": round(float(sharpe(nav)), 6),
        "ret_full": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
        "max_dd": round(float(max_drawdown(nav)), 6),
        "nav_last": round(float(nav.iloc[-1]), 2),
        "returns": [round(float(v), 8) for v in rets.to_numpy()],
        "per_sym": per_sym,
    }


def main():
    print("[T-136] loading legacy axis ...")
    prices, P, close = load_legacy_face()
    facts = L.axis_face_facts(prices, "legacy")
    print("[T-136] panel:", facts)

    entry, weights, elig = L.build_signal(close, P["volume"], P["amount"],
                                          89, 2)
    active = [c for c in entry.columns if entry[c].any()]
    print("[T-136] active members:", active)

    out = {"batch": "LOWAMP-P1", "cell": "LA-REP", "axis": "legacy",
           "panel_facts": facts, "active": active,
           "cost_x1_rate": COST_X1_RATE}

    # ---------------- Leg A: as-burned replay ----------------
    print("[T-136] Leg A: as-burned replay ...")
    A = engine_run_per_symbol(prices, close, entry, weights, "base", active)
    art_rets = ART["returns"]
    a_rets = A["returns"]
    max_diff = (max(abs(a - b) for a, b in zip(a_rets, art_rets))
                if len(a_rets) == len(art_rets) else None)
    out["legA_as_burned"] = {
        "replay": {k: A[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "n_trades", "n_entries", "nav_last")},
        "artifact": {k: ART[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                         "n_trades", "n_entries", "nav_last")},
        "returns_len_replay": len(a_rets),
        "returns_len_artifact": len(art_rets),
        "returns_max_abs_diff": max_diff,
        "returns_bp_match": (max_diff is not None and max_diff < 5e-7),
        "summary_fields_match": all(
            A[k] == ART[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                    "n_trades", "n_entries", "nav_last")),
        "per_sym": A["per_sym"],
    }
    print("[T-136] Leg A ret_full:", A["ret_full"],
          "| artifact:", ART["ret_full"],
          "| returns bp match:", out["legA_as_burned"]["returns_bp_match"],
          "| summary match:",
          out["legA_as_burned"]["summary_fields_match"])
    print("[T-136] Leg A exit reasons:",
          json.dumps({s: v["reasons"] for s, v in A["per_sym"].items()},
                     ensure_ascii=False))

    # ---------------- Leg B: exit-stack neutralized ----------------
    print("[T-136] Leg B: exit-stack neutralized (P1 only) ...")
    params_B = {"take_profit_levels": (), "time_decay_period": 10 ** 6,
                "time_decay_threshold": -1.0, "initial_stop": -1.0,
                "trailing_stop_activate": 10.0}
    B = engine_run_per_symbol(prices, close, entry, weights, "base", active,
                              params_override=params_B,
                              exit_patch={"loss_time_days": 10 ** 6,
                                          "global_hard_limit": 10 ** 6})
    out["legB_p1_only"] = {
        "params_override": params_B,
        "exit_patch": {"loss_time_days": 10 ** 6,
                       "global_hard_limit": 10 ** 6},
        "result": {k: B[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "n_trades", "n_entries", "nav_last")},
        "per_sym": B["per_sym"],
    }
    print("[T-136] Leg B ret_full:", B["ret_full"], "sharpe:",
          B["sharpe_full"], "n_trades:", B["n_trades"])

    # ---------------- Leg C: independent arithmetic ----------------
    print("[T-136] Leg C: independent P1-only arithmetic ...")
    C = leg_c_independent(prices, close, entry, weights, active)
    b_rets = B["returns"]
    c_rets = C["returns"]
    bc_max = (max(abs(a - b) for a, b in zip(b_rets, c_rets))
              if len(b_rets) == len(c_rets) else None)
    out["legC_independent"] = {
        "result": {k: C[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "nav_last")},
        "per_sym": C["per_sym"],
        "B_vs_C_returns_max_abs_diff": bc_max,
    }
    print("[T-136] Leg C ret_full:", C["ret_full"], "nav_last:", C["nav_last"],
          "| B-vs-C max diff:", bc_max)

    # ---------------- decomposition ----------------
    gross_path = {}
    for sym in active:
        df = prices[sym]
        gross_path[sym] = {
            "first_close": round(float(df["close"].iloc[0]), 3),
            "last_close": round(float(df["close"].iloc[-1]), 3),
            "path_ret": round(float(df["close"].iloc[-1]
                                    / df["close"].iloc[0] - 1), 4),
        }
    churn_pp = round((A["ret_full"] - B["ret_full"]) * 100, 2)
    out["decomposition"] = {
        "raw_path_BH": gross_path,
        "as_burned_ret_pp": round(A["ret_full"] * 100, 2),
        "intended_p1_only_ret_pp": round(B["ret_full"] * 100, 2),
        "exit_stack_churn_cost_pp": churn_pp,
    }
    print("[T-136] decomposition:", json.dumps(out["decomposition"],
                                              ensure_ascii=False))

    path = os.path.join(OUT_DIR, "t136_leg123.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("[T-136] evidence written:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
