"""J15 combined exit-softening family -> one-shot G1'+G2 acceptance.

PRE-REGISTERED before running (research/COMBINED_EXIT_SOFTENING.md,
written first). Do NOT tune thresholds after seeing results (p-hacking
ban, iron rule 3).

Family CE on the low_vol daily (60, k=5) base (J14 LC-C same base):
  core 2x2  : loss_time_days {8,16} x decay {(12,0.02),(25,0.05)}
              ce_base / ce_c2 / ce_c3 are J14 anchors (bit-reproduce
              0.7583 / 0.8649 / 1.0867); ce_c23 = the new combo point.
  neighborhood around ce_c23 (6): L-axis {12,24}, D-axis {20,32}
              (threshold held 0.05), plus c1/c4 stacking probes
              (tp-sparser / trail-late) -- ALL 10 are GATE points
              (strict verdict, J14 "N8 makes family stricter" precedent).

Green = six G1' clauses (constants from results/p2_calibration.json,
unchanged) AND OOS Sharpe >= 0.70 x 1.3631 (low_vol family reference,
bars do not move). Family PASS = all 10 green + 3 anchors reproduce
(|d|<0.002) + representative cost-x2 survive (full>0.4004 AND
OOS>=0.9542) + representative no crash year (>-30%). Representative =
argmax full Sharpe among green points. x3 recorded only.

Exit-param variants use the runtime ExitConfig factory patch (engine
files untouched, params-bridge kwargs WIN over patch fields); cost
stress uses the FeeSchedule factory patch (G2-proven). Both self-tested
before the batch (patch that does not bite = fake evidence, G2 6.1).

PASS -> register firm/traders/VOLATILITY-CE-01.json (INTERN) with an
explicit exit_overrides + repro block (non-bridged patch fields cannot
be expressed in params alone -- reproducibility gap closed by contract).

FAIL branch (pre-registered): cost-thickness constraint unbreakable on
the daily ETF universe -> next batch pivots to low-frequency holding /
low-cost instruments (money/bond ETF basket).

Products: research/combined_exit_results.csv + results/combined_exit.json.
Trial ledger: 696 (prior) + actual runs this batch.
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

OOS_START = "2025-01-01"
DECAY_FLOOR = 0.70
ANCHOR_TOL = 0.002
CRASH_YEAR = -0.30
COST_MULTS = [2, 3]
MIN_TRADES = 30
MAX_DD = -0.35
COST_X2_RATE = 0.0026082     # G2-recorded stressed single-side cost
COST_X1_RATE = 0.0013041     # G2-recorded baseline single-side cost

BASE_PARAMS = {"max_positions": 5, "position_size_pct": 0.10}


def c3_params(period=25, threshold=0.05, **extra):
    return {**BASE_PARAMS, "time_decay_period": period,
            "time_decay_threshold": threshold, **extra}


# point -> (params, exit_patch, role)  [pre-registered grid]
GRID = [
    ("ce_base",         dict(BASE_PARAMS),                                   None, "core"),
    ("ce_c2",           dict(BASE_PARAMS),                {"loss_time_days": 16}, "core"),
    ("ce_c3",           c3_params(),                                      None, "core"),
    ("ce_c23",          c3_params(),                     {"loss_time_days": 16}, "core"),
    ("ce_c23_L12",      c3_params(),                     {"loss_time_days": 12}, "nbhd"),
    ("ce_c23_L24",      c3_params(),                     {"loss_time_days": 24}, "nbhd"),
    ("ce_c23_D20",      c3_params(period=20),            {"loss_time_days": 16}, "nbhd"),
    ("ce_c23_D32",      c3_params(period=32),            {"loss_time_days": 16}, "nbhd"),
    ("ce_c23_tp1",      c3_params(take_profit_levels=(0.10, 0.25)),
                        {"loss_time_days": 16,
                         "take_profit_fractions": (0.5, 1.0)},                   "nbhd"),
    ("ce_c23_trail4",   c3_params(trailing_stop_activate=0.10),
                                                        {"loss_time_days": 16}, "nbhd"),
]

ANCHOR_KEYS = {          # ce point -> J14 lowchurn_family.json runs_1x key
    "ce_base": "lowvol_n60_k5_daily",
    "ce_c2": "lc_c2_losstime16",
    "ce_c3": "lc_c3_decay_loose",
}


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
    (take_profit_levels / trailing_stop_activate / time_decay_period /
    time_decay_threshold / position_size_pct / max_positions). Fields the
    bridge cannot reach (take_profit_fractions, loss_time_days, ...) are
    injected here. Precedence: bridge kwargs (from params) WIN over patch
    fields. Exit-rule PRIORITY untouched; engine files untouched.
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
    with CostPatch(2):
        fee = _eb.FeeSchedule()
        rate = (fee.commission_rate + fee.handling_fee
                + fee.supervision_fee + fee.slippage_a)
        ok &= abs(rate - COST_X2_RATE) < 1e-6
    fee = _eb.FeeSchedule()
    rate = (fee.commission_rate + fee.handling_fee
            + fee.supervision_fee + fee.slippage_a)
    ok &= abs(rate - COST_X1_RATE) < 1e-6
    with ExitPatch({"loss_time_days": 16, "take_profit_fractions": (0.5, 1.0)}):
        cfg = _eb.ExitConfig(max_positions=7)
        ok &= cfg.loss_time_days == 16 and cfg.take_profit_fractions == (0.5, 1.0)
        ok &= cfg.max_positions == 7
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

    print("loading G1' constants + J14 anchors...")
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    p95_full, vi_bar = g["i_full_sharpe_gt"], g["vi_full_sharpe_gt"]
    with open(os.path.join(PATHS.results_dir, "p2_survivors.json"),
              encoding="utf-8") as fh:
        surv = json.load(fh)
    ref_lv = surv["constants"]["ref_oos_low_vol"]      # 1.3631
    decay_bar = DECAY_FLOOR * ref_lv
    with open(os.path.join(PATHS.results_dir, "lowchurn_family.json"),
              encoding="utf-8") as fh:
        lc = json.load(fh)
    anchor_exp = {}
    for ce_key, lc_key in ANCHOR_KEYS.items():
        try:
            anchor_exp[ce_key] = lc["runs_1x"][lc_key]["full"]["sharpe"]
        except KeyError:
            print(f"anchor key missing in lowchurn_family.json: {lc_key}")
            sys.exit(2)
    print(f"  i>{p95_full} vi>{vi_bar} ref_lv={ref_lv} decay_bar={decay_bar:.4f}")
    print(f"  anchors expected: {anchor_exp}")

    print("loading core universe (bare codes)...")
    prices = load_core()
    print(f"  {len(prices)} ETFs")
    P = {f: pd.DataFrame({s: df[f] for s, df in prices.items()}).sort_index().ffill()
         for f in ["open", "high", "low", "close", "volume", "amount"]}
    close = P["close"]
    idx = close.index

    def green_clauses(r):
        f_, o_ = r["full"], r["oos"]
        c = {"i_beats_rand_p95": f_["sharpe"] > p95_full,
             "ii_ann_pos": f_["annual_return"] > 0,
             "iii_dd_ok": f_["max_drawdown"] >= MAX_DD,
             "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
             "v_oos_ok": o_["sharpe"] > 0 and o_["annual_return"] > 0,
             "vi_beats_passive": f_["sharpe"] > vi_bar}
        decay_ok = o_["sharpe"] >= decay_bar
        return c, decay_ok, all(c.values()) and decay_ok

    rows, runs = [], {}

    def do_run(point, params, exit_patch, role):
        r = run_one(prices, idx, entry_w, params, exit_patch)
        c, decay, green = green_clauses(r)
        runs[point] = {"role": role, "point": point, "params": params,
                       "exit_patch": exit_patch, "full": r["full"],
                       "oos": r["oos"], "clauses": c, "decay_ok": decay,
                       "green": green, "n_trades": r["n_trades"],
                       "oos_trades": r["oos_trades"], "equity": r["equity"]}
        rows.append({"role": role, "point": point, "cost_mult": 1,
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
        print(f"  {point:<16} full_s={r['full']['sharpe']:>7.3f} "
              f"oos_s={r['oos']['sharpe']:>7.3f} trades={r['n_trades']:<5} "
              f"{'GREEN' if green else 'RED'}")
        return runs[point]

    entry_w = volatility.low_vol_long(close, 60, top_k=5)  # daily (60,5) base
    print("CE grid: 10 pre-registered 1x gate points...")
    for point, params, patch, role in GRID:
        do_run(point, params, patch, role)

    n_runs = len(rows)

    # ---------- anchor reproduction ----------
    anchors = {}
    for ce_key, exp in anchor_exp.items():
        got = runs[ce_key]["full"]["sharpe"]
        anchors[ce_key] = {"expected": exp, "got": got,
                           "ok": abs(got - exp) < ANCHOR_TOL}
    anchor_ok = all(a["ok"] for a in anchors.values())
    print(f"anchors reproduce (|d|<{ANCHOR_TOL}): "
          f"{ {k: v['got'] for k, v in anchors.items()} } ok={anchor_ok}")

    # ---------- representative + cost stress ----------
    greens = [v for v in runs.values() if v["green"]]
    rep = max(greens, key=lambda v: v["full"]["sharpe"]) if greens else None
    cost_runs, cost2_ok, yearly, worst, yearly_ok = {}, False, {}, None, False
    elasticity = None
    if rep:
        print(f"representative: {rep['point']} (full {rep['full']['sharpe']})")
        for m in COST_MULTS:
            with CostPatch(m):
                r = run_one(prices, idx, entry_w, rep["params"], rep["exit_patch"])
            survive = bool(r["full"]["sharpe"] > vi_bar
                           and r["oos"]["sharpe"] >= decay_bar)
            cost_runs[f"rep_x{m}"] = {
                "rep": rep["point"], "cost_mult": m,
                "full": r["full"], "oos": r["oos"], "n_trades": r["n_trades"],
                "survive_clause": survive,
                "note": "G2 gate clause" if m == 2 else "recorded only"}
            rows.append({"role": "stress", "point": f"{rep['point']}_costx{m}",
                         "cost_mult": m, "params": json.dumps(rep["params"]),
                         "exit_patch": json.dumps(rep["exit_patch"] or ""),
                         "i_beats_rand_p95": r["full"]["sharpe"] > p95_full,
                         "ii_ann_pos": r["full"]["annual_return"] > 0,
                         "iii_dd_ok": r["full"]["max_drawdown"] >= MAX_DD,
                         "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
                         "v_oos_ok": r["oos"]["sharpe"] > 0 and r["oos"]["annual_return"] > 0,
                         "vi_beats_passive": r["full"]["sharpe"] > vi_bar,
                         "decay_ok": r["oos"]["sharpe"] >= decay_bar,
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
            print(f"  x{m}: full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} survive={survive}")
            if m == 2:
                cost2_ok = survive
                if r["n_trades"] > 0:
                    elasticity = round(
                        (rep["full"]["sharpe"] - r["full"]["sharpe"])
                        / (r["n_trades"] / 100), 4)
        yearly = yearly_returns(rep["equity"])
        worst = min(yearly.values())
        yearly_ok = worst > CRASH_YEAR
        print(f"  worst year {worst} (no-crash>{CRASH_YEAR}: {yearly_ok}), "
              f"elasticity={elasticity} Sharpe/100trades/+13bp")
    else:
        print("no green point -> family FAIL, stress skipped")

    # ---------- family verdict (pre-registered template) ----------
    all_green = len(greens) == len(GRID)
    red_points = [v["point"] for v in runs.values() if not v["green"]]
    g2_pass = bool(all_green and anchor_ok and cost2_ok and yearly_ok)
    verdict = {
        "template": "full-G2 one-shot (J15 pre-registered)",
        "g2_pass": g2_pass,
        "all_green": all_green,
        "n_gate_points": len(GRID),
        "red_points": red_points,
        "anchors": anchors, "anchor_ok": anchor_ok,
        "representative": rep["point"] if rep else None,
        "cost_x2_survive": cost2_ok,
        "yearly_returns": yearly, "worst_year": worst,
        "yearly_no_crash": yearly_ok,
        "elasticity_per_100trades_per_13bp": elasticity,
        "fail_branch": None if g2_pass else
        "cost-thickness constraint unbreakable on daily ETF universe -> "
        "pivot to low-frequency holding / low-cost instruments "
        "(money/bond ETF basket) next batch",
    }
    print(f"\nCE family: {'PASS' if g2_pass else 'FAIL'} "
          f"(all_green={all_green} anchor={anchor_ok} cost2x={cost2_ok} "
          f"yearly={yearly_ok})")
    if red_points:
        print(f"  red: {red_points}")

    # ---------- trader registration (full-G2 passer only) ----------
    registered = []
    today = time.strftime("%Y-%m-%d")
    ledger_note = f"ledger N={696 + n_runs}"
    if g2_pass:
        r = runs[rep["point"]]
        eq = r["equity"]
        iseg = seg_metrics(eq[eq.index < OOS_START])
        trader = {
            "id": "VOLATILITY-CE-01", "name": "组合软化一号",
            "school": "volatility", "author": "researcher-j15",
            "created": today, "level": "INTERN",
            "params": {"entry": "low_vol_long(n=60, top_k=5, daily)",
                       **rep["params"]},
            "exit_overrides": rep["exit_patch"] or {},
            "repro": {
                "script": "scripts/combined_exit_screen.py",
                "note": "non-bridged exit fields (loss_time_days / "
                        "take_profit_fractions) require the runtime "
                        "ExitConfig factory patch; engine files untouched; "
                        "params-bridge kwargs take precedence"},
            "backtest": {
                "in_sample": {"sharpe": iseg["sharpe"],
                               "max_dd": iseg["max_drawdown"],
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
                 "note": "J15 combined-exit one-shot G2 pass: G1' six clauses "
                         "on all 10 gate points + 3 anchors reproduced + "
                         "cost x2 survive + no crash year. Evidence: "
                         "research/COMBINED_EXIT_SOFTENING.md, "
                         "research/combined_exit_results.csv, " + ledger_note},
            ],
            "notes": "combined exit softening (loss_time_days 16 + decay "
                     "25d/5%) on low_vol(60,5) daily rotation; exit-rule "
                     "priority untouched",
        }
        path = os.path.join(PATHS.root, "firm", "traders",
                            "VOLATILITY-CE-01.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(trader, fh, indent=2, ensure_ascii=False)
        registered.append("VOLATILITY-CE-01")
        print(f"registered trader: {path}")

    # ---------- CSV ----------
    csv_path = os.path.join(PATHS.root, "research", "combined_exit_results.csv")
    cols = ["role", "point", "cost_mult", "params", "exit_patch",
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
        "batch": "J15-combined-exit-softening",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc":
            "research/COMBINED_EXIT_SOFTENING.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": OOS_START,
        "constants": {
            "g1_prime_i_bar": p95_full, "g1_prime_vi_bar": vi_bar,
            "decay_floor": DECAY_FLOOR, "ref_oos_low_vol": ref_lv,
            "oos_decay_bar": round(decay_bar, 4),
            "crash_year": CRASH_YEAR, "min_trades": MIN_TRADES,
            "max_dd": MAX_DD,
        },
        "runs_1x": {k: {"role": v["role"], "params": v["params"],
                        "exit_patch": v["exit_patch"], "full": v["full"],
                        "oos": v["oos"], "clauses": v["clauses"],
                        "decay_ok": v["decay_ok"], "green": v["green"],
                        "n_trades": v["n_trades"],
                        "oos_trades": v["oos_trades"]}
                    for k, v in runs.items()},
        "cost_stress": cost_runs,
        "verdict": verdict,
        "traders_registered": registered,
        "trials_ledger": [
            {"batch": "432-MA-param-grid (pre-plan)", "n": 432},
            {"batch": "J6-factor-IC-study", "n": 30},
            {"batch": "P1-strategy-screen", "n": 59},
            {"batch": "P2-null-calibration", "n": 122},
            {"batch": "P2-survivor-deepening", "n": 27},
            {"batch": "J14-low-churn-family", "n": 26},
            {"batch": "J15-combined-exit-softening", "n": n_runs},
        ],
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "combined_exit.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    print(f"\n===== J15 verdict: {'PASS' if g2_pass else 'FAIL'} =====")
    print(f"runs={n_runs} elapsed: {time.time()-t0:.0f}s ledger={696 + n_runs}")
    if not g2_pass:
        print("pre-registered FAIL branch -> pivot to low-frequency / "
              "low-cost instruments next batch")


if __name__ == "__main__":
    main()
