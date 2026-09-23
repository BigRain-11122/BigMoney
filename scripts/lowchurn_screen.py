"""J14 low-churn structural family -> one-shot G1'+G2 acceptance.

PRE-REGISTERED before running (research/LOW_CHURN_FAMILY.md, written first).
Do NOT tune thresholds after seeing results (p-hacking ban, iron rule 3).

Three families, same engine / core48 bare-code pool / 13bp cost /
OOS split 2025-01-01 / one-shot serial run (<=26 backtests):
  LC-A  low_vol rebal-frozen grid: (n, rebal) in {60,80} x {20,40,60},
        k=5 fixed, sizing 5x10%; plus the daily (60,5) anchor point
        (must reproduce G2 full Sharpe 0.7583). Full G2 template.
  LC-B  composite low-churn wing: N {3,5,8} x rebal {40,60,80},
        sizing round(0.95/N,4); anchor N5_r40 (must reproduce 0.8174).
        Full G2 template.
  LC-C  exit-param churn-axis probe on low_vol daily (60,5) base:
        4 single-axis variants (tp-sparser / losstime16 / decay-loose /
        trail-late). Axis-probe verdict, NO trader registration.

Green = six G1' clauses (constants from results/p2_calibration.json,
unchanged) AND OOS Sharpe >= 0.70 x family reference (low_vol 1.3631,
composite 1.0405 -- bars do not move for low-churn variants).

Cost stress x2 (G2 gate clause) / x3 (recorded) on each family's
representative = argmax full Sharpe among 1x green points. Exit-param
variants use a runtime ExitConfig factory patch (engine files untouched,
params-bridge kwargs take precedence over patch fields); cost stress uses
the FeeSchedule factory patch (G2-proven). Both patches self-tested
before the batch runs (G2 lesson 6.1: patch that does not bite = fake
evidence). No green point -> family FAIL, stress skipped.

Full-G2 passers (LC-A/LC-B only) are registered as firm/traders/<ID>.json
INTERN level. LC-C conditional pass only authorizes next round's
neighborhood expansion.

Products: research/lowchurn_results.csv + results/lowchurn_family.json.
Trial ledger: 670 (prior) + actual runs this batch.
"""
import csv
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
import engine.backtester as _eb
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown
from strategies import volatility
from strategies.composite_rotation import top_n_rotation

OOS_START = "2025-01-01"
DECAY_FLOOR = 0.70
ANCHOR_TOL = 0.002
CRASH_YEAR = -0.30
COST_MULTS = [2, 3]
MIN_TRADES = 30
MAX_DD = -0.35
BASE_PARAMS = {"max_positions": 5, "position_size_pct": 0.10}
COST_X2_RATE = 0.0026082     # G2-recorded stressed single-side cost
COST_X1_RATE = 0.0013041     # G2-recorded baseline single-side cost


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


def seg_metrics(equity: pd.Series, start: str | None = None) -> dict:
    seg = equity[equity.index >= start] if start else equity
    if len(seg) < 20:
        return {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    return {"sharpe": round(float(sharpe(seg)), 4),
            "annual_return": round(float(annual_return(seg)), 4),
            "max_drawdown": round(float(max_drawdown(seg)), 4)}


def yearly_returns(equity: pd.Series) -> dict:
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    return out


class CostPatch:
    """FeeSchedule name-factory stress patch (G2-proven pattern)."""

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


class ExitPatch:
    """ExitConfig name-factory patch: inject NON-bridged exit fields.

    Backtester builds ExitConfig from params-bridge kwargs only
    (take_profit_levels / trailing_activate / time_decay_period /
    time_decay_threshold / position_size_pct / max_positions). Fields the
    bridge cannot reach (take_profit_fractions, loss_time_days, ...) are
    injected here. Precedence: bridge kwargs (from params) WIN over patch
    fields, so a patch never silently overrides an explicit param.
    Exit-rule PRIORITY untouched; engine files untouched; name restored.
    """

    def __init__(self, overrides: dict | None):
        self.overrides = overrides or {}
        self.orig = None

    def __enter__(self):
        if not self.overrides:
            return self
        self.orig = _eb.ExitConfig
        Orig, ov = self.orig, self.overrides

        def factory(**kw):
            return Orig(**{**ov, **kw})

        _eb.ExitConfig = factory
        return self

    def __exit__(self, *exc):
        if self.orig is not None:
            _eb.ExitConfig = self.orig
        return False


def run_one(prices, idx, entry, params, exit_patch=None):
    ctx = ExitPatch(exit_patch) if exit_patch else nullcontext()
    with ctx:
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_trades = sum(1 for t in res["trades"] if str(t["date"]) >= OOS_START)
    return {"full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "equity": eq, "n_trades": res["metrics"]["num_trades"],
            "oos_trades": oos_trades}


def self_test_patches():
    """Gate: patches must bite AND restore (G2 lesson 6.1)."""
    ok = True
    # CostPatch x2 / restore
    with CostPatch(2):
        fee = _eb.FeeSchedule()
        rate = (fee.commission_rate + fee.handling_fee
                + fee.supervision_fee + fee.slippage_a)
        ok &= abs(rate - COST_X2_RATE) < 1e-6
    fee = _eb.FeeSchedule()
    rate = (fee.commission_rate + fee.handling_fee
            + fee.supervision_fee + fee.slippage_a)
    ok &= abs(rate - COST_X1_RATE) < 1e-6
    # ExitPatch inject + bridge-precedence + restore
    with ExitPatch({"loss_time_days": 16, "take_profit_fractions": (0.5, 1.0)}):
        cfg = _eb.ExitConfig(max_positions=7)
        ok &= cfg.loss_time_days == 16 and cfg.take_profit_fractions == (0.5, 1.0)
        ok &= cfg.max_positions == 7          # bridge kwarg wins over nothing
        cfg2 = _eb.ExitConfig(take_profit_fractions=(1/3, 1/3, 1.0))
        ok &= cfg2.take_profit_fractions == (1/3, 1/3, 1.0)  # bridge kwarg WINS
        ok &= cfg2.loss_time_days == 16
    cfg = _eb.ExitConfig()
    ok &= cfg.loss_time_days == 8 and cfg.take_profit_fractions == (1/3, 1/3, 1.0)
    if not ok:
        print("SELF-TEST FAILED -- batch aborted (fake-evidence guard)")
        sys.exit(2)
    print("patch self-tests: PASS (CostPatch x2 bite/restore, ExitPatch "
          "inject/precedence/restore)")


def main():
    t0 = time.time()
    self_test_patches()

    print("loading G1' constants + G2 family references...")
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    p95_full, vi_bar = g["i_full_sharpe_gt"], g["vi_full_sharpe_gt"]
    with open(os.path.join(PATHS.results_dir, "p2_survivors.json"),
              encoding="utf-8") as fh:
        surv = json.load(fh)
    ref_lv = surv["constants"]["ref_oos_low_vol"]      # 1.3631
    ref_cp = surv["constants"]["ref_oos_composite"]    # 1.0405
    anchor_exp = {
        "lowvol_n60_k5_daily": next(p["full"]["sharpe"] for p in
                                    surv["families"]["low_vol"]["points"]
                                    if p["point"] == "lowvol_n60_k5"),
        "comp_N5_r40": next(p["full"]["sharpe"] for p in
                            surv["families"]["composite"]["points"]
                            if p["point"] == "comp_N5_r40"),
    }
    print(f"  i>{p95_full} vi>{vi_bar} ref_lv={ref_lv} ref_cp={ref_cp}")
    print(f"  anchors expected: {anchor_exp}")

    print("loading core universe (bare codes)...")
    prices = load_core()
    print(f"  {len(prices)} ETFs")
    P = {f: pd.DataFrame({s: df[f] for s, df in prices.items()}).sort_index().ffill()
         for f in ["open", "high", "low", "close", "volume", "amount"]}
    close, high, low = P["close"], P["high"], P["low"]
    idx = close.index

    def green_clauses(r, ref_oos):
        f_, o_ = r["full"], r["oos"]
        c = {"i_beats_rand_p95": f_["sharpe"] > p95_full,
             "ii_ann_pos": f_["annual_return"] > 0,
             "iii_dd_ok": f_["max_drawdown"] >= MAX_DD,
             "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
             "v_oos_ok": o_["sharpe"] > 0 and o_["annual_return"] > 0,
             "vi_beats_passive": f_["sharpe"] > vi_bar}
        decay_ok = o_["sharpe"] >= DECAY_FLOOR * ref_oos
        return c, decay_ok, all(c.values()) and decay_ok

    rows, runs = [], {}

    def do_run(fam, point, entry, params, ref_oos, meta, exit_patch=None):
        r = run_one(prices, idx, entry, params, exit_patch)
        c, decay, green = green_clauses(r, ref_oos)
        runs[point] = {"family": fam, "point": point, "params": params,
                       "exit_patch": exit_patch, "meta": meta, "full": r["full"],
                       "oos": r["oos"], "clauses": c, "decay_ok": decay,
                       "green": green, "n_trades": r["n_trades"],
                       "oos_trades": r["oos_trades"], "equity": r["equity"],
                       "ref_oos": ref_oos}
        rows.append({"family": fam, "point": point, "cost_mult": 1,
                     "params": json.dumps(params),
                     "exit_patch": json.dumps(exit_patch) if exit_patch else "",
                     **c, "decay_ok": decay, "green": green,
                     "full_sharpe": r["full"]["sharpe"],
                     "full_ann": r["full"]["annual_return"],
                     "full_dd": r["full"]["max_drawdown"],
                     "avg_hold_days": r["full"].get("avg_hold_days", ""),
                     "n_trades": r["n_trades"],
                     "oos_sharpe": r["oos"]["sharpe"],
                     "oos_ann": r["oos"]["annual_return"],
                     "worst_year": "", "yearly": ""})
        print(f"  {point:<26} full_s={r['full']['sharpe']:>7.3f} "
              f"oos_s={r['oos']['sharpe']:>7.3f} "
              f"trades={r['n_trades']:<5} {'GREEN' if green else 'RED'}")
        return runs[point]

    # ---------- LC-A: low_vol rebal grid (7) ----------
    print("LC-A: low_vol rebal-frozen grid (7 points)...")
    for n, rb in [(60, None), (60, 20), (60, 40), (60, 60),
                  (80, 20), (80, 40), (80, 60)]:
        w = volatility.low_vol_long(close, n, top_k=5, rebal_days=rb)
        tag = "daily" if rb is None else f"r{rb}"
        do_run("LC-A", f"lowvol_n{n}_k5_{tag}", w, BASE_PARAMS, ref_lv,
               {"n": n, "rebal_days": rb, "top_k": 5})

    # ---------- LC-B: composite low-churn wing (9) ----------
    print("LC-B: composite low-churn wing (9 points)...")
    for nn in (3, 5, 8):
        for rb in (40, 60, 80):
            w = top_n_rotation(high, low, close, top_n=nn, rebal_days=rb)
            do_run("LC-B", f"comp_N{nn}_r{rb}", w,
                   {"max_positions": nn,
                    "position_size_pct": round(0.95 / nn, 4)}, ref_cp,
                   {"top_n": nn, "rebal_days": rb})

    # ---------- LC-C: exit-param axis probe (4, base shared with LC-A) ----------
    print("LC-C: exit-param churn-axis probe (4 variants)...")
    w_daily = volatility.low_vol_long(close, 60, top_k=5)  # (60,5) daily base
    lcc_specs = [
        ("lc_c1_tp_sparser",
         {**BASE_PARAMS, "take_profit_levels": (0.10, 0.25)},
         {"take_profit_fractions": (0.5, 1.0)}),
        ("lc_c2_losstime16", dict(BASE_PARAMS), {"loss_time_days": 16}),
        ("lc_c3_decay_loose",
         {**BASE_PARAMS, "time_decay_period": 25, "time_decay_threshold": 0.05},
         None),
        ("lc_c4_trail_late",
         {**BASE_PARAMS, "trailing_stop_activate": 0.10}, None),
    ]
    for point, params, patch in lcc_specs:
        do_run("LC-C", point, w_daily, params, ref_lv,
               {"axis": point}, exit_patch=patch)

    n_runs = len(rows)

    # ---------- cost stress on representatives ----------
    print("cost stress x2/x3 on family representatives (argmax green 1x)...")
    fams = {"LC-A": {"ref": ref_lv}, "LC-B": {"ref": ref_cp}, "LC-C": {"ref": ref_lv}}
    cost_runs = {}
    reps = {}
    for fam, info in fams.items():
        greens = [v for v in runs.values()
                  if v["family"] == fam and v["green"]]
        if not greens:
            print(f"  {fam}: no green point -> family FAIL, stress skipped")
            fams[fam]["rep"] = None
            continue
        rep = max(greens, key=lambda v: v["full"]["sharpe"])
        reps[fam] = rep
        print(f"  {fam} rep: {rep['point']} (full {rep['full']['sharpe']})")
        for m in COST_MULTS:
            # rebuild entry matrix deterministically from rep meta
            meta = rep["meta"]
            if fam == "LC-A":
                w = volatility.low_vol_long(close, meta["n"], top_k=meta["top_k"],
                                            rebal_days=meta["rebal_days"])
            elif fam == "LC-B":
                w = top_n_rotation(high, low, close, top_n=meta["top_n"],
                                   rebal_days=meta["rebal_days"])
            else:
                w = w_daily
            with CostPatch(m):
                r = run_one(prices, idx, w, rep["params"], rep["exit_patch"])
            survive = bool(r["full"]["sharpe"] > vi_bar
                           and r["oos"]["sharpe"] >= DECAY_FLOOR * info["ref"])
            cost_runs[f"{fam}_{rep['point']}_x{m}"] = {
                "family": fam, "rep": rep["point"], "cost_mult": m,
                "full": r["full"], "oos": r["oos"],
                "survive_x2_clause": survive,
                "note": "G2 gate clause" if m == 2 else "recorded only"}
            rows.append({"family": fam, "point": f"{rep['point']}_costx{m}",
                         "cost_mult": m, "params": json.dumps(rep["params"]),
                         "exit_patch": json.dumps(rep["exit_patch"] or ""),
                         "i_beats_rand_p95": r["full"]["sharpe"] > p95_full,
                         "ii_ann_pos": r["full"]["annual_return"] > 0,
                         "iii_dd_ok": r["full"]["max_drawdown"] >= MAX_DD,
                         "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
                         "v_oos_ok": r["oos"]["sharpe"] > 0 and r["oos"]["annual_return"] > 0,
                         "vi_beats_passive": r["full"]["sharpe"] > vi_bar,
                         "decay_ok": r["oos"]["sharpe"] >= DECAY_FLOOR * info["ref"],
                         "green": survive if m == 2 else "",
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "avg_hold_days": r["full"].get("avg_hold_days", ""),
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "worst_year": "", "yearly": ""})
            n_runs += 1
            print(f"    x{m}: full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} survive={survive}")
        fams[fam]["rep"] = rep["point"]

    # ---------- family verdicts ----------
    print("\nverdicts...")
    verdicts = {}
    for fam in ("LC-A", "LC-B"):
        pts = [v for v in runs.values() if v["family"] == fam]
        all_green = all(p["green"] for p in pts)
        akey = ("lowvol_n60_k5_daily" if fam == "LC-A" else "comp_N5_r40")
        exp, got = anchor_exp[akey], runs[akey]["full"]["sharpe"]
        anchor_ok = abs(got - exp) < ANCHOR_TOL
        rep = reps.get(fam)
        cost2_ok = bool(rep and any(
            k.startswith(f"{fam}_") and k.endswith("_x2") and v["survive_x2_clause"]
            for k, v in cost_runs.items()))
        if rep:
            yr = yearly_returns(runs[rep["point"]]["equity"])
            worst = min(yr.values())
        else:
            yr, worst = {}, None
        yearly_ok = worst is not None and worst > CRASH_YEAR
        verdicts[fam] = {
            "template": "full-G2",
            "g2_pass": bool(all_green and anchor_ok and cost2_ok and yearly_ok),
            "neighborhood_all_green": all_green,
            "n_points": len(pts),
            "red_points": [p["point"] for p in pts if not p["green"]],
            "anchor": {"point": akey, "expected": exp, "got": got,
                       "ok": anchor_ok},
            "representative": rep["point"] if rep else None,
            "cost_x2_survive": cost2_ok,
            "yearly_returns": yr, "worst_year": worst,
            "yearly_no_crash": yearly_ok,
        }
        v = verdicts[fam]
        print(f"  {fam}: G2={'PASS' if v['g2_pass'] else 'FAIL'} "
              f"(green={all_green} anchor={anchor_ok} cost2x={cost2_ok} "
              f"yearly={yearly_ok})")
        if v["red_points"]:
            print(f"    red: {v['red_points']}")
    # LC-C axis-probe verdict
    cpts = [v for v in runs.values() if v["family"] == "LC-C"]
    cgreens = [p for p in cpts if p["green"]]
    crep = max(cgreens, key=lambda v: v["full"]["sharpe"]) if cgreens else None
    ccost2 = bool(crep and any(
        k.startswith("LC-C_") and k.endswith("_x2") and v["survive_x2_clause"]
        for k, v in cost_runs.items()))
    if crep:
        yr = yearly_returns(crep["equity"])
        cworst = min(yr.values())
        cyearly = cworst > CRASH_YEAR
    else:
        yr, cworst, cyearly = {}, None, False
    verdicts["LC-C"] = {
        "template": "axis-probe (no trader registration by design)",
        "any_green": bool(cgreens),
        "green_variants": [p["point"] for p in cgreens],
        "representative": crep["point"] if crep else None,
        "cost_x2_survive": ccost2,
        "yearly_returns": yr, "worst_year": cworst, "yearly_no_crash": cyearly,
        "conditional_pass": bool(cgreens and ccost2 and cyearly),
    }
    v = verdicts["LC-C"]
    print(f"  LC-C: conditional={'PASS' if v['conditional_pass'] else 'FAIL'} "
          f"(greens={v['green_variants']} cost2x={ccost2} yearly={cyearly})")

    # ---------- trader registration (full-G2 passers only) ----------
    registered = []
    today = time.strftime("%Y-%m-%d")
    ledger_note = f"ledger N={670 + n_runs}"

    def register(path_id, name, school, rep, iseg, notes):
        r = runs[rep["point"]]
        trader = {
            "id": path_id, "name": name, "school": school,
            "author": "researcher-j14", "created": today, "level": "INTERN",
            "params": {**rep["meta"], **rep["params"]},
            "backtest": {
                "in_sample": {"sharpe": iseg["sharpe"], "max_dd": iseg["max_drawdown"],
                              "annual": iseg["annual_return"],
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
                 "note": "J14 low-churn one-shot G2 pass: G1' six clauses on "
                         "every grid point + anchor reproduction + cost x2 "
                         "survive + no crash year. Evidence: "
                         "research/LOW_CHURN_FAMILY.md, "
                         f"research/lowchurn_results.csv, {ledger_note}"},
            ],
            "notes": notes,
        }
        path = os.path.join(PATHS.root, "firm", "traders", f"{path_id}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(trader, fh, indent=2, ensure_ascii=False)
        registered.append(path_id)
        print(f"registered trader: {path}")

    if verdicts["LC-A"]["g2_pass"]:
        rep = reps["LC-A"]
        register("VOLATILITY-LC-01", "低波慢转一号", "volatility", rep,
                 seg_metrics(runs[rep["point"]]["equity"], None, OOS_START),
                 "low_vol_long(60/80, k=5) rebal-frozen rotation, "
                 "50% target exposure, engine exit rules untouched")
    if verdicts["LC-B"]["g2_pass"]:
        rep = reps["LC-B"]
        register("COMPOSITE-LC-01", "复合慢转一号", "composite", rep,
                 seg_metrics(runs[rep["point"]]["equity"], None, OOS_START),
                 "J6 composite factor Top-N rotation, rebal>=40d non-overlap")

    # ---------- CSV ----------
    csv_path = os.path.join(PATHS.root, "research", "lowchurn_results.csv")
    cols = ["family", "point", "cost_mult", "params", "exit_patch",
            "i_beats_rand_p95", "ii_ann_pos", "iii_dd_ok", "iv_trades_ok",
            "v_oos_ok", "vi_beats_passive", "decay_ok", "green",
            "full_sharpe", "full_ann", "full_dd", "avg_hold_days",
            "n_trades", "oos_sharpe", "oos_ann", "worst_year", "yearly"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    # ---------- JSON ----------
    out = {
        "batch": "J14-low-churn-family",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/LOW_CHURN_FAMILY.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": OOS_START,
        "constants": {
            "g1_prime_i_bar": p95_full, "g1_prime_vi_bar": vi_bar,
            "decay_floor": DECAY_FLOOR, "ref_oos_low_vol": ref_lv,
            "ref_oos_composite": ref_cp, "crash_year": CRASH_YEAR,
            "min_trades": MIN_TRADES, "max_dd": MAX_DD,
        },
        "runs_1x": {k: {"family": v["family"], "params": v["params"],
                        "exit_patch": v["exit_patch"], "meta": v["meta"],
                        "full": v["full"], "oos": v["oos"],
                        "clauses": v["clauses"], "decay_ok": v["decay_ok"],
                        "green": v["green"], "n_trades": v["n_trades"],
                        "oos_trades": v["oos_trades"]}
                    for k, v in runs.items()},
        "cost_stress": cost_runs,
        "verdicts": verdicts,
        "traders_registered": registered,
        "trials_ledger": [
            {"batch": "432-MA-param-grid (pre-plan)", "n": 432},
            {"batch": "J6-factor-IC-study", "n": 30},
            {"batch": "P1-strategy-screen", "n": 59},
            {"batch": "P2-null-calibration", "n": 122},
            {"batch": "P2-survivor-deepening", "n": 27},
            {"batch": "J14-low-churn-family", "n": n_runs},
        ],
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "lowchurn_family.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    print("\n===== J14 verdicts =====")
    for fam in ("LC-A", "LC-B"):
        print(f"  {fam}: {'PASS' if verdicts[fam]['g2_pass'] else 'FAIL'}")
    print(f"  LC-C: {'CONDITIONAL-PASS' if verdicts['LC-C']['conditional_pass'] else 'FAIL'}")
    if registered:
        print(f"  traders registered: {registered}")
    print(f"runs={n_runs} total elapsed: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
