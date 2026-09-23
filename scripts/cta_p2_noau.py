"""CTA_P2_NOAU batch runner — no-AU mechanism-decomposition re-eval of CTA_P1.

Prereg: research/CTA_P2_NOAU.md (frozen a3fe81f sha e3248d0b..., claim cafb15c).
R50 finding under test: best family vol_target_tsmom_60@daily PnL was dominated
by the AU gold bull single leg (+121.5M vs RB -47.6/IF -21.2/T -17.1). Drop AU
from the 9-variety panel, re-run the same 16 frozen candidates + 50 nulls +
2 passives (68 cells). If candidates collapse => trend alpha = AU beta; if a
survivor stands => multi-variety trend alpha claim upgrades.

Universe: 8 varieties (IF/IC/IH/IM/T/TF/RB/SC), window 2017-01-17 ->
2026-09-23, pool cta_futures_noau (own passive strict-max + null term; never
borrows the 9-variety cta_futures passives — AU must stay out of the line).

Subcommands:
  gates    G0 smoke / G1 engine selftest / G2 cost constants / G3 data / G4 null determinism
  run      full batch (gates re-run inside; aborts exit 2 on any gate FAIL)
  selftest offline unit tests (synthetic panel; no data files needed)

Ledger: science_gates.append_ledger("cta_p2_noau", 68, ..., evidence_cutoff=2026-09-23).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screening"))

import numpy as np
import pandas as pd

from engine import futures_runner as fr
import cta_p1_screen as p1
import science_gates as sg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG_PATH = os.path.join(ROOT, "research", "CTA_P2_NOAU.md")
RESULTS_JSON = os.path.join(ROOT, "results", "shortline_cta_p2_noau.json")
RESULTS_CSV = os.path.join(ROOT, "research", "cta_p2_noau_results.csv")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
CUTOFF = p1.CUTOFF                      # 2026-09-23 (prereg SS2, same window as CTA_P1)
WINDOW_START = p1.WINDOW_START           # 2017-01-17
IS2_START = p1.IS2_START
FROZEN_PREREG_SHA = "e3248d0b3fb45c8045a2c004898e06fee69a1e4b4eba5b26ccfd4fefdc8077ff"
SEED_BASE = 50_500                      # SEED_REGISTRY["cta_p2_noau"] (prereg SS3)
K_NULLS = p1.K_NULLS                    # 50
BATCH_CELLS = 68                        # 16 candidates + 50 nulls + 2 passives
START_CASH = p1.START_CASH              # 10M (same implementation choice, disclosed)
VARIETIES_NOAU = [v for v in fr.FUT_META if v != "AU"]   # 8 varieties
SOURCE_GAP_DATES = p1.SOURCE_GAP_DATES  # same two allowed cross-exchange holes


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ------------------------------------------------- local variants (universe/seed params)

def build_null_weights_noau(panel_close: pd.DataFrame, k: int,
                            rebalance_idx: np.ndarray) -> pd.DataFrame:
    """Same algorithm as cta_p1_screen.build_null_weights; seed base 50_500+k
    per prereg SS3 (SEED_REGISTRY["cta_p2_noau"], rg-scanned free at R52)."""
    rng = np.random.default_rng(SEED_BASE + k)
    m = panel_close.shape[1]
    out = pd.DataFrame(np.nan, index=panel_close.index, columns=panel_close.columns)
    alive = panel_close.notna().to_numpy()
    for t in rebalance_idx:
        draws = rng.integers(0, 3, size=m) - 1        # {0,1,2} -> {-1,0,1}
        n_alive = int(alive[t].sum())
        if n_alive == 0:
            continue
        row = np.full(m, np.nan)
        row[alive[t]] = draws[alive[t]] / n_alive
        out.iloc[t] = row
    return out


def gate_g3_noau() -> dict:
    """Data completeness on the 8-variety no-AU panel (p1.gate_g3 semantics)."""
    problems = []
    per_variety = {}
    for v in VARIETIES_NOAU:
        path = os.path.join(fr.FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            problems.append(f"{v}: csv missing")
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        seg = df[(df.index >= pd.Timestamp(WINDOW_START)) & (df.index <= pd.Timestamp(CUTOFF))]
        last = str(seg.index[-1].date()) if len(seg) else None
        if last != CUTOFF:
            problems.append(f"{v}: last bar {last} != cutoff {CUTOFF}")
        for fld in ("open", "high", "low", "close", "volume"):
            col = seg[fld].to_numpy(dtype=float)
            col = col[~np.isnan(col)]
            if len(col) and float(col.min()) < 0:
                problems.append(f"{v}.{fld}: negative values")
        s = seg["close"].dropna()
        in_span = seg["close"][seg.index >= s.index[0]]
        holes = [str(d.date()) for d in in_span.index[in_span.isna()]]
        extra = [h for h in holes if h not in SOURCE_GAP_DATES]
        if extra:
            problems.append(f"{v}: in-span NaN holes {extra}")
        per_variety[v] = {"rows": int(len(seg)), "first": str(s.index[0].date()),
                          "last": last, "holes_in_span": holes}
    return {"gate": "G3 data completeness (8-variety no-AU)",
            "ok": len(problems) == 0, "problems": problems,
            "per_variety": per_variety,
            "source_gap_dates_allowed": sorted(SOURCE_GAP_DATES)}


def gate_g4_noau() -> dict:
    """Null determinism on the no-AU panel + noau seed base."""
    panel = fr.load_panel(WINDOW_START, CUTOFF, varieties=VARIETIES_NOAU)
    ridx = p1.r20_rebalance_index(panel["dates"])
    w1 = build_null_weights_noau(panel["close"], 0, ridx)
    w2 = build_null_weights_noau(panel["close"], 0, ridx)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        return {"gate": "G4 null determinism (no-AU)", "ok": False,
                "stage": "weights rebuild differ"}
    r1 = fr.run(panel, w1, start_cash=START_CASH)
    r2 = fr.run(panel, w2, start_cash=START_CASH)
    eq_ok = np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
    tr_ok = r1.trades == r2.trades
    return {"gate": "G4 null determinism (no-AU)", "ok": bool(eq_ok and tr_ok),
            "equity_bitexact": bool(eq_ok), "trades_bitexact": bool(tr_ok)}


def run_gates(include_g0: bool = True) -> dict:
    """G0 smoke / G1 engine selftest / G2 cost constants reused from cta_p1
    (universe-independent); G3/G4 are no-AU local variants."""
    out = {}
    if include_g0:
        out["G0"] = p1.gate_g0()
    out["G1"] = p1.engine_selftest()
    out["G2"] = p1.gate_g2()
    out["G3"] = gate_g3_noau()
    out["G4"] = gate_g4_noau()
    return out


# ---------------------------------------------------------------- batch run

def do_run() -> int:
    t0 = time.time()
    print("[cta_p2_noau] gates ...")
    gates = run_gates(include_g0=True)
    gates_ok = all(g.get("ok") for g in gates.values())
    for name, g in gates.items():
        print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
        if not g.get("ok"):
            print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not gates_ok:
        print("[cta_p2_noau] GATES FAILED — batch aborted (exit 2), no numbers produced")
        return 2

    panel = fr.load_panel(WINDOW_START, CUTOFF, varieties=VARIETIES_NOAU)
    dates = panel["dates"]
    close = panel["close"]
    r20_idx = p1.r20_rebalance_index(dates)
    mon_idx = p1.month_first_index(dates)

    cells: dict[str, dict] = {}
    # 16 candidates x1 + x2 info runs (families byte-identical to CTA_P1)
    for fam_name, builder in p1.FAMILIES.items():
        state = builder(close)
        for regime, ridx in (("daily", None), ("r20", r20_idx)):
            name = f"{fam_name}@{regime}"
            w = p1.build_weights(state, close, ridx)
            cell = p1.run_cell(panel, w, cost_mult=1.0)
            cell_x2 = p1.run_cell(panel, w, cost_mult=2.0)
            cell["x2_full_sharpe"] = cell_x2["full"]["sharpe"]
            cells[name] = cell
            print(f"  {name}: full={cell['full']['sharpe']} x2={cell['x2_full_sharpe']} "
                  f"trades={cell['full']['n_trades']} entries={cell['full']['n_entries']}")
    # 50 nulls (seed 50_500+k)
    null_sharpes = []
    null_cells = {}
    for k in range(K_NULLS):
        w = build_null_weights_noau(close, k, r20_idx)
        cell = p1.run_cell(panel, w, cost_mult=1.0)
        null_cells[f"null_{k}"] = p1.public_cell(cell)
        null_sharpes.append(cell["full"]["sharpe"])
    null_vals = [float(x) for x in null_sharpes]
    mu = sum(null_vals) / len(null_vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / (len(null_vals) - 1))
    null_summary = {"n": len(null_vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(null_vals, 95)), 4),
                    "max": round(max(null_vals), 4), "min": round(min(null_vals), 4)}
    # 2 passives (this batch's own no-AU long baselines)
    passive_cells = {}
    passive_sharpes = {}
    for pname, ridx in (("passive_long_r20", r20_idx), ("passive_long_monthly", mon_idx)):
        w = p1.build_passive_weights(close, ridx)
        cell = p1.run_cell(panel, w, cost_mult=1.0)
        passive_cells[pname] = p1.public_cell(cell)
        passive_sharpes[pname] = cell["full"]["sharpe"]
        print(f"  {pname}: full={cell['full']['sharpe']}")

    at_run_sha = _sha256_file(PREREG_PATH)
    meta = {
        "window": {"start": WINDOW_START, "end": CUTOFF, "n_days": int(len(dates))},
        "varieties": VARIETIES_NOAU,
        "variety_note": ("R50 mechanism decomposition: AU dropped from the 9-variety "
                         "panel (AU.csv on disk untouched); 8-variety re-eval"),
        "start_cash": START_CASH,
        "start_cash_note": ("implementation choice carried from CTA_P1 (10M so "
                            "whole-lot granularity doesn't dominate per-variety "
                            "margin shares); disclosed per prereg SS0"),
        "rebalance": {"r20_days": int(len(r20_idx)), "monthly_days": int(len(mon_idx))},
        "cost": {v: {"fee_lot": fr.FUT_META[v]["fee_lot"], "tick": fr.FUT_META[v]["tick"],
                     "slippage_per_side_yuan": round(fr.FUT_META[v]["tick"] * fr.FUT_META[v]["mult"], 2)}
                 for v in VARIETIES_NOAU},
        "prereg_sha_frozen": FROZEN_PREREG_SHA,
        "prereg_sha_at_run": at_run_sha,
        "prereg_amendments": [],
    }
    phase1 = {
        "batch": "cta_p2_noau",
        "meta": meta,
        **sg.cutoff_meta(CUTOFF),
        "gates": gates,
        "nulls": {"summary": null_summary,
                  "cells": {k: {"full": v["full"]} for k, v in null_cells.items()}},
        "passive": passive_cells,
        "candidates": {k: p1.public_cell(v) for k, v in cells.items()},
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(phase1, fh, ensure_ascii=False, indent=1, default=str)
    print("[cta_p2_noau] phase-1 JSON written (no-AU passive pool registered)")

    # ---- verdicts (pool cta_futures_noau reads THIS file's passives) ----
    null_pool = {"values": null_vals,
                 "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["cta_p2_noau:nulls.summary (K=50 in-batch)"],
                              "known_unparsed": []}}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="cta_futures_noau",
                            null_pool=null_pool)
    print(f"[cta_p2_noau] skill_line_v2 = {line['line']} "
          f"(passive_term={line['passive_term']} null_term={line['null_term']})")
    verdicts = {}
    passers = []
    for name, cell in cells.items():
        v = sg.g1_prime_v2(sharpe_full=cell["full"]["sharpe"], returns=cell["_returns"],
                           batch_cells=BATCH_CELLS, pool="cta_futures_noau",
                           null_pool=null_pool, n_trades=cell["full"]["n_trades"],
                           n_entries=cell["full"]["n_entries"])
        is2 = cell["is2"]
        desc = {
            "annual_positive": bool(cell["full"]["annual_return"] > 0),
            "is2_dual_positive": bool(is2.get("sharpe", 0) > 0 and is2.get("annual_return", 0) > 0),
            "dd_ok": bool(cell["full"]["max_drawdown"] >= -0.35),
            "no_crash_year": bool(cell["worst_year"] >= -0.35),
            "x2_info_sharpe": cell["x2_full_sharpe"],
        }
        v["descriptive"] = desc
        verdicts[name] = v
        if v["pass_v2"]:
            passers.append(name)
            print(f"  >> {name} PASSES g1_prime_v2")

    # within-batch pairwise corr (D6 disclosure, all 16)
    rets_df = pd.DataFrame({k: cells[k]["_returns"] for k in cells})
    corr = rets_df.corr()
    within_max = {}
    for name in cells:
        others = corr[name].drop(name).abs()
        within_max[name] = round(float(others.max()), 4) if len(others) else None

    # family PBO for all 8 families (2-cell CSCV, informational) + G2 columns for passers
    from pbo import cscv_pbo, align_returns
    family_pbo = {}
    for fam in p1.FAMILIES:
        pair = {f"{fam}@daily": cells[f"{fam}@daily"]["_returns"],
                f"{fam}@r20": cells[f"{fam}@r20"]["_returns"]}
        mat = align_returns(pair)
        family_pbo[fam] = cscv_pbo(mat)

    verdicts_g2 = {}
    d6_inregister = {}
    if passers:
        try:
            import ew6_portfolio as E
            E._init_worker()
            from firm.hr import TRADERS_DIR, load_trader
            member_rets = {}
            for fn in sorted(os.listdir(TRADERS_DIR)):
                if not fn.endswith(".json"):
                    continue
                tid = fn[:-5]
                t = load_trader(tid)
                if t.get("status") == "FIRE":
                    continue
                mr = E.member_run(tid)
                eq = pd.Series(mr["eq"], index=pd.to_datetime(mr["dates"]))
                member_rets[tid] = eq.pct_change().dropna()
            for name in passers:
                cr = cells[name]["_returns"]
                pairs = {}
                for tid, mret in member_rets.items():
                    j = pd.concat([cr, mret], axis=1, join="inner").dropna()
                    if len(j) > 60 and j.iloc[:, 1].std() > 0:
                        pairs[tid] = round(float(j.corr().iloc[0, 1]), 4)
                d6_inregister[name] = {"max_abs_corr": round(max(abs(v) for v in pairs.values()), 4) if pairs else None,
                                       "pairs": pairs}
        except Exception as exc:  # noqa: BLE001
            d6_inregister = {"error": f"in-register corr skipped: {exc}"}
        for name in passers:
            fam = name.split("@")[0]
            dsr = sg.deflated_sharpe_ratio(cells[name]["_returns"],
                                            n_trials=line["n_eff"],
                                            var_null_sr=sigma ** 2)
            verdicts_g2[name] = sg.g2_registration_v2(
                g1_pass=True, dsr=dsr, pbo=family_pbo[fam]["pbo"])

    # ---- ledger append (single source, live chain head) ----
    ledger = sg.append_ledger("cta_p2_noau", BATCH_CELLS, "results/shortline_cta_p2_noau.json",
                              evidence_cutoff=CUTOFF,
                              note=("no-AU mechanism decomposition (R50 pointer): same "
                                    "16 frozen families x daily/r20 + 50 nulls (seed "
                                    "50_500+k) + 2 passive longs on the 8-variety panel; "
                                    "pool cta_futures_noau (own passive strict-max + null "
                                    "term); prereg research/CTA_P2_NOAU.md frozen a3fe81f"))
    # ---- audit segment (compute_audit in-batch, prereg SS0) ----
    audit_seg = {}
    try:
        subprocess.run([sys.executable, os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_p2_noau] compute_audit in-batch run failed: {exc}")
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"), "flags": latest.get("flags")}
    final = dict(phase1)
    final.update({
        "null_pool": null_pool,
        "skill_line": line,
        "verdicts_g1": verdicts,
        "g1_passers": passers,
        "verdicts_g2": verdicts_g2,
        "d6": {"within_batch_max_abs_corr": within_max,
               "in_register": d6_inregister,
               "reject_line": 0.7},
        "family_pbo": family_pbo,
        "trials_ledger": ledger,
        "audit": audit_seg,
        "passive_sharpes": passive_sharpes,
    })
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(final, fh, ensure_ascii=False, indent=1, default=str)

    # ---- CSV (68 rows) ----
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cell", "family", "regime", "kind", "sharpe_full", "annual_return",
                     "max_drawdown", "worst_year", "is2_sharpe", "is2_annual",
                     "x2_full_sharpe", "n_trades", "n_entries", "turnover", "win_rate",
                     "line", "line_ok", "ci_ok", "pass_v2"])
        for name, cell in cells.items():
            v = verdicts[name]
            fam, reg = name.split("@")
            wr.writerow([name, fam, reg, "candidate", cell["full"]["sharpe"],
                         cell["full"]["annual_return"], cell["full"]["max_drawdown"],
                         cell["worst_year"], cell["is2"].get("sharpe"),
                         cell["is2"].get("annual_return"), cell["x2_full_sharpe"],
                         cell["full"]["n_trades"], cell["full"]["n_entries"],
                         cell["full"]["turnover"], cell["full"]["win_rate"],
                         v["skill_line"]["line"], v["line_ok"],
                         v["ci_lower_bound_positive"], v["pass_v2"]])
        for k in range(K_NULLS):
            c = null_cells[f"null_{k}"]
            wr.writerow([f"null_{k}", "random", "r20", "null", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         "", c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"],
                         "", "", "", ""])
        for pname, c in passive_cells.items():
            wr.writerow([pname, "passive_long", pname, "passive", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         "", c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"],
                         "", "", "", ""])

    # ---- gate_attrition entry ----
    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "CTA_P2_NOAU",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "search",
            "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": ledger.get("total"),
            "gates": {"skill_line_v2": line["line"],
                      "g1_passers": len(passers),
                      "descriptive_all_pass_candidates": int(sum(
                          1 for n in cells
                          if all(verdicts[n]["descriptive"][k]
                                 for k in ("annual_positive", "is2_dual_positive",
                                           "dd_ok", "no_crash_year"))))},
            "eliminated": 16 - len(passers),
            "refs": {"results": "results/shortline_cta_p2_noau.json",
                     "prereg": "research/CTA_P2_NOAU.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_p2_noau] attrition append failed: {exc}")

    print(f"[cta_p2_noau] DONE in {time.time() - t0:.1f}s — passers: {passers}")
    print(f"[cta_p2_noau] null summary: {null_summary}")
    print(f"[cta_p2_noau] skill line: {line}")
    return 0


# ---------------------------------------------------------------- selftest (offline)

def do_selftest() -> int:
    fails = []
    # universe definition: 8 varieties, AU excluded, FUT_META order preserved
    if VARIETIES_NOAU != [v for v in fr.FUT_META if v != "AU"] or len(VARIETIES_NOAU) != 8:
        fails.append(f"VARIETIES_NOAU wrong: {VARIETIES_NOAU}")
    if "AU" in VARIETIES_NOAU:
        fails.append("AU not excluded")
    # seed isolation: noau null k=0 must differ from cta_p1 null k=0 on same panel
    dates = pd.bdate_range("2020-01-01", periods=100)
    close = pd.DataFrame({"A": np.arange(100, dtype=float) + 10,
                          "B": np.arange(100, dtype=float) * 0.5 + 5},
                         index=dates)
    r20 = p1.r20_rebalance_index(dates)
    w_noau = build_null_weights_noau(close, 0, r20)
    w_p1 = p1.build_null_weights(close, 0, r20)
    if np.array_equal(np.nan_to_num(w_noau.to_numpy(), nan=-999.0),
                      np.nan_to_num(w_p1.to_numpy(), nan=-999.0)):
        fails.append("seed isolation broken: noau(50_500) null == p1(50_000) null")
    # noau null determinism (offline)
    w1 = build_null_weights_noau(close, 0, r20)
    w2 = build_null_weights_noau(close, 0, r20)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        fails.append("noau null weights rebuild differ (synthetic)")
    # passive weights reuse: alive-only long equal share
    wp = p1.build_passive_weights(close, r20)
    row0 = wp.iloc[0].dropna()
    if len(row0) != 2 or not np.allclose(row0.to_numpy(), 0.5):
        fails.append(f"passive weights row0 {row0.to_dict()}")
    # engine unit assertions (G1 body, offline synthetic)
    g1 = p1.engine_selftest()
    if not g1["ok"]:
        fails.extend(g1["failures"])
    # schedule determinism (reused)
    r20b = p1.r20_rebalance_index(dates)
    if list(r20b[:3]) != [0, 20, 40]:
        fails.append(f"r20 schedule {list(r20b[:3])}")
    print(f"[cta_p2_noau selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "gates":
        gs = run_gates()
        for name, g in gs.items():
            print(f"{name}: {'PASS' if g.get('ok') else 'FAIL'}")
            if not g.get("ok"):
                print(json.dumps(g, ensure_ascii=False, default=str)[:600])
        sys.exit(0 if all(g.get("ok") for g in gs.values()) else 2)
    if cmd == "run":
        sys.exit(do_run())
    if cmd == "selftest":
        sys.exit(do_selftest())
    print("usage: cta_p2_noau.py gates|run|selftest")
    sys.exit(1)
