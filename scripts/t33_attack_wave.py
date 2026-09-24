"""T-33 deliverable-2 attack-corps recruitment wave (CEO O-20260924-2012).

Preregistered in research/T33_ATTACK_WAVE.md BEFORE any run (frozen commit
f807911; pre-run zero cells). 20 candidates x 2 cost faces (base V1 + x2
CostPatch(2.0)) = 40 cells, G1' v2 canon via science_gates shared library
(no hand-copied lines). Honest zero if none pass (ticket spec verbatim).

Candidate groups (D6 priority order, prereg sec.1):
  A  CEO-named PROSPECT attack members (5, frozen member params)
  B  digest wave-1 momentum families (3, runner-local parameterized
     variants of momentum/composite_rotation skeletons -- ZERO new engine
     or library parts)
  C  library trend families (12, P1 default caliber verbatim: trend.py 5 +
     momentum.py 5 + composite_rotation.py 2)

Hard gates (any FAIL = batch void, exit 2): 6 registered anchor reproductions
(p3 member_run 1x + x2, anchor_checks), core48 panel complete @cutoff,
skill-line inputs present (null pool >= 30, passive baseline).

Usage (detached BelowNormal per O-1136; JSONL checkpoint resumable):
  python scripts/t33_attack_wave.py run        # gates then 40 cells, auto-finalize
  python scripts/t33_attack_wave.py status     # progress read
  python scripts/t33_attack_wave.py finalize   # verdicts from checkpointed cells
  python scripts/t33_attack_wave.py selftest   # offline, no data files
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

TICKET = "T-2026-09-24-33"
CUTOFF = "2026-09-24"               # prereg sec.2 (panel truncated; fwd lock)
BATCH_CELLS = 40                    # 20 candidates x 2 faces (prereg sec.0)
OOS_START = "2025-01-01"            # company constant-blind split
FACES = ("base", "x2")
TURNOVER_BUDGET = 50.0              # entries/year eligibility clause (prereg s3)
D6_LINE = 0.70                      # prereg sec.1 merge clause
PREREG_PATH = os.path.join("research", "T33_ATTACK_WAVE.md")
CELLS_PATH = os.path.join("results", "t33_attack_wave_cells.jsonl")
GATES_JSON = os.path.join("results", "t33_attack_wave_gates.json")
OUT_JSON = os.path.join("results", "t33_attack_wave.json")
OUT_CSV = os.path.join("research", "t33_attack_wave_results.csv")
LOG_PATH = os.path.join("results", "t33_attack_wave.log")
ATT_JSON = os.path.join("results", "gate_attrition.json")

DEFENSE_B = ("511260", "518880")    # core48 pool law (511880 not a bare code)
GEM_LEGS = ("510300", "513100", "513180")
GEM_DEFENSE = "511260"

# (id, group, kind) in D6 priority order (prereg sec.1)
CANDIDATES = [
    ("PROS-VOB-CE-01", "A", "member"),
    ("PROS-IBB-01", "A", "member"),
    ("PROS-IBB-CE-01", "A", "member"),
    ("PROS-DUCK-01", "A", "member"),
    ("PROS-DUCK-CE-01", "A", "member"),
    ("slope_r2_rotation_25_top3_r8", "B", "slope_r2"),
    ("dual_momentum_etf_20_60_top3", "B", "dual_mom_v"),
    ("gem_ashare_m12", "B", "gem"),
    ("donchian_20_10", "C", "lib_donchian"),
    ("dual_ma_5_20", "C", "lib_dual_ma"),
    ("triple_ma_5_20_60", "C", "lib_triple_ma"),
    ("parabolic_sar", "C", "lib_sar"),
    ("supertrend_10_3", "C", "lib_supertrend"),
    ("xsec_mom_120_20", "C", "lib_xsec_mom"),
    ("dual_mom_120", "C", "lib_dual_mom_120"),
    ("ts_mom_200", "C", "lib_ts_mom"),
    ("rs_rotation_20", "C", "lib_rs_rot"),
    ("mom_accel_20_120", "C", "lib_mom_accel"),
    ("composite_top5", "C", "lib_comp5"),
    ("composite_top8", "C", "lib_comp8"),
]

_G: dict = {}


def _log(msg: str):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {msg}\n")


def _sha256_file(path: str) -> str:
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ------------------------------------------------------- B-group local builders
# (parameterized variants; strategies/ and engine/ untouched -- prereg s3)

def _slope_r2(close: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    """Rolling OLS slope x R^2 of log(close) vs time, closed form (vectorized).

    Window-relative x = 0..n-1. Windows overlapping any NaN -> NaN (warmup /
    late-listing semantics identical to library rolling min_periods=n).
    """
    y = np.log(close.to_numpy(dtype=float))
    T, S = y.shape
    fin = np.isfinite(y)
    y0 = np.where(fin, y, 0.0)
    pos = np.arange(T, dtype=float)[:, None]
    z = np.zeros((1, S))
    cs_y = np.vstack([z, np.cumsum(y0, axis=0)])
    cs_yy = np.vstack([z, np.cumsum(y0 * y0, axis=0)])
    cs_ty = np.vstack([z, np.cumsum(y0 * pos, axis=0)])
    zi = np.zeros((1, S), dtype=int)
    cs_f = np.vstack([zi, np.cumsum(fin.astype(int), axis=0)])
    Sx = n * (n - 1) / 2.0
    Sxx = (n - 1) * n * (2 * n - 1) / 6.0
    den_x = n * Sxx - Sx * Sx
    out = np.full((T, S), np.nan)
    for i in range(n - 1, T):
        nfin = cs_f[i + 1] - cs_f[i + 1 - n]
        if not (nfin == n).any():
            continue
        Sy = cs_y[i + 1] - cs_y[i + 1 - n]
        Syy = cs_yy[i + 1] - cs_yy[i + 1 - n]
        St = cs_ty[i + 1] - cs_ty[i + 1 - n]
        x0 = float(i - n + 1)
        Sxy = St - x0 * Sy
        num = n * Sxy - Sx * Sy
        var_y = n * Syy - Sy * Sy
        with np.errstate(divide="ignore", invalid="ignore"):
            slope = num / den_x
            r2 = (num * num) / (var_y * den_x)
        bad = (nfin != n) | ~np.isfinite(num) | (var_y <= 1e-18)
        out[i] = np.where(bad, np.nan, slope * r2)
    return pd.DataFrame(out, index=close.index, columns=close.columns)


def slope_r2_entry(close: pd.DataFrame, n: int = 25, top_k: int = 3,
                   rebal: int = 8) -> pd.DataFrame:
    """#81: annualized 25d log-price OLS slope x R^2 score, hold Top3,
    min-hold approximated by 8-day non-overlapping rebalance windows
    (composite_rotation.rebal mechanism, parameterized)."""
    score = _slope_r2(close, n) * 252.0
    ranks = score.rank(axis=1, ascending=False)
    in_set = ranks <= top_k
    held = in_set.iloc[::rebal].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def dual_mom_v_entry(close: pd.DataFrame, n_rel: int = 20, n_abs: int = 60,
                     top_k: int = 3, defense=DEFENSE_B) -> pd.DataFrame:
    """#82: 20d relative-momentum rank Top3 AND 60d absolute momentum > 0;
    no qualifier -> defense = argmax 20d momentum in {511260, 518880}
    (pool law: 511880 not a core48 bare code, prereg s3 disclosure);
    defense momentum <= 0 -> flat (cash)."""
    rel = close.pct_change(n_rel)
    ranks = rel.rank(axis=1, ascending=False)
    entry = ((ranks <= top_k) & (close.pct_change(n_abs) > 0)).astype(int)
    dcol = [c for c in defense if c in close.columns]
    if dcol:
        dmom = close[dcol].pct_change(n_rel)
        sub = dmom[dmom.notna().any(axis=1)]      # skip warmup all-NaN rows
        if len(sub):
            best = sub.idxmax(axis=1)
            bestv = sub.max(axis=1)
            no_qual = entry.sum(axis=1).reindex(sub.index) == 0
            take = no_qual & (bestv > 0)
            for dt in sub.index[take]:
                entry.at[dt, best.loc[dt]] = 1
    return entry


def gem_entry(close: pd.DataFrame, legs=GEM_LEGS, defense: str = GEM_DEFENSE,
              mom_n: int = 252) -> pd.DataFrame:
    """#83: monthly 12m dual momentum over {510300, 513100, 513180}; hold the
    winner; winner 12m momentum <= 0 -> defense 511260. Decision at month-end
    close T, state effective from T+1 (engine buys next-day open; causal)."""
    idx = close.index
    mom = close[list(legs)].pct_change(mom_n)
    pos = pd.Series(np.arange(len(idx)), index=idx)
    me_days = pos.groupby(idx.to_period("M")).tail(1).index   # month-end days
    me_set = set(me_days)
    target: dict = {}
    for d in me_days:
        row = mom.loc[d]
        if not row.notna().any():
            continue
        best = row.idxmax()
        target[d] = best if row.max() > 0 else defense
    entry = pd.DataFrame(0, index=idx, columns=close.columns, dtype=int)
    last_t = None
    for d in idx:
        if last_t is not None:
            entry.at[d, last_t] = 1
        if d in target:
            last_t = target[d] or None
    return entry


# ------------------------------------------------------------------- workers

def _init_worker():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)     # O-1136 full-load low-priority pool
        except Exception:
            pass
    from config import PATHS
    from live.paper import SIGNAL_BUILDERS, build_panels, load_core
    from firm.hr import load_trader
    from strategies import momentum, trend
    from strategies.composite_rotation import top_n_rotation

    prices_full = load_core()
    ps = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    close, high, low = P["close"], P["high"], P["low"]
    idx = close.index
    syms = list(close.columns)

    def sym_panel(fn):
        pos = pd.DataFrame({s: fn(s) for s in syms}, index=idx).fillna(0)
        return (pos > 0).astype(int)

    bench = pd.read_csv(os.path.join(PATHS.basic_dir, "csi300.csv"),
                        parse_dates=["date"]).set_index("date")["close"].sort_index()

    entries, params, exits = {}, {}, {}
    for cid, grp, kind in CANDIDATES:
        if kind == "member":
            t = load_trader(cid)                      # frozen member params
            probe = dict(t)
            probe["evidence_cutoff"] = CUTOFF          # prereg s3 cutoff override
            probe["params"] = dict(t["params"])
            probe["params"]["report_num_entries"] = True
            entries[cid] = SIGNAL_BUILDERS[probe["params"]["entry"]](P)
            params[cid] = {k: v for k, v in probe["params"].items() if k != "entry"}
            exits[cid] = probe.get("exit_overrides")
        elif kind == "slope_r2":
            entries[cid] = slope_r2_entry(close, 25, 3, 8)
            params[cid] = {"max_positions": 3, "position_size_pct": 0.3167,
                           "report_num_entries": True}
        elif kind == "dual_mom_v":
            entries[cid] = dual_mom_v_entry(close, 20, 60, 3)
            params[cid] = {"max_positions": 3, "position_size_pct": 0.3167,
                           "report_num_entries": True}
        elif kind == "gem":
            entries[cid] = gem_entry(close)
            params[cid] = {"max_positions": 1, "position_size_pct": 0.95,
                           "report_num_entries": True}
        else:                                          # C group: P1 caliber
            params[cid] = {"report_num_entries": True}
            if kind == "lib_donchian":
                entries[cid] = sym_panel(lambda sm: trend.donchian_breakout(
                    close[sm], high[sm], low[sm], entry_n=20, exit_n=10))
            elif kind == "lib_dual_ma":
                entries[cid] = sym_panel(lambda sm: trend.dual_ma_cross(close[sm], 5, 20))
            elif kind == "lib_triple_ma":
                entries[cid] = sym_panel(lambda sm: trend.triple_ma(close[sm], 5, 20, 60))
            elif kind == "lib_sar":
                entries[cid] = sym_panel(lambda sm: trend.parabolic_sar(close[sm]))
            elif kind == "lib_supertrend":
                entries[cid] = sym_panel(lambda sm: trend.supertrend(
                    close[sm], high[sm], low[sm], 10, 3.0))
            elif kind == "lib_xsec_mom":
                entries[cid] = momentum.cross_sectional_momentum(close, n=120, skip=20, top_k=5)
            elif kind == "lib_dual_mom_120":
                entries[cid] = momentum.dual_momentum(close, bench, n=120, top_k=5)
            elif kind == "lib_ts_mom":
                entries[cid] = sym_panel(lambda sm: momentum.time_series_momentum(close[sm], 200))
            elif kind == "lib_rs_rot":
                entries[cid] = momentum.relative_strength_rotation(close, bench, n=20, top_k=5)
            elif kind == "lib_mom_accel":
                entries[cid] = momentum.momentum_acceleration(close, fast=20, slow=120)
            elif kind == "lib_comp5":
                entries[cid] = top_n_rotation(high, low, close, top_n=5, rebal_days=20)
                params[cid] = {"max_positions": 5, "position_size_pct": 0.19,
                               "report_num_entries": True}
            elif kind == "lib_comp8":
                entries[cid] = top_n_rotation(high, low, close, top_n=8, rebal_days=20)
                params[cid] = {"max_positions": 8, "position_size_pct": 0.1188,
                               "report_num_entries": True}
    _G.update(prices=prices, idx=idx, entries=entries, params=params, exits=exits)


def _run_cell(cid: str, face: str) -> dict:
    """One (candidate, cost-face) cell. Exit signal = (entry <= 0) uniform
    (member convention == P1 panel convention)."""
    from engine import run_backtest
    from live.paper import ExitPatch, seg_metrics
    from science_gates import CostPatch
    t0 = time.time()
    entry = _G["entries"][cid]
    params = _G["params"][cid]
    prices = _G["prices"]
    row = {"key": f"{cid}|{face}", "cand": cid, "face": face, "status": "ok"}
    try:
        with ExitPatch(_G["exits"].get(cid)):
            if face == "x2":
                with CostPatch(2.0):           # multiplier (r82 J18 law)
                    res = run_backtest(prices, params, entry_signal=entry,
                                       exit_signal=(entry <= 0))
            else:
                res = run_backtest(prices, params, entry_signal=entry,
                                   exit_signal=(entry <= 0))
        eq = pd.Series(res["equity_curve"],
                       index=_G["idx"][:len(res["equity_curve"])])
        full = res["metrics"]
        oos = seg_metrics(eq, OOS_START)
        oos_trades = sum(1 for tr in res["trades"]
                         if str(tr["date"]) >= OOS_START)
        row.update({
            "sharpe_full": round(float(full["sharpe"]), 4),
            "annual_return": round(float(full["annual_return"]), 4),
            "max_drawdown": round(float(full["max_drawdown"]), 4),
            "n_trades": int(full["num_trades"]),
            "n_entries": int(full.get("num_entries", -1)),
            "oos_sharpe": round(float(oos["sharpe"]), 4),
            "oos_annual_return": round(float(oos["annual_return"]), 4),
            "oos_max_drawdown": round(float(oos["max_drawdown"]), 4),
            "oos_trades": int(oos_trades),
        })
        if face == "base":
            rets = eq.pct_change().dropna()
            row["rets"] = [round(float(x), 8) for x in rets.to_numpy()]
    except Exception as ex:
        row["status"] = "cell_error"
        row["error"] = f"{type(ex).__name__}: {ex}"
    row["elapsed_s"] = round(time.time() - t0, 2)
    return row


# ---------------------------------------------------------------- checkpoint

def load_done_keys(path: str) -> set:
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for ln in lines[:-1]:                      # tolerate truncated tail (t22 law)
        try:
            keys.add(json.loads(ln)["key"])
        except (ValueError, KeyError):
            continue
    try:
        keys.add(json.loads(lines[-1])["key"])  # last line only if complete
    except (ValueError, KeyError, IndexError):
        pass
    return keys


# --------------------------------------------------------------------- gates

def _anchor_check(t: dict, r1: dict, r2: dict) -> dict:
    """Local mirror of p3.anchor_checks tolerating the three members whose
    registered cost_x2 block predates the oos_sharpe key (DROUGHT/ENGULF/
    NEEDLE registered {sharpe,survive,note} only). Compares exactly the
    RECORDED keys -- no loosening of any recorded clause (J18: implementation
    repair, judgments untouched; zero cells had run when this was fixed)."""
    from live.paper import ANCHOR_TOL, OOS_START as _OOS, seg_metrics
    from p3_portfolio import _evidence_matches
    got_is = {**seg_metrics(r1["eq"][r1["eq"].index < _OOS]),
              "trades": r1["n_trades"] - r1["oos_trades"]}
    got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
    a_ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
            and _evidence_matches(got_oos, t["backtest"]["out_sample"]))
    x2 = t["backtest"]["cost_x2"]
    clauses = {"x2_full": abs(r2["full"]["sharpe"] - x2["sharpe"]) < ANCHOR_TOL}
    if "oos_sharpe" in x2:
        clauses["x2_oos"] = abs(r2["oos"]["sharpe"]
                                - x2["oos_sharpe"]) < ANCHOR_TOL
    return {"anchor_ok": bool(a_ok),
            "x2_ok": bool(all(clauses.values())),
            "x2_clauses": {k: bool(v) for k, v in clauses.items()}}


def run_gates() -> dict:
    """Hard gates (prereg sec.2/sec.4): anchor repro x6, panel completeness,
    skill-line inputs. Writes GATES_JSON (registered returns for D6)."""
    from live.paper import PAPER_LEVELS, load_core
    from firm.hr import TRADERS_DIR, load_trader
    from p3_portfolio import member_run
    import science_gates as sg

    prices_full = load_core()
    n_syms = len(prices_full)
    end_510300 = str(prices_full["510300"].index[-1].date())
    panel_ok = bool(n_syms == 48 and end_510300 == CUTOFF)

    anchors, reg_rets = [], {}
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        r1 = member_run(t, prices_full)                 # own cutoff, 1x
        r2 = member_run(t, prices_full, cost_mult=2.0)  # own cutoff, x2
        chk = _anchor_check(t, r1, r2)
        anchors.append({"member": t["id"],
                        "anchor_ok": chk["anchor_ok"], "x2_ok": chk["x2_ok"],
                        "x2_clauses": chk["x2_clauses"]})
        reg_rets[t["id"]] = [round(float(x), 8)
                             for x in r1["eq"].pct_change().dropna().to_numpy()]
    anchor_ok = all(a["anchor_ok"] and a["x2_ok"] for a in anchors)

    np_ = sg.null_sharpes()["coverage"]
    line_ok = bool(np_["n_values"] >= 30 and np_["mu"] is not None)
    passive = sg.passive_baseline("core48")
    line_ok = bool(line_ok and passive is not None)

    gates = {
        "g1_anchor_repro": {"ok": bool(anchor_ok and len(anchors) == 6),
                            "members": anchors},
        "g2_panel": {"ok": panel_ok, "n_syms": n_syms,
                     "end_510300": end_510300, "cutoff": CUTOFF},
        "g4_line_inputs": {"ok": line_ok, "null_n": np_["n_values"],
                           "null_mu": np_["mu"], "null_sigma": np_["sigma"],
                           "passive_core48": passive},
        "ok": bool(anchor_ok and panel_ok and line_ok and len(anchors) == 6),
    }
    with open(GATES_JSON, "w", encoding="utf-8") as fh:
        json.dump({"gates": gates, "registered_rets": reg_rets}, fh,
                  ensure_ascii=False, indent=1)
    return gates


# ----------------------------------------------------------------------- run

def cmd_run(_) -> int:
    if os.environ.get("T33_DETACHED") == "1":
        sys.stdout = open(LOG_PATH, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    _log("T-33 attack wave: gates...")
    gates = run_gates()
    _log(f"gates: anchor={gates['g1_anchor_repro']['ok']} "
         f"panel={gates['g2_panel']['ok']} line={gates['g4_line_inputs']['ok']}")
    if not gates["ok"]:
        _log("GATES FAILED -- batch void (prereg sec.4), exit 2")
        return 2

    jobs = []
    done = load_done_keys(CELLS_PATH)
    for cid, _, _ in CANDIDATES:
        for face in FACES:
            if f"{cid}|{face}" not in done:
                jobs.append((cid, face))
    _log(f"cells todo={len(jobs)}/40 (resume-skipped={40 - len(jobs)})")
    if jobs:
        from parallel_runner import worker_cap
        from concurrent.futures import ProcessPoolExecutor, as_completed
        workers = worker_cap()
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_init_worker) as pool:
            futs = {pool.submit(_run_cell, c, f): (c, f) for c, f in jobs}
            with open(CELLS_PATH, "a", encoding="utf-8") as fh:
                for fut in as_completed(futs):
                    row = fut.result()
                    fh.write(json.dumps(row, default=bool) + "\n")
                    fh.flush()
                    if row["status"] == "ok":
                        _log(f"cell {row['key']}: sharpe={row['sharpe_full']} "
                             f"entries={row['n_entries']} ({row['elapsed_s']}s)")
                    else:
                        _log(f"cell {row['key']}: {row['status']} "
                             f"{row.get('error', '')}")
    _log(f"run phase done in {time.time() - t0:.0f}s -- finalizing")
    return cmd_finalize(_)


def cmd_status(_) -> int:
    done = load_done_keys(CELLS_PATH)
    print(f"cells done={len(done)}/40")
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as fh:
            for ln in fh.read().splitlines()[-8:]:
                print(ln)
    if os.path.exists(OUT_JSON):
        print("results JSON present (finalize already ran)")
    return 0


# ------------------------------------------------------------------- finalize

def _pearson(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def _panel_index() -> pd.DatetimeIndex:
    """Rebuild the batch panel calendar (union of core48 dates <= CUTOFF).

    Cell rows carry plain return lists (lean JSONL); dates are re-attached
    here so D6 corr aligns BY DATE (registered members run at their own
    09-22 cutoff -> tail short by 2 days, inner-join drops honestly)."""
    from live.paper import load_core
    ps = pd.Timestamp(CUTOFF)
    all_idx: set = set()
    for df in load_core().values():
        all_idx.update(df.index[df.index <= ps])
    return pd.DatetimeIndex(sorted(all_idx))


def cmd_finalize(_) -> int:
    import science_gates as sg
    rows = {}
    with open(CELLS_PATH, encoding="utf-8") as fh:
        for ln in fh.read().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("status") == "ok":
                rows[r["key"]] = r
    missing = [f"{c}|{f}" for c, _, _ in CANDIDATES for f in FACES
               if f"{c}|{f}" not in rows]
    if missing:
        print(f"finalize refused: {len(missing)} cells missing: {missing[:5]}")
        return 2
    if os.path.exists(OUT_JSON) and os.environ.get("T33_REFINALIZE") != "1":
        print("finalize refused: OUT_JSON already written "
              "(double ledger append guard; set T33_REFINALIZE=1 to redo)")
        return 2

    gates = json.load(open(GATES_JSON, encoding="utf-8"))
    pidx = _panel_index()
    rets_by = {}
    for c, _, _ in CANDIDATES:
        rl = rows[f"{c}|base"]["rets"]
        rets_by[c] = pd.Series(rl, index=pidx[1:len(rl) + 1])
    span_days = float((pd.Timestamp(CUTOFF) - pidx[0]).days)
    years = max(span_days / 365.25, 1e-9)

    cand_rows, merged_into = [], {}
    for i, (cid, grp, kind) in enumerate(CANDIDATES):
        base, x2 = rows[f"{cid}|base"], rows[f"{cid}|x2"]
        rseries = rets_by[cid]
        # D6: vs earlier-priority same-batch candidates (merge clause)
        d6_status, d6_max, d6_pair = "unique", 0.0, None
        for earlier in [c for c, _, _ in CANDIDATES[:i]]:
            cc = abs(_pearson(rseries, rets_by[earlier]))
            if np.isfinite(cc) and cc > d6_max:
                d6_max = cc
            if np.isfinite(cc) and cc >= D6_LINE and d6_pair is None:
                d6_pair = earlier
        if d6_pair is not None:
            merged_into[cid] = d6_pair
            d6_status = "d6-merged"
        # D6 disclosure vs registered six (no rejection, prereg s1)
        reg_max, reg_arg = 0.0, None
        for rid, rrets in gates["registered_rets"].items():
            rs = pd.Series(rrets, index=pidx[1:len(rrets) + 1])
            cc = abs(_pearson(rseries, rs))
            if np.isfinite(cc) and cc > reg_max:
                reg_max, reg_arg = cc, rid

        g1 = sg.g1_prime_v2(base["sharpe_full"], base["rets"],
                            batch_cells=BATCH_CELLS,
                            n_trades=base["n_trades"],
                            n_entries=base["n_entries"])
        entries_per_year = base["n_entries"] / years
        oos_double = bool(base["oos_sharpe"] > 0 and base["oos_annual_return"] > 0)
        cand_rows.append({
            "cand": cid, "group": grp, "kind": kind,
            "exit_regime": "ce" if kind == "member" and cid.endswith("CE-01") else "default",
            "sharpe_full": base["sharpe_full"],
            "annual_return": base["annual_return"],
            "max_drawdown": base["max_drawdown"],
            "oos_sharpe": base["oos_sharpe"],
            "oos_annual_return": base["oos_annual_return"],
            "oos_double_positive": oos_double,
            "n_trades": base["n_trades"], "n_entries": base["n_entries"],
            "oos_trades": base["oos_trades"],
            "entries_per_year": round(entries_per_year, 2),
            "turnover_budget_ok": bool(entries_per_year <= TURNOVER_BUDGET),
            "x2_full_sharpe": x2["sharpe_full"],
            "descriptive": {
                "ann_positive": bool(base["annual_return"] > 0),
                "oos_double_positive": oos_double,
                "dd_ok": bool(base["max_drawdown"] >= -0.35),
            },
            "d6": {"status": d6_status,
                   "max_corr_same_batch": round(d6_max, 4),
                   "merged_into": d6_pair,
                   "max_corr_vs_registered": round(reg_max, 4),
                   "vs_registered_argmax": reg_arg},
            "g1_prime_v2": g1,
            "dist_to_line": round(base["sharpe_full"] - g1["skill_line"]["line"], 4),
            "pass_v2": bool(g1["pass_v2"]),
        })

    line = cand_rows[0]["g1_prime_v2"]["skill_line"]
    n_pass = sum(1 for r in cand_rows if r["pass_v2"])
    led = sg.append_ledger("t33_attack_wave", BATCH_CELLS,
                           file_name="results/t33_attack_wave.json",
                           evidence_cutoff=CUTOFF)

    att = json.load(open(ATT_JSON, encoding="utf-8"))
    att["entries"].append({
        "batch": "T33_ATTACK_WAVE", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "cells_ledger_delta": BATCH_CELLS,
        "ledger_total_after": led["total"],
        "gates": {"g1_prime_v2_pass": n_pass,
                  "skill_line_v2": line["line"],
                  "anchor_repro_all_pass": True},
        "eliminated": len(cand_rows) - n_pass,
        "refs": {"results": OUT_JSON, "prereg": PREREG_PATH},
    })
    with open(ATT_JSON, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)

    out = {
        **sg.cutoff_meta(CUTOFF),
        "batch": "T33_ATTACK_WAVE", "ticket": TICKET,
        "prereg": PREREG_PATH, "prereg_sha256_16": _sha256_file(PREREG_PATH)[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "rule": {"batch_cells": BATCH_CELLS, "faces": list(FACES),
                 "oos_start": OOS_START, "cost": "V1 legacy 13bp x2 + CostPatch(2.0)",
                 "turnover_budget_per_year": TURNOVER_BUDGET,
                 "d6_line": D6_LINE,
                 "d6_priority_order": [c for c, _, _ in CANDIDATES]},
        "gates": gates["gates"],
        "skill_line": line,
        "summary": {
            "n_candidates": len(cand_rows),
            "g1_prime_v2_pass": n_pass,
            "d6_merged": sorted(merged_into.keys()),
            "turnover_breaches": [r["cand"] for r in cand_rows
                                  if not r["turnover_budget_ok"]],
        },
        "candidates": cand_rows,
        "ledger": led,
        "audit": {
            "machine": _machine_id(),
            "engine_runs": 40,
            "anchor_repro_runs": 12,
            "null_pool_consumed": "shared core48 collector (K=0 own nulls, prereg s3)",
            "prereg_frozen_before_run": True,
        },
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    cols = ["cand", "group", "exit_regime", "sharpe_full", "dist_to_line",
            "pass_v2", "line_ok", "ci_ok", "entries_ok", "annual_return",
            "oos_sharpe", "oos_annual_return", "oos_double_positive",
            "max_drawdown", "x2_full_sharpe", "n_trades", "n_entries",
            "entries_per_year", "turnover_budget_ok", "d6_status",
            "d6_merged_into", "max_corr_vs_registered", "n_oos_trades"]
    import csv as _csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for r in cand_rows:
            w.writerow([r["cand"], r["group"], r["exit_regime"],
                         r["sharpe_full"], r["dist_to_line"], r["pass_v2"],
                         r["g1_prime_v2"]["line_ok"],
                         r["g1_prime_v2"]["ci_lower_bound_positive"],
                         r["g1_prime_v2"].get("trade_gate", {}).get("entries_ok", ""),
                         r["annual_return"], r["oos_sharpe"],
                         r["oos_annual_return"], r["oos_double_positive"],
                         r["max_drawdown"], r["x2_full_sharpe"],
                         r["n_trades"], r["n_entries"], r["entries_per_year"],
                         r["turnover_budget_ok"], r["d6"]["status"],
                         r["d6"]["merged_into"] or "",
                         r["d6"]["max_corr_vs_registered"], r["oos_trades"]])
    _log(f"finalize: {n_pass}/20 pass_v2, line={line['line']}, "
         f"ledger total={led['total']}")
    print(f"finalize OK: {n_pass}/20 pass_v2; skill_line={line['line']}; "
          f"ledger={led['total']}; d6_merged={sorted(merged_into.keys())}")
    return 0


def _common_index(rets_by: dict) -> pd.DatetimeIndex:
    """Deprecated shim kept for import compatibility (unused by finalize)."""
    for s in rets_by.values():
        return s.index
    return pd.DatetimeIndex([])


def _machine_id() -> str:
    try:
        with open(os.path.join("fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except Exception:
        return "unknown"


# ------------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    rng = np.random.default_rng(7)
    fails = []

    def check(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # S1: slope_r2 closed form vs brute-force OLS
    T, S, n = 90, 3, 25
    close = pd.DataFrame(100 + np.cumsum(rng.normal(0, 1, (T, S)), axis=0),
                         index=pd.bdate_range("2024-01-01", periods=T),
                         columns=[f"s{j}" for j in range(S)])
    got = _slope_r2(close, n)
    y = np.log(close.to_numpy())
    for i in (n - 1, 50, T - 1):
        for j in range(S):
            w = y[i - n + 1:i + 1, j]
            x = np.arange(n)
            b, a = np.polyfit(x, w, 1)
            pred = a + b * x
            ss_res = float(((w - pred) ** 2).sum())
            ss_tot = float(((w - w.mean()) ** 2).sum())
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            want = b * r2
            check_ok = abs(got.iloc[i, j] - want) < 1e-9
            if not check_ok:
                check(f"S1 slope_r2@({i},{j}) {got.iloc[i, j]} vs {want}", False)
                break
        else:
            continue
        break
    check("S1 slope_r2 closed form == polyfit", True)
    # warmup rows NaN
    check("S1b warmup NaN", bool(got.iloc[:n - 1].isna().all().all()))

    # S2: dual momentum variant -- qualify / defense / flat
    idx = pd.bdate_range("2024-01-01", periods=140)
    p = pd.DataFrame({
        "AAA": np.linspace(100, 140, 140),      # strong up
        "BBB": np.linspace(100, 130, 140),      # medium up
        "CCC": np.linspace(100, 95, 140),       # down
        "511260": np.linspace(100, 101, 140),   # defense mild up
        "518880": np.linspace(100, 100.5, 140),
    }, index=idx)
    e = dual_mom_v_entry(p)
    last = e.iloc[-1]
    check("S2a qualifiers top3 all-up", bool(last["AAA"] == 1 and last["BBB"] == 1))
    # S2b: risk assets crash (60d mom<0); defense NOT rank-qualifiable (60d
    # mom<0) but 20d mom>0 -> the switch leg must pick the defense argmax.
    p2 = p.copy()
    p2[["AAA", "BBB", "CCC"]] = np.repeat(
        np.linspace(100, 70, 140)[:, None], 3, axis=1)   # all crash
    dpath = np.concatenate([np.linspace(100, 104, 80),       # early rise
                            np.linspace(104, 98, 40),        # dip
                            np.linspace(98, 100, 20)])       # 20d rebound
    p2["511260"] = dpath
    p2["518880"] = dpath * 0.99                              # weaker argmax
    e2 = dual_mom_v_entry(p2)
    check("S2b defense switch picks argmax when none qualify",
          bool(e2.iloc[-1].sum() == 1 and e2.iloc[-1]["511260"] == 1))
    p3 = p2.copy()
    p3[["511260", "518880"]] = np.repeat(
        np.linspace(100, 90, 140)[:, None], 2, axis=1)   # defense down too
    e3 = dual_mom_v_entry(p3)
    check("S2c flat when defense momentum <= 0", bool(e3.iloc[-1].sum() == 0))

    # S3: GEM monthly causality
    idx = pd.bdate_range("2022-01-03", periods=420)
    up = np.linspace(100, 160, 420)         # 510300 strong
    dn = np.linspace(100, 80, 420)          # 513100 weak
    flat = np.linspace(100, 99, 420)
    pg = pd.DataFrame({"510300": up, "513100": dn, "513180": flat,
                       "511260": np.linspace(100, 103, 420)}, index=idx)
    eg = gem_entry(pg)
    me_days = pd.Series(np.arange(len(idx)), index=idx).groupby(
        idx.to_period("M")).tail(1).index
    after_me = idx.get_loc(me_days[13]) + 1     # first day after 14th month-end
                                              # (mom12 needs 252d warmup)
    check("S3a winner state held after month-end",
          bool(eg.iloc[after_me]["510300"] == 1 and eg.iloc[after_me].sum() == 1))
    check("S3b warmup before 252d all-flat",
          bool(eg.iloc[:250].to_numpy().sum() == 0))
    pgb = pg.copy()
    pgb[["510300", "513100", "513180"]] = np.repeat(
        np.linspace(100, 60, 420)[:, None], 3, axis=1)
    egb = gem_entry(pgb)
    after_me2 = idx.get_loc(me_days[14]) + 1
    check("S3c defense leg when winner momentum <= 0",
          bool(egb.iloc[after_me2]["511260"] == 1 and egb.iloc[after_me2].sum() == 1))

    # S4: D6 merge priority order
    order = [c for c, _, _ in CANDIDATES]
    check("S4 candidate order A>B>C",
          bool(order[0].startswith("PROS-VOB") and order[5] == "slope_r2_rotation_25_top3_r8"
               and order[8] == "donchian_20_10" and len(order) == 20))

    # S5: turnover years math
    yrs = (pd.Timestamp(CUTOFF) - pd.Timestamp("2020-01-02")).days / 365.25
    check("S5 span ~6.7y", bool(6.0 < yrs < 7.5))

    # S6: checkpoint truncated-tail tolerance
    tmp = CELLS_PATH + ".selftest"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"key": "a|base"}) + "\n")
        fh.write('{"key": "b|base", "rets": [0.1,')  # truncated tail
    keys = load_done_keys(tmp)
    os.remove(tmp)
    check("S6 truncated tail tolerated", bool(keys == {"a|base"}))

    # S7: probe cutoff override semantic
    t = {"evidence_cutoff": "2026-09-22", "params": {"entry": "x"}}
    probe = dict(t)
    probe["evidence_cutoff"] = CUTOFF
    probe["params"] = dict(t["params"])
    probe["params"]["report_num_entries"] = True
    check("S7 probe override + flag, source untouched",
          bool(probe["evidence_cutoff"] == CUTOFF
               and t["evidence_cutoff"] == "2026-09-22"
               and "report_num_entries" not in t["params"]
               and probe["params"]["report_num_entries"] is True))

    # S8: 8d rebal gating == composite pattern on synthetic
    sc = pd.DataFrame(rng.normal(0, 0.02, (60, 5)).cumsum(axis=0) + 100,
                      index=pd.bdate_range("2024-01-01", periods=60),
                      columns=["a", "b", "c", "d", "e"])
    sig = slope_r2_entry(sc, 25, 2, 8)
    in_set_any = (sig.diff().abs().sum(axis=1) > 0)
    change_days = [i for i in range(len(sig)) if in_set_any.iloc[i]]
    gaps = {change_days[k + 1] - change_days[k] for k in range(len(change_days) - 1)}
    check("S8 rebal changes only on 8d grid", bool(all(g % 8 == 0 for g in gaps)))

    print(f"selftest: {len(fails)} FAIL" if fails else "selftest: ALL PASS")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "status", "finalize", "selftest"])
    return {"run": cmd_run, "status": cmd_status,
            "finalize": cmd_finalize, "selftest": cmd_selftest}[
        ap.parse_args().cmd](None)


if __name__ == "__main__":
    sys.exit(main())
