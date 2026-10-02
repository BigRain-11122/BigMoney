# -*- coding: utf-8 -*-
"""r397 bm-c LOWAMP-DEEP-P1 E1 known-answer three-leg reconciliation
(r492/r301/r522 law; P3 r551 pattern adapted to the deep runner).

MUST run BEFORE any LOWAMP-DEEP-P1 verdict number is consumed downstream
(prereg sec.4 E1 four-leg precondition). The batch burned WITH the
dual-channel exit-axis (sec.0.6: NEUTRALIZED_PARAMS bridge 4 keys +
ExitPatch loss_time_days/global_hard_limit), so the as-burned face IS the
declared hold-through face. Legs:

  Leg A  as-burned replay of the headline cell (LAD-EDGE deep base) through
         the runner's OWN machinery (build_signal + run_cell_portfolio,
         zero reimplementation) reconciled to the recorded cont artifact
         summary + full returns series to the bp.
  Leg A2 exit-reason census via the runner's own _exit_reason_census
         (single source, r303 law) -- dual-channel held = only
         signal_reversal lawful, default_share <= 0.20 gate.
  Leg C  fully independent no-engine arithmetic simulator (T+1 open fills,
         COST_X1_RATE both ways, 1-day re-entry gap, weights set at entry
         never resized) cross-validating the engine leg (B/C <= 5bp/day,
         r301 tolerance). Engine leg B == as-burned Leg A by construction
         (ExitPatch already inside run_cell_portfolio), so B_vs_C is
         computed as engine-as-burned vs Leg C.

  Leg 4 (verdict-face reconciliation) vs lowamp_deep_p1_results.json:
         headline face reconciled against E1 Leg A artifact to 1e-9,
         nulls k=2000, finalize census pass.

Zero network, deterministic, evidence_cutoff 2026-09-22 (runner's own lock).
Evidence: results/lowamp_deep_p1/e1_three_leg.json
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

import lowamp_deep_p1 as L
from live.paper import build_panels, COST_X1_RATE
from knowledge.rules import is_t0

CELL = "LAD-EDGE"
AXIS = "deep"
FACE = "base"
ART = json.load(open(os.path.join(L.OUT_DIR, f"cont_{CELL}_{AXIS}_{FACE}.json"),
                     encoding="utf-8"))


def leg_c_independent(prices, close, entry, weights, active):
    """Independent arithmetic simulator -- no engine on the path.
    Semantics mirrored from the frozen engine contract (read-only audit):
    entry signal at close T -> buy at open T+1 (the symbol's next own
    bar), budget = 1M x w_s(T); not-selected at close T -> sell all at
    open T+1; buy rate = sell rate = COST_X1_RATE; NAV marked at close;
    after an exit fill at open E, a fresh entry at close E fills at
    open E+1.
    DEEP-axis fixes (r397, first divergence vs the P3 r551 pattern):
    (1) the per-symbol loop runs on the symbol's OWN bar index (mid-
    panel listings/delistings make panel-reindex closes NaN -- the
    engine itself runs on win={sym: own bars} and never sees a NaN);
    pre-listing days contribute 0, post-last-bar holdings freeze at the
    last valid close (engine ffill face).
    (2) engine backtester.py L722-724 T+1 sell-eval block: on the entry
    fill bar a T+1 symbol skips exit evaluation; T+0 codes (T0_ETF_CODES
    single source: gold/cross-border/bond ETFs) evaluate immediately.
    The P3 pattern's unconditional i > bought_today pending-gate was a
    latent bug that never fired on the legacy 4-member universe but
    breaks the deep universe's 10-member rotation."""
    idx = close.index
    r = COST_X1_RATE
    pnl = pd.Series(0.0, index=idx)
    per_sym = {}
    for sym in active:
        t0 = is_t0(sym)                  # engine L723: T+0 codes exempt the
        df = prices[sym]                 # entry-day sell-eval block
        sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
        w = weights[sym].reindex(df.index)
        opens = df["open"].to_numpy()
        closes = df["close"].to_numpy()
        cash = L.CAPITAL
        qty = 0.0
        nav_vals = []
        pending = None
        bought_today = -1
        n_buys = n_sells = 0
        for i in range(len(df)):
            op = opens[i]
            if pending is not None:
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
                # engine backtester.py L722-724 (verbatim semantics): on the
                # entry fill bar (hold_days==0) a T+1 symbol SKIPS the exit
                # evaluation entirely ("T+1: cannot sell on entry day");
                # T+0 codes (gold/cross-border/bond ETFs, knowledge/rules.py
                # T0_ETF_CODES single source) evaluate immediately. Proven
                # by cost_price recovery: 159920 entry 09-14 -> exit fill
                # 09-17 hold=1 (T+0, entry-day read); 159919 entry 12-17 ->
                # exit fill 12-19 hold=2 (T+1, entry-day skip).
                if not (i == bought_today and not t0):
                    if not sig[i]:
                        pending = ("sell", None)
            else:
                if sig[i]:
                    pending = ("buy", float(w.iloc[i]))
            nav_vals.append(cash + qty * closes[i])
        nav_sym = pd.Series(nav_vals, index=df.index)
        p = (nav_sym - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
        pnl = pnl + p
        per_sym[sym] = {"n_buys": n_buys, "n_sells": n_sells,
                        "nav_last": round(float(nav_sym.iloc[-1]), 2)}
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
    print("[E1-DEEP] loading deep axis ...")
    prices = L.load_axis(AXIS)
    P = build_panels(prices)
    close = P["close"]
    facts = L.axis_face_facts(prices, AXIS)
    print("[E1-DEEP] panel:", facts)

    spec = L.CELLS[CELL]
    entry, weights, _ = L.build_signal(close, P["volume"], P["amount"],
                                       spec["W"], spec["N"], spec["sizing"])
    active = [c for c in entry.columns if entry[c].any()]
    print("[E1-DEEP] active members:", len(active))

    out = {"batch": L.BATCH_NAME, "cell": CELL, "axis": AXIS, "face": FACE,
           "panel_facts": facts, "active_n": len(active),
           "cost_x1_rate": COST_X1_RATE, "evidence_cutoff": "2026-09-22"}

    # ---- Leg A: as-burned replay via the runner's own machinery ----
    print("[E1-DEEP] Leg A: as-burned replay (runner machinery) ...")
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
    sum_keys = ("sharpe_full", "ret_full", "max_dd", "n_trades", "n_entries",
                "trades_per_year", "n_days", "nav_first", "nav_last")
    summary_match = all(A[k] == ART[k] for k in sum_keys)
    out["legA_as_burned"] = {
        "replay": {k: A[k] for k in sum_keys},
        "artifact": {k: ART[k] for k in sum_keys},
        "returns_len_replay": len(a_rets),
        "returns_len_artifact": len(art_rets),
        "returns_max_abs_diff": max_diff,
        "returns_bp_match": (max_diff is not None and max_diff < 5e-7),
        "summary_fields_match": summary_match,
    }
    print("[E1-DEEP] Leg A sharpe:", A["sharpe_full"], "vs art:",
          ART["sharpe_full"], "| bp match:",
          out["legA_as_burned"]["returns_bp_match"],
          "| summary match:", summary_match)

    # ---- Leg A2: exit-reason census (runner single source, r303 law) ----
    print("[E1-DEEP] Leg A2: exit-reason census (runner _exit_reason_census) ...")
    cen = L._exit_reason_census(AXIS, CELL, FACE)
    default_fires = {k: v for k, v in cen["per_reason"].items()
                     if k not in L.LAWFUL_EXIT_REASONS}
    out["legA2_exit_census"] = {
        "reason_totals": cen["per_reason"],
        "per_sym_reasons": {s: v["reasons"] for s, v in cen["per_sym"].items()},
        "default_stack_fires": default_fires,
        "total_exits": cen["total_exits"],
        "default_share": cen["default_share"],
        "block_share": cen["block_share"],
        "census_pass": cen["pass"],
        "dual_channel_held": not default_fires,
    }
    print("[E1-DEEP] Leg A2 reasons:", cen["per_reason"],
          "| default_share:", cen["default_share"],
          "| dual-channel held:",
          out["legA2_exit_census"]["dual_channel_held"])

    # ---- Leg C: independent arithmetic (no engine) ----
    print("[E1-DEEP] Leg C: independent arithmetic (no engine) ...")
    C = leg_c_independent(prices, close, entry, weights, active)
    c_rets = C["returns"]
    diffs = [abs(a - b) for a, b in zip(a_rets, c_rets)]
    ac_max = max(diffs) if len(a_rets) == len(c_rets) else None
    over_5bp = [i for i, d in enumerate(diffs) if d > 5e-4]
    tol = 5e-4
    out["legC_independent"] = {
        "result": {k: C[k] for k in ("sharpe_full", "ret_full", "max_dd",
                                     "nav_last")},
        "per_sym": C["per_sym"],
        "engine_vs_C_returns_max_abs_diff": ac_max,
        "days_over_5bp": len(over_5bp),
        "days_total": len(diffs),
        "over_day_is_trade_boundary": bool(
            over_5bp and rets.index[over_5bp[0]].date()
            in set(t.date() for t in run["trade_dates"])),
        "second_largest_diff": round(sorted(diffs)[-2], 8) if len(diffs) > 1 else None,
        "letter_within_5bp_per_day": (ac_max is not None and ac_max <= tol),
        "B_vs_C_within_5bp_per_day": (ac_max is not None and ac_max <= tol),
    }
    print("[E1-DEEP] Leg C ret_full:", C["ret_full"], "sharpe:",
          C["sharpe_full"], "| engine-vs-C max diff:", ac_max,
          "| days over 5bp:", len(over_5bp),
          "| letter within:",
          out["legC_independent"]["letter_within_5bp_per_day"])
    if ac_max is not None and ac_max > tol:
        out["legC_residual_note"] = {
            "value": ac_max,
            "reading": "letter exceedance disclosed: %d/%d days over 5bp, "
                       "max %.6g (second-largest %s)"
                       % (len(over_5bp), len(diffs), ac_max,
                          out["legC_independent"]["second_largest_diff"]),
            "canonical_precedents": [
                "research/T136_VERDICT_AUDIT.md L48 (boundary fill-semantics "
                "residue adjudication)",
                "research/LOWAMP-P2.md sec.9 L78 (engine+ExitPatch vs "
                "independent leg, T-136 Legs B/C precedent)",
            ],
            "disposition": "at-boundary-residue reading applies ONLY if "
                           "exactly one day over AND that day is a trade "
                           "boundary; otherwise FAIL stands",
        }

    # ---- Leg B note: engine leg == as-burned Leg A by construction ----
    out["legB_engine_note"] = {
        "b_equals_a_by_construction": True,
        "exit_patch_overrides": L.EXIT_PATCH_OVERRIDES,
        "b_vs_c_ref": "legC_independent.engine_vs_C_returns_max_abs_diff",
    }

    # ---- Leg 4: verdict-face reconciliation vs finalize results ----
    res_path = os.path.join(L.OUT_DIR, "lowamp_deep_p1_results.json")
    if not os.path.exists(res_path):
        out["verdict_face_reconciliation"] = {
            "status": "DEFERRED",
            "reason": "results file absent (finalize pending)",
            "results_file_present": False,
        }
    else:
        res = json.load(open(res_path, encoding="utf-8"))
        head = res["headline"]
        art = out["legA_as_burned"]["artifact"]

        def _close(a, b, tol=1e-9):
            return abs(float(a) - float(b)) <= tol

        recon_fields = {
            "sharpe_full": _close(head["sharpe_full"], art["sharpe_full"]),
            "ret_full": _close(head["ret_full"], art["ret_full"]),
            "max_dd": _close(head["max_dd"], art["max_dd"]),
            "n_trades": head["n_trades"] == art["n_trades"],
            "n_entries": head["n_entries"] == art["n_entries"],
        }
        nulls_k = res["nulls"]["same_mask"]["k"]
        census_ok = (res["gates"]["exit_census"]["default_share"]
                     <= res["gates"]["exit_census"]["block_share"])
        out["verdict_face_reconciliation"] = {
            "status": "RECONCILED" if (all(recon_fields.values())
                                      and nulls_k == 2000
                                      and census_ok) else "MISMATCH",
            "results_file_present": True,
            "verdict": res.get("verdict"),
            "headline_matches_legA_artifact": recon_fields,
            "nulls_k": nulls_k,
            "finalize_census_pass": census_ok,
            "note": "finalize-window reconciliation (r397 bm-c): headline "
                    "face reconciled against E1 as-burned Leg A artifact "
                    "to 1e-9; nulls k and finalize census carried",
        }

    # B/C gate: letter pass OR the canonical at-boundary-residue case
    # (exactly one day over and that day is a trade-boundary fill day),
    # per T-136 audit + LOWAMP-P2 sec.9 adjudications -- threshold itself
    # unchanged at 5bp.
    b_vs_c_ok = (out["legC_independent"]["B_vs_C_within_5bp_per_day"]
                 or (out["legC_independent"]["days_over_5bp"] == 1
                     and out["legC_independent"]["over_day_is_trade_boundary"]))
    out["e1_verdict"] = "PASS" if (
        out["legA_as_burned"]["returns_bp_match"]
        and out["legA_as_burned"]["summary_fields_match"]
        and out["legA2_exit_census"]["census_pass"]
        and out["legA2_exit_census"]["dual_channel_held"]
        and b_vs_c_ok) else "FAIL"

    path = os.path.join(L.OUT_DIR, "e1_three_leg.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("[E1-DEEP] E1 VERDICT:", out["e1_verdict"], "| evidence:", path)
    return 0 if out["e1_verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
