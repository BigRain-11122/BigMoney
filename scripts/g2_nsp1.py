"""G2 deepening for the two NSP1 G1' candidates (research/G2_NSP1.md).

PRE-REGISTERED before running (2026-09-23, research/G2_NSP1.md written
first). Do NOT tune thresholds or re-run after results (iron rule 3).

Two candidate families, CE exit regime only (registered contract:
bridge time_decay 25d/5% + trailing 0.10 + ExitPatch loss_time_days=16):
  A. triple_ma_5_20_60      center (5,20,60), OAT+- grid = 7 points
  B. high252_prox_top5_r20  center (win252,k5,r20), OAT+- grid = 7 pts

Per-point green = six G1' clauses on RECORDED constants (CE i-line =
max(NSP1 in-batch CE p95, recorded floor) = 0.4229; vi = 0.4004; rest
from p2_calibration.json, unchanged) AND OOS Sharpe >= 0.70 x family
reference (reference = candidate's own NSP1 recorded OOS).

Cost stress x2/x3 on both centers (CostPatch factory paradigm, engine
files untouched, restored after). x2 survive (G2 clause) = full Sharpe
> 0.4004 AND OOS >= 0.70 x ref. x3 recorded only. Yearly (G2 clause) =
no calendar year <= -30% on center 1x equity (2026 partial, honest).

G2 pass == neighborhood all green + center anchored (|dSharpe| < 0.002
vs NSP1 recorded full Sharpe) + cost x2 survive + no crash year.
Passer -> register firm/traders/ (INTERN, evidence_cutoff=2026-09-22,
exit_overrides + repro contract, cost_x2 certificate). FAIL -> honest
archival, NSP1 line closed, no exception clause.

All panels truncated to EVIDENCE_CUT (J16 anchor pattern): the batch
judges exactly the evidence the G1' screen produced, so same-day data
growth after 15:30 can never break the anchors.

No new random baselines this batch: deepening batches judge on recorded
constants (J8-G2 / J14 / J15 / J19 precedent); NSP1 already created the
core48 CE null (0.4229) this batch cites.

Products: research/g2_nsp1_results.csv + results/g2_nsp1.json.
Trial ledger: 1025 (prior, new_signal_p1.json) + 18 = 1043.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # new_signal_p1

import pandas as pd

from config import PATHS
from science_gates import append_ledger, ledger_head, ledger_total  # T-03 F3 (audit P0-7)
from live.paper import (OOS_START, build_panels, load_core, seg_metrics,
                        self_test_patches)
from new_signal_p1 import _topk_frozen, run_cell
from strategies import trend

EVIDENCE_CUT = "2026-09-22"     # NSP1 data_end (pre-reg sec.0)
DECAY_FLOOR = 0.70              # OOS decay < 30% vs family reference
ANCHOR_TOL = 0.002              # center must reproduce NSP1 full Sharpe
CRASH_YEAR = -0.30
COST_MULTS = [2, 3]
BATCH_N = 18                    # 7 + 7 neighborhood 1x + 2 centers x(x2,x3)


def load_recorded():
    """Recorded constants + NSP1 anchor cells (data-driven, no hardcode)."""
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        gate = json.load(fh)["g1_prime_gate"]
    with open(os.path.join(PATHS.results_dir, "new_signal_p1.json"),
              encoding="utf-8") as fh:
        nsp1 = json.load(fh)
    ce_p95 = nsp1["gate"]["random_p95_inbatch_full"]["ce"]
    ce_i_bar = max(float(ce_p95), float(nsp1["gate"]["i_line_recorded"]))
    cells = {c["name"]: c for c in nsp1["cells"]
             if c["exit_regime"] == "ce" and c.get("status") == "ok"}
    return gate, ce_i_bar, cells, nsp1["trials_ledger"]


def build_family_a(close, idx, syms):
    """OAT +- grid around center (5,20,60); params={} engine default sizing."""
    grid = [(5, 20, 60), (3, 20, 60), (10, 20, 60), (5, 10, 60),
            (5, 40, 60), (5, 20, 40), (5, 20, 120)]
    out = []
    for a, b, c in grid:
        pos = pd.DataFrame({s: trend.triple_ma(close[s], a, b, c)
                            for s in syms}, index=idx).fillna(0)
        out.append((f"triple_ma_{a}_{b}_{c}", (pos > 0), (pos <= 0), {},
                    f"MA({a},{b},{c})"))
    return out


def build_family_b(close, idx):
    """OAT +- grid around (win252,k5,r20); sizing=round(0.95/k,4)."""
    grid = [(252, 5, 20, 200), (126, 5, 20, 100), (504, 5, 20, 400),
            (252, 3, 20, 200), (252, 8, 20, 200), (252, 5, 10, 200),
            (252, 5, 40, 200)]
    out = []
    for win, k, r, mp in grid:
        score = close / close.rolling(win, min_periods=mp).max()
        w = _topk_frozen(score, k, r)
        params = {"max_positions": k,
                  "position_size_pct": round(0.95 / k, 4)}
        out.append((f"high252_w{win}_k{k}_r{r}", w, (w <= 0), params,
                    f"win={win} mp={mp} k={k} rebal={r}"))
    return out


def yearly_returns(equity: pd.Series) -> dict:
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    return out


def register_trader(tid, name, school, entry_desc, sizing_desc, r1, cost2,
                    ledger_note):
    """Only called on G2 pass (pre-reg sec.4). Mirrors VOLATILITY-CE-01."""
    today = time.strftime("%Y-%m-%d")
    eq = r1["eq"]
    is_ = seg_metrics(eq[eq.index < pd.Timestamp(OOS_START)])
    trader = {
        "id": tid, "name": name, "school": school,
        "author": "researcher-g2nsp1", "created": today,
        "evidence_cutoff": EVIDENCE_CUT, "level": "INTERN",
        "params": {"entry": entry_desc, **sizing_desc,
                   "time_decay_period": 25, "time_decay_threshold": 0.05,
                   "trailing_stop_activate": 0.1},
        "exit_overrides": {"loss_time_days": 16},
        "repro": {"script": "scripts/g2_nsp1.py",
                  "note": "non-bridged exit field loss_time_days requires "
                          "the runtime ExitConfig factory patch "
                          "(live.paper ExitPatch); engine files untouched; "
                          "params-bridge kwargs take precedence"},
        "backtest": {
            "in_sample": {"sharpe": is_["sharpe"],
                          "max_dd": is_["max_drawdown"],
                          "annual": is_["annual_return"],
                          "trades": r1["n_trades"] - r1["oos_trades"]},
            "out_sample": {"sharpe": r1["oos"]["sharpe"],
                           "max_dd": r1["oos"]["max_drawdown"],
                           "annual": r1["oos"]["annual_return"],
                           "trades": r1["oos_trades"]},
            "cost_x2": {"sharpe": cost2["full"]["sharpe"],
                        "oos_sharpe": cost2["oos"]["sharpe"],
                        "survive": True, "note": ledger_note},
        },
        "paper": {"months_tracked": 0, "monthly_returns": [],
                  "current_dd": 0.0, "as_of": today, "cutoff": EVIDENCE_CUT},
        "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": 0},
        "status_history": [{"date": today, "from": None, "to": "INTERN",
                            "note": ledger_note}],
    }
    path = os.path.join(PATHS.root, "firm", "traders", f"{tid}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(trader, fh, indent=2, ensure_ascii=False)
    print(f"registered trader: {path} -- SIGNAL_BUILDERS wiring required")
    return tid


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    print("patch self-tests: PASS")

    gate, ce_i_bar, anchors_cells, prior_ledger = load_recorded()
    vi_bar = float(gate["vi_full_sharpe_gt"])
    print(f"recorded constants: CE i-line={ce_i_bar}  vi={vi_bar}")
    fam_meta = {
        "A": {"cand": "triple_ma_5_20_60",
              "exp_full": anchors_cells["triple_ma_5_20_60"]["full"]["sharpe"],
              "ref_oos": anchors_cells["triple_ma_5_20_60"]["oos"]["sharpe"],
              "exp_x2": anchors_cells["triple_ma_5_20_60"]["x2_full_sharpe"]},
        "B": {"cand": "high252_prox_top5_r20",
              "exp_full": anchors_cells["high252_prox_top5_r20"]["full"]["sharpe"],
              "ref_oos": anchors_cells["high252_prox_top5_r20"]["oos"]["sharpe"],
              "exp_x2": anchors_cells["high252_prox_top5_r20"]["x2_full_sharpe"]},
    }
    print(f"  A anchor full={fam_meta['A']['exp_full']} "
          f"ref_oos={fam_meta['A']['ref_oos']} x2={fam_meta['A']['exp_x2']}")
    print(f"  B anchor full={fam_meta['B']['exp_full']} "
          f"ref_oos={fam_meta['B']['ref_oos']} x2={fam_meta['B']['exp_x2']}")

    prices = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    raw_end = max(df.index[-1] for df in prices.values())
    if raw_end > cut:
        prices = {s: df.loc[:cut].copy() for s, df in prices.items()}
        print(f"panels truncated to evidence cut {EVIDENCE_CUT} "
              f"(raw end {raw_end.date()})")
    P = build_panels(prices)
    close = P["close"]
    idx, syms = close.index, list(close.columns)
    data_end = str(idx[-1].date())
    print(f"core48: {len(syms)} syms, window {idx[0].date()} .. {data_end}")

    def green_clauses(r, ref_oos):
        f_, o_ = r["full"], r["oos"]
        c = {
            "i_beats_rand_p95": f_["sharpe"] > ce_i_bar,
            "ii_ann_pos": f_["annual_return"] > gate["ii_ann_gt"],
            "iii_dd_ok": f_["max_drawdown"] >= gate["iii_dd_min"],
            "iv_trades_ok": r["n_trades"] >= gate["iv_trades_min"],
            "v_oos_ok": (o_["sharpe"] > gate["v_oos_sharpe_gt"]
                         and o_["annual_return"] > gate["v_oos_ann_gt"]),
            "vi_beats_passive": f_["sharpe"] > vi_bar,
        }
        decay_ok = o_["sharpe"] >= DECAY_FLOOR * ref_oos
        return c, decay_ok, all(c.values()) and decay_ok

    rows, fam_points, centers, cost_runs = [], {"A": [], "B": []}, {}, {}
    grids = {"A": build_family_a(close, idx, syms),
             "B": build_family_b(close, idx)}

    # ---------- neighborhood grids (7 + 7, 1x, CE regime) ----------
    for famkey, meta in fam_meta.items():
        print(f"family {famkey} ({meta['cand']}) neighborhood, "
              f"ref_oos={meta['ref_oos']}...")
        for name, entry, exit_, params, desc in grids[famkey]:
            r = run_cell(prices, idx, entry, exit_, params, ce=True)
            c, decay, green = green_clauses(r, meta["ref_oos"])
            is_center = name == ("triple_ma_5_20_60" if famkey == "A"
                                 else "high252_w252_k5_r20")
            yr = yearly_returns(r["eq"]) if is_center else {}
            pt = {"point": name, "desc": desc, "params": params,
                  "clauses": c, "decay_ok": decay, "green": green,
                  "full": r["full"], "oos": r["oos"],
                  "n_trades": r["n_trades"], "oos_trades": r["oos_trades"]}
            fam_points[famkey].append(pt)
            rows.append({"family": famkey, "point": name, "cost_mult": 1,
                         "params": json.dumps(params), **c,
                         "decay_ok": decay, "green": green,
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "worst_year": min(yr.values()) if yr else "",
                         "yearly": json.dumps(yr) if yr else ""})
            if is_center:
                centers[famkey] = {"r": r, "entry": entry, "exit": exit_,
                                   "params": params}
            print(f"  {name:<22} full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} "
                  f"trades={r['n_trades']:<5} "
                  f"{'GREEN' if green else 'RED'}")

    # ---------- cost stress x2/x3 on both centers ----------
    print("cost stress x2/x3 on centers...")
    for famkey, meta in fam_meta.items():
        ce_ = centers[famkey]
        for m in COST_MULTS:
            r = run_cell(prices, idx, ce_["entry"], ce_["exit"],
                         ce_["params"], ce=True, cost_mult=m)
            survive = bool(r["full"]["sharpe"] > vi_bar
                           and r["oos"]["sharpe"] >= DECAY_FLOOR * meta["ref_oos"])
            x2_check = (abs(r["full"]["sharpe"] - float(meta["exp_x2"]))
                        < ANCHOR_TOL) if m == 2 else None
            cost_runs[f"{famkey}_x{m}"] = {
                "center": meta["cand"], "cost_mult": m,
                "full": r["full"], "oos": r["oos"], "n_trades": r["n_trades"],
                "survive_x2_clause": survive,
                "x2_matches_nsp1_info_column": x2_check,
                "note": ("G2 clause" if m == 2
                         else "recorded only (G4 reference)")}
            rows.append({"family": famkey, "point": f"{meta['cand']}_costx{m}",
                         "cost_mult": m, "params": json.dumps(ce_["params"]),
                         "i_beats_rand_p95": r["full"]["sharpe"] > ce_i_bar,
                         "ii_ann_pos": r["full"]["annual_return"] > 0,
                         "iii_dd_ok": r["full"]["max_drawdown"] >= gate["iii_dd_min"],
                         "iv_trades_ok": r["n_trades"] >= gate["iv_trades_min"],
                         "v_oos_ok": r["oos"]["sharpe"] > 0 and r["oos"]["annual_return"] > 0,
                         "vi_beats_passive": r["full"]["sharpe"] > vi_bar,
                         "decay_ok": r["oos"]["sharpe"] >= DECAY_FLOOR * meta["ref_oos"],
                         "green": survive if m == 2 else "",
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "worst_year": "", "yearly": ""})
            print(f"  {famkey} x{m}: full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} survive={survive}"
                  + (f" nsp1_x2_match={x2_check}" if x2_check is not None else ""))

    # ---------- anchors + verdicts ----------
    print("\nverdicts...")
    verdicts, registered = {}, []
    for famkey, meta in fam_meta.items():
        pts = fam_points[famkey]
        all_green = all(p["green"] for p in pts)
        got = centers[famkey]["r"]["full"]["sharpe"]
        anchored = {"expected": meta["exp_full"], "got": got,
                    "ok": abs(got - float(meta["exp_full"])) < ANCHOR_TOL}
        cost2_ok = bool(cost_runs[f"{famkey}_x2"]["survive_x2_clause"])
        yr_tab = yearly_returns(centers[famkey]["r"]["eq"])
        worst = min(yr_tab.values())
        yearly_ok = worst > CRASH_YEAR
        red_points = [p["point"] for p in pts if not p["green"]]
        g2_pass = bool(all_green and anchored["ok"] and cost2_ok and yearly_ok)
        verdicts[famkey] = {
            "candidate": meta["cand"], "g2_pass": g2_pass,
            "neighborhood_all_green": all_green,
            "n_points": len(pts), "red_points": red_points,
            "center_anchor": anchored, "cost_x2_survive": cost2_ok,
            "yearly_returns": yr_tab, "worst_year": worst,
            "yearly_no_crash": yearly_ok,
        }
        v = verdicts[famkey]
        print(f"  {famkey} ({meta['cand']}): G2="
              f"{'PASS' if g2_pass else 'FAIL'} (green={all_green} "
              f"anchor={anchored['ok']} cost2x={cost2_ok} yearly={yearly_ok})")
        if red_points:
            print(f"    red points: {red_points}")
        if g2_pass:  # pre-reg sec.4 pass branch (prior: <=5%)
            cost2 = cost_runs[f"{famkey}_x2"]
            note = (f"G2_NSP1 pass: 7-pt neighborhood all green + anchor "
                    f"reproduced + cost x2 survive + no crash year. "
                    f"i-line 0.4229/6 clauses, ledger N="
                    f"{ledger_head()['total'] + BATCH_N}. "  # T-03-F3 data-driven chain head
                    f"Evidence: research/G2_NSP1.md, "
                    f"research/g2_nsp1_results.csv, results/g2_nsp1.json")
            if famkey == "A":
                registered.append(register_trader(
                    "TREND-CE-01", "三线软化一号", "trend",
                    "triple_ma(5,20,60) state>0, daily",
                    {"max_positions": 5, "position_size_pct": 0.10},
                    centers[famkey]["r"], cost2, note))
            else:
                registered.append(register_trader(
                    "HIGH252-CE-01", "高点软化一号", "high252_proximity",
                    "close/rolling(252,mp200).max() top5 frozen 20d",
                    {"max_positions": 5, "position_size_pct": 0.19},
                    centers[famkey]["r"], cost2, note))
    anchor_ok = all(v["center_anchor"]["ok"] for v in verdicts.values())
    void = not anchor_ok   # pre-reg sec.5 hard gate

    # ---------- CSV ----------
    csv_path = os.path.join(PATHS.root, "research", "g2_nsp1_results.csv")
    cols = ["family", "point", "cost_mult", "params", "i_beats_rand_p95",
            "ii_ann_pos", "iii_dd_ok", "iv_trades_ok", "v_oos_ok",
            "vi_beats_passive", "decay_ok", "green", "full_sharpe",
            "full_ann", "full_dd", "n_trades", "oos_sharpe", "oos_ann",
            "worst_year", "yearly"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    # ---------- JSON ----------
    ledger = append_ledger(
        "G2-NSP1-deepening", BATCH_N, "g2_nsp1.json",
        note="7+7 OAT neighborhood 1x + 2 centers x(x2,x3) cost stress; "
             "pre-registered n=18 (research/G2_NSP1.md sec.7); "
             "gates on recorded constants (CE i-line 0.4229, vi 0.4004); "
             "T-03-F3 unified dict schema (flat chain narrative retired)")
    out = {
        "batch": "G2-NSP1-deepening",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/G2_NSP1.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(syms),
                     "window": f"{idx[0].date()} .. {data_end}",
                     "evidence_cutoff": EVIDENCE_CUT},
        "oos_start": OOS_START,
        "void": void,
        "constants": {"g1_prime_gate": gate, "ce_i_line": ce_i_bar,
                      "vi_bar": vi_bar, "decay_floor": DECAY_FLOOR,
                      "ref_oos_A": fam_meta["A"]["ref_oos"],
                      "ref_oos_B": fam_meta["B"]["ref_oos"],
                      "crash_year": CRASH_YEAR, "anchor_tol": ANCHOR_TOL},
        "families": fam_points, "cost_stress": cost_runs,
        "verdicts_g2": verdicts, "traders_registered": registered,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(rows), "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "g2_nsp1.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"runs={len(rows)} elapsed={time.time()-t0:.0f}s "
          f"ledger N={sum(x['n'] for x in ledger)}")
    print(f"\n===== G2_NSP1 verdicts =====")
    for k, v in verdicts.items():
        print(f"  {k} ({v['candidate']}): "
              f"{'PASS' if v['g2_pass'] else 'FAIL'}")
    if registered:
        print(f"  traders registered: {registered} "
              f"-- SIGNAL_BUILDERS wiring REQUIRED (pre-reg sec.4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
