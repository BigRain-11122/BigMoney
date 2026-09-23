"""J19 CE exit-machine transfer probe -> one-shot verdict (pre-registered).

PRE-REGISTERED before running (research/CE_TRANSFER.md, written first).
Do NOT tune thresholds after seeing results (p-hacking ban, iron rule 3).

Question: is the J15-registered CE exit machine (loss_time_days 16 +
decay 25d/5% + trailing activate 0.10, trader VOLATILITY-CE-01) a
GENERAL cure for "engine exits destroy alpha", or low_vol-specific?
Transfer targets = the other two G1' survivors, composite_top5/top8
(20d rebalance, fully-invested sizing), which died on cost x2 in G2
(0.4225 -> -0.103 / 0.4327 -> 0.192). As-is port: entry family keeps
its own sizing, only the exit machine is swapped.

Grid (5 pre-registered 1x points):
  ct_anchor    low_vol(60,5) daily + CE machine, run TRUNCATED to the
               combined_exit.json universe.history end (evidence_cutoff
               lesson J16) -- must reproduce runs_1x.ce_c23_trail4
               (|d|<0.002) or the whole batch is void.
  ct_base_top5 / ct_base_top8   composite bases, default exits;
               consistency-checked against p1_screen.json records
               (informational, bars are recorded constants).
  ct_ce_top5   / ct_ce_top8     the transfer candidates.

Transfer green = six G1' clauses (p2_calibration constants) AND
OOS Sharpe >= 0.70 x ref_oos_composite (1.0405, p2_survivors.json
record) = 0.7284. Transfer PASS = green + cost-x2 survive
(full>0.4004 AND OOS>=0.7284) + no crash year (>-30%). Stress runs
(x2 gate / x3 record) only for green candidates.

PASS -> register COMPOSITE-CE-01/-02 (INTERN, evidence_cutoff +
exit_overrides + repro contract) AND wire live/paper.py
SIGNAL_BUILDERS (no registration without paper-pipeline wiring).
FAIL (pre-registered): CE machine is low_vol-specific, transfer
question closed; strategy line pivots to low-frequency holding /
low-cost instruments next batch. NO exit-param retries this batch.

Products: research/ce_transfer_results.csv + results/ce_transfer.json.
Trial ledger: cumulative from combined_exit.json + actual runs.
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
from science_gates import COST_X2_RATE, CostPatch, append_ledger, ledger_head, ledger_total  # T-03 F3/F12
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown
from strategies import volatility
from strategies.composite_rotation import top_n_rotation

OOS_START = "2025-01-01"
DECAY_FLOOR = 0.70
ANCHOR_TOL = 0.002
CRASH_YEAR = -0.30
MIN_TRADES = 30
MAX_DD = -0.35
COST_MULTS = [2, 3]
# COST_X2_RATE -> single source scripts/science_gates.py (T-03-F12)
COST_X1_RATE = 0.0013041     # G2-recorded baseline single-side cost

# registered CE machine (J15, trader VOLATILITY-CE-01, verbatim)
CE_BRIDGE = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.10}
CE_PATCH = {"loss_time_days": 16}

ENTRY_KEYS = {5: "top_n_rotation(composite, n=5, rebal_days=20)",
              8: "top_n_rotation(composite, n=8, rebal_days=20)"}
TRADER_IDS = {5: ("COMPOSITE-CE-01", "复合软化一号"),
              8: ("COMPOSITE-CE-02", "复合软化二号")}


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


def panels(prices: dict) -> dict:
    return {f: pd.DataFrame({s: df[f] for s, df in prices.items()})
            .sort_index().ffill()
            for f in ["open", "high", "low", "close", "volume", "amount"]}


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


# CostPatch -> single source scripts/science_gates.py (T-03-F12)


class ExitPatch:
    """ExitConfig name-factory patch: inject NON-bridged exit fields.

    Bridge kwargs (from params) WIN over patch fields. Exit-rule
    PRIORITY untouched; engine files untouched.
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


def run_one(prices, idx, entry, params, exit_patch=None, cost_mult=None):
    ectx = ExitPatch(exit_patch) if exit_patch else nullcontext()
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ectx:
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

    print("loading constants (p2_calibration / p2_survivors / "
          "combined_exit / p1_screen)...")
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    p95_full, vi_bar = g["i_full_sharpe_gt"], g["vi_full_sharpe_gt"]
    with open(os.path.join(PATHS.results_dir, "p2_survivors.json"),
              encoding="utf-8") as fh:
        surv = json.load(fh)
    ref_oos_comp = surv["constants"]["ref_oos_composite"]      # 1.0405
    oos_bar = round(DECAY_FLOOR * ref_oos_comp, 4)
    with open(os.path.join(PATHS.results_dir, "combined_exit.json"),
              encoding="utf-8") as fh:
        ce_prior = json.load(fh)
    anchor_exp = ce_prior["runs_1x"]["ce_c23_trail4"]
    anchor_hist_end = str(anchor_exp.get("history_end")
                          or ce_prior["universe"]["history"].split("..")[-1].strip())
    prior_ledger = ce_prior["trials_ledger"]
    prior_n = ledger_total(prior_ledger)  # T-03-F3 tolerant reader (dict | flat list)
    with open(os.path.join(PATHS.results_dir, "p1_screen.json"),
              encoding="utf-8") as fh:
        p1 = json.load(fh)
    p1_runs = {r["strategy"]: r for r in p1["runs"] if r.get("status") == "ok"}
    print(f"  i>{p95_full} vi>{vi_bar} ref_oos_composite={ref_oos_comp} "
          f"oos_bar={oos_bar}")
    print(f"  anchor expected: full={anchor_exp['full']['sharpe']} "
          f"oos={anchor_exp['oos']['sharpe']} "
          f"hist_end={anchor_hist_end}")

    print("loading core universe (bare codes)...")
    prices = load_core()
    P = panels(prices)
    close, high, low = P["close"], P["high"], P["low"]
    idx = close.index
    data_end = str(idx[-1].date())
    print(f"  {len(prices)} ETFs, data through {data_end}")

    rows, runs, n_runs = [], {}, 0

    def record(point, role, r, params, patch, cost_mult=1, green="",
               extra=None):
        runs[point] = {"role": role, "params": params, "exit_patch": patch,
                       "full": r["full"], "oos": r["oos"],
                       "n_trades": r["n_trades"], "oos_trades": r["oos_trades"],
                       "equity": r["equity"], "cost_mult": cost_mult,
                       "green": green, **(extra or {})}
        rows.append({"role": role, "point": point, "cost_mult": cost_mult,
                     "params": json.dumps(params),
                     "exit_patch": json.dumps(patch) if patch else "",
                     "full_sharpe": r["full"]["sharpe"],
                     "full_ann": r["full"]["annual_return"],
                     "full_dd": r["full"]["max_drawdown"],
                     "avg_hold_days": r["full"].get("avg_hold_days", ""),
                     "n_trades": r["n_trades"],
                     "oos_sharpe": r["oos"]["sharpe"],
                     "oos_ann": r["oos"]["annual_return"],
                     "green": green,
                     **({k: v for k, v in (extra or {}).items()
                         if not isinstance(v, (dict, pd.Series))})})
        print(f"  {point:<14} full_s={r['full']['sharpe']:>7.3f} "
              f"oos_s={r['oos']['sharpe']:>7.3f} trades={r['n_trades']:<5} "
              f"x{cost_mult} {green}")

    # ---------- 1) hard anchor: CE machine on low_vol, truncated ----------
    ps = pd.Timestamp(anchor_hist_end)
    prices_a = {s: df[df.index <= ps] for s, df in prices.items()}
    P_a = panels(prices_a)
    entry_a = volatility.low_vol_long(P_a["close"], 60, top_k=5)
    params_a = {"max_positions": 5, "position_size_pct": 0.10, **CE_BRIDGE}
    r = run_one(prices_a, P_a["close"].index, entry_a, params_a, CE_PATCH)
    n_runs += 1
    anchor = {"expected_full": anchor_exp["full"]["sharpe"],
              "expected_oos": anchor_exp["oos"]["sharpe"],
              "got_full": r["full"]["sharpe"], "got_oos": r["oos"]["sharpe"],
              "history_end": anchor_hist_end,
              "ok": abs(r["full"]["sharpe"] - anchor_exp["full"]["sharpe"])
                    < ANCHOR_TOL
              and abs(r["oos"]["sharpe"] - anchor_exp["oos"]["sharpe"])
                    < ANCHOR_TOL}
    record("ct_anchor", "anchor", r, params_a, CE_PATCH, 1,
           "OK" if anchor["ok"] else "BROKEN",
           {"anchor_ok": anchor["ok"]})
    print(f"anchor reproduce (|d|<{ANCHOR_TOL}): "
          f"{anchor['got_full']}/{anchor['got_oos']} ok={anchor['ok']}")
    if not anchor["ok"]:
        print("ANCHOR BROKEN -- batch void, no verdict, no registration")
        write_outputs(rows, runs, anchor, None, None, n_runs, prior_ledger,
                      p95_full, vi_bar, oos_bar, data_end, t0, prices, p1_runs,
                      void=True)
        return

    # ---------- 2) composite bases (consistency vs P1 records) ----------
    entries = {n: top_n_rotation(high, low, close, top_n=n, rebal_days=20)
               for n in (5, 8)}
    consistency = {}
    for n in (5, 8):
        params = {"max_positions": n,
                  "position_size_pct": round(0.95 / n, 4)}
        r = run_one(prices, idx, entries[n], params, None)
        n_runs += 1
        exp = p1_runs.get(f"composite_top{n}")
        c_ok = None
        if exp:
            c_ok = bool(abs(r["full"]["sharpe"] - exp["full"]["sharpe"])
                       < ANCHOR_TOL
                       and abs(r["oos"]["sharpe"] - exp["oos"]["sharpe"])
                       < ANCHOR_TOL
                       and r["n_trades"] == exp["n_trades"])
            consistency[f"composite_top{n}"] = {
                "expected_full_sharpe": exp["full"]["sharpe"],
                "expected_oos_sharpe": exp["oos"]["sharpe"],
                "expected_trades": exp["n_trades"],
                "got_full_sharpe": r["full"]["sharpe"],
                "got_oos_sharpe": r["oos"]["sharpe"],
                "got_trades": r["n_trades"], "ok": c_ok,
                "note": "informational; valid while data end == P1 data end "
                        f"({p1['universe']['history']})"}
        record(f"ct_base_top{n}", "base", r, params, None, 1, "",
               {"consistency_ok": c_ok})

    # ---------- 3) transfer candidates: CE machine on composite ----------
    def green_clauses(r):
        f_, o_ = r["full"], r["oos"]
        c = {"i_beats_rand_p95": f_["sharpe"] > p95_full,
             "ii_ann_pos": f_["annual_return"] > 0,
             "iii_dd_ok": f_["max_drawdown"] >= MAX_DD,
             "iv_trades_ok": r["n_trades"] >= MIN_TRADES,
             "v_oos_ok": o_["sharpe"] > 0 and o_["annual_return"] > 0,
             "vi_beats_passive": f_["sharpe"] > vi_bar}
        decay_ok = o_["sharpe"] >= oos_bar
        return c, decay_ok, all(c.values()) and decay_ok

    transfers, stress, yearly_all = {}, {}, {}
    for n in (5, 8):
        params = {"max_positions": n,
                  "position_size_pct": round(0.95 / n, 4), **CE_BRIDGE}
        r = run_one(prices, idx, entries[n], params, CE_PATCH)
        n_runs += 1
        c, decay_ok, green = green_clauses(r)
        yearly = yearly_returns(r["equity"])
        worst = min(yearly.values())
        transfers[f"composite_top{n}"] = {
            "params": params, "exit_patch": CE_PATCH, "clauses": c,
            "decay_ok": decay_ok, "green": green, "full": r["full"],
            "oos": r["oos"], "n_trades": r["n_trades"],
            "oos_trades": r["oos_trades"], "yearly_returns": yearly,
            "worst_year": worst, "cost_x2_survive": None,
            "transfer_pass": False}
        record(f"ct_ce_top{n}", "transfer", r, params, CE_PATCH, 1,
               "GREEN" if green else "RED",
               {"i_beats_rand_p95": c["i_beats_rand_p95"],
                "ii_ann_pos": c["ii_ann_pos"], "iii_dd_ok": c["iii_dd_ok"],
                "iv_trades_ok": c["iv_trades_ok"], "v_oos_ok": c["v_oos_ok"],
                "vi_beats_passive": c["vi_beats_passive"],
                "decay_ok": decay_ok, "worst_year": worst})
        if green:
            for m in COST_MULTS:
                rx = run_one(prices, idx, entries[n], params, CE_PATCH,
                             cost_mult=m)
                n_runs += 1
                survive = bool(rx["full"]["sharpe"] > vi_bar
                               and rx["oos"]["sharpe"] >= oos_bar)
                stress[f"ce_top{n}_x{m}"] = {
                    "entry": f"composite_top{n}", "cost_mult": m,
                    "full": rx["full"], "oos": rx["oos"],
                    "n_trades": rx["n_trades"], "survive": survive,
                    "note": "G2 gate clause" if m == 2 else "recorded only"}
                record(f"ct_ce_top{n}_x{m}", "stress", rx, params, CE_PATCH,
                       m, ("SURVIVE" if survive else "DEAD") if m == 2
                       else "rec")
                if m == 2:
                    transfers[f"composite_top{n}"]["cost_x2_survive"] = survive
            t = transfers[f"composite_top{n}"]
            t["transfer_pass"] = bool(green and t["cost_x2_survive"]
                                      and worst > CRASH_YEAR)

    n_pass = sum(1 for t in transfers.values() if t["transfer_pass"])
    print(f"\nJ19 transfer: anchor OK, {n_pass}/2 candidates PASS "
          f"(green: "
          f"{[k for k, v in transfers.items() if v['green']]})")

    write_outputs(rows, runs, anchor, transfers, stress, n_runs, prior_ledger,
                  p95_full, vi_bar, oos_bar, data_end, t0, prices, p1_runs,
                  consistency=consistency)


def write_outputs(rows, runs, anchor, transfers, stress, n_runs, prior_ledger,
                  p95_full, vi_bar, oos_bar, data_end, t0, prices, p1_runs,
                  consistency=None, void=False):
    consistency = consistency or {}
    n_pass = 0 if void or transfers is None else sum(
        1 for t in transfers.values() if t["transfer_pass"])
    today = time.strftime("%Y-%m-%d")

    # ---------- trader registration (transfer PASS only) ----------
    registered = []
    if not void and transfers:
        for n in (5, 8):
            t = transfers[f"composite_top{n}"]
            if not t["transfer_pass"]:
                continue
            tid, tname = TRADER_IDS[n]
            r1 = runs[f"ct_ce_top{n}"]
            eq = r1["equity"]
            iseg = seg_metrics(eq[eq.index < OOS_START])
            x2 = (stress or {}).get(f"ce_top{n}_x2") or {}
            trader = {
                "id": tid, "name": tname, "school": "composite",
                "author": "researcher-j19", "created": today,
                "evidence_cutoff": data_end, "level": "INTERN",
                "params": {"entry": ENTRY_KEYS[n], **t["params"]},
                "exit_overrides": t["exit_patch"],
                "repro": {
                    "script": "scripts/ce_transfer.py",
                    "note": "non-bridged exit field (loss_time_days) "
                            "requires the runtime ExitConfig factory "
                            "patch; engine files untouched; params-bridge "
                            "kwargs take precedence; anchor run truncated "
                            "to evidence_cutoff reproduces registered "
                            "evidence"},
                "backtest": {
                    "in_sample": {"sharpe": iseg["sharpe"],
                                  "max_dd": iseg["max_drawdown"],
                                  "annual": iseg["annual_return"],
                                  "trades": t["n_trades"] - t["oos_trades"]},
                    "out_sample": {"sharpe": t["oos"]["sharpe"],
                                   "max_dd": t["oos"]["max_drawdown"],
                                   "annual": t["oos"]["annual_return"],
                                   "trades": t["oos_trades"]},
                    "cost_x2": {
                        "sharpe": x2.get("full", {}).get("sharpe"),
                        "oos_sharpe": x2.get("oos", {}).get("sharpe"),
                        "survive": x2.get("survive"),
                        "note": "J19 transfer gate x2 (26bp single-side); "
                                "x3 recorded only. Evidence: "
                                "results/ce_transfer.json cost_stress"},
                },
                "paper": {"months_tracked": 0, "monthly_returns": [],
                          "current_dd": 0.0, "as_of": today,
                          "cutoff": data_end},
                "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": 0},
                "status_history": [
                    {"date": today, "from": None, "to": "INTERN",
                     "note": "J19 CE-machine transfer one-shot pass: six "
                             "G1' clauses + OOS>=0.7284 + cost x2 survive "
                             "+ no crash year. Evidence: "
                             "research/CE_TRANSFER.md, "
                             "research/ce_transfer_results.csv, ledger "
                             f"N={ledger_head()['total'] + n_runs}"},  # T-03-F3 data-driven chain head
                ],
                "notes": "J15-registered CE exit machine (loss_time 16 + "
                         "decay 25d/5% + trail 0.10) as-is port onto "
                         f"composite_top{n} 20d rotation; exit-rule priority "
                         "untouched",
            }
            path = os.path.join(PATHS.root, "firm", "traders", f"{tid}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(trader, fh, indent=2, ensure_ascii=False)
            registered.append(tid)
            print(f"registered trader: {path}")

    # ---------- CSV ----------
    csv_path = os.path.join(PATHS.root, "research", "ce_transfer_results.csv")
    cols = ["role", "point", "cost_mult", "params", "exit_patch",
            "full_sharpe", "full_ann", "full_dd", "avg_hold_days",
            "n_trades", "oos_sharpe", "oos_ann", "green",
            "i_beats_rand_p95", "ii_ann_pos", "iii_dd_ok", "iv_trades_ok",
            "v_oos_ok", "vi_beats_passive", "decay_ok", "worst_year",
            "consistency_ok", "anchor_ok"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    # ---------- JSON ----------
    ledger = append_ledger("J19-ce-transfer", n_runs, "ce_transfer.json",
                           note="T-03-F3 unified dict schema; flat chain narrative retired (git history)")
    out = {
        "batch": "J19-ce-transfer",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc":
            "research/CE_TRANSFER.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"anchor .. {data_end}"},
        "oos_start": OOS_START,
        "constants": {
            "g1_prime_i_bar": p95_full, "g1_prime_vi_bar": vi_bar,
            "decay_floor": DECAY_FLOOR,
            "ref_oos_composite": None if void
            else round(oos_bar / DECAY_FLOOR, 4),
            "oos_decay_bar": oos_bar,
            "crash_year": CRASH_YEAR, "min_trades": MIN_TRADES,
            "max_dd": MAX_DD,
        },
        "anchor": anchor,
        "consistency_vs_p1": consistency,
        "runs": {k: {kk: vv for kk, vv in v.items()
                     if kk not in ("equity",)} for k, v in runs.items()},
        "transfers": transfers if not void else None,
        "cost_stress": stress,
        "verdict": {
            "template": "J19 transfer one-shot (pre-registered)",
            "anchor_ok": anchor["ok"], "void": void,
            "n_pass": n_pass,
            "n_candidates": 0 if transfers is None else len(transfers),
            "green_entries": [] if not transfers else
            [k for k, v in transfers.items() if v["green"]],
            "fail_branch": None if (void or n_pass) else
            "CE machine is low_vol-specific, does not transfer -> "
            "strategy line pivots to low-frequency holding / low-cost "
            "instruments (money/bond ETF basket) next batch",
        },
        "traders_registered": registered,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "ce_transfer.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    print(f"\n===== J19 verdict: "
          f"{'VOID (anchor broken)' if void else f'{n_pass}/2 PASS'} =====")
    print(f"runs={n_runs} elapsed: {time.time()-t0:.0f}s "
          f"ledger={sum(x['n'] for x in ledger)}")
    if not void and not n_pass:
        print("pre-registered FAIL branch -> CE machine low_vol-specific; "
              "pivot to low-frequency / low-cost instruments next batch")


if __name__ == "__main__":
    main()
