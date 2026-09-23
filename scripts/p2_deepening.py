"""J10 P2 survivor deepening -> G2 factory gate (research/G2_DEEPENING.md).

PRE-REGISTERED before running (2026-09-23 09:58, see research/G2_DEEPENING.md).
Do NOT tune thresholds after seeing results (p-hacking ban, iron rule 3).

Two G1'-survivor families, same engine / core48 bare-code pool / 13bp cost /
OOS split 2025-01-01 / one-shot serial run (27 backtests):
  A. low_vol_long   grid = lookback {40,60,80,120} x top_k {3,5,8}
     sizing control: constant 50% total target exposure
     (max_positions=top_k, position_size_pct=round(0.5/top_k,4));
     center (60,5) must reproduce P1 bit-for-bit (engine defaults 5x10%).
  B. composite Top-N rotation grid = N {3,5,8} x rebal {10,20,40},
     sizing = round(0.95/N,4) (P1 convention); centers (5,20),(8,20)
     must reproduce P1. Family judged as ONE unit.

Per-point green = all six G1' clauses (constants loaded from
results/p2_calibration.json, unchanged) AND OOS Sharpe >= 0.70 x family
reference OOS (reference = best G1' passer OOS of the family, from P1 CSV).

Cost stress x2/x3 on family centers: runtime FeeSchedule class-attribute
patch (engine files untouched, restored after). x2 survive (G2 clause) =
full Sharpe > 0.4004 AND OOS Sharpe >= 0.70 x reference. x3 recorded only.

Yearly stability (G2 clause): no calendar year return <= -30% on center
1x equity (2026 partial, honest).

G2 pass == neighborhood all green + centers anchored (|dSharpe|<0.002)
+ cost x2 survive + no crash year. Passer families are registered as
firm/traders/<ID>.json (INTERN level, one trader per family; for composite
the center with the higher G1' full Sharpe represents the family -- no
double-counting of one alpha source).

Products: research/p2_deepening.csv + results/p2_survivors.json.
Trial ledger: 643 (prior) + 27 (this batch) = 670.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
import engine.backtester as _eb
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown
from knowledge.rules import FeeSchedule
from strategies import volatility
from strategies.composite_rotation import top_n_rotation

OOS_START = "2025-01-01"
LOWVOL_LOOKBACKS = [40, 60, 80, 120]
LOWVOL_TOPK = [3, 5, 8]
COMP_NS = [3, 5, 8]
COMP_REBALS = [10, 20, 40]
DECAY_FLOOR = 0.70          # OOS decay < 30% vs family reference
ANCHOR_TOL = 0.002          # center must reproduce P1 full Sharpe
CRASH_YEAR = -0.30
COST_MULTS = [2, 3]
MIN_TRADES = 30
MAX_DD = -0.35


def load_core(min_listing_days: int = 60) -> dict:
    out = {}
    daily = PATHS.daily_dir
    for f in sorted(os.listdir(daily)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < min_listing_days:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        if "amount" not in df.columns:
            df["amount"] = df["volume"] * df["close"]
        out[f[:-4]] = df[["open", "high", "low", "close", "volume", "amount"]]
    return out


def seg_metrics(equity: pd.Series, start: str | None = None,
                end: str | None = None) -> dict:
    seg = equity
    if start:
        seg = seg[seg.index >= start]
    if end:
        seg = seg[seg.index < end]
    if len(seg) < 20:
        return {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    return {
        "sharpe": round(float(sharpe(seg)), 4),
        "annual_return": round(float(annual_return(seg)), 4),
        "max_drawdown": round(float(max_drawdown(seg)), 4),
    }


def run_one(prices, idx, entry, exit_, params, name):
    res = run_backtest(prices, params, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    full = res["metrics"]
    oos = seg_metrics(eq, OOS_START)
    oos_trades = sum(1 for t in res["trades"] if str(t["date"]) >= OOS_START)
    return {"name": name, "full": full, "oos": oos, "equity": eq,
            "trades": res["trades"],
            "n_trades": full["num_trades"], "oos_trades": oos_trades}


def yearly_returns(equity: pd.Series) -> dict:
    """Calendar-year simple returns from the equity curve (honest partials)."""
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    return out


class CostPatch:
    """Runtime stress profile: multiply fee components by `mult`.

    Replaces the FeeSchedule NAME inside engine.backtester with a factory
    returning a stressed instance. (Class-attribute patching does NOT work
    here: dataclass __init__ bakes field defaults into the function signature
    at class creation, so FeeSchedule() ignores later class-attr edits --
    verified empirically 2026-09-23.) Engine/knowledge files untouched,
    name always restored. Stress only ever makes costs STRICTER.
    """

    def __init__(self, mult: float):
        self.mult = mult
        self.orig = None

    def __enter__(self):
        self.orig = _eb.FeeSchedule
        Orig, m = self.orig, self.mult
        _eb.FeeSchedule = lambda: Orig(
            commission_rate=Orig.commission_rate * m,
            handling_fee=Orig.handling_fee * m,
            supervision_fee=Orig.supervision_fee * m,
            slippage_a=Orig.slippage_a * m)
        return self

    def __exit__(self, *exc):
        _eb.FeeSchedule = self.orig
        return False


def main():
    t0 = time.time()
    print("loading calibration constants (results/p2_calibration.json)...")
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    p95_full = calib["g1_prime_gate"]["i_full_sharpe_gt"]
    vi_bar = calib["g1_prime_gate"]["vi_full_sharpe_gt"]
    skill_bar = calib["g1_prime_gate"]["effective_skill_bar"]
    print(f"  G1' constants: i>{p95_full}  vi>{vi_bar}  skill_bar={skill_bar}")

    print("loading P1 anchor rows (research/strategy_rank.csv)...")
    with open(os.path.join(PATHS.root, "research", "strategy_rank.csv"),
              encoding="utf-8") as fh:
        rank = {r["strategy"]: r for r in csv.DictReader(fh)}
    anchor = {}
    for s in ("low_vol_long_60", "composite_top5", "composite_top8"):
        anchor[s] = {"full_sharpe": float(rank[s]["sharpe"]),
                     "oos_sharpe": float(rank[s]["oos_sharpe"]),
                     "n_trades": int(rank[s]["n_trades"])}
    print(f"  {json.dumps(anchor)}")

    print("loading core universe (bare codes)...")
    prices = load_core()
    print(f"  {len(prices)} ETFs")
    P = {f: pd.DataFrame({s: df[f] for s, df in prices.items()}).sort_index().ffill()
         for f in ["open", "high", "low", "close", "volume", "amount"]}
    close, high, low = P["close"], P["high"], P["low"]
    idx = close.index

    # family references (pre-registered: best G1' passer OOS of the family)
    ref_lowvol_oos = anchor["low_vol_long_60"]["oos_sharpe"]
    ref_comp_oos = max(anchor["composite_top5"]["oos_sharpe"],
                       anchor["composite_top8"]["oos_sharpe"])
    print(f"  family OOS references: low_vol={ref_lowvol_oos} composite={ref_comp_oos}")

    def green_clauses(r, ref_oos):
        f_, o_ = r["full"], r["oos"]
        c = {
            "i_beats_rand_p95": f_["sharpe"] > p95_full,
            "ii_ann_pos": f_["annual_return"] > 0,
            "iii_dd_ok": f_["max_drawdown"] >= MAX_DD,
            "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
            "v_oos_ok": o_["sharpe"] > 0 and o_["annual_return"] > 0,
            "vi_beats_passive": f_["sharpe"] > vi_bar,
        }
        decay_ok = o_["sharpe"] >= DECAY_FLOOR * ref_oos
        return c, decay_ok, all(c.values()) and decay_ok

    rows = []   # CSV rows
    fam = {"low_vol": [], "composite": []}
    centers = {}  # (family, key) -> run dict at 1x

    # ---------- family A: low_vol_long grid (12) ----------
    print("family A: low_vol_long grid (12 points)...")
    for n in LOWVOL_LOOKBACKS:
        for k in LOWVOL_TOPK:
            t1 = time.time()
            w = volatility.low_vol_long(close, n, top_k=k)
            params = {"max_positions": k, "position_size_pct": round(0.5 / k, 4)}
            r = run_one(prices, idx, w, (w <= 0), params,
                        f"lowvol_n{n}_k{k}")
            c, decay, green = green_clauses(r, ref_lowvol_oos)
            yr = yearly_returns(r["equity"]) if (n, k) == (60, 5) else {}
            rows.append({"family": "low_vol", "point": r["name"],
                         "cost_mult": 1,
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
            fam["low_vol"].append({"point": r["name"], "params": params,
                                   "clauses": c, "decay_ok": decay,
                                   "green": green, "full": r["full"],
                                   "oos": r["oos"], "n_trades": r["n_trades"],
                                   "oos_trades": r["oos_trades"]})
            if (n, k) == (60, 5):
                centers[("low_vol", "low_vol_long_60")] = r
            print(f"  lowvol_n{n}_k{k}  full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} "
                  f"{'GREEN' if green else 'RED'} ({time.time()-t1:.1f}s)")

    # ---------- family B: composite grid (9) ----------
    print("family B: composite Top-N grid (9 points)...")
    for nn in COMP_NS:
        for rb in COMP_REBALS:
            t1 = time.time()
            w = top_n_rotation(high, low, close, top_n=nn, rebal_days=rb)
            params = {"max_positions": nn,
                      "position_size_pct": round(0.95 / nn, 4)}
            r = run_one(prices, idx, w, (w <= 0), params,
                        f"comp_N{nn}_r{rb}")
            c, decay, green = green_clauses(r, ref_comp_oos)
            is_center = (nn, rb) in ((5, 20), (8, 20))
            yr = yearly_returns(r["equity"]) if is_center else {}
            rows.append({"family": "composite", "point": r["name"],
                         "cost_mult": 1,
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
            fam["composite"].append({"point": r["name"], "params": params,
                                     "clauses": c, "decay_ok": decay,
                                     "green": green, "full": r["full"],
                                     "oos": r["oos"], "n_trades": r["n_trades"],
                                     "oos_trades": r["oos_trades"]})
            if is_center:
                centers[("composite", f"composite_top{nn}")] = r
            print(f"  comp_N{nn}_r{rb}  full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} "
                  f"{'GREEN' if green else 'RED'} ({time.time()-t1:.1f}s)")

    # ---------- cost stress on centers (6 runs) ----------
    print("cost stress x2/x3 on centers...")
    cost_runs = {}
    for (famkey, key), r1x in centers.items():
        ref_oos = ref_lowvol_oos if famkey == "low_vol" else ref_comp_oos
        # rebuild the same entry/exit matrices deterministically
        if famkey == "low_vol":
            w = volatility.low_vol_long(close, 60, top_k=5)
            params = {"max_positions": 5, "position_size_pct": 0.10}
        else:
            nn = 8 if key == "composite_top8" else 5
            w = top_n_rotation(high, low, close, top_n=nn, rebal_days=20)
            params = {"max_positions": nn,
                      "position_size_pct": round(0.95 / nn, 4)}
        for m in COST_MULTS:
            with CostPatch(m):
                r = run_one(prices, idx, w, (w <= 0), params,
                            f"{key}_costx{m}")
            survive = bool(r["full"]["sharpe"] > vi_bar
                           and r["oos"]["sharpe"] >= DECAY_FLOOR * ref_oos)
            cost_runs[f"{key}_x{m}"] = {
                "family": famkey, "center": key, "cost_mult": m,
                "full": r["full"], "oos": r["oos"], "survive_x2_clause": survive,
                "note": ("G2 clause" if m == 2 else "recorded only (G4 reference)")}
            rows.append({"family": famkey, "point": f"{key}_costx{m}",
                         "cost_mult": m, "params": json.dumps(params),
                         "i_beats_rand_p95": r["full"]["sharpe"] > p95_full,
                         "ii_ann_pos": r["full"]["annual_return"] > 0,
                         "iii_dd_ok": r["full"]["max_drawdown"] >= MAX_DD,
                         "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
                         "v_oos_ok": r["oos"]["sharpe"] > 0 and r["oos"]["annual_return"] > 0,
                         "vi_beats_passive": r["full"]["sharpe"] > vi_bar,
                         "decay_ok": r["oos"]["sharpe"] >= DECAY_FLOOR * ref_oos,
                         "green": survive if m == 2 else "",
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "worst_year": "", "yearly": ""})
            print(f"  {key} x{m}: full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} "
                  f"survive={survive}")

    # ---------- anchors, yearly, verdicts ----------
    print("\nverdicts...")
    verdicts = {}
    for famkey in ("low_vol", "composite"):
        pts = fam[famkey]
        all_green = all(p["green"] for p in pts)
        ref_oos = ref_lowvol_oos if famkey == "low_vol" else ref_comp_oos
        keys = (["low_vol_long_60"] if famkey == "low_vol"
                else ["composite_top5", "composite_top8"])
        anchored = {}
        for key in keys:
            exp = anchor[key]["full_sharpe"]
            got = centers[(famkey, key)]["full"]["sharpe"]
            anchored[key] = {"expected": exp, "got": got,
                             "ok": abs(got - exp) < ANCHOR_TOL}
        anchor_ok = all(v["ok"] for v in anchored.values())
        cost2_ok = all(cost_runs[f"{k}_x2"]["survive_x2_clause"] for k in keys)
        yearly_tables = {k: yearly_returns(centers[(famkey, k)]["equity"])
                         for k in keys}
        crash = {k: min(y.values()) for k, y in yearly_tables.items()}
        yearly_ok = all(v > CRASH_YEAR for v in crash.values())
        red_points = [p["point"] for p in pts if not p["green"]]
        verdicts[famkey] = {
            "g2_pass": bool(all_green and anchor_ok and cost2_ok and yearly_ok),
            "neighborhood_all_green": all_green,
            "n_points": len(pts), "red_points": red_points,
            "centers_anchored": anchored, "anchor_ok": anchor_ok,
            "cost_x2_survive": cost2_ok,
            "yearly_returns": yearly_tables,
            "worst_year_per_center": crash,
            "yearly_no_crash": yearly_ok,
        }
        v = verdicts[famkey]
        print(f"  {famkey}: G2={'PASS' if v['g2_pass'] else 'FAIL'} "
              f"(green={all_green} anchor={anchor_ok} cost2x={cost2_ok} "
              f"yearly={yearly_ok})")
        if red_points:
            print(f"    red points: {red_points}")

    # ---------- CSV ----------
    csv_path = os.path.join(PATHS.root, "research", "p2_deepening.csv")
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

    # ---------- trader registration (only for G2 passers) ----------
    registered = []
    today = time.strftime("%Y-%m-%d")
    if verdicts["low_vol"]["g2_pass"]:
        r = centers[("low_vol", "low_vol_long_60")]
        eq = r["equity"]
        is_ = seg_metrics(eq, None, OOS_START)
        trader = {
            "id": "VOLATILITY-001", "name": "低波一号", "school": "volatility",
            "author": "researcher-j10", "created": today, "level": "INTERN",
            "params": {"n": 60, "top_k": 5, "max_positions": 5,
                       "position_size_pct": 0.10},
            "backtest": {
                "in_sample": {"sharpe": is_["sharpe"], "max_dd": is_["max_drawdown"],
                              "annual": is_["annual_return"],
                              "trades": r["n_trades"] - r["oos_trades"]},
                "out_sample": {"sharpe": r["oos"]["sharpe"],
                               "max_dd": r["oos"]["max_drawdown"],
                               "annual": r["oos"]["annual_return"],
                               "trades": r["oos_trades"]},
            },
            "paper": {"months_tracked": 0, "monthly_returns": [], "current_dd": 0},
            "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": 0},
            "status_history": [
                {"date": today, "from": None, "to": "INTERN",
                 "note": "G2 factory gate pass: G1' margin +0.358 over 0.4004; "
                         "12-pt neighborhood all green; cost x2 survive; "
                         "no crash year. Evidence: research/G2_DEEPENING.md, "
                         "research/p2_deepening.csv, results/p2_survivors.json, "
                         "ledger N=670"},
            ],
            "notes": "low_vol_long(60,5) Top-5 lowest 60d-vol rotation, "
                     "50% target exposure, engine exit rules untouched",
        }
        path = os.path.join(PATHS.root, "firm", "traders", "VOLATILITY-001.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(trader, fh, indent=2, ensure_ascii=False)
        registered.append("VOLATILITY-001")
        print(f"registered trader: {path}")
    if verdicts["composite"]["g2_pass"]:
        rep = "composite_top8" if (anchor["composite_top8"]["full_sharpe"]
                                   >= anchor["composite_top5"]["full_sharpe"]) \
            else "composite_top5"
        r = centers[("composite", rep)]
        nn = 8 if rep == "composite_top8" else 5
        eq = r["equity"]
        is_ = seg_metrics(eq, None, OOS_START)
        trader = {
            "id": "COMPOSITE-001", "name": "复合一号", "school": "composite",
            "author": "researcher-j10", "created": today, "level": "INTERN",
            "params": {"top_n": nn, "rebal_days": 20, "max_positions": nn,
                       "position_size_pct": round(0.95 / nn, 4)},
            "backtest": {
                "in_sample": {"sharpe": is_["sharpe"], "max_dd": is_["max_drawdown"],
                              "annual": is_["annual_return"],
                              "trades": r["n_trades"] - r["oos_trades"]},
                "out_sample": {"sharpe": r["oos"]["sharpe"],
                               "max_dd": r["oos"]["max_drawdown"],
                               "annual": r["oos"]["annual_return"],
                               "trades": r["oos_trades"]},
            },
            "paper": {"months_tracked": 0, "monthly_returns": [], "current_dd": 0},
            "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": 0},
            "status_history": [
                {"date": today, "from": None, "to": "INTERN",
                 "note": f"G2 factory gate pass, family representative {rep} "
                         f"(one trader per alpha family); 9-pt grid all green; "
                         "cost x2 survive; no crash year. Evidence: "
                         "research/G2_DEEPENING.md, research/p2_deepening.csv, "
                         "results/p2_survivors.json, ledger N=670"},
            ],
            "notes": "J6 composite factor Top-N rotation, 20d non-overlap rebal",
        }
        path = os.path.join(PATHS.root, "firm", "traders", "COMPOSITE-001.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(trader, fh, indent=2, ensure_ascii=False)
        registered.append("COMPOSITE-001")
        print(f"registered trader: {path}")

    # ---------- JSON ----------
    out = {
        "batch": "P2-survivor-deepening-G2",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/G2_DEEPENING.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": OOS_START,
        "constants": {
            "g1_prime_i_bar": p95_full, "g1_prime_vi_bar": vi_bar,
            "effective_skill_bar": skill_bar,
            "decay_floor": DECAY_FLOOR,
            "ref_oos_low_vol": ref_lowvol_oos,
            "ref_oos_composite": ref_comp_oos,
            "crash_year": CRASH_YEAR, "min_trades": MIN_TRADES,
            "max_dd": MAX_DD,
        },
        "families": {k: {"points": v} for k, v in fam.items()},
        "cost_stress": cost_runs,
        "verdicts_g2": verdicts,
        "traders_registered": registered,
        "trials_ledger": [
            {"batch": "432-MA-param-grid (pre-plan)", "n": 432},
            {"batch": "J6-factor-IC-study", "n": 30},
            {"batch": "P1-strategy-screen", "n": 59},
            {"batch": "P2-null-calibration", "n": 122},
            {"batch": "P2-survivor-deepening", "n": len(rows),
             "note": "12 low_vol grid + 9 composite grid + 6 cost-stress runs"},
        ],
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(rows), "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "p2_survivors.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    print(f"\n===== G2 verdicts =====")
    for k, v in verdicts.items():
        print(f"  {k}: {'PASS' if v['g2_pass'] else 'FAIL'}")
    if registered:
        print(f"  traders registered: {registered}")
    print(f"total elapsed: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
